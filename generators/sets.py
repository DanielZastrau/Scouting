import json
import os
import argparse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak

def aggregate_counts(set_type_data):
    """
    Helper function to sum values in the 4th level dict (ignoring set type).
    e.g., {"1": 0, "2": 1, ...} -> returns 1
    """
    return sum(set_type_data.values())

def create_setter_report(data, output_filename: str, complex: str):

    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Title Style
    title_style = ParagraphStyle(
        'SetterTitle',
        parent=styles['Heading1'],
        alignment=1, # Center
        fontSize=16,
        spaceAfter=12
    )

    # Sort players numerically
    player_ids = sorted(data.keys(), key=lambda x: int(x))

    for player_id in player_ids:
        player_data = data[player_id]

        # 1. Add Player Title
        elements.append(Paragraph(f"Setter Distribution: Player #{player_id}  --  Complex {complex}", title_style))
        elements.append(Spacer(1, 0.5*cm))

        # 2. Prepare Main Table Data
        # Header Row - Added "Total"
        main_table_data = [[
            "Rotation", 
            "Position Distribution\ntop row 1-6-5", 
            "Setter\nDump",
            "Total\nSets"
        ]]

        # Sort rotations numerically (0, 1, 2...)
        rotations = sorted(player_data.keys(), key=lambda x: int(x))

        for rot in rotations:
            destinations = player_data[rot]
            
            # Helper to safely get counts
            def get_cnt(p):
                key = str(p)
                return aggregate_counts(destinations[key]) if key in destinations else 0

            # --- Construct the Nested Grid (2x3) ---
            # Also calculate total for positions 1-6
            
            p1, p6, p5 = get_cnt(1), get_cnt(6), get_cnt(5)
            p2, p3, p4 = get_cnt(2), get_cnt(3), get_cnt(4)
            
            grid_data = [
                [p1, p6, p5], # Top Row
                [p2, p3, p4]  # Bottom Row
            ]

            # Create the Nested Table Object
            nested_t = Table(grid_data, colWidths=[1.2*cm]*3, rowHeights=[0.8*cm]*2)
            
            # Style the Nested Table (The Grid)
            nested_t.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke) 
            ]))

            # --- Dump Count ---
            dump_count = get_cnt(7)

            # --- Total Count ---
            total_count = p1 + p6 + p5 + p2 + p3 + p4 + dump_count

            # Add Row to Main Table
            main_table_data.append([f"Rot {int(rot) + 1}", nested_t, dump_count, total_count])

        # 3. Create and Style Main Table
        # Columns: Rotation, Grid, Dump, Total
        # Adjusted widths to fit A4
        t = Table(main_table_data, colWidths=[2.5*cm, 6.0*cm, 2.0*cm, 2.0*cm])

        t.setStyle(TableStyle([
            # Header Styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # Data Rows Styling
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'), # Vertically center the nested table
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            
            # Dump Column Styling (Light Grey)
            ('BACKGROUND', (2, 1), (2, -1), colors.lightgrey),
            
            # Total Column Styling (Bold + Slightly darker grey or distinctive)
            ('BACKGROUND', (3, 1), (3, -1), colors.gainsboro),
            ('FONTSIZE', (3, 1), (3, -1), 12),
        ]))

        elements.append(t)
        elements.append(PageBreak())

    # Build the PDF
    doc.build(elements)
    print(f"PDF generated successfully: {output_filename}")


if __name__ == "__main__":
    
    # Process both K1 and K2 files
    for complex in ['K1', 'K2']:

        input_path = os.path.join('.', 'analysis', f'sets{complex}.json')
        output_path = os.path.join('.', 'reports', f'sets{complex}_report.pdf')

        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                sets_data = json.load(file)
            
            create_setter_report(sets_data, output_path, complex)

        except FileNotFoundError:
            print(f"Skipping {complex_type}: File not found at {input_path}")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {input_path}")
        except Exception as e:
            print(f"An unexpected error occurred processing {complex_type}: {e}")