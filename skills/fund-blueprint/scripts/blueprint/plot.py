"""Speed of execution against estimated KPI impact, as inline SVG with a wide and a narrow layout."""
from __future__ import annotations

import html
import textwrap
from typing import Dict, List, Tuple

from . import constants as c
from . import tokens as t
from .enums import Quadrant
from .models import ScoredActivity
from .scoring import effect_text, impact_level, lower_first


def band_index(weeks: float) -> int:
    """0 is the slowest band, on the left. Faster work sits further right."""
    for index, (_, high, _) in enumerate(c.SPEED_BANDS):
        if weeks < high:
            return len(c.SPEED_BANDS) - 1 - index
    return 0


def timeline_share(weeks: float) -> float:
    """Where a project ends on the department timeline: the end of its speed band, not an exact date."""
    for index, (_, high, _) in enumerate(c.SPEED_BANDS):
        if weeks < high or index == len(c.SPEED_BANDS) - 1:
            return (index + 1) / len(c.SPEED_BANDS)
    return 1.0


def mark_shape(x: float, y: float, size: float, fits: bool, attributes: str) -> str:
    """A circle fits the budget. A diamond may not, and it is slightly larger so the two look the same weight."""
    if fits:
        return f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{size}" {attributes}/>'
    reach = size * t.PLOT_DIAMOND_FACTOR
    return f'<polygon points="{x:.1f},{y - reach:.1f} {x + reach:.1f},{y:.1f} {x:.1f},{y + reach:.1f} {x - reach:.1f},{y:.1f}" {attributes}/>'


def level_index(impact: float) -> int:
    return c.LEVEL_NAMES.index(impact_level(impact))


class Canvas:
    def __init__(self, spec: Dict[str, int], band_labels: Tuple[str, ...], kind: str) -> None:
        self.spec, self.band_labels, self.kind = spec, band_labels, kind
        self.left, self.right = spec["left"], spec["width"] - spec["right"]
        self.top, self.bottom = spec["top"], spec["height"] - spec["bottom"]
        self.band_width = (self.right - self.left) / len(c.SPEED_BANDS)
        self.level_height = (self.bottom - self.top) / len(c.LEVEL_NAMES)

    def text(self, x: float, y: float, content: str, size: int, fill: str = t.COLOR_INK_SOFT, anchor: str = "middle", weight: int = 400) -> str:
        return f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{html.escape(content)}</text>'

    def y_title(self, kpi_text: str) -> str:
        """The firm's own number names the axis. A long name takes two lines, so it never runs off the plot."""
        lines = textwrap.wrap(c.Y_AXIS_TITLE.format(kpi=kpi_text), self.spec["title_wrap"])[:2]
        middle = (self.top + self.bottom) / 2
        parts = []
        for index, line in enumerate(lines):
            x = t.PLOT_Y_TITLE_X + index * t.PLOT_Y_TITLE_LINE
            parts.append(f'<text x="{x}" y="{middle:.0f}" transform="rotate(-90 {x} {middle:.0f})" font-size="{self.spec["axis"]}" fill="{t.COLOR_INK}" text-anchor="middle" font-weight="{t.PLOT_LABEL_WEIGHT}">{html.escape(line)}</text>')
        return "".join(parts)

    def cells(self, items: List[ScoredActivity]) -> Dict[Tuple[int, int], List[int]]:
        found: Dict[Tuple[int, int], List[int]] = {}
        for item in sorted(items, key=lambda row: row.number):
            found.setdefault((band_index(item.weeks), level_index(item.impact)), []).append(item.number)
        return found

    def step(self) -> float:
        return 2 * self.spec["radius"] + t.PLOT_MARK_GAP

    def per_row(self) -> int:
        return max(int((self.band_width - 4) // self.step()), 1)

    def fit_height(self, items: List[ScoredActivity]) -> None:
        """A crowded cell makes the plot taller, so marks never leave their row or cover a label."""
        most = max((len(numbers) for numbers in self.cells(items).values()), default=1)
        rows = -(-most // self.per_row())
        needed = (rows - 1) * self.step() + 2 * self.spec["radius"] + 2 * t.PLOT_LABEL_STRIP + t.PLOT_MARK_GAP
        extra = max(0.0, needed - self.level_height) * len(c.LEVEL_NAMES)
        if extra:
            self.spec = dict(self.spec, height=int(self.spec["height"] + extra))
            self.bottom = self.spec["height"] - self.spec["bottom"]
            self.level_height = (self.bottom - self.top) / len(c.LEVEL_NAMES)

    def place_markers(self, items: List[ScoredActivity]) -> Dict[int, Tuple[float, float]]:
        """Each band and impact level is one cell, and markers sit in a tidy grid inside it."""
        spots: Dict[int, Tuple[float, float]] = {}
        step, per_row = self.step(), self.per_row()
        for (band, level), numbers in self.cells(items).items():
            center_x = self.left + (band + 0.5) * self.band_width
            center_y = self.bottom - (level + 0.5) * self.level_height
            rows = [numbers[i : i + per_row] for i in range(0, len(numbers), per_row)]
            top = center_y - (len(rows) - 1) * step / 2
            top_edge = self.bottom - (level + 1) * self.level_height + t.PLOT_LABEL_STRIP + self.spec["radius"]
            bottom_edge = self.bottom - level * self.level_height - t.PLOT_LABEL_STRIP - self.spec["radius"]
            top = max(top_edge, min(top, bottom_edge - (len(rows) - 1) * step))
            for row_index, row in enumerate(rows):
                left = center_x - (len(row) - 1) * step / 2
                for column, number in enumerate(row):
                    spots[number] = (left + column * step, top + row_index * step)
        return spots

    def render(self, items: List[ScoredActivity], kpi_label: str, recommended: Tuple[int, ...]) -> str:
        self.fit_height(items)
        spec = self.spec
        label, axis = spec["label"], spec["axis"]
        kpi_text = lower_first(kpi_label)
        mid_x = self.left + c.SLOW_BAND_COUNT * self.band_width
        mid_y = self.bottom - self.level_height
        parts = [
            f'<svg viewBox="0 0 {spec["width"]} {spec["height"]}" role="group" aria-label="Each numbered activity by speed of execution and estimated impact on {html.escape(kpi_label, quote=True)}. The table below holds the same data." class="plot plot-{self.kind}">'
        ]
        for index, name in enumerate(c.LEVEL_NAMES):
            parts.append(self.text(self.left - t.PLOT_TICK_GAP, self.bottom - (index + 0.5) * self.level_height + t.PLOT_TEXT_NUDGE, name, label, anchor="end"))
            if index:
                y = self.bottom - index * self.level_height
                parts.append(f'<line x1="{self.left}" x2="{self.right}" y1="{y:.0f}" y2="{y:.0f}" stroke="{t.COLOR_LINE}"/>')
        for index in range(1, len(c.SPEED_BANDS)):
            x = self.left + index * self.band_width
            parts.append(f'<line x1="{x:.0f}" x2="{x:.0f}" y1="{self.bottom}" y2="{self.bottom + t.PLOT_TICK}" stroke="{t.COLOR_INK}"/>')
        parts.append(f'<line x1="{self.left}" x2="{self.right}" y1="{self.bottom}" y2="{self.bottom}" stroke="{t.COLOR_INK}" stroke-width="{t.PLOT_AXIS_STROKE}"/>')
        parts.append(f'<line x1="{self.left}" x2="{self.left}" y1="{self.top}" y2="{self.bottom}" stroke="{t.COLOR_INK}" stroke-width="{t.PLOT_AXIS_STROKE}"/>')
        parts.append(f'<line x1="{mid_x:.0f}" x2="{mid_x:.0f}" y1="{self.top}" y2="{self.bottom}" stroke="{t.COLOR_LINE_STRONG}" stroke-dasharray="{t.PLOT_DASH}"/>')
        parts.append(f'<line x1="{self.left}" x2="{self.right}" y1="{mid_y:.0f}" y2="{mid_y:.0f}" stroke="{t.COLOR_LINE_STRONG}" stroke-dasharray="{t.PLOT_DASH}"/>')

        corners = (
            (self.right - t.PLOT_CORNER_INSET_RIGHT, self.top + t.PLOT_CORNER_INSET_TOP, "end", Quadrant.QUICK_WINS, t.COLOR_INK),
            (self.left + t.PLOT_CORNER_INSET_X, self.top + t.PLOT_CORNER_INSET_TOP, "start", Quadrant.STRATEGIC_BETS, t.COLOR_INK_SOFT),
            (self.right - t.PLOT_CORNER_INSET_RIGHT, self.bottom - t.PLOT_CORNER_INSET_BOTTOM, "end", Quadrant.FILL_INS, t.COLOR_INK_SOFT),
            (self.left + t.PLOT_CORNER_INSET_X, self.bottom - t.PLOT_CORNER_INSET_BOTTOM, "start", Quadrant.DEPRIORITIZE, t.COLOR_INK_SOFT),
        )
        for x, y, anchor, quadrant, fill in corners:
            names = c.QUADRANT_LABELS_SHORT if self.kind == "narrow" else c.QUADRANT_LABELS
            parts.append(self.text(x, y, names[quadrant], label, fill=fill, anchor=anchor, weight=t.PLOT_LABEL_WEIGHT))
        for index, band in enumerate(self.band_labels):
            parts.append(self.text(self.right - (index + 0.5) * self.band_width, self.bottom + t.PLOT_BAND_LABEL_OFFSET, band, label))
        parts.append(self.text((self.left + self.right) / 2, spec["height"] - t.PLOT_AXIS_TITLE_OFFSET, "Estimated speed, faster to the right", axis, fill=t.COLOR_INK, weight=t.PLOT_LABEL_WEIGHT))

        parts.append(self.y_title(kpi_text))

        spots = self.place_markers(items)
        for item in sorted(items, key=lambda row: row.number):
            x, y = spots[item.number]
            color = t.VERDICT_COLORS[item.verdict]
            hollow = item.verdict in t.VERDICT_HOLLOW
            fill, stroke, ink = (t.COLOR_SURFACE, color, color) if hollow else (color, t.COLOR_SURFACE, t.COLOR_SURFACE)
            summary = f"{item.number}. {item.label}: {c.VERDICT_LABELS[item.verdict]}, {item.speed_label}, {effect_text(item.impact, kpi_text)}, {item.money_line}"
            ring = mark_shape(x, y, spec["radius"] + t.PLOT_RING_GAP, item.fits, f'fill="none" stroke="{t.COLOR_INK}" stroke-width="{t.PLOT_RING_STROKE}"') if item.number in recommended else ""
            parts.append(
                f'<g class="mark" tabindex="0" role="img" aria-label="{html.escape(summary, quote=True)}"><title>{html.escape(summary)}</title>{ring}'
                + mark_shape(x, y, spec["radius"], item.fits, f'fill="{fill}" stroke="{stroke}" stroke-width="{t.PLOT_MARK_STROKE}"')
                + f'<text x="{x:.0f}" y="{y + t.PLOT_TEXT_NUDGE:.0f}" font-size="{label}" fill="{ink}" text-anchor="middle" font-weight="{t.PLOT_LABEL_WEIGHT}" aria-hidden="true">{item.number}</text></g>'
            )
        parts.append("</svg>")
        return "".join(parts)


def render_plot(items: List[ScoredActivity], kpi_label: str, recommended: Tuple[int, ...] = ()) -> str:
    wide = Canvas(t.PLOT_WIDE, tuple(band[2] for band in c.SPEED_BANDS), "wide")
    narrow = Canvas(t.PLOT_NARROW, c.SPEED_BANDS_SHORT, "narrow")
    return wide.render(items, kpi_label, recommended) + narrow.render(items, kpi_label, recommended)
