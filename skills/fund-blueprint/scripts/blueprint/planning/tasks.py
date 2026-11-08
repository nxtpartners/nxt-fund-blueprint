"""Scores one task: decides its rule, then fills in what the report says about it."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set

from .. import constants as c
from ..data import Library
from ..enums import AiHere, AiStage, Depth, KpiClaim, Nature, Rule, Spend, TimeGoes, Verdict
from ..models import Activity, Answers, ScoredActivity, WorkstreamAnswers
from ..text import lower_first
from .decisions import decide_rule
from .effect import estimate_impact, measure_off_here, relevance_for, task_value
from .evidence import evidence_for
from .facts import HUMAN_NATURES, serious_work, stage_for, told, told_here
from .levels import horizon_for, quadrant_for, speed_label
from .move_text import reason_text, relevance_note, tailored_text, why_line
from .routes import money_line, route_for
from .weeks import estimate_weeks


@dataclass
class WorkContext:
    """One work area, with what every task in it shares."""

    library: Library
    answers: Answers
    work: WorkstreamAnswers
    meta: Dict[str, Any]
    say: Callable[[str], str]
    kpi_text: str
    evidence: str
    activities: List[Activity]
    using: Set[str]
    custom_flags: Dict[str, Optional[bool]]
    named_here: Set[str]
    anchor: str
    step_task: str


@dataclass
class Decision:
    """What the rules decided for one task, before any text is written."""

    activity: Activity
    in_use: bool
    anchored: bool
    relevance: int
    measure_label: str
    rule: Rule
    row: Dict[str, Any]
    verdict: Verdict
    claim: KpiClaim
    real_fix: bool
    ai_assumed: bool


def custom_activities(work: WorkstreamAnswers) -> List[Activity]:
    rows = []
    for index, item in enumerate(work.custom):
        nature = Nature(item[c.KEY_NATURE])
        rows.append(Activity(
            f"custom_{work.id}_{index}", work.id, item[c.KEY_NAME], nature, {}, c.CUSTOM_SOLUTIONS[nature],
            c.CUSTOM_FIRST_STEP, c.CUSTOM_CHECK, custom=True, kpi_link=item.get(c.KEY_KPI_LINK),
        ))
    return rows


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


def owner_for(
    work: WorkstreamAnswers, answers: Answers, meta: dict, verdict: Optional[Verdict] = None, serious: bool = False,
    needs_money: bool = True,
) -> str:
    """Who leads comes from who does the work.

    Who builds software moves comes from who they said would set changes up.
    """
    base = meta["owner"]
    if answers.team == c.SMALL_TEAM and told(answers, "team"):
        one_kind = told_here(work, answers, "who") and len(work.who) == 1
        base = c.WHO_OWNER[work.who[0]] if one_kind else c.SMALL_TEAM_OWNER
    if verdict in c.TECH_VERDICTS and needs_money and not serious and told(answers, "capacity"):
        for value in answers.capacity:
            if value in c.CAPACITY_TECH_OWNER:
                return c.CAPACITY_TECH_OWNER[value].format(owner=lower_first(base))
    return base


def work_context(
    library: Library, answers: Answers, work: WorkstreamAnswers, say: Callable[[str], str], kpi_text: str
) -> WorkContext:
    chosen = [library.activities[activity_id] for activity_id in work.activities]
    humans = [row for row in library.human_activities(work.id) if row.id not in work.activities]
    activities = chosen + custom_activities(work) + humans
    customs = (row for row in activities if row.custom)
    named_here = {activity.id for activity in activities if answers.named_task in (activity.id, activity.label)}
    active = [row for row in activities if row.nature not in HUMAN_NATURES]
    anchor = next(iter(named_here), "") or work.heavy_task or (active[0].id if len(active) == 1 else "")
    fallback_step = active[0].id if active and work.slow_step else ""
    return WorkContext(
        library=library,
        answers=answers,
        work=work,
        meta=library.workstreams[work.id],
        say=say,
        kpi_text=kpi_text,
        evidence=say(evidence_for(work, answers, library)),
        activities=activities,
        using=in_use_ids(work, activities),
        custom_flags={activity.id: item.get(c.KEY_USES_AI) for activity, item in zip(customs, work.custom)},
        named_here=named_here,
        anchor=anchor,
        step_task=anchor if any(row.id == anchor for row in active) else fallback_step,
    )


def decide(ctx: WorkContext, activity: Activity) -> Decision:
    work, answers = ctx.work, ctx.answers
    in_use = activity.id in ctx.using
    relevance, measure_label = relevance_for(activity, work, answers, ctx.library)
    anchored = activity.id == ctx.anchor or not ctx.anchor
    rule = decide_rule(activity, work, answers, in_use, relevance, anchored)
    row = c.RULES[rule]
    claim = row["claim"]
    real_fix = claim == KpiClaim.SOME or bool(rule == Rule.ONE_PERSON and activity.process_solution)
    assumed_all = work.ai_here != AiHere.NONE.value and not work.ai_tasks
    return Decision(
        activity, in_use, anchored, relevance, measure_label, rule, row, row["verdict"], claim, real_fix,
        ai_assumed=in_use and assumed_all and not activity.custom,
    )


def capped_impact(ctx: WorkContext, d: Decision, value: float, off_target: str) -> float:
    """A move can claim no more than its rule allows."""
    activity, work = d.activity, ctx.work
    impact = estimate_impact(activity, work, ctx.answers, ctx.meta["area"], d.relevance, value, off_target)
    if d.real_fix and d.relevance >= c.LINKED_RELEVANCE_MIN:
        impact = min(impact, c.IMPACT_CAP_SOME)
    elif d.claim != KpiClaim.FULL:
        impact = min(impact, c.IMPACT_CAP_PREPARES)
    if d.verdict == Verdict.BUILD_ON and stage_for(activity, work) == AiHere.DEPLOYED.value:
        impact = min(impact, c.DEPLOYED_IMPACT_CAP)
    return impact


def ai_use_unknown(ctx: WorkContext, d: Decision) -> bool:
    """Nobody said whether AI is already used here, and the move would add it."""
    answers, work, activity = ctx.answers, ctx.work, d.activity
    could_use_ai = answers.ai_stage != AiStage.NONE.value or not told(answers, "ai_stage")
    said_none = told_here(work, answers, "ai_here") and work.ai_here == AiHere.NONE.value
    if activity.custom:
        unknown = ctx.custom_flags.get(activity.id) is None and could_use_ai and not said_none
    else:
        unknown = not told_here(work, answers, "ai_here") and could_use_ai
    return unknown and not d.in_use and d.verdict in c.AI_VERDICTS


def ai_note_for(ctx: WorkContext, d: Decision, ai_unknown: bool) -> str:
    if ai_unknown:
        return c.AI_NOT_ASKED_NOTE if ctx.work.depth == Depth.QUICK.value else c.AI_UNKNOWN_NOTE
    if not d.in_use:
        return ""
    return c.AI_ASSUMED_NOTE if d.ai_assumed else c.HERE_PHRASES[stage_for(d.activity, ctx.work)]


def anchor_first_step(ctx: WorkContext, d: Decision, first_step: str) -> str:
    """The hardest task's first step also carries what they said about where its time goes."""
    work, library = ctx.work, ctx.library
    fixed_step = "first_step" in d.row or d.ai_assumed or d.verdict == Verdict.BUILD_ON
    if work.slow_step:
        if not fixed_step:
            first_step = c.SLOW_STEP_TEXT.format(slow_step=work.slow_step)
    elif d.rule in c.RULE_ANCHOR_STEPS:
        first_step = c.RULE_ANCHOR_STEPS[d.rule].replace("{task}", lower_first(d.activity.label))
    elif not fixed_step:
        first_step += next((ending for key, ending in c.TIME_STEP_ENDINGS if key in work.time_goes), "")
    if d.verdict in c.TECH_VERDICTS and not work.slow_step:
        first_step += c.RHYTHM_STEP_ENDINGS.get(work.rhythm, "")
    tracked = work.measures_tracked or []
    tracked_here = next(
        (m["label"] for m in library.measures_for(work.id) if m["id"] in tracked and d.activity.id in m["tasks"]),
        "",
    )
    if tracked_here and not fixed_step:
        first_step += c.TRACKED_MEASURE_ENDING.format(measure=lower_first(tracked_here))
    return first_step


def move_wording(ctx: WorkContext, d: Decision) -> Dict[str, str]:
    """Solution, first step, check, and reason, with the changes this firm's answers call for."""
    activity, work, answers = d.activity, ctx.work, ctx.answers
    solution, first_step, check = tailored_text(activity, d.rule, work, answers, d.in_use)
    reason = reason_text(activity, d.rule, work, answers, ctx.kpi_text)
    assumed_step = c.ASSUMED_FIRST_STEP.replace("{task}", lower_first(activity.label))
    if d.ai_assumed and d.rule == Rule.BUILD_ON:
        reason, first_step = c.REASON_ASSUMED, assumed_step
        solution = c.ASSUMED_SOLUTION_LEAD + solution
    if d.ai_assumed and d.rule == Rule.PAUSE_USE:
        reason, first_step = c.REASON_ASSUMED_RESTRICTED, assumed_step
    if activity.id == ctx.step_task and d.verdict != Verdict.LEAVE:
        first_step = anchor_first_step(ctx, d, first_step)
    waits = TimeGoes.WAIT_SIGNOFF.value in work.time_goes and told_here(work, answers, "time_goes")
    signs_off = activity.workstream not in c.NO_SIGNOFF_WORKSTREAMS
    if d.verdict in (Verdict.ADD_AI, Verdict.BUILD_ON) and waits and d.anchored and signs_off:
        solution += c.SIGNOFF_SUFFIX
    return {"solution": solution, "first_step": first_step, "check": check, "reason": reason}


def timing_fields(weeks: Optional[float], impact: float) -> Dict[str, Any]:
    if weeks is None:
        return {"weeks": None, "speed_label": "", "horizon": None, "quadrant": None}
    return {
        "weeks": weeks,
        "speed_label": speed_label(weeks),
        "horizon": horizon_for(weeks),
        "quadrant": quadrant_for(weeks, impact),
    }


def money_fields(ctx: WorkContext, d: Decision, people: bool) -> Dict[str, Any]:
    budget = ctx.answers.budget
    route, spend = ("", Spend.NONE) if people else route_for(d.activity, d.rule, d.verdict, ctx.work, ctx.answers)
    outside_help = c.CAPACITY_OUTSIDE in ctx.answers.capacity and told(ctx.answers, "capacity")
    if d.verdict in c.TECH_VERDICTS and spend == Spend.NONE and outside_help:
        spend = Spend.SMALL
    fits = spend in c.BUDGET_COVERS[budget]
    return {
        "route": route,
        "spend": spend,
        "fits": fits,
        "money_line": "" if people else money_line(spend, fits, budget),
        "fit_note": "" if fits else c.FIT_NOTES[budget],
    }


def chain_text(measure_label: str, kpi_text: str) -> str:
    return c.CHAIN_LINE.format(measure=lower_first(measure_label), kpi=kpi_text) if measure_label else ""


def score_activity(ctx: WorkContext, activity: Activity) -> ScoredActivity:
    d = decide(ctx, activity)
    answers, work, say, kpi_text = ctx.answers, ctx.work, ctx.say, ctx.kpi_text
    people = d.verdict == Verdict.LEAVE
    human = activity.nature in HUMAN_NATURES
    value = 0.0 if human else task_value(activity, work, ctx.activities, d.anchored)
    off_target = measure_off_here(activity, work, ctx.library)
    impact = capped_impact(ctx, d, value, off_target)
    words = move_wording(ctx, d)
    ai_unknown = ai_use_unknown(ctx, d)
    weeks = None if people else estimate_weeks(activity, d.verdict, work, answers, d.anchored)
    linked = d.relevance > 0 and (d.claim in (KpiClaim.FULL, KpiClaim.SOME) or d.real_fix)
    named = activity.id in ctx.named_here
    slow_step = work.slow_step if activity.id == ctx.step_task else ""
    claim_shown = KpiClaim.SOME if d.real_fix else d.claim
    why = why_line(named, words["reason"], d.relevance, linked, kpi_text, say(off_target), slow_step)
    chain = chain_text(d.measure_label, kpi_text) if linked else ""
    money = money_fields(ctx, d, people)
    needs_money = money["spend"] != Spend.NONE
    return ScoredActivity(
        number=0,
        label=say(activity.label),
        workstream_label=ctx.meta["label"],
        verdict=d.verdict,
        rule=d.rule,
        reason=say(words["reason"]),
        evidence=ctx.evidence,
        relevance_note="" if people else relevance_note(d.rule, claim_shown, d.relevance, kpi_text),
        solution=say(words["solution"]),
        first_step=say(words["first_step"]),
        check=say(words["check"]),
        impact=impact,
        custom=activity.custom,
        activity_id=activity.id,
        thesis_note=answers.thesis_notes.get(activity.id, ""),
        ai_assumed=d.ai_assumed,
        ai_unknown=ai_unknown,
        restricted_in_use=d.rule == Rule.PAUSE_USE,
        kpi_linked=linked,
        off_measure=bool(off_target),
        ai_note=ai_note_for(ctx, d, ai_unknown),
        owner_role=activity.owner
        or owner_for(work, answers, ctx.meta, d.verdict, serious_work(activity, work), needs_money),
        workstream_id=work.id,
        value=value,
        relevance=d.relevance,
        named=named,
        depth=work.depth,
        chain_line=chain,
        anchor=activity.id == ctx.anchor,
        why_line="" if people else say(why),
        **timing_fields(weeks, impact),
        **money,
    )
