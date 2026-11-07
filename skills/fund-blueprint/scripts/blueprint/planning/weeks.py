"""How long a move should take. Delays are planning assumptions, not measurements."""
from __future__ import annotations

from typing import Dict, List

from .. import constants as c
from ..enums import Capacity, TimeGoes, Verdict
from ..models import Activity, Answers, WorkstreamAnswers
from .facts import stage_for


def worst(table: Dict[str, float], values: List[str]) -> float:
    return max(table[value] for value in values)


def capacity_factor(answers: Answers) -> float:
    """Several ways to do the work: the fastest counts, and 'nobody' only when it stands alone."""
    usable = [value for value in answers.capacity if value != Capacity.NOBODY.value] or answers.capacity
    return min(c.WEEKS_CAPACITY[value] for value in usable)


def source_drag(work: WorkstreamAnswers) -> float:
    return worst(c.WEEKS_SOURCE, work.sources) - 1 + c.WEEKS_EXTRA_SOURCE * (len(work.sources) - 1)


def estimate_weeks(
    activity: Activity, verdict: Verdict, work: WorkstreamAnswers, answers: Answers, anchored: bool = True
) -> float:
    """Delays add up rather than multiply: several blockers can share one fix."""
    if verdict == Verdict.BUILD_ON:
        drag = (
            (c.WEEKS_POLICY[answers.policy] - 1)
            + (worst(c.WEEKS_TRUST, answers.trust) - 1)
            + (c.WEEKS_ADOPTION[answers.ai_adoption] - 1)
        )
        return round(c.BUILD_ON_WEEKS[stage_for(activity, work)] * max(1.0 + drag, c.WEEKS_MIN_FACTOR), 1)
    weeks = c.BASE_WEEKS[verdict]
    if verdict == Verdict.REMOVE:
        return weeks
    if verdict == Verdict.OPTIMIZE:
        return round(weeks * c.WEEKS_EFFORT[activity.effort], 1)
    drag = (
        source_drag(work)
        + (c.WEEKS_SYSTEMS[answers.systems] - 1)
        + (capacity_factor(answers) - 1)
        + (c.WEEKS_ERROR[work.error_cost] - 1)
    )
    if anchored and TimeGoes.WAIT_OUTSIDE.value in work.time_goes:
        drag += c.WEEKS_WAIT_OUTSIDE - 1
    if verdict in c.AI_VERDICTS:
        drag += (c.WEEKS_POLICY[answers.policy] - 1) + (worst(c.WEEKS_TRUST, answers.trust) - 1)
        drag += (
            (c.WEEKS_EXPERIENCE[answers.ai_stage] - 1)
            + (c.WEEKS_RESULTS[answers.ai_results] - 1)
            + (c.WEEKS_ADOPTION[answers.ai_adoption] - 1)
        )
    estimate = round(weeks * c.WEEKS_EFFORT[activity.effort] * max(1.0 + drag, c.WEEKS_MIN_FACTOR), 1)
    return min(estimate, c.WEEKS_AXIS_MAX)
