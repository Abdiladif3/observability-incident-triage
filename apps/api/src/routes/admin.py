"""Admin / operational endpoints."""

from decimal import Decimal

import structlog
from fastapi import APIRouter, HTTPException

from src.data.store import accounts
from src.models.domain import AccountStatus, RiskCheckRequest, RiskCheckResult
from src.services.downstream import fetch_quote

log = structlog.get_logger("api.admin")

router = APIRouter(prefix="/admin", tags=["admin"])

POSITION_SIZE_LIMIT = 10_000


@router.post("/risk-check", response_model=RiskCheckResult)
async def risk_check(payload: RiskCheckRequest) -> RiskCheckResult:
    account = accounts.get(payload.account_id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Account '{payload.account_id}' not found")

    quote_data = await fetch_quote(payload.symbol.upper())
    ask = Decimal(quote_data["ask"])

    margin_required = (ask * Decimal(payload.quantity)).quantize(Decimal("0.01"))
    buying_power_after = (account.buying_power - margin_required).quantize(Decimal("0.01"))

    checks_passed: list[str] = []
    checks_failed: list[str] = []

    if account.status == AccountStatus.active:
        checks_passed.append("account.active")
    else:
        checks_failed.append("account.active")

    if buying_power_after >= 0:
        checks_passed.append("buying_power.sufficient")
    else:
        checks_failed.append("buying_power.sufficient")

    if payload.quantity <= POSITION_SIZE_LIMIT:
        checks_passed.append("position_size.within_limit")
    else:
        checks_failed.append("position_size.within_limit")

    approved = len(checks_failed) == 0

    log.info(
        "admin.risk_check",
        account_id=payload.account_id,
        symbol=payload.symbol.upper(),
        approved=approved,
        margin_required=str(margin_required),
    )

    return RiskCheckResult(
        account_id=payload.account_id,
        symbol=payload.symbol.upper(),
        approved=approved,
        margin_required=margin_required,
        estimated_buying_power_after=buying_power_after,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
    )
