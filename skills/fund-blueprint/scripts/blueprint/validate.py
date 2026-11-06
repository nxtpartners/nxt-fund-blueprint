"""Boundary check: answers are accepted only if they match the closed sets and the expected shape."""
from __future__ import annotations

import re
from typing import Any, Dict, List

from . import constants as c
from .data import Library
from .enums import AiHere, AiStage, Nature
from .models import Answers, WorkstreamAnswers

CUSTOM_NATURES = (Nature.RULES.value, Nature.DRAFTING.value, Nature.MULTI_SYSTEM.value, Nature.JUDGMENT.value)
UNSAFE_TEXT = re.compile(r"[<>{}\[\]\\|]|https?://|www\.", re.IGNORECASE)
SAFE_URL = re.compile(r"https://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[A-Za-z0-9._~%/?=&+,:;@!$'()*#-]*)?")


class AnswerError(ValueError):
    """The message tells the conversation which question to ask again."""


def require_type(value: Any, expected: type, label: str) -> None:
    if not isinstance(value, expected):
        raise AnswerError(f"{label} has the wrong format. Rebuild answers.json as shown in the skill's example.")


def clean_text(value: Any, limit: int, label: str) -> str:
    """Confirmed free text: plain, short, and safe to place in the report."""
    if value is None:
        return ""
    require_type(value, str, label)
    text = " ".join(value.split()).replace("—", ",").replace("–", "-")
    if len(text) > limit or UNSAFE_TEXT.search(text):
        raise AnswerError(f"{label} must be plain text of at most {limit} characters, without links or markup. Rewrite it and confirm it again.")
    return text


def clean_public_facts(raw: Dict[str, Any]) -> List[Dict[str, str]]:
    """Confirmed public facts, each with the https page it came from."""
    items = raw.get(c.KEY_PUBLIC_FACTS) or []
    require_type(items, list, c.KEY_PUBLIC_FACTS)
    if len(items) > c.PUBLIC_FACTS_MAX:
        raise AnswerError(f"Keep at most {c.PUBLIC_FACTS_MAX} public facts.")
    facts = []
    for item in items:
        require_type(item, dict, c.KEY_PUBLIC_FACTS)
        source = str(item.get(c.KEY_SOURCE) or "").strip()
        if not SAFE_URL.fullmatch(source) or len(source) > c.SOURCE_URL_MAX:
            raise AnswerError("Each public fact needs the https address of the page it came from. Remove any fact without one.")
        fact = clean_text(item.get(c.KEY_FACT), c.PUBLIC_FACT_MAX, "A public fact")
        if not fact:
            raise AnswerError("A public fact is empty. Remove it.")
        facts.append({c.KEY_FACT: fact, c.KEY_SOURCE: source})
    return facts


def clean_custom(item: Any, workstream: str) -> Dict[str, Any]:
    require_type(item, dict, f"A custom task in '{workstream}'")
    name = clean_text(item.get(c.KEY_NAME), c.CUSTOM_NAME_MAX, f"A custom task in '{workstream}'")
    if not name:
        raise AnswerError(f"A custom task in '{workstream}' has no name. Ask for it again.")
    nature = item.get(c.KEY_NATURE)
    if nature not in CUSTOM_NATURES:
        raise AnswerError(f"Custom task '{name}' needs a nature from {CUSTOM_NATURES}. Ask the kind-of-task question.")
    link = item.get(c.KEY_KPI_LINK)
    if link is not None and (not isinstance(link, str) or link not in c.KPI_LINK_RELEVANCE):
        raise AnswerError(f"Custom task '{name}' has an invalid KPI link. Ask that question again.")
    uses_ai = item.get(c.KEY_USES_AI)
    if uses_ai is not None and not isinstance(uses_ai, bool):
        raise AnswerError(f"Custom task '{name}' needs true or false for uses_ai. Ask that question again.")
    return {c.KEY_NAME: name, c.KEY_NATURE: nature, c.KEY_USES_AI: uses_ai, c.KEY_KPI_LINK: link}


def closed_answer(library: Library, raw: Dict[str, Any], field: str, assumed: List[str], skipped: List[str], where: str = "", key: str = "", expected: bool = True, allowed: Any = None) -> str:
    value = raw.get(field)
    if value is None:
        if expected:
            assumed.append(f"{library.question(field)['header']}{where}")
            skipped.append(key or field)
        return c.NEUTRAL_ANSWERS[field]
    options = allowed if allowed is not None else library.option_ids(field)
    if not isinstance(value, str) or value not in options:
        raise AnswerError(f"Invalid answer '{value}' for '{field}'{where}. Allowed: {', '.join(options)}. Ask this question again.")
    return value


def string_list(raw: Dict[str, Any], key: str, label: str) -> List[str]:
    items = raw.get(key) or []
    require_type(items, list, label)
    for item in items:
        require_type(item, str, label)
    return list(dict.fromkeys(items))


def parse_answers(library: Library, raw: Any) -> Answers:
    require_type(raw, dict, "The answers file")
    assumed: List[str] = []
    skipped: List[str] = []
    uses_ai = raw.get("ai_stage") not in (None, AiStage.NONE.value)
    firm: Dict[str, str] = {}
    for field in c.FIRM_FIELDS:
        allowed = library.thesis_options(raw.get("strategy")) if field == "thesis" else None
        firm[field] = closed_answer(library, raw, field, assumed, skipped, expected=(uses_ai or field not in c.AI_FOLLOW_UPS), allowed=allowed)

    tools = string_list(raw, c.KEY_AI_TOOLS, c.KEY_AI_TOOLS)
    allowed_tools = library.option_ids(c.KEY_AI_TOOLS)
    if any(tool not in allowed_tools for tool in tools):
        raise AnswerError(f"Invalid ai_tools. Allowed: {', '.join(allowed_tools)}. Ask this question again.")

    kpi = raw.get(c.KEY_KPI)
    if not isinstance(kpi, str) or kpi not in library.kpis:
        raise AnswerError(f"A KPI is required. Allowed: {', '.join(library.kpis)}. Ask the KPI question again.")

    selected = raw.get(c.KEY_WORKSTREAMS) or {}
    require_type(selected, dict, c.KEY_WORKSTREAMS)
    if not selected:
        raise AnswerError("At least one work area is required. Ask the work area questions.")
    if len(selected) > c.MAX_WORKSTREAMS:
        raise AnswerError(f"At most {c.MAX_WORKSTREAMS} work areas can be assessed. Ask which to keep.")

    workstreams: List[WorkstreamAnswers] = []
    for workstream_id, row in selected.items():
        if workstream_id not in library.workstreams:
            raise AnswerError(f"Unknown work area '{workstream_id}'.")
        require_type(row, dict, f"Work area '{workstream_id}'")
        label = library.workstreams[workstream_id]["label"]
        where = f" in {label}"
        details = {
            field: closed_answer(library, row, field, assumed, skipped, where, key=f"{workstream_id}.{field}", expected=(uses_ai or field != "ai_here"))
            for field in c.DETAIL_FIELDS
        }
        activities = string_list(row, c.KEY_ACTIVITIES, f"Tasks in '{workstream_id}'")
        for activity_id in activities:
            activity = library.activities.get(activity_id)
            if activity is None or activity.workstream != workstream_id:
                raise AnswerError(f"Activity '{activity_id}' does not belong to '{workstream_id}'. Ask the tasks question again.")
        custom_rows = row.get(c.KEY_CUSTOM) or []
        require_type(custom_rows, list, f"Custom tasks in '{workstream_id}'")
        custom = [clean_custom(item, workstream_id) for item in custom_rows]
        if not activities and not custom:
            raise AnswerError(f"Work area '{workstream_id}' needs at least one task. Ask the tasks question again.")
        ai_tasks = string_list(row, c.KEY_AI_TASKS, f"AI tasks in '{workstream_id}'")
        if any(task not in activities for task in ai_tasks):
            raise AnswerError(f"ai_tasks in '{workstream_id}' must come from its selected activities. Ask this question again.")
        if details["ai_here"] != AiHere.NONE.value and not ai_tasks and activities:
            assumed.append(f"Where AI is used in {label}, so its routine tasks were treated as using AI")
        workstreams.append(WorkstreamAnswers.from_dict(workstream_id, {**details, c.KEY_ACTIVITIES: activities, c.KEY_CUSTOM: custom, c.KEY_AI_TASKS: ai_tasks}))

    focus = string_list(raw, c.KEY_THESIS_FOCUS, c.KEY_THESIS_FOCUS)
    if len(focus) > c.THESIS_FOCUS_MAX or any(item not in library.workstreams for item in focus):
        raise AnswerError(f"thesis_focus takes at most {c.THESIS_FOCUS_MAX} work area ids. Ask the thesis focus question again.")
    notes_raw = raw.get(c.KEY_THESIS_NOTES) or {}
    require_type(notes_raw, dict, c.KEY_THESIS_NOTES)
    notes = {str(key): clean_text(value, c.THESIS_NOTE_MAX, "A thesis note") for key, value in notes_raw.items()}
    return Answers(
        kpi=kpi, workstreams=workstreams, assumed=assumed, skipped=skipped, ai_tools=tools,
        thesis_summary=clean_text(raw.get(c.KEY_THESIS_SUMMARY), c.THESIS_SUMMARY_MAX, "thesis_summary"),
        thesis_focus=focus, thesis_notes=notes,
        firm_name=clean_text(raw.get(c.KEY_FIRM_NAME), c.FIRM_NAME_MAX, "firm_name"),
        public_facts=clean_public_facts(raw), **firm,
    )
