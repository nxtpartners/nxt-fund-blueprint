"""Single source of truth for field names and scoring tables. Report wording is re-exported from wording.py."""
from __future__ import annotations

from pathlib import Path

from .enums import Rule, Spend, Verdict
from .wording import *  # noqa: F401,F403

VERSION = "0.23.7"

SKILL_DIR = Path(__file__).resolve().parents[2]
CATALOG_PATH = SKILL_DIR / "references" / "catalog.json"
QUESTIONS_PATH = SKILL_DIR / "references" / "questions.json"
LOGO_PATH = SKILL_DIR / "assets" / "nxt-partners-logo-light.png"
FONT_FILES = (
    ("Space Grotesk", 700, SKILL_DIR / "assets" / "fonts" / "SpaceGrotesk-Bold.woff2"),
    ("Inter", 400, SKILL_DIR / "assets" / "fonts" / "Inter-Regular.woff2"),
    ("Inter", 600, SKILL_DIR / "assets" / "fonts" / "Inter-SemiBold.woff2"),
    ("JetBrains Mono", 400, SKILL_DIR / "assets" / "fonts" / "JetBrainsMono-Regular.woff2"),
)

# Answer fields. A firm-level field is answered once, a detail field once per work area.
FIRM_FIELDS = (
    "strategy",
    "team",
    "thesis",
    "pressure",
    "kpi_status",
    "ai_stage",
    "ai_adoption",
    "ai_results",
    "systems",
    "policy",
    "region",
)
FIRM_LISTS = ("fund_stage", "trust", "capacity")
OPTIONAL_FIRM_FIELDS = ("aum", "budget")
AI_FOLLOW_UPS = ("ai_adoption", "ai_results")
NOT_NOTED_WHEN_SKIPPED = ("region",)
DETAIL_SINGLE = ("hours", "error_cost", "depends", "rhythm", "same_way", "ai_here")
DETAIL_LISTS = ("sources", "who", "time_goes")
DETAIL_FIELDS = DETAIL_SINGLE + DETAIL_LISTS
NOT_NOTED_DETAIL = ("rhythm", "same_way")
# Which questions each depth asks. Anything else is not asked, so it is never reported as skipped.
ASKED_AT_DEPTH = {
    "deep": DETAIL_FIELDS,
    "second": ("hours", "sources", "time_goes", "ai_here"),
    "quick": ("hours", "sources"),
}
KEY_DEPTH = "depth"
KEY_LEGACY_TASKS = "legacy_tasks"
KEY_HARM_TASKS = "harm_tasks"
KEY_HEAVY_TASK = "heavy_task"
KEY_MEASURES_TRACKED = "measures_tracked"
KEY_MEASURES_OFF = "measures_off"
KEY_UNTRACKED = "untracked"
KEY_WALKTHROUGH = "walkthrough"
KEY_STEPS = "steps"
KEY_SLOW_STEP = "slow_step"
KEY_NAMED_TASK = "named_task"
WALKTHROUGH_STEPS_MAX = 6
WALKTHROUGH_STEP_MAX = 160
KEY_AI_TOOLS = "ai_tools"
KEY_AI_TASKS = "ai_tasks"
KEY_KPI = "kpi"
KEY_KPI_NAME = "kpi_name"
CUSTOM_KPI = "custom"
KPI_NAME_MAX = 44
KPI_NAME_WORD_MAX = 24
KEY_WORKSTREAMS = "workstreams"
KEY_ACTIVITIES = "activities"
KEY_CUSTOM = "custom"
KEY_NAME = "name"
KEY_NATURE = "nature"
KEY_USES_AI = "uses_ai"
KEY_KPI_LINK = "kpi_link"
KPI_LINK_RELEVANCE = {"direct": 3, "some": 1, "none": 0}
CUSTOM_DEFAULT_RELEVANCE = 1
KEY_KPI_LINKS = "kpi_links"
RELEVANCE_FLOOR = 0.5
RELATIVE_IMPACT = {"High": 4.0, "Medium": 3.0, "Low": 2.0}
RELATIVE_TIERS = ("High", "Medium", "Low")
CUSTOM_NAME_MAX = 160
KEY_THESIS_SUMMARY = "thesis_summary"
KEY_THESIS_FOCUS = "thesis_focus"
KEY_THESIS_NOTES = "thesis_notes"
THESIS_SUMMARY_MAX = 280
THESIS_NOTE_MAX = 220
THESIS_FOCUS_MAX = 3
KEY_FIRM_NAME = "firm_name"
KEY_PUBLIC_FACTS = "public_facts"
KEY_FACT = "fact"
KEY_SOURCE = "source"
FIRM_NAME_MAX = 160
PUBLIC_FACT_MAX = 200
PUBLIC_FACTS_MAX = 6
SOURCE_URL_MAX = 300
MAX_WORKSTREAMS = 4

# Skipped answers use a neutral value, and the blueprint says so.
NEUTRAL_ANSWERS = {
    "strategy": "multi",
    "team": "15_50",
    "thesis": "operational",
    "pressure": "lean",
    "kpi_status": "no_target",
    "ai_stage": "none",
    "ai_adoption": "under_10",
    "ai_results": "unmeasured",
    "region": "other",
    "ai_here": "none",
    "systems": "connected",
    "policy": "pilot",
    "hours": "20_60",
    "error_cost": "unsure",
    "depends": "effort",
    "rhythm": "monthly",
    "same_way": "same",
    "fund_stage": [],
    "trust": ["experimenting"],
    "capacity": ["ops_lead"],
    "sources": ["spreadsheets"],
    "who": ["investment"],
    "time_goes": [],
}

# Scoring model. All of these are planning assumptions, not data.
RELEVANCE_MAX = 3
HOURS_MIDPOINT = {"under_20": 10, "20_60": 40, "60_200": 130, "over_200": 300}
HOURS_RANGE = {"under_20": (0, 20), "20_60": (20, 60), "60_200": (60, 200), "over_200": (200, None)}
WHO_RATE = {"partners": 4.0, "investment": 2.0, "operations": 1.0, "outside": 1.0}
VALUE_CEILING = 300 * 4.0
HEAVY_TASK_SHARE = 2.0
EFFECT_VALUE_FLOOR = 0.5
IMPACT_BOOST = 0.08
STEADY_VALUE_FACTOR = 1.1
PRIORITY_WEIGHT_IMPACT = 0.6
PRIORITY_WEIGHT_VALUE = 0.4
PRIORITY_SPEED_BONUS = 0.5
NAMED_TASK_FLOOR = 3
IMPACT_CAP_SOME = 3.6
IMPACT_CAP_PREPARES = 2.4
LINKED_RELEVANCE_MIN = 2
# Senior hours can only be freed where senior people do the work.
SENIOR_LINK_CAP = {"partners": 3, "investment": 2, "operations": 1, "outside": 1}
TEAM_ROUTE_TIER = {"under_15": "low", "15_50": "mid", "50_150": "mid", "over_150": "high"}
SMALL_TEAM = "under_15"
LARGE_TEAM = "over_150"

THESIS_WORKSTREAMS = {
    "buy_build": ("sourcing", "execution", "value_creation"),
    "operational": ("value_creation", "reporting", "board"),
    "expansion": ("sourcing", "diligence", "exit"),
    "sector": ("knowledge", "diligence", "sourcing"),
    "income": ("reporting", "compliance", "accounting"),
    "special_situations": ("diligence", "execution", "reporting"),
    "origination": ("sourcing", "relations", "knowledge"),
}
STAGE_AREAS = {"raising": ("investors",), "deploying": ("investing",), "harvesting": ("portfolio",)}

BASE_WEEKS = {
    Verdict.REMOVE: 3.5,
    Verdict.OPTIMIZE: 5.0,
    Verdict.AUTOMATE: 6.0,
    Verdict.ADD_AI: 7.0,
    Verdict.AGENTIC: 16.0,
}
BUILD_ON_WEEKS = {"task": 3.0, "adhoc": 3.0, "pilot": 6.0, "deployed": 4.0}
TECH_VERDICTS = (Verdict.AUTOMATE, Verdict.ADD_AI, Verdict.AGENTIC)
AI_VERDICTS = (Verdict.ADD_AI, Verdict.AGENTIC)
WEEKS_SOURCE = {"system": 1.0, "spreadsheets": 1.2, "email": 1.3, "documents": 1.25}
WEEKS_EXTRA_SOURCE = 0.05
WEEKS_SYSTEMS = {"integrated": 0.9, "connected": 1.0, "disconnected": 1.3, "manual": 1.4}
WEEKS_POLICY = {"approved": 1.0, "pilot": 1.15, "none": 1.25, "restricted": 2.0}
WEEKS_TRUST = {"daily": 0.9, "experimenting": 1.0, "skeptical": 1.25, "resistant": 1.5}
WEEKS_CAPACITY = {"in_house": 0.85, "ops_lead": 1.1, "partner": 0.9, "nobody": 1.25}
WEEKS_ERROR = {"minor": 1.0, "awkward": 1.1, "severe": 1.4, "unsure": 1.1}
WEEKS_ADOPTION = {"under_10": 1.1, "10_30": 1.05, "30_60": 1.0, "over_60": 0.9}
WEEKS_WAIT_OUTSIDE = 1.15
WEEKS_EXPERIENCE = {"none": 1.1, "individuals": 1.0, "pilots": 0.95, "deployed": 0.85}
WEEKS_RESULTS = {"measured": 0.9, "unmeasured": 1.0, "mixed": 1.05, "disappointing": 1.15}
WEEKS_MIN_FACTOR = 0.9
WEEKS_EFFORT = {"low": 0.7, "medium": 1.0, "high": 1.3}

WEEKS_NOW = 30 / 7
WEEKS_NEXT = 90 / 7
WEEKS_LATER = 180 / 7
WEEKS_AXIS_MAX = 52.0
WEEKS_SIXTY = 60 / 7
SPEED_BANDS = (
    (0.0, WEEKS_NOW, "Under 30 days"),
    (WEEKS_NOW, WEEKS_SIXTY, "30 to 60 days"),
    (WEEKS_SIXTY, WEEKS_NEXT, "60 to 90 days"),
    (WEEKS_NEXT, WEEKS_AXIS_MAX, "Over 90 days"),
)
SPEED_BANDS_SHORT = ("Under 30d", "30-60d", "60-90d", "Over 90d")
SLOW_BAND_COUNT = 2
QUADRANT_WEEKS = WEEKS_SIXTY
QUADRANT_IMPACT = 2.5
IMPACT_LEVELS = ((2.5, "Low"), (3.7, "Medium"), (99.0, "High"))
LEVEL_NAMES = ("Low", "Medium", "High")
IMPACT_MIN = 1.0
IMPACT_MAX = 5.0
INFORMAL_STAGE = "adhoc"
DEPLOYED_IMPACT_CAP = 3.6
DEFAULT_IN_USE_STAGE = "task"
BUDGET_TIER = {"unset": "low", "under_100k": "low", "100k_500k": "mid", "over_500k": "high"}
ALL_SPEND = (Spend.NONE, Spend.SMALL, Spend.DECISION)
BUDGET_COVERS = {
    "": ALL_SPEND,
    "unset": (Spend.NONE,),
    "under_100k": (Spend.NONE, Spend.SMALL),
    "100k_500k": ALL_SPEND,
    "over_500k": ALL_SPEND,
}
# A skipped answer means no limit: normal order, all circles, one view.
BUDGET_REORDERS = ("unset", "under_100k")
KEY_KPI_VALUE = "kpi_value"
KPI_VALUE_MAX = 60
COVERAGE_MAX = 2
NEXT_30_MAX_FOUNDATIONS = 3

# Reading the answers together, on the first page.
READING_MAX = 4
CHANGE_NAMES_MAX = 3
SENIOR_KPI = "senior_hours"
MULTI_STRATEGY = "multi"
HUMAN_NATURE_VALUES = ("judgment", "relationship")
MEASURE_ACTIONS_MAX = 1
INTEGRATED_SYSTEMS = "integrated"
NO_LINK_PRIORITY_FACTOR = 0.7
PRIORITY_WEIGHTS_BY_STATUS = {"off_target": (0.75, 0.25), "on_target": (0.4, 0.6)}
ASKED_LISTS_AT_DEPTH = {
    "deep": ("legacy_tasks", "harm_tasks", "heavy_task", "measures", "walkthrough"),
    "second": ("legacy_tasks", "heavy_task", "measures"),
    "quick": (),
}
CHANGE_GROUPS_MAX = 2
COUNTED_AS_UNTOLD = ("ai_adoption", "ai_results", "thesis")
CREDIT_NOTE_STRATEGY = "credit"
NAMED_PRIORITY_FACTOR = 1.35
PROCESS_TEXT_RULES = (
    Rule.KEEP_MINIMAL,
    Rule.RESTRICTED,
    Rule.AGREE_FIRST,
    Rule.REDO,
    Rule.ONE_PLACE,
    Rule.SERIOUS_PROCESS_FIRST,
)
BUDGET_ALL_AT_ONCE = "under_100k"
NO_SIGNOFF_WORKSTREAMS = ("knowledge", "sourcing")
CAPACITY_OUTSIDE = "partner"
