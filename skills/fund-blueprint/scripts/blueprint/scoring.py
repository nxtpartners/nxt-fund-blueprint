"""Deterministic scoring: the same answers always give the same plan. The catalog supplies priors; the firm's answers decide."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Set, Tuple

from . import constants as c
from .data import Library
from .enums import AiHere, AiStage, Capacity, Depth, ErrorCost, Horizon, KpiClaim, Nature, Policy, Quadrant, Rhythm, Rule, Source, Systems, TimeGoes, Trust, Verdict, Who, Spend
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
    reading: List[str] = field(default_factory=list)
    start_line: str = ""
    start_moves: List[int] = field(default_factory=list)
    changes: List[str] = field(default_factory=list)
    measure_rows: List[Tuple[str, str, int, str, str]] = field(default_factory=list)
    measure_actions: List[Tuple[str, str]] = field(default_factory=list)
    focus_missing: List[str] = field(default_factory=list)
    walkthroughs: Dict[str, List[str]] = field(default_factory=dict)
    budget: str = ""
    stuck: List[Tuple[str, List[str]]] = field(default_factory=list)
    people_elsewhere: List[str] = field(default_factory=list)

    @property
    def plotted(self) -> List[ScoredActivity]:
        return [item for item in self.items if item.verdict != Verdict.LEAVE]

    @property
    def people(self) -> List[ScoredActivity]:
        return [item for item in self.items if item.verdict == Verdict.LEAVE]

    @property
    def top(self) -> List[ScoredActivity]:
        return self.plotted[:3]


# Source predicates: the only place that knows what a mix of sources means.
def has_documents(work: WorkstreamAnswers) -> bool:
    return Source.DOCUMENTS.value in work.sources or Source.EMAIL.value in work.sources


def has_system(work: WorkstreamAnswers) -> bool:
    return Source.SYSTEM.value in work.sources


def join_words(words: List[str]) -> str:
    if len(words) < 3:
        return " and ".join(words)
    return f"{', '.join(words[:-1])}, and {words[-1]}"


def sources_text(sources: List[str]) -> str:
    return join_words([c.SOURCE_PHRASES[source] for source in sources])


def doc_sources_text(work: WorkstreamAnswers) -> str:
    return join_words([c.SOURCE_PHRASES[source] for source in work.sources if source in (Source.DOCUMENTS.value, Source.EMAIL.value)])


def told(answers: Answers, field_name: str) -> bool:
    return field_name not in answers.skipped


def told_here(work: WorkstreamAnswers, answers: Answers, field_name: str) -> bool:
    return f"{work.id}.{field_name}" not in answers.skipped and field_name not in work.unasked


def firm_uses_ai(answers: Answers) -> bool:
    stated = told(answers, "ai_stage") and answers.ai_stage != AiStage.NONE.value
    in_work = any(work.ai_here != AiHere.NONE.value or any(item.get(c.KEY_USES_AI) for item in work.custom) for work in answers.workstreams)
    return stated or in_work


def stage_for(activity: Activity, work: WorkstreamAnswers) -> str:
    """A custom task's AI use is its own answer, separate from the work area's."""
    if activity.custom or work.ai_here == AiHere.NONE.value:
        return c.DEFAULT_IN_USE_STAGE
    return work.ai_here


def build_on_text(activity: Activity, work: WorkstreamAnswers, answers: Answers) -> Tuple[str, str, str]:
    """Reason, solution, and first step for AI that already exists in this work."""
    table = c.BUILD_ON_TEXT
    stage = stage_for(activity, work)
    return table.get((stage, answers.ai_results)) or table[(stage, "any")]


def risky(activity: Activity, work: WorkstreamAnswers) -> bool:
    """Serious harm can be narrowed to named tasks. Anything not named, or unsure, stays cautious."""
    if work.error_cost == ErrorCost.UNSURE.value:
        return True
    if work.error_cost != ErrorCost.SEVERE.value:
        return False
    return activity.custom or not work.harm_tasks or activity.id in work.harm_tasks


def serious_work(activity: Activity, work: WorkstreamAnswers) -> bool:
    return activity.required or risky(activity, work)


def route_for(activity: Activity, rule: Rule, verdict: Verdict, work: WorkstreamAnswers, answers: Answers) -> Tuple[str, Spend]:
    """Where the work could run, and the money that takes. One place, so the two never disagree."""
    if rule == Rule.OUTSIDE:
        return c.OUTSIDE_ROUTE, Spend.NONE
    stage = stage_for(activity, work)
    informal = stage == c.INFORMAL_STAGE or (stage == c.DEFAULT_IN_USE_STAGE and answers.policy != Policy.APPROVED.value)
    if verdict == Verdict.BUILD_ON and informal:
        return c.ROUTES[(Verdict.BUILD_ON, "informal")], Spend.SMALL
    tier = c.BUDGET_TIER.get(answers.budget) or c.TEAM_ROUTE_TIER[answers.team]
    if verdict == Verdict.ADD_AI:
        if answers.policy == Policy.NONE.value:
            return c.ROUTES[(Verdict.ADD_AI, "no_policy")], Spend.SMALL
        own = next((text for tool, text in c.TOOL_ROUTES if firm_uses_ai(answers) and tool in answers.ai_tools and not (tool == "assistants" and serious_work(activity, work))), "")
        if serious_work(activity, work):
            return (c.ROUTES[(Verdict.ADD_AI, "careful_own")].format(tool=own), Spend.NONE) if own else (c.ROUTES[(Verdict.ADD_AI, "careful")], Spend.DECISION)
        if own:
            return own, Spend.NONE
    if verdict == Verdict.AUTOMATE and answers.systems == c.INTEGRATED_SYSTEMS:
        return c.ROUTE_INTEGRATED, Spend.NONE
    if verdict == Verdict.AGENTIC and Capacity.IN_HOUSE.value in answers.capacity:
        return c.ROUTES[(Verdict.AGENTIC, "own_team")], Spend.SMALL
    if verdict == Verdict.AGENTIC and answers.policy == Policy.PILOT.value:
        return c.ROUTES[(Verdict.AGENTIC, "trial")], Spend.DECISION
    if verdict in (Verdict.OPTIMIZE, Verdict.REMOVE, Verdict.BUILD_ON):
        return c.ROUTES.get((verdict, "any"), ""), Spend.NONE
    return c.ROUTES.get((verdict, tier), ""), Spend.DECISION if verdict == Verdict.AGENTIC or tier == "high" else Spend.SMALL


def money_line(spend: Spend, fits: bool, budget: str) -> str:
    if spend == Spend.NONE:
        return c.SPEND_LABELS[spend]
    return c.SPEND_LABELS[spend] + c.SPEND_ENDINGS[budget][0 if fits else 1]


def in_use_ids(work: WorkstreamAnswers, activities: List[Activity]) -> Set[str]:
    """Which tasks already use AI. If they did not say which, assume all of them, so nobody is told to add it."""
    if work.ai_here == AiHere.NONE.value:
        found: Set[str] = set()
    elif work.ai_tasks:
        found = set(work.ai_tasks)
    else:
        found = {activity.id for activity in activities if not activity.custom and activity.nature not in HUMAN_NATURES}
    customs = [activity for activity in activities if activity.custom]
    for activity, item in zip(customs, work.custom):
        if item.get(c.KEY_USES_AI):
            found.add(activity.id)
    return found


def agent_blocker(activity: Activity, work: WorkstreamAnswers, answers: Answers, anchored: bool = True) -> str:
    """First hit wins, and the reason shown names the answer that actually blocks it."""
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
    if told(answers, "capacity") and answers.capacity == [Capacity.NOBODY.value]:
        return "capacity"
    if told(answers, "systems") and answers.systems == Systems.MANUAL.value:
        return "systems_manual"
    if told(answers, "systems") and answers.systems == Systems.DISCONNECTED.value:
        return "systems_disconnected"
    if not told_here(work, answers, "sources"):
        return "sources_unknown"
    if not has_system(work):
        return "sources"
    if Source.EMAIL.value in work.sources and answers.policy != Policy.APPROVED.value:
        return "email"
    if anchored and TimeGoes.REKEY.value in work.time_goes:
        return "rekey"
    return ""


def decide_rule(activity: Activity, work: WorkstreamAnswers, answers: Answers, in_use: bool, relevance: int, anchored: bool) -> Rule:
    """Ordered on purpose: never automate a step that should not exist, and never add what is already there.

    Where the time goes was asked about the hardest task, so those rules touch that task only.
    """
    nature = activity.nature
    restricted = answers.policy == Policy.RESTRICTED.value
    process_flexible = not activity.control and anchored
    if nature in HUMAN_NATURES:
        return Rule.LEAVE
    if activity.id in work.legacy_tasks:
        if activity.control:
            return Rule.KEEP_CONTROL
        if activity.required or risky(activity, work):
            return Rule.KEEP_MINIMAL
        if relevance >= c.LINKED_RELEVANCE_MIN or work.id in answers.thesis_focus:
            return Rule.LEGACY_CHECK
        return Rule.REMOVE
    if in_use:
        return Rule.PAUSE_USE if restricted else Rule.BUILD_ON
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
    if TimeGoes.WAIT_SIGNOFF.value in work.time_goes and nature != Nature.DRAFTING and not activity.required and process_flexible:
        return Rule.SIGNOFFS
    if anchored and work.rhythm == Rhythm.PERIODIC.value and work.hours == "under_20" and nature == Nature.RULES:
        return Rule.TEMPLATE_ENOUGH
    if nature == Nature.RULES:
        if activity.custom:
            if has_documents(work):
                if restricted:
                    return Rule.RESTRICTED
                if answers.policy != Policy.APPROVED.value:
                    return Rule.CUSTOM_WRITE_RULES
                return Rule.DOCS_REVIEW if serious_work(activity, work) else Rule.CUSTOM_RULES
            return Rule.CUSTOM_RULES
        if activity.needs_agreed_rules and not has_system(work):
            return Rule.AGREE_FIRST
        if has_documents(work) and activity.reads_documents:
            if restricted:
                return Rule.RESTRICTED
            unsettled = answers.ai_results != "measured" or answers.systems in (Systems.DISCONNECTED.value, Systems.MANUAL.value)
            if serious_work(activity, work) and activity.process_solution and unsettled:
                return Rule.SERIOUS_PROCESS_FIRST
            return Rule.DOCS_REVIEW if serious_work(activity, work) else Rule.DOCS_PLAIN
        return Rule.AUTOMATE
    if restricted:
        return Rule.RESTRICTED
    if nature == Nature.DRAFTING:
        return Rule.DRAFT
    if not has_system(work) and not activity.custom and not activity.required:
        return Rule.ONE_PLACE
    if anchored and TimeGoes.REKEY.value in work.time_goes and not has_documents(work) and has_system(work):
        return Rule.REKEY_AUTOMATE
    unsettled = answers.ai_results != "measured" or answers.systems in (Systems.DISCONNECTED.value, Systems.MANUAL.value)
    if serious_work(activity, work) and activity.process_solution and unsettled:
        return Rule.SERIOUS_PROCESS_FIRST
    if activity.no_agent:
        return Rule.NO_AGENT
    if risky(activity, work):
        return Rule.SEVERE_MULTI
    return Rule.AGENT_BLOCKED if agent_blocker(activity, work, answers, anchored) else Rule.AGENT


def worst(table: Dict[str, float], values: List[str]) -> float:
    return max(table[value] for value in values)


def capacity_factor(answers: Answers) -> float:
    """Several ways to do the work: the fastest counts, and 'nobody' only when it stands alone."""
    usable = [value for value in answers.capacity if value != Capacity.NOBODY.value] or answers.capacity
    return min(c.WEEKS_CAPACITY[value] for value in usable)


def source_drag(work: WorkstreamAnswers) -> float:
    return worst(c.WEEKS_SOURCE, work.sources) - 1 + c.WEEKS_EXTRA_SOURCE * (len(work.sources) - 1)


def estimate_weeks(activity: Activity, verdict: Verdict, work: WorkstreamAnswers, answers: Answers, anchored: bool = True) -> float:
    """Delays add up rather than multiply: several blockers can share one fix."""
    if verdict == Verdict.BUILD_ON:
        drag = (c.WEEKS_POLICY[answers.policy] - 1) + (worst(c.WEEKS_TRUST, answers.trust) - 1) + (c.WEEKS_ADOPTION[answers.ai_adoption] - 1)
        return round(c.BUILD_ON_WEEKS[stage_for(activity, work)] * max(1.0 + drag, c.WEEKS_MIN_FACTOR), 1)
    weeks = c.BASE_WEEKS[verdict]
    if verdict == Verdict.REMOVE:
        return weeks
    if verdict == Verdict.OPTIMIZE:
        return round(weeks * c.WEEKS_EFFORT[activity.effort], 1)
    drag = source_drag(work) + (c.WEEKS_SYSTEMS[answers.systems] - 1) + (capacity_factor(answers) - 1) + (c.WEEKS_ERROR[work.error_cost] - 1)
    if anchored and TimeGoes.WAIT_OUTSIDE.value in work.time_goes:
        drag += c.WEEKS_WAIT_OUTSIDE - 1
    if verdict in c.AI_VERDICTS:
        drag += (c.WEEKS_POLICY[answers.policy] - 1) + (worst(c.WEEKS_TRUST, answers.trust) - 1)
        drag += (c.WEEKS_EXPERIENCE[answers.ai_stage] - 1) + (c.WEEKS_RESULTS[answers.ai_results] - 1) + (c.WEEKS_ADOPTION[answers.ai_adoption] - 1)
    return min(round(weeks * c.WEEKS_EFFORT[activity.effort] * max(1.0 + drag, c.WEEKS_MIN_FACTOR), 1), c.WEEKS_AXIS_MAX)


def relevance_for(activity: Activity, work: WorkstreamAnswers, answers: Answers, library: Library) -> Tuple[int, str]:
    """Link to the fund KPI: the catalog's prior, or the path through a department measure, whichever is stronger. Every task has a link."""
    if answers.kpi == c.CUSTOM_KPI:
        link = answers.kpi_links.get(activity.id) or answers.kpi_links.get(activity.label) or activity.kpi_link
        return (c.KPI_LINK_RELEVANCE[link] if link else c.CUSTOM_DEFAULT_RELEVANCE), ""
    if activity.custom:
        return (c.KPI_LINK_RELEVANCE[activity.kpi_link] if activity.kpi_link else c.CUSTOM_DEFAULT_RELEVANCE), ""
    prior = activity.kpis.get(answers.kpi, 0)
    relevance, measure_label = prior, ""
    for measure in library.measures_for(work.id):
        if activity.id in measure["tasks"]:
            link = min(measure["links"].get(answers.kpi, 0), prior + 1)
            if link and link >= relevance:
                relevance, measure_label = link, "" if measure.get("same_as") == answers.kpi else measure["label"]
    if answers.kpi == c.SENIOR_KPI:
        relevance = min(relevance, max(c.SENIOR_LINK_CAP[who] for who in work.who))
    return relevance, measure_label


def task_value(activity: Activity, work: WorkstreamAnswers, activities: List[Activity], anchored: bool = True) -> float:
    """Hours times seniority, shared across the work area's tasks. Used for order, and never shown as a number."""
    active = [row for row in activities if row.nature not in HUMAN_NATURES]
    weight = lambda row: c.HEAVY_TASK_SHARE if row.id == work.heavy_task else 1.0
    share = weight(activity) / (sum(weight(row) for row in active) or 1.0)
    hours = c.HOURS_MIDPOINT[work.hours] * share
    rate = sum(c.WHO_RATE[who] for who in work.who) / len(work.who)
    value = math.log(1 + hours * rate) / math.log(1 + c.VALUE_CEILING)
    if anchored and work.rhythm == Rhythm.STEADY.value:
        value *= c.STEADY_VALUE_FACTOR
    return min(value, 1.0)


def measure_off_here(activity: Activity, work: WorkstreamAnswers, library: Library) -> str:
    for measure in library.measures_for(work.id):
        if measure["id"] in work.measures_off and activity.id in measure["tasks"]:
            return measure["label"]
    return ""


def estimate_impact(activity: Activity, work: WorkstreamAnswers, answers: Answers, area: str, relevance: int, value: float, off_target: str) -> float:
    score = (relevance + c.RELEVANCE_FLOOR) / (c.RELEVANCE_MAX + c.RELEVANCE_FLOOR) * (c.EFFECT_VALUE_FLOOR + (1 - c.EFFECT_VALUE_FLOOR) * value)
    if (told(answers, "thesis") and work.id in c.THESIS_WORKSTREAMS.get(answers.thesis, ())) or work.id in answers.thesis_focus:
        score += c.IMPACT_BOOST
    if any(area in c.STAGE_AREAS[stage] for stage in answers.fund_stage):
        score += c.IMPACT_BOOST
    if off_target:
        score += c.IMPACT_BOOST
    return round(c.IMPACT_MIN + (c.IMPACT_MAX - c.IMPACT_MIN) * min(score, 1.0), 1)


def impact_level(impact: float) -> str:
    for limit, label in c.IMPACT_LEVELS:
        if impact < limit:
            return label
    return c.IMPACT_LEVELS[-1][1]


def relative_levels(items: List[ScoredActivity]) -> None:
    """High, Medium, and Low compare this firm's own moves. Work that does not itself move the number, such as pausing, stays Low."""
    for item in items:
        item.raw_impact = item.impact
    ranked = [item for item in items if c.RULES[item.rule]["claim"] != KpiClaim.NONE]
    key = lambda item: (c.RULES[item.rule]["claim"] != KpiClaim.PREPARES, item.off_measure, item.relevance, item.raw_impact, round(item.value, 3))
    strongest = max((item.relevance for item in ranked), default=0)
    order = sorted((key(item) for item in ranked), reverse=True)
    for item in items:
        if item not in ranked:
            level = c.RELATIVE_TIERS[-1]
        elif len(set(order)) == 1:
            level = c.RELATIVE_TIERS[1]
        else:
            level = c.RELATIVE_TIERS[min(order.index(key(item)) * len(c.RELATIVE_TIERS) // len(order), len(c.RELATIVE_TIERS) - 1)]
        if (c.RULES[item.rule]["claim"] == KpiClaim.PREPARES or item.relevance == 0 or item.relevance < strongest) and level == c.RELATIVE_TIERS[0]:
            level = c.RELATIVE_TIERS[1]
        if item.relevance == 0 and strongest > 0:
            level = c.RELATIVE_TIERS[-1]
        item.impact = c.RELATIVE_IMPACT[level]
        item.quadrant = quadrant_for(item.weeks, item.impact)
        item.speed_band = next(index for index, band in enumerate(c.SPEED_BANDS) if band[2] == item.speed_label)


def effect_text(impact: float, kpi_text: str = "") -> str:
    return f"{impact_level(impact)} effect on {kpi_text}" if kpi_text else impact_level(impact)


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


def serious_documents(activity: Activity, work: WorkstreamAnswers) -> bool:
    return serious_work(activity, work) and has_documents(work)


def not_ready_for_ai_step(answers: Answers) -> bool:
    return answers.policy in (Policy.NONE.value, Policy.RESTRICTED.value) or not told(answers, "policy")


def plan_first_step(activity: Activity, answers: Answers, verdict: Verdict) -> str:
    """Keep the specific step, and use the version that needs no AI where the move or the firm does not use AI."""
    no_ai = verdict not in c.AI_VERDICTS and verdict != Verdict.BUILD_ON
    if activity.first_step_if_no_ai and (answers.ai_stage == AiStage.NONE.value or (activity.first_step_uses_ai and (no_ai or not_ready_for_ai_step(answers)))):
        return activity.first_step_if_no_ai
    return activity.first_step


def human_check(row: dict, activity: Activity, work: WorkstreamAnswers, verdict: Verdict, in_use: bool) -> str:
    """A rule may add to a safeguard, and never replace it. Text about AI tools appears only where AI is in play."""
    ai_in_play = in_use or verdict in c.AI_VERDICTS or verdict == Verdict.BUILD_ON
    parts = [row.get("check"), activity.check, activity.check_ai if ai_in_play else ""]
    if activity.custom and activity.nature not in HUMAN_NATURES and risky(activity, work):
        parts.append(c.CUSTOM_SERIOUS_CHECK)
    return " ".join(part for part in parts if part)


def tailored_text(activity: Activity, rule: Rule, work: WorkstreamAnswers, answers: Answers, in_use: bool) -> Tuple[str, str, str]:
    row = c.RULES[rule]
    verdict = row["verdict"]
    task = lower_first(activity.label)
    if rule == Rule.BUILD_ON:
        _, lead, first_step = build_on_text(activity, work, answers)
        prefix = c.DEPLOYED_GOAL_PREFIX if stage_for(activity, work) == AiHere.DEPLOYED.value else c.GOAL_PREFIX
        goal = base_solution(activity, verdict)
        text = f"{lead} {prefix}{goal[0].lower()}{goal[1:]}"
        return text + (c.DOCS_REVIEW_SUFFIX if serious_documents(activity, work) else ""), first_step.replace("{task}", task), human_check({}, activity, work, verdict, in_use)
    if rule == Rule.LEAVE and (in_use or answers.policy == Policy.RESTRICTED.value):
        return AI_CLAUSE.sub("", activity.solution), activity.first_step.replace("{task}", task), human_check({}, activity, work, verdict, in_use)
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
        stated = work.error_cost == ErrorCost.SEVERE.value and told_here(work, answers, "error_cost") and risky(activity, work)
        return row["reason"] if stated else row["reason_unknown"]
    if rule == Rule.LEGACY_CHECK:
        return row["reason"].format(kpi=kpi_text)
    return row["reason"]


def relevance_note(rule: Rule, claim: KpiClaim, relevance: int, kpi_text: str) -> str:
    """One ladder for the link everywhere. Pausing or stopping work does not itself move a KPI, so it never says it does."""
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


def custom_activities(work: WorkstreamAnswers) -> List[Activity]:
    rows = []
    for index, item in enumerate(work.custom):
        nature = Nature(item[c.KEY_NATURE])
        rows.append(Activity(f"custom_{work.id}_{index}", work.id, item[c.KEY_NAME], nature, {}, c.CUSTOM_SOLUTIONS[nature], c.CUSTOM_FIRST_STEP, c.CUSTOM_CHECK, custom=True, kpi_link=item.get(c.KEY_KPI_LINK)))
    return rows


def priority(item: ScoredActivity, status: str = "", boost_named: bool = True) -> Tuple[float, int, str]:
    """Named work wins ties. Off-target numbers weigh effect more, and on-target numbers weigh hours more."""
    speed_bonus = 1.0 - min(item.weeks or c.WEEKS_AXIS_MAX, c.WEEKS_LATER) / c.WEEKS_LATER
    effect = ((item.raw_impact or item.impact) - c.IMPACT_MIN) / (c.IMPACT_MAX - c.IMPACT_MIN)
    weight_effect, weight_value = c.PRIORITY_WEIGHTS_BY_STATUS.get(status, (c.PRIORITY_WEIGHT_IMPACT, c.PRIORITY_WEIGHT_VALUE))
    base = (weight_effect * effect + weight_value * item.value) * (1.0 + c.PRIORITY_SPEED_BONUS * speed_bonus)
    if item.relevance == 0 and not item.named:
        base *= c.NO_LINK_PRIORITY_FACTOR
    if item.named and boost_named:
        base *= c.NAMED_PRIORITY_FACTOR
    return (-round(base, 4), 0 if item.named else 1, item.label)


def hardest_task_label(work: WorkstreamAnswers, answers: Answers, library: Library) -> str:
    """Some questions ask about the hardest task, so what they said is quoted for that task."""
    if answers.named_task:
        if answers.named_task in work.activities:
            return library.activities[answers.named_task].label
        if any(item[c.KEY_NAME] == answers.named_task for item in work.custom):
            return answers.named_task
    return library.activities[work.heavy_task].label if work.heavy_task else ""


def evidence_for(work: WorkstreamAnswers, answers: Answers, library: Library) -> str:
    """Only what they actually said. A skipped or unasked answer never becomes 'you reported'."""
    area = []
    if told_here(work, answers, "hours"):
        area.append(f"{c.HOURS_PHRASES[work.hours]} a month")
    if told_here(work, answers, "sources"):
        area.append(f"information in {sources_text(work.sources)}")
    if told_here(work, answers, "who"):
        area.append(f"worked on by {join_words([c.WHO_PHRASES[who] for who in work.who])}")
    if told_here(work, answers, "error_cost"):
        area.append(c.ERROR_PHRASES[work.error_cost])
    hardest = []
    if told_here(work, answers, "time_goes") and work.time_goes:
        hardest.append(f"time going on {join_words([c.TIME_PHRASES[item] for item in work.time_goes])}")
    if told_here(work, answers, "depends"):
        hardest.append(c.DEPENDS_PHRASES[work.depends])
    if told_here(work, answers, "rhythm"):
        hardest.append(c.RHYTHM_PHRASES[work.rhythm])
    if told_here(work, answers, "same_way"):
        hardest.append(c.SAME_WAY_PHRASES[work.same_way])
    label = hardest_task_label(work, answers, library)
    if not label:
        area, hardest = area + hardest, []
    text = f"You reported: {', '.join(area)}." if area else ""
    if hardest:
        text = f"{text} {c.HARDEST_FACTS.format(task=lower_first(label), facts=', '.join(hardest))}".strip()
    return text


def why_line(item_named: bool, reason: str, relevance: int, linked: bool, kpi_text: str, off_target: str, slow_step: str = "") -> str:
    """The rule's reason, which reasons from the answer, plus what links it to the number. Facts about the work area stay in its group line."""
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


def add_comparison(plotted: List[ScoredActivity], kpi_text: str, status: str, money_ordered: bool = False) -> None:
    """Say why the first move leads over the second, using the same score that ranked them."""
    if len(plotted) < 2:
        return
    first, second = plotted[0], plotted[1]
    next_task = lower_first(second.label)
    if money_ordered and first.fits and not second.fits:
        line = c.LEADS_BUDGET.format(next_task=next_task)
    elif first.named and priority(first, status, boost_named=False)[0] > priority(second, status, boost_named=False)[0]:
        line = c.LEADS_NAMED
    elif priority(first, status)[0] == priority(second, status)[0]:
        line = c.LEADS_TIE.format(next_task=next_task)
    elif first.kpi_linked and first.relevance > second.relevance:
        line = c.LEADS_MORE_DIRECT.format(kpi=kpi_text, next_task=next_task)
    elif first.value > second.value:
        line = c.LEADS_MORE_HOURS.format(next_task=next_task)
    elif first.speed_label != second.speed_label and (first.weeks or 0) < (second.weeks or 0):
        line = c.LEADS_FASTER.format(next_task=next_task)
    else:
        return
    first.why_line = f"{first.why_line} {line}".strip()


def foundations_for(answers: Answers, library: Library, top_label: str, items: List[ScoredActivity]) -> List[Tuple[str, str, str]]:
    """What must come first. Connecting data matters only when a move adds software."""
    needs_software = any(item.verdict in c.TECH_VERDICTS for item in items)
    return [row for row in foundation_rows(answers, library, top_label, items) if needs_software or row[0] != c.CONNECT_DATA_TITLE]


def foundation_rows(answers: Answers, library: Library, top_label: str, items: List[ScoredActivity]) -> List[Tuple[str, str, str]]:
    uses_ai = firm_uses_ai(answers)
    restricted = answers.policy == Policy.RESTRICTED.value
    kpi = library.kpi_view(answers.kpi, answers.kpi_name)
    kpi_text, baseline = lower_first(kpi["label"]), kpi["baseline"]
    found: List[Tuple[str, str, str]] = []
    if uses_ai and answers.policy == Policy.NONE.value and told(answers, "policy"):
        found.append(c.SHADOW_FOUNDATION)
    elif uses_ai and restricted:
        found.append(c.SHADOW_RESTRICTED_FOUNDATION)
    if told(answers, "capacity") and answers.capacity == [Capacity.NOBODY.value]:
        found.append(c.OWNER_FOUNDATION)
    title, text, action = c.ONE_PERSON_FOUNDATION
    held = [work for work in answers.workstreams if work.depends == "no" and told_here(work, answers, "depends")]
    for work in held:
        area = lower_first(library.workstreams[work.id]["label"])
        label = hardest_task_label(work, answers, library)
        subject = lower_first(label) if label else area
        harm = c.ONE_PERSON_HARM if work.error_cost == ErrorCost.SEVERE.value and told_here(work, answers, "error_cost") else ""
        found.append((f"{title}: {area}" if len(held) > 1 else title, text.format(subject=subject, harm=harm), action.format(subject=subject)))
    keys: List[Tuple[str, str]] = []
    if told(answers, "kpi_status"):
        keys.append(("kpi_status", answers.kpi_status))
    shared = [item.label for item in items if item.activity_id and library.activities.get(item.activity_id) and library.activities[item.activity_id].shared_data and item.verdict != Verdict.LEAVE]
    if len(shared) >= 2:
        title, text, action = c.SHARED_DATA_FOUNDATION
        found.append((title, text.format(count=len(shared), tasks=join_words([lower_first(label) for label in shared])), action))
    if uses_ai and told(answers, "ai_results"):
        keys.append(("ai_results", answers.ai_results))
    if uses_ai and told(answers, "ai_adoption"):
        keys.append(("ai_adoption", answers.ai_adoption))
    if not uses_ai and told(answers, "policy"):
        keys.append(("policy", answers.policy))
    if told(answers, "systems"):
        keys.append(("systems", answers.systems))
    if told(answers, "trust") and not (restricted and not uses_ai):
        keys += [("trust", value) for value in answers.trust]
    seen_actions: Set[str] = {row[2] for row in found}
    for key in keys:
        row = c.FOUNDATIONS.get(key)
        if not row:
            continue
        fill = lambda text: text.format(kpi=kpi_text, baseline=baseline, task=lower_first(top_label) if top_label else "your first move")
        title, text, action = fill(row[0]), fill(row[1]), fill(row[2])
        if action not in seen_actions:
            seen_actions.add(action)
            found.append((title[0].upper() + title[1:], text, action))
    return found


def verdict_counts(plan_items: List[ScoredActivity]) -> str:
    counts: Dict[Verdict, int] = {}
    for item in plan_items:
        counts[item.verdict] = counts.get(item.verdict, 0) + 1
    return join_words([f"{count} {c.COUNT_WORDS[verdict][0 if count == 1 else 1]}" for verdict, count in counts.items()])


def named_reason(named: ScoredActivity, plotted: List[ScoredActivity], lifted: bool, kpi_text: str, money_ordered: bool = False) -> str:
    """The reason given must be true of the moves actually above it."""
    if money_ordered and not named.fits:
        place = plotted.index(named)
        if any(item.fits for item in plotted[place + 1 :]):
            return c.NAMED_REASON_BUDGET_LIFTED
        if any(item.fits for item in plotted[:place]):
            return c.NAMED_REASON_BUDGET
    if lifted:
        return c.NAMED_REASON_LIFTED
    above = plotted[: plotted.index(named)]
    subject = ("The move above it", "the move above it", "has") if len(above) == 1 else ("The moves above it", "the moves above it", "have")
    if all(item.relevance > named.relevance for item in above):
        return c.NAMED_REASON_CLOSER.format(above=f"{subject[0]} {subject[2]}", kpi=kpi_text)
    if all(item.value > named.value for item in above):
        return c.NAMED_REASON_TIME.format(above_lower=subject[1])
    return c.NAMED_REASON_SCORE.format(above=f"{subject[0]} {subject[2]}")


def read_together(answers: Answers, items: List[ScoredActivity], library: Library, kpi_text: str, lifted: bool = False) -> List[str]:
    """What the answers mean side by side. Only their own answers and the plan's own counts, so nothing is invented."""
    plotted = [item for item in items if item.verdict != Verdict.LEAVE]
    lines: List[str] = []
    named = next((item for item in items if item.named), None)
    if named and named.verdict == Verdict.LEAVE:
        lines.append(f"You named {lower_first(named.label)} as the task to take off your team. It rests on judgment or relationships, so it stays with your people, and the moves below work around it.")
    elif named:
        position = plotted.index(named) + 1
        lines.append(c.NAMED_FIRST.format(task=lower_first(named.label)) if position == 1 else c.NAMED_LATER.format(task=lower_first(named.label), position=position, reason=named_reason(named, plotted, lifted, kpi_text, answers.budget in c.BUDGET_REORDERS)))
    assessed = {work.id for work in answers.workstreams}
    drivers = [row for row in library.catalog["workstreams"] if any(measure["links"].get(answers.kpi) == c.RELEVANCE_MAX for measure in row["measures"])]
    if drivers and not any(row["id"] in assessed for row in drivers):
        lines.append(c.COVERAGE_LINE.format(areas=join_words([lower_first(row["label"]) for row in drivers[: c.COVERAGE_MAX]])))
    if answers.budget in c.BUDGET_REORDERS and any(not item.fits for item in plotted):
        fitting = [item for item in plotted if item.fits]
        out_of_order = any(not item.fits and any(later.fits for later in plotted[index + 1 :]) for index, item in enumerate(plotted))
        lines.append((c.BUDGET_READING[answers.budget] + (c.BUDGET_READING_EXCEPTION if out_of_order else "")) if fitting else c.BUDGET_READING_NONE_FIT)
        needing = [item for item in plotted if not item.fits and item.kpi_linked]
        best = max(needing, key=lambda item: c.LEVEL_NAMES.index(impact_level(item.impact)), default=None)
        if best and fitting and c.LEVEL_NAMES.index(impact_level(best.impact)) > max(c.LEVEL_NAMES.index(impact_level(item.impact)) for item in fitting):
            lines.append(c.BUDGET_WORTH_FUNDING.format(label=lower_first(best.label), level=impact_level(best.impact)))
    if answers.budget and answers.budget != "unset" and all(item.fits for item in plotted) and any(item.spend != Spend.NONE for item in plotted):
        lines.append(c.BUDGET_READING_COVERED)
    if answers.policy == Policy.RESTRICTED.value and plotted and not any(item.verdict in c.AI_VERDICTS + (Verdict.BUILD_ON,) for item in plotted):
        scope = "the one move does not use AI" if len(plotted) == 1 else f"none of the {len(plotted)} moves uses AI"
        lines.append(f"Your AI policy is restricted, so {scope}: {verdict_counts(plotted)}.")
    if firm_uses_ai(answers) and answers.policy == Policy.NONE.value and told(answers, "policy"):
        lines.append("People at the firm use AI, and there is no AI policy, so settling that comes before adding anything.")
    worked = [work for work in answers.workstreams if told_here(work, answers, "hours")]
    if len(worked) >= 2:
        heaviest = max(worked, key=lambda work: c.HOURS_MIDPOINT[work.hours])
        strength = {work.id: max((item.relevance for item in items if item.workstream_id == work.id), default=0) for work in worked}
        linked = max(worked, key=lambda work: strength[work.id])
        if heaviest.id != linked.id and strength[linked.id] > strength[heaviest.id] and c.HOURS_MIDPOINT[heaviest.hours] > c.HOURS_MIDPOINT[linked.hours]:
            label = lambda work: lower_first(library.workstreams[work.id]["label"])
            lines.append(f"The most hours you reported sit in {label(heaviest)} ({c.HOURS_PHRASES[heaviest.hours]} a month), but the work most linked to {kpi_text} is {label(linked)} ({c.HOURS_PHRASES[linked.hours]} a month).")
    if told(answers, "kpi_status"):
        text = c.KPI_STATUS_READING.get(answers.kpi_status)
        if text:
            lines.append(text.format(kpi=kpi_text))
    if told(answers, "capacity") and answers.capacity == [Capacity.NOBODY.value]:
        lines.append("Nobody is set to carry out this work yet, so naming an owner comes before any move.")
    bare = [work for work in answers.workstreams if told_here(work, answers, "sources") and not has_system(work)]
    if told(answers, "systems") and answers.systems in (Systems.DISCONNECTED.value, Systems.MANUAL.value) and bare and plotted and plotted[0].verdict == Verdict.OPTIMIZE:
        lines.append(f"You said your tools do not hold this work together, and {lower_first(library.workstreams[bare[0].id]['label'])} runs on {sources_text(bare[0].sources)}, so process fixes come first.")
    habit = [item for item in plotted if item.activity_id in {task for work in answers.workstreams for task in work.legacy_tasks}]
    if habit:
        many = len(habit) > 1
        count = f"{len(habit)} of these tasks are" if many else "1 of these tasks is"
        testing = [item for item in habit if item.rule in (Rule.REMOVE, Rule.LEGACY_CHECK)]
        pronoun = ("they", "them") if many else ("it", "it")
        if testing and len(testing) == len(habit):
            ending = "so the plan tests cutting before spending."
        elif testing:
            ending = "so the plan tests cutting where it can, and simplifies what may be required."
        else:
            ending = f"but {pronoun[0]} may be required, or costly if wrong, so the plan simplifies {pronoun[1]} instead of stopping {pronoun[1]}."
        lines.append(f"You said {count} done mainly out of habit, {ending}")
    told_areas = [work for work in answers.workstreams if told_here(work, answers, "ai_here")]
    if answers.ai_stage == "deployed" and told(answers, "ai_stage") and told_areas and all(work.ai_here != AiHere.DEPLOYED.value for work in told_areas):
        lines.append(c.AI_BEHIND)
    def signs_off(item: ScoredActivity) -> bool:
        work = next(row for row in answers.workstreams if row.id == item.workstream_id)
        applies = item.anchor or not hardest_task_label(work, answers, library)
        return applies and item.verdict in c.AI_VERDICTS and TimeGoes.WAIT_SIGNOFF.value in work.time_goes and told_here(work, answers, "time_goes")
    sign_off = [item for item in plotted[:3] if signs_off(item)]
    if sign_off:
        lines.append(f"You said time goes on internal sign-off, which more drafting will not shorten, so pair {lower_first(sign_off[0].label)} with a clear sign-off path.")
    outside_only = [work for work in answers.workstreams if work.who == [Who.OUTSIDE.value] and told_here(work, answers, "who")]
    if outside_only:
        lines.append(f"An outside provider does {lower_first(library.workstreams[outside_only[0].id]['label'])}, so that plan starts with what they deliver, not new software.")
    return lines[: c.READING_MAX]


def start_line(answers: Answers, plotted: List[ScoredActivity], status: str, off_target_tasks: Dict[str, str]) -> Tuple[str, List[int]]:
    """The line on the first page, and which moves it starts, which also sets the 30-day list."""
    money_ordered = answers.budget in c.BUDGET_REORDERS
    if money_ordered and plotted and not any(item.fits for item in plotted):
        return c.START_NONE_FIT, [0]
    if len(plotted) < 2:
        return "", list(range(len(plotted)))
    if told(answers, "capacity") and answers.capacity == [Capacity.NOBODY.value]:
        return "With nobody assigned yet, start with move 1.", [0]
    if told(answers, "team") and answers.team == c.SMALL_TEAM:
        return "With under 15 people, start with move 1.", [0]
    if money_ordered and plotted[0].fits and not plotted[1].fits:
        return c.START_BUDGET, [0]
    if priority(plotted[0], status)[0] == priority(plotted[1], status)[0]:
        return c.TIE_START, [0, 1]
    if len(plotted) > 2 and plotted[0].activity_id not in off_target_tasks and plotted[1].activity_id not in off_target_tasks and plotted[2].activity_id in off_target_tasks and plotted[2].kpi_linked and (plotted[2].fits or not money_ordered):
        return c.START_OFF_TARGET.format(measure=lower_first(off_target_tasks[plotted[2].activity_id])), [0, 2]
    return "Start with moves 1 and 2." + (" The rest can follow once those are running." if len(plotted) > 3 else ""), [0, 1]


def what_would_change(library: Library, answers: Answers, plan_items: List[ScoredActivity]) -> List[str]:
    """Re-run the same rules with one answer moved, so the firm can see which of its constraints matter most."""
    levers = []
    if answers.policy in (Policy.RESTRICTED.value, Policy.NONE.value) and told(answers, "policy"):
        levers.append((c.LEVER_POLICY, {"policy": Policy.APPROVED.value}))
    if answers.systems in (Systems.DISCONNECTED.value, Systems.MANUAL.value) and told(answers, "systems"):
        levers.append((c.LEVER_SYSTEMS, {"systems": "connected"}))
    if told(answers, "capacity") and answers.capacity == [Capacity.NOBODY.value]:
        levers.append((c.LEVER_CAPACITY, {"capacity": ["ops_lead"]}))
    lines: List[str] = []
    before = {item.activity_id: item for item in plan_items}
    for text, change in levers:
        after = score_answers(library, replace(answers, **change), with_levers=False).items
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
        shown = lambda names: join_words(names[: c.CHANGE_NAMES_MAX] + ([c.AND_OTHERS.replace("and ", "")] if len(names) > c.CHANGE_NAMES_MAX else []))
        parts = [f"the estimate for {shown(names)} would change from {c.CHANGE_WORDS[old]} to {c.CHANGE_WORDS[new]}" for (old, new), names in groups.items()]
        parts += [f"the estimate for {shown(names)} would change from {lower_first(old)} to {lower_first(new)}" for (old, new), names in faster.items()]
        if parts:
            more = f" {c.MORE_CHANGES}" if len(parts) > c.CHANGE_GROUPS_MAX else ""
            lines.append(f"If {text}: {'; '.join(parts[: c.CHANGE_GROUPS_MAX])}.{more}")
    return lines


def measure_view(answers: Answers, library: Library, say) -> Tuple[List[Tuple[str, str, int, str, List[str]]], List[Tuple[str, str]]]:
    """The chain from each work area's own measures to the fund KPI. The link shown never overstates the task's own."""
    rows: List[Tuple[str, str, int, str, List[str]]] = []
    actions: List[Tuple[str, str]] = []
    firm_status = c.KPI_STATUS_ROW.get(answers.kpi_status) if told(answers, "kpi_status") else None
    for work in answers.workstreams:
        meta = library.workstreams[work.id]
        asked = work.measures_tracked is not None
        tracked = set(work.measures_tracked or [])
        same_as_kpi = {m["id"] for m in library.measures_for(work.id) if firm_status and m.get("same_as") == answers.kpi}
        linked = sorted((m for m in library.measures_for(work.id) if m["links"].get(answers.kpi, 0) and any(task in work.activities for task in m["tasks"])), key=lambda m: -m["links"][answers.kpi])
        for measure in library.measures_for(work.id):
            link = measure["links"].get(answers.kpi, 0)
            if not link and measure["id"] not in tracked:
                continue
            if measure["id"] in work.measures_off:
                status = "Off target, you said"
            elif measure["id"] in tracked:
                status = "Tracked"
            elif measure["id"] in same_as_kpi:
                status = firm_status
            elif asked:
                status = "Not tracked"
            else:
                status = "Not asked"
            tasks = [task for task in measure["tasks"] if task in work.activities]
            capped = [relevance_for(library.activities[task], work, answers, library)[0] for task in tasks]
            shown = min(link, min(capped)) if capped else link
            rows.append((meta["label"], say(measure["label"]), shown, status, tasks))
        if asked and linked and not (tracked | same_as_kpi).intersection(m["id"] for m in linked):
            first = linked[0]
            actions.append((first.get("action") or c.MEASURE_ACTION.format(measure=say(lower_first(first["label"]))), meta["owner"]))
    return rows, actions


def strategy_words(strategy: str):
    pairs = c.STRATEGY_WORDS.get(strategy, ())

    def say(text: str) -> str:
        for old, new in pairs:
            text = text.replace(old, new)
        return text
    return say


def owner_for(work: WorkstreamAnswers, answers: Answers, meta: dict, verdict: Optional[Verdict] = None, serious: bool = False) -> str:
    """Who leads comes from who does the work. Who builds software moves comes from who they said would set changes up."""
    base = meta["owner"]
    if answers.team == c.SMALL_TEAM and told(answers, "team"):
        base = c.WHO_OWNER[work.who[0]] if told_here(work, answers, "who") and len(work.who) == 1 else c.SMALL_TEAM_OWNER
    if verdict in c.TECH_VERDICTS and not serious and told(answers, "capacity"):
        for value in answers.capacity:
            if value in c.CAPACITY_TECH_OWNER:
                return c.CAPACITY_TECH_OWNER[value].format(owner=lower_first(base))
    return base


def stuck_lines(work: WorkstreamAnswers, answers: Answers, library: Library) -> List[str]:
    """Where this work gets stuck, using only what they said about it."""
    label = hardest_task_label(work, answers, library)
    line = lambda named, area, **words: named.format(task=label, **words) if label else area.format(**words)
    lines: List[str] = []
    if told_here(work, answers, "time_goes"):
        lines += [line(c.STUCK_TIME, c.STUCK_TIME_AREA, what=c.TIME_PHRASES[item]) for item in work.time_goes]
    if work.slow_step:
        lines.append(line(c.STUCK_SLOW, c.STUCK_SLOW_AREA, step=work.slow_step))
    if told_here(work, answers, "depends") and work.depends == "no":
        lines.append(line(c.STUCK_ONE_PERSON, c.STUCK_ONE_PERSON_AREA))
    if told_here(work, answers, "same_way") and work.same_way == "different":
        lines.append(line(c.STUCK_VARIES, c.STUCK_VARIES_AREA))
    lines += [c.STUCK_HABIT.format(task=library.activities[task].label) for task in work.legacy_tasks if task in library.activities]
    if told_here(work, answers, "sources") and len(work.sources) > 1:
        lines.append((c.STUCK_SOURCES_SYSTEM if has_system(work) else c.STUCK_SOURCES).format(sources=sources_text(work.sources)))
    return lines


def unlimited_view(library: Library, answers: Answers) -> Tuple[Answers, Plan]:
    """The same answers with no budget limit, for the report's second view."""
    open_answers = replace(answers, budget="")
    return open_answers, score_answers(library, open_answers)


def score_answers(library: Library, answers: Answers, with_levers: bool = True) -> Plan:
    kpi_text = lower_first(library.kpi_view(answers.kpi, answers.kpi_name)["label"])
    say = strategy_words(answers.strategy if told(answers, "strategy") else "")
    items: List[ScoredActivity] = []
    hours_low, hours_high, open_ended, hours_known = 0, 0, False, False
    walkthroughs: Dict[str, List[str]] = {}
    off_target_tasks: Dict[str, str] = {}

    for work in answers.workstreams:
        meta = library.workstreams[work.id]
        if told_here(work, answers, "hours"):
            hours_known = True
            low, high = c.HOURS_RANGE[work.hours]
            hours_low += low
            if high is None:
                open_ended = True
            else:
                hours_high += high
        if work.walkthrough_steps:
            walkthroughs[meta["label"]] = work.walkthrough_steps
        evidence = say(evidence_for(work, answers, library))
        unknown_area = not told_here(work, answers, "ai_here")
        assumed_all = work.ai_here != AiHere.NONE.value and not work.ai_tasks

        chosen = [library.activities[activity_id] for activity_id in work.activities]
        humans = [row for row in library.human_activities(work.id) if row.id not in work.activities]
        activities = chosen + custom_activities(work) + humans
        using = in_use_ids(work, activities)
        custom_flags = {activity.id: item.get(c.KEY_USES_AI) for activity, item in zip((row for row in activities if row.custom), work.custom)}
        named_here = {activity.id for activity in activities if answers.named_task in (activity.id, activity.label)}
        active = [row for row in activities if row.nature not in HUMAN_NATURES]
        anchor = next(iter(named_here), "") or work.heavy_task or (active[0].id if len(active) == 1 else "")
        step_task = anchor if any(row.id == anchor for row in active) else (active[0].id if active and work.slow_step else "")
        off_target_tasks.update({task: say(measure["label"]) for measure in library.measures_for(work.id) if measure["id"] in work.measures_off and measure["links"].get(answers.kpi) for task in measure["tasks"] if task in work.activities})
        for activity in activities:
            in_use = activity.id in using
            relevance, measure_label = relevance_for(activity, work, answers, library)
            anchored = activity.id == anchor or not anchor
            rule = decide_rule(activity, work, answers, in_use, relevance, anchored)
            row = c.RULES[rule]
            verdict, claim = row["verdict"], row["claim"]
            value = task_value(activity, work, activities, anchored) if activity.nature not in HUMAN_NATURES else 0.0
            off_target = measure_off_here(activity, work, library)
            impact = estimate_impact(activity, work, answers, meta["area"], relevance, value, off_target)
            real_fix = claim == KpiClaim.SOME or (rule == Rule.ONE_PERSON and activity.process_solution)
            if real_fix and relevance >= c.LINKED_RELEVANCE_MIN:
                impact = min(impact, c.IMPACT_CAP_SOME)
            elif claim != KpiClaim.FULL:
                impact = min(impact, c.IMPACT_CAP_PREPARES)
            if verdict == Verdict.BUILD_ON and stage_for(activity, work) == AiHere.DEPLOYED.value:
                impact = min(impact, c.DEPLOYED_IMPACT_CAP)
            solution, first_step, check = tailored_text(activity, rule, work, answers, in_use)
            reason = reason_text(activity, rule, work, answers, kpi_text)
            could_use_ai = answers.ai_stage != AiStage.NONE.value or not told(answers, "ai_stage")
            said_none = told_here(work, answers, "ai_here") and work.ai_here == AiHere.NONE.value
            unknown = (custom_flags.get(activity.id) is None and could_use_ai and not said_none) if activity.custom else (unknown_area and could_use_ai)
            ai_unknown = unknown and not in_use and verdict in c.AI_VERDICTS
            people = verdict == Verdict.LEAVE
            weeks = None if people else estimate_weeks(activity, verdict, work, answers, anchored)
            note = ""
            ai_assumed = in_use and assumed_all and not activity.custom
            if in_use:
                note = c.AI_ASSUMED_NOTE if ai_assumed else c.HERE_PHRASES[stage_for(activity, work)]
            restricted_in_use = rule == Rule.PAUSE_USE
            if ai_assumed and rule == Rule.BUILD_ON:
                reason, first_step = c.REASON_ASSUMED, c.ASSUMED_FIRST_STEP.replace("{task}", lower_first(activity.label))
                solution = c.ASSUMED_SOLUTION_LEAD + solution
            if ai_assumed and restricted_in_use:
                reason, first_step = c.REASON_ASSUMED_RESTRICTED, c.ASSUMED_FIRST_STEP.replace("{task}", lower_first(activity.label))
            if ai_unknown:
                note = c.AI_NOT_ASKED_NOTE if work.depth == Depth.QUICK.value else c.AI_UNKNOWN_NOTE
            route, spend = ("", Spend.NONE) if people else route_for(activity, rule, verdict, work, answers)
            fits = spend in c.BUDGET_COVERS[answers.budget]
            task_text = lower_first(activity.label)
            if activity.id == step_task and not people:
                fixed_step = "first_step" in row or ai_assumed or verdict == Verdict.BUILD_ON
                if work.slow_step and not fixed_step:
                    first_step = c.SLOW_STEP_TEXT.format(slow_step=work.slow_step)
                elif work.slow_step:
                    first_step += c.SLOW_STEP_ENDING.format(slow_step=work.slow_step)
                elif rule in c.RULE_ANCHOR_STEPS:
                    first_step = c.RULE_ANCHOR_STEPS[rule].replace("{task}", task_text)
                elif not fixed_step:
                    first_step += next((ending for key, ending in c.TIME_STEP_ENDINGS if key in work.time_goes), "")
                if verdict in c.TECH_VERDICTS and not work.slow_step:
                    first_step += c.RHYTHM_STEP_ENDINGS.get(work.rhythm, "")
                tracked_here = next((m["label"] for m in library.measures_for(work.id) if m["id"] in (work.measures_tracked or []) and activity.id in m["tasks"]), "")
                if tracked_here and not fixed_step:
                    first_step += c.TRACKED_MEASURE_ENDING.format(measure=lower_first(tracked_here))
            if verdict in (Verdict.ADD_AI, Verdict.BUILD_ON) and TimeGoes.WAIT_SIGNOFF.value in work.time_goes and told_here(work, answers, "time_goes") and (activity.id == anchor or not anchor):
                solution += c.SIGNOFF_SUFFIX
            linked = relevance > 0 and (claim in (KpiClaim.FULL, KpiClaim.SOME) or bool(real_fix))
            named = activity.id in named_here
            chain = c.CHAIN_LINE.format(measure=lower_first(measure_label), kpi=kpi_text) if measure_label and linked else ""
            items.append(ScoredActivity(
                0, say(activity.label), meta["label"], verdict, rule, say(reason), evidence,
                "" if people else relevance_note(rule, KpiClaim.SOME if real_fix else claim, relevance, kpi_text), say(solution), say(first_step), say(check),
                weeks, "" if people else speed_label(weeks), impact,
                None if people else horizon_for(weeks), None if people else quadrant_for(weeks, impact), activity.custom,
                activity_id=activity.id, thesis_note=answers.thesis_notes.get(activity.id, ""),
                route=route, spend=spend, fits=fits, money_line="" if people else money_line(spend, fits, answers.budget), fit_note="" if fits else c.FIT_NOTES[answers.budget],
                ai_assumed=ai_assumed, ai_unknown=ai_unknown, restricted_in_use=restricted_in_use,
                kpi_linked=linked, off_measure=bool(off_target),
                ai_note=note, owner_role=owner_for(work, answers, meta, verdict, serious_work(activity, work)),
                workstream_id=work.id, value=value, relevance=relevance, named=named, depth=work.depth, chain_line=chain, anchor=activity.id == anchor,
                why_line="" if people else say(why_line(named, reason, relevance, linked, kpi_text, say(off_target), work.slow_step if activity.id == step_task else "")),
            ))

    status = answers.kpi_status if told(answers, "kpi_status") else ""
    money_ordered = answers.budget in c.BUDGET_REORDERS
    relative_levels([item for item in items if item.verdict != Verdict.LEAVE])
    plotted = sorted((item for item in items if item.verdict != Verdict.LEAVE), key=lambda item: (money_ordered and not item.fits, -(c.RELATIVE_IMPACT[c.RELATIVE_TIERS[0]] if item.named else item.impact), not (item.off_measure or item.named), item.workstream_id not in answers.thesis_focus, item.speed_band, priority(item, status)))
    named = next((item for item in plotted if item.named), None)
    lifted = bool(named) and plotted.index(named) >= c.NAMED_TASK_FLOOR
    if lifted:
        plotted.remove(named)
        plotted.insert(c.NAMED_TASK_FLOOR - 1, named)
    leave = sorted((item for item in items if item.verdict == Verdict.LEAVE), key=lambda item: item.label)
    for number, item in enumerate(plotted + leave, start=1):
        item.number = number
    if answers.strategy == c.MULTI_STRATEGY and plotted and told(answers, "strategy"):
        plotted[0].first_step = c.MULTI_STRATEGY_STEP_LEAD + plotted[0].first_step

    ordered = plotted + leave
    assessed_ids = {work.id for work in answers.workstreams}
    not_assessed = [row["label"] for row in library.catalog["workstreams"] if row["id"] not in assessed_ids]
    focus_missing = [library.workstreams[item]["label"] for item in answers.thesis_focus if item not in assessed_ids]
    measure_rows, measure_actions = measure_view(answers, library, say)
    add_comparison(plotted, kpi_text, status, money_ordered)
    start, start_moves = start_line(answers, plotted, status, off_target_tasks)
    return Plan(
        ordered, [(say(title), say(text), say(action)) for title, text, action in foundations_for(answers, library, plotted[0].label if plotted else "", ordered)], hours_low, None if open_ended else hours_high, hours_known, not_assessed,
        reading=read_together(answers, ordered, library, kpi_text, lifted), start_line=start, start_moves=start_moves,
        changes=what_would_change(library, answers, ordered) if with_levers else [],
        measure_rows=measure_rows, measure_actions=measure_actions, focus_missing=focus_missing, walkthroughs=walkthroughs, budget=answers.budget,
        people_elsewhere=[say(row.label) for row in library.activities.values() if row.nature.value in c.HUMAN_NATURE_VALUES and row.id not in {item.activity_id for item in leave}],
        stuck=[(library.workstreams[work.id]["label"], lines) for work in answers.workstreams for lines in [[say(line) for line in stuck_lines(work, answers, library)]] if lines],
    )
