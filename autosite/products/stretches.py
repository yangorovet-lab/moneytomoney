"""Paid: 5-Minute Desk Stretch Routine (PDF poster and pocket card)."""

from __future__ import annotations

from . import pdfkit as k

SAFETY = ("Move slowly and gently, and never stretch into pain. This is general information, not medical "
          "advice. If you have an injury or ongoing pain, check with a doctor or physiotherapist first.")

STRETCHES = [
    ("Neck side tilt", "Neck", "15-20 s each side",
     "Sit tall. Slowly tilt your right ear toward your right shoulder until you feel a gentle stretch. "
     "Keep both shoulders down. Switch sides."),
    ("Chin tuck", "Neck and posture", "5 s, repeat 8 times",
     "Look straight ahead and gently draw your chin straight back, as if making a double chin. "
     "Hold, then relax."),
    ("Shoulder rolls", "Shoulders", "10 rolls each way",
     "Lift your shoulders toward your ears, roll them back and down in a slow circle. "
     "Then reverse the direction."),
    ("Chest opener", "Chest and upper back", "15-20 s",
     "Clasp your hands behind your back or hold the sides of your chair. Squeeze your shoulder "
     "blades together and lift your chest."),
    ("Wrist flexor stretch", "Wrists and forearms", "15 s each side",
     "Hold one arm straight out, palm up. With the other hand, gently pull the fingers down "
     "and back. Switch arms."),
    ("Seated twist", "Mid and lower back", "15 s each side",
     "Sit tall with feet flat. Turn your upper body to one side, holding the backrest or armrest. "
     "Breathe out as you turn. Switch sides."),
    ("Standing hip flexor stretch", "Hips", "20 s each side",
     "Stand and step one foot back. Tuck your hips under and shift forward until you feel a stretch "
     "at the front of the back hip. Hold the desk for balance."),
    ("Calf raises", "Legs and circulation", "15 slow reps",
     "Stand behind your chair and hold it lightly. Rise onto your toes, pause, and lower slowly."),
]

SCHEDULE = [
    "Every 20 minutes: look about 20 feet (6 m) away for 20 seconds.",
    "Every 30-60 minutes: stand up and do 2 or 3 of these stretches.",
    "Twice a day: do the full routine (about 5 minutes).",
    "Mix it up: pick neck and wrist stretches on heavy typing days.",
]


def build(path) -> None:
    c = k.new_canvas(path, "5-Minute Desk Stretch Routine")

    y = k.header(c, "5-Minute Desk Stretch Routine", "Eight gentle stretches you can do at your desk. Print and pin it up.")
    gap = 14
    card_w = (k.PAGE_W - 2 * k.MARGIN - gap) / 2
    card_h = 128
    for i, (name, area, dose, steps) in enumerate(STRETCHES):
        col, row = i % 2, i // 2
        x = k.MARGIN + col * (card_w + gap)
        top = y - row * (card_h + gap)
        k.box(c, x, top, card_w, card_h, fill=k.ACCENT_LIGHT if i % 3 == 0 else None)
        c.setFillColor(k.ACCENT)
        c.circle(x + 20, top - 22, 11, stroke=0, fill=1)
        c.setFillColor(k.WHITE)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x + 20, top - 26, str(i + 1))
        k.label(c, x + 38, top - 20, name, size=12, color=k.INK, bold=True)
        k.label(c, x + 38, top - 33, f"{area}  |  {dose}", size=8.5)
        k.paragraph(c, x + 12, top - 54, steps, card_w - 24, size=9.5, leading=12.5)

    k.paragraph(c, k.MARGIN, 62, SAFETY, k.PAGE_W - 2 * k.MARGIN, size=8, leading=10, color=k.MUTED)
    k.footer(c)
    c.showPage()

    y = k.header(c, "Break Schedule and Pocket Card")
    y = k.section(c, y, "When to stretch")
    for line in SCHEDULE:
        y = k.check_item(c, y, line)
    y -= 16

    y = k.section(c, y, "Pocket card (cut out)")
    card_w, card_h = 252, 162
    for n in range(4):
        x = k.MARGIN + (n % 2) * (card_w + 12)
        if n == 2:
            y -= card_h + 12
        c.setDash(4, 3)
        c.setStrokeColor(k.MUTED)
        c.rect(x, y - card_h, card_w, card_h, stroke=1, fill=0)
        c.setDash()
        k.label(c, x + 12, y - 18, "5-MINUTE DESK ROUTINE", size=9, color=k.ACCENT, bold=True)
        line_y = y - 34
        for i, (name, _, dose, _) in enumerate(STRETCHES):
            k.label(c, x + 12, line_y, f"{i + 1}. {name}", size=8.5, color=k.INK)
            c.setFont("Helvetica", 8)
            c.setFillColor(k.MUTED)
            c.drawRightString(x + card_w - 12, line_y, dose)
            line_y -= 15

    k.paragraph(c, k.MARGIN, 62, SAFETY, k.PAGE_W - 2 * k.MARGIN, size=8, leading=10, color=k.MUTED)
    k.footer(c)
    c.showPage()
    c.save()
