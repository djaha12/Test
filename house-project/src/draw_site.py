# -*- coding: utf-8 -*-
"""ГП-1 — Схема планировочной организации земельного участка (генплан), М 1:200."""
from model import *
from svg import Sheet, mm

HX, HY = SITE["house_origin"]          # положение осей 1/А на участке


def hx(x):  # координаты дома → участка
    return HX + x


def hy(y):
    return HY + y


# объекты на участке (координаты участка, м; y — от красной линии вглубь)
OBJECTS = [
    # (номер, название, x, y, тип, размер)
    ("1", "Жилой дом (2 этажа, 13×16 м)", None, None, "house", None),
    ("2", "Терраса 12,6×3,0 м, мощение", None, None, "terrace", None),
    ("3", "Крыльцо с навесом", None, None, "porch", None),
    ("4", "Площадка-стоянка на 2 а/м (5,0×5,5 м), проезд к гаражу", None, None, "drive", None),
    ("5", "Скважина с кессоном Ø1,5 м", 1.5, 2.0, "circle", 0.75),
    ("6", "Станция биологической очистки (СБО) 1,6 м³/сут", 18.0, 27.0, "circle", 0.6),
    ("7", "Колодец дренажный (сброс очищенной воды), 9,3 м от дома", 11.5, 28.8, "circle", 0.5),
    ("8", "Шкаф газовый (ГРПШ / узел учёта газа) на ограде", 18.4, 0.3, "box", (0.6, 0.4)),
    ("9", "Щит учёта электроэнергии (ЩУ) на ограде", 2.2, 0.3, "box", (0.5, 0.3)),
    ("10", "Площадка ТБО", 8.6, 0.6, "box", (1.2, 0.8)),
    ("11", "Ворота 4,0 м + калитка 1,0 м", None, None, "gate", None),
    ("12", "Дождеприёмный колодец (ливневая канализация)", 1.5, 22.0, "circle", 0.5),
    ("13", "Зона отдыха / газон, плодовые деревья", None, None, "garden", None),
    ("14", "Ограждение h = 1,8 м (со стороны улицы), 1,6 м (соседи, сетчатое)", None, None, "fence", None),
]


def site_sheet(sheet_no, total):
    sh = Sheet("A2", code="ГП-1", title="Схема планировочной организации земельного участка", scale_txt="1:200",
               sheet_no=sheet_no, sheets_total=total)
    k = 5.0  # мм на м при 1:200
    v = sh.view(ox=60, oy=50, scale=200)
    W, D = SITE["width"], SITE["depth"]
    sh.ptext(300, 20, "Генплан участка 6 соток (20×30 м), М 1:200", size=5, anchor="start", weight="bold")

    # улица
    v.rect(-6, -7, W + 6, -1.0, fill="#e6e6e6", stroke=None)
    v.line(-6, -7, W + 6, -7, w="mid"); v.line(-6, -1.0, W + 6, -1.0, w="mid")
    v.text(W / 2, -4.0, "улица / проезд (асфальт), ширина 6 м", size=2.6)
    v.line(-6, 0, W + 6, 0, w="thick", dash="6 2 1 2")
    v.text(W + 3.0, -0.6, "красная линия", size=2.2, anchor="end")
    # соседи
    v.rect(-6, 0, 0, D, fill="url(#hGrass)", stroke=None, opacity=0.4)
    v.rect(W, 0, W + 6, D, fill="url(#hGrass)", stroke=None, opacity=0.4)
    v.rect(-6, D, W + 6, D + 4, fill="url(#hGrass)", stroke=None, opacity=0.4)
    v.text(-3, D / 2, "соседний участок", size=2.4, rot=-90)
    v.text(W + 3, D / 2, "соседний участок", size=2.4, rot=-90)
    v.text(W / 2, D + 2, "соседний участок", size=2.4)

    # участок: газон
    v.rect(0, 0, W, D, fill="#eef5e6", stroke=None)
    # границы участка
    v.rect(0, 0, W, D, sw="xthick")
    # линии отступов (регулирования застройки)
    v.rect(3.0, 5.0, W - 3.0, D - 3.0, sw="thin", dash="3 1.5")
    v.text(W / 2, 4.5, "линия регулирования застройки: 5 м от красной линии, 3 м от границ", size=2.0)

    # мощение: проезд/стоянка, дорожка
    v.rect(2.0, 0, 8.6, 5.0, fill="url(#hPaving)", sw="thin")
    v.text(5.3, 2.4, "4", size=3.2, weight="bold")
    # машиноместа
    for x0 in (2.4, 5.2):
        v.rect(x0, 0.3, x0 + 2.5, 5.0, sw="thin", dash="1 1")
    v.rect(8.6, 0, 9.6, 5.0, fill="url(#hPaving)", sw="thin")   # дорожка к крыльцу
    v.rect(8.6, 3.3, hx(8.6) + 0.3, 5.0, fill="url(#hPaving)", sw="thin")
    # отмостка вокруг дома
    o = EXT_OUTER
    v.rect(hx(o[0]) - 1.0, hy(o[1]) - 1.0, hx(o[2]) + 1.0, hy(o[3]) + 1.0, fill="#ddd", sw="thin")
    # дорожка вокруг дома к террасе (вдоль восточной стороны)
    v.rect(hx(o[2]) + 1.0, hy(o[1]) - 1.0, hx(o[2]) + 2.0, hy(o[3]) + 3.0, fill="url(#hPaving)", sw="thin")
    # терраса
    t = TERRACE["rect"]
    v.rect(hx(t[0]), hy(t[1]), hx(t[2]), hy(t[3]), fill="url(#hPaving)", sw="mid")
    v.text(hx(6.3), hy(17.3), "2", size=3.2, weight="bold")
    # крыльцо
    p = PORCH["rect"]
    v.rect(hx(p[0]), hy(p[1]), hx(p[2]), hy(p[3]), fill="#ccc", sw="mid")
    v.text(hx(7.4), hy(-1.0), "3", size=3.0, weight="bold")
    # дом: контур кровли и стен
    v.rect(hx(ROOF["eave_edge_x_w"]), hy(ROOF["gable_y_n"]), hx(ROOF["eave_edge_x_e"]), hy(ROOF["gable_y_s"]),
           fill="#b9bfc6", sw="thin")
    v.line(hx(ROOF["ridge_x"]), hy(ROOF["gable_y_n"]), hx(ROOF["ridge_x"]), hy(ROOF["gable_y_s"]), w="mid")
    v.rect(hx(o[0]), hy(o[1]), hx(o[2]), hy(o[3]), fill="none", sw="thick", dash="2 1")
    v.text(hx(6.3), hy(6.5), "1", size=4.5, weight="bold")
    v.text(hx(6.3), hy(8.3), "жилой дом 2 эт.", size=2.6)
    v.text(hx(6.3), hy(9.6), "±0,000 = +0,45 от земли", size=2.0)
    # въезд в гараж / вход
    v.line(hx(2.05), hy(-0.2), hx(2.05), hy(-2.6), w="mid", marker="arrow")
    v.text(hx(2.05) - 1.3, hy(-2.3), "въезд", size=2.0)
    v.line(hx(7.4), hy(-2.0), hx(7.4), hy(-0.4), w="mid", marker="arrow")
    # ворота и калитка
    v.line(3.75, 0, 7.75, 0, w="xthick", color="#c00")
    v.line(8.0, 0, 9.0, 0, w="xthick", color="#c00")
    v.text(5.75, -1.5, "11 (ворота 4,0)", size=2.0)
    v.text(9.6, -1.5, "калитка", size=2.0)
    # точечные объекты
    for n, name, x, y, kind, size in OBJECTS:
        if kind == "circle":
            v.circle(x, y, size * k, fill="#fff", sw="mid")
            v.text(x, y, n, size=2.6, weight="bold")
        elif kind == "box":
            w, h = size
            v.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill="#fff", sw="mid")
            v.text(x, y - h / 2 - 0.9, n, size=2.6, weight="bold")
    # инженерные сети (трассы)
    # канализация: выпуск от дома (восточная стена, y≈10) → СБО → дренажный колодец
    v.poly([(hx(12.8), hy(10.0)), (hx(12.8) + 1.5, hy(10.0)), (hx(12.8) + 1.5, 27.0), (18.0 - 0.6, 27.0)],
           closed=False, stroke="#7a4a1a", sw="mid", dash="4 1.5")
    v.line(17.4, 27.4, 12.0, 28.8, color="#7a4a1a", w="mid", dash="4 1.5")
    v.text(hx(12.8) + 2.6, 18.0, "К1", size=2.4, color="#7a4a1a", rot=-90)
    # водопровод от скважины до котельной
    v.poly([(1.5, 2.0), (1.5, 3.5), (hx(4.4), 3.5), (hx(4.4), hy(0.3))], closed=False, stroke="#1a5fb4", sw="mid", dash="6 1.5")
    v.text(4.5, 3.0, "В1", size=2.4, color="#1a5fb4")
    # газ от ГРПШ до котельной (по фасаду/под землёй)
    v.poly([(18.4, 0.5), (18.4, 1.5), (hx(5.2), 1.5), (hx(5.2), hy(-0.2))], closed=False, stroke="#c8a000", sw="mid", dash="2 1")
    v.text(14.5, 2.1, "Г (газ)", size=2.2, color="#c8a000")
    # электрокабель от ЩУ до хозяйственной (ввод ВВГнг 5×10)
    v.poly([(2.2, 0.5), (2.2, 0.9), (hx(5.0), 0.9), (hx(5.0), hy(-0.2))], closed=False, stroke="#c00", sw="mid", dash="8 2 1 2")
    v.text(4.4, 1.25, "W", size=2.2, color="#c00", anchor="start")
    # ливневая: водостоки → дождеприёмник
    v.poly([(hx(-0.8), hy(16.0)), (1.5, hy(16.0)), (1.5, 22.0)], closed=False, stroke="#3a8fb7", sw="thin", dash="2 1")
    v.poly([(hx(-0.8), hy(-0.5)), (1.5, hy(-0.5)), (1.5, 8.0)], closed=False, stroke="#3a8fb7", sw="thin", dash="2 1")
    # деревья
    for (x, y, r) in [(2.0, 27.5, 1.8), (6.0, 28.2, 1.6), (10.0, 27.8, 1.8), (18.5, 20.0, 1.4), (18.5, 15.0, 1.4), (18.5, 8.0, 1.2), (1.2, 12.0, 1.0), (1.2, 16.5, 1.0)]:
        v.circle(x, y, r * k, fill="#cfe8bf", stroke="#5a9a3a", sw="thin")
        v.circle(x, y, 0.6, fill="#5a9a3a", stroke=None)
    v.text(10.0, 24.6, "13 — сад / газон / зона отдыха", size=2.4)
    # огород / грядки
    for i in range(3):
        v.rect(12.5, 26.5 + i * 1.1, 16.0, 27.3 + i * 1.1, fill="#e9dcc3", sw="thin")
    # освещение (4 столбика)
    for (x, y) in [(3.0, 1.0), (9.8, 4.2), (17.0, 6.0), (10.0, 25.0)]:
        v.circle(x, y, 0.9, fill="#fff", sw="thin"); v.circle(x, y, 0.3, fill="#000", stroke=None)
    # размеры
    v.dim_h([0, 3.5, hx(o[2]), W], D + 0.5, 18, values=None, ext_from=D, flip_text=True)
    v.dim_h([0, W], D + 0.5, 26, ext_from=D, flip_text=True)
    v.dim_v([0, 5.0, hy(o[3]), hy(TERRACE["rect"][3]), D], W + 0.5, 14, ext_from=W)
    v.dim_v([0, D], W + 0.5, 22, ext_from=W)
    v.dim_h([hx(o[0]), hx(o[2])], -7.5, -6, ext_from=-7.0)
    v.north_arrow(W + 5.5, -5.5, r_mm=7)
    v.text(-7.5, D + 0.5, "", size=2)
    # розы ветров нет — примечание
    # --- таблицы справа
    xr = 300
    yy = 40
    sh.ptext(xr, yy, "Ведомость зданий и сооружений", size=3.2, anchor="start", weight="bold")
    rows = [[n, name] for n, name, *_ in OBJECTS]
    yy = sh.table(xr, yy + 4, [("№", 10, "c"), ("Наименование", 150, "l")], rows, size=2.2)
    yy += 12
    sh.ptext(xr, yy, "Баланс территории", size=3.2, anchor="start", weight="bold")
    s_house = FOOTPRINT_W * FOOTPRINT_D
    s_terr = rect_area(TERRACE["rect"])
    s_porch = rect_area(PORCH["rect"])
    s_drive = 6.6 * 5.0 + 1.0 * 5.0 + 1.0 * 20.0 + 2.0 * 1.7
    s_paths = 2 * (13.0 + 16.0 + 4) * 1.0
    s_total = SITE["width"] * SITE["depth"]
    s_green = s_total - s_house - s_terr - s_porch - s_drive - s_paths
    bal = [
        ["Площадь участка", f"{s_total:.0f}", "100"],
        ["Пятно застройки дома", f"{s_house:.1f}", f"{100 * s_house / s_total:.1f}"],
        ["Терраса, крыльцо", f"{s_terr + s_porch:.1f}", f"{100 * (s_terr + s_porch) / s_total:.1f}"],
        ["Проезд, стоянка, дорожки", f"{s_drive:.1f}", f"{100 * s_drive / s_total:.1f}"],
        ["Отмостка", f"{s_paths:.1f}", f"{100 * s_paths / s_total:.1f}"],
        ["Озеленение (газон, сад, огород)", f"{s_green:.1f}", f"{100 * s_green / s_total:.1f}"],
    ]
    bal = [[a, b.replace(".", ","), c.replace(".", ",")] for a, b, c in bal]
    yy = sh.table(xr, yy + 4, [("Показатель", 90, "l"), ("м²", 30, "r"), ("%", 20, "r")], bal, size=2.2)
    yy += 12
    sh.ptext(xr, yy, "Нормативные расстояния (СП 53.13330.2019, СП 30-102-99, СанПиН)", size=3.0, anchor="start", weight="bold")
    lines = [
        "• от дома до красной линии улицы — 5,0 м (норма ≥ 5 м);",
        "• от дома до боковых границ — 3,5 м (норма ≥ 3 м), до задней — 9,0 м;",
        "• противопожарный разрыв до соседних домов: ≥ 6 м (I–II ст. огнест.), ≥ 8–10 м (III), ≥ 15 м (V);",
        "  фактический — не менее 3,5 м + отступ соседа (уточнить по фактической застройке!);",
        "• скважина (5) — 4,0 м от дома, 30 м от СБО (6) (норма ≥ 15 м до герметичных сооружений, ≥ 25–50 м до фильтрующих);",
        "• СБО (6) герметичная, аэрационная — 6,2 м от дома (норма для септика ≥ 5 м, СП 53.13330.2011 п. 8.7), 2 м от границ;",
        "• дренажный (фильтрующий) колодец (7) — 9,3 м от дома (норма ≥ 8 м), 1,2 м от границы; сброс в кювет — по согласованию;",
        "• коэффициент застройки 34,7 % (проверить ПЗЗ муниципалитета: обычно ≤ 30–40 %).",
        "• Дождевая вода с кровли — в дождеприёмный колодец (12) с дренажным полем на газоне.",
    ]
    sh.ptext_lines(xr, yy + 6, lines, size=2.2, lh=4.0)
    yy += 6 + 4.0 * len(lines) + 6
    sh.ptext(xr, yy, "Условные обозначения сетей", size=3.0, anchor="start", weight="bold")
    yy += 5
    for col, dash, txt in [("#1a5fb4", "6 1.5", "В1 — водопровод от скважины, ПНД Ø32, глубина 1,6 м (ниже промерзания)"),
                           ("#7a4a1a", "4 1.5", "К1 — канализация самотёчная, ПП Ø110, уклон 2 %"),
                           ("#c8a000", "2 1", "Г — газопровод низкого давления, ПЭ Ø32 подземный"),
                           ("#c00", "8 2 1 2", "W — кабель 0,4 кВ ВВГнг(A)-LS 5×10 в ПНД-трубе, глубина 0,7 м"),
                           ("#3a8fb7", "2 1", "К2 — ливневая канализация, ПП Ø110")]:
        sh.pline(xr, yy, xr + 20, yy, w="mid", color=col, dash=dash)
        sh.ptext(xr + 24, yy, txt, size=2.2, anchor="start")
        yy += 5
    return sh


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "drawings")
    site_sheet(1, 20).save(os.path.join(out, "ГП-1_Генплан.svg"))
    print("ok")
