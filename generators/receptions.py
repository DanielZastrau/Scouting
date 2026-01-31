import argparse
import json
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def calculate_reception_stats(player_serves: dict) -> dict:
    """
    Aggregates reception stats per serve type and a grand total.
    """
    summary = {}
    for key in ['1', '2', '3', 'All']:
        summary[key] = {'total': 0, 'perfect': 0, 'okay': 0, 'bad': 0, 'error': 0}

    for serve_type, outcomes in player_serves.items():
        if serve_type not in summary:
            continue

        p = outcomes.get('1', 0)
        o = outcomes.get('2', 0)
        b = outcomes.get('3', 0)
        e = outcomes.get('4', 0)
        total = p + o + b + e

        summary[serve_type]['perfect'] += p
        summary[serve_type]['okay'] += o
        summary[serve_type]['bad'] += b
        summary[serve_type]['error'] += e
        summary[serve_type]['total'] += total

        summary['All']['perfect'] += p
        summary['All']['okay'] += o
        summary['All']['bad'] += b
        summary['All']['error'] += e
        summary['All']['total'] += total

    return summary

def generate_reception_pdf(data: dict, output_filename: str):
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # --- Title ---
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        alignment=1, # Center
        fontSize=18,
        spaceAfter=12
    )
    elements.append(Paragraph("Reception Report (By Serve Type)", title_style))
    elements.append(Spacer(1, 0.5*cm))

    # --- Table Setup ---
    headers = [
        "Player", 
        "Type", 
        "Tot", 
        "Perf", 
        "Okay", 
        "Bad", 
        "Err"
    ]
    table_data = [headers]

    # Initialize styling with Header styles
    # Note: We removed the global 'GRID' command to handle spacing manually
    table_style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        # Grid for Header only
        ('GRID', (0, 0), (-1, 0), 0.5, colors.grey),
    ]

    sorted_player_keys = sorted(data.keys(), key=lambda x: int(x))

    row_idx = 1 # Start after header

    for player_num in sorted_player_keys:
        stats = calculate_reception_stats(data[player_num])
        
        # Row 1: Float
        s1 = stats['1']
        row_float = [f"#{player_num}", "Float", s1['total'], s1['perfect'], s1['okay'], s1['bad'], s1['error']]
        
        # Row 2: Jump
        s2 = stats['2']
        row_jump = ["", "Jump", s2['total'], s2['perfect'], s2['okay'], s2['bad'], s2['error']]
        
        # Row 3: Hybrid
        s3 = stats['3']
        row_hyb = ["", "Hybrid", s3['total'], s3['perfect'], s3['okay'], s3['bad'], s3['error']]
        
        # Row 4: Total Summary
        st = stats['All']
        row_tot = ["", "TOTAL", st['total'], st['perfect'], st['okay'], st['bad'], st['error']]

        # Row 5: Whitespace (Empty row)
        row_space = [""] * 7

        # Add all rows to data
        table_data.extend([row_float, row_jump, row_hyb, row_tot, row_space])

        # --- Styling for this player block ---
        
        # 1. Grid: Apply only to the 4 data rows, NOT the spacer row
        #    rows: row_idx to row_idx + 3
        table_style_cmds.append(('GRID', (0, row_idx), (-1, row_idx + 3), 0.5, colors.grey))

        # 2. Span Player Name across the 4 data rows
        table_style_cmds.append(('SPAN', (0, row_idx), (0, row_idx + 3)))
        
        # 3. Total Row Highlights (Bold + Grey Background)
        table_style_cmds.append(('FONTBOLD', (1, row_idx + 3), (-1, row_idx + 3), True))
        table_style_cmds.append(('BACKGROUND', (1, row_idx + 3), (-1, row_idx + 3), colors.whitesmoke))
        
        # 4. Thick Separator Line at the bottom of the DATA block (above the spacer)
        table_style_cmds.append(('LINEBELOW', (0, row_idx + 3), (-1, row_idx + 3), 1.5, colors.black))

        # Advance index by 5 (4 data rows + 1 spacer row)
        row_idx += 5

    # --- Build Table ---
    col_widths = [2.5*cm, 2.5*cm, 1.5*cm, 2.0*cm, 2.0*cm, 2.0*cm, 2.0*cm]
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle(table_style_cmds))

    elements.append(t)

    try:
        doc.build(elements)
        print(f"Success: Reception report generated at '{output_filename}'")
    except Exception as e:
        print(f"Error building PDF: {e}")

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