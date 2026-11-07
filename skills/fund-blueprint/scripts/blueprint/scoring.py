"""Deterministic scoring: the same answers always give the same plan.

The catalog supplies priors, and the firm's answers decide.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Dict, List, Optional, Tuple

from . import constants as c
from .data import Library
from .enums import Verdict
from .models import Answers, Plan, ScoredActivity
from .planning.effect import relative_levels
from .planning.evidence import strategy_words, stuck_lines
from .planning.facts import told, told_here
from .planning.foundations import foundations_for
from .planning.levers import what_would_change
from .planning.measures import measure_view, off_target_map
from .planning.ordering import add_comparison, order_moves, start_line
from .planning.reading import read_together
from .planning.tasks import score_activity, work_context
from .text import lower_first


def reported_hours(answers: Answers) -> Tuple[int, Optional[int], bool]:
    """Lowest and highest monthly hours reported, with no highest for an open-ended answer, and whether any were."""
    low, high, open_ended, known = 0, 0, False, False
    for work in answers.workstreams:
        if not told_here(work, answers, "hours"):
            continue
        known = True
        area_low, area_high = c.HOURS_RANGE[work.hours]
        low += area_low
        if area_high is None:
            open_ended = True
        else:
            high += area_high
    return low, None if open_ended else high, known


def walkthroughs_for(answers: Answers, library: Library) -> Dict[str, List[str]]:
    return {
        library.workstreams[work.id]["label"]: work.walkthrough_steps
        for work in answers.workstreams
        if work.walkthrough_steps
    }


def score_answers(library: Library, answers: Answers, with_levers: bool = True) -> Plan:
    kpi_text = lower_first(library.kpi_view(answers.kpi, answers.kpi_name)["label"])
    say = strategy_words(answers.strategy if told(answers, "strategy") else "")
    status = answers.kpi_status if told(answers, "kpi_status") else ""

    items: List[ScoredActivity] = []
    for work in answers.workstreams:
        context = work_context(library, answers, work, say, kpi_text)
        items += [score_activity(context, activity) for activity in context.activities]
    relative_levels([item for item in items if item.verdict != Verdict.LEAVE])
    plotted, leave, lifted = order_moves(items, answers, status)
    ordered = plotted + leave

    assessed = {work.id for work in answers.workstreams}
    kept_with_people = {item.activity_id for item in leave}
    measure_rows, measure_actions = measure_view(answers, library, say)
    add_comparison(plotted, kpi_text, status, answers.budget in c.BUDGET_REORDERS)
    start, start_moves = start_line(answers, plotted, status, off_target_map(answers, library, say))
    foundations = foundations_for(answers, library, plotted[0].label if plotted else "", ordered)
    hours_low, hours_high, hours_known = reported_hours(answers)
    rescore = lambda changed: score_answers(library, changed, with_levers=False)
    return Plan(
        ordered,
        [(say(title), say(text), say(action)) for title, text, action in foundations],
        hours_low,
        hours_high,
        hours_known,
        [row["label"] for row in library.catalog["workstreams"] if row["id"] not in assessed],
        reading=read_together(answers, ordered, library, kpi_text, lifted),
        start_line=start,
        start_moves=start_moves,
        changes=what_would_change(rescore, answers, ordered) if with_levers else [],
        measure_rows=measure_rows,
        measure_actions=measure_actions,
        focus_missing=[library.workstreams[item]["label"] for item in answers.thesis_focus if item not in assessed],
        walkthroughs=walkthroughs_for(answers, library),
        budget=answers.budget,
        people_elsewhere=[
            say(row.label) for row in library.activities.values()
            if row.nature.value in c.HUMAN_NATURE_VALUES and row.id not in kept_with_people
        ],
        stuck=[
            (library.workstreams[work.id]["label"], lines)
            for work in answers.workstreams
            for lines in [[say(line) for line in stuck_lines(work, answers, library)]]
            if lines
        ],
    )


def unlimited_view(library: Library, answers: Answers) -> Tuple[Answers, Plan]:
    """The same answers with no budget limit, for the report's second view."""
    open_answers = replace(answers, budget="")
    return open_answers, score_answers(library, open_answers)
