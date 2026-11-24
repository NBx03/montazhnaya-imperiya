"""
Main FastAPI Application Entrypoint.

Configures:
- Structured logging (systemd/journalctl compatible).
- Application lifespan events.
- Request payload size limiter middleware (DoS protection).
- CORS middleware with strict allowed origins.
- Rate-limiting exception handlers.
- Static media and admin SPA delivery.
"""

from contextlib import asynccontextmanager
import logging
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import Base, engine, init_db
from app.limiter import custom_rate_limit_handler, limiter
from app.routers import auth, content, leads, upload

# ==========================================
# STRUCTURED LOGGING SETUP
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("montazh.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Ensures runtime directories and database tables/indexes exist on startup.
    """
    logger.info("Инициализация приложения (окружение: %s)...", settings.ENVIRONMENT)
    settings.ensure_directories()
    await init_db()
    logger.info("Бэкенд успешно запущен и готов к обработке входящих запросов.")
    yield
    logger.info("Остановка бэкенда...")


app = FastAPI(
    title="Монтажная Империя API",
    description="Бэкенд и панель управления для монтажной компании (FastAPI + SQLite WAL)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
)

# SlowAPI Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)


# Request body size limiter middleware (DoS mitigation)
@app.middleware("http")
async def limit_request_payload_size(request: Request, call_next):
    """
    Rejects requests whose Content-Length exceeds safe limits:
    - 16 MB for admin media upload.
    - 1 MB for all other endpoints (JSON forms, auth).
    """
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            length = int(content_length)
            is_upload = request.url.path.startswith("/api/v1/admin/upload")
            max_limit = (settings.MAX_UPLOAD_SIZE_BYTES + 1024 * 1024) if is_upload else (1024 * 1024)

            if length > max_limit:
                return JSONResponse(
                    status_code=413,
                    content={
                        "status": "error",
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": "Тело запроса превышает допустимый размер сервера.",
                    },
                )
        except ValueError:
            pass

    return await call_next(request)


# CORS Middleware (using configurable origins from settings)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(leads.router)
app.include_router(upload.router)


# Healthcheck Endpoints
@app.get("/health")
@app.get("/api/v1/health")
async def health():
    return {
        "status": "ok",
        "service": "montazh-backend",
        "environment": settings.ENVIRONMENT,
    }


# Mount static directories
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")
app.mount("/admin", StaticFiles(directory=str(settings.STATIC_ADMIN_DIR), html=True), name="admin")
