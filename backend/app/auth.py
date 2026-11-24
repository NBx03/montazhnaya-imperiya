"""
Authentication & Authorization Module.

Uses native bcrypt for secure password hashing and PyJWT for signed bearer tokens.
Zero external deprecated dependencies (eliminates legacy passlib/crypt).
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import AdminUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain text password against bcrypt hashed password."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generates standard bcrypt hash with salt rounds=12."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates signed JWT token with expiration timestamp."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    secret = settings.SECRET_KEY.get_secret_value()
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_admin(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    """
    FastAPI dependency that validates JWT bearer token and retrieves AdminUser.
    Distinguishes expired tokens from invalid/tampered tokens for precise error feedback.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация в системе",
            headers={"WWW-Authenticate": "Bearer"},
        )

    secret = settings.SECRET_KEY.get_secret_value()
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен авторизации (отсутствует sub)",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия сессии истек. Пожалуйста, выполните вход повторно.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = select(AdminUser).where(AdminUser.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
