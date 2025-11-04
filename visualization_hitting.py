import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, Any

# --- Define Type Hints for the new data structure ---
# { row_key: { col_key: { triangle_key: value, ... }, ... }, ... }
TriangleData = Dict[int, int]
ColumnData = Dict[int, TriangleData]
DataDict = Dict[int, ColumnData]


def draw_triangle_squares(data: DataDict, output_filename: str = 'triangle_plot.png'):
    """
    Draws a grid of squares, each filled with 5 triangles
    based on a nested dictionary.
    
    - Top-level key = Row
    - Second-level key = Column
    - Third-level key (1-5) = Triangle
    - Third-level value = Label for that triangle
    """
    
    # --- 1. Setup the Plot ---
    try:
        if not data:
            print("Error: Data dictionary is empty.")
            return
        sorted_row_keys = sorted(data.keys())
        # Assume all rows have the same column keys, get from first row
        col_keys = sorted(data[sorted_row_keys[0]].keys())
    except Exception as e:
        print(f"Error processing data keys: {e}")
        return

    num_rows = len(sorted_row_keys)
    num_cols = len(col_keys) # Should be 3 based on description
    
    if num_cols != 3:
        print(f"Warning: Expected 3 columns, but data has {num_cols}.")

    # Define spacing for each grid cell
    # (Square + label area)
    cell_width = 3.0
    cell_height = 1.5
    square_size = 1.0
    
    # Calculate total figure size
    fig_width = num_cols * cell_width
    fig_height = num_rows * cell_height
    
    fig, ax = plt.subplots(1, figsize=(fig_width, fig_height + 1))
    ax.set_aspect('equal')

    # Set plot limits, adding padding
    ax.set_xlim(-1, fig_width)
    ax.set_ylim(-1, fig_height)
    ax.axis('off')
    
    # --- 2. Iterate and Draw ---
    for row_idx, row_key in enumerate(sorted_row_keys):
        
        # Calculate y_base for the current row
        # (0,0) is bottom-left, so we reverse the row_idx
        y_center = (num_rows - 1 - row_idx) * cell_height + (cell_height / 2)
        
        # Draw Row Label
        ax.text(-0.5, y_center, f"#{row_key}", ha='center', va='center', fontsize=12, fontweight='bold')
        
        for col_idx, col_key in enumerate(col_keys):
            
            # Calculate x_base for the current column
            x_center = col_idx * cell_width + (cell_width / 2)
            
            # --- Draw Column Label (for first row only) ---
            if row_idx == 0:
                positions = [4, 2, 3]
                ax.text(x_center, fig_height + 0.5, f"Pos: {positions[col_key - 1]}", ha='center', va='center', fontsize=12, fontweight='bold')
            
            # Get the data for this specific square
            try:
                triangle_data = data[row_key][col_key]
            except KeyError:
                print(f"Warning: No data for row {row_key}, col {col_key}. Skipping.")
                continue

            # --- Define Square Coordinates ---
            half_s = square_size / 2
            left = x_center - half_s
            right = x_center + half_s
            top = y_center + half_s
            bottom = y_center - half_s

            # --- Draw the Square Outline ---
            square = patches.Rectangle(
                (left, bottom), square_size, square_size,
                edgecolor='black', facecolor='white', linewidth=1
            )
            ax.add_patch(square)

            # Draw horizontal line
            line_start_x = x_center - square_size / 2
            line_end_x = x_center + square_size / 2
            line_y = y_center + square_size / 2 - square_size / 3
            ax.plot([line_start_x, line_end_x], [line_y, line_y], color='black', linewidth=1)

            # --- Define Triangle and Label points based on column index ---
            definitions = {}
            label_offset = 0.1 # How far to put text from border

            # Col 1: Tip at Top-Right (TR)
            if col_idx == 0:
                tip = (right, top)
                # 6 points define 5 bases: 3 on Left, 2 on Bottom
                points = [
                    (left, top), 
                    (left, top - (square_size * 1/3)), 
                    (left, top - (square_size * 3/4)),
                    (left + (square_size / 5), bottom), 
                    (left + (2 * square_size / 3), bottom), 
                    (right, bottom)
                ]
                # Label positions
                labels = [
                    {'pos': (left - label_offset, top - (square_size / 6)), 'ha': 'right', 'va': 'center'},
                    {'pos': (left - label_offset, top - (7 * square_size / 12)), 'ha': 'right', 'va': 'center'},
                    {'pos': (left - label_offset, bottom), 'ha': 'right', 'va': 'center'},
                    {'pos': (x_center - (square_size / 7), bottom - label_offset), 'ha': 'center', 'va': 'top'},
                    {'pos': (right - (square_size / 6), bottom - label_offset), 'ha': 'center', 'va': 'top'}
                ]

            # Col 2: Tip at Top-Left (TL)
            elif col_idx == 1:
                tip = (left, top)
                # 6 points define 5 bases: 3 on Right, 2 on Bottom
                points = [
                    (right, top), 
                    (right, top - (square_size * 1/3)), 
                    (right, top - (square_size * 3/4)),
                    (right - (square_size / 5), bottom), 
                    (right - (2 * square_size/ 3), bottom), 
                    (left, bottom)
                ]
                # Label positions
                labels = [
                    {'pos': (right + label_offset, top - (square_size / 6)), 'ha': 'left', 'va': 'center'},
                    {'pos': (right + label_offset, top - (7 * square_size / 12)), 'ha': 'left', 'va': 'center'},
                    {'pos': (right + label_offset, bottom), 'ha': 'left', 'va': 'center'},
                    {'pos': (x_center + (square_size / 7), bottom - label_offset), 'ha': 'center', 'va': 'top'},
                    {'pos': (left + (square_size / 6), bottom - label_offset), 'ha': 'center', 'va': 'top'}
                ]

            # Col 3: Tip at Top-Center (TC)
            else:
                tip = (x_center, top)
                # 6 points define 5 bases: 2 on Left, 1 on Bottom, 2 on Right
                points = [
                    (left, top), 
                    (left, top - (2 * square_size / 3)), 
                    (left + (square_size / 4), bottom), 
                    (right - (square_size / 4), bottom), 
                    (right, top - (2 * square_size / 3)),
                    (right, top) # Last point repeated, use 5 segments
                ]
            
                labels = [
                    {'pos': (left - label_offset, top - (square_size / 4)), 'ha': 'right', 'va': 'center'},
                    {'pos': (left - label_offset, bottom - label_offset), 'ha': 'right', 'va': 'center'},
                    {'pos': (x_center, bottom - label_offset), 'ha': 'center', 'va': 'top'},
                    {'pos': (right + label_offset, bottom - label_offset), 'ha': 'center', 'va': 'top'},
                    {'pos': (right + label_offset, top - (square_size / 4)), 'ha': 'left', 'va': 'center'}
                ]

            # --- Draw 5 Triangles and Labels ---
            for i, point in enumerate(points):
                triangle_key = i + 1
                value = triangle_data.get(triangle_key, 'N/A')
                
                # Draw line
                ax.plot([tip[0], point[0]], [tip[1], point[1]], color='black', linewidth=1)
                
                # Draw the label
                if i < len(labels):
                    info = labels[i]
                    ax.text(info['pos'][0], info['pos'][1], str(value), ha=info['ha'], va=info['va'], fontsize=8)

    # --- 3. Save and Show ---
    try:
        plt.savefig(output_filename, bbox_inches='tight', dpi=150)
        print(f"Grid image saved to {output_filename}")
    except Exception as e:
        print(f"Error saving or showing plot: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    
    # Example data showing the required structure:
    # { row: { col: { triangle_key: value, ... } } }
    plot_data = {
        10: { # Row 10
            1: {1: 10, 2: 20, 3: 30, 4: 40, 5: 50}, # Col 1 (Tip TR)
            2: {1: 11, 2: 22, 3: 33, 4: 44, 5: 55}, # Col 2 (Tip TL)
            3: {1: 15, 2: 25, 3: 35, 4: 45, 5: 59}  # Col 3 (Tip TC)
        },
        20: { # Row 20
            1: {1: 5, 2: 4, 3: 3, 4: 2, 5: 1},
            2: {1: 9, 2: 8, 3: 7, 4: 6, 5: 0},
            3: {1: 99, 2: 88, 3: 77, 4: 66, 5: 55}
        }
    }

    # Call the function
    draw_triangle_squares(plot_data, output_filename='hitting.png')
