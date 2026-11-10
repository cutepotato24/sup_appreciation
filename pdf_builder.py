"""Build a colourful PDF keepsake of the team messages."""

from io import BytesIO
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Light card backgrounds and matching accent colours for the author line.
CARD_COLORS = [
    ("#FFD6E0", "#C2185B"),
    ("#E4D9FF", "#5E35B1"),
    ("#CFF5E7", "#00695C"),
    ("#FFE3B8", "#BF360C"),
    ("#D4E4FF", "#1A237E"),
    ("#FFF1B8", "#E65100"),
]


def _clean(text: str) -> str:
    """Make text safe for the built-in PDF font and for XML markup.

    Parameters
    ----------
    text : str
        Raw text, possibly containing emoji or other unsupported characters.

    Returns
    -------
    str
        Escaped text with characters the standard font cannot draw removed.
    """
    supported = text.encode("cp1252", errors="ignore").decode("cp1252").strip()
    return escape(supported).replace("\n", "<br/>")


def build_pdf(config: dict[str, Any], messages: list[dict[str, str]]) -> bytes:
    """Create the PDF keepsake.

    Parameters
    ----------
    config : dict[str, Any]
        Site configuration with ``title``, ``intro`` and ``closing`` keys.
    messages : list[dict[str, str]]
        Team messages, each with ``name`` and ``message`` keys.

    Returns
    -------
    bytes
        The finished PDF file content.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=_clean(config["title"]) or "Thank You",
    )

    title_style = ParagraphStyle(
        "Title", fontName="Helvetica-Bold", fontSize=28, leading=34, alignment=TA_CENTER,
        textColor=colors.white,
    )
    intro_style = ParagraphStyle(
        "Intro", fontName="Helvetica", fontSize=12, leading=18, alignment=TA_CENTER,
        textColor=colors.HexColor("#4A3B78"),
    )
    heading_style = ParagraphStyle(
        "Heading", fontName="Helvetica-Bold", fontSize=18, leading=22, alignment=TA_CENTER,
        textColor=colors.HexColor("#8E24AA"),
    )
    closing_style = ParagraphStyle(
        "Closing", fontName="Helvetica-Bold", fontSize=16, leading=22, alignment=TA_CENTER,
        textColor=colors.HexColor("#E91E63"),
    )
    body_style = ParagraphStyle(
        "Body", fontName="Helvetica", fontSize=12, leading=18, textColor=colors.HexColor("#2B2B2B"),
    )

    banner = Table([[Paragraph(_clean(config["title"]), title_style)]], colWidths=[doc.width])
    banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FF4D8D")),
                ("ROUNDEDCORNERS", [14, 14, 14, 14]),
                ("TOPPADDING", (0, 0), (-1, -1), 18),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
            ]
        )
    )

    story: list[Any] = [
        banner,
        Spacer(1, 8 * mm),
        Paragraph(_clean(config["intro"]), intro_style),
        Spacer(1, 8 * mm),
        Paragraph(f"Messages from the team ({len(messages)})", heading_style),
        Spacer(1, 5 * mm),
    ]

    for index, item in enumerate(messages):
        background, accent = CARD_COLORS[index % len(CARD_COLORS)]
        author_style = ParagraphStyle(
            f"Author{index}", fontName="Helvetica-Bold", fontSize=12, leading=16, alignment=TA_RIGHT,
            textColor=colors.HexColor(accent),
        )
        card = Table(
            [[Paragraph(_clean(item["message"]), body_style)], [Paragraph(f"- {_clean(item['name'])}", author_style)]],
            colWidths=[doc.width],
        )
        card.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(background)),
                    ("ROUNDEDCORNERS", [12, 12, 12, 12]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 14),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                    ("TOPPADDING", (0, 0), (0, 0), 12),
                    ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
                ]
            )
        )
        story.append(KeepTogether([card, Spacer(1, 5 * mm)]))

    story.extend([Spacer(1, 4 * mm), Paragraph(_clean(config["closing"]), closing_style)])
    doc.build(story)
    return buffer.getvalue()
