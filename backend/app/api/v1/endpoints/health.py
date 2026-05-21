from __future__ import annotations

import httpx
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    ai_status = "local"
    if settings.inference_mode == "remote":
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{settings.ai_service_url}/health")
            ai_status = "ok" if response.is_success else "degraded"
        except httpx.HTTPError:
            ai_status = "unreachable"
    return {
        "status": "ok",
        "service": "ghostproof-api",
        "environment": settings.env,
        "inference_mode": settings.inference_mode,
        "ai_service": ai_status,
    }
