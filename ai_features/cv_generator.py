import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER

PRIMARY   = colors.HexColor('#1a1a2e')
ACCENT    = colors.HexColor('#0f3460')
HIGHLIGHT = colors.HexColor('#e94560')
LIGHT     = colors.HexColor('#f5f5f5')


def build_cv_pdf(cv) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm,  bottomMargin=1.5*cm,
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        'Name', fontSize=24, textColor=PRIMARY,
        fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4,
    )
    title_style = ParagraphStyle(
        'Title', fontSize=13, textColor=ACCENT,
        fontName='Helvetica', alignment=TA_CENTER, spaceAfter=4,
    )
    contact_style = ParagraphStyle(
        'Contact', fontSize=9, textColor=colors.grey,
        alignment=TA_CENTER, spaceAfter=2,
    )
    section_style = ParagraphStyle(
        'Section', fontSize=12, textColor=PRIMARY,
        fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        'Body', fontSize=10, textColor=colors.black,
        leading=14, spaceAfter=3,
    )
    job_title_style = ParagraphStyle(
        'JobTitle', fontSize=10, textColor=ACCENT,
        fontName='Helvetica-Bold', spaceAfter=1,
    )
    small_style = ParagraphStyle(
        'Small', fontSize=9, textColor=colors.grey, spaceAfter=2,
    )

    story = []

    story.append(Paragraph(cv.full_name, name_style))
    story.append(Paragraph(cv.title, title_style))

    contact_parts = []
    if cv.email:    contact_parts.append(cv.email)
    if cv.phone:    contact_parts.append(cv.phone)
    if cv.location: contact_parts.append(cv.location)
    story.append(Paragraph('  |  '.join(contact_parts), contact_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width='100%', thickness=2, color=HIGHLIGHT))
    story.append(Spacer(1, 6))

    summary_text = cv.enhanced_summary or cv.summary
    if summary_text:
        story.append(Paragraph('PROFESSIONAL SUMMARY', section_style))
        story.append(HRFlowable(width='100%', thickness=0.5, color=LIGHT))
        story.append(Spacer(1, 4))
        story.append(Paragraph(summary_text, body_style))

    experience_data = cv.enhanced_experience if cv.enhanced_experience else cv.experience
    if experience_data:
        story.append(Paragraph('WORK EXPERIENCE', section_style))
        story.append(HRFlowable(width='100%', thickness=0.5, color=LIGHT))
        story.append(Spacer(1, 4))
        for exp in experience_data:
            story.append(Paragraph(f"{exp.get('role', '')} — {exp.get('company', '')}", job_title_style))
            story.append(Paragraph(exp.get('duration', ''), small_style))
            if exp.get('description'):
                story.append(Paragraph(exp.get('description'), body_style))
            story.append(Spacer(1, 4))

    if cv.education:
        story.append(Paragraph('EDUCATION', section_style))
        story.append(HRFlowable(width='100%', thickness=0.5, color=LIGHT))
        story.append(Spacer(1, 4))
        for edu in cv.education:
            story.append(Paragraph(f"{edu.get('degree', '')} — {edu.get('institution', '')}", job_title_style))
            story.append(Paragraph(edu.get('year', ''), small_style))
            story.append(Spacer(1, 4))

    if cv.skills:
        story.append(Paragraph('SKILLS', section_style))
        story.append(HRFlowable(width='100%', thickness=0.5, color=LIGHT))
        story.append(Spacer(1, 4))
        skills = cv.skills
        rows   = [skills[i:i+3] for i in range(0, len(skills), 3)]
        for row in rows:
            while len(row) < 3:
                row.append('')
            table = Table([row], colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
                ('TEXTCOLOR',  (0, 0), (-1, -1), PRIMARY),
                ('FONTNAME',   (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE',   (0, 0), (-1, -1), 9),
                ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
                ('ROWPADDING', (0, 0), (-1, -1), 6),
                ('GRID',       (0, 0), (-1, -1), 0.5, colors.white),
            ]))
            story.append(table)
            story.append(Spacer(1, 3))

    if cv.languages:
        story.append(Paragraph('LANGUAGES', section_style))
        story.append(HRFlowable(width='100%', thickness=0.5, color=LIGHT))
        story.append(Spacer(1, 4))
        story.append(Paragraph(', '.join(cv.languages), body_style))

    doc.build(story)
    return buffer.getvalue()