"""Presentation values, from the NXT Partners identity. Edit here to restyle the blueprint."""
from __future__ import annotations

from .enums import Verdict

COLOR_INK = "#141428"
COLOR_INK_SOFT = "#55555F"
COLOR_LINE = "#E3E3E8"
COLOR_LINE_STRONG = "#7C7C88"
COLOR_SURFACE = "#FFFFFF"
COLOR_ACCENT = "#644FCB"
COLOR_ACCENT_HOVER = "#5641B5"

# Filled colours pass the dataviz palette checker. Hollow markers are the secondary encoding for the two
# verdicts that involve no new technology decision or that improve something existing.
VERDICT_COLORS = {
    Verdict.AUTOMATE: "#644FCB",
    Verdict.ADD_AI: "#007D9C",
    Verdict.AGENTIC: "#B4236B",
    Verdict.REMOVE: "#5E7D00",
    Verdict.OPTIMIZE: "#55555F",
    Verdict.BUILD_ON: "#644FCB",
    Verdict.LEAVE: "#55555F",
}
VERDICT_HOLLOW = (Verdict.OPTIMIZE, Verdict.BUILD_ON)

FONT_DISPLAY = "'Space Grotesk', system-ui, sans-serif"
FONT_BODY = "'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif"
FONT_MONO = "'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace"

SPACE_PAGE = "clamp(1.25rem, 0.75rem + 2.5vw, 3.5rem)"
SPACE_SECTION = "clamp(2rem, 1.6rem + 2vw, 3.5rem)"
SPACE_BLOCK = "clamp(1rem, 0.85rem + 0.7vw, 1.6rem)"
SPACE_GAP = "clamp(1rem, 0.75rem + 1.2vw, 2.25rem)"
TEXT_HEADLINE = "clamp(1.6rem, 1.25rem + 1.7vw, 2.6rem)"
TEXT_SECTION = "clamp(1.1rem, 1.02rem + 0.4vw, 1.3rem)"
TEXT_ITEM = "clamp(1.02rem, 0.98rem + 0.2vw, 1.12rem)"
TEXT_BODY = "clamp(0.92rem, 0.89rem + 0.15vw, 1rem)"
TEXT_SMALL = "clamp(0.78rem, 0.76rem + 0.1vw, 0.85rem)"
RULE_HEAVY = f"2px solid {COLOR_INK}"
RULE_LIGHT = f"1px solid {COLOR_LINE}"
RADIUS_BUTTON = "8px"
LOGO_HEIGHT = "clamp(2.4rem, 2.1rem + 1vw, 3.1rem)"
PAGE_MAX_WIDTH = "72rem"
SECTION_RAIL = "13rem"
RAIL_BREAKPOINT = "54rem"
COLUMN_MIN = "min(100%, 15rem)"
MIN_TARGET = "44px"

LAYOUT_BREAKPOINT = "44rem"
PLOT_NARROW_BREAKPOINT = "34rem"
PLOT_WIDE = {"width": 760, "height": 480, "left": 74, "right": 16, "top": 14, "bottom": 64, "radius": 12, "label": 12, "axis": 13}
PLOT_NARROW = {"width": 420, "height": 500, "left": 84, "right": 8, "top": 14, "bottom": 66, "radius": 13, "label": 14, "axis": 15}
PLOT_AXIS_STROKE = 1.5
PLOT_DASH = "3 4"
PLOT_MARK_STROKE = 2
PLOT_LABEL_WEIGHT = 600
PLOT_MARK_GAP = 5
PLOT_TICK_GAP = 8
PLOT_CORNER_INSET_X = 8
PLOT_CORNER_INSET_RIGHT = 6
PLOT_CORNER_INSET_TOP = 14
PLOT_CORNER_INSET_BOTTOM = 8
PLOT_BAND_LABEL_OFFSET = 20
PLOT_AXIS_TITLE_OFFSET = 12
PLOT_Y_TITLE_X = 14
PLOT_TEXT_NUDGE = 4
