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
import matplotlib.dates as mdates  # Add missing import for date formatting

# Add parent directory to path to import plotbot modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

import plotbot as pb
from plotbot.multiplot_options import plt as pbplt
from plotbot.multiplot import multiplot
from plotbot.x_axis_positional_data_helpers import XAxisPositionalDataMapper

class TestPositionalXAxisTypes(unittest.TestCase):
    """Test all three positional data types (r_sun, carrington_lon, carrington_lat) as x-axis options"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use the actual data file path
        project_root = pathlib.Path(__file__).parent.parent.parent
        self.data_path = project_root / "support_data" / "trajectories" / "Parker_positional_data.npz"
        self.assertTrue(self.data_path.exists(), f"Data file not found at {self.data_path}")
        
        # Set up the directory for saving test images
        self.image_dir = project_root / "local_images"
        self.assertTrue(self.image_dir.exists(), f"Image directory not found at {self.image_dir}")
        
        # Create a mapper instance for direct testing
        self.mapper = XAxisPositionalDataMapper(str(self.data_path))
        self.assertTrue(self.mapper.data_loaded, "Positional data should load successfully")
        
        # Set test center time and data range
        self.center_time = '2023-09-27 23:28:00.000'  # Enc 17 perihelion
        self.time_range = [
            '2023-09-27 12:00:00.000',  # 12 hours before
            '2023-09-28 12:00:00.000'   # 12 hours after
        ]
        
        # Load sample data for plotting
        pb.get_data(self.time_range, pb.mag_rtn_4sa.br)
        
        # Skip tests if data is not available
        if not hasattr(pb.mag_rtn_4sa.br, 'datetime_array') or len(pb.mag_rtn_4sa.br.datetime_array) == 0:
            self.skipTest("Skipping tests - no magnetic field data available")
        
        # Store original options to restore after tests
        self.original_settings = {
            'x_axis_carrington_lon': pbplt.options.x_axis_carrington_lon,
            'x_axis_carrington_lat': pbplt.options.x_axis_carrington_lat,
            'x_axis_r_sun': pbplt.options.x_axis_r_sun,
            'use_relative_time': pbplt.options.use_relative_time,
            'window': pbplt.options.window,
            'x_axis_positional_range': pbplt.options.x_axis_positional_range
        }
        
        # Reset all options to defaults
        pbplt.options.reset()
        pbplt.options.window = '24:00:00.000'  # 24 hour window
        
    def tearDown(self):
        """Restore original settings and close plots"""
        plt.close('all')
        
        # Restore original settings
        for key, value in self.original_settings.items():
            setattr(pbplt.options, key, value)
    
    def save_figure(self, fig, filename):
        """Helper method to properly render and save a figure"""
        # Make sure the figure is fully rendered
        fig.tight_layout()
        fig.canvas.draw()
        
        # Save with high quality
        filepath = os.path.join(self.image_dir, filename)
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"Saved image to {filepath}")
        return filepath
    
    def test_mapper_data_availability(self):
        """Verify the mapper has all three data types available"""
        # Check that the mapper has all three data arrays
        self.assertIsNotNone(self.mapper.longitude_values)
        self.assertIsNotNone(self.mapper.radial_values)
        self.assertIsNotNone(self.mapper.latitude_values)
        
        # Ensure all arrays have the same length as times
        self.assertEqual(len(self.mapper.longitude_values), len(self.mapper.times_numeric))
        self.assertEqual(len(self.mapper.radial_values), len(self.mapper.times_numeric))
        self.assertEqual(len(self.mapper.latitude_values), len(self.mapper.times_numeric))
        
        # Check that values are within expected ranges
        self.assertTrue(np.all((self.mapper.longitude_values >= 0) & (self.mapper.longitude_values <= 360)))
        self.assertTrue(np.all(self.mapper.radial_values > 0))  # R_sun should be positive
        self.assertTrue(np.all((self.mapper.latitude_values >= -90) & (self.mapper.latitude_values <= 90)))
        
        # Print range information for each data type
        print(f"\nCarrington Longitude range: {np.min(self.mapper.longitude_values):.2f}° to {np.max(self.mapper.longitude_values):.2f}°")
        print(f"R_sun range: {np.min(self.mapper.radial_values):.2f} to {np.max(self.mapper.radial_values):.2f}")
        print(f"Carrington Latitude range: {np.min(self.mapper.latitude_values):.2f}° to {np.max(self.mapper.latitude_values):.2f}°")
        
        # Create a simple plot showing data ranges
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
        
        # Sample points for plotting
        sample_indices = np.linspace(0, len(self.mapper.times_numeric)-1, 1000, dtype=int)
        
        # Plot longitude data
        ax1.plot(self.mapper.longitude_values[sample_indices], 'b-')
        ax1.set_title('Carrington Longitude Data')
        ax1.set_ylabel('Longitude (degrees)')
        ax1.grid(True)
        
        # Plot radial data
        ax2.plot(self.mapper.radial_values[sample_indices], 'r-')
        ax2.set_title('Radial Distance Data')
        ax2.set_ylabel('Distance (R_sun)')
        ax2.grid(True)
        
        # Plot latitude data
        ax3.plot(self.mapper.latitude_values[sample_indices], 'g-')
        ax3.set_title('Carrington Latitude Data')
        ax3.set_ylabel('Latitude (degrees)')
        ax3.set_xlabel('Sample Index')
        ax3.grid(True)
        
        # Save the data overview plot
        self.save_figure(fig, "positional_data_overview.png")
        plt.close(fig)
    
    def test_mapping_functionality(self):
        """Test that all three mapping types work with the map_to_position method"""
        # Create a sample datetime array
        dates = pd.date_range(self.time_range[0], self.time_range[1], periods=100)
        dates_np = dates.to_numpy()
        
        # Test mapping for each data type
        longitude_values = self.mapper.map_to_position(dates_np, 'carrington_lon')
        radial_values = self.mapper.map_to_position(dates_np, 'r_sun')
        latitude_values = self.mapper.map_to_position(dates_np, 'carrington_lat')
        
        # Check that all mappings returned valid data
        self.assertIsNotNone(longitude_values)
        self.assertIsNotNone(radial_values)
        self.assertIsNotNone(latitude_values)
        
        # Check dimensions
        self.assertEqual(len(longitude_values), len(dates_np))
        self.assertEqual(len(radial_values), len(dates_np))
        self.assertEqual(len(latitude_values), len(dates_np))
        
        # Print first few mapped values for each type
        print("\nSample mapped values:")
        for i in range(min(5, len(dates_np))):
            print(f"{dates_np[i]} -> Lon: {longitude_values[i]:.2f}°, R_sun: {radial_values[i]:.2f}, Lat: {latitude_values[i]:.2f}°")
        
        # Create a visualization of the mapping
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
        
        # Convert dates to matplotlib format for plotting
        date_nums = mdates.date2num(dates)
        
        # Plot mappings
        ax1.plot(date_nums, longitude_values, 'b-')
        ax1.set_title('Time to Longitude Mapping')
        ax1.set_ylabel('Longitude (degrees)')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax1.grid(True)
        
        ax2.plot(date_nums, radial_values, 'r-')
        ax2.set_title('Time to Radial Distance Mapping')
        ax2.set_ylabel('Distance (R_sun)')
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax2.grid(True)
        
        ax3.plot(date_nums, latitude_values, 'g-')
        ax3.set_title('Time to Latitude Mapping')
        ax3.set_ylabel('Latitude (degrees)')
        ax3.set_xlabel('Time')
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax3.grid(True)
        
        fig.autofmt_xdate()  # Rotate date labels for better visibility
        
        # Save the mapping visualization
        self.save_figure(fig, "time_to_position_mapping.png")
        plt.close(fig)
    
    def test_carrington_longitude_x_axis(self):
        """Test multiplot with Carrington longitude x-axis"""
        # Configure for longitude x-axis
        pbplt.options.x_axis_carrington_lon = True
        pbplt.options.x_axis_r_sun = False
        pbplt.options.x_axis_carrington_lat = False
        
        # Create plot
        fig, axes = multiplot([(self.center_time, pb.mag_rtn_4sa.br)])
        
        # Check x-axis label contains "longitude"
        x_label = axes[0].get_xlabel().lower()
        self.assertIn("longitude", x_label)
        
        # Get some x-data to verify it's in the longitude range
        lines = axes[0].get_lines()
        if lines:
            x_data = lines[0].get_xdata()
            self.assertTrue(np.all((x_data >= 0) & (x_data <= 360)))
        
        # Save image with enhanced approach
        self.save_figure(fig, "test_carrington_longitude.png")
        plt.close(fig)
    
    def test_r_sun_x_axis(self):
        """Test multiplot with R_sun (radial distance) x-axis"""
        # Configure for R_sun x-axis
        pbplt.options.x_axis_carrington_lon = False
        pbplt.options.x_axis_r_sun = True
        pbplt.options.x_axis_carrington_lat = False
        
        # Create plot
        fig, axes = multiplot([(self.center_time, pb.mag_rtn_4sa.br)])
        
        # Check x-axis label contains "radial" or "r_sun"
        x_label = axes[0].get_xlabel().lower()
        self.assertTrue("radial" in x_label or "r_sun" in x_label or "distance" in x_label)
        
        # Get some x-data to verify it's in a reasonable R_sun range
        lines = axes[0].get_lines()
        if lines:
            x_data = lines[0].get_xdata()
            self.assertTrue(np.all(x_data > 0))  # R_sun should be positive
        
        # Save image with enhanced approach
        self.save_figure(fig, "test_r_sun.png")
        plt.close(fig)
    
    def test_carrington_latitude_x_axis(self):
        """Test multiplot with Carrington latitude x-axis"""
        # Configure for latitude x-axis
        pbplt.options.x_axis_carrington_lon = False
        pbplt.options.x_axis_r_sun = False
        pbplt.options.x_axis_carrington_lat = True
        
        # Create plot
        fig, axes = multiplot([(self.center_time, pb.mag_rtn_4sa.br)])
        
        # Check x-axis label contains "latitude"
        x_label = axes[0].get_xlabel().lower()
        self.assertIn("latitude", x_label)
        
        # Get some x-data to verify it's in the latitude range
        lines = axes[0].get_lines()
        if lines:
            x_data = lines[0].get_xdata()
            self.assertTrue(np.all((x_data >= -90) & (x_data <= 90)))
        
        # Save image with enhanced approach
        self.save_figure(fig, "test_carrington_latitude.png")
        plt.close(fig)
    
    def test_multiple_positional_options_conflict(self):
        """Test that the most recently set positional x-axis option takes precedence"""
        # Reset options
        pbplt.options.reset()
        
        # Set options in sequence - last one should win
        pbplt.options.x_axis_carrington_lon = True
        pbplt.options.x_axis_r_sun = True
        pbplt.options.x_axis_carrington_lat = True  # This should be the one used
        
        # Create plot
        fig, axes = multiplot([(self.center_time, pb.mag_rtn_4sa.br)])
        
        # Check that latitude is the active type since it was set last
        self.assertEqual(pbplt.options.active_positional_data_type, 'carrington_lat')
        
        # Check x-axis label contains "latitude"
        x_label = axes[0].get_xlabel().lower()
        self.assertIn("latitude", x_label)
        
        # Save image with enhanced approach
        self.save_figure(fig, "test_priority_latitude.png")
        plt.close(fig)
        
        # Try in a different order - longitude should win
        pbplt.options.reset()
        pbplt.options.x_axis_r_sun = True
        pbplt.options.x_axis_carrington_lat = True
        pbplt.options.x_axis_carrington_lon = True  # This should be the one used
        
        # Create plot
        fig, axes = multiplot([(self.center_time, pb.mag_rtn_4sa.br)])
        
        # Check that longitude is the active type since it was set last
        self.assertEqual(pbplt.options.active_positional_data_type, 'carrington_lon')
        
        # Check x-axis label contains "longitude"
        x_label = axes[0].get_xlabel().lower()
        self.assertIn("longitude", x_label)
        
        # Save image with enhanced approach
        self.save_figure(fig, "test_priority_longitude.png")
        plt.close(fig)
    
    def test_dynamic_plotting_with_all_types(self):
        """Test plotting with all three positional data types in sequence"""
        
        # Test all three types in sequence
        data_types = [
            {'name': 'Carrington Longitude', 'setting': 'x_axis_carrington_lon', 'expected': 'longitude'},
            {'name': 'Radial Distance', 'setting': 'x_axis_r_sun', 'expected': 'distance'},
            {'name': 'Carrington Latitude', 'setting': 'x_axis_carrington_lat', 'expected': 'latitude'}
        ]
        
        for data_type in data_types:
            print(f"\nTesting {data_type['name']} x-axis")
            
            # Reset options
            pbplt.options.reset()
            pbplt.options.window = '24:00:00.000'
            
            # Set only this data type
            setattr(pbplt.options, data_type['setting'], True)
            
            # Create plot
            fig, axes = multiplot([(self.center_time, pb.mag_rtn_4sa.br)])
            
            # Verify x-axis label
            x_label = axes[0].get_xlabel().lower()
            self.assertIn(data_type['expected'], x_label, 
                         f"X-axis label should contain '{data_type['expected']}', got '{x_label}'")
            
            # Save with enhanced approach
            filename = f"test_{data_type['name'].lower().replace(' ', '_')}_xaxis.png"
            self.save_figure(fig, filename)
            plt.close(fig)
    
    def test_positional_range_option(self):
        """Test the x_axis_positional_range option for all positional data types"""
        
        # Test cases for each data type with custom ranges
        test_cases = [
            {
                'name': 'Carrington Longitude',
                'setting': 'x_axis_carrington_lon',
                'range': (120, 180),  # Custom longitude range in degrees
                'filename': 'test_longitude_fixed_range.png'
            },
            {
                'name': 'Radial Distance',
                'setting': 'x_axis_r_sun',
                'range': (11, 14),  # Custom radial range in R_sun
                'filename': 'test_rsun_fixed_range.png'
            },
            {
                'name': 'Carrington Latitude',
                'setting': 'x_axis_carrington_lat',
                'range': (-4, -1),  # Custom latitude range in degrees
                'filename': 'test_latitude_fixed_range.png'
            }
        ]
        
        for case in test_cases:
            print(f"\nTesting {case['name']} with fixed range {case['range']}")
            
            # Reset options
            pbplt.options.reset()
            pbplt.options.window = '24:00:00.000'
            
            # Set positional x-axis type and custom range
            setattr(pbplt.options, case['setting'], True)
            pbplt.options.x_axis_positional_range = case['range']
            
            # Create plot
            fig, axes = multiplot([(self.center_time, pb.mag_rtn_4sa.br)])
            
            # Verify the x-axis limits are set to our custom range
            x_min, x_max = axes[0].get_xlim()
            min_range, max_range = case['range']
            
            # Check that limits match our specified range (with small tolerance for floating point)
            self.assertAlmostEqual(x_min, min_range, delta=0.1, 
                                 msg=f"X-axis minimum should be {min_range}, got {x_min}")
            self.assertAlmostEqual(x_max, max_range, delta=0.1,
                                 msg=f"X-axis maximum should be {max_range}, got {x_max}")
            
            # Save the image
            self.save_figure(fig, case['filename'])
            plt.close(fig)
    
    def test_common_x_axis_with_multiple_panels(self):
        """Test using common x-axis with multiple panels of positional data"""
        # Reset options
        pbplt.options.reset()
        
        # Configure for multiple panels with common x-axis
        pbplt.options.window = '24:00:00.000'
        pbplt.options.use_single_x_axis = True
        pbplt.options.x_axis_carrington_lon = True
        
        # Create a plot with three panels
        fig, axes = multiplot([
            (self.center_time, pb.mag_rtn_4sa.br),
            (self.center_time, pb.mag_rtn_4sa.bt),
            (self.center_time, pb.mag_rtn_4sa.bn)
        ])
        
        # Verify all panels have the same x-axis range
        x_ranges = [ax.get_xlim() for ax in axes]
        
        # All panels should have the same range as the bottom panel
        for i in range(len(axes)-1):
            self.assertEqual(x_ranges[i], x_ranges[-1], 
                           f"Panel {i+1} should have same x-range as bottom panel")
            
        # Only the bottom panel should have x-tick labels
        for i in range(len(axes)-1):
            tick_labels = [t.get_text() for t in axes[i].get_xticklabels()]
            self.assertTrue(all(t == '' for t in tick_labels), 
                          f"Panel {i+1} should have empty x-tick labels")
        
        # Save the result
        self.save_figure(fig, "test_common_x_axis_multiplot.png")
        plt.close(fig)
        
        # Now test with fixed range
        pbplt.options.x_axis_positional_range = (140, 160)
        
        fig, axes = multiplot([
            (self.center_time, pb.mag_rtn_4sa.br),
            (self.center_time, pb.mag_rtn_4sa.bt),
            (self.center_time, pb.mag_rtn_4sa.bn)
        ])
        
        # Verify all panels have our fixed range
        for i, ax in enumerate(axes):
            x_min, x_max = ax.get_xlim()
            self.assertAlmostEqual(x_min, 140, delta=0.1)
            self.assertAlmostEqual(x_max, 160, delta=0.1)
        
        # Save the result
        self.save_figure(fig, "test_common_x_axis_fixed_range.png")
        plt.close(fig)
    
if __name__ == '__main__':
    unittest.main() 