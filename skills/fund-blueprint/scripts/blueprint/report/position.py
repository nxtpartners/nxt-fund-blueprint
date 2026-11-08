"""Where the firm stands today: what they said, what already runs, and what to clear first."""
from __future__ import annotations

from typing import List, Tuple

from .. import constants as c
from ..data import Library
from ..enums import AiStage
from ..models import Answers, Plan
from ..planning.facts import told
from ..text import label_list
from .common import esc, lead_item, ledger_rows


def ai_rows(answers: Answers, library: Library) -> List[Tuple[str, str]]:
    rows = []
    tools = ", ".join(library.option_label("ai_tools", tool) for tool in answers.ai_tools)
    if tools:
        rows.append(("Tools", tools))
    if told(answers, "ai_adoption"):
        rows.append(("Weekly use", c.ADOPTION_PHRASES[answers.ai_adoption]))
    if told(answers, "ai_results"):
        rows.append(("Results so far", c.RESULTS_PHRASES[answers.ai_results]))
    return rows


def position_rows(answers: Answers, library: Library) -> List[Tuple[str, str]]:
    rows = []
    if told(answers, "ai_stage"):
        rows.append(("AI today", c.STAGE_PHRASES[answers.ai_stage]))
    if answers.ai_stage != AiStage.NONE.value:
        rows += ai_rows(answers, library)
    if told(answers, "policy"):
        rows.append(("AI policy", library.option_label("policy", answers.policy)))
    if told(answers, "systems"):
        rows.append((c.SYSTEMS_LABEL, library.option_label("systems", answers.systems)))
    if told(answers, "trust"):
        rows.append((c.TRUST_LABEL, label_list([library.option_label("trust", value) for value in answers.trust])))
    if told(answers, "capacity"):
        capacity = label_list([library.option_label("capacity", value) for value in answers.capacity])
        rows.append((c.CAPACITY_LABEL, capacity))
    if answers.budget:
        rows.append(("Budget", library.option_label("budget", answers.budget)))
    return rows


def position(answers: Answers, plan: Plan, library: Library) -> str:
    ledger = ledger_rows(position_rows(answers, library))
    existing = [item for item in plan.items if item.ai_note and not item.ai_unknown]
    existing_html = ""
    if existing:
        lines = "".join(lead_item(item.label, f"{item.ai_note}.") for item in existing)
        existing_html = f'<h3 class="subhead">AI already in this work</h3><ul class="list">{lines}</ul>'
    stuck = ""
    if plan.stuck:
        lines = "".join(lead_item(area, " ".join(rows)) for area, rows in plan.stuck)
        stuck = f'<h3 class="subhead">{esc(c.STUCK_TITLE)}</h3><ul class="list">{lines}</ul>'
    clear = ""
    if plan.foundations:
        lines = "".join(lead_item(title, text) for title, text, _ in plan.foundations)
        clear = f'<h3 class="subhead">Clear these first</h3><ol class="list">{lines}</ol>'
    if not (ledger or existing_html or stuck or clear):
        return ""
    ledger_html = f'<dl class="ledger">{ledger}</dl>' if ledger else ""
    return f"{ledger_html}{stuck}{existing_html}{clear}"
