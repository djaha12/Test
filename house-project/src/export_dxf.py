# -*- coding: utf-8 -*-
"""Экспорт основных чертежей в DXF (R12/AC1009, мм, кодировка cp1251) для AutoCAD/nanoCAD/ArchiCAD.
Файлы: dxf/АР-1_План_1_этажа.dxf, АР-2, ГП-1, КР-1, АР-4 (фасады N/S), АР-5 (фасады E/W)."""
import math, os
from model import *
import draw_site as DS

M = 1000.0   # м → мм


class DXF:
    def __init__(self):
        self.layers = {}
        self.ents = []

    def layer(self, name, color=7):
        self.layers[name] = color

    def line(self, x1, y1, x2, y2, layer):
        self.ents.append(f"0\nLINE\n8\n{layer}\n10\n{x1:.1f}\n20\n{y1:.1f}\n30\n0\n11\n{x2:.1f}\n21\n{y2:.1f}\n31\n0\n")

    def pline(self, pts, layer, closed=True):
        s = f"0\nPOLYLINE\n8\n{layer}\n66\n1\n70\n{1 if closed else 0}\n"
        for x, y in pts:
            s += f"0\nVERTEX\n8\n{layer}\n10\n{x:.1f}\n20\n{y:.1f}\n30\n0\n"
        s += f"0\nSEQEND\n8\n{layer}\n"
        self.ents.append(s)

    def rect(self, x1, y1, x2, y2, layer):
        self.pline([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], layer)

    def circle(self, x, y, r, layer):
        self.ents.append(f"0\nCIRCLE\n8\n{layer}\n10\n{x:.1f}\n20\n{y:.1f}\n30\n0\n40\n{r:.1f}\n")

    def arc(self, x, y, r, a1, a2, layer):
        self.ents.append(f"0\nARC\n8\n{layer}\n10\n{x:.1f}\n20\n{y:.1f}\n30\n0\n40\n{r:.1f}\n50\n{a1:.2f}\n51\n{a2:.2f}\n")

    def text(self, x, y, h, s, layer, rot=0, center=True):
        s = s.replace("\n", " ")
        if center:
            self.ents.append(f"0\nTEXT\n8\n{layer}\n10\n{x:.1f}\n20\n{y:.1f}\n30\n0\n40\n{h:.1f}\n1\n{s}\n50\n{rot}\n72\n1\n73\n2\n11\n{x:.1f}\n21\n{y:.1f}\n31\n0\n")
        else:
            self.ents.append(f"0\nTEXT\n8\n{layer}\n10\n{x:.1f}\n20\n{y:.1f}\n30\n0\n40\n{h:.1f}\n1\n{s}\n50\n{rot}\n")

    def save(self, path):
        out = ["0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n9\n$DWGCODEPAGE\n3\nANSI_1251\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n",
               f"0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n70\n{len(self.layers)}\n"]
        for name, col in self.layers.items():
            out.append(f"0\nLAYER\n2\n{name}\n70\n0\n62\n{col}\n6\nCONTINUOUS\n")
        out.append("0\nENDTAB\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n")
        out.extend(self.ents)
        out.append("0\nENDSEC\n0\nEOF\n")
        with open(path, "w", encoding="cp1251", errors="replace") as f:
            f.write("".join(out))


def std_layers(d):
    for name, col in (("WALLS", 7), ("WALLS_INT", 8), ("OPENINGS", 7), ("WINDOWS", 5), ("DOORS", 3), ("AXES", 1), ("DIM", 4), ("TEXT", 7),
                      ("STAIR", 6), ("VENT", 2), ("OUTDOOR", 8), ("FURN", 9), ("SITE", 3), ("WATER", 5), ("SEWER", 30), ("GAS", 2), ("POWER", 1), ("ROOF", 8), ("REBAR", 1)):
        d.layer(name, col)


def segs_minus(a, b, cuts):
    """отрезок [a,b] минус интервалы cuts → список отрезков"""
    segs = [(a, b)]
    for c1, c2 in cuts:
        new = []
        for s1, s2 in segs:
            if c2 <= s1 or c1 >= s2:
                new.append((s1, s2))
            else:
                if c1 > s1: new.append((s1, c1))
                if c2 < s2: new.append((c2, s2))
        segs = new
    return segs


def Y(y):   # y модели (на юг) → DXF Y (на север)
    return -y * M


def plan_dxf(floor, path):
    d = DXF(); std_layers(d)
    o, i = EXT_OUTER, EXT_INNER
    # проёмы по сторонам
    op = {"N": [], "S": [], "W": [], "E": []}
    for s, a1, a2, h, sill, tag in WINDOWS[floor]:
        op[s].append((a1, a2, "W", tag))
    for s, a1, a2, h, tag, kind in EXT_DOORS[floor]:
        op[s].append((a1, a2, "D", tag))
    # наружные стены: грани с вырезами
    for side in ("N", "S"):
        yo = o[1] if side == "N" else o[3]
        yi = i[1] if side == "N" else i[3]
        cuts = [(a1, a2) for a1, a2, *_ in op[side]]
        for x1, x2 in segs_minus(o[0], o[2], cuts):
            d.line(x1 * M, Y(yo), x2 * M, Y(yo), "WALLS")
        for x1, x2 in segs_minus(i[0], i[2], cuts):
            d.line(x1 * M, Y(yi), x2 * M, Y(yi), "WALLS")
        for a1, a2, kind, tag in op[side]:
            d.line(a1 * M, Y(yo), a1 * M, Y(yi), "OPENINGS"); d.line(a2 * M, Y(yo), a2 * M, Y(yi), "OPENINGS")
            if kind == "W":
                for off in (0.10, 0.16):
                    yy = yo + off if side == "N" else yo - off
                    d.line(a1 * M, Y(yy), a2 * M, Y(yy), "WINDOWS")
            d.text((a1 + a2) / 2 * M, Y(yo - 0.45 if side == "N" else yo + 0.45), 180, tag, "TEXT")
    for side in ("W", "E"):
        xo = o[0] if side == "W" else o[2]
        xi = i[0] if side == "W" else i[2]
        cuts = [(a1, a2) for a1, a2, *_ in op[side]]
        for y1, y2 in segs_minus(o[1], o[3], cuts):
            d.line(xo * M, Y(y1), xo * M, Y(y2), "WALLS")
        for y1, y2 in segs_minus(i[1], i[3], cuts):
            d.line(xi * M, Y(y1), xi * M, Y(y2), "WALLS")
        for a1, a2, kind, tag in op[side]:
            d.line(xo * M, Y(a1), xi * M, Y(a1), "OPENINGS"); d.line(xo * M, Y(a2), xi * M, Y(a2), "OPENINGS")
            for off in (0.10, 0.16):
                xx = xo + off if side == "W" else xo - off
                d.line(xx * M, Y(a1), xx * M, Y(a2), "WINDOWS")
            d.text((xo - 0.45 if side == "W" else xo + 0.45) * M, Y((a1 + a2) / 2), 180, tag, "TEXT", rot=90)
    # внутренние стены
    for w in WALLS[floor]:
        x1, y1, x2, y2 = w["rect"]
        layer = "WALLS" if w["kind"] in ("bear", "fire") else "WALLS_INT"
        horiz = (x2 - x1) > (y2 - y1)
        doors = [dd["rect"] for dd in INT_DOORS[floor] if dd["rect"][0] >= x1 - 1e-3 and dd["rect"][2] <= x2 + 1e-3 and dd["rect"][1] >= y1 - 1e-3 and dd["rect"][3] <= y2 + 1e-3]
        if horiz:
            cuts = [(r[0], r[2]) for r in doors]
            for s1, s2 in segs_minus(x1, x2, cuts):
                d.line(s1 * M, Y(y1), s2 * M, Y(y1), layer); d.line(s1 * M, Y(y2), s2 * M, Y(y2), layer)
            d.line(x1 * M, Y(y1), x1 * M, Y(y2), layer); d.line(x2 * M, Y(y1), x2 * M, Y(y2), layer)
        else:
            cuts = [(r[1], r[3]) for r in doors]
            for s1, s2 in segs_minus(y1, y2, cuts):
                d.line(x1 * M, Y(s1), x1 * M, Y(s2), layer); d.line(x2 * M, Y(s1), x2 * M, Y(s2), layer)
            d.line(x1 * M, Y(y1), x2 * M, Y(y1), layer); d.line(x1 * M, Y(y2), x2 * M, Y(y2), layer)
    # двери
    for dd in INT_DOORS[floor]:
        x1, y1, x2, y2 = dd["rect"]
        horiz = (x2 - x1) > (y2 - y1)
        if horiz:
            d.line(x1 * M, Y(y1), x1 * M, Y(y2), "OPENINGS"); d.line(x2 * M, Y(y1), x2 * M, Y(y2), "OPENINGS")
        else:
            d.line(x1 * M, Y(y1), x2 * M, Y(y1), "OPENINGS"); d.line(x1 * M, Y(y2), x2 * M, Y(y2), "OPENINGS")
        w = dd["w"]
        if dd["swing"]:
            if horiz:
                hx_ = x1 if dd["hinge"] == "W" else x2
                yb = y1 if dd["swing"] == "N" else y2
                diry = -1 if dd["swing"] == "N" else 1
                dirx = 1 if dd["hinge"] == "W" else -1
                tip = (hx_, yb + diry * w); jamb = (hx_ + dirx * w, yb)
            else:
                hy_ = y1 if dd["hinge"] == "N" else y2
                xb = x2 if dd["swing"] == "E" else x1
                dirx = 1 if dd["swing"] == "E" else -1
                diry = 1 if dd["hinge"] == "N" else -1
                tip = (xb + dirx * w, hy_); jamb = (xb, hy_ + diry * w)
                hx_, yb = xb, hy_
            d.line(hx_ * M, Y(yb), tip[0] * M, Y(tip[1]), "DOORS")
            a_t = math.degrees(math.atan2(Y(tip[1]) - Y(yb), tip[0] * M - hx_ * M))
            a_j = math.degrees(math.atan2(Y(jamb[1]) - Y(yb), jamb[0] * M - hx_ * M))
            if (a_j - a_t) % 360 <= 180:
                d.arc(hx_ * M, Y(yb), w * M, a_t, a_j, "DOORS")
            else:
                d.arc(hx_ * M, Y(yb), w * M, a_j, a_t, "DOORS")
        d.text((x1 + x2) / 2 * M, Y((y1 + y2) / 2) + (350 if horiz else 0), 150, dd["tag"], "TEXT", rot=0 if horiz else 90)
    # лестница
    st = STAIR
    f1, f2 = st["flight1"], st["flight2"]
    for k in range(10):
        y = f1["y_start"] + k * st["tread"]
        d.line(f1["x1"] * M, Y(y), f1["x2"] * M, Y(y), "STAIR")
        y2 = f2["y_start"] - k * st["tread"]
        d.line(f2["x1"] * M, Y(y2), f2["x2"] * M, Y(y2), "STAIR")
    d.rect(st["landing"][0] * M, Y(st["landing"][1]), st["landing"][2] * M, Y(st["landing"][3]), "STAIR")
    d.line(f1["x1"] * M, Y(f1["y_start"]), f1["x1"] * M, Y(f1["y_end"]), "STAIR"); d.line(f2["x2"] * M, Y(f2["y_start"]), f2["x2"] * M, Y(f2["y_end"]), "STAIR")
    if floor == 2:
        d.rect(STAIR_WELL[0] * M, Y(STAIR_WELL[1]), STAIR_WELL[2] * M, Y(STAIR_WELL[3]), "STAIR")
    # вентшахты
    for x1, y1, x2, y2, name, desc, floors in VENT_SHAFTS:
        if floor in floors:
            d.rect(x1 * M, Y(y1), x2 * M, Y(y2), "VENT"); d.text((x1 + x2) / 2 * M, Y(y1 - 0.3), 150, name, "VENT")
    # помещения
    for r in ROOMS[floor]:
        rect = max(r["rects"], key=rect_area)
        cx, cy = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
        d.text(cx * M, Y(cy) + 250, 250, f"{r['n']} {r['name']}", "TEXT")
        d.text(cx * M, Y(cy) - 200, 220, f"{room_area(r):.2f} м2", "TEXT")
    # оси
    for lbl, x in AXES_X:
        d.line(x * M, Y(o[1] - 4.0), x * M, Y(o[3] + 4.0), "AXES"); d.circle(x * M, Y(o[1] - 4.5), 400, "AXES"); d.text(x * M, Y(o[1] - 4.5), 350, lbl, "AXES")
        d.circle(x * M, Y(o[3] + 4.5), 400, "AXES"); d.text(x * M, Y(o[3] + 4.5), 350, lbl, "AXES")
    for lbl, y in AXES_Y:
        d.line((o[0] - 3.2) * M, Y(y), (o[2] + 3.2) * M, Y(y), "AXES"); d.circle((o[0] - 3.7) * M, Y(y), 400, "AXES"); d.text((o[0] - 3.7) * M, Y(y), 350, lbl, "AXES")
        d.circle((o[2] + 3.7) * M, Y(y), 400, "AXES"); d.text((o[2] + 3.7) * M, Y(y), 350, lbl, "AXES")
    # размерные цепочки (упрощённо, линии + текст + засечки)
    def chain_h(xs, y, yref):
        for x in xs:
            d.line(x * M, Y(yref), x * M, Y(y) - (200 if y < yref else -200), "DIM")
        d.line(xs[0] * M, Y(y), xs[-1] * M, Y(y), "DIM")
        for k, x in enumerate(xs):
            d.line(x * M - 100, Y(y) - 100, x * M + 100, Y(y) + 100, "DIM")
            if k < len(xs) - 1:
                d.text((x + xs[k + 1]) / 2 * M, Y(y) + 120, 200, f"{(xs[k + 1] - x) * 1000:.0f}", "DIM")

    def chain_v(ys, x, xref):
        for y in ys:
            d.line(xref * M, Y(y), x * M + (200 if x > xref else -200), Y(y), "DIM")
        d.line(x * M, Y(ys[0]), x * M, Y(ys[-1]), "DIM")
        for k, y in enumerate(ys):
            d.line(x * M - 100, Y(y) - 100, x * M + 100, Y(y) + 100, "DIM")
            if k < len(ys) - 1:
                d.text(x * M - 120, Y((y + ys[k + 1]) / 2), 200, f"{(ys[k + 1] - y) * 1000:.0f}", "DIM", rot=90)
    for side, yref, off in (("N", o[1], -2.9), ("S", o[3], 2.9)):
        pts = {o[0], o[2]} | {a for a1, a2, *_ in op[side] for a in (a1, a2)}
        chain_h(sorted(pts), yref + off, yref)
        chain_h([x for _, x in AXES_X], yref + off * 1.35, yref)
        chain_h([o[0], o[2]], yref + off * 1.7, yref)
    for side, xref, off in (("W", o[0], -2.6), ("E", o[2], 2.6)):
        pts = {o[1], o[3]} | {a for a1, a2, *_ in op[side] for a in (a1, a2)}
        chain_v(sorted(pts), xref + off, xref)
        chain_v([y for _, y in AXES_Y], xref + off * 1.35, xref)
        chain_v([o[1], o[3]], xref + off * 1.7, xref)
    # терраса, крыльцо, козырёк
    t = TERRACE["rect"]; d.rect(t[0] * M, Y(t[1]), t[2] * M, Y(t[3]), "OUTDOOR")
    p = PORCH["rect"]; d.rect(p[0] * M, Y(p[1]), p[2] * M, Y(p[3]), "OUTDOOR")
    c = PORCH["canopy"]; d.rect(c[0] * M, Y(c[1]), c[2] * M, Y(c[3]), "OUTDOOR")
    d.text(6.3 * M, Y(-3.6), 400, f"План {floor}-го этажа на отм. {'0,000' if floor == 1 else '+3,300'}. Размеры в мм.", "TEXT")
    d.save(path)


def site_dxf(path):
    d = DXF(); std_layers(d)
    W, D = SITE["width"], SITE["depth"]
    hx, hy = DS.hx, DS.hy
    d.rect(0, Y(0), W * M, Y(D), "SITE")
    d.rect(3.0 * M, Y(5.0), (W - 3.0) * M, Y(D - 3.0), "DIM")
    o = EXT_OUTER
    d.rect(hx(o[0]) * M, Y(hy(o[1])), hx(o[2]) * M, Y(hy(o[3])), "WALLS")
    d.rect(hx(ROOF["eave_edge_x_w"]) * M, Y(hy(ROOF["gable_y_n"])), hx(ROOF["eave_edge_x_e"]) * M, Y(hy(ROOF["gable_y_s"])), "ROOF")
    d.line(hx(6.3) * M, Y(hy(ROOF["gable_y_n"])), hx(6.3) * M, Y(hy(ROOF["gable_y_s"])), "ROOF")
    t = TERRACE["rect"]; d.rect(hx(t[0]) * M, Y(hy(t[1])), hx(t[2]) * M, Y(hy(t[3])), "OUTDOOR")
    p = PORCH["rect"]; d.rect(hx(p[0]) * M, Y(hy(p[1])), hx(p[2]) * M, Y(hy(p[3])), "OUTDOOR")
    d.rect(2.0 * M, Y(0), 8.6 * M, Y(5.0), "OUTDOOR"); d.rect(8.6 * M, Y(0), 9.6 * M, Y(5.0), "OUTDOOR")
    for n, name, x, y, kind, size in DS.OBJECTS:
        if kind == "circle":
            d.circle(x * M, Y(y), size * M, "SITE"); d.text(x * M, Y(y), 300, n, "TEXT")
        elif kind == "box":
            w, h = size; d.rect((x - w / 2) * M, Y(y - h / 2), (x + w / 2) * M, Y(y + h / 2), "SITE"); d.text(x * M, Y(y - h / 2 - 0.6), 300, n, "TEXT")
    d.text(hx(6.3) * M, Y(hy(6.5)), 600, "1", "TEXT")
    for pts, layer in (([(hx(12.8), hy(10.0)), (hx(12.8) + 1.5, hy(10.0)), (hx(12.8) + 1.5, 27.0), (17.4, 27.0), (12.0, 28.8)], "SEWER"),
                       ([(1.5, 2.0), (1.5, 3.5), (hx(4.4), 3.5), (hx(4.4), hy(0.3))], "WATER"),
                       ([(18.4, 0.5), (18.4, 1.5), (hx(5.2), 1.5), (hx(5.2), hy(-0.2))], "GAS"),
                       ([(2.2, 0.5), (2.2, 0.9), (hx(5.0), 0.9), (hx(5.0), hy(-0.2))], "POWER")):
        for k in range(len(pts) - 1):
            d.line(pts[k][0] * M, Y(pts[k][1]), pts[k + 1][0] * M, Y(pts[k + 1][1]), layer)
    d.text(W / 2 * M, Y(-2.0), 500, "Генплан участка 20х30 м. Размеры в мм. Улица — сверху (север).", "TEXT")
    d.save(path)


def foundation_dxf(path):
    d = DXF(); std_layers(d)
    o, i = EXT_OUTER, EXT_INNER
    d.rect(-0.5 * M, Y(-0.5), 13.1 * M, Y(16.1), "WALLS")
    d.rect(o[0] * M, Y(o[1]), o[2] * M, Y(o[3]), "WALLS"); d.rect(i[0] * M, Y(i[1]), i[2] * M, Y(i[3]), "WALLS")
    d.rect(6.175 * M, Y(0.2), 6.425 * M, Y(15.4), "WALLS")
    for x, y, lbl in ((10.6, 5.0, "Ст1 Ø160"), (6.0, 4.8, "Ст2 Ø160"), (0.6, 10.4, "Ст3 Ø160"), (4.4, 0.5, "В1 Ø50"), (5.5, 3.3, "W Ø63")):
        d.circle(x * M, Y(y), 150, "SEWER"); d.text(x * M, Y(y - 0.4), 200, lbl, "TEXT")
    for pts in ([(0.6, 10.4), (13.6, 10.4)], [(6.0, 4.8), (6.0, 10.4)], [(10.6, 5.0), (10.6, 10.4)]):
        d.line(pts[0][0] * M, Y(pts[0][1]), pts[1][0] * M, Y(pts[1][1]), "SEWER")
    d.rect(-1.4 * M, Y(-1.4), 14.0 * M, Y(17.0), "WATER")
    for lbl, x in AXES_X:
        d.line(x * M, Y(-4.0), x * M, Y(19.6), "AXES"); d.circle(x * M, Y(-4.5), 400, "AXES"); d.text(x * M, Y(-4.5), 350, lbl, "AXES")
    for lbl, y in AXES_Y:
        d.line(-3.2 * M, Y(y), 15.8 * M, Y(y), "AXES"); d.circle(-3.7 * M, Y(y), 400, "AXES"); d.text(-3.7 * M, Y(y), 350, lbl, "AXES")
    d.text(6.3 * M, Y(13.0), 250, "Плита 300 B25 W6 F150, сетки С1/С2 Ø14 A500C 200х200, рёбра 400х300 / 250х300", "REBAR")
    d.text(6.3 * M, Y(-3.5), 400, "Схема фундаментной плиты на отм. -0,300. Размеры в мм.", "TEXT")
    d.save(path)


def elevation_dxf(path, sides):
    from draw_elev import side_map, ROOF_T
    d = DXF(); std_layers(d)
    x_off = 0.0
    for side in sides:
        U, umin, umax, axes, title = side_map(side)
        def PX(u): return (x_off + (u - umin)) * M
        o = EXT_OUTER
        zg = LEVELS["grade"]
        if side in ("N", "S"):
            zt_edge = roof_z(o[0]) - ROOF_T; zt_ridge = ROOF["ridge_z"] - ROOF_T
            d.pline([(PX(U(o[0])), 0), (PX(U(o[2])), 0), (PX(U(o[2])), zt_edge * M), (PX(U(6.3)), zt_ridge * M), (PX(U(o[0])), zt_edge * M)], "WALLS")
            xw, xe = ROOF["eave_edge_x_w"], ROOF["eave_edge_x_e"]; ze = ROOF["eave_edge_z"]
            d.pline([(PX(U(xw)), ze * M), (PX(U(6.3)), ROOF["ridge_z"] * M), (PX(U(xe)), ze * M), (PX(U(xe)), (ze - ROOF_T) * M), (PX(U(6.3)), zt_ridge * M), (PX(U(xw)), (ze - ROOF_T) * M)], "ROOF")
        else:
            ze = ROOF["eave_edge_z"]
            d.rect(PX(U(o[1])), 0, PX(U(o[3])), (ze - ROOF_T) * M, "WALLS")
            d.rect(PX(U(ROOF["gable_y_n"])), (ze - ROOF_T) * M, PX(U(ROOF["gable_y_s"])), ze * M, "ROOF")
            d.rect(PX(U(ROOF["gable_y_n"])), ze * M, PX(U(ROOF["gable_y_s"])), ROOF["ridge_z"] * M, "ROOF")
        d.rect(PX(U(o[0] if side in ("N", "S") else o[1])), zg * M, PX(U(o[2] if side in ("N", "S") else o[3])), 0, "WALLS")
        for fl, z0 in ((1, 0.0), (2, 3.3)):
            for s, a1, a2, h, sill, tag in WINDOWS[fl]:
                if s == side:
                    d.rect(PX(U(a1)), (z0 + sill) * M, PX(U(a2)), (z0 + sill + h) * M, "WINDOWS")
        for s, a1, a2, h, tag, kind in EXT_DOORS[1]:
            if s == side:
                zb = LEVELS["garage_floor"] if kind == "garage" else (LEVELS["porch"] if kind == "entrance" else 0.0)
                d.rect(PX(U(a1)), zb * M, PX(U(a2)), (zb + h) * M, "DOORS")
        d.line(PX(umin - 2), zg * M, PX(umax + 2), zg * M, "SITE")
        for lbl, u in axes:
            d.circle(PX(u), (zg - 1.3) * M, 400, "AXES"); d.text(PX(u), (zg - 1.3) * M, 350, lbl, "AXES")
        d.text(PX((umin + umax) / 2), (ROOF["ridge_z"] + 1.0) * M, 400, title, "TEXT")
        x_off += (umax - umin) + 6.0
    d.save(path)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "dxf")
    os.makedirs(out, exist_ok=True)
    plan_dxf(1, os.path.join(out, "АР-1_План_1_этажа.dxf"))
    plan_dxf(2, os.path.join(out, "АР-2_План_2_этажа.dxf"))
    site_dxf(os.path.join(out, "ГП-1_Генплан.dxf"))
    foundation_dxf(os.path.join(out, "КР-1_Фундаментная_плита.dxf"))
    elevation_dxf(os.path.join(out, "АР-4_Фасады_3-1_1-3.dxf"), ("N", "S"))
    elevation_dxf(os.path.join(out, "АР-5_Фасады_А-Б_Б-А.dxf"), ("W", "E"))
    print("dxf ok")
