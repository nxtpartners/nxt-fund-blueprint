"""Boundary check: answers are accepted only if they match the closed sets and the expected shape."""
from __future__ import annotations

import re
from typing import Any, Dict, List

from . import constants as c
from .data import Library
from .enums import AiHere, AiStage, Depth, Nature
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


def closed_answer(library: Library, raw: Dict[str, Any], field: str, assumed: List[str], skipped: List[str], where: str = "", key: str = "", expected: bool = True, noted: bool = True, allowed: Any = None) -> str:
    value = raw.get(field)
    if value is None:
        if expected:
            skipped.append(key or field)
            if noted:
                assumed.append(f"{library.question(field)['header']}{where}")
        elif field in c.COUNTED_AS_UNTOLD:
            skipped.append(key or field)
        return c.NEUTRAL_ANSWERS[field]
    options = allowed if allowed is not None else library.option_ids(field)
    if not isinstance(value, str) or value not in options:
        raise AnswerError(f"Invalid answer '{value}' for '{field}'{where}. Allowed: {', '.join(options)}. Ask this question again.")
    return value


def closed_list(library: Library, raw: Dict[str, Any], field: str, assumed: List[str], skipped: List[str], where: str = "", key: str = "", expected: bool = True) -> List[str]:
    value = raw.get(field)
    if value is None or value == []:
        if expected:
            skipped.append(key or field)
            assumed.append(f"{library.question(field)['header']}{where}")
        return list(c.NEUTRAL_ANSWERS[field])
    require_type(value, list, f"'{field}'{where}")
    options = library.option_ids(field)
    for item in value:
        if not isinstance(item, str) or item not in options:
            raise AnswerError(f"Invalid answer '{item}' for '{field}'{where}. Allowed: {', '.join(options)}. Ask this question again.")
    return list(dict.fromkeys(value))


def string_list(raw: Dict[str, Any], key: str, label: str) -> List[str]:
    items = raw.get(key) or []
    require_type(items, list, label)
    for item in items:
        require_type(item, str, label)
    return list(dict.fromkeys(items))


def from_selected(row: Dict[str, Any], key: str, activities: List[str], workstream_id: str) -> List[str]:
    items = string_list(row, key, f"{key} in '{workstream_id}'")
    if any(task not in activities for task in items):
        raise AnswerError(f"{key} in '{workstream_id}' must come from its selected activities. Ask this question again.")
    return items


def clean_measures(library: Library, row: Dict[str, Any], workstream_id: str) -> Dict[str, Any]:
    known = {measure["id"] for measure in library.measures_for(workstream_id)}
    tracked = None
    items = string_list(row, c.KEY_MEASURES_TRACKED, f"{c.KEY_MEASURES_TRACKED} in '{workstream_id}'")
    if items:
        if any(item not in known and item != c.KEY_UNTRACKED for item in items):
            raise AnswerError(f"Unknown measure in '{workstream_id}'. Ask the measures question again.")
        if c.KEY_UNTRACKED in items and len(items) > 1:
            raise AnswerError(f"Measures in '{workstream_id}' say both tracked and not tracked. Ask the measures question again.")
        tracked = [item for item in items if item != c.KEY_UNTRACKED]
    off = string_list(row, c.KEY_MEASURES_OFF, f"{c.KEY_MEASURES_OFF} in '{workstream_id}'")
    if any(item not in (tracked or []) for item in off):
        raise AnswerError(f"{c.KEY_MEASURES_OFF} in '{workstream_id}' must come from the measures they track. Ask this question again.")
    return {c.KEY_MEASURES_TRACKED: tracked, c.KEY_MEASURES_OFF: off}


def clean_walkthrough(row: Dict[str, Any], workstream_id: str) -> Dict[str, Any]:
    raw = row.get(c.KEY_WALKTHROUGH)
    if raw is None:
        return {"walkthrough_steps": [], c.KEY_SLOW_STEP: ""}
    require_type(raw, dict, f"The walkthrough in '{workstream_id}'")
    steps = raw.get(c.KEY_STEPS) or []
    require_type(steps, list, f"The walkthrough steps in '{workstream_id}'")
    if len(steps) > c.WALKTHROUGH_STEPS_MAX:
        raise AnswerError(f"The walkthrough in '{workstream_id}' takes at most {c.WALKTHROUGH_STEPS_MAX} steps. Restate it and confirm it again.")
    cleaned = [clean_text(step, c.WALKTHROUGH_STEP_MAX, "A walkthrough step") for step in steps]
    slow = clean_text(raw.get(c.KEY_SLOW_STEP), c.WALKTHROUGH_STEP_MAX, "The slowest step")
    if slow and slow not in cleaned:
        raise AnswerError(f"The slowest step in '{workstream_id}' must be one of the confirmed steps. Ask that question again.")
    return {"walkthrough_steps": cleaned, c.KEY_SLOW_STEP: slow}


def parse_workstream(library: Library, workstream_id: str, row: Dict[str, Any], assumed: List[str], skipped: List[str], firm_has_no_ai: bool, ai_assumed_areas: List[str]) -> WorkstreamAnswers:
    label = library.workstreams[workstream_id]["label"]
    where = f" in {label}"
    depth = row.get(c.KEY_DEPTH)
    depth = Depth.DEEP.value if depth is None else depth
    if not isinstance(depth, str) or depth not in c.ASKED_AT_DEPTH:
        raise AnswerError(f"Invalid depth '{depth}' for '{workstream_id}'. Allowed: {', '.join(c.ASKED_AT_DEPTH)}.")
    row = dict(row)
    for field in c.DETAIL_FIELDS:
        if field not in c.ASKED_AT_DEPTH[depth]:
            row[field] = None
    lists = c.ASKED_LISTS_AT_DEPTH[depth]
    for key, group in ((c.KEY_LEGACY_TASKS, "legacy_tasks"), (c.KEY_HARM_TASKS, "harm_tasks"), (c.KEY_HEAVY_TASK, "heavy_task"), (c.KEY_MEASURES_TRACKED, "measures"), (c.KEY_MEASURES_OFF, "measures"), (c.KEY_WALKTHROUGH, "walkthrough")):
        if group not in lists:
            row.pop(key, None)
    asked = c.ASKED_AT_DEPTH[depth]
    unasked = [field for field in c.DETAIL_FIELDS if field not in asked or (field == "ai_here" and firm_has_no_ai)]
    details: Dict[str, Any] = {}
    for field in c.DETAIL_SINGLE:
        details[field] = closed_answer(library, row, field, assumed, skipped, where, key=f"{workstream_id}.{field}", expected=(field not in unasked), noted=(field not in c.NOT_NOTED_DETAIL))
    for field in c.DETAIL_LISTS:
        details[field] = closed_list(library, row, field, assumed, skipped, where, key=f"{workstream_id}.{field}", expected=(field not in unasked))
    unasked += [field for field in c.NOT_NOTED_DETAIL if row.get(field) is None]
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
    if firm_has_no_ai and (details["ai_here"] != AiHere.NONE.value or any(item[c.KEY_USES_AI] for item in custom)):
        raise AnswerError(f"The answers say the firm does not use AI, but ai_here or uses_ai in '{workstream_id}' say it does. These may be left over from an earlier answer. Ask the person which is right. If the firm does not use AI, set ai_here to none, clear ai_tasks, and set uses_ai to false. Otherwise, correct ai_stage.")
    ai_tasks = from_selected(row, c.KEY_AI_TASKS, activities, workstream_id)
    legacy = from_selected(row, c.KEY_LEGACY_TASKS, activities, workstream_id)
    harm = from_selected(row, c.KEY_HARM_TASKS, activities, workstream_id)
    heavy = row.get(c.KEY_HEAVY_TASK)
    if heavy is not None and (not isinstance(heavy, str) or heavy not in activities):
        raise AnswerError(f"heavy_task in '{workstream_id}' must be one of its selected activities. Ask this question again.")
    if details["ai_here"] != AiHere.NONE.value and not ai_tasks and activities:
        ai_assumed_areas.append(label)
    return WorkstreamAnswers.from_dict(workstream_id, {
        **details, c.KEY_DEPTH: depth, c.KEY_ACTIVITIES: activities, c.KEY_CUSTOM: custom, c.KEY_AI_TASKS: ai_tasks,
        c.KEY_LEGACY_TASKS: legacy, c.KEY_HARM_TASKS: harm, c.KEY_HEAVY_TASK: heavy or "", "unasked": unasked,
        **clean_measures(library, row, workstream_id), **clean_walkthrough(row, workstream_id),
    })


def parse_answers(library: Library, raw: Any) -> Answers:
    require_type(raw, dict, "The answers file")
    assumed: List[str] = []
    skipped: List[str] = []
    ai_assumed_areas: List[str] = []
    firm_has_no_ai = raw.get("ai_stage") == AiStage.NONE.value
    has_thesis = bool(raw.get(c.KEY_THESIS_SUMMARY) or raw.get(c.KEY_THESIS_FOCUS))
    stage_asked_used = raw.get("ai_stage") not in (None, AiStage.NONE.value)
    firm: Dict[str, Any] = {}
    for field in c.FIRM_FIELDS:
        allowed = library.thesis_options(raw.get("strategy")) if field == "thesis" else None
        expected = (stage_asked_used or field not in c.AI_FOLLOW_UPS) and not (field == "thesis" and has_thesis)
        firm[field] = closed_answer(library, raw, field, assumed, skipped, expected=expected, noted=(field not in c.NOT_NOTED_WHEN_SKIPPED), allowed=allowed)
    for field in c.FIRM_LISTS:
        firm[field] = closed_list(library, raw, field, assumed, skipped)
    for field in c.OPTIONAL_FIRM_FIELDS:
        value = raw.get(field)
        if value is not None and (not isinstance(value, str) or value not in library.option_ids(field)):
            raise AnswerError(f"Invalid answer '{value}' for '{field}'. Allowed: {', '.join(library.option_ids(field))}. Ask this question again.")
        firm[field] = value or ""

    tools = string_list(raw, c.KEY_AI_TOOLS, c.KEY_AI_TOOLS)
    allowed_tools = library.option_ids(c.KEY_AI_TOOLS)
    if any(tool not in allowed_tools for tool in tools):
        raise AnswerError(f"Invalid ai_tools. Allowed: {', '.join(allowed_tools)}. Ask this question again.")

    kpi = raw.get(c.KEY_KPI)
    if not isinstance(kpi, str) or kpi not in library.kpis:
        raise AnswerError(f"A KPI is required. Allowed: {', '.join(library.kpis)}. Ask the KPI question again.")
    if raw.get("pressure") is not None and library.kpis[kpi]["pressure"] != raw.get("pressure"):
        raise AnswerError(f"KPI '{kpi}' does not belong to priority '{raw.get('pressure')}'. Ask the KPI question again.")

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
        workstreams.append(parse_workstream(library, workstream_id, row, assumed, skipped, firm_has_no_ai, ai_assumed_areas))

    named = raw.get(c.KEY_NAMED_TASK)
    if named is not None:
        require_type(named, str, c.KEY_NAMED_TASK)
        names = {task for work in workstreams for task in work.activities} | {item[c.KEY_NAME] for work in workstreams for item in work.custom}
        if named and named not in names:
            raise AnswerError("named_task must be a selected activity id or a confirmed custom task name. Check the named task, and add it to its work area.")

    focus = string_list(raw, c.KEY_THESIS_FOCUS, c.KEY_THESIS_FOCUS)
    if len(focus) > c.THESIS_FOCUS_MAX or any(item not in library.workstreams for item in focus):
        raise AnswerError(f"thesis_focus takes at most {c.THESIS_FOCUS_MAX} work area ids. Ask the thesis focus question again.")
    notes_raw = raw.get(c.KEY_THESIS_NOTES) or {}
    require_type(notes_raw, dict, c.KEY_THESIS_NOTES)
    notes = {str(key): clean_text(value, c.THESIS_NOTE_MAX, "A thesis note") for key, value in notes_raw.items()}
    return Answers(
        kpi=kpi, workstreams=workstreams, assumed=assumed, skipped=skipped, ai_assumed_areas=ai_assumed_areas, ai_tools=tools,
        thesis_summary=clean_text(raw.get(c.KEY_THESIS_SUMMARY), c.THESIS_SUMMARY_MAX, "thesis_summary"),
        thesis_focus=focus, thesis_notes=notes, named_task=named or "",
        firm_name=clean_text(raw.get(c.KEY_FIRM_NAME), c.FIRM_NAME_MAX, "firm_name"),
        public_facts=clean_public_facts(raw), **firm,
    )
