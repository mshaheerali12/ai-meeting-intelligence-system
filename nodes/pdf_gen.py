from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from langsmith import traceable
import io


@traceable(name="generate meeting PDF")
async def generate_meeting_pdf_bytes( summary_text: str):
    buffer = io.BytesIO()  # 🔥 In-memory buffer

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4
    )

    elements = []
    styles = getSampleStyleSheet()

    # Custom Heading Style
    heading_style = ParagraphStyle(
        name="HeadingStyle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.darkblue,
        spaceAfter=14
    )

    # Body Style
    body_style = ParagraphStyle(
        name="BodyStyle",
        parent=styles["Normal"],
        fontSize=12,
        leading=16
    )

    # -----------------------
    # TRANSCRIPTION SECTION
    # -----------------------


    # -----------------------
    # SUMMARY SECTION
    # -----------------------

    elements.append(Paragraph("Summary", heading_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(
        Paragraph(summary_text.replace("\n", "<br/>"), body_style)
    )

    # Build PDF into memory
    doc.build(elements)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes