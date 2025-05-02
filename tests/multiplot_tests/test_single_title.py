"""
Test script to verify that use_single_title works correctly, regardless of save_preset setting.
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

# Test 1: Single title without preset
print("\n=== Test 1: Single title without preset ===")
pbplt.options.reset()
pbplt.options.window = '24:00:00.000'
pbplt.options.use_single_title = True
pbplt.options.single_title_text = "Test Single Title Without Preset"
pbplt.options.save_preset = False

# Create a 3-panel plot
fig1, axes1 = multiplot([
    (center_time, pb.mag_rtn_4sa.br),
    (center_time, pb.mag_rtn_4sa.bt),
    (center_time, pb.mag_rtn_4sa.bn)
])

# Save the figure for visual inspection
output_path1 = os.path.join(output_dir, "test_single_title_no_preset.png")
fig1.savefig(output_path1)
plt.close(fig1)
print(f"Saved figure to {output_path1}")

# Test 2: Multiple plots with single title off
print("\n=== Test 2: Multiple plots with single title off ===")
pbplt.options.reset()
pbplt.options.window = '24:00:00.000'
pbplt.options.use_single_title = False

# Create a 3-panel plot
fig2, axes2 = multiplot([
    (center_time, pb.mag_rtn_4sa.br),
    (center_time, pb.mag_rtn_4sa.bt),
    (center_time, pb.mag_rtn_4sa.bn)
])

# Save the figure for visual inspection
output_path2 = os.path.join(output_dir, "test_no_single_title.png")
fig2.savefig(output_path2)
plt.close(fig2)
print(f"Saved figure to {output_path2}")

print("\nTest completed. Please visually inspect the output images to verify that:")
print("1. In the first image, there should be a single title at the top and NO individual panel titles.")
print("2. In the second image, there should be individual titles for each panel and NO overall title.") 