"""
Media Upload API Router.

Validates file types, sanitizes names, checks magic bytes to prevent spoofing,
resizes oversized images (decompression bomb protection), and optimizes to WebP.
"""

from datetime import datetime, timezone
import io
import logging
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from PIL import Image, ImageOps
from sqlalchemy import delete as sql_delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_admin
from app.config import settings
from app.database import get_db
from app.models import AdminUser, MediaAsset, SiteContent
from app.schemas import MediaFileItem, MediaListResponse, UploadResponse

logger = logging.getLogger("montazh.upload")
router = APIRouter(prefix="/api/v1/admin/upload", tags=["upload"])

# Strict safe filename regex (32 hex chars + .webp/.mp4/.webm) to block path traversal
_SAFE_MEDIA_FILENAME_RE = re.compile(r"^[a-f0-9]{32}\.(webp|mp4|webm)$")

# Maximum pixel bounds to prevent memory exhaustion (DoS decompression bombs)
MAX_IMAGE_WIDTH = 4096
MAX_IMAGE_HEIGHT = 4096


def is_valid_mp4(data: bytes) -> bool:
    """Checks for standard ISO Base Media File Format (MP4) signature."""
    if len(data) < 12:
        return False
    # Standard MP4 container begins with 'ftyp' or 'moov' atom at offset 4
    return data[4:8] in (b"ftyp", b"moov")


def is_valid_webm(data: bytes) -> bool:
    """Checks for Matroska/WebM EBML magic signature."""
    return len(data) >= 4 and data.startswith(b"\x1a\x45\xdf\xa3")


def _collect_active_upload_refs(obj, section_key: str, prefix: str = "", out: Optional[Dict[str, Tuple[str, str]]] = None):
    """Maps every /uploads/... URL currently used in SiteContent to (section_key, field_path)."""
    if out is None:
        out = {}
    if isinstance(obj, str) and obj.startswith("/uploads/"):
        out.setdefault(obj, (section_key, prefix))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            _collect_active_upload_refs(v, section_key, path, out)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            path = f"{prefix}.{idx}" if prefix else str(idx)
            _collect_active_upload_refs(item, section_key, path, out)
    return out


@router.post("", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    section_key: Optional[str] = Form(None),
    field_path: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """
    Handles media upload from admin dashboard.
    - Validates file size (max 15MB).
    - Validates magic byte signatures (prevents executable masquerading).
    - Downscales oversized images if exceeding 4K resolution.
    - Converts all image uploads into optimized .webp files.
    """
    content_type = (file.content_type or "").lower()
    # Strip any potential path traversal in filename
    original_name = Path(file.filename or "uploaded_file").name

    is_image = content_type in settings.ALLOWED_IMAGE_TYPES
    is_video = content_type in settings.ALLOWED_VIDEO_TYPES

    if not is_image and not is_video:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый формат файла. Разрешены JPG, PNG, WEBP, MP4 и WEBM.",
        )

    # Read binary content
    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Файл слишком большой. Максимальный размер — {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} МБ.",
        )

    unique_id = uuid.uuid4().hex

    if is_image:
        try:
            image = Image.open(io.BytesIO(data))
            image.verify()  # Verify image integrity

            # Reopen after verify (verify destroys image buffer pointer)
            image = Image.open(io.BytesIO(data))
            image = ImageOps.exif_transpose(image)

            # Decompression bomb mitigation: auto-downscale if larger than 4K
            if image.width > MAX_IMAGE_WIDTH or image.height > MAX_IMAGE_HEIGHT:
                image.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)

            # Palette and transparency conversion
            if image.mode in ("P", "LA"):
                image = image.convert("RGBA")
            elif image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")

            saved_filename = f"{unique_id}.webp"
            target_path = settings.UPLOAD_DIR / saved_filename
            image.save(target_path, format="WEBP", quality=85, method=6)
            saved_size = target_path.stat().st_size
            saved_content_type = "image/webp"

            logger.info(
                "Изображение оптимизировано и сохранено: %s (%s КБ, оригинал: '%s')",
                saved_filename,
                saved_size // 1024,
                original_name
            )

        except Exception as e:
            logger.error("Ошибка при обработке изображения '%s': %s", original_name, e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Поврежденное изображение или неподдерживаемый формат: {str(e)}",
            )
    else:
        # Video verification (MP4 or WebM)
        if content_type == "video/webm":
            if not is_valid_webm(data):
                logger.warning("Заблокирована попытка загрузки невалидного WebM '%s' от %s", original_name, admin.username)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Файл не является валидным WebM видео.",
                )
            ext = "webm"
            saved_content_type = "video/webm"
        else:
            if not is_valid_mp4(data):
                logger.warning("Заблокирована попытка загрузки невалидного видео '%s' от %s", original_name, admin.username)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Файл не является валидным MP4 видео.",
                )
            ext = "mp4"
            saved_content_type = "video/mp4"

        saved_filename = f"{unique_id}.{ext}"
        target_path = settings.UPLOAD_DIR / saved_filename
        with open(target_path, "wb") as f:
            f.write(data)
        saved_size = len(data)

        logger.info("Видео сохранено: %s (%s КБ, оригинал: '%s')", saved_filename, saved_size // 1024, original_name)

    url = f"/uploads/{saved_filename}"
    now_utc = datetime.now(timezone.utc)
    asset = MediaAsset(
        filename=saved_filename,
        url=url,
        original_name=original_name[:256],
        content_type=saved_content_type,
        size_bytes=saved_size,
        section_key=section_key[:64] if section_key else None,
        field_path=field_path[:128] if field_path else None,
        last_used_at=now_utc if (section_key and field_path) else None,
        created_at=now_utc,
    )
    db.add(asset)
    await db.commit()

    return UploadResponse(
        filename=saved_filename,
        url=url,
        original_name=original_name,
        size_bytes=saved_size,
        content_type=saved_content_type,
    )


@router.get("", response_model=MediaListResponse)
async def list_uploaded_media(
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """Lists server media files enriched with original names, slot bindings, and active state."""
    settings.ensure_directories()
    mime_map = {".mp4": "video/mp4", ".webm": "video/webm", ".webp": "image/webp"}

    # Fetch currently active upload URLs from all site content sections
    active_refs: Dict[str, Tuple[str, str]] = {}
    sec_res = await db.execute(select(SiteContent))
    for sec in sec_res.scalars().all():
        _collect_active_upload_refs(sec.data, sec.section_key, out=active_refs)

    # Fetch MediaAsset metadata map by filename
    asset_res = await db.execute(select(MediaAsset))
    asset_map: Dict[str, MediaAsset] = {a.filename: a for a in asset_res.scalars().all()}

    items: List[MediaFileItem] = []
    for path in settings.UPLOAD_DIR.iterdir():
        if not path.is_file() or not _SAFE_MEDIA_FILENAME_RE.match(path.name):
            continue
        stat = path.stat()
        url = f"/uploads/{path.name}"
        asset = asset_map.get(path.name)
        active_slot = active_refs.get(url)

        sec_key = (active_slot[0] if active_slot else None) or (asset.section_key if asset else None)
        fld_path = (active_slot[1] if active_slot else None) or (asset.field_path if asset else None)
        created_dt = asset.created_at if asset else datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        last_used_dt = asset.last_used_at if asset else None

        items.append(
            MediaFileItem(
                filename=path.name,
                url=url,
                original_name=asset.original_name if asset else path.name,
                size_bytes=stat.st_size,
                content_type=mime_map.get(path.suffix, "application/octet-stream"),
                section_key=sec_key,
                field_path=fld_path,
                is_active=url in active_refs,
                last_used_at=last_used_dt,
                created_at=created_dt,
            )
        )

    items.sort(key=lambda item: item.last_used_at or item.created_at, reverse=True)
    return MediaListResponse(files=items)


@router.delete("/{filename}")
async def delete_uploaded_media(
    filename: str,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """Deletes an uploaded media file from disk and removes its MediaAsset record."""
    if not _SAFE_MEDIA_FILENAME_RE.match(filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректное имя медиафайла.",
        )

    target_path = (settings.UPLOAD_DIR / filename).resolve()
    if target_path.parent != settings.UPLOAD_DIR.resolve() or not target_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден.",
        )

    target_path.unlink()
    await db.execute(sql_delete(MediaAsset).where(MediaAsset.filename == filename))
    await db.commit()
    logger.info("Медиафайл '%s' удален администратором '%s'", filename, admin.username)
    return {"status": "success", "message": f"Файл {filename} удален"}
