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


def generate_breaks_report(breaks: dict, breaks_player: dict, output_filename: str):

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
    elements.append(Paragraph("Break Report", title_style))
    elements.append(Spacer(1, 0.5*cm))


    col_widths = [7*cm, 7*cm]


    # --- Build Rotation Table ---

    subtitle_style = ParagraphStyle(        
        'Subtitle',
        parent=styles['Heading2'],
        alignment=1, # Center
        fontSize=12,
        spaceAfter=12
    )
    elements.append(Paragraph(f'Breaks by Rotation', subtitle_style))
    elements.append(Spacer(1, 0.5*cm))

    headers = ["Rotation", "Breaks"]
    table_data = [headers]

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

    max_val = max(breaks.values())
    max_row_ids = []

    min_val = min(breaks.values())
    min_row_ids = []

    curr_row_id = 1
    for rotation in breaks:

        datarow = [
            f'{int(rotation) + 1}',
            f'Breaks: {breaks[rotation]}'
        ]

        table_data.append(datarow)

        if breaks[rotation] == max_val:
            max_row_ids.append(curr_row_id)

        if breaks[rotation] == min_val:
            min_row_ids.append(curr_row_id)

        curr_row_id += 1

    # Highlights
    for row_id in max_row_ids:
        table_style_cmds.append(('BACKGROUND', (0, row_id), (1, row_id), colors.red))

    for row_id in min_row_ids:
        table_style_cmds.append(('BACKGROUND', (0, row_id), (1, row_id), colors.green))

    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle(table_style_cmds))

    elements.append(t)

    elements.append(Spacer(1, 1*cm))


    # --- Build Serve Table ---
    subtitle_style = ParagraphStyle(        
        'Subtitle',
        parent=styles['Heading2'],
        alignment=1, # Center
        fontSize=12,
        spaceAfter=12
    )
    elements.append(Paragraph(f'Breaks by Serve', subtitle_style))
    elements.append(Spacer(1, 0.5*cm))

    headers = ["Player", "Breaks"]
    table_data = [headers]

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

    max_val = max(breaks_player.values())
    max_row_ids = []

    curr_row_id = 1

    sorted_keys = sorted(breaks_player.keys(), key = lambda x: int(x))
    for player in sorted_keys:

        datarow = [
            player,
            f'Breaks: {breaks_player[player]}'
        ]

        table_data.append(datarow)

        if breaks_player[player] == max_val:
            max_row_ids.append(curr_row_id)

        curr_row_id += 1

    # Highlights
    for row_id in max_row_ids:
        table_style_cmds.append(('BACKGROUND', (0, row_id), (1, row_id), colors.red))

    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle(table_style_cmds))

    elements.append(t)

    elements.append(Spacer(1, 1*cm))


    # Build the PDF
    doc.build(elements)
    print(f"PDF generated successfully: {output_filename}")


if __name__ == "__main__":
    
    # Determine paths
    input_path_1 = os.path.join('.', 'analysis', 'breakpoints.json')
    input_path_2 = os.path.join('.', 'analysis', 'breakpoints_players.json')
    output_path = os.path.join('.', 'reports', 'breaks_report.pdf')

    try:
        with open(input_path_1, 'r', encoding='utf-8') as file:
            breaks_data = json.load(file)

        with open(input_path_2, 'r', encoding='utf-8') as file:
            breaks_player_data = json.load(file)
        
        generate_breaks_report(breaks_data, breaks_player_data, output_path)

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {input_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")