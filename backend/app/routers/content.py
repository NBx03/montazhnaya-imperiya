"""
Content API Router.

Handles public landing page content queries with ETag / 304 Not Modified caching,
and protected admin updates with payload validation.
"""

from datetime import datetime, timezone
import hashlib
import json
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_admin
from app.database import get_db
from app.models import AdminUser, MediaAsset, SiteContent
from app.schemas import SiteContentOut, SiteContentUpdate, validate_section_payload


def _collect_section_uploads(obj, prefix: str = "", out: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Extracts mapping {field_path: /uploads/..._url} from validated section payload."""
    if out is None:
        out = {}
    if isinstance(obj, str) and obj.startswith("/uploads/"):
        out[prefix] = obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            _collect_section_uploads(v, path, out)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            path = f"{prefix}.{idx}" if prefix else str(idx)
            _collect_section_uploads(item, path, out)
    return out

router = APIRouter(tags=["content"])

# Public endpoint: fast full-site JSON with ETag & 304 support
@router.get("/api/v1/content")
async def get_public_content(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Public content delivery for landing page hydration.
    Supports HTTP caching via Cache-Control and ETag (returns 304 Not Modified if unchanged).
    """
    stmt = select(SiteContent).order_by(SiteContent.order)
    result = await db.execute(stmt)
    records = result.scalars().all()

    sections = {}
    latest_timestamp = ""
    for r in records:
        sections[r.section_key] = r.data
        if r.updated_at:
            up_iso = r.updated_at.isoformat()
            if up_iso > latest_timestamp:
                latest_timestamp = up_iso

    # Generate deterministic ETag based on timestamp and payload digest
    content_hash = hashlib.md5(json.dumps(sections, sort_keys=True, default=str).encode()).hexdigest()[:8]
    etag_source = f"{len(records)}:{latest_timestamp}:{content_hash}"
    etag = f'W/"{hashlib.md5(etag_source.encode()).hexdigest()[:16]}"'

    # Check conditional GET
    client_etag = request.headers.get("if-none-match")
    if client_etag and client_etag.strip() == etag.strip():
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "no-cache, public"

    return {
        "status": "success",
        "sections": sections,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


# Admin endpoint: get all sections with metadata
@router.get("/api/v1/admin/content", response_model=List[SiteContentOut])
async def get_admin_content(
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """Returns all content sections for the admin editor interface."""
    stmt = select(SiteContent).order_by(SiteContent.order)
    result = await db.execute(stmt)
    return result.scalars().all()


# Admin endpoint: get specific section
@router.get("/api/v1/admin/content/{section_key}", response_model=SiteContentOut)
async def get_section_content(
    section_key: str,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """Returns a single section by its unique key."""
    stmt = select(SiteContent).where(SiteContent.section_key == section_key)
    result = await db.execute(stmt)
    section = result.scalars().first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Секция '{section_key}' не найдена",
        )
    return section


# Admin endpoint: update specific section
@router.put("/api/v1/admin/content/{section_key}", response_model=SiteContentOut)
async def update_section_content(
    section_key: str,
    payload: SiteContentUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """
    Updates data for a section.
    Protected: requires admin JWT token.
    """
    if not payload.data or not isinstance(payload.data, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Поле 'data' должно быть непустым словарем.",
        )

    stmt = select(SiteContent).where(SiteContent.section_key == section_key)
    result = await db.execute(stmt)
    section = result.scalars().first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Секция '{section_key}' не найдена",
        )

    try:
        validated_data = validate_section_payload(section_key, payload.data)
    except ValidationError as exc:
        errors = []
        for err in exc.errors():
            loc = ".".join(str(p) for p in err.get("loc", []))
            msg = err.get("msg", "Некорректное значение").replace("Value error, ", "")
            errors.append({"field": loc, "message": msg})
        first_msg = errors[0]["message"] if errors else "Ошибка валидации полей секции"
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": first_msg, "errors": errors},
        )

    now_utc = datetime.now(timezone.utc)
    section.data = validated_data
    section.updated_at = now_utc

    # Remember which media slots use which uploaded files for instant history & restore
    upload_map = _collect_section_uploads(validated_data)
    if upload_map:
        urls = list(set(upload_map.values()))
        url_to_path = {url: path for path, url in upload_map.items()}
        assets_res = await db.execute(select(MediaAsset).where(MediaAsset.url.in_(urls)))
        for asset in assets_res.scalars().all():
            asset.section_key = section_key
            asset.field_path = url_to_path[asset.url][:128]
            asset.last_used_at = now_utc

    await db.commit()
    await db.refresh(section)
    return section
