"""Market data endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from src.data.store import quotes
from src.models.domain import MarketStatus, Quote

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/quote/{symbol}", response_model=Quote)
def get_quote(symbol: str) -> Quote:
    quote = quotes.get(symbol.upper())
    if quote is None:
        raise HTTPException(status_code=404, detail=f"No quote available for symbol '{symbol}'")
    return quote


@router.get("/status", response_model=MarketStatus)
def get_market_status() -> MarketStatus:
    return MarketStatus(session="open", as_of=datetime.now(UTC))
