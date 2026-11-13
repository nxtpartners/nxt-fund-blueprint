"""The closing sections: what to scope next, plain terms, public sources, and notes."""
from __future__ import annotations

from .. import constants as c
from ..data import Library
from ..enums import Depth
from ..models import Answers, Plan
from ..text import join_words
from .common import esc, lead_item, ledger_rows


def scope_next() -> str:
    rows = "".join(lead_item(title, text) for title, text in c.SCOPE_ITEMS)
    return f'<p class="sec-lede soft">{esc(c.SCOPE_LEDE)}</p><ul class="list">{rows}</ul>'


def plain_terms() -> str:
    return f'<dl class="terms">{ledger_rows(c.PLAIN_TERMS)}</dl>'


def public_sources(answers: Answers) -> str:
    if not answers.public_facts:
        return ""
    rows = "".join(
        f'<li><span>{esc(item[c.KEY_FACT])} '
        f'<a href="{esc(item[c.KEY_SOURCE], quote=True)}" rel="noopener noreferrer">Source</a></span></li>'
        for item in answers.public_facts
    )
    return (
        '<p class="sec-lede soft">Found on public websites and confirmed by you during this assessment.</p>'
        f'<ol class="notes">{rows}</ol>'
    )


def notes(answers: Answers, plan: Plan, library: Library) -> str:
    rows = [
        c.METHOD_NOTE,
        "The answers behind this report come from one person. Other people at your firm may see it differently.",
        "Money levels are broad estimates, not prices. Ask for a price on your first priority before committing.",
        "This is operational guidance generated with AI. It is not investment, legal, tax, or compliance advice, "
        "so have the right people review it before acting.",
        c.REGION_NOTES[answers.region],
    ]
    if answers.strategy == c.CREDIT_NOTE_STRATEGY:
        rows.append(c.CREDIT_NOTE)
    if plan.focus_missing:
        missing = join_words(plan.focus_missing)
        rows.append(f"You said {missing} matters to your thesis, but it was not assessed in this run.")
    quick = [work.id for work in answers.workstreams if work.depth != Depth.DEEP.value]
    if quick:
        areas = ", ".join(library.workstreams[item]["label"] for item in quick)
        rows.append("These work areas had fewer questions, so their rows rest on less detail: " + areas + ".")
    if plan.not_assessed:
        rows.append("Not assessed in this run: " + ", ".join(plan.not_assessed) + ".")
    if answers.assumed:
        rows.append("You skipped these, so a neutral assumption was used: " + ", ".join(answers.assumed) + ".")
    if answers.ai_assumed_areas:
        areas = ", ".join(answers.ai_assumed_areas)
        rows.append(f"You did not say which tasks use AI in {areas}, so its routine tasks were treated as using AI.")
    return f'<ol class="notes">{"".join(f"<li><span>{esc(row)}</span></li>" for row in rows)}</ol>'
