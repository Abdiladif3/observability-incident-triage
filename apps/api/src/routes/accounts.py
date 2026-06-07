"""Account read endpoints."""

from fastapi import APIRouter, HTTPException

from src.data.store import accounts, orders, positions_by_account
from src.models.domain import Account, Order, Position

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/{account_id}", response_model=Account)
def get_account(account_id: str) -> Account:
    account = accounts.get(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Account '{account_id}' not found")
    return account


@router.get("/{account_id}/positions", response_model=list[Position])
def get_positions(account_id: str) -> list[Position]:
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail=f"Account '{account_id}' not found")
    return positions_by_account.get(account_id, [])


@router.get("/{account_id}/orders", response_model=list[Order])
def get_account_orders(account_id: str) -> list[Order]:
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail=f"Account '{account_id}' not found")
    return [order for order in orders.values() if order.account_id == account_id]
