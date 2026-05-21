from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import analysis, health, history, jobs

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(analysis.router, tags=["analysis"])
api_router.include_router(jobs.router, tags=["jobs"])
api_router.include_router(history.router, tags=["history"])
