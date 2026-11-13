"""The first 30 days: the actions from this plan, each with a suggested owner."""
from __future__ import annotations

from .. import constants as c
from ..data import Library
from ..models import Answers, Plan
from ..planning.facts import told
from ..text import lower_first
from .common import esc


def foundation_owner(action: str, data_owner: str) -> str:
    """Data work goes to the first move's owner, written-down know-how to whoever does the work."""
    if action.startswith(c.DATA_ACTION_START):
        return data_owner
    if action.startswith(c.ONE_PERSON_ACTION_START):
        return c.ONE_PERSON_OWNER
    return c.FIRM_WIDE_OWNER


def next_30_days(plan: Plan, answers: Answers, library: Library) -> str:
    data_owner = plan.top[0].owner_role if plan.top else c.FIRM_WIDE_OWNER
    rows = [("", action, foundation_owner(action, data_owner)) for _, _, action in plan.foundations[: c.NEXT_30_MAX_FOUNDATIONS]]
    if not told(answers, "kpi_status"):
        rows.append(("", library.kpi_view(answers.kpi, answers.kpi_name)["baseline"], c.FIRM_WIDE_OWNER))
    rows += [("", action, owner) for action, owner in plan.measure_actions[: c.MEASURE_ACTIONS_MAX]]
    if told(answers, "team") and answers.team == c.LARGE_TEAM:
        rows.append(("", c.TEAM_REVIEW_ACTION, c.FIRM_WIDE_OWNER))
    unknown_areas = list(dict.fromkeys(item.workstream_label for item in plan.items if item.ai_unknown))
    rows += [("", c.AI_UNKNOWN_ACTION.format(area=lower_first(area)), c.FIRM_WIDE_OWNER) for area in unknown_areas]
    started = [plan.plotted[index] for index in plan.start_moves] or plan.top[:1]
    named = [item for item in plan.plotted if item.named and item not in started]
    for item in started + named:
        rows.append((item.label, item.first_step, item.owner_role))
    by_opening = {action.split(". ")[0].lower(): (task, action, owner) for task, action, owner in reversed(rows)}
    rows = list(by_opening.values())[::-1]
    lines = "".join(
        f'<li><span class="num">{index}</span>'
        f'<span>{f"<span class=lead>{esc(task)}.</span> " if task else ""}{esc(action)}</span>'
        f'<span class="owner">{esc(owner)}</span></li>'
        for index, (task, action, owner) in enumerate(rows, start=1)
    )
    return (
        '<p class="sec-lede soft">First steps from this plan, with a suggested owner for each. '
        f'Adjust the owners to fit how your firm is organized.</p><ol class="actions-list">{lines}</ol>'
    )
