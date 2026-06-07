"""Market data endpoints."""

from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter

from src.models.domain import MarketStatus, Quote
from src.services.downstream import fetch_quote

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/quote/{symbol}", response_model=Quote)
async def get_quote(symbol: str) -> Quote:
    data = await fetch_quote(symbol)
    return Quote(
        symbol=data["symbol"],
        bid=Decimal(data["bid"]),
        ask=Decimal(data["ask"]),
        last=Decimal(data["last"]),
        as_of=datetime.fromisoformat(data["as_of"]),
    )


@router.get("/status", response_model=MarketStatus)
def get_market_status() -> MarketStatus:
    return MarketStatus(session="open", as_of=datetime.now(UTC))
