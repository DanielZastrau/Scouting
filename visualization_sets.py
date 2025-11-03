import argparse
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, Any

# Define type hints for clarity
InnerDict = Dict[int, Any]
OuterDict = Dict[int, InnerDict]

def draw_grid(dict1: OuterDict, dict2: OuterDict, output_filename: str = 'sets.png'):
    """
    Draws a 2x3 grid of squares and populates them with numbers from two dictionaries.

    Args:
        dict1: Dictionary for the first row (keys 1, 2, 3).
        dict2: Dictionary for the second row (keys 1, 2, 3).
        output_filename: The file to save the resulting image to.
    """
    
    # --- 1. Setup the Plot ---
    # Create a figure and a single axes
    # We set figsize to (9, 6) to make the 3x2 grid look proportional
    fig, ax = plt.subplots(1, figsize=(9, 6))

    # Set the aspect of the plot to 'equal' so squares are square
    ax.set_aspect('equal')

    # Set the limits for the x and y axes to frame the 3x2 grid
    # We add extra padding for the new labels
    ax.set_xlim(-1.0, 3.5)
    ax.set_ylim(-0.5, 3.0)

    # Turn off the axis lines and labels
    ax.axis('off')
    
    # --- 1b. Add Row and Column Labels ---
    label_fontsize = 14
    label_fontweight = 'bold'
    
    # Column Labels (top)
    ax.text(1, 2.8, 'perfect', ha='center', va='bottom', fontsize=label_fontsize, fontweight=label_fontweight)
    ax.text(2, 2.8, 'mehh', ha='center', va='bottom', fontsize=label_fontsize, fontweight=label_fontweight)
    ax.text(3, 2.8, 'bad', ha='center', va='bottom', fontsize=label_fontsize, fontweight=label_fontweight)
    
    # Row Labels (left)
    ax.text(-0.8, 2, 'K1', ha='center', va='center', fontsize=label_fontsize, fontweight=label_fontweight, rotation=90)
    ax.text(-0.8, 1, 'K2', ha='center', va='center', fontsize=label_fontsize, fontweight=label_fontweight, rotation=90)
    
    # --- 2. Define Layout and Styling ---
    square_size = 0.95  # Reduced from 1.0 to create whitespace
    padding = 0.1  # Padding for text inside the square
    
    # Combine the dictionaries and their row positions
    # Row 1 (dict1) will be centered at y=2
    # Row 0 (dict2) will be centered at y=1
    # We reverse the order to [dict2, dict1] to match y-coordinates [1, 2]
    rows_data = [(dict1, 2), (dict2, 1)]
    
    # --- 3. Iterate and Draw ---
    for data_dict, y_base in rows_data:
        # Iterate through columns 1, 2, 3
        for col_index in [1, 2, 3]:
            if col_index not in data_dict:
                print(f"Warning: Key {col_index} not in dictionary for row.")
                continue
                
            inner_dict = data_dict[col_index]
            
            # Column 1 at x=1, Col 2 at x=2, Col 3 at x=3
            x_base = col_index
            
            # --- Draw the Square ---
            # We calculate the bottom-left corner for the Rectangle patch
            bottom_left_x = x_base - (square_size / 2)
            bottom_left_y = y_base - (square_size / 2)
            
            square = patches.Rectangle(
                (bottom_left_x, bottom_left_y),
                square_size,
                square_size,
                edgecolor='black',
                facecolor='white',
                linewidth=2
            )
            ax.add_patch(square)
            
            # --- Define Text Positions ---
            # These are absolute coordinates on the plot
            left_x = bottom_left_x + padding
            right_x = bottom_left_x + square_size - padding
            center_x = x_base
            
            top_y = bottom_left_y + square_size - padding
            bottom_y = bottom_left_y + padding
            center_y = y_base
            
            # --- Place the 6 Numbers ---
            # We use horizontal alignment (ha) and vertical alignment (va)
            # to position the text relative to the coordinate.
            
            # 1: Top Left
            if 1 in inner_dict:
                ax.text(left_x, top_y, inner_dict[1], ha='left', va='top', fontsize=12)
            
            # 2: Bottom Left
            if 2 in inner_dict:
                ax.text(left_x, bottom_y, inner_dict[2], ha='left', va='bottom', fontsize=12)
                
            # 3: Bottom Center
            if 3 in inner_dict:
                ax.text(center_x, bottom_y, inner_dict[3], ha='center', va='bottom', fontsize=12)
                
            # 4: Bottom Right
            if 4 in inner_dict:
                ax.text(right_x, bottom_y, inner_dict[4], ha='right', va='bottom', fontsize=12)
            
            # 5: Top Right
            if 5 in inner_dict:
                ax.text(right_x, top_y, inner_dict[5], ha='right', va='top', fontsize=12)
                
            # 6: Top Center
            if 6 in inner_dict:
                ax.text(center_x, top_y, inner_dict[6], ha='center', va='top', fontsize=12)

    # --- 4. Save and Show ---
    try:
        plt.savefig(output_filename, bbox_inches='tight', dpi=150)
        print(f"Grid image saved to {output_filename}")
        
        # Show the plot in a window
        plt.show()
        
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



    K1, K2, serves, serve_outcomes = loaded_dicts[0], loaded_dicts[1], loaded_dicts[2], loaded_dicts[3]
    K1 = {int(key): {int(key_): value_ for key_, value_ in value.items()} for key, value in K1.items()}
    K2 = {int(key): {int(key_): value_ for key_, value_ in value.items()} for key, value in K2.items()}    

    # Call the function with the example data
    # The output will be saved as 'squares_grid.png' and also displayed
    draw_grid(K1, K2)
