"""How much a move could matter: its link to the fund KPI, the hours behind it, and its level among the firm's."""
from __future__ import annotations

import math
from typing import List, Tuple

from .. import constants as c
from ..data import Library
from ..enums import KpiClaim, Rhythm
from ..models import Activity, Answers, ScoredActivity, WorkstreamAnswers
from .facts import HUMAN_NATURES, told
from .levels import quadrant_for


def relevance_for(activity: Activity, work: WorkstreamAnswers, answers: Answers, library: Library) -> Tuple[int, str]:
    """Link to the fund KPI: the catalog's prior, or the path through a department measure, whichever is stronger.

    Every task has a link.
    """
    if answers.kpi == c.CUSTOM_KPI:
        link = answers.kpi_links.get(activity.id) or answers.kpi_links.get(activity.label) or activity.kpi_link
        return (c.KPI_LINK_RELEVANCE[link] if link else c.CUSTOM_DEFAULT_RELEVANCE), ""
    if activity.custom:
        return (c.KPI_LINK_RELEVANCE[activity.kpi_link] if activity.kpi_link else c.CUSTOM_DEFAULT_RELEVANCE), ""
    prior = activity.kpis.get(answers.kpi, 0)
    relevance, measure_label = prior, ""
    for measure in library.measures_for(work.id):
        if activity.id in measure["tasks"]:
            link = min(measure["links"].get(answers.kpi, 0), prior + 1)
            if link and link >= relevance:
                relevance, measure_label = link, "" if measure.get("same_as") == answers.kpi else measure["label"]
    if answers.kpi == c.SENIOR_KPI:
        relevance = min(relevance, max(c.SENIOR_LINK_CAP[who] for who in work.who))
    return relevance, measure_label


def task_value(activity: Activity, work: WorkstreamAnswers, activities: List[Activity], anchored: bool = True) -> float:
    """Hours times seniority, shared across the work area's tasks. Used for order, and never shown as a number."""
    active = [row for row in activities if row.nature not in HUMAN_NATURES]
    weight = lambda row: c.HEAVY_TASK_SHARE if row.id == work.heavy_task else 1.0
    share = weight(activity) / (sum(weight(row) for row in active) or 1.0)
    hours = c.HOURS_MIDPOINT[work.hours] * share
    rate = sum(c.WHO_RATE[who] for who in work.who) / len(work.who)
    value = math.log(1 + hours * rate) / math.log(1 + c.VALUE_CEILING)
    if anchored and work.rhythm == Rhythm.STEADY.value:
        value *= c.STEADY_VALUE_FACTOR
    return min(value, 1.0)


def measure_off_here(activity: Activity, work: WorkstreamAnswers, library: Library) -> str:
    for measure in library.measures_for(work.id):
        if measure["id"] in work.measures_off and activity.id in measure["tasks"]:
            return measure["label"]
    return ""


def estimate_impact(
    activity: Activity,
    work: WorkstreamAnswers,
    answers: Answers,
    area: str,
    relevance: int,
    value: float,
    off_target: str,
) -> float:
    link_share = (relevance + c.RELEVANCE_FLOOR) / (c.RELEVANCE_MAX + c.RELEVANCE_FLOOR)
    score = link_share * (c.EFFECT_VALUE_FLOOR + (1 - c.EFFECT_VALUE_FLOOR) * value)
    in_thesis = told(answers, "thesis") and work.id in c.THESIS_WORKSTREAMS.get(answers.thesis, ())
    if in_thesis or work.id in answers.thesis_focus:
        score += c.IMPACT_BOOST
    if any(area in c.STAGE_AREAS[stage] for stage in answers.fund_stage):
        score += c.IMPACT_BOOST
    if off_target:
        score += c.IMPACT_BOOST
    return round(c.IMPACT_MIN + (c.IMPACT_MAX - c.IMPACT_MIN) * min(score, 1.0), 1)


def relative_levels(items: List[ScoredActivity]) -> None:
    """High, Medium, and Low compare this firm's own moves.

    Work that does not itself move the number, such as pausing, stays Low.
    """
    for item in items:
        item.raw_impact = item.impact
    ranked = [item for item in items if c.RULES[item.rule]["claim"] != KpiClaim.NONE]
    key = lambda item: (
        c.RULES[item.rule]["claim"] != KpiClaim.PREPARES,
        item.off_measure,
        item.relevance,
        item.raw_impact,
        round(item.value, 3),
    )
    strongest = max((item.relevance for item in ranked), default=0)
    order = sorted((key(item) for item in ranked), reverse=True)
    tiers = c.RELATIVE_TIERS
    for item in items:
        if item not in ranked:
            level = tiers[-1]
        elif len(set(order)) == 1:
            level = tiers[1]
        else:
            level = tiers[min(order.index(key(item)) * len(tiers) // len(order), len(tiers) - 1)]
        prepares = c.RULES[item.rule]["claim"] == KpiClaim.PREPARES
        if (prepares or item.relevance == 0 or item.relevance < strongest) and level == tiers[0]:
            level = tiers[1]
        if item.relevance == 0 and strongest > 0:
            level = tiers[-1]
        item.impact = c.RELATIVE_IMPACT[level]
        item.quadrant = quadrant_for(item.weeks, item.impact)
        item.speed_band = next(index for index, band in enumerate(c.SPEED_BANDS) if band[2] == item.speed_label)
