# -*- coding: utf-8 -*-
"""Раздел КР: КР-1 фундаментная плита, КР-2 перекрытие и перемычки, КР-3 стропильная система, КР-4 узлы."""
import math
from model import *
from svg import Sheet, mm
import calcs
from draw_plans import draw_axes
from draw_sections import roof_transverse, RAFTER_V

R = calcs.run_all()
ZG = LEVELS["grade"]
RAFT = (-0.5, -0.5, 13.1, 16.1)


def lintel_mark(side, w):
    if side in ("E", "W"):
        return "ПМ-1" if w <= 1.2 else ("ПМ-2" if w <= 1.5 else "ПМ-3")
    return "ПМ-1" if w <= 1.5 else ("ПМ-2" if w <= 1.8 else "ПМ-4")


# ============================================================================
# КР-1 — фундаментная плита
# ============================================================================
def foundation_sheet(sheet_no, total):
    sh = Sheet("A2", code="КР-1", title="Схема расположения фундаментной плиты. Сечение 1-1", scale_txt="1:100, 1:20", sheet_no=sheet_no, sheets_total=total)
    v = sh.view(ox=60, oy=60, scale=100)
    sh.ptext(60, 22, "Схема расположения фундаментной плиты на отм. −0,300   М 1:100", size=4.5, anchor="start", weight="bold")
    o = EXT_OUTER
    # плита
    v.rect(*RAFT, fill="#eef0f2", sw="thick")
    # рёбра под стенами
    ring = (f"M{v.X(o[0]):.2f} {v.Y(o[1]):.2f} H{v.X(o[2]):.2f} V{v.Y(o[3]):.2f} H{v.X(o[0]):.2f} Z "
            f"M{v.X(EXT_INNER[0]):.2f} {v.Y(EXT_INNER[1]):.2f} H{v.X(EXT_INNER[2]):.2f} V{v.Y(EXT_INNER[3]):.2f} H{v.X(EXT_INNER[0]):.2f} Z")
    v.s.add(f'<path d="{ring}" fill="url(#hConcrete)" fill-rule="evenodd" stroke="#000" stroke-width="0.35"/>')
    v.rect(6.175, 0.2, 6.425, 15.4, fill="url(#hConcrete)", sw="mid")
    # перегородки 200 (гараж) — без рёбер, показаны пунктиром
    v.rect(3.9, 0.2, 4.1, 6.6, sw="thin", dash="1 1")
    v.rect(0.2, 6.6, 6.175, 6.8, sw="thin", dash="1 1")
    # терраса, крыльцо, пандус — отдельные плиты с деформационным швом
    t = TERRACE["rect"]
    v.rect(*t, sw="mid", dash="3 1")
    v.text((t[0] + t[2]) / 2, (t[1] + t[3]) / 2, "плита террасы 150 мм на ПГС 300, сетка Ø8 ш.200, деф. шов 20 мм", size=2.0)
    p = PORCH["rect"]
    v.rect(*p, sw="mid", dash="3 1")
    v.text((p[0] + p[2]) / 2, p[1] - 0.4, "крыльцо: плита 150 + ступени, деф. шов", size=1.8)
    a = GARAGE_APRON["rect"]
    v.rect(*a, sw="thin", dash="1 1")
    v.text((a[0] + a[2]) / 2, a[1] - 0.4, "пандус (бетон 150 по ПГС)", size=1.8)
    # гильзы и вводы
    sleeves = [
        (10.6, 5.0, "Ст1 Ø160", "#7a4a1a"), (6.0, 4.8, "Ст2 Ø160", "#7a4a1a"), (0.6, 10.4, "Ст3 Ø160", "#7a4a1a"),
        (4.4, 0.5, "В1 Ø50 (ввод воды)", "#1a5fb4"), (5.5, 3.3, "W Ø63 (кабель)", "#c00"),
    ]
    for x, y, lbl, col in sleeves:
        v.circle(x, y, 1.6, fill="#fff", stroke=col, sw="mid")
        v.text_mm(x, y, 0, -3.5, lbl, size=1.8, color=col)
    # трасса канализации под плитой
    v.poly([(0.6, 10.4), (12.8, 10.4), (13.6, 10.4)], closed=False, stroke="#7a4a1a", sw="mid", dash="4 1.5")
    v.poly([(6.0, 4.8), (6.0, 10.4)], closed=False, stroke="#7a4a1a", sw="mid", dash="4 1.5")
    v.poly([(10.6, 5.0), (10.6, 10.4)], closed=False, stroke="#7a4a1a", sw="mid", dash="4 1.5")
    v.text(13.0, 9.8, "К1 выпуск Ø110, лоток −1,100", size=1.8, color="#7a4a1a", anchor="start")
    v.text(3.0, 10.0, "К1 под плитой Ø110, i=0,02, в ПГС", size=1.8, color="#7a4a1a")
    # дренаж пристенный
    v.rect(RAFT[0] - 0.9, RAFT[1] - 0.9, RAFT[2] + 0.9, RAFT[3] + 0.9, sw="thin", dash="6 1.5", stroke="#3a8fb7")
    for (x, y) in ((RAFT[0] - 0.9, RAFT[1] - 0.9), (RAFT[2] + 0.9, RAFT[1] - 0.9), (RAFT[0] - 0.9, RAFT[3] + 0.9), (RAFT[2] + 0.9, RAFT[3] + 0.9)):
        v.circle(x, y, 2.2, fill="#fff", stroke="#3a8fb7", sw="mid")
    v.text(RAFT[2] + 0.9, RAFT[1] - 1.6, "дренаж Ø110 в геотекстиле, колодцы Ø315", size=1.8, color="#3a8fb7", anchor="end")
    # сечение 1-1
    v.line(-2.2, 8.5, -1.2, 8.5, w="xthick"); v.line(14.0, 8.5, 15.0, 8.5, w="xthick")
    v.line(-1.7, 8.5, -1.7, 9.4, w="mid", marker="arrow"); v.line(14.5, 8.5, 14.5, 9.4, w="mid", marker="arrow")
    v.text_mm(-1.7, 8.5, 0, -3, "1", size=4, weight="bold"); v.text_mm(14.5, 8.5, 0, -3, "1", size=4, weight="bold")
    # оси и размеры
    draw_axes(v)
    v.dim_h([RAFT[0], o[0], o[2], RAFT[2]], RAFT[3] + 3.5, 8, ext_from=RAFT[3], flip_text=True)
    v.dim_h([RAFT[0], RAFT[2]], RAFT[3] + 3.5, 16, ext_from=RAFT[3], flip_text=True)
    v.dim_v([RAFT[1], o[1], o[3], RAFT[3]], RAFT[2] + 3.5, 8, ext_from=RAFT[2])
    v.dim_v([RAFT[1], RAFT[3]], RAFT[2] + 3.5, 16, ext_from=RAFT[2])
    v.text(6.3, 13.0, "Плита 300 мм, B25 W6 F150; сетки С1 (низ) и С2 (верх) Ø14 A500C ш.200×200", size=2.4)
    v.text(6.3, 13.6, "защитный слой: низ 50 мм, верх 35 мм; фиксаторы, рёбра ростверк 400×300 / 250×300", size=2.2)
    v.text(9.4, 2.5, "доп. нижние Ø14 ш.200 (l=2,0 м) в полосе 2,0 м вдоль оси 2", size=2.0, rot=-90)
    v.rect(5.3, 0.2, 7.3, 15.4, sw="thin", dash="2 1", stroke="#c00")

    # ---- сечение 1-1 (М 1:20) ----
    d = sh.view(ox=330, oy=260, scale=20, flip_y=True)
    sh.ptext(330, 118, "Сечение 1-1 (узел цоколя у оси 1)   М 1:20", size=4, anchor="start", weight="bold")
    x0 = -1.6
    # грунт
    d.rect(x0, ZG - 0.95, -0.5, ZG, fill="url(#hEarth)", stroke=None)
    d.rect(x0, LEVELS["cushion_bottom"] - 0.3, 2.2, LEVELS["cushion_bottom"], fill="url(#hEarth)", stroke=None)
    d.rect(x0, LEVELS["cushion_bottom"] - 0.3, -0.8, ZG - 0.95, fill="url(#hEarth)", stroke=None)
    d.line(x0, ZG, -1.3, ZG, w="thick")
    # подушка ПГС, ЭППС, плита
    d.rect(-0.8, LEVELS["cushion_bottom"], 2.2, LEVELS["xps_bottom"], fill="url(#hGravel)", sw="thin")
    d.rect(-0.5, LEVELS["xps_bottom"], 2.2, LEVELS["raft_bottom"], fill="url(#hInsul)", sw="thin")
    d.rect(-0.5, LEVELS["raft_bottom"], 2.2, LEVELS["raft_top"], fill="url(#hConcrete)", sw="mid")
    d.rect(-0.2, LEVELS["raft_top"], 0.2, 0.0, fill="url(#hConcrete)", sw="mid")
    # арматура плиты: сетки
    for z in (LEVELS["raft_bottom"] + 0.05, LEVELS["raft_top"] - 0.035):
        d.line(-0.45, z, 2.2, z, w="thick", color="#c00")
        x = -0.4
        while x < 2.2:
            d.circle(x, z, 0.7, fill="#c00", stroke=None)
            x += 0.2
    # П-образный по торцу
    d.s.ppath(f"M{d.X(0.0):.2f} {d.Y(LEVELS['raft_bottom'] + 0.05):.2f} H{d.X(-0.45):.2f} V{d.Y(LEVELS['raft_top'] - 0.035):.2f} H{d.X(0.0):.2f}", stroke="#c00", sw="thick")
    # ребро: продольные 4Ø12 и хомут
    for (x, z) in ((-0.15, -0.26), (0.15, -0.26), (-0.15, -0.04), (0.15, -0.04)):
        d.circle(x, z, 0.7, fill="#c00", stroke=None)
    d.rect(-0.16, -0.27, 0.16, -0.03, stroke="#c00", sw="mid")
    d.line(-0.15, -0.27, -0.15, LEVELS["raft_bottom"] + 0.06, w="mid", color="#c00")   # выпуск
    d.line(0.15, -0.27, 0.15, LEVELS["raft_bottom"] + 0.06, w="mid", color="#c00")
    # стена и пол
    d.rect(-0.2, 0.0, 0.2, 1.1, fill="url(#hAerated)", sw="mid")
    d.rect(0.2, LEVELS["raft_top"], 2.2, -0.15, fill="url(#hInsul)", sw="thin")
    d.rect(0.2, -0.15, 2.2, -0.03, fill="url(#hConcrete)", sw="thin")
    d.rect(0.2, -0.03, 2.2, 0.0, fill="#ddd", sw="thin")
    for x in (0.4, 0.55, 0.7, 0.85, 1.0, 1.15, 1.3, 1.45, 1.6, 1.75, 1.9, 2.05):
        d.circle(x, -0.10, 0.6, fill="#fff", stroke="#c00", sw="thin")
    d.rect(0.2, 0.0, 0.215, 1.1, fill="#ddd", sw="thin")   # штукатурка внутр.
    # утепление цоколя и отделка
    d.rect(-0.25, LEVELS["raft_top"], -0.2, 1.1, fill="url(#hInsul)", sw="thin")
    d.rect(-0.55, LEVELS["raft_bottom"], -0.5, LEVELS["raft_top"], fill="url(#hInsul)", sw="thin")
    d.rect(-0.27, LEVELS["raft_top"] + 0.02, -0.25, 1.1, fill="#555", stroke=None)
    d.rect(-0.28, 0.3, -0.25, 1.1, fill="#f2efe8", stroke=None)
    d.line(-0.56, LEVELS["raft_top"] + 0.02, -0.28, LEVELS["raft_top"] + 0.06, w="mid")   # отлив
    # отмостка
    d.rect(-1.3, ZG - 0.10, -0.55, ZG + 0.02, fill="url(#hConcrete)", sw="thin")
    d.rect(-1.3, ZG - 0.25, -0.55, ZG - 0.10, fill="url(#hSand)", sw="thin")
    d.rect(-1.3, ZG - 0.30, -0.55, ZG - 0.25, fill="url(#hInsul)", sw="thin")
    d.rect(-1.3, ZG - 0.45, -0.55, ZG - 0.30, fill="url(#hGravel)", sw="thin")
    # дренаж
    d.circle(-1.4, LEVELS["cushion_bottom"] + 0.1, 0.11 * d.k, fill="#fff", sw="mid")
    d.rect(-1.65, LEVELS["cushion_bottom"] - 0.15, -1.15, LEVELS["cushion_bottom"] + 0.35, fill="url(#hGravel)", sw="thin")
    # отметки
    for z, txt in ((LEVELS["cushion_bottom"], "−1,100"), (LEVELS["xps_bottom"], "−0,700"), (LEVELS["raft_bottom"], "−0,600"), (LEVELS["raft_top"], "−0,300"), (0.0, "±0,000"), (ZG, "−0,450")):
        d.level_mark(2.2 + 0.25, z, txt, side="right", len_mm=8, size=2.2)
    d.dim_v([LEVELS["cushion_bottom"], LEVELS["xps_bottom"], LEVELS["raft_bottom"], LEVELS["raft_top"], 0.0], -0.5, -40, text_size=2.0)
    d.dim_h([-0.5, -0.2, 0.2], LEVELS["cushion_bottom"] - 0.3, 8, text_size=2.0, flip_text=True)
    d.dim_h([-1.3, -0.5], ZG - 0.45, 8, text_size=2.0, flip_text=True, ext_from=ZG - 0.45)
    # выноски
    def lead(x, z, dx, dz, txt):
        X, Y = d.P(x, z)
        d.s.pcircle(X, Y, 0.6, fill="#000", stroke=None)
        d.s.pline(X, Y, X + dx, Y + dz, w="thin")
        d.s.pline(X + dx, Y + dz, X + dx + (4 if dx >= 0 else -4), Y + dz, w="thin")
        d.s.ptext(X + dx + (1 if dx >= 0 else -1), Y + dz - 1, txt, size=2.0, anchor="start" if dx >= 0 else "end", baseline="auto")
    lead(1.2, LEVELS["cushion_bottom"] + 0.2, 30, 20, "ПГС 400 мм, K_упл ≥ 0,95, геотекстиль 200 г/м² под подушкой")
    lead(1.5, LEVELS["xps_bottom"] + 0.05, 30, 12, "ЭППС 100 мм (σ10 ≥ 250 кПа) + плёнка ПЭ 200 мкм")
    lead(1.7, LEVELS["raft_bottom"] + 0.15, 30, 4, "плита 300 мм B25 W6 F150, сетки С1/С2 Ø14 ш.200, фиксаторы 50/35")
    lead(0.0, -0.15, 30, -40, "ребро 400×300: 4Ø12 A500C, хомуты Ø8 ш.300, выпуски из плиты")
    lead(1.0, -0.10, 30, -52, "ЭППС 150 + стяжка 120 (трубы ТП 16 ш.150) + покрытие")
    lead(0.0, 0.8, 30, -70, "газобетон D400 400 мм; 1-й ряд на ЦПР по гидроизоляции (2 слоя)")
    lead(-0.23, 0.5, -20, -20, "цоколь: ЭППС 50 + клинкер / штукатурка, отлив")
    lead(-0.9, ZG - 0.2, -14, -22, "отмостка 1,0 м: бетон 100 (сетка Ø4), ПГС 150, ЭППС 50, i=3 %")
    lead(-1.4, LEVELS["cushion_bottom"] + 0.1, -12, 28, "дренаж Ø110 в щебне и геотекстиле")
    # спецификация арматуры
    xr = 60
    yy = 300
    sh.ptext(xr, yy, "Ведомость расхода стали (ориентировочно)", size=3.2, anchor="start", weight="bold")
    F = R["foundation"]
    A_raft = (RAFT[2] - RAFT[0]) * (RAFT[3] - RAFT[1])
    m14 = 1.21
    rows = [
        ["С1", "Сетка нижняя Ø14 A500C, 200×200", f"{A_raft:.0f} м²", f"{A_raft * 2 * 5.0 * m14 * 1.06 / 1000:.2f} т"],
        ["С2", "Сетка верхняя Ø14 A500C, 200×200", f"{A_raft:.0f} м²", f"{A_raft * 2 * 5.0 * m14 * 1.06 / 1000:.2f} т"],
        ["3", "Доп. стержни Ø14 ш.200, l=2,0 м, полоса оси 2", "76 шт.", f"{76 * 2.0 * m14 / 1000:.2f} т"],
        ["4", "Продольные рёбер Ø12 A500C", f"{(56.4 + 15.2) * 4:.0f} м", f"{(56.4 + 15.2) * 4 * 0.888 / 1000:.2f} т"],
        ["5", "Хомуты рёбер Ø8, ш.300", f"{(56.4 + 15.2) / 0.3:.0f} шт.", f"{(56.4 + 15.2) / 0.3 * 1.3 * 0.395 / 1000:.2f} т"],
        ["6", "П-образные по торцам Ø12, ш.200", f"{2 * (RAFT[2] - RAFT[0] + RAFT[3] - RAFT[1]) / 0.2:.0f} шт.", f"{2 * (RAFT[2] - RAFT[0] + RAFT[3] - RAFT[1]) / 0.2 * 0.75 * 0.888 / 1000:.2f} т"],
        ["", "Итого арматуры", "", f"≈ {F['steel_t']:.1f} т"],
        ["", "Бетон B25 W6 F150 (плита + рёбра)", "", f"{F['V_concrete']:.1f} м³"],
    ]
    sh.table(xr, yy + 4, [("Поз.", 12, "c"), ("Наименование", 95, "l"), ("Кол-во", 30, "r"), ("Масса / объём", 32, "r")], rows, size=2.2)
    notes = [
        "1. Основание — уплотнённая подушка из ПГС 400 мм по геотекстилю на естественном грунте (суглинок), выемка растительного слоя и слабых грунтов до отм. −1,100.",
        "2. ТРЕБУЮТСЯ инженерно-геологические изыскания (не менее 3 скважин по 8 м) и уточнение R₀, УГВ, пучинистости; при высоком УГВ — кольцевой дренаж обязателен.",
        "3. Плита выступает за грань стен на 300 мм; торцы плиты и рёбер утепляются ЭППС 50, вокруг — утеплённая отмостка (защита от морозного пучения, СТО 36554501-012).",
        "4. Бетонирование плиты — за один приём, уход за бетоном ≥ 7 сут; рёбра — вторым этапом по выпускам (шероховатая поверхность, адгезионный шов).",
        "5. До бетонирования уложить гильзы вводов (К1, В1, W), закладные заземления (выпуск полосы 40×4 в 1.12) и трубы канализации под плитой с испытанием.",
    ]
    sh.ptext(xr, 372, "Примечания", size=3.0, anchor="start", weight="bold")
    sh.ptext_lines(xr, 378, notes, size=2.1, lh=3.9)
    return sh


# ============================================================================
# КР-2 — перекрытие и перемычки
# ============================================================================
def slab_sheet(sheet_no, total):
    sh = Sheet("A2", code="КР-2", title="Схема армирования перекрытий. Балка Б-1. Ведомость перемычек", scale_txt="1:100, 1:20", sheet_no=sheet_no, sheets_total=total)
    v = sh.view(ox=60, oy=55, scale=100)
    sh.ptext(60, 20, "Схема армирования монолитного перекрытия на отм. +3,000 (аналогично +6,300)   М 1:100", size=4.2, anchor="start", weight="bold")
    o = EXT_OUTER
    sl = (o[0] + 0.1, o[1] + 0.1, o[2] - 0.1, o[3] - 0.1)
    v.rect(*sl, fill="#f4f4f4", sw="thick")
    # стены под плитой
    ring = (f"M{v.X(o[0]):.2f} {v.Y(o[1]):.2f} H{v.X(o[2]):.2f} V{v.Y(o[3]):.2f} H{v.X(o[0]):.2f} Z "
            f"M{v.X(EXT_INNER[0]):.2f} {v.Y(EXT_INNER[1]):.2f} H{v.X(EXT_INNER[2]):.2f} V{v.Y(EXT_INNER[3]):.2f} H{v.X(EXT_INNER[0]):.2f} Z")
    v.s.add(f'<path d="{ring}" fill="none" fill-rule="evenodd" stroke="#000" stroke-width="0.35" stroke-dasharray="2 1"/>')
    v.rect(6.175, 0.2, 6.425, 15.4, sw="mid", dash="2 1")
    # проём лестницы
    w = STAIR_WELL
    v.rect(*w, fill="#fff", sw="mid")
    v.line(w[0], w[1], w[2], w[3], w="thin"); v.line(w[2], w[1], w[0], w[3], w="thin")
    v.rect(w[0] - 0.25, w[1] - 0.25, w[2] + 0.25, w[3] + 0.25, sw="thin", dash="1 1", stroke="#c00")
    v.text((w[0] + w[2]) / 2, w[3] + 0.6, "скрытые балки 250×200 по контуру проёма: 4Ø14, хомуты Ø8 ш.150", size=1.8, color="#c00")
    # зоны верхней арматуры
    v.rect(6.3 - 1.5, 0.2, 6.3 + 1.5, 15.4, fill="url(#hMasonry)", stroke="#c00", sw="thin", opacity=0.5)
    v.text(6.3, 7.0, "верх: Ø12 A500C ш.150, l=3,0 м (над осью 2)", size=2.0, rot=-90, color="#c00")
    for (x1, y1, x2, y2) in ((sl[0], sl[1], sl[0] + 1.2, sl[3]), (sl[2] - 1.2, sl[1], sl[2], sl[3]), (sl[0], sl[1], sl[2], sl[1] + 1.2), (sl[0], sl[3] - 1.2, sl[2], sl[3])):
        v.rect(x1, y1, x2, y2, fill="url(#hMasonry)", stroke="#c00", sw="thin", opacity=0.3)
    v.text(0.5, 8.0, "верх у наружных стен: Ø10 ш.200, l=1,2 м", size=1.8, rot=-90, color="#c00")
    # нижняя сетка
    v.text(3.2, 3.6, "низ: рабочая Ø12 ш.200 (вдоль пролёта, ⟷)", size=2.0)
    v.text(3.2, 4.2, "распределительная Ø10 ш.250 (↕)", size=2.0)
    v.text(9.6, 12.0, "низ: Ø12 ш.200 ⟷ / Ø10 ш.250 ↕", size=2.0)
    # рабочее направление
    for y in (2.0, 12.6):
        v.line(0.6, y, 5.8, y, w="mid", marker="arrow"); v.line(5.8, y, 0.6, y, w="mid", marker="arrow")
        v.line(6.8, y, 12.0, y, w="mid", marker="arrow"); v.line(12.0, y, 6.8, y, w="mid", marker="arrow")
    # балка Б-1
    v.rect(6.175, 10.9, 6.425, 14.5, fill="#c00", stroke=None, opacity=0.6)
    v.text(6.9, 12.7, "Б-1 250×600", size=2.2, rot=-90, color="#c00")
    # терморазрыв по периметру
    v.text(6.3, 15.7, "по периметру — торец плиты ЭППС 100 мм, монолитный участок совмещён с обвязочным поясом", size=2.0)
    # ЭППС над гаражом? нет. Обозначить проходы вентшахт
    for x1, y1, x2, y2, name, desc, floors in VENT_SHAFTS:
        if 2 in floors or name in ("В1", "В7"):
            v.rect(x1, y1, x2, y2, fill="#fff", sw="thin")
            v.text_mm((x1 + x2) / 2, (y1 + y2) / 2, 5, 0, name, size=1.6)
    draw_axes(v)
    v.dim_h([sl[0], sl[2]], sl[3] + 3.5, 8, ext_from=sl[3], flip_text=True)
    v.dim_v([sl[1], sl[3]], sl[2] + 3.5, 8, ext_from=sl[2])
    # сечение балки Б-1 (1:20)
    d = sh.view(ox=360, oy=185, scale=20, flip_y=True)
    sh.ptext(340, 30, "Балка Б-1 (сечение)   М 1:20", size=3.6, anchor="start", weight="bold")
    B = R["beam"]
    d.rect(-0.125, 0.0, 0.125, 0.6, fill="url(#hConcrete)", sw="mid")
    d.rect(-1.0, 0.4, -0.125, 0.6, fill="url(#hConcrete)", sw="mid"); d.rect(0.125, 0.4, 1.0, 0.6, fill="url(#hConcrete)", sw="mid")
    d.rect(-0.095, 0.03, 0.095, 0.57, stroke="#c00", sw="mid")
    for x in (-0.075, -0.025, 0.025, 0.075):
        d.circle(x, 0.055, 1.2, fill="#c00", stroke=None)
    for x in (-0.07, 0.07):
        d.circle(x, 0.545, 0.9, fill="#c00", stroke=None)
    for x in (-0.9, -0.7, -0.5, -0.3, 0.3, 0.5, 0.7, 0.9):
        d.circle(x, 0.43, 0.8, fill="#c00", stroke=None); d.circle(x, 0.57, 0.7, fill="#c00", stroke=None)
    d.dim_h([-0.125, 0.125], -0.05, 8, text_size=2.0, flip_text=True)
    d.dim_v([0.0, 0.4, 0.6], 0.125, 8, text_size=2.0)
    d.text(0.0, -0.32, f"низ {B['bars']}; верх 2Ø12 (+2Ø16 у опор); хомуты {B['stirrups']}", size=1.9)
    d.text(0.0, -0.45, f"M = {B['M']:.0f} кН·м ≤ M_u = {B['M_u']:.0f} кН·м; Q = {B['Q']:.0f} кН; опирание 600 мм на подушку 250×600×200", size=1.9)
    # ведомость перемычек
    xr = 340
    yy = 215
    sh.ptext(xr, yy, "Ведомость перемычек", size=3.2, anchor="start", weight="bold")
    rows = []
    cnt = {}
    for fl in (1, 2):
        for s, a1, a2, h, sill, tag in WINDOWS[fl]:
            mk = lintel_mark(s, a2 - a1)
            cnt.setdefault(mk, []).append(f"{tag}")
        for s, a1, a2, h, tag, kind in EXT_DOORS[fl]:
            mk = lintel_mark(s, a2 - a1)
            cnt.setdefault(mk, []).append(tag)
    spec = {l["tag"].split(" ")[0]: l for l in B["lintels"]}
    for mk in ("ПМ-1", "ПМ-2", "ПМ-3", "ПМ-4"):
        l = spec.get(mk)
        rows.append([mk, l["core"] if l else "монолит 400×300", l["bars"] if l else "3Ø16 + 2Ø10, хомуты Ø8 ш.200", f"{len(cnt.get(mk, []))}", ", ".join(sorted(set(cnt.get(mk, []))))])
    rows.append(["Б-1", "балка 250×600 (ось 2)", B["bars"] + "; " + "Ø8 ш.150/250", "1", "ПР-1 3000×2600"])
    rows.append(["ПМ-5", "U-блок 250, ядро 150×200", "2Ø12 + 2Ø8, хомуты Ø6 ш.150", "5", "двери в стене оси 2 (Д-2), ПР-2"])
    rows.append(["ПМ-6", "заводская газобетонная / 2∠50×5", "—", "16", "двери в перегородках 100/200 мм"])
    sh.table(xr, yy + 4, [("Марка", 14, "c"), ("Сечение", 48, "l"), ("Армирование", 70, "l"), ("шт.", 10, "c"), ("Проёмы", 80, "l")], rows, size=2.0)
    notes = [
        "1. Плиты перекрытий — монолитные ж/б 200 мм, бетон B25 W6 F150, арматура A500C; защитный слой 25 мм; опирание на наружные стены 300 мм, на стену оси 2 — на всю ширину.",
        "2. Стыковка стержней — внахлёст 40d вразбежку; в углах и у проёмов — дополнительные Г-образные стержни Ø12 l=1,5 м; по контуру плиты — П-образные Ø10 ш.200.",
        "3. Перед бетонированием по верху кладки — выравнивающий слой ЦПР M100 20 мм; торец плиты — ЭППС 100 мм (терморазрыв), в углах — ЭППС 50.",
        "4. Перемычки ПМ-1…ПМ-3 — из U-блоков D500 400 мм с монолитным ядром 250×200 и вкладышем ЭППС 50 с наружной стороны; ПМ-4 — монолитные 400×300 в U-блоках/опалубке; опирание ПМ ≥ 250 мм (ПМ-4 ≥ 300).",
        "5. Чердачное перекрытие +6,300 — армирование аналогично (рабочая Ø12 ш.200, верх над осью 2 Ø12 ш.150); дополнительно под лежнями стоек — нет требований; проём люка 700×900 окаймлён 2Ø12.",
        "6. Лестница — монолитная, плита марша 150 мм, площадка 200 мм, рабочая Ø12 ш.150 (низ), Ø8 ш.200 распределительная; опирание на стены оси 2 и на балки проёма.",
    ]
    sh.ptext(60, 300, "Примечания", size=3.0, anchor="start", weight="bold")
    sh.ptext_lines(60, 306, notes, size=2.1, lh=3.9)
    return sh


# ============================================================================
# КР-3 — стропильная система
# ============================================================================
def roof_struct_sheet(sheet_no, total):
    sh = Sheet("A2", code="КР-3", title="Схема стропильной системы. Разрез по кровле", scale_txt="1:100, 1:50", sheet_no=sheet_no, sheets_total=total)
    v = sh.view(ox=60, oy=60, scale=100)
    sh.ptext(60, 20, "Схема расположения элементов стропильной системы (план)   М 1:100", size=4.2, anchor="start", weight="bold")
    o = EXT_OUTER
    xw, xe = ROOF["eave_edge_x_w"], ROOF["eave_edge_x_e"]
    yn, ys = ROOF["gable_y_n"], ROOF["gable_y_s"]
    # стены (верх) и фронтоны
    ring = (f"M{v.X(o[0]):.2f} {v.Y(o[1]):.2f} H{v.X(o[2]):.2f} V{v.Y(o[3]):.2f} H{v.X(o[0]):.2f} Z "
            f"M{v.X(EXT_INNER[0]):.2f} {v.Y(EXT_INNER[1]):.2f} H{v.X(EXT_INNER[2]):.2f} V{v.Y(EXT_INNER[3]):.2f} H{v.X(EXT_INNER[0]):.2f} Z")
    v.s.add(f'<path d="{ring}" fill="url(#hAerated)" fill-rule="evenodd" stroke="#000" stroke-width="0.35"/>')
    v.rect(6.175, 0.2, 6.425, 15.4, fill="url(#hAerated)", sw="thin")
    # мауэрлат
    v.rect(-0.15, o[1] + 0.2, 0.0, o[3] - 0.2, fill="url(#hWood)", sw="thin")
    v.rect(12.6, o[1] + 0.2, 12.75, o[3] - 0.2, fill="url(#hWood)", sw="thin")
    # стропила
    y = o[1]
    n_r = 0
    while y <= o[3] + 0.01:
        v.rect(xw, y - 0.025, xe, y + 0.025, fill="#e8d3b0", sw="thin")
        y += ROOF["rafter_step"]
        n_r += 1
    # выносные стропила фронтонных свесов
    for yy in (yn + 0.05, ys - 0.05):
        v.rect(xw, yy - 0.025, xe, yy + 0.025, fill="#e8d3b0", sw="thin")
    # кобылки/консоли фронтона (выпуски прогонов)
    # прогоны
    for x in ROOF["purlin_x"]:
        v.rect(x - 0.05, yn, x + 0.05, ys, fill="url(#hWood)", sw="mid")
        v.text(x + 0.35, 1.5, f"прогон {int(ROOF['purlin'][0]*1000)}×{int(ROOF['purlin'][1]*1000)}" + (" (коньковый)" if x == ROOF["ridge_x"] else ""), size=1.9, rot=-90)
        # лежень
        v.rect(x - 0.075, o[1] + 0.2, x + 0.075, o[3] - 0.2, sw="thin", dash="2 1")
        # стойки и подкосы
        yp = 0.5
        while yp < 15.6:
            v.rect(x - 0.05, yp - 0.075, x + 0.05, yp + 0.075, fill="#000", sw="thin")
            v.line(x - 0.25, yp - 0.9, x, yp - 0.15, w="thin"); v.line(x + 0.25, yp - 0.9, x, yp - 0.15, w="thin")
            v.line(x - 0.25, yp + 0.9, x, yp + 0.15, w="thin"); v.line(x + 0.25, yp + 0.9, x, yp + 0.15, w="thin")
            yp += ROOF["post_step"]
    # ветровые связи (диагонали под стропилами у фронтонов)
    for (y1, y2) in ((0.2, 3.8), (11.8, 15.4)):
        for (xa, xb) in ((0.0, 6.3), (6.3, 12.6)):
            v.line(xa, y1, xb, y2, w="mid", dash="3 1"); v.line(xa, y2, xb, y1, w="mid", dash="3 1")
    v.text(3.15, 2.0, "ветровые связи — доска 50×150", size=1.8)
    # обозначения
    v.text(9.5, 8.0, f"стропила {int(ROOF['rafter'][0]*1000)}×{int(ROOF['rafter'][1]*1000)}, шаг {int(ROOF['rafter_step']*1000)}", size=2.2)
    v.text(9.5, 8.6, f"стойки {int(ROOF['post'][0]*1000)}×{int(ROOF['post'][1]*1000)} шаг {ROOF['post_step']:.1f} м; подкосы 100×100", size=2.0)
    v.text(3.15, 8.0, "мауэрлат 150×150 на шпильках М12 ш.1000", size=2.0)
    v.text(3.15, 8.6, "лежни 150×150 по плите на гидроизоляции", size=2.0)
    draw_axes(v)
    v.dim_h([xw, o[0], 3.0, 6.3, 9.6, o[2], xe], ys + 3.5, 8, ext_from=ys, flip_text=True)
    v.dim_v([yn, o[1], o[3], ys], xe + 3.5, 8, ext_from=xe)
    v.text(xw - 0.4, 8.0, "свес 600", size=1.8, rot=-90)
    # разрез по кровле (1:50)
    d = sh.view(ox=312, oy=250, scale=50, flip_y=True)
    sh.ptext(300, 20, "Разрез по кровле (поперечный)   М 1:50", size=3.6, anchor="start", weight="bold")
    d.rect(-0.2, 5.0, 0.2, 6.5, fill="url(#hAerated)", sw="mid"); d.rect(12.4, 5.0, 12.8, 6.5, fill="url(#hAerated)", sw="mid")
    d.rect(6.175, 5.0, 6.425, 6.3, fill="url(#hAerated)", sw="mid")
    d.rect(-0.1, 6.3, 12.7, 6.5, fill="url(#hConcrete)", sw="mid")
    roof_transverse(d, lambda x: x)
    # подкосы (проекция) у коньковой стойки
    for x in ROOF["purlin_x"]:
        zt = roof_z(x) - RAFTER_V - ROOF["purlin"][1]
        d.line(x - 0.05, 7.0, x - 0.05, zt, w="thin", dash="1 1")
    d.level_mark(-1.4, 6.5, "+6,500", side="left", len_mm=8, size=2.0)
    d.level_mark(-1.4, LEVELS["eaves_rafter_top"], "+6,900", side="left", len_mm=8, size=2.0)
    d.level_mark(-1.4, ROOF["ridge_z"], "+10,650", side="left", len_mm=8, size=2.0)
    d.level_mark(-1.4, ROOF["eave_edge_z"], "+6,554", side="left", len_mm=8, size=2.0)
    d.dim_h([xw, -0.2, 3.0, 6.3, 9.6, 12.8, xe], 4.9, 8, text_size=2.0, flip_text=True)
    d.text(6.3, 11.3, "30°", size=2.5)
    d.text(1.5, 9.0, "стропило 50×200", size=1.9, rot=-30)
    d.text(3.0, 7.4, "стойка 100×150", size=1.8, rot=-90)
    d.text(6.3 + 0.5, 8.4, "коньковая стойка 100×150 (на стене оси 2)", size=1.8, rot=-90)
    d.text(9.6, 7.9, "прогон 100×250", size=1.8)
    d.text(6.3, 6.95, "минвата 250 по пароизоляции", size=1.9)
    # ведомость элементов
    xr = 340
    yy = 262
    sh.ptext(xr, yy, "Ведомость элементов стропильной системы (ориентировочно)", size=3.0, anchor="start", weight="bold")
    Ls = (xe - ROOF["ridge_x"]) / ROOF["cos"]
    rows = [
        ["Стропила 50×200, С24", f"{(n_r + 2) * 2} шт. × {Ls:.2f} м", f"{(n_r + 2) * 2 * Ls * 0.05 * 0.2:.2f} м³"],
        ["Прогоны 100×250", f"3 × {ys - yn:.1f} м", f"{3 * (ys - yn) * 0.1 * 0.25:.2f} м³"],
        ["Стойки 100×150", f"{3 * 6} шт. (1,6…3,5 м)", f"{6 * 1.6 * 2 * 0.015 + 6 * 3.5 * 0.015:.2f} м³"],
        ["Подкосы 100×100", f"{3 * 6 * 2} шт. × 1,3 м", f"{36 * 1.3 * 0.01:.2f} м³"],
        ["Лежни 150×150", f"3 × 15,2 м", f"{3 * 15.2 * 0.0225:.2f} м³"],
        ["Мауэрлат 150×150", f"2 × 15,6 м", f"{2 * 15.6 * 0.0225:.2f} м³"],
        ["Ветровые связи, доска 50×150", "8 × 7,2 м", f"{8 * 7.2 * 0.0075:.2f} м³"],
        ["Обрешётка 50×50 + контробрешётка", f"{278.7:.0f} м² ската", f"{278.7 * (1 / 0.3 + 1 / 0.6) * 0.0025:.2f} м³"],
        ["Настил ОСП-3 12 мм", "279 м²", "+10 % раскрой"],
        ["Мембрана гидроветрозащитная", "279 м²", "+15 % нахлёсты"],
        ["Крепёж: пластины, уголки, шпильки М12, гвозди", "компл.", "оцинкованные"],
    ]
    sh.table(xr, yy + 4, [("Элемент", 80, "l"), ("Количество", 60, "l"), ("Объём", 60, "l")], rows, size=2.0)
    notes = [
        "1. Древесина хвойных пород 2-го сорта (С24) по ГОСТ 8486, влажность ≤ 20 %; антисептирование и огнебиозащита (II группа) всех элементов.",
        "2. Стойки на лежнях по гидроизоляции (2 слоя рубероида); лежни к плите — анкер-болты М12 ш.1000. Коньковые стойки — над стеной оси 2.",
        "3. Стропила к мауэрлату — скользящая/жёсткая опора (уголки 90×90×65 с усилением), к прогонам — уголки; в коньке — накладки на болтах М12.",
        "4. Продольная жёсткость — подкосы 100×100 к стойкам под 45° в плоскости прогона; поперечная — ветровые связи у фронтонов и сплошной настил.",
        "5. Расчёт см. docs/03_КР: σ_стропила = 6,2 МПа ≤ 13 МПа; прогон с подкосами 3,9 МПа; стойки N ≤ N_u.",
    ]
    sh.ptext(60, 315, "Примечания", size=3.0, anchor="start", weight="bold")
    sh.ptext_lines(60, 321, notes, size=2.1, lh=3.9)
    return sh


# ============================================================================
# КР-4 — узлы
# ============================================================================
def details_sheet(sheet_no, total):
    sh = Sheet("A2", code="КР-4", title="Узлы: опирание перекрытия, карниз, стойка кровли, перемычка", scale_txt="1:20", sheet_no=sheet_no, sheets_total=total)

    def lead(d, x, z, dx, dz, txt):
        X, Y = d.P(x, z)
        d.s.pcircle(X, Y, 0.6, fill="#000", stroke=None)
        d.s.pline(X, Y, X + dx, Y + dz, w="thin")
        d.s.pline(X + dx, Y + dz, X + dx + (4 if dx >= 0 else -4), Y + dz, w="thin")
        d.s.ptext(X + dx + (1 if dx >= 0 else -1), Y + dz - 1, txt, size=2.0, anchor="start" if dx >= 0 else "end", baseline="auto")

    # ---- Узел 1: опирание перекрытия на наружную стену, перемычка окна ----
    d = sh.view(ox=95, oy=262, scale=20, flip_y=True)
    sh.ptext(40, 22, "Узел 1. Опирание плиты перекрытия на наружную стену; перемычка ПМ-3   М 1:20", size=3.6, anchor="start", weight="bold")
    # стена низ (до перемычки 2,4) — с окном
    d.rect(-0.2, 1.2, 0.2, 2.4, fill="#fff", sw="thin")   # проём окна (вид сбоку — откос)
    d.rect(-0.2 + 0.10, 1.2, -0.2 + 0.17, 2.4, fill="#2e3236", stroke=None)  # рама
    d.rect(-0.2, 2.4, 0.2, 2.65, fill="url(#hAerated)", sw="mid")   # U-блок
    d.rect(-0.15, 2.4, -0.10, 2.65, fill="url(#hInsul)", sw="thin")   # ЭППС в U-блоке
    d.rect(-0.10, 2.42, 0.15, 2.65, fill="url(#hConcrete)", sw="thin")  # ядро
    for x in (-0.06, 0.11):
        d.circle(x, 2.46, 0.9, fill="#c00", stroke=None); d.circle(x, 2.61, 0.7, fill="#c00", stroke=None)
    d.rect(-0.2, 2.65, 0.2, 3.0, fill="url(#hAerated)", sw="mid")
    # плита
    d.rect(-0.1, 3.0, 1.6, 3.2, fill="url(#hConcrete)", sw="mid")
    d.rect(-0.2, 3.0, -0.1, 3.2, fill="url(#hInsul)", sw="thin")
    d.line(-0.05, 3.03, 1.6, 3.03, w="thick", color="#c00"); d.line(-0.05, 3.17, 1.6, 3.17, w="thick", color="#c00")
    d.s.ppath(f"M{d.X(0.3):.2f} {d.Y(3.03):.2f} H{d.X(-0.05):.2f} V{d.Y(3.17):.2f} H{d.X(0.3):.2f}", stroke="#c00", sw="thick")
    d.rect(-0.2, 2.98, 0.2, 3.0, fill="#bbb", sw="thin")   # ЦПР 20
    # пол 2 этажа
    d.rect(0.2, 3.2, 1.6, 3.22, fill="url(#hInsul)", sw="thin"); d.rect(0.2, 3.22, 1.6, 3.29, fill="url(#hConcrete)", sw="thin"); d.rect(0.2, 3.29, 1.6, 3.3, fill="#ddd", sw="thin")
    # стена 2 эт.
    d.rect(-0.2, 3.2, 0.2, 4.4, fill="url(#hAerated)", sw="mid")
    d.rect(-0.2, 3.9, 0.2, 4.4, fill="#fff", sw="thin"); d.rect(-0.1, 3.9, -0.03, 4.4, fill="#2e3236", stroke=None)
    d.rect(0.2, 1.2, 0.215, 4.4, fill="#ddd", sw="thin"); d.rect(-0.21, 1.2, -0.2, 4.4, fill="#f2efe8", stroke=None)
    d.rect(0.2, 1.2, 1.6, 2.98, fill="none", stroke=None)
    d.level_mark(1.9, 3.0, "+3,000", side="right", len_mm=8, size=2.0); d.level_mark(1.9, 3.3, "+3,300", side="right", len_mm=8, size=2.0)
    d.level_mark(1.9, 2.4, "+2,400 верх проёма", side="right", len_mm=8, size=2.0)
    d.dim_h([-0.2, -0.1, 0.2], 1.1, 8, text_size=2.0, flip_text=True)
    lead(d, 0.8, 3.1, 25, -20, "плита 200 B25: низ Ø12 ш.200, верх у стены Ø10 ш.200 l=1,2 м, П-обр. Ø10 ш.200")
    lead(d, -0.15, 3.1, -22, -22, "ЭППС 100 мм — терморазрыв торца плиты")
    lead(d, 0.0, 2.99, 25, -8, "выравнивающий слой ЦПР M100 20 мм; опирание 300 мм")
    lead(d, 0.02, 2.53, 25, 6, "ПМ-3: U-блок 400 + ядро 250×200 (2Ø18 низ, 2Ø10 верх, Ø6 ш.150), ЭППС 50 снаружи")
    lead(d, -0.16, 1.8, -20, 10, "окно ПВХ 70 мм в четверти, монтаж по ГОСТ 30971 (ПСУЛ + пена + пароизоляционная лента)")
    lead(d, 0.9, 3.25, 25, -30, "пол 2 эт.: ПСБ-С 20 (звукоизоляция) + стяжка 70 с ТП + покрытие")
    lead(d, 0.0, 4.0, 25, -50, "газобетон D400 B2.5 400 мм на клею 2 мм; подоконный ряд армирован 2Ø8")

    # ---- Узел 2: карнизный узел ----
    d2 = sh.view(ox=335, oy=418, scale=20, flip_y=True)
    sh.ptext(300, 22, "Узел 2. Карнизный узел, опирание стропил   М 1:20", size=3.6, anchor="start", weight="bold")
    d2.rect(-0.2, 5.4, 0.2, 6.3, fill="url(#hAerated)", sw="mid")
    d2.rect(-0.1, 6.3, 1.8, 6.5, fill="url(#hConcrete)", sw="mid")
    d2.rect(-0.2, 6.3, -0.1, 6.5, fill="url(#hInsul)", sw="thin")
    d2.line(-0.05, 6.33, 1.8, 6.33, w="thick", color="#c00"); d2.line(-0.05, 6.47, 1.8, 6.47, w="thick", color="#c00")
    d2.rect(0.2, 6.5, 1.8, 6.75, fill="url(#hInsul)", sw="thin")
    d2.rect(-0.15, 6.5, 0.0, 6.65, fill="url(#hWood)", sw="mid")   # мауэрлат
    d2.line(-0.075, 6.2, -0.075, 6.75, w="mid", color="#c00")       # шпилька
    d2.rect(-0.2, 6.5, -0.15, 6.65, fill="url(#hInsul)", sw="thin")
    # стропило
    tan = ROOF["tan"]
    def rz(x):  # верх стропила
        return LEVELS["eaves_rafter_top"] + (x + 0.2) * tan
    pts_top = [(-0.8, rz(-0.8)), (1.8, rz(1.8))]
    pts_bot = [(1.8, rz(1.8) - RAFTER_V), (-0.8, rz(-0.8) - RAFTER_V)]
    d2.poly(pts_top + pts_bot, fill="url(#hWood)", sw="mid")
    # запил на мауэрлате
    d2.poly([(-0.15, 6.65), (0.0, 6.65), (0.0, rz(0.0) - RAFTER_V)], fill="#fff", sw="thin")
    # кровельный пирог
    d2.poly([(-0.8, rz(-0.8)), (1.8, rz(1.8)), (1.8, rz(1.8) + 0.05), (-0.8, rz(-0.8) + 0.05)], fill="#e8d3b0", sw="thin")   # контробрешётка
    d2.poly([(-0.8, rz(-0.8) + 0.05), (1.8, rz(1.8) + 0.05), (1.8, rz(1.8) + 0.10), (-0.8, rz(-0.8) + 0.10)], fill="#d9c090", sw="thin")  # обрешётка/настил
    d2.poly([(-0.85, rz(-0.85) + 0.10), (1.8, rz(1.8) + 0.10), (1.8, rz(1.8) + 0.115), (-0.85, rz(-0.85) + 0.115)], fill="#3c3f42", sw="thin")  # фальц
    # лобовая доска, софит, желоб
    d2.rect(-0.85, rz(-0.8) - RAFTER_V - 0.05, -0.8, rz(-0.8) + 0.1, fill="url(#hWood)", sw="thin")
    d2.line(-0.8, rz(-0.8) - RAFTER_V - 0.05, -0.2, rz(-0.8) - RAFTER_V - 0.05, w="mid")
    d2.circle(-0.93, rz(-0.8) - 0.02, 0.0625 * d2.k, fill="#fff", sw="mid")
    d2.rect(-0.21, 5.4, -0.2, 6.45, fill="#f2efe8", stroke=None)
    d2.rect(0.2, 5.4, 0.215, 6.3, fill="#ddd", sw="thin")
    d2.level_mark(2.1, 6.5, "+6,500", side="right", len_mm=8, size=2.0)
    d2.level_mark(2.1, LEVELS["eaves_rafter_top"], "+6,900", side="right", len_mm=8, size=2.0)
    d2.level_mark(2.1, ROOF["eave_edge_z"], "+6,554", side="right", len_mm=8, size=2.0)
    d2.dim_h([-0.8, -0.2, 0.2], 5.3, 8, text_size=2.0, flip_text=True)
    lead(d2, -0.075, 6.57, -30, 20, "мауэрлат 150×150 на шпильках М12 ш.1000, гидроизоляция; ЭППС 50 снаружи")
    lead(d2, 0.9, 6.62, 25, 30, "минвата 250 мм (2×125 вразбежку) по пароизоляции; ветрозащита сверху; продух карниза")
    lead(d2, 1.2, rz(1.2) - 0.1, 20, -20, "стропило 50×200 ш.600; запил ≤ 1/3 h; крепление уголками 90×90")
    lead(d2, 0.5, rz(0.5) + 0.11, 20, -34, "фальц 0,5 мм / настил ОСП 12 / обрешётка 50×50 / контробрешётка 50 / мембрана")
    lead(d2, -0.82, rz(-0.8) - 0.12, -20, 10, "лобовая доска 25×200, софит перфорированный (приток в чердак)")
    lead(d2, -0.93, rz(-0.8) - 0.02, -20, 24, "желоб Ø125, кронштейны ш.600, капельник")
    lead(d2, 0.8, 6.4, 25, 44, "чердачная плита 200 с обвязочным поясом; торец — ЭППС 100")

    # ---- Узел 3: стойка на лежне, подкос ----
    d3 = sh.view(ox=-40, oy=688, scale=20, flip_y=True)
    sh.ptext(40, 218, "Узел 3. Стойка кровли на лежне, подкосы, прогон   М 1:20", size=3.6, anchor="start", weight="bold")
    x = 3.0
    zt = roof_z(x) - RAFTER_V
    d3.rect(x - 1.5, 6.3, x + 1.5, 6.5, fill="url(#hConcrete)", sw="mid")
    d3.rect(x - 1.5, 6.5, x + 1.5, 6.75, fill="url(#hInsul)", sw="thin")
    d3.rect(x - 0.075, 6.5, x + 0.075, 6.65, fill="url(#hWood)", sw="mid")   # лежень (сечение) — на самом деле вдоль y; рисуем вид сбоку
    d3.rect(x - 1.5, 6.5, x + 1.5, 6.515, fill="#333", stroke=None)          # гидроизоляция под лежень (условно)
    d3.rect(x - 0.05, 6.65, x + 0.05, zt - ROOF["purlin"][1], fill="url(#hWood)", sw="mid")
    d3.rect(x - 0.05, zt - ROOF["purlin"][1], x + 0.05, zt, fill="url(#hWood)", sw="mid")
    # стропило поверх
    d3.poly([(x - 1.5, roof_z(x - 1.5)), (x + 1.5, roof_z(x + 1.5)), (x + 1.5, roof_z(x + 1.5) - RAFTER_V), (x - 1.5, roof_z(x - 1.5) - RAFTER_V)], fill="url(#hWood)", sw="mid")
    # подкосы (в плоскости прогона — показаны условно как проекция)
    d3.line(x - 0.05, 7.1, x - 0.9, zt - ROOF["purlin"][1] - 0.02, w="mid", dash="2 1")
    d3.line(x + 0.05, 7.1, x + 0.9, zt - ROOF["purlin"][1] - 0.02, w="mid", dash="2 1")
    d3.text(x, zt - ROOF["purlin"][1] - 0.25, "подкосы 100×100 (вдоль прогона), врубка + болт М12", size=1.8)
    d3.level_mark(x + 1.8, 6.5, "+6,500", side="right", len_mm=8, size=2.0)
    d3.level_mark(x + 1.8, zt, f"+{zt:.3f}".replace(".", ","), side="right", len_mm=8, size=2.0)
    lead(d3, x, 6.575, 28, 20, "лежень 150×150 на 2 слоях гидроизоляции, анкер М12 ш.1000 к плите")
    lead(d3, x, 7.4, 28, 4, "стойка 100×150 (С24), крепление к лежню уголками 90×90×2,5 с 2 сторон")
    lead(d3, x, zt - 0.12, 28, -12, "прогон 100×250, стык над стойкой, накладки 50×150 на болтах")
    lead(d3, x + 1.0, roof_z(x + 1.0) - 0.1, 20, -28, "стропила 50×200 к прогону — уголки + гвозди 4×100")

    # ---- Узел 4: перемычка ПМ-4 (монолитная) и балка над воротами ----
    d4 = sh.view(ox=360, oy=322, scale=20, flip_y=True)
    sh.ptext(300, 218, "Узел 4. Монолитная перемычка ПМ-4 над воротами/порталом (сечение)   М 1:20", size=3.6, anchor="start", weight="bold")
    d4.rect(-0.2, 0.0, 0.2, 0.30, fill="url(#hConcrete)", sw="mid")
    d4.rect(-0.2, 0.0, -0.15, 0.30, fill="url(#hInsul)", sw="thin")
    d4.rect(-0.13, 0.03, 0.17, 0.27, stroke="#c00", sw="mid")
    for x in (-0.09, 0.02, 0.13):
        d4.circle(x, 0.06, 1.0, fill="#c00", stroke=None)
    for x in (-0.09, 0.13):
        d4.circle(x, 0.24, 0.8, fill="#c00", stroke=None)
    d4.rect(-0.2, 0.30, 0.2, 0.9, fill="url(#hAerated)", sw="mid")
    d4.rect(-0.2, -0.5, 0.2, 0.0, fill="#fff", sw="thin")
    d4.text(0.0, -0.25, "проём", size=2.0)
    d4.dim_h([-0.2, -0.15, 0.2], -0.55, 8, text_size=2.0, flip_text=True)
    d4.dim_v([0.0, 0.3, 0.9], 0.2, 8, text_size=2.0)
    lead(d4, 0.02, 0.15, 25, -10, "ПМ-4 400×300 B25: низ 3Ø16, верх 2Ø10, хомуты Ø8 ш.200; опирание ≥ 300 мм")
    lead(d4, -0.175, 0.15, -18, -10, "ЭППС 50 (терморазрыв)")
    lead(d4, 0.0, 0.6, 25, -30, "кладка D400; над ПМ-4 — ряд с армированием 2Ø8")
    lead(d4, 0.0, -0.4, 25, 20, "ворота ВС-1 3000×2400 / портал ДБ-2 3000×2300; направляющие крепить к ПМ-4 и стене")
    return sh


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "drawings")
    foundation_sheet(8, 20).save(os.path.join(out, "КР-1_Фундаментная_плита.svg"))
    slab_sheet(9, 20).save(os.path.join(out, "КР-2_Перекрытие_перемычки.svg"))
    roof_struct_sheet(10, 20).save(os.path.join(out, "КР-3_Стропильная_система.svg"))
    details_sheet(11, 20).save(os.path.join(out, "КР-4_Узлы.svg"))
    print("ok")
