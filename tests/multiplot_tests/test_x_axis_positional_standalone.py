import unittest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import pathlib

# Add parent directory to path to import plotbot modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from plotbot.x_axis_positional_data_helpers import XAxisPositionalDataMapper
import plotbot as pb

class TestXAxisPositionalStandalone(unittest.TestCase):
    """Simple standalone tests for positional mapping functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use the actual data file path
        project_root = pathlib.Path(__file__).parent.parent.parent
        self.data_path = project_root / "support_data" / "trajectories" / "Parker_positional_data.npz"
        self.assertTrue(self.data_path.exists(), f"Data file not found at {self.data_path}")

    def test_direct_mapping(self):
        """Test the mapper directly without multiplot"""
        # Initialize the mapper
        mapper = XAxisPositionalDataMapper(str(self.data_path))
        self.assertTrue(mapper.data_loaded, "Positional data should load successfully")
        
        # Create a simple test date range
        center_date = pd.to_datetime("2023-09-27 23:28:00.000")  # Enc 17 perihelion
        
        # Create test dates spanning 24 hours
        test_dates = []
        for hour in range(-12, 13):
            test_dates.append(center_date + pd.Timedelta(hours=hour))
        
        # Convert to numpy array
        date_array = np.array(test_dates)
        print(f"Test dates: {date_array}")
        
        # Map to longitude
        longitudes = mapper.map_to_position(date_array, 'carrington_lon')
        
        # Verify we got valid longitudes
        self.assertIsNotNone(longitudes, "Should return valid longitudes")
        self.assertEqual(len(longitudes), len(date_array), "Should return same number of points")
        self.assertTrue(np.all((longitudes >= 0) & (longitudes <= 360)), 
                        "All longitudes should be in range 0-360°")
        
        # Print the mapping results for verification
        print("\nDirect Positional Mapping Test Results:")
        for date, lon in zip(date_array, longitudes):
            print(f"{date} -> {lon:.2f}°")
    
    def test_basic_plot(self):
        """Test creating a basic plot with positional mapping"""
        # Initialize the mapper
        mapper = XAxisPositionalDataMapper(str(self.data_path))
        
        # Create test data
        dates = pd.date_range("2023-09-27 12:00:00", "2023-09-28 12:00:00", periods=100)
        dates_np = dates.to_numpy()
        
        # Map to longitudes 
        longitudes = mapper.map_to_position(dates_np, 'carrington_lon')
        self.assertIsNotNone(longitudes)
        
        # Create some fake data that varies with longitude
        data = np.sin(np.radians(longitudes * 2)) * 10 + 20
        
        # Create plot manually
        plt.figure(figsize=(10, 5))
        plt.plot(longitudes, data, 'b-')
        plt.xlabel("Carrington Longitude (deg)")
        plt.ylabel("Test Data")
        plt.title("Test Longitude Plot")
        plt.grid(True)
        
        # Save the plot for inspection
        plt.savefig("test_longitude_plot.png")
        print("\nSaved test plot to test_longitude_plot.png")
        plt.close()
        
        # Verify data looks reasonable
        self.assertTrue(np.isfinite(data).all(), "All data points should be finite")
        
        return longitudes, data
    
    def test_minimal_multiplot(self):
        """Test the most minimal multiplot with positional axis"""
        from plotbot.multiplot_options import plt
        from plotbot.multiplot import multiplot
        
        # Store original settings
        original_settings = {
            'x_axis_carrington_lon': plt.options.x_axis_carrington_lon,
            'use_relative_time': plt.options.use_relative_time,
            'window': plt.options.window,
        }
        
        try:
            # Reset all options to defaults first
            plt.options.reset()
            
            # Configure only the absolute minimum needed 
            plt.options.x_axis_carrington_lon = True
            plt.options.window = '24:00:00.000'
            plt.options.save_output = False
            
            # Verify use_relative_time is disabled to avoid conflict
            self.assertFalse(plt.options.use_relative_time, 
                            "use_relative_time should be False by default")
            
            # Load some test data - try with magnetic field which should be available
            center_time = '2023-09-27 23:28:00.000'  # Enc 17 perihelion
            time_range = [
                '2023-09-27 12:00:00.000',  # 12 hours before
                '2023-09-28 12:00:00.000'   # 12 hours after
            ]
            pb.get_data(time_range, pb.mag_rtn_4sa.br)
            
            # Check that data loaded
            self.assertTrue(hasattr(pb.mag_rtn_4sa.br, 'datetime_array') and 
                          len(pb.mag_rtn_4sa.br.datetime_array) > 0,
                          "Should have loaded data")
            
            # Create the plot data
            plot_data = [(center_time, pb.mag_rtn_4sa.br)]
            
            # Print current settings
            print("\nCreating minimal multiplot with these settings:")
            print(f"x_axis_carrington_lon = {plt.options.x_axis_carrington_lon}")
            print(f"use_relative_time = {plt.options.use_relative_time}")
            print(f"Data points available: {len(pb.mag_rtn_4sa.br.datetime_array)}")
            
            # Create the plot
            fig, axes = multiplot(plot_data)
            
            # Check the X-axis label
            x_label = axes[0].get_xlabel().lower()
            print(f"X-axis label: '{x_label}'")
            
            # Check that longitude is mentioned in the label
            self.assertIn("longitude", x_label, "X-axis label should contain 'longitude'")
            
            # Check if there's any data on the plot
            lines = axes[0].get_lines()
            self.assertTrue(len(lines) > 0, "Plot should have at least one line")
            
            # Check that data is visible
            if lines:
                data_points = len(lines[0].get_xdata())
                print(f"Data points in plot: {data_points}")
                self.assertTrue(data_points > 0, "Plot should contain data points")
                
                # Check data type of X values
                x_data = lines[0].get_xdata()
                print(f"X-data type: {type(x_data)}")
                print(f"First few X values: {x_data[:5]}")
                
                # Save the plot
                plt.savefig("test_minimal_multiplot.png")
                print("Saved test plot to test_minimal_multiplot.png")
            
            plt.close(fig)
            
        finally:
            # Restore original settings
            for key, value in original_settings.items():
                setattr(plt.options, key, value)

    def test_complex_options_conflict_resolution(self):
        """Test that positional mapping properly resolves conflicts with other options"""
        from plotbot.multiplot_options import plt
        from plotbot.multiplot import multiplot
        
        # Store original settings
        original_settings = {
            'x_axis_carrington_lon': plt.options.x_axis_carrington_lon,
            'use_relative_time': plt.options.use_relative_time,
            'use_custom_x_axis_label': plt.options.use_custom_x_axis_label,
            'custom_x_axis_label': plt.options.custom_x_axis_label,
            'use_single_x_axis': plt.options.use_single_x_axis,
            'window': plt.options.window,
        }
        
        try:
            # Reset all options to defaults first
            plt.options.reset()
            
            # Load test data
            center_time = '2023-09-27 23:28:00.000'  # Enc 17 perihelion
            time_range = [
                '2023-09-27 12:00:00.000',  # 12 hours before
                '2023-09-28 12:00:00.000'   # 12 hours after
            ]
            pb.get_data(time_range, pb.mag_rtn_4sa.br)
            
            # 1. Test positional vs. relative time conflict
            plt.options.x_axis_carrington_lon = True
            plt.options.use_relative_time = True
            print("\nTesting with both x_axis_carrington_lon=True and use_relative_time=True")
            
            # Create the plot
            fig, axes = multiplot([(center_time, pb.mag_rtn_4sa.br)])
            
            # Check which one took precedence (should be positional over relative)
            x_label = axes[0].get_xlabel().lower()
            print(f"X-axis label: '{x_label}'")
            has_longitude = "longitude" in x_label
            has_relative = "relative" in x_label
            print(f"Has longitude in label: {has_longitude}")
            print(f"Has relative in label: {has_relative}")
            # Assert positional took precedence
            self.assertTrue(has_longitude and not has_relative, 
                          "Positional mapping should take precedence over relative time")
            plt.close(fig)
            
            # 2. Test custom axis label with positional mapping
            plt.options.reset()
            plt.options.x_axis_carrington_lon = True
            plt.options.use_custom_x_axis_label = True
            plt.options.custom_x_axis_label = "Custom Test Label"
            print("\nTesting with x_axis_carrington_lon=True and custom_x_axis_label")
                
            # Create the plot
            fig2, axes2 = multiplot([(center_time, pb.mag_rtn_4sa.br)])
            x_label2 = axes2[0].get_xlabel()
            print(f"X-axis label: '{x_label2}'")
                
            # Positional mapping should override custom label
            has_longitude2 = "longitude" in x_label2.lower()
            is_custom_label = x_label2 == "Custom Test Label"
            print(f"Has longitude in label: {has_longitude2}")
            print(f"Is custom label: {is_custom_label}")
            self.assertTrue(has_longitude2 and not is_custom_label,
                          "Positional mapping should override custom label")
            plt.close(fig2)
            
        finally:
            # Restore original settings
            for key, value in original_settings.items():
                setattr(plt.options, key, value)

if __name__ == '__main__':
    unittest.main() 