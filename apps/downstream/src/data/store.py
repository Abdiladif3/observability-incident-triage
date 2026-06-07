"""Seeded data + simulation state for the downstream service."""

from datetime import UTC, datetime
from decimal import Decimal

# "Source of truth" market data the upstream API depends on.
quotes: dict[str, dict] = {
    "AAPL": {"bid": Decimal("184.25"), "ask": Decimal("184.32"), "last": Decimal("184.30"), "volume": 38_221_000},
    "MSFT": {"bid": Decimal("338.05"), "ask": Decimal("338.18"), "last": Decimal("338.10"), "volume": 22_104_000},
    "TSLA": {"bid": Decimal("234.40"), "ask": Decimal("234.60"), "last": Decimal("234.50"), "volume": 91_002_000},
    "GOOGL": {"bid": Decimal("162.10"), "ask": Decimal("162.25"), "last": Decimal("162.18"), "volume": 18_550_000},
    "NVDA": {"bid": Decimal("875.40"), "ask": Decimal("875.80"), "last": Decimal("875.60"), "volume": 41_780_000},
}

# Per-account margin position held downstream.
account_margins: dict[str, dict] = {
    "acct-001": {"margin_used": Decimal("37000.00"), "margin_available": Decimal("213000.00")},
    "acct-002": {"margin_used": Decimal("8500.00"), "margin_available": Decimal("41500.00")},
}

# Simulation state. Controls how the downstream behaves until explicitly reset.
#   mode: normal | latency | errors | outage
simulation_state: dict = {
    "mode": "normal",
    "latency_ms": 800,
    "error_rate": 0.5,
    "updated_at": datetime.now(UTC).isoformat(),
}


def set_mode(mode: str, *, latency_ms: int | None = None, error_rate: float | None = None) -> dict:
    simulation_state["mode"] = mode
    simulation_state["updated_at"] = datetime.now(UTC).isoformat()
    if latency_ms is not None:
        simulation_state["latency_ms"] = latency_ms
    if error_rate is not None:
        simulation_state["error_rate"] = error_rate
    return simulation_state
