"""The first page: the headline, what shaped the plan, and the firm at a glance."""
from __future__ import annotations

from typing import List, Tuple

from .. import constants as c
from ..data import Library
from ..enums import Quadrant, Verdict
from ..models import Answers, Plan
from ..planning.facts import told
from ..planning.levels import impact_level
from ..text import join_words, lower_first
from .common import esc, hours_text, ledger_rows, plural


def headline(plan: Plan, kpi: str) -> str:
    if not plan.top:
        return "Your answers point to work that should stay with your people"
    item = plan.top[0]
    label = lower_first(item.label)
    if item.ai_assumed and item.restricted_in_use:
        return f"Your first move is to settle how AI is used in {lower_first(item.workstream_label)}"
    if item.ai_assumed and item.verdict == Verdict.BUILD_ON:
        area = lower_first(item.workstream_label)
        return f"Your first move is to review how AI is used in {area}, starting with {label}"
    if item.restricted_in_use:
        return f"Your first move is to settle how AI is used for {label}"
    if item.quadrant == Quadrant.DEPRIORITIZE and not any(impact_level(row.impact) != "Low" for row in plan.plotted):
        return f"Nothing here ranks highly against {lower_first(kpi)}, so start with {label}"
    if item.rule in c.HEADLINE_RULES:
        return c.HEADLINE_RULES[item.rule].format(label=label)
    if item.ai_unknown:
        return f"Your first move is to check whether AI is already used for {label}, and if not, to add it"
    return c.HEADLINE_VERBS[item.verdict].format(label=label)


def standfirst(plan: Plan) -> str:
    """At most one sentence. How the moves were estimated belongs with the roadmap."""
    if not plan.plotted:
        return "The work you selected depends on judgment and relationships, so it stays with your people."
    return ""


def firm_line(answers: Answers, library: Library) -> str:
    bits = []
    if told(answers, "strategy"):
        bits.append(library.option_label("strategy", answers.strategy))
    if answers.aum:
        bits.append(f"{library.option_label('aum', answers.aum)} AUM")
    if told(answers, "team"):
        bits.append(f"{library.option_label('team', answers.team)} people")
    if answers.fund_stage and told(answers, "fund_stage"):
        stages = [library.option_label("fund_stage", stage) for stage in answers.fund_stage]
        bits.append(f"{join_words(stages)} now")
    return " · ".join(bits)


def glance_line(plan: Plan) -> str:
    quick = sum(1 for item in plan.plotted if item.quadrant == Quadrant.QUICK_WINS)
    stops = sum(1 for item in plan.plotted if item.verdict == Verdict.REMOVE)
    glance = []
    if plan.hours_known:
        glance.append(f"{hours_text(plan)} hours a month reported")
    if plan.plotted:
        glance += [plural(len(plan.plotted), "move"), f"{quick} at Medium effect or above within 60 days"]
    if stops:
        glance.append(f"{stops} to test stopping")
    if plan.people:
        glance.append(f"{len(plan.people)} {'stays' if len(plan.people) == 1 else 'stay'} with your people")
    return " · ".join(glance)


def opening_rows(answers: Answers, plan: Plan, library: Library, kpi: str) -> List[Tuple[str, str]]:
    thesis_answer = told(answers, "thesis") and not answers.thesis_focus
    thesis = answers.thesis_summary or (library.option_label("thesis", answers.thesis) if thesis_answer else "")
    return [
        ("Prepared for", answers.firm_name),
        ("Firm", firm_line(answers, library)),
        ("Thesis", thesis),
        ("Priority", library.option_label("pressure", answers.pressure) if told(answers, "pressure") else ""),
        ("Measured against", f"{kpi} ({answers.kpi_value})" if answers.kpi_value else kpi),
        ("Assessed", ", ".join(library.workstreams[work.id]["label"] for work in answers.workstreams)),
        ("At a glance", glance_line(plan)),
    ]


def opening(answers: Answers, plan: Plan, library: Library, kpi: str) -> str:
    rows = opening_rows(answers, plan, library, kpi)
    ledger = ledger_rows((key, value) for key, value in rows if value)
    reading = "".join(f"<li>{esc(line)}</li>" for line in plan.reading + plan.changes)
    reading_html = ""
    if reading:
        reading_html = f'<p class="reading-title">{esc(c.READING_TITLE)}</p><ul class="reading">{reading}</ul>'
    start = f'<p class="start">{esc(plan.start_line)}</p>' if plan.start_line else ""
    first = standfirst(plan)
    first_html = f'<p class="standfirst">{esc(first)}</p>' if first else ""
    return (
        f'<div class="opening"><h1>{esc(headline(plan, kpi))}</h1>{first_html}{start}{reading_html}</div>'
        f'<dl class="ledger">{ledger}</dl><div class="spacer"></div>'
    )
