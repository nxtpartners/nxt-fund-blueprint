"""The final report: a self-contained memo on a white background, in the NXT Partners identity."""
from __future__ import annotations

import datetime as dt

from . import constants as c
from .data import Library
from .models import Answers, Plan
from .report.common import esc, section
from .report.connections import connections
from .report.details import details_table, people
from .report.messages import render_email, render_summary  # noqa: F401
from .report.next_steps import next_30_days
from .report.notes import notes, plain_terms, public_sources, scope_next
from .report.opening import opening
from .report.position import position
from .report.priorities import priorities
from .report.recommendation import recommendation
from .report.roadmap import department_roadmap, roadmap
from .scoring import unlimited_view
from .styles import data_uri, stylesheet


def closing(logo: str) -> str:
    return (
        f'<section class="close" aria-labelledby="close-title"><img class="logo" src="{logo}" alt="{c.SITE_NAME}">'
        f'<h2 id="close-title">{esc(c.CLOSING_TITLE)}</h2><p>{esc(c.CLOSING_BODY)}</p>'
        f'<div class="actions"><a class="button" href="mailto:{c.CONTACT_EMAIL}?subject={c.CONTACT_SUBJECT}">'
        f'Email {c.CONTACT_EMAIL}</a><a href="{c.DEMO_URL}">{c.DEMO_TEXT}{c.DEMO_LABEL}</a></div></section>'
    )


def view_body(answers: Answers, plan: Plan, library: Library, prefix: str = "") -> str:
    """The whole report for one set of answers, from the headline to the notes."""
    view = library.kpi_view(answers.kpi, answers.kpi_name)
    kpi = view["label"]
    registry = [
        ("Where you stand", position(answers, plan, library)),
        ("Recommendation", recommendation(plan)),
        ("What could move this number soonest", priorities(plan, kpi, view)),
        ("Your next 30 days", next_30_days(plan, answers, library)),
        ("How this work connects", connections(plan, kpi)),
        ("Roadmap", roadmap(plan)),
        ("Roadmap by department", department_roadmap(plan)),
        (c.SCOPE_TITLE, scope_next() if plan.plotted else ""),
        ("Activity by activity", details_table(plan, kpi)),
        ("Leave with your people", people(plan)),
        ("In plain terms", plain_terms()),
        ("Public sources", public_sources(answers)),
        ("Notes", notes(answers, plan, library)),
    ]
    numbered = [(title, content) for title, content in registry if content]
    sections = "".join(
        section(number, title, content, prefix) for number, (title, content) in enumerate(numbered, start=1)
    )
    return opening(answers, plan, library, kpi) + sections


def budget_views(answers: Answers, plan: Plan, library: Library) -> str:
    """Two tabs when the budget changes something, and one plain view when it does not.

    No script, so they work wherever the file opens.
    """
    if not any(not item.fits for item in plan.plotted):
        return view_body(answers, plan, library)
    open_answers, open_plan = unlimited_view(library, answers)
    return (
        f'<div class="views" role="group" aria-label="{esc(c.VIEW_GROUP_LABEL)}">'
        '<input class="view-radio" type="radio" name="view" id="view-budget" checked>'
        f'<label class="view-tab" for="view-budget">{esc(c.VIEW_TAB_BUDGET)}</label>'
        '<input class="view-radio" type="radio" name="view" id="view-open">'
        f'<label class="view-tab" for="view-open">{esc(c.VIEW_TAB_OPEN)}</label>'
        f'<div class="view view-budget"><p class="view-print note">{esc(c.VIEW_PRINT_BUDGET)}</p>'
        f'{view_body(answers, plan, library, "budget-")}</div>'
        f'<div class="view view-open"><p class="view-print note">{esc(c.VIEW_PRINT_OPEN)}</p>'
        f'<p class="view-note note">{esc(c.VIEW_NOTE_OPEN)}</p>'
        f'{view_body(open_answers, open_plan, library, "open-")}</div>'
        "</div>"
    )


def render_blueprint(answers: Answers, plan: Plan, library: Library, today: dt.date) -> str:
    logo = data_uri(c.LOGO_PATH, "image/png")
    body = budget_views(answers, plan, library) + closing(logo)
    page_title = f"{c.REPORT_NAME}: {answers.firm_name}" if answers.firm_name else f"{c.REPORT_NAME} by {c.SITE_NAME}"
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{esc(page_title)}</title><meta name="generator" content="Fund Blueprint {c.VERSION}">'
        f'<style>{stylesheet()}</style></head><body><div class="page">'
        f'<header class="letterhead"><img class="logo" src="{logo}" alt="{c.SITE_NAME}">'
        f'<p>{esc(c.REPORT_NAME)}<br>{today.day} {today.strftime("%B %Y")}</p></header><main>{body}</main>'
        f"<footer>Created by {esc(c.SITE_NAME)} · {c.CONTACT_EMAIL}</footer></div>"
        "<script>addEventListener('beforeprint',function(){document.querySelectorAll('details').forEach("
        "function(d){d.open=true})})</script></body></html>"
    )
