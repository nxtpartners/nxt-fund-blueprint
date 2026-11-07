"""What they said about a work area, quoted back. A skipped or unasked answer is never quoted."""
from __future__ import annotations

from typing import Callable, List

from .. import constants as c
from ..data import Library
from ..models import Answers, WorkstreamAnswers
from ..text import join_words, lower_first
from .facts import has_system, hardest_task_label, sources_text, told_here


def strategy_words(strategy: str) -> Callable[[str], str]:
    pairs = c.STRATEGY_WORDS.get(strategy, ())

    def say(text: str) -> str:
        for old, new in pairs:
            text = text.replace(old, new)
        return text
    return say


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
    lines += [
        c.STUCK_HABIT.format(task=library.activities[task].label)
        for task in work.legacy_tasks
        if task in library.activities
    ]
    if told_here(work, answers, "sources") and len(work.sources) > 1:
        template = c.STUCK_SOURCES_SYSTEM if has_system(work) else c.STUCK_SOURCES
        lines.append(template.format(sources=sources_text(work.sources)))
    return lines
