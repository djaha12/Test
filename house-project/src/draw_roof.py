# -*- coding: utf-8 -*-
"""АР-3 — План кровли, М 1:100."""
from model import *
from svg import Sheet, mm


def roof_sheet(sheet_no, total):
    sh = Sheet("A2", code="АР-3", title="План кровли", scale_txt="1:100", sheet_no=sheet_no, sheets_total=total)
    v = sh.view(ox=70, oy=60, scale=100)
    sh.ptext(330, 22, "План кровли   М 1:100", size=5, anchor="start", weight="bold")
    xw, xe = ROOF["eave_edge_x_w"], ROOF["eave_edge_x_e"]
    yn, ys = ROOF["gable_y_n"], ROOF["gable_y_s"]
    rx = ROOF["ridge_x"]
    o = EXT_OUTER
    # скаты
    v.rect(xw, yn, rx, ys, fill="#dfe3e8", sw="mid")
    v.rect(rx, yn, xe, ys, fill="#d3d8de", sw="mid")
    # фальцы (шаг 0,5 м)
    x = xw + 0.5
    while x < xe - 0.01:
        if abs(x - rx) > 0.05:
            v.line(x, yn, x, ys, w="thin", color="#999")
        x += 0.5
    # конёк
    v.line(rx, yn, rx, ys, w="xthick")
    v.text(rx + 0.55, (yn + ys) / 2 - 1.0, "конёк +10,650", size=2.4, rot=-90)
    # контур стен под кровлей
    v.rect(*o, sw="mid", dash="3 1.5")
    # стрелки уклона
    for yy in (3.0, 8.0, 13.0):
        v.line(rx - 0.8, yy, xw + 1.0, yy, w="mid", marker="arrow")
        v.line(rx + 0.8, yy, xe - 1.0, yy, w="mid", marker="arrow")
        v.text(rx - 3.5, yy - 0.4, "i = 58 % (30°)", size=2.2)
        v.text(rx + 3.5, yy - 0.4, "i = 58 % (30°)", size=2.2)
    # желоба
    for xx in (xw, xe):
        v.line(xx, yn, xx, ys, w="thick")
        v.line(xx + (0.15 if xx == xw else -0.15), yn, xx + (0.15 if xx == xw else -0.15), ys, w="thin")
    # водосточные трубы
    for xx in (xw, xe):
        for yy in (yn + 0.3, (yn + ys) / 2, ys - 0.3):
            v.circle(xx + (-0.35 if xx == xw else 0.35), yy, 1.2, fill="#fff", sw="mid")
            v.text(xx + (-0.35 if xx == xw else 0.35), yy, "Ø", size=1.6)
    v.text(xw - 1.5, yn - 1.0, "водосточные трубы Ø100 — 6 шт.", size=2.2, anchor="start")
    # снегозадержатели (трубчатые), в 0,6 м от карниза
    v.line(xw + 0.8, yn + 0.3, xw + 0.8, ys - 0.3, w="mid", dash="4 1")
    v.line(xe - 0.8, yn + 0.3, xe - 0.8, ys - 0.3, w="mid", dash="4 1")
    v.text(xw + 1.2, ys - 0.9, "снегозадержатели трубчатые", size=2.0, anchor="start")
    # вентиляционные выходы
    for x1, y1, x2, y2, name, desc, floors in VENT_SHAFTS:
        v.rect(x1, y1, x2, y2, fill="#fff", sw="mid")
        v.rect(x1 - 0.15, y1 - 0.15, x2 + 0.15, y2 + 0.15, sw="thin")
        v.text_mm((x1 + x2) / 2, (y1 + y2) / 2, 0, -4.5, name, size=2.0, weight="bold")
    # люк на чердак (пунктиром — в перекрытии)
    h = ATTIC_HATCH
    v.rect(*h, sw="thin", dash="1 1")
    v.text((h[0] + h[2]) / 2, h[3] + 0.5, "люк на чердак 700×900", size=1.8)
    # коаксиальный дымоход котла — через северную стену (не на кровле)
    v.circle(ROOF["flue_x"], -0.35, 1.4, fill="#fff", sw="mid")
    v.text(ROOF["flue_x"], -1.2, "коакс. дымоход котла Ø60/100 через стену", size=1.8)
    # оси
    for lbl, xx in AXES_X:
        v.axis_line(xx, yn - 3.0, xx, ys + 3.0)
        v.axis_bubble(xx, yn - 3.0, lbl, dy=-4)
        v.axis_bubble(xx, ys + 3.0, lbl, dy=4)
    for lbl, yy in AXES_Y:
        v.axis_line(xw - 3.0, yy, xe + 3.0, yy)
        v.axis_bubble(xw - 3.0, yy, lbl, dx=-4)
        v.axis_bubble(xe + 3.0, yy, lbl, dx=4)
    # размеры
    v.dim_h([xw, o[0], rx, o[2], xe], ys + 3.5, 8, ext_from=ys, flip_text=True)
    v.dim_h([xw, xe], ys + 3.5, 16, ext_from=ys, flip_text=True)
    v.dim_v([yn, o[1], o[3], ys], xe + 3.5, 8, ext_from=xe)
    v.dim_v([yn, ys], xe + 3.5, 16, ext_from=xe)
    v.north_arrow(xe + 5.5, yn - 2.5)
    # таблица
    xr = 330
    yy = 40
    slope_len = (xe - rx) / ROOF["cos"]
    area_h = (xe - xw) * (ys - yn)
    area_s = area_h / ROOF["cos"]
    sh.ptext(xr, yy, "Основные показатели кровли", size=3.2, anchor="start", weight="bold")
    rows = [
        ["Тип кровли", "двускатная, холодный чердак"],
        ["Уклон", "30° (58 %)"],
        ["Покрытие", "фальцевая кровля, сталь 0,5 мм, RAL 7016"],
        ["Площадь в плане", f"{area_h:.1f} м²".replace(".", ",")],
        ["Площадь скатов", f"{area_s:.1f} м²".replace(".", ",")],
        ["Длина ската", f"{slope_len:.2f} м".replace(".", ",")],
        ["Длина конька", f"{ys - yn:.1f} м".replace(".", ",")],
        ["Свесы: карниз / фронтон", "600 / 500 мм"],
        ["Желоба Ø125", f"2 × {ys - yn:.1f} м".replace(".", ",")],
        ["Водосточные трубы Ø100", "6 шт. × ≈7,3 м"],
        ["Снегозадержатели", f"2 × {ys - yn - 0.6:.1f} м".replace(".", ",")],
        ["Вентвыходы", "7 шт. (В1…В7), утеплённые, с колпаками"],
        ["Отметка конька / карниза", "+10,650 / +6,554 (низ свеса)"],
    ]
    yy = sh.table(xr, yy + 4, [("Показатель", 70, "l"), ("Значение", 150, "l")], rows, size=2.3)
    yy += 10
    sh.ptext(xr, yy, "Состав кровли (сверху вниз)", size=3.0, anchor="start", weight="bold")
    lines = [
        "1. Фальцевая кровля (двойной стоячий фальц), сталь 0,5 мм с покрытием.",
        "2. Подкладочный ковёр / объёмная разделительная мембрана.",
        "3. Сплошной настил — влагостойкая фанера ФСФ 12 мм или ОСП-3 12 мм.",
        "4. Обрешётка 50×50 шаг 300 мм; контробрешётка 50×50 (вентзазор 50 мм).",
        "5. Гидроветрозащитная диффузионная мембрана.",
        "6. Стропила 50×200 (С24), шаг 600 мм; прогоны 100×200; стойки 100×150 шаг 3,0 м.",
        "7. Чердак холодный, проветриваемый: карнизные продухи + жалюзийные решётки 600×900 во фронтонах.",
        "8. Утепление — по чердачному перекрытию: минвата 250 мм (λ ≤ 0,040) по пароизоляции, сверху ветрозащита.",
        "9. Проходы вентканалов через кровлю — заводские проходные элементы с уплотнением, вентвыходы утеплённые.",
        "10. Водосток наружный организованный: желоба Ø125, трубы Ø100, отвод в ливневую канализацию.",
    ]
    sh.ptext_lines(xr, yy + 6, lines, size=2.2, lh=4.2)
    return sh


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "drawings")
    roof_sheet(4, 20).save(os.path.join(out, "АР-3_План_кровли.svg"))
    print("ok")
