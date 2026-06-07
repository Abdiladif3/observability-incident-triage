"""Risk and margin lookup endpoint."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from src.data.store import account_margins
from src.simulation import apply_simulation

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/account/{account_id}/margin")
async def get_account_margin(account_id: str) -> dict:
    await apply_simulation()

    margin = account_margins.get(account_id)
    if margin is None:
        raise HTTPException(status_code=404, detail=f"No margin record for account '{account_id}'")

    return {
        "account_id": account_id,
        "margin_used": str(margin["margin_used"]),
        "margin_available": str(margin["margin_available"]),
        "as_of": datetime.now(UTC).isoformat(),
    }
