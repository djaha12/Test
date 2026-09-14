# -*- coding: utf-8 -*-
"""АР-4, АР-5 — Фасады, М 1:100."""
from model import *
from svg import Sheet, mm

LEAVES = {"ОК-1": 2, "ОК-2": 2, "ОК-3": 1, "ОК-4": 1, "ОК-4а": 1, "ОК-5": 1, "ОК-6": 2, "ОК-7": 2, "ОК-8": 1, "ОК-9": 3}
C_PLASTER = "#f2efe8"
C_WOOD = "#c99a5b"
C_ROOF = "#3c3f42"
C_PLINTH = "#5b5550"
C_FRAME = "#2e3236"
C_GLASS = "#b8d4e8"
ROOF_T = 0.28   # видимая толщина кровельного пакета (вертикальная), м
Z2 = LEVELS["floor2"]


def side_map(side):
    o = EXT_OUTER
    if side == "S":
        return (lambda a: a), o[0], o[2], [(l, x) for l, x in AXES_X], "Фасад 1-3 (южный, со стороны сада)"
    if side == "N":
        return (lambda a: -a), -o[2], -o[0], [(l, -x) for l, x in AXES_X], "Фасад 3-1 (северный, со стороны улицы)"
    if side == "W":
        return (lambda a: a), o[1], o[3], [(l, y) for l, y in AXES_Y], "Фасад А-Б (западный)"
    return (lambda a: -a), -o[3], -o[1], [(l, -y) for l, y in AXES_Y], "Фасад Б-А (восточный)"


def window(v, u1, u2, z1, z2, tag):
    v.rect(u1, z1, u2, z2, fill=C_FRAME, stroke="#000", sw="thin")
    f = 0.06
    v.rect(u1 + f, z1 + f, u2 - f, z2 - f, fill=C_GLASS, stroke=None)
    v.rect(u1 + f, z1 + f, u2 - f, z2 - f, fill="url(#hGlass)", stroke=None, opacity=0.5)
    n = LEAVES.get(tag, 1)
    w = u2 - u1
    for i in range(1, n):
        uu = u1 + w * i / n
        v.line(uu, z1 + f, uu, z2 - f, w="mid", color=C_FRAME)
    # подоконник / отлив
    v.line(u1 - 0.05, z1, u2 + 0.05, z1, w="mid")


def vent_stacks(v, side, U):
    """Вентвыходы над кровлей на фасаде."""
    for x1, y1, x2, y2, name, desc, floors in VENT_SHAFTS:
        xc = (x1 + x2) / 2
        base = roof_z(xc)
        top = base + 0.7
        if side in ("N", "S"):
            u1, u2 = U(x1), U(x2)
            v.rect(u1, base, u2, top, fill="#777", sw="thin")
            v.rect(u1 - 0.08, top, u2 + 0.08, top + 0.12, fill="#444", sw="thin")
        else:
            near = (xc > ROOF["ridge_x"]) if side == "E" else (xc < ROOF["ridge_x"])
            zb = base if near else ROOF["ridge_z"]
            if top > zb:
                u1, u2 = U(y1), U(y2)
                v.rect(u1, zb, u2, top, fill="#777", sw="thin")
                v.rect(u1 - 0.08, top, u2 + 0.08, top + 0.12, fill="#444", sw="thin")


def draw_elevation(sh, side, x_left, oy, scale=100):
    U, umin, umax, axes, title = side_map(side)
    k = 1000.0 / scale
    ox = x_left - umin * k + 20
    v = sh.view(ox=ox, oy=oy, scale=scale, flip_y=True)
    o = EXT_OUTER
    zg = LEVELS["grade"]
    zt_edge = roof_z(o[0]) - ROOF_T            # низ кровельного пакета у стены
    zt_ridge = ROOF["ridge_z"] - ROOF_T
    sh.ptext(v.X((umin + umax) / 2), oy - 122, title + "   М 1:" + str(scale), size=4.2, anchor="middle", weight="bold")
    # грунт
    v.rect(umin - 2.5, zg - 0.5, umax + 2.5, zg, fill="url(#hEarth)", stroke=None, opacity=0.6)
    v.line(umin - 2.5, zg, umax + 2.5, zg, w="thick")
    if side in ("N", "S"):
        # стена + фронтон
        v.poly([(U(o[0]), 0), (U(o[2]), 0), (U(o[2]), zt_edge), (U(6.3), zt_ridge), (U(o[0]), zt_edge)],
               fill=C_PLASTER, stroke="#000", sw="mid")
        # фронтон — планкен
        v.poly([(U(o[0]), 6.5), (U(o[2]), 6.5), (U(o[2]), zt_edge), (U(6.3), zt_ridge), (U(o[0]), zt_edge)],
               fill=C_WOOD, stroke="#000", sw="mid")
        z = 6.5 + 0.14
        while z < zt_ridge:
            d = (zt_ridge - z) / ROOF["tan"]
            x1, x2 = max(o[0], 6.3 - d), min(o[2], 6.3 + d)
            v.line(U(x1), z, U(x2), z, w="thin", color="#8a6a3a")
            z += 0.14
        # жалюзийная решётка проветривания чердака
        g = GABLE_LOUVER
        v.rect(U(6.3 - g["w"] / 2), g["z"], U(6.3 + g["w"] / 2), g["z"] + g["h"], fill="#666", sw="thin")
        for i in range(6):
            zz = g["z"] + 0.12 + i * 0.13
            v.line(U(6.3 - g["w"] / 2), zz, U(6.3 + g["w"] / 2), zz, w="thin", color="#ccc")
        # цоколь
        v.rect(U(o[0]), zg, U(o[2]), 0.0, fill=C_PLINTH, sw="mid")
        # кровельный пакет (торец — ветровая доска)
        xw, xe = ROOF["eave_edge_x_w"], ROOF["eave_edge_x_e"]
        ze = ROOF["eave_edge_z"]
        v.poly([(U(xw), ze), (U(6.3), ROOF["ridge_z"]), (U(xe), ze), (U(xe), ze - ROOF_T), (U(6.3), zt_ridge), (U(xw), ze - ROOF_T)],
               fill=C_ROOF, stroke="#000", sw="mid")
        # окна
        for fl, z0 in ((1, 0.0), (2, Z2)):
            for s, a1, a2, h, sill, tag in WINDOWS[fl]:
                if s == side:
                    window(v, U(a1), U(a2), z0 + sill, z0 + sill + h, tag)
        if side == "N":
            # ворота
            for s, a1, a2, h, tag, kind in EXT_DOORS[1]:
                if s == "N" and kind == "garage":
                    zb = LEVELS["garage_floor"]
                    v.rect(U(a1), zb, U(a2), zb + h, fill="#9a9a9a", stroke="#000", sw="mid")
                    zz = zb + 0.5
                    while zz < zb + h - 0.1:
                        v.line(U(a1), zz, U(a2), zz, w="thin", color="#666")
                        zz += 0.5
                    v.text(U((a1 + a2) / 2), zb + h / 2, tag, size=2.2, color="#fff")
                elif s == "N" and kind == "entrance":
                    zb = LEVELS["porch"]
                    v.rect(U(a1), zb, U(a2), zb + h, fill="#4a4e52", stroke="#000", sw="mid")
                    v.rect(U(a1) + 0.12 * (1 if U(a2) > U(a1) else -1), zb + 0.9, U(a2) - 0.12 * (1 if U(a2) > U(a1) else -1), zb + h - 0.15, fill="#6a7075", stroke=None)
                    v.circle(U(a1 + 0.15), zb + 1.05, 0.6, fill="#ddd", sw="thin")
            # крыльцо
            p = PORCH["rect"]
            v.rect(U(p[0]), zg, U(p[2]), LEVELS["porch"], fill="#bbb", stroke="#000", sw="mid")
            for zz in (-0.31, -0.17):
                v.line(U(p[0]), zz, U(p[2]), zz, w="thin")
            # козырёк
            c = PORCH["canopy"]
            zc = PORCH["canopy_z"]
            v.rect(U(c[0]), zc, U(c[2]), zc + 0.15, fill=C_ROOF, stroke="#000", sw="mid")
            v.line(U(c[0] + 0.3), zc, U(c[0] + 0.3), zc - 0.6, w="mid")
            v.line(U(c[2] - 0.3), zc, U(c[2] - 0.3), zc - 0.6, w="mid")
            v.line(U(c[0] + 0.3), zc - 0.6, U(c[0] + 0.3) + (0.9 if U(c[2]) > U(c[0]) else -0.9), zc - 0.6, w="mid")
            v.line(U(c[2] - 0.3), zc - 0.6, U(c[2] - 0.3) - (0.9 if U(c[2]) > U(c[0]) else -0.9), zc - 0.6, w="mid")
            # пандус гаража
            a = GARAGE_APRON["rect"]
            v.line(U(a[0]), zg, U(a[2]), zg, w="thick")
            v.poly([(U(a[0]), zg), (U(a[0]), LEVELS["garage_floor"]), (U(a[2]), LEVELS["garage_floor"]), (U(a[2]), zg)], fill="#ccc", stroke="#000", sw="thin")
        else:
            # раздвижные двери на террасу
            for s, a1, a2, h, tag, kind in EXT_DOORS[1]:
                if s == "S":
                    zb = 0.0
                    v.rect(U(a1), zb, U(a2), zb + h, fill=C_FRAME, stroke="#000", sw="mid")
                    f = 0.06
                    v.rect(U(a1) + f, zb + f, U(a2) - f, zb + h - f, fill=C_GLASS, stroke=None)
                    v.rect(U(a1) + f, zb + f, U(a2) - f, zb + h - f, fill="url(#hGlass)", stroke=None, opacity=0.5)
                    v.line(U((a1 + a2) / 2), zb + f, U((a1 + a2) / 2), zb + h - f, w="mid", color=C_FRAME)
            # терраса
            t = TERRACE["rect"]
            v.rect(U(t[0]), zg, U(t[2]), TERRACE["level"], fill="#bbb", stroke="#000", sw="mid")
            v.line(U(t[0] + 4.0), zg + 0.15, U(t[0] + 6.0), zg + 0.15, w="thin")
        vent_stacks(v, side, U)
    else:
        # восточный / западный фасад
        yn, ys = ROOF["gable_y_n"], ROOF["gable_y_s"]
        ze = ROOF["eave_edge_z"]
        v.rect(U(o[1]), 0.0, U(o[3]), ze - ROOF_T, fill=C_PLASTER, stroke="#000", sw="mid")
        v.rect(U(o[1]), zg, U(o[3]), 0.0, fill=C_PLINTH, sw="mid")
        # лобовая доска / карнизный свес
        v.rect(U(yn), ze - ROOF_T, U(ys), ze, fill=C_ROOF, stroke="#000", sw="mid")
        # скат
        v.rect(U(yn), ze, U(ys), ROOF["ridge_z"], fill="#4d5156", stroke="#000", sw="mid")
        yy = yn + 0.5
        while yy < ys - 0.01:
            v.line(U(yy), ze, U(yy), ROOF["ridge_z"], w="thin", color="#6b7075")
            yy += 0.5
        v.line(U(yn), ROOF["ridge_z"], U(ys), ROOF["ridge_z"], w="thick")
        # окна
        for fl, z0 in ((1, 0.0), (2, Z2)):
            for s, a1, a2, h, sill, tag in WINDOWS[fl]:
                if s == side:
                    window(v, U(a1), U(a2), z0 + sill, z0 + sill + h, tag)
        # терраса и крыльцо в профиле
        t = TERRACE["rect"]
        v.rect(U(o[3]), zg, U(t[3]), TERRACE["level"], fill="#bbb", stroke="#000", sw="thin")
        p = PORCH["rect"]
        v.rect(U(p[1]), zg, U(o[1]), LEVELS["porch"], fill="#bbb", stroke="#000", sw="thin")
        c = PORCH["canopy"]
        zc = PORCH["canopy_z"]
        v.rect(U(c[1]), zc, U(o[1]), zc + 0.15, fill=C_ROOF, stroke="#000", sw="thin")
        if side == "E":
            v.line(U(c[1] + 0.3), zc, U(c[1] + 0.3), zc - 0.6, w="thin")
            v.line(U(c[1] + 0.3), zc - 0.6, U(o[1]), zc - 0.6, w="thin")
        vent_stacks(v, side, U)
    # отметки
    ul = umin - 1.6
    for z, txt in ((zg, "−0,450"), (0.0, "±0,000"), (Z2, "+3,300"), (6.5, "+6,500"), (ROOF["ridge_z"], "+10,650")):
        v.level_mark(ul, z, txt, side="left", len_mm=9)
    if side in ("N", "S"):
        v.level_mark(umax + 1.4, ROOF["eave_edge_z"], "+6,554", side="right", len_mm=9)
    else:
        v.level_mark(umax + 1.4, ROOF["eave_edge_z"], "+6,554", side="right", len_mm=9)
    # оси
    for lbl, uu in axes:
        v.line(uu, zg - 0.5, uu, zg - 1.3, w="thin", dash="4 1.5")
        v.axis_bubble(uu, zg - 1.3, lbl, dy=4)
    # габарит по осям
    v.dim_h(sorted(uu for _, uu in axes), zg - 2.6, 0, text_size=2.4)
    return v


def elev_sheet_ns(sheet_no, total):
    sh = Sheet("A2", code="АР-4", title="Фасады 3-1 и 1-3", scale_txt="1:100", sheet_no=sheet_no, sheets_total=total)
    draw_elevation(sh, "N", 30, 200)
    draw_elevation(sh, "S", 300, 200)
    materials(sh, 40, 262)
    return sh


def elev_sheet_ew(sheet_no, total):
    sh = Sheet("A2", code="АР-5", title="Фасады А-Б и Б-А", scale_txt="1:100", sheet_no=sheet_no, sheets_total=total)
    draw_elevation(sh, "W", 20, 200)
    draw_elevation(sh, "E", 300, 200)
    materials(sh, 40, 262)
    return sh


def materials(sh, x, y):
    sh.ptext(x, y, "Наружная отделка (ведомость)", size=3.2, anchor="start", weight="bold")
    rows = [
        ["1", "Стены", "штукатурка тонкослойная паропроницаемая по газобетону, окраска силикатной краской, RAL 9003 (белый)"],
        ["2", "Фронтоны", "планкен лиственница 20×140, скрытый крепёж, масло с УФ-фильтром, тон «натуральный»"],
        ["3", "Кровля, желоба, козырёк", "фальцевая кровля / водосток сталь с полимерным покрытием RAL 7016 (антрацит)"],
        ["4", "Цоколь", "клинкерная плитка тёмно-серая по ЭППС 50 мм, отлив из окрашенной стали"],
        ["5", "Окна, двери, ворота", "ПВХ/алюминий ламинация RAL 7016 снаружи, белые внутри; ворота секционные RAL 7016"],
        ["6", "Терраса, крыльцо", "керамогранит морозостойкий R11 / крупноформатная плитка по бетонному основанию"],
        ["7", "Ограждения", "французские балконы отсутствуют; ограждение крыльца — сталь, порошковая окраска RAL 7016"],
    ]
    sh.table(x, y + 4, [("№", 8, "c"), ("Элемент", 40, "l"), ("Материал / цвет", 210, "l")], rows, size=2.2)


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "drawings")
    elev_sheet_ns(5, 20).save(os.path.join(out, "АР-4_Фасады_3-1_1-3.svg"))
    elev_sheet_ew(6, 20).save(os.path.join(out, "АР-5_Фасады_А-Б_Б-А.svg"))
    print("ok")
