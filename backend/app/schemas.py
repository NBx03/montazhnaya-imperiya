"""
Pydantic V2 Schemas for Request & Response Data Validation.

Provides strict input validation for leads, authentication, media uploads,
and per-section site content payloads so invalid formats (oversized phones,
malformed emails, dangerous URIs, non-numeric odometers) are rejected both
server-side and client-side.
"""

from datetime import datetime
import re
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.models import LeadStatus

# ==========================================
# SHARED VALIDATION HELPERS
# ==========================================
_PHONE_CHARS_RE = re.compile(r"^[+\d\s()\-]+$")
_CLEAN_PHONE_RE = re.compile(r"^\+?\d{10,15}$")
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,63}$")
_DIGITS_ONLY_RE = re.compile(r"^\d{1,6}$")
_DANGEROUS_URI_PREFIXES = ("javascript:", "data:", "vbscript:")
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _clean_text(value: Any, *, field_label: str, min_len: int = 1, max_len: int = 500) -> str:
    """Normalizes whitespace, strips dangerous control chars, and enforces length limits."""
    if not isinstance(value, str):
        raise ValueError(f"Поле «{field_label}» должно быть строкой")
    cleaned = _CONTROL_CHARS_RE.sub("", value).strip()
    if "<script" in cleaned.lower():
        raise ValueError(f"Поле «{field_label}» содержит недопустимые теги")
    if len(cleaned) < min_len:
        raise ValueError(f"Поле «{field_label}» не может быть пустым")
    if len(cleaned) > max_len:
        raise ValueError(f"Поле «{field_label}» не должно превышать {max_len} символов (сейчас {len(cleaned)})")
    return cleaned


def _validate_display_phone(value: Any, field_label: str = "Телефон (для отображения)") -> str:
    """Validates human-readable phone format with 10-15 digits and max 25 chars."""
    cleaned = _clean_text(value, field_label=field_label, min_len=7, max_len=25)
    if not _PHONE_CHARS_RE.match(cleaned):
        raise ValueError(f"Поле «{field_label}» может содержать только цифры, +, пробелы, скобки и дефисы")
    digits = re.sub(r"\D", "", cleaned)
    if not (10 <= len(digits) <= 15):
        raise ValueError(f"Поле «{field_label}» должно содержать от 10 до 15 цифр (сейчас {len(digits)})")
    return cleaned


def _validate_clean_phone(value: Any, field_label: str = "Телефон (для ссылки tel:)") -> str:
    """Validates E.164-like phone string used in tel: links."""
    cleaned = _clean_text(value, field_label=field_label, min_len=10, max_len=16)
    # Remove accidental spaces/hyphens only if caller didn't add letters, then strictly check
    normalized = re.sub(r"[\s()-]", "", cleaned)
    if not _CLEAN_PHONE_RE.match(normalized):
        raise ValueError(
            f"Поле «{field_label}» должно быть в формате +74232000000 (от 10 до 15 цифр без букв и лишних символов)"
        )
    return normalized


def _validate_external_url(value: Any, field_label: str) -> str:
    """Validates safe http(s) URLs for messenger/external links."""
    cleaned = _clean_text(value, field_label=field_label, min_len=8, max_len=250)
    lower = cleaned.lower()
    if lower.startswith(_DANGEROUS_URI_PREFIXES):
        raise ValueError(f"Поле «{field_label}» содержит небезопасную схему ссылки")
    if not (lower.startswith("https://") or lower.startswith("http://")):
        raise ValueError(f"Поле «{field_label}» должно начинаться с https:// или http://")
    return cleaned


def _validate_media_path(value: Any, field_label: str) -> str:
    """Validates relative site media path (/images/..., /uploads/...) or safe https URL."""
    cleaned = _clean_text(value, field_label=field_label, min_len=2, max_len=300)
    lower = cleaned.lower()
    if lower.startswith(_DANGEROUS_URI_PREFIXES) or ".." in cleaned:
        raise ValueError(f"Поле «{field_label}» содержит недопустимый путь")
    if not (cleaned.startswith("/") or lower.startswith("https://") or lower.startswith("http://")):
        raise ValueError(f"Поле «{field_label}» должно начинаться с / (например /images/... или /uploads/...) или https://")
    return cleaned


# ==========================================
# AUTH SCHEMAS
# ==========================================
class LoginRequest(BaseModel):
    """Admin login request credentials."""
    username: str = Field(..., min_length=3, max_length=64, description="Username")
    password: str = Field(..., min_length=4, max_length=128, description="Password")


class TokenResponse(BaseModel):
    """Bearer token response upon successful authentication."""
    access_token: str
    token_type: str = "bearer"
    username: str


class AdminUserOut(BaseModel):
    """Public representation of an admin user."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime


# ==========================================
# LEAD SCHEMAS
# ==========================================
class LeadCreate(BaseModel):
    """
    Public lead submission schema.
    Includes anti-spam honeypot field.
    """
    name: Optional[str] = Field(None, max_length=128, description="Client name")
    phone: str = Field(..., min_length=7, max_length=25, description="Contact phone number")
    source: Optional[str] = Field("general", max_length=64, description="Source form identifier")
    company_website: Optional[str] = Field(None, max_length=256, description="Honeypot trap: must remain empty")

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = _CONTROL_CHARS_RE.sub("", v).strip()
        return cleaned or None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = v.strip()
        if not _PHONE_CHARS_RE.match(clean):
            raise ValueError("Недопустимые символы в номере телефона")
        digits = re.sub(r"\D", "", clean)
        if not (10 <= len(digits) <= 15):
            raise ValueError("Номер телефона должен содержать от 10 до 15 цифр")
        return clean


class LeadUpdate(BaseModel):
    """Admin schema for updating lead status and notes."""
    status: Optional[LeadStatus] = None
    notes: Optional[str] = Field(None, max_length=2000, description="Internal admin notes")


class LeadOut(BaseModel):
    """Lead response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Optional[str]
    phone: str
    status: LeadStatus
    source: str
    notes: Optional[str]
    ip_address: Optional[str] = None
    created_at: datetime


class LeadListResponse(BaseModel):
    """Paginated lead listing with summary metrics."""
    total: int
    new_count: int
    processed_count: int
    leads: List[LeadOut]


# ==========================================
# SECTION-SPECIFIC CONTENT SCHEMAS
# ==========================================
class _StrictContentBase(BaseModel):
    model_config = ConfigDict(extra="ignore")


class HeaderContentData(_StrictContentBase):
    phone: str
    phone_clean: str
    working_hours: str
    tg_link: str
    wa_link: str
    cta_button: str = "ОСТАВИТЬ ЗАЯВКУ"
    logo_image: str = "/icons/logo-header-hd.png"

    @field_validator("phone")
    @classmethod
    def v_phone(cls, v: Any) -> str:
        return _validate_display_phone(v, "Номер телефона (для отображения)")

    @field_validator("phone_clean")
    @classmethod
    def v_phone_clean(cls, v: Any) -> str:
        return _validate_clean_phone(v, "Номер телефона (для ссылки tel:)")

    @field_validator("working_hours")
    @classmethod
    def v_hours(cls, v: Any) -> str:
        return _clean_text(v, field_label="Режим работы", max_len=60)

    @field_validator("tg_link")
    @classmethod
    def v_tg(cls, v: Any) -> str:
        return _validate_external_url(v, "Ссылка на Telegram")

    @field_validator("wa_link")
    @classmethod
    def v_wa(cls, v: Any) -> str:
        return _validate_external_url(v, "Ссылка на WhatsApp")

    @field_validator("cta_button")
    @classmethod
    def v_cta(cls, v: Any) -> str:
        return _clean_text(v, field_label="Текст на кнопке", max_len=40)

    @field_validator("logo_image")
    @classmethod
    def v_logo(cls, v: Any) -> str:
        return _validate_media_path(v, "Логотип в шапке")


class HeroContentData(_StrictContentBase):
    title: str
    description: str
    features: List[str] = Field(..., min_length=1, max_length=5)
    subtext: str
    cta_button: str
    bg_video: str = "/videos/hero-bg.mp4"
    bg_poster: str = "/images/hero-rack-bg.jpg"

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Заголовок", max_len=80)

    @field_validator("description")
    @classmethod
    def v_desc(cls, v: Any) -> str:
        return _clean_text(v, field_label="Описание", max_len=400)

    @field_validator("features")
    @classmethod
    def v_features(cls, v: List[str]) -> List[str]:
        return [_clean_text(item, field_label="Преимущество", max_len=80) for item in v]

    @field_validator("subtext")
    @classmethod
    def v_subtext(cls, v: Any) -> str:
        return _clean_text(v, field_label="Поясняющий текст", max_len=300)

    @field_validator("cta_button")
    @classmethod
    def v_cta(cls, v: Any) -> str:
        return _clean_text(v, field_label="Текст на кнопке", max_len=40)

    @field_validator("bg_video")
    @classmethod
    def v_bg_video(cls, v: Any) -> str:
        return _validate_media_path(v, "Фоновое видео (Hero)")

    @field_validator("bg_poster")
    @classmethod
    def v_bg_poster(cls, v: Any) -> str:
        return _validate_media_path(v, "Постер (стоп-кадр Hero)")


class ExpertiseItem(_StrictContentBase):
    title: str
    desc: str
    image: str = "/images/clean-icon-shield.png"

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Заголовок карточки", max_len=100)

    @field_validator("desc")
    @classmethod
    def v_desc(cls, v: Any) -> str:
        return _clean_text(v, field_label="Описание карточки", max_len=300)

    @field_validator("image")
    @classmethod
    def v_img(cls, v: Any) -> str:
        return _validate_media_path(v, "Иконка карточки")


class ExpertiseContentData(_StrictContentBase):
    title: str
    lead: str
    items: List[ExpertiseItem] = Field(..., min_length=1, max_length=6)

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Заголовок", max_len=120)

    @field_validator("lead")
    @classmethod
    def v_lead(cls, v: Any) -> str:
        return _clean_text(v, field_label="Вводный текст", max_len=300)


class ServiceItem(_StrictContentBase):
    name: str
    desc: str
    image: str = "/images/service-cctv.png"

    @field_validator("name")
    @classmethod
    def v_name(cls, v: Any) -> str:
        return _clean_text(v, field_label="Название услуги", max_len=80)

    @field_validator("desc")
    @classmethod
    def v_desc(cls, v: Any) -> str:
        return _clean_text(v, field_label="Описание услуги", max_len=300)

    @field_validator("image")
    @classmethod
    def v_img(cls, v: Any) -> str:
        return _validate_media_path(v, "Изображение услуги")


class ServicesContentData(_StrictContentBase):
    title: str
    subtitle: str
    banner_image: str = "/images/banner-3d-hardware.png"
    items: List[ServiceItem] = Field(..., min_length=1, max_length=12)

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Заголовок", max_len=120)

    @field_validator("subtitle")
    @classmethod
    def v_sub(cls, v: Any) -> str:
        return _clean_text(v, field_label="Подзаголовок", max_len=300)

    @field_validator("banner_image")
    @classmethod
    def v_banner_img(cls, v: Any) -> str:
        return _validate_media_path(v, "Изображение CTA-баннера")


class WhyUsItem(_StrictContentBase):
    val: str
    unit: str
    title: str
    desc: str

    @field_validator("val")
    @classmethod
    def v_val(cls, v: Any) -> str:
        cleaned = _clean_text(str(v), field_label="Числовой показатель", max_len=6)
        if not _DIGITS_ONLY_RE.match(cleaned):
            raise ValueError("Числовой показатель должен содержать только целое число (например: 12, 450, 98)")
        return cleaned

    @field_validator("unit")
    @classmethod
    def v_unit(cls, v: Any) -> str:
        return _clean_text(v, field_label="Единица измерения", max_len=15)

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Заголовок метрики", max_len=80)

    @field_validator("desc")
    @classmethod
    def v_desc(cls, v: Any) -> str:
        return _clean_text(v, field_label="Описание метрики", max_len=150)


class WhyUsTickerPhotos(_StrictContentBase):
    worker_yellow: str = "/images/section03-worker-yellow.png"
    cables: str = "/images/section03-cables.png"
    worker_helmet: str = "/images/section03-worker-helmet.png"

    @field_validator("worker_yellow", "cables", "worker_helmet")
    @classmethod
    def v_photo(cls, v: Any) -> str:
        return _validate_media_path(v, "Фото в бегущей строке")


class WhyUsContentData(_StrictContentBase):
    items: List[WhyUsItem] = Field(..., min_length=1, max_length=6)
    ticker_photos: WhyUsTickerPhotos = Field(default_factory=WhyUsTickerPhotos)


class StepItem(_StrictContentBase):
    step: str
    name: str
    desc: str

    @field_validator("step")
    @classmethod
    def v_step(cls, v: Any) -> str:
        return _clean_text(v, field_label="Номер шага", max_len=10)

    @field_validator("name")
    @classmethod
    def v_name(cls, v: Any) -> str:
        return _clean_text(v, field_label="Название этапа", max_len=80)

    @field_validator("desc")
    @classmethod
    def v_desc(cls, v: Any) -> str:
        return _clean_text(v, field_label="Описание этапа", max_len=400)


class StepsContentData(_StrictContentBase):
    title: str
    illustration_image: str = "/images/section04-installation-3d.png"
    items: List[StepItem] = Field(..., min_length=1, max_length=10)

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Заголовок", max_len=120)

    @field_validator("illustration_image")
    @classmethod
    def v_ill(cls, v: Any) -> str:
        return _validate_media_path(v, "3D-иллюстрация этапов")


class SectorItem(_StrictContentBase):
    title: str
    desc: str
    image: str
    icon: str = "/images/sector-icon-home.png"

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Название отрасли", max_len=120)

    @field_validator("desc")
    @classmethod
    def v_desc(cls, v: Any) -> str:
        return _clean_text(v, field_label="Описание отрасли", max_len=400)

    @field_validator("image", "icon")
    @classmethod
    def v_img(cls, v: Any) -> str:
        return _validate_media_path(v, "Медиафайл отрасли")


class SectorsContentData(_StrictContentBase):
    title: str
    items: List[SectorItem] = Field(..., min_length=1, max_length=8)
    partner_logos: List[str] = Field(
        default_factory=lambda: [
            "/images/logos/logo-fssp.png",
            "/images/logos/logo-sber.png",
            "/images/logos/logo-mchs.png",
            "/images/logos/logo-gazprom.png",
            "/images/logos/logo-tbank.png",
        ],
        min_length=1,
        max_length=10,
    )

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Заголовок", max_len=120)

    @field_validator("partner_logos")
    @classmethod
    def v_logos(cls, v: List[str]) -> List[str]:
        return [_validate_media_path(item, "Логотип партнёра") for item in v]


class CaseItem(_StrictContentBase):
    title: str
    scope: str
    image: str

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Название объекта", max_len=120)

    @field_validator("scope")
    @classmethod
    def v_scope(cls, v: Any) -> str:
        return _clean_text(v, field_label="Состав выполненных работ", max_len=500)

    @field_validator("image")
    @classmethod
    def v_img(cls, v: Any) -> str:
        return _validate_media_path(v, "Путь к изображению")


class CasesContentData(_StrictContentBase):
    title: str
    items: List[CaseItem] = Field(..., min_length=1, max_length=8)

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Заголовок", max_len=120)


class EngineerCtaContentData(_StrictContentBase):
    title: str
    subtitle: str
    engineer_photo: str
    success_bg_image: str = "/images/success-3d-bg.png"
    button_text: str

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Заголовок", max_len=120)

    @field_validator("subtitle")
    @classmethod
    def v_sub(cls, v: Any) -> str:
        return _clean_text(v, field_label="Подзаголовок", max_len=300)

    @field_validator("engineer_photo", "success_bg_image")
    @classmethod
    def v_photo(cls, v: Any) -> str:
        return _validate_media_path(v, "Изображение секции")

    @field_validator("button_text")
    @classmethod
    def v_btn(cls, v: Any) -> str:
        return _clean_text(v, field_label="Текст на кнопке", max_len=40)


class FaqItem(_StrictContentBase):
    q: str
    a: str

    @field_validator("q")
    @classmethod
    def v_q(cls, v: Any) -> str:
        return _clean_text(v, field_label="Вопрос", max_len=200)

    @field_validator("a")
    @classmethod
    def v_a(cls, v: Any) -> str:
        return _clean_text(v, field_label="Ответ", max_len=1500)


class FaqContentData(_StrictContentBase):
    title: str
    items: List[FaqItem] = Field(..., min_length=1, max_length=15)

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Заголовок", max_len=120)


class ContactsContentData(_StrictContentBase):
    title: str
    phone: str
    phone_clean: str
    email: str
    address: str
    hours: str
    inn: str
    tg_link: str
    wa_link: str
    footer_logo: str = "/images/footer-logo-mi.png"

    @field_validator("title")
    @classmethod
    def v_title(cls, v: Any) -> str:
        return _clean_text(v, field_label="Название компании", max_len=100)

    @field_validator("phone")
    @classmethod
    def v_phone(cls, v: Any) -> str:
        return _validate_display_phone(v, "Номер телефона (для отображения)")

    @field_validator("phone_clean")
    @classmethod
    def v_phone_clean(cls, v: Any) -> str:
        return _validate_clean_phone(v, "Номер телефона (для ссылки tel:)")

    @field_validator("email")
    @classmethod
    def v_email(cls, v: Any) -> str:
        cleaned = _clean_text(v, field_label="Email", max_len=100)
        if not _EMAIL_RE.match(cleaned):
            raise ValueError("Некорректный формат Email (пример: info@montazh-imperia.ru)")
        return cleaned

    @field_validator("address")
    @classmethod
    def v_addr(cls, v: Any) -> str:
        return _clean_text(v, field_label="Фактический адрес", max_len=200)

    @field_validator("hours")
    @classmethod
    def v_hours(cls, v: Any) -> str:
        return _clean_text(v, field_label="Часы работы", max_len=60)

    @field_validator("inn")
    @classmethod
    def v_inn(cls, v: Any) -> str:
        return _clean_text(v, field_label="Реквизиты (ИНН / ОГРН)", max_len=250)

    @field_validator("tg_link")
    @classmethod
    def v_tg(cls, v: Any) -> str:
        return _validate_external_url(v, "Ссылка на Telegram")

    @field_validator("wa_link")
    @classmethod
    def v_wa(cls, v: Any) -> str:
        return _validate_external_url(v, "Ссылка на WhatsApp")

    @field_validator("footer_logo")
    @classmethod
    def v_footer_logo(cls, v: Any) -> str:
        return _validate_media_path(v, "Логотип в подвале")


SECTION_SCHEMA_MAP: Dict[str, Type[_StrictContentBase]] = {
    "header": HeaderContentData,
    "hero": HeroContentData,
    "expertise": ExpertiseContentData,
    "services": ServicesContentData,
    "why_us": WhyUsContentData,
    "steps": StepsContentData,
    "sectors": SectorsContentData,
    "cases": CasesContentData,
    "engineer_cta": EngineerCtaContentData,
    "faq": FaqContentData,
    "contacts": ContactsContentData,
}


def validate_section_payload(section_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates section content dictionary against its typed Pydantic schema.
    Raises ValueError with readable localized message on validation failure.
    """
    schema_cls = SECTION_SCHEMA_MAP.get(section_key)
    if not schema_cls:
        return data
    validated = schema_cls.model_validate(data)
    return validated.model_dump()


# ==========================================
# CONTENT SCHEMAS
# ==========================================
class SiteContentOut(BaseModel):
    """Site content section output."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    section_key: str
    title: str
    order: int
    data: Dict[str, Any]
    updated_at: datetime


class SiteContentUpdate(BaseModel):
    """Admin schema for updating section content."""
    data: Dict[str, Any]


class AllContentResponse(BaseModel):
    """Full-site JSON bundle response for client-side hydration."""
    status: str = "success"
    sections: Dict[str, Any]
    fetched_at: str


# ==========================================
# UPLOAD SCHEMAS
# ==========================================
class UploadResponse(BaseModel):
    """Response schema for uploaded media asset."""
    filename: str
    url: str
    original_name: str
    size_bytes: int
    content_type: str


class MediaFileItem(BaseModel):
    """Server-stored media file entry enriched with slot-history metadata."""
    filename: str
    url: str
    original_name: Optional[str] = None
    size_bytes: int
    content_type: str
    section_key: Optional[str] = None
    field_path: Optional[str] = None
    is_active: bool = False
    last_used_at: Optional[datetime] = None
    created_at: datetime


class MediaListResponse(BaseModel):
    """Server media gallery response."""
    files: List[MediaFileItem]
