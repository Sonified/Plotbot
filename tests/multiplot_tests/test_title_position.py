"""
Test script to demonstrate how to adjust the title position using title_y_position.
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

# Create output directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(output_dir, exist_ok=True)

# Test different title positions
positions = [0.98, 0.95, 0.92, 0.90, 0.85]

for pos in positions:
    # Reset options for each test
    pbplt.options.reset()
    pbplt.options.window = '24:00:00.000'
    pbplt.options.use_single_title = True
    pbplt.options.single_title_text = f"Title Position {pos}"
    
    # Set the title position
    pbplt.options.title_y_position = pos
    
    # Create a 3-panel plot
    fig, axes = multiplot([
        (center_time, pb.mag_rtn_4sa.br),
        (center_time, pb.mag_rtn_4sa.bt),
        (center_time, pb.mag_rtn_4sa.bn)
    ])
    
    # Save the figure for visual inspection
    output_path = os.path.join(output_dir, f"test_title_position_{pos}.png")
    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved figure with title_y_position={pos} to {output_path}")

print("\nTest completed. Please visually inspect the output images to compare different title positions.")
print("Lower values of title_y_position (e.g., 0.85-0.92) place the title closer to the plots.")
print("Higher values (e.g., 0.95-0.98) place the title closer to the top of the figure.") 