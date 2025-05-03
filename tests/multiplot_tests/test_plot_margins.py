"""
Test script to evaluate title and x-axis label positioning with different numbers of panels.
This script creates plots with 1, 3, 5, and 7 panels to see how positioning scales.
"""

import os
import sys
import matplotlib.pyplot as plt
import numpy as np

# Add the parent directory to the path so we can import plotbot
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import plotbot as pb
from plotbot.multiplot import multiplot
from plotbot import config
from plotbot.multiplot_options import plt as pbplt

# Set server to Berkeley
config.server = 'berkeley'

# Create output directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(output_dir, exist_ok=True)

# Define test time ranges (perihelion encounters)
test_times = [
    '2022/02/25 15:32:00.000',  # Enc 10
    '2022/06/01 13:38:00.000',  # Enc 11
    '2022/09/06 00:25:00.000',  # Enc 12
    '2022/12/11 01:17:00.000',  # Enc 13
    '2023/03/17 01:34:00.000',  # Enc 14
    '2023/04/21 11:56:00.000',  # Enc 15
    '2023/06/22 03:46:00.000',  # Enc 16
    '2023/09/27 23:28:00.000',  # Enc 17
]

# Define variables for plotting (use mag_rtn components for simplicity)
test_variables = [
    pb.mag_rtn_4sa.br,
    pb.mag_rtn_4sa.bt, 
    pb.mag_rtn_4sa.bn,
    pb.mag_rtn_4sa.bmag,
    pb.mag_rtn_4sa.br,
    pb.mag_rtn_4sa.bt,
    pb.mag_rtn_4sa.bn
]

def run_test_with_panels(num_panels):
    """Run a test with the specified number of panels at width=22 and height=3, rainbow mode, each panel gets its own title."""
    pbplt.options.reset()
    pbplt.options.window = '12:00:00.000'
    pbplt.options.use_single_title = False  # Each panel gets its own title
    pbplt.options.width = 22
    pbplt.options.height_per_panel = 3
    pbplt.options.color_mode = 'rainbow'
    pbplt.options.title_fontsize = 14
    pbplt.options.x_label_size = 14
    pbplt.options.y_label_size = 13
    pbplt.options.y_label_pad = 12
    pbplt.options.x_label_pad = 8
    pbplt.options.bold_title = True
    pbplt.options.bold_x_axis_label = False
    pbplt.options.bold_y_axis_label = False
    pbplt.options.use_default_plot_settings = False
    pbplt.options.use_single_x_axis = True
    pbplt.options.title_pad = 2  # Negative padding to bring titles closer to the plot when using per-panel titles
    plot_data = [(test_times[i], test_variables[i]) for i in range(min(num_panels, len(test_times), len(test_variables)))]
    fig, axs = multiplot(plot_data)
    output_file = os.path.join(output_dir, f"margin_test_{num_panels}_panels_width22_height3_rainbow_panel_titles.png")
    fig.savefig(output_file, dpi=150)
    print(f"Saved plot with {num_panels} panel{'s' if num_panels > 1 else ''} (width=22, height=3, rainbow, panel titles) to {output_file}")
    plt.close(fig)

# Run tests with different numbers of panels
print("Starting margin tests for width=22, height=3, rainbow mode, panels 1, 3, 5, 7...")
for n in [1, 3, 5, 7]:
    run_test_with_panels(n)
print("Tests completed. Check the output directory for the generated images.") 