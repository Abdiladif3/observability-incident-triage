from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.logging_config import configure_logging
from src.middleware.metrics import MetricsMiddleware
from src.middleware.request_context import RequestContextMiddleware
from src.routes import health, pricing, risk, simulate

load_dotenv()
configure_logging()

app = FastAPI(
    title="Acme Trading Platform Downstream",
    description="Simulated downstream pricing and risk service with controllable failure modes.",
    version="0.1.0",
)

# Middleware order (Starlette runs them in reverse order of registration):
#   RequestContextMiddleware  → innermost
#   MetricsMiddleware         → outermost
app.add_middleware(RequestContextMiddleware)
app.add_middleware(MetricsMiddleware)

app.include_router(health.router)
app.include_router(pricing.router)
app.include_router(risk.router)
app.include_router(simulate.router)


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
