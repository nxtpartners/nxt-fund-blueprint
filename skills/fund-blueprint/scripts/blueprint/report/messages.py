"""The plain-text outputs: the summary printed to the conversation, and the email draft."""
from __future__ import annotations

from .. import constants as c
from ..data import Library
from ..enums import Verdict
from ..models import Answers, Plan
from ..planning.facts import told
from ..planning.levels import effect_text
from .common import hours_text


def render_summary(answers: Answers, plan: Plan, library: Library) -> str:
    """Printed to the conversation, so the result survives any display failure."""
    kpi_label = library.kpi_view(answers.kpi, answers.kpi_name)["label"]
    lines = [
        f"KPI: {kpi_label}",
        f"Reported hours a month: {hours_text(plan) if plan.hours_known else 'not answered'}",
        "",
        f"| # | Activity | Id | Verdict | Speed, estimated | Effect, estimated | {c.MONEY_LABEL} |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in plan.items:
        speed = item.speed_label or "Not applicable"
        impact = effect_text(item.impact) if item.verdict != Verdict.LEAVE else "Not applicable"
        verdict = c.VERDICT_LABELS[item.verdict] + (c.AI_UNKNOWN_TABLE if item.ai_unknown else "")
        money = item.money_line or "Not applicable"
        cells = (item.number, item.label, item.activity_id, verdict, speed, impact, money)
        lines.append("| " + " | ".join(str(cell) for cell in cells) + " |")
    return "\n".join(lines)


def render_email(answers: Answers, plan: Plan, library: Library) -> str:
    """Closed answers and the firm's name if they gave it. No other typed text, so nothing confidential leaks in."""
    catalog_top = [item.label for item in plan.top if not item.custom]
    lines = [
        f"To: {c.CONTACT_EMAIL}",
        f"Subject: {c.CONTACT_SUBJECT_TEXT}",
        "",
        f"Hello {c.SITE_NAME},",
        "",
        "We completed the AI Strategy and Blueprint and would like to talk about implementation.",
        "",
        *([f"Firm: {answers.firm_name}"] if answers.firm_name else []),
        *([f"Strategy: {library.option_label('strategy', answers.strategy)}"] if told(answers, "strategy") else []),
        *([f"AUM: {library.option_label('aum', answers.aum)}"] if answers.aum else []),
        *([f"AI today: {library.option_label('ai_stage', answers.ai_stage)}"] if told(answers, "ai_stage") else []),
        *([f"Priority: {library.option_label('pressure', answers.pressure)}"] if told(answers, "pressure") else []),
        f"KPI: {library.kpi_view(answers.kpi, answers.kpi_name)['label']}",
        *(["Top priorities: " + "; ".join(catalog_top)] if catalog_top else []),
        "",
        "Thank you",
    ]
    return "\n".join(lines)
