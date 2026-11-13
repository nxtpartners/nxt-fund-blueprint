"""The recommended moves, each with why it leads and its first step."""
from __future__ import annotations

from .. import constants as c
from ..models import Plan, ScoredActivity
from ..planning.levels import effect_text
from .common import esc, priority_no, shape_mark


def move_card(index: int, item: ScoredActivity, prefix: str = "") -> str:
    facts = [
        (c.FACT_APPROACH, esc(c.VERDICT_LABELS[item.verdict])),
        (c.FACT_TIME, esc(item.speed_label)),
        (c.FACT_EFFECT, esc(effect_text(item.impact))),
        (c.FACT_MONEY, f"{shape_mark(item.fits)} {esc(item.money_line)}"),
        (c.FACT_OWNER, esc(item.owner_role)),
        (c.FACT_LINK, esc(item.relevance_note)),
    ] + ([(c.FACT_AI, esc(c.AI_UNKNOWN_CARD))] if item.ai_unknown else [])
    thesis = f'<p><span class="lead">For your thesis.</span> {esc(item.thesis_note)}</p>' if item.thesis_note else ""
    why = f'<p><span class="lead">Why this one.</span> {esc(item.why_line)}</p>' if item.why_line else ""
    return (
        f'<li id="{c.PRIORITY_ANCHOR.format(prefix=prefix, number=item.number)}"><div class="head">{priority_no(item, large=True)}<h3>{esc(item.label)}</h3></div>'
        f'<div class="body"><p>{esc(item.solution)}</p>{why}'
        f'<p><span class="lead">First step.</span> {esc(item.first_step)}</p>{thesis}</div>'
        f'<dl class="facts">{"".join(f"<div><dt>{esc(key)}</dt><dd>{value}</dd></div>" for key, value in facts)}</dl></li>'
    )


def recommendation(plan: Plan, prefix: str = "") -> str:
    if not plan.top:
        return ""
    moves = "".join(move_card(index, item, prefix) for index, item in enumerate(plan.top, start=1))
    return (
        f'<p class="sec-lede soft">{esc(c.STRATEGY_LINE)} All times, effects, and money levels in this report '
        f'are planning estimates, not quotes.</p><ol class="moves">{moves}</ol>'
    )
