import argparse
import os
from pypdf import PdfWriter

# Define the order priority based on substrings
PRIORITY_ORDER = [
    'serves',
    'receptions',
    'setsK1',
    'setsK2',
    'hits'
]

def get_sort_key(filename):
    """
    Returns a tuple (priority_index, filename) for sorting.
    Lower priority_index means earlier in the list.
    """
    filename_lower = filename.lower()
    
    for index, keyword in enumerate(PRIORITY_ORDER):
        # We check if the keyword (e.g., 'hits') is inside the filename
        if keyword.lower() in filename_lower:
            return (index, filename_lower)
            
    # If not found in priority list, place at the end (len(PRIORITY_ORDER))
    return (len(PRIORITY_ORDER), filename_lower)

def merge_pdfs(folder_path, output_filename):
    """
    Merges PDF files in the specified folder into a single PDF,
    sorted by a custom priority order.
    """
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    # Get all PDF files
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"No PDF files found in '{folder_path}'.")
        return

    # Apply custom sort
    pdf_files.sort(key=get_sort_key)

    merger = PdfWriter()

    print(f"Found {len(pdf_files)} PDFs. Merging in this order:")

    try:
        for filename in pdf_files:
            file_path = os.path.join(folder_path, filename)
            print(f"  [{pdf_files.index(filename) + 1}] {filename}")
            merger.append(file_path)

        # Write the merged PDF
        with open(output_filename, "wb") as f_out:
            merger.write(f_out)
        
        print(f"\nSuccess! Merged PDF saved to: {output_filename}")

    except Exception as e:
        print(f"An error occurred during merging: {e}")
    finally:
        merger.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge PDFs in a specific order (Serves > Receptions > SetsK1 > SetsK2 > Hits).")

    parser.add_argument(
        '--output', 
        required=True, 
        help='Path (including filename) for the output merged PDF.'
    )

    args = parser.parse_args()

    merge_pdfs('.\\reports', f'final_reports\\{args.output}')