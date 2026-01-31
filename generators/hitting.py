import argparse
import json
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics import renderPDF


translations = {
    'outsides': {
        '1': 'fast ball',
        '2': 'normal',
        '3': 'high ball',
    },
    'middles': {
        '1': 'quickset',
        '2': 'quickset behind',
        '3': 'shoot',
        '4': 'push',
    }
}

def draw_hitting_cones(origin_type):
    """
    Creates a Drawing object representing the court and hitting lanes.
    origin_type: 
        'left' (Pos 4 - Bottom Left Origin)
        'center' (Pos 3 - Bottom Center Origin)
        'right' (Pos 2 - Bottom Right Origin)
    """
    width = 150
    height = 150
    d = Drawing(width, height)

    # Draw the Court (Opponent's side)
    d.add(Rect(0, 0, width, height, strokeColor=colors.black, fillColor=colors.whitesmoke, strokeWidth=2))

    # Define Origin X coordinate
    if origin_type == 'left':
        origin_x = 0
        origin_y = 0
    elif origin_type == 'center':
        origin_x = width / 2
        origin_y = 0
    else: # right
        origin_x = width
        origin_y = 0

    x_targets = [
        0,
        width / 4,
        width / 3,
        width / 2,
        2 * width / 3,
        3 * width / 4,
        width
    ]
    y_targets = [
        height,
        3 * height / 4,
        2 * height / 3,
        height / 2,
        height / 3,
        height / 4,
        0
    ]
    
    outside_selectors = [(2, 0), (4, 0), (6, 1), (6, 4)]
    middle_selectors = [(0, 3), (1, 0), (5, 0), (6, 3)]
    opposite_selectors = [(0, 4), (0, 1), (2, 0), (4, 0)]

    # Draw dividing lines
    if origin_type == 'left':
        selectors = outside_selectors
    elif origin_type == 'center':
        selectors = middle_selectors
    else:
        selectors = opposite_selectors

    for x_selector, y_selector in selectors:
        target_x = x_targets[x_selector]
        target_y = y_targets[y_selector]

        d.add(Line(origin_x, origin_y, target_x, target_y, strokeColor=colors.red, strokeWidth=1, strokeDashArray=[2, 2]))

    return d


def generate_hitting_report(data: dict, output_filename: str):
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )

    elements = []
    styles = getSampleStyleSheet()
    
    # --- Styles ---
    title_style = ParagraphStyle('MainTitle', parent=styles['Heading1'], alignment=1, fontSize=18, spaceAfter=12)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, spaceBefore=12, spaceAfter=6, textColor=colors.darkblue)
    h3_style = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=12, spaceBefore=10, spaceAfter=4)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, leading=12)

    # --- Section 1: Introduction & Diagrams ---
    elements.append(Paragraph("Attacking Report: Zones & Analysis", title_style))
    
    intro_text = (
        "<b>Zone Definition:</b> The opponent's court is divided into 5 equal vertical slices relative to the attacker. "
        "<b>Zone 1</b> represents the leftmost zone, while <b>Zone 5</b> represents the rightmost zone. "
        "The diagrams below visualize these lanes radiating from the attacker's perspective."
    )
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 1*cm))

    # Diagram Table
    drawing_left = draw_hitting_cones('left')
    drawing_center = draw_hitting_cones('center')
    drawing_right = draw_hitting_cones('right')

    # Labels for diagrams
    lbl_left = Paragraph("<b>From Pos 4</b><br/>(Left Front)", styles['Normal'])
    lbl_center = Paragraph("<b>From Pos 3</b><br/>(Middle)", styles['Normal'])
    lbl_right = Paragraph("<b>From Pos 2</b><br/>(Right Front)", styles['Normal'])

    diag_data = [
        [drawing_left, drawing_center, drawing_right],
        [lbl_left, lbl_center, lbl_right]
    ]

    diag_table = Table(diag_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
    diag_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    
    elements.append(diag_table)
    elements.append(PageBreak())


    # --- Section 2: Player Analysis ---
    
    # Sort players numerically
    player_ids = sorted(data.keys(), key=lambda x: int(x))

    for player_id in player_ids:
        player_data = data[player_id]
        
        elements.append(Paragraph(f"Player #{player_id}", h2_style))
        
        # Initialize Player Totals (Aggregator across all positions)
        player_totals = {
            'point': 0,
            'defended': 0,
            'blocked': 0,
            'error': 0,
            'total': 0
        }

        # Iterate positions (where they hit FROM)
        positions = sorted(player_data.keys(), key=lambda x: int(x))
        
        for pos in positions:
            pos_data = player_data[pos]

            elements.append(Paragraph(f"Attacking from Position {pos}", h3_style))
            
            if pos in ['2', '4', '1']:
                translation_key = 'outsides'
            else:
                translation_key = 'middles'

            # Prepare Table Data
            table_rows = [[
                "Set Type", 
                "Hit Zone", 
                "Point", "Defended", "Blocked", "Error", 
                "Total"
            ]]
            
            # Aggregators for the current position summary
            pos_stats = {
                'point': 0, 'defended': 0, 'blocked': 0, 'error': 0, 'total': 0
            }

            has_data = False
            
            set_types = sorted(pos_data.keys(), key=lambda x: int(x))
            
            for st in set_types:
                zone_dict = pos_data[st]
                zones = sorted(zone_dict.keys(), key=lambda x: int(x))

                for z in zones:
                    outcomes = zone_dict[z]
                    
                    c1 = outcomes.get('1', 0) # Point
                    c2 = outcomes.get('2', 0) # Defended
                    c3 = outcomes.get('3', 0) # Blocked
                    c4 = outcomes.get('4', 0) # Error
                    
                    total = c1 + c2 + c3 + c4
                    
                    if total > 0:
                        has_data = True
                        
                        # Add to position stats
                        pos_stats['point'] += c1
                        pos_stats['defended'] += c2
                        pos_stats['blocked'] += c3
                        pos_stats['error'] += c4
                        pos_stats['total'] += total

                        row = [
                            f"{translations[translation_key].get(st, st)}",
                            f"Zone {z}",
                            c1, c2, c3, c4,
                            total
                        ]
                        table_rows.append(row)
            
            if has_data:
                # Add Position Summary Row
                summary_row = [
                    "SUMMARY",
                    "-",
                    pos_stats['point'], 
                    pos_stats['defended'], 
                    pos_stats['blocked'], 
                    pos_stats['error'],
                    pos_stats['total']
                ]
                table_rows.append(summary_row)

                # Add to Player Global Totals
                player_totals['point'] += pos_stats['point']
                player_totals['defended'] += pos_stats['defended']
                player_totals['blocked'] += pos_stats['blocked']
                player_totals['error'] += pos_stats['error']
                player_totals['total'] += pos_stats['total']

                t = Table(table_rows, colWidths=[2.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm])
                
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    
                    # Highlight Total Column
                    ('BACKGROUND', (-1, 1), (-1, -1), colors.whitesmoke),
                    ('FONTBOLD', (-1, 1), (-1, -1), True),

                    # Highlight Position Summary Row
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ]))
                
                elements.append(t)
                elements.append(Spacer(1, 0.5*cm))
            else:
                elements.append(Paragraph("No hitting data recorded for this position.", styles['Italic']))
                elements.append(Spacer(1, 0.5*cm))
        
        # --- Player Total Summary Table ---
        if player_totals['total'] > 0:
            elements.append(Spacer(1, 0.2*cm))
            elements.append(Paragraph(f"Player #{player_id}: Overall Summary", h3_style))
            
            total_headers = [
                "Scope", "Hit Zone", "Point", "Defended", "Blocked", "Error", "Total"
            ]
            total_data = [
                "Total", 
                "-", 
                player_totals['point'], 
                player_totals['defended'], 
                player_totals['blocked'], 
                player_totals['error'],
                player_totals['total']
            ]
            
            t_total = Table([total_headers, total_data], colWidths=[2.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm])
            
            t_total.setStyle(TableStyle([
                # Black Header to differentiate from position tables
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                
                # Bold data row
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ]))
            
            elements.append(t_total)

        # Divide players visually
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph("_" * 60, styles['Normal']))
        elements.append(Spacer(1, 1*cm))

    # Build PDF
    try:
        doc.build(elements)
        print(f"PDF generated successfully: {output_filename}")
    except Exception as e:
        print(f"Error generating PDF: {e}")

if __name__ == "__main__":
    
    # Determine paths
    input_path = os.path.join('.', 'analysis', 'hits.json')
    output_path = os.path.join('.', 'reports', 'hits_report.pdf')

    try:
        if not os.path.exists(input_path):
            print(f"File not found: {input_path}")
        else:
            with open(input_path, 'r', encoding='utf-8') as file:
                hits_data = json.load(file)

            generate_hitting_report(hits_data, output_path)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")