"""
SQLAlchemy 2.0 ORM Models for Montazh Imperiya.

Fully type-annotated with Mapped[...] and mapped_column(...) for static typing
compatibility with MyPy, Pyright, and modern IDEs.
"""

import enum
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, Enum, Index, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utc_now() -> datetime:
    """Returns timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class LeadStatus(str, enum.Enum):
    """Lifecycle status of a customer lead."""
    NEW = "new"
    PROCESSED = "processed"


class AdminUser(Base):
    """
    Administrator accounts allowed to access the /admin panel.
    """
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<AdminUser id={self.id} username='{self.username}'>"


class SiteContent(Base):
    """
    Landing page content sections stored as structured JSON.
    Allows granular text and media editing from the admin panel.
    """
    __tablename__ = "site_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    section_key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<SiteContent id={self.id} key='{self.section_key}' title='{self.title}'>"


class Lead(Base):
    """
    Customer inquiry submitted from landing page forms.
    """
    __tablename__ = "leads"
    __table_args__ = (
        Index("ix_leads_status_created_at", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    phone: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, native_enum=False, length=32),
        default=LeadStatus.NEW,
        index=True,
        nullable=False
    )
    source: Mapped[str] = mapped_column(String(64), default="general", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        index=True,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Lead id={self.id} phone='{self.phone}' status='{self.status.value}'>"


class MediaAsset(Base):
    """
    Tracks uploaded media files metadata and which landing slot they belong to,
    enabling quick slot-aware restoration without cluttering disk or config.
    """
    __tablename__ = "media_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    url: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    original_name: Mapped[str] = mapped_column(String(256), nullable=False)
    content_type: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    section_key: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    field_path: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        index=True,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<MediaAsset filename='{self.filename}' slot='{self.section_key}:{self.field_path}'>"
