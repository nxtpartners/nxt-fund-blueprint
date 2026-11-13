"""The roadmap: moves in waves, and the same plan by department."""
from __future__ import annotations

from .. import constants as c
from .. import tokens as t
from ..models import Plan, ScoredActivity
from ..plot import timeline_share
from ..text import join_words, lower_first
from .common import by_workstream, esc, plural, priority_no


def planning_line(plan: Plan) -> str:
    software = [item for item in plan.plotted if item.verdict in c.TECH_VERDICTS]
    if not software:
        return (
            "None of these priorities needs new software beyond what you already use, "
            "so they are process changes you could start soon."
        )
    within = sum(1 for item in software if item.weeks < c.WEEKS_NEXT)
    if len(software) == 1:
        timing = "could reach a first working version within 90 days" if within else "would take over 90 days"
        return c.PLANNING_LINE_ONE.format(timing=timing)
    count = plural(len(software), "priority")
    if within == 0:
        return f"Under our planning rules, the {count} that add software would each take over 90 days."
    share = f"each of the {count}" if within == len(software) else f"{within} of the {count}"
    return f"Under our planning rules, {share} that add software could reach a first working version within 90 days."


def wave_row(item: ScoredActivity) -> str:
    fit = " · " + esc(item.fit_note) if item.fit_note else ""
    return (
        f'<li>{priority_no(item)}<span>{esc(item.label)}<br>'
        f'<span class="small soft">{esc(c.VERDICT_LABELS[item.verdict])} · {esc(item.speed_label)}{fit}</span>'
        "</span></li>"
    )


def roadmap(plan: Plan, prefix: str = "") -> str:
    if not plan.plotted:
        return ""
    columns = []
    start = 0
    for index, (title, size) in enumerate(c.ROADMAP_WAVES):
        size = (max(plan.start_moves) + 1 if plan.start_moves else size) if index == 0 else size
        rows = plan.plotted[start:] if size is None else plan.plotted[start : start + size]
        if not rows:
            continue
        if len(rows) == 1:
            span = c.ROADMAP_WAVE_ONE.format(first=rows[0].number)
        else:
            pattern = c.ROADMAP_WAVE_PAIR if len(rows) == 2 else c.ROADMAP_WAVE_SPAN
            span = pattern.format(first=rows[0].number, last=rows[-1].number)
        body = "".join(wave_row(item) for item in rows)
        columns.append(f'<div><h3>{esc(title)}</h3><small>{esc(span)}</small><ul>{body}</ul></div>')
        start += len(rows)
    return (
        f'<p class="sec-lede soft">{esc(planning_line(plan))} Each estimate assumes the priority is worked on alone. '
        f'Running several at once takes longer.</p><div class="stages">{"".join(columns)}</div>{people_note(plan, prefix)}'
    )


def people_note(plan: Plan, prefix: str) -> str:
    """Work the firm selected that stays with people has no place on the roadmap, so say where it went."""
    if not plan.people:
        return ""
    count = len(plan.people)
    text = c.ROADMAP_PEOPLE_NOTE[1] if count == 1 else c.ROADMAP_PEOPLE_NOTE["many"].format(count=count)
    link = f'<a href="#{c.PEOPLE_ANCHOR.format(prefix=prefix)}">{esc(c.ROADMAP_PEOPLE_LINK)}</a>'
    return f'<p class="note gap-top">{esc(text)} {link}.</p>'


def timeline_row(badge: str, label: str, speed: str, share: float, color: str, hollow: bool) -> str:
    """One line of the timeline. The badge is markup already built, such as a priority number."""
    dot_fill = t.COLOR_SURFACE if hollow else color
    percent = f"{share * 100:.1f}%"
    return (
        f'<div class="tl-row"><div class="tl-label">{badge}'
        f'<span>{esc(label)}<br><span class="small soft">{esc(speed)}</span></span></div>'
        '<div class="tl-track" aria-hidden="true">'
        f'<span class="tl-bar" style="width:{percent};background:{color}"></span>'
        f'<span class="tl-dot" style="left:{percent};background:{dot_fill};border-color:{color}"></span></div></div>'
    )


def item_timeline_row(item: ScoredActivity) -> str:
    fit = f" · {item.fit_note}" if item.fit_note else ""
    speed = f"{c.VERDICT_LABELS[item.verdict]} · {item.speed_label}{fit}"
    color, hollow = t.VERDICT_COLORS[item.verdict], item.verdict in t.VERDICT_HOLLOW
    return timeline_row(priority_no(item), item.label, speed, timeline_share(item.weeks), color, hollow)


def department_roadmap(plan: Plan) -> str:
    if not plan.plotted:
        return ""
    last_mark = len(c.TIMELINE_MARKS) - 1
    marks = "".join(
        f'<span style="left:{index * 100 / last_mark:.0f}%">{esc(mark)}</span>'
        for index, mark in enumerate(c.TIMELINE_MARKS)
    )
    axis = (
        '<div class="tl-axis" aria-hidden="true"><span class="small soft">Project and suggested owner</span>'
        f'<div class="tl-scale">{marks}</div></div>'
    )
    groups = []
    if plan.foundations:
        titles = join_words([lower_first(title) for title, _, _ in plan.foundations[: c.NEXT_30_MAX_FOUNDATIONS]])
        groups.append(
            f'<div class="tl-group"><h3>{esc(c.FIRM_WIDE_LABEL)}</h3>'
            f'<p class="owner">Suggested owner: {esc(c.FIRM_WIDE_OWNER)}</p>'
            f"<p>{esc(c.FIRM_WIDE_SPEED)}: {esc(titles)}.</p></div>"
        )
    for label, items in by_workstream(plan.plotted).items():
        rows = "".join(item_timeline_row(item) for item in sorted(items, key=lambda row: (row.weeks, row.number)))
        groups.append(
            f'<div class="tl-group"><h3>{esc(label)}</h3>'
            f'<p class="owner">Suggested owner: {esc(items[0].owner_role)}</p>{rows}</div>'
        )
    return (
        '<p class="sec-lede soft">The same plan by department, so each owner can see their part. '
        "Each line shows the estimated time if started today and worked on alone. The scale is not even.</p>"
        f'<div class="timeline">{axis}{"".join(groups)}</div>'
    )
