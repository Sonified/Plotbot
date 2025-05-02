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
    """Run a test with the specified number of panels."""
    # Reset options to defaults
    pbplt.options.reset()
    
    # Use the default settings (to test these)
    pbplt.options.window = '12:00:00.000'
    pbplt.options.use_single_title = True
    pbplt.options.single_title_text = f"Test Plot with {num_panels} Panel{'s' if num_panels > 1 else ''}"
    
    # Explicitly set the use_single_x_axis option
    pbplt.options.use_single_x_axis = True
    
    # Explicitly set font sizes to test the updated defaults
    pbplt.options.title_fontsize = 14
    pbplt.options.x_label_size = 14
    pbplt.options.y_label_size = 13
    pbplt.options.y_label_pad = 12
    pbplt.options.x_tick_label_size = 11
    pbplt.options.y_tick_label_size = 11
    
    # Create plot data list (use only as many times/variables as panels requested)
    plot_data = [(test_times[i], test_variables[i]) for i in range(min(num_panels, len(test_times), len(test_variables)))]
    
    # Create and save the plot
    fig, axs = multiplot(plot_data)
    
    # Save figure to output directory
    output_file = os.path.join(output_dir, f'margin_test_{num_panels}_panels.png')
    fig.savefig(output_file, dpi=150)
    print(f"Saved plot with {num_panels} panel{'s' if num_panels > 1 else ''} to {output_file}")
    
    # Close the figure to avoid memory issues
    plt.close(fig)

# Run tests with different numbers of panels
print("Starting margin tests with different panel counts...")
run_test_with_panels(1)
run_test_with_panels(3)
run_test_with_panels(5)
run_test_with_panels(7)  # Added test for 7 panels
print("Tests completed. Check the output directory for the generated images.") 