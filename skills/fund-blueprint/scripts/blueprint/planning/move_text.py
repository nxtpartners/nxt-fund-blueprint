"""What a move says: its solution, first step, check, reason, and why line, written from the rule and the answers."""
from __future__ import annotations

import re
from typing import Tuple

from .. import constants as c
from ..enums import AiHere, AiStage, ErrorCost, KpiClaim, Nature, Policy, Rule, Verdict
from ..models import Activity, Answers, WorkstreamAnswers
from ..text import lower_first
from .decisions import agent_blocker
from .facts import (
    HUMAN_NATURES,
    doc_sources_text,
    risky,
    serious_documents,
    sources_text,
    stage_for,
    told,
    told_here,
)

AI_CLAUSE = re.compile(r"\s*AI (?:can|should)[^.]*\.")


def build_on_text(activity: Activity, work: WorkstreamAnswers, answers: Answers) -> Tuple[str, str, str]:
    """Reason, solution, and first step for AI that already exists in this work."""
    table = c.BUILD_ON_TEXT
    stage = stage_for(activity, work)
    return table.get((stage, answers.ai_results)) or table[(stage, "any")]


def base_solution(activity: Activity, verdict: Verdict) -> str:
    """Only an agent verdict may describe an agent, and prepare-only work stays prepare-only."""
    if activity.nature != Nature.MULTI_SYSTEM or verdict == Verdict.AGENTIC:
        return activity.solution
    return c.CUSTOM_PREPARE_SOLUTION if activity.custom else activity.solution


def not_ready_for_ai_step(answers: Answers) -> bool:
    return answers.policy in (Policy.NONE.value, Policy.RESTRICTED.value) or not told(answers, "policy")


def plan_first_step(activity: Activity, answers: Answers, verdict: Verdict) -> str:
    """Keep the specific step, and use the version that needs no AI where the move or the firm does not use AI."""
    no_ai = verdict not in c.AI_VERDICTS and verdict != Verdict.BUILD_ON
    uses_ai_needlessly = activity.first_step_uses_ai and (no_ai or not_ready_for_ai_step(answers))
    if activity.first_step_if_no_ai and (answers.ai_stage == AiStage.NONE.value or uses_ai_needlessly):
        return activity.first_step_if_no_ai
    return activity.first_step


def human_check(row: dict, activity: Activity, work: WorkstreamAnswers, verdict: Verdict, in_use: bool) -> str:
    """A rule may add to a safeguard, and never replace it. Text about AI tools appears only where AI is in play."""
    ai_in_play = in_use or verdict in c.AI_VERDICTS or verdict == Verdict.BUILD_ON
    parts = [row.get("check"), activity.check, activity.check_ai if ai_in_play else ""]
    if activity.custom and activity.nature not in HUMAN_NATURES and risky(activity, work):
        parts.append(c.CUSTOM_SERIOUS_CHECK)
    return " ".join(part for part in parts if part)


def build_on_move(
    activity: Activity, work: WorkstreamAnswers, answers: Answers, verdict: Verdict, in_use: bool
) -> Tuple[str, str, str]:
    _, lead, first_step = build_on_text(activity, work, answers)
    prefix = c.DEPLOYED_GOAL_PREFIX if stage_for(activity, work) == AiHere.DEPLOYED.value else c.GOAL_PREFIX
    goal = base_solution(activity, verdict)
    text = f"{lead} {prefix}{goal[0].lower()}{goal[1:]}"
    suffix = c.DOCS_REVIEW_SUFFIX if serious_documents(activity, work) else ""
    step = first_step.replace("{task}", lower_first(activity.label))
    return text + suffix, step, human_check({}, activity, work, verdict, in_use)


def tailored_text(
    activity: Activity, rule: Rule, work: WorkstreamAnswers, answers: Answers, in_use: bool
) -> Tuple[str, str, str]:
    row = c.RULES[rule]
    verdict = row["verdict"]
    task = lower_first(activity.label)
    if rule == Rule.BUILD_ON:
        return build_on_move(activity, work, answers, verdict, in_use)
    if rule == Rule.LEAVE and (in_use or answers.policy == Policy.RESTRICTED.value):
        step = activity.first_step.replace("{task}", task)
        return AI_CLAUSE.sub("", activity.solution), step, human_check({}, activity, work, verdict, in_use)
    solution = (row.get("solution") or base_solution(activity, verdict)).replace("{task}", task)
    if activity.process_solution and rule in c.PROCESS_TEXT_RULES:
        solution = activity.process_solution
    elif activity.process_solution and rule == Rule.ONE_PERSON:
        solution = f"{solution} Then: {activity.process_solution[0].lower()}{activity.process_solution[1:]}"
    first_step = (row.get("first_step") or plan_first_step(activity, answers, verdict)).replace("{task}", task)
    check = human_check(row, activity, work, verdict, in_use)
    if rule == Rule.REMOVE:
        check = row["check"]
    if verdict == Verdict.ADD_AI and serious_documents(activity, work):
        solution += c.DOCS_REVIEW_SUFFIX
    return solution, first_step, check


def reason_text(activity: Activity, rule: Rule, work: WorkstreamAnswers, answers: Answers, kpi_text: str) -> str:
    if rule == Rule.BUILD_ON:
        return build_on_text(activity, work, answers)[0]
    row = c.RULES[rule]
    if rule == Rule.AGENT_BLOCKED:
        blocker, unlock = c.AGENT_BLOCKERS[agent_blocker(activity, work, answers)]
        return row["reason"].format(blocker=blocker, unlock=unlock)
    if rule in (Rule.AGREE_FIRST, Rule.ONE_PLACE):
        if not told_here(work, answers, "sources"):
            return row["reason_unknown"]
        return row["reason"].format(sources=sources_text(work.sources))
    if rule in (Rule.DOCS_PLAIN, Rule.DOCS_REVIEW):
        return row["reason"].format(doc_sources=doc_sources_text(work))
    if rule == Rule.SERIOUS_PROCESS_FIRST:
        severe = work.error_cost == ErrorCost.SEVERE.value
        stated = severe and told_here(work, answers, "error_cost") and risky(activity, work)
        return row["reason"] if stated else row["reason_unknown"]
    if rule == Rule.LEGACY_CHECK:
        return row["reason"].format(kpi=kpi_text)
    return row["reason"]


def relevance_note(rule: Rule, claim: KpiClaim, relevance: int, kpi_text: str) -> str:
    """One ladder for the link everywhere.

    Pausing or stopping work does not itself move a KPI, so it never says it does.
    """
    if rule == Rule.PAUSE_USE:
        return c.RELEVANCE_PAUSE.format(kpi=kpi_text)
    if claim == KpiClaim.NONE:
        return c.RELEVANCE_NONE
    link = f"{c.LINK_LADDER[relevance]} to {kpi_text}"
    if relevance == 0:
        return link
    if claim == KpiClaim.PREPARES:
        return c.RELEVANCE_PREPARES.format(kpi=kpi_text)
    if claim == KpiClaim.SOME:
        return c.RELEVANCE_ONCE_FIXED.format(link=c.LINK_LADDER[relevance], kpi=kpi_text)
    return link


def why_line(
    item_named: bool,
    reason: str,
    relevance: int,
    linked: bool,
    kpi_text: str,
    off_target: str,
    slow_step: str = "",
) -> str:
    """The rule's reason, which reasons from the answer, plus what links it to the number.

    Facts about the work area stay in its group line.
    """
    parts = []
    if item_named:
        parts.append("You named this as the task to take off your team.")
    if slow_step:
        parts.append(c.SLOW_STEP_WHY.format(slow_step=slow_step))
    if reason:
        parts.append(reason)
    if off_target:
        parts.append(f"You said {lower_first(off_target)} is off target.")
    elif linked:
        parts.append(f"It {c.LINK_WORDS[relevance]} {kpi_text}.")
    return " ".join(parts)
