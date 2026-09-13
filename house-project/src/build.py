# -*- coding: utf-8 -*-
"""Полная сборка проекта: чертежи (SVG+PNG), расчёты, документы, 3D, рендеры, смета, сайт-артефакт.
Запуск: python3 build.py [--no-render]
"""
import os, sys, subprocess, importlib

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(HERE)
sys.path.insert(0, HERE)
for d in ("drawings", "docs", "calc", "3d", "renders", "site"):
    os.makedirs(os.path.join(BASE, d), exist_ok=True)

TOTAL = 20
steps = []


def step(name, fn):
    print(f"→ {name}")
    fn()


import draw_site, draw_plans, draw_roof, draw_elev, draw_sections, calcs, draw_struct, draw_eng, export3d, boq, docs_gen

D = os.path.join(BASE, "drawings")
step("ГП-1", lambda: draw_site.site_sheet(1, TOTAL).save(os.path.join(D, "ГП-1_Генплан.svg")))
step("АР-1", lambda: draw_plans.floor_plan_sheet(1, 2, TOTAL).save(os.path.join(D, "АР-1_План_1_этажа.svg")))
step("АР-2", lambda: draw_plans.floor_plan_sheet(2, 3, TOTAL).save(os.path.join(D, "АР-2_План_2_этажа.svg")))
step("АР-3", lambda: draw_roof.roof_sheet(4, TOTAL).save(os.path.join(D, "АР-3_План_кровли.svg")))
step("АР-4", lambda: draw_elev.elev_sheet_ns(5, TOTAL).save(os.path.join(D, "АР-4_Фасады_3-1_1-3.svg")))
step("АР-5", lambda: draw_elev.elev_sheet_ew(6, TOTAL).save(os.path.join(D, "АР-5_Фасады_А-Б_Б-А.svg")))
step("АР-6", lambda: draw_sections.sections_sheet(7, TOTAL).save(os.path.join(D, "АР-6_Разрезы.svg")))
step("расчёты", lambda: subprocess.run([sys.executable, "calcs.py"], check=True))
step("КР-1", lambda: draw_struct.foundation_sheet(8, TOTAL).save(os.path.join(D, "КР-1_Фундаментная_плита.svg")))
step("КР-2", lambda: draw_struct.slab_sheet(9, TOTAL).save(os.path.join(D, "КР-2_Перекрытие_перемычки.svg")))
step("КР-3", lambda: draw_struct.roof_struct_sheet(10, TOTAL).save(os.path.join(D, "КР-3_Стропильная_система.svg")))
step("КР-4", lambda: draw_struct.details_sheet(11, TOTAL).save(os.path.join(D, "КР-4_Узлы.svg")))
step("ОВ-1", lambda: draw_eng.ov_sheet(1, 12, TOTAL).save(os.path.join(D, "ОВ-1_Отопление_вентиляция_1_этаж.svg")))
step("ОВ-2", lambda: draw_eng.ov_sheet(2, 13, TOTAL).save(os.path.join(D, "ОВ-2_Отопление_вентиляция_2_этаж.svg")))
step("ОВ-3", lambda: draw_eng.boiler_scheme_sheet(14, TOTAL).save(os.path.join(D, "ОВ-3_Схема_котельной.svg")))
step("ВК-1", lambda: draw_eng.vk_sheet(1, 15, TOTAL).save(os.path.join(D, "ВК-1_Водоснабжение_канализация_1_этаж.svg")))
step("ВК-2", lambda: draw_eng.vk_sheet(2, 16, TOTAL).save(os.path.join(D, "ВК-2_Водоснабжение_канализация_2_этаж.svg")))
step("ВК-3", lambda: draw_eng.vk_scheme_sheet(17, TOTAL).save(os.path.join(D, "ВК-3_Принципиальные_схемы.svg")))
step("ЭО-1", lambda: draw_eng.eo_sheet(1, 18, TOTAL).save(os.path.join(D, "ЭО-1_Электрооборудование_1_этаж.svg")))
step("ЭО-2", lambda: draw_eng.eo_sheet(2, 19, TOTAL).save(os.path.join(D, "ЭО-2_Электрооборудование_2_этаж.svg")))
step("ЭО-3", lambda: draw_eng.single_line_sheet(20, TOTAL).save(os.path.join(D, "ЭО-3_Однолинейная_схема.svg")))
step("смета и график", lambda: boq.write_reports(BASE))
step("документы", lambda: subprocess.run([sys.executable, "docs_gen.py"], check=True))
step("3D-модель", lambda: subprocess.run([sys.executable, "export3d.py"], check=True))
if "--no-render" not in sys.argv:
    step("PNG чертежей", lambda: subprocess.run(["node", "svg2png.js", D, "1"], check=True))
    step("3D-рендеры", lambda: subprocess.run(["node", "render3d.js"], check=True))
if os.path.exists(os.path.join(HERE, "make_site.py")):
    step("сайт-артефакт", lambda: subprocess.run([sys.executable, "make_site.py"], check=True))
print("Сборка завершена.")
