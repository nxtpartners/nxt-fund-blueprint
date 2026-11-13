"""How each team's own numbers link to the fund's number. Only rows that touch this plan."""
from __future__ import annotations

from typing import List

from .. import constants as c
from ..models import Plan
from ..text import join_words, lower_first
from .common import esc


def connections(plan: Plan, kpi: str) -> str:
    """How each team's own numbers link to the fund's number, and what they said about each."""
    linked = [row for row in plan.measure_rows if row[2] and row[4]]
    if not linked:
        return ""
    numbers = {item.activity_id: item.number for item in plan.plotted if item.kpi_linked}

    def moves(tasks: List[str]) -> str:
        return ", ".join(str(number) for number in sorted(numbers[task] for task in tasks if task in numbers)) or "None"
    rows = "".join(
        f'<tr><th scope="row">{esc(measure)}</th><td>{esc(c.LINK_LADDER[link])}</td>'
        f"<td>{esc(status)}</td><td>{esc(moves(tasks))}</td></tr>"
        for _, measure, link, status, tasks in linked
    )
    others = [row[1] for row in plan.measure_rows if not row[2]]
    tail = ""
    if others:
        names = join_words([lower_first(name) for name in others])
        tail = f'<p class="note">Also tracked, with only an indirect link to {esc(lower_first(kpi))}: {esc(names)}.</p>'
    return (
        f"<p class=\"sec-lede soft\">How each team's own number feeds {esc(lower_first(kpi))}. "
        "These links are planning assumptions, so ask each team whether they hold.</p>"
        '<table class="link-table"><thead><tr><th scope="col">Team\'s number</th><th scope="col">Link</th>'
        f'<th scope="col">Today</th><th scope="col">Priorities</th></tr></thead><tbody>{rows}</tbody></table>{tail}'
    )
