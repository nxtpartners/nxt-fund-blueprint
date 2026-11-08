"""The order of the moves, and what the first page says about where to start."""
from __future__ import annotations

from typing import Dict, List, Tuple

from .. import constants as c
from ..enums import Verdict
from ..models import Answers, ScoredActivity
from ..text import lower_first
from .facts import nobody_assigned, told


def priority(item: ScoredActivity, status: str = "", boost_named: bool = True) -> Tuple[float, int, str]:
    """Named work wins ties. Off-target numbers weigh effect more, and on-target numbers weigh hours more."""
    speed_bonus = 1.0 - min(item.weeks or c.WEEKS_AXIS_MAX, c.WEEKS_LATER) / c.WEEKS_LATER
    effect = ((item.raw_impact or item.impact) - c.IMPACT_MIN) / (c.IMPACT_MAX - c.IMPACT_MIN)
    weights = c.PRIORITY_WEIGHTS_BY_STATUS.get(status, (c.PRIORITY_WEIGHT_IMPACT, c.PRIORITY_WEIGHT_VALUE))
    weight_effect, weight_value = weights
    base = (weight_effect * effect + weight_value * item.value) * (1.0 + c.PRIORITY_SPEED_BONUS * speed_bonus)
    if item.relevance == 0 and not item.named:
        base *= c.NO_LINK_PRIORITY_FACTOR
    if item.named and boost_named:
        base *= c.NAMED_PRIORITY_FACTOR
    return (-round(base, 4), 0 if item.named else 1, item.label)


def add_comparison(
    plotted: List[ScoredActivity], kpi_text: str, status: str, money_ordered: bool = False, thesis_focus: List[str] = ()
) -> None:
    """Say why the first move leads over the second, using the same score that ranked them."""
    if len(plotted) < 2:
        return
    for earlier, later in zip(plotted[1:], plotted[2:]):
        explain_follow(earlier, later, thesis_focus)
    first, second = plotted[0], plotted[1]
    next_task = lower_first(second.label)
    if money_ordered and first.fits and not second.fits:
        line = c.LEADS_BUDGET.format(next_task=next_task)
    elif first.named:
        line = c.LEADS_NAMED
    elif priority(first, status)[0] == priority(second, status)[0]:
        line = c.LEADS_TIE.format(next_task=next_task)
    elif first.kpi_linked and first.relevance > second.relevance:
        line = c.LEADS_MORE_DIRECT.format(kpi=kpi_text, next_task=next_task)
    elif first.value > second.value:
        line = c.LEADS_MORE_HOURS.format(next_task=next_task)
    elif first.speed_label != second.speed_label and (first.weeks or 0) < (second.weeks or 0):
        line = c.LEADS_FASTER.format(next_task=next_task)
    else:
        return
    first.why_line = f"{first.why_line} {line}".strip()


def looks_same(one: ScoredActivity, other: ScoredActivity) -> bool:
    """Two moves whose cards show the same verdict, speed, effect, money, and link."""
    return (one.verdict, one.speed_label, one.impact, one.spend, one.fits, one.relevance) == (
        other.verdict, other.speed_label, other.impact, other.spend, other.fits, other.relevance
    )


def explain_follow(earlier: ScoredActivity, later: ScoredActivity, thesis_focus: List[str]) -> None:
    """When two moves in a row look the same, say on the second why the first comes ahead of it."""
    if earlier.named or later.named or not looks_same(earlier, later):
        return
    prev_task = lower_first(earlier.label)
    if earlier.workstream_id in thesis_focus and later.workstream_id not in thesis_focus:
        line = c.FOLLOWS_THESIS
    elif round(earlier.value, 3) > round(later.value, 3):
        line = c.FOLLOWS_HOURS
    elif (earlier.raw_impact or 0) > (later.raw_impact or 0):
        line = c.FOLLOWS_EFFECT
    elif (earlier.weeks or 0) < (later.weeks or 0):
        line = c.FOLLOWS_FASTER
    else:
        line = c.FOLLOWS_TIE
    later.why_line = f"{later.why_line} {line.format(prev_task=prev_task)}".strip()


def order_moves(
    items: List[ScoredActivity], answers: Answers, status: str
) -> Tuple[List[ScoredActivity], List[ScoredActivity], bool]:
    """Moves in order, the work that stays with people, and whether the named task had to be lifted."""
    money_ordered = answers.budget in c.BUDGET_REORDERS
    top_impact = c.RELATIVE_IMPACT[c.RELATIVE_TIERS[0]]
    plotted = sorted(
        (item for item in items if item.verdict != Verdict.LEAVE),
        key=lambda item: (
            money_ordered and not item.fits,
            -(top_impact if item.named else item.impact),
            not (item.off_measure or item.named),
            item.speed_band,
            item.workstream_id not in answers.thesis_focus,
            priority(item, status),
        ),
    )
    named = next((item for item in plotted if item.named), None)
    lifted = bool(named) and plotted.index(named) >= c.NAMED_TASK_FLOOR
    if lifted:
        plotted.remove(named)
        plotted.insert(c.NAMED_TASK_FLOOR - 1, named)
    leave = sorted((item for item in items if item.verdict == Verdict.LEAVE), key=lambda item: item.label)
    for number, item in enumerate(plotted + leave, start=1):
        item.number = number
    if answers.strategy == c.MULTI_STRATEGY and plotted and told(answers, "strategy"):
        plotted[0].first_step = c.MULTI_STRATEGY_STEP_LEAD + plotted[0].first_step
    return plotted, leave, lifted


def start_line(
    answers: Answers, plotted: List[ScoredActivity], status: str, off_target_tasks: Dict[str, str]
) -> Tuple[str, List[int]]:
    """The line on the first page, and which moves it starts, which also sets the 30-day list."""
    money_ordered = answers.budget in c.BUDGET_REORDERS
    if money_ordered and plotted and not any(item.fits for item in plotted):
        return c.START_NONE_FIT, [0]
    if len(plotted) < 2:
        return "", list(range(len(plotted)))
    if nobody_assigned(answers):
        return "With nobody assigned yet, start with move 1.", [0]
    if told(answers, "team") and answers.team == c.SMALL_TEAM:
        return "With under 15 people, start with move 1.", [0]
    if money_ordered and plotted[0].fits and not plotted[1].fits:
        return c.START_BUDGET, [0]
    if priority(plotted[0], status)[0] == priority(plotted[1], status)[0]:
        return c.TIE_START, [0, 1]
    if len(plotted) > 2 and third_acts_on_off_target(plotted, off_target_tasks, money_ordered):
        return c.START_OFF_TARGET.format(measure=lower_first(off_target_tasks[plotted[2].activity_id])), [0, 2]
    rest = " The rest can follow once those are running." if len(plotted) > 3 else ""
    return "Start with moves 1 and 2." + rest, [0, 1]


def third_acts_on_off_target(
    plotted: List[ScoredActivity], off_target_tasks: Dict[str, str], money_ordered: bool
) -> bool:
    """Move 3 is the first to touch a measure they said is off target."""
    first, second, third = plotted[0], plotted[1], plotted[2]
    earlier_miss = first.activity_id not in off_target_tasks and second.activity_id not in off_target_tasks
    third_counts = third.activity_id in off_target_tasks and third.kpi_linked
    return earlier_miss and third_counts and (third.fits or not money_ordered)
