# -*- coding: utf-8 -*-
"""Минимальная библиотека для генерации чертежей в SVG.
Единицы бумаги — миллиметры (viewBox в мм). Модельные координаты — метры.
"""
import math
from xml.sax.saxutils import escape

FONT = "'DejaVu Sans', 'Liberation Sans', Arial, sans-serif"
SHEETS = {"A1": (841, 594), "A2": (594, 420), "A3": (420, 297), "A4L": (297, 210)}

LW = {"thin": 0.18, "mid": 0.35, "thick": 0.7, "xthick": 1.0}


def fmt(v, nd=0):
    if nd == 0:
        return str(int(round(v)))
    return f"{v:.{nd}f}".replace(".", ",")


def mm(v):
    """метры → мм (для подписей размеров)"""
    return str(int(round(v * 1000)))


class Sheet:
    def __init__(self, size="A2", code="", title="", stage="ЭП", scale_txt="", sheet_no=1, sheets_total=1,
                 project="Индивидуальный жилой дом, 2 этажа, ~400 м²", frame=True):
        self.w, self.h = SHEETS[size]
        self.size = size
        self.code, self.title, self.stage, self.scale_txt = code, title, stage, scale_txt
        self.sheet_no, self.sheets_total, self.project = sheet_no, sheets_total, project
        self.parts = []
        self.defs = []
        self._pattern_ids = set()
        self.frame = frame
        self.margin_l = 20.0
        self.margin = 5.0
        self._add_patterns()

    # ---------------- patterns ----------------
    def _add_patterns(self):
        self.defs.append(
            '<pattern id="hConcrete" patternUnits="userSpaceOnUse" width="3" height="3" patternTransform="rotate(45)">'
            '<line x1="0" y1="0" x2="0" y2="3" stroke="#333" stroke-width="0.18"/>'
            '<circle cx="1.5" cy="1.5" r="0.22" fill="#333"/></pattern>')
        self.defs.append(
            '<pattern id="hMasonry" patternUnits="userSpaceOnUse" width="2.2" height="2.2" patternTransform="rotate(45)">'
            '<line x1="0" y1="0" x2="0" y2="2.2" stroke="#444" stroke-width="0.18"/></pattern>')
        self.defs.append(
            '<pattern id="hAerated" patternUnits="userSpaceOnUse" width="4" height="4" patternTransform="rotate(45)">'
            '<line x1="0" y1="0" x2="0" y2="4" stroke="#555" stroke-width="0.18"/>'
            '<circle cx="2" cy="2" r="0.25" fill="none" stroke="#555" stroke-width="0.15"/></pattern>')
        self.defs.append(
            '<pattern id="hInsul" patternUnits="userSpaceOnUse" width="4" height="4">'
            '<path d="M0 2 Q1 0 2 2 T4 2" fill="none" stroke="#666" stroke-width="0.18"/></pattern>')
        self.defs.append(
            '<pattern id="hWood" patternUnits="userSpaceOnUse" width="3" height="3" patternTransform="rotate(45)">'
            '<line x1="0" y1="0" x2="0" y2="3" stroke="#7a4a1a" stroke-width="0.15"/>'
            '<line x1="1.2" y1="0" x2="1.2" y2="3" stroke="#7a4a1a" stroke-width="0.15"/></pattern>')
        self.defs.append(
            '<pattern id="hEarth" patternUnits="userSpaceOnUse" width="5" height="5">'
            '<line x1="0" y1="2.5" x2="2.5" y2="2.5" stroke="#777" stroke-width="0.18"/>'
            '<line x1="3.5" y1="1" x2="5" y2="1" stroke="#777" stroke-width="0.18"/>'
            '<line x1="2" y1="4.2" x2="4.5" y2="4.2" stroke="#777" stroke-width="0.18"/></pattern>')
        self.defs.append(
            '<pattern id="hSand" patternUnits="userSpaceOnUse" width="3" height="3">'
            '<circle cx="0.7" cy="0.8" r="0.2" fill="#777"/><circle cx="2.1" cy="2.2" r="0.2" fill="#777"/></pattern>')
        self.defs.append(
            '<pattern id="hGravel" patternUnits="userSpaceOnUse" width="5" height="5">'
            '<circle cx="1.2" cy="1.2" r="0.6" fill="none" stroke="#666" stroke-width="0.15"/>'
            '<circle cx="3.6" cy="3.4" r="0.8" fill="none" stroke="#666" stroke-width="0.15"/></pattern>')
        self.defs.append(
            '<pattern id="hGrass" patternUnits="userSpaceOnUse" width="6" height="6">'
            '<path d="M1 5 l1 -2 l1 2 M4 4 l1 -2 l1 2" fill="none" stroke="#5a9a3a" stroke-width="0.2"/></pattern>')
        self.defs.append(
            '<pattern id="hPaving" patternUnits="userSpaceOnUse" width="4" height="4">'
            '<rect x="0" y="0" width="4" height="4" fill="none" stroke="#999" stroke-width="0.15"/></pattern>')
        self.defs.append(
            '<pattern id="hGlass" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(-45)">'
            '<line x1="0" y1="0" x2="0" y2="6" stroke="#5b8fc7" stroke-width="0.25"/></pattern>')
        self.defs.append(
            '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="#000"/></marker>')
        self.defs.append(
            '<marker id="arrowR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="#c00"/></marker>')
        self.defs.append(
            '<marker id="arrowB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="#1a5fb4"/></marker>')

    # ---------------- raw primitives (paper mm) ----------------
    def add(self, s):
        self.parts.append(s)

    def pline(self, x1, y1, x2, y2, w="mid", color="#000", dash=None, cls=None, marker=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = f' marker-end="url(#{marker})"' if marker else ""
        self.add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{LW.get(w, w)}"{d}{m} stroke-linecap="round"/>')

    def prect(self, x, y, w, h, fill="none", stroke="#000", sw="mid", dash=None, rx=0, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{opacity}"' if opacity is not None else ""
        r = f' rx="{rx}"' if rx else ""
        s = f' stroke="{stroke}" stroke-width="{LW.get(sw, sw)}"' if stroke else ' stroke="none"'
        self.add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}"{o}{s}{d}{r}/>')

    def ppoly(self, pts, fill="none", stroke="#000", sw="mid", dash=None, closed=True, opacity=None, linejoin="round"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{opacity}"' if opacity is not None else ""
        p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        s = f' stroke="{stroke}" stroke-width="{LW.get(sw, sw)}"' if stroke else ' stroke="none"'
        tag = "polygon" if closed else "polyline"
        self.add(f'<{tag} points="{p}" fill="{fill}"{o}{s}{d} stroke-linejoin="{linejoin}"/>')

    def ppath(self, d, fill="none", stroke="#000", sw="mid", dash=None, opacity=None):
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{opacity}"' if opacity is not None else ""
        s = f' stroke="{stroke}" stroke-width="{LW.get(sw, sw)}"' if stroke else ' stroke="none"'
        self.add(f'<path d="{d}" fill="{fill}"{o}{s}{dd} stroke-linecap="round" stroke-linejoin="round"/>')

    def pcircle(self, cx, cy, r, fill="none", stroke="#000", sw="mid"):
        s = f' stroke="{stroke}" stroke-width="{LW.get(sw, sw)}"' if stroke else ' stroke="none"'
        self.add(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}"{s}/>')

    def ptext(self, x, y, s, size=2.5, anchor="middle", rot=0, weight="normal", color="#000", italic=False, baseline="middle", family=None):
        t = f' transform="rotate({rot} {x:.2f} {y:.2f})"' if rot else ""
        st = ' font-style="italic"' if italic else ""
        fam = family or FONT
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{fam}" font-size="{size}" text-anchor="{anchor}" '
                 f'dominant-baseline="{baseline}" font-weight="{weight}" fill="{color}"{st}{t}>{escape(str(s))}</text>')

    def ptext_lines(self, x, y, lines, size=2.5, anchor="start", lh=None, weight="normal", color="#000"):
        lh = lh or size * 1.45
        for i, ln in enumerate(lines):
            self.ptext(x, y + i * lh, ln, size=size, anchor=anchor, weight=weight, color=color)

    def table(self, x, y, cols, rows, size=2.4, row_h=None, header=True, weights=None):
        """cols: [(title, width_mm, align)], rows: list of lists"""
        row_h = row_h or size * 2.3
        total_w = sum(c[1] for c in cols)
        yy = y
        if header:
            self.prect(x, yy, total_w, row_h * 1.3, fill="#e9e9e9", sw="mid")
            xx = x
            for title, w, al in cols:
                self.pline(xx, yy, xx, yy + row_h * 1.3, w="mid")
                self.ptext(xx + w / 2, yy + row_h * 0.65, title, size=size, anchor="middle", weight="bold")
                xx += w
            yy += row_h * 1.3
        for r in rows:
            xx = x
            self.prect(x, yy, total_w, row_h, sw="thin")
            for (title, w, al), val in zip(cols, r):
                self.pline(xx, yy, xx, yy + row_h, w="thin")
                if al == "l":
                    self.ptext(xx + 1.2, yy + row_h / 2, val, size=size, anchor="start")
                elif al == "r":
                    self.ptext(xx + w - 1.2, yy + row_h / 2, val, size=size, anchor="end")
                else:
                    self.ptext(xx + w / 2, yy + row_h / 2, val, size=size, anchor="middle")
                xx += w
            yy += row_h
        self.prect(x, y, total_w, yy - y, sw="mid")
        return yy

    # ---------------- frame + title block ----------------
    def _frame(self):
        W, H = self.w, self.h
        out = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>']
        if not self.frame:
            return "\n".join(out)
        out.append(f'<rect x="{self.margin_l}" y="{self.margin}" width="{W - self.margin_l - self.margin}" height="{H - 2 * self.margin}" fill="none" stroke="#000" stroke-width="0.7"/>')
        # штамп (упрощённая форма 3 по ГОСТ 21.101) 185×55
        sw, sh = 185, 40
        x0, y0 = W - self.margin - sw, H - self.margin - sh
        out.append(f'<rect x="{x0}" y="{y0}" width="{sw}" height="{sh}" fill="#fff" stroke="#000" stroke-width="0.7"/>')
        # строки
        rows = [8, 8, 8, 8, 8]
        yy = y0
        for i in range(1, 5):
            yy += rows[i - 1]
            out.append(f'<line x1="{x0}" y1="{yy}" x2="{x0 + sw}" y2="{yy}" stroke="#000" stroke-width="0.35"/>')
        out.append(f'<line x1="{x0 + 65}" y1="{y0}" x2="{x0 + 65}" y2="{y0 + sh}" stroke="#000" stroke-width="0.7"/>')
        out.append(f'<line x1="{x0 + 135}" y1="{y0 + 16}" x2="{x0 + 135}" y2="{y0 + sh}" stroke="#000" stroke-width="0.7"/>')
        out.append(f'<line x1="{x0 + 160}" y1="{y0 + 16}" x2="{x0 + 160}" y2="{y0 + sh}" stroke="#000" stroke-width="0.35"/>')

        def t(x, y, s, size=2.5, anchor="start", weight="normal"):
            return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" text-anchor="{anchor}" '
                    f'dominant-baseline="middle" font-weight="{weight}">{escape(s)}</text>')
        out.append(t(x0 + 2, y0 + 4, "Разраб.", 2.2))
        out.append(t(x0 + 22, y0 + 4, "Claude (ИИ)", 2.2))
        out.append(t(x0 + 2, y0 + 12, "Пров.", 2.2))
        out.append(t(x0 + 22, y0 + 12, "— (требуется ГИП/ГАП)", 2.0))
        out.append(t(x0 + 2, y0 + 20, "Стадия", 2.2))
        out.append(t(x0 + 2, y0 + 28, "Шифр", 2.2))
        out.append(t(x0 + 22, y0 + 28, self.code, 2.4, weight="bold"))
        out.append(t(x0 + 2, y0 + 36, "Дата", 2.2))
        out.append(t(x0 + 22, y0 + 36, "09.2026", 2.2))
        out.append(t(x0 + 100, y0 + 5, self.project, 2.6, anchor="middle", weight="bold"))
        out.append(t(x0 + 100, y0 + 12, "Участок 6 соток (20×30 м), 2 этажа + холодный чердак", 2.2, anchor="middle"))
        out.append(t(x0 + 100, y0 + 23, self.title, 3.0, anchor="middle", weight="bold"))
        out.append(t(x0 + 100, y0 + 30, f"Масштаб {self.scale_txt}" if self.scale_txt else "", 2.3, anchor="middle"))
        out.append(t(x0 + 100, y0 + 36, "Стадия: " + self.stage, 2.2, anchor="middle"))
        out.append(t(x0 + 147, y0 + 20, "Лист", 2.2, anchor="middle"))
        out.append(t(x0 + 147, y0 + 30, str(self.sheet_no), 3.0, anchor="middle", weight="bold"))
        out.append(t(x0 + 172, y0 + 20, "Листов", 2.2, anchor="middle"))
        out.append(t(x0 + 172, y0 + 30, str(self.sheets_total), 3.0, anchor="middle", weight="bold"))
        out.append(t(x0 + 147, y0 + 38, "Эскизный проект — не для строительства", 1.7, anchor="middle"))
        return "\n".join(out)

    def render(self, px_per_mm=3):
        body = "\n".join(self.parts)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{self.w * px_per_mm}" height="{self.h * px_per_mm}" viewBox="0 0 {self.w} {self.h}">\n'
                f'<defs>{"".join(self.defs)}</defs>\n{self._frame()}\n{body}\n</svg>')

    def save(self, path, px_per_mm=3):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.render(px_per_mm))

    def view(self, ox, oy, scale, flip_y=False):
        return View(self, ox, oy, scale, flip_y)


class View:
    """Отображение модельных координат (м) на бумагу (мм).
    flip_y=False: y модели вниз (планы, север сверху). flip_y=True: y модели вверх (фасады/разрезы: z)."""

    def __init__(self, sheet, ox, oy, scale, flip_y=False):
        self.s = sheet
        self.ox, self.oy = ox, oy
        self.k = 1000.0 / scale   # мм на метр
        self.flip = flip_y

    def X(self, x):
        return self.ox + x * self.k

    def Y(self, y):
        return self.oy - y * self.k if self.flip else self.oy + y * self.k

    def P(self, x, y):
        return (self.X(x), self.Y(y))

    # primitives in model coords
    def line(self, x1, y1, x2, y2, **kw):
        self.s.pline(self.X(x1), self.Y(y1), self.X(x2), self.Y(y2), **kw)

    def rect(self, x1, y1, x2, y2, **kw):
        X1, Y1, X2, Y2 = self.X(min(x1, x2)), self.Y(y1), self.X(max(x1, x2)), self.Y(y2)
        y_top, h = min(Y1, Y2), abs(Y2 - Y1)
        self.s.prect(X1, y_top, X2 - X1, h, **kw)

    def poly(self, pts, **kw):
        self.s.ppoly([self.P(x, y) for x, y in pts], **kw)

    def circle(self, x, y, r_mm, **kw):
        self.s.pcircle(self.X(x), self.Y(y), r_mm, **kw)

    def text(self, x, y, s, **kw):
        self.s.ptext(self.X(x), self.Y(y), s, **kw)

    def text_mm(self, x, y, dx, dy, s, **kw):
        self.s.ptext(self.X(x) + dx, self.Y(y) + dy, s, **kw)

    # ---------- размерные линии (ГОСТ 2.307: засечки 45°) ----------
    def _tick(self, X, Y, size=1.2):
        self.s.pline(X - size * 0.7, Y + size * 0.7, X + size * 0.7, Y - size * 0.7, w="mid")

    def dim_h(self, xs, y, off_mm, text_size=2.5, values=None, ext_from=None, flip_text=False):
        """Горизонтальная размерная цепочка: xs — точки по x (м); линия на y (м) со смещением off_mm (мм, + вниз на плане)."""
        Yl = self.Y(y) + off_mm
        y_from = self.Y(ext_from) if ext_from is not None else self.Y(y)
        for x in xs:
            X = self.X(x)
            a, b = (y_from, Yl + (2 if off_mm >= 0 else -2))
            self.s.pline(X, a, X, b, w="thin")
        self.s.pline(self.X(xs[0]), Yl, self.X(xs[-1]), Yl, w="thin")
        for i, x in enumerate(xs):
            self._tick(self.X(x), Yl)
            if i < len(xs) - 1:
                xm = (self.X(x) + self.X(xs[i + 1])) / 2
                val = values[i] if values else mm(abs(xs[i + 1] - x))
                self.s.ptext(xm, Yl - 1.2 if not flip_text else Yl + 2.6, val, size=text_size, anchor="middle", baseline="auto" if not flip_text else "middle")

    def dim_v(self, ys, x, off_mm, text_size=2.5, values=None, ext_from=None):
        """Вертикальная размерная цепочка: ys — точки по y (м); линия на x (м) со смещением off_mm (мм, + вправо)."""
        Xl = self.X(x) + off_mm
        x_from = self.X(ext_from) if ext_from is not None else self.X(x)
        for y in ys:
            Y = self.Y(y)
            self.s.pline(x_from, Y, Xl + (2 if off_mm >= 0 else -2), Y, w="thin")
        self.s.pline(Xl, self.Y(ys[0]), Xl, self.Y(ys[-1]), w="thin")
        for i, y in enumerate(ys):
            self._tick(Xl, self.Y(y))
            if i < len(ys) - 1:
                ym = (self.Y(y) + self.Y(ys[i + 1])) / 2
                val = values[i] if values else mm(abs(ys[i + 1] - y))
                self.s.ptext(Xl - 1.2, ym, val, size=text_size, anchor="middle", rot=-90, baseline="auto")

    # ---------- оси ----------
    def axis_bubble(self, x, y, label, r=4.0, dx=0, dy=0):
        X, Y = self.X(x) + dx, self.Y(y) + dy
        self.s.pcircle(X, Y, r, fill="#fff", stroke="#000", sw="mid")
        self.s.ptext(X, Y, label, size=r * 0.9, anchor="middle", weight="bold")

    def axis_line(self, x1, y1, x2, y2):
        self.s.pline(self.X(x1), self.Y(y1), self.X(x2), self.Y(y2), w="thin", dash="8 2 1 2", color="#000")

    # ---------- отметка уровня (фасады/разрезы) ----------
    def level_mark(self, x, z, text=None, side="right", size=2.5, len_mm=10):
        X, Y = self.X(x), self.Y(z)
        h = 2.0
        self.s.ppoly([(X, Y), (X - h * 0.7, Y - h), (X + h * 0.7, Y - h)], fill="#000", stroke="#000", sw="thin")
        dirn = 1 if side == "right" else -1
        self.s.pline(X, Y - h, X + dirn * len_mm, Y - h, w="thin")
        txt = text if text is not None else (("+" if z > 0 else ("" if z < 0 else "±")) + f"{z:.3f}".replace(".", ","))
        self.s.ptext(X + dirn * len_mm / 2, Y - h - 1.0, txt, size=size, anchor="middle", baseline="auto")

    def leader(self, x, y, dx_mm, dy_mm, text, size=2.3, anchor="start"):
        X, Y = self.X(x), self.Y(y)
        self.s.pline(X, Y, X + dx_mm, Y + dy_mm, w="thin")
        L = 3 if anchor == "start" else -3
        self.s.pline(X + dx_mm, Y + dy_mm, X + dx_mm + L * (1 if anchor == "start" else 1), Y + dy_mm, w="thin")
        self.s.pcircle(X, Y, 0.5, fill="#000", stroke=None)
        self.s.ptext(X + dx_mm + (1 if anchor == "start" else -1), Y + dy_mm - 1.0, text, size=size, anchor=anchor, baseline="auto")

    def north_arrow(self, x, y, r_mm=8):
        X, Y = self.X(x), self.Y(y)
        self.s.pcircle(X, Y, r_mm, fill="#fff", stroke="#000", sw="thin")
        self.s.ppoly([(X, Y - r_mm + 1), (X - r_mm * 0.35, Y + r_mm * 0.5), (X, Y + r_mm * 0.2), (X + r_mm * 0.35, Y + r_mm * 0.5)], fill="#000", stroke="#000", sw="thin")
        self.s.ptext(X, Y - r_mm - 2.5, "С", size=3.5, anchor="middle", weight="bold")


def door_symbol(view, rect, swing, hinge, w, orientation):
    """Дверь на плане: полотно + дуга. rect — проём в стене; orientation 'h' (стена горизонтальная) или 'v'."""
    x1, y1, x2, y2 = rect
    if orientation == "h":
        # проём вдоль x; дверь открывается на N (y-) или S (y+)
        hx = x1 if hinge == "W" else x2
        dirx = 1 if hinge == "W" else -1
        diry = -1 if swing == "N" else 1
        # полотно перпендикулярно стене от петли
        yb = y1 if swing == "N" else y2
        view.line(hx, yb, hx, yb + diry * w, w="mid")
        # дуга
        X0, Y0 = view.P(hx, yb)
        Xe, Ye = view.P(hx + dirx * w, yb)
        Xt, Yt = view.P(hx, yb + diry * w)
        r = abs(view.X(hx + w) - view.X(hx))
        sweep = 0 if (dirx * diry) > 0 else 1
        view.s.ppath(f"M{Xt:.2f} {Yt:.2f} A{r:.2f} {r:.2f} 0 0 {sweep} {Xe:.2f} {Ye:.2f}", sw="thin")
    else:
        hy = y1 if hinge == "N" else y2
        diry = 1 if hinge == "N" else -1
        dirx = 1 if swing == "E" else -1
        xb = x2 if swing == "E" else x1
        view.line(xb, hy, xb + dirx * w, hy, w="mid")
        Xe, Ye = view.P(xb, hy + diry * w)
        Xt, Yt = view.P(xb + dirx * w, hy)
        r = abs(view.X(hy + w) - view.X(hy))
        sweep = 0 if (dirx * diry) < 0 else 1
        view.s.ppath(f"M{Xt:.2f} {Yt:.2f} A{r:.2f} {r:.2f} 0 0 {sweep} {Xe:.2f} {Ye:.2f}", sw="thin")
