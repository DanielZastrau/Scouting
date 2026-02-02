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

def generate_pdf_report(data_k1: dict, data_k2: dict, output_filename: str):

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
    player_ids = sorted(data_k1.keys(), key=lambda x: int(x))

    for player_id in player_ids:
        player_data_k1 = data_k1[player_id]
        player_data_k2 = data_k2[player_id]


        # Add Player Title
        elements.append(Paragraph(f"Setter Distribution: Player #{player_id}", title_style))
        elements.append(Spacer(1, 0.5*cm))


        # Header Row
        main_table_data = [["Rotation", "K1 in %", "Total\nSets", "K2 in %", "Total\nSets"]]
        col_widths = [1.5*cm, 6.0*cm, 2.0*cm, 6.0*cm, 2.0*cm]


        # Add example row detailing the positions
        grid_data = [
            [1, 6, 5], # Top Row
            [2, 3, 4]  # Bottom Row
        ]
        val_map = [
            (1, 0, 0), (6, 1, 0), (5, 2, 0),
            (2, 0, 1), (3, 1, 1), (4, 2, 1)
        ]


        # Create the Nested Table Object
        nested_styles = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke) # Default background
        ]

        nested_t = Table(grid_data, colWidths=[1.2*cm]*3, rowHeights=[0.8*cm]*2)
        nested_t.setStyle(TableStyle(nested_styles))


        # Add Row to Main Table
        main_table_data.append([f"Rot -", nested_t, '-', '-', '-'])


        # Sort rotations numerically (0, 1, 2...)
        rotations = sorted(player_data_k1.keys(), key=lambda x: int(x))

        for rot in rotations:
            destinations_k1 = player_data_k1[rot]
            destinations_k2 = player_data_k2[rot]
            
            # Helper to safely get counts
            def get_count(p, data):
                key = str(p)
                return aggregate_counts(data[key]) if key in data else 0



            # Construct the Nested Grid for K1
            p1, p6, p5 = get_count(1, destinations_k1), get_count(6, destinations_k1), get_count(5, destinations_k1)
            p2, p3, p4 = get_count(2, destinations_k1), get_count(3, destinations_k1), get_count(4, destinations_k1)
            
            total_count_k1 = p1 + p6 + p5 + p2 + p3 + p4

            ps = [p1, p2, p3, p4, p5, p6]

            # Convert to percentages
            if total_count_k1 != 0:
                ps = list(map(lambda x: x / total_count_k1 * 100, ps))
                p1, p2, p3, p4, p5, p6 = ps

            grid_data = [
                [f'{p1:.0f}', f'{p6:.0f}', f'{p5:.0f}'], # Top Row
                [f'{p2:.0f}', f'{p3:.0f}', f'{p4:.0f}']  # Bottom Row
            ]

            # --- Logic to Highlight Max Value ---
            # Map values to their (col, row) coordinates in the nested table
            # Top Row (Row 0): p1(0,0), p6(1,0), p5(2,0)
            # Bottom Row (Row 1): p2(0,1), p3(1,1), p4(2,1)
            val_map = [
                (p1, 0, 0), (p6, 1, 0), (p5, 2, 0),
                (p2, 0, 1), (p3, 1, 1), (p4, 2, 1)
            ]

            # Find maximum value
            max_val = max(v for v, c, r in val_map)

            # Base Nested Table Styles
            nested_styles = [
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke) # Default background
            ]

            # Apply Highlight if max > 0
            if max_val > 0:
                for val, col, row in val_map:
                    if val == max_val:
                        # Append style to override default background for this cell
                        nested_styles.append(('BACKGROUND', (col, row), (col, row), colors.yellow))

            # Create the Nested Table Object
            nested_t_k1 = Table(grid_data, colWidths=[1.2*cm]*3, rowHeights=[0.8*cm]*2)
            nested_t_k1.setStyle(TableStyle(nested_styles))

            
            
            # Construct the Nested Grid for K2
            p1, p6, p5 = get_count(1, destinations_k2), get_count(6, destinations_k2), get_count(5, destinations_k2)
            p2, p3, p4 = get_count(2, destinations_k2), get_count(3, destinations_k2), get_count(4, destinations_k2)
            
            total_count_k2 = p1 + p6 + p5 + p2 + p3 + p4

            ps = [p1, p2, p3, p4, p5, p6]

            # Convert to percentages
            if total_count_k2 != 0:
                ps = list(map(lambda x: x / total_count_k2 * 100, ps))
                p1, p2, p3, p4, p5, p6 = ps

            grid_data = [
                [f'{p1:.0f}', f'{p6:.0f}', f'{p5:.0f}'], # Top Row
                [f'{p2:.0f}', f'{p3:.0f}', f'{p4:.0f}']  # Bottom Row
            ]

            # --- Logic to Highlight Max Value ---
            # Map values to their (col, row) coordinates in the nested table
            # Top Row (Row 0): p1(0,0), p6(1,0), p5(2,0)
            # Bottom Row (Row 1): p2(0,1), p3(1,1), p4(2,1)
            val_map = [
                (p1, 0, 0), (p6, 1, 0), (p5, 2, 0),
                (p2, 0, 1), (p3, 1, 1), (p4, 2, 1)
            ]

            # Find maximum value
            max_val = max(v for v, c, r in val_map)

            # Base Nested Table Styles
            nested_styles = [
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke) # Default background
            ]

            # Apply Highlight if max > 0
            if max_val > 0:
                for val, col, row in val_map:
                    if val == max_val:
                        # Append style to override default background for this cell
                        nested_styles.append(('BACKGROUND', (col, row), (col, row), colors.yellow))

            # Create the Nested Table Object
            nested_t_k2 = Table(grid_data, colWidths=[1.2*cm]*3, rowHeights=[0.8*cm]*2)
            nested_t_k2.setStyle(TableStyle(nested_styles))



            # Add Row to Main Table
            main_table_data.append([f"Rot {int(rot) + 1}", nested_t_k1, total_count_k1, nested_t_k2, total_count_k2])



        # 3. Create and Style Main Table
        t = Table(main_table_data, colWidths=col_widths)

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
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            
            # Dump Column Styling
            ('BACKGROUND', (2, 1), (2, -1), colors.lightgrey),
            
            # Total Column Styling
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

    input_path_1 = os.path.join('.', 'analysis', f'setsK1.json')
    input_path_2 = os.path.join('.', 'analysis', f'setsK2.json')
    output_path = os.path.join('.', 'reports', f'setter_report.pdf')

    if not os.path.exists(input_path_1) or not os.path.exists(input_path_2):
            print("Error: Input files not found.")
    else:
        with open(input_path_1, 'r', encoding='utf-8') as file:
            k1 = json.load(file)

        with open(input_path_2, 'r', encoding='utf-8') as file:
            k2 = json.load(file)

        generate_pdf_report(k1, k2, output_filename=output_path)