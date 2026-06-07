"""Pricing feed endpoint."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from src.data.store import quotes
from src.simulation import apply_simulation

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/quote/{symbol}")
async def get_quote(symbol: str) -> dict:
    await apply_simulation()

    symbol_upper = symbol.upper()
    quote_data = quotes.get(symbol_upper)
    if quote_data is None:
        raise HTTPException(status_code=404, detail=f"No pricing data for symbol '{symbol}'")

    return {
        "symbol": symbol_upper,
        "bid": str(quote_data["bid"]),
        "ask": str(quote_data["ask"]),
        "last": str(quote_data["last"]),
        "volume": quote_data["volume"],
        "as_of": datetime.now(UTC).isoformat(),
    }
