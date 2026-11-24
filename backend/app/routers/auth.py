"""
Authentication API Router.

Provides admin login endpoint with brute-force rate-limiting and session check.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, get_current_admin, verify_password
from app.database import get_db
from app.limiter import get_client_ip, limiter
from app.models import AdminUser
from app.schemas import AdminUserOut, LoginRequest, TokenResponse

logger = logging.getLogger("montazh.auth")
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/10minutes")
async def login(
    request: Request,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticates administrator and returns JWT bearer token.
    Rate-limited to 5 attempts per 10 minutes per IP to prevent brute-force attacks.
    """
    client_ip = get_client_ip(request)
    username_clean = credentials.username.strip()

    stmt = select(AdminUser).where(AdminUser.username == username_clean)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(
            "Неудачная попытка входа: пользователь '%s', IP %s",
            username_clean,
            client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("Успешная авторизация: пользователь '%s', IP %s", user.username, client_ip)
    token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=token, username=user.username)


@router.get("/me", response_model=AdminUserOut)
async def get_me(current_admin: AdminUser = Depends(get_current_admin)):
    """Returns currently authenticated admin profile."""
    return current_admin
