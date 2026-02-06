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
# New imports for drawing graphics
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Circle
from reportlab.graphics import renderPDF

serve_translation = {
    '1': 'Float',
    '2': 'Jumper',
    '3': 'Jumper after<br/>float toss',
    '4': 'Floater after<br/>jump toss',
}
outcome_translation = {
    '1': 'Ace',
    '2': 'Overpass',
    '3': 'Received',
    '4': 'Error',
}


def draw_court_diagram(data: None | dict = None):
    """
    Creates a Drawing object representing one side of the volleyball court.
    Includes custom user lines and standard zone markers.
    """
    # Dimensions for the drawing (in points)
    width = 200
    height = 200 # Square (9m x 9m aspect ratio)
    
    d = Drawing(width, height)

    # --- 1. BASE COURT STRUCTURE ---
    d.add(Rect(0, 0, width, height, strokeColor=colors.black, fillColor=colors.whitesmoke, strokeWidth=2))

    # Draw the 3-meter line (Attack line)
    attack_line_y = height * (2/3) 
    d.add(Line(0, attack_line_y, width, attack_line_y, strokeColor=colors.black, strokeWidth=1))

    # Draw the Net (Thicker line at the top)
    d.add(Line(0, height, width, height, strokeColor=colors.black, strokeWidth=4))

    # --- USER CUSTOM LINES (Vertical Strips) ---
    zone_one_zone_nine_border = ((width / 2, height), (width / 2, 2 * height / 3))
    zone_two_zone_thr_border = ((width / 7, 2 * height / 3), (width / 7, 0))
    zone_thr_zone_fou_border = ((2 * width / 7, 2 * height / 3), (2 * width / 7, 0))
    zone_fou_zone_fiv_border = ((3 * width / 7, 2 * height / 3), (3 * width / 7, 0))
    zone_fiv_zone_six_border = ((4 * width / 7, 2 * height / 3), (4 * width / 7, 0))
    zone_six_zone_sev_border = ((5 * width / 7, 2 * height / 3), (5 * width / 7, 0))
    zone_sev_zone_eig_border = ((6 * width / 7, 2 * height / 3), (6 * width / 7, 0))

    borders = [
        zone_one_zone_nine_border, zone_two_zone_thr_border,
        zone_thr_zone_fou_border, zone_fou_zone_fiv_border,
        zone_fiv_zone_six_border, zone_six_zone_sev_border,
        zone_sev_zone_eig_border
    ]

    for border in borders:
        d.add(Line(border[0][0], border[0][1], border[1][0], border[1][1], strokeColor=colors.darkgrey, strokeWidth=0.5))


    # --- 3. LABELS AND DOTS (Standard 3x3 Grid Overlay) ---
    
    # Dictionary mapping Zone Number -> (x, y)
    zone_coords = {
        1: (width / 4, 5 * height / 6),
        2: (width / 8, height / 5),
        3: (2 * width / 8, height / 5),
        4: (3 * width / 8, height / 5),
        5: (4 * width / 8, height / 5),
        6: (5 * width / 8, height / 5),
        7: (6 * width / 8, height / 5),
        8: (7 * width / 8, height / 5),
        9: (3 * width / 4, 5 * height / 6)
    }

    # Add data
    if data == None:
        data = {str(i): i for i in range(1, 10)}

    for z_num, (zx, zy) in zone_coords.items():
        d.add(String(zx, zy - 3, str(data[str(z_num)]), textAnchor='middle', fontName='Helvetica-Bold', fontSize=12, fillColor=colors.gray))

    # Add dots symbolizing receivers
    dot_coords = [
        (2 * width / 8, height / 4),
        (4 * width / 8, height / 4),
        (6 * width / 8, height / 4),
    ]
    for cx, cy in dot_coords:
        d.add(Circle(cx, cy + 10, 4, fillColor=colors.red, strokeColor=colors.black, strokeWidth=0.5))

    return d


def calculate_stats(data: dict) -> dict:
    """Calculates zone distribution and outcome distribution

    zone 10 is for not attributable errors (i.e. net errors)

    data = serves[player_num]
    """
    
    stats = {
        str(serve_type): {
            'total_serves': 0,
            'total_serves_for_zone_count': 0,
            'zone_dist': {str(i): 0 for i in range(1, 10)},
            'outcome_dist': {str(i): 0 for i in range(1, 5)},
        } for serve_type in range(1, 5)
    }


    for serve_type, zones in data.items():
        for zone, outcomes in zones.items():

            if zone != '10':
                stats[serve_type]['zone_dist'][zone] = sum(outcomes.values())
                stats[serve_type]['total_serves_for_zone_count'] += sum(outcomes.values())

            stats[serve_type]['total_serves'] += sum(outcomes.values())

            stats[serve_type]['outcome_dist']['1'] += outcomes.get('1', 0)
            stats[serve_type]['outcome_dist']['2'] += outcomes.get('2', 0)
            stats[serve_type]['outcome_dist']['3'] += outcomes.get('3', 0)
            stats[serve_type]['outcome_dist']['4'] += outcomes.get('4', 0)


    # convert to percentages
    for serve_type in stats:

        if stats[serve_type]['total_serves'] == 0:
            continue

        for zone in stats[serve_type]['zone_dist']:

            if stats[serve_type]['total_serves_for_zone_count'] == 0:
                continue

            stats[serve_type]['zone_dist'][zone] = f'{stats[serve_type]['zone_dist'][zone]  / (stats[serve_type]['total_serves_for_zone_count']) * 100:.0f}'

        for outcome in stats[serve_type]['outcome_dist']:
            stats[serve_type]['outcome_dist'][outcome] = f'{stats[serve_type]['outcome_dist'][outcome] / stats[serve_type]['total_serves'] * 100:.0f}'
            

    return stats


def get_legend_table():
    """Returns the Legend as a formatted Table element."""
    data = [
        ["ZONE KEY (1-9) when looking towards the net"],
        ["1: Frontcourt Left Half  | 2: Left Sideline   | 3: on Pos 5             "],
        ["4: Gap 5-6               | 5: Pos 6           | 6: Gap 6-1              "],
        ["7: on Pos 1              | 8: Right Sideline  | 9: Frontcourt Right Half"],
        ["Red Highlight: Most Aces | Blue Highlight: Most Serves"]
    ]
    
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('FONTBOLD', (0, 0), (-1, 0), True),
        ('TEXTCOLOR', (0, 4), (0, 4), colors.darkgrey), 
    ])
    
    t = Table(data, colWidths=[16*cm])
    t.setStyle(style)

    return t

def generate_pdf_report(serves: dict, output_filename: str):

    # Define the doc
    doc = SimpleDocTemplate(
        output_filename, 
        pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm, 
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()


    # Define the styles
    table_para_style = ParagraphStyle(
        'TablePara',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10 
    )
    
    title_style = ParagraphStyle(
        'CustomTitle', 
        parent=styles['Heading1'], 
        alignment=1, 
        fontSize=16, 
        spaceAfter=10
    )
    
    stat_style = ParagraphStyle(
        'Stats', 
        parent=styles['Normal'], 
        fontSize=9, 
        leading=10
    )
    
    
    # Append the Title to the elements
    elements.append(Paragraph("SERVES REPORT", title_style))
    

    # Add the description of the zones
    elements.append(get_legend_table())
    elements.append(Spacer(1, 0.5*cm))


    # Draw a diagram of the court and the 9 zones to illustrate the concept
    court_drawing = draw_court_diagram()

    description_text = """
    The image to the left serves as an illustration of the 9 defined serve zones. The red dots symbolize the receivers.
    <font color="red">When the receivers move, the zones move with them, this serves only as an illustration. That is, no matter where the receivers start,
    zone 4 is always the gap between the receiver on position 6 and the one on position 5</font>.
    """
    desc_para = Paragraph(description_text, styles['Normal'])
    
    diagram_table_data = [[court_drawing, desc_para]]
    diagram_table = Table(diagram_table_data, colWidths=[7.5*cm, 9.5*cm])
    diagram_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Vertically center the text relative to image
        ('LEFTPADDING', (1,0), (1,0), 12),     # Add padding between image and text
    ]))
    
    elements.append(diagram_table)
    elements.append(Spacer(1, 0.5*cm))
    

    # --- Main Data Table Setup ---
    header_row = ['Plyr', 'Serve', 'Zone Dist in %', 'Outcome Dist in %']
    
    col_widths = [1*cm, 2.5*cm, 8*cm, 5*cm]


    table_rows = [header_row] 


    row_with_diff_styling = []
    row_id = 1


    sorted_players = sorted(serves.keys(), key = lambda x: int(x))
    for player_num in sorted_players:

        player_stats = calculate_stats(serves[player_num])

        already_added_player_id = False

        for serve_type in player_stats:
                
            if player_stats[serve_type]['total_serves'] == 0:
                continue

            # col 1  --  player num
            if already_added_player_id:
                col_1 = '-'
            else:
                col_1 = f'#{player_num}'
                already_added_player_id = True


            # col 2  -- serve type
            col_2 = Paragraph(f'{serve_translation[serve_type]}', stat_style)


            # Zone Distribution, i.e. court diagram
            zone_dist = draw_court_diagram(data=player_stats[serve_type]['zone_dist'])

            # Outcomes
            lines = []

            lines.append(f'<b>Total Serves:</b> {player_stats[serve_type]['total_serves']}<br/>')

            lines.append('<b>By Outcome:</b>')
            for outcome_key, outcome_name in outcome_translation.items():
                lines.append(f'- {outcome_name}: {player_stats[serve_type]['outcome_dist'][outcome_key]}%')
            outcome_dist = "<br/>".join(lines)

            outcome_dist = Paragraph(outcome_dist, stat_style)


            table_rows.append([col_1, col_2, zone_dist, outcome_dist])

            row_id += 1


        table_rows.append(['', '', '', ''])
        row_with_diff_styling.append(row_id)
        row_id += 1


    # --- Build Main Table ---
    main_table = Table(table_rows, colWidths = col_widths)
    

    table_style = TableStyle([
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
    ])

    # rows with different styling
    for row in row_with_diff_styling:
        table_style.add(
            'BACKGROUND', (0, row), (-1, row), colors.lightgrey
        )


    main_table.setStyle(table_style)

    elements.append(main_table)


    doc.build(elements)
    print(f"PDF generated successfully: {output_filename}")


if __name__ == "__main__":

    # Determine paths
    input_path = os.path.join('.', 'analysis', 'serves.json')
    output_path = os.path.join('.', 'reports', 'serves_report.pdf')

    if not os.path.exists(input_path):
            print("Error: Input files not found.")
    else:
        with open(input_path, 'r', encoding='utf-8') as file:
            serves_data = json.load(file)

        generate_pdf_report(serves_data, output_filename=output_path)