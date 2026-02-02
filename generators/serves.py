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

translation = {'f': 'Float',  's': 'Jumper',  'h': 'Hybrid'}

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


def calculate_stats(zones: dict) -> dict:
    """Calculates zone distribution and outcome distribution
    
    zones = serves[player_num]
    """
    
    stats = {
        'zone_dist': {str(i): 0 for i in range(1, 10)},
        'outcome_dist': {str(i): 0 for i in range(1, 5)},
        'total_serves': 0,
        'total_errs': 0,
    }

    for zone, outcomes in zones.items():

        stats['zone_dist'][zone] = outcomes.get('1', 0) + outcomes.get('2', 0) + outcomes.get('3', 0)

        stats['total_serves'] += outcomes.get('1', 0) + outcomes.get('2', 0) + outcomes.get('3', 0) + outcomes.get('4', 0)
        stats['total_errs'] += outcomes.get('4', 0)

        stats['outcome_dist']['1'] += outcomes.get('1', 0)
        stats['outcome_dist']['2'] += outcomes.get('2', 0)
        stats['outcome_dist']['4'] += outcomes.get('4', 0)

    # convert to percentages
    for zone in stats['zone_dist']:
        
        if stats['total_serves'] == stats['total_errs']:
            perc = 0
        else:
            perc = (stats['zone_dist'][zone]  / (stats['total_serves'] - stats['total_errs'])) * 100
        
        stats['zone_dist'][zone] = f'{perc:.0f}'

    for outcome in stats['outcome_dist']:
        stats['outcome_dist'][outcome] = f'{stats['outcome_dist'][outcome] / stats['total_serves'] * 100:.0f}'
            
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

def generate_pdf_report(serves: dict, serve_types: dict, output_filename: str):

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
    
    
    # Append the Title to the elements
    elements.append(Paragraph("SERVES REPORT", title_style))
    

    # Add the description of the zones
    elements.append(get_legend_table())
    elements.append(Spacer(1, 0.5*cm))


    # Draw a diagram of the court and the 9 zones to illustrate the concept
    court_drawing = draw_court_diagram()

    description_text = """
    The image to the left serves as an illustration of the 9 defined serve zones. The red dots symbolize the receivers.
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
    header_row = ['Plyr', 'Zone Distribution in %', 'Outcome Distribution']
    
    col_widths = [1.5*cm, 8*cm, 7.5*cm]
    current_table_data = [header_row] 
    
    current_table_style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTBOLD', (0, 0), (-1, 0), True),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]

    sorted_players = sorted(serves.keys(), key = lambda x: int(x))
    row_idx = 1

    for player_num in sorted_players:
        already_added_serve_type = False

        player_stats = calculate_stats(serves[player_num])
        
        most_serves_zones = [zone for zone in player_stats['zone_dist'] if player_stats['zone_dist'][zone] == max(player_stats['zone_dist'].values())]

        # Zone Distribution, i.e. court diagram
        zone_dist = draw_court_diagram(data=player_stats['zone_dist'])

        # Outcomes
        outcome_dist = f'Type: {translation[serve_types[player_num]]}\n\
Total serves:  {player_stats['total_serves']}\n\
aces {player_stats['outcome_dist']['1']}% / came back {player_stats['outcome_dist']['2']}% / err {player_stats['outcome_dist']['4']}%'

        summary_row = [f"#{player_num}", zone_dist, outcome_dist]

        current_table_data.append(summary_row)
        current_table_style.append(('FONTBOLD', (0, row_idx), (0, row_idx), True))
        row_idx += 1

        current_table_style.append(('LINEBELOW', (0, row_idx-1), (-1, row_idx-1), 0.5, colors.lightgrey))

    if len(current_table_data) > 1:
        t = Table(current_table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle(current_table_style))
        elements.append(t)

    doc.build(elements)
    print(f"PDF generated successfully: {output_filename}")

if __name__ == "__main__":

    # Determine paths
    input_path_1 = os.path.join('.', 'analysis', 'serves.json')
    input_path_2 = os.path.join('.', 'analysis', 'serve_types.json')
    output_path = os.path.join('.', 'reports', 'serves_report.pdf')

    if not os.path.exists(input_path_1) or not os.path.exists(input_path_2):
            print("Error: Input files not found.")
    else:
        with open(input_path_1, 'r', encoding='utf-8') as file:
            serves_data = json.load(file)

        with open(input_path_2, 'r', encoding='utf-8') as file:
            serve_types = json.load(file)

        generate_pdf_report(serves_data, serve_types, output_filename=output_path)