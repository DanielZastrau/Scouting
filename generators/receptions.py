import argparse
import json
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def calculate_reception_stats(player_serves: dict, serve_type: str) -> dict:
    """
    Aggregates reception stats per serve type (Float/Jump) and a grand total.
    1 for float, 2 for jumper
    """
    summary = {
        'total': 0,
        'perfect': 0,
        'okay': 0,
        'bad': 0,
        'error': 0,
    }

    translation = {'1': 'float', '2': 'jumper'}

    for serve, outcomes in player_serves.items():

        if translation[serve] != serve_type.lower():
            continue

        # Outcome keys in JSON are strings '1' through '4'
        perfect = outcomes.get('1', 0)
        okay = outcomes.get('2', 0)
        bad = outcomes.get('3', 0)
        error = outcomes.get('4', 0)
        total = perfect + okay + bad + error

        # Turn to percentages and add to summary
        if not total == 0:
            summary['perfect'] += perfect
            summary['okay'] += okay
            summary['bad'] += bad
            summary['error'] += error
            summary['total'] += total

    return summary


def generate_reception_pdf(receptions: dict, output_filename: str):

    # Define the doc
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    elements = []
    styles = getSampleStyleSheet()


    # title
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        alignment=1, # Center
        fontSize=18,
        spaceAfter=12
    )
    elements.append(Paragraph("Reception Report (By Serve Type)", title_style))
    elements.append(Spacer(1, 0.5*cm))


    for serve_type in ['Float', 'Jumper']:

        # Subtitle per serve type
        subtitle_style = ParagraphStyle(        
            'Subtitle',
            parent=styles['Heading2'],
            alignment=1, # Center
            fontSize=12,
            spaceAfter=12
        )
        elements.append(Paragraph(f'Serve Type: {serve_type}', subtitle_style))
        elements.append(Spacer(1, 0.5*cm))


        # --- Table Setup ---
        headers = ["Player", "Tot", "Perf(%)", "Okay(%)", "Bad(%)", "Err(%)"]
        col_widths = [2.5*cm, 2.5*cm, 2.0*cm, 2.0*cm, 2.0*cm, 2.0*cm]

        table_data = [headers]


        # Initialize styling with Header styles
        table_style_cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),

            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
        ]


        # Sort players numerically
        sorted_player_keys = sorted(receptions.keys(), key=lambda x: int(x))
        row_idx = 1 # Start after header


        for player_num in sorted_player_keys:

            stats = calculate_reception_stats(receptions[player_num], serve_type=serve_type)


            if stats['total'] == 0:
                continue


            datarow = [
                f"#{player_num}",
                str(stats['total']),
                f"{stats['perfect'] / stats['total'] * 100:.0f}%  ({stats['perfect']})",
                f"{stats['okay'] / stats['total'] * 100:.0f}%  ({stats['okay']})",
                f"{stats['bad'] / stats['total'] * 100:.0f}%  ({stats['bad']})",
                f"{stats['error'] / stats['total'] * 100:.0f}%  ({stats['error']})",
            ]

            table_data.append(datarow)

        # --- Build Table ---
        t = Table(table_data, colWidths=col_widths)
        t.setStyle(TableStyle(table_style_cmds))

        elements.append(t)

        elements.append(Spacer(1, 1*cm))

    # Build the PDF
    doc.build(elements)
    print(f"PDF generated successfully: {output_filename}")

if __name__ == "__main__":
    
    # Determine paths
    input_path = os.path.join('.', 'analysis', 'receptions.json')
    output_path = os.path.join('.', 'reports', 'receptions_report.pdf')

    try:
        with open(input_path, 'r', encoding='utf-8') as file:
            receptions_data = json.load(file)
        
        generate_reception_pdf(receptions_data, output_path)

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {input_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")