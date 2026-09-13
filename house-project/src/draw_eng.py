# -*- coding: utf-8 -*-
"""Инженерные разделы: ОВ-1/ОВ-2 (отопление и вентиляция), ОВ-3 (схема котельной),
ВК-1/ВК-2 (водоснабжение и канализация), ВК-3 (принципиальные схемы), ЭО-1/ЭО-2 (электрика), ЭО-3 (однолинейная схема)."""
import math
from model import *
from svg import Sheet, mm
import furniture as F
import calcs
from draw_plans import base_plan, draw_axes

R = calcs.run_all()
RED, BLUE, BROWN, GREEN, ORANGE, GREY = "#c00", "#1a5fb4", "#7a4a1a", "#2a8a3a", "#e08a00", "#666"
STACKS = {"Ст1": (10.62, 4.62), "Ст2": (5.95, 5.25), "Ст3": (0.45, 10.55)}
COLLECTORS = {1: (6.0, 3.6, "К1"), 2: (6.0, 6.2, "К2")}


def eng_sheet(code, title, floor, sheet_no, total):
    lvl = "0,000" if floor == 1 else "+3,300"
    sh = Sheet("A1", code=code, title=title, scale_txt="1:50", sheet_no=sheet_no, sheets_total=total)
    v = sh.view(ox=75, oy=95, scale=50)
    sh.ptext(470, 22, f"{title}. План на отм. {lvl}   М 1:50", size=4.6, anchor="start", weight="bold")
    base_plan(v, floor, light=True, labels=True, furniture=False, vents=True, names_only=True)
    draw_axes(v)
    v.north_arrow(15.5, -2.2)
    return sh, v


def legend_block(sh, x, y, title, items, size=2.2):
    sh.ptext(x, y, title, size=3.0, anchor="start", weight="bold")
    yy = y + 6
    for sym, txt in items:
        sym(sh, x + 5, yy)
        sh.ptext(x + 14, yy, txt, size=size, anchor="start")
        yy += 6
    return yy


# ============================================================================
# ОВ — отопление и вентиляция
# ============================================================================
def ufh_symbol(v, rect, color=RED):
    x1, y1, x2, y2 = rect
    x1 += 0.35; y1 += 0.35; x2 -= 0.35; y2 -= 0.35
    if x2 - x1 < 0.6 or y2 - y1 < 0.6:
        return
    n = max(int((y2 - y1) / 0.3), 2)
    pts = []
    for i in range(n + 1):
        y = y1 + (y2 - y1) * i / n
        pts.append((x1 if i % 2 == 0 else x2, y))
        pts.append((x2 if i % 2 == 0 else x1, y))
    v.poly(pts, closed=False, stroke=color, sw="thin")


def ov_sheet(floor, sheet_no, total):
    sh, v = eng_sheet(f"ОВ-{floor}", "Отопление и вентиляция", floor, sheet_no, total)
    H = R["heating"]
    loops = {l["n"]: l for l in H["ufh"]}
    rooms_q = {x["n"]: x for x in H["rooms"]}
    for r in ROOMS[floor]:
        rect = max(r["rects"], key=rect_area)
        if r["heated"] == "garage":
            v.rect(1.0, 0.25, 2.6, 0.35, fill=RED, stroke=RED, sw="thin")
            v.text(1.8, 0.75, "Р-1 стальной панельный 1,5 кВт (+10 °С)", size=1.8, color=RED)
            continue
        for rc in r["rects"]:
            ufh_symbol(v, rc)
        l = loops.get(r["n"])
        q = rooms_q.get(r["n"])
        if l:
            cx, cy = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
            X, Y = v.P(cx, cy)
            v.s.prect(X - 17, Y + 3.2, 34, 8.5, fill="#fff", stroke=None, opacity=0.85)
            v.s.ptext(X, Y + 5.6, f"ТП-{r['n']}: {l['length']:.0f} м, ш.{l['step']*1000:.0f}, {l['loops']} петл.", size=1.8, color=RED)
            v.s.ptext(X, Y + 9.4, f"Q = {q['Q_W']:.0f} Вт ({q['q_Wm2']:.0f} Вт/м²)", size=1.8, color=RED)
    # коллектор
    cx, cy, name = COLLECTORS[floor]
    v.rect(cx - 0.08, cy - 0.5, cx + 0.08, cy + 0.5, fill="#fff", stroke=RED, sw="mid")
    v.line(cx - 0.05, cy - 0.5, cx - 0.05, cy + 0.5, w="mid", color=BLUE)
    n_out = H["loops_1"] if floor == 1 else H["loops_2"]
    v.text_mm(cx, cy, -9, 0, f"{name}: {n_out} вых., смесит. узел, насос 25-60", size=1.8, rot=-90, color=RED)
    if floor == 1:
        # котельная
        v.rect(4.4, 0.25, 4.9, 0.65, fill="#fff", stroke=RED, sw="mid"); v.text(4.65, 0.45, "К", size=2.2, color=RED)
        v.text(4.65, 0.95, "котёл 32 кВт", size=1.7, color=RED)
        v.circle(5.3, 1.6, 0.3 * v.k, fill="#fff", stroke=RED, sw="mid"); v.text(5.3, 1.6, "БКН 200", size=1.7, color=RED)
        v.rect(4.2, 2.2, 4.9, 2.8, fill="#fff", stroke=BLUE, sw="mid"); v.text(4.55, 2.5, "ВО", size=1.8, color=BLUE)
        v.circle(5.9, 1.2, 0.2 * v.k, fill="#fff", stroke=RED, sw="thin"); v.text(5.9, 1.2, "РБ", size=1.5, color=RED)
        v.circle(ROOF["flue_x"], -0.2, 1.6, fill="#fff", sw="mid"); v.text(ROOF["flue_x"], -0.75, "дымоход Ø60/100", size=1.6)
        v.line(4.9, 0.45, 5.9, 0.45, w="mid", color=RED); v.line(4.9, 0.55, 5.6, 0.55, w="mid", color=BLUE)
        v.line(5.6, 0.55, 5.6, 1.3, w="mid", color=BLUE); v.line(5.9, 0.45, 5.9, 1.0, w="mid", color=RED)
        v.text(5.2, 2.05, "гидрострелка + группа безопасности", size=1.5, color=RED)
        # магистрали от котельной к коллектору К1 (через хозяйственную)
        v.poly([(5.6, 2.9), (5.6, 3.6), (6.0, 3.6)], closed=False, stroke=RED, sw="mid")
        v.poly([(5.5, 2.9), (5.5, 3.5), (5.92, 3.5)], closed=False, stroke=BLUE, sw="mid")
        v.text(5.2, 3.3, "2×Ø32 PP-R", size=1.5, rot=-90, color=RED)
        # стояк к К2 (2 этаж) в шахте В2
        v.circle(6.0, 4.5, 1.2, fill="#fff", stroke=RED, sw="mid"); v.text(6.0, 5.4, "ст. отопл. 2×Ø25 → К2", size=1.5, color=RED)
    else:
        v.circle(6.0, 4.5, 1.2, fill="#fff", stroke=RED, sw="mid"); v.text(6.0, 5.4, "ст. отопл. 2×Ø25 из 1.12", size=1.5, color=RED)
    # вентиляция: решётки на шахтах
    vent = {x[0]: x for x in R["ventilation"]["exhaust"]}
    for x1, y1, x2, y2, name, desc, floors in VENT_SHAFTS:
        if floor in floors:
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            X, Y = v.P(cx, cy)
            v.s.prect(X - 2.2, Y - 2.2, 4.4, 4.4, fill="#fff", stroke=GREEN, sw="mid")
            v.s.pline(X - 2.2, Y - 2.2, X + 2.2, Y + 2.2, w="thin", color=GREEN); v.s.pline(X + 2.2, Y - 2.2, X - 2.2, Y + 2.2, w="thin", color=GREEN)
            e = vent.get(name)
            side = 1 if cx < 6.3 else -1
            v.text_mm(cx, cy, side * 4, 6, f"{name} {e[3].split(' ')[0] if e else ''} {e[2]:.0f} м³/ч" if e else name, size=1.6, color=GREEN, anchor="start" if side > 0 else "end")
    if floor == 1:
        v.rect(2.5, 10.4, 3.3, 10.9, fill="#fff", stroke=GREEN, sw="mid"); v.text(2.9, 11.3, "зонт 400 м³/ч → В4 Ø150", size=1.6, color=GREEN)
        v.line(3.3, 10.65, 5.775, 10.55, w="mid", color=GREEN, dash="2 1")
        v.rect(1.0, -0.15, 3.1, -0.05, fill=GREEN, stroke=None); v.text(2.05, -0.5, "приточная решётка в воротах 0,05 м²", size=1.6, color=GREEN)
        v.rect(7.2, 15.35, 7.8, 15.45, fill=GREEN, stroke=None); v.text(7.5, 15.05, "стеновой клапан Ø125", size=1.5, color=GREEN)
    # приточные клапаны на окнах жилых комнат
    for s, a1, a2, h, sill, tag in WINDOWS[floor]:
        if tag in ("ОК-4", "ОК-4б", "ОК-5", "ОК-8"):
            continue
        if s == "N": X, Y = v.P((a1 + a2) / 2, 0.45)
        elif s == "S": X, Y = v.P((a1 + a2) / 2, 15.15)
        elif s == "W": X, Y = v.P(0.45, (a1 + a2) / 2)
        else: X, Y = v.P(12.15, (a1 + a2) / 2)
        v.s.ppoly([(X - 1.5, Y - 1.3), (X + 1.5, Y - 1.3), (X, Y + 1.3)], fill=GREEN, stroke=None)
    # кондиционеры
    ac = {1: [((11.9, 9.2, 12.4, 9.35), (12.9, 8.5, 13.5, 9.4), "СК-1")],
          2: [((0.2, 11.9, 0.7, 12.05), (-0.9, 11.0, -0.3, 11.9), "СК-2"), ((0.2, 3.1, 0.7, 3.25), (-0.9, 3.4, -0.3, 4.3), "СК-3")]}
    for inner, outer, name in ac[floor]:
        v.rect(*inner, fill="#fff", stroke=ORANGE, sw="mid"); v.rect(*outer, fill="#fff", stroke=ORANGE, sw="mid")
        v.text((outer[0] + outer[2]) / 2, outer[3] + 0.4, name, size=1.7, color=ORANGE)
    # правая колонка: таблица петель, легенда, примечания
    xr = 470
    yy = 40
    sh.ptext(xr, yy, f"Петли тёплого пола, {floor}-й этаж (коллектор {COLLECTORS[floor][2]})", size=3.0, anchor="start", weight="bold")
    rows = []
    for l in H["ufh"]:
        if l["floor"] == floor:
            q = rooms_q[l["n"]]
            rows.append([l["n"], l["name"], f"{l['area']:.1f}".replace(".", ","), f"{q['Q_W']:.0f}", f"{l['step']*1000:.0f}", f"{l['length']:.0f}", str(l["loops"])])
    tot_L = sum(l["length"] for l in H["ufh"] if l["floor"] == floor)
    rows.append(["", "Итого", "", "", "", f"{tot_L:.0f}", str(H["loops_1"] if floor == 1 else H["loops_2"])])
    yy = sh.table(xr, yy + 4, [("№", 12, "c"), ("Помещение", 52, "l"), ("S, м²", 16, "r"), ("Q, Вт", 16, "r"), ("Шаг", 12, "c"), ("L, м", 14, "r"), ("Петель", 14, "c")], rows, size=2.0)
    yy += 8
    def s_ufh(sh, x, y): sh.pline(x - 4, y, x + 4, y, w="thin", color=RED); sh.pline(x - 4, y + 1.5, x + 4, y + 1.5, w="thin", color=RED)
    def s_col(sh, x, y): sh.prect(x - 1, y - 3, 2, 6, fill="#fff", stroke=RED, sw="mid")
    def s_vent(sh, x, y): sh.prect(x - 2, y - 2, 4, 4, stroke=GREEN, sw="mid"); sh.pline(x - 2, y - 2, x + 2, y + 2, w="thin", color=GREEN); sh.pline(x + 2, y - 2, x - 2, y + 2, w="thin", color=GREEN)
    def s_sup(sh, x, y): sh.ppoly([(x - 1.5, y - 1.3), (x + 1.5, y - 1.3), (x, y + 1.3)], fill=GREEN, stroke=None)
    def s_rad(sh, x, y): sh.prect(x - 4, y - 0.7, 8, 1.4, fill=RED, stroke=None)
    def s_ac(sh, x, y): sh.prect(x - 3, y - 1.5, 6, 3, stroke=ORANGE, sw="mid")
    yy = legend_block(sh, xr, yy, "Условные обозначения", [
        (s_ufh, "контур водяного тёплого пола PE-Xa 16×2,0, шаг 150 (100 в санузлах), в стяжке"),
        (s_col, "коллекторный шкаф К1/К2 с расходомерами, сервоприводами и смесительным узлом"),
        (s_vent, "вытяжная решётка на вентканале (естественная вытяжка, канал Ø125/Ø160 в шахте)"),
        (s_sup, "приточный оконный клапан 30–35 м³/ч (ПВХ-профиль)"),
        (s_rad, "стальной панельный радиатор (гараж) с термоголовкой"),
        (s_ac, "сплит-система (внутренний / наружный блок), трасса в штробе, дренаж в канализацию"),
    ])
    Hh = R["heating"]
    notes = [
        f"1. Расчётная тепловая нагрузка дома {Hh['Q_total']:.1f} кВт (трансмиссия {Hh['Q_tr']:.1f} + вентиляция {Hh['Q_vent']:.1f}); котёл конденсационный 32 кВт, одноконтурный, + БКН 200 л.",
        "2. Отопление — водяной тёплый пол во всех помещениях, график 40/33 °С; смесительные узлы на К1, К2; погодозависимая автоматика котла; комнатные термостаты → сервоприводы.",
        "3. Магистрали PP-R PN20 Ø32/25 в изоляции, стояк к К2 — в шахте В2. Заполнение системы — подготовленной водой, давление 1,5 бар, группа безопасности 3 бара, РБ 35 л.",
        "4. Стяжка над трубами ТП ≥ 45 мм (1 эт. — 120 мм общая, 2 эт. — 70 мм), демпферная лента по периметру, деформационные швы по дверным проёмам.",
        "5. Вентиляция — естественная вытяжная через каналы В1…В7 (выше конька), приток через оконные клапаны и стеновой клапан; кухонный зонт 400 м³/ч в отдельный канал Ø150.",
        f"6. Вариант с ПВУ (рекуперация ≥ 75 %, {R['ventilation']['hrv']['L']} м³/ч) снижает нагрузку до {Hh['Q_total_hrv']:.1f} кВт; установка в чердаке (утеплённый бокс), воздуховоды по чердаку.",
        "7. Полотенцесушители — электрические 300 Вт в санузлах 1.05, 2.03, 2.08, 2.11. Котельная и гараж — см. ОВ-3 (схема котельной).",
    ]
    sh.ptext(xr, yy + 6, "Примечания", size=3.0, anchor="start", weight="bold")
    sh.ptext_lines(xr, yy + 12, notes, size=2.1, lh=4.0)
    return sh


def boiler_scheme_sheet(sheet_no, total):
    sh = Sheet("A3", code="ОВ-3", title="Принципиальная схема котельной и системы отопления", scale_txt="б/м", sheet_no=sheet_no, sheets_total=total)
    sh.ptext(30, 20, "Принципиальная схема котельной (тепломеханическая)", size=4.5, anchor="start", weight="bold")

    def box(x, y, w, h, txt, col="#000", size=2.4, fill="#fff"):
        sh.prect(x, y, w, h, fill=fill, stroke=col, sw="mid")
        lines = txt.split("\n")
        for i, ln in enumerate(lines):
            sh.ptext(x + w / 2, y + h / 2 + (i - (len(lines) - 1) / 2) * 3.2, ln, size=size, color=col)

    def pipe(pts, col, w="thick", dash=None, arrow=False):
        for i in range(len(pts) - 1):
            sh.pline(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], w=w, color=col, dash=dash, marker=("arrow" if (arrow and i == len(pts) - 2) else None))

    # газ
    box(30, 60, 30, 14, "Газопровод\nввод от ГРПШ", GREEN)
    box(70, 60, 22, 14, "Счётчик G4\n+ кран", GREEN)
    box(100, 60, 26, 14, "Клапан эл.магн.\n+ сигнализатор CH4/CO", GREEN, size=2.0)
    pipe([(60, 67), (70, 67)], GREEN); pipe([(92, 67), (100, 67)], GREEN); pipe([(126, 67), (150, 67), (150, 100)], GREEN, arrow=True)
    # котёл
    box(135, 100, 30, 40, "Котёл\nконденсационный\n32 кВт\nмодуляция 4–32", RED, size=2.2)
    box(135, 143, 30, 8, "дымоход Ø60/100", GREY, size=1.9)
    # гидрострелка
    box(195, 95, 10, 60, "", RED)
    sh.ptext(200, 90, "Гидрострелка", size=2.2)
    pipe([(165, 110), (195, 110)], RED, arrow=True); pipe([(195, 140), (165, 140)], BLUE, arrow=True)
    box(172, 104, 12, 8, "Н1", RED, size=2.0); sh.ptext(178, 100, "насос котла", size=1.8)
    box(150, 150, 28, 10, "группа безоп. 3 бар\nманометр, возд.", GREY, size=1.7)
    box(120, 118, 14, 14, "РБ\n35 л", RED, size=2.0); pipe([(134, 125), (135, 125)], RED)
    box(105, 100, 24, 10, "подпитка\nчерез ВО", BLUE, size=1.8); pipe([(129, 105), (135, 105)], BLUE)
    # контуры
    circuits = [("К1 — тёплый пол 1 эт.\n" + f"{R['heating']['loops_1']} петель, 40/33 °С", 225, 60), ("К2 — тёплый пол 2 эт.\n" + f"{R['heating']['loops_2']} петель, 40/33 °С", 225, 100), ("Р-1 радиатор гаража\n(прямой контур 70/50)", 225, 140)]
    for txt, x, y in circuits:
        box(x + 40, y, 60, 22, txt, RED, size=2.0)
        box(x, y + 3, 30, 16, "смесит. узел\nнасос 25-60\n3-х ход. клапан", RED, size=1.7)
        pipe([(205, y + 8), (225, y + 8)], RED, arrow=True); pipe([(255, y + 8), (265, y + 8)], RED, arrow=True)
        pipe([(265, y + 16), (255, y + 16)], BLUE, arrow=True); pipe([(225, y + 16), (205, y + 16)], BLUE, arrow=True)
    # ГВС
    box(225, 180, 40, 30, "БКН 200 л\nзмеевик 30 кВт\nТЭН 3 кВт (резерв)", RED, size=2.0)
    pipe([(205, 150), (215, 150), (215, 188), (225, 188)], RED, arrow=True); pipe([(225, 202), (210, 202), (210, 154), (205, 154)], BLUE, arrow=True)
    box(212, 170, 14, 8, "Н4", RED, size=1.8); sh.ptext(219, 166, "приоритет ГВС", size=1.7)
    # водоснабжение
    box(30, 190, 36, 14, "Скважина\nнасос 3 м³/ч, 60 м", BLUE, size=2.0)
    box(76, 190, 26, 14, "ГА 100 л\nреле 2,5/4 бар", BLUE, size=1.9)
    box(112, 190, 24, 14, "фильтр\n100 мкм", BLUE, size=1.9)
    box(146, 190, 30, 14, "ВО: аэрация,\nобезжелез., умягч.", BLUE, size=1.8)
    box(186, 190, 24, 14, "УФ +\nсчётчик", BLUE, size=1.9)
    pipe([(66, 197), (76, 197)], BLUE); pipe([(102, 197), (112, 197)], BLUE); pipe([(136, 197), (146, 197)], BLUE); pipe([(176, 197), (186, 197)], BLUE)
    pipe([(210, 197), (225, 197)], BLUE, arrow=True)
    pipe([(210, 197), (218, 197), (218, 230), (300, 230)], BLUE, arrow=True); sh.ptext(300, 226, "ХВС → коллекторы 1.12 / 2.09", size=2.0, anchor="end", color=BLUE)
    pipe([(265, 195), (300, 195)], RED, arrow=True); sh.ptext(300, 191, "ГВС 60 °С → коллекторы", size=2.0, anchor="end", color=RED)
    pipe([(300, 212), (275, 212), (275, 205)], ORANGE, w="mid", arrow=True); sh.ptext(300, 216, "рециркуляция ГВС, насос Н5 (таймер)", size=1.8, anchor="end", color=ORANGE)
    # легенда
    yy = 250
    for col, txt in ((RED, "подающий трубопровод / ГВС"), (BLUE, "обратный трубопровод / ХВС"), (GREEN, "газопровод"), (ORANGE, "рециркуляция ГВС")):
        sh.pline(30, yy, 45, yy, w="thick", color=col); sh.ptext(48, yy, txt, size=2.2, anchor="start"); yy += 5
    notes = [
        "Автоматика: погодозависимый контроллер котла (уличный датчик), приоритет ГВС, комнатные термостаты по помещениям (проводные), защита от замерзания.",
        "Электропитание котельной — через стабилизатор и ИБП (1 кВА, 30 мин) от отдельной группы; заземление котла и труб. Слив в трап Ø50 (котельная 1.13).",
        "Резерв: электрокотёл 9 кВт (опция) параллельно газовому; при отключении газа — ТЭН бойлера 3 кВт.",
    ]
    sh.ptext_lines(30, yy + 4, notes, size=2.1, lh=4.0)
    return sh


# ============================================================================
# ВК — водоснабжение и канализация
# ============================================================================
def vk_sheet(floor, sheet_no, total):
    sh, v = eng_sheet(f"ВК-{floor}", "Водоснабжение и канализация", floor, sheet_no, total)
    # санприборы
    if floor == 1:
        F.wc(v, 11.9, 6.1, "N"); F.basin(v, 12.4, 4.9, orient="W"); F.shower(v, 10.55, 5.2, 0.85)
        F.washer(v, 4.2, 3.1); F.washer(v, 4.85, 3.1); F.basin(v, 5.9, 3.0, orient="S")
        F.counter(v, 0.2, 10.35, 0.8, 15.0, sink=(0.5, 12.3)); v.rect(0.8, 10.35, 1.4, 10.95, stroke=GREY, sw="thin"); v.text(1.1, 10.65, "ПМ", size=1.6, color=GREY)
        v.rect(4.2, 2.2, 4.9, 2.8, fill="#fff", stroke=BLUE, sw="mid"); v.text(4.55, 2.5, "ВО", size=1.8, color=BLUE)
        v.circle(5.3, 1.6, 0.3 * v.k, fill="#fff", stroke=RED, sw="mid"); v.text(5.3, 1.6, "БКН", size=1.7, color=RED)
        v.rect(4.4, 0.25, 4.9, 0.65, fill="#fff", stroke=RED, sw="mid"); v.text(4.65, 0.45, "К", size=2.0, color=RED)
        v.circle(4.4, 0.5, 1.8, fill="#fff", stroke=BLUE, sw="mid"); v.text(3.9, 0.9, "В1 ввод ПНД Ø32", size=1.6, color=BLUE)
        v.rect(5.0, 2.2, 5.4, 2.8, fill="#fff", stroke=BLUE, sw="thin"); v.text(5.2, 2.5, "ГА", size=1.6, color=BLUE)
        v.circle(4.3, 2.75, 1.3, fill="#fff", stroke=BROWN, sw="thin"); v.text(4.0, 2.4, "трап Ø50", size=1.4, color=BROWN)
        v.circle(12.6, 10.4, 1.8, fill="#fff", stroke=BROWN, sw="mid"); v.text(13.9, 10.9, "К1 выпуск Ø110, −1,100", size=1.6, color=BROWN, anchor="start")
        v.circle(0.45, 15.0, 1.4, fill="#fff", stroke=BLUE, sw="thin"); v.text(1.5, 15.05, "поливочный кран", size=1.4, color=BLUE, anchor="start")
        v.circle(12.2, 15.0, 1.4, fill="#fff", stroke=BLUE, sw="thin"); v.text(11.2, 15.05, "поливочный кран", size=1.4, color=BLUE, anchor="end")
    else:
        F.bath(v, 0.25, 4.65); F.shower(v, 0.22, 6.8, 0.8); F.wc(v, 2.85, 8.0, "N"); F.basin(v, 3.2, 6.2, orient="W")
        F.washer(v, 3.35, 4.65); F.washer(v, 4.0, 4.65); F.basin(v, 5.0, 4.6, orient="S")
        F.bath(v, 10.55, 6.0); F.wc(v, 11.9, 4.0, "S"); F.basin(v, 12.4, 5.2, orient="W")
        F.shower(v, 0.25, 9.55, 0.9); F.wc(v, 1.75, 9.5, "S"); F.basin(v, 0.2, 11.0, orient="E")
    # стояки
    for name, (x, y) in STACKS.items():
        v.circle(x, y, 0.055 * v.k, fill="#fff", stroke=BROWN, sw="thick")
        v.text_mm(x, y, 0, -4.5, f"{name} Ø110", size=1.8, color=BROWN, weight="bold")
        v.circle(x + 0.25, y, 0.6, fill=BLUE, stroke=None); v.circle(x + 0.45, y, 0.6, fill=RED, stroke=None)
    # коллекторы ХВС/ГВС
    cx, cy, name = COLLECTORS[floor]
    cy += 1.3
    v.rect(cx - 0.08, cy - 0.35, cx + 0.08, cy + 0.35, fill="#fff", stroke=BLUE, sw="mid")
    v.text_mm(cx, cy, -8, 0, f"коллекторы ХВС/ГВС {floor} эт. (гребёнки ×8)", size=1.7, rot=-90, color=BLUE)
    # трассы (упрощённо): ХВС синий, ГВС красный — к группам приборов; канализация — к стоякам
    if floor == 1:
        routes = [
            ([(6.0, 4.9), (6.0, 3.6), (5.6, 3.6), (5.6, 2.9), (5.3, 1.9)], BLUE, "к БКН"),
            ([(5.3, 1.3), (5.6, 1.3), (5.6, 4.9), (6.0, 4.9)], RED, ""),
            ([(6.0, 5.2), (6.4, 5.2), (6.4, 8.3), (10.0, 8.3), (10.0, 4.6), (10.45, 4.6)], BLUE, "к 1.05"),
            ([(6.0, 5.3), (6.4, 5.3), (6.4, 8.4), (10.1, 8.4), (10.1, 4.7), (10.45, 4.7)], RED, ""),
            ([(6.0, 5.1), (5.0, 5.1), (5.0, 3.4)], BLUE, "к СМ"),
            ([(6.0, 5.4), (6.0, 8.5), (6.0, 10.5), (1.0, 10.5), (0.7, 12.2)], BLUE, "к мойке/ПМ"),
            ([(5.9, 5.5), (5.9, 10.6), (1.1, 10.6), (0.8, 12.3)], RED, ""),
        ]
        sew = [
            ([(11.9, 6.0), (10.9, 4.9), (10.62, 4.62)], "Ø110"), ([(12.1, 4.9), (10.62, 4.62)], "Ø50"), ([(10.9, 5.6), (10.62, 4.62)], "Ø50"),
            ([(4.5, 3.4), (5.95, 5.25)], "Ø50"), ([(5.9, 3.3), (5.95, 5.25)], "Ø50"), ([(4.3, 2.75), (5.95, 5.25)], "Ø50"),
            ([(0.5, 12.3), (0.45, 10.55)], "Ø50"), ([(1.1, 10.7), (0.45, 10.55)], "Ø50"),
        ]
    else:
        routes = [
            ([(6.0, 7.5), (5.5, 7.5), (5.5, 5.0), (5.0, 5.0)], BLUE, "к 2.09"),
            ([(6.0, 7.6), (5.6, 7.6), (5.6, 5.1), (4.9, 5.1)], RED, ""),
            ([(6.0, 7.4), (3.35, 7.4), (3.35, 6.2), (2.0, 6.2), (1.0, 5.5)], BLUE, "к 2.08"),
            ([(6.0, 7.3), (3.45, 7.3), (3.45, 6.3), (2.1, 6.3), (1.1, 5.6)], RED, ""),
            ([(6.0, 7.8), (6.4, 7.8), (6.4, 8.7), (10.1, 8.7), (10.1, 5.2), (10.45, 5.2)], BLUE, "к 2.03"),
            ([(6.0, 7.9), (6.5, 7.9), (6.5, 8.8), (10.2, 8.8), (10.2, 5.3), (10.45, 5.3)], RED, ""),
            ([(6.0, 7.7), (4.8, 7.7), (4.8, 8.7), (1.0, 8.7), (1.0, 9.9)], BLUE, "к 2.11"),
            ([(5.9, 7.65), (4.9, 7.65), (4.9, 8.8), (1.1, 8.8), (1.1, 9.9)], RED, ""),
        ]
        sew = [
            ([(2.85, 7.6), (5.95, 5.25)], "Ø110"), ([(1.0, 5.0), (5.95, 5.25)], "Ø50"), ([(2.9, 6.2), (5.95, 5.25)], "Ø50"), ([(3.65, 5.0), (5.95, 5.25)], "Ø50"),
            ([(11.9, 4.6), (10.62, 4.62)], "Ø110"), ([(12.0, 5.2), (10.62, 4.62)], "Ø50"), ([(11.0, 6.2), (10.62, 4.62)], "Ø50"),
            ([(1.75, 10.1), (0.45, 10.55)], "Ø110"), ([(0.7, 11.0), (0.45, 10.55)], "Ø50"), ([(0.7, 10.0), (0.45, 10.55)], "Ø50"),
        ]
    for pts, col, lbl in routes:
        v.poly(pts, closed=False, stroke=col, sw="mid")
        if lbl:
            v.text(pts[-1][0], pts[-1][1] - 0.25, lbl, size=1.4, color=col)
    for pts, lbl in sew:
        v.poly(pts, closed=False, stroke=BROWN, sw="mid", dash="3 1")
    # правая колонка
    xr = 470
    yy = 40
    sh.ptext(xr, yy, f"Ведомость санитарно-технических приборов, {floor}-й этаж", size=3.0, anchor="start", weight="bold")
    fx = {1: [["Унитаз подвесной с инсталляцией", "1"], ["Умывальник", "2"], ["Душевой уголок 900×900", "1"], ["Мойка кухонная + ПМ", "1+1"], ["Стиральная машина", "2"], ["Трап Ø50 (котельная)", "1"], ["Поливочный кран", "2"]],
          2: [["Унитаз подвесной с инсталляцией", "3"], ["Умывальник", "3"], ["Ванна 1700×750", "2"], ["Душевой уголок", "2"], ["Стиральная + сушильная машина", "1+1"], ["Полотенцесушитель эл.", "3"]]}
    yy = sh.table(xr, yy + 4, [("Прибор", 90, "l"), ("шт.", 20, "c")], fx[floor], size=2.2)
    yy += 8
    def s_cold(sh, x, y): sh.pline(x - 5, y, x + 5, y, w="mid", color=BLUE)
    def s_hot(sh, x, y): sh.pline(x - 5, y, x + 5, y, w="mid", color=RED)
    def s_sew(sh, x, y): sh.pline(x - 5, y, x + 5, y, w="mid", color=BROWN, dash="3 1")
    def s_stack(sh, x, y): sh.pcircle(x, y, 2.5, fill="#fff", stroke=BROWN, sw="thick")
    def s_coll(sh, x, y): sh.prect(x - 1, y - 3, 2, 6, fill="#fff", stroke=BLUE, sw="mid")
    yy = legend_block(sh, xr, yy, "Условные обозначения", [
        (s_cold, "трубопровод ХВС — PP-R PN20 / PEX Ø16–25 в изоляции 6 мм, в стяжке (в защитной гофре)"),
        (s_hot, "трубопровод ГВС — PP-R PN25 (армир.) / PEX Ø16–25 в изоляции 9 мм; рециркуляция Ø16"),
        (s_sew, "канализация ПП Ø50 (уклон 0,035) / Ø110 (уклон 0,02), отводы 45°, ревизии"),
        (s_stack, "канализационный стояк Ø110 с вентиляционной частью в шахте (Ст3 — с вакуумным клапаном)"),
        (s_coll, "коллекторы ХВС/ГВС с запорными кранами по каждому прибору"),
    ])
    Wt = R["water"]
    notes = [
        f"1. Расход воды: {Wt['q_day']:.1f} м³/сут ({Wt['people']} чел.), расчётный секундный расход {Wt['q_s']:.2f} л/с. Источник — скважина с насосом {Wt['pump']['Q']} м³/ч / {Wt['pump']['H']} м, ГА 100 л.",
        "2. Водоподготовка (по анализу воды): грубая очистка 100 мкм, обезжелезивание/умягчение, УФ. ГВС — БКН 200 л с рециркуляцией.",
        "3. Разводка коллекторная (лучевая) в стяжке пола; подводки к приборам Ø16, стояки ХВС/ГВС Ø25 в шахте В2 (1.12 → 2.09).",
        "4. Канализация: 3 стояка Ø110 ПП, вентиляционные выходы Ст1, Ст2 через кровлю (в шахтах В3, В2), Ст3 — вакуумный клапан; ревизии на каждом стояке.",
        "5. Выпуск Ø110 через гильзу в плите на отм. −1,100 → колодец → СБО (8 усл. жит.) → дренажный колодец. Наружный участок — в утеплителе/с греющим кабелем (выше глубины промерзания).",
        "6. Мокрые зоны — обмазочная гидроизоляция с заведением на стены 200 мм (ванные — 1500 мм у душа), трапы в душевых уголках.",
        "7. Наружный водопровод от скважины — ПНД Ø32 на глубине 1,6 м; ввод через гильзу с уплотнением; на вводе — кран, фильтр, обратный клапан, счётчик.",
    ]
    sh.ptext(xr, yy + 6, "Примечания", size=3.0, anchor="start", weight="bold")
    sh.ptext_lines(xr, yy + 12, notes, size=2.1, lh=4.0)
    return sh


def vk_scheme_sheet(sheet_no, total):
    sh = Sheet("A3", code="ВК-3", title="Принципиальные схемы водоснабжения и канализации", scale_txt="б/м", sheet_no=sheet_no, sheets_total=total)
    sh.ptext(30, 20, "Принципиальная схема водоснабжения", size=4.2, anchor="start", weight="bold")

    def box(x, y, w, h, txt, col="#000", size=2.2):
        sh.prect(x, y, w, h, fill="#fff", stroke=col, sw="mid")
        lines = txt.split("\n")
        for i, ln in enumerate(lines):
            sh.ptext(x + w / 2, y + h / 2 + (i - (len(lines) - 1) / 2) * 3.0, ln, size=size, color=col)

    def link(x1, y1, x2, y2, col, dash=None):
        sh.pline(x1, y1, x2, y2, w="thick", color=col, dash=dash, marker="arrow")

    chain = [("Скважина 50–60 м\nнасос 3 м³/ч, 60 м, 1,1 кВт", BLUE), ("Кессон Ø1,5 м\nоголовок, кран, обр. клапан", BLUE), ("Ввод ПНД Ø32\nглубина 1,6 м, гильза", BLUE),
             ("Реле давления 2,5/4 бар\nГА 100 л, манометр", BLUE), ("Фильтр 100 мкм\nсчётчик ХВС", BLUE), ("Водоподготовка\nаэрация + обезжелезивание\n+ умягчение + УФ", BLUE),
             ("Коллектор ХВС 1.12\n(8 выходов)", BLUE)]
    x = 30
    for i, (txt, col) in enumerate(chain):
        box(x, 40, 44, 22, txt, col, size=1.9)
        if i < len(chain) - 1:
            link(x + 44, 51, x + 52, 51, col)
        x += 52
    box(342, 40, 44, 22, "Коллектор ХВС 2.09\n(стояк Ø25 в В2)", BLUE, size=1.9)
    link(x - 52 + 22, 62, x - 52 + 22, 75, BLUE); box(x - 52 - 20, 75, 84, 20, "Потребители 1 этажа: кухня, санузел 1.05, хозяйственная 1.12, поливочные краны, подпитка отопления", BLUE, size=1.8)
    link(342 + 22, 62, 342 + 22, 75, BLUE); box(342 - 10, 75, 64, 20, "Потребители 2 этажа:\nсанузлы 2.03, 2.08, 2.11, постирочная 2.09", BLUE, size=1.8)
    # ГВС
    box(30, 110, 60, 22, "БКН 200 л (котельная)\nзмеевик от котла, ТЭН 3 кВт", RED, size=1.9)
    link(90, 121, 120, 121, RED); box(120, 110, 50, 22, "Коллектор ГВС 1.12", RED, size=1.9)
    link(170, 121, 200, 121, RED); box(200, 110, 50, 22, "Коллектор ГВС 2.09", RED, size=1.9)
    link(250, 128, 90, 128, ORANGE); sh.ptext(170, 136, "рециркуляция Ø16, насос по таймеру, обратный клапан", size=1.8, color=ORANGE)
    sh.pline(60, 62, 60, 110, w="thick", color=BLUE, marker="arrow"); sh.ptext(63, 90, "ХВС в БКН (предохр. клапан 6 бар, РБ ГВС 12 л)", size=1.8, anchor="start", color=BLUE)
    # канализация
    sh.ptext(30, 160, "Принципиальная схема канализации", size=4.2, anchor="start", weight="bold")
    stacks = [("Ст1 Ø110\nсанузлы 1.05, 2.03\nвент. выход в В3", 30), ("Ст2 Ø110\n1.12, 2.08, 2.09\nвент. выход в В2", 90), ("Ст3 Ø110\nкухня 1.08, санузел 2.11\nвакуумный клапан", 150)]
    for txt, x in stacks:
        box(x, 175, 50, 24, txt, BROWN, size=1.8)
        link(x + 25, 199, x + 25, 212, BROWN)
    box(30, 212, 170, 12, "Лежак Ø110 под плитой, i = 0,02, ревизии; выпуск через гильзу, лоток −1,100", BROWN, size=1.9)
    link(200, 218, 225, 218, BROWN); box(225, 206, 40, 24, "Колодец Ø1,0\nповоротный", BROWN, size=1.9)
    link(265, 218, 290, 218, BROWN); box(290, 206, 50, 24, "СБО 8 усл. жит.\n1,6 м³/сут, аэрация\nэл. 0,3 кВт", BROWN, size=1.8)
    link(340, 218, 360, 218, BROWN); box(360, 206, 50, 24, "Дренажный колодец\nØ1,0 (2 кольца) /\nкювет", BROWN, size=1.8)
    box(225, 240, 100, 14, "Ливневая: 6 водосточных труб → Ø110 → дождеприёмный колодец + дренажное поле", "#3a8fb7", size=1.8)
    notes = ["Материалы: ПП внутренняя (Ostendorf/аналог), НПВХ SN4 наружная; уклоны Ø50 — 0,035, Ø110 — 0,02; наружный участок 20 м с утеплением ППУ-скорлупой.",
             "Обслуживание СБО — откачка ила 1–2 раза в год; расстояние до скважины 30 м, до дома 6,2 м, до границ ≥ 2 м."]
    sh.ptext_lines(30, 262, notes, size=2.0, lh=4.0)
    return sh


# ============================================================================
# ЭО — электрооборудование
# ============================================================================
def lamp(v, x, y):
    X, Y = v.P(x, y)
    v.s.pcircle(X, Y, 1.6, fill="#fff", stroke="#000", sw="mid")
    v.s.pline(X - 1.1, Y - 1.1, X + 1.1, Y + 1.1, w="mid"); v.s.pline(X + 1.1, Y - 1.1, X - 1.1, Y + 1.1, w="mid")


def switch(v, x, y, n=1):
    X, Y = v.P(x, y)
    v.s.pcircle(X, Y, 1.0, fill="#000", stroke=None)
    v.s.pline(X, Y, X + 2.2, Y - 2.2, w="mid")
    v.s.pline(X + 2.2, Y - 2.2, X + 1.4, Y - 2.6, w="mid")
    if n == 2:
        v.s.pline(X + 1.7, Y - 1.7, X + 0.9, Y - 2.1, w="mid")


def socket(v, x, y, wall="N", label=None):
    X, Y = v.P(x, y)
    if wall in ("N", "S"):
        d = 1 if wall == "N" else -1
        v.s.ppath(f"M{X-1.6:.2f} {Y:.2f} A1.6 1.6 0 0 {1 if d>0 else 0} {X+1.6:.2f} {Y:.2f}", sw="mid", fill="#fff")
        v.s.pline(X, Y + d * 1.6, X, Y + d * 3.0, w="mid"); v.s.pline(X - 1.6, Y + d * 3.0, X + 1.6, Y + d * 3.0, w="mid")
    else:
        d = 1 if wall == "W" else -1
        v.s.ppath(f"M{X:.2f} {Y-1.6:.2f} A1.6 1.6 0 0 {1 if d>0 else 0} {X:.2f} {Y+1.6:.2f}", sw="mid", fill="#fff")
        v.s.pline(X + d * 1.6, Y, X + d * 3.0, Y, w="mid"); v.s.pline(X + d * 3.0, Y - 1.6, X + d * 3.0, Y + 1.6, w="mid")
    if label:
        v.s.ptext(X, Y - 3.2 if wall != "N" else Y + 5.0, label, size=1.5)


def room_lights(v, rect, n):
    x1, y1, x2, y2 = rect
    if n == 1:
        lamp(v, (x1 + x2) / 2, (y1 + y2) / 2); return
    if n == 2:
        if (x2 - x1) >= (y2 - y1):
            for f in (0.25, 0.75): lamp(v, x1 + (x2 - x1) * f, (y1 + y2) / 2)
        else:
            for f in (0.25, 0.75): lamp(v, (x1 + x2) / 2, y1 + (y2 - y1) * f)
        return
    cols = 2 if n <= 4 else 3
    rows = n // cols
    for i in range(cols):
        for j in range(rows):
            lamp(v, x1 + (x2 - x1) * (i + 0.5) / cols, y1 + (y2 - y1) * (j + 0.5) / rows)


def eo_sheet(floor, sheet_no, total):
    sh, v = eng_sheet(f"ЭО-{floor}", "Электрооборудование: освещение и силовая сеть", floor, sheet_no, total)
    E = R["electrical"]
    n_lamps = 0
    n_sock = 0
    for r in ROOMS[floor]:
        a = room_area(r)
        rect = max(r["rects"], key=rect_area)
        n = 1 if a <= 8 else (2 if a <= 16 else (4 if a <= 32 else 6))
        room_lights(v, rect, n)
        n_lamps += n
        if len(r["rects"]) > 1:
            lamp(v, (r["rects"][0][0] + r["rects"][0][2]) / 2, (r["rects"][0][1] + r["rects"][0][3]) / 2); n_lamps += 1
        # розетки: по 2 на каждой длинной стене (кроме мокрых мест) — упрощённо
        x1, y1, x2, y2 = rect
        w, d = x2 - x1, y2 - y1
        if a >= 6:
            if w >= d:
                for f in (0.3, 0.7):
                    socket(v, x1 + w * f, y1 + 0.1, "N"); socket(v, x1 + w * f, y2 - 0.1, "S"); n_sock += 2
            else:
                for f in (0.3, 0.7):
                    socket(v, x1 + 0.1, y1 + d * f, "W"); socket(v, x2 - 0.1, y1 + d * f, "E"); n_sock += 2
        else:
            socket(v, x1 + w * 0.5, y2 - 0.1, "S"); n_sock += 1
    # выключатели у дверей (со стороны открывания, у ручки)
    for dd in INT_DOORS[floor]:
        if not dd["swing"]:
            continue
        x1, y1, x2, y2 = dd["rect"]
        horizontal = (x2 - x1) > (y2 - y1)
        if horizontal:
            sx = x2 + 0.25 if dd["hinge"] == "W" else x1 - 0.25
            sy = y1 - 0.15 if dd["swing"] == "N" else y2 + 0.15
        else:
            sy = y2 + 0.25 if dd["hinge"] == "N" else y1 - 0.25
            sx = x2 + 0.15 if dd["swing"] == "E" else x1 - 0.15
        switch(v, sx, sy)
    if floor == 1:
        switch(v, 8.2, 0.4)   # тамбур
        # силовые точки
        pts = [((2.8, 10.55), "ВП 7 кВт 3ф", "N"), ((3.6, 10.55), "ДШ", "N"), ((1.1, 10.55), "ПМ", "N"), ((0.35, 11.0), "ХЛ", "W"),
               ((4.5, 3.05), "СМ", "N"), ((5.2, 3.05), "СМ", "N"), ((4.65, 0.8), "К (ИБП)", "N"), ((5.8, 0.4), "Н скв.", "N"), ((4.3, 2.05), "ВО", "W"),
               ((12.35, 9.3), "СК-1", "E"), ((1.0, 0.4), "привод ворот", "N"), ((12.3, 5.5), "ПС", "E")]
        for (x, y), lbl, wall in pts:
            X, Y = v.P(x, y)
            v.s.prect(X - 2, Y - 2, 4, 4, fill="#fff", stroke="#000", sw="mid"); v.s.pline(X - 2, Y - 2, X + 2, Y + 2, w="thin")
            v.s.ptext(X, Y + 4.5, lbl, size=1.5)
        # щиты
        v.rect(4.15, 3.05, 4.75, 3.2, fill="#000", stroke=None); v.text(4.45, 3.6, "ЩР (72 мод.)", size=1.8, weight="bold")
        v.rect(4.85, 3.05, 5.25, 3.2, fill="#fff", sw="mid"); v.text(5.05, 3.6, "ЩС", size=1.6)
        v.text(4.45, 4.0, "ГЗШ, ввод 5×10 из ЩУ", size=1.5)
        v.line(5.0, -0.2, 5.0, 3.05, w="thick", color=RED, dash="8 2 1 2"); v.text(5.3, 1.0, "ввод W", size=1.5, color=RED, rot=-90)
        v.rect(3.5, 0.2, 3.9, 0.8, sw="thin", dash="1 1"); v.text(3.2, 1.2, "полоса заземления 40×4 → контур", size=1.4, anchor="start")
    else:
        pts = [((3.5, 4.65), "СМ", "N"), ((4.2, 4.65), "СШ", "N"), ((0.35, 12.0), "СК-2", "W"), ((0.35, 3.2), "СК-3", "W"), ((12.3, 6.0), "ПС", "E"), ((0.3, 7.5), "ПС", "W"), ((2.5, 9.6), "ПС", "N")]
        for (x, y), lbl, wall in pts:
            X, Y = v.P(x, y)
            v.s.prect(X - 2, Y - 2, 4, 4, fill="#fff", stroke="#000", sw="mid"); v.s.pline(X - 2, Y - 2, X + 2, Y + 2, w="thin")
            v.s.ptext(X, Y + 4.5, lbl, size=1.5)
        v.circle(6.0, 4.8, 1.4, fill="#fff", stroke=RED, sw="mid"); v.text(6.0, 5.6, "стояк 5×6 → щиток 2 эт. (в 2.04)", size=1.4, color=RED)
        v.rect(10.55, 6.95, 11.0, 7.1, fill="#000", stroke=None); v.text(11.4, 7.5, "ЩР-2", size=1.6, weight="bold")
    # наружное освещение (1 этаж)
    if floor == 1:
        for (x, y) in ((7.4, -0.6), (2.05, -0.6), (12.9, 8.0), (6.3, 16.2)):
            X, Y = v.P(x, y)
            v.s.pcircle(X, Y, 1.6, fill="#000", stroke=None); v.s.ptext(X, Y - 3, "НО", size=1.4)
    # правая колонка
    xr = 470
    yy = 40
    sh.ptext(xr, yy, "Групповые линии (щит ЩР), выборка", size=3.0, anchor="start", weight="bold")
    rows = [[a, f"{b:.1f}".replace(".", ","), c, str(d)] for a, b, c, d, e in E["loads"]]
    yy = sh.table(xr, yy + 4, [("Потребитель", 105, "l"), ("кВт", 14, "r"), ("Кабель", 22, "c"), ("А", 12, "c")], rows, size=1.9)
    yy += 6
    def s_lamp(sh, x, y): sh.pcircle(x, y, 1.6, fill="#fff", sw="mid"); sh.pline(x - 1.1, y - 1.1, x + 1.1, y + 1.1, w="mid"); sh.pline(x + 1.1, y - 1.1, x - 1.1, y + 1.1, w="mid")
    def s_sw(sh, x, y): sh.pcircle(x, y, 1.0, fill="#000", stroke=None); sh.pline(x, y, x + 2.2, y - 2.2, w="mid"); sh.pline(x + 2.2, y - 2.2, x + 1.4, y - 2.6, w="mid")
    def s_sock(sh, x, y): sh.ppath(f"M{x-1.6} {y} A1.6 1.6 0 0 1 {x+1.6} {y}", sw="mid", fill="#fff"); sh.pline(x, y + 1.6, x, y + 3.0, w="mid"); sh.pline(x - 1.6, y + 3.0, x + 1.6, y + 3.0, w="mid")
    def s_pow(sh, x, y): sh.prect(x - 2, y - 2, 4, 4, fill="#fff", sw="mid"); sh.pline(x - 2, y - 2, x + 2, y + 2, w="thin")
    def s_panel(sh, x, y): sh.prect(x - 4, y - 1.5, 8, 3, fill="#000", stroke=None)
    def s_out(sh, x, y): sh.pcircle(x, y, 1.6, fill="#000", stroke=None)
    yy = legend_block(sh, xr, yy, "Условные обозначения", [
        (s_lamp, "светильник потолочный LED (точечный/накладной), группы освещения — кабель 3×1,5"),
        (s_sw, "выключатель одно-/двухклавишный, h = 900 мм от пола (проходные — в коридорах и спальнях)"),
        (s_sock, "розетка двойная с заземлением, h = 300 мм (кухня — 1100 мм, санузлы — IP44 с УЗО)"),
        (s_pow, "силовой вывод / отдельная линия для оборудования (ВП, ДШ, ПМ, СМ, К, Н, СК, ПС)"),
        (s_panel, "распределительный щит (ЩР — 1.12; ЩР-2 — 2.04; ЩС — слаботочный)"),
        (s_out, "светильник наружного освещения (фасад, крыльцо, ворота), датчик движения/освещённости"),
    ], size=2.0)
    notes = [
        f"1. Электроснабжение 380/220 В, {E['P_allowed']:.0f} кВт, TN-C-S; P_расч = {E['P_calc']:.1f} кВт (k_с = {E['k_c']}), I = {E['I_calc']:.0f} А; вводной автомат {E['input_breaker']} А 3P в ЩУ на ограде.",
        "2. Ввод в дом — ВВГнг(A)-LS 5×10 в ПНД-трубе; ЩР на 72 модуля в 1.12: ВН, УЗИП кл. II, ВА 40А 3P, селективное УЗО 300 мА, групповые дифавтоматы 16А/30мА.",
        "3. Групповые сети — ВВГнг(A)-LS 3×2,5 (розетки), 3×1,5 (свет), 5×2,5 (варочная панель), в штробах и гофре ПВХ, в стяжке — в ПНД-трубах; проходы через перекрытие — в гильзах.",
        "4. Освещённость по СП 52.13330: жилые 150 лк, кабинет 300 лк, кухня 200 лк, санузлы 100 лк; светильники LED 4000 K, диммирование в гостиной и спальнях (опция).",
        "5. Заземление: контур 3 стержня Ø16 L=3 м + полоса 40×4, R ≤ 30 Ом; СУП в санузлах (ДСУП); молниезащита III кат. — фальцевая кровля как молниеприёмник, 2 токоотвода.",
        f"6. {E['load_mgmt']}. Котельная и насос скважины — через ИБП/стабилизатор.",
        "7. Слаботочные сети: оптический ввод, роутер в 1.02, UTP cat.6 в комнаты, видеодомофон, дымовые извещатели, резервные трубы ПНД 25 для «умного дома».",
        f"8. Ориентировочно: светильников {n_lamps} шт., розеток ≈ {n_sock * 2} (двойных {n_sock}); точное количество — по дизайн-проекту.",
    ]
    sh.ptext(xr, yy + 6, "Примечания", size=3.0, anchor="start", weight="bold")
    sh.ptext_lines(xr, yy + 12, notes, size=2.0, lh=3.9)
    return sh


def single_line_sheet(sheet_no, total):
    sh = Sheet("A3", code="ЭО-3", title="Схема электрическая однолинейная ЩУ и ЩР", scale_txt="б/м", sheet_no=sheet_no, sheets_total=total)
    E = R["electrical"]
    sh.ptext(30, 18, "Схема электрическая однолинейная (ЩУ → ЩР)", size=4.2, anchor="start", weight="bold")
    # ввод
    x0, y0 = 35, 40
    sh.ptext(x0, y0 - 6, "ВЛИ-0,4 кВ (опора) → СИП-4 4×16, 25 м", size=2.2, anchor="start")
    sh.pline(x0, y0, x0 + 60, y0, w="thick")
    def breaker(x, y, txt, rot=False):
        sh.pline(x, y, x + 6, y - 4, w="thick")
        sh.pline(x + 6, y - 4, x + 9, y - 4, w="thin")
        sh.ptext(x + 4, y - 6.5, txt, size=1.9, anchor="middle")
    sh.prect(x0 + 60, y0 - 12, 70, 26, fill="none", stroke="#000", sw="thin", dash="2 1"); sh.ptext(x0 + 95, y0 - 14.5, "ЩУ (на ограде, IP54)", size=2.2)
    sh.pline(x0 + 60, y0, x0 + 66, y0, w="thick"); breaker(x0 + 66, y0, "ВН 63A"); sh.pline(x0 + 75, y0, x0 + 82, y0, w="thick")
    sh.prect(x0 + 82, y0 - 5, 16, 10, fill="#fff", sw="mid"); sh.ptext(x0 + 90, y0, "kWh 3ф", size=2.0)
    sh.pline(x0 + 98, y0, x0 + 104, y0, w="thick"); breaker(x0 + 104, y0, "ВА 25A 3P\nC"); sh.pline(x0 + 113, y0, x0 + 130, y0, w="thick")
    sh.ptext(x0 + 150, y0 - 5, "ВВГнг(A)-LS 5×10 в ПНД Ø50, 0,7 м, 12 м", size=2.0)
    sh.pline(x0 + 130, y0, x0 + 190, y0, w="thick"); sh.pline(x0 + 190, y0, x0 + 190, y0 + 30, w="thick")
    # ЩР
    y1 = y0 + 30
    sh.prect(25, y1 - 6, 370, 130, fill="none", stroke="#000", sw="thin", dash="2 1"); sh.ptext(35, y1 - 9, "ЩР (1.12), 72 модуля, IP31", size=2.2, anchor="start")
    sh.pline(x0 + 190, y1, x0 + 40, y1, w="thick")
    breaker(x0 + 40, y1, "ВА 40A 3P"); sh.pline(x0 + 34, y1 - 4, x0 + 30, y1 - 4, w="thin")
    sh.prect(x0 + 60, y1 + 4, 24, 10, fill="#fff", sw="mid"); sh.ptext(x0 + 72, y1 + 9, "УЗИП кл. II", size=1.9); sh.pline(x0 + 72, y1, x0 + 72, y1 + 4, w="thin")
    sh.prect(x0 + 100, y1 - 5, 30, 10, fill="#fff", sw="mid"); sh.ptext(x0 + 115, y1, "УЗО 63A/300mA S", size=1.8)
    sh.pline(x0 + 84, y1, x0 + 100, y1, w="thick"); sh.pline(x0 + 130, y1, x0 + 150, y1, w="thick")
    # шины
    yb = y1 + 22
    sh.pline(35, yb, 390, yb, w="xthick"); sh.ptext(33, yb, "L1 L2 L3", size=2.0, anchor="end")
    sh.pline(35, yb + 3, 390, yb + 3, w="mid", color=BLUE); sh.ptext(33, yb + 3, "N", size=2.0, anchor="end", color=BLUE)
    sh.pline(35, yb + 6, 390, yb + 6, w="mid", color=GREEN); sh.ptext(33, yb + 6, "PE", size=2.0, anchor="end", color=GREEN)
    sh.pline(x0 + 150, y1, x0 + 150, yb, w="thick")
    # группы
    groups = []
    phases = ["L1", "L2", "L3"]
    for i, (name, p, cab, amp, note) in enumerate(E["loads"]):
        groups.append((f"Гр.{i+1}", name, cab, amp, phases[i % 3] if "5×" not in cab else "3ф"))
    n = len(groups)
    pitch = 355 / n
    for i, (g, name, cab, amp, ph) in enumerate(groups):
        x = 40 + i * pitch
        sh.pline(x, yb + 6, x, yb + 14, w="mid")
        dif = "3×2.5" in cab or "5×" in cab
        sh.prect(x - 2.5, yb + 14, 5, 9, fill="#fff", sw="mid")
        sh.ptext(x, yb + 18.5, f"{amp}", size=1.7)
        sh.ptext(x, yb + 12, ph, size=1.5)
        sh.ptext(x, yb + 27, "дифавт." if dif else "ВА", size=1.4)
        sh.ptext(x, yb + 30, "30 мА" if dif else "C", size=1.4)
        sh.pline(x, yb + 23, x, yb + 33, w="mid", marker="arrow")
        sh.ptext(x + 1.2, yb + 36, f"{g} {cab}", size=1.5, rot=-90, anchor="end")
        sh.ptext(x + 4.5, yb + 36, name[:34], size=1.5, rot=-90, anchor="end")
    sh.ptext(35, y1 + 122, f"Итого групп: {n} + резерв; P_уст = {E['P_inst']:.1f} кВт, P_расч = {E['P_calc']:.1f} кВт, I_расч = {E['I_calc']:.0f} А.", size=2.1, anchor="start")
    notes = [
        "ЩР-2 (2 этаж, в 2.04): питание ВВГнг(A)-LS 5×6 от ЩР через ВА 32A 3P; группы 2 этажа (свет, розетки, СМ/СШ, ПС, СК-2/3) — аналогично.",
        "Все розеточные группы — через дифавтоматы 16A/30мА тип A; ванные — 10 мА. Наружные потребители — УЗО 30 мА, IP44/65.",
        "Заземление TN-C-S: разделение PEN в ЩУ, повторный заземлитель у ЩУ (R ≤ 30 Ом), ГЗШ в ЩР; СУП — санузлы, котельная (котёл, трубы, БКН).",
    ]
    sh.ptext_lines(30, 215, notes, size=2.0, lh=4.0)
    return sh


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "drawings")
    ov_sheet(1, 12, 20).save(os.path.join(out, "ОВ-1_Отопление_вентиляция_1_этаж.svg"))
    ov_sheet(2, 13, 20).save(os.path.join(out, "ОВ-2_Отопление_вентиляция_2_этаж.svg"))
    boiler_scheme_sheet(14, 20).save(os.path.join(out, "ОВ-3_Схема_котельной.svg"))
    vk_sheet(1, 15, 20).save(os.path.join(out, "ВК-1_Водоснабжение_канализация_1_этаж.svg"))
    vk_sheet(2, 16, 20).save(os.path.join(out, "ВК-2_Водоснабжение_канализация_2_этаж.svg"))
    vk_scheme_sheet(17, 20).save(os.path.join(out, "ВК-3_Принципиальные_схемы.svg"))
    eo_sheet(1, 18, 20).save(os.path.join(out, "ЭО-1_Электрооборудование_1_этаж.svg"))
    eo_sheet(2, 19, 20).save(os.path.join(out, "ЭО-2_Электрооборудование_2_этаж.svg"))
    single_line_sheet(20, 20).save(os.path.join(out, "ЭО-3_Однолинейная_схема.svg"))
    print("ok")
