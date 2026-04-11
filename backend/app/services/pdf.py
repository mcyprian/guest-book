"""PDF generation service replicating the official Hlasenie pobytu form."""

from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from app.models import Guest

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"

_fonts_registered = False


def _register_fonts() -> None:
    global _fonts_registered
    if _fonts_registered:
        return
    pdfmetrics.registerFont(TTFont("DejaVuSans", str(FONTS_DIR / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(FONTS_DIR / "DejaVuSans-Bold.ttf")))
    _fonts_registered = True


def generate_pdf(guest: Guest) -> BytesIO:
    """Generate a pre-filled Hlasenie pobytu PDF matching the official form layout.

    Returns a BytesIO buffer containing the PDF.
    """
    _register_fonts()

    buf = BytesIO()
    w, h = A4  # 595.28 x 841.89 points
    c = Canvas(buf, pagesize=A4)

    # Margins
    left = 50
    right = w - 50
    content_width = right - left
    mid = left + content_width * 0.55  # split point for two-column fields

    # --- Title ---
    y = h - 60
    c.setFont("DejaVuSans-Bold", 14)
    c.drawCentredString(w / 2, y, "HL\u00c1SENIE POBYTU")

    # --- Stay dates box ---
    y -= 30
    box_top = y + 5
    box_bottom = y - 25
    c.rect(left, box_bottom, content_width, box_top - box_bottom)
    c.setFont("DejaVuSans-Bold", 10)
    c.drawString(left + 8, y - 12, "Pobyt od:")
    c.setFont("DejaVuSans", 10)
    c.drawString(left + 70, y - 12, str(guest.stay_from))
    c.setFont("DejaVuSans-Bold", 10)
    c.drawString(mid, y - 12, "do:")
    c.setFont("DejaVuSans", 10)
    c.drawString(mid + 25, y - 12, str(guest.stay_to))

    # --- Helper to draw a field row ---
    def draw_line(y_pos: float) -> None:
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(0.5)
        c.line(left, y_pos, right, y_pos)

    def label_value(
        x: float,
        y_pos: float,
        label: str,
        value: str,
        bold_label: bool = True,
    ) -> None:
        if bold_label:
            c.setFont("DejaVuSans-Bold", 9)
        else:
            c.setFont("DejaVuSans", 9)
        c.drawString(x, y_pos, label)
        label_w = c.stringWidth(label, c._fontname, 9)
        c.setFont("DejaVuSans", 10)
        c.drawString(x + label_w + 4, y_pos, value)

    # --- Fields 1 & 2: Meno / Priezvisko ---
    y = box_bottom - 35
    label_value(left, y, "1.", "")
    c.setFont("DejaVuSans", 9)
    c.drawString(left + 14, y, "Meno:")
    c.setFont("DejaVuSans", 10)
    c.drawString(left + 52, y, guest.first_name)

    label_value(mid, y, "2.", "")
    c.setFont("DejaVuSans", 9)
    c.drawString(mid + 14, y, "Priezvisko:")
    c.setFont("DejaVuSans", 10)
    c.drawString(mid + 75, y, guest.last_name)

    # --- Line + Fields 3 & 4 ---
    y -= 30
    draw_line(y + 18)
    label_value(left, y, "3.", "")
    c.setFont("DejaVuSans", 9)
    c.drawString(left + 14, y, "D\u00e1tum a miesto narodenia (\u0161t\u00e1t):")
    c.setFont("DejaVuSans", 10)
    dob_text = f"{guest.date_of_birth}, {guest.birth_place}"
    c.drawString(left + 14, y - 14, dob_text)

    label_value(mid, y, "4.", "")
    c.setFont("DejaVuSans", 9)
    c.drawString(mid + 14, y, "\u0160t\u00e1tna pr\u00edslu\u0161nos\u0165:")
    c.setFont("DejaVuSans", 10)
    c.drawString(mid + 14, y - 14, guest.nationality)

    # --- Line + Field 5 ---
    y -= 48
    draw_line(y + 18)
    label_value(left, y, "5.", "")
    c.setFont("DejaVuSans", 9)
    c.drawString(left + 14, y, "Trval\u00fd pobyt v domovskom \u0161t\u00e1te:")
    c.setFont("DejaVuSans", 10)
    c.drawString(left + 14, y - 14, guest.permanent_address)

    # --- Line + Fields 6 & 7 ---
    y -= 45
    draw_line(y + 15)
    label_value(left, y, "6.", "")
    c.setFont("DejaVuSans", 9)
    c.drawString(left + 14, y, "\u00da\u010del cesty do Slovenskej republiky:")
    c.setFont("DejaVuSans", 10)
    c.drawString(left + 14, y - 14, guest.travel_purpose)

    label_value(mid, y, "7.", "")
    c.setFont("DejaVuSans", 9)
    c.drawString(mid + 14, y, "\u010c\u00edslo pasu:")
    c.setFont("DejaVuSans", 10)
    c.drawString(mid + 14, y - 14, guest.passport_number)

    # --- Line + Field 8 ---
    y -= 48
    draw_line(y + 18)
    label_value(left, y, "8.", "")
    c.setFont("DejaVuSans", 8)
    c.drawString(
        left + 14,
        y,
        "V\u00edzum (druh, \u010d\u00edslo, platnos\u0165 od \u2013 do, miesto vydania) "
        "alebo doklad o pobyte SR/E\u00da (\u010d\u00edslo",
    )
    c.drawString(left + 14, y - 11, "a platnos\u0165 od \u2013 do):")
    c.setFont("DejaVuSans", 10)
    visa = guest.visa_details or ""
    c.drawString(left + 14, y - 26, visa)

    # --- Line + Field 9 ---
    y -= 60
    draw_line(y + 14)
    label_value(left, y, "9.", "")
    c.setFont("DejaVuSans", 9)
    c.drawString(
        left + 14,
        y,
        "Meno a adresa ubytovacieho zariadenia v Slovenskej republike:",
    )
    c.setFont("DejaVuSans", 10)
    accommodation = f"{guest.accommodation_name}, {guest.accommodation_address}"
    c.drawString(left + 14, y - 16, accommodation)

    # --- Line + Field 10: Children ---
    y -= 48
    draw_line(y + 14)
    label_value(left, y, "10.", "")
    c.setFont("DejaVuSans", 9)
    c.drawString(left + 20, y, "Spolucestuj\u00face deti:")

    children_sorted = sorted(guest.children, key=lambda ch: ch.position)
    for i in range(4):
        y -= 18
        c.setFont("DejaVuSans", 9)
        c.drawString(left, y, f"{i + 1}.")
        if i < len(children_sorted):
            c.setFont("DejaVuSans", 10)
            c.drawString(left + 16, y, children_sorted[i].name)
        else:
            # Draw dotted line placeholder
            c.setFont("DejaVuSans", 9)
            c.drawString(left + 16, y, "." * 80)

    # --- Footer: signature line ---
    footer_y = 65
    c.setLineWidth(0.5)
    # Signature dots
    c.setFont("DejaVuSans", 9)
    c.drawString(left, footer_y + 14, "." * 60)
    c.drawCentredString(left + 120, footer_y, "Podpis cudzinca")

    # Form identifier
    c.setFont("DejaVuSans", 8)
    c.drawRightString(right, footer_y, "T MV SR 11-060-1    VII/2018")

    c.save()
    buf.seek(0)
    return buf
