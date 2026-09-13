# -*- coding: utf-8 -*-
"""Условные обозначения мебели и оборудования на планах (модельные координаты, м)."""

GREY = "#666"


def bed(v, x, y, w, l, head="N"):
    """кровать w×l, изголовье head (N/S/E/W). x,y — левый верхний угол."""
    v.rect(x, y, x + w, y + l, stroke=GREY, sw="thin", fill="#fff")
    if head == "N":
        v.rect(x + 0.1, y + 0.1, x + w / 2 - 0.05, y + 0.5, stroke=GREY, sw="thin")
        v.rect(x + w / 2 + 0.05, y + 0.1, x + w - 0.1, y + 0.5, stroke=GREY, sw="thin")
        v.line(x, y + 0.7, x + w, y + 0.7, color=GREY, w="thin")
    elif head == "S":
        v.rect(x + 0.1, y + l - 0.5, x + w / 2 - 0.05, y + l - 0.1, stroke=GREY, sw="thin")
        v.rect(x + w / 2 + 0.05, y + l - 0.5, x + w - 0.1, y + l - 0.1, stroke=GREY, sw="thin")
        v.line(x, y + l - 0.7, x + w, y + l - 0.7, color=GREY, w="thin")
    elif head == "W":
        v.rect(x + 0.1, y + 0.1, x + 0.5, y + l / 2 - 0.05, stroke=GREY, sw="thin")
        v.rect(x + 0.1, y + l / 2 + 0.05, x + 0.5, y + l - 0.1, stroke=GREY, sw="thin")
        v.line(x + 0.7, y, x + 0.7, y + l, color=GREY, w="thin")
    else:
        v.rect(x + w - 0.5, y + 0.1, x + w - 0.1, y + l / 2 - 0.05, stroke=GREY, sw="thin")
        v.rect(x + w - 0.5, y + l / 2 + 0.05, x + w - 0.1, y + l - 0.1, stroke=GREY, sw="thin")
        v.line(x + w - 0.7, y, x + w - 0.7, y + l, color=GREY, w="thin")


def single_bed(v, x, y, w=0.9, l=2.0, head="N"):
    v.rect(x, y, x + w, y + l, stroke=GREY, sw="thin", fill="#fff")
    if head == "N":
        v.rect(x + 0.1, y + 0.1, x + w - 0.1, y + 0.5, stroke=GREY, sw="thin")
        v.line(x, y + 0.7, x + w, y + 0.7, color=GREY, w="thin")
    elif head == "W":
        v.rect(x + 0.1, y + 0.1, x + 0.5, y + l - 0.1, stroke=GREY, sw="thin")
        v.line(x + 0.7, y, x + 0.7, y + l, color=GREY, w="thin")
    elif head == "E":
        v.rect(x + w - 0.5, y + 0.1, x + w - 0.1, y + l - 0.1, stroke=GREY, sw="thin")
        v.line(x + w - 0.7, y, x + w - 0.7, y + l, color=GREY, w="thin")
    else:
        v.rect(x + 0.1, y + l - 0.5, x + w - 0.1, y + l - 0.1, stroke=GREY, sw="thin")
        v.line(x, y + l - 0.7, x + w, y + l - 0.7, color=GREY, w="thin")


def sofa(v, x, y, w, d, back="N"):
    v.rect(x, y, x + w, y + d, stroke=GREY, sw="thin", fill="#fff")
    if back == "N":
        v.line(x, y + 0.2, x + w, y + 0.2, color=GREY, w="thin")
        v.line(x + 0.2, y + 0.2, x + 0.2, y + d, color=GREY, w="thin")
        v.line(x + w - 0.2, y + 0.2, x + w - 0.2, y + d, color=GREY, w="thin")
    elif back == "E":
        v.line(x + w - 0.2, y, x + w - 0.2, y + d, color=GREY, w="thin")
        v.line(x, y + 0.2, x + w - 0.2, y + 0.2, color=GREY, w="thin")
        v.line(x, y + d - 0.2, x + w - 0.2, y + d - 0.2, color=GREY, w="thin")
    elif back == "W":
        v.line(x + 0.2, y, x + 0.2, y + d, color=GREY, w="thin")
        v.line(x + 0.2, y + 0.2, x + w, y + 0.2, color=GREY, w="thin")
        v.line(x + 0.2, y + d - 0.2, x + w, y + d - 0.2, color=GREY, w="thin")
    else:
        v.line(x, y + d - 0.2, x + w, y + d - 0.2, color=GREY, w="thin")


def table(v, x, y, w, d, chairs=0):
    v.rect(x, y, x + w, y + d, stroke=GREY, sw="thin", fill="#fff")
    if chairs:
        n = chairs // 2
        for i in range(n):
            cx = x + (i + 0.5) * w / n
            v.rect(cx - 0.22, y - 0.5, cx + 0.22, y - 0.08, stroke=GREY, sw="thin")
            v.rect(cx - 0.22, y + d + 0.08, cx + 0.22, y + d + 0.5, stroke=GREY, sw="thin")


def round_table(v, x, y, r_m):
    v.circle(x, y, r_m * v.k, stroke=GREY, sw="thin", fill="#fff")


def counter(v, x1, y1, x2, y2, sink=None, hob=None):
    v.rect(x1, y1, x2, y2, stroke=GREY, sw="thin", fill="#f4f4f4")
    if sink:
        sx, sy = sink
        v.rect(sx - 0.35, sy - 0.2, sx + 0.35, sy + 0.2, stroke=GREY, sw="thin", fill="#fff", rx=1)
        v.circle(sx, sy, 0.06 * v.k, stroke=GREY, sw="thin")
    if hob:
        hx, hy = hob
        for dx in (-0.15, 0.15):
            for dy in (-0.15, 0.15):
                v.circle(hx + dx, hy + dy, 0.09 * v.k, stroke=GREY, sw="thin")


def wc(v, x, y, orient="N"):
    """унитаз; x,y — центр бачка у стены; orient — направление от стены."""
    if orient in ("N", "S"):
        d = 1 if orient == "S" else -1
        v.rect(x - 0.2, y, x + 0.2, y + d * 0.18, stroke=GREY, sw="thin", fill="#fff")
        cx, cy = x, y + d * 0.45
        v.s.add(f'<ellipse cx="{v.X(cx):.2f}" cy="{v.Y(cy):.2f}" rx="{0.18 * v.k:.2f}" ry="{0.27 * v.k:.2f}" fill="#fff" stroke="{GREY}" stroke-width="0.18"/>')
    else:
        d = 1 if orient == "E" else -1
        v.rect(x, y - 0.2, x + d * 0.18, y + 0.2, stroke=GREY, sw="thin", fill="#fff")
        cx, cy = x + d * 0.45, y
        v.s.add(f'<ellipse cx="{v.X(cx):.2f}" cy="{v.Y(cy):.2f}" rx="{0.27 * v.k:.2f}" ry="{0.18 * v.k:.2f}" fill="#fff" stroke="{GREY}" stroke-width="0.18"/>')


def basin(v, x, y, w=0.5, d=0.4, orient="N"):
    if orient in ("N", "S"):
        y2 = y + d if orient == "S" else y - d
        v.rect(x - w / 2, min(y, y2), x + w / 2, max(y, y2), stroke=GREY, sw="thin", fill="#fff", rx=0.8)
        v.circle(x, (y + y2) / 2, 0.04 * v.k, stroke=GREY, sw="thin")
    else:
        x2 = x + d if orient == "E" else x - d
        v.rect(min(x, x2), y - w / 2, max(x, x2), y + w / 2, stroke=GREY, sw="thin", fill="#fff", rx=0.8)
        v.circle((x + x2) / 2, y, 0.04 * v.k, stroke=GREY, sw="thin")


def bath(v, x, y, l=1.7, w=0.75, horizontal=True):
    if horizontal:
        v.rect(x, y, x + l, y + w, stroke=GREY, sw="thin", fill="#fff", rx=1.5)
        v.rect(x + 0.1, y + 0.1, x + l - 0.1, y + w - 0.1, stroke=GREY, sw="thin", rx=2)
    else:
        v.rect(x, y, x + w, y + l, stroke=GREY, sw="thin", fill="#fff", rx=1.5)
        v.rect(x + 0.1, y + 0.1, x + w - 0.1, y + l - 0.1, stroke=GREY, sw="thin", rx=2)


def shower(v, x, y, s=0.9):
    v.rect(x, y, x + s, y + s, stroke=GREY, sw="thin", fill="#fff")
    v.line(x, y, x + s, y + s, color=GREY, w="thin")
    v.line(x + s, y, x, y + s, color=GREY, w="thin")
    v.circle(x + s / 2, y + s / 2, 0.05 * v.k, stroke=GREY, sw="thin")


def washer(v, x, y, s=0.6):
    v.rect(x, y, x + s, y + s, stroke=GREY, sw="thin", fill="#fff")
    v.circle(x + s / 2, y + s / 2, 0.2 * v.k, stroke=GREY, sw="thin")


def wardrobe(v, x1, y1, x2, y2):
    v.rect(x1, y1, x2, y2, stroke=GREY, sw="thin", fill="#fff")
    v.line(x1, y1, x2, y2, color=GREY, w="thin", dash="1 1")
    v.line(x2, y1, x1, y2, color=GREY, w="thin", dash="1 1")


def car(v, x, y, l=4.6, w=1.85, vertical=True):
    if vertical:
        v.rect(x, y, x + w, y + l, stroke=GREY, sw="thin", fill="#fff", rx=2.5)
        v.rect(x + 0.15, y + 1.1, x + w - 0.15, y + l - 1.3, stroke=GREY, sw="thin", rx=2)
        v.line(x + 0.15, y + 1.6, x + w - 0.15, y + 1.6, color=GREY, w="thin")
    else:
        v.rect(x, y, x + l, y + w, stroke=GREY, sw="thin", fill="#fff", rx=2.5)
        v.rect(x + 1.1, y + 0.15, x + l - 1.3, y + w - 0.15, stroke=GREY, sw="thin", rx=2)


def boiler(v, x, y):
    v.rect(x, y, x + 0.5, y + 0.4, stroke=GREY, sw="thin", fill="#fff")
    v.text(x + 0.25, y + 0.2, "К", size=2.2, color=GREY)


def cylinder(v, x, y, r=0.3):
    v.circle(x, y, r * v.k, stroke=GREY, sw="thin", fill="#fff")
    v.text(x, y, "БКН", size=1.8, color=GREY)


def desk(v, x, y, w=1.4, d=0.7, chair="S"):
    v.rect(x, y, x + w, y + d, stroke=GREY, sw="thin", fill="#fff")
    cx = x + w / 2
    if chair == "S":
        v.circle(cx, y + d + 0.35, 0.25 * v.k, stroke=GREY, sw="thin")
    elif chair == "N":
        v.circle(cx, y - 0.35, 0.25 * v.k, stroke=GREY, sw="thin")
    elif chair == "E":
        v.circle(x + w + 0.35, y + d / 2, 0.25 * v.k, stroke=GREY, sw="thin")
    else:
        v.circle(x - 0.35, y + d / 2, 0.25 * v.k, stroke=GREY, sw="thin")


def fireplace(v, x, y, w=1.2, d=0.6):
    v.rect(x, y, x + w, y + d, stroke=GREY, sw="thin", fill="#fff")
    v.rect(x + 0.2, y + 0.1, x + w - 0.2, y + d - 0.1, stroke=GREY, sw="thin")
