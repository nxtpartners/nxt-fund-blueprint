"""What would change the plan: the same rules re-run with one answer moved."""
from __future__ import annotations

from dataclasses import replace
from typing import Callable, Dict, List, Tuple

from .. import constants as c
from ..enums import Policy, Verdict
from ..models import Answers, Plan, ScoredActivity
from ..text import join_words, lower_first
from .facts import nobody_assigned, systems_apart, told


def levers_for(answers: Answers) -> List[Tuple[str, Dict[str, object]]]:
    levers: List[Tuple[str, Dict[str, object]]] = []
    if answers.policy in (Policy.RESTRICTED.value, Policy.NONE.value) and told(answers, "policy"):
        levers.append((c.LEVER_POLICY, {"policy": Policy.APPROVED.value}))
    if systems_apart(answers) and told(answers, "systems"):
        levers.append((c.LEVER_SYSTEMS, {"systems": "connected"}))
    if nobody_assigned(answers):
        levers.append((c.LEVER_CAPACITY, {"capacity": ["ops_lead"]}))
    return levers


def shown_names(names: List[str]) -> str:
    extra = [c.AND_OTHERS.replace("and ", "")] if len(names) > c.CHANGE_NAMES_MAX else []
    return join_words(names[: c.CHANGE_NAMES_MAX] + extra)


def change_parts(before: Dict[str, ScoredActivity], after: List[ScoredActivity]) -> List[str]:
    groups: Dict[Tuple[Verdict, Verdict], List[str]] = {}
    faster: Dict[Tuple[str, str], List[str]] = {}
    for row in after:
        old = before[row.activity_id]
        if row.verdict == Verdict.LEAVE:
            continue
        if old.verdict != row.verdict:
            groups.setdefault((old.verdict, row.verdict), []).append(lower_first(row.label))
        elif old.speed_label != row.speed_label:
            faster.setdefault((old.speed_label, row.speed_label), []).append(lower_first(row.label))
    parts = [
        f"the estimate for {shown_names(names)} would change from {c.CHANGE_WORDS[old]} to {c.CHANGE_WORDS[new]}"
        for (old, new), names in groups.items()
    ]
    parts += [
        f"the estimate for {shown_names(names)} would change from {lower_first(old)} to {lower_first(new)}"
        for (old, new), names in faster.items()
    ]
    return parts


def what_would_change(
    rescore: Callable[[Answers], Plan], answers: Answers, plan_items: List[ScoredActivity]
) -> List[str]:
    """Re-run the same rules with one answer moved, so the firm can see which of its constraints matter most."""
    lines: List[str] = []
    before = {item.activity_id: item for item in plan_items}
    for text, change in levers_for(answers):
        parts = change_parts(before, rescore(replace(answers, **change)).items)
        if parts:
            more = f" {c.MORE_CHANGES}" if len(parts) > c.CHANGE_GROUPS_MAX else ""
            lines.append(f"If {text}: {'; '.join(parts[: c.CHANGE_GROUPS_MAX])}.{more}")
    return lines
