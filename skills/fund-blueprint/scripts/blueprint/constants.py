"""Single source of truth for field names, scoring tables, and shipped copy."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from .enums import Horizon, Nature, Quadrant, Verdict

VERSION = "0.9.1"

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

CONTACT_EMAIL = "info@nxtpartners.ai"
CONTACT_SUBJECT_TEXT = "NXT Fund Blueprint: next steps"
CONTACT_SUBJECT = quote(CONTACT_SUBJECT_TEXT)
DEMO_LABEL = "pe.nxtpartners.ai"
DEMO_URL = f"https://{DEMO_LABEL}"
DEMO_TEXT = "See a demo at "
SITE_NAME = "NXT Partners AI"
CLOSING_TITLE = "Help with implementation"

# Answer fields. A firm-level field is answered once, a detail field once per work area.
FIRM_FIELDS = ("strategy", "aum", "team", "fund_stage", "thesis", "pressure", "ai_stage", "ai_adoption", "ai_results", "ai_obstacle", "systems", "policy", "trust", "capacity", "region", "budget")
AI_FOLLOW_UPS = ("ai_adoption", "ai_results")
DETAIL_FIELDS = ("hours", "data", "owner", "error_cost", "usage", "ai_here")
KEY_AI_TOOLS = "ai_tools"
KEY_AI_TASKS = "ai_tasks"
KEY_KPI = "kpi"
KEY_WORKSTREAMS = "workstreams"
KEY_ACTIVITIES = "activities"
KEY_CUSTOM = "custom"
KEY_NAME = "name"
KEY_NATURE = "nature"
KEY_USES_AI = "uses_ai"
KEY_KPI_LINK = "kpi_link"
KPI_LINK_RELEVANCE = {"direct": 3, "some": 1, "none": 0}
CUSTOM_DEFAULT_RELEVANCE = 1
CUSTOM_NAME_MAX = 80
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
FIRM_NAME_MAX = 80
PUBLIC_FACT_MAX = 200
PUBLIC_FACTS_MAX = 6
SOURCE_URL_MAX = 300
MAX_WORKSTREAMS = 4

# Skipped answers use a neutral value, and the blueprint says so.
NEUTRAL_ANSWERS = {
    "strategy": "multi", "aum": "500m_2b", "team": "15_50", "fund_stage": "several", "thesis": "operational",
    "pressure": "lean", "ai_stage": "none", "ai_adoption": "under_10", "ai_results": "unmeasured", "ai_obstacle": "owner", "region": "other", "budget": "unset", "ai_here": "none", "systems": "connected", "policy": "pilot", "trust": "experimenting", "capacity": "ops_lead",
    "hours": "5_20", "data": "spreadsheets", "owner": "mid", "error_cost": "unsure", "usage": "unsure",
}

# Scoring model.
IMPACT_WEIGHT_RELEVANCE = 0.65
IMPACT_WEIGHT_VOLUME = 0.25
IMPACT_WEIGHT_SENIORITY = 0.10
IMPACT_UNRELATED_FACTOR = 0.5
IMPACT_BOOST = 0.08
HOURS_VOLUME = {"under_5": 0.1, "5_20": 0.4, "20_60": 0.7, "over_60": 1.0}
HOURS_RANGE = {"under_5": (0, 5), "5_20": (5, 20), "20_60": (20, 60), "over_60": (60, None)}
OWNER_SENIORITY = {"partners": 1.0, "mid": 0.65, "junior": 0.35, "operations": 0.45}
RELEVANCE_MAX = 3

THESIS_WORKSTREAMS = {
    "buy_build": ("sourcing", "execution", "value_creation"),
    "operational": ("value_creation", "reporting", "board"),
    "expansion": ("sourcing", "diligence", "exit"),
    "sector": ("knowledge", "diligence", "sourcing"),
    "income": ("reporting", "compliance", "accounting"),
    "special_situations": ("diligence", "execution", "reporting"),
    "origination": ("sourcing", "relations", "knowledge"),
}
STAGE_AREAS = {"raising": ("investors",), "deploying": ("investing",), "harvesting": ("portfolio",), "several": ()}

BASE_WEEKS = {Verdict.REMOVE: 2.0, Verdict.OPTIMIZE: 4.0, Verdict.AUTOMATE: 6.0, Verdict.ADD_AI: 6.0, Verdict.AGENTIC: 10.0}
BUILD_ON_WEEKS = {"task": 3.0, "adhoc": 3.0, "pilot": 6.0, "deployed": 4.0}
TECH_VERDICTS = (Verdict.AUTOMATE, Verdict.ADD_AI, Verdict.AGENTIC)
AI_VERDICTS = (Verdict.ADD_AI, Verdict.AGENTIC)
WEEKS_DATA = {"system": 1.0, "spreadsheets": 1.25, "documents": 1.25, "heads": 1.5}
WEEKS_SYSTEMS = {"integrated": 0.9, "connected": 1.0, "disconnected": 1.4, "manual": 1.25}
WEEKS_POLICY = {"approved": 1.0, "pilot": 1.15, "none": 1.5, "restricted": 2.0}
WEEKS_TRUST = {"daily": 0.9, "experimenting": 1.0, "skeptical": 1.25, "resistant": 1.5}
WEEKS_CAPACITY = {"in_house": 0.85, "ops_lead": 1.1, "partner": 0.9, "nobody": 1.4}
WEEKS_SEVERE_ERROR = 1.4
WEEKS_EXPERIENCE = {"none": 1.1, "individuals": 1.0, "pilots": 0.95, "deployed": 0.85}
WEEKS_RESULTS = {"measured": 0.9, "unmeasured": 1.0, "mixed": 1.05, "disappointing": 1.15}
WEEKS_MIN_FACTOR = 0.6
WEEKS_EFFORT = {"low": 0.7, "medium": 1.0, "high": 1.3}
WEEKS_SMALL_TEAM = 1.15
SMALL_TEAM = "under_15"

WEEKS_NOW = 30 / 7
WEEKS_NEXT = 90 / 7
WEEKS_LATER = 180 / 7
WEEKS_AXIS_MAX = 52.0
SPEED_BANDS = (
    (0.0, WEEKS_NOW, "Under 30 days"),
    (WEEKS_NOW, WEEKS_NEXT, "30 to 90 days"),
    (WEEKS_NEXT, WEEKS_LATER, "90 to 180 days"),
    (WEEKS_LATER, WEEKS_AXIS_MAX, "Over 180 days"),
)
SPEED_BANDS_SHORT = ("Under 30d", "30-90d", "90-180d", "Over 180d")
QUADRANT_WEEKS = WEEKS_NEXT
QUADRANT_IMPACT = 2.5
IMPACT_LEVELS = ((2.5, "Low"), (3.7, "Medium"), (99.0, "High"))
LEVEL_NAMES = ("Low", "Medium", "High")
IMPACT_MIN = 1.0
IMPACT_MAX = 5.0

# Shipped copy. No em dashes in anything a reader sees.
VERDICT_LABELS = {
    Verdict.AUTOMATE: "Automate", Verdict.ADD_AI: "Add AI", Verdict.OPTIMIZE: "Optimize",
    Verdict.AGENTIC: "Add agentic AI", Verdict.REMOVE: "Remove", Verdict.BUILD_ON: "Build on existing AI", Verdict.LEAVE: "Leave with people",
}
VERDICT_DEFINITIONS = {
    Verdict.AUTOMATE: "Fixed rules, no AI needed",
    Verdict.ADD_AI: "AI drafts, a person reviews",
    Verdict.OPTIMIZE: "Fix the process first",
    Verdict.AGENTIC: "An agent runs steps, a person approves",
    Verdict.REMOVE: "Stop doing it",
    Verdict.BUILD_ON: "AI is already here, improve it",
    Verdict.LEAVE: "Human judgment stays",
}
VERDICT_REASONS = {
    Verdict.AUTOMATE: "It follows fixed rules, so ordinary automation can do it without AI.",
    Verdict.ADD_AI: "It needs reading and drafting that rules cannot handle, so AI prepares the work and a person reviews it.",
    Verdict.AGENTIC: "It runs across several systems, so an agent can carry the steps while a person approves anything that leaves the firm.",
    Verdict.REMOVE: "You said the output is rarely used, so test stopping it before spending anything on it.",
    Verdict.LEAVE: "The value here comes from human judgment or relationships, so this stays with your people.",
}
REASON_REQUIRED = "You said the output is rarely used, but this work may be required or mistakes could be serious, so simplify it to the minimum instead of stopping it."
REQUIRED_SOLUTION = "Check what is actually required, and cut the process back to that minimum before spending anything on it."
REQUIRED_FIRST_STEP = "List who receives this output and which obligation requires it."
REASON_HEADS = "You said the knowledge is mostly in people's heads, so it needs writing down before automation or AI can help."
REASON_RESTRICTED = "Your policy restricts AI today, so the best available gain is a simpler process."
REASON_RESTRICTED_IN_USE = "You said AI is used here, and also that your policy restricts it. Settle that before anything else."
RESTRICTED_IN_USE_SOLUTION = "Bring this use under your policy, or pause it, before doing anything more with AI here."
RESTRICTED_IN_USE_FIRST_STEP = "Ask your CCO to review how AI is used on this task today."
REASON_SEVERE_MULTI = "It runs across several tools, and mistakes could be costly or their cost is unclear, so AI should prepare the work and a person should carry it out."
REASON_TRUST = "You said your team is resistant to AI output, so start with AI that prepares work under full review, not an agent."
REASON_NOT_READY = "Start with AI that prepares the work. An agent makes more sense once the firm has some experience with AI and someone owns it."
REASON_AI_UNKNOWN = "You did not say whether AI is already used here, so check that first. "
AI_UNKNOWN_FIRST_STEP = "Check whether anyone already uses AI on this task."
AI_ASSUMED_NOTE = "AI is used somewhere in this work area, but you did not say on which tasks"
PREPARE_PREFIX = "AI prepares each step for a person to carry out. "
NEUTRAL_CHECK = "The current owner reviews any change to this process."
OPTIMIZE_RELEVANCE = "Prepares the ground for later work on {kpi}"
REMOVE_RELEVANCE = "Frees time for other work"
LOW_EFFORT_IMPACT_CAP = 3.6

BUILD_ON_TEXT = {
    ("task", "any"): ("You said AI is already used on this task.", "Review how it is used, and agree one approved approach with clear review.", "Ask who uses AI on this task, and how."),
    ("adhoc", "any"): ("You said some people already use AI here informally, with no shared approach.", "Turn personal use into one approved way of working, with shared templates and clear review.", "Ask each person how they use AI on this task today."),
    ("pilot", "measured"): ("You have a trial here, and you said AI has shown measured gains at the firm. The decision is whether this one goes to the whole team.", "Decide whether to take this trial into daily use, with an owner and a monthly results check.", "Agree the results that would justify using it across the team."),
    ("pilot", "any"): ("You have a trial here, and you did not report measured gains from AI at the firm. Find out whether this one works before expanding it.", "Compare the trial with the old process, then decide whether to expand, fix, or stop it.", "Choose five cases to time with the current process and with the trial."),
    ("deployed", "measured"): ("This is standard for the team here, and you said AI has shown measured gains at the firm. Look next at the steps around it.", "Look for gains in the steps before and after this task, and keep measuring.", "Map the steps before and after this task, and find where people still rework the output."),
    ("deployed", "disappointing"): ("This is standard for the team here, and you described AI results at the firm as disappointing. Check whether that applies here before extending it.", "Review it against what users actually need, then fix, replace, or stop it.", "Ask three regular users what works and what does not, and review a sample of recent outputs."),
    ("deployed", "any"): ("This is standard for the team here, and you did not report measured gains from AI at the firm. Without a starting measure, you cannot tell whether to invest further.", "Measure time saved and error rates before spending more here.", "Pick two measures and start collecting them."),
}
DEFAULT_IN_USE_STAGE = "task"
GOAL_PREFIX = "The goal: "

ROUTE_LABEL = "How to get there"
ROUTES = {
    (Verdict.AUTOMATE, "low"): "Start with the automation in software you already pay for",
    (Verdict.AUTOMATE, "mid"): "Automation in your existing software, or a workflow tool if that falls short",
    (Verdict.AUTOMATE, "high"): "A workflow tool, or a connection built for you",
    (Verdict.ADD_AI, "low"): "An approved AI chat tool, with shared templates",
    (Verdict.ADD_AI, "mid"): "A specialist tool, if one fits, before building anything",
    (Verdict.ADD_AI, "high"): "A specialist tool, or something built on your own documents",
    (Verdict.AGENTIC, "low"): "A small trial on one workflow before committing budget",
    (Verdict.AGENTIC, "mid"): "A trial on one workflow, with outside help if needed",
    (Verdict.AGENTIC, "high"): "Built in-house or with a partner, connected to your software",
    (Verdict.BUILD_ON, "any"): "Keep your current tools for now, and decide on any change after measuring them",
    (Verdict.OPTIMIZE, "any"): "No new technology needed yet",
    (Verdict.REMOVE, "any"): "No technology needed",
}
BUDGET_TIER = {"unset": "low", "under_100k": "low", "100k_500k": "mid", "over_500k": "high"}

STAGE_PHRASES = {"none": "Not used yet", "individuals": "Individuals use AI on their own", "pilots": "Trials in some teams", "deployed": "Standard across teams"}
ADOPTION_PHRASES = {"under_10": "Under 10% of the team", "10_30": "10% to 30% of the team", "30_60": "30% to 60% of the team", "over_60": "Over 60% of the team"}
RESULTS_PHRASES = {"measured": "Measured gains", "unmeasured": "Useful, but not measured", "mixed": "Mixed so far", "disappointing": "Disappointing so far"}
OBSTACLE_PHRASES = {"data": "Data quality or access", "trust": "Trust in the output", "security": "Security or compliance", "owner": "No owner or no time"}
HERE_PHRASES = {"task": "In use on this task", "adhoc": "Some people, informally", "pilot": "A small trial", "deployed": "Standard for the team"}
REGION_NOTES = {
    "us": "Have counsel check how SEC recordkeeping and marketing rules apply to AI-assisted work.",
    "eu": "Have counsel check how GDPR, AIFMD, and the EU AI Act apply to these uses.",
    "uk": "Have counsel check how UK GDPR and FCA rules apply to these uses.",
    "other": "Have counsel check data protection and AI rules in each jurisdiction where you operate.",
}

REMOVE_SOLUTION = "Stop this work or cut it back, after checking with the people who receive it. If few would notice it stopping, automating it may not be worth it."
REMOVE_FIRST_STEP = "Check whether anything requires this work. If nothing does, skip one cycle, tell the recipients, and record who asks for it."
REMOVE_CHECK = "Keep anything required by regulation, your LPA, or a side letter."
HEADS_SOLUTION = "Write the process down before adding technology: the steps, the decisions, and where the information comes from."
HEADS_FIRST_STEP = "Have the person who does this most often write down the steps and decisions."
RESTRICTED_SOLUTION = "Simplify the process and templates now, then revisit AI once policy allows it."
RESTRICTED_FIRST_STEP = "Ask your CCO which AI uses could be allowed, starting with internal, non-confidential documents."
CUSTOM_SOLUTIONS = {
    Nature.RULES: "Write the rules down and automate the routine path, sending exceptions to the owner.",
    Nature.DRAFTING: "Have AI prepare a first draft from your source material, with citations, for the owner to review.",
    Nature.MULTI_SYSTEM: "Connect the tools involved, and let an agent carry the steps, with the owner approving the result.",
    Nature.JUDGMENT: "Keep the decision with your people. AI can prepare background and past examples.",
}
CUSTOM_FIRST_STEP = "Write down this task's inputs, decisions, and who receives the result."
CUSTOM_PREPARE_SOLUTION = "Have AI gather the information and prepare the work, and have the owner carry out each step."
CUSTOM_CHECK = "The current owner reviews results until error rates are known."
CUSTOM_TAG = "Added by you"

DATA_PHRASES = {"system": "in a proper system", "spreadsheets": "in spreadsheets and email", "documents": "in PDFs and documents", "heads": "in people's heads"}
OWNER_PHRASES = {"partners": "partners or principals", "mid": "VPs and associates", "junior": "analysts", "operations": "finance, IR, or ops staff"}
HOURS_PHRASES = {"under_5": "under 5 hours", "5_20": "5 to 20 hours", "20_60": "20 to 60 hours", "over_60": "over 60 hours"}
RELEVANCE_PHRASES = {3: "Estimated direct effect on {kpi}", 2: "Estimated strong link to {kpi}", 1: "Estimated some effect on {kpi}", 0: "No direct link to {kpi} expected"}
RELEVANCE_NOT_ASSESSED = "Link to {kpi} not assessed"

FIRM_WIDE_LABEL = "Firm-wide"
FIRM_WIDE_OWNER = "COO or managing partner"
FIRM_WIDE_SPEED = "Aim to settle within 30 days"
NEXT_30_MAX_FOUNDATIONS = 2
PLAIN_TERMS = (
    ("Automation", "Software that follows fixed rules, the same way every time. Where rules are enough, you may not need AI at all."),
    ("AI that drafts", "Software that can read documents and write a first version, much like a junior colleague. A person reviews the result before it is used."),
    ("Agentic AI", "AI that carries out several steps in a row across your tools, such as requesting a file, checking it, and loading it. In this plan, a person approves anything that leaves the firm."),
    ("Trial", "A small, time-limited test with a few people, to learn whether something works before the whole team uses it."),
    ("First working version", "The point when a real team can use it on real work. Refinement continues after that."),
    ("Human check", "The step where a named person reviews the output. Accountability stays with people, not software."),
)
TIMELINE_MARKS = ("Today", "30 days", "90 days", "180 days", "Later")

METHOD_NOTE = "How the estimates work: speed and impact come from fixed planning rules applied to your answers, such as the hours you reported, where the information lives, your constraints, and how directly each task relates to your KPI. They are planning assumptions, not benchmarks, and they use no benchmark data from any firm. Test them with your team before relying on them."
HORIZON_LABELS = {Horizon.NOW: "Now", Horizon.NEXT: "Next", Horizon.LATER: "Later"}
HORIZON_SPANS = {Horizon.NOW: "Under 30 days, estimated", Horizon.NEXT: "30 to 90 days, estimated", Horizon.LATER: "Over 90 days, estimated"}
QUADRANT_LABELS = {Quadrant.QUICK_WINS: "Quick wins", Quadrant.STRATEGIC_BETS: "Strategic bets", Quadrant.FILL_INS: "Fill-ins", Quadrant.DEPRIORITIZE: "Deprioritize"}

SHADOW_FOUNDATION = ("Bring existing AI use under a policy", "You said people use AI, and that the firm has no AI policy. Confidential data may be reaching tools you have not approved. Set rules before adding anything new.", "Agree which AI tools are approved, and what data may go into them.")
SHADOW_RESTRICTED_FOUNDATION = ("Settle how existing AI use fits your policy", "You said people use AI, and also that your policy restricts it. Find out what is happening in practice, and decide what is allowed.", "Ask your CCO to review how AI is used today, against your policy.")
FOUNDATIONS = {
    ("ai_results", "unmeasured"): ("Measure what you already have", "You said AI is useful, but not measured. Without a starting measure, you cannot tell which work to expand.", "Pick two measures and start recording them for your current AI work."),
    ("ai_results", "disappointing"): ("Find out why earlier AI work fell short", "You described results so far as disappointing. Review what fell short before starting something new: the use case, the data, or the adoption.", "List what was tried, and the reason each effort fell short."),
    ("ai_obstacle", "data"): ("Connect your core data", "You named data as the main obstacle. Look first for a connection that several items below depend on.", "List which items below depend on the same data."),
    ("ai_obstacle", "trust"): ("Build trust with visible checks", "You named trust as the main obstacle. Show sources in every output, and keep review with your senior people at first.", "Agree which outputs must show their sources, and who reviews them."),
    ("ai_obstacle", "security"): ("Settle security and compliance early", "You named this as the main obstacle. Agree approved tools and data rules with your CCO before any trial begins.", "Meet your CCO to agree approved tools and data rules."),
    ("ai_obstacle", "owner"): ("Name an owner", "You named ownership as the main obstacle. Name one accountable person and protect time for them.", "Name one accountable person, and protect time for them."),
    ("policy", "none"): ("Agree an AI policy", "AI items below are held back without one. A short list of approved tools and data rules is enough to start.", "Write a one-page list of approved tools and data rules."),
    ("policy", "restricted"): ("Revisit the AI restriction", "AI items are held back until your policy allows them. Ask your CCO which low-risk uses could be approved first.", "Ask your CCO which low-risk AI uses could be approved first."),
    ("systems", "disconnected"): ("Connect your core data", "You said your software tools do not share data. Look first for a connection that several items below depend on.", "List which items below depend on the same data."),
    ("systems", "manual"): ("Give key data one home", "You said most work runs on Excel and email. Pick one dataset to centralize first, and let the first item below decide which.", "Choose the one dataset to centralize first."),
    ("trust", "skeptical"): ("Win over the skeptics", "Pick one item that a skeptical senior person cares about, and measure it next to the current process.", "Pick one item that a skeptical senior person cares about."),
    ("trust", "resistant"): ("Start with work people dislike", "With a resistant team, begin with tasks nobody wants to keep, and leave review power with them.", "Ask the team which routine tasks they would most like to lose."),
    ("capacity", "nobody"): ("Name an owner", "Nobody is assigned to implement this yet, so the plan has no one to carry it out. Name one accountable person first.", "Name one accountable person, and protect time for them."),
}
