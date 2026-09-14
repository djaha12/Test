# -*- coding: utf-8 -*-
"""Экспорт геометрии дома и участка в JSON для three.js-вьюера (3d/model.json)."""
import json, os
from model import *

HX, HY = SITE["house_origin"]


def box(x1, y1, x2, y2, z1, z2, mat, name=""):
    return {"t": "box", "x": [min(x1, x2), max(x1, x2)], "y": [min(y1, y2), max(y1, y2)], "z": [z1, z2], "m": mat, "n": name}


def build():
    items = []
    # --- стены наружные: 4 полосы по этажам (с проёмами как вырезами не делаем; окна — накладные панели)
    o, i = EXT_OUTER, EXT_INNER
    for (z1, z2) in ((0.0, 3.2), (3.2, 6.5)):
        items.append(box(o[0], o[1], o[2], i[1], z1, z2, "wall"))
        items.append(box(o[0], i[3], o[2], o[3], z1, z2, "wall"))
        items.append(box(o[0], o[1], i[0], o[3], z1, z2, "wall"))
        items.append(box(i[2], o[1], o[2], o[3], z1, z2, "wall"))
    # цоколь
    items.append(box(o[0] - 0.02, o[1] - 0.02, o[2] + 0.02, o[3] + 0.02, LEVELS["grade"] - 0.3, 0.0, "plinth"))
    # фронтоны (треугольники) — как экструзия
    zt_edge = roof_z(o[0]) - 0.28
    zt_ridge = ROOF["ridge_z"] - 0.28
    items.append({"t": "gable", "y": o[1] - 0.3, "y2": o[1] + 0.0, "pts": [[o[0], 6.5], [o[2], 6.5], [o[2], zt_edge], [6.3, zt_ridge], [o[0], zt_edge]], "m": "wood"})
    items.append({"t": "gable", "y": o[3] - 0.0, "y2": o[3] + 0.3, "pts": [[o[0], 6.5], [o[2], 6.5], [o[2], zt_edge], [6.3, zt_ridge], [o[0], zt_edge]], "m": "wood"})
    # внутренние стены (для разреза/интерьера)
    for fl, (z1, z2) in ((1, (0.0, 3.0)), (2, (3.3, 6.3))):
        for w in WALLS[fl]:
            x1, y1, x2, y2 = w["rect"]
            items.append(box(x1, y1, x2, y2, z1, z2, "wall_int"))
    # перекрытия
    items.append(box(o[0] + 0.1, o[1] + 0.1, 6.425, o[3] - 0.1, 3.0, 3.2, "slab"))
    items.append(box(6.425, o[1] + 0.1, o[2] - 0.1, STAIR_WELL[1], 3.0, 3.2, "slab"))
    items.append(box(6.425, STAIR_WELL[3], o[2] - 0.1, o[3] - 0.1, 3.0, 3.2, "slab"))
    items.append(box(STAIR_WELL[2], STAIR_WELL[1], o[2] - 0.1, STAIR_WELL[3], 3.0, 3.2, "slab"))
    items.append(box(o[0] + 0.1, o[1] + 0.1, o[2] - 0.1, o[3] - 0.1, 6.3, 6.5, "slab"))
    # пол 1 этажа
    items.append(box(o[0], o[1], o[2], o[3], -0.6, 0.0, "slab"))
    # кровля: два ската как наклонные плиты + конёк
    xw, xe, rx = ROOF["eave_edge_x_w"], ROOF["eave_edge_x_e"], ROOF["ridge_x"]
    yn, ys = ROOF["gable_y_n"], ROOF["gable_y_s"]
    ze, zr = ROOF["eave_edge_z"], ROOF["ridge_z"]
    items.append({"t": "roof", "pts": [[xw, ze], [rx, zr], [rx, zr - 0.28], [xw, ze - 0.28]], "y": yn, "y2": ys, "m": "roof"})
    items.append({"t": "roof", "pts": [[rx, zr], [xe, ze], [xe, ze - 0.28], [rx, zr - 0.28]], "y": yn, "y2": ys, "m": "roof"})
    items.append(box(rx - 0.12, yn, rx + 0.12, ys, zr - 0.02, zr + 0.08, "roof_dark"))
    # желоба
    items.append(box(xw - 0.15, yn, xw, ys, ze - 0.14, ze - 0.02, "roof_dark"))
    items.append(box(xe, yn, xe + 0.15, ys, ze - 0.14, ze - 0.02, "roof_dark"))
    for xx in (o[0] - 0.08, o[2] + 0.08):
        for yy in (o[1] + 0.35, o[3] - 0.35):
            items.append(box(xx - 0.05, yy - 0.05, xx + 0.05, yy + 0.05, LEVELS["grade"], ze - 0.5, "roof_dark"))
            # колено к желобу
            xa, xb = (xx - 0.05, xw + 0.1) if xx < 6.3 else (xe - 0.1, xx + 0.05)
            items.append(box(xa, yy - 0.05, xb, yy + 0.05, ze - 0.5, ze - 0.4, "roof_dark"))
    # вентвыходы
    for x1, y1, x2, y2, name, desc, floors in VENT_SHAFTS:
        xc = (x1 + x2) / 2
        items.append(box(x1, y1, x2, y2, roof_z(xc) - 0.2, roof_z(xc) + 0.7, "roof_dark"))
    # окна и двери — панели на фасаде (чуть выступают)
    for fl, z0 in ((1, 0.0), (2, 3.3)):
        for s, a1, a2, h, sill, tag in WINDOWS[fl]:
            z1, z2 = z0 + sill, z0 + sill + h
            if s == "N": items.append(box(a1, o[1] - 0.03, a2, o[1] + 0.12, z1, z2, "glass"))
            elif s == "S": items.append(box(a1, o[3] - 0.12, a2, o[3] + 0.03, z1, z2, "glass"))
            elif s == "W": items.append(box(o[0] - 0.03, a1, o[0] + 0.12, a2, z1, z2, "glass"))
            else: items.append(box(o[2] - 0.12, a1, o[2] + 0.03, a2, z1, z2, "glass"))
    for s, a1, a2, h, tag, kind in EXT_DOORS[1]:
        if s == "N":
            zb = LEVELS["garage_floor"] if kind == "garage" else LEVELS["porch"]
            items.append(box(a1, o[1] - 0.03, a2, o[1] + 0.12, zb, zb + h, "door" if kind != "garage" else "garage"))
        else:
            items.append(box(a1, o[3] - 0.12, a2, o[3] + 0.03, 0.0, h, "glass"))
    # терраса, крыльцо, козырёк, пандус
    t = TERRACE["rect"]
    items.append(box(t[0], t[1], t[2], t[3], LEVELS["grade"], TERRACE["level"], "paving"))
    p = PORCH["rect"]
    items.append(box(p[0], p[1], p[2], p[3], LEVELS["grade"], LEVELS["porch"], "paving"))
    for k, zz in enumerate((-0.31, -0.17)):
        items.append(box(p[0], p[1] - 0.3 * (k + 1), p[2], p[1] - 0.3 * k, LEVELS["grade"], zz, "paving"))
    c = PORCH["canopy"]
    items.append(box(c[0], c[1], c[2], c[3], PORCH["canopy_z"], PORCH["canopy_z"] + 0.15, "roof_dark"))
    for xx in (c[0] + 0.3, c[2] - 0.3):
        items.append(box(xx - 0.03, c[1] + 0.2, xx + 0.03, c[3], PORCH["canopy_z"] - 0.05, PORCH["canopy_z"], "roof_dark"))
        items.append(box(xx - 0.03, c[3] - 0.3, xx + 0.03, c[3], PORCH["canopy_z"] - 0.6, PORCH["canopy_z"], "roof_dark"))
    a = GARAGE_APRON["rect"]
    items.append(box(a[0], a[1], a[2], a[3], LEVELS["grade"] - 0.02, LEVELS["grade"] + 0.06, "paving"))
    # лестница внутренняя (упрощённо)
    st = STAIR
    f1, f2 = st["flight1"], st["flight2"]
    for k in range(9):
        y = f1["y_start"] + k * st["tread"]
        items.append(box(f1["x1"], y, f1["x2"], y + st["tread"], 0, (k + 1) * st["riser_h"], "stair"))
    items.append(box(*st["landing"][:2], *st["landing"][2:], st["landing_z"] - 0.2, st["landing_z"], "stair"))
    for k in range(9):
        y = f2["y_start"] - (k + 1) * st["tread"]
        items.append(box(f2["x1"], y, f2["x2"], y + st["tread"], st["landing_z"] - 0.2, st["landing_z"] + (k + 1) * st["riser_h"], "stair"))
    # --- участок (в координатах дома: участок сдвинут на -HX, -HY)
    W, D = SITE["width"], SITE["depth"]
    site = {"x": [-HX, W - HX], "y": [-HY, D - HY], "z": LEVELS["grade"]}
    site_items = []
    site_items.append(box(-HX + 2.0 - 0.0, -HY, -HX + 8.6, -HY + 5.0, LEVELS["grade"] - 0.01, LEVELS["grade"] + 0.02, "asphalt"))
    site_items.append(box(-HX + 8.6, -HY, -HX + 9.6, -HY + 5.0, LEVELS["grade"] - 0.01, LEVELS["grade"] + 0.02, "paving"))
    site_items.append(box(o[0] - 1.0, o[1] - 1.0, o[2] + 1.0, o[3] + 1.0, LEVELS["grade"] - 0.02, LEVELS["grade"] + 0.01, "concrete"))
    site_items.append(box(o[2] + 1.0, o[1] - 1.0, o[2] + 2.0, o[3] + 3.0, LEVELS["grade"] - 0.01, LEVELS["grade"] + 0.02, "paving"))
    # забор
    zg = LEVELS["grade"]
    fence = []
    for (x1, y1, x2, y2, h) in ((-HX, -HY, W - HX, -HY + 0.05, 1.8), (-HX, D - HY - 0.05, W - HX, D - HY, 1.6), (-HX, -HY, -HX + 0.05, D - HY, 1.6), (W - HX - 0.05, -HY, W - HX, D - HY, 1.6)):
        fence.append(box(x1, y1, x2, y2, zg, zg + h, "fence"))
    # ворота/калитка — проём в заборе (упрощённо: тёмная панель)
    trees = [(2.0, 27.5, 1.8, 5.0), (6.0, 28.2, 1.6, 4.5), (10.0, 27.8, 1.8, 5.0), (18.5, 20.0, 1.4, 4.0), (18.5, 15.0, 1.4, 4.0), (18.5, 8.0, 1.2, 3.5), (1.2, 12.0, 1.0, 3.0), (1.2, 16.5, 1.0, 3.0)]
    trees = [{"x": x - HX, "y": y - HY, "r": r, "h": h} for x, y, r, h in trees]
    objs = [{"x": 1.5 - HX, "y": 2.0 - HY, "r": 0.75, "h": 0.15, "m": "concrete", "n": "скважина"},
            {"x": 18.0 - HX, "y": 27.0 - HY, "r": 0.6, "h": 0.15, "m": "concrete", "n": "СБО"},
            {"x": 15.0 - HX, "y": 28.5 - HY, "r": 0.5, "h": 0.1, "m": "concrete", "n": "дренажный колодец"}]
    cars = [{"x": 2.4 + 1.25 - HX, "y": 0.3 + 2.5 - HY}, {"x": 5.2 + 1.25 - HX, "y": 0.3 + 2.5 - HY}]
    return {"items": items, "site": site, "site_items": site_items, "fence": fence, "trees": trees, "objs": objs, "cars": cars,
            "levels": LEVELS, "ridge": ROOF["ridge_z"], "house": {"x": [o[0], o[2]], "y": [o[1], o[3]]},
            "summary": summary()}


MTL = {"wall": (0.95, 0.94, 0.91), "wall_int": (0.97, 0.96, 0.94), "plinth": (0.36, 0.33, 0.31), "wood": (0.79, 0.60, 0.36), "slab": (0.81, 0.81, 0.81),
       "roof": (0.24, 0.25, 0.26), "roof_dark": (0.17, 0.18, 0.19), "glass": (0.56, 0.72, 0.85), "door": (0.29, 0.31, 0.32), "garage": (0.54, 0.55, 0.56),
       "paving": (0.72, 0.71, 0.67), "asphalt": (0.55, 0.55, 0.55), "concrete": (0.79, 0.79, 0.79), "fence": (0.42, 0.44, 0.45), "stair": (0.85, 0.83, 0.80),
       "grass": (0.50, 0.69, 0.41), "trunk": (0.42, 0.29, 0.16), "crown": (0.31, 0.56, 0.25)}


def write_obj(data, path):
    """Экспорт в Wavefront OBJ (+MTL). Оси: Y — вверх (x, z, −y), метры."""
    V = []
    F = {}   # material -> list of faces (списки индексов вершин, 1-based)

    def vtx(x, y, z):
        V.append((x, z, -y))
        return len(V)

    def quad(mat, a, b, c, d):
        F.setdefault(mat, []).append((a, b, c, d))

    def box(it):
        x1, x2 = it["x"]; y1, y2 = it["y"]; z1, z2 = it["z"]
        m = it["m"]
        p = [vtx(x1, y1, z1), vtx(x2, y1, z1), vtx(x2, y2, z1), vtx(x1, y2, z1), vtx(x1, y1, z2), vtx(x2, y1, z2), vtx(x2, y2, z2), vtx(x1, y2, z2)]
        quad(m, p[0], p[3], p[2], p[1])   # низ
        quad(m, p[4], p[5], p[6], p[7])   # верх
        quad(m, p[0], p[1], p[5], p[4])   # y1
        quad(m, p[2], p[3], p[7], p[6])   # y2
        quad(m, p[0], p[4], p[7], p[3])   # x1
        quad(m, p[1], p[2], p[6], p[5])   # x2

    def extrude(it):
        pts, ya, yb, m = it["pts"], it["y"], it["y2"], it["m"]
        a = [vtx(x, ya, z) for x, z in pts]
        b = [vtx(x, yb, z) for x, z in pts]
        F.setdefault(m, []).append(tuple(reversed(a)))
        F.setdefault(m, []).append(tuple(b))
        n = len(pts)
        for k in range(n):
            quad(m, a[k], a[(k + 1) % n], b[(k + 1) % n], b[k])

    for it in data["items"] + data["site_items"] + data["fence"]:
        if it["t"] == "box":
            box(it)
        else:
            extrude(it)
    s = data["site"]
    g = [vtx(s["x"][0], s["y"][0], s["z"]), vtx(s["x"][1], s["y"][0], s["z"]), vtx(s["x"][1], s["y"][1], s["z"]), vtx(s["x"][0], s["y"][1], s["z"])]
    F.setdefault("grass", []).append(tuple(g))
    for t in data["trees"]:
        r, h = t["r"], t["h"]
        box({"x": [t["x"] - 0.1, t["x"] + 0.1], "y": [t["y"] - 0.1, t["y"] + 0.1], "z": [s["z"], s["z"] + h * 0.45], "m": "trunk"})
        box({"x": [t["x"] - r, t["x"] + r], "y": [t["y"] - r, t["y"] + r], "z": [s["z"] + h * 0.45, s["z"] + h * 0.45 + 1.6 * r], "m": "crown"})
    mtl_path = os.path.splitext(path)[0] + ".mtl"
    with open(mtl_path, "w", encoding="utf-8") as f:
        for m, (r_, g_, b_) in MTL.items():
            f.write(f"newmtl {m}\nKd {r_:.3f} {g_:.3f} {b_:.3f}\nKa 0.2 0.2 0.2\nKs 0.05 0.05 0.05\nd {0.6 if m == 'glass' else 1.0}\n\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Индивидуальный жилой дом 13×16 м — параметрическая модель (стадия ЭП). Единицы: м, Y — вверх.\n")
        f.write(f"mtllib {os.path.basename(mtl_path)}\n")
        for x, y, z in V:
            f.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
        for m, faces in F.items():
            f.write(f"g {m}\nusemtl {m}\n")
            for fc in faces:
                f.write("f " + " ".join(str(i) for i in fc) + "\n")
    return len(V), sum(len(v) for v in F.values())


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "3d")
    os.makedirs(out, exist_ok=True)
    data = build()
    with open(os.path.join(out, "model.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    with open(os.path.join(out, "model.js"), "w", encoding="utf-8") as f:
        f.write("window.HOUSE_MODEL = " + json.dumps(data, ensure_ascii=False) + ";")
    nv, nf = write_obj(data, os.path.join(out, "house.obj"))
    print("items:", len(data["items"]), "obj:", nv, "vertices,", nf, "faces")
