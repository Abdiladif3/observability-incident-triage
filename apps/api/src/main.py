import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.logging_config import configure_logging
from src.middleware.metrics import MetricsMiddleware
from src.middleware.request_context import RequestContextMiddleware
from src.routes import accounts, admin, market, orders
from src.services.downstream import DownstreamError, close_client

load_dotenv()
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_client()


app = FastAPI(
    title="Acme Trading Platform API",
    description="Instrumented backend API for the Observability & Incident Triage SE demo.",
    version="0.1.0",
    lifespan=lifespan,
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


@app.exception_handler(DownstreamError)
async def downstream_error_handler(request: Request, exc: DownstreamError) -> JSONResponse:
    payload: dict = {
        "error": exc.error,
        "message": exc.message,
    }
    if exc.recommended_action is not None:
        payload["recommended_action"] = exc.recommended_action
    if exc.downstream_status is not None:
        payload["downstream_status"] = exc.downstream_status
    return JSONResponse(status_code=exc.status_code, content=payload)
