import matplotlib.colors as colors

def get_plot_colors(n_panels, color_mode='default', single_color=None):
    """
    Get colors for multiplot panels based on color mode.
    
    Args:
        n_panels (int): Number of panels to generate colors for
        color_mode (str): One of 'default', 'rainbow', or 'single'
        single_color (str): Color to use when color_mode is 'single'
    
    Returns:
        dict: Contains:
            'panel_colors': List of colors for each panel
            'title_color': Color for the main title
            'bottom_color': Color for bottom axis elements
    """
    if color_mode == 'default':
        return None
    
    if color_mode == 'single':
        if not single_color:
            single_color = 'red'  # Default if none specified
        return {
            'panel_colors': [single_color] * n_panels,
            'title_color': single_color,
            'bottom_color': single_color
        }
    
    if color_mode == 'rainbow':
        # Define standard rainbow colors
        rainbow_colors = [
            'red',          # Red
            'darkorange',   # Orange
            'gold',         # Yellow
            'green',        # Green
            'blue',         # Blue
            'indigo',       # Indigo
            'darkviolet'    # Violet
        ]
        
        # Special handling for n_panels <= 7
        if n_panels == 1:
            colors_to_use = ['red']
        elif n_panels == 2:
            colors_to_use = ['red', 'green']
        elif n_panels == 3:
            colors_to_use = ['red', 'gold', 'blue']
        elif n_panels == 4:
            colors_to_use = ['red', 'gold', 'blue', 'violet']
        elif n_panels == 5:
            colors_to_use = ['red', 'orange', 'gold', 'green', 'blue']
        elif n_panels == 6:
            colors_to_use = ['red', 'orange', 'gold', 'green', 'blue', 'violet']
        elif n_panels == 7:
            colors_to_use = rainbow_colors
        else:
            # For more than 7 panels, interpolate between rainbow colors
            colors_to_use = []
            for i in range(n_panels):
                position = (i / (n_panels - 1)) * (len(rainbow_colors) - 1)
                color_index = int(position)
                color_remainder = position - color_index
                
                # Handle the case where we're at the last color
                if color_index >= len(rainbow_colors) - 1:
                    colors_to_use.append(rainbow_colors[-1])
                    continue
                
                # Get the two colors to interpolate between
                color1 = colors.to_rgb(rainbow_colors[color_index])
                color2 = colors.to_rgb(rainbow_colors[color_index + 1])
                
                # Interpolate between the two colors
                r = color1[0] + (color2[0] - color1[0]) * color_remainder
                g = color1[1] + (color2[1] - color1[1]) * color_remainder
                b = color1[2] + (color2[2] - color1[2]) * color_remainder
                
                colors_to_use.append((r, g, b))
        
        return {
            'panel_colors': colors_to_use,
            'title_color': 'red',  # Title always red in rainbow mode
            'bottom_color': 'darkviolet'  # Bottom axis always violet in rainbow mode
        }

def apply_panel_color(ax, color, options=None):
    """
    Apply a color to all elements of a panel
    
    Args:
        ax: The matplotlib axis
        color: The color to apply
        options: The MultiplotOptions instance (for accessing settings)
    """
    # Store original y-limits before any modifications
    original_ylim = ax.get_ylim()
    
    # Color the y-axis label and make bold
    if ax.yaxis.label:
        ax.yaxis.label.set_color(color)
        ax.yaxis.label.set_weight('bold')
    
    # Color the title if it exists and not using single title
    if options and not options.use_single_title:
        if ax.get_title():
            ax.title.set_color(color)
    
    # Color all y-axis elements
    ax.tick_params(axis='y', colors=color, which='both')
    
    # Color all spines
    for spine in ax.spines.values():
        spine.set_color(color)
    
    # Update vertical line if it exists
    if options and options.draw_vertical_line:
        for line in ax.get_lines():
            if line.get_linestyle() == '--':  # Assuming this identifies the vertical line
                line.set_color(color)
                line.set_linewidth(options.vertical_line_width)
    
    # Check if y-limits changed during the styling process
    new_ylim = ax.get_ylim()
    if new_ylim != original_ylim:
        # Restore original y-limits if they were changed
        ax.set_ylim(original_ylim)

def apply_bottom_axis_color(ax, color):
    """
    Apply color to bottom axis elements only
    
    Args:
        ax: The matplotlib axis
        color: The color to apply
    """
    # Color x-axis label
    if ax.xaxis.label:
        ax.xaxis.label.set_color(color)
        ax.xaxis.label.set_weight('bold')
    
    # Color x-axis ticks
    ax.tick_params(axis='x', colors=color, which='both')
    
    # Color bottom spine only
    ax.spines['bottom'].set_color(color)
    
def validate_log_scale_limits(y_limit, y_scale, axis_name):
    """
    Validates that y-limits are appropriate for the chosen scale.
    
    Args:
        y_limit: Tuple of (min, max) limits
        y_scale: Scale type ('log', 'linear', etc.)
        axis_name: Name of the axis for warning messages
        
    Returns:
        Tuple of validated (min, max) limits
    """
    if y_scale != 'log' or y_limit is None:
        return y_limit
        
    min_val, max_val = y_limit
    validated_min = min_val
    validated_max = max_val
    
    if min_val <= 0:
        validated_min = 0.01
        print(f"WARNING: {min_val} is not a valid minimum with logarithmic y-axis for {axis_name}. Setting to {validated_min}")
    
    if max_val <= 0:
        validated_max = 1.0
        print(f"WARNING: {max_val} is not a valid maximum with logarithmic y-axis for {axis_name}. Setting to {validated_max}")
    
    if validated_min != min_val or validated_max != max_val:
        return (validated_min, validated_max)
    else:
        return y_limit