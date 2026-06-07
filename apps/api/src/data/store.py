"""Seeded in-memory data store for the demo."""

from datetime import UTC, datetime
from decimal import Decimal

from src.models.domain import (
    Account,
    AccountStatus,
    AccountType,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
    Quote,
)


def _now() -> datetime:
    return datetime.now(UTC)


accounts: dict[str, Account] = {
    "acct-001": Account(
        id="acct-001",
        holder_name="Acme Capital LLC",
        account_type=AccountType.margin,
        buying_power=Decimal("250000.00"),
        status=AccountStatus.active,
    ),
    "acct-002": Account(
        id="acct-002",
        holder_name="Greenfield Trading Partners",
        account_type=AccountType.cash,
        buying_power=Decimal("50000.00"),
        status=AccountStatus.active,
    ),
}


positions_by_account: dict[str, list[Position]] = {
    "acct-001": [
        Position(
            account_id="acct-001",
            symbol="AAPL",
            quantity=500,
            avg_cost=Decimal("175.20"),
            current_price=Decimal("184.30"),
        ),
        Position(
            account_id="acct-001",
            symbol="MSFT",
            quantity=200,
            avg_cost=Decimal("310.50"),
            current_price=Decimal("338.10"),
        ),
    ],
    "acct-002": [
        Position(
            account_id="acct-002",
            symbol="TSLA",
            quantity=50,
            avg_cost=Decimal("220.00"),
            current_price=Decimal("234.50"),
        ),
    ],
}


orders: dict[str, Order] = {
    "ord-001": Order(
        id="ord-001",
        account_id="acct-001",
        symbol="AAPL",
        side=OrderSide.buy,
        order_type=OrderType.limit,
        quantity=100,
        limit_price=Decimal("180.00"),
        status=OrderStatus.filled,
        submitted_at=datetime(2026, 6, 5, 14, 30, tzinfo=UTC),
        filled_at=datetime(2026, 6, 5, 14, 30, 12, tzinfo=UTC),
    ),
}


quotes: dict[str, Quote] = {
    "AAPL": Quote(symbol="AAPL", bid=Decimal("184.25"), ask=Decimal("184.32"), last=Decimal("184.30"), as_of=_now()),
    "MSFT": Quote(symbol="MSFT", bid=Decimal("338.05"), ask=Decimal("338.18"), last=Decimal("338.10"), as_of=_now()),
    "TSLA": Quote(symbol="TSLA", bid=Decimal("234.40"), ask=Decimal("234.60"), last=Decimal("234.50"), as_of=_now()),
    "GOOGL": Quote(symbol="GOOGL", bid=Decimal("162.10"), ask=Decimal("162.25"), last=Decimal("162.18"), as_of=_now()),
    "NVDA": Quote(symbol="NVDA", bid=Decimal("875.40"), ask=Decimal("875.80"), last=Decimal("875.60"), as_of=_now()),
}
