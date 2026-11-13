"""Markup used by more than one section."""
from __future__ import annotations

import html
from typing import Dict, Iterable, List, Tuple

from .. import constants as c
from .. import tokens as t
from ..enums import Verdict
from ..models import Plan, ScoredActivity
from ..plot import mark_badge

esc = html.escape


def key_mark(verdict: Verdict) -> str:
    color = t.VERDICT_COLORS[verdict]
    fill = t.COLOR_SURFACE if verdict in t.VERDICT_HOLLOW else color
    return f'<i class="key-mark" style="color:{color};background:{fill}" aria-hidden="true"></i>'


def shape_mark(fits: bool) -> str:
    inner = '<circle cx="6" cy="6" r="4.6"/>' if fits else '<path d="M6 .8 11.2 6 6 11.2 .8 6Z"/>'
    return f'<svg class="shape-mark" viewBox="0 0 12 12" aria-hidden="true">{inner}</svg>'


def section(number: int, title: str, body: str, prefix: str = "") -> str:
    slug = f"{prefix}sec-{number}"
    return (
        f'<section class="sec" aria-labelledby="{slug}"><div class="sec-head"><span class="sec-no">{number:02d}</span>'
        f'<h2 id="{slug}">{esc(title)}</h2></div><div>{body}</div></section>'
    )


def priority_no(item: ScoredActivity, large: bool = False) -> str:
    """The priority number, drawn like its marker on the chart. Work that stays with people gets a plain number."""
    if item.verdict == Verdict.LEAVE:
        return "<span></span>"
    size = " badge-lg" if large else ""
    return (
        f'<span class="pno{size}"><span class="vh">{esc(c.PRIORITY_WORD)} {item.number}</span>'
        f"{mark_badge(item, item.number <= c.TOP_COUNT)}</span>"
    )


def hours_text(plan: Plan) -> str:
    if plan.hours_high is None:
        return f"At least {plan.hours_low}"
    return f"Up to {plan.hours_high}" if plan.hours_low == 0 else f"{plan.hours_low} to {plan.hours_high}"


def plural(count: int, word: str) -> str:
    if count == 1:
        return f"{count} {word}"
    return f"{count} {word[:-1]}ies" if word.endswith("y") and word[-2:-1] not in "aeiou" else f"{count} {word}s"


def ledger_rows(rows: Iterable[Tuple[str, str]]) -> str:
    return "".join(f"<div><dt>{esc(key)}</dt><dd>{esc(value)}</dd></div>" for key, value in rows)


def lead_item(title: str, text: str) -> str:
    return f'<li><span class="lead">{esc(title)}.</span> {esc(text)}</li>'


def by_workstream(items: List[ScoredActivity]) -> Dict[str, List[ScoredActivity]]:
    groups: Dict[str, List[ScoredActivity]] = {}
    for item in items:
        groups.setdefault(item.workstream_label, []).append(item)
    return groups
