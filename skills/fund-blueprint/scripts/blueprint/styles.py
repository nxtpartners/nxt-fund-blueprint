"""The report's stylesheet. Colours, fonts, and sizes come from tokens.py."""
from __future__ import annotations

import base64

from . import constants as c
from . import tokens as t


def data_uri(path, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def font_faces() -> str:
    faces = []
    for family, weight, path in c.FONT_FILES:
        faces.append(
            f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:normal;font-display:swap;"
            f"src:url({data_uri(path, 'font/woff2')}) format('woff2');}}"
        )
    return "".join(faces)


def stylesheet() -> str:
    return font_faces() + f"""
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:{t.COLOR_SURFACE};color:{t.COLOR_INK};font-family:{t.FONT_BODY};font-size:{t.TEXT_BODY};line-height:1.55;font-feature-settings:'kern'}}
.page{{max-width:{t.PAGE_MAX_WIDTH};margin-inline:auto;padding-inline:{t.SPACE_PAGE};container-type:inline-size}}
h1,h2,h3{{margin:0;font-weight:700;text-wrap:balance}}
p,li,dd{{text-wrap:pretty}}
p,ol,ul,dl,dd{{margin:0;padding:0}}
ol,ul{{list-style:none}}
a{{color:{t.COLOR_ACCENT}}}
a:focus-visible,summary:focus-visible,.mark:focus-visible{{outline:2px solid {t.COLOR_ACCENT};outline-offset:2px}}
.soft{{color:{t.COLOR_INK_SOFT}}}
.small{{font-size:{t.TEXT_SMALL}}}
.num{{font-family:{t.FONT_MONO};font-size:.92em;color:{t.COLOR_INK_SOFT}}}
.vh{{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}}
.pno{{display:block;justify-self:start;align-self:center;width:{t.BADGE_SIZE};height:{t.BADGE_SIZE};flex:none;print-color-adjust:exact;-webkit-print-color-adjust:exact}}
.pno.badge-lg{{width:{t.BADGE_SIZE_LARGE};height:{t.BADGE_SIZE_LARGE}}}
.badge{{display:block;width:100%;height:100%;overflow:visible;font-family:{t.FONT_BODY}}}
.letterhead{{display:flex;flex-wrap:wrap;gap:1rem;align-items:flex-end;justify-content:space-between;padding-block:{t.SPACE_BLOCK} .9rem;border-bottom:{t.RULE_HEAVY}}}
.logo{{height:{t.LOGO_HEIGHT};width:auto;display:block}}
.logo-link{{display:block;width:fit-content}}
.logo-link:focus-visible{{outline:2px solid {t.COLOR_ACCENT};outline-offset:4px}}
.letterhead p{{font-family:{t.FONT_MONO};font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT};text-align:end;line-height:1.4}}
.opening{{padding-block:{t.SPACE_SECTION} {t.SPACE_BLOCK}}}
@container (min-width:{t.RAIL_BREAKPOINT}){{.opening{{margin-inline-start:calc({t.SECTION_RAIL} + {t.SPACE_GAP})}}}}
h1{{font-family:{t.FONT_DISPLAY};font-size:{t.TEXT_HEADLINE};line-height:1.12;letter-spacing:-.018em}}
.standfirst{{margin-top:1rem;font-size:{t.TEXT_ITEM};line-height:1.45}}
.reading{{margin-top:.4rem}}
.reading li{{border-top:{t.RULE_LIGHT};padding-block:.5rem}}
.reading li:last-child{{border-bottom:{t.RULE_LIGHT}}}
.reading-title{{font-weight:600;margin-top:{t.SPACE_BLOCK}}}
.top-strip{{margin-top:1.1rem;border-top:1px solid {t.COLOR_INK}}}
.top-strip li{{border-bottom:{t.RULE_LIGHT}}}
.top-strip a{{display:grid;grid-template-columns:{t.BADGE_COLUMN} minmax(0,1fr);column-gap:.3rem;align-items:center;padding-block:.55rem;min-height:{t.MIN_TARGET};color:inherit;text-decoration:none}}
.top-strip a:hover .name{{text-decoration:underline;text-underline-offset:.15em}}
.top-strip .meta{{grid-column:2;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
@container (min-width:{t.RAIL_BREAKPOINT}){{.top-strip a{{grid-template-columns:{t.BADGE_COLUMN} minmax(0,1fr) auto;column-gap:.75rem}}.top-strip .meta{{grid-column:3;text-align:end}}}}
.moves li{{scroll-margin-top:{t.SPACE_BLOCK}}}
.start{{margin-top:1rem;font-size:{t.TEXT_ITEM};font-weight:600}}
.link-table{{width:100%;border-collapse:collapse;font-size:{t.TEXT_SMALL}}}
.link-table th{{text-align:start;font-weight:400;color:{t.COLOR_INK_SOFT};padding-block:.3rem;border-bottom:1px solid {t.COLOR_INK}}}
.link-table td{{padding:.45rem .75rem .45rem 0;border-bottom:{t.RULE_LIGHT};vertical-align:top}}
.link-table th[scope=row]{{font-weight:600;color:{t.COLOR_INK};border-bottom:{t.RULE_LIGHT};padding:.45rem .75rem .45rem 0}}
.plot-y{{font-weight:600;line-height:1.3;margin:0 0 .6rem}}
.plot-note{{margin:0 0 .9rem}}
@container (min-width:{t.RAIL_BREAKPOINT}){{.opening~.ledger>div{{grid-template-columns:{t.SECTION_RAIL} 1fr!important;column-gap:{t.SPACE_GAP}!important}}}}
.ledger>div{{display:grid;grid-template-columns:minmax(5.5rem,24%) 1fr;gap:.25rem 1rem;padding-block:.5rem;border-top:{t.RULE_LIGHT}}}
.ledger>div:last-child{{border-bottom:{t.RULE_LIGHT}}}
.ledger dt{{color:{t.COLOR_INK_SOFT};font-size:{t.TEXT_SMALL};padding-top:.12em}}
.sec{{border-top:{t.RULE_HEAVY};padding-block:{t.SPACE_BLOCK} {t.SPACE_SECTION}}}
.sec-head{{display:flex;gap:.7rem;align-items:baseline;margin-bottom:{t.SPACE_BLOCK}}}
h2{{font-family:{t.FONT_DISPLAY};font-size:{t.TEXT_SECTION};line-height:1.2;letter-spacing:-.005em}}
.sec-lede{{margin-bottom:{t.SPACE_BLOCK}}}
@container (min-width:{t.RAIL_BREAKPOINT}){{.sec{{display:grid;grid-template-columns:{t.SECTION_RAIL} minmax(0,1fr);column-gap:{t.SPACE_GAP}}}.sec-head{{margin-bottom:0;padding-inline-end:1rem}}}}
.moves{{display:grid;gap:{t.SPACE_BLOCK}}}
.moves li{{border-top:1px solid {t.COLOR_INK};padding-top:.6rem;display:grid;gap:.5rem}}
.moves .body{{display:grid;gap:.5rem;align-content:start}}
@container (min-width:{t.RAIL_BREAKPOINT}){{.moves li{{grid-template-columns:minmax(0,1fr) {t.FACTS_RAIL};column-gap:{t.SPACE_GAP}}}.moves .head{{grid-column:1 / -1}}.moves .facts{{border-top:0;padding-top:.15rem}}}}
.moves .head{{display:flex;align-items:center;gap:.7rem}}
.sec-no{{font-family:{t.FONT_MONO};font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
h3{{font-family:{t.FONT_BODY};font-weight:600;font-size:{t.TEXT_ITEM};line-height:1.3}}
.lead{{font-weight:600}}
.facts{{padding-top:.6rem;border-top:{t.RULE_LIGHT};align-content:start;font-size:{t.TEXT_SMALL};display:grid;gap:.55rem}}
.facts dt{{color:{t.COLOR_INK_SOFT}}}
.facts dd{{color:{t.COLOR_INK};line-height:1.4}}
.list>li{{padding-block:.7rem;border-top:{t.RULE_LIGHT}}}
.list>li:last-child{{border-bottom:{t.RULE_LIGHT}}}
.subhead{{font-family:{t.FONT_BODY};font-weight:600;font-size:{t.TEXT_BODY};margin-block:{t.SPACE_BLOCK} .5rem}}
.key-mark{{display:inline-block;width:.68em;height:.68em;border-radius:50%;margin-inline-end:.45em;border:2px solid currentColor;vertical-align:baseline;flex:none}}
.plot{{width:100%;height:auto;display:block;font-family:{t.FONT_BODY};max-width:50rem}}
.mark{{outline:none;cursor:default}}
.mark:hover circle,.mark:focus-visible circle{{stroke-width:3}}
.plot-narrow{{display:none;max-width:{t.PLOT_NARROW_MAX}}}
@container (max-width:{t.PLOT_NARROW_BREAKPOINT}){{.plot-wide{{display:none}}.plot-narrow{{display:block}}}}
.spacer{{height:{t.SPACE_SECTION}}}
.flush{{margin:0}}
.gap-top{{margin-top:.7rem}}
.legend li{{display:grid;grid-template-columns:1.2em 1fr}}
.legend .key-mark{{margin-top:.38em}}
.legend{{display:flex;flex-wrap:wrap;gap:.3rem 1.2rem;margin-top:.9rem;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
.legend b{{color:{t.COLOR_INK};font-weight:600}}
.legend+.legend{{margin-top:.3rem}}
.views{{position:relative;display:flex;flex-wrap:wrap;justify-content:center;align-items:center;row-gap:.5rem;margin-top:{t.SPACE_BLOCK}}}
@container (max-width:{t.LAYOUT_BREAKPOINT}){{.view-tab{{flex:1 1 0;min-width:0;padding-inline:.5rem}}}}
.view-radio{{position:absolute;top:0;left:0;width:1px;height:1px;opacity:0;margin:0}}
.view-tab{{display:inline-flex;align-items:center;justify-content:center;min-height:{t.MIN_TARGET};min-width:min(11rem,40vw);padding-inline:1rem;font-weight:600;color:{t.COLOR_INK_SOFT};background:{t.COLOR_SURFACE};border:1px solid {t.COLOR_INK};cursor:pointer}}
.views>label:first-of-type{{border-radius:{t.RADIUS_BUTTON} 0 0 {t.RADIUS_BUTTON}}}
.views>label:last-of-type{{border-radius:0 {t.RADIUS_BUTTON} {t.RADIUS_BUTTON} 0;border-left:0}}
.view-tab:hover{{color:{t.COLOR_INK};text-decoration:underline;text-underline-offset:.2em}}
.view-radio:checked+.view-tab{{background:{t.COLOR_INK};color:{t.COLOR_SURFACE};text-decoration:none;cursor:default}}
.view-radio:focus-visible+.view-tab{{outline:2px solid {t.COLOR_ACCENT};outline-offset:2px}}
.view{{flex:0 0 100%;min-width:0;margin-top:{t.SPACE_BLOCK};border-top:{t.RULE_LIGHT};padding-top:{t.SPACE_BLOCK}}}
.view-open{{display:none}}
#view-open:checked~.view-budget{{display:none}}
#view-open:checked~.view-open{{display:block}}
.view-print{{display:none}}
.view-note{{margin:0 0 {t.SPACE_BLOCK}}}
@media print{{.view-tab,.view-radio{{display:none}}.view-print{{display:block;margin:0 0 {t.SPACE_BLOCK}}}}}
.shape-mark{{width:.72em;height:.72em;fill:none;stroke:currentColor;stroke-width:1.6;display:inline-block;vertical-align:-.02em}}
.legend .shape-mark{{margin-top:.38em}}
.plot-key{{columns:2 16rem;column-gap:{t.SPACE_GAP};margin-top:{t.SPACE_BLOCK};font-size:{t.TEXT_SMALL}}}
.plot-key li{{break-inside:avoid;display:grid;grid-template-columns:{t.BADGE_COLUMN} 1fr;align-items:center;padding-block:.18rem}}
.note{{margin-top:.75rem;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
.stages{{display:grid;grid-template-columns:repeat(auto-fit,minmax({t.COLUMN_MIN},1fr));gap:{t.SPACE_BLOCK} {t.SPACE_GAP}}}
.stages>div{{border-top:1px solid {t.COLOR_INK};padding-top:.6rem}}
.stages small{{display:block;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
.stages ul{{margin-top:.7rem;display:grid;gap:.55rem}}
.stages li{{display:grid;grid-template-columns:{t.BADGE_COLUMN} 1fr;align-items:start;line-height:1.35}}
.stages .pno{{align-self:start;margin-top:-.25em}}
.table-head,summary{{display:grid;grid-template-columns:.9rem {t.BADGE_COLUMN} minmax(11rem,1fr) 10.5rem 7.5rem 7rem;gap:.15rem .6rem;align-items:center}}
.table-head{{font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT};padding-bottom:.4rem;border-bottom:1px solid {t.COLOR_INK}}}
@container (max-width:{t.RAIL_BREAKPOINT}){{.table-head{{display:none}}summary{{grid-template-columns:.9rem {t.BADGE_COLUMN} 1fr}}summary .col{{grid-column:3;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}summary .toggle,summary .pno,summary .num{{grid-row:1}}}}
.group{{margin-top:{t.SPACE_BLOCK}}}
.group h3{{font-size:{t.TEXT_BODY}}}
.group>p{{font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT};margin-bottom:.4rem}}
.rows{{border-bottom:{t.RULE_LIGHT}}}
details{{border-top:{t.RULE_LIGHT}}}
summary{{cursor:pointer;list-style:none;padding-block:.6rem;min-height:{t.MIN_TARGET}}}
summary::-webkit-details-marker{{display:none}}
summary:hover .name{{text-decoration:underline;text-underline-offset:.15em}}
.name{{font-weight:600;line-height:1.3}}
.toggle{{justify-self:center;align-self:center;width:.5em;height:.5em;border-right:2px solid {t.COLOR_INK_SOFT};border-bottom:2px solid {t.COLOR_INK_SOFT};transform:rotate(-45deg);transition:transform .15s ease-out}}
details[open] .toggle{{transform:rotate(45deg)}}
@media (prefers-reduced-motion:reduce){{.toggle{{transition:none}}}}
.row-body{{padding:.1rem 0 1rem calc(2.1rem + {t.BADGE_COLUMN});display:grid;gap:.6rem}}
.row-body dt{{font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
.row-body dl{{display:grid;gap:.55rem}}
.notes{{counter-reset:note;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT};display:grid;gap:.45rem}}
.notes li{{counter-increment:note;display:grid;grid-template-columns:1.6em 1fr}}
.notes li::before{{content:counter(note);font-family:{t.FONT_MONO}}}
.actions-list>li{{display:grid;grid-template-columns:2em minmax(0,1fr);gap:.1rem .25rem;padding-block:.7rem;border-top:{t.RULE_LIGHT}}}
.actions-list>li:last-child{{border-bottom:{t.RULE_LIGHT}}}
.actions-list .owner{{grid-column:2;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
@container (min-width:{t.RAIL_BREAKPOINT}){{.actions-list>li{{grid-template-columns:2em minmax(0,1fr) 13rem;column-gap:1rem}}.actions-list .owner{{grid-column:3;text-align:end;padding-top:.15em}}}}
.tl-axis,.tl-row{{display:grid;grid-template-columns:minmax(0,1fr);gap:.2rem}}
@container (min-width:{t.LAYOUT_BREAKPOINT}){{.tl-axis,.tl-row{{grid-template-columns:minmax(14rem,2fr) minmax(0,3fr);column-gap:1.25rem;align-items:center}}}}
.tl-scale{{position:relative;height:1.3em;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
.tl-scale span{{position:absolute;transform:translateX(-50%);white-space:nowrap}}
.tl-scale span:first-child{{transform:none}}
.tl-scale span:last-child{{transform:translateX(-100%)}}
.tl-axis{{padding-bottom:.35rem;border-bottom:1px solid {t.COLOR_INK}}}
.tl-group{{padding-block:.85rem .5rem;border-bottom:{t.RULE_LIGHT}}}
.tl-group h3{{font-size:{t.TEXT_BODY}}}
.tl-group .owner{{font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT};margin-bottom:.35rem}}
.tl-row{{padding-block:.32rem}}
.tl-label{{display:grid;grid-template-columns:{t.BADGE_COLUMN} minmax(0,1fr);align-items:start;line-height:1.3}}
.tl-track{{position:relative;height:1.1rem;background-image:linear-gradient(to right,{t.COLOR_LINE} 1px,transparent 1px);background-size:25% 100%;border-right:1px solid {t.COLOR_LINE}}}
.tl-bar{{position:absolute;left:0;top:50%;height:2px;transform:translateY(-50%)}}
.tl-dot{{position:absolute;top:50%;width:.8rem;height:.8rem;border-radius:50%;border:2px solid;transform:translate(-50%,-50%)}}
.terms>div{{display:grid;grid-template-columns:minmax(0,1fr);gap:.1rem;padding-block:.6rem;border-top:{t.RULE_LIGHT}}}
.terms>div:last-child{{border-bottom:{t.RULE_LIGHT}}}
.terms dt{{font-weight:600}}
@container (min-width:{t.LAYOUT_BREAKPOINT}){{.terms>div{{grid-template-columns:11rem minmax(0,1fr);column-gap:1rem}}}}
.close{{border-top:{t.RULE_HEAVY};padding-block:{t.SPACE_SECTION};display:grid;gap:1rem;justify-items:start}}
.close-body{{display:grid;gap:1rem;justify-items:start}}
@container (min-width:{t.RAIL_BREAKPOINT}){{.close{{grid-template-columns:{t.SECTION_RAIL} minmax(0,1fr);column-gap:{t.SPACE_GAP};align-items:start}}.close h2{{margin-top:0}}}}
.close h2{{font-size:{t.TEXT_SECTION};line-height:1.2;margin-top:.5rem}}
.actions{{display:flex;flex-wrap:wrap;gap:.75rem 1.25rem;align-items:center;margin-top:.4rem}}
.button{{display:inline-flex;align-items:center;min-height:{t.MIN_TARGET};padding:.55rem 1.15rem;background:{t.COLOR_ACCENT};color:{t.COLOR_SURFACE};border-radius:{t.RADIUS_BUTTON};font-weight:600;text-decoration:none}}
.button:hover{{background:{t.COLOR_ACCENT_HOVER}}}
footer{{border-top:{t.RULE_LIGHT};padding-block:1rem 2rem;text-align:center;font-family:{t.FONT_MONO};font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
@media print{{.toggle{{display:none}}.button{{background:none;color:{t.COLOR_ACCENT};padding:0;min-height:0}}.sec{{display:block;break-inside:auto}}.stages>div,figure{{break-inside:avoid}}.key-mark,.tl-bar,.tl-dot,.tl-track{{print-color-adjust:exact;-webkit-print-color-adjust:exact}}.sec-head,.group h3,.group>p,.tl-group h3,.subhead,.sec-lede{{break-after:avoid}}.row-body,.row-body dl{{display:block}}.row-body dl>div{{break-inside:avoid;margin-bottom:.55rem}}.plot-wide{{display:block!important}}.plot-narrow{{display:none!important}}.moves li,.moves .body,.moves .meta{{display:block}}.moves .body>*{{margin-bottom:.5rem}}.moves .meta{{break-inside:avoid;margin-top:.5rem}}.tl-row,.close{{break-inside:avoid}}.moves .meta span:not(:last-child)::after{{content:" · "}}.tl-axis{{break-inside:avoid;break-after:avoid}}.moves{{display:block}}.moves li{{margin-bottom:1.2rem}}.moves .head{{break-after:avoid}}footer{{break-before:avoid}}}}
"""


