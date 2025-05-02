import unittest
import numpy as np
import pandas as pd
import sys
import os
import pathlib

# Force matplotlib to use non-interactive Agg backend
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # For date formatting

# Add parent directory to path to import plotbot modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent.parent))

import plotbot as pb
from plotbot.multiplot_options import plt as pbplt
from plotbot.multiplot import multiplot
from plotbot.x_axis_positional_data_helpers import XAxisPositionalDataMapper

# Import the encounter ranges from the analysis script output
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.parent / "local_tests_and_utils"))
try:
    from encounter_positional_ranges import ENCOUNTERS, ENCOUNTER_RANGES
except ImportError:
    # Fallback if the file doesn't exist
    ENCOUNTERS = {
        'E17': '2023/09/27 23:28:00.000',
        'E18': '2023/12/29 00:56:00.000',
        'E19': '2024/03/30 02:21:00.000'
    }
    ENCOUNTER_RANGES = {
        'E17': {
            'perihelion': '2023/09/27 23:28:00.000',
            'carrington_lon': (141.0, 226.0),
            'r_sun': (11.4, 13.6),
            'carrington_lat': (-3.9, -1.5),
        },
        'E18': {
            'perihelion': '2023/12/29 00:56:00.000',
            'carrington_lon': (276.0, 360.0),
            'r_sun': (11.4, 13.6),
            'carrington_lat': (-3.9, -1.5),
        },
        'E19': {
            'perihelion': '2024/03/30 02:21:00.000',
            'carrington_lon': (50.0, 134.0),
            'r_sun': (11.4, 13.6),
            'carrington_lat': (-3.9, -1.5),
        },
    }

class TestMultiplePositionalPlots(unittest.TestCase):
    """Test class to diagnose issues with multiple plots using positional x-axis data"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use the actual data file path
        project_root = pathlib.Path(__file__).parent.parent.parent.parent
        self.data_path = project_root / "support_data" / "trajectories" / "Parker_positional_data.npz"
        self.assertTrue(self.data_path.exists(), f"Data file not found at {self.data_path}")
        
        # Set up the directory for saving test images
        self.image_dir = project_root / "local_images"
        self.assertTrue(self.image_dir.exists(), f"Image directory not found at {self.image_dir}")
        
        # Create a mapper instance for direct testing
        self.mapper = XAxisPositionalDataMapper(str(self.data_path))
        self.assertTrue(self.mapper.data_loaded, "Positional data should load successfully")
        
        # Store original options to restore after tests
        self.original_settings = {
            'x_axis_carrington_lon': pbplt.options.x_axis_carrington_lon,
            'x_axis_carrington_lat': pbplt.options.x_axis_carrington_lat,
            'x_axis_r_sun': pbplt.options.x_axis_r_sun,
            'use_relative_time': pbplt.options.use_relative_time,
            'window': pbplt.options.window,
            'x_axis_positional_range': pbplt.options.x_axis_positional_range,
            'use_single_x_axis': pbplt.options.use_single_x_axis
        }
        
        # Reset all options to defaults
        pbplt.options.reset()
        pbplt.options.window = '24:00:00.000'  # 24 hour window
        
        # Load data for all three encounters
        for encounter, perihelion in ENCOUNTERS.items():
            # Calculate time range for each encounter
            center_time = pd.Timestamp(perihelion)
            start_time = center_time - pd.Timedelta(hours=12)
            end_time = center_time + pd.Timedelta(hours=12)
            
            # Format time range
            time_range = [
                start_time.strftime('%Y-%m-%d/%H:%M:%S.%f'),
                end_time.strftime('%Y-%m-%d/%H:%M:%S.%f')
            ]
            
            # Load magnetic field data for this encounter
            print(f"Loading data for {encounter}: {time_range[0]} to {time_range[1]}")
            pb.get_data(time_range, pb.mag_rtn_4sa.br)
            
        # Skip tests if data is not available for any encounter
        if not hasattr(pb.mag_rtn_4sa.br, 'datetime_array') or len(pb.mag_rtn_4sa.br.datetime_array) == 0:
            self.skipTest("Skipping tests - no magnetic field data available")
    
    def tearDown(self):
        """Restore original settings and close plots"""
        plt.close('all')
        
        # Restore original settings
        for key, value in self.original_settings.items():
            setattr(pbplt.options, key, value)
    
    def save_figure(self, fig, filename):
        """Helper method to properly render and save a figure"""
        # Make sure the figure is fully rendered
        try:
            fig.tight_layout()
        except ValueError as e:
            print(f"Warning during tight_layout: {e}")
        
        fig.canvas.draw()
        
        # Save with high quality
        filepath = os.path.join(self.image_dir, filename)
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"Saved image to {filepath}")
        return filepath
    
    def diagnostic_plot_raw_data(self, encounter_id='E17', data_type='carrington_lon'):
        """Create a diagnostic plot showing the raw positional data for an encounter"""
        # Get encounter information
        perihelion = ENCOUNTERS[encounter_id]
        center_time = pd.Timestamp(perihelion)
        
        # Create time range
        start_time = center_time - pd.Timedelta(hours=12)
        end_time = center_time + pd.Timedelta(hours=12)
        dates = pd.date_range(start=start_time, end=end_time, periods=200)
        dates_np = dates.to_numpy()
        
        # Get positional data
        values = self.mapper.map_to_position(dates_np, data_type)
        
        # Create a diagnostic plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot raw data points
        ax.plot(dates, values, 'o-', markersize=3, linewidth=1)
        
        # Format x-axis as dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        fig.autofmt_xdate()
        
        # Add title and labels
        if data_type == 'carrington_lon':
            ylabel = 'Carrington Longitude (degrees)'
        elif data_type == 'r_sun':
            ylabel = 'Radial Distance (R_sun)'
        else:
            ylabel = 'Carrington Latitude (degrees)'
            
        ax.set_title(f'Raw {data_type} Data for {encounter_id}')
        ax.set_xlabel('Time')
        ax.set_ylabel(ylabel)
        ax.grid(True)
        
        # Save and return
        self.save_figure(fig, f"diagnostic_{encounter_id}_{data_type}_raw.png")
        return fig
    
    def test_single_plot_vs_multiple_plots(self):
        """Test how positional x-axis works with single vs multiple plots"""
        # Test each data type separately
        for data_type, setting in [
            ('carrington_lon', 'x_axis_carrington_lon'),
            ('r_sun', 'x_axis_r_sun'),
            ('carrington_lat', 'x_axis_carrington_lat')
        ]:
            print(f"\n=== Testing {data_type} as x-axis ===")
            
            # Reset options
            pbplt.options.reset()
            pbplt.options.window = '24:00:00.000'
            pbplt.options.use_single_x_axis = True
            
            # Enable this positional data type
            setattr(pbplt.options, setting, True)
            
            # First, create a single plot for E17
            print(f"Creating single plot for E17 with {data_type}...")
            fig1, ax1 = multiplot([(ENCOUNTERS['E17'], pb.mag_rtn_4sa.br)])
            
            # Save the single plot
            self.save_figure(fig1, f"test_single_plot_{data_type}_e17.png")
            
            # Get the x-axis range from this plot
            single_plot_xlim = ax1[0].get_xlim()
            print(f"Single plot x-axis range: {single_plot_xlim}")
            
            # Now create multiple plots with the same data from E17
            print(f"Creating multiple plot (3 panels) for E17 with {data_type}...")
            fig2, ax2 = multiplot([
                (ENCOUNTERS['E17'], pb.mag_rtn_4sa.br),
                (ENCOUNTERS['E17'], pb.mag_rtn_4sa.bt),
                (ENCOUNTERS['E17'], pb.mag_rtn_4sa.bn)
            ])
            
            # Save the multiple plot
            self.save_figure(fig2, f"test_multiple_plot_{data_type}_e17.png")
            
            # Get x-axis ranges from multiple plot
            multiple_plot_xlims = [ax.get_xlim() for ax in ax2]
            print(f"Multiple plot x-axis ranges: {multiple_plot_xlims}")
            
            # Verify all panels in multiple plot have same range
            for i in range(len(ax2)-1):
                self.assertEqual(multiple_plot_xlims[i], multiple_plot_xlims[-1],
                               f"Panel {i+1} should have same x-range as bottom panel")
            
            # Check for any discontinuities in the data by creating diagnostic plots
            self.diagnostic_plot_raw_data('E17', data_type)
            
            plt.close(fig1)
            plt.close(fig2)
    
    def test_multiple_encounters_fixed_range(self):
        """Test multiple encounters with a fixed x-axis range"""
        # Test each data type
        for data_type, setting in [
            ('carrington_lon', 'x_axis_carrington_lon'),
            ('r_sun', 'x_axis_r_sun'),
            ('carrington_lat', 'x_axis_carrington_lat')
        ]:
            print(f"\n=== Testing multiple encounters with fixed {data_type} range ===")
            
            # Reset options
            pbplt.options.reset()
            pbplt.options.window = '24:00:00.000'
            pbplt.options.use_single_x_axis = True
            
            # Enable this positional data type and set fixed range
            setattr(pbplt.options, setting, True)
            
            # Get a range that covers all encounters
            if data_type == 'carrington_lon':
                # Special case for longitude - it wraps around 360°
                pbplt.options.x_axis_positional_range = (0, 360)
            else:
                # Get min/max from all encounters
                min_vals = [ENCOUNTER_RANGES[enc][data_type][0] for enc in ENCOUNTERS]
                max_vals = [ENCOUNTER_RANGES[enc][data_type][1] for enc in ENCOUNTERS]
                pbplt.options.x_axis_positional_range = (min(min_vals), max(max_vals))
            
            print(f"Using fixed range: {pbplt.options.x_axis_positional_range}")
            
            # Create a plot with all three encounters
            fig, axes = multiplot([
                (ENCOUNTERS['E17'], pb.mag_rtn_4sa.br),
                (ENCOUNTERS['E18'], pb.mag_rtn_4sa.br),
                (ENCOUNTERS['E19'], pb.mag_rtn_4sa.br)
            ])
            
            # Save the plot
            self.save_figure(fig, f"test_multiple_encounters_fixed_{data_type}.png")
            
            # Verify all panels have the expected range
            expected_range = pbplt.options.x_axis_positional_range
            for i, ax in enumerate(axes):
                actual_range = ax.get_xlim()
                print(f"Panel {i+1} range: {actual_range}")
                self.assertAlmostEqual(actual_range[0], expected_range[0], delta=1.0,
                                     msg=f"Panel {i+1} lower limit should match fixed range")
                self.assertAlmostEqual(actual_range[1], expected_range[1], delta=1.0,
                                     msg=f"Panel {i+1} upper limit should match fixed range")
            
            plt.close(fig)
    
    def test_multiple_encounters_auto_range(self):
        """Test multiple encounters with auto x-axis range"""
        # Test each data type
        for data_type, setting in [
            ('carrington_lon', 'x_axis_carrington_lon'),
            ('r_sun', 'x_axis_r_sun'),
            ('carrington_lat', 'x_axis_carrington_lat')
        ]:
            print(f"\n=== Testing multiple encounters with auto {data_type} range ===")
            
            # Reset options
            pbplt.options.reset()
            pbplt.options.window = '24:00:00.000'
            
            # Test both with single x-axis and separate x-axes
            for use_single in [True, False]:
                pbplt.options.use_single_x_axis = use_single
                mode = "common" if use_single else "separate"
                
                # Enable this positional data type without setting a range
                setattr(pbplt.options, setting, True)
                pbplt.options.x_axis_positional_range = None
                
                print(f"Using {mode} x-axis (auto range)")
                
                # Create a plot with all three encounters
                fig, axes = multiplot([
                    (ENCOUNTERS['E17'], pb.mag_rtn_4sa.br),
                    (ENCOUNTERS['E18'], pb.mag_rtn_4sa.br),
                    (ENCOUNTERS['E19'], pb.mag_rtn_4sa.br)
                ])
                
                # Save the plot
                self.save_figure(fig, f"test_multiple_encounters_{mode}_auto_{data_type}.png")
                
                # Get the x-axis ranges
                x_ranges = [ax.get_xlim() for ax in axes]
                
                # If using common x-axis, verify all panels have the same range
                if use_single:
                    for i in range(len(axes)-1):
                        self.assertEqual(x_ranges[i], x_ranges[-1],
                                      f"Panel {i+1} should have same x-range as bottom panel with common axis")
                else:
                    # With separate axes, each encounter should have its own appropriate range
                    # Just print for diagnosis - we expect different ranges here
                    print("Separate x-axis ranges:")
                    for i, rng in enumerate(x_ranges):
                        enc = list(ENCOUNTERS.keys())[i]
                        print(f"  Panel {i+1} ({enc}): {rng}")
                
                plt.close(fig)
    
    def test_discontinuities_in_data(self):
        """Test for discontinuities in the positional data, especially at encounter boundaries"""
        # Create a big figure showing all encounters side by side for each data type
        for data_type in ['carrington_lon', 'r_sun', 'carrington_lat']:
            # Create a large figure
            fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
            
            for i, (enc_id, perihelion) in enumerate(ENCOUNTERS.items()):
                center_time = pd.Timestamp(perihelion)
                
                # Create time range
                start_time = center_time - pd.Timedelta(hours=12)
                end_time = center_time + pd.Timedelta(hours=12)
                dates = pd.date_range(start=start_time, end=end_time, periods=200)
                dates_np = dates.to_numpy()
                
                # Get positional data
                values = self.mapper.map_to_position(dates_np, data_type)
                
                # Plot data
                axes[i].plot(dates, values, 'o-', markersize=2, linewidth=1)
                axes[i].set_title(f"{enc_id} ({perihelion.split()[0]})")
                axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                
                # Add vertical line at perihelion
                axes[i].axvline(x=center_time, color='r', linestyle='--', alpha=0.7)
            
            # Add common labels
            fig.suptitle(f"{data_type} Values Across Encounters", fontsize=14)
            
            if data_type == 'carrington_lon':
                ylabel = 'Carrington Longitude (degrees)'
            elif data_type == 'r_sun':
                ylabel = 'Radial Distance (R_sun)'
            else:
                ylabel = 'Carrington Latitude (degrees)'
                
            # Add common y-label
            fig.text(0.04, 0.5, ylabel, va='center', rotation='vertical', fontsize=12)
            
            # Adjust layout
            plt.tight_layout()
            plt.subplots_adjust(left=0.1)
            
            # Save
            self.save_figure(fig, f"test_discontinuities_{data_type}.png")
            plt.close(fig)

if __name__ == '__main__':
    unittest.main() 