"""What the answers mean side by side, on the first page. Only their own answers and the plan's own counts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from .. import constants as c
from ..data import Library
from ..enums import AiHere, Policy, Rule, Spend, TimeGoes, Verdict, Who
from ..models import Answers, ScoredActivity
from ..text import join_words, lower_first
from .facts import (
    firm_uses_ai,
    hardest_task_label,
    has_system,
    nobody_assigned,
    sources_text,
    systems_apart,
    told,
    told_here,
)
from .levels import impact_level


@dataclass
class Reading:
    answers: Answers
    items: List[ScoredActivity]
    plotted: List[ScoredActivity]
    library: Library
    kpi_text: str
    lifted: bool


def verdict_counts(plan_items: List[ScoredActivity]) -> str:
    counts: Dict[Verdict, int] = {}
    for item in plan_items:
        counts[item.verdict] = counts.get(item.verdict, 0) + 1
    return join_words([
        f"{count} {c.COUNT_WORDS[verdict][0 if count == 1 else 1]}" for verdict, count in counts.items()
    ])


def named_reason(
    named: ScoredActivity, plotted: List[ScoredActivity], lifted: bool, kpi_text: str, money_ordered: bool = False
) -> str:
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
    if len(above) == 1:
        subject = ("The priority above it", "the priority above it", "has")
    else:
        subject = ("The priorities above it", "the priorities above it", "have")
    if all(item.relevance > named.relevance for item in above):
        return c.NAMED_REASON_CLOSER.format(above=f"{subject[0]} {subject[2]}", kpi=kpi_text)
    if all(item.value > named.value for item in above):
        return c.NAMED_REASON_TIME.format(above_lower=subject[1])
    return c.NAMED_REASON_SCORE.format(above=f"{subject[0]} {subject[2]}")


def named_lines(r: Reading) -> List[str]:
    named = next((item for item in r.items if item.named), None)
    if not named:
        return []
    task = lower_first(named.label)
    if named.verdict == Verdict.LEAVE:
        return [
            f"You named {task} as the task to take off your team. "
            "It rests on judgment or relationships, so it stays with your team, and the priorities below work around it."
        ]
    position = r.plotted.index(named) + 1
    if position == 1:
        return [c.NAMED_FIRST.format(task=task)]
    money_ordered = r.answers.budget in c.BUDGET_REORDERS
    reason = named_reason(named, r.plotted, r.lifted, r.kpi_text, money_ordered)
    return [c.NAMED_LATER.format(task=task, position=position, reason=reason)]


def coverage_lines(r: Reading) -> List[str]:
    answers = r.answers
    assessed = {work.id for work in answers.workstreams}
    drivers = [
        row for row in r.library.catalog["workstreams"]
        if any(measure["links"].get(answers.kpi) == c.RELEVANCE_MAX for measure in row["measures"])
    ]
    if not drivers or any(row["id"] in assessed for row in drivers):
        return []
    return [c.COVERAGE_LINE.format(areas=join_words([lower_first(row["label"]) for row in drivers[: c.COVERAGE_MAX]]))]


def level_rank(item: ScoredActivity) -> int:
    return c.LEVEL_NAMES.index(impact_level(item.impact))


def budget_lines(r: Reading) -> List[str]:
    answers, plotted = r.answers, r.plotted
    if answers.budget not in c.BUDGET_REORDERS or not any(not item.fits for item in plotted):
        return []
    fitting = [item for item in plotted if item.fits]
    out_of_order = any(
        not item.fits and any(later.fits for later in plotted[index + 1 :]) for index, item in enumerate(plotted)
    )
    exception = c.BUDGET_READING_EXCEPTION if out_of_order else ""
    lines = [c.BUDGET_READING[answers.budget] + exception if fitting else c.BUDGET_READING_NONE_FIT]
    needing = [item for item in plotted if not item.fits and item.kpi_linked]
    best = max(needing, key=lambda item: (level_rank(item), -item.speed_band), default=None)
    if best and fitting and level_rank(best) > max(level_rank(item) for item in fitting):
        lines.append(c.BUDGET_WORTH_FUNDING.format(label=lower_first(best.label), level=impact_level(best.impact)))
    return lines


def budget_covered_lines(r: Reading) -> List[str]:
    budget, plotted = r.answers.budget, r.plotted
    spends = any(item.spend != Spend.NONE for item in plotted)
    if budget and budget != "unset" and all(item.fits for item in plotted) and spends:
        several = sum(item.spend != Spend.NONE for item in plotted) > 1 and budget == c.BUDGET_ALL_AT_ONCE
        return [c.BUDGET_READING_COVERED + (c.BUDGET_READING_ALL_AT_ONCE if several else "")]
    return []


def restricted_lines(r: Reading) -> List[str]:
    plotted = r.plotted
    uses_ai = any(item.verdict in c.AI_VERDICTS + (Verdict.BUILD_ON,) for item in plotted)
    if r.answers.policy != Policy.RESTRICTED.value or not plotted or uses_ai:
        return []
    scope = "the one priority does not use AI" if len(plotted) == 1 else f"none of the {len(plotted)} priorities uses AI"
    return [f"Your AI policy is restricted, so {scope}: {verdict_counts(plotted)}."]


def no_policy_lines(r: Reading) -> List[str]:
    answers = r.answers
    if firm_uses_ai(answers) and answers.policy == Policy.NONE.value and told(answers, "policy"):
        return ["People at the firm use AI, and there is no AI policy, so settling that comes before adding anything."]
    return []


def hours_lines(r: Reading) -> List[str]:
    """Where the hours sit against where the link is, when those differ."""
    answers = r.answers
    worked = [work for work in answers.workstreams if told_here(work, answers, "hours")]
    if len(worked) < 2:
        return []
    heaviest = max(worked, key=lambda work: c.HOURS_MIDPOINT[work.hours])
    strength = {
        work.id: max((item.relevance for item in r.items if item.workstream_id == work.id), default=0)
        for work in worked
    }
    linked = max(worked, key=lambda work: strength[work.id])
    more_hours = c.HOURS_MIDPOINT[heaviest.hours] > c.HOURS_MIDPOINT[linked.hours]
    if heaviest.id == linked.id or strength[linked.id] <= strength[heaviest.id] or not more_hours:
        return []
    label = lambda work: lower_first(r.library.workstreams[work.id]["label"])
    return [
        f"The most hours you reported sit in {label(heaviest)} ({c.HOURS_PHRASES[heaviest.hours]} a month), "
        f"but the work most linked to {r.kpi_text} is {label(linked)} ({c.HOURS_PHRASES[linked.hours]} a month)."
    ]


def kpi_status_lines(r: Reading) -> List[str]:
    if not told(r.answers, "kpi_status"):
        return []
    text = c.KPI_STATUS_READING.get(r.answers.kpi_status)
    return [text.format(kpi=r.kpi_text)] if text else []


def owner_lines(r: Reading) -> List[str]:
    if nobody_assigned(r.answers):
        return ["Nobody is set to carry out this work yet, so naming an owner comes before any priority."]
    return []


def tools_lines(r: Reading) -> List[str]:
    answers, plotted = r.answers, r.plotted
    bare = [work for work in answers.workstreams if told_here(work, answers, "sources") and not has_system(work)]
    apart = told(answers, "systems") and systems_apart(answers)
    if not (apart and bare and plotted and plotted[0].verdict == Verdict.OPTIMIZE):
        return []
    area = lower_first(r.library.workstreams[bare[0].id]["label"])
    return [
        f"You said your tools do not hold this work together, and {area} "
        f"runs on {sources_text(bare[0].sources)}, so process fixes come first."
    ]


def habit_lines(r: Reading) -> List[str]:
    legacy = {task for work in r.answers.workstreams for task in work.legacy_tasks}
    habit = [item for item in r.plotted if item.activity_id in legacy]
    if not habit:
        return []
    many = len(habit) > 1
    count = f"{len(habit)} of these tasks are" if many else "1 of these tasks is"
    testing = [item for item in habit if item.rule in (Rule.REMOVE, Rule.LEGACY_CHECK)]
    pronoun = ("they", "them") if many else ("it", "it")
    if testing and len(testing) == len(habit):
        ending = "so the plan tests cutting before spending."
    elif testing:
        ending = "so the plan tests cutting where it can, and simplifies what may be required."
    else:
        ending = (
            f"but {pronoun[0]} may be required, or costly if wrong, "
            f"so the plan simplifies {pronoun[1]} instead of stopping {pronoun[1]}."
        )
    return [f"You said {count} done mainly out of habit, {ending}"]


def ai_behind_lines(r: Reading) -> List[str]:
    answers = r.answers
    told_areas = [work for work in answers.workstreams if told_here(work, answers, "ai_here")]
    says_standard = answers.ai_stage == "deployed" and told(answers, "ai_stage")
    if says_standard and told_areas and all(work.ai_here != AiHere.DEPLOYED.value for work in told_areas):
        return [c.AI_BEHIND]
    return []


def signs_off(item: ScoredActivity, r: Reading) -> bool:
    answers = r.answers
    work = next(row for row in answers.workstreams if row.id == item.workstream_id)
    applies = item.anchor or not hardest_task_label(work, answers, r.library)
    waits = TimeGoes.WAIT_SIGNOFF.value in work.time_goes and told_here(work, answers, "time_goes")
    return applies and item.verdict in c.AI_VERDICTS and waits


def signoff_lines(r: Reading) -> List[str]:
    sign_off = [item for item in r.plotted[:3] if signs_off(item, r)]
    if not sign_off:
        return []
    return [
        "You said time goes on internal sign-off, which more drafting will not shorten, "
        f"so pair {lower_first(sign_off[0].label)} with a clear sign-off path."
    ]


def outside_lines(r: Reading) -> List[str]:
    answers = r.answers
    outside_only = [
        work for work in answers.workstreams
        if work.who == [Who.OUTSIDE.value] and told_here(work, answers, "who")
    ]
    if not outside_only:
        return []
    area = lower_first(r.library.workstreams[outside_only[0].id]["label"])
    return [f"An outside provider does {area}, so that plan starts with what they deliver, not new software."]


# Order is the order they appear on the page, and the cap in read_together keeps the first few.
READERS: Tuple[Callable[[Reading], List[str]], ...] = (
    named_lines,
    coverage_lines,
    budget_lines,
    budget_covered_lines,
    restricted_lines,
    no_policy_lines,
    hours_lines,
    kpi_status_lines,
    owner_lines,
    tools_lines,
    habit_lines,
    ai_behind_lines,
    signoff_lines,
    outside_lines,
)


def read_together(
    answers: Answers, items: List[ScoredActivity], library: Library, kpi_text: str, lifted: bool = False
) -> List[str]:
    """What the answers mean side by side. Only their own answers and the plan's own counts, so nothing is invented."""
    plotted = [item for item in items if item.verdict != Verdict.LEAVE]
    reading = Reading(answers, items, plotted, library, kpi_text, lifted)
    return [line for reader in READERS for line in reader(reading)][: c.READING_MAX]
