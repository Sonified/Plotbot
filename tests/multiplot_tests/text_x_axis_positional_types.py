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

# Define rainbow_encounters directly in the test file for simplicity
rainbow_encounters = [
    {'perihelion': '2018/11/06 03:27:00.000'}, #Enc 1
    {'perihelion': '2019/04/04 22:39:00.000'}, #Enc 2
    {'perihelion': '2019/09/01 17:50:00.000'}, #Enc 3
    {'perihelion': '2020/01/29 09:37:00.000'}, #Enc 4
    {'perihelion': '2020/06/07 08:23:00.000'}, #Enc 5
    {'perihelion': '2020/09/27 09:16:00.000'}, #Enc 6
    {'perihelion': '2021/01/17 17:40:00.000'}, #Enc 7
    {'perihelion': '2021/04/29 08:48:00.000'}, #Enc 8
    {'perihelion': '2021/08/09 19:11:00.000'}, #Enc 9
    {'perihelion': '2021/11/21 08:23:00.000'}, #Enc 10
    {'perihelion': '2022/02/25 15:38:00.000'}, #Enc 11 - Start from E11 for testing brevity? Or uncomment all for full 23
    {'perihelion': '2022/06/01 22:51:00.000'}, #Enc 12
    {'perihelion': '2022/09/06 06:04:00.000'}, #Enc 13
    {'perihelion': '2022/12/11 13:16:00.000'}, #Enc 14
    {'perihelion': '2023/03/17 20:30:00.000'}, #Enc 15
    {'perihelion': '2023/06/22 03:46:00.000'}, #Enc 16
    {'perihelion': '2023/09/27 23:28:00.000'}, #Enc 17
    {'perihelion': '2023/12/29 00:56:00.000'}, #Enc 18
    {'perihelion': '2024/03/30 02:21:00.000'}, #Enc 19
    {'perihelion': '2024/06/30 03:47:00.000'}, #Enc 20
    {'perihelion': '2024/09/30 05:15:00.000'}, #Enc 21
    {'perihelion': '2024/12/24 11:53:00.000'}, #Enc 22
    {'perihelion': '2025/03/22 22:42:00.000'}, #Enc 23
]

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
            'x_axis_positional_range': pbplt.options.x_axis_positional_range,
            # Add perihelion option if it exists
            **({'use_degrees_from_perihelion': getattr(pbplt.options, 'use_degrees_from_perihelion', None)} 
              if hasattr(pbplt.options, 'use_degrees_from_perihelion') else {})
        }
        print("\n[setUp] Original options stored:", self.original_settings)
        
        # Reset all options to defaults
        pbplt.options.reset()
        pbplt.options.window = '24:00:00.000'  # 24 hour window
        print("[setUp] Options reset to defaults.")
        
    def tearDown(self):
        """Restore original settings and close plots"""
        plt.close('all')
        
        # Restore original settings
        print("\n[tearDown] Restoring original options:")
        for key, value in self.original_settings.items():
            if hasattr(pbplt.options, key):
                print(f"  Restoring {key} = {value}")
                setattr(pbplt.options, key, value)
            else:
                 print(f"  Skipping restore for {key} (not found in current options)")
    
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
        
        # Reconstruct datetime array from times_numeric (seconds since epoch)
        times_datetime = pd.to_datetime(self.mapper.times_numeric * 1e9)
        ax1.plot(times_datetime[sample_indices], self.mapper.longitude_values[sample_indices], 'b-')
        ax1.set_title('Carrington Longitude Data')
        ax1.set_ylabel('Carrington Longitude (deg)')
        ax1.set_xlabel('Time')
        ax1.grid(True)
        
        # Plot radial data
        ax2.plot(sample_indices, self.mapper.radial_values[sample_indices], 'r-')
        ax2.set_title('Radial Distance Data')
        ax2.set_ylabel('Distance (R_sun)')
        ax2.grid(True)
        
        # Plot latitude data
        ax3.plot(sample_indices, self.mapper.latitude_values[sample_indices], 'g-')
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
        print("\n--- Running test_carrington_longitude_x_axis ---")
        # Configure for longitude x-axis
        pbplt.options.x_axis_carrington_lon = True
        pbplt.options.x_axis_r_sun = False
        pbplt.options.x_axis_carrington_lat = False
        print(f"[Pre-plot] Options: lon={pbplt.options.x_axis_carrington_lon}, lat={pbplt.options.x_axis_carrington_lat}, rsun={pbplt.options.x_axis_r_sun}, peri={getattr(pbplt.options, 'use_degrees_from_perihelion', 'N/A')}")
        
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
    
    def test_degrees_from_perihelion_x_axis(self):
        """Test multiplot with degrees from perihelion x-axis for multiple encounters."""
        print("\n--- Running test_degrees_from_perihelion_x_axis (Multi-Encounter) ---")

        plot_variable = pb.mag_rtn_4sa.br # Assuming this variable for plotting

        # Ensure the option exists
        if not hasattr(pbplt.options, 'use_degrees_from_perihelion'):
            self.skipTest("Option 'use_degrees_from_perihelion' not found.")
            return

        # Loop through each encounter
        # Start enumeration from 11 as per the current list, adjust if using full list
        for i, encounter_data in enumerate(rainbow_encounters, start=11):
            perihelion_time = encounter_data['perihelion']
            enc_num = i # Use the loop index as encounter number (adjust if list changes)

            print(f"\nProcessing Encounter {enc_num} ({perihelion_time})...")

            # Reset options for each plot
            pbplt.options.reset()

            # Configure plot options
            pbplt.options.window = '144:00:00.000' # +/- 72 hours = 144 hours total
            pbplt.options.position = 'around'
            pbplt.options.use_degrees_from_perihelion = True
            pbplt.options.use_single_title = True
            pbplt.options.single_title_text = f"Encounter {enc_num} (+/- 72hr) Degrees from Perihelion"
            pbplt.options.color_mode = 'single' # Use single color for clarity per plot
            pbplt.options.single_color = 'blue'
            pbplt.options.draw_vertical_line = True # Draw line at perihelion time (0 degrees)
            pbplt.options.vertical_line_color = 'red'

            # Define plot data for this specific encounter
            plot_data = [(perihelion_time, plot_variable)]

            # Ensure data for this window is loaded (multiplot handles this internally now, but good practice)
            # Calculate time range for get_data
            center_dt = pd.Timestamp(perihelion_time)
            start_dt = center_dt - pd.Timedelta(hours=72)
            end_dt = center_dt + pd.Timedelta(hours=72)
            trange_load = [start_dt.strftime('%Y-%m-%d/%H:%M:%S'), end_dt.strftime('%Y-%m-%d/%H:%M:%S')]
            try:
                pb.get_data(trange_load, plot_variable)
                # Check if data was actually loaded for the variable instance
                if not hasattr(plot_variable, 'datetime_array') or plot_variable.datetime_array is None or len(plot_variable.datetime_array) == 0:
                     print(f"Warning: No data loaded for {plot_variable.subclass_name} for Encounter {enc_num} window.")
                     # Optionally skip plot generation if no data
                     # continue
            except Exception as e:
                print(f"Error loading data for Encounter {enc_num}: {e}")
                continue # Skip this encounter if data loading fails

            # Create plot
            print(f"Generating plot for Encounter {enc_num}...")
            try:
                fig, axes = multiplot(plot_data)

                # Save image with enhanced approach
                filename = f"test_degrees_perihelion_enc{enc_num}.png"
                self.save_figure(fig, filename)
                print(f"Saved plot: {filename}")
                plt.close(fig)
            except Exception as plot_e:
                print(f"Error generating plot for Encounter {enc_num}: {plot_e}")
                # Ensure figure is closed if it exists
                if 'fig' in locals() and plt.fignum_exists(fig.number):
                    plt.close(fig)
    
    def test_r_sun_x_axis(self):
        """Test multiplot with R_sun (radial distance) x-axis"""
        print("\n--- Running test_r_sun_x_axis ---")
        # Configure for R_sun x-axis
        pbplt.options.x_axis_carrington_lon = False
        pbplt.options.x_axis_r_sun = True
        pbplt.options.x_axis_carrington_lat = False
        print(f"[Pre-plot] Options: lon={pbplt.options.x_axis_carrington_lon}, lat={pbplt.options.x_axis_carrington_lat}, rsun={pbplt.options.x_axis_r_sun}, peri={getattr(pbplt.options, 'use_degrees_from_perihelion', 'N/A')}")
        
        # Create plot
        fig, axes = multiplot([(self.center_time, pb.mag_rtn_4sa.br)])
        
        # Check x-axis label contains "radial" or "r_sun"
        x_label = axes[0].get_xlabel().lower()
        print(f"[Post-plot] Actual x-label: '{x_label}'")
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
        print("\n--- Running test_carrington_latitude_x_axis ---")
        # Configure for latitude x-axis
        pbplt.options.x_axis_carrington_lon = False
        pbplt.options.x_axis_r_sun = False
        pbplt.options.x_axis_carrington_lat = True
        print(f"[Pre-plot] Options: lon={pbplt.options.x_axis_carrington_lon}, lat={pbplt.options.x_axis_carrington_lat}, rsun={pbplt.options.x_axis_r_sun}, peri={getattr(pbplt.options, 'use_degrees_from_perihelion', 'N/A')}")
        
        # Create plot
        fig, axes = multiplot([(self.center_time, pb.mag_rtn_4sa.br)])
        
        # Check x-axis label contains "latitude"
        x_label = axes[0].get_xlabel().lower()
        print(f"[Post-plot] Actual x-label: '{x_label}'")
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
        print("\n--- Running test_multiple_positional_options_conflict ---")
        # Reset options
        pbplt.options.reset()
        print("[Conflict Test 1] Options reset.")
        
        # Set options in sequence - last one should win
        pbplt.options.x_axis_carrington_lon = True
        pbplt.options.x_axis_r_sun = True
        pbplt.options.x_axis_carrington_lat = True  # This should be the one used
        print(f"[Conflict Test 1 - Pre-plot] Options: lon={pbplt.options.x_axis_carrington_lon}, lat={pbplt.options.x_axis_carrington_lat}, rsun={pbplt.options.x_axis_r_sun}, peri={getattr(pbplt.options, 'use_degrees_from_perihelion', 'N/A')}, active={pbplt.options.active_positional_data_type}")
        
        # Create plot
        fig, axes = multiplot([(self.center_time, pb.mag_rtn_4sa.br)])
        
        # Check that latitude is the active type since it was set last
        print(f"[Conflict Test 1 - Post-plot] Active type: {pbplt.options.active_positional_data_type}, Expected: carrington_lat")
        self.assertEqual(pbplt.options.active_positional_data_type, 'carrington_lat')
        
        # Check x-axis label contains "latitude"
        x_label = axes[0].get_xlabel().lower()
        self.assertIn("latitude", x_label)
        
        # Save image with enhanced approach
        self.save_figure(fig, "test_priority_latitude.png")
        plt.close(fig)
        
        # Try in a different order - longitude should win
        pbplt.options.reset()
        print("\n[Conflict Test 2] Options reset.")
        pbplt.options.x_axis_r_sun = True
        pbplt.options.x_axis_carrington_lat = True
        pbplt.options.x_axis_carrington_lon = True  # This should be the one used
        print(f"[Conflict Test 2 - Pre-plot] Options: lon={pbplt.options.x_axis_carrington_lon}, lat={pbplt.options.x_axis_carrington_lat}, rsun={pbplt.options.x_axis_r_sun}, peri={getattr(pbplt.options, 'use_degrees_from_perihelion', 'N/A')}, active={pbplt.options.active_positional_data_type}")
        
        # Create plot
        fig, axes = multiplot([(self.center_time, pb.mag_rtn_4sa.br)])
        
        # Check that longitude is the active type since it was set last
        print(f"[Conflict Test 2 - Post-plot] Active type: {pbplt.options.active_positional_data_type}, Expected: carrington_lon")
        self.assertEqual(pbplt.options.active_positional_data_type, 'carrington_lon')
        
        # Check x-axis label contains "longitude"
        x_label = axes[0].get_xlabel().lower()
        self.assertIn("longitude", x_label)
        
        # Save image with enhanced approach
        self.save_figure(fig, "test_priority_longitude.png")
        plt.close(fig)
    
    def test_dynamic_plotting_with_all_types(self):
        """Test plotting with all three positional data types in sequence"""
        print("\n--- Running test_dynamic_plotting_with_all_types ---")
        # Test all three types in sequence
        data_types = [
            {'name': 'Carrington Longitude', 'setting': 'x_axis_carrington_lon', 'expected': 'longitude'},
            {'name': 'Radial Distance', 'setting': 'x_axis_r_sun', 'expected': 'distance'},
            {'name': 'Carrington Latitude', 'setting': 'x_axis_carrington_lat', 'expected': 'latitude'},
            # Add perihelion test here
            {'name': 'Degrees from Perihelion', 'setting': 'use_degrees_from_perihelion', 'expected': 'degrees from perihelion'}
        ]
        
        for data_type in data_types:
            print(f"\n[Dynamic Test] Testing {data_type['name']} x-axis")
            
            # Reset options
            pbplt.options.reset()
            pbplt.options.window = '24:00:00.000'
            print("[Dynamic Test] Options reset.")
            
            # Set only this data type
            # Check if attribute exists before setting
            if hasattr(pbplt.options, data_type['setting']):
                setattr(pbplt.options, data_type['setting'], True)
                print(f"[Dynamic Test - Pre-plot] Set {data_type['setting']}=True")
                print(f"  Options: lon={pbplt.options.x_axis_carrington_lon}, lat={pbplt.options.x_axis_carrington_lat}, rsun={pbplt.options.x_axis_r_sun}, peri={getattr(pbplt.options, 'use_degrees_from_perihelion', 'N/A')}")
            else:
                self.skipTest(f"Option '{data_type['setting']}' not found.")
                continue # Skip to next data type
            
            # Create plot
            fig, axes = multiplot([(self.center_time, pb.mag_rtn_4sa.br)])
            
            # Verify x-axis label
            x_label = axes[0].get_xlabel().lower()
            print(f"[Dynamic Test - Post-plot] Actual x-label: '{x_label}'")
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
    
    def test_carrington_longitude_perihelion_windows(self):
        """Plot Carrington longitude vs. time for ±36 hours around each perihelion encounter."""
        for i, encounter in enumerate(rainbow_encounters, start=1):
            perihelion_time = pd.to_datetime(encounter['perihelion'])
            start_time = perihelion_time - pd.Timedelta(hours=36)
            end_time = perihelion_time + pd.Timedelta(hours=36)
            times_window = pd.date_range(start_time, end_time, periods=500)
            times_window_np = times_window.to_numpy()
            longitude_window = self.mapper.map_to_position(times_window_np, 'carrington_lon')

            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(times_window, longitude_window, 'b-')
            ax.set_title(f'Carrington Longitude vs Time\nEncounter {i} ({perihelion_time.strftime("%Y-%m-%d %H:%M")})')
            ax.set_ylabel('Carrington Longitude (deg)')
            ax.set_xlabel('Time')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            ax.grid(True)
            fig.autofmt_xdate()

            # Add red dashed vertical line at perihelion
            ax.axvline(perihelion_time, color='red', linestyle='--', linewidth=2)

            # Find Carrington longitude at perihelion
            idx_peri = np.argmin(np.abs(times_window_np - np.datetime64(perihelion_time)))
            peri_lon = longitude_window[idx_peri]
            y_min, y_max = ax.get_ylim()
            y_mid = y_min + 0.5 * (y_max - y_min)

            # Annotate perihelion inside plot, to the right of the red line, at mid-y
            ax.annotate(
                f'Perihelion\n{perihelion_time.strftime("%Y-%m-%d %H:%M")}',
                xy=(perihelion_time, y_mid),
                xytext=(20, 0), textcoords='offset points',
                ha='left', va='center', color='red', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='red', lw=1, alpha=0.7),
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5)
            )

            # Draw horizontal dashed line at Carrington longitude at perihelion
            ax.axhline(peri_lon, color='red', linestyle='dashed', linewidth=1)
            # Annotate the longitude value
            ax.annotate(
                f'{peri_lon:.2f}°',
                xy=(perihelion_time, peri_lon),
                xytext=(30, -20), textcoords='offset points',
                ha='left', va='center', color='red', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='red', lw=1, alpha=0.7),
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5)
            )

            filename = f'carrington_longitude_enc{i:02d}.png'
            self.save_figure(fig, filename)
            plt.close(fig)
    
    def test_rainbow_longitude_offset(self):
        """Rainbow plot: Carrington longitude relative to perihelion for each encounter (±3 days), using mag_rtn_4sa.br as y-axis."""
        # Load trajectory data from NPZ
        data = np.load(self.data_path)
        tlongits = pd.to_datetime(data['times'])
        longits = data['carrington_lon']
        tlongits_np = tlongits.to_numpy()
        tlongits_sec = tlongits_np.astype('datetime64[ns]').astype(np.int64) / 1e9

        encounters = [
            '2018-11-06T03:27:00.000', '2019-04-04T22:39:00.000', '2019-09-01T17:50:00.000',
            '2020-01-29T09:37:00.000', '2020-06-07T08:23:00.000', '2020-09-27T09:16:00.000',
            '2021-01-17T17:40:00.000', '2021-04-29T08:48:00.000', '2021-08-09T19:11:00.000',
            '2021-11-21T08:23:00.000', '2022-02-25T15:38:00.000', '2022-06-01T22:51:00.000',
            '2022-09-06T06:04:00.000', '2022-12-11T13:16:00.000', '2023-03-17T20:30:00.000',
            '2023-06-22T03:46:00.000', '2023-09-27T23:28:00.000', '2023-12-29T00:56:00.000',
            '2024-03-30T02:21:00.000', '2024-06-30T03:47:00.000', '2024-09-30T05:15:00.000',
            '2024-12-24T11:53:00.000', '2025-03-22T22:42:00.000'
        ]
        num_enc = len(encounters)
        x_plot_list, y_plot_list = [], []
        day_range = 3
        for enc in encounters:
            enc_dt = pd.to_datetime(enc)
            start_time = enc_dt - pd.Timedelta(days=day_range)
            end_time = enc_dt + pd.Timedelta(days=day_range)
            trange = [start_time.strftime('%Y-%m-%d/%H:%M:%S'), end_time.strftime('%Y-%m-%d/%H:%M:%S')]
            # Load magnetic field data for this window
            pb.get_data(trange, pb.mag_rtn_4sa.br)
            time_us = pb.mag_rtn_4sa.br.datetime_array
            y_var = pb.mag_rtn_4sa.br.data
            if len(time_us) == 0 or len(y_var) == 0:
                x_plot_list.append([])
                y_plot_list.append([])
                continue
            # Interpolate longitude to match science data timestamps
            time_us_sec = time_us.astype('datetime64[ns]').astype(np.int64) / 1e9
            long_us = np.interp(time_us_sec, tlongits_sec, longits)
            # Find perihelion index and offset
            peri_sec = enc_dt.to_datetime64().astype('datetime64[ns]').astype(np.int64) / 1e9
            peri_ind = np.argmin(np.abs(time_us_sec - peri_sec))
            peri_offset = long_us[peri_ind]
            long_off = long_us - peri_offset
            x_plot_list.append(long_off)
            y_plot_list.append(y_var)
        # Plot
        color_map = plt.cm.get_cmap('gist_rainbow')
        color_range = np.linspace(0, 1, num_enc)
        fig, ax = plt.subplots(num_enc, 1, figsize=(8, num_enc * 0.6), sharex=True)
        for i in range(num_enc):
            color = color_map(color_range[i])
            if len(x_plot_list[i]) > 0:
                ax[i].plot(x_plot_list[i], y_plot_list[i], color=color, linewidth=2)
            ax[i].set_ylabel(f'E{i+1}')
            ax[i].axvline(0, color='k', linestyle='--', linewidth=1)
        ax[-1].set_xlabel('Carrington longitude relative to perihelion (deg)')
        fig.suptitle('Carrington Longitude Offset Rainbow Plot (±3 days)')
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        self.save_figure(fig, 'rainbow_longitude_offset_test.png')
        plt.close(fig)

if __name__ == '__main__':
    unittest.main() 