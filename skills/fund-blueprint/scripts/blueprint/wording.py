"""Everything the report says, kept apart from the scoring tables. No em dashes in anything a reader sees."""
from __future__ import annotations

from urllib.parse import quote

from .enums import KpiClaim, Horizon, Nature, Quadrant, Rule, Spend, Verdict

CONTACT_EMAIL = "info@nxtpartners.ai"
CONTACT_SUBJECT_TEXT = "NXT AI Strategy and Blueprint: next steps"
CONTACT_SUBJECT = quote(CONTACT_SUBJECT_TEXT)
DEMO_LABEL = "pe.nxtpartners.ai"
DEMO_URL = f"https://{DEMO_LABEL}"
DEMO_TEXT = "See a demo at "
SITE_NAME = "NXT Partners AI"
CLOSING_TITLE = "Want a second opinion on this plan?"
CLOSING_BODY = "This plan rests on one person's answers and fixed rules. NXT Partners AI can test it with your team, correct what is wrong, and help you carry out the priorities you keep. If that would help, email us this report and tell us which priority you would start with."
SMALL_TEAM_OWNER = "Whoever does this today"
WHO_OWNER = {
    "partners": "The partner who does this today",
    "investment": "The VP, associate, or analyst who does this today",
    "operations": "The finance, IR, compliance, or ops person who does this today",
    "outside": "Whoever manages your provider",
}
STRATEGY_WORDS = {
    "credit": (
        ("portfolio companies", "borrowers"),
        ("portfolio company", "borrower"),
        ("portcos", "borrowers"),
        ("portco", "borrower"),
    ),
    "real_estate": (
        ("portfolio companies", "properties"),
        ("portfolio company", "property"),
        ("portcos", "properties"),
        ("portco", "property"),
        ("inbound teaser or CIM", "inbound offering memorandum"),
        ("teasers and CIMs", "offering memoranda"),
        ("CIMs", "offering memoranda"),
        ("CIM", "offering memorandum"),
        ("PE tools", "real estate tools"),
    ),
}
MULTI_STRATEGY_STEP_LEAD = "Pick one strategy to start in. "
TEAM_REVIEW_ACTION = "Have each department lead correct the answers for their area, because this plan rests on one person's view."

# Shipped copy. No em dashes in anything a reader sees.
VERDICT_LABELS = {
    Verdict.AUTOMATE: "Automate",
    Verdict.ADD_AI: "Add AI",
    Verdict.OPTIMIZE: "Optimize",
    Verdict.AGENTIC: "Let AI run the steps (agentic AI)",
    Verdict.REMOVE: "Remove",
    Verdict.BUILD_ON: "Build on existing AI",
    Verdict.LEAVE: "Keep with team",
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
# Each verdict rule in one place: its verdict, reason, what replaces the catalog text,
# and what it may claim about the KPI.
# None means use the catalog's own text. "{kpi}" and similar placeholders are filled when scoring.
RULES = {
    Rule.LEAVE: {
        "verdict": Verdict.LEAVE,
        "reason": "The value here comes from human judgment or relationships, so this stays with your team.",
        "claim": KpiClaim.NONE,
    },
    Rule.REMOVE: {
        "verdict": Verdict.REMOVE,
        "reason": "You said few would notice if this changed or stopped. Check that, then test stopping it before spending anything on it.",
        "solution": "Stop this work or cut it back, after checking with the people who receive it. If few would notice it stopping, automating it may not be worth it.",
        "first_step": "Check whether anything requires {task}. If nothing does, skip one cycle, tell the recipients, and record who asks for it.",
        "check": "Keep anything required by regulation, your LPA, or a side letter.",
        "claim": KpiClaim.NONE,
    },
    Rule.LEGACY_CHECK: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said few would notice if this changed, yet this work area matters to {kpi} or to your thesis. Check which is true before cutting it.",
        "solution": "Check who uses {task} before changing it, then simplify or stop what nobody needs.",
        "first_step": "Ask who uses the output of {task}, and who would notice if it were cut back.",
        "check": "Keep anything required by regulation, your LPA, or a side letter.",
        "claim": KpiClaim.PREPARES,
    },
    Rule.KEEP_MINIMAL: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said few would notice if this changed, but it may be required, or a mistake here could be costly. Simplify it to the minimum instead of stopping it.",
        "solution": "Check what is actually required, and cut the process back to that minimum before spending anything on it.",
        "first_step": "Ask who uses the output of {task}, and who would notice if it were cut back.",
        "check": "Keep anything required by regulation, your LPA, or a side letter.",
        "claim": KpiClaim.NONE,
    },
    Rule.KEEP_CONTROL: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said few would notice if this changed, but this work is a control, so keep it and make it simpler.",
        "solution": "Keep the control, and remove a step only where whoever leads compliance agrees it adds no protection.",
        "claim": KpiClaim.NONE,
    },
    Rule.PAUSE_USE: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said AI is used here, and also that your policy restricts it. Settle that before anything else.",
        "solution": "Bring any AI use here under your policy, or pause it, before doing anything more with AI.",
        "first_step": "Ask whoever leads compliance to review how AI is used on {task} today.",
        "check": "The current owner reviews any change to this process.",
        "claim": KpiClaim.NONE,
    },
    Rule.BUILD_ON: {"verdict": Verdict.BUILD_ON, "claim": KpiClaim.FULL},
    Rule.ONE_PERSON: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said this depends on one or two people, so it needs writing down before automation or AI can help.",
        "solution": "Write down the steps for {task}, who holds what, and what they check, so someone else could run one cycle, before adding technology.",
        "check": "The current owner reviews any change to this process.",
        "claim": KpiClaim.PREPARES,
    },
    Rule.OUTSIDE: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said an outside provider does this, so check what they can deliver under your agreement before buying or building anything.",
        "solution": "Agree with your provider what they deliver for {task}, in what format, and by when. Whoever owns this work decides what is re-checked.",
        "check": "The current owner reviews any change to this process.",
        "claim": KpiClaim.SOME,
    },
    Rule.QUICK_REVIEW: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "We did not examine this in detail, so review it before choosing a tool.",
        "solution": "Review how {task} runs today, and come back to this plan with what you find.",
        "claim": KpiClaim.PREPARES,
    },
    Rule.NOT_SAME_WAY: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said each team runs this its own way, so automating it now would mean automating several versions.",
        "solution": "Agree one standard across teams for {task}, then automate what repeats.",
        "check": "The current owner reviews any change to this process.",
        "claim": KpiClaim.SOME,
    },
    Rule.REDO: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said time goes on fixing errors and mismatches here, so fix the cause before automating it.",
        "solution": "For {task}, agree the definitions and the source for the figures that disagree, and check them at the point of entry. Keep every existing review and approval.",
        "check": "The current owner reviews any change to this process.",
        "claim": KpiClaim.SOME,
    },
    Rule.SIGNOFFS: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said this waits on internal sign-off, and software will not shorten that.",
        "solution": "Agree a clear turnaround for each sign-off on {task}, and cut only those that whoever leads compliance agrees add no protection.",
        "first_step": "List each sign-off on {task}, who gives it, and how long it takes today.",
        "check": "Whoever leads compliance confirms that required controls stay.",
        "claim": KpiClaim.SOME,
    },
    Rule.TEMPLATE_ENOUGH: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said this runs a few times a year with few hours, so a good template may be all it needs.",
        "solution": "Build one reusable template and checklist for {task}, and revisit automation only if volumes grow.",
        "check": "The current owner reviews the template.",
        "claim": KpiClaim.SOME,
    },
    Rule.AGREE_FIRST: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said this runs on {sources}, with no system behind it. Agree one template and one set of definitions first, if you have not already, then automate what repeats.",
        "reason_unknown": "You did not say where this information lives. If it has no system behind it, agree one template and one set of definitions first, then automate what repeats.",
        "solution": "Agree one template and one set of definitions for {task}, so that what repeats can be automated next.",
        "claim": KpiClaim.SOME,
    },
    Rule.CUSTOM_RULES: {
        "verdict": Verdict.AUTOMATE,
        "reason": "You said it follows fixed rules, so ordinary automation may be enough.",
        "claim": KpiClaim.FULL,
    },
    Rule.SERIOUS_PROCESS_FIRST: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said a mistake here could cause serious harm. Standardize it first, then consider AI.",
        "reason_unknown": "This work may be required, or costly if wrong. Standardize it first, then consider AI.",
        "claim": KpiClaim.SOME,
    },
    Rule.CUSTOM_WRITE_RULES: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said it follows fixed rules. No AI is needed to start, so this can begin before any decision on AI.",
        "solution": "Write the rules down for {task}, keep one live version, then automate what repeats.",
        "first_step": "Write down what goes into {task}, where each field comes from, and who reads it.",
        "claim": KpiClaim.PREPARES,
    },
    Rule.DOCS_PLAIN: {
        "verdict": Verdict.ADD_AI,
        "reason": "The rules are clear, but the information arrives in {doc_sources}, so AI extracts it, fixed checks verify it, and a person handles exceptions.",
        "claim": KpiClaim.FULL,
    },
    Rule.DOCS_REVIEW: {
        "verdict": Verdict.ADD_AI,
        "reason": "The rules are clear, but the information arrives in {doc_sources}, and this work may be required, or costly if wrong. AI extracts the information, and a person checks it.",
        "claim": KpiClaim.FULL,
    },
    Rule.AUTOMATE: {
        "verdict": Verdict.AUTOMATE,
        "reason": "It follows fixed rules, so ordinary automation can do it without AI.",
        "claim": KpiClaim.FULL,
    },
    Rule.RESTRICTED: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "Your policy restricts AI today, so the best available gain is a simpler process.",
        "solution": "Simplify how {task} runs now, then revisit AI once policy allows it.",
        "check": "The current owner reviews any change to this process.",
        "claim": KpiClaim.SOME,
    },
    Rule.REKEY_AUTOMATE: {
        "verdict": Verdict.AUTOMATE,
        "reason": "You said people retype what already sits in your tools, so connect the tools. This needs no AI.",
        "solution": "Connect the tools behind {task}, so this information moves once, with no retyping.",
        "claim": KpiClaim.FULL,
    },
    Rule.DRAFT: {
        "verdict": Verdict.ADD_AI,
        "reason": "It needs reading and drafting that rules cannot handle, so AI prepares the work and a person reviews it.",
        "claim": KpiClaim.FULL,
    },
    Rule.ONE_PLACE: {
        "verdict": Verdict.OPTIMIZE,
        "reason": "You said this sits in {sources}, with no system holding it. Put it in one shared place first, then consider AI.",
        "reason_unknown": "You did not say where this information lives. If no system holds it, put it in one shared place first, then consider AI.",
        "solution": "Put {task} in one shared tracker with an owner and a date for each item, before adding any AI.",
        "claim": KpiClaim.SOME,
    },
    Rule.NO_AGENT: {
        "verdict": Verdict.ADD_AI,
        "reason": "A person should decide at each step here, so AI prepares the work and a person carries it out.",
        "claim": KpiClaim.FULL,
    },
    Rule.SEVERE_MULTI: {
        "verdict": Verdict.ADD_AI,
        "reason": "It runs across several tools, and mistakes could be costly or their cost is unclear, so AI should prepare the work and a person should carry it out.",
        "claim": KpiClaim.FULL,
    },
    Rule.AGENT_BLOCKED: {
        "verdict": Verdict.ADD_AI,
        "reason": "{blocker} So AI prepares the work for now, and a person carries it out. An agent becomes an option once {unlock}.",
        "claim": KpiClaim.FULL,
    },
    Rule.AGENT: {
        "verdict": Verdict.AGENTIC,
        "reason": "You said this work sits in a system, and nothing in your answers blocks it, so an agent can carry the steps while a person approves anything that leaves the firm.",
        "claim": KpiClaim.FULL,
    },
}
# First hit wins. Each entry: what the person said, and what would change it.
AGENT_BLOCKERS = {
    "trust": (
        "You said some people at the firm are skeptical of or against relying on AI's work.",
        "people have seen it work under review",
    ),
    "policy_none": ("You said the firm has no AI policy.", "a policy is in place"),
    "policy_unknown": ("You did not say whether the firm has an AI policy.", "you have a policy"),
    "stage_none": ("You said the firm does not use AI yet.", "the firm has run a trial"),
    "stage_unknown": ("You did not say how far along AI is at the firm.", "the firm has run a trial"),
    "stage_individuals": (
        "You said individuals use AI on their own, with no firm-wide approach.",
        "the firm has run a shared trial",
    ),
    "results": ("You described AI results so far as disappointing.", "you know why earlier work fell short"),
    "capacity": ("You said nobody is set to carry out this work yet.", "someone is responsible for it"),
    "systems_manual": ("You said most work runs on Excel and email.", "the work sits in a system"),
    "systems_disconnected": ("You said your software tools do not share data.", "the tools it needs can share data"),
    "sources": ("You said this work has no system behind it.", "it sits in a system"),
    "sources_unknown": ("You did not say whether this work has a system behind it.", "you know it sits in a system"),
    "email": (
        "You said this work runs partly through email, and your AI policy covers trials only.",
        "your policy covers email data",
    ),
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
RELEVANCE_PREPARES = "Prepares the ground for later work on {kpi}"
RELEVANCE_NONE = "Frees time for other work"
RELEVANCE_PAUSE = "Settles a policy question first. This does not itself move {kpi}"
RELEVANCE_ONCE_FIXED = "{link} to {kpi}, once this process is fixed"

BUILD_ON_TEXT = {
    ("task", "any"): (
        "You said AI is already used on this task.",
        "Review how it is used, and agree one approved approach with clear review.",
        "Ask who uses AI on {task}, and how.",
    ),
    ("adhoc", "any"): (
        "You said some people already use AI here informally, with no shared approach.",
        "Turn personal use into one approved way of working, with shared templates and clear review.",
        "Ask each person how they use AI on {task} today.",
    ),
    ("pilot", "measured"): (
        "You have a trial here, and you said AI has shown measured gains at the firm. The decision is whether this one goes to the whole team.",
        "Decide whether to take this trial into daily use, with an owner and a monthly results check.",
        "For {task}, agree the results that would justify using it across the team.",
    ),
    ("pilot", "any"): (
        "You have a trial here, and you did not report measured gains from AI at the firm. Find out whether this one works before expanding it.",
        "Compare the trial with the old process, then decide whether to expand, fix, or stop it.",
        "For {task}, choose five cases to time with the current process and with the trial.",
    ),
    ("deployed", "measured"): (
        "This is standard for the team here, and you said AI has shown measured gains at the firm. Look next at the steps around it.",
        "Look for gains in the steps before and after this task, and keep measuring.",
        "Map the steps before and after {task}, and find where people still rework the output.",
    ),
    ("deployed", "disappointing"): (
        "This is standard for the team here, and you described AI results at the firm as disappointing. Check whether that applies here before extending it.",
        "Review it against what users actually need, then fix, replace, or stop it.",
        "For {task}, ask three regular users what works and what does not, and review a sample of recent outputs.",
    ),
    ("deployed", "any"): (
        "This is standard for the team here, and you did not report measured gains from AI at the firm. Without a starting measure, you cannot tell whether to invest further.",
        "Measure time saved and error rates before spending more here.",
        "For {task}, pick two measures and start collecting them.",
    ),
}
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
# Money levels are planning estimates set by the type of move and the firm's tools. They are not quotes.
SPEND_LABELS = {
    Spend.NONE: "No new money expected",
    Spend.SMALL: "Small spend",
    Spend.DECISION: "Needs a budget decision",
}
SPEND_ENDINGS = {
    "": ("", ""),
    "unset": ("", ", and nothing is set aside yet"),
    "under_100k": (", which should fit what you set aside", ", which may be more than you set aside"),
    "100k_500k": (", which should fit what you set aside", ""),
    "over_500k": (", which should fit what you set aside", ""),
}
SHAPE_KEY_FITS = {
    "unset": "No new money expected",
    "under_100k": "Should fit what you set aside",
    "100k_500k": "Should fit what you set aside",
    "over_500k": "Should fit what you set aside",
}
SHAPE_KEY_NOT = {"unset": "Needs money you have not set aside", "under_100k": "May need more than you set aside"}
FIT_NOTES = {"unset": "Needs money", "under_100k": "May need more"}
BUDGET_READING = {
    "unset": "You have no money set aside yet, so priorities that need none come first.",
    "under_100k": "With under $100K set aside, priorities that may need more come after the rest.",
}
BUDGET_READING_COVERED = "Taken one at a time, the priorities that need money should fit what you set aside, so your budget did not change the order."
BUDGET_READING_ALL_AT_ONCE = " Doing them all at once may not fit."
BUDGET_READING_NONE_FIT = "Every priority in this plan needs money you have not set aside, so a budget decision comes first."
BUDGET_WORTH_FUNDING = "The priority most worth finding money for is {label}, rated {level} compared with your other priorities."
LEADS_BUDGET = "It comes ahead of {next_task}, which may need money you have not set aside."
NAMED_REASON_BUDGET = "It may need money you have not set aside, so it comes after priorities that do not."
NAMED_REASON_BUDGET_LIFTED = "It may need money you have not set aside, but you named it, so it stays in the top three."
BUDGET_READING_EXCEPTION = " The task you named is the one exception."
START_NONE_FIT = "Decide its budget before you start."
START_BUDGET = "Take this priority on by itself first. The next priorities may need money you have not set aside."
START_NOBODY = "With nobody assigned yet, take this priority on by itself first."
START_SMALL = "With under 15 people, take this priority on by itself first."
START_PAIR = "Your second priority, on {label}, can run alongside it."
START_REST = " The rest can follow once both are running."
MONEY_LABEL = "Money, estimated"
CONNECT_DATA_TITLE = "Connect your core data"
SCOPE_TITLE = "After this blueprint: what to scope"
SCOPE_LEDE = "This blueprint decides which activities to take forward. Scoping each one comes next, and covers these."
SCOPE_ITEMS = (
    (
        "Data",
        "What data the priority touches, how good it is, and who may see it. This includes LP data, inside information, and personal data.",
    ),
    ("Systems", "Where that data lives, and whether it can be exported or connected."),
    ("Vendor and cost", "Which tools fit, what they cost, and how they handle your data."),
    (
        "Compliance",
        "Whether compliance has cleared the tool, how outputs are kept, and whether any LP or regulatory statement is affected.",
    ),
    ("People", "Who owns the priority, and how many hours they really have."),
)
ROADMAP_WAVES = (("Start now", 3), ("Then", 4), ("After that", None))
ROADMAP_WAVE_SPAN = "Priorities {first} to {last}"
ROADMAP_WAVE_ONE = "Priority {first}"
PRIORITY_WORD = "Priority"
TOP_STRIP_LABEL = "Your first priorities"
TOP_STRIP_META = "{verdict} · {speed} · {level} effect"
PRIORITY_ANCHOR = "{prefix}priority-{number}"
FACT_APPROACH = "Approach"
FACT_TIME = "Time"
FACT_EFFECT = "Effect"
FACT_MONEY = "Money"
FACT_LINK = "Link"
FACT_OWNER = "Suggested owner"
FACT_AI = "AI today"
ROADMAP_WAVE_PAIR = "Priorities {first} and {last}"
COVERAGE_LINE = "Your number depends most on {areas}, which you did not assess. Add it for a fuller plan."
PEOPLE_ELSEWHERE = "Across the firm, these also stay with your team: {items}."
STRATEGY_LINE = "This is your AI strategy and blueprint, built from one person's answers. It sets which activities to take forward, and in what order."
REPORT_NAME = "AI Strategy and Blueprint for PE Funds"
VERSION_LABEL = "Version {version}"
KPI_STATUS_ROW = {
    "on_target": "On target, you said",
    "off_target": "Off target, you said",
    "no_target": "Tracked, no target set",
}
STUCK_TITLE = "Where the work gets stuck"
STUCK_TASK = "{task}: {facts}"
STUCK_TIME_AREA = "Time goes on {what}."
STUCK_SLOW_AREA = "The slowest step is {step}."
STUCK_ONE_PERSON_AREA = "Know-how is held by one or two people."
STUCK_VARIES_AREA = "It runs differently by team."
STUCK_HABIT = "{task}: done mainly out of habit."
STUCK_SOURCES = "Information is split across {sources}, with no system holding it."
STUCK_SOURCES_SYSTEM = "Information is split across {sources}."
CAPACITY_TECH_OWNER = {"in_house": "Your tech team, with {owner}", "partner": "{owner}, with the outside firm that sets it up"}
Y_AXIS_TITLE = "Relative effect on {kpi}"
KPI_TYPED_EFFECT = "change {kpi}"
KPI_TYPED_HEADING = "How your priorities compare on {kpi}"
PLOT_HEADING = "How much each priority could {effect}"
KPI_OWN_NO_FORECAST = "The ratings rank your priorities against each other. They do not predict any change in {kpi}."
KPI_TYPED_BASELINE = "Record where {kpi} stands today, and how you measure it."
FEEDS_LINE = "This number feeds {feeds}."
FEEDS_LINKS = {
    "direct": "The link is direct.",
    "partial": "The link is partial, because other factors also matter.",
    "indirect": "The link is indirect, because other factors also matter.",
}
NO_RETURNS_CLAIM = "This plan makes no claim about IRR, MOIC, or DPI."
KPI_MATCHED_NOTE = "You chose your own number. Effect is estimated with the rules for {matched}, the closest on our list."
KPI_OWN_NOTE = "You chose your own number. Each priority shows its link to it."
RELATIVE_NOTE = "Effect compares your priorities with each other, using each task's link and the hours behind it. It is not a forecast."
VIEW_GROUP_LABEL = "Report view"
VIEW_TAB_BUDGET = "With your budget"
VIEW_TAB_OPEN = "No budget limit"
VIEW_NOTE_OPEN = "This view ignores your budget. The priorities are the same, in the order they would take with no limit. Tool suggestions and money levels can differ."
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
STAGE_PHRASES = {
    "none": "Not used yet",
    "individuals": "Individuals use AI on their own",
    "pilots": "Trials in some teams",
    "deployed": "Standard across teams",
}
ADOPTION_PHRASES = {
    "under_10": "A few people",
    "10_30": "Some people",
    "30_60": "Many people",
    "over_60": "Most people",
}
RESULTS_PHRASES = {
    "measured": "Measured gains",
    "unmeasured": "Useful, but not measured",
    "mixed": "Mixed, or too early to say",
    "disappointing": "Disappointing",
}
HERE_PHRASES = {
    "task": "In use on this task",
    "adhoc": "Some people, informally",
    "pilot": "A small trial",
    "deployed": "Standard for the team",
}
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
    Nature.JUDGMENT: "Keep the decision with your team. AI can prepare background and past examples.",
}
CUSTOM_FIRST_STEP = "Write down the inputs, decisions, and who receives the result for {task}."
CUSTOM_SERIOUS_CHECK = "Have a second person check the results while this is new."
CUSTOM_PREPARE_SOLUTION = "Have AI gather the information and prepare the work, and have the owner carry out each step."
CUSTOM_CHECK = "The current owner reviews the results."
CUSTOM_TAG = "Added by you"

SOURCE_PHRASES = {
    "system": "a proper system",
    "spreadsheets": "spreadsheets",
    "email": "email",
    "documents": "documents",
}
WHO_PHRASES = {
    "partners": "partners or principals",
    "investment": "VPs, associates, or analysts",
    "operations": "finance, IR, compliance, or ops staff",
    "outside": "an outside provider",
}
TIME_PHRASES = {
    "wait_outside": "waiting on outside parties",
    "wait_signoff": "waiting on internal sign-off",
    "rekey": "retyping or rebuilding",
    "fixing": "fixing errors and mismatches",
}
LINK_WORDS = {3: "has a direct link to", 2: "has a strong link to", 1: "has some link to", 0: "has an indirect link to"}
# Fixes the first step on the hardest task in a work area, from where they said the time goes. First hit wins.
TIME_STEP_ENDINGS = (
    ("wait_signoff", " Also list who signs, and what each changed last cycle."),
    ("rekey", " Also count how often the same figure is typed."),
    ("fixing", " Also collect the reasons for the last ten corrections."),
)
TRACKED_MEASURE_ENDING = " Watch {measure}, which you already track."
SIGNOFF_SUFFIX = " Agree a turnaround with whoever signs off, because you said time goes there. Approvals stay in place."
RHYTHM_STEP_ENDINGS = {
    "periodic": " Test on last period's files, because the next live run is at the next period end.",
    "bursts": " Test on a past burst, using files from the last deal or request.",
}
SLOW_STEP_TEXT = "You said the slowest step is: {slow_step}. Write down how it runs and what it checks, and keep any check that protects the numbers."
NOT_EXAMINED = "Not examined in detail, because you chose a quick check of this work area."
WALKTHROUGH_TITLE = "How it runs today, as you described it"
HOURS_PHRASES = {
    "under_20": "under 20 hours",
    "20_60": "20 to 60 hours",
    "60_200": "60 to 200 hours",
    "over_200": "over 200 hours",
}
LINK_LADDER = {3: "Direct link", 2: "Strong link", 1: "Some link", 0: "Indirect link"}

FIRM_WIDE_LABEL = "Firm-wide"
FIRM_WIDE_OWNER = "COO or managing partner"
FIRM_WIDE_SPEED = "Decide within 30 days"
PLAIN_TERMS = (
    (
        "Automation",
        "Software that follows fixed rules, the same way every time. Where rules are enough, you may not need AI at all.",
    ),
    (
        "AI that drafts",
        "Software that can read documents and write a first version. A person reviews the result before it is used.",
    ),
    (
        "Agentic AI",
        "AI that carries out several steps in a row across your tools, such as requesting a file, checking it, and loading it. In this plan, a person approves anything that leaves the firm.",
    ),
    (
        "Trial",
        "A small, time-limited test with a few people, to learn whether something works before the whole team uses it.",
    ),
    ("First working version", "The point when a real team can use it on real work. Refinement continues after that."),
    ("Human check", "The step where a named person reviews the output. That person remains responsible."),
)
TIMELINE_MARKS = ("Today", "30 days", "60 days", "90 days", "Later")

METHOD_NOTE = "How the estimates work: speed and effect come from fixed planning rules applied to your answers, such as the hours you reported, who does the work, where the information lives, where the time goes, your constraints, and how directly each task relates to the number you chose, including through each team's own measures. They are planning assumptions, not benchmarks, and they use no benchmark data from any firm. Test them with your team before relying on them."
HORIZON_LABELS = {Horizon.NOW: "Now", Horizon.NEXT: "Next", Horizon.LATER: "Later"}
HORIZON_SPANS = {
    Horizon.NOW: "Under 30 days, estimated",
    Horizon.NEXT: "30 to 90 days, estimated",
    Horizon.LATER: "Over 90 days, estimated",
}
QUADRANT_LABELS = {
    Quadrant.QUICK_WINS: "Faster, higher effect",
    Quadrant.STRATEGIC_BETS: "Slower, higher effect",
    Quadrant.FILL_INS: "Faster, lower effect",
    Quadrant.DEPRIORITIZE: "Slower, lower effect",
}

SHADOW_FOUNDATION = (
    "Bring existing AI use under a policy",
    "You said people use AI, and that the firm has no AI policy. Confidential data may be reaching tools you have not approved. Set rules before adding anything new.",
    "Agree which AI tools are approved, and what data may go into them.",
)
SHADOW_RESTRICTED_FOUNDATION = (
    "Settle how existing AI use fits your policy",
    "You said people use AI, and also that your policy restricts it. Find out what is happening in practice, and decide what is allowed.",
    "Ask whoever leads compliance to review how AI is used today, against your policy.",
)
ONE_PERSON_FOUNDATION = (
    "Write down what only one or two people know",
    "You said {subject} depends on one or two people{harm}.",
    "Write down how {subject} runs today, step by step.",
)
# The person who does the work writes it down. A senior owner only signs it off.
ONE_PERSON_ACTION_START = "Write down how"
ONE_PERSON_OWNER = "Whoever does this today, signed off by the COO or managing partner"
ONE_PERSON_HARM = ", and a mistake there could cause serious harm"
OWNER_FOUNDATION = (
    "Name an owner",
    "Nobody is set to carry out this work yet, so the plan has no one to run it. Name one accountable person first.",
    "Name one accountable person, and protect time for them.",
)
DATA_ACTION = "List the data that {task} relies on, and pick one source to clean up."
FOUNDATIONS = {
    ("ai_results", "unmeasured"): (
        "Measure what you already have",
        "You said AI is useful, but not measured. Without a starting measure, you cannot tell which work to expand.",
        "Pick two measures and start recording them for your current AI work.",
    ),
    ("ai_results", "mixed"): (
        "Find out where AI works and where it does not",
        "You said results are mixed, or that it is too early to say. Compare what has worked with what has not before extending it.",
        "List where AI has worked and where it has not, and what differs.",
    ),
    ("ai_results", "disappointing"): (
        "Find out why earlier AI work fell short",
        "You described results so far as disappointing. Review what fell short before starting something new: the use case, the data, or the adoption.",
        "List what was tried, and the reason each effort fell short.",
    ),
    ("ai_adoption", "under_10"): (
        "Get more use out of what you have",
        "You said only a few people use AI each week, so tools may be sitting unused. Find out why before adding new ones.",
        "Ask five people who do not use AI what stops them.",
    ),
    ("policy", "none"): (
        "Agree an AI policy",
        "Any AI work is held back without one. A short list of approved tools and data rules is enough to start.",
        "Write a one-page list of approved tools and data rules.",
    ),
    ("policy", "restricted"): (
        "Keep AI on hold for now",
        "Nothing in this plan needs AI, so your policy can stay as it is. If the team later wants AI, ask whoever leads compliance which low-risk uses could be approved.",
        "Confirm with whoever leads compliance that the priorities below fit your policy.",
    ),
    ("systems", "disconnected"): (
        "Connect your core data",
        "You said your software tools do not share data, so the same figures may end up in more than one place.",
        DATA_ACTION,
    ),
    ("systems", "manual"): (
        "Keep one master copy of your most-used data",
        "You said most work runs on Excel and email. Pick one dataset to centralize first, and let your first priority decide which.",
        DATA_ACTION,
    ),
    ("trust", "skeptical"): (
        "Win over the skeptics",
        "You said some people are skeptical of relying on AI's work. Pick one item that a skeptical senior person cares about, and measure it next to the current process.",
        "Pick one item that a skeptical senior person cares about.",
    ),
    ("trust", "resistant"): (
        "Start with work people dislike",
        "You said some people are against relying on AI's work. Begin with tasks nobody wants to keep, and leave review power with them.",
        "Ask the team which routine tasks they would most like to lose.",
    ),
    ("kpi_status", "untracked"): (
        "Start measuring {kpi}",
        "You chose this number, and you do not track it today, so you cannot yet tell whether any priority helps.",
        "{baseline}",
    ),
    ("kpi_status", "no_target"): (
        "Set a target for {kpi}",
        "You track this number, with no target set, so there is nothing to judge progress against.",
        "Agree a target for {kpi}.",
    ),
}
SHARED_DATA_FOUNDATION = (
    "Build this data once",
    "You selected {count} tasks that draw on the same portfolio data: {tasks}. Agree one owner and one copy, and let each task draw from it.",
    "Name one owner for the portfolio data that these tasks share.",
)
COUNT_WORDS = {
    Verdict.AUTOMATE: ("automates with fixed rules", "automate with fixed rules"),
    Verdict.OPTIMIZE: ("fixes the process", "fix the process"),
    Verdict.REMOVE: ("tests stopping", "test stopping"),
    Verdict.ADD_AI: ("uses AI to prepare work", "use AI to prepare work"),
    Verdict.AGENTIC: ("lets AI run the steps", "let AI run the steps"),
    Verdict.BUILD_ON: ("builds on AI already here", "build on AI already here"),
}
NAMED_FIRST = "You named {task} as the task to take off your team, and it comes first."
NAMED_LATER = "You named {task} as the task to take off your team. It is priority {position}. {reason} If freeing that time matters more than this number, start there instead."
NAMED_REASON_CLOSER = "{above} a closer link to {kpi}."
NAMED_REASON_TIME = "More senior time or hours sit with {above_lower}, on your answers."
NAMED_REASON_SCORE = "{above} a higher score under our planning rules."
NAMED_REASON_LIFTED = "It is placed here because you named it."
KPI_STATUS_READING = {
    "untracked": "You chose {kpi}, and you do not track it today, so measuring it comes before judging any priority.",
    "off_target": "You said {kpi} is off target, so the plan weighs effect on it more heavily.",
    "on_target": "You said {kpi} is on target, so hours count for more in this ranking. Check that it is the right number to move.",
}
MEASURE_ACTION = "Record {measure} for one cycle, by hand if needed."
CHAIN_LINE = "Through {measure}, a measure that feeds {kpi}. This link is a planning assumption."
LEVER_POLICY = "whoever leads compliance approved AI tools"
LEVER_SYSTEMS = "your tools shared data"
LEVER_CAPACITY = "someone were responsible for this work"
QUADRANT_NOTE_TOP = "Ringed: the priorities recommended above."
QUADRANT_LABELS_SHORT = {
    Quadrant.QUICK_WINS: "Fast, high",
    Quadrant.STRATEGIC_BETS: "Slow, high",
    Quadrant.FILL_INS: "Fast, low",
    Quadrant.DEPRIORITIZE: "Slow, low",
}

STAYS_WITH_PEOPLE_LEDE = "These stay with your team, because they rest on judgment or relationships."
PEOPLE_ANCHOR = "{prefix}people"
GLANCE_PEOPLE = "{count} {verb} with your team"
ROADMAP_PEOPLE_NOTE = {
    1: "Not on the roadmap: 1 activity you selected stays with your team, because it rests on judgment or relationships.",
    "many": "Not on the roadmap: {count} activities you selected stay with your team, because they rest on judgment or relationships.",
}
ROADMAP_PEOPLE_LINK = "See which ones"
NAMED_TAG = "You named this as the task to take off your team"

RULE_ANCHOR_STEPS = {
    Rule.ONE_PERSON: "Have the person who knows {task} walk a colleague through one full cycle, and record it.",
    Rule.NOT_SAME_WAY: "For {task}, pick one team's way as the starting standard, and list where the others differ.",
    Rule.REDO: "For {task}, collect the reasons for the last ten corrections.",
    Rule.SIGNOFFS: "For {task}, list who signs, and what each changed last cycle. Keep every required control.",
    Rule.OUTSIDE: "For {task}, list what you send the provider, and what you re-check afterwards.",
    Rule.TEMPLATE_ENOUGH: "Build the template for {task} from last period's work.",
    Rule.REKEY_AUTOMATE: "For {task}, count how often the same figure is typed, and which source wins.",
}
DEPENDS_PHRASES = {
    "yes": "the know-how written down",
    "effort": "know-how someone else could pick up with some effort",
    "no": "know-how held by one or two people",
}
RHYTHM_PHRASES = {
    "steady": "running daily or weekly",
    "monthly": "running every month",
    "periodic": "running quarterly or yearly",
    "bursts": "running in bursts",
}
SAME_WAY_PHRASES = {
    "same": "run one way across teams",
    "mostly": "run mostly one way, with local differences",
    "different": "run differently by team",
}
ERROR_PHRASES = {
    "minor": "mistakes noticed and fixed internally",
    "awkward": "mistakes visible to LPs or boards",
    "severe": "mistakes that could cause financial, legal, or regulatory harm",
    "unsure": "the cost of mistakes unclear",
}
ROUTE_INTEGRATED = "Automation inside your main platform, which should need the least new software"
HEADLINE_VERBS = {
    Verdict.AUTOMATE: "Your first priority is to automate {label}",
    Verdict.ADD_AI: "Your first priority is to use AI for {label}",
    Verdict.AGENTIC: "Your first priority is to use an AI agent for {label}",
    Verdict.OPTIMIZE: "Your first priority is to fix the process behind {label}",
    Verdict.REMOVE: "Your first priority is to test whether {label} can stop",
    Verdict.BUILD_ON: "Your first priority is to build on the AI you already use for {label}",
}
HEADLINE_RULES = {
    Rule.AGREE_FIRST: "Your first priority is to agree the rules for {label}",
    Rule.ONE_PLACE: "Your first priority is to set up one shared place for {label}",
    Rule.ONE_PERSON: "Your first priority is to write down the steps for {label}",
    Rule.OUTSIDE: "Your first priority is to agree what your provider delivers for {label}",
    Rule.NOT_SAME_WAY: "Your first priority is to agree one standard across teams for {label}",
    Rule.REDO: "Your first priority is to fix the cause of errors in {label}",
    Rule.SIGNOFFS: "Your first priority is to shorten sign-offs on {label}",
    Rule.RESTRICTED: "Your AI policy rules out AI for now, so start with the process for {label}",
    Rule.TEMPLATE_ENOUGH: "Your first priority is to build one template for {label}",
    Rule.KEEP_MINIMAL: "Your first priority is to agree the minimum for {label}",
    Rule.KEEP_CONTROL: "Your first priority is to simplify the process for {label}, and keep the control",
    Rule.LEGACY_CHECK: "Your first priority is to check who still needs {label}",
    Rule.QUICK_REVIEW: "Your first priority is to review how {label} runs",
    Rule.SERIOUS_PROCESS_FIRST: "Your first priority is to settle the process for {label}",
    Rule.CUSTOM_WRITE_RULES: "Your first priority is to write down the rules for {label}",
}
CHANGE_WORDS = {
    Verdict.OPTIMIZE: "a process fix",
    Verdict.ADD_AI: "AI that prepares the work",
    Verdict.AUTOMATE: "automation",
    Verdict.AGENTIC: "AI that runs the steps",
    Verdict.BUILD_ON: "building on AI already here",
    Verdict.REMOVE: "testing a stop",
}
LEADS_NAMED = "It leads because you named it."
LEADS_MORE_DIRECT = "It leads because it has a closer link to {kpi} than {next_task}."
LEADS_MORE_HOURS = "It leads because more senior time or hours are at stake here than on {next_task}."
LEADS_FASTER = "It leads because it should reach a result sooner than {next_task}."
LEADS_TIE = "It is level with {next_task} under our rules, so start with whichever causes more trouble today."
# A move rated the same as the one before it says why it comes second.
FOLLOWS_THESIS = "It is rated the same as {prev_task}, which comes first because its work is in your thesis focus."
FOLLOWS_HOURS = "It is rated the same as {prev_task}, which comes first because more senior time or hours are at stake there."
FOLLOWS_EFFECT = "It is rated the same as {prev_task}, which comes first because it scored slightly higher on effect under our rules."
FOLLOWS_FASTER = "It is rated the same as {prev_task}, which comes first because it should reach a result a little sooner."
FOLLOWS_TIE = "It is level with {prev_task} under our rules, so take whichever causes more trouble today first."
TIE_START = "Your second priority, on {label}, ranks level with it, so run both and choose the order that suits your team."
READING_TITLE = "What in your answers shaped this plan"
PLANNING_LINE_ONE = "Under our planning rules, the one priority that adds software {timing}."
AI_NOT_ASKED_NOTE = "Not asked in this quick check"
AND_OTHERS = "and others"
START_OFF_TARGET = "Your third priority, on {label}, can run alongside it, because it acts on {measure}, the measure you said is off target."
AI_BEHIND = "You said AI is standard across teams, but in the areas assessed it is less than that. Check whether these areas are behind, or whether the answer needs correcting."
DATA_ACTION_START = "List the data that"
HARDEST_FACTS = "On {task}: {facts}."
SLOW_STEP_WHY = "You said the slowest step is: {slow_step}."
MORE_CHANGES = "Other priorities would change too."
