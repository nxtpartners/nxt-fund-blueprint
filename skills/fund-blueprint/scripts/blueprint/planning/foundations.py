"""What must come first, before any of the moves."""
from __future__ import annotations

from typing import List, Tuple

from .. import constants as c
from ..data import Library
from ..enums import ErrorCost, Policy, Verdict
from ..models import Answers, ScoredActivity
from ..text import join_words, lower_first
from .facts import firm_uses_ai, hardest_task_label, nobody_assigned, told, told_here

Foundation = Tuple[str, str, str]


def foundations_for(
    answers: Answers, library: Library, top_label: str, items: List[ScoredActivity]
) -> List[Foundation]:
    """What must come first. Connecting data matters only when a move adds software."""
    needs_software = any(item.verdict in c.TECH_VERDICTS for item in items)
    rows = foundation_rows(answers, library, top_label, items)
    return [row for row in rows if needs_software or row[0] != c.CONNECT_DATA_TITLE]


def one_person_rows(answers: Answers, library: Library) -> List[Foundation]:
    title, text, action = c.ONE_PERSON_FOUNDATION
    held = [work for work in answers.workstreams if work.depends == "no" and told_here(work, answers, "depends")]
    rows: List[Foundation] = []
    for work in held:
        area = lower_first(library.workstreams[work.id]["label"])
        label = hardest_task_label(work, answers, library)
        subject = lower_first(label) if label else area
        severe = work.error_cost == ErrorCost.SEVERE.value and told_here(work, answers, "error_cost")
        harm = c.ONE_PERSON_HARM if severe else ""
        heading = f"{title}: {area}" if len(held) > 1 else title
        rows.append((heading, text.format(subject=subject, harm=harm), action.format(subject=subject)))
    return rows


def shared_data_rows(library: Library, items: List[ScoredActivity]) -> List[Foundation]:
    shared = [
        item.label for item in items
        if item.activity_id
        and library.activities.get(item.activity_id)
        and library.activities[item.activity_id].shared_data
        and item.verdict != Verdict.LEAVE
    ]
    if len(shared) < 2:
        return []
    title, text, action = c.SHARED_DATA_FOUNDATION
    tasks = join_words([lower_first(label) for label in shared])
    return [(title, text.format(count=len(shared), tasks=tasks), action)]


def answer_keys(answers: Answers, uses_ai: bool) -> List[Tuple[str, str]]:
    """Which answers call for their own foundation, in the order they appear."""
    keys: List[Tuple[str, str]] = []
    if told(answers, "kpi_status"):
        keys.append(("kpi_status", answers.kpi_status))
    if uses_ai and told(answers, "ai_results"):
        keys.append(("ai_results", answers.ai_results))
    if uses_ai and told(answers, "ai_adoption"):
        keys.append(("ai_adoption", answers.ai_adoption))
    if not uses_ai and told(answers, "policy"):
        keys.append(("policy", answers.policy))
    if told(answers, "systems"):
        keys.append(("systems", answers.systems))
    restricted = answers.policy == Policy.RESTRICTED.value
    if told(answers, "trust") and not (restricted and not uses_ai):
        keys += [("trust", value) for value in answers.trust]
    return keys


def foundation_rows(
    answers: Answers, library: Library, top_label: str, items: List[ScoredActivity]
) -> List[Foundation]:
    uses_ai = firm_uses_ai(answers)
    kpi = library.kpi_view(answers.kpi, answers.kpi_name)
    kpi_text, baseline = lower_first(kpi["label"]), kpi["baseline"]
    found: List[Foundation] = []
    if uses_ai and answers.policy == Policy.NONE.value and told(answers, "policy"):
        found.append(c.SHADOW_FOUNDATION)
    elif uses_ai and answers.policy == Policy.RESTRICTED.value:
        found.append(c.SHADOW_RESTRICTED_FOUNDATION)
    if nobody_assigned(answers):
        found.append(c.OWNER_FOUNDATION)
    found += one_person_rows(answers, library)
    found += shared_data_rows(library, items)
    seen_actions = {row[2] for row in found}
    task = lower_first(top_label) if top_label else "your first move"
    fill = lambda text: text.format(kpi=kpi_text, baseline=baseline, task=task)
    for key in answer_keys(answers, uses_ai):
        row = c.FOUNDATIONS.get(key)
        if not row:
            continue
        title, text, action = fill(row[0]), fill(row[1]), fill(row[2])
        if action not in seen_actions:
            seen_actions.add(action)
            found.append((title[0].upper() + title[1:], text, action))
    return found
