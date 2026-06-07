"""Account read endpoints."""

from decimal import Decimal

from fastapi import APIRouter, HTTPException

from src.data.store import accounts, orders, positions_by_account
from src.models.domain import Account, Order, Position
from src.services.downstream import fetch_quote

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/{account_id}", response_model=Account)
def get_account(account_id: str) -> Account:
    account = accounts.get(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Account '{account_id}' not found")
    return account


@router.get("/{account_id}/positions", response_model=list[Position])
async def get_positions(account_id: str) -> list[Position]:
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail=f"Account '{account_id}' not found")

    enriched: list[Position] = []
    # Sequential downstream calls by design: this is the call-graph fan-out that makes
    # latency incidents visible in the dashboards. Parallelizing with asyncio.gather()
    # would hide the cascade — the demo wants it visible.
    for position in positions_by_account.get(account_id, []):
        quote_data = await fetch_quote(position.symbol)
        enriched.append(
            Position(
                account_id=position.account_id,
                symbol=position.symbol,
                quantity=position.quantity,
                avg_cost=position.avg_cost,
                current_price=Decimal(quote_data["last"]),
            )
        )
    return enriched


@router.get("/{account_id}/orders", response_model=list[Order])
def get_account_orders(account_id: str) -> list[Order]:
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail=f"Account '{account_id}' not found")
    return [order for order in orders.values() if order.account_id == account_id]
