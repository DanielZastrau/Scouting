import argparse
import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Any

# Define type hints for clarity
# This is the assumed data structure to meet the requirement
# for 3 text labels per square.
# { row_key: { col_key: { circle_key: "text", ... }, ... }, ... }
CircleData = Dict[int, str]
ColumnData = Dict[int, CircleData]
DataDict = Dict[int, ColumnData]


def draw_squares_with_circles(data: DataDict, output_filename: str = 'circle_plot.png'):
    """
    Draws a grid of squares based on a nested dictionary.
    
    Each top-level key is a row.
    Each row has 3 columns (1, 6, 5).
    Each square contains 3 concentric, colored half-circles and 3
    horizontal lines pointing to text labels.
    """
    
    # --- 1. Setup the Plot ---
    try:
        sorted_row_keys = sorted(data.keys())
        if not sorted_row_keys:
            print("Error: Data dictionary is empty.")
            return
    except Exception as e:
        print(f"Error sorting row keys: {e}")
        return

    # Define column order as requested
    col_keys = [1, 6, 5]
    
    num_rows = len(sorted_row_keys)
    num_cols = len(col_keys)
    
    # Define spacing for each grid cell
    # (Square + text area)
    cell_width = 3.0
    cell_height = 1.5
    
    # Calculate total figure size
    fig_width = num_cols * cell_width
    fig_height = num_rows * cell_height
    
    fig, ax = plt.subplots(1, figsize=(fig_width, fig_height + 1))
    ax.set_aspect('equal')

    # Set plot limits, adding padding
    ax.set_xlim(-1.5, fig_width - 1)
    ax.set_ylim(-1, fig_height)
    ax.axis('off')

    # --- 2. Define Layout and Styling ---
    square_size = 1.0
    # Radii for the 3 concentric circles
    radii = [0.75, 0.45, 0.25] # Large, Medium, Small
    text_y_offsets = [0.75, 0.45, 0.25]
    
    # --- 3. Iterate and Draw ---
    for row_idx, row_key in enumerate(sorted_row_keys):
        
        # Calculate y_center for the current row
        # (0,0) is bottom-left, so we reverse the row_idx
        y_center = (num_rows - 1 - row_idx) * cell_height
        
        # Draw Row Label
        ax.text(-1.0, y_center, f"#{row_key}", ha='center', va='center', 
                fontsize=12, fontweight='bold')
        
        for col_idx, col_key in enumerate(col_keys):
            
            # Calculate x_center for the current column
            x_center = col_idx * cell_width
            
            # --- Draw Column Label (for first row only) ---
            if row_idx == 0:
                ax.text(x_center, fig_height - 0.5, f"Pos: {col_key}", ha='center', va='center', fontsize=12, fontweight='bold')
            
            # Check if data exists for this cell
            if col_key not in data.get(row_key, {}):
                print(f"Warning: No data for row {row_key}, col {col_key}. Skipping.")
                continue
                
            circle_data = data[row_key][col_key]
            
            # --- Draw Concentric Half-Circles ---
            circle_center_x = x_center - square_size / 5
            circle_center_y = y_center - square_size / 2

            circle_colors = ['#FFB6C1', '#FFFFE0', '#90EE90'] 
            
            # radii = [0.4, 0.3, 0.2] # Large, Medium, Small
            for i, r in enumerate(radii):
                color = circle_colors[i]
                
                # FIX: Use Wedge instead of Arc for a fillable half-circle.
                # theta1=0, theta2=180 is the top half.
                wedge = patches.Wedge(
                    (circle_center_x, circle_center_y), r=r, theta1=0, theta2=180,
                    edgecolor='black', facecolor=color, fill=True, linewidth=0.8
                )
                ax.add_patch(wedge)

            # --- Draw the Square ---
            bottom_left_x = x_center - (square_size / 2)
            bottom_left_y = y_center - (square_size / 2)
            
            square = patches.Rectangle((bottom_left_x, bottom_left_y), square_size, square_size, edgecolor='black', facecolor='none', linewidth=1)
            ax.add_patch(square)

            # --- Draw Lines and Text ---
            line_start_x = circle_center_x
            line_end_x = line_start_x + square_size
            text_start_x = line_end_x + 0.2
            
            # Expects circle_data to have keys 1, 2, 3
            for i in range(3):
                circle_key = i + 1
                text_to_display = circle_data.get(circle_key, "N/A")
                y_pos = y_center - square_size / 2 + text_y_offsets[i]
                
                # Draw horizontal line
                ax.plot([line_start_x, line_end_x], [y_pos, y_pos], 
                        color='gray', linewidth=1)
                
                # Draw text
                ax.text(text_start_x, y_pos, text_to_display, 
                        ha='left', va='center', fontsize=9)

    # --- 4. Save and Show ---
    try:
        plt.savefig(output_filename, bbox_inches='tight', dpi=150)
        print(f"Grid image saved to {output_filename}")
    except Exception as e:
        print(f"Error saving or showing plot: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename',)

    args = parser.parse_args()

    loaded_dicts = []
    with open(args.filename, 'r') as f:
        for line in f:
            # Strip the newline character and parse the JSON string
            loaded_dict = json.loads(line.strip())
            loaded_dicts.append(loaded_dict)

    K1, K2, serves, serve_positions, reception = loaded_dicts[0], loaded_dicts[1], loaded_dicts[2], loaded_dicts[3], loaded_dicts[4]

    # Call the function
    draw_squares_with_circles(reception, output_filename='reception.png')

