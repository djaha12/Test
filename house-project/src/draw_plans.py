# -*- coding: utf-8 -*-
"""Планы этажей (АР-1, АР-2) и базовая подложка планов для инженерных схем."""
import math
from model import *
from svg import Sheet, door_symbol, mm, fmt
import furniture as F

WALL_FILL = {"ext": "url(#hAerated)", "bear": "url(#hAerated)", "fire": "url(#hMasonry)", "part": "#d9d9d9"}


def all_wall_rects(floor):
    """Все стены этажа как прямоугольники (наружные — 4 полосы)."""
    o, i = EXT_OUTER, EXT_INNER
    rects = [
        (o[0], o[1], o[2], i[1], "ext"),   # N
        (o[0], i[3], o[2], o[3], "ext"),   # S
        (o[0], o[1], i[0], o[3], "ext"),   # W
        (i[2], o[1], o[2], o[3], "ext"),   # E
    ]
    for w in WALLS[floor]:
        rects.append((*w["rect"], w["kind"]))
    return rects


def draw_walls(v, floor, light=False):
    o, i = EXT_OUTER, EXT_INNER
    # наружные стены — кольцо (even-odd)
    d = (f"M{v.X(o[0]):.2f} {v.Y(o[1]):.2f} H{v.X(o[2]):.2f} V{v.Y(o[3]):.2f} H{v.X(o[0]):.2f} Z "
         f"M{v.X(i[0]):.2f} {v.Y(i[1]):.2f} H{v.X(i[2]):.2f} V{v.Y(i[3]):.2f} H{v.X(i[0]):.2f} Z")
    fill = "#cfcfcf" if light else WALL_FILL["ext"]
    v.s.add(f'<path d="{d}" fill="{fill}" fill-rule="evenodd" stroke="#000" stroke-width="{0.35 if light else 0.7}"/>')
    for w in WALLS[floor]:
        x1, y1, x2, y2 = w["rect"]
        v.rect(x1, y1, x2, y2, fill="#cfcfcf" if light else WALL_FILL[w["kind"]], stroke="#000",
               sw="mid" if (w["kind"] in ("bear", "fire") and not light) else "thin")


def draw_openings(v, floor, light=False):
    o, i = EXT_OUTER, EXT_INNER
    # окна
    for side, a1, a2, h, sill, tag in WINDOWS[floor]:
        if side == "N":
            v.rect(a1, o[1], a2, i[1], fill="#fff", stroke=None)
            v.line(a1, o[1], a1, i[1], w="thin"); v.line(a2, o[1], a2, i[1], w="thin")
            for off in (0.10, 0.16):
                v.line(a1, o[1] + off, a2, o[1] + off, w="mid")
            if not light:
                v.text((a1 + a2) / 2, o[1] - 0.45, tag, size=2.0)
        elif side == "S":
            v.rect(a1, i[3], a2, o[3], fill="#fff", stroke=None)
            v.line(a1, i[3], a1, o[3], w="thin"); v.line(a2, i[3], a2, o[3], w="thin")
            for off in (0.10, 0.16):
                v.line(a1, o[3] - off, a2, o[3] - off, w="mid")
            if not light:
                v.text((a1 + a2) / 2, o[3] + 0.5, tag, size=2.0)
        elif side == "W":
            v.rect(o[0], a1, i[0], a2, fill="#fff", stroke=None)
            v.line(o[0], a1, i[0], a1, w="thin"); v.line(o[0], a2, i[0], a2, w="thin")
            for off in (0.10, 0.16):
                v.line(o[0] + off, a1, o[0] + off, a2, w="mid")
            if not light:
                v.text(o[0] - 0.45, (a1 + a2) / 2, tag, size=2.0, rot=-90)
        else:
            v.rect(i[2], a1, o[2], a2, fill="#fff", stroke=None)
            v.line(i[2], a1, o[2], a1, w="thin"); v.line(i[2], a2, o[2], a2, w="thin")
            for off in (0.10, 0.16):
                v.line(o[2] - off, a1, o[2] - off, a2, w="mid")
            if not light:
                v.text(o[2] + 0.5, (a1 + a2) / 2, tag, size=2.0, rot=-90)
    # наружные двери
    for side, a1, a2, h, tag, kind in EXT_DOORS[floor]:
        if side == "N":
            v.rect(a1, o[1], a2, i[1], fill="#fff", stroke=None)
            v.line(a1, o[1], a1, i[1], w="thin"); v.line(a2, o[1], a2, i[1], w="thin")
            if kind == "entrance":
                # открывается наружу
                v.line(a2, o[1], a2, o[1] - (a2 - a1), w="mid")
                X0, Y0 = v.P(a2, o[1] - (a2 - a1)); X1, Y1 = v.P(a1, o[1]); r = (a2 - a1) * v.k
                v.s.ppath(f"M{X0:.2f} {Y0:.2f} A{r:.2f} {r:.2f} 0 0 0 {X1:.2f} {Y1:.2f}", sw="thin")
            elif kind == "garage":
                v.line(a1, o[1] + 0.12, a2, o[1] + 0.12, w="thick")
                v.line(a1, o[1] + 0.22, a2, o[1] + 0.22, w="thin", dash="2 1")
            if not light:
                v.text((a1 + a2) / 2, o[1] - 0.45, tag, size=2.0)
        elif side == "S":
            v.rect(a1, i[3], a2, o[3], fill="#fff", stroke=None)
            v.line(a1, i[3], a1, o[3], w="thin"); v.line(a2, i[3], a2, o[3], w="thin")
            if kind == "slide":
                mid = (a1 + a2) / 2
                v.line(a1, o[3] - 0.10, mid + 0.05, o[3] - 0.10, w="mid")
                v.line(mid - 0.05, o[3] - 0.18, a2, o[3] - 0.18, w="mid")
                v.line(a1 + 0.2, i[3] - 0.3, mid - 0.1, i[3] - 0.3, w="thin", marker="arrow")
            if not light:
                v.text((a1 + a2) / 2, o[3] + 0.5, tag, size=2.0)
    # внутренние двери / проёмы
    for d in INT_DOORS[floor]:
        x1, y1, x2, y2 = d["rect"]
        v.rect(x1, y1, x2, y2, fill="#fff", stroke=None)
        horizontal = (x2 - x1) > (y2 - y1)
        if horizontal:
            v.line(x1, y1, x1, y2, w="thin"); v.line(x2, y1, x2, y2, w="thin")
        else:
            v.line(x1, y1, x2, y1, w="thin"); v.line(x1, y2, x2, y2, w="thin")
        if d["swing"]:
            door_symbol(v, d["rect"], d["swing"], d["hinge"], d["w"], "h" if horizontal else "v")
        else:
            # открытый проём — пунктир по оси
            if horizontal:
                v.line(x1, (y1 + y2) / 2, x2, (y1 + y2) / 2, w="thin", dash="1.5 1")
            else:
                v.line((x1 + x2) / 2, y1, (x1 + x2) / 2, y2, w="thin", dash="1.5 1")
        if not light:
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            if horizontal:
                v.text_mm(cx, cy, 0, (5 if d["swing"] == "N" else -3.5) if d["swing"] else -3.5, d["tag"], size=1.8)
            else:
                v.text_mm(cx, cy, (-4.5 if d["swing"] == "E" else 4.5) if d["swing"] else 4.5, 0, d["tag"], size=1.8, rot=-90)


def draw_stair(v, floor):
    st = STAIR
    f1, f2 = st["flight1"], st["flight2"]
    t = st["tread"]
    lx1, ly1, lx2, ly2 = st["landing"]
    if floor == 1:
        # марш 1 (восток), вверх на юг
        v.rect(f1["x1"], f1["y_start"], f1["x2"], f1["y_end"], fill="#fff", sw="thin")
        for k in range(10):
            y = f1["y_start"] + k * t
            v.line(f1["x1"], y, f1["x2"], y, w="thin")
            if k < 9:
                v.text((f1["x1"] + f1["x2"]) / 2 + 0.35, y + t / 2, str(k + 1), size=1.6)
        v.rect(lx1, ly1, lx2, ly2, fill="#fff", sw="thin")
        v.text((lx1 + lx2) / 2, (ly1 + ly2) / 2 + 0.35, "площадка +1,737", size=1.7)
        # марш 2 (запад) — виден в плане 1 этажа снизу (пунктир) до линии обрыва
        for k in range(10):
            y = f2["y_start"] - k * t
            v.line(f2["x1"], y, f2["x2"], y, w="thin", dash="1 1")
        # стрелка «вверх»
        cx1 = (f1["x1"] + f1["x2"]) / 2
        cx2 = (f2["x1"] + f2["x2"]) / 2
        pts = [(cx1, f1["y_start"] + 0.15), (cx1, (ly1 + ly2) / 2), (cx2, (ly1 + ly2) / 2), (cx2, f2["y_end"] + 0.3)]
        v.poly(pts, closed=False, sw="mid")
        v.circle(cx1, f1["y_start"] + 0.15, 0.8, fill="#000")
        X, Y = v.P(cx2, f2["y_end"] + 0.3)
        v.s.ppoly([(X, Y - 2.5), (X - 1, Y), (X + 1, Y)], fill="#000", stroke=None)
        v.text(9.65, 7.4, "вверх 19×174", size=1.8)
        # линия обрыва на марше 2
        v.line(f2["x1"] - 0.1, 5.4, f2["x2"] + 0.1, 5.2, w="thin")
    else:
        # проём в перекрытии
        wx1, wy1, wx2, wy2 = STAIR_WELL
        v.rect(wx1, wy1, wx2, wy2, fill="#fff", sw="mid")
        # марш 2 (верхний) — видимый; марш 1 — скрыт (пунктир)
        for k in range(10):
            y = f2["y_start"] - k * t
            v.line(f2["x1"], y, f2["x2"], y, w="thin")
            if k < 9:
                v.text((f2["x1"] + f2["x2"]) / 2 - 0.35, y - t / 2, str(11 + k), size=1.6)
        for k in range(10):
            y = f1["y_start"] + k * t
            v.line(f1["x1"], y, f1["x2"], y, w="thin", dash="1 1")
        v.rect(lx1, ly1, lx2, ly2, fill="#fff", sw="thin")
        v.text((lx1 + lx2) / 2, (ly1 + ly2) / 2 + 0.35, "площадка +1,737", size=1.7)
        # ограждение (толстая линия) вдоль проёма
        v.line(wx2, wy1, wx2, wy2, w="xthick")
        v.line(wx1, wy2, wx2, wy2, w="xthick")
        v.line(f1["x1"], wy1, wx2, wy1, w="xthick")
        v.line(f1["x1"] - 0.1, wy1, f1["x1"] - 0.1, wy1 + 0.3, w="xthick")
        # стрелка «вниз»
        cx2 = (f2["x1"] + f2["x2"]) / 2
        cx1 = (f1["x1"] + f1["x2"]) / 2
        pts = [(cx2, f2["y_end"] + 0.15), (cx2, (ly1 + ly2) / 2), (cx1, (ly1 + ly2) / 2), (cx1, f1["y_start"] + 0.3)]
        v.poly(pts, closed=False, sw="mid")
        v.circle(cx2, f2["y_end"] + 0.15, 0.8, fill="#000")
        X, Y = v.P(cx1, f1["y_start"] + 0.3)
        v.s.ppoly([(X, Y - 2.5), (X - 1, Y), (X + 1, Y)], fill="#000", stroke=None)
        v.text(9.65, 7.4, "вниз 19×174", size=1.8)


def draw_vents(v, floor, label=True):
    for x1, y1, x2, y2, name, desc, floors in VENT_SHAFTS:
        if floor in floors:
            v.rect(x1, y1, x2, y2, fill="url(#hConcrete)", sw="thin")
            if label:
                X, Y = v.P((x1 + x2) / 2, (y1 + y2) / 2)
                side = -1 if x1 > 6.3 else 1
                v.s.prect(X + side * 4.5 - 2.6, Y - 1.5, 5.2, 3.0, fill="#fff", stroke=None, opacity=0.9)
                v.s.ptext(X + side * 4.5, Y, name, size=1.8, weight="bold", anchor="middle")


def draw_room_labels(v, floor, light=False, size=2.6, only_names=False):
    for r in ROOMS[floor]:
        rect = max(r["rects"], key=rect_area)
        cx, cy = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
        off = LABEL_OFFSETS.get((floor, r["n"]), (0, 0))
        cx += off[0]; cy += off[1]
        a = room_area(r)
        col = "#555" if light else "#000"
        if only_names:
            v.text(cx, cy, f"{r['n']} {r['name']}", size=size * 0.8, color=col)
            continue
        wmm = max(len(r["name"]), 9) * size * 0.58 + 2
        X, Y = v.P(cx, cy)
        v.s.prect(X - wmm / 2, Y - 4.0, wmm, 10.4, fill="#fff", stroke=None, opacity=0.85)
        v.text_mm(cx, cy, 0, -2.2, f"{r['n']}", size=size * 0.85, color=col, weight="bold")
        v.text_mm(cx, cy, 0, 1.2, r["name"], size=size, color=col)
        v.text_mm(cx, cy, 0, 4.4, f"{a:.2f} м²".replace(".", ","), size=size * 0.9, color=col)


LABEL_OFFSETS = {
    (1, "1.02"): (0.0, 0.0),
    (1, "1.04"): (0.9, -1.2),
    (1, "1.07"): (0.0, 1.8),
    (1, "1.08"): (0.3, -0.6),
    (1, "1.14"): (0.0, 2.4),
    (2, "2.02"): (0.6, 0.0),
    (2, "2.07"): (0.0, 0.9),
    (2, "2.14"): (-0.8, -0.6),
    (2, "2.01"): (-1.0, 0.0),
}


def draw_axes(v, floor_or_none=None, top=True, bottom=True, left=True, right=True, ext_mm=30):
    o = EXT_OUTER
    for lbl, x in AXES_X:
        y_top = o[1] - 4.0
        y_bot = o[3] + 4.0
        v.axis_line(x, y_top, x, y_bot)
        if top:
            v.axis_bubble(x, y_top, lbl, dy=-4)
        if bottom:
            v.axis_bubble(x, y_bot, lbl, dy=4)
    for lbl, y in AXES_Y:
        x_l = o[0] - 3.2
        x_r = o[2] + 3.2
        v.axis_line(x_l, y, x_r, y)
        if left:
            v.axis_bubble(x_l, y, lbl, dx=-4)
        if right:
            v.axis_bubble(x_r, y, lbl, dx=4)


def ext_dims(v, floor):
    o = EXT_OUTER
    # север
    pts = {o[0], o[2]}
    for side, a1, a2, *_ in WINDOWS[floor]:
        if side == "N":
            pts |= {a1, a2}
    for side, a1, a2, *_ in EXT_DOORS[floor]:
        if side == "N":
            pts |= {a1, a2}
    y_ref = -2.7
    v.dim_h(sorted(pts), y_ref, -6, ext_from=o[1])
    v.dim_h([x for _, x in AXES_X], y_ref, -14, ext_from=o[1])
    v.dim_h([o[0], o[2]], y_ref, -22, ext_from=o[1])
    # юг
    pts = {o[0], o[2]}
    for side, a1, a2, *_ in WINDOWS[floor]:
        if side == "S":
            pts |= {a1, a2}
    for side, a1, a2, *_ in EXT_DOORS[floor]:
        if side == "S":
            pts |= {a1, a2}
    y_ref = TERRACE["rect"][3] + 0.2
    v.dim_h(sorted(pts), y_ref, 6, ext_from=o[3], flip_text=True)
    v.dim_h([x for _, x in AXES_X], y_ref, 14, ext_from=o[3], flip_text=True)
    v.dim_h([o[0], o[2]], y_ref, 22, ext_from=o[3], flip_text=True)
    # запад
    pts = {o[1], o[3]}
    for side, a1, a2, *_ in WINDOWS[floor]:
        if side == "W":
            pts |= {a1, a2}
    v.dim_v(sorted(pts), o[0], -6)
    v.dim_v([y for _, y in AXES_Y], o[0], -14)
    v.dim_v([o[1], o[3]], o[0], -22)
    # восток
    pts = {o[1], o[3]}
    for side, a1, a2, *_ in WINDOWS[floor]:
        if side == "E":
            pts |= {a1, a2}
    v.dim_v(sorted(pts), o[2], 6)
    v.dim_v([o[1], o[3]], o[2], 14)


def interior_chain_h(v, floor, y0, x_from=None, x_to=None):
    x_from = EXT_OUTER[0] if x_from is None else x_from
    x_to = EXT_OUTER[2] if x_to is None else x_to
    pts = set()
    for x1, y1, x2, y2, kind in all_wall_rects(floor):
        if y1 <= y0 <= y2 and x2 > x_from and x1 < x_to:
            pts |= {max(x1, x_from), min(x2, x_to)}
    pts = sorted(pts)
    v.dim_h(pts, y0, 0, text_size=1.9)


def interior_chain_v(v, floor, x0, y_from=None, y_to=None):
    y_from = EXT_OUTER[1] if y_from is None else y_from
    y_to = EXT_OUTER[3] if y_to is None else y_to
    pts = set()
    for x1, y1, x2, y2, kind in all_wall_rects(floor):
        if x1 <= x0 <= x2 and y2 > y_from and y1 < y_to:
            pts |= {max(y1, y_from), min(y2, y_to)}
    pts = sorted(pts)
    v.dim_v(pts, x0, 0, text_size=1.9)


def draw_outdoor(v, floor, light=False):
    t = TERRACE["rect"]
    v.rect(*t, fill="url(#hPaving)" if not light else "none", sw="thin")
    if not light:
        v.text((t[0] + t[2]) / 2, (t[1] + t[3]) / 2 - 0.5, "Терраса 37,8 м²", size=2.4)
        v.text((t[0] + t[2]) / 2, (t[1] + t[3]) / 2 + 0.2, "отм. −0,150, мощение по бетонному основанию", size=1.9)
        # ступени в сад
        for i in range(3):
            v.line(t[0] + 4.0, t[3] + 0.15 * i, t[0] + 6.0, t[3] + 0.15 * i, w="thin")
    p = PORCH["rect"]
    v.rect(*p, fill="#fff", sw="thin")
    for i in range(3):
        v.line(p[0], p[1] + 0.3 * i, p[2], p[1] + 0.3 * i, w="thin")
    if not light:
        v.text((p[0] + p[2]) / 2, p[1] + 1.3, "крыльцо −0,030", size=1.9)
    c = PORCH["canopy"]
    v.rect(*c, sw="thin", dash="2 1")
    a = GARAGE_APRON["rect"]
    v.rect(*a, sw="thin", dash="1 1")
    if not light:
        v.text((a[0] + a[2]) / 2, a[1] + 1.2, "пандус i=8%", size=1.9)
    # отмостка
    o = EXT_OUTER
    v.rect(o[0] - 1.0, o[1] - 1.0, o[2] + 1.0, o[3] + 1.0, sw="thin", dash="0.5 1")


def draw_furniture(v, floor):
    if floor == 1:
        F.car(v, 1.05, 0.9)
        F.wardrobe(v, 0.2, 0.2, 0.7, 6.6)
        F.boiler(v, 4.4, 0.25)
        F.cylinder(v, 5.3, 1.6)
        v.rect(4.2, 2.2, 4.9, 2.8, stroke="#666", sw="thin", fill="#fff"); v.text(4.55, 2.5, "ВО", size=1.7, color="#666")
        F.washer(v, 4.2, 3.1); F.washer(v, 4.85, 3.1)
        F.basin(v, 5.9, 3.0, orient="S")
        F.wardrobe(v, 4.1, 5.9, 6.175, 6.6)
        F.desk(v, 0.35, 8.2, 1.5, 0.75, chair="E")
        F.wardrobe(v, 3.5, 6.85, 4.0, 8.5)
        F.wardrobe(v, 4.1, 6.8, 4.5, 8.2); F.wardrobe(v, 5.775, 6.8, 6.175, 8.2)
        F.counter(v, 0.2, 10.35, 0.8, 15.0, sink=(0.5, 12.3))
        F.counter(v, 0.8, 10.35, 4.5, 10.95, hob=(2.8, 10.65))
        F.counter(v, 2.2, 12.2, 3.4, 13.9)
        F.table(v, 4.0, 12.8, 2.0, 1.0, chairs=6)
        F.sofa(v, 6.9, 10.6, 3.0, 1.0, back="S")
        F.round_table(v, 8.4, 9.7, 0.45)
        v.rect(7.0, 8.15, 8.3, 8.3, stroke="#666", sw="thin", fill="#fff")
        F.sofa(v, 10.5, 9.3, 0.9, 0.9, back="E"); F.sofa(v, 10.5, 10.5, 0.9, 0.9, back="E")
        F.wardrobe(v, 10.5, 0.2, 12.4, 0.8)
        F.wc(v, 11.9, 6.1, "N"); F.basin(v, 12.4, 4.9, orient="W"); F.shower(v, 10.55, 5.2, 0.85)
        F.wardrobe(v, 10.5, 7.5, 12.4, 8.0)
        F.round_table(v, 9.0, 17.3, 0.6)
    else:
        F.sofa(v, 9.0, 0.3, 3.0, 0.9, back="N"); F.round_table(v, 10.5, 2.0, 0.4)
        F.wardrobe(v, 6.45, 0.25, 6.95, 2.3)
        F.bed(v, 2.0, 2.3, 1.8, 2.1, head="S")
        F.wardrobe(v, 4.9, 0.25, 6.15, 2.3)
        F.desk(v, 0.3, 0.3, 1.4, 0.7, chair="S")
        F.bath(v, 0.25, 4.65)
        F.shower(v, 0.22, 6.8, 0.8)
        F.wc(v, 2.85, 8.0, "N"); F.basin(v, 3.2, 6.2, orient="W")
        F.washer(v, 3.35, 4.65); F.washer(v, 4.0, 4.65); F.basin(v, 5.0, 4.6, orient="S")
        v.rect(3.4, 7.0, 4.9, 7.4, stroke="#666", sw="thin", fill="#fff")
        F.wardrobe(v, 5.6, 5.1, 6.15, 7.9)
        F.bath(v, 10.55, 6.0); F.wc(v, 11.9, 4.0, "S"); F.basin(v, 12.4, 5.2, orient="W")
        F.wardrobe(v, 10.5, 6.95, 12.4, 7.5); F.wardrobe(v, 11.9, 7.5, 12.4, 9.35)
        F.single_bed(v, 8.25, 9.6, head="N"); F.desk(v, 7.3, 14.6, 1.4, 0.7, chair="N"); F.wardrobe(v, 6.45, 9.55, 6.95, 11.5)
        F.bed(v, 10.9, 9.55, 1.4, 2.0, head="N"); F.desk(v, 10.3, 14.6, 1.4, 0.7, chair="N"); F.wardrobe(v, 9.35, 11.0, 9.95, 13.0)
        F.bed(v, 4.05, 12.9, 2.1, 1.8, head="E")
        v.rect(4.05, 12.4, 4.55, 12.85, stroke="#666", sw="thin"); v.rect(4.05, 14.75, 4.55, 15.2, stroke="#666", sw="thin")
        v.rect(0.25, 12.9, 0.75, 14.2, stroke="#666", sw="thin", fill="#fff")
        F.shower(v, 0.25, 9.55, 0.9); F.wc(v, 1.75, 9.5, "S"); F.basin(v, 0.2, 11.0, orient="E")
        F.wardrobe(v, 2.75, 9.55, 3.25, 11.65); F.wardrobe(v, 4.05, 9.55, 4.55, 11.65)


def section_marks(v):
    o = EXT_OUTER
    # 1-1: горизонтальная на y=5.0, взгляд на юг
    y = 5.0
    for x, side in ((o[0] - 3.4, -1), (o[2] + 3.4, 1)):
        v.line(x, y, x + side * 0.8, y, w="xthick")
        v.line(x + side * 0.4, y, x + side * 0.4, y + 0.9, w="mid", marker="arrow")
        v.text_mm(x + side * 0.4, y, 0, -3, "1", size=4, weight="bold")
    v.line(o[0] - 3.0, y, o[0] - 1.5, y, w="thin", dash="4 1.5"); v.line(o[2] + 1.5, y, o[2] + 3.0, y, w="thin", dash="4 1.5")
    # 2-2: вертикальная на x=9.6, взгляд на запад
    x = 9.6
    for y, side in ((o[1] - 3.6, -1), (TERRACE["rect"][3] + 1.2, 1)):
        v.line(x, y, x, y + side * 0.8, w="xthick")
        v.line(x, y + side * 0.4, x - 0.9, y + side * 0.4, w="mid", marker="arrow")
        v.text_mm(x, y + side * 0.4, 3.5, 0, "2", size=4, weight="bold")


def base_plan(v, floor, light=False, labels=True, furniture=False, vents=True, names_only=False):
    """Подложка плана: стены, проёмы, лестница, вентканалы, подписи."""
    draw_outdoor(v, floor, light=True)
    draw_walls(v, floor, light=light)
    draw_openings(v, floor, light=light)
    draw_stair(v, floor)
    if vents:
        draw_vents(v, floor, label=not light)
    if furniture:
        draw_furniture(v, floor)
    if labels:
        draw_room_labels(v, floor, light=light, only_names=names_only, size=2.2 if names_only else 2.6)


def schedule_table(sh, floor, x, y):
    rows = []
    total = 0.0
    for r in ROOMS[floor]:
        a = room_area(r)
        total += a
        rows.append([r["n"], r["name"], f"{a:.2f}".replace(".", ","), r["finish"]])
    rows.append(["", "Итого по этажу", f"{total:.2f}".replace(".", ","), ""])
    cols = [("№", 14, "c"), ("Наименование помещения", 62, "l"), ("Площадь, м²", 24, "r"), ("Пол", 44, "l")]
    sh.ptext(x, y - 5, f"Экспликация помещений {floor}-го этажа", size=3.2, anchor="start", weight="bold")
    return sh.table(x, y, cols, rows, size=2.4)


def legend(sh, x, y):
    sh.ptext(x, y, "Условные обозначения", size=3.0, anchor="start", weight="bold")
    items = [
        ("url(#hAerated)", "Наружные стены — газобетон D400 B2.5, 400 мм (несущие)"),
        ("url(#hAerated)", "Внутренняя несущая стена по оси 2 — газобетон D500 B3.5, 250 мм"),
        ("url(#hMasonry)", "Перегородки 200 мм (гараж, котельная) — газобетон D500, REI 45"),
        ("#d9d9d9", "Перегородки 100 мм — газобетон D500 (в мокрых зонах — гидроизоляция)"),
        ("url(#hConcrete)", "Вентиляционные каналы В1…В7 (сталь/пластик Ø125–160 в шахте)"),
    ]
    yy = y + 6
    for fill, txt in items:
        sh.prect(x, yy - 2.5, 10, 5, fill=fill, sw="thin")
        sh.ptext(x + 13, yy, txt, size=2.3, anchor="start")
        yy += 7.5
    return yy


def notes(sh, x, y, lines, title="Примечания"):
    sh.ptext(x, y, title, size=3.0, anchor="start", weight="bold")
    sh.ptext_lines(x, y + 6, lines, size=2.3, lh=4.2)
    return y + 6 + 4.2 * len(lines)


def floor_plan_sheet(floor, sheet_no, total):
    lvl = "0,000" if floor == 1 else "+3,300"
    sh = Sheet("A1", code=f"АР-{floor}", title=f"План {floor}-го этажа на отм. {lvl}", scale_txt="1:50",
               sheet_no=sheet_no, sheets_total=total)
    v = sh.view(ox=75, oy=95, scale=50)
    sh.ptext(470, 22, f"План {floor}-го этажа на отм. {lvl}   М 1:50", size=5, anchor="start", weight="bold")
    base_plan(v, floor, light=False, labels=True, furniture=True)
    draw_axes(v)
    ext_dims(v, floor)
    if floor == 1:
        interior_chain_h(v, 1, 5.0)
        interior_chain_h(v, 1, 12.0)
        interior_chain_v(v, 1, 2.0)
        interior_chain_v(v, 1, 11.5)
        section_marks(v)
        v.level_mark(1.2, 6.15, "−0,280 (гараж)", side="right")
        v.text(9.0, 6.3, "±0,000", size=2.4)
    else:
        interior_chain_h(v, 2, 2.0)
        interior_chain_h(v, 2, 12.5)
        interior_chain_v(v, 2, 1.5)
        interior_chain_v(v, 2, 11.5)
        section_marks(v)
        v.text(9.6, 6.0, "+3,300", size=2.4)
    v.north_arrow(15.5, -2.2)
    # правая часть: экспликация, легенда, примечания
    xr = 470
    yy = schedule_table(sh, floor, xr, 40)
    yy = legend(sh, xr, yy + 14)
    lines = [
        "1. Отметка ±0,000 соответствует уровню чистого пола 1-го этажа; планировочная отметка земли −0,450.",
        "2. Высота этажа 3,300 (в чистоте 3,000). Перекрытия — монолитные ж/б плиты 200 мм по СП 63.13330.",
        "3. Наружные стены — газобетон D400 B2.5 400 мм на клею (шов 2–3 мм), наружная отделка — паропроницаемая",
        "   штукатурка 10 мм, фронтоны — планкен из лиственницы; цоколь — клинкерная плитка по ЭППС 50 мм.",
        "4. Перемычки — из U-блоков с монолитным ж/б заполнением (см. КР-2), над проёмами ≥ 2,4 м — монолитные балки.",
        "5. Окна — ПВХ 70 мм, 2-камерный стеклопакет с i-стеклом и аргоном, R ≥ 0,72 м²·°С/Вт; цвет — антрацит.",
        "6. Полы 1-го этажа: по плите — ЭППС/ПСБ-С 150 мм, стяжка 120 мм с трубами тёплого пола, покрытие.",
        "7. Гараж — отапливаемый (+10 °С), отделён противопожарными перегородками EI 45 и дверью EI 30.",
        "8. Котельная: газовый конденсационный котёл 32 кВт, окно 0,9×1,2 (≥0,03 м²/м³), вентканал В1, дверь EI 30.",
        "9. Расстановка мебели и оборудования — условная, для проверки функциональности планировки.",
    ]
    notes(sh, xr, yy + 8, lines)
    return sh


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "drawings")
    os.makedirs(out, exist_ok=True)
    floor_plan_sheet(1, 2, 20).save(os.path.join(out, "АР-1_План_1_этажа.svg"))
    floor_plan_sheet(2, 3, 20).save(os.path.join(out, "АР-2_План_2_этажа.svg"))
    print("ok")
