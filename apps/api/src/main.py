import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app = FastAPI(
    title="Acme Trading Platform API",
    description="Instrumented backend API for the Observability & Incident Triage SE demo.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": os.getenv("SERVICE_NAME", "api"),
        "environment": os.getenv("ENV", "local"),
    }
