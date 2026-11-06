"""The final report: a self-contained memo on a white background, in the NXT Partners identity."""
from __future__ import annotations

import datetime as dt
import html
from typing import Dict, List

from . import constants as c
from . import tokens as t
from .data import Library
from .enums import AiStage, Horizon, Quadrant, Verdict
from .models import Answers, ScoredActivity
from .plot import render_plot, timeline_share
from .scoring import Plan, effect_text, impact_level, lower_first
from .styles import data_uri, stylesheet

esc = html.escape


def key_mark(verdict: Verdict) -> str:
    color = t.VERDICT_COLORS[verdict]
    fill = t.COLOR_SURFACE if verdict in t.VERDICT_HOLLOW else color
    return f'<i class="key-mark" style="color:{color};background:{fill}" aria-hidden="true"></i>'


def section(number: int, title: str, body: str) -> str:
    slug = f"sec-{number}"
    return f'<section class="sec" aria-labelledby="{slug}"><div class="sec-head"><span class="sec-no">{number:02d}</span><h2 id="{slug}">{esc(title)}</h2></div><div>{body}</div></section>'


def hours_text(plan: Plan) -> str:
    if plan.hours_high is None:
        return f"At least {plan.hours_low}"
    return f"Up to {plan.hours_high}" if plan.hours_low == 0 else f"{plan.hours_low} to {plan.hours_high}"


def plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


HEADLINE_VERBS = {
    Verdict.AUTOMATE: "Your first move is to automate {label}",
    Verdict.ADD_AI: "Your first move is to use AI for {label}",
    Verdict.AGENTIC: "Your first move is to use an AI agent for {label}",
    Verdict.OPTIMIZE: "Your first move is to fix the process behind {label}",
    Verdict.REMOVE: "Your first move is to test whether {label} can stop",
    Verdict.BUILD_ON: "Your first move is to build on the AI you already use for {label}",
}


def headline(plan: Plan) -> str:
    if not plan.top:
        return "Your answers point to work that should stay with your people"
    item = plan.top[0]
    label = lower_first(item.label)
    if item.ai_assumed and item.restricted_in_use:
        return f"Your first move is to settle how AI is used in {lower_first(item.workstream_label)}"
    if item.ai_assumed and item.verdict == Verdict.BUILD_ON:
        return f"Your first move is to review how AI is used in {lower_first(item.workstream_label)}, starting with {label}"
    if item.restricted_in_use:
        return f"Your first move is to settle how AI is used for {label}"
    if item.quadrant == Quadrant.DEPRIORITIZE and item.effect_rated:
        return f"Nothing here ranks highly against your KPI, so start with {label}"
    if item.ai_unknown:
        return f"Your first move is to check whether AI is already used for {label}, and if not, to add it"
    return HEADLINE_VERBS[item.verdict].format(label=label)


def standfirst(plan: Plan, kpi: str) -> str:
    total = len(plan.plotted)
    if not total:
        return "The work you selected depends on judgment and relationships, so it stays with your people. To find work to automate, run this again on your more repetitive tasks."
    top = plan.top[0]
    lead = f"It ranks first when we weigh its likely effect on {lower_first(kpi)} against the estimated time, based on your answers." if top.kpi_linked else "It ranks first on the estimated time and the hours involved, based on your answers."
    if len(plan.top) > 1 and plan.top[1].impact == top.impact and plan.top[1].weeks == top.weeks:
        lead += f" It ties with {lower_first(plan.top[1].label)} under our rules, so start with whichever causes more trouble today."
    software = [item for item in plan.plotted if item.verdict in c.TECH_VERDICTS]
    if not software:
        return f"{lead} None of the moves below adds new software, so these are process changes you could start soon."
    within = sum(1 for item in software if item.weeks < c.WEEKS_NEXT)
    if len(software) == 1:
        timing = "could reach a first working version within 90 days" if within else "would take over 90 days"
        return f"{lead} Under our planning rules, the one move that adds software {timing}, if worked on alone."
    count = plural(len(software), "move")
    if within == 0:
        return f"{lead} Under our planning rules, the {count} that add software would each take over 90 days."
    share = f"each of the {count}" if within == len(software) else f"{within} of the {count}"
    return f"{lead} Under our planning rules, {share} that add software could reach a first working version within 90 days if worked on alone.{' Choose two or three to start.' if len(plan.plotted) > 3 else ''}"


def told(answers: Answers, field: str) -> bool:
    return field not in answers.skipped


def opening(answers: Answers, plan: Plan, library: Library, kpi: str) -> str:
    firm_bits = []
    if told(answers, "strategy"):
        firm_bits.append(library.option_label("strategy", answers.strategy))
    if told(answers, "aum"):
        firm_bits.append(f"{library.option_label('aum', answers.aum)} AUM")
    if told(answers, "team"):
        firm_bits.append(f"{library.option_label('team', answers.team)} people")
    if told(answers, "fund_stage"):
        firm_bits.append(f"fund stage: {library.option_label('fund_stage', answers.fund_stage).lower()}")
    thesis = answers.thesis_summary or (library.option_label("thesis", answers.thesis) if told(answers, "thesis") else "")
    rows = [
        ("Prepared for", answers.firm_name),
        ("Firm", " · ".join(firm_bits)),
        ("Thesis", thesis),
        ("Priority", library.option_label("pressure", answers.pressure) if told(answers, "pressure") else ""),
        ("Measured against", kpi),
        ("Assessed", ", ".join(library.workstreams[work.id]["label"] for work in answers.workstreams)),
    ]
    quick = sum(1 for item in plan.plotted if item.quadrant == Quadrant.QUICK_WINS)
    stops = sum(1 for item in plan.plotted if item.verdict == Verdict.REMOVE) + len(plan.people)
    glance = []
    if plan.hours_known:
        glance.append(f"{hours_text(plan)} hours a month reported")
    if plan.plotted:
        glance += [plural(len(plan.plotted), "move"), f"{plural(quick, 'higher-effect move')} within 90 days, estimated"]
    if stops:
        glance.append(f"{stops} to stop, or leave with people")
    rows.append(("At a glance", " · ".join(glance)))
    ledger = "".join(f"<div><dt>{esc(key)}</dt><dd>{esc(value)}</dd></div>" for key, value in rows if value)
    return f'<div class="opening"><h1>{esc(headline(plan))}</h1><p class="standfirst">{esc(standfirst(plan, kpi))}</p></div><dl class="ledger">{ledger}</dl><div class="spacer"></div>'


def recommendation(plan: Plan) -> str:
    if not plan.top:
        return ""
    moves = []
    for index, item in enumerate(plan.top, start=1):
        unknown = f"<span>{esc(c.AI_UNKNOWN_CARD)}</span>" if item.ai_unknown else ""
        thesis = f'<p><span class="lead">For your thesis.</span> {esc(item.thesis_note)}</p>' if item.thesis_note else ""
        moves.append(
            f'<li><span class="no">Move {index}</span><h3>{esc(item.label)}</h3><p>{esc(item.solution)}</p>'
            f'<p><span class="lead">First step.</span> {esc(item.first_step)}</p>{thesis}'
            f'<p class="meta"><span>{esc(c.VERDICT_LABELS[item.verdict])} · {esc(item.speed_label)}, estimated</span><span>{esc(item.relevance_note)}</span>{unknown}</p></li>'
        )
    return f'<ol class="moves">{"".join(moves)}</ol>'


def position(answers: Answers, plan: Plan, library: Library) -> str:
    rows = []
    if told(answers, "ai_stage"):
        rows.append(("AI today", c.STAGE_PHRASES[answers.ai_stage]))
    if answers.ai_stage != AiStage.NONE.value:
        tools = ", ".join(library.option_label("ai_tools", tool) for tool in answers.ai_tools)
        if tools:
            rows.append(("Tools", tools))
        if told(answers, "ai_adoption"):
            rows.append(("Weekly use", c.ADOPTION_PHRASES[answers.ai_adoption]))
        if told(answers, "ai_results"):
            rows.append(("Results so far", c.RESULTS_PHRASES[answers.ai_results]))
    if told(answers, "ai_obstacle"):
        rows.append(("Main obstacle", c.OBSTACLE_PHRASES[answers.ai_obstacle]))
    if told(answers, "policy"):
        rows.append(("AI policy", library.option_label("policy", answers.policy)))
    if told(answers, "budget"):
        rows.append(("Budget", library.option_label("budget", answers.budget)))
    ledger = "".join(f"<div><dt>{esc(key)}</dt><dd>{esc(value)}</dd></div>" for key, value in rows)
    existing = [item for item in plan.items if item.ai_note and not item.ai_unknown]
    existing_html = ""
    if existing:
        lines = "".join(f'<li><span class="lead">{esc(item.label)}.</span> {esc(item.ai_note)}.</li>' for item in existing)
        existing_html = f'<h3 class="subhead">AI already in this work</h3><ul class="list">{lines}</ul>'
    clear = ""
    if plan.foundations:
        lines = "".join(f'<li><span class="lead">{esc(title)}.</span> {esc(text)}</li>' for title, text, _ in plan.foundations)
        clear = f'<h3 class="subhead">Clear these first</h3><ol class="list">{lines}</ol>'
    if not (ledger or existing_html or clear):
        return ""
    ledger_html = f'<dl class="ledger">{ledger}</dl>' if ledger else ""
    return f"{ledger_html}{existing_html}{clear}"


def legend(plan: Plan) -> str:
    present = [v for v in Verdict if v != Verdict.LEAVE and any(item.verdict == v for item in plan.plotted)]
    rows = "".join(f"<li>{key_mark(v)}<b>{esc(c.VERDICT_LABELS[v])}</b>. {esc(c.VERDICT_DEFINITIONS[v])}</li>" for v in present)
    return f'<ul class="legend">{rows}</ul>'


def priorities(plan: Plan, kpi: str) -> str:
    if not plan.plotted:
        return ""
    key = "".join(f'<li><span class="mono soft">{item.number}</span><span>{esc(item.label)}</span></li>' for item in plan.plotted)
    return (
        f'<figure class="flush">{render_plot(plan.plotted, kpi)}{legend(plan)}<ol class="plot-key">{key}</ol>'
        f'<figcaption class="note">Speed is the estimated time to a first working version, or to finish a process change. Effect is the estimated effect on {esc(lower_first(kpi))}. Both are planning estimates, explained in the notes, not measurements.</figcaption></figure>'
    )


def roadmap(plan: Plan) -> str:
    if not plan.plotted:
        return ""
    columns = []
    for horizon in Horizon:
        rows = sorted((item for item in plan.plotted if item.horizon == horizon), key=lambda item: (item.verdict != Verdict.REMOVE, item.number))
        body = "".join(f'<li><span class="mono soft">{item.number}</span><span>{esc(item.label)}<br><span class="small soft">{esc(c.VERDICT_LABELS[item.verdict])}</span></span></li>' for item in rows)
        body = f"<ul>{body}</ul>" if body else '<p class="soft small gap-top">Nothing reaches a first working version this soon. See Your next 30 days for what starts now.</p>'
        columns.append(f'<div><h3>{esc(c.HORIZON_LABELS[horizon])}</h3><small>{esc(c.HORIZON_SPANS[horizon])}</small>{body}</div>')
    return f'<p class="sec-lede soft">Each estimate assumes the move is worked on alone. Running several at once takes longer.</p><div class="stages">{"".join(columns)}</div>'


def detail_row(item: ScoredActivity) -> str:
    planned = item.verdict != Verdict.LEAVE
    speed = f'<span class="col">{esc(item.speed_label)}, estimated</span><span class="col">{esc(effect_text(item.impact, item.effect_rated))}</span>' if planned else '<span class="col"></span><span class="col"></span>'
    fields = [("Why", item.reason), ("What changes for your team", item.solution)]
    if item.route:
        fields.append((c.ROUTE_LABEL, item.route))
    fields += [("First step", item.first_step), ("Human check", item.check), ("Suggested owner", item.owner_role)]
    if item.relevance_note:
        fields.append(("Link to your KPI", item.relevance_note))
    if item.ai_note:
        fields.append(("AI here today", item.ai_note))
    if item.thesis_note:
        fields.append(("For your thesis", item.thesis_note))
    if item.custom:
        fields.append(("Source", c.CUSTOM_TAG))
    body = "".join(f"<div><dt>{esc(key)}</dt><dd>{esc(value)}</dd></div>" for key, value in fields)
    return (
        f'<details><summary><span class="mono soft">{item.number}</span><span class="name">{esc(item.label)}</span>'
        f'<span class="col">{key_mark(item.verdict)}{esc(c.VERDICT_LABELS[item.verdict])}</span>{speed}<span class="toggle" aria-hidden="true"></span></summary>'
        f'<div class="row-body"><dl>{body}</dl></div></details>'
    )


TABLE_HEAD = '<div class="table-head" aria-hidden="true"><span></span><span>Activity</span><span>Recommendation</span><span>Estimated time</span><span>Effect on your KPI</span><span></span></div>'


def details_table(plan: Plan) -> str:
    if not plan.plotted:
        return ""
    groups: Dict[str, List[ScoredActivity]] = {}
    for item in plan.plotted:
        groups.setdefault(item.workstream_label, []).append(item)
    blocks = "".join(f'<div class="group"><h3>{esc(label)}</h3>{f"<p>{esc(items[0].evidence)}</p>" if items[0].evidence else ""}<div class="rows">{"".join(detail_row(item) for item in items)}</div></div>' for label, items in groups.items())
    return f'<p class="sec-lede soft">Open a row to see why, what changes for your team, the first step, and who should own it. Effect is rated only against the KPI you chose, so a task can matter to the firm and still rate Low here.</p>{TABLE_HEAD}{blocks}'


def people(plan: Plan) -> str:
    if not plan.people:
        return ""
    return f'<p class="sec-lede soft">These stay with your people.</p><div class="rows">{"".join(detail_row(item) for item in plan.people)}</div>'


def notes(answers: Answers, plan: Plan) -> str:
    rows = [
        c.METHOD_NOTE,
        "The answers behind this report come from one person. Other people at your firm may see it differently.",
        "We did not estimate cost. Ask for a price on your first move before committing.",
        "This is operational guidance generated with AI. It is not investment, legal, tax, or compliance advice, so have the right people review it before acting.",
        c.REGION_NOTES[answers.region],
    ]
    if answers.strategy == "credit":
        rows.append(c.CREDIT_NOTE)
    if plan.not_assessed:
        rows.append("Not assessed in this run: " + ", ".join(plan.not_assessed) + ".")
    if answers.assumed:
        rows.append("You skipped these, so a neutral assumption was used: " + ", ".join(answers.assumed) + ".")
    if answers.ai_assumed_areas:
        rows.append("You did not say which tasks use AI in " + ", ".join(answers.ai_assumed_areas) + ", so its routine tasks were treated as using AI.")
    return f'<ol class="notes">{"".join(f"<li><span>{esc(row)}</span></li>" for row in rows)}</ol>'


def public_sources(answers: Answers) -> str:
    if not answers.public_facts:
        return ""
    rows = "".join(
        f'<li><span>{esc(item[c.KEY_FACT])} <a href="{esc(item[c.KEY_SOURCE], quote=True)}" rel="noopener noreferrer">Source</a></span></li>'
        for item in answers.public_facts
    )
    return f'<p class="sec-lede soft">Found on public websites and confirmed by you during this assessment.</p><ol class="notes">{rows}</ol>'


def next_30_days(plan: Plan, kpi: str) -> str:
    rows = [("", action, c.FIRM_WIDE_OWNER) for _, _, action in plan.foundations[: c.NEXT_30_MAX_FOUNDATIONS]]
    rows.append(("", c.KPI_BASELINE_ACTION.format(kpi=lower_first(kpi)), c.FIRM_WIDE_OWNER))
    unknown_areas = list(dict.fromkeys(item.workstream_label for item in plan.items if item.ai_unknown))
    rows += [("", c.AI_UNKNOWN_ACTION.format(area=lower_first(area)), c.FIRM_WIDE_OWNER) for area in unknown_areas]
    rows += [(item.label, item.first_step, item.owner_role) for item in plan.top]
    lines = "".join(
        f'<li><span class="mono soft">{index}</span><span>{f"<span class=lead>{esc(task)}.</span> " if task else ""}{esc(action)}</span><span class="owner">{esc(owner)}</span></li>'
        for index, (task, action, owner) in enumerate(rows, start=1)
    )
    return f'<p class="sec-lede soft">First steps from this plan, with a suggested owner for each. Adjust the owners to fit how your firm is organized.</p><ol class="actions-list">{lines}</ol>'


def timeline_row(number: str, label: str, speed: str, share: float, color: str, hollow: bool) -> str:
    dot_fill = t.COLOR_SURFACE if hollow else color
    percent = f"{share * 100:.1f}%"
    return (
        f'<div class="tl-row"><div class="tl-label"><span class="mono soft">{number}</span><span>{esc(label)}<br><span class="small soft">{esc(speed)}</span></span></div>'
        f'<div class="tl-track" aria-hidden="true"><span class="tl-bar" style="width:{percent};background:{color}"></span><span class="tl-dot" style="left:{percent};background:{dot_fill};border-color:{color}"></span></div></div>'
    )


def department_roadmap(plan: Plan) -> str:
    if not plan.plotted and not plan.foundations:
        return ""
    marks = "".join(f'<span style="left:{index * 100 / (len(c.TIMELINE_MARKS) - 1):.0f}%">{esc(mark)}</span>' for index, mark in enumerate(c.TIMELINE_MARKS))
    axis = f'<div class="tl-axis" aria-hidden="true"><span class="small soft">Project and suggested owner</span><div class="tl-scale">{marks}</div></div>'
    groups = []
    if plan.foundations:
        rows = "".join(timeline_row("·", title, c.FIRM_WIDE_SPEED, 1 / len(c.SPEED_BANDS), t.COLOR_INK_SOFT, True) for title, _, _ in plan.foundations)
        groups.append(f'<div class="tl-group"><h3>{esc(c.FIRM_WIDE_LABEL)}</h3><p class="owner">Suggested owner: {esc(c.FIRM_WIDE_OWNER)}</p>{rows}</div>')
    departments: Dict[str, List[ScoredActivity]] = {}
    for item in plan.plotted:
        departments.setdefault(item.workstream_label, []).append(item)
    for label, items in departments.items():
        rows = "".join(timeline_row(str(item.number), item.label, f"{c.VERDICT_LABELS[item.verdict]} · {item.speed_label}, estimated", timeline_share(item.weeks), t.VERDICT_COLORS[item.verdict], item.verdict in t.VERDICT_HOLLOW) for item in sorted(items, key=lambda row: row.weeks))
        groups.append(f'<div class="tl-group"><h3>{esc(label)}</h3><p class="owner">Suggested owner: {esc(items[0].owner_role)}</p>{rows}</div>')
    return f'<p class="sec-lede soft">The same plan by department, so each owner can see their part. Each line shows the estimated period for this move.</p><div class="timeline">{axis}{"".join(groups)}</div>'


def plain_terms() -> str:
    rows = "".join(f"<div><dt>{esc(term)}</dt><dd>{esc(meaning)}</dd></div>" for term, meaning in c.PLAIN_TERMS)
    return f'<dl class="terms">{rows}</dl>'


def closing(logo: str, answers: Answers) -> str:
    capacity = "" if "capacity" in answers.skipped else c.CLOSING_CAPACITY.get(answers.capacity, "")
    body = f"{capacity} {c.CLOSING_BODY}".strip()
    return (
        f'<section class="close" aria-labelledby="close-title"><img class="logo" src="{logo}" alt="{c.SITE_NAME}"><h2 id="close-title">{esc(c.CLOSING_TITLE)}</h2>'
        f'<p>{esc(body)}</p>'
        f'<div class="actions"><a class="button" href="mailto:{c.CONTACT_EMAIL}?subject={c.CONTACT_SUBJECT}">Email {c.CONTACT_EMAIL}</a>'
        f'<a href="{c.DEMO_URL}">{c.DEMO_TEXT}{c.DEMO_LABEL}</a></div></section>'
    )


def render_blueprint(answers: Answers, plan: Plan, library: Library, today: dt.date) -> str:
    kpi = library.kpis[answers.kpi]["label"]
    logo = data_uri(c.LOGO_PATH, "image/png")
    registry = [
        ("Recommendation", recommendation(plan)),
        ("Your next 30 days", next_30_days(plan, kpi)),
        ("Where you stand", position(answers, plan, library)),
        ("Speed against your KPI", priorities(plan, kpi)),
        ("Roadmap", roadmap(plan)),
        ("Roadmap by department", department_roadmap(plan)),
        ("Activity by activity", details_table(plan)),
        ("Leave with your people", people(plan)),
        ("In plain terms", plain_terms()),
        ("Public sources", public_sources(answers)),
        ("Notes", notes(answers, plan)),
    ]
    numbered = [(title, content) for title, content in registry if content]
    sections = "".join(section(number, title, content) for number, (title, content) in enumerate(numbered, start=1))
    body = opening(answers, plan, library, kpi) + sections + closing(logo, answers)
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>Fund Blueprint by {esc(c.SITE_NAME)}</title><style>{stylesheet()}</style></head><body><div class=\"page\">"
        f'<header class="letterhead"><img class="logo" src="{logo}" alt="{c.SITE_NAME}"><p>Fund Blueprint<br>{today.isoformat()}</p></header><main>{body}</main>'
        f"<footer>Created by {esc(c.SITE_NAME)} · {c.CONTACT_EMAIL} · Blueprint {c.VERSION}</footer></div>"
        "<script>addEventListener('beforeprint',function(){document.querySelectorAll('details').forEach(function(d){d.open=true})})</script></body></html>"
    )


def render_summary(answers: Answers, plan: Plan, library: Library) -> str:
    """Printed to the conversation, so the result survives any display failure."""
    kpi_label = library.kpis[answers.kpi]["label"]
    lines = [f"KPI: {kpi_label}", f"Reported hours a month: {hours_text(plan) if plan.hours_known else 'not answered'}", "", "| # | Activity | Id | Verdict | Speed, estimated | Impact, estimated |", "|---|---|---|---|---|---|"]
    for item in plan.items:
        speed = item.speed_label or "Not applicable"
        impact = effect_text(item.impact, item.effect_rated) if item.verdict != Verdict.LEAVE else "Not applicable"
        verdict = c.VERDICT_LABELS[item.verdict] + (c.AI_UNKNOWN_TABLE if item.ai_unknown else "")
        lines.append(f"| {item.number} | {item.label} | {item.activity_id} | {verdict} | {speed} | {impact} |")
    return "\n".join(lines)


def render_email(answers: Answers, plan: Plan, library: Library) -> str:
    """Closed answers and the firm's name if they gave it. No other typed text, so nothing confidential leaks in."""
    catalog_top = [item.label for item in plan.top if not item.custom]
    lines = [
        f"To: {c.CONTACT_EMAIL}",
        f"Subject: {c.CONTACT_SUBJECT_TEXT}",
        "",
        f"Hello {c.SITE_NAME},",
        "",
        "We completed the Fund Blueprint and would like to talk about implementation.",
        "",
        *([f"Firm: {answers.firm_name}"] if answers.firm_name else []),
        *([f"Strategy: {library.option_label('strategy', answers.strategy)}"] if told(answers, "strategy") else []),
        *([f"AUM: {library.option_label('aum', answers.aum)}"] if told(answers, "aum") else []),
        *([f"AI today: {library.option_label('ai_stage', answers.ai_stage)}"] if told(answers, "ai_stage") else []),
        *([f"Priority: {library.option_label('pressure', answers.pressure)}"] if told(answers, "pressure") else []),
        f"KPI: {library.kpis[answers.kpi]['label']}",
        *(["Top priorities: " + "; ".join(catalog_top)] if catalog_top else []),
        "",
        "Thank you",
    ]
    return "\n".join(lines)
