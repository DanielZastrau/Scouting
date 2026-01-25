import argparse
import json
from typing import Dict, List, Any

# ReportLab Imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

# Define type hints
OuterDict1 = Dict[int, Dict[int, int]]

def calculate_stats(zones: dict) -> dict:
    """
    Aggregates stats for a single player.
    """
    stats = {
        'total_serves': 0, 'aces': 0, 'errors': 0, 'zone_breakdown': {}
    }
    for i in range(9):
        stats['zone_breakdown'][str(i)] = {'total': 0, 'detail': ''}

    for zone, outcomes in zones.items():
        zone_total = sum(outcomes.values())
        stats['total_serves'] += zone_total
        stats['aces'] += outcomes.get('1', 0)
        
        if zone == '0':
            stats['errors'] += zone_total
        else:
            stats['errors'] += outcomes.get('4', 0)

        if zone in stats['zone_breakdown']:
            stats['zone_breakdown'][zone]['total'] = zone_total
            aces = outcomes.get('1', 0)
            errs = outcomes.get('4', 0) if zone != '0' else zone_total
            # Removed 'Total' suffix to save space, format is T/A/E
            stats['zone_breakdown'][zone]['raw_aces'] = aces # Store for comparison
            stats['zone_breakdown'][zone]['detail'] = f"{zone_total}Total/{aces}Aces/{errs}Errors"
            
    return stats

def get_legend_table():
    """Returns the Legend as a formatted Table element."""
    data = [
        ["ZONE KEY (0-8)"],
        ["0: Frontcourt Left Half  | 1: Left Sideline   | 2: on Pos 5             "],
        ["3: Gap 5-6               | 4: Pos 6           | 5: Gap 6-1              "],
        ["6: on Pos 1              | 7: Right Sideline  | 8: Frontcourt Right Half"],
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
        # Color the legend text roughly to match logic
        ('TEXTCOLOR', (0, 4), (0, 4), colors.darkgrey), 
    ])
    
    t = Table(data, colWidths=[16*cm])
    t.setStyle(style)
    return t

def generate_pdf_report(serves: OuterDict1, output_filename: str):
    doc = SimpleDocTemplate(
        output_filename, 
        pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm, 
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    # Create a custom style for the table text that allows inline XML tags
    table_para_style = ParagraphStyle(
        'TablePara',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10 # Line spacing
    )
    
    # --- Title ---
    title_style = ParagraphStyle(
        'CustomTitle', 
        parent=styles['Heading1'], 
        alignment=1, # Center 
        fontSize=16, 
        spaceAfter=10
    )
    elements.append(Paragraph("SERVES REPORT", title_style))
    
    # --- Legend ---
    elements.append(get_legend_table())
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
        p_stats = calculate_stats(serves[player_num])
        
        # --- Identify Max Zones ---
        max_aces = -1
        max_ace_zone = None
        max_serves = -1
        max_serve_zone = None

        for z, data in p_stats['zone_breakdown'].items():
            # Check Max Aces
            if data.get('raw_aces', 0) > max_aces:
                max_aces = data.get('raw_aces', 0)
                max_ace_zone = z
            # Check Max Serves
            if data['total'] > max_serves:
                max_serves = data['total']
                max_serve_zone = z
                
        # Handle cases where counts are 0 (optional: don't highlight if 0)
        if max_aces == 0: max_ace_zone = None
        if max_serves == 0: max_serve_zone = None

        # 1. Summary Row
        summary_row = [
            f"#{player_num}", 
            p_stats['total_serves'], 
            p_stats['aces'], 
            p_stats['errors'], 
            "" 
        ]
        current_table_data.append(summary_row)
        current_table_style.append(('FONTBOLD', (0, row_idx), (0, row_idx), True))
        row_idx += 1
        
        # 2. Detail Row(s)
        active_zones = [z for z, data in p_stats['zone_breakdown'].items()]
        
        if not active_zones:
            # ... (No serves logic) ...
            pass 
        else:
            chunk_size = 3
            for i in range(0, len(active_zones), chunk_size):
                chunk = active_zones[i:i+chunk_size]
                detail_strs = []
                
                for z in chunk:
                    # Base string
                    txt = f"Z{z}:{p_stats['zone_breakdown'][z]['detail']}"
                    
                    # --- APPLY COLORS ---
                    # Priority: Aces (Red) > Serves (Blue) if they happen to be the same zone
                    font_size = 6
                    if z == max_ace_zone:
                        txt = f"<font color='red' size='{font_size}'>{txt}</font>"
                    elif z == max_serve_zone:
                        txt = f"<font color='blue' size='{font_size}'>{txt}</font>"
                    else:
                        txt = f"<font color='black' size='{font_size}'>{txt}</font>"
                    
                    detail_strs.append(txt)
                
                # Join with separator
                row_xml = " | ".join(detail_strs)
                
                # Wrap in Paragraph to render the XML tags
                para = Paragraph(row_xml, table_para_style)
                
                current_table_data.append(["", "", "", "", para])
                
                # Note: We do NOT append TEXTCOLOR style here, as the Paragraph handles it internally.
                row_idx += 1

        # Add a divider line
        current_table_style.append(('LINEBELOW', (0, row_idx-1), (-1, row_idx-1), 0.5, colors.lightgrey))

    # --- Flush data ---
    if len(current_table_data) > 1:
        t = Table(current_table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle(current_table_style))
        elements.append(t)

    doc.build(elements)
    print(f"PDF Report saved to {output_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', required=True)
    args = parser.parse_args()

    loaded_dicts = []
    try:
        with open(args.filename, 'r') as f:
            for line in f:
                if line.strip():
                    loaded_dicts.append(json.loads(line.strip()))
        
        if len(loaded_dicts) < 5:
            print("Error: Input file must contain at least 5 JSON lines.")
        else:
            serves_data = loaded_dicts[2]
            if serves_data:
                generate_pdf_report(serves_data, output_filename='serves_report.pdf')
            else:
                print("Warning: 'serves' dictionary is empty.")

    except Exception as e:
        print(f"Error processing file: {e}")