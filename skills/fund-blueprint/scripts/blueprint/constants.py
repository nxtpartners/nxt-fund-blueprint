"""Single source of truth for field names, scoring tables, and shipped copy."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from .enums import Horizon, KpiClaim, Nature, Quadrant, Rule, Verdict, Spend

VERSION = "0.22.5"

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
CLOSING_TITLE = "Want a second opinion on this plan?"
CLOSING_BODY = "This plan rests on one person's answers and fixed rules. NXT Partners AI can test it with your team, correct what is wrong, and help you carry out the moves you keep. If that would help, email us this report and tell us which move you would start with."

# Answer fields. A firm-level field is answered once, a detail field once per work area.
FIRM_FIELDS = ("strategy", "team", "thesis", "pressure", "kpi_status", "ai_stage", "ai_adoption", "ai_results", "systems", "policy", "region")
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
WALKTHROUGH_STEP_MAX = 80
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
    "strategy": "multi", "team": "15_50", "thesis": "operational", "pressure": "lean", "kpi_status": "no_target",
    "ai_stage": "none", "ai_adoption": "under_10", "ai_results": "unmeasured", "region": "other", "ai_here": "none",
    "systems": "connected", "policy": "pilot", "hours": "20_60", "error_cost": "unsure", "depends": "effort", "rhythm": "monthly", "same_way": "same",
    "fund_stage": [], "trust": ["experimenting"], "capacity": ["ops_lead"], "sources": ["spreadsheets"], "who": ["investment"], "time_goes": [],
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
SMALL_TEAM_OWNER = "Whoever does this today"
WHO_OWNER = {"partners": "The partner who does this today", "investment": "The VP, associate, or analyst who does this today", "operations": "The finance, IR, compliance, or ops person who does this today", "outside": "Whoever manages your provider"}
STRATEGY_WORDS = {
    "credit": (("portfolio companies", "borrowers"), ("portfolio company", "borrower"), ("portcos", "borrowers"), ("portco", "borrower")),
    "growth": (("inbound teaser or CIM", "inbound deck"), ("teasers and CIMs", "inbound decks"), ("CIMs", "decks"), ("CIM", "deck"), ("teasers", "inbound decks"), ("teaser", "inbound deck")),
}
MULTI_STRATEGY_STEP_LEAD = "Pick one strategy to start in. "
TEAM_REVIEW_ACTION = "Have each department lead correct the answers for their area, because this plan rests on one person's view."

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

BASE_WEEKS = {Verdict.REMOVE: 3.5, Verdict.OPTIMIZE: 5.0, Verdict.AUTOMATE: 6.0, Verdict.ADD_AI: 7.0, Verdict.AGENTIC: 16.0}
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

# Shipped copy. No em dashes in anything a reader sees.
VERDICT_LABELS = {
    Verdict.AUTOMATE: "Automate", Verdict.ADD_AI: "Add AI", Verdict.OPTIMIZE: "Optimize",
    Verdict.AGENTIC: "Let AI run the steps (agentic AI)", Verdict.REMOVE: "Remove", Verdict.BUILD_ON: "Build on existing AI", Verdict.LEAVE: "Leave with people",
}
VERDICT_DEFINITIONS = {
    Verdict.AUTOMATE: "Fixed rules, no AI needed",
    Verdict.ADD_AI: "AI drafts, a person reviews",
    Verdict.OPTIMIZE: "Fix the process first",
    Verdict.AGENTIC: "AI runs the steps, a person approves",
    Verdict.REMOVE: "Stop doing it",
    Verdict.BUILD_ON: "AI is already here, improve it",
    Verdict.LEAVE: "Human judgment stays",
}
# Each verdict rule in one place: its verdict, reason, what replaces the catalog text, and what it may claim about the KPI.
# None means use the catalog's own text. "{kpi}" and similar placeholders are filled when scoring.
RULES = {
    Rule.LEAVE: {"verdict": Verdict.LEAVE, "reason": "The value here comes from human judgment or relationships, so this stays with your people.", "claim": KpiClaim.NONE},
    Rule.REMOVE: {"verdict": Verdict.REMOVE, "reason": "You said few would notice if this changed or stopped. Check that, then test stopping it before spending anything on it.", "solution": "Stop this work or cut it back, after checking with the people who receive it. If few would notice it stopping, automating it may not be worth it.", "first_step": "Check whether anything requires {task}. If nothing does, skip one cycle, tell the recipients, and record who asks for it.", "check": "Keep anything required by regulation, your LPA, or a side letter.", "claim": KpiClaim.NONE},
    Rule.LEGACY_CHECK: {"verdict": Verdict.OPTIMIZE, "reason": "You said few would notice if this changed, yet this work area matters to {kpi} or to your thesis. Check which is true before cutting it.", "solution": "Check who uses {task} before changing it, then simplify or stop what nobody needs.", "first_step": "Ask who uses the output of {task}, and who would notice if it were cut back.", "check": "Keep anything required by regulation, your LPA, or a side letter.", "claim": KpiClaim.PREPARES},
    Rule.KEEP_MINIMAL: {"verdict": Verdict.OPTIMIZE, "reason": "You said few would notice if this changed, but it may be required, or a mistake here could be costly. Simplify it to the minimum instead of stopping it.", "solution": "Check what is actually required, and cut the process back to that minimum before spending anything on it.", "first_step": "Ask who uses the output of {task}, and who would notice if it were cut back.", "check": "Keep anything required by regulation, your LPA, or a side letter.", "claim": KpiClaim.NONE},
    Rule.KEEP_CONTROL: {"verdict": Verdict.OPTIMIZE, "reason": "You said few would notice if this changed, but this work is a control, so keep it and make it simpler.", "solution": "Keep the control, and remove a step only where whoever leads compliance agrees it adds no protection.", "claim": KpiClaim.NONE},
    Rule.PAUSE_USE: {"verdict": Verdict.OPTIMIZE, "reason": "You said AI is used here, and also that your policy restricts it. Settle that before anything else.", "solution": "Bring any AI use here under your policy, or pause it, before doing anything more with AI.", "first_step": "Ask whoever leads compliance to review how AI is used on {task} today.", "check": "The current owner reviews any change to this process.", "claim": KpiClaim.NONE},
    Rule.BUILD_ON: {"verdict": Verdict.BUILD_ON, "claim": KpiClaim.FULL},
    Rule.ONE_PERSON: {"verdict": Verdict.OPTIMIZE, "reason": "You said this depends on one or two people, so it needs writing down before automation or AI can help.", "solution": "Write down the steps for {task}, who holds what, and what they check, so someone else could run one cycle, before adding technology.", "check": "The current owner reviews any change to this process.", "claim": KpiClaim.PREPARES},
    Rule.OUTSIDE: {"verdict": Verdict.OPTIMIZE, "reason": "You said an outside provider does this, so check what they can deliver under your agreement before buying or building anything.", "solution": "Agree with your provider what they deliver for {task}, in what format, and by when. Whoever owns this work decides what is re-checked.", "check": "The current owner reviews any change to this process.", "claim": KpiClaim.SOME},
    Rule.QUICK_REVIEW: {"verdict": Verdict.OPTIMIZE, "reason": "We did not examine this in detail, so review it before choosing a tool.", "solution": "Review how {task} runs today, and come back to this plan with what you find.", "claim": KpiClaim.PREPARES},
    Rule.NOT_SAME_WAY: {"verdict": Verdict.OPTIMIZE, "reason": "You said each team runs this its own way, so automating it now would mean automating several versions.", "solution": "Agree one standard across teams for {task}, then automate what repeats.", "check": "The current owner reviews any change to this process.", "claim": KpiClaim.SOME},
    Rule.REDO: {"verdict": Verdict.OPTIMIZE, "reason": "You said time goes on fixing errors and mismatches here, so fix the cause before automating it.", "solution": "For {task}, agree the definitions and the source for the figures that disagree, and check them at the point of entry. Keep every existing review and approval.", "check": "The current owner reviews any change to this process.", "claim": KpiClaim.SOME},
    Rule.SIGNOFFS: {"verdict": Verdict.OPTIMIZE, "reason": "You said this waits on internal sign-off, and software will not shorten that.", "solution": "Agree a clear turnaround for each sign-off on {task}, and cut only those nothing requires.", "check": "Whoever leads compliance confirms that required controls stay.", "claim": KpiClaim.SOME},
    Rule.TEMPLATE_ENOUGH: {"verdict": Verdict.OPTIMIZE, "reason": "You said this runs a few times a year with few hours, so a good template may be all it needs.", "solution": "Build one reusable template and checklist for {task}, and revisit automation only if volumes grow.", "check": "The current owner reviews the template.", "claim": KpiClaim.SOME},
    Rule.AGREE_FIRST: {"verdict": Verdict.OPTIMIZE, "reason": "You said this runs on {sources}, with no system behind it. Agree one template and one set of definitions first, if you have not already, then automate what repeats.", "reason_unknown": "You did not say where this information lives. If it has no system behind it, agree one template and one set of definitions first, then automate what repeats.", "solution": "Agree one template and one set of definitions for {task}, so that what repeats can be automated next.", "claim": KpiClaim.SOME},
    Rule.CUSTOM_RULES: {"verdict": Verdict.AUTOMATE, "reason": "You said it follows fixed rules, so ordinary automation may be enough.", "claim": KpiClaim.FULL},
    Rule.SERIOUS_PROCESS_FIRST: {"verdict": Verdict.OPTIMIZE, "reason": "You said a mistake here could cause serious harm. Standardize it first, then consider AI.", "reason_unknown": "This work may be required, or costly if wrong. Standardize it first, then consider AI.", "claim": KpiClaim.SOME},
    Rule.CUSTOM_WRITE_RULES: {"verdict": Verdict.OPTIMIZE, "reason": "You said it follows fixed rules. No AI is needed to start, so this can begin before any decision on AI.", "solution": "Write the rules down for {task}, keep one live version, then automate what repeats.", "first_step": "Write down what goes into {task}, where each field comes from, and who reads it.", "claim": KpiClaim.PREPARES},
    Rule.DOCS_PLAIN: {"verdict": Verdict.ADD_AI, "reason": "The rules are clear, but the information arrives in {doc_sources}, so AI extracts it, fixed checks verify it, and a person handles exceptions.", "claim": KpiClaim.FULL},
    Rule.DOCS_REVIEW: {"verdict": Verdict.ADD_AI, "reason": "The rules are clear, but the information arrives in {doc_sources}, and this work may be required, or costly if wrong. AI extracts the information, and a person checks it.", "claim": KpiClaim.FULL},
    Rule.AUTOMATE: {"verdict": Verdict.AUTOMATE, "reason": "It follows fixed rules, so ordinary automation can do it without AI.", "claim": KpiClaim.FULL},
    Rule.RESTRICTED: {"verdict": Verdict.OPTIMIZE, "reason": "Your policy restricts AI today, so the best available gain is a simpler process.", "solution": "Simplify how {task} runs now, then revisit AI once policy allows it.", "check": "The current owner reviews any change to this process.", "claim": KpiClaim.SOME},
    Rule.REKEY_AUTOMATE: {"verdict": Verdict.AUTOMATE, "reason": "You said people retype what already sits in your tools, so connect the tools. This needs no AI.", "solution": "Connect the tools behind {task}, so this information moves once, with no retyping.", "claim": KpiClaim.FULL},
    Rule.DRAFT: {"verdict": Verdict.ADD_AI, "reason": "It needs reading and drafting that rules cannot handle, so AI prepares the work and a person reviews it.", "claim": KpiClaim.FULL},
    Rule.ONE_PLACE: {"verdict": Verdict.OPTIMIZE, "reason": "You said this sits in {sources}, with no system holding it. Put it in one shared place first, then consider AI.", "reason_unknown": "You did not say where this information lives. If no system holds it, put it in one shared place first, then consider AI.", "solution": "Put {task} in one shared tracker with an owner and a date for each item, before adding any AI.", "claim": KpiClaim.SOME},
    Rule.NO_AGENT: {"verdict": Verdict.ADD_AI, "reason": "A person should decide at each step here, so AI prepares the work and a person carries it out.", "claim": KpiClaim.FULL},
    Rule.SEVERE_MULTI: {"verdict": Verdict.ADD_AI, "reason": "It runs across several tools, and mistakes could be costly or their cost is unclear, so AI should prepare the work and a person should carry it out.", "claim": KpiClaim.FULL},
    Rule.AGENT_BLOCKED: {"verdict": Verdict.ADD_AI, "reason": "{blocker} So AI prepares the work for now, and a person carries it out. An agent becomes an option once {unlock}.", "claim": KpiClaim.FULL},
    Rule.AGENT: {"verdict": Verdict.AGENTIC, "reason": "You said this work sits in a system, and nothing in your answers blocks it, so an agent can carry the steps while a person approves anything that leaves the firm.", "claim": KpiClaim.FULL},
}
# First hit wins. Each entry: what the person said, and what would change it.
AGENT_BLOCKERS = {
    "trust": ("You said some people at the firm are skeptical of or against relying on AI's work.", "people have seen it work under review"),
    "policy_none": ("You said the firm has no AI policy.", "a policy is in place"),
    "policy_unknown": ("You did not say whether the firm has an AI policy.", "you have a policy"),
    "stage_none": ("You said the firm does not use AI yet.", "the firm has run a trial"),
    "stage_unknown": ("You did not say how far along AI is at the firm.", "the firm has run a trial"),
    "stage_individuals": ("You said individuals use AI on their own, with no firm-wide approach.", "the firm has run a shared trial"),
    "results": ("You described AI results so far as disappointing.", "you know why earlier work fell short"),
    "capacity": ("You said nobody is set to carry out this work yet.", "someone is responsible for it"),
    "systems_manual": ("You said most work runs on Excel and email.", "the work sits in a system"),
    "systems_disconnected": ("You said your software tools do not share data.", "the tools it needs can share data"),
    "sources": ("You said this work has no system behind it.", "it sits in a system"),
    "sources_unknown": ("You did not say whether this work has a system behind it.", "you know it sits in a system"),
    "email": ("You said this work runs partly through email, and your AI policy covers trials only.", "your policy covers email data"),
    "rekey": ("You said people retype information between tools here.", "that retyping is gone"),
}
REASON_ASSUMED = "You said AI is used somewhere in this work area, but not on which tasks. Check whether this is one of them."
REASON_ASSUMED_RESTRICTED = "You said AI is used somewhere in this work area, and that your policy restricts it. Settle that first."
ASSUMED_SOLUTION_LEAD = "Find out whether AI is used here. If it is: "
AI_UNKNOWN_CARD = "AI use here not confirmed"
AI_UNKNOWN_TABLE = " (check current AI use)"
CREDIT_NOTE = "This task list was written mainly for equity investing, so some credit work may be missing."

DOCS_REVIEW_SUFFIX = " A person reviews every item AI extracts."
AI_UNKNOWN_NOTE = "You did not say whether AI is already used here"
AI_UNKNOWN_ACTION = "Ask the people doing {area} whether they already use AI there."
AI_ASSUMED_NOTE = "AI is used somewhere in this work area, but you did not say on which tasks"
ASSUMED_FIRST_STEP = "Find out whether AI is used on {task}, and how."
INFORMAL_STAGE = "adhoc"
DEPLOYED_IMPACT_CAP = 3.6
RELEVANCE_PREPARES = "Prepares the ground for later work on {kpi}"
RELEVANCE_NONE = "Frees time for other work"
RELEVANCE_PAUSE = "Settles a policy question first. This does not itself move {kpi}"
RELEVANCE_ONCE_FIXED = "{link} to {kpi}, once this process is fixed"

BUILD_ON_TEXT = {
    ("task", "any"): ("You said AI is already used on this task.", "Review how it is used, and agree one approved approach with clear review.", "Ask who uses AI on {task}, and how."),
    ("adhoc", "any"): ("You said some people already use AI here informally, with no shared approach.", "Turn personal use into one approved way of working, with shared templates and clear review.", "Ask each person how they use AI on {task} today."),
    ("pilot", "measured"): ("You have a trial here, and you said AI has shown measured gains at the firm. The decision is whether this one goes to the whole team.", "Decide whether to take this trial into daily use, with an owner and a monthly results check.", "For {task}, agree the results that would justify using it across the team."),
    ("pilot", "any"): ("You have a trial here, and you did not report measured gains from AI at the firm. Find out whether this one works before expanding it.", "Compare the trial with the old process, then decide whether to expand, fix, or stop it.", "For {task}, choose five cases to time with the current process and with the trial."),
    ("deployed", "measured"): ("This is standard for the team here, and you said AI has shown measured gains at the firm. Look next at the steps around it.", "Look for gains in the steps before and after this task, and keep measuring.", "Map the steps before and after {task}, and find where people still rework the output."),
    ("deployed", "disappointing"): ("This is standard for the team here, and you described AI results at the firm as disappointing. Check whether that applies here before extending it.", "Review it against what users actually need, then fix, replace, or stop it.", "For {task}, ask three regular users what works and what does not, and review a sample of recent outputs."),
    ("deployed", "any"): ("This is standard for the team here, and you did not report measured gains from AI at the firm. Without a starting measure, you cannot tell whether to invest further.", "Measure time saved and error rates before spending more here.", "For {task}, pick two measures and start collecting them."),
}
DEFAULT_IN_USE_STAGE = "task"
GOAL_PREFIX = "The goal: "
DEPLOYED_GOAL_PREFIX = "Check your setup against this standard: "

ROUTE_LABEL = "How to get there"
ROUTES = {
    (Verdict.AUTOMATE, "low"): "Check first whether software you already have can do this. If not, price a small workflow tool",
    (Verdict.AUTOMATE, "mid"): "Automation in your existing software, or a workflow tool if that falls short",
    (Verdict.AUTOMATE, "high"): "Software that moves work between your tools by set rules, or a custom link between your systems",
    (Verdict.ADD_AI, "low"): "An approved AI chat tool, with shared templates",
    (Verdict.ADD_AI, "mid"): "A specialist tool, if one fits, before building anything",
    (Verdict.ADD_AI, "high"): "A specialist tool, or one set up to read your own documents",
    (Verdict.AGENTIC, "low"): "A small trial on one workflow before committing budget",
    (Verdict.AGENTIC, "mid"): "A trial on one workflow, with outside help if needed",
    (Verdict.AGENTIC, "high"): "Built in-house or with a partner, connected to your software",
    (Verdict.BUILD_ON, "any"): "Keep your current tools for now, and decide on any change after measuring them",
    (Verdict.BUILD_ON, "informal"): "Move this work onto an approved tool first",
    (Verdict.ADD_AI, "careful"): "A specialist tool, if one fits, or an add-on to your current software, with a person checking the output",
    (Verdict.ADD_AI, "careful_own"): "{tool}, with a person checking the output",
    (Verdict.ADD_AI, "no_policy"): "A shortlisted AI tool, once it is approved",
    (Verdict.AGENTIC, "trial"): "A trial on one workflow, under your current AI policy",
    (Verdict.AGENTIC, "own_team"): "A trial on one workflow, run by your own tech team",
    (Verdict.OPTIMIZE, "any"): "No new technology needed yet",
    (Verdict.REMOVE, "any"): "No technology needed",
}
BUDGET_TIER = {"unset": "low", "under_100k": "low", "100k_500k": "mid", "over_500k": "high"}
# Money levels are planning estimates set by the type of move and the firm's tools. They are not quotes.
SPEND_LABELS = {Spend.NONE: "No new money expected", Spend.SMALL: "Small spend", Spend.DECISION: "Needs a budget decision"}
ALL_SPEND = (Spend.NONE, Spend.SMALL, Spend.DECISION)
BUDGET_COVERS = {"": ALL_SPEND, "unset": (Spend.NONE,), "under_100k": (Spend.NONE, Spend.SMALL), "100k_500k": ALL_SPEND, "over_500k": ALL_SPEND}
# A skipped answer means no limit: normal order, all circles, one view.
BUDGET_REORDERS = ("unset", "under_100k")
SPEND_ENDINGS = {"": ("", ""), "unset": ("", ", and nothing is set aside yet"), "under_100k": (", which should fit what you set aside", ", which may be more than you set aside"), "100k_500k": (", which should fit what you set aside", ""), "over_500k": (", which should fit what you set aside", "")}
SHAPE_KEY_FITS = {"unset": "No new money expected", "under_100k": "Should fit what you set aside", "100k_500k": "Should fit what you set aside", "over_500k": "Should fit what you set aside"}
SHAPE_KEY_NOT = {"unset": "Needs money you have not set aside", "under_100k": "May need more than you set aside"}
FIT_NOTES = {"unset": "Needs money", "under_100k": "May need more"}
BUDGET_READING = {"unset": "You have no money set aside yet, so moves that need none come first.", "under_100k": "With under $100K set aside, moves that may need more come after the rest."}
BUDGET_READING_COVERED = "Taken one at a time, the moves that need money should fit what you set aside, so your budget did not change the order. Doing them all at once may not fit."
BUDGET_READING_NONE_FIT = "Every move in this plan needs money you have not set aside, so a budget decision comes first."
BUDGET_WORTH_FUNDING = "The move most worth finding money for is {label}, rated {level} compared with your other moves."
LEADS_BUDGET = "It comes ahead of {next_task}, which may need money you have not set aside."
NAMED_REASON_BUDGET = "It may need money you have not set aside, so it comes after moves that do not."
NAMED_REASON_BUDGET_LIFTED = "It may need money you have not set aside, but you named it, so it stays in the top three."
BUDGET_READING_EXCEPTION = " The task you named is the one exception."
START_NONE_FIT = "Decide the budget for move 1 before you start it."
START_BUDGET = "Start with move 1. The next moves may need money you have not set aside."
MONEY_LABEL = "Money, estimated"
CONNECT_DATA_TITLE = "Connect your core data"
SCOPE_TITLE = "After this blueprint: what to scope"
SCOPE_LEDE = "This blueprint decides which activities to take forward. Scoping each one comes next, and covers these."
SCOPE_ITEMS = (
    ("Data", "What data the move touches, how good it is, and who may see it. This includes LP data, inside information, and personal data."),
    ("Systems", "Where that data lives, and whether it can be exported or connected."),
    ("Vendor and cost", "Which tools fit, what they cost, and how they handle your data."),
    ("Compliance", "Whether compliance has cleared the tool, how outputs are kept, and whether any LP or regulatory statement is affected."),
    ("People", "Who owns the move, and how many hours they really have."),
)
KEY_KPI_VALUE = "kpi_value"
KPI_VALUE_MAX = 60
ROADMAP_WAVES = (("Start now", 3), ("Then", 4), ("After that", None))
ROADMAP_WAVE_SPAN = "Moves {first} to {last}"
ROADMAP_WAVE_ONE = "Move {first}"
COVERAGE_LINE = "Your number depends most on {areas}, which you did not assess. Add it for a fuller plan."
COVERAGE_MAX = 2
PEOPLE_ELSEWHERE = "Across the firm, these also stay with your people: {items}."
STRATEGY_LINE = "This is your AI strategy and blueprint, built from one person's answers. It sets which activities to take forward, and in what order."
REPORT_NAME = "AI Strategy and Blueprint"
KPI_STATUS_ROW = {"on_target": "On target, you said", "off_target": "Off target, you said", "no_target": "Tracked, no target set"}
STUCK_TITLE = "Where the work gets stuck"
STUCK_TIME = "{task}: time goes on {what}."
STUCK_TIME_AREA = "Time goes on {what}."
STUCK_SLOW_AREA = "The slowest step is {step}."
STUCK_ONE_PERSON_AREA = "Know-how is held by one or two people."
STUCK_VARIES_AREA = "It runs differently by team."
STUCK_SLOW = "{task}: the slowest step is {step}."
STUCK_ONE_PERSON = "{task}: know-how is held by one or two people."
STUCK_VARIES = "{task}: it runs differently by team."
STUCK_HABIT = "{task}: done mainly out of habit."
STUCK_SOURCES = "Information is split across {sources}, with no system holding it."
STUCK_SOURCES_SYSTEM = "Information is split across {sources}."
CAPACITY_TECH_OWNER = {"in_house": "Your tech team, with {owner}", "partner": "{owner}, with your outside firm"}
Y_AXIS_TITLE = "Relative effect on {kpi}"
KPI_TYPED_EFFECT = "change {kpi}"
KPI_TYPED_HEADING = "How your moves compare on {kpi}"
PLOT_HEADING = "How much each move could {effect}"
KPI_OWN_NO_FORECAST = "The ratings rank your moves against each other. They do not predict any change in {kpi}."
KPI_TYPED_BASELINE = "Record where {kpi} stands today, and how you measure it."
FEEDS_LINE = "This number feeds {feeds}."
FEEDS_LINKS = {"direct": "The link is direct.", "partial": "The link is partial, because other factors also matter.", "indirect": "The link is indirect, because other factors also matter."}
NO_RETURNS_CLAIM = "This plan makes no claim about IRR, MOIC, or DPI."
KPI_MATCHED_NOTE = "You chose your own number. Effect is estimated with the rules for {matched}, the closest on our list."
KPI_OWN_NOTE = "You chose your own number. Each move shows its link to it."
RELATIVE_NOTE = "Effect compares your moves with each other, using each task's link and the hours behind it. It is not a forecast."
VIEW_GROUP_LABEL = "Report view"
VIEW_TAB_BUDGET = "With your budget"
VIEW_TAB_OPEN = "No budget limit"
VIEW_NOTE_OPEN = "This view ignores your budget. The moves are the same, in the order they would take with no limit. Tool suggestions and money levels can differ."
VIEW_PRINT_BUDGET = "This printout shows the plan with your budget. The report file also has a view with no budget limit."
VIEW_PRINT_OPEN = "This printout shows the view with no budget limit. The report file also has the plan with your budget."
# What they already run comes first, so nobody is told to buy what they own. First hit wins.
TOOL_ROUTES = (
    ("custom", "Your own team, on the custom AI you already run, and a specialist tool only if that falls short"),
    ("specialist", "Check first whether the specialist tool you already have can do this"),
    ("embedded", "Check first whether AI features in your current software can do this"),
    ("assistants", "Start in the AI chat tools you already use, with shared templates"),
)
OUTSIDE_ROUTE = "No new technology until you have asked the provider"

SYSTEMS_LABEL = "Your tools"
TRUST_LABEL = "Team on AI"
CAPACITY_LABEL = "Who sets it up"
STAGE_PHRASES = {"none": "Not used yet", "individuals": "Individuals use AI on their own", "pilots": "Trials in some teams", "deployed": "Standard across teams"}
ADOPTION_PHRASES = {"under_10": "A few people", "10_30": "Some people", "30_60": "Many people", "over_60": "Most people"}
RESULTS_PHRASES = {"measured": "Measured gains", "unmeasured": "Useful, but not measured", "mixed": "Mixed, or too early to say", "disappointing": "Disappointing"}
HERE_PHRASES = {"task": "In use on this task", "adhoc": "Some people, informally", "pilot": "A small trial", "deployed": "Standard for the team"}
REGION_NOTES = {
    "us": "Have counsel check how SEC recordkeeping and marketing rules apply to AI-assisted work.",
    "eu": "Have counsel check how GDPR, AIFMD, and the EU AI Act apply to these uses.",
    "uk": "Have counsel check how UK GDPR and FCA rules apply to these uses.",
    "other": "Have counsel check data protection and AI rules in each jurisdiction where you operate.",
}

CUSTOM_SOLUTIONS = {
    Nature.RULES: "Write the rules down and automate the routine path, sending exceptions to the owner.",
    Nature.DRAFTING: "Have AI prepare a first draft from your source material, with citations, for the owner to review.",
    Nature.MULTI_SYSTEM: "Connect the tools involved, and let an agent carry the steps, with the owner approving the result.",
    Nature.JUDGMENT: "Keep the decision with your people. AI can prepare background and past examples.",
}
CUSTOM_FIRST_STEP = "Write down the inputs, decisions, and who receives the result for {task}."
CUSTOM_SERIOUS_CHECK = "Have a second person check the results while this is new."
CUSTOM_PREPARE_SOLUTION = "Have AI gather the information and prepare the work, and have the owner carry out each step."
CUSTOM_CHECK = "The current owner reviews the results."
CUSTOM_TAG = "Added by you"

SOURCE_PHRASES = {"system": "a proper system", "spreadsheets": "spreadsheets", "email": "email", "documents": "documents"}
WHO_PHRASES = {"partners": "partners or principals", "investment": "VPs, associates, or analysts", "operations": "finance, IR, compliance, or ops staff", "outside": "an outside provider"}
TIME_PHRASES = {"wait_outside": "waiting on outside parties", "wait_signoff": "waiting on internal sign-off", "rekey": "retyping or rebuilding", "fixing": "fixing errors and mismatches"}
LINK_WORDS = {3: "has a direct link to", 2: "has a strong link to", 1: "has some link to", 0: "has an indirect link to"}
# Fixes the first step on the hardest task in a work area, from where they said the time goes. First hit wins.
TIME_STEP_ENDINGS = (
    ("wait_signoff", " Also list who signs, and what each changed last cycle."),
    ("rekey", " Also count how often the same figure is typed."),
    ("fixing", " Also collect the reasons for the last ten corrections."),
)
TRACKED_MEASURE_ENDING = " Watch {measure}, which you already track."
SIGNOFF_SUFFIX = " Agree which items need sign-off, with a turnaround for each, because you said time goes there."
RHYTHM_STEP_ENDINGS = {"periodic": " Test on last period's files, because the next live run is at the next period end.", "bursts": " Test on a past burst, using files from the last deal or request."}
SLOW_STEP_TEXT = "You said the slowest step is: {slow_step}. Write down how it runs and what it checks, and keep any check that protects the numbers."
SLOW_STEP_ENDING = " You said the slowest step is: {slow_step}."
NOT_EXAMINED = "Not examined in detail, because you chose a quick check of this work area."
WALKTHROUGH_TITLE = "How it runs today, as you described it"
HOURS_PHRASES = {"under_20": "under 20 hours", "20_60": "20 to 60 hours", "60_200": "60 to 200 hours", "over_200": "over 200 hours"}
LINK_LADDER = {3: "Direct link", 2: "Strong link", 1: "Some link", 0: "Indirect link"}

FIRM_WIDE_LABEL = "Firm-wide"
FIRM_WIDE_OWNER = "COO or managing partner"
FIRM_WIDE_SPEED = "Start within 30 days"
NEXT_30_MAX_FOUNDATIONS = 3
PLAIN_TERMS = (
    ("Automation", "Software that follows fixed rules, the same way every time. Where rules are enough, you may not need AI at all."),
    ("AI that drafts", "Software that can read documents and write a first version. A person reviews the result before it is used."),
    ("Agentic AI", "AI that carries out several steps in a row across your tools, such as requesting a file, checking it, and loading it. In this plan, a person approves anything that leaves the firm."),
    ("Trial", "A small, time-limited test with a few people, to learn whether something works before the whole team uses it."),
    ("First working version", "The point when a real team can use it on real work. Refinement continues after that."),
    ("Human check", "The step where a named person reviews the output. That person remains responsible."),
)
TIMELINE_MARKS = ("Today", "30 days", "60 days", "90 days", "Later")

METHOD_NOTE = "How the estimates work: speed and effect come from fixed planning rules applied to your answers, such as the hours you reported, who does the work, where the information lives, where the time goes, your constraints, and how directly each task relates to the number you chose, including through each team's own measures. They are planning assumptions, not benchmarks, and they use no benchmark data from any firm. Test them with your team before relying on them."
HORIZON_LABELS = {Horizon.NOW: "Now", Horizon.NEXT: "Next", Horizon.LATER: "Later"}
HORIZON_SPANS = {Horizon.NOW: "Under 30 days, estimated", Horizon.NEXT: "30 to 90 days, estimated", Horizon.LATER: "Over 90 days, estimated"}
QUADRANT_LABELS = {Quadrant.QUICK_WINS: "Fast, higher effect", Quadrant.STRATEGIC_BETS: "Slower, higher effect", Quadrant.FILL_INS: "Fast, lower effect", Quadrant.DEPRIORITIZE: "Slower, lower effect"}

SHADOW_FOUNDATION = ("Bring existing AI use under a policy", "You said people use AI, and that the firm has no AI policy. Confidential data may be reaching tools you have not approved. Set rules before adding anything new.", "Agree which AI tools are approved, and what data may go into them.")
SHADOW_RESTRICTED_FOUNDATION = ("Settle how existing AI use fits your policy", "You said people use AI, and also that your policy restricts it. Find out what is happening in practice, and decide what is allowed.", "Ask whoever leads compliance to review how AI is used today, against your policy.")
ONE_PERSON_FOUNDATION = ("Write down what only one or two people know", "You said {subject} depends on one or two people{harm}.", "Have the person who knows {subject} write down how it runs.")
ONE_PERSON_HARM = ", and a mistake there could cause serious harm"
OWNER_FOUNDATION = ("Name an owner", "Nobody is set to carry out this work yet, so the plan has no one to run it. Name one accountable person first.", "Name one accountable person, and protect time for them.")
DATA_ACTION = "List the data that {task} relies on, and pick one source to clean up."
FOUNDATIONS = {
    ("ai_results", "unmeasured"): ("Measure what you already have", "You said AI is useful, but not measured. Without a starting measure, you cannot tell which work to expand.", "Pick two measures and start recording them for your current AI work."),
    ("ai_results", "mixed"): ("Find out where AI works and where it does not", "You said results are mixed, or that it is too early to say. Compare what has worked with what has not before extending it.", "List where AI has worked and where it has not, and what differs."),
    ("ai_results", "disappointing"): ("Find out why earlier AI work fell short", "You described results so far as disappointing. Review what fell short before starting something new: the use case, the data, or the adoption.", "List what was tried, and the reason each effort fell short."),
    ("ai_adoption", "under_10"): ("Get more use out of what you have", "You said only a few people use AI each week, so tools may be sitting unused. Find out why before adding new ones.", "Ask five people who do not use AI what stops them."),
    ("policy", "none"): ("Agree an AI policy", "Any AI work is held back without one. A short list of approved tools and data rules is enough to start.", "Write a one-page list of approved tools and data rules."),
    ("policy", "restricted"): ("Keep AI on hold for now", "Nothing in this plan needs AI, so your policy can stay as it is. If the team later wants AI, ask whoever leads compliance which low-risk uses could be approved.", "Confirm with whoever leads compliance that the moves below fit your policy."),
    ("systems", "disconnected"): ("Connect your core data", "You said your software tools do not share data, so the same figures may end up in more than one place.", DATA_ACTION),
    ("systems", "manual"): ("Keep one master copy of your most-used data", "You said most work runs on Excel and email. Pick one dataset to centralize first, and let your first move decide which.", DATA_ACTION),
    ("trust", "skeptical"): ("Win over the skeptics", "You said some people are skeptical of relying on AI's work. Pick one item that a skeptical senior person cares about, and measure it next to the current process.", "Pick one item that a skeptical senior person cares about."),
    ("trust", "resistant"): ("Start with work people dislike", "You said some people are against relying on AI's work. Begin with tasks nobody wants to keep, and leave review power with them.", "Ask the team which routine tasks they would most like to lose."),
    ("kpi_status", "untracked"): ("Start measuring {kpi}", "You chose this number, and you do not track it today, so you cannot yet tell whether any move helps.", "{baseline}"),
    ("kpi_status", "no_target"): ("Set a target for {kpi}", "You track this number, with no target set, so there is nothing to judge progress against.", "Agree a target for {kpi}."),
}
SHARED_DATA_FOUNDATION = ("Build this data once", "You selected {count} tasks that draw on the same portfolio data: {tasks}. Agree one owner and one copy, and let each task draw from it.", "Name one owner for the portfolio data that these tasks share.")

# Reading the answers together, on the first page.
READING_MAX = 4
COUNT_WORDS = {Verdict.AUTOMATE: ("automates with fixed rules", "automate with fixed rules"), Verdict.OPTIMIZE: ("fixes the process", "fix the process"), Verdict.REMOVE: ("tests stopping", "test stopping"), Verdict.ADD_AI: ("uses AI to prepare work", "use AI to prepare work"), Verdict.AGENTIC: ("lets AI run the steps", "let AI run the steps"), Verdict.BUILD_ON: ("builds on AI already here", "build on AI already here")}
NAMED_FIRST = "You named {task} as the task to take off your team, and it comes first."
NAMED_LATER = "You named {task} as the task to take off your team. It is move {position}. {reason} If freeing that time matters more than this number, start there instead."
NAMED_REASON_CLOSER = "{above} a closer link to {kpi}."
NAMED_REASON_TIME = "More senior time or hours sit with {above_lower}, on your answers."
NAMED_REASON_SCORE = "{above} a higher score under our planning rules."
NAMED_REASON_LIFTED = "It is placed here because you named it."
KPI_STATUS_READING = {
    "untracked": "You chose {kpi}, and you do not track it today, so measuring it comes before judging any move.",
    "off_target": "You said {kpi} is off target, so the plan weighs effect on it more heavily.",
    "on_target": "You said {kpi} is on target, so hours count for more in this ranking. Check that it is the right number to move.",
}
CHANGE_NAMES_MAX = 3
MEASURE_ACTION = "Record {measure} for one cycle, by hand if needed."
CHAIN_LINE = "Through {measure}, a measure that feeds {kpi}. This link is a planning assumption."
SENIOR_KPI = "senior_hours"
MULTI_STRATEGY = "multi"
LEVER_POLICY = "whoever leads compliance approved AI tools"
LEVER_SYSTEMS = "your tools shared data"
LEVER_CAPACITY = "someone were responsible for this work"
HUMAN_NATURE_VALUES = ("judgment", "relationship")
QUADRANT_NOTE_TOP = "Ringed: the moves recommended above."
QUADRANT_LABELS_SHORT = {Quadrant.QUICK_WINS: "Fast, high", Quadrant.STRATEGIC_BETS: "Slow, high", Quadrant.FILL_INS: "Fast, low", Quadrant.DEPRIORITIZE: "Slow, low"}

STAYS_WITH_PEOPLE_LEDE = "These stay with your people, because they rest on judgment or relationships."
NAMED_TAG = "You named this as the task to take off your team"
MEASURE_ACTIONS_MAX = 1

RULE_ANCHOR_STEPS = {
    Rule.ONE_PERSON: "Have the person who knows {task} walk a colleague through one full cycle, and record it.",
    Rule.NOT_SAME_WAY: "For {task}, pick one team's way as the starting standard, and list where the others differ.",
    Rule.REDO: "For {task}, collect the reasons for the last ten corrections.",
    Rule.SIGNOFFS: "For {task}, list who signs, and what each changed last cycle. Keep every required control.",
    Rule.OUTSIDE: "For {task}, list what you send the provider, and what you re-check afterwards.",
    Rule.TEMPLATE_ENOUGH: "Build the template for {task} from last period's work.",
    Rule.REKEY_AUTOMATE: "For {task}, count how often the same figure is typed, and which source wins.",
}
DEPENDS_PHRASES = {"yes": "the know-how written down", "effort": "know-how someone else could pick up with some effort", "no": "know-how held by one or two people"}
RHYTHM_PHRASES = {"steady": "running daily or weekly", "monthly": "running every month", "periodic": "running quarterly or yearly", "bursts": "running in bursts"}
SAME_WAY_PHRASES = {"same": "run one way across teams", "mostly": "run mostly one way, with local differences", "different": "run differently by team"}
ERROR_PHRASES = {"minor": "mistakes noticed and fixed internally", "awkward": "mistakes visible to LPs or boards", "severe": "mistakes that could cause financial, legal, or regulatory harm", "unsure": "the cost of mistakes unclear"}
ROUTE_INTEGRATED = "Automation inside your main platform, which should need the least new software"
INTEGRATED_SYSTEMS = "integrated"
NO_LINK_PRIORITY_FACTOR = 0.7
PRIORITY_WEIGHTS_BY_STATUS = {"off_target": (0.75, 0.25), "on_target": (0.4, 0.6)}
HEADLINE_RULES = {
    Rule.AGREE_FIRST: "Your first move is to agree the rules for {label}",
    Rule.ONE_PLACE: "Your first move is to set up one shared place for {label}",
    Rule.ONE_PERSON: "Your first move is to write down the steps for {label}",
    Rule.OUTSIDE: "Your first move is to agree what your provider delivers for {label}",
    Rule.NOT_SAME_WAY: "Your first move is to agree one standard across teams for {label}",
    Rule.REDO: "Your first move is to fix the cause of errors in {label}",
    Rule.SIGNOFFS: "Your first move is to shorten sign-offs on {label}",
    Rule.RESTRICTED: "Your AI policy rules out AI for now, so start with the process for {label}",
    Rule.TEMPLATE_ENOUGH: "Your first move is to build one template for {label}",
    Rule.KEEP_MINIMAL: "Your first move is to agree the minimum for {label}",
    Rule.KEEP_CONTROL: "Your first move is to simplify the process for {label}, and keep the control",
    Rule.LEGACY_CHECK: "Your first move is to check who still needs {label}",
    Rule.QUICK_REVIEW: "Your first move is to review how {label} runs",
    Rule.SERIOUS_PROCESS_FIRST: "Your first move is to settle the process for {label}",
    Rule.CUSTOM_WRITE_RULES: "Your first move is to write down the rules for {label}",
}
CHANGE_WORDS = {Verdict.OPTIMIZE: "a process fix", Verdict.ADD_AI: "AI that prepares the work", Verdict.AUTOMATE: "automation", Verdict.AGENTIC: "AI that runs the steps", Verdict.BUILD_ON: "building on AI already here", Verdict.REMOVE: "testing a stop"}
LEADS_NAMED = "It leads because you named it."
LEADS_MORE_DIRECT = "It leads because it has a closer link to {kpi} than {next_task}."
LEADS_MORE_HOURS = "It leads because more senior time or hours are at stake here than on {next_task}."
LEADS_FASTER = "It leads because it should reach a result sooner than {next_task}."
LEADS_TIE = "It is level with {next_task} under our rules, so start with whichever causes more trouble today."
TIE_START = "Start with moves 1 and 2. The top moves rank level, so choose what suits your team."
READING_TITLE = "What in your answers shaped this plan"
PLANNING_LINE_ONE = "Under our planning rules, the one move that adds software {timing}."
ASKED_LISTS_AT_DEPTH = {"deep": ("legacy_tasks", "harm_tasks", "heavy_task", "measures", "walkthrough"), "second": ("legacy_tasks", "heavy_task", "measures"), "quick": ()}
CHANGE_GROUPS_MAX = 2
COUNTED_AS_UNTOLD = ("ai_adoption", "ai_results", "thesis")
CREDIT_NOTE_STRATEGY = "credit"
NAMED_PRIORITY_FACTOR = 1.35
AI_NOT_ASKED_NOTE = "Not asked in this quick check"
AND_OTHERS = "and others"
START_OFF_TARGET = "Start with moves 1 and 3. Move 3 acts on {measure}, the measure you said is off target."
AI_BEHIND = "You said AI is standard across teams, but in the areas assessed it is less than that. Check whether these areas are behind, or whether the answer needs correcting."
PROCESS_TEXT_RULES = (Rule.KEEP_MINIMAL, Rule.RESTRICTED, Rule.AGREE_FIRST, Rule.REDO, Rule.ONE_PLACE, Rule.SERIOUS_PROCESS_FIRST)
DATA_ACTION_START = "List the data that"
HARDEST_FACTS = "On {task}: {facts}."
SLOW_STEP_WHY = "You said the slowest step is: {slow_step}."
MORE_CHANGES = "Other moves would change too."
