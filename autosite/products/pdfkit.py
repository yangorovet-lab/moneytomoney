"""Small drawing helpers shared by the printable PDF templates."""

from __future__ import annotations

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

PAGE_W, PAGE_H = letter
MARGIN = 48
ACCENT = HexColor("#1a6b54")
ACCENT_LIGHT = HexColor("#e8f2ed")
INK = HexColor("#1f2328")
MUTED = HexColor("#5d6470")
LINE = HexColor("#c9ced3")
WHITE = HexColor("#ffffff")

BRAND = "Desk Setup Guide"


def new_canvas(path, title: str) -> Canvas:
    c = Canvas(str(path), pagesize=letter)
    c.setTitle(title)
    c.setAuthor(BRAND)
    return c


def header(c: Canvas, title: str, subtitle: str = "") -> float:
    """Draw the page header band and return the y position below it."""
    band = 84 if subtitle else 64
    c.setFillColor(ACCENT)
    c.rect(0, PAGE_H - band, PAGE_W, band, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(MARGIN, PAGE_H - 40, title)
    if subtitle:
        c.setFont("Helvetica", 11)
        c.drawString(MARGIN, PAGE_H - 62, subtitle)
    return PAGE_H - band - 28


def footer(c: Canvas, note: str = "") -> None:
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    if note:
        c.drawString(MARGIN, 30, note)
    c.drawRightString(PAGE_W - MARGIN, 30, BRAND)


def section(c: Canvas, y: float, text: str) -> float:
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, y, text.upper())
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1)
    c.line(MARGIN, y - 5, PAGE_W - MARGIN, y - 5)
    return y - 24


def checkbox(c: Canvas, x: float, y: float, size: float = 10) -> None:
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.rect(x, y - 1, size, size, stroke=1, fill=0)


def wrap(text: str, font: str, size: float, width: float) -> list[str]:
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if stringWidth(trial, font, size) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def paragraph(c: Canvas, x: float, y: float, text: str, width: float,
              font: str = "Helvetica", size: float = 10, leading: float = 13, color=INK) -> float:
    c.setFont(font, size)
    c.setFillColor(color)
    for line in wrap(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def check_item(c: Canvas, y: float, text: str, width: float = PAGE_W - 2 * MARGIN - 22,
               size: float = 10.5, gap: float = 5) -> float:
    checkbox(c, MARGIN, y, size=size)
    y = paragraph(c, MARGIN + size + 9, y, text, width, size=size, leading=size * 1.3)
    return y - gap


def write_lines(c: Canvas, x: float, y: float, width: float, count: int, gap: float = 20) -> float:
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    for _ in range(count):
        c.line(x, y, x + width, y)
        y -= gap
    return y


def label(c: Canvas, x: float, y: float, text: str, size: float = 9, color=MUTED, bold: bool = False) -> None:
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.setFillColor(color)
    c.drawString(x, y, text)


def box(c: Canvas, x: float, y: float, w: float, h: float, title: str = "", fill=None) -> None:
    """A rounded box whose top-left corner is at (x, y)."""
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    if fill is not None:
        c.setFillColor(fill)
    c.roundRect(x, y - h, w, h, 6, stroke=1, fill=1 if fill is not None else 0)
    if title:
        label(c, x + 10, y - 16, title.upper(), size=9, color=ACCENT, bold=True)
