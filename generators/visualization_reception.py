import argparse
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def calculate_reception_stats(player_zones: dict) -> dict:
    """
    Aggregates reception stats across all zones for a single player.
    Input format: {'ZoneID': {'1': count, '2': count, ...}, ...}
    """
    stats = {
        'total': 0,
        'perfect': 0, # Code 1
        'okay': 0,    # Code 2
        'bad': 0,     # Code 3
        'error': 0    # Code 4
    }

    # Iterate through every zone the player received in
    for zone, outcomes in player_zones.items():
        # outcomes is {'1': int, '2': int, '3': int, '4': int}
        p = outcomes.get('1', 0)
        o = outcomes.get('2', 0)
        b = outcomes.get('3', 0)
        e = outcomes.get('4', 0)

        stats['perfect'] += p
        stats['okay'] += o
        stats['bad'] += b
        stats['error'] += e
        stats['total'] += (p + o + b + e)

    return stats

def generate_reception_pdf(data: dict, output_filename: str):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # --- 1. Title ---
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        alignment=1, # Center
        fontSize=18,
        spaceAfter=12
    )
    elements.append(Paragraph("Reception Report", title_style))
    elements.append(Spacer(1, 0.5*cm))

    # --- 2. Table Data Setup ---
    # Header Row
    headers = [
        "Player", 
        "Total", 
        "Perfect (#)", 
        "Okay (+)", 
        "Bad (-)", 
        "Error (=)"
    ]
    table_data = [headers]

    # Sort players by number (converting string key to int)
    sorted_player_keys = sorted(data.keys(), key=lambda x: int(x))

    for player_num in sorted_player_keys:
        stats = calculate_reception_stats(data[player_num])
        
        row = [
            f"#{player_num}",
            stats['total'],
            stats['perfect'],
            stats['okay'],
            stats['bad'],
            stats['error']
        ]
        table_data.append(row)

    # --- 3. Table Styling ---
    # Define column widths (Adjusted to fit A4 width)
    # Total width available approx 17cm (21 - 2*2 margins)
    col_widths = [3*cm, 2.5*cm, 2.8*cm, 2.8*cm, 2.8*cm, 2.8*cm]

    t = Table(table_data, colWidths=col_widths)

    t.setStyle(TableStyle([
        # Header Style
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        # Body Style
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        
        # Alternating Row Colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))

    elements.append(t)

    # Build PDF
    try:
        doc.build(elements)
        print(f"Success: Reception report generated at '{output_filename}'")
    except Exception as e:
        print(f"Error building PDF: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', help='Path to the JSON analysis file', required=True)
    args = parser.parse_args()

    loaded_dicts = []
    try:
        with open(args.filename, 'r') as f:
            for line in f:
                if line.strip():
                    loaded_dicts.append(json.loads(line.strip()))
        
        # Check if we have enough lines
        if len(loaded_dicts) < 5:
            print("Error: Input file must contain at least 5 lines of JSON data.")
        else:
            # Reception data is in the 5th line (index 4)
            reception_data = loaded_dicts[4]
            generate_reception_pdf(reception_data, 'reception_report.pdf')

    except FileNotFoundError:
        print(f"Error: File '{args.filename}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{args.filename}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")