# -*- coding: utf-8 -*-
"""Полная сборка проекта: чертежи (SVG+PNG), расчёты, документы, 3D (JSON/OBJ), рендеры, DXF, PDF-альбом, смета, сайт-артефакт.
Запуск: python3 build.py [--no-render] [--no-pdf]
  --no-render — без Playwright (PNG листов, 3D-рендеры); --no-pdf — без PDF-альбома (cairosvg + pypdf).
"""
import os, sys, subprocess, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(HERE)
sys.path.insert(0, HERE)
for d in ("drawings", "docs", "calc", "3d", "renders", "site", "dxf", "pdf"):
    os.makedirs(os.path.join(BASE, d), exist_ok=True)

import registry
from registry import SHEETS, TOTAL, number
import draw_site, draw_plans, draw_roof, draw_elev, draw_sections, calcs, calcs2, draw_struct, draw_eng, draw_extra, export3d, export_dxf, boq, docs_gen
from model import summary

D = os.path.join(BASE, "drawings")
FN = {s[0]: s[3] for s in SHEETS}
BUILDERS = {
    "ОД-1": lambda n: draw_extra.general_data_sheet(n, TOTAL),
    "ГП-1": lambda n: draw_site.site_sheet(n, TOTAL),
    "ВП-1": lambda n: draw_extra.vertical_sheet(n, TOTAL),
    "СГП-1": lambda n: draw_extra.construction_sheet(n, TOTAL),
    "АР-1": lambda n: draw_plans.floor_plan_sheet(1, n, TOTAL),
    "АР-2": lambda n: draw_plans.floor_plan_sheet(2, n, TOTAL),
    "АР-3": lambda n: draw_roof.roof_sheet(n, TOTAL),
    "АР-4": lambda n: draw_elev.elev_sheet_ns(n, TOTAL),
    "АР-5": lambda n: draw_elev.elev_sheet_ew(n, TOTAL),
    "АР-6": lambda n: draw_sections.sections_sheet(n, TOTAL),
    "КЛ-1": lambda n: draw_extra.masonry_sheet(1, n, TOTAL),
    "КЛ-2": lambda n: draw_extra.masonry_sheet(2, n, TOTAL),
    "ПП-1": lambda n: draw_extra.floors_sheet(1, n, TOTAL),
    "ПП-2": lambda n: draw_extra.floors_sheet(2, n, TOTAL),
    "ПБ-1": lambda n: draw_extra.fire_sheet(n, TOTAL),
    "КР-1": lambda n: draw_struct.foundation_sheet(n, TOTAL),
    "КР-2": lambda n: draw_struct.slab_sheet(n, TOTAL),
    "КР-3": lambda n: draw_struct.roof_struct_sheet(n, TOTAL),
    "КР-4": lambda n: draw_struct.details_sheet(n, TOTAL),
    "ОВ-1": lambda n: draw_eng.ov_sheet(1, n, TOTAL),
    "ОВ-2": lambda n: draw_eng.ov_sheet(2, n, TOTAL),
    "ОВ-3": lambda n: draw_eng.boiler_scheme_sheet(n, TOTAL),
    "ОВ-4": lambda n: draw_extra.axon_ov_sheet(n, TOTAL),
    "ВК-1": lambda n: draw_eng.vk_sheet(1, n, TOTAL),
    "ВК-2": lambda n: draw_eng.vk_sheet(2, n, TOTAL),
    "ВК-3": lambda n: draw_eng.vk_scheme_sheet(n, TOTAL),
    "ВК-4": lambda n: draw_extra.axon_vk_sheet(n, TOTAL),
    "ЭО-1": lambda n: draw_eng.eo_sheet(1, n, TOTAL),
    "ЭО-2": lambda n: draw_eng.eo_sheet(2, n, TOTAL),
    "ЭО-3": lambda n: draw_eng.single_line_sheet(n, TOTAL),
}


def step(name, fn):
    print(f"→ {name}", flush=True)
    fn()


# расчёты и документы (сначала — от них зависят листы со сметой)
step("расчёты КР/ОВ/ВК/ЭО", lambda: subprocess.run([sys.executable, "calcs.py"], check=True, stdout=subprocess.DEVNULL))
step("дополнительные расчёты", lambda: subprocess.run([sys.executable, "calcs2.py"], check=True, stdout=subprocess.DEVNULL))
step("смета, ресурсная ведомость, графики ГР-1/ФГ-1", lambda: boq.write_reports(BASE, sheet_no=(number("ГР-1"), number("ФГ-1")), total=TOTAL))
for code, title, scale, fn, fmt in SHEETS:
    if code in BUILDERS:
        step(code, (lambda c=code, f=fn: BUILDERS[c](number(c)).save(os.path.join(D, f))))
step("документы", lambda: subprocess.run([sys.executable, "docs_gen.py"], check=True, stdout=subprocess.DEVNULL))
step("3D-модель (JSON, OBJ)", lambda: subprocess.run([sys.executable, "export3d.py"], check=True, stdout=subprocess.DEVNULL))
step("DXF", lambda: subprocess.run([sys.executable, "export_dxf.py"], check=True, stdout=subprocess.DEVNULL))
S = summary()
reg = {"date": datetime.date.today().strftime("%d.%m.%Y"), "summary": {"area_total": f"{S['area_total']:.1f}".replace(".", ","), "gross": f"{S['building_area_gross']:.0f}"},
       "sheets": [{"code": c, "title": t, "scale": sc, "file": f, "format": fm} for c, t, sc, f, fm in SHEETS]}
with open(os.path.join(D, "register.json"), "w", encoding="utf-8") as f:
    json.dump(reg, f, ensure_ascii=False, indent=1)
if "--no-render" not in sys.argv:
    step("PNG чертежей", lambda: subprocess.run(["node", "svg2png.js", D, "1"], check=True, stdout=subprocess.DEVNULL))
    step("3D-рендеры", lambda: subprocess.run(["node", "render3d.js"], check=True, stdout=subprocess.DEVNULL))
if "--no-pdf" not in sys.argv:
    step("PDF-альбом (cairosvg + pypdf)", lambda: subprocess.run([sys.executable, "make_pdf.py"], check=True, stdout=subprocess.DEVNULL))
step("сайт-артефакт", lambda: subprocess.run([sys.executable, "make_site.py"], check=True))
print("Сборка завершена.")
