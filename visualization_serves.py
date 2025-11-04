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

def aggregate_outcomes(zones: dict) -> dict:

    out = {'1': 0, '2': 0, '3': 0, '4': 0}

    for zone, outcomes in zones.items():

        for outcome, count in outcomes.items():

            if zone == '0': # only count one count of the error zone
                out['4'] += count
                break

            else:
                out[outcome] += count

    return out


def zone_with_most_serves(zones: dict) -> str:

    most_servers_zone = '1'

    for zone, outcomes in zones.items():
        if zone == '0':
            continue

        if sum(outcomes.values()) > sum(zones[most_servers_zone].values()):
            most_servers_zone = zone

    return most_servers_zone


def zone_with_most_aces(zones: dict) -> str:

    most_aces_zone = '1'

    for zone, outcomes in zones.items():
        if zone == '0':
            continue

        if outcomes['1'] > zones[most_aces_zone]['1']:
            most_aces_zone = zone

    if zones[most_aces_zone]['1'] == 0:
        return '-1'

    return most_aces_zone


def draw_stacked_squares(serves: OuterDict1, serve_positions: OuterDict3, output_filename: str = 'stacked_squares.png'):
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
        sorted_keys = sorted(serves.keys())
        if not sorted_keys:
            print("Error: Dictionaries are empty.")
            return
    except Exception as e:
        print(f"Error sorting keys: {e}")
        return

    num_keys = len(sorted_keys)
    
    # --- Define Grid Layout ---
    num_cols = 1
    num_rows = num_keys
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
    map_outcome_labels = {1: 'ace', 2: 'received good', 3: 'received bad', 4: 'err'}
    
    top_row_y_center = 2.5 # Y-center for the first row

    # --- 3. Iterate and Draw per number_of_player ---
    for i, number_of_player in enumerate(sorted_keys):

        zones = serves[number_of_player]
        
        # --- Calculate grid position ---
        col_index = 0
        row_index = i
        
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

        # --- Draw Top Labels ---
        aggr_outcomes = aggregate_outcomes(zones)
        mapping = {'1': 'ace', '2': '+rec', '3': '-rec', '4': 'err'}

        label_y_start = y_base_center + 1.1    # Just above the top square
        for label_key, text in mapping.items():
            count = aggr_outcomes.get(label_key, 0)
            label_str = f"{text}: {count}"
            # Place text relative to its key (1, 2, 3)
            if label_key == '1': # left
                ax.text(x_base - 0.6, label_y_start, label_str, ha='left', va='bottom', fontsize=9)
            elif label_key == '2': # center left
                ax.text(x_base - 0.4, label_y_start + 0.3, label_str, ha='center', va='bottom', fontsize=9)
            elif label_key == '3': # center right
                ax.text(x_base + 0.4, label_y_start + 0.3, label_str, ha='center', va='bottom', fontsize=9)
            elif label_key == '4': # right
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

        x = bottom_sq_bl_x + square_size + 7 * padding

        y_top = bottom_sq_bl_y + 2 * square_size - padding
        
        # draw the lines
        line_origin = line_origins[serve_positions[number_of_player] - 1]
        for num_key, pos in dest_positions.items():
            
            dest_x, dest_y = pos
            ax.plot([line_origin[0], dest_x], [line_origin[1], dest_y], 
                    color='gray', linestyle='--', linewidth=1)
        
        # draw the counts
        ax.text(x, y_top + (2 * square_size / 9), 'aces / +rec / -rec', ha='center', va='center', fontsize=7, fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.6, pad=0.1, boxstyle='round,pad=0.2'))
        for zone in map(lambda x: str(x), [i for i in range(1, 10)]):
            count = zones[zone]

            string = f"zone {zone}: {count['1']} / {count['2']} / {count['3']}"
            
            # Draw the label (count) at the tip of the line
            ax.text(x, y_top - (int(zone) - 1) * (2 * square_size / 9), string, ha='center', va='center', 
                    fontsize=7, fontweight='bold', bbox=dict(facecolor='white', alpha=0.6, pad=0.1, boxstyle='round,pad=0.2'))


        ###########################################################################################
        # draw a yellow dot in the zone with most serves and a red dot in the zone with most aces
        dest_positions = {
            1: (dest_left, dest_bottom + square_size / 2),
            2: (dest_segm_one, dest_bottom),
            3: (dest_segm_two, dest_bottom),
            4: (dest_segm_thr, dest_bottom),
            5: (dest_segm_fou, dest_bottom),
            6: (dest_segm_fiv, dest_bottom),
            7: (dest_segm_six, dest_bottom),
            8: (dest_right, dest_bottom),
            9: (dest_right + 2 * square_size / 14, dest_bottom + square_size / 2)
        }

        # add most serves zone
        most_serves_zone = zone_with_most_serves(zones)

        x_position, y_position = dest_positions[int(most_serves_zone)]
        x_position = x_position - square_size / 14
        radius = 0.05      
        
        circle = patches.Circle(
            (x_position, y_position), 
            radius=radius, 
            facecolor='yellow', 
            edgecolor='black',
            linewidth=0.1
        )
        ax.add_patch(circle)       
        
        # add most aces zone
        most_aces_zone = zone_with_most_aces(zones)
        if not most_aces_zone == '-1':
            x_position, y_position = dest_positions[int(most_aces_zone)]
            x_position = x_position - square_size / 14
            y_position = y_position + 0.05
            radius = 0.05      
            
            circle = patches.Circle(
                (x_position, y_position), 
                radius=radius, 
                facecolor='red', 
                edgecolor='black',
                linewidth=0.1
            )
            ax.add_patch(circle)   

    # --- 4. Save and Show ---
    try:
        plt.savefig(output_filename, bbox_inches='tight', dpi=150)
        print(f"Grid image saved to {output_filename}")
    except Exception as e:
        print(f"Error saving or showing plot: {e}")

######################################################################################################################################################################

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

    # Call the new function
    draw_stacked_squares(serves, serve_positions, output_filename='serves.png')

