"""Team measures: how each work area's own numbers link to the fund KPI."""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .. import constants as c
from ..data import Library
from ..models import Answers
from ..text import lower_first
from .effect import relevance_for
from .facts import told

MeasureRow = Tuple[str, str, int, str, List[str]]


def off_target_map(answers: Answers, library: Library, say: Callable[[str], str]) -> Dict[str, str]:
    """Each selected task that feeds a measure they said is off target, with that measure's name."""
    found: Dict[str, str] = {}
    for work in answers.workstreams:
        for measure in library.measures_for(work.id):
            if measure["id"] in work.measures_off and measure["links"].get(answers.kpi):
                found.update({task: say(measure["label"]) for task in measure["tasks"] if task in work.activities})
    return found


def measure_status(
    measure: Dict[str, Any],
    measures_off: List[str],
    tracked: Set[str],
    same_as_kpi: Set[str],
    firm_status: Optional[str],
    asked: bool,
) -> Optional[str]:
    if measure["id"] in measures_off:
        return "Off target, you said"
    if measure["id"] in tracked:
        return "Tracked"
    if measure["id"] in same_as_kpi:
        return firm_status
    return "Not tracked" if asked else "Not asked"


def measure_view(
    answers: Answers, library: Library, say: Callable[[str], str]
) -> Tuple[List[MeasureRow], List[Tuple[str, str]]]:
    """The chain from each work area's own measures to the fund KPI. The link shown never overstates the task's own."""
    rows: List[MeasureRow] = []
    actions: List[Tuple[str, str]] = []
    firm_status = c.KPI_STATUS_ROW.get(answers.kpi_status) if told(answers, "kpi_status") else None
    for work in answers.workstreams:
        meta = library.workstreams[work.id]
        measures = library.measures_for(work.id)
        asked = work.measures_tracked is not None
        tracked = set(work.measures_tracked or [])
        same_as_kpi = {m["id"] for m in measures if firm_status and m.get("same_as") == answers.kpi}
        linked = sorted(
            (
                m for m in measures
                if m["links"].get(answers.kpi, 0) and any(task in work.activities for task in m["tasks"])
            ),
            key=lambda m: -m["links"][answers.kpi],
        )
        for measure in measures:
            link = measure["links"].get(answers.kpi, 0)
            if not link and measure["id"] not in tracked:
                continue
            status = measure_status(measure, work.measures_off, tracked, same_as_kpi, firm_status, asked)
            tasks = [task for task in measure["tasks"] if task in work.activities]
            capped = [relevance_for(library.activities[task], work, answers, library)[0] for task in tasks]
            shown = min(link, min(capped)) if capped else link
            rows.append((meta["label"], say(measure["label"]), shown, status, tasks))
        if asked and linked and not (tracked | same_as_kpi).intersection(m["id"] for m in linked):
            first = linked[0]
            action = first.get("action") or c.MEASURE_ACTION.format(measure=say(lower_first(first["label"])))
            actions.append((action, meta["owner"]))
    return rows, actions
