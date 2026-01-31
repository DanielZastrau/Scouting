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

def draw_court_diagram():
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
        2: (width / 8, height / 4),
        3: (2 * width / 8, height / 4),
        4: (3 * width / 8, height / 4),
        5: (4 * width / 8, height / 4),
        6: (5 * width / 8, height / 4),
        7: (6 * width / 8, height / 4),
        8: (7 * width / 8, height / 4),
        9: (3 * width / 4, 5 * height / 6)
    }

    # Add Labels 1-9
    for z_num, (zx, zy) in zone_coords.items():
        d.add(String(zx, zy - 3, str(z_num), textAnchor='middle', fontName='Helvetica-Bold', fontSize=12, fillColor=colors.gray))

    # Add Requested Dots (Zones 3, 5, 7)
    target_zones = [3, 5, 7]
    for z in target_zones:
        cx, cy = zone_coords[z]
        d.add(Circle(cx, cy + 10, 4, fillColor=colors.red, strokeColor=colors.black, strokeWidth=0.5))

    return d

def calculate_stats(zones: dict) -> dict:
    """
    Aggregates stats for a single player.
    """
    stats = {
        'total_serves': 0, 'aces': 0, 'errors': 0, 'zone_breakdown': {}
    }
    for i in range(1, 10):
        stats['zone_breakdown'][str(i)] = {'total': 0, 'detail': ''}

    for zone, outcomes in zones.items():
        zone_total = sum(outcomes.values())

        stats['total_serves'] += zone_total
        stats['aces'] += outcomes.get('1', 0)
        stats['errors'] += outcomes.get('4', 0)

        if zone in stats['zone_breakdown']:

            stats['zone_breakdown'][zone]['total'] = zone_total

            aces = outcomes.get('1', 0)
            errs = outcomes.get('4', 0)

            stats['zone_breakdown'][zone]['raw_aces'] = aces 
            stats['zone_breakdown'][zone]['detail'] = f"{zone_total}Total/{aces}Aces/{errs}Errors"
            
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

    doc = SimpleDocTemplate(
        output_filename, 
        pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm, 
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()


    table_para_style = ParagraphStyle(
        'TablePara',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10 
    )
    
    # --- Title ---
    title_style = ParagraphStyle(
        'CustomTitle', 
        parent=styles['Heading1'], 
        alignment=1, 
        fontSize=16, 
        spaceAfter=10
    )
    elements.append(Paragraph("SERVES REPORT", title_style))
    
    # --- Legend ---
    elements.append(get_legend_table())
    elements.append(Spacer(1, 0.5*cm))

    # --- Court Diagram & Description ---
    
    # 1. Get the Drawing
    court_drawing = draw_court_diagram()
    
    # 2. Define the Template Description Text
    # You can use standard ReportLab XML tags here (<b>, <i>, <br/>, <font color>)
    description_text = """
    The image to the left serves as an illustration of the 9 defined serve zones. The red dots symbolize the receivers.
    """
    
    desc_para = Paragraph(description_text, styles['Normal'])

    # 3. Layout: Table with 2 columns (Drawing | Text)
    # Court Drawing is 200 pts wide (~7cm). We'll give it 7.5cm space.
    # Text gets the remaining space (approx 9cm).
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
    header_row = ['Plyr', 'Tot', 'Ace', 'Err', 'Zone Details (Total/Ace/Err)']
    
    col_widths = [1.5*cm, 1.2*cm, 1.2*cm, 1.2*cm, 11*cm]
    current_table_data = [header_row] 
    
    current_table_style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTBOLD', (0, 0), (-1, 0), True),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]

    sorted_players = sorted(serves.keys())
    row_idx = 1 

    for player_num in sorted_players:
        already_added_serve_type = False 

        p_stats = calculate_stats(serves[player_num])
        
        # --- Identify Max Zones ---
        max_aces = -1
        max_ace_zone = None
        max_serves = -1
        max_serve_zone = None

        for z, data in p_stats['zone_breakdown'].items():

            if data.get('raw_aces', 0) > max_aces:
                max_aces = data.get('raw_aces', 0)
                max_ace_zone = z
            
            if data['total'] > max_serves:
                max_serves = data['total']
                max_serve_zone = z
                
        if max_aces == 0:
            max_ace_zone = None
        
        if max_serves == 0:
            max_serve_zone = None

        # 1. Summary Row
        summary_row = [f"#{player_num}",  p_stats['total_serves'],  p_stats['aces'],  p_stats['errors'],  "" ]

        current_table_data.append(summary_row)
        current_table_style.append(('FONTBOLD', (0, row_idx), (0, row_idx), True))
        row_idx += 1
        

        # 2. Detail Row(s)
        active_zones = [z for z, data in p_stats['zone_breakdown'].items()]
        
        if not active_zones:
            pass 
        else:
            chunk_size = 3
            for i in range(0, len(active_zones), chunk_size):
                chunk = active_zones[i:i+chunk_size]
                detail_strs = []
                
                for z in chunk:
                    txt = f"Z{z}:{p_stats['zone_breakdown'][z]['detail']}"
                    
                    font_size = 6
                    if z == max_ace_zone:
                        txt = f"<font color='red' size='{font_size}'>{txt}</font>"
                    elif z == max_serve_zone:
                        txt = f"<font color='blue' size='{font_size}'>{txt}</font>"
                    else:
                        txt = f"<font color='black' size='{font_size}'>{txt}</font>"
                    
                    detail_strs.append(txt)
                
                row_xml = " | ".join(detail_strs)
                para = Paragraph(row_xml, table_para_style)
                
                if already_added_serve_type:
                    first_elem = ''
                else:
                    first_elem = translation.get(serve_types.get(str(player_num), ''), 'Unknown')
                    already_added_serve_type = True

                current_table_data.append([first_elem, "", "", "", para])
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

    try:
        if not os.path.exists(input_path_1) or not os.path.exists(input_path_2):
             print("Error: Input files not found.")
        else:
            with open(input_path_1, 'r', encoding='utf-8') as file:
                serves_data = json.load(file)

            with open(input_path_2, 'r', encoding='utf-8') as file:
                serve_types = json.load(file)

            generate_pdf_report(serves_data, serve_types, output_filename=output_path)
    except Exception as e:
        print(f"Error: {e}")