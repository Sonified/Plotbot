"""
Test script to demonstrate how to adjust the x-axis label padding using x_label_pad.
"""

import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import plotbot
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotbot as pb
from plotbot.multiplot import multiplot
from plotbot.multiplot_options import plt as pbplt

# Set up center time for test
center_time = "2021-11-16 12:00:00"

# Create output directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(output_dir, exist_ok=True)

# Test different x-label paddings
padding_values = [5, 10, 20, 30, 40]

for i, pad in enumerate(padding_values):
    # Reset options for each plot
    pbplt.options.reset()
    
    # Enable single x-axis and set custom title
    pbplt.options.use_single_x_axis = True
    pbplt.options.use_single_title = True
    pbplt.options.single_title_text = f"X-Label Padding: {pad}px"
    
    # Set the x-label padding
    pbplt.options.x_label_pad = pad
    
    # Configure the window
    pbplt.options.window = '24:00:00.000'
    
    # Use actual plotbot variables
    var1 = pb.mag_rtn.br
    var2 = pb.mag_rtn.bt
    var3 = pb.mag_rtn.bn
    
    # Create and save the plot
    plot_list = [(center_time, var1), (center_time, var2), (center_time, var3)]
    fig, axs = multiplot(plot_list)
    
    # Save figure to output directory
    output_file = os.path.join(output_dir, f'x_label_pad_{pad}.png')
    fig.savefig(output_file, dpi=150)
    print(f"Saved plot with x_label_pad={pad} to {output_file}")
    
    # Close the figure to avoid memory issues
    plt.close(fig)

print("\nTest completed. Check the output directory for the generated images.") 