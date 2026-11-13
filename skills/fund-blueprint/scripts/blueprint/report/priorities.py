"""The plot of speed against effect, with its key."""
from __future__ import annotations

from typing import Dict

from .. import constants as c
from ..enums import Verdict
from ..models import Plan
from ..plot import render_plot
from ..text import lower_first
from .common import esc, key_mark, priority_no, shape_mark


def legend(plan: Plan) -> str:
    present = [v for v in Verdict if v != Verdict.LEAVE and any(item.verdict == v for item in plan.plotted)]
    rows = "".join(
        f"<li>{key_mark(v)}<span><b>{esc(c.VERDICT_LABELS[v])}</b>. {esc(c.VERDICT_DEFINITIONS[v])}</span></li>"
        for v in present
    )
    budget = plan.budget
    shapes = ""
    if budget and any(item.fits for item in plan.plotted):
        shapes += f"<li>{shape_mark(True)}<span>{esc(c.SHAPE_KEY_FITS[budget])}</span></li>"
    if any(not item.fits for item in plan.plotted):
        shapes += f"<li>{shape_mark(False)}<span>{esc(c.SHAPE_KEY_NOT[budget])}</span></li>"
    return f'<ul class="legend">{rows}</ul>' + (f'<ul class="legend">{shapes}</ul>' if shapes else "")


def kpi_note(view: Dict[str, str]) -> str:
    """What the number on the axis feeds, with no size attached, or how a typed number was handled."""
    if view.get("feeds"):
        feeds = c.FEEDS_LINE.format(feeds=view["feeds"])
        return " ".join((feeds, c.FEEDS_LINKS[view["feeds_link"]], c.RELATIVE_NOTE, c.NO_RETURNS_CLAIM))
    if view.get("matched"):
        matched = c.KPI_MATCHED_NOTE.format(matched=lower_first(view["matched"]))
        return " ".join((matched, c.RELATIVE_NOTE, c.NO_RETURNS_CLAIM))
    return " ".join((c.KPI_OWN_NOTE, c.RELATIVE_NOTE, c.KPI_OWN_NO_FORECAST.format(kpi=view["words"])))


def priorities(plan: Plan, kpi: str, view: Dict[str, str]) -> str:
    if not plan.plotted:
        return ""
    key = "".join(
        f'<li>{priority_no(item)}'
        f'<span>{esc(item.label)}</span></li>'
        for item in plan.plotted
    )
    recommended = tuple(item.number for item in plan.top)
    marks = [c.QUADRANT_NOTE_TOP] if recommended else []
    heading = view.get("heading") or c.PLOT_HEADING.format(effect=view["effect_phrase"])
    return (
        f'<figure class="flush"><p class="plot-y">{esc(heading)}</p><p class="note plot-note">{esc(kpi_note(view))}</p>'
        f'{render_plot(plan.plotted, kpi, recommended)}{legend(plan)}<ol class="plot-key">{key}</ol>'
        f'<figcaption class="note">{esc(" ".join(marks))} Speed is the estimated time to a first working version, '
        f"or to finish a process change. Effect is the estimated effect on {esc(lower_first(kpi))}, "
        "compared with your other priorities. Both are planning estimates, explained in the notes, not measurements. "
        "Money levels are planning estimates too, set by the type of priority and your tools, "
        "for each priority taken alone. They are not quotes.</figcaption></figure>"
    )
