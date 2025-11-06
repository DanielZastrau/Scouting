import argparse
import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Any

def visualize_reception_sets(K1: dict):
    """1 file per player
    top level: player nubmer + dict
    second level: setter position + dict
    third level: reception quality + dict
    fourth level: pos + dict
    fifth level: set + count
    """

    # --- 1. Setup the Plot ---
    try:
        keys_for_files = sorted(K1.keys())
        if not keys_for_files:
            print("Error: Data dictionary is empty.")
            return
    except Exception as e:
        print(f"Error sorting row keys: {e}")
        return

    for player_number in keys_for_files:

        # row keys
        row_keys = ["1", "2", "3", "4", "5", "6"]
        col_keys = ['1', '2', '3']
        
        num_rows = 6
        num_cols = 3
        
        # Define spacing for each grid cell
        # (Square + text area)
        cell_width = 4.0
        cell_height = 2.0
        
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
        square_size = 1.5

        # --- 3. Iterate and Draw ---
        for row_idx, rotation in enumerate(row_keys):
            
            # Calculate y_center for the current row
            # (0,0) is bottom-left, so we reverse the row_idx
            y_center = (num_rows - 1 - row_idx) * cell_height
            
            # Draw Row Label
            ax.text(-1.5, y_center, f"rotation: {rotation}", ha='center', va='center', fontsize=12, fontweight='bold')
            
            for col_idx, reception_quality in enumerate(col_keys):
                
                # Calculate x_center for the current column
                x_center = col_idx * cell_width

                # --- Draw Column Label (for first row only) ---
                map = {"1": 'perfect', '2': 'mehh', '3': 'bad'}
                if row_idx == 0:
                    ax.text(x_center, fig_height - 0.5, f"Reception Quality: {reception_quality}", ha='center', va='center', fontsize=12, fontweight='bold')
                

                # --- Draw the Square ---
                bottom_left_x = x_center - (square_size / 2)
                bottom_left_y = y_center - (square_size / 2)
                
                square = patches.Rectangle((bottom_left_x, bottom_left_y), square_size, square_size, edgecolor='black', facecolor='none', linewidth=1)
                ax.add_patch(square)

                # --- Draw 3m line
                x_start = x_center - (square_size / 2)
                x_end = x_center + (square_size / 2)
                y = y_center - (square_size / 2) + (square_size / 3)

                ax.plot([x_start, x_end], [y, y], color="black", linewidth=0.7)

                # --- Draw Numbers in Court for set counts ---

                points = {
                    "1": (x_center - square_size  / 2 + square_size / 6, y_center + square_size / 4),
                    "2": (x_center - square_size  / 2 + square_size / 6, y_center - square_size / 4),
                    "3": (x_center, y_center - square_size / 4),
                    "4": (x_center + square_size / 2 - square_size / 6, y_center - square_size / 4),
                    "5": (x_center + square_size / 2 - square_size / 6, y_center + square_size / 4),
                    "6": (x_center, y_center + square_size / 4)
                }

                sets = K1[player_number][rotation][reception_quality]

                for i, e in sets.items():
                    text_to_display = f'{sum(e.values())}'
                    
                    # Draw text
                    ax.text(points[i][0], points[i][1], text_to_display, ha='left', va='center', fontsize=9)

                # Draw text to the right for set types of middle
                text_x = x_center + square_size / 2 + 0.5
                text_y = y_center + square_size / 2

                map = {"1": 'fast', "2": "push", "3": "shoot", "4": "back fast"}

                
                ax.text(text_x, text_y, 'middle sets', ha="left", va="center", fontsize=9)
                for i, e in sets["3"].items():
                    text_to_display = f'{map[i]}: {e}'

                    ax.text(text_x, text_y - float(i) * square_size / 5, text_to_display, ha="left", va="center", fontsize=9)

        # --- 4. Save and Show ---
        try:
            plt.savefig(os.path.join('.', f'Reception_Setter_{player_number}'), bbox_inches='tight', dpi=150)
            print(f"Grid image saved to {os.path.join('.', f'Reception_Setter_{player_number}')}")
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
    visualize_reception_sets(K1)

