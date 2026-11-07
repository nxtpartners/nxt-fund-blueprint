"""Where the work could run, and the money that takes."""
from __future__ import annotations

from typing import Tuple

from .. import constants as c
from ..enums import Capacity, Policy, Rule, Spend, Verdict
from ..models import Activity, Answers, WorkstreamAnswers
from .facts import firm_uses_ai, serious_work, stage_for


def own_tool_route(activity: Activity, work: WorkstreamAnswers, answers: Answers) -> str:
    """What they already run comes first, except a chat tool for serious work."""
    return next(
        (
            text
            for tool, text in c.TOOL_ROUTES
            if firm_uses_ai(answers)
            and tool in answers.ai_tools
            and not (tool == "assistants" and serious_work(activity, work))
        ),
        "",
    )


def route_for(
    activity: Activity, rule: Rule, verdict: Verdict, work: WorkstreamAnswers, answers: Answers
) -> Tuple[str, Spend]:
    """Where the work could run, and the money that takes. One place, so the two never disagree."""
    if rule == Rule.OUTSIDE:
        return c.OUTSIDE_ROUTE, Spend.NONE
    stage = stage_for(activity, work)
    unapproved = stage == c.DEFAULT_IN_USE_STAGE and answers.policy != Policy.APPROVED.value
    informal = stage == c.INFORMAL_STAGE or unapproved
    if verdict == Verdict.BUILD_ON and informal:
        return c.ROUTES[(Verdict.BUILD_ON, "informal")], Spend.SMALL
    tier = c.BUDGET_TIER.get(answers.budget) or c.TEAM_ROUTE_TIER[answers.team]
    if verdict == Verdict.ADD_AI:
        if answers.policy == Policy.NONE.value:
            return c.ROUTES[(Verdict.ADD_AI, "no_policy")], Spend.SMALL
        own = own_tool_route(activity, work, answers)
        if serious_work(activity, work):
            if own:
                return c.ROUTES[(Verdict.ADD_AI, "careful_own")].format(tool=own), Spend.NONE
            return c.ROUTES[(Verdict.ADD_AI, "careful")], Spend.DECISION
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
    spend = Spend.DECISION if verdict == Verdict.AGENTIC or tier == "high" else Spend.SMALL
    return c.ROUTES.get((verdict, tier), ""), spend


def money_line(spend: Spend, fits: bool, budget: str) -> str:
    if spend == Spend.NONE:
        return c.SPEND_LABELS[spend]
    return c.SPEND_LABELS[spend] + c.SPEND_ENDINGS[budget][0 if fits else 1]
