# -*- coding: utf-8 -*-
"""АР-6 — Разрезы 1-1 и 2-2, М 1:50."""
from model import *
from svg import Sheet, mm

Z2 = LEVELS["floor2"]
ZG = LEVELS["grade"]
RAFT_EXT = 0.3   # выступ плиты за грань стены
RAFTER_V = ROOF["rafter"][1] / ROOF["cos"]   # вертикальная толщина стропила 0,231


def ground_and_raft(v, U, u_out1, u_out2, walls_u, garage=None, terrace=None, porch=None):
    """Грунт, подушка, плита, ростверк, пол 1-го этажа.
    u_out1/u_out2 — наружные грани здания (в координатах разреза, u_out1 < u_out2).
    walls_u — список (u1,u2) несущих стен (под ними — рёбра ростверка).
    """
    r1, r2 = u_out1 - RAFT_EXT, u_out2 + RAFT_EXT
    # грунт снаружи
    v.rect(u_out1 - 2.4, ZG - 0.9, r1, ZG, fill="url(#hEarth)", stroke=None)
    v.rect(r2, ZG - 0.9, u_out2 + 2.4, ZG, fill="url(#hEarth)", stroke=None)
    v.rect(r1, -1.4, r2, LEVELS["cushion_bottom"], fill="url(#hEarth)", stroke=None)
    v.rect(u_out1 - 2.4, -1.4, r1, ZG - 0.9, fill="url(#hEarth)", stroke=None)
    v.rect(r2, -1.4, u_out2 + 2.4, ZG - 0.9, fill="url(#hEarth)", stroke=None)
    v.line(u_out1 - 2.4, ZG, u_out1 - 1.2, ZG, w="thick")
    v.line(u_out2 + 1.2, ZG, u_out2 + 2.4, ZG, w="thick")
    # отмостка (1,0 м, бетон 100 + ПГС 150 + ЭППС 50)
    for a, b in ((u_out1 - 1.2, u_out1), (u_out2, u_out2 + 1.2)):
        v.rect(a, ZG - 0.10, b, ZG, fill="url(#hConcrete)", sw="thin")
        v.rect(a, ZG - 0.25, b, ZG - 0.10, fill="url(#hSand)", sw="thin")
        v.rect(a, ZG - 0.30, b, ZG - 0.25, fill="url(#hInsul)", sw="thin")
    # подушка ПГС 400
    v.rect(r1 - 0.3, LEVELS["cushion_bottom"], r2 + 0.3, LEVELS["xps_bottom"], fill="url(#hGravel)", sw="thin")
    # ЭППС 100 под плитой
    v.rect(r1, LEVELS["xps_bottom"], r2, LEVELS["raft_bottom"], fill="url(#hInsul)", sw="thin")
    # плита 300
    v.rect(r1, LEVELS["raft_bottom"], r2, LEVELS["raft_top"], fill="url(#hConcrete)", sw="mid")
    # рёбра (ростверк) под стенами
    for (a, b) in walls_u:
        v.rect(a, LEVELS["raft_top"], b, 0.0, fill="url(#hConcrete)", sw="mid")
    # утепление торцов плиты и рёбер (ЭППС 50) + отлив по выступу
    for a, side in ((r1, -1), (r2, 1)):
        v.rect(a + side * 0.05 if side < 0 else a, LEVELS["raft_bottom"], a if side < 0 else a + 0.05, LEVELS["raft_top"], fill="url(#hInsul)", sw="thin")
    v.rect(u_out1 - 0.05, LEVELS["raft_top"], u_out1, 0.0, fill="url(#hInsul)", sw="thin")
    v.rect(u_out2, LEVELS["raft_top"], u_out2 + 0.05, 0.0, fill="url(#hInsul)", sw="thin")
    # ЭППС 50 по верху выступа плиты (устранение мостика холода) + отлив из оцинкованной стали
    v.rect(r1, LEVELS["raft_top"], u_out1 - 0.05, LEVELS["raft_top"] + 0.05, fill="url(#hInsul)", sw="thin")
    v.rect(u_out2 + 0.05, LEVELS["raft_top"], r2, LEVELS["raft_top"] + 0.05, fill="url(#hInsul)", sw="thin")
    v.line(r1 - 0.05, LEVELS["raft_top"] + 0.05, u_out1 - 0.05, LEVELS["raft_top"] + 0.09, w="mid")
    v.line(u_out2 + 0.05, LEVELS["raft_top"] + 0.09, r2 + 0.05, LEVELS["raft_top"] + 0.05, w="mid")
    # пол 1 этажа между рёбрами
    spans = []
    edges = sorted([u for w in walls_u for u in w])
    inner = [(edges[i], edges[i + 1]) for i in range(1, len(edges) - 1, 2)]
    for (a, b) in inner:
        if garage and a >= garage[0] - 0.01 and b <= garage[1] + 0.01:
            v.rect(a, LEVELS["raft_top"], b, LEVELS["garage_floor"], fill="#bbb", sw="thin")
        else:
            v.rect(a, LEVELS["raft_top"], b, -0.15, fill="url(#hInsul)", sw="thin")
            v.rect(a, -0.15, b, -0.03, fill="url(#hConcrete)", sw="thin")
            v.rect(a, -0.03, b, 0.0, fill="#ddd", sw="thin")
    if terrace:
        a, b = terrace
        v.rect(a, ZG - 0.10, b, ZG, fill="url(#hSand)", sw="thin")
        v.rect(a, -0.30, b, -0.15, fill="url(#hConcrete)", sw="mid")
        v.rect(a, ZG, b, -0.30, fill="url(#hGravel)", sw="thin")
    if porch:
        a, b = porch
        v.rect(a, ZG, b, LEVELS["porch"], fill="url(#hConcrete)", sw="mid")
        for zz in (-0.31, -0.17):
            v.line(a, zz, b, zz, w="thin")


def wall_cut(v, u1, u2, z1, z2, kind="ext"):
    fill = {"ext": "url(#hAerated)", "bear": "url(#hAerated)", "part": "#d9d9d9", "fire": "url(#hMasonry)"}[kind]
    v.rect(u1, z1, u2, z2, fill=fill, sw="mid" if kind in ("ext", "bear") else "thin")


def slab(v, u1, u2, z_bot, xps_left=False, xps_right=False, build_up=True):
    v.rect(u1, z_bot, u2, z_bot + SLAB_T, fill="url(#hConcrete)", sw="mid")
    if xps_left:
        v.rect(u1 - 0.1, z_bot, u1, z_bot + SLAB_T, fill="url(#hInsul)", sw="thin")
    if xps_right:
        v.rect(u2, z_bot, u2 + 0.1, z_bot + SLAB_T, fill="url(#hInsul)", sw="thin")
    if build_up:
        v.rect(u1, z_bot + SLAB_T, u2, z_bot + SLAB_T + 0.1, fill="#e5e5e5", sw="thin")


def opening_cut(v, u1, u2, z1, z2, frame=True, outer_side=None):
    """Проём в разрезанной стене (белый), с рамой окна/двери."""
    v.rect(u1, z1, u2, z2, fill="#fff", sw="thin")
    if frame:
        if outer_side == "left":
            v.rect(u1 + 0.10, z1, u1 + 0.17, z2, fill="#2e3236", stroke=None)
        elif outer_side == "right":
            v.rect(u2 - 0.17, z1, u2 - 0.10, z2, fill="#2e3236", stroke=None)
        else:
            v.rect((u1 + u2) / 2 - 0.03, z1, (u1 + u2) / 2 + 0.03, z2, fill="#2e3236", stroke=None)


def beyond_opening(v, u1, u2, z1, z2, label=None):
    v.rect(u1, z1, u2, z2, fill="none", sw="thin")
    if label:
        v.text((u1 + u2) / 2, (z1 + z2) / 2, label, size=1.9, color="#555")


def levels_left(v, u, items):
    for z, txt in items:
        v.level_mark(u, z, txt, side="left", len_mm=9, size=2.2)


def roof_transverse(v, U):
    """Кровля в поперечном разрезе (стропила, прогоны, стойки, утепление)."""
    xw, xe, rx = ROOF["eave_edge_x_w"], ROOF["eave_edge_x_e"], ROOF["ridge_x"]
    ze, zr = ROOF["eave_edge_z"], ROOF["ridge_z"]
    # утепление чердака
    v.rect(U(EXT_INNER[0]), 6.5, U(EXT_INNER[2]), 6.75, fill="url(#hInsul)", sw="thin")
    # мауэрлат
    v.rect(U(-0.15), 6.5, U(0.0), 6.65, fill="url(#hWood)", sw="thin")
    v.rect(U(12.6), 6.5, U(12.75), 6.65, fill="url(#hWood)", sw="thin")
    # стропила (ближайшие за плоскостью разреза)
    pts_top = [(U(xw), ze), (U(rx), zr), (U(xe), ze)]
    pts_bot = [(U(xe), ze - RAFTER_V), (U(rx), zr - RAFTER_V), (U(xw), ze - RAFTER_V)]
    v.poly(pts_top + pts_bot, fill="url(#hWood)", sw="mid")
    # кровельный пирог сверху (обрешётка+настил+фальц ≈ 100)
    pts_top2 = [(U(xw), ze + 0.1), (U(rx), zr + 0.1), (U(xe), ze + 0.1)]
    v.poly(pts_top2 + [(U(xe), ze), (U(rx), zr), (U(xw), ze)], fill="#4d5156", sw="thin")
    # прогоны, лежни, стойки
    for x in ROOF["purlin_x"]:
        zt = roof_z(x) - RAFTER_V
        pw, ph = ROOF["purlin"]
        v.rect(U(x - pw / 2), zt - ph, U(x + pw / 2), zt, fill="url(#hWood)", sw="mid")
        v.rect(U(x - 0.075), 6.5, U(x + 0.075), 6.65, fill="url(#hWood)", sw="thin")
        v.rect(U(x - 0.05), 6.65, U(x + 0.05), zt - ph, fill="#fff", sw="thin")
        # подкосы к промежуточным прогонам (продольные — за плоскостью)
    # коньковая доска
    v.rect(U(rx - 0.025), zr - RAFTER_V - 0.05, U(rx + 0.025), zr + 0.05, fill="url(#hWood)", sw="thin")
    # ветровая доска / карниз
    for x in (xw, xe):
        v.line(U(x), ze - RAFTER_V - 0.05, U(x), ze + 0.1, w="mid")
    # софит карниза
    v.line(U(xw), ze - RAFTER_V - 0.05, U(-0.2), ze - RAFTER_V - 0.05 + 0.6 * 0 + 0.0, w="thin")
    v.line(U(xe), ze - RAFTER_V - 0.05, U(12.8), ze - RAFTER_V - 0.05, w="thin")


def section_1_1(sh, ox, oy):
    """Разрез 1-1: плоскость y = 5,0, взгляд на юг; u = x."""
    v = sh.view(ox=ox, oy=oy, scale=50, flip_y=True)
    U = lambda x: x
    o = EXT_OUTER
    sh.ptext(v.X(6.3), oy - 245, "Разрез 1-1   М 1:50", size=5, anchor="middle", weight="bold")
    ground_and_raft(v, U, o[0], o[2], [(o[0], EXT_INNER[0]), (6.175, 6.425), (EXT_INNER[2], o[2])],
                    garage=(EXT_INNER[0], 3.9))
    # стены 1 этажа
    wall_cut(v, o[0], EXT_INNER[0], 0, 6.5, "ext")
    wall_cut(v, EXT_INNER[2], o[2], 0, 6.5, "ext")
    wall_cut(v, 6.175, 6.425, 0, 3.0, "bear")
    wall_cut(v, 6.175, 6.425, 3.2, 6.3, "bear")
    wall_cut(v, 3.9, 4.1, 2.1, 3.0, "fire")     # над дверью гараж→хоз.
    wall_cut(v, 10.4, 10.5, 2.1, 3.0, "part")   # над дверью санузла
    v.rect(3.9, 0, 4.1, 2.1, fill="none", sw="thin"); v.text(4.0, 1.0, "Д-2п", size=1.8, rot=-90)
    v.rect(10.4, 0, 10.5, 2.1, fill="none", sw="thin"); v.text(10.45, 1.0, "Д-3", size=1.8, rot=-90)
    # стены 2 этажа
    wall_cut(v, 3.2, 3.3, Z2, 6.3, "part")
    wall_cut(v, 10.4, 10.5, Z2 + 2.1, 6.3, "part")
    v.rect(10.4, Z2, 10.5, Z2 + 2.1, fill="none", sw="thin"); v.text(10.45, Z2 + 1.0, "Д-3", size=1.8, rot=-90)
    # перекрытия
    slab(v, o[0] + 0.1, 6.425, 3.0, xps_left=True)
    slab(v, 8.925, o[2] - 0.1, 3.0, xps_right=True)
    slab(v, o[0] + 0.1, o[2] - 0.1, 6.3, xps_left=True, xps_right=True, build_up=False)
    v.text(2.0, 3.1, "монолитная ж/б плита 200, B25", size=1.9, color="#fff")
    # окна в разрезанной восточной стене (санузлы)
    opening_cut(v, EXT_INNER[2], o[2], 1.5, 2.5, outer_side="right")
    opening_cut(v, EXT_INNER[2], o[2], Z2 + 1.5, Z2 + 2.5, outer_side="right")
    # лестница (сечение по y=5,0)
    st = STAIR
    rh, t = st["riser_h"], st["tread"]
    f1, f2 = st["flight1"], st["flight2"]
    # марш 1 (восточный): за плоскостью — ступени выше
    zc1 = rh * (int((5.0 - f1["y_start"]) / t) + 1)
    v.rect(f1["x1"], zc1 - 0.3, f1["x2"], zc1, fill="url(#hConcrete)", sw="mid")
    k0 = int(zc1 / rh) + 1
    for k in range(k0, 11):
        v.line(f1["x1"], k * rh, f1["x2"], k * rh, w="thin")
    # марш 2 (западный): за плоскостью — ступени ниже (к площадке)
    n2 = int((f2["y_start"] - 5.0) / t) + 1
    zc2 = st["landing_z"] + n2 * rh
    v.rect(f2["x1"], zc2 - 0.3, f2["x2"], zc2, fill="url(#hConcrete)", sw="mid")
    for k in range(0, n2):
        v.line(f2["x1"], st["landing_z"] + k * rh, f2["x2"], st["landing_z"] + k * rh, w="thin")
    # площадка (за плоскостью)
    v.rect(f2["x1"], st["landing_z"] - 0.2, f1["x2"], st["landing_z"], fill="none", sw="thin")
    v.text(7.675, st["landing_z"] - 0.1, "площадка +1,737", size=1.8, color="#555")
    # ограждение проёма 2 этажа (за плоскостью, по южной кромке проёма)
    v.rect(6.425, Z2, 8.925, Z2 + 0.9, fill="none", sw="thin")
    for i in range(1, 12):
        v.line(6.425 + i * 2.5 / 12, Z2, 6.425 + i * 2.5 / 12, Z2 + 0.9, w="thin", color="#777")
    v.line(8.925, Z2, 8.925, Z2 + 1.0, w="mid")
    # проёмы за плоскостью разреза
    beyond_opening(v, 8.925, 10.0, 0.0, 2.5, "ДБ-2 (терраса)")
    beyond_opening(v, 1.0, 1.8, Z2, Z2 + 2.1, "Д-3")
    beyond_opening(v, 4.2, 5.1, Z2, Z2 + 2.1, "Д-2")
    beyond_opening(v, 7.0, 7.9, Z2, Z2 + 2.1, "Д-2")
    beyond_opening(v, 9.5, 10.4, Z2, Z2 + 2.1, "Д-2")
    # решётка фронтона (за плоскостью)
    g = GABLE_LOUVER
    beyond_opening(v, 6.3 - g["w"] / 2, 6.3 + g["w"] / 2, g["z"], g["z"] + g["h"], "жалюзи")
    # кровля
    roof_transverse(v, U)
    # люк на чердак — не в этой плоскости
    # отметки слева
    levels_left(v, o[0] - 1.6, [(LEVELS["cushion_bottom"], "−1,100"), (LEVELS["raft_bottom"], "−0,600"), (LEVELS["raft_top"], "−0,300"),
                               (0.0, "±0,000"), (3.0, "+3,000"), (Z2, "+3,300"), (6.3, "+6,300"), (6.5, "+6,500"),
                               (LEVELS["eaves_rafter_top"], "+6,900"), (ROOF["ridge_z"], "+10,650")])
    v.level_mark(o[0] - 1.6, ZG, "−0,450", side="left", len_mm=9, size=2.2)
    # размеры справа: высоты этажей
    v.dim_v([ZG, 0.0, 3.0, 3.2, Z2, 6.3, 6.5, ROOF["ridge_z"]], o[2] + 1.6, 6, text_size=2.0,
            values=["450", "3000", "200", "100", "3000", "200", "4150"])
    # оси и размеры снизу
    for lbl, x in AXES_X:
        v.line(x, -1.3, x, -1.9, w="thin", dash="4 1.5")
        v.axis_bubble(x, -1.9, lbl, dy=4)
    v.dim_h([0.0, 6.3, 12.6], -1.3, 22, text_size=2.4)
    v.dim_h([ROOF["eave_edge_x_w"], o[0], o[2], ROOF["eave_edge_x_e"]], -1.3, 12, text_size=2.0)
    # выноски состава
    callouts(v, [
        (6.9, 3.1, 30, -20, "1 — перекрытие: ж/б плита 200 мм; ЭППС 100 по краю"),
        (9.0, 6.4, 40, -14, "2 — чердачное перекрытие: плита 200 + минвата 250 по пароизоляции"),
        (9.6, 8.9, 30, -18, "3 — кровля: фальц по настилу, стропила 50×200 ш. 600, прогоны 100×200, стойки 100×150"),
        (4.5, -0.45, 40, 22, "4 — пол 1 эт.: ЭППС 150, стяжка 120 с ТП, покрытие; плита 300 на ЭППС 100 и ПГС 400"),
        (12.6, 5.0, 35, -8, "5 — наружная стена: газобетон D400 400 мм, штукатурка 10 мм снаружи, 15 мм внутри"),
    ])
    return v


def callouts(v, items):
    for x, z, dx, dz, txt in items:
        X, Y = v.P(x, z)
        v.s.pcircle(X, Y, 0.6, fill="#000", stroke=None)
        v.s.pline(X, Y, X + dx, Y + dz, w="thin")
        L = 4 if dx >= 0 else -4
        v.s.pline(X + dx, Y + dz, X + dx + L, Y + dz, w="thin")
        v.s.ptext(X + dx + (1 if dx >= 0 else -1), Y + dz - 1.0, txt, size=2.0, anchor="start" if dx >= 0 else "end", baseline="auto")


def section_2_2(sh, ox, oy):
    """Разрез 2-2: плоскость x = 9,6, взгляд на запад; u = -y (север справа)."""
    v = sh.view(ox=ox, oy=oy, scale=50, flip_y=True)
    U = lambda y: -y
    o = EXT_OUTER
    sh.ptext(v.X(-7.8), oy - 245, "Разрез 2-2   М 1:50", size=5, anchor="middle", weight="bold")
    # наружные грани по u: юг (u=-15.8) слева, север (u=0.2) справа
    ground_and_raft(v, U, U(o[3]), U(o[1]), [(U(o[3]), U(EXT_INNER[3])), (U(EXT_INNER[1]), U(o[1]))],
                    terrace=(U(TERRACE["rect"][3]), U(o[3])), porch=(U(o[1]), U(PORCH["rect"][1])))
    # фронтоны (разрезаны при x=9,6): высота кровли в этой плоскости
    zroof = roof_z(9.6)
    zg_top = zroof - RAFTER_V
    wall_cut(v, U(EXT_INNER[1]), U(o[1]), 0, 6.5, "ext")
    wall_cut(v, U(EXT_INNER[1]), U(o[1]), 6.5, zg_top, "ext")
    wall_cut(v, U(o[3]), U(EXT_INNER[3]), 0, 6.5, "ext")
    wall_cut(v, U(o[3]), U(EXT_INNER[3]), 6.5, zg_top, "ext")
    v.text(U(0.0), 7.2, "фронтон 300", size=1.8, rot=-90)
    # перегородка 2 эт. y 9.4–9.5 (над дверью спальни 4)
    wall_cut(v, U(9.5), U(9.4), Z2 + 2.1, 6.3, "part")
    v.rect(U(9.5), Z2, U(9.4), Z2 + 2.1, fill="none", sw="thin"); v.text(U(9.45), Z2 + 1.0, "Д-2", size=1.8, rot=-90)
    # перекрытия (сплошные при x=9,6)
    slab(v, U(o[3] - 0.1), U(o[1] + 0.1), 3.0, xps_left=True, xps_right=True)
    slab(v, U(o[3] - 0.1), U(o[1] + 0.1), 6.3, xps_left=True, xps_right=True, build_up=False)
    # люк на чердак (в плоскости разреза)
    h = ATTIC_HATCH
    v.rect(U(h[3]), 6.3, U(h[1]), 6.5, fill="#fff", sw="thin")
    v.rect(U(h[3]), 6.3, U(h[1]), 6.3 + 0.05, fill="#fff", sw="mid")
    v.text(U(5.45), 6.9, "люк 700×900", size=1.8)
    # окна/двери в разрезанных стенах
    opening_cut(v, U(EXT_INNER[1]), U(o[1]), 1.0, 2.5, outer_side="right")            # ОК-3 прихожая
    opening_cut(v, U(EXT_INNER[1]), U(o[1]), Z2 + 1.0, Z2 + 2.5, outer_side="right")  # ОК-3 холл
    opening_cut(v, U(o[3]), U(EXT_INNER[3]), 0.0, 2.5, outer_side="left")              # ДБ-2
    # за плоскостью (взгляд на запад): стена по оси 2 с проёмами; лестница
    beyond_opening(v, U(3.9), U(3.0), 0, 2.1, "Д-2")
    beyond_opening(v, U(9.5), U(8.6), 0, 2.1, "Д-2")
    beyond_opening(v, U(14.2), U(11.2), 0, 2.5, "ПР-1 3000×2500 (балка Б-1 250×700 над проёмом)")
    beyond_opening(v, U(3.3), U(2.4), Z2, Z2 + 2.1, "Д-2")
    beyond_opening(v, U(9.4), U(8.2), Z2, Z2 + 2.25, "ПР-2")
    # лестница: профиль марша 1 (ближний) и марша 2 (дальний, выше)
    st = STAIR
    rh, t = st["riser_h"], st["tread"]
    f1, f2 = st["flight1"], st["flight2"]
    pts = [(U(f1["y_start"]), 0.0)]
    for k in range(1, 11):
        y = f1["y_start"] + (k - 1) * t
        pts.append((U(y), k * rh))
        pts.append((U(y + t), k * rh))
    pts[-1] = (U(f1["y_end"]), 10 * rh)
    pts += [(U(st["landing"][3]), 10 * rh), (U(st["landing"][3]), 10 * rh - 0.2), (U(f1["y_end"] + 0.3), 10 * rh - 0.2),
            (U(f1["y_start"] + 0.9), 0.0)]
    v.poly(pts, fill="#eee", sw="mid")
    pts2 = [(U(f2["y_start"]), 10 * rh)]
    for k in range(1, 10):
        y = f2["y_start"] - (k - 1) * t
        pts2.append((U(y), 10 * rh + k * rh))
        pts2.append((U(y - t), 10 * rh + k * rh))
    pts2[-1] = (U(f2["y_end"]), Z2)
    pts2 += [(U(f2["y_end"]), 3.0), (U(f2["y_end"] + 0.4), 3.0), (U(f2["y_start"] - 0.35), 10 * rh - 0.2), (U(f2["y_start"]), 10 * rh - 0.2)]
    v.poly(pts2, fill="#f6f6f6", sw="thin")
    v.text(U(6.0), 2.2, "лестница монолитная ж/б, 19×174×280", size=1.8, color="#555", rot=-33)
    # ограждение проёма (за плоскостью, вдоль x=8,925)
    for yy in [4.33 + i * 0.3 for i in range(13)]:
        v.line(U(yy), Z2, U(yy), Z2 + 0.9, w="thin", color="#777")
    v.line(U(4.33), Z2 + 0.9, U(8.0), Z2 + 0.9, w="mid")
    v.line(U(4.33), Z2 + 1.0, U(4.33), Z2, w="mid")
    # козырёк и крыльцо (за плоскостью)
    c = PORCH["canopy"]
    zc = PORCH["canopy_z"]
    v.rect(U(c[3]), zc, U(c[1]), zc + 0.15, fill="none", sw="thin")
    v.line(U(c[1] + 0.3), zc, U(c[1] + 0.3), zc - 0.6, w="thin"); v.line(U(c[1] + 0.3), zc - 0.6, U(o[1]), zc - 0.6, w="thin")
    # кровля в продольном разрезе: пакет на высоте roof_z(9.6), горизонтальный
    yn, ys = ROOF["gable_y_n"], ROOF["gable_y_s"]
    v.rect(U(EXT_INNER[3]), 6.5, U(EXT_INNER[1]), 6.75, fill="url(#hInsul)", sw="thin")
    v.rect(U(ys), zroof - RAFTER_V, U(yn), zroof, fill="url(#hWood)", sw="mid")
    v.rect(U(ys), zroof, U(yn), zroof + 0.1, fill="#4d5156", sw="thin")
    # прогон x=9,6 (в плоскости) и стойки
    pw, ph = ROOF["purlin"]
    v.rect(U(ys + 0.5), zroof - RAFTER_V - ph, U(yn - 0.5), zroof - RAFTER_V, fill="url(#hWood)", sw="mid")
    v.rect(U(EXT_INNER[3]), 6.5, U(EXT_INNER[1]), 6.65, fill="url(#hWood)", sw="thin")
    yp = 0.5
    while yp < 15.6:
        v.rect(U(yp + 0.05), 6.65, U(yp - 0.05), zroof - RAFTER_V - ph, fill="url(#hWood)", sw="thin")
        # подкосы продольные
        v.line(U(yp), 6.65 + 0.4, U(yp + 1.0), zroof - RAFTER_V - ph, w="thin")
        v.line(U(yp), 6.65 + 0.4, U(yp - 1.0), zroof - RAFTER_V - ph, w="thin")
        yp += 3.0
    # конёк (за плоскостью) и стропила за плоскостью — линия низа конька
    v.line(U(ys), ROOF["ridge_z"] - RAFTER_V, U(yn), ROOF["ridge_z"] - RAFTER_V, w="thin", dash="3 1")
    v.line(U(ys), ROOF["ridge_z"], U(yn), ROOF["ridge_z"], w="mid")
    v.text(U(7.8), ROOF["ridge_z"] + 0.35, "конёк +10,650", size=2.0)
    v.line(U(ys), zroof - RAFTER_V - 0.05, U(yn), zroof - RAFTER_V - 0.05, w="thin")
    # отметки
    levels_left(v, U(o[3]) - 1.6, [(LEVELS["cushion_bottom"], "−1,100"), (LEVELS["raft_bottom"], "−0,600"),
                                  (0.0, "±0,000"), (3.0, "+3,000"), (Z2, "+3,300"), (6.3, "+6,300"),
                                  (6.5, "+6,500"), (zroof, f"+{zroof:.3f}".replace(".", ",")), (ROOF["ridge_z"], "+10,650")])
    v.level_mark(U(o[1]) + 1.6, LEVELS["porch"], "−0,030", side="right", len_mm=9, size=2.2)
    v.level_mark(U(o[1]) + 1.6, ZG, "−0,450", side="right", len_mm=9, size=2.2)
    v.level_mark(U(o[3]) - 1.6, TERRACE["level"], "−0,150 (терраса)", side="left", len_mm=9, size=2.2)
    v.level_mark(U(o[1]) + 1.6, PORCH["canopy_z"], "+2,700", side="right", len_mm=9, size=2.2)
    # оси
    for lbl, y in AXES_Y:
        v.line(U(y), -1.3, U(y), -1.9, w="thin", dash="4 1.5")
        v.axis_bubble(U(y), -1.9, lbl, dy=4)
    v.dim_h([U(15.6), U(0.0)], -1.3, 22, text_size=2.4)
    v.dim_h([U(TERRACE["rect"][3]), U(o[3]), U(o[1]), U(PORCH["rect"][1])], -1.3, 12, text_size=2.0)
    callouts(v, [
        (U(12.0), 6.4, -30, -14, "2 — чердачное перекрытие с утеплением 250 мм"),
        (U(1.5), 3.1, 30, -16, "1 — монолитная плита 200 мм"),
        (U(17.5), -0.2, 20, 22, "6 — терраса: плитка по бетонной плите 150 мм на ПГС, деформационный шов у дома"),
    ])
    return v


def sections_sheet(sheet_no, total):
    sh = Sheet("A1", code="АР-6", title="Разрезы 1-1, 2-2", scale_txt="1:50", sheet_no=sheet_no, sheets_total=total)
    section_1_1(sh, ox=75, oy=300)
    section_2_2(sh, ox=770, oy=300)
    notes = [
        "1. Разрез 1-1 — по оси лестницы (y = 5,0 м), взгляд на юг; разрез 2-2 — по холлу и гостиной (x = 9,6 м), взгляд на запад.",
        "2. Фундамент — монолитная ж/б плита 300 мм (B25 W6 F150) с рёбрами-ростверком 400×300 под несущими стенами, по ЭППС 100 мм",
        "   и уплотнённой подушке из ПГС 400 мм; утеплённая отмостка 1,0 м (ЭППС 50). Требуются инженерно-геологические изыскания!",
        "3. Перекрытия монолитные 200 мм B25, арматура A500C (см. КР-2). По периметру — терморазрыв ЭППС 100 мм (торец плиты).",
        "4. Кровля наслонная: стропила 50×200 ш. 600 по прогонам 100×200 на стойках 100×150 (шаг 3,0 м) и лежнях 150×150 по плите.",
        "5. Утепление чердачного перекрытия — минеральная вата 250 мм (2 слоя вразбежку) по пароизоляции; чердак холодный, проветриваемый.",
        "6. Лестница монолитная ж/б, ширина марша 1150, 19 подъёмов 174×280, ограждение h = 900 (для детей — 1100, с заполнением ≤ 100 мм).",
    ]
    sh.ptext(35, 395, "Примечания", size=3.2, anchor="start", weight="bold")
    sh.ptext_lines(35, 402, notes, size=2.3, lh=4.4)
    return sh


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "drawings")
    sections_sheet(7, 20).save(os.path.join(out, "АР-6_Разрезы.svg"))
    print("ok")
