"""Turns weeks and effect scores into the bands the report shows."""
from __future__ import annotations

from .. import constants as c
from ..enums import Horizon, Quadrant


def impact_level(impact: float) -> str:
    for limit, label in c.IMPACT_LEVELS:
        if impact < limit:
            return label
    return c.IMPACT_LEVELS[-1][1]


def effect_text(impact: float, kpi_text: str = "") -> str:
    return f"{impact_level(impact)} effect on {kpi_text}" if kpi_text else impact_level(impact)


def speed_label(weeks: float) -> str:
    for low, high, label in c.SPEED_BANDS:
        if low <= weeks < high:
            return label
    return c.SPEED_BANDS[-1][2]


def horizon_for(weeks: float) -> Horizon:
    if weeks < c.WEEKS_NOW:
        return Horizon.NOW
    if weeks < c.WEEKS_NEXT:
        return Horizon.NEXT
    return Horizon.LATER


def quadrant_for(weeks: float, impact: float) -> Quadrant:
    fast, high = weeks < c.QUADRANT_WEEKS, impact >= c.QUADRANT_IMPACT
    if fast:
        return Quadrant.QUICK_WINS if high else Quadrant.FILL_INS
    return Quadrant.STRATEGIC_BETS if high else Quadrant.DEPRIORITIZE
