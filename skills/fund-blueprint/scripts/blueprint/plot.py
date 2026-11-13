"""Speed of execution against estimated KPI impact, as inline SVG with a wide and a narrow layout."""
from __future__ import annotations

import html
import textwrap
from typing import Any, Dict, List, Tuple

from . import constants as c
from . import tokens as t
from .enums import Quadrant
from .models import ScoredActivity
from .planning.levels import effect_text, impact_level
from .text import lower_first


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
    points = f"{x:.1f},{y - reach:.1f} {x + reach:.1f},{y:.1f} {x:.1f},{y + reach:.1f} {x - reach:.1f},{y:.1f}"
    return f'<polygon points="{points}" {attributes}/>'


def mark_colors(item: ScoredActivity) -> Tuple[str, str, str]:
    """Fill, outline, and number colour: filled verdicts carry a white number, hollow ones a coloured outline."""
    color = t.VERDICT_COLORS[item.verdict]
    if item.verdict in t.VERDICT_HOLLOW:
        return t.COLOR_SURFACE, color, color
    return color, t.COLOR_SURFACE, t.COLOR_SURFACE


def mark_glyph(item: ScoredActivity, x: float, y: float, radius: float, label: int, ringed: bool) -> str:
    """The marker as drawn on the plot: colour, fill, shape for money, and a ring when recommended."""
    fill, stroke, ink = mark_colors(item)
    ring_style = f'fill="none" stroke="{t.COLOR_INK}" stroke-width="{t.PLOT_RING_STROKE}"'
    ring = mark_shape(x, y, radius + t.PLOT_RING_GAP, item.fits, ring_style) if ringed else ""
    mark_style = f'fill="{fill}" stroke="{stroke}" stroke-width="{t.PLOT_MARK_STROKE}"'
    return (
        ring
        + mark_shape(x, y, radius, item.fits, mark_style)
        + f'<text x="{x:.0f}" y="{y + t.PLOT_TEXT_NUDGE:.0f}" font-size="{label}" fill="{ink}" '
        f'text-anchor="middle" font-weight="{t.PLOT_LABEL_WEIGHT}" aria-hidden="true">{item.number}</text>'
    )


def mark_badge(item: ScoredActivity, ringed: bool) -> str:
    """The same marker, small, to name a priority anywhere else in the report."""
    centre = t.BADGE_BOX / 2
    return (
        f'<svg class="badge" viewBox="0 0 {t.BADGE_BOX} {t.BADGE_BOX}" aria-hidden="true">'
        f"{mark_glyph(item, centre, centre, t.BADGE_RADIUS, t.BADGE_LABEL, ringed)}</svg>"
    )


def level_index(impact: float) -> int:
    return c.LEVEL_NAMES.index(impact_level(impact))


class Canvas:
    def __init__(self, spec: Dict[str, int], band_labels: Tuple[str, ...], kind: str) -> None:
        self.spec, self.band_labels, self.kind = spec, band_labels, kind
        self.left, self.right = spec["left"], spec["width"] - spec["right"]
        self.top, self.bottom = spec["top"], spec["height"] - spec["bottom"]
        self.band_width = (self.right - self.left) / len(c.SPEED_BANDS)
        self.level_height = (self.bottom - self.top) / len(c.LEVEL_NAMES)

    def text(
        self,
        x: float,
        y: float,
        content: str,
        size: int,
        fill: str = t.COLOR_INK_SOFT,
        anchor: str = "middle",
        weight: int = 400,
    ) -> str:
        return (
            f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{html.escape(content)}</text>'
        )

    def y_title(self, kpi_text: str) -> str:
        """The firm's own number names the axis. A long name takes two lines, so it never runs off the plot."""
        lines = textwrap.wrap(c.Y_AXIS_TITLE.format(kpi=kpi_text), self.spec["title_wrap"])[:2]
        middle = (self.top + self.bottom) / 2
        parts = []
        for index, line in enumerate(lines):
            x = t.PLOT_Y_TITLE_X + index * t.PLOT_Y_TITLE_LINE
            parts.append(
                f'<text x="{x}" y="{middle:.0f}" transform="rotate(-90 {x} {middle:.0f})" '
                f'font-size="{self.spec["axis"]}" fill="{t.COLOR_INK}" text-anchor="middle" '
                f'font-weight="{t.PLOT_LABEL_WEIGHT}">{html.escape(line)}</text>'
            )
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

    def line(self, x1: Any, x2: Any, y1: Any, y2: Any, stroke: str, extra: str = "") -> str:
        """Coordinates arrive as the caller wants them printed, so the numbers on the plot stay as they were."""
        return f'<line x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" stroke="{stroke}"{extra}/>'

    def grid(self) -> List[str]:
        """Level labels and rules, band ticks, the two axes, and the dashed lines that split the quadrants."""
        label, parts = self.spec["label"], []
        for index, name in enumerate(c.LEVEL_NAMES):
            y = self.bottom - (index + 0.5) * self.level_height + t.PLOT_TEXT_NUDGE
            parts.append(self.text(self.left - t.PLOT_TICK_GAP, y, name, label, anchor="end"))
            if index:
                y = f"{self.bottom - index * self.level_height:.0f}"
                parts.append(self.line(self.left, self.right, y, y, t.COLOR_LINE))
        for index in range(1, len(c.SPEED_BANDS)):
            x = f"{self.left + index * self.band_width:.0f}"
            parts.append(self.line(x, x, self.bottom, self.bottom + t.PLOT_TICK, t.COLOR_INK))
        axis = f' stroke-width="{t.PLOT_AXIS_STROKE}"'
        dash = f' stroke-dasharray="{t.PLOT_DASH}"'
        mid_x = f"{self.left + c.SLOW_BAND_COUNT * self.band_width:.0f}"
        mid_y = f"{self.bottom - self.level_height:.0f}"
        parts.append(self.line(self.left, self.right, self.bottom, self.bottom, t.COLOR_INK, axis))
        parts.append(self.line(self.left, self.left, self.top, self.bottom, t.COLOR_INK, axis))
        parts.append(self.line(mid_x, mid_x, self.top, self.bottom, t.COLOR_LINE_STRONG, dash))
        parts.append(self.line(self.left, self.right, mid_y, mid_y, t.COLOR_LINE_STRONG, dash))
        return parts

    def corner_labels(self) -> List[str]:
        right = self.right - t.PLOT_CORNER_INSET_RIGHT
        left = self.left + t.PLOT_CORNER_INSET_X
        top = self.top + t.PLOT_CORNER_INSET_TOP
        bottom = self.bottom - t.PLOT_CORNER_INSET_BOTTOM
        corners = (
            (right, top, "end", Quadrant.QUICK_WINS, t.COLOR_INK),
            (left, top, "start", Quadrant.STRATEGIC_BETS, t.COLOR_INK_SOFT),
            (right, bottom, "end", Quadrant.FILL_INS, t.COLOR_INK_SOFT),
            (left, bottom, "start", Quadrant.DEPRIORITIZE, t.COLOR_INK_SOFT),
        )
        names = c.QUADRANT_LABELS_SHORT if self.kind == "narrow" else c.QUADRANT_LABELS
        return [
            self.text(x, y, names[quadrant], self.spec["label"], fill=fill, anchor=anchor, weight=t.PLOT_LABEL_WEIGHT)
            for x, y, anchor, quadrant, fill in corners
        ]

    def axis_labels(self, kpi_text: str) -> List[str]:
        label, axis = self.spec["label"], self.spec["axis"]
        y = self.bottom + t.PLOT_BAND_LABEL_OFFSET
        parts = [
            self.text(self.right - (index + 0.5) * self.band_width, y, band, label)
            for index, band in enumerate(self.band_labels)
        ]
        parts.append(self.text(
            (self.left + self.right) / 2, self.spec["height"] - t.PLOT_AXIS_TITLE_OFFSET,
            "Estimated speed, faster to the right", axis, fill=t.COLOR_INK, weight=t.PLOT_LABEL_WEIGHT,
        ))
        parts.append(self.y_title(kpi_text))
        return parts

    def marker(self, item: ScoredActivity, x: float, y: float, kpi_text: str, ringed: bool) -> str:
        radius, label = self.spec["radius"], self.spec["label"]
        summary = (
            f"{item.number}. {item.label}: {c.VERDICT_LABELS[item.verdict]}, {item.speed_label}, "
            f"{effect_text(item.impact, kpi_text)}, {item.money_line}"
        )
        return (
            f'<g class="mark" tabindex="0" role="img" aria-label="{html.escape(summary, quote=True)}">'
            f"<title>{html.escape(summary)}</title>{mark_glyph(item, x, y, radius, label, ringed)}</g>"
        )

    def render(self, items: List[ScoredActivity], kpi_label: str, recommended: Tuple[int, ...]) -> str:
        self.fit_height(items)
        spec = self.spec
        kpi_text = lower_first(kpi_label)
        parts = [
            f'<svg viewBox="0 0 {spec["width"]} {spec["height"]}" role="group" '
            "aria-label=\"Each numbered activity by speed of execution and estimated impact on "
            f'{html.escape(kpi_label, quote=True)}. The table below holds the same data." '
            f'class="plot plot-{self.kind}">'
        ]
        parts += self.grid() + self.corner_labels() + self.axis_labels(kpi_text)
        spots = self.place_markers(items)
        for item in sorted(items, key=lambda row: row.number):
            x, y = spots[item.number]
            parts.append(self.marker(item, x, y, kpi_text, item.number in recommended))
        parts.append("</svg>")
        return "".join(parts)


def render_plot(items: List[ScoredActivity], kpi_label: str, recommended: Tuple[int, ...] = ()) -> str:
    wide = Canvas(t.PLOT_WIDE, tuple(band[2] for band in c.SPEED_BANDS), "wide")
    narrow = Canvas(t.PLOT_NARROW, c.SPEED_BANDS_SHORT, "narrow")
    return wide.render(items, kpi_label, recommended) + narrow.render(items, kpi_label, recommended)
