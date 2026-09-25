"""Free lead magnet: Ergonomic Home Office Setup Checklist (PDF)."""

from __future__ import annotations

from . import pdfkit as k

NOTE = "General information, not medical advice. See a doctor or physiotherapist for persistent pain."

PAGE_ONE = {
    "Chair": [
        "Feet rest flat on the floor, or on a footrest or a stack of books.",
        "Hips level with or slightly above your knees.",
        "A gap of two to three fingers between the seat edge and the back of your knees.",
        "Lumbar support sits in the curve of your lower back (a rolled towel works too).",
        "Backrest reclined slightly, about 100 to 110 degrees, and you actually lean on it.",
    ],
    "Desk": [
        "Elbows bent at about 90 degrees with shoulders relaxed while typing.",
        "Forearms roughly parallel to the floor.",
        "Enough legroom to sit close to the desk without twisting.",
        "Things you use every hour are within easy reach.",
    ],
    "Monitor": [
        "Top of the screen at or slightly below eye level.",
        "Screen about an arm's length away. Text is readable without leaning in.",
        "Main screen straight in front of you, not off to one side.",
        "Laptop raised to eye level, with an external keyboard and mouse.",
    ],
}

PAGE_TWO = {
    "Keyboard and mouse": [
        "Wrists straight while typing, not bent up, down or sideways.",
        "Mouse right next to the keyboard, at the same height.",
        "Keyboard flat or tilted slightly away from you.",
    ],
    "Lighting": [
        "Window beside the screen, not directly behind it or behind you.",
        "No glare or reflections on the screen.",
        "Desk lamp lights your desk and papers, not the screen.",
        "Screen brightness roughly matches the room.",
    ],
    "Daily habits": [
        "Stand up, move or stretch every 30 to 60 minutes.",
        "Every 20 minutes, look at something about 20 feet (6 m) away for 20 seconds.",
        "Change position during the day: sit back, sit upright, stand if you can.",
    ],
}

FREE_FIXES = [
    "Rolled towel behind your lower back for lumbar support.",
    "Books or a sturdy box under your feet as a footrest.",
    "A stack of books under your laptop, plus a spare keyboard and mouse.",
    "Turn your desk so the window is beside the screen instead of behind it.",
]

MEASUREMENTS = [
    "Chair seat height (floor to seat)",
    "Desk or keyboard height (floor to surface)",
    "Top of monitor (floor to top edge)",
    "Monitor distance (eyes to screen)",
    "Standing desk height (if you have one)",
]


def build(path) -> None:
    c = k.new_canvas(path, "Ergonomic Home Office Setup Checklist")

    y = k.header(c, "Ergonomic Home Office Setup Checklist",
                 "Work through each section, adjust as you go, and tick what's done.")
    for title, items in PAGE_ONE.items():
        y = k.section(c, y, title)
        for item in items:
            y = k.check_item(c, y, item, size=12, gap=12)
        y -= 14

    k.box(c, k.MARGIN, y, k.PAGE_W - 2 * k.MARGIN, y - 56, "Free fixes to try before buying anything", fill=k.ACCENT_LIGHT)
    fy = y - 40
    for fix in FREE_FIXES:
        k.label(c, k.MARGIN + 14, fy, "-", size=11, color=k.ACCENT, bold=True)
        fy = k.paragraph(c, k.MARGIN + 26, fy, fix, k.PAGE_W - 2 * k.MARGIN - 40, size=11, leading=14) - 8
    k.footer(c, NOTE)
    c.showPage()

    y = k.header(c, "Setup Checklist, continued")
    for title, items in PAGE_TWO.items():
        y = k.section(c, y, title)
        for item in items:
            y = k.check_item(c, y, item, size=12, gap=12)
        y -= 14

    y = k.section(c, y, "My measurements")
    col = k.PAGE_W - k.MARGIN - 150
    for name in MEASUREMENTS:
        k.label(c, k.MARGIN, y, name, size=10.5, color=k.INK)
        c.setStrokeColor(k.LINE)
        c.line(col, y - 2, k.PAGE_W - k.MARGIN, y - 2)
        y -= 24
    k.label(c, k.MARGIN, y - 4, "Date checked: ____________      Re-check whenever you change your chair, desk or screen.",
            size=9.5)
    k.footer(c, NOTE)
    c.showPage()
    c.save()
