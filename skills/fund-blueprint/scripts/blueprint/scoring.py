"""Deterministic scoring: the same answers always give the same plan."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

from . import constants as c
from .data import Library
from .enums import AiHere, AiResults, AiStage, Capacity, DataHome, ErrorCost, Horizon, Nature, Policy, Quadrant, Trust, Usage, Verdict
from .models import Activity, Answers, ScoredActivity, WorkstreamAnswers

HUMAN_NATURES = (Nature.JUDGMENT, Nature.RELATIONSHIP)
AI_CLAUSE = re.compile(r"\s*AI (?:can|should)[^.]*\.")


@dataclass
class Plan:
    items: List[ScoredActivity]
    foundations: List[Tuple[str, str, str]]
    hours_low: int
    hours_high: Optional[int]
    hours_known: bool
    not_assessed: List[str]

    @property
    def plotted(self) -> List[ScoredActivity]:
        return [item for item in self.items if item.verdict != Verdict.LEAVE]

    @property
    def people(self) -> List[ScoredActivity]:
        return [item for item in self.items if item.verdict == Verdict.LEAVE]

    @property
    def top(self) -> List[ScoredActivity]:
        return self.plotted[:3]


def build_on_text(work: WorkstreamAnswers, answers: Answers) -> Tuple[str, str, str]:
    """Reason, solution, and first step for AI that already exists in this work."""
    table = c.BUILD_ON_TEXT
    stage = in_use_stage(work)
    return table.get((stage, answers.ai_results)) or table[(stage, "any")]


def in_use_stage(work: WorkstreamAnswers) -> str:
    """A custom task can use AI even where the work area as a whole does not."""
    return c.DEFAULT_IN_USE_STAGE if work.ai_here == AiHere.NONE.value else work.ai_here


def route_for(verdict: Verdict, answers: Answers) -> str:
    return c.ROUTES.get((verdict, "any")) or c.ROUTES.get((verdict, c.BUDGET_TIER[answers.budget]), "")


def in_use_ids(work: WorkstreamAnswers, activities: List[Activity]) -> Set[str]:
    """Which tasks already use AI. If they did not say which, assume all of them, so nobody is told to add it."""
    if work.ai_here == AiHere.NONE.value:
        found: Set[str] = set()
    elif work.ai_tasks:
        found = set(work.ai_tasks)
    else:
        found = {activity.id for activity in activities if not activity.custom and activity.nature not in HUMAN_NATURES}
    for activity, item in zip(activities[-len(work.custom) :] if work.custom else [], work.custom):
        if item.get(c.KEY_USES_AI):
            found.add(activity.id)
    return found


def decide_verdict(activity: Activity, work: WorkstreamAnswers, answers: Answers, in_use: bool) -> Tuple[Verdict, str]:
    """Ordered on purpose: never automate a step that should not exist, and never add what is already there."""
    nature = activity.nature
    restricted = answers.policy == Policy.RESTRICTED.value
    if nature in HUMAN_NATURES:
        return Verdict.LEAVE, c.VERDICT_REASONS[Verdict.LEAVE]
    if work.usage == Usage.RARELY.value:
        if activity.required or activity.custom or work.error_cost in (ErrorCost.SEVERE.value, ErrorCost.UNSURE.value):
            return Verdict.OPTIMIZE, c.REASON_REQUIRED
        return Verdict.REMOVE, c.VERDICT_REASONS[Verdict.REMOVE]
    if in_use and restricted:
        return Verdict.OPTIMIZE, c.REASON_RESTRICTED_IN_USE
    if in_use:
        return Verdict.BUILD_ON, build_on_text(work, answers)[0]
    if work.data == DataHome.HEADS.value:
        return Verdict.OPTIMIZE, c.REASON_HEADS
    if nature == Nature.RULES:
        if work.data == DataHome.DOCUMENTS.value:
            if restricted:
                return Verdict.OPTIMIZE, c.REASON_RESTRICTED
            return Verdict.ADD_AI, "The rules are clear, but the information sits in documents, so AI extracts it and fixed checks verify it."
        return Verdict.AUTOMATE, c.VERDICT_REASONS[Verdict.AUTOMATE]
    if restricted:
        return Verdict.OPTIMIZE, c.REASON_RESTRICTED
    if nature == Nature.DRAFTING:
        return Verdict.ADD_AI, c.VERDICT_REASONS[Verdict.ADD_AI]
    if activity.no_agent or work.error_cost in (ErrorCost.SEVERE.value, ErrorCost.UNSURE.value):
        return Verdict.ADD_AI, c.REASON_SEVERE_MULTI
    if answers.trust == Trust.RESISTANT.value:
        return Verdict.ADD_AI, c.REASON_TRUST
    no_policy = answers.policy == Policy.NONE.value or "policy" in answers.skipped
    if answers.ai_stage == AiStage.NONE.value or answers.capacity == Capacity.NOBODY.value or no_policy:
        return Verdict.ADD_AI, c.REASON_NOT_READY
    return Verdict.AGENTIC, c.VERDICT_REASONS[Verdict.AGENTIC]


def estimate_weeks(activity: Activity, verdict: Verdict, work: WorkstreamAnswers, answers: Answers) -> float:
    """Delays add up rather than multiply: several blockers can share one fix."""
    if verdict == Verdict.BUILD_ON:
        drag = (c.WEEKS_POLICY[answers.policy] - 1) + (c.WEEKS_TRUST[answers.trust] - 1)
        return round(c.BUILD_ON_WEEKS[in_use_stage(work)] * max(1.0 + drag, c.WEEKS_MIN_FACTOR), 1)
    weeks = c.BASE_WEEKS[verdict]
    if verdict not in c.TECH_VERDICTS:
        return weeks
    drag = (c.WEEKS_DATA[work.data] - 1) + (c.WEEKS_SYSTEMS[answers.systems] - 1) + (c.WEEKS_CAPACITY[answers.capacity] - 1)
    if answers.team == c.SMALL_TEAM:
        drag += c.WEEKS_SMALL_TEAM - 1
    if verdict in c.AI_VERDICTS:
        drag += (c.WEEKS_POLICY[answers.policy] - 1) + (c.WEEKS_TRUST[answers.trust] - 1)
        drag += (c.WEEKS_EXPERIENCE[answers.ai_stage] - 1) + (c.WEEKS_RESULTS[answers.ai_results] - 1)
        if work.error_cost == ErrorCost.SEVERE.value:
            drag += c.WEEKS_SEVERE_ERROR - 1
    return min(round(weeks * c.WEEKS_EFFORT[activity.effort] * max(1.0 + drag, c.WEEKS_MIN_FACTOR), 1), c.WEEKS_AXIS_MAX)


def relevance_for(activity: Activity, answers: Answers) -> Tuple[int, bool]:
    """The hand-assigned link to the KPI, and whether it was actually assessed."""
    if activity.custom:
        if activity.kpi_link is None:
            return c.CUSTOM_DEFAULT_RELEVANCE, False
        return c.KPI_LINK_RELEVANCE[activity.kpi_link], True
    return activity.kpis.get(answers.kpi, 0), True


def estimate_impact(activity: Activity, work: WorkstreamAnswers, answers: Answers, area: str) -> Tuple[float, str]:
    relevance, assessed = relevance_for(activity, answers)
    score = (
        c.IMPACT_WEIGHT_RELEVANCE * relevance / c.RELEVANCE_MAX
        + c.IMPACT_WEIGHT_VOLUME * c.HOURS_VOLUME[work.hours]
        + c.IMPACT_WEIGHT_SENIORITY * c.OWNER_SENIORITY[work.owner]
    )
    if relevance == 0:
        score *= c.IMPACT_UNRELATED_FACTOR
    thesis_known = "thesis" not in answers.skipped
    if (thesis_known and work.id in c.THESIS_WORKSTREAMS.get(answers.thesis, ())) or work.id in answers.thesis_focus:
        score += c.IMPACT_BOOST
    if area in c.STAGE_AREAS.get(answers.fund_stage, ()):
        score += c.IMPACT_BOOST
    impact = c.IMPACT_MIN + (c.IMPACT_MAX - c.IMPACT_MIN) * min(score, 1.0)
    phrase = c.RELEVANCE_PHRASES[relevance] if assessed else c.RELEVANCE_NOT_ASSESSED
    return round(impact, 1), phrase


def impact_level(impact: float) -> str:
    for limit, label in c.IMPACT_LEVELS:
        if impact < limit:
            return label
    return c.IMPACT_LEVELS[-1][1]


def lower_first(label: str) -> str:
    """Lowercase for use mid-sentence, but keep acronyms such as LP, DDQ, and NDAs."""
    first = label.split()[0]
    return label if first[:2].isupper() else label[0].lower() + label[1:]


def speed_label(weeks: float) -> str:
    for low, high, label in c.SPEED_BANDS:
        if low <= weeks < high:
            return label
    return c.SPEED_BANDS[-1][2]


def horizon_for(weeks: float) -> Horizon:
    if weeks < c.WEEKS_NOW:
        return Horizon.NOW
    if weeks < c.WEEKS_NEXT:
        return Horizon.NEXT
    return Horizon.LATER


def quadrant_for(weeks: float, impact: float) -> Quadrant:
    fast, high = weeks < c.QUADRANT_WEEKS, impact >= c.QUADRANT_IMPACT
    if fast:
        return Quadrant.QUICK_WINS if high else Quadrant.FILL_INS
    return Quadrant.STRATEGIC_BETS if high else Quadrant.DEPRIORITIZE


def base_solution(activity: Activity, verdict: Verdict) -> str:
    """Only an agent verdict may describe an agent, and prepare-only work stays prepare-only."""
    if activity.nature != Nature.MULTI_SYSTEM or verdict == Verdict.AGENTIC:
        return activity.solution
    return c.CUSTOM_PREPARE_SOLUTION if activity.custom else activity.solution


def tailored_text(activity: Activity, verdict: Verdict, reason: str, work: WorkstreamAnswers, answers: Answers, in_use: bool) -> Tuple[str, str, str]:
    solution = base_solution(activity, verdict)
    if verdict == Verdict.BUILD_ON:
        _, lead, first_step = build_on_text(work, answers)
        return f"{lead} {c.GOAL_PREFIX}{solution}", first_step, activity.check
    if verdict == Verdict.REMOVE:
        return c.REMOVE_SOLUTION, c.REMOVE_FIRST_STEP, c.REMOVE_CHECK
    if reason == c.REASON_REQUIRED:
        return c.REQUIRED_SOLUTION, c.REQUIRED_FIRST_STEP, c.REMOVE_CHECK
    if reason == c.REASON_RESTRICTED_IN_USE:
        return c.RESTRICTED_IN_USE_SOLUTION, c.RESTRICTED_IN_USE_FIRST_STEP, c.NEUTRAL_CHECK
    if reason == c.REASON_HEADS:
        return c.HEADS_SOLUTION, c.HEADS_FIRST_STEP, c.NEUTRAL_CHECK
    if reason == c.REASON_RESTRICTED:
        return c.RESTRICTED_SOLUTION, c.RESTRICTED_FIRST_STEP, c.NEUTRAL_CHECK
    if verdict == Verdict.LEAVE and (in_use or answers.policy == Policy.RESTRICTED.value):
        return AI_CLAUSE.sub("", solution), activity.first_step, activity.check
    if verdict == Verdict.ADD_AI and activity.nature == Nature.MULTI_SYSTEM and not activity.custom:
        return c.PREPARE_PREFIX + solution, activity.first_step, activity.check
    return solution, activity.first_step, activity.check


def relevance_note(verdict: Verdict, phrase: str, kpi_text: str) -> str:
    """Writing a process down or stopping work does not itself move a KPI, so it never says it does."""
    if verdict == Verdict.LEAVE:
        return ""
    if verdict == Verdict.OPTIMIZE:
        return c.OPTIMIZE_RELEVANCE.format(kpi=kpi_text)
    if verdict == Verdict.REMOVE:
        return c.REMOVE_RELEVANCE
    return phrase.format(kpi=kpi_text)


def custom_activities(work: WorkstreamAnswers) -> List[Activity]:
    rows = []
    for index, item in enumerate(work.custom):
        nature = Nature(item[c.KEY_NATURE])
        rows.append(Activity(f"custom_{work.id}_{index}", work.id, item[c.KEY_NAME], nature, {}, c.CUSTOM_SOLUTIONS[nature], c.CUSTOM_FIRST_STEP, c.CUSTOM_CHECK, custom=True, kpi_link=item.get(c.KEY_KPI_LINK)))
    return rows


def priority(item: ScoredActivity) -> Tuple[float, str]:
    speed_bonus = 1.0 - min(item.weeks or c.WEEKS_AXIS_MAX, c.WEEKS_LATER) / c.WEEKS_LATER
    return (-(item.impact * (1.0 + 0.5 * speed_bonus)), item.label)


def evidence_for(work: WorkstreamAnswers, answers: Answers) -> str:
    """Only what they actually said. A skipped answer never becomes 'you reported'."""
    told = lambda field: f"{work.id}.{field}" not in answers.skipped
    parts = []
    if told("hours"):
        parts.append(f"{c.HOURS_PHRASES[work.hours]} a month")
    if told("data"):
        parts.append(f"mostly {c.DATA_PHRASES[work.data]}")
    if told("owner"):
        parts.append(f"led by {c.OWNER_PHRASES[work.owner]}")
    return f"You reported: {', '.join(parts)}." if parts else ""


def foundations_for(answers: Answers) -> List[Tuple[str, str, str]]:
    uses_ai = answers.ai_stage != AiStage.NONE.value and "ai_stage" not in answers.skipped
    no_policy = answers.policy == Policy.NONE.value and "policy" not in answers.skipped
    restricted = answers.policy == Policy.RESTRICTED.value
    found: List[Tuple[str, str, str]] = []
    if uses_ai and no_policy:
        found.append(c.SHADOW_FOUNDATION)
    elif uses_ai and restricted:
        found.append(c.SHADOW_RESTRICTED_FOUNDATION)
    for field in ("ai_results", "policy", "ai_obstacle", "systems", "trust", "capacity"):
        if field in answers.skipped or (field == "policy" and uses_ai) or (field == "ai_results" and not uses_ai):
            continue
        item = c.FOUNDATIONS.get((field, getattr(answers, field)))
        if item and all(item[0] != existing[0] for existing in found):
            found.append(item)
    return found


def score_answers(library: Library, answers: Answers) -> Plan:
    kpi_text = lower_first(library.kpis[answers.kpi]["label"])
    items: List[ScoredActivity] = []
    hours_low, hours_high, open_ended, hours_known = 0, 0, False, False

    for work in answers.workstreams:
        meta = library.workstreams[work.id]
        if f"{work.id}.hours" not in answers.skipped:
            hours_known = True
            low, high = c.HOURS_RANGE[work.hours]
            hours_low += low
            if high is None:
                open_ended = True
            else:
                hours_high += high
        evidence = evidence_for(work, answers)
        unknown_area = f"{work.id}.ai_here" in answers.skipped
        assumed_all = work.ai_here != AiHere.NONE.value and not work.ai_tasks

        activities = [library.activities[activity_id] for activity_id in work.activities] + custom_activities(work)
        using = in_use_ids(work, activities)
        custom_flags = {activity.id: item.get(c.KEY_USES_AI) for activity, item in zip((row for row in activities if row.custom), work.custom)}
        for activity in activities:
            in_use = activity.id in using
            verdict, reason = decide_verdict(activity, work, answers, in_use)
            impact, phrase = estimate_impact(activity, work, answers, meta["area"])
            if verdict in (Verdict.OPTIMIZE, Verdict.REMOVE):
                impact = min(impact, c.LOW_EFFORT_IMPACT_CAP)
            solution, first_step, check = tailored_text(activity, verdict, reason, work, answers, in_use)
            custom_unknown = activity.custom and custom_flags.get(activity.id) is None and answers.ai_stage != AiStage.NONE.value
            if (unknown_area or custom_unknown) and not in_use and verdict in c.AI_VERDICTS:
                reason = c.REASON_AI_UNKNOWN + reason
                first_step = c.AI_UNKNOWN_FIRST_STEP
            people = verdict == Verdict.LEAVE
            weeks = None if people else estimate_weeks(activity, verdict, work, answers)
            note = ""
            if in_use:
                note = c.AI_ASSUMED_NOTE if assumed_all and not activity.custom else c.HERE_PHRASES[in_use_stage(work)]
            items.append(ScoredActivity(
                0, activity.label, meta["label"], verdict, reason, evidence,
                relevance_note(verdict, phrase, kpi_text), solution, first_step, check,
                weeks, "" if people else speed_label(weeks), impact,
                None if people else horizon_for(weeks), None if people else quadrant_for(weeks, impact), activity.custom,
                activity_id=activity.id, thesis_note=answers.thesis_notes.get(activity.id, ""),
                route="" if people else route_for(verdict, answers),
                ai_note=note, owner_role=meta["owner"],
            ))

    plotted = sorted((item for item in items if item.verdict != Verdict.LEAVE), key=priority)
    leave = sorted((item for item in items if item.verdict == Verdict.LEAVE), key=lambda item: item.label)
    for number, item in enumerate(plotted + leave, start=1):
        item.number = number

    assessed = {work.id for work in answers.workstreams}
    not_assessed = [row["label"] for row in library.catalog["workstreams"] if row["id"] not in assessed]
    return Plan(plotted + leave, foundations_for(answers), hours_low, None if open_ended else hours_high, hours_known, not_assessed)
