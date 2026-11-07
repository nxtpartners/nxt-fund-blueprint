"""Activity by activity: the open-a-row table, and the work that stays with people."""
from __future__ import annotations

from typing import List, Tuple

from .. import constants as c
from ..enums import Depth, Verdict
from ..models import Plan, ScoredActivity
from ..planning.levels import effect_text
from ..text import join_words, lower_first
from .common import by_workstream, esc, key_mark, ledger_rows

TABLE_HEAD = (
    '<div class="table-head" aria-hidden="true"><span></span><span>Activity</span><span>Recommendation</span>'
    "<span>Estimated time</span><span>Effect</span><span></span></div>"
)


def detail_fields(item: ScoredActivity, kpi: str, planned: bool) -> List[Tuple[str, str]]:
    fields = [("Why", item.reason), ("What changes for your team", item.solution)]
    if item.route:
        fields.append((c.ROUTE_LABEL, item.route))
    if planned:
        fields.append((c.MONEY_LABEL, item.money_line))
    fields += [("First step", item.first_step), ("Human check", item.check), ("Suggested owner", item.owner_role)]
    if item.relevance_note:
        fields.append((f"Link to {lower_first(kpi)}", item.relevance_note))
    if item.chain_line:
        fields.append(("Through", item.chain_line))
    if item.ai_note:
        fields.append(("AI here today", item.ai_note))
    if item.thesis_note:
        fields.append(("For your thesis", item.thesis_note))
    if item.named:
        fields.append(("Source", c.NAMED_TAG))
    elif item.custom:
        fields.append(("Source", c.CUSTOM_TAG))
    if item.depth == Depth.QUICK.value and planned:
        fields.append(("Depth", c.NOT_EXAMINED))
    return fields


def detail_row(item: ScoredActivity, kpi: str = "") -> str:
    planned = item.verdict != Verdict.LEAVE
    if planned:
        speed = (
            f'<span class="col">{esc(item.speed_label)}</span>'
            f'<span class="col">{esc(effect_text(item.impact))}</span>'
        )
    else:
        speed = '<span class="col"></span><span class="col"></span>'
    body = ledger_rows(detail_fields(item, kpi, planned))
    return (
        f'<details><summary><span class="mono soft">{item.number}</span><span class="name">{esc(item.label)}</span>'
        f'<span class="col">{key_mark(item.verdict)}{esc(c.VERDICT_LABELS[item.verdict])}</span>{speed}'
        '<span class="toggle" aria-hidden="true"></span></summary>'
        f'<div class="row-body"><dl>{body}</dl></div></details>'
    )


def details_table(plan: Plan, kpi: str) -> str:
    if not plan.plotted:
        return ""
    blocks = []
    for label, items in by_workstream(plan.plotted).items():
        evidence = f"<p>{esc(items[0].evidence)}</p>" if items[0].evidence else ""
        steps = plan.walkthroughs.get(label)
        walk = f'<p><span class="lead">{esc(c.WALKTHROUGH_TITLE)}:</span> {esc("; ".join(steps))}.</p>' if steps else ""
        rows = "".join(detail_row(item, kpi) for item in items)
        blocks.append(f'<div class="group"><h3>{esc(label)}</h3>{evidence}{walk}<div class="rows">{rows}</div></div>')
    rated_line = (
        f" Effect is rated only against {esc(lower_first(kpi))}, "
        "so a task can matter to the firm and still rate Low here."
    )
    return (
        '<p class="sec-lede soft">Open a row to see why, what changes for your team, the first step, '
        f'and who should own it.{rated_line}</p>{TABLE_HEAD}{"".join(blocks)}'
    )


def people(plan: Plan) -> str:
    elsewhere = ""
    if plan.people_elsewhere:
        items = join_words([lower_first(label) for label in plan.people_elsewhere])
        elsewhere = f'<p class="note">{esc(c.PEOPLE_ELSEWHERE.format(items=items))}</p>'
    if not plan.people and not elsewhere:
        return ""
    rows = ""
    if plan.people:
        body = "".join(detail_row(item) for item in plan.people)
        rows = f'<p class="sec-lede soft">{esc(c.STAYS_WITH_PEOPLE_LEDE)}</p><div class="rows">{body}</div>'
    return rows + elsewhere
