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


def draw_squares_with_circles(reception: DataDict, output_filename: str = 'circle_plot.png'):
    """
    Draws a grid of squares based on a nested dictionary.
    
    Each top-level key is a row.
    Each row has 3 columns (1, 6, 5).
    Each square contains 3 concentric, colored half-circles and 3
    horizontal lines pointing to text labels.
    """
    
    # --- 1. Setup the Plot ---
    try:
        sorted_row_keys = sorted(reception.keys())
        if not sorted_row_keys:
            print("Error: Data dictionary is empty.")
            return
    except Exception as e:
        print(f"Error sorting row keys: {e}")
        return

    # Define column order as requested
    col_keys = ["none", "1", "6", "5"]
    
    num_rows = len(sorted_row_keys)
    num_cols = len(col_keys) + 1
    
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
    
    modifier_first_column = 1.5

    # --- 3. Iterate and Draw ---
    for row_idx, number_of_player in enumerate(sorted_row_keys):
        
        # Calculate y_center for the current row
        # (0,0) is bottom-left, so we reverse the row_idx
        y_center = (num_rows - 1 - row_idx) * cell_height
        
        # Draw Row Label
        ax.text(-1.0, y_center, f"#{number_of_player}", ha='center', va='center', fontsize=12, fontweight='bold')
        
        for col_idx, col_key in enumerate(col_keys):
            
            # Calculate x_center for the current column
            x_center = col_idx * cell_width

            # --- Draw Column Label (for first row only) ---
            if row_idx == 0:
                if col_idx != 0:
                    ax.text(x_center, fig_height - 0.5, f"Pos: {col_key}", ha='center', va='center', fontsize=12, fontweight='bold')
            
            # --- Draw Concentric Half-Circles ---
            if col_idx == 0:
                circle_center_x = x_center - square_size / 5
                circle_center_y = y_center - square_size / 2

                if col_idx == 0:
                    circle_center_x += modifier_first_column

                circle_colors = ['#FFB6C1', '#FFFFE0', '#90EE90'] 
            
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
                bottom_left_x = x_center - (square_size / 2) + modifier_first_column
                bottom_left_y = y_center - (square_size / 2)
                
                square = patches.Rectangle((bottom_left_x, bottom_left_y), square_size, square_size, edgecolor='black', facecolor='none', linewidth=1)
                ax.add_patch(square)

                # --- Draw 3m line
                x_start = x_center - (square_size / 2) + modifier_first_column
                x_end = x_center + (square_size / 2) + modifier_first_column
                y = y_center - (square_size / 2) + (square_size / 3)

                ax.plot([x_start, x_end], [y, y], color="black", linewidth=0.7)

            # --- Draw Lines and Text ---
            if col_idx != 0:
                text_start_x = x_center
                
                map = {0: "4", 1: "3", 2: "2", 3: "1"}
                mapp = {"1": "perfect", "2": "mehh", "3": "bad", "4": "err"}
                reception_outcomes = reception[number_of_player][col_key]

                for i in range(4):
                    text_to_display = f'{mapp[map[i]]}: {reception_outcomes.get(map[i], "N/A")}'
                    y_pos = y_center + square_size / 2 - (i * square_size / 4)
                    
                    # Draw text
                    ax.text(text_start_x, y_pos, text_to_display, ha='left', va='center', fontsize=9)

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

