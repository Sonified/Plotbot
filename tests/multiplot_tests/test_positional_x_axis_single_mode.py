import os
import sys
import unittest
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import plotbot
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import plotbot as pb 
from plotbot.time_utils import str_to_datetime
from plotbot.multiplot import multiplot
# import plotbot.plotting as pbplt  # COMMENTED OUT: ModuleNotFoundError

class TestPositionalXAxisSingleMode(unittest.TestCase):
    """Test class to verify x-axis tick labels only show on bottom plot with use_single_x_axis=True"""
    
    def setUp(self):
        """Set up test data and directories"""
        # Define test time range
        self.center_time = str_to_datetime("2021-11-16 12:00:00")
        
        # Make sure output directory exists
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_figure(self, fig, filename):
        """Helper to save figure to the output directory"""
        output_path = os.path.join(self.output_dir, filename)
        fig.savefig(output_path)
        plt.close(fig)
        print(f"Saved figure to {output_path}")
        return output_path
    
    def test_single_x_axis_with_positional_data(self):
        """Test that x-axis tick labels only appear on bottom plot with positional data"""
        # Test each positional data type
        for data_type, setting in [
            ('carrington_lon', 'x_axis_carrington_lon'),
            ('r_sun', 'x_axis_r_sun'),
            ('carrington_lat', 'x_axis_carrington_lat')
        ]:
            print(f"\n=== Testing {data_type} with single x-axis ===")
            
            # Reset options
            pbplt.options.reset()
            pbplt.options.window = '24:00:00.000'
            pbplt.options.use_single_x_axis = True
            
            # Enable this positional data type
            setattr(pbplt.options, setting, True)
            
            # Create a multiplot with 3 panels
            fig, axes = multiplot([
                (self.center_time, pb.mag_rtn_4sa.br),
                (self.center_time, pb.mag_rtn_4sa.bt),
                (self.center_time, pb.mag_rtn_4sa.bn)
            ])
            
            # Save the figure for visual inspection
            self.save_figure(fig, f"test_single_x_axis_{data_type}.png")
            
            # Check that only the bottom panel has visible tick labels
            for i, ax in enumerate(axes):
                tick_labels = [t.get_visible() for t in ax.get_xticklabels()]
                
                if i < len(axes) - 1:
                    # Non-bottom panels should have no visible tick labels
                    self.assertFalse(any(tick_labels), 
                                    f"Panel {i+1} should not have visible x-tick labels")
                    print(f"✅ Panel {i+1}: No visible tick labels as expected")
                else:
                    # Bottom panel should have visible tick labels
                    self.assertTrue(any(tick_labels), 
                                   f"Bottom panel should have visible x-tick labels")
                    print(f"✅ Bottom panel: Has visible tick labels as expected")

if __name__ == '__main__':
    unittest.main() 