"""
Test the ham_binned_degrees_overlay feature in multiplot.

This test creates a simple multiplot with degrees_from_perihelion x-axis
and enables the HAM binned degrees overlay.
"""

import sys
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

import plotbot as pb
from plotbot import multiplot

# Test encounters - E18-E21 have good HAM data
test_times = [
    '2023/12/29 00:56:00',  # E18 perihelion
    '2024/03/30 02:21:00',  # E19 perihelion
    '2024/06/30 03:47:00',  # E20 perihelion
    '2024/09/30 05:15:00',  # E21 perihelion
]

# Build plot list - use mag_rtn.br as a simple variable
plot_list = [(t, pb.mag_rtn.br) for t in test_times]

# Configure options
pb.plt.options.reset()
pb.plt.options.use_degrees_from_perihelion = True
pb.plt.options.degrees_from_perihelion_range = (-60, 60)
pb.plt.options.color_mode = 'rainbow'
pb.plt.options.ham_binned_degrees_overlay = True
pb.plt.options.ham_binned_bar_opacity = 0.5
pb.plt.options.r_hand_single_color = '#363737'
pb.plt.options.window = '06:00:00'

print("=" * 60)
print("Testing ham_binned_degrees_overlay")
print("=" * 60)
print(f"ham_binned_degrees_overlay = {pb.plt.options.ham_binned_degrees_overlay}")
print(f"use_degrees_from_perihelion = {pb.plt.options.use_degrees_from_perihelion}")
print(f"color_mode = {pb.plt.options.color_mode}")
print("=" * 60)

# Create the plot
multiplot(plot_list)

# Save the figure
output_path = os.path.join(os.path.dirname(__file__), 'ham_binned_overlay_test.png')
pb.plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"\nSaved: {output_path}")
