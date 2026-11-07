"""Which rule applies to a task. The order of the checks is the policy, so it stays readable top to bottom."""
from __future__ import annotations

from typing import Optional

from .. import constants as c
from ..enums import AiStage, Depth, Nature, Policy, Rhythm, Rule, Source, Systems, TimeGoes, Trust, Who
from ..models import Activity, Answers, WorkstreamAnswers
from .facts import (
    HUMAN_NATURES,
    has_documents,
    has_system,
    nobody_assigned,
    risky,
    serious_work,
    systems_apart,
    told,
    told_here,
)


def firm_blocker(answers: Answers) -> str:
    """What about the firm as a whole rules out an agent. First hit wins."""
    if any(value in answers.trust for value in (Trust.RESISTANT.value, Trust.SKEPTICAL.value)):
        return "trust"
    if not told(answers, "policy"):
        return "policy_unknown"
    if answers.policy == Policy.NONE.value:
        return "policy_none"
    if not told(answers, "ai_stage"):
        return "stage_unknown"
    if answers.ai_stage == AiStage.NONE.value:
        return "stage_none"
    if answers.ai_stage == AiStage.INDIVIDUALS.value:
        return "stage_individuals"
    if told(answers, "ai_results") and answers.ai_results == "disappointing":
        return "results"
    if nobody_assigned(answers):
        return "capacity"
    if told(answers, "systems") and answers.systems == Systems.MANUAL.value:
        return "systems_manual"
    if told(answers, "systems") and answers.systems == Systems.DISCONNECTED.value:
        return "systems_disconnected"
    return ""


def agent_blocker(activity: Activity, work: WorkstreamAnswers, answers: Answers, anchored: bool = True) -> str:
    """First hit wins, and the reason shown names the answer that actually blocks it."""
    firm = firm_blocker(answers)
    if firm:
        return firm
    if not told_here(work, answers, "sources"):
        return "sources_unknown"
    if not has_system(work):
        return "sources"
    if Source.EMAIL.value in work.sources and answers.policy != Policy.APPROVED.value:
        return "email"
    if anchored and TimeGoes.REKEY.value in work.time_goes:
        return "rekey"
    return ""


def legacy_rule(activity: Activity, work: WorkstreamAnswers, answers: Answers, relevance: int) -> Rule:
    """A task done mainly out of habit: stop it only where nothing depends on it."""
    if activity.control:
        return Rule.KEEP_CONTROL
    if activity.required or risky(activity, work):
        return Rule.KEEP_MINIMAL
    if relevance >= c.LINKED_RELEVANCE_MIN or work.id in answers.thesis_focus:
        return Rule.LEGACY_CHECK
    return Rule.REMOVE


def process_rule(activity: Activity, work: WorkstreamAnswers, anchored: bool) -> Optional[Rule]:
    """Problems no software fixes, so they come before any talk of tools."""
    nature = activity.nature
    process_flexible = not activity.control and anchored
    if work.depth == Depth.QUICK.value and activity.no_agent:
        return Rule.QUICK_REVIEW
    if work.depends == "no" and not activity.input_documents and anchored:
        return Rule.ONE_PERSON
    if work.who == [Who.OUTSIDE.value]:
        return Rule.OUTSIDE
    if work.same_way == "different" and process_flexible:
        return Rule.NOT_SAME_WAY
    if TimeGoes.FIXING.value in work.time_goes and nature in (Nature.RULES, Nature.MULTI_SYSTEM) and process_flexible:
        return Rule.REDO
    waits = TimeGoes.WAIT_SIGNOFF.value in work.time_goes
    if waits and nature != Nature.DRAFTING and not activity.required and process_flexible:
        return Rule.SIGNOFFS
    if anchored and work.rhythm == Rhythm.PERIODIC.value and work.hours == "under_20" and nature == Nature.RULES:
        return Rule.TEMPLATE_ENOUGH
    return None


def process_comes_first(activity: Activity, work: WorkstreamAnswers, answers: Answers) -> bool:
    """Serious work with a process fix on offer waits for it, unless AI and the tools are already proven."""
    unsettled = answers.ai_results != "measured" or systems_apart(answers)
    return bool(serious_work(activity, work) and activity.process_solution and unsettled)


def custom_rules_rule(activity: Activity, work: WorkstreamAnswers, answers: Answers) -> Rule:
    if not has_documents(work):
        return Rule.CUSTOM_RULES
    if answers.policy == Policy.RESTRICTED.value:
        return Rule.RESTRICTED
    if answers.policy == Policy.APPROVED.value and serious_work(activity, work):
        return Rule.DOCS_REVIEW
    return Rule.CUSTOM_WRITE_RULES


def fixed_rules_rule(activity: Activity, work: WorkstreamAnswers, answers: Answers) -> Rule:
    """Work that follows fixed rules: automation, unless the information arrives as documents."""
    if activity.custom:
        return custom_rules_rule(activity, work, answers)
    if activity.needs_agreed_rules and not has_system(work):
        return Rule.AGREE_FIRST
    if has_documents(work) and activity.reads_documents:
        if answers.policy == Policy.RESTRICTED.value:
            return Rule.RESTRICTED
        if process_comes_first(activity, work, answers):
            return Rule.SERIOUS_PROCESS_FIRST
        return Rule.DOCS_REVIEW if serious_work(activity, work) else Rule.DOCS_PLAIN
    return Rule.AUTOMATE


def multi_system_rule(activity: Activity, work: WorkstreamAnswers, answers: Answers, anchored: bool) -> Rule:
    """Work across several tools: an agent only when nothing in the answers stands in the way."""
    if not has_system(work) and not activity.custom and not activity.required:
        return Rule.ONE_PLACE
    if anchored and TimeGoes.REKEY.value in work.time_goes and not has_documents(work) and has_system(work):
        return Rule.REKEY_AUTOMATE
    if process_comes_first(activity, work, answers):
        return Rule.SERIOUS_PROCESS_FIRST
    if activity.no_agent:
        return Rule.NO_AGENT
    if risky(activity, work):
        return Rule.SEVERE_MULTI
    return Rule.AGENT_BLOCKED if agent_blocker(activity, work, answers, anchored) else Rule.AGENT


def decide_rule(
    activity: Activity, work: WorkstreamAnswers, answers: Answers, in_use: bool, relevance: int, anchored: bool
) -> Rule:
    """Ordered on purpose: never automate a step that should not exist, and never add what is already there.

    Where the time goes was asked about the hardest task, so those rules touch that task only.
    """
    nature = activity.nature
    restricted = answers.policy == Policy.RESTRICTED.value
    if nature in HUMAN_NATURES:
        return Rule.LEAVE
    if activity.id in work.legacy_tasks:
        return legacy_rule(activity, work, answers, relevance)
    if in_use:
        return Rule.PAUSE_USE if restricted else Rule.BUILD_ON
    process = process_rule(activity, work, anchored)
    if process is not None:
        return process
    if nature == Nature.RULES:
        return fixed_rules_rule(activity, work, answers)
    if restricted:
        return Rule.RESTRICTED
    if nature == Nature.DRAFTING:
        return Rule.DRAFT
    return multi_system_rule(activity, work, answers, anchored)
