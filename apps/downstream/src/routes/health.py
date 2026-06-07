"""Health endpoint."""

import os

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": os.getenv("SERVICE_NAME", "downstream"),
        "environment": os.getenv("ENV", "local"),
    }
