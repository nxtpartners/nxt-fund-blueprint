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
h1,h2,h3{{margin:0;font-weight:700}}
p,ol,ul,dl,dd{{margin:0;padding:0}}
ol,ul{{list-style:none}}
a{{color:{t.COLOR_ACCENT}}}
a:focus-visible,summary:focus-visible,.mark:focus-visible{{outline:2px solid {t.COLOR_ACCENT};outline-offset:2px}}
.soft{{color:{t.COLOR_INK_SOFT}}}
.small{{font-size:{t.TEXT_SMALL}}}
.mono{{font-family:{t.FONT_MONO};font-size:.92em}}
.letterhead{{display:flex;flex-wrap:wrap;gap:1rem;align-items:flex-end;justify-content:space-between;padding-block:{t.SPACE_BLOCK} .9rem;border-bottom:{t.RULE_HEAVY}}}
.logo{{height:{t.LOGO_HEIGHT};width:auto;display:block}}
.letterhead p{{font-family:{t.FONT_MONO};font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT};text-align:end;line-height:1.4}}
.opening{{padding-block:{t.SPACE_SECTION} {t.SPACE_BLOCK}}}
h1{{font-family:{t.FONT_DISPLAY};font-size:{t.TEXT_HEADLINE};line-height:1.12;letter-spacing:-.018em;max-width:26ch}}
.standfirst{{margin-top:1rem;max-width:58ch;font-size:{t.TEXT_ITEM};line-height:1.45}}
.reading{{max-width:66ch;margin-top:.4rem}}
.reading li{{border-top:{t.RULE_LIGHT};padding-block:.5rem}}
.reading li:last-child{{border-bottom:{t.RULE_LIGHT}}}
.reading-title{{font-weight:600;margin-top:{t.SPACE_BLOCK}}}
.start{{margin-top:1rem;font-size:{t.TEXT_ITEM};font-weight:600;max-width:58ch}}
.link-table{{width:100%;border-collapse:collapse;font-size:{t.TEXT_SMALL}}}
.link-table th{{text-align:start;font-weight:400;color:{t.COLOR_INK_SOFT};padding-block:.3rem;border-bottom:1px solid {t.COLOR_INK}}}
.link-table td{{padding:.45rem .75rem .45rem 0;border-bottom:{t.RULE_LIGHT};vertical-align:top}}
.link-table th[scope=row]{{font-weight:600;color:{t.COLOR_INK};border-bottom:{t.RULE_LIGHT};padding:.45rem .75rem .45rem 0}}
.plot-y{{font-weight:600;line-height:1.3;margin:0 0 .6rem;max-width:44ch}}
.plot-note{{margin:0 0 .9rem;max-width:60ch}}
@container (min-width:{t.RAIL_BREAKPOINT}){{.opening~.ledger>div{{grid-template-columns:{t.SECTION_RAIL} 1fr!important;column-gap:{t.SPACE_GAP}!important}}}}
.ledger>div{{display:grid;grid-template-columns:minmax(5.5rem,24%) 1fr;gap:.25rem 1rem;padding-block:.5rem;border-top:{t.RULE_LIGHT}}}
.ledger>div:last-child{{border-bottom:{t.RULE_LIGHT}}}
.ledger dt{{color:{t.COLOR_INK_SOFT};font-size:{t.TEXT_SMALL};padding-top:.12em}}
.sec{{border-top:{t.RULE_HEAVY};padding-block:{t.SPACE_BLOCK} {t.SPACE_SECTION}}}
.sec-head{{display:flex;gap:.7rem;align-items:baseline;margin-bottom:{t.SPACE_BLOCK}}}
.sec-no{{font-family:{t.FONT_MONO};font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
h2{{font-family:{t.FONT_DISPLAY};font-size:{t.TEXT_SECTION};line-height:1.2;letter-spacing:-.005em}}
.sec-lede{{max-width:62ch;margin-bottom:{t.SPACE_BLOCK}}}
@container (min-width:{t.RAIL_BREAKPOINT}){{.sec{{display:grid;grid-template-columns:{t.SECTION_RAIL} minmax(0,1fr);column-gap:{t.SPACE_GAP}}}.sec-head{{margin-bottom:0;padding-inline-end:1rem}}}}
.moves{{display:grid;gap:{t.SPACE_BLOCK}}}
.moves li{{border-top:1px solid {t.COLOR_INK};padding-top:.6rem;display:grid;gap:.5rem}}
.moves .body{{display:grid;gap:.5rem;max-width:62ch}}
@container (min-width:{t.RAIL_BREAKPOINT}){{.moves li{{grid-template-columns:minmax(0,1fr) 13rem;column-gap:{t.SPACE_GAP}}}.moves .head{{grid-column:1 / -1}}.moves .meta{{border-top:0;padding-top:0}}}}
.moves .no{{font-family:{t.FONT_MONO};font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
h3{{font-family:{t.FONT_BODY};font-weight:600;font-size:{t.TEXT_ITEM};line-height:1.3}}
.lead{{font-weight:600}}
.moves .meta{{padding-top:.5rem;border-top:{t.RULE_LIGHT};align-content:start;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT};display:grid;gap:.1rem}}
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
.views{{position:relative;display:flex;flex-wrap:wrap;column-gap:.35rem;align-items:flex-end;margin-top:{t.SPACE_BLOCK}}}
.view-radio{{position:absolute;top:0;left:0;width:1px;height:1px;opacity:0;margin:0}}
.view-tab{{position:relative;display:inline-flex;align-items:center;min-height:2.75rem;padding-inline:clamp(.6rem,2.5vw,1.1rem);font-weight:600;color:{t.COLOR_INK_SOFT};background:{t.COLOR_TAB_IDLE};border:1px solid {t.COLOR_LINE_STRONG};border-bottom:0;cursor:pointer}}
.view-tab:hover{{color:{t.COLOR_INK}}}
.view-radio:checked+.view-tab{{color:{t.COLOR_INK};background:{t.COLOR_SURFACE};border-color:{t.COLOR_INK};border-top-width:3px;z-index:1;margin-bottom:-1px}}
.view-radio:focus-visible+.view-tab{{outline:2px solid {t.COLOR_ACCENT};outline-offset:2px}}
.view{{flex:0 0 100%;min-width:0;border-top:1px solid {t.COLOR_INK};padding-top:{t.SPACE_BLOCK}}}
.view-open{{display:none}}
#view-open:checked~.view-budget{{display:none}}
#view-open:checked~.view-open{{display:block}}
.view-print{{display:none}}
.view-note{{margin:0 0 {t.SPACE_BLOCK}}}
@media print{{.view-tab,.view-radio{{display:none}}.view-print{{display:block;margin:0 0 {t.SPACE_BLOCK}}}}}
.shape-mark{{width:.72em;height:.72em;fill:none;stroke:currentColor;stroke-width:1.6;display:inline-block;vertical-align:-.02em}}
.legend .shape-mark{{margin-top:.38em}}
.plot-key{{columns:2 16rem;column-gap:{t.SPACE_GAP};margin-top:{t.SPACE_BLOCK};font-size:{t.TEXT_SMALL}}}
.plot-key li{{break-inside:avoid;display:grid;grid-template-columns:2em 1fr;padding-block:.18rem}}
.note{{margin-top:.75rem;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT};max-width:68ch}}
.stages{{display:grid;grid-template-columns:repeat(auto-fit,minmax({t.COLUMN_MIN},1fr));gap:{t.SPACE_BLOCK} {t.SPACE_GAP}}}
.stages>div{{border-top:1px solid {t.COLOR_INK};padding-top:.6rem}}
.stages small{{display:block;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
.stages ul{{margin-top:.7rem;display:grid;gap:.55rem}}
.stages li{{display:grid;grid-template-columns:2em 1fr;line-height:1.35}}
.table-head,summary{{display:grid;grid-template-columns:2rem minmax(11rem,1fr) 10.5rem 7.5rem 7rem 1.2rem;gap:.15rem .75rem;align-items:baseline}}
.table-head{{font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT};padding-bottom:.4rem;border-bottom:1px solid {t.COLOR_INK}}}
@container (max-width:{t.RAIL_BREAKPOINT}){{.table-head{{display:none}}summary{{grid-template-columns:2rem 1fr 1.2rem}}summary .col{{grid-column:2;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}summary .toggle{{grid-column:3;grid-row:1}}}}
.group{{margin-top:{t.SPACE_BLOCK}}}
.group h3{{font-size:{t.TEXT_BODY}}}
.group>p{{font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT};margin-bottom:.4rem}}
.rows{{border-bottom:{t.RULE_LIGHT}}}
details{{border-top:{t.RULE_LIGHT}}}
summary{{cursor:pointer;list-style:none;padding-block:.6rem;min-height:{t.MIN_TARGET}}}
summary::-webkit-details-marker{{display:none}}
summary:hover .name{{text-decoration:underline;text-underline-offset:.15em}}
.name{{font-weight:600;line-height:1.3}}
.toggle{{font-family:{t.FONT_MONO};color:{t.COLOR_INK_SOFT};text-align:end}}
.toggle::before{{content:'+'}}
details[open] .toggle::before{{content:'\\2212'}}
.row-body{{padding:.1rem 0 1rem 2.75em;display:grid;gap:.6rem;max-width:60rem}}
.row-body dt{{font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
.row-body dl{{display:grid;gap:.55rem}}
.notes{{counter-reset:note;font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT};display:grid;gap:.45rem;max-width:68ch}}
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
.tl-label{{display:grid;grid-template-columns:2em minmax(0,1fr);line-height:1.3}}
.tl-track{{position:relative;height:1.1rem;background-image:linear-gradient(to right,{t.COLOR_LINE} 1px,transparent 1px);background-size:25% 100%;border-right:1px solid {t.COLOR_LINE}}}
.tl-bar{{position:absolute;left:0;top:50%;height:2px;transform:translateY(-50%)}}
.tl-dot{{position:absolute;top:50%;width:.8rem;height:.8rem;border-radius:50%;border:2px solid;transform:translate(-50%,-50%)}}
.terms>div{{display:grid;grid-template-columns:minmax(0,1fr);gap:.1rem;padding-block:.6rem;border-top:{t.RULE_LIGHT}}}
.terms>div:last-child{{border-bottom:{t.RULE_LIGHT}}}
.terms dt{{font-weight:600}}
@container (min-width:{t.LAYOUT_BREAKPOINT}){{.terms>div{{grid-template-columns:11rem minmax(0,1fr);column-gap:1rem}}}}
.close{{border-top:{t.RULE_HEAVY};padding-block:{t.SPACE_SECTION};display:grid;gap:1rem;justify-items:start}}
.close h2{{font-size:{t.TEXT_SECTION};line-height:1.2;margin-top:.5rem}}
.close p{{max-width:54ch}}
.actions{{display:flex;flex-wrap:wrap;gap:.75rem 1.25rem;align-items:center;margin-top:.4rem}}
.button{{display:inline-flex;align-items:center;min-height:{t.MIN_TARGET};padding:.55rem 1.15rem;background:{t.COLOR_ACCENT};color:{t.COLOR_SURFACE};border-radius:{t.RADIUS_BUTTON};font-weight:600;text-decoration:none}}
.button:hover{{background:{t.COLOR_ACCENT_HOVER}}}
footer{{border-top:{t.RULE_LIGHT};padding-block:1rem 2rem;font-family:{t.FONT_MONO};font-size:{t.TEXT_SMALL};color:{t.COLOR_INK_SOFT}}}
@media print{{.toggle{{display:none}}.button{{background:none;color:{t.COLOR_ACCENT};padding:0;min-height:0}}.sec{{display:block;break-inside:auto}}.stages>div,figure{{break-inside:avoid}}.key-mark,.tl-bar,.tl-dot,.tl-track{{print-color-adjust:exact;-webkit-print-color-adjust:exact}}.sec-head,.group h3,.group>p,.tl-group h3,.subhead,.sec-lede{{break-after:avoid}}.row-body,.row-body dl{{display:block}}.row-body dl>div{{break-inside:avoid;margin-bottom:.55rem}}.plot-wide{{display:block!important}}.plot-narrow{{display:none!important}}.moves li,.moves .body,.moves .meta{{display:block}}.moves .body>*{{margin-bottom:.5rem}}.moves .meta{{break-inside:avoid;margin-top:.5rem}}.tl-row,.close{{break-inside:avoid}}.moves .meta span:not(:last-child)::after{{content:" · "}}.tl-axis{{break-inside:avoid;break-after:avoid}}.moves{{display:block}}.moves li{{margin-bottom:1.2rem}}.moves .head{{break-after:avoid}}footer{{break-before:avoid}}}}
"""


