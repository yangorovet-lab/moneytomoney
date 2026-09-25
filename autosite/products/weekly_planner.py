"""Paid: Remote Work Weekly Planner (printable PDF, undated)."""

from __future__ import annotations

from . import pdfkit as k

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
HABITS = ["Moved every hour", "20-20-20 eye breaks", "Stretch routine", "Lunch away from desk",
          "Water", "Stopped work on time", "Outside / daylight"]


def _field(c, x, y, w, name):
    k.label(c, x, y, name, size=9, color=k.MUTED)
    c.setStrokeColor(k.LINE)
    c.line(x + 72, y - 2, x + w, y - 2)


def weekly(c):
    y = k.header(c, "Weekly Plan", "Pick your priorities first, then protect time for them.")
    full = k.PAGE_W - 2 * k.MARGIN
    _field(c, k.MARGIN, y, 220, "Week of")
    y -= 30

    k.box(c, k.MARGIN, y, full, 96, "Top 3 priorities this week")
    for i in range(3):
        k.checkbox(c, k.MARGIN + 12, y - 38 - i * 22)
        k.write_lines(c, k.MARGIN + 30, y - 38 - i * 22, full - 44, 1)
    y -= 112

    k.label(c, k.MARGIN, y, "FOCUS BLOCKS AND MEETINGS", size=9, color=k.ACCENT, bold=True)
    y -= 10
    row_h = 72
    for day in DAYS:
        k.box(c, k.MARGIN, y, full, row_h)
        k.label(c, k.MARGIN + 10, y - 16, day, size=10, color=k.INK, bold=True)
        k.label(c, k.MARGIN + 10, y - 32, "Focus:", size=8.5)
        k.label(c, k.MARGIN + 10, y - 50, "Meetings:", size=8.5)
        k.write_lines(c, k.MARGIN + 110, y - 32, full - 124, 2, gap=18)
        y -= row_h + 6

    k.box(c, k.MARGIN, y, full, y - 50, "Notes and next week")
    k.write_lines(c, k.MARGIN + 12, y - 36, full - 24, int((y - 90) // 18), gap=18)
    k.footer(c)
    c.showPage()


def daily(c):
    y = k.header(c, "Daily Page", "Plan the day in blocks. Breaks count as part of the plan.")
    full = k.PAGE_W - 2 * k.MARGIN
    _field(c, k.MARGIN, y, 220, "Date")
    y -= 28

    left_w = full * 0.58
    right_x = k.MARGIN + left_w + 14
    right_w = full - left_w - 14
    top = y

    k.label(c, k.MARGIN, y, "TIME BLOCKS", size=9, color=k.ACCENT, bold=True)
    y -= 16
    for hour in range(8, 19):
        label = f"{hour if hour <= 12 else hour - 12}:00 {'am' if hour < 12 else 'pm'}"
        k.label(c, k.MARGIN, y, label, size=8.5)
        c.setStrokeColor(k.LINE)
        c.line(k.MARGIN + 52, y - 2, k.MARGIN + left_w, y - 2)
        c.line(k.MARGIN + 52, y - 21, k.MARGIN + left_w, y - 21)
        y -= 42

    ry = top
    k.box(c, right_x, ry, right_w, 120, "Must do today")
    for i in range(4):
        k.checkbox(c, right_x + 12, ry - 40 - i * 20)
        k.write_lines(c, right_x + 28, ry - 40 - i * 20, right_w - 40, 1)
    ry -= 134

    k.box(c, right_x, ry, right_w, 112, "Break tracker")
    k.label(c, right_x + 12, ry - 34, "Tick each time you stand up or stretch:", size=8.5)
    for i in range(12):
        k.checkbox(c, right_x + 12 + (i % 6) * 24, ry - 56 - (i // 6) * 22, size=13)
    ry -= 126

    k.box(c, right_x, ry, right_w, 150, "End-of-day shutdown")
    items = ["Inbox and messages checked", "Tomorrow's first task written down", "Desk cleared",
             "Laptop closed, notifications off"]
    iy = ry - 38
    for item in items:
        k.checkbox(c, right_x + 12, iy)
        iy = k.paragraph(c, right_x + 30, iy, item, right_w - 42, size=9, leading=11.5) - 8
    ry -= 164

    k.box(c, right_x, ry, right_w, 84, "Energy today (circle)")
    for i in range(5):
        cx = right_x + 26 + i * ((right_w - 40) / 4)
        c.setStrokeColor(k.INK)
        c.circle(cx, ry - 48, 10, stroke=1, fill=0)
        k.label(c, cx - 3, ry - 51, str(i + 1), size=9, color=k.INK)
    k.footer(c)
    c.showPage()


def monthly(c):
    y = k.header(c, "Monthly Review", "Fifteen minutes at the end of each month.")
    full = k.PAGE_W - 2 * k.MARGIN
    _field(c, k.MARGIN, y, 220, "Month")
    y -= 26
    for title, lines in [("What went well", 4), ("What got in the way", 4),
                         ("Workspace: anything uncomfortable or annoying?", 3),
                         ("One change for next month", 2), ("Goals for next month", 4)]:
        h = 36 + lines * 20
        k.box(c, k.MARGIN, y, full, h, title)
        k.write_lines(c, k.MARGIN + 12, y - 40, full - 24, lines)
        y -= h + 12
    k.footer(c)
    c.showPage()


def habits(c):
    y = k.header(c, "Habit Tracker", "One row per habit. Fill a square each day you do it.")
    k.label(c, k.MARGIN, y, "Month: ____________________", size=10, color=k.INK)
    y -= 30
    name_w = 150
    cell = (k.PAGE_W - 2 * k.MARGIN - name_w) / 31
    for d in range(31):
        c.setFont("Helvetica", 6.5)
        c.setFillColor(k.MUTED)
        c.drawCentredString(k.MARGIN + name_w + d * cell + cell / 2, y, str(d + 1))
    y -= 8
    rows = HABITS + [""] * 5
    for habit in rows:
        k.label(c, k.MARGIN, y - 13, habit, size=9, color=k.INK)
        if not habit:
            c.setStrokeColor(k.LINE)
            c.line(k.MARGIN, y - 15, k.MARGIN + name_w - 10, y - 15)
        c.setStrokeColor(k.LINE)
        for d in range(31):
            c.rect(k.MARGIN + name_w + d * cell, y - 18, cell, 18, stroke=1, fill=0)
        y -= 24
    y -= 20
    k.box(c, k.MARGIN, y, k.PAGE_W - 2 * k.MARGIN, y - 50, "Notes")
    k.write_lines(c, k.MARGIN + 12, y - 40, k.PAGE_W - 2 * k.MARGIN - 24, int((y - 100) // 20))
    k.footer(c)
    c.showPage()


def build(path) -> None:
    c = k.new_canvas(path, "Remote Work Weekly Planner")
    weekly(c)
    daily(c)
    monthly(c)
    habits(c)
    c.save()
