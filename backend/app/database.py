"""
Database Configuration & Engine Module.

Uses SQLAlchemy 2.0 async engine with aiosqlite.
Configures SQLite WAL mode (Write-Ahead Logging) to ensure zero write-lock contention
during concurrent read and write operations.
"""

from typing import AsyncGenerator
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    # SQLite performance & concurrency tuning
    connect_args={
        "check_same_thread": False,
        "timeout": settings.SQLITE_BUSY_TIMEOUT_MS / 1000.0,
    } if "sqlite" in settings.DATABASE_URL else {},
)

# Apply WAL mode, busy timeout, and foreign key enforcement on connect for SQLite
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute(f"PRAGMA busy_timeout={settings.SQLITE_BUSY_TIMEOUT_MS};")
        cursor.close()

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# SQLAlchemy 2.0 Modern Declarative Base
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 ORM models."""
    pass


async def init_db() -> None:
    """
    Initializes database schema and ensures critical performance indexes exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Ensure composite & ordering indexes exist
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_leads_status_created_at ON leads (status, created_at DESC);"))
        await conn.execute(text('CREATE INDEX IF NOT EXISTS ix_site_content_order ON site_content ("order");'))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency providing an async database session per request.
    Automatically handles commit rollback upon exceptions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
