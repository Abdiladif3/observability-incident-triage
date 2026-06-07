"""Order submission and lookup endpoints."""

import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, HTTPException

from src.data.store import accounts, orders
from src.metrics import orders_submitted_total
from src.models.domain import CreateOrderRequest, Order, OrderStatus, OrderType

log = structlog.get_logger("api.orders")

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=Order, status_code=201)
def submit_order(payload: CreateOrderRequest) -> Order:
    if payload.account_id not in accounts:
        raise HTTPException(status_code=404, detail=f"Account '{payload.account_id}' not found")

    if payload.order_type == OrderType.limit and payload.limit_price is None:
        raise HTTPException(status_code=400, detail="limit_price is required for limit orders")

    order_id = f"ord-{uuid.uuid4().hex[:8]}"
    order = Order(
        id=order_id,
        account_id=payload.account_id,
        symbol=payload.symbol.upper(),
        side=payload.side,
        order_type=payload.order_type,
        quantity=payload.quantity,
        limit_price=payload.limit_price,
        status=OrderStatus.pending,
        submitted_at=datetime.now(UTC),
    )
    orders[order_id] = order

    orders_submitted_total.labels(side=payload.side.value, symbol=order.symbol).inc()

    log.info(
        "order.submitted",
        order_id=order_id,
        account_id=payload.account_id,
        symbol=order.symbol,
        side=payload.side.value,
        quantity=payload.quantity,
    )
    return order


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str) -> Order:
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    return order
