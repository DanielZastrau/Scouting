import argparse
import os
import io
from pypdf import PdfWriter, PdfReader

# ReportLab imports for generating the TOC page
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Define the order priority based on substrings
PRIORITY_ORDER = [
    'serves_report',
    'receptions_report',
    'setter_report',
    'setter_report',
    'setter_afterReception1_report',
    'hits_report',
    'breaks_report'
    'for_oli_report'
]

translations = {
    'Setter Afterreception1 Report': 'Setter after Reception on Pos 1 Report',
    'Foroli Report': 'For Oli'
}

def get_sort_key(filename):
    """
    Returns a tuple (priority_index, filename) for sorting.
    Lower priority_index means earlier in the list.
    """
    filename_lower = filename.lower()
    
    for index, keyword in enumerate(PRIORITY_ORDER):
        if keyword.lower() in filename_lower:
            return (index, filename_lower)
            
    return (len(PRIORITY_ORDER), filename_lower)

def create_toc_pdf(toc_entries, output_path):
    """
    Generates a single-page PDF containing the Table of Contents.
    toc_entries: List of tuples (Title, Page Number)
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'TOCTitle', parent=styles['Heading1'], alignment=1, spaceAfter=20
    )
    elements.append(Paragraph("Table of Contents", title_style))
    elements.append(Spacer(1, 1*cm))

    # Build Table Data
    # Headers
    table_data = [["Report Name", "Start Page"]]
    
    for name, page in toc_entries:
        # Clean up filename for display (e.g., "serves_report.pdf" -> "Serves Report")
        display_name = os.path.splitext(name)[0].replace('_', ' ').replace('-', ' ').title()

        if display_name in translations:
            display_name = translations[display_name]

        table_data.append([display_name, str(page)])

    # Styling the table
    t = Table(table_data, colWidths=[12*cm, 3*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),      # Align names left
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),    # Align page nums center
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))

    elements.append(t)
    doc.build(elements)

def merge_pdfs(folder_path, output_filename):
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    # 1. Gather and Sort Files
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in '{folder_path}'.")
        return

    pdf_files.sort(key=get_sort_key)
    
    # 2. Calculate Page Offsets for TOC
    print("Analyzing files for Table of Contents...")
    
    toc_entries = []
    # Start on Page 2 (Assuming TOC takes exactly 1 page)
    # If TOC might be longer, we'd need to generate it first to check length, 
    # but for 5-10 reports, 1 page is safe.
    current_page = 2 
    
    file_paths_ordered = []

    for filename in pdf_files:
        file_path = os.path.join(folder_path, filename)
        file_paths_ordered.append(file_path)
        
        try:
            # Open reader to count pages
            reader = PdfReader(file_path)
            num_pages = len(reader.pages)
            
            # Add entry
            toc_entries.append((filename, current_page))
            
            # Increment current page for the next file
            current_page += num_pages
            
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return

    # 3. Generate Temporary TOC PDF
    temp_toc_filename = "temp_toc_page.pdf"
    try:
        create_toc_pdf(toc_entries, temp_toc_filename)
        print("Table of Contents generated.")
    except Exception as e:
        print(f"Error generating TOC: {e}")
        return

    # 4. Merge Everything
    merger = PdfWriter()
    print(f"Merging {len(pdf_files)} files...")

    try:
        # Add TOC first
        merger.append(temp_toc_filename)
        
        # Add Reports
        for file_path in file_paths_ordered:
            print(f"  Appending: {os.path.basename(file_path)}")
            merger.append(file_path)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)

        # Write final
        with open(output_filename, "wb") as f_out:
            merger.write(f_out)
        
        print(f"\nSuccess! Final report with TOC saved to: {output_filename}")

    except Exception as e:
        print(f"An error occurred during merging: {e}")
    finally:
        merger.close()
        # Clean up temp file
        if os.path.exists(temp_toc_filename):
            os.remove(temp_toc_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge PDFs with a Table of Contents.")

    parser.add_argument(
        '--output', 
        required=True, 
        help='Filename for the output merged PDF.'
    )

    args = parser.parse_args()
    
    # Using raw string for path to avoid escape char issues in Windows
    input_folder = r'.\reports'
    output_file = os.path.join(r'final_reports', args.output)

    merge_pdfs(input_folder, output_file)