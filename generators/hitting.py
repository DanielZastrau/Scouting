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
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF

# Translation maps for Sets and Outcomes
translations = {
    'outsides': {
        '1': 'Fast', '2': 'Normal', '3': 'High',
    },
    'middles': {
        '1': 'Quick', '2': 'Behind', '3': 'Shoot', '4': 'Push',
    }
}

OUTCOME_MAP = {
    '1': 'Point',
    '2': 'Defended',
    '3': 'Blocked',
    '4': 'Error'
}


def aggregate_hitting_data(player_data: dict) -> dict:
    """player data is {hitting_position: set_type: hitting_zone: hitting_outcome: count}
    hitting_position 1 - 6
    set_type 1 - 4
    hitting outcome 1 - 4
    """

    summary = {str(i): {
        'total_hits': 0,
        'total_blocks_and_errors': 0,
        'zone_counts': {str(i): 0 for i in range(1, 6)},
        'set_type_counts': {str(i): 0 for i in range(1, 5)},
        'outcome_counts': {str(i): 0 for i in range(1, 5)},
    } for i in range(1, 7)}


    # Aggregate data
    for position, position_data in player_data.items():

        for set_type, set_data in position_data.items():

            for zone, zone_data in set_data.items():

                for outcome, outcome_count in zone_data.items():

                    summary[position]['total_hits'] += outcome_count

                    if outcome in ['3', '4']:
                        summary[position]['total_blocks_and_errors'] += outcome_count

                    if not outcome in ['3', '4']:
                        summary[position]['zone_counts'][zone] += outcome_count

                    summary[position]['set_type_counts'][set_type] += outcome_count

                    summary[position]['outcome_counts'][outcome] += outcome_count

    # Convert to percentages
    for position in summary:

        for zone, zone_count in summary[position]['zone_counts'].items():

            if summary[position]['total_hits'] != 0 and summary[position]['total_hits'] != summary[position]['total_blocks_and_errors']:
                summary[position]['zone_counts'][zone] = zone_count / (summary[position]['total_hits'] - summary[position]['total_blocks_and_errors']) * 100

        for set_type, set_type_count in summary[position]['set_type_counts'].items():

            if summary[position]['total_hits'] != 0:
                summary[position]['set_type_counts'][set_type] = set_type_count / summary[position]['total_hits'] * 100

        for outcome, outcome_count in summary[position]['outcome_counts'].items():
    
            if summary[position]['total_hits'] != 0:
                summary[position]['outcome_counts'][outcome] = outcome_count / summary[position]['total_hits'] * 100

    return summary


def draw_hitting_cones(origin_type, data: None | dict = None):
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

    # Draw data
    if data is None:
        data = {str(i): i for i in range(1, 6)}

    x_targets = [i * width / 10 for i in range(1, 10)]
    y_targets = [i * height / 10 for i in range(1, 10)]

    outside_selectors = [(0, 8), (4, 8), (8, 8), (8, 4), (8, 1)]
    middle_selectors = [(0, 1), (0, 5), (4, 8), (8, 5), (8, 1)]
    opposite_selectors = [(0, 1), (0, 4), (0, 8), (5, 8), (8, 8)]

    if origin_type == 'left':
        selectors = outside_selectors
    elif origin_type == 'center':
        selectors = middle_selectors
    else:
        selectors = opposite_selectors

    for i, (x_selector, y_selector) in enumerate(selectors):
        target_x = x_targets[x_selector]
        target_y = y_targets[y_selector]

        d.add(String(target_x, target_y, f'{data[str(i + 1)]:.0f}', textAnchor='middle', fontName='Helvetica-Bold', fontSize=12, fillColor=colors.gray))

    return d


def generate_hitting_report(data: dict, output_filename: str):

    # Define the doc
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
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, leading=12)
    stat_style = ParagraphStyle('Stats', parent=styles['Normal'], fontSize=9, leading=10)


    # --- Section 1: Introduction & Diagrams ---
    elements.append(Paragraph("Attacking Report: Zones & Analysis", title_style))
    
    intro_text = (
        "<b>Zone Definition:</b> The opponent's court is divided into 5 equal pizza slices relative to the attacker. "
        "<b>Zone 1</b> represents the leftmost zone, while <b>Zone 5</b> represents the rightmost zone. "
        "The diagrams below visualize these lanes radiating from the attacker's perspective."
    )
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 1*cm))


    # Diagram Table (Initial Reference)
    drawing_left = draw_hitting_cones('left')
    drawing_center = draw_hitting_cones('center')
    drawing_right = draw_hitting_cones('right')

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


    # --- Section 2: Player Analysis Table ---
    
    # Define Table Headers
    table_rows = [[
        "Player",
        "Pos",
        "Zone Dist in %", 
        "Stats"
    ]]
    col_widths = [2.5*cm, 2.5*cm, 7.0*cm, 5*cm]

    # Sort players numerically
    player_ids = sorted(data.keys(), key=lambda x: int(x))

    for player_id in player_ids:
        player_data = data[player_id]

        summary = aggregate_hitting_data(player_data)

        for position in [position for position in summary if summary[position]['total_hits'] != 0]:


            # Column 1: Player ID
            player_num = Paragraph(f"<b>#{player_id}</b>", h2_style)


            # Column 2: Position
            position_ = Paragraph(f"Pos: {position}", normal_style)


            # Column 3: Distribution Diagram
            if position == '4':
                zones_dist = draw_hitting_cones('left', summary[position]['zone_counts'])
            elif position in ['3', '6']:
                zones_dist = draw_hitting_cones('center', summary[position]['zone_counts'])
            elif position in ['1', '2']:
                zones_dist = draw_hitting_cones('right', summary[position]['zone_counts'])


            # Column 4: Stats Text
            if position == '3':
                set_translations = translations['middles']
            else:
                set_translations = translations['outsides']

            if summary[position]['total_hits'] > 0:
                lines = [f"<b>Total Hits: {summary[position]['total_hits']}</b><br/>"]
                
                # outcomes
                lines.append("<b>By Outcome:</b>")
                for outcome_key, outcome_name in OUTCOME_MAP.items():
                    percentage = summary[position]['outcome_counts'].get(outcome_key, 0)
                    lines.append(f"- {outcome_name}: {percentage:.0f}%")
                
                # set types
                lines.append("<br/><b>By Set Type:</b>")
                for set_key, set_percentage in summary[position]['set_type_counts'].items():

                    if position != '3' and set_key == '4':
                        continue

                    lines.append(f"- {set_translations[set_key]}: {set_percentage:.0f}%")
                
                stats_text = "<br/>".join(lines)
            else:
                stats_text = "No Data"

            stats_dist = Paragraph(stats_text, stat_style)

            # Append Row
            table_rows.append([player_num, position_, zones_dist, stats_dist])

    # --- Build Main Table ---
    main_table = Table(table_rows, colWidths = col_widths)
    
    main_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data Rows
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'), # Center ID
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    elements.append(main_table)

    # Build PDF
    doc.build(elements)
    print(f"PDF generated successfully: {output_filename}")

if __name__ == "__main__":
    
    # Determine paths
    input_path = os.path.join('.', 'analysis', 'hits.json')
    output_path = os.path.join('.', 'reports', 'hits_report.pdf')

    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
    else:
        with open(input_path, 'r', encoding='utf-8') as file:
            hits_data = json.load(file)

        generate_hitting_report(hits_data, output_path)