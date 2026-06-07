"""Apply the active simulation mode to an incoming downstream request."""

import asyncio
import random

from fastapi import HTTPException

from src.data.store import simulation_state


async def apply_simulation() -> None:
    mode = simulation_state["mode"]

    if mode == "latency":
        latency_ms = simulation_state["latency_ms"]
        await asyncio.sleep(latency_ms / 1000)
    elif mode == "errors":
        if random.random() < simulation_state["error_rate"]:
            raise HTTPException(status_code=503, detail="downstream temporarily unavailable")
    elif mode == "outage":
        raise HTTPException(status_code=503, detail="downstream is unavailable")
