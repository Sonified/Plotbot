"""
Test script to verify that when using positional data with use_single_x_axis=True,
tick labels only appear on the bottom plot.
"""

import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import plotbot
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import plotbot as pb
from plotbot.multiplot import multiplot
from plotbot.multiplot_options import plt as pbplt

# Set up center time for test
center_time = "2021-11-16 12:00:00"

# Reset options and set up test configuration
pbplt.options.reset()
pbplt.options.window = '24:00:00.000'
pbplt.options.use_single_x_axis = True

# Enable Carrington Longitude for x-axis
pbplt.options.x_axis_carrington_lon = True

# Create a 3-panel plot
print("Creating 3-panel multiplot with positional data and use_single_x_axis=True...")
fig, axes = multiplot([
    (center_time, pb.mag_rtn_4sa.br),
    (center_time, pb.mag_rtn_4sa.bt),
    (center_time, pb.mag_rtn_4sa.bn)
])

# Create output directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(output_dir, exist_ok=True)

# Save the figure for visual inspection
output_path = os.path.join(output_dir, "test_single_x_axis_positional.png")
fig.savefig(output_path)
plt.close(fig)
print(f"Saved figure to {output_path} for visual inspection")

# Check if tick labels are visible only on the bottom plot
print("\nChecking tick label visibility...")
for i, ax in enumerate(axes):
    tick_labels = [t.get_visible() for t in ax.get_xticklabels()]
    visible_count = sum(tick_labels)
    
    if i < len(axes) - 1:
        print(f"Panel {i+1}: {visible_count} visible tick labels - Should be 0")
    else:
        print(f"Bottom panel: {visible_count} visible tick labels - Should be > 0")

print("\nTest completed. Please visually inspect the output image to confirm the fix is working properly.") 