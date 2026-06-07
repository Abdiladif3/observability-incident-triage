"""Simulation-mode controls for the downstream service."""

from fastapi import APIRouter, Body

from src.data.store import set_mode, simulation_state

router = APIRouter(prefix="/simulate", tags=["simulate"])


@router.post("/latency")
def trigger_latency(latency_ms: int = Body(default=800, embed=True)) -> dict:
    return set_mode("latency", latency_ms=latency_ms)


@router.post("/errors")
def trigger_errors(error_rate: float = Body(default=0.5, embed=True)) -> dict:
    return set_mode("errors", error_rate=error_rate)


@router.post("/outage")
def trigger_outage() -> dict:
    return set_mode("outage")


@router.post("/recovery")
def trigger_recovery() -> dict:
    return set_mode("normal")


@router.get("/status")
def simulation_status() -> dict:
    return simulation_state
