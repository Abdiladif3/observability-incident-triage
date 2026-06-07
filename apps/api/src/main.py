import os

from dotenv import load_dotenv
from fastapi import FastAPI

from src.logging_config import configure_logging
from src.middleware.request_context import RequestContextMiddleware
from src.routes import accounts, admin, market, orders

load_dotenv()
configure_logging()

app = FastAPI(
    title="Acme Trading Platform API",
    description="Instrumented backend API for the Observability & Incident Triage SE demo.",
    version="0.1.0",
)

app.add_middleware(RequestContextMiddleware)

app.include_router(accounts.router)
app.include_router(orders.router)
app.include_router(market.router)
app.include_router(admin.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": os.getenv("SERVICE_NAME", "api"),
        "environment": os.getenv("ENV", "local"),
    }
