"""
Leads API Router.

Handles public lead submission with proxy-aware rate-limiting and anti-spam honeypot,
as well as admin-only lead triage, status updates, and CSV injection-safe exports.
"""

import csv
import io
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_admin
from app.database import get_db
from app.limiter import get_client_ip, limiter
from app.models import AdminUser, Lead, LeadStatus
from app.schemas import LeadCreate, LeadListResponse, LeadOut, LeadUpdate

logger = logging.getLogger("montazh.leads")
router = APIRouter(tags=["leads"])


def sanitize_csv_cell(val: Optional[str]) -> str:
    """
    Prevents CSV Formula Injection (CWE-1236).
    Escapes dangerous leading characters (=, +, -, @, tab) with a single quote.
    """
    if not val:
        return ""
    text_val = str(val).strip()
    if text_val.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{text_val}"
    return text_val


# Public: submit lead with rate limit & honeypot
@router.post("/api/v1/leads")
@limiter.limit("5/minute")
async def submit_lead(
    request: Request,
    payload: LeadCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Receives public lead inquiries from landing page forms.
    - Honeypot: silently discards submissions with filled company_website trap.
    - Rate-limiting: max 5 requests per minute per real client IP.
    """
    client_ip = get_client_ip(request)

    # Honeypot spam check: if filled by a bot, silently return success without saving
    if payload.company_website:
        logger.info("Спам-бот пойман в honeypot-ловушку с IP %s (сайт: %s)", client_ip, payload.company_website)
        return {"status": "success", "message": "Заявка успешно отправлена!"}

    user_agent = request.headers.get("user-agent")
    clean_name = payload.name.strip() if payload.name else None

    lead = Lead(
        name=clean_name,
        phone=payload.phone,
        status=LeadStatus.NEW,
        source=payload.source or "general",
        ip_address=client_ip,
        user_agent=user_agent[:256] if user_agent else None,
        created_at=datetime.now(timezone.utc),
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    logger.info(
        "Новая заявка #%s: %s (%s), источник: '%s', IP: %s",
        lead.id,
        lead.phone,
        lead.name or "без имени",
        lead.source,
        client_ip
    )

    return {
        "status": "success",
        "message": "Заявка успешно принята! Наш инженер свяжется с вами в течение 15 минут.",
        "lead_id": lead.id,
    }


# Admin: get list of leads with counts
@router.get("/api/v1/admin/leads", response_model=LeadListResponse)
async def get_admin_leads(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """
    Returns paginated list of leads with status breakdown metrics.
    Protected: requires admin JWT token.
    """
    total_q = await db.execute(select(func.count(Lead.id)))
    total = total_q.scalar() or 0

    new_q = await db.execute(select(func.count(Lead.id)).where(Lead.status == LeadStatus.NEW))
    new_count = new_q.scalar() or 0

    processed_q = await db.execute(select(func.count(Lead.id)).where(Lead.status == LeadStatus.PROCESSED))
    processed_count = processed_q.scalar() or 0

    stmt = select(Lead).order_by(desc(Lead.created_at)).offset(offset).limit(limit)
    if status_filter in ("new", "processed"):
        stmt = stmt.where(Lead.status == LeadStatus(status_filter))

    result = await db.execute(stmt)
    leads = result.scalars().all()

    return LeadListResponse(
        total=total,
        new_count=new_count,
        processed_count=processed_count,
        leads=[LeadOut.model_validate(l) for l in leads],
    )


# Admin: update lead status or notes
@router.patch("/api/v1/admin/leads/{lead_id}", response_model=LeadOut)
async def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """Updates lead triage status (new/processed) and optional admin comments."""
    stmt = select(Lead).where(Lead.id == lead_id)
    result = await db.execute(stmt)
    lead = result.scalars().first()

    if not lead:
        raise HTTPException(status_code=404, detail=f"Заявка #{lead_id} не найдена")

    if payload.status is not None:
        lead.status = payload.status
    if payload.notes is not None:
        lead.notes = payload.notes.strip() if payload.notes else None

    await db.commit()
    await db.refresh(lead)

    logger.info("Заявка #%s обновлена: статус '%s' (администратор: %s)", lead.id, lead.status.value, admin.username)
    return LeadOut.model_validate(lead)


# Admin: delete lead
@router.delete("/api/v1/admin/leads/{lead_id}")
async def delete_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """Deletes a spam or invalid lead entry."""
    stmt = select(Lead).where(Lead.id == lead_id)
    result = await db.execute(stmt)
    lead = result.scalars().first()

    if not lead:
        raise HTTPException(status_code=404, detail=f"Заявка #{lead_id} не найдена")

    await db.delete(lead)
    await db.commit()

    logger.info("Заявка #%s удалена администратором '%s'", lead_id, admin.username)
    return {"status": "success", "message": f"Заявка #{lead_id} удалена"}


# Admin: export CSV
@router.get("/api/v1/admin/leads/export-csv")
async def export_leads_csv(
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """
    Exports all leads to CSV format with UTF-8 BOM encoding for Microsoft Excel compatibility.
    Sanitizes values against CSV Formula Injection.
    """
    stmt = select(Lead).order_by(desc(Lead.created_at))
    result = await db.execute(stmt)
    leads = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    writer.writerow([
        "ID", "Дата создания (UTC)", "Имя клиента", "Телефон",
        "Источник формы", "Статус", "IP-адрес", "Заметки"
    ])

    for l in leads:
        created_str = l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else ""
        writer.writerow([
            l.id,
            created_str,
            sanitize_csv_cell(l.name),
            sanitize_csv_cell(l.phone),
            sanitize_csv_cell(l.source),
            "Новая" if l.status == LeadStatus.NEW else "Обработана",
            sanitize_csv_cell(l.ip_address),
            sanitize_csv_cell(l.notes),
        ])

    csv_data = output.getvalue().encode("utf-8-sig")
    filename = f"leads_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"

    logger.info("Экспорт CSV заявок: выгружено %s строк (администратор: %s)", len(leads), admin.username)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )
