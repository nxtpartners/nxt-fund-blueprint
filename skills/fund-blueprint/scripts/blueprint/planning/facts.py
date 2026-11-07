"""What the answers say: the only place that knows what was told, skipped, or implied by a mix of answers."""
from __future__ import annotations

from typing import List

from .. import constants as c
from ..data import Library
from ..enums import AiHere, AiStage, Capacity, ErrorCost, Nature, Source, Systems
from ..models import Activity, Answers, WorkstreamAnswers
from ..text import join_words

HUMAN_NATURES = (Nature.JUDGMENT, Nature.RELATIONSHIP)


# Source predicates: the only place that knows what a mix of sources means.
def has_documents(work: WorkstreamAnswers) -> bool:
    return Source.DOCUMENTS.value in work.sources or Source.EMAIL.value in work.sources


def has_system(work: WorkstreamAnswers) -> bool:
    return Source.SYSTEM.value in work.sources


def sources_text(sources: List[str]) -> str:
    return join_words([c.SOURCE_PHRASES[source] for source in sources])


def doc_sources_text(work: WorkstreamAnswers) -> str:
    documents = (Source.DOCUMENTS.value, Source.EMAIL.value)
    return join_words([c.SOURCE_PHRASES[source] for source in work.sources if source in documents])


def told(answers: Answers, field_name: str) -> bool:
    return field_name not in answers.skipped


def told_here(work: WorkstreamAnswers, answers: Answers, field_name: str) -> bool:
    return f"{work.id}.{field_name}" not in answers.skipped and field_name not in work.unasked


def nobody_assigned(answers: Answers) -> bool:
    return told(answers, "capacity") and answers.capacity == [Capacity.NOBODY.value]


def systems_apart(answers: Answers) -> bool:
    return answers.systems in (Systems.DISCONNECTED.value, Systems.MANUAL.value)


def firm_uses_ai(answers: Answers) -> bool:
    stated = told(answers, "ai_stage") and answers.ai_stage != AiStage.NONE.value
    in_work = any(
        work.ai_here != AiHere.NONE.value or any(item.get(c.KEY_USES_AI) for item in work.custom)
        for work in answers.workstreams
    )
    return stated or in_work


def stage_for(activity: Activity, work: WorkstreamAnswers) -> str:
    """A custom task's AI use is its own answer, separate from the work area's."""
    if activity.custom or work.ai_here == AiHere.NONE.value:
        return c.DEFAULT_IN_USE_STAGE
    return work.ai_here


def risky(activity: Activity, work: WorkstreamAnswers) -> bool:
    """Serious harm can be narrowed to named tasks. Anything not named, or unsure, stays cautious."""
    if work.error_cost == ErrorCost.UNSURE.value:
        return True
    if work.error_cost != ErrorCost.SEVERE.value:
        return False
    return activity.custom or not work.harm_tasks or activity.id in work.harm_tasks


def serious_work(activity: Activity, work: WorkstreamAnswers) -> bool:
    return activity.required or risky(activity, work)


def serious_documents(activity: Activity, work: WorkstreamAnswers) -> bool:
    return serious_work(activity, work) and has_documents(work)


def hardest_task_label(work: WorkstreamAnswers, answers: Answers, library: Library) -> str:
    """Some questions ask about the hardest task, so what they said is quoted for that task."""
    if answers.named_task:
        if answers.named_task in work.activities:
            return library.activities[answers.named_task].label
        if any(item[c.KEY_NAME] == answers.named_task for item in work.custom):
            return answers.named_task
    return library.activities[work.heavy_task].label if work.heavy_task else ""
