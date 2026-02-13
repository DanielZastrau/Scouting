import argparse
import os
import random
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def generate_joke_report(output_filename: str):
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # --- Title ---
    title_style = ParagraphStyle(
        'JokeTitle',
        parent=styles['Heading1'],
        alignment=1, # Center
        fontSize=24,
        spaceAfter=2*cm
    )
    elements.append(Paragraph("For Oli", title_style))
    
    # --- Stats Styles ---
    stat_style = ParagraphStyle(
        'JokeStat',
        parent=styles['Normal'],
        alignment=1, # Center
        fontSize=14,
        leading=18,
        spaceAfter=12
    )

    # --- Generate Random Stats ---
    stats = [
        ("Trainer - Discussions with Ref", random.randint(1, 10)),
        ("Trainer - Crashouts", random.randint(1, 10)),
        ("Trainer - Thrown tactic boards", random.randint(1, 10))
    ]

    for label, value in stats:
        text = f"<b>{label}:</b> {value}"
        elements.append(Paragraph(text, stat_style))
        elements.append(Spacer(1, 0.5*cm))

    # Build PDF
    try:
        doc.build(elements)
        print(f"PDF generated successfully: {output_filename}")
    except Exception as e:
        print(f"Error generating PDF: {e}")

if __name__ == "__main__":

    # Determine path
    output_path = os.path.join('.', 'reports', 'for_oli_report.pdf')

    generate_joke_report(output_path)