"""
Debug script to test if use_single_x_axis=True is working properly.
"""

import os
import sys
import matplotlib.pyplot as plt

# Add the parent directory to the path to import plotbot
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotbot as pb
from plotbot.multiplot import multiplot
from plotbot.multiplot_options import plt as pbplt
from plotbot.print_manager import print_manager

# Enable debug output
print_manager.debug_level = 3

# Define test times
test_times = [
    '2022/02/25 15:32:00.000',  # Enc 10
    '2022/06/01 13:38:00.000',  # Enc 11
    '2022/09/06 00:25:00.000',  # Enc 12
]

# Define variables for the test
test_vars = [
    pb.mag_rtn_4sa.br, 
    pb.mag_rtn_4sa.bt, 
    pb.mag_rtn_4sa.bn
]

# Output directory setup
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(output_dir, exist_ok=True)

# Reset and configure options
pbplt.options.reset()
pbplt.options.window = '12:00:00.000'
pbplt.options.title_fontsize = 14
pbplt.options.x_label_size = 14
pbplt.options.y_label_size = 13
pbplt.options.use_single_title = True
pbplt.options.single_title_text = "Debug Single X-Axis Test"

# IMPORTANT: Explicitly set use_single_x_axis to True
pbplt.options.use_single_x_axis = True
print(f"use_single_x_axis is set to: {pbplt.options.use_single_x_axis}")

# Enable relative time
pbplt.options.use_relative_time = True
print(f"use_relative_time is set to: {pbplt.options.use_relative_time}")

# Create plot data
plot_data = [(test_times[i], test_vars[i]) for i in range(3)]

# Create the plot
print("Creating multiplot with use_single_x_axis=True...")
fig, axs = multiplot(plot_data)

# Verify if tick labels are visible
print("\nChecking tick label visibility after multiplot...")
for i, ax in enumerate(axs):
    tick_labels = [t.get_visible() for t in ax.get_xticklabels()]
    visible_count = sum(tick_labels)
    print(f"Panel {i+1}: {visible_count} visible tick labels (Should be 0 for all except bottom panel)")

# Save the figure
output_file = os.path.join(output_dir, 'debug_single_x_axis.png')
fig.savefig(output_file, dpi=150)
print(f"Saved debug plot to {output_file}")

plt.close(fig) 