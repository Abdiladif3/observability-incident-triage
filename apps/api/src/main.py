import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.logging_config import configure_logging
from src.middleware.metrics import MetricsMiddleware
from src.middleware.request_context import RequestContextMiddleware
from src.routes import accounts, admin, market, orders

load_dotenv()
configure_logging()

app = FastAPI(
    title="Acme Trading Platform API",
    description="Instrumented backend API for the Observability & Incident Triage SE demo.",
    version="0.1.0",
)

# Middleware order (Starlette runs them in reverse order of registration):
#   RequestContextMiddleware  → innermost (request_id, structured access log)
#   MetricsMiddleware         → outermost (captures total request time)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(MetricsMiddleware)

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


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
