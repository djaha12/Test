# -*- coding: utf-8 -*-
"""Единый векторный PDF-альбом из SVG-листов: титул + все листы в своих форматах (A1/A2/A3), закладки по листам.
Требует: pip install cairosvg pypdf. Запуск: python3 make_pdf.py → ../pdf/Проект_дома_13x16_ЭП.pdf
"""
import os, io, json, sys
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
SIZES = {"A1": (841, 594), "A2": (594, 420), "A3": (420, 297)}
PT = 96 / 25.4   # cairosvg принимает размеры в CSS-px (96 dpi): 1 мм = 3,78 px → в PDF 1 мм = 2,835 pt


def cover_svg(reg):
    W, H = 420, 297
    n = len(reg["sheets"])
    half = (n + 1) // 2
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
           f'<rect width="{W}" height="{H}" fill="#fff"/>',
           '<rect x="10" y="10" width="400" height="277" fill="none" stroke="#000" stroke-width="0.5"/>']
    t = lambda x, y, s, size=4, w="normal", c="#000", a="start": out.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans, Arial, sans-serif" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{a}">{escape(s)}</text>')
    t(30, 40, "Индивидуальный жилой дом 13×16 м, 2 этажа, ≈ 400 м²", 11, "bold")
    t(30, 52, "на участке 6 соток (20×30 м)", 11, "bold")
    t(30, 64, f"Эскизный проект (стадия ЭП). Альбом чертежей — {n} листов: ОД, ГП, ВП, СГП, АР, КЛ, ПП, ПБ, КР, ОВ, ВК, ЭО, ГР, ФГ", 5, c="#333")
    t(30, 76, f"Общая площадь помещений {reg['summary']['area_total']} м², площадь по наружному обмеру {reg['summary']['gross']} м², пятно застройки 13,0 × 16,0 м.", 3.6)
    t(30, 82, "Конструкции: монолитная плита с рёбрами, газобетон D400 400 мм, монолитные перекрытия 200 мм, наслонные стропила, фальцевая кровля.", 3.6)
    t(30, 88, "Инженерия: газовый конденсационный котёл 32 кВт, тёплые полы, естественная вентиляция (опция ПВУ), скважина, СБО, 15 кВт.", 3.6)
    t(30, 100, "Состав альбома", 4.5, "bold")
    for i, s in enumerate(reg["sheets"]):
        x = 30 if i < half else 220
        y = 108 + (i if i < half else i - half) * 5.2
        t(x, y, f"{i + 1}.", 3.0, c="#555")
        t(x + 8, y, s["code"], 3.0, "bold")
        title = s["title"] if len(s["title"]) <= 72 else s["title"][:70] + "…"
        t(x + 24, y, f"{title} ({s['scale']})", 2.9)
    out.append('<line x1="30" y1="258" x2="390" y2="258" stroke="#333" stroke-width="0.4"/>')
    t(30, 265, f"Разработал: Claude (ИИ-ассистент) · {reg['date']} · Эскизный проект — не для строительства: требуются инженерно-геологические изыскания, ТУ и рабочая документация.", 2.8, c="#555")
    t(30, 271, "Расчётные записки — docs/, численные результаты — calc/, 3D-модель — 3d/ (three.js, OBJ), планы и фасады для CAD — dxf/. Проект параметрический (src/model.py).", 2.8, c="#555")
    out.append("</svg>")
    return "\n".join(out)


def main():
    try:
        import cairosvg
        from pypdf import PdfWriter, PdfReader
    except ImportError as e:
        print(f"PDF пропущен: нет модуля {e.name} (pip install cairosvg pypdf)")
        return 0
    with open(os.path.join(BASE, "drawings", "register.json"), encoding="utf-8") as f:
        reg = json.load(f)
    out_dir = os.path.join(BASE, "pdf")
    os.makedirs(out_dir, exist_ok=True)
    w = PdfWriter()
    cov = cairosvg.svg2pdf(bytestring=cover_svg(reg).encode("utf-8"), output_width=420 * PT, output_height=297 * PT)
    w.append(PdfReader(io.BytesIO(cov)))
    w.add_outline_item("Титульный лист", 0)
    for i, s in enumerate(reg["sheets"]):
        W, H = SIZES.get(s.get("format", "A2"), SIZES["A2"])
        pdf = cairosvg.svg2pdf(url=os.path.join(BASE, "drawings", s["file"]), output_width=W * PT, output_height=H * PT)
        w.append(PdfReader(io.BytesIO(pdf)))
        w.add_outline_item(f"{s['code']} — {s['title']}", i + 1)
        print(f"  {s['code']} {s.get('format')}", flush=True)
    w.add_metadata({"/Title": "Индивидуальный жилой дом 13×16 м, 2 этажа — эскизный проект (альбом чертежей)", "/Author": "Claude (ИИ-ассистент)", "/Subject": "Стадия ЭП, 32 листа"})
    out = os.path.join(out_dir, "Проект_дома_13x16_ЭП.pdf")
    with open(out, "wb") as f:
        w.write(f)
    print(f"pdf ok {out} {os.path.getsize(out) / 1e6:.1f} MB, страниц {len(w.pages)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
