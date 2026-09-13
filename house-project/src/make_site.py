# -*- coding: utf-8 -*-
"""Сборка одностраничного HTML-альбома проекта (site/index.html) — для публикации как артефакт."""
import os, re, json, base64, html
from model import *
import calcs

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D = os.path.join(BASE, "drawings")
R = calcs.run_all()
S = summary()
with open(os.path.join(BASE, "calc", "boq.json"), encoding="utf-8") as f:
    BOQ = json.load(f)
with open(os.path.join(BASE, "3d", "model.js"), encoding="utf-8") as f:
    MODEL_JS = f.read()

SHEETS = {
    "site": [("ГП-1", "Генплан участка 20×30 м", "1:200", "ГП-1_Генплан.svg")],
    "plans": [("АР-1", "План 1-го этажа на отм. 0,000", "1:50", "АР-1_План_1_этажа.svg"),
              ("АР-2", "План 2-го этажа на отм. +3,300", "1:50", "АР-2_План_2_этажа.svg"),
              ("АР-3", "План кровли", "1:100", "АР-3_План_кровли.svg")],
    "facades": [("АР-4", "Фасады 3-1 (улица) и 1-3 (сад)", "1:100", "АР-4_Фасады_3-1_1-3.svg"),
                ("АР-5", "Фасады А-Б (запад) и Б-А (восток)", "1:100", "АР-5_Фасады_А-Б_Б-А.svg"),
                ("АР-6", "Разрезы 1-1 и 2-2", "1:50", "АР-6_Разрезы.svg")],
    "structure": [("КР-1", "Фундаментная плита, сечение цоколя", "1:100, 1:20", "КР-1_Фундаментная_плита.svg"),
                  ("КР-2", "Армирование перекрытий, балка Б-1, перемычки", "1:100, 1:20", "КР-2_Перекрытие_перемычки.svg"),
                  ("КР-3", "Стропильная система", "1:100, 1:50", "КР-3_Стропильная_система.svg"),
                  ("КР-4", "Узлы", "1:20", "КР-4_Узлы.svg")],
    "engineering": [("ОВ-1", "Отопление и вентиляция, 1-й этаж", "1:50", "ОВ-1_Отопление_вентиляция_1_этаж.svg"),
                    ("ОВ-2", "Отопление и вентиляция, 2-й этаж", "1:50", "ОВ-2_Отопление_вентиляция_2_этаж.svg"),
                    ("ОВ-3", "Схема котельной", "б/м", "ОВ-3_Схема_котельной.svg"),
                    ("ВК-1", "Водоснабжение и канализация, 1-й этаж", "1:50", "ВК-1_Водоснабжение_канализация_1_этаж.svg"),
                    ("ВК-2", "Водоснабжение и канализация, 2-й этаж", "1:50", "ВК-2_Водоснабжение_канализация_2_этаж.svg"),
                    ("ВК-3", "Принципиальные схемы ВК", "б/м", "ВК-3_Принципиальные_схемы.svg"),
                    ("ЭО-1", "Электрооборудование, 1-й этаж", "1:50", "ЭО-1_Электрооборудование_1_этаж.svg"),
                    ("ЭО-2", "Электрооборудование, 2-й этаж", "1:50", "ЭО-2_Электрооборудование_2_этаж.svg"),
                    ("ЭО-3", "Однолинейная схема", "б/м", "ЭО-3_Однолинейная_схема.svg")],
    "cost": [("ГР-1", "Календарный график (диаграмма Ганта)", "б/м", "ГР-1_Календарный_график.svg")],
}
RENDERS = [("01_вид_с_северо-востока.png", "Вид с северо-востока (улица, въезд)"), ("02_вид_со_стороны_сада.png", "Вид со стороны сада (юго-запад)"),
           ("03_вид_с_улицы.png", "Северный фасад с улицы"), ("04_план_2_этажа_3D.png", "2-й этаж без кровли"),
           ("05_план_1_этажа_3D.png", "1-й этаж без перекрытия"), ("06_интерьер_1_этаж.png", "Гостиная — вид в сторону кухни")]


def svg_inline(fname, idx):
    with open(os.path.join(D, fname), encoding="utf-8") as f:
        s = f.read()
    # уникализируем id паттернов/маркеров, чтобы не конфликтовали между листами
    s = re.sub(r'id="([A-Za-z]+)"', lambda m: f'id="{m.group(1)}_{idx}"', s)
    s = re.sub(r'url\(#([A-Za-z]+)\)', lambda m: f'url(#{m.group(1)}_{idx})', s)
    s = re.sub(r'<svg ([^>]*?)width="[\d.]+" height="[\d.]+"', r'<svg \1', s, count=1)
    s = s.replace("<svg ", '<svg class="sheet-svg" preserveAspectRatio="xMidYMid meet" ', 1)
    return s


def md_to_html(text):
    lines = text.split("\n")
    out = []
    i = 0
    in_list = None
    para = []

    def inline(t):
        t = html.escape(t, quote=False)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
        return t

    def flush_para():
        nonlocal para
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1].strip()):
            flush_para(); close_list()
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            numeric = [all(re.match(r"^[\d\s,.%−–\-+×/]*$", r[c]) and re.search(r"\d", r[c]) for r in rows if c < len(r) and r[c]) for c in range(len(head))]
            out.append('<div class="tbl"><table><thead><tr>' + "".join(f"<th{' class=num' if numeric[c] else ''}>{inline(h)}</th>" for c, h in enumerate(head)) + "</tr></thead><tbody>")
            for r in rows:
                out.append("<tr>" + "".join(f"<td{' class=num' if c < len(numeric) and numeric[c] else ''}>{inline(x)}</td>" for c, x in enumerate(r)) + "</tr>")
            out.append("</tbody></table></div>")
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", ln)
        if m:
            flush_para(); close_list()
            lvl = len(m.group(1)) + 1
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
        elif ln.startswith(">"):
            flush_para(); close_list()
            out.append(f"<blockquote>{inline(ln[1:].strip())}</blockquote>")
        elif re.match(r"^\s*[-•]\s+", ln):
            flush_para()
            if in_list != "ul":
                close_list(); out.append("<ul>"); in_list = "ul"
            item = re.sub(r"^\s*[-•]\s+", "", ln)
            out.append(f"<li>{inline(item)}</li>")
        elif re.match(r"^\s*\d+\.\s+", ln):
            flush_para()
            if in_list != "ol":
                close_list(); out.append("<ol>"); in_list = "ol"
            item = re.sub(r"^\s*\d+\.\s+", "", ln)
            out.append(f"<li>{inline(item)}</li>")
        elif ln.strip() == "":
            flush_para(); close_list()
        else:
            if in_list and ln.startswith("  "):
                out[-1] = out[-1][:-5] + " " + inline(ln.strip()) + "</li>"
            else:
                close_list()
                para.append(ln.strip())
        i += 1
    flush_para(); close_list()
    return "\n".join(out)


def doc_html(name):
    with open(os.path.join(BASE, "docs", name), encoding="utf-8") as f:
        return md_to_html(f.read())


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def sheet_block(code, title, scale, fname, idx):
    return f'''
<figure class="sheet" id="sheet-{code}">
  <figcaption class="sheet-head">
    <span class="chip">{code}</span>
    <span class="sheet-title">{html.escape(title)}</span>
    <span class="sheet-scale">М {scale}</span>
    <button class="zoom" type="button" data-zoom="{code}" aria-label="Открыть лист {code} крупно">увеличить ⤢</button>
  </figcaption>
  <div class="sheet-body">{svg_inline(fname, idx)}</div>
</figure>'''


def build_page():
    H, T, L, F = R["heating"], R["thermal"], R["loads"], R["foundation"]
    total = BOQ["total"]
    idx = 0
    sheets_html = {}
    for key, lst in SHEETS.items():
        parts = []
        for code, title, scale, fname in lst:
            idx += 1
            parts.append(sheet_block(code, title, scale, fname, idx))
        sheets_html[key] = "\n".join(parts)
    renders_html = "".join(
        f'<figure class="render"><img src="data:image/png;base64,{b64(os.path.join(BASE, "renders", fn))}" alt="{html.escape(cap)}" loading="lazy"><figcaption>{html.escape(cap)}</figcaption></figure>'
        for fn, cap in RENDERS)
    rooms_tbl = ""
    for fl in (1, 2):
        rows = "".join(f"<tr><td>{r['n']}</td><td>{html.escape(r['name'])}</td><td class=num>{room_area(r):.2f}</td></tr>".replace(".", ",") if False else
                       f"<tr><td>{r['n']}</td><td>{html.escape(r['name'])}</td><td class=num>{f'{room_area(r):.2f}'.replace('.', ',')}</td></tr>" for r in ROOMS[fl])
        rooms_tbl += f'<div class="tbl"><table><caption>{fl}-й этаж — {f"{floor_area(fl):.2f}".replace(".", ",")} м²</caption><thead><tr><th>№</th><th>Помещение</th><th class=num>м²</th></tr></thead><tbody>{rows}</tbody></table></div>'
    tep = [
        ("Пятно застройки", "13,0 × 16,0 м — 208 м²"),
        ("Площадь по наружному обмеру, 2 этажа", f"{S['building_area_gross']:.0f} м²"),
        ("Общая площадь помещений", f"{S['area_total']:.1f} м²".replace(".", ",")),
        ("1-й / 2-й этаж", f"{S['area_floor1']:.1f} / {S['area_floor2']:.1f} м²".replace(".", ",")),
        ("Спален / санузлов", "4 (+ кабинет) / 4"),
        ("Высота этажа / до конька", "3,0 м в чистоте / +10,650"),
        ("Остекление", f"{S['windows']:.1f} м², {sum(len(WINDOWS[f]) for f in (1,2))} окон".replace(".", ",")),
        ("Участок", "6 соток, 20 × 30 м; отступы 5,0 / 3,5 / 9,0 м"),
        ("Тепловая нагрузка", f"{H['Q_total']:.1f} кВт ({H['Q_total']*1000/S['area_total']:.0f} Вт/м²)".replace(".", ",")),
        ("Котёл / отопление", "конденсационный 32 кВт, тёплый пол везде"),
        ("Давление на грунт", f"{F['p_n']:.0f} кПа при R₀ = 200 кПа"),
        ("Ориентировочная стоимость", f"{total/1e6:.1f} млн ₽ ({total/S['area_total']/1000:.0f} тыс. ₽/м²)".replace(".", ",")),
    ]
    tep_html = "".join(f'<div class="kv"><dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd></div>' for k, v in tep)
    nav = [("overview", "00", "Титул и обзор"), ("site", "ГП", "Генплан"), ("plans", "АР", "Планы"), ("facades", "АР", "Фасады и разрезы"),
           ("viewer3d", "3D", "3D-модель"), ("structure", "КР", "Конструкции и расчёты"), ("engineering", "ИОС", "Инженерные системы"),
           ("cost", "СМ", "Смета и график"), ("questions", "ТЗ", "ТЗ, ПЗ и вопросы")]
    nav_html = "".join(f'<a href="#{k}" data-sec="{k}"><span class="code">{c}</span><span>{t}</span></a>' for k, c, t in nav)
    sec_sum = BOQ["sections"]
    cost_bars = "".join(
        f'<div class="bar"><span class="bar-label">{html.escape(k)}</span><span class="bar-track"><span class="bar-fill" style="width:{v / max(sec_sum.values()) * 100:.1f}%"></span></span><span class="bar-val">{v/1e6:.2f}</span></div>'.replace(f"{v/1e6:.2f}", f"{v/1e6:.2f}".replace(".", ","))
        for k, v in sec_sum.items())

    page = f'''<title>Дом 13×16 на шести сотках</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root {{
  --paper: #f3f4f1; --paper-2: #e9ebe6; --ink: #1f2426; --ink-2: #4a5156; --muted: #7d858b; --rule: #cfd4d0;
  --anth: #3c3f42; --anth-2: #2f3235; --wood: #c08a45; --wood-2: #a5733a; --blue: #2f5d8a; --blue-soft: #dfe8f1;
  --sheet-bg: #ffffff; --shadow: 0 1px 2px rgba(31,36,38,.08), 0 8px 24px rgba(31,36,38,.08);
  --ok: #2f7d4a; --warn: #b8741a;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper: #1b1f22; --paper-2: #23282c; --ink: #e8e6e0; --ink-2: #c4c1b9; --muted: #8f969c; --rule: #3a4045;
    --anth: #2a2f33; --anth-2: #16191c; --wood: #d9a35e; --wood-2: #e2b578; --blue: #7fa7cf; --blue-soft: #253340;
    --sheet-bg: #f6f6f4; --shadow: 0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.35);
  }}
}}
:root[data-theme="dark"] {{
  --paper: #1b1f22; --paper-2: #23282c; --ink: #e8e6e0; --ink-2: #c4c1b9; --muted: #8f969c; --rule: #3a4045;
  --anth: #2a2f33; --anth-2: #16191c; --wood: #d9a35e; --wood-2: #e2b578; --blue: #7fa7cf; --blue-soft: #253340;
  --sheet-bg: #f6f6f4; --shadow: 0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.35);
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} * {{ transition: none !important; }} }}
body {{ margin: 0; background: var(--paper); color: var(--ink); font-family: 'IBM Plex Sans', 'Segoe UI', Roboto, Arial, sans-serif; font-size: 15px; line-height: 1.55; }}
a {{ color: var(--blue); }}
code {{ font-family: 'IBM Plex Mono', Consolas, monospace; font-size: .92em; background: var(--paper-2); padding: 0 .3em; border-radius: 3px; }}
.app {{ display: grid; grid-template-columns: 250px 1fr; min-height: 100vh; }}
.spine {{ background: var(--anth); color: #e8e6e0; padding-block: 22px; padding-inline: 18px; position: sticky; top: 0; height: 100vh; overflow-y: auto; }}
.spine .brand {{ font-family: Oswald, 'Roboto Condensed', Arial, sans-serif; font-weight: 500; font-size: 20px; letter-spacing: .02em; text-transform: uppercase; line-height: 1.15; margin: 0 0 4px; }}
.spine .stage {{ font-family: 'IBM Plex Mono', monospace; font-size: 11.5px; color: #b9bdc0; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 22px; }}
.spine nav {{ display: flex; flex-direction: column; gap: 2px; }}
.spine nav a {{ display: grid; grid-template-columns: 38px 1fr; align-items: center; gap: 8px; color: #d8d6cf; text-decoration: none; padding: 8px 8px; border-radius: 6px; font-size: 13.5px; border-left: 2px solid transparent; }}
.spine nav a .code {{ font-family: Oswald, sans-serif; font-weight: 500; font-size: 13px; letter-spacing: .06em; color: #9aa0a5; }}
.spine nav a:hover {{ background: rgba(255,255,255,.06); }}
.spine nav a.active {{ background: rgba(255,255,255,.09); border-left-color: var(--wood); color: #fff; }}
.spine nav a.active .code {{ color: var(--wood); }}
.spine nav a:focus-visible, button:focus-visible {{ outline: 2px solid var(--wood); outline-offset: 2px; }}
.spine .foot {{ margin-top: 26px; font-size: 11.5px; color: #9aa0a5; line-height: 1.5; }}
.spine .foot b {{ color: #d8d6cf; font-weight: 500; }}
main {{ padding-block: 28px 60px; padding-inline: 32px; min-width: 0; }}
section {{ display: none; max-width: 1240px; }}
section.active {{ display: block; }}
.eyebrow {{ font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 0 0 6px; }}
h1 {{ font-family: Oswald, 'Roboto Condensed', Arial, sans-serif; font-weight: 500; font-size: clamp(30px, 4vw, 44px); line-height: 1.05; letter-spacing: .005em; margin: 0 0 10px; text-wrap: balance; }}
h2 {{ font-family: Oswald, 'Roboto Condensed', Arial, sans-serif; font-weight: 500; font-size: 26px; line-height: 1.15; margin: 30px 0 12px; text-wrap: balance; }}
h3 {{ font-family: Oswald, sans-serif; font-weight: 500; font-size: 20px; margin: 22px 0 8px; }}
h4 {{ font-size: 15px; font-weight: 600; margin: 18px 0 6px; }}
p {{ max-width: 72ch; margin: 0 0 12px; }}
.lead {{ font-size: 17px; color: var(--ink-2); max-width: 70ch; }}
blockquote {{ margin: 12px 0; padding: 10px 14px; border-left: 3px solid var(--wood); background: var(--paper-2); color: var(--ink-2); max-width: 80ch; font-size: 14px; }}
ul, ol {{ max-width: 80ch; padding-left: 22px; }}
li {{ margin: 3px 0; }}
.doc {{ max-width: 1000px; }}
.doc h2 {{ font-size: 22px; padding-top: 10px; border-top: 1px solid var(--rule); }}
.tbl {{ overflow-x: auto; margin: 12px 0 18px; }}
table {{ border-collapse: collapse; font-size: 13.5px; min-width: 320px; }}
caption {{ text-align: left; font-family: Oswald, sans-serif; font-size: 15px; font-weight: 500; padding: 6px 0; }}
th, td {{ border-bottom: 1px solid var(--rule); padding: 5px 9px; text-align: left; vertical-align: top; }}
th {{ font-weight: 600; font-size: 12.5px; letter-spacing: .02em; color: var(--ink-2); background: var(--paper-2); }}
td.num, th.num {{ text-align: right; font-family: 'IBM Plex Mono', monospace; font-variant-numeric: tabular-nums; white-space: nowrap; }}
tbody tr:hover {{ background: var(--paper-2); }}
.tep {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 0 28px; margin: 18px 0 8px; padding: 0; border-top: 1px solid var(--ink); }}
.kv {{ display: grid; grid-template-columns: 1fr auto; gap: 12px; padding: 8px 0; border-bottom: 1px solid var(--rule); margin: 0; align-items: baseline; }}
.kv dt {{ color: var(--ink-2); font-size: 13.5px; }}
.kv dd {{ margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 13.5px; font-variant-numeric: tabular-nums; text-align: right; }}
.renders {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin: 16px 0; }}
.render {{ margin: 0; }}
.render img {{ width: 100%; height: auto; display: block; border: 1px solid var(--rule); border-radius: 4px; background: #dfe8f0; }}
.render figcaption {{ font-size: 13px; color: var(--muted); margin-top: 6px; }}
.sheet {{ margin: 22px 0 34px; }}
.sheet-head {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 10px 14px; margin-bottom: 8px; }}
.chip {{ font-family: Oswald, sans-serif; font-weight: 500; letter-spacing: .06em; background: var(--anth); color: #fff; padding: 2px 9px; border-radius: 3px; font-size: 13px; }}
.sheet-title {{ font-family: Oswald, sans-serif; font-size: 19px; font-weight: 500; }}
.sheet-scale {{ font-family: 'IBM Plex Mono', monospace; font-size: 12.5px; color: var(--muted); }}
.zoom {{ margin-left: auto; font: 500 12.5px 'IBM Plex Sans', sans-serif; color: var(--blue); background: none; border: 1px solid var(--rule); border-radius: 4px; padding: 4px 10px; cursor: pointer; }}
.zoom:hover {{ border-color: var(--blue); }}
.sheet-body {{ background: var(--sheet-bg); box-shadow: var(--shadow); border-radius: 3px; overflow: hidden; }}
.sheet-svg {{ width: 100%; height: auto; display: block; }}
.lightbox {{ position: fixed; inset: 0; background: rgba(20,22,24,.92); z-index: 50; display: none; overflow: auto; padding: 24px; }}
.lightbox.open {{ display: block; }}
.lightbox .close {{ position: fixed; top: 14px; right: 18px; z-index: 51; font: 500 14px 'IBM Plex Sans', sans-serif; background: var(--wood); color: #1f2426; border: 0; border-radius: 4px; padding: 8px 14px; cursor: pointer; }}
.lightbox .hint {{ position: fixed; top: 18px; left: 24px; color: #d8d6cf; font-size: 13px; }}
.lightbox .inner {{ width: 2400px; max-width: none; margin: 40px auto 0; background: #fff; }}
.lightbox .inner svg {{ width: 100%; height: auto; display: block; }}
.grid2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px 32px; }}
.viewer {{ position: relative; width: 100%; aspect-ratio: 16/10; max-height: 640px; background: #dfe8f0; border-radius: 4px; overflow: hidden; border: 1px solid var(--rule); }}
.viewer canvas {{ width: 100%; height: 100%; display: block; }}
.viewer .vui {{ position: absolute; left: 10px; top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }}
.viewer .vui button, .viewer .vui label {{ font: 500 12.5px 'IBM Plex Sans', sans-serif; background: rgba(255,255,255,.92); color: #1f2426; border: 1px solid #c9ced3; border-radius: 4px; padding: 5px 9px; cursor: pointer; }}
.viewer .vui label {{ display: inline-flex; align-items: center; gap: 5px; }}
.viewer .nogl {{ position: absolute; inset: 0; display: none; align-items: center; justify-content: center; color: #1f2426; padding: 20px; text-align: center; }}
.cost {{ display: grid; grid-template-columns: minmax(0, 1fr); gap: 4px; max-width: 760px; margin: 12px 0 20px; }}
.bar {{ display: grid; grid-template-columns: 240px 1fr 60px; align-items: center; gap: 10px; font-size: 13px; }}
.bar-track {{ height: 14px; background: var(--paper-2); border-radius: 2px; overflow: hidden; }}
.bar-fill {{ display: block; height: 100%; background: var(--blue); }}
.bar-val {{ font-family: 'IBM Plex Mono', monospace; text-align: right; font-variant-numeric: tabular-nums; }}
.bar-label {{ color: var(--ink-2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.total {{ font-family: Oswald, sans-serif; font-size: 30px; font-weight: 500; margin: 6px 0 2px; }}
.total small {{ font-family: 'IBM Plex Sans', sans-serif; font-size: 14px; color: var(--muted); font-weight: 400; margin-left: 10px; }}
.note {{ font-size: 13px; color: var(--muted); }}
details {{ margin: 10px 0; border: 1px solid var(--rule); border-radius: 4px; padding: 6px 14px; max-width: 1000px; }}
summary {{ cursor: pointer; font-family: Oswald, sans-serif; font-size: 17px; font-weight: 500; padding: 6px 0; }}
.assump {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 10px 24px; padding: 0; margin: 10px 0 0; list-style: none; max-width: 1100px; }}
.assump li {{ padding: 8px 0 8px 12px; border-left: 2px solid var(--wood); font-size: 14px; }}
.assump b {{ font-weight: 600; }}
.topbar {{ display: none; }}
@media (max-width: 900px) {{
  .app {{ grid-template-columns: 1fr; }}
  .spine {{ position: static; height: auto; padding-block: 14px; }}
  .spine nav {{ flex-direction: row; overflow-x: auto; gap: 4px; padding-bottom: 4px; }}
  .spine nav a {{ grid-template-columns: auto; white-space: nowrap; border-left: 0; border-bottom: 2px solid transparent; border-radius: 4px 4px 0 0; }}
  .spine nav a .code {{ display: none; }}
  .spine nav a.active {{ border-bottom-color: var(--wood); }}
  .spine .foot {{ display: none; }}
  main {{ padding-inline: 16px; }}
  .bar {{ grid-template-columns: 1fr 50px; }}
  .bar-track {{ grid-column: 1 / -1; }}
  .lightbox .inner {{ width: 1600px; }}
}}
</style>

<div class="app">
<aside class="spine">
  <div class="brand">Дом 13×16<br>на шести сотках</div>
  <div class="stage">Эскизный проект · стадия ЭП · 09.2026</div>
  <nav>{nav_html}</nav>
  <div class="foot"><b>20 листов</b> чертежей, расчёты КР/ОВ/ВК/ЭО, 3D-модель, смета и график.<br><br>Проект параметрический: геометрия в <code>src/model.py</code>, всё остальное генерируется скриптами.<br><br>Не для строительства: требуются изыскания и рабочая документация.</div>
</aside>
<main>

<section id="overview" class="active">
  <p class="eyebrow">Индивидуальный жилой дом · 2 этажа + холодный чердак · участок 20 × 30 м</p>
  <h1>Двухэтажный дом ≈ 400 м² на шести сотках</h1>
  <p class="lead">Компактный объём 13 × 16 м с двускатной кровлей, гаражом, террасой к саду и четырьмя спальнями. Пакет включает генплан, архитектуру, конструктив с расчётами, инженерные системы, 3D-модель, ведомость объёмов со стоимостью и календарный график — всё сгенерировано из одной параметрической модели.</p>
  <h2>Технико-экономические показатели</h2>
  <dl class="tep">{tep_html}</dl>
  <p class="note">Общая площадь помещений считается по внутренним граням стен (Приказ Минстроя 393/пр); «≈ 400 м²» — по наружному обмеру двух этажей. Стоимость — ориентир ±20 % для Московской области, уровень цен 2025–2026.</p>
  <h2>Визуализации</h2>
  <div class="renders">{renders_html}</div>
  <h2>Что принято без уточнения у заказчика</h2>
  <ul class="assump">
    <li><b>Регион — Московская область</b>: −25 °С, снег III (1,5 кПа), ветер I. Для сейсмичных районов конструктив другой.</li>
    <li><b>Грунт — суглинок, R₀ = 200 кПа, УГВ 2,5 м</b>: отсюда плитный фундамент. Нужны изыскания.</li>
    <li><b>Участок 20 × 30 м, улица с севера</b>: жилые комнаты и терраса смотрят на юг.</li>
    <li><b>Семья 2 + 3 детей</b>: 4 спальни, кабинет-гостевая, 4 санузла.</li>
    <li><b>Гараж на 1 машину в доме</b> + 2 места на площадке: экономия пятна на маленьком участке.</li>
    <li><b>Сети: газ есть, воды и канализации нет</b>: скважина, водоподготовка, станция биоочистки, 15 кВт.</li>
    <li><b>Материалы</b>: газобетон D400 400 мм, монолитные перекрытия, фальцевая кровля, ПВХ-окна.</li>
    <li><b>Отопление</b>: конденсационный котёл 32 кВт, водяной тёплый пол во всех помещениях.</li>
  </ul>
  <p style="margin-top:14px">Полный список — в разделе «ТЗ, ПЗ и вопросы». Модель параметрическая, большинство ответов меняет проект за одну пересборку.</p>
</section>

<section id="site">
  <p class="eyebrow">Раздел ГП · схема планировочной организации участка</p>
  <h1>Генплан</h1>
  <p class="lead">Дом посажен с отступом 5 м от красной линии и 3,5 м от боковых границ; южные 9 м участка остаются под сад и террасу. Скважина и станция очистки разнесены на 30 м, въезд и стоянка на 2 машины — у улицы.</p>
  {sheets_html["site"]}
</section>

<section id="plans">
  <p class="eyebrow">Раздел АР · планы этажей и кровли</p>
  <h1>Планы</h1>
  <p class="lead">Несущая схема — две наружные продольные стены и центральная стена по оси 2, пролёты 6,3 м. Входная и техническая группа с гаражом — у улицы, гостиная 43,6 м² и кухня-столовая 30,2 м² — у сада, с порталами на террасу.</p>
  <div class="grid2">{rooms_tbl}</div>
  {sheets_html["plans"]}
</section>

<section id="facades">
  <p class="eyebrow">Раздел АР · фасады, разрезы, отделка</p>
  <h1>Фасады и разрезы</h1>
  <p class="lead">Светлая штукатурка по газобетону, фронтоны в планкене из лиственницы, кровля и окна — антрацит RAL 7016. Разрез 1-1 проходит по лестнице, разрез 2-2 — по холлу и гостиной.</p>
  {sheets_html["facades"]}
</section>

<section id="viewer3d">
  <p class="eyebrow">3D · параметрическая модель (three.js)</p>
  <h1>3D-модель</h1>
  <p class="lead">Модель собрана из тех же данных, что и чертежи. Вращение — левая кнопка мыши, панорама — правая, зум — колесо. Кровлю и второй этаж можно скрыть, чтобы посмотреть планировку.</p>
  <div class="viewer" id="viewer">
    <canvas id="c3d"></canvas>
    <div class="vui">
      <button type="button" data-v="ne">С северо-востока</button><button type="button" data-v="sw">Со стороны сада</button><button type="button" data-v="n">С улицы</button><button type="button" data-v="top">Сверху</button><button type="button" data-v="int1">Интерьер</button>
      <label><input type="checkbox" id="chk-roof" checked> кровля</label><label><input type="checkbox" id="chk-fl2" checked> 2-й этаж</label><label><input type="checkbox" id="chk-site" checked> участок</label>
    </div>
    <div class="nogl" id="nogl">Интерактивная модель недоступна в этом окружении (нет WebGL или не загрузилась библиотека three.js). Ниже — статичные виды.</div>
  </div>
  <h2>Статичные виды</h2>
  <div class="renders">{renders_html}</div>
</section>

<section id="structure">
  <p class="eyebrow">Раздел КР · конструктивные решения и расчёты</p>
  <h1>Конструкции и расчёты</h1>
  <p class="lead">Плита 300 мм с рёбрами на подушке ПГС и ЭППС, стены из газобетона, монолитные перекрытия 200 мм, наслонные стропила. Ниже — чертежи и полный расчётный отчёт: сбор нагрузок, основание, плита, перекрытие, балка над проёмом, перемычки, стены, стропила.</p>
  {sheets_html["structure"]}
  <details open><summary>Расчётная записка КР (сбор нагрузок, фундамент, перекрытия, балка Б-1, перемычки, стены, кровля)</summary><div class="doc">{doc_html("03_КР_Конструктивные_решения_расчёты.md")}</div></details>
</section>

<section id="engineering">
  <p class="eyebrow">Разделы ОВ · ВК · ЭО · ГСВ</p>
  <h1>Инженерные системы</h1>
  <p class="lead">Тепловая нагрузка {f"{H['Q_total']:.1f}".replace('.', ',')} кВт, конденсационный котёл 32 кВт, тёплый пол (≈ {H['pipe_total']:.0f} м трубы, {H['loops_1'] + H['loops_2']} петель), естественная вентиляция с опцией рекуперации, скважина и станция биоочистки, 15 кВт электричества на {R['electrical']['groups']} групп.</p>
  {sheets_html["engineering"]}
  <details><summary>Теплотехника, теплопотери, отопление и вентиляция — расчётная записка ОВ</summary><div class="doc">{doc_html("04_ОВ_Отопление_вентиляция_теплотехника.md")}</div></details>
  <details><summary>Водоснабжение, канализация, электроснабжение, газ — записка ВК/ЭО/ГСВ</summary><div class="doc">{doc_html("05_ВК_ЭО_ГСВ_Инженерные_сети.md")}</div></details>
</section>

<section id="cost">
  <p class="eyebrow">Ведомость объёмов · ориентировочная стоимость · график</p>
  <h1>Смета и график</h1>
  <div class="total">{total/1e6:.1f} млн ₽<small>≈ {total/S['area_total']/1000:.0f} тыс. ₽/м² общей площади · {total/S['building_area_gross']/1000:.0f} тыс. ₽/м² по наружному обмеру · ±20 %</small></div>
  <p class="note">Материалы + работа, без НДС и прибыли генподрядчика, включая 8 % непредвиденных. Уровень цен Московской области 2025–2026, требует проверки по коммерческим предложениям.</p>
  <div class="cost">{cost_bars}</div>
  <p class="note">Столбцы — млн ₽ по разделам ведомости.</p>
  {sheets_html["cost"]}
  <details><summary>Ведомость объёмов работ и стоимость по позициям</summary><div class="doc">{doc_html("06_Ведомость_объёмов_и_смета.md")}</div></details>
  <details><summary>Календарный график по этапам и контрольные точки</summary><div class="doc">{doc_html("07_Календарный_график.md")}</div></details>
</section>

<section id="questions">
  <p class="eyebrow">Исходные данные · пояснительная записка · открытые вопросы</p>
  <h1>ТЗ, пояснительная записка и вопросы</h1>
  <p class="lead">Проект выполнен под допущения; ответы на вопросы ниже позволят выпустить следующую итерацию. Помеченное «ПРИНЯТО» — решения проектировщика, а не заказчика.</p>
  <details open><summary>Вопросы заказчику и принятые допущения</summary><div class="doc">{doc_html("08_Вопросы_заказчику.md")}</div></details>
  <details><summary>Техническое задание (восстановленное)</summary><div class="doc">{doc_html("00_ТЗ_Техническое_задание.md")}</div></details>
  <details><summary>Пояснительная записка</summary><div class="doc">{doc_html("01_Пояснительная_записка.md")}</div></details>
  <details><summary>Ведомости АР: экспликация, спецификация проёмов, состав конструкций, отделка</summary><div class="doc">{doc_html("02_АР_Ведомости_и_спецификации.md")}</div></details>
</section>

</main>
</div>
<div class="lightbox" id="lightbox" role="dialog" aria-label="Лист крупно"><div class="hint">Прокрутка — перемещение по листу</div><button class="close" type="button" id="lb-close">Закрыть ✕</button><div class="inner" id="lb-inner"></div></div>

<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/controls/OrbitControls.js"></script>
<script>
{MODEL_JS}
</script>
<script>
(function() {{
  const links = document.querySelectorAll('.spine nav a');
  const sections = document.querySelectorAll('main > section');
  function show(id) {{
    if (!document.getElementById(id)) id = 'overview';
    sections.forEach(s => s.classList.toggle('active', s.id === id));
    links.forEach(a => a.classList.toggle('active', a.dataset.sec === id));
    if (id === 'viewer3d') init3D();
    window.scrollTo({{ top: 0 }});
  }}
  links.forEach(a => a.addEventListener('click', e => {{ e.preventDefault(); history.replaceState(null, '', '#' + a.dataset.sec); show(a.dataset.sec); }}));
  show((location.hash || '#overview').slice(1));
  // lightbox
  const lb = document.getElementById('lightbox'), inner = document.getElementById('lb-inner');
  document.querySelectorAll('.zoom').forEach(b => b.addEventListener('click', () => {{
    const svg = document.querySelector('#sheet-' + CSS.escape(b.dataset.zoom) + ' svg');
    inner.innerHTML = ''; inner.appendChild(svg.cloneNode(true)); lb.classList.add('open'); lb.scrollTop = 0;
  }}));
  document.getElementById('lb-close').addEventListener('click', () => lb.classList.remove('open'));
  lb.addEventListener('click', e => {{ if (e.target === lb) lb.classList.remove('open'); }});
  document.addEventListener('keydown', e => {{ if (e.key === 'Escape') lb.classList.remove('open'); }});

  // 3D
  let started = false;
  function init3D() {{
    if (started) return; started = true;
    const M = window.HOUSE_MODEL;
    const canvas = document.getElementById('c3d');
    if (!window.THREE || !THREE.OrbitControls) {{ document.getElementById('nogl').style.display = 'flex'; return; }}
    let renderer;
    try {{ renderer = new THREE.WebGLRenderer({{ canvas, antialias: true }}); }} catch (e) {{ document.getElementById('nogl').style.display = 'flex'; return; }}
    renderer.setPixelRatio(window.devicePixelRatio || 1);
    renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    const scene = new THREE.Scene(); scene.background = new THREE.Color(0xdfe8f0); scene.fog = new THREE.Fog(0xdfe8f0, 60, 140);
    const camera = new THREE.PerspectiveCamera(45, 2, 0.1, 500);
    const controls = new THREE.OrbitControls(camera, canvas); controls.target.set(6.3, 2.5, 7.8);
    const mk = (c, o) => new THREE.MeshStandardMaterial(Object.assign({{ color: c, roughness: 0.9 }}, o || {{}}));
    const mats = {{ wall: mk(0xf2efe8), wall_int: mk(0xf7f5f0), plinth: mk(0x5b5550), wood: mk(0xc99a5b, {{ roughness: .8 }}), slab: mk(0xcfcfcf),
      roof: mk(0x3c3f42, {{ roughness: .6, metalness: .3 }}), roof_dark: mk(0x2b2e31, {{ roughness: .6, metalness: .4 }}),
      glass: mk(0x8fb8d8, {{ roughness: .1, metalness: .6, transparent: true, opacity: .85 }}), door: mk(0x4a4e52, {{ roughness: .7 }}), garage: mk(0x8a8d90, {{ roughness: .7 }}),
      paving: mk(0xb8b4ac, {{ roughness: 1 }}), asphalt: mk(0x8c8c8c, {{ roughness: 1 }}), concrete: mk(0xc9c9c9, {{ roughness: 1 }}), fence: mk(0x6b6f72, {{ roughness: .8 }}),
      stair: mk(0xd9d4cc), grass: mk(0x7fb069, {{ roughness: 1 }}), trunk: mk(0x6b4a2a, {{ roughness: 1 }}), crown: mk(0x4f8f3f, {{ roughness: 1 }}), car: mk(0x3a5fa0, {{ roughness: .4, metalness: .5 }}) }};
    const groups = {{ roof: new THREE.Group(), fl2: new THREE.Group(), site: new THREE.Group(), base: new THREE.Group() }};
    Object.values(groups).forEach(g => scene.add(g));
    function addBox(it, group, mat) {{
      const w = it.x[1] - it.x[0], d = it.y[1] - it.y[0], h = it.z[1] - it.z[0];
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat || mats[it.m]);
      m.position.set((it.x[0] + it.x[1]) / 2, (it.z[0] + it.z[1]) / 2, (it.y[0] + it.y[1]) / 2);
      m.castShadow = true; m.receiveShadow = true; group.add(m);
    }}
    function addExtrude(pts, y1, y2, mat, group) {{
      const shape = new THREE.Shape(); pts.forEach((p, i) => i === 0 ? shape.moveTo(p[0], p[1]) : shape.lineTo(p[0], p[1])); shape.closePath();
      const m = new THREE.Mesh(new THREE.ExtrudeGeometry(shape, {{ depth: y2 - y1, bevelEnabled: false }}), mat);
      m.position.z = y1; m.castShadow = true; m.receiveShadow = true; group.add(m);
    }}
    for (const it of M.items) {{
      let grp = groups.base;
      if (it.m === 'roof' || it.m === 'roof_dark' || (it.t === 'box' && it.z[0] >= 6.29 && it.m === 'slab') || it.t === 'gable') grp = groups.roof;
      else if (it.t === 'box' && it.z[0] >= 3.19 && it.z[0] < 6.29) grp = groups.fl2;
      if (it.t === 'box') addBox(it, grp); else addExtrude(it.pts, it.y, it.y2, mats[it.m], grp);
    }}
    const s = M.site;
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(s.x[1] - s.x[0], s.y[1] - s.y[0]), mats.grass);
    ground.rotation.x = -Math.PI / 2; ground.position.set((s.x[0] + s.x[1]) / 2, s.z, (s.y[0] + s.y[1]) / 2); ground.receiveShadow = true; groups.site.add(ground);
    const outer = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), mk(0x9fbf8a, {{ roughness: 1 }}));
    outer.rotation.x = -Math.PI / 2; outer.position.set(6.3, s.z - 0.02, 10); outer.receiveShadow = true; groups.site.add(outer);
    const road = new THREE.Mesh(new THREE.PlaneGeometry(60, 6), mats.asphalt); road.rotation.x = -Math.PI / 2; road.position.set(6.3, s.z + 0.005, s.y[0] - 3.5); groups.site.add(road);
    for (const it of M.site_items) addBox(it, groups.site);
    for (const it of M.fence) addBox(it, groups.site);
    for (const t of M.trees) {{
      const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.18, t.h * 0.45, 8), mats.trunk); trunk.position.set(t.x, s.z + t.h * 0.225, t.y); trunk.castShadow = true; groups.site.add(trunk);
      const crown = new THREE.Mesh(new THREE.SphereGeometry(t.r, 12, 10), mats.crown); crown.position.set(t.x, s.z + t.h * 0.45 + t.r * 0.8, t.y); crown.castShadow = true; groups.site.add(crown);
    }}
    for (const o of M.objs) {{ const c = new THREE.Mesh(new THREE.CylinderGeometry(o.r, o.r, o.h, 16), mats.concrete); c.position.set(o.x, s.z + o.h / 2, o.y); groups.site.add(c); }}
    for (const c of M.cars) {{
      const body = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.7, 4.4), mats.car); body.position.set(c.x, s.z + 0.55, c.y); body.castShadow = true; groups.site.add(body);
      const top = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.6, 2.2), mats.glass); top.position.set(c.x, s.z + 1.2, c.y - 0.1); groups.site.add(top);
    }}
    scene.add(new THREE.HemisphereLight(0xffffff, 0x88aa77, 0.7));
    const sun = new THREE.DirectionalLight(0xfff2dd, 1.4); sun.position.set(-20, 30, -25); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
    Object.assign(sun.shadow.camera, {{ left: -30, right: 30, top: 30, bottom: -30, near: 1, far: 120 }}); sun.target.position.set(6.3, 0, 7.8); scene.add(sun); scene.add(sun.target);
    const fill = new THREE.DirectionalLight(0xdde8ff, 0.4); fill.position.set(30, 20, 30); scene.add(fill);
    const views = {{ ne: [[30, 16, -16], [6.3, 3, 7.8]], sw: [[-16, 12, 32], [6.3, 3, 7.8]], n: [[6.3, 6, -30], [6.3, 3.5, 7.8]], top: [[6.3, 60, 10.5], [6.3, 0, 10.4]], int1: [[11.5, 1.6, 14.5], [2.0, 1.4, 11.0]] }};
    const chkRoof = document.getElementById('chk-roof'), chkFl2 = document.getElementById('chk-fl2'), chkSite = document.getElementById('chk-site');
    function setView(k) {{
      const [p, t] = views[k]; camera.position.set(...p); controls.target.set(...t); controls.update();
      if (k === 'int1') {{ groups.roof.visible = false; groups.fl2.visible = false; chkRoof.checked = false; chkFl2.checked = false; }}
    }}
    document.querySelectorAll('.vui button').forEach(b => b.addEventListener('click', () => setView(b.dataset.v)));
    chkRoof.addEventListener('change', e => groups.roof.visible = e.target.checked);
    chkFl2.addEventListener('change', e => groups.fl2.visible = e.target.checked);
    chkSite.addEventListener('change', e => groups.site.visible = e.target.checked);
    setView('ne');
    function loop() {{
      const w = canvas.clientWidth, h = canvas.clientHeight;
      if (w && h && (canvas.width !== Math.round(w * (window.devicePixelRatio || 1)) || canvas.height !== Math.round(h * (window.devicePixelRatio || 1)))) {{
        renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
      }}
      controls.update(); renderer.render(scene, camera); requestAnimationFrame(loop);
    }}
    loop();
  }}
}})();
</script>
'''
    return page


if __name__ == "__main__":
    out = os.path.join(BASE, "site")
    os.makedirs(out, exist_ok=True)
    page = build_page()
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("site ok", f"{len(page.encode('utf-8')) / 1e6:.1f} MB")
