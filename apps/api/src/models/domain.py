"""Domain models for the Acme Trading Platform API."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class AccountType(StrEnum):
    cash = "cash"
    margin = "margin"


class AccountStatus(StrEnum):
    active = "active"
    suspended = "suspended"
    closed = "closed"


class Account(BaseModel):
    id: str
    holder_name: str
    account_type: AccountType
    buying_power: Decimal
    status: AccountStatus


class Position(BaseModel):
    account_id: str
    symbol: str
    quantity: int
    avg_cost: Decimal
    current_price: Decimal


class OrderSide(StrEnum):
    buy = "buy"
    sell = "sell"


class OrderType(StrEnum):
    market = "market"
    limit = "limit"


class OrderStatus(StrEnum):
    pending = "pending"
    filled = "filled"
    cancelled = "cancelled"
    rejected = "rejected"


class Order(BaseModel):
    id: str
    account_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int = Field(gt=0)
    limit_price: Decimal | None = None
    status: OrderStatus
    submitted_at: datetime
    filled_at: datetime | None = None


class CreateOrderRequest(BaseModel):
    account_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int = Field(gt=0)
    limit_price: Decimal | None = None


class Quote(BaseModel):
    symbol: str
    bid: Decimal
    ask: Decimal
    last: Decimal
    as_of: datetime


class MarketStatus(BaseModel):
    session: Literal["pre-market", "open", "after-hours", "closed"]
    as_of: datetime


class RiskCheckRequest(BaseModel):
    account_id: str
    symbol: str
    side: OrderSide
    quantity: int = Field(gt=0)


class RiskCheckResult(BaseModel):
    account_id: str
    symbol: str
    approved: bool
    margin_required: Decimal
    estimated_buying_power_after: Decimal
    checks_passed: list[str]
    checks_failed: list[str]
