"""Scenario listing router."""
from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["scenarios"])


class ScenarioItem(BaseModel):
    id: str
    label: str
    description: str


class ScenariosResponse(BaseModel):
    scenarios: list[ScenarioItem]


_SCENARIOS = [
    ScenarioItem(
        id="baseline",
        label="Baseline — Current Market Conditions",
        description=(
            "The EV market continues its current trajectory with existing federal incentives, "
            "moderate infrastructure growth, stable gas prices, and OEM electrification "
            "roadmaps on track."
        ),
    ),
    ScenarioItem(
        id="ev_subsidies_rollback",
        label="Federal EV Subsidies Roll Back",
        description=(
            "Federal EV tax credits are eliminated or significantly reduced. "
            "Consumer price sensitivity rises and OEM EV programmes face revised financial models."
        ),
    ),
    ScenarioItem(
        id="gas_prices_spike",
        label="Gas Prices Spike 20 %",
        description=(
            "Gasoline prices rise sharply by 20 % or more. "
            "Consumer urgency to switch to lower running-cost vehicles intensifies, "
            "and hybrid/PHEV options see renewed mainstream interest."
        ),
    ),
]


@router.get("/scenarios", response_model=ScenariosResponse)
async def list_scenarios() -> ScenariosResponse:
    return ScenariosResponse(scenarios=_SCENARIOS)
