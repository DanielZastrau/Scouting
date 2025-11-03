import argparse
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, Any

# Define type hints for clarity
# dict1: { 1: {1: count, 2: count, ..., 6: count}, 2: ... }
# dict2: { 1: {1: count, 2: count, 3: count}, 2: ... }
CountDict1 = Dict[int, int]
CountDict2 = Dict[int, int]
OuterDict1 = Dict[int, CountDict1]
OuterDict2 = Dict[int, CountDict2]
OuterDict3 = Dict[int, int]

def draw_stacked_squares(dict1: OuterDict1, dict2: OuterDict2, serve_positions: OuterDict3, output_filename: str = 'stacked_squares.png'):
    """
    Draws a visualization based on two dictionaries.

    For each matching top-level key, it draws:
    - A key label on the left.
    - A stack of two squares.
    - Labels from dict2 ("ace", "received", "err") above the top square.
    - Lines from the top square to 6 points in the bottom square,
      labeled with counts from dict1.
    """
    
    # --- 1. Setup the Plot ---
    # Get the keys and sort them to ensure consistent order
    try:
        sorted_keys = sorted(dict1.keys())
        if not sorted_keys:
            print("Error: Dictionaries are empty.")
            return
    except Exception as e:
        print(f"Error sorting keys: {e}")
        return

    num_keys = len(sorted_keys)
    
    # --- Define Grid Layout ---
    num_cols = 3
    num_rows = (num_keys + num_cols - 1) // num_cols
    col_width = 3.0  # Increased horizontal spacing
    row_height = 4.0 # Vertical spacing for each row
    
    # Each key group (label + squares) will take ~3 units of width
    # and ~4 units of height (squares + labels)
    plot_width = num_cols * col_width
    plot_height = num_rows * row_height
    fig_width = num_cols * 3.5  # Figure width
    fig_height = num_rows * 4.0 # Figure height
    
    fig, ax = plt.subplots(1, figsize=(fig_width, fig_height))
    ax.set_aspect('equal')

    # Set plot limits
    top_y_limit = 3.5 # Y-coordinate for the top
    ax.set_xlim(-1.5, plot_width - 1.5)
    ax.set_ylim(top_y_limit - plot_height, top_y_limit)
    ax.axis('off')

    # --- 2. Define Layout and Styling ---
    square_size = 1.0
    padding = 0.15  # Padding for text inside the bottom square
    
    # Map for dict2 labels
    dict2_labels = {1: 'ace', 2: 'received', 3: 'err'}
    
    top_row_y_center = 2.5 # Y-center for the first row

    # --- 3. Iterate and Draw per number_of_player ---
    for i, number_of_player in enumerate(sorted_keys):
        if number_of_player not in dict2:
            print(f"Warning: Key {number_of_player} from dict1 not found in dict2. Skipping.")
            continue
            
        inner_dict1 = dict1[number_of_player]
        inner_dict2 = dict2[number_of_player]
        
        # --- Calculate grid position ---
        col_index = i % num_cols
        row_index = i // num_cols
        
        # x_base is the horizontal center for this key's square stack
        x_base = col_index * col_width
        # y_base_center is the vertical center for this row's squares
        y_base_center = top_row_y_center - (row_index * row_height)
        
        # --- Draw Key Label ---
        ax.text(x_base - 0.6, y_base_center + 0.5, f"#{number_of_player}", ha='right', va='center', fontsize=14, fontweight='bold')

        # --- Draw Squares (Top and Bottom) ---
        # Top square
        top_sq_bl_x = x_base - (square_size / 2)
        top_sq_bl_y = y_base_center # Bottom-left y for top square
        top_square = patches.Rectangle(
            (top_sq_bl_x, top_sq_bl_y),
            square_size, square_size,
            edgecolor='black', facecolor='white', linewidth=1.5
        )
        ax.add_patch(top_square)
        
        # Bottom square
        bottom_sq_bl_x = x_base - (square_size / 2)
        bottom_sq_bl_y = y_base_center - 1.0 # Touches top square
        bottom_square = patches.Rectangle(
            (bottom_sq_bl_x, bottom_sq_bl_y),
            square_size, square_size,
            edgecolor='black', facecolor='white', linewidth=1.5
        )
        ax.add_patch(bottom_square)

        # --- Draw Top Labels (from dict2) ---
        label_y_start = y_base_center + 1.1 # Just above the top square
        for label_key, text in dict2_labels.items():
            count = inner_dict2.get(label_key, 0)
            label_str = f"{text}: {count}"
            # Place text relative to its key (1, 2, 3)
            if label_key == 1: # left
                ax.text(x_base - 0.6, label_y_start, label_str, ha='left', va='bottom', fontsize=9)
            elif label_key == 2: # center
                ax.text(x_base, label_y_start + 0.3, label_str, ha='center', va='bottom', fontsize=9)
            elif label_key == 3: # right
                ax.text(x_base + 0.6, label_y_start, label_str, ha='right', va='bottom', fontsize=9)
        
        # --- Draw Lines and Bottom Labels (from dict1) ---
        
        # Line Origin: Center of top border of top square
        line_origins = [
            (x_base - square_size / 2, y_base_center + 1.0),
            (x_base - square_size / 4, y_base_center + 1.0),
            (x_base                  , y_base_center + 1.0),
            (x_base + square_size / 4, y_base_center + 1.0),
            (x_base + square_size / 2, y_base_center + 1.0),
        ]

        # Bottom square boundaries: x=[x_base-0.5, x_base+0.5], y=[y_base_center-1.0, y_base_center]
        # Destination positions inside BOTTOM square
        dest_left = bottom_sq_bl_x
        dest_segm_one = dest_left + 1 * square_size / 7
        dest_segm_two = dest_left + 2 * square_size / 7
        dest_segm_thr = dest_left + 3 * square_size / 7
        dest_segm_fou = dest_left + 4 * square_size / 7
        dest_segm_fiv = dest_left + 5 * square_size / 7
        dest_segm_six = dest_left + 6 * square_size / 7
        dest_right = bottom_sq_bl_x + square_size
        
        dest_bottom = bottom_sq_bl_y
        
        dest_positions = {
            1: (dest_left, dest_bottom),
            2: (dest_segm_one, dest_bottom),
            3: (dest_segm_two, dest_bottom),
            4: (dest_segm_thr, dest_bottom),
            5: (dest_segm_fou, dest_bottom),
            6: (dest_segm_fiv, dest_bottom),
            7: (dest_segm_six, dest_bottom),
            8: (dest_right, dest_bottom),
        }

        # Count positions outside of bottom square

        x_one = bottom_sq_bl_x - padding
        x_two = x_one + 1 * square_size / 6
        x_thr = x_one + 2 * square_size / 6
        x_fou = x_one + 3 * square_size / 6
        x_fiv = x_one + 4 * square_size / 6
        x_six = x_one + 5 * square_size / 6
        x_sev = x_one + 6 * square_size / 6
        x_eig = x_one + 7 * square_size / 6
        x_nin = bottom_sq_bl_x + square_size + padding

        y_center = bottom_sq_bl_y + square_size / 2
        y_bottom = bottom_sq_bl_y - padding

        count_positions = {
            1: (x_one, y_center),
            2: (x_two, y_bottom),
            3: (x_thr, y_bottom),
            4: (x_fou, y_bottom),
            5: (x_fiv, y_bottom),
            6: (x_six, y_bottom),
            7: (x_sev, y_bottom),
            8: (x_eig, y_bottom),
            9: (x_nin, y_center),
        }
        
        # draw the lines
        line_origin = line_origins[serve_positions[number_of_player] - 1]
        for num_key, pos in dest_positions.items():
            
            dest_x, dest_y = pos
            ax.plot([line_origin[0], dest_x], [line_origin[1], dest_y], 
                    color='gray', linestyle='--', linewidth=1)
        
        # draw the counts
        for num_key in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            # count = inner_dict1[num_key]
            count = 0
            
            # Draw the label (count) at the tip of the line
            ax.text(count_positions[num_key][0], count_positions[num_key][1], str(count), ha='center', va='center', 
                    fontsize=7, fontweight='bold', bbox=dict(facecolor='white', alpha=0.6, pad=0.1, boxstyle='round,pad=0.2'))

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

    K1, K2, serves, serve_outcomes, serve_positions = loaded_dicts[0], loaded_dicts[1], loaded_dicts[2], loaded_dicts[3], loaded_dicts[4]
    serves = {int(key): {int(key_): value_ for key_, value_ in value.items()} for key, value in serves.items()}
    serve_outcomes = {int(key): {int(key_): value_ for key_, value_ in value.items()} for key, value in serve_outcomes.items()}  
    serve_positions = {int(key): value for key, value in serve_positions.items()}

    # Call the new function
    draw_stacked_squares(serves, serve_outcomes, serve_positions, output_filename='serves.png')

