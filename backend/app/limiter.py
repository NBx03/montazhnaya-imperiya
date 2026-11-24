"""
Rate Limiting Infrastructure Module.

Provides proxy-aware client IP resolution (supporting Caddy, Nginx, Cloudflare)
and custom user-friendly error handlers for HTTP 429 Too Many Requests.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded


def get_client_ip(request: Request) -> str:
    """
    Extracts real client IP address respecting reverse proxies.
    Checks X-Forwarded-For, X-Real-IP, and falls back to socket host.
    """
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For can be a comma-separated list: client, proxy1, proxy2
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"


# Singleton proxy-aware limiter
limiter = Limiter(key_func=get_client_ip)


async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Returns uniform, localized JSON response when rate limit is exceeded.
    """
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "Слишком много запросов. Пожалуйста, подождите немного перед следующей попыткой.",
            "detail": str(exc.detail),
        },
        headers={"Retry-After": "60"},
    )
