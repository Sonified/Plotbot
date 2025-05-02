import unittest
import numpy as np
import pandas as pd
from datetime import datetime
import plotbot as pb
from plotbot.x_axis_positional_data_helpers import XAxisPositionalDataMapper
import os
import pathlib

class TestXAxisPositionalData(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Use the actual data file path
        project_root = pathlib.Path(__file__).parent.parent
        data_path = project_root / "support_data" / "trajectories" / "Parker_positional_data.npz"
        self.assertTrue(data_path.exists(), f"Data file not found at {data_path}")
        self.mapper = XAxisPositionalDataMapper(str(data_path))
        
        # Also load the raw positional data for format tests
        self.raw_positional_data = np.load(data_path)

    def test_attributes(self):
        """Test that the mapper has the expected attributes after initialization"""
        self.assertIsNotNone(self.mapper)
        self.assertTrue(hasattr(self.mapper, 'data_path'))
        self.assertTrue(hasattr(self.mapper, 'data_loaded'))
        self.assertTrue(hasattr(self.mapper, 'times_numeric'))
        self.assertTrue(hasattr(self.mapper, 'longitude_values'))
        self.assertTrue(hasattr(self.mapper, 'radial_values'))
        self.assertTrue(hasattr(self.mapper, 'latitude_values'))
        
    def test_data_loading(self):
        """Test that positional data loads correctly"""
        self.assertTrue(self.mapper.data_loaded)
        self.assertIsNotNone(self.mapper.times_numeric)
        self.assertIsNotNone(self.mapper.longitude_values)
        
        # Check data structure
        self.assertIsInstance(self.mapper.times_numeric, np.ndarray)
        self.assertIsInstance(self.mapper.longitude_values, np.ndarray)
        
        # Verify we have a reasonable amount of data
        self.assertGreater(len(self.mapper.times_numeric), 0)
        self.assertEqual(len(self.mapper.times_numeric), len(self.mapper.longitude_values))
        
        # Verify the data ranges are sensible for Carrington longitude (0-360)
        self.assertGreaterEqual(np.min(self.mapper.longitude_values), 0)
        self.assertLessEqual(np.max(self.mapper.longitude_values), 360)
    
    def test_positional_data_format(self):
        """Test the format of the raw positional data matches the expected format for processing"""
        # Check that the NPZ file has the expected keys
        self.assertIn('times', self.raw_positional_data)
        self.assertIn('carrington_lon', self.raw_positional_data)
        
        # Test that times can be converted to datetime64
        times_raw = self.raw_positional_data['times']
        # This is what the XAxisPositionalDataMapper does internally
        try:
            datetime_array_pd = pd.to_datetime(times_raw, utc=True).tz_convert(None)
            datetime_array_np = datetime_array_pd.to_numpy()
            numeric_times = datetime_array_np.astype(np.int64) / 1e9
            
            self.assertTrue(isinstance(numeric_times, np.ndarray))
            self.assertTrue(np.issubdtype(numeric_times.dtype, np.floating))
        except Exception as e:
            self.fail(f"Failed to convert raw times to numeric format: {str(e)}")
    
    def test_timestamp_interpolation(self):
        """Test the interpolation of timestamps to positions"""
        # Convert a numeric timestamp back to datetime64 for testing
        if len(self.mapper.times_numeric) > 2:
            # Create a timestamp midway in the data range
            midpoint_idx = len(self.mapper.times_numeric) // 2
            midpoint_timestamp_sec = self.mapper.times_numeric[midpoint_idx]
            midpoint_timestamp = np.array([np.datetime64('1970-01-01') + np.timedelta64(int(midpoint_timestamp_sec * 1e9), 'ns')])
            
            # Map this timestamp to position (longitude)
            longitude = self.mapper.map_to_position(midpoint_timestamp, 'carrington_lon')
            
            # Should return a valid longitude for a timestamp within the data range
            self.assertIsNotNone(longitude)
            self.assertIsInstance(longitude, np.ndarray)
            self.assertEqual(len(longitude), 1)
            
            # Longitude should be in valid range
            self.assertGreaterEqual(longitude[0], 0)
            self.assertLessEqual(longitude[0], 360)
            
            # Verify that the interpolated value is close to the actual value at that time
            # This directly tests the interpolation accuracy
            expected_longitude = self.mapper.longitude_values[midpoint_idx]
            self.assertAlmostEqual(longitude[0], expected_longitude, delta=0.01,
                                 msg="Interpolation at exact datapoint should return original value")
    
    def test_out_of_range_timestamps(self):
        """Test handling of timestamps outside the positional data range"""
        if len(self.mapper.times_numeric) > 0:
            # Convert to datetime64 for testing
            first_timestamp_sec = self.mapper.times_numeric[0]
            first_timestamp = np.datetime64('1970-01-01') + np.timedelta64(int(first_timestamp_sec * 1e9), 'ns')
            
            # Create timestamps outside the data range
            early_timestamp = np.array([first_timestamp - np.timedelta64(10, 'D')])
            longitude = self.mapper.map_to_position(early_timestamp, 'carrington_lon')
            
            # Implementation might either return None or extrapolate
            if longitude is not None:
                self.assertIsInstance(longitude, np.ndarray)
                self.assertEqual(len(longitude), 1)
            
            # Test with timestamp after the last longitude time
            last_timestamp_sec = self.mapper.times_numeric[-1]
            last_timestamp = np.datetime64('1970-01-01') + np.timedelta64(int(last_timestamp_sec * 1e9), 'ns')
            late_timestamp = np.array([last_timestamp + np.timedelta64(10, 'D')])
            longitude = self.mapper.map_to_position(late_timestamp, 'carrington_lon')
            
            if longitude is not None:
                self.assertIsInstance(longitude, np.ndarray)
                self.assertEqual(len(longitude), 1)
    
    def test_format_compatibility(self):
        """Test format compatibility between positional data and science data"""
        try:
            # Use a small sample of science data for quick testing
            time_range = ['2021/04/26 00:00:00.000', '2021/04/26 02:00:00.000']  # Just 2 hours
            
            # Get minimal magnetic field data for testing
            pb.get_data(time_range, pb.mag_rtn_4sa.br)
            
            # Skip test if data is not available
            if not hasattr(pb.mag_rtn_4sa.br, 'datetime_array') or len(pb.mag_rtn_4sa.br.datetime_array) == 0:
                self.skipTest("Skipping test - no magnetic field data available")
                return
                
            # Get the datetime array from the magnetic field data
            mag_dt_array = pb.mag_rtn_4sa.br.datetime_array
            
            # Examine the format of the datetime array
            self.assertTrue(isinstance(mag_dt_array, np.ndarray), 
                          f"Expected numpy array, got {type(mag_dt_array)}")
            self.assertTrue(np.issubdtype(mag_dt_array.dtype, np.datetime64),
                          f"Expected np.datetime64 dtype, got {mag_dt_array.dtype}")
            
            # Verify that the position mapper can handle this format
            # This tests the critical format compatibility
            longitudes = self.mapper.map_to_position(mag_dt_array, 'carrington_lon')
            self.assertIsNotNone(longitudes, "Position mapping returned None for valid mag data")
            self.assertEqual(len(longitudes), len(mag_dt_array))
            
            # Check if all longitudes are within valid range
            self.assertTrue(np.all((longitudes >= 0) & (longitudes <= 360)))
            
            # Test format conversion in the mapper
            # This tests that the datetime array from science data can be converted to numeric times
            # in the same way that the position times are converted
            try:
                # The critical conversion step in map_to_position
                science_times_numeric = mag_dt_array.astype(np.int64) / 1e9
                self.assertTrue(isinstance(science_times_numeric, np.ndarray))
                self.assertTrue(np.issubdtype(science_times_numeric.dtype, np.floating))
                
                # Test that these numeric values are in the same range/format as the mapper's times_numeric
                # Not exact match, but similar order of magnitude (seconds since epoch)
                self.assertGreater(np.min(science_times_numeric), 1e9)  # After year 2000
                
                # Test manual interpolation with these values
                manual_interpolated = np.interp(
                    science_times_numeric, 
                    self.mapper.times_numeric,
                    self.mapper.longitude_values
                )
                
                # Compare manual interpolation with mapper's result
                self.assertTrue(np.allclose(manual_interpolated, longitudes),
                              "Manual interpolation should match mapper's result")
                
            except Exception as e:
                self.fail(f"Failed to convert science datetime to numeric: {str(e)}")
            
        except unittest.SkipTest:
            raise
        except Exception as e:
            error_msg = f"Failed format compatibility test: {str(e)}\n"
            self.fail(error_msg)
    
    def test_interpolation_accuracy(self):
        """Test the accuracy of the position interpolation"""
        # Create a synthetic test case where we know the expected result
        if len(self.mapper.times_numeric) > 10:
            # Take three consecutive points from the longitude data
            idx = len(self.mapper.times_numeric) // 2
            t1 = self.mapper.times_numeric[idx]
            t2 = self.mapper.times_numeric[idx + 1]
            t3 = self.mapper.times_numeric[idx + 2]
            
            # Get corresponding longitude values
            lon1 = self.mapper.longitude_values[idx]
            lon2 = self.mapper.longitude_values[idx + 1]
            lon3 = self.mapper.longitude_values[idx + 2]
            
            # Create a timestamp exactly halfway between t1 and t2
            mid_t = (t1 + t2) / 2
            mid_timestamp = np.array([np.datetime64('1970-01-01') + np.timedelta64(int(mid_t * 1e9), 'ns')])
            
            # Calculate expected longitude by linear interpolation
            expected_lon = (lon1 + lon2) / 2
            
            # Get the interpolated value from the mapper
            interpolated_lon = self.mapper.map_to_position(mid_timestamp, 'carrington_lon')
            
            # Should be close to the expected value
            self.assertIsNotNone(interpolated_lon)
            self.assertAlmostEqual(interpolated_lon[0], expected_lon, delta=1.0,
                                 msg="Linear interpolation should match expected value within 1 degree")
    
    def test_timestamp_format_handling(self):
        """Test the mapper's ability to handle different timestamp formats"""
        # Test with different datetime formats
        test_formats = [
            np.datetime64('2021-01-01 12:00'),                     # numpy datetime64
            pd.Timestamp('2021-01-01 12:00'),                      # pandas Timestamp
            datetime(2021, 1, 1, 12, 0),                           # python datetime
            '2021-01-01 12:00:00',                                # string format
            pd.DatetimeIndex(['2021-01-01 12:00:00']).to_numpy()  # DatetimeIndex as np.array
        ]
        
        for dt_format in test_formats:
            try:
                # Try to convert to np.array if it's not already
                if not isinstance(dt_format, np.ndarray):
                    if isinstance(dt_format, str) or isinstance(dt_format, datetime) or isinstance(dt_format, pd.Timestamp):
                        dt_array = np.array([dt_format])
                    else:
                        dt_array = np.array(dt_format)
                else:
                    dt_array = dt_format
                    
                # Test map_to_position with this format
                result = self.mapper.map_to_position(dt_array, 'carrington_lon')
        
                # Just verify it returns something and doesn't crash
                self.assertIsNotNone(result, f"Failed to handle datetime format: {type(dt_format)}")
                
            except Exception as e:
                self.fail(f"Failed to handle datetime format {type(dt_format)}: {e}")
    
    def test_edge_cases(self):
        """Test edge cases like empty arrays, or single point arrays"""
        # Test with an empty array
        empty_array = np.array([])
        result = self.mapper.map_to_position(empty_array, 'carrington_lon')
        self.assertIsNotNone(result, "Should handle empty arrays")
        self.assertEqual(len(result), 0, "Should return empty array for empty input")
        
        # Test with a single datapoint
        if len(self.mapper.times_numeric) > 0:
            single_time = np.array([np.datetime64('1970-01-01') + np.timedelta64(int(self.mapper.times_numeric[0] * 1e9), 'ns')])
            result = self.mapper.map_to_position(single_time, 'carrington_lon')
            self.assertIsNotNone(result, "Should handle single-point arrays")
            self.assertEqual(len(result), 1, "Should return single-point array for single-point input")
    
    def test_debug_multiplot_integration(self):
        """Test the integration with multiplot options"""
        from plotbot.multiplot_options import plt
        from plotbot.multiplot import multiplot
        
        # Store original settings
        original_settings = {
            'x_axis_carrington_lon': plt.options.x_axis_carrington_lon,
            'use_relative_time': plt.options.use_relative_time,
            'window': plt.options.window
        }
        
        try:
            # Reset all options to defaults first
            plt.options.reset()
            
            # Configure options for testing - use the simplest possible configuration
            plt.options.x_axis_carrington_lon = True  # Enable longitude x-axis
            plt.options.window = '1:00:00.000'  # Just 1 hour for quick test
            
            # Load test data
            test_time = '2023-09-27 23:28:00.000'  # Enc 17 perihelion
            
            # Get some simple test data for plotting
            pb.get_data(['2023-09-27 23:00:00.000', '2023-09-28 00:00:00.000'], pb.mag_rtn_4sa.br)
            
            # Skip test if data not available
            if not hasattr(pb.mag_rtn_4sa.br, 'datetime_array') or len(pb.mag_rtn_4sa.br.datetime_array) == 0:
                self.skipTest("Skipping test - no magnetic field data available")
                return
            
            # Create the most basic plot possible
            fig, axs = multiplot([(test_time, pb.mag_rtn_4sa.br)])
            
            # Basic checks that the plot was created
            self.assertIsNotNone(fig)
            self.assertIsNotNone(axs)
            self.assertEqual(len(axs), 1)
            
            # Check if any data was plotted
            lines = axs[0].get_lines()
            self.assertTrue(len(lines) > 0, "Plot should have at least one data line")
            
            if len(lines) > 0:
                x_data = lines[0].get_xdata()
                y_data = lines[0].get_ydata()
                
                # Verify data exists
                self.assertTrue(len(x_data) > 0, "Plot should have x data")
                self.assertTrue(len(y_data) > 0, "Plot should have y data")
            
                # X data should be longitude values, not datetime objects
                self.assertTrue(np.issubdtype(x_data.dtype, np.floating) or 
                               np.issubdtype(x_data.dtype, np.integer),
                              f"X-axis data should be numeric (longitude), got {x_data.dtype}")
            
                # Verify x-label mentions longitude
                x_label = axs[0].get_xlabel().lower()
                self.assertTrue("longitude" in x_label or "lon" in x_label,
                              f"X-axis label should mention longitude, got '{x_label}'")
            
            plt.close(fig)
            
        except unittest.SkipTest:
            raise
        except Exception as e:
            plt.close('all')  # Close any open figures
            self.fail(f"Multiplot integration test failed: {str(e)}")
        finally:
            # Restore original settings
            for key, value in original_settings.items():
                setattr(plt.options, key, value)
    
    def test_multiplot_positional_axis(self):
        """Test multiplot with positional (longitude) axis in more detail"""
        from plotbot.multiplot_options import plt
        from plotbot.multiplot import multiplot
        import matplotlib.dates as mdates
        
        # Store original settings
        original_settings = {
            'x_axis_carrington_lon': plt.options.x_axis_carrington_lon,
            'use_relative_time': plt.options.use_relative_time,
            'window': plt.options.window
        }
        
        try:
            # Reset all options to defaults first
            plt.options.reset()
            
            # Configure options for testing
            plt.options.x_axis_carrington_lon = True  # Enable longitude x-axis
            plt.options.window = '1:00:00.000'  # Just 1 hour for quick test
            
            # Load test data
            center_time = '2023-09-27 23:28:00.000'  # Enc 17 perihelion
            
            # Get some test data for plotting
            pb.get_data(['2023-09-27 23:00:00.000', '2023-09-28 00:00:00.000'], pb.mag_rtn_4sa.br)
            
            # Skip test if data not available
            if not hasattr(pb.mag_rtn_4sa.br, 'datetime_array') or len(pb.mag_rtn_4sa.br.datetime_array) == 0:
                self.skipTest("Skipping test - no magnetic field data available")
                return
                
            # Create plot
            fig, axs = multiplot([(center_time, pb.mag_rtn_4sa.br)])
            
            # Check if formatter is different from the default date formatter
            # Default matplotlib uses mdates formatters for time, but should use a different
            # formatter for longitude
            if len(axs) > 0:
                formatter = axs[0].xaxis.get_major_formatter()
                
                # Should NOT be one of matplotlib's date formatters
                self.assertFalse(isinstance(formatter, mdates.DateFormatter), 
                                "X-axis formatter should not be DateFormatter when using longitude")
                self.assertFalse(isinstance(formatter, mdates.ConciseDateFormatter),
                                "X-axis formatter should not be ConciseDateFormatter when using longitude")
            
                # Extract some sample tick labels to verify they look like longitude values
                fig.canvas.draw()  # Force drawing to generate tick labels
                tick_labels = [t.get_text() for t in axs[0].get_xticklabels()]
                
                # Skip test if no tick labels (can happen in CI environments without proper rendering)
                if tick_labels:
                    # Verify some tick labels - should contain degree symbols or look like angles
                    has_expected_format = False
                    for label in tick_labels:
                        # Check for degree symbols, or numeric values that might be angles
                        if '°' in label or (label.replace('.', '').isdigit() and float(label) <= 360):
                            has_expected_format = True
                            break
                    
                    self.assertTrue(has_expected_format, f"Tick labels don't appear to be longitude values: {tick_labels}")
            
            plt.close(fig)
            
        except unittest.SkipTest:
            raise
        except Exception as e:
            plt.close('all')  # Close any open figures
            self.fail(f"Multiplot longitude axis test failed: {str(e)}")
        finally:
            # Restore original settings
            for key, value in original_settings.items():
                setattr(plt.options, key, value)

    def test_notebook_example_simulation(self):
        """Test that multiplot with positional (longitude) axis works with a notebook-like example"""
        from plotbot.multiplot_options import plt
        from plotbot.multiplot import multiplot
        
        # Store original settings
        original_settings = {
            'x_axis_carrington_lon': plt.options.x_axis_carrington_lon,
            'use_relative_time': plt.options.use_relative_time,
            'window': plt.options.window,
            'use_single_title': plt.options.use_single_title
        }
        
        try:
            # This test simulates what a user might do in a notebook
            
            # Step 1: Reset and configure options
            plt.options.reset()
            plt.options.x_axis_carrington_lon = True
            plt.options.window = '12:00:00.000'  # 12 hours
            plt.options.use_single_title = True
            plt.options.single_title_text = "Magnetic Field vs. Carrington Longitude"
            
            # Step 2: Define time point(s) to plot
            perihelion_17 = '2023-09-27 23:28:00.000'
            
            # Step 3: Get some data
            pb.get_data(['2023-09-27 17:28:00.000', '2023-09-28 05:28:00.000'], 
                       pb.mag_rtn_4sa.br, pb.mag_rtn_4sa.bt, pb.mag_rtn_4sa.bn)
            
            # Step 4: Create the plot
            try:
                fig, axs = multiplot([
                    (perihelion_17, pb.mag_rtn_4sa.br),
                    (perihelion_17, pb.mag_rtn_4sa.bt),
                    (perihelion_17, pb.mag_rtn_4sa.bn)
                ])
                
                # Basic verification
                self.assertEqual(len(axs), 3, "Should have 3 panels")
            
                # Check for x-axis labels
                x_label = axs[-1].get_xlabel().lower()
                self.assertTrue("longitude" in x_label or "lon" in x_label,
                              f"Bottom x-axis label should mention longitude, got '{x_label}'")
                
                # Verify top panels don't have x-labels (with default single_x_axis=True)
                self.assertEqual(axs[0].get_xlabel(), "", "Top panel should have empty x label")
            
                # Check that data was actually plotted in each panel
                for i, ax in enumerate(axs):
                    lines = ax.get_lines()
                    self.assertTrue(len(lines) > 0, f"Panel {i+1} should have at least one data line")
                    
                    if lines:
                        x_data = lines[0].get_xdata()
                        self.assertTrue(len(x_data) > 0, f"Panel {i+1} should have plotted data")
                
                plt.close(fig)
                
            except Exception as e:
                plt.close('all')
                self.fail(f"Notebook example simulation failed: {str(e)}")
            
        except unittest.SkipTest:
            raise
        except Exception as e:
            plt.close('all')
            self.fail(f"Test setup failed: {str(e)}")
        finally:
            # Restore original settings
            for key, value in original_settings.items():
                setattr(plt.options, key, value)

if __name__ == '__main__':
    unittest.main()
