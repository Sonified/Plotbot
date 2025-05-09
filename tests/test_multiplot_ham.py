"""
Tests for the new HAM data integration in multiplot functionality.

This file tests the new hamify feature that allows displaying HAM data on the right axis
of multiplot panels. The test creates a multiplot with data around noon on March 19-21, 2025.

To run these tests:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_multiplot_ham.py -v -s
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys
import os
import traceback

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import relevant modules from plotbot
from plotbot import mag_rtn_4sa, plt
from plotbot.data_classes.psp_ham_classes import ham as ham_instance
from plotbot.multiplot import multiplot
from plotbot.print_manager import print_manager
from plotbot.data_cubby import data_cubby
from plotbot.data_tracker import global_tracker
from plotbot.plotbot_helpers import time_clip
from plotbot.get_data import get_data

# Add the tests directory to sys.path
sys.path.append(os.path.dirname(__file__))

# Import the record_test_result function from conftest
try:
    from conftest import record_test_result
except ImportError:
    # Fallback in case import fails
    def record_test_result(test_name, check):
        pass

# Fixture to clear caches before each test
@pytest.fixture(autouse=True)
def clear_caches():
    """Clear all cached data before each test"""
    # Clear global tracker cache if it exists
    if hasattr(global_tracker, 'clear_calculation_cache'):
        print_manager.debug("Clearing global_tracker cache.")
        global_tracker.clear_calculation_cache()
    
    # Clear data cubby's containers if clear_all exists
    if hasattr(data_cubby, 'clear_all'):
        print_manager.debug("Clearing data_cubby main containers.")
        data_cubby.clear_all()
    
    plt.options.reset()  # Reset all plot options
    
    print_manager.debug("Cache clearing fixture finished.")

def setup_plot_options_for_ham_test():
    """Configure the plot options for HAM plotting tests"""
    plt.options.reset()
    
    # Enable status printing
    print_manager.show_status = True
    print_manager.status("Status printing enabled for HAM test")
    
    # General plot settings
    plt.options.width = 18
    plt.options.height_per_panel = 2.5
    plt.options.hspace = 0.5
    
    # Title and labels
    plt.options.use_single_title = True
    plt.options.single_title_text = "PSP HAM Data Test - March 2025"
    plt.options.y_label_uses_encounter = False
    plt.options.title_fontsize = 15
    
    # Time window settings
    plt.options.window = '06:00:00'  # 6 hours total window
    plt.options.position = 'around'  # Center the window around specified time
    
    # Vertical line 
    plt.options.draw_vertical_line = True
    plt.options.vertical_line_color = 'black'
    plt.options.vertical_line_width = 1.0
    plt.options.vertical_line_style = '--'
    
    # HAM settings
    plt.options.hamify = True  # Enable HAM plotting

@pytest.mark.mission("HAM Multiplot Test")
def test_multiplot_with_ham_on_right_axis():
    """Test multiplot with HAM data on right axis using the new hamify feature"""
    print_manager.test("\n=== Testing HAM Data on Right Axis (hamify feature) ===")
    
    # Define test time ranges (noon on March 19-21, 2025)
    test_dates = [
        "2025-03-19/12:00:00.000",
        "2025-03-20/12:00:00.000", 
        "2025-03-21/12:00:00.000"
    ]
    
    # Set up plot options
    setup_plot_options_for_ham_test()
    
    # Select main variable for left axis (magnetic field component)
    main_var = mag_rtn_4sa.br
    
    # Select HAM variable for right axis
    ham_var = ham_instance.hamogram_30s
    
    # Load HAM data for ALL dates first
    print_manager.status("Loading HAM data for all dates...")
    for date in test_dates:
        # Create time range (±3 hours around noon)
        center_time = pd.Timestamp(date)
        start_time = center_time - pd.Timedelta(hours=3)
        end_time = center_time + pd.Timedelta(hours=3)
        trange = [start_time.strftime('%Y-%m-%d/%H:%M:%S'), end_time.strftime('%Y-%m-%d/%H:%M:%S')]
        
        # Load the HAM data using get_data for each date
        print_manager.status(f"Loading HAM data for {date}...")
        get_data(trange, ham_var)
    
    # Get a fresh reference to the HAM variable from data_cubby
    print_manager.status("Getting fresh reference to HAM variable...")
    ham_class_instance = data_cubby.grab('ham')
    if ham_class_instance:
        ham_var = ham_class_instance.get_subclass('hamogram_30s')
        print_manager.status(f"Successfully retrieved fresh reference to HAM variable")
    else:
        print_manager.error("Failed to get ham class from data_cubby")
    
    # Verify ham_var has data after loading
    print_manager.test(f"HAM variable after loading - has datetime_array: {ham_var.datetime_array is not None}")
    if ham_var.datetime_array is not None:
        print_manager.test(f"HAM variable datetime_array length: {len(ham_var.datetime_array)}")
        print_manager.test(f"HAM variable datetime range: {ham_var.datetime_array[0]} to {ham_var.datetime_array[-1]}")
    
    # Set the HAM variable for plotting
    plt.options.ham_var = ham_var
    
    # Create plot data list with all three dates
    plot_data = [(date, main_var) for date in test_dates]
    
    try:
        # Create the multiplot with multiple panels
        print_manager.test(f"Creating multiplot with {len(test_dates)} panels")
        print_manager.test(f"Main variable: {main_var.subclass_name}, HAM variable: {ham_var.subclass_name}")
        
        # Create the standard multiplot
        fig, axs = multiplot(plot_data)
        
        # Verify necessary conditions after plotting
        assert plt.options.hamify, "hamify option should be True"
        assert plt.options.ham_var is not None, "ham_var should be set"
        
        print_manager.test("✅ Successfully created multiplot with HAM data on right axis")
        record_test_result("test_multiplot_with_ham_on_right_axis", {
            "description": "Create multiplot with HAM data on right axis",
            "result": "PASS",
            "message": "Successfully created multiplot with HAM data"
        })
        
        # No more interactive waiting - just let the test finish
        print_manager.test("Plot was created successfully, test complete")

    except Exception as e:
        tb_str = traceback.format_exc()
        print_manager.error(f"❌ Failed to create multiplot with HAM data: {e}")
        print_manager.error(f"Traceback: {tb_str}")
        record_test_result("test_multiplot_with_ham_on_right_axis", {
            "description": "Create multiplot with HAM data on right axis",
            "result": "FAIL",
            "message": f"Exception: {e}"
        })
        pytest.fail(f"Test failed: {e}")

@pytest.mark.mission("HAM Multiplot with Position Axis")
def test_multiplot_ham_with_positional_axis():
    """Test multiplot with HAM data on right axis and positional x-axis"""
    print_manager.test("\n=== Testing HAM Data with Positional X-Axis ===")
    
    # Define test time ranges (noon on March 19-21, 2025)
    test_dates = [
        "2025-03-19/12:00:00.000",
        "2025-03-20/12:00:00.000", 
        "2025-03-21/12:00:00.000"
    ]
    
    # Set up plot options
    setup_plot_options_for_ham_test()
    
    # Enable positional x-axis (radial distance)
    plt.options.x_axis_r_sun = True
    
    # Select main variable for left axis (magnetic field component)
    main_var = mag_rtn_4sa.br
    
    # Select HAM variable for right axis
    ham_var = ham_instance.hamogram_30s
    
    # Load HAM data for each time range
    print_manager.status("Loading HAM data for each time range...")
    ham_vars = {}  # Dictionary to store HAM data for each date
    
    for date in test_dates:
        # Create time range (±3 hours around noon)
        center_time = pd.Timestamp(date)
        start_time = center_time - pd.Timedelta(hours=3)
        end_time = center_time + pd.Timedelta(hours=3)
        trange = [start_time.strftime('%Y-%m-%d/%H:%M:%S'), end_time.strftime('%Y-%m-%d/%H:%M:%S')]
        
        # Load the HAM data using get_data
        print_manager.status(f"Loading HAM data for {date}...")
        get_data(trange, ham_var)
        
        # Get a fresh reference to the HAM variable from data_cubby
        print_manager.status(f"Getting fresh reference to HAM variable for {date}...")
        ham_class_instance = data_cubby.grab('ham')
        if ham_class_instance:
            fresh_ham_var = ham_class_instance.get_subclass('hamogram_30s')
            print_manager.status(f"Successfully retrieved fresh reference to HAM variable for {date}")
            ham_vars[date] = fresh_ham_var
            
            # Verify ham_var has data after loading
            print_manager.test(f"HAM variable for {date} - has datetime_array: {fresh_ham_var.datetime_array is not None}")
            if fresh_ham_var.datetime_array is not None:
                print_manager.test(f"HAM variable {date} datetime_array length: {len(fresh_ham_var.datetime_array)}")
                print_manager.test(f"HAM variable {date} datetime range: {fresh_ham_var.datetime_array[0]} to {fresh_ham_var.datetime_array[-1]}")
        else:
            print_manager.error(f"Failed to get ham class from data_cubby for {date}")
    
    # Set the HAM variable for the most recent date (for compatibility)
    plt.options.ham_var = ham_vars[test_dates[-1]]
    
    # Create a custom multiplot function wrapper that sets the right HAM variable for each panel
    def custom_multiplot(plot_list):
        # Store original ham_var
        original_ham_var = plt.options.ham_var
        
        # Create figure and axes ourselves
        num_panels = len(plot_list)
        fig, axs = plt.subplots(num_panels, 1, figsize=(plt.options.width, plt.options.height_per_panel * num_panels))
        if num_panels == 1:
            axs = [axs]
        
        # Plot each panel with the appropriate HAM data
        for i, (center_time, var) in enumerate(plot_list):
            # Set the appropriate HAM variable for this panel
            date_str = center_time
            if date_str in ham_vars:
                plt.options.ham_var = ham_vars[date_str]
                print_manager.status(f"Setting HAM data for panel {i+1} (date: {date_str})")
            
            # Create a single-panel plot
            single_plot_list = [(center_time, var)]
            
            # Adjust figure and plotting area for this panel
            if i == 0:  # First panel
                plt.subplots_adjust(top=0.85)
            elif i == num_panels - 1:  # Last panel
                plt.subplots_adjust(bottom=0.15)
            
            # Store original hamify setting before plotting
            original_hamify = plt.options.hamify
            
            # Plot this panel
            from plotbot.multiplot import multiplot
            _, _ = multiplot(single_plot_list)
        
        # Restore original ham_var
        plt.options.ham_var = original_ham_var
        plt.options.hamify = original_hamify
        
        return fig, axs
        
    # Create plot data list using list comprehension
    plot_data = [(date, main_var) for date in test_dates]
    
    try:
        # Set a descriptive title
        plt.options.use_single_title = True
        plt.options.single_title_text = "Test 7: Positional X-Axis (HAM on right axis, x_axis_r_sun=True)"
        # Create the multiplot with standard multiplot (not custom)
        fig, axs = multiplot(plot_data)
        # Suppress display
        plt.close(fig)
        # Save to file with numeric ordering and short name
        output_dir = os.path.join(os.path.dirname(__file__), "multiplot_ham_tests")
        os.makedirs(output_dir, exist_ok=True)
        filename = "7_positional_xaxis.png"
        filepath = os.path.join(output_dir, filename)
        fig.savefig(filepath, dpi=200)
        print_manager.test(f"✅ Positional X-Axis test - Saved to {filepath}")
    except Exception as e:
        tb_str = traceback.format_exc()
        print_manager.error(f"❌ Positional X-Axis test - Exception: {e}")
        print_manager.error(f"Traceback: {tb_str}")
        pytest.fail(f"Positional X-Axis test failed: {e}")

@pytest.mark.mission("HAM Multiplot Extended Integration")
def test_multiplot_ham_extended_variants():
    """Test multiplot with HAM data over a week, various color/opacity/HAM settings."""
    print_manager.test("\n=== Extended HAM Multiplot Integration Test ===")

    # Define test time ranges (noon on March 19-27, 2025)
    test_dates = [
        f"2025-03-{day:02d}/12:00:00.000" for day in range(19, 28)
    ]

    # Create plot data list
    main_var = mag_rtn_4sa.br
    plot_data = [(date, main_var) for date in test_dates]

    # Helper to load HAM data for all dates
    def load_ham_data_for_all_dates(ham_var):
        for date in test_dates:
            center_time = pd.Timestamp(date)
            start_time = center_time - pd.Timedelta(hours=12)
            end_time = center_time + pd.Timedelta(hours=12)
            trange = [start_time.strftime('%Y-%m-%d/%H:%M:%S'), end_time.strftime('%Y-%m-%d/%H:%M:%S')]
            get_data(trange, ham_var)
        # Refresh from data_cubby
        ham_class_instance = data_cubby.grab('ham')
        if ham_class_instance:
            return ham_class_instance.get_subclass(ham_var.subclass_name)
        return ham_var

    # Test variants
    variants = [
        {"desc": "Standard plot (default color, default opacity, hamogram_30s)",
         "color_mode": "default", "ham_opacity": 1.0, "ham_var": ham_instance.hamogram_30s, "ham_color": None, "short_name": "standard"},
        {"desc": "Rainbow plot (hamogram_30s)",
         "color_mode": "rainbow", "ham_opacity": 1.0, "ham_var": ham_instance.hamogram_30s, "ham_color": None, "short_name": "rainbow"},
        {"desc": "Rainbow plot, ham at 50% opacity (hamogram_30s)",
         "color_mode": "rainbow", "ham_opacity": 0.5, "ham_var": ham_instance.hamogram_30s, "ham_color": None, "short_name": "rainbow_50pct"},
        {"desc": "Rainbow plot, ham at 75% opacity (hamogram_30s)",
         "color_mode": "rainbow", "ham_opacity": 0.75, "ham_var": ham_instance.hamogram_30s, "ham_color": None, "short_name": "rainbow_75pct"},
        {"desc": "Rainbow plot, ham at 75% opacity (hamogram_30s) [tight margins]",
         "color_mode": "rainbow", "ham_opacity": 0.75, "ham_var": ham_instance.hamogram_30s, "ham_color": None, "short_name": "4.1_rainbow_tightmargins", "margin_top": 0.99, "margin_bottom": 0.01},
        {"desc": "Rainbow plot, ham at 50% opacity, hamogram_2m",
         "color_mode": "rainbow", "ham_opacity": 0.5, "ham_var": ham_instance.hamogram_2m, "ham_color": None, "short_name": "rainbow_2m_50pct"},
        {"desc": "Rainbow plot, ham at 50% opacity, hamogram_20m, red",
         "color_mode": "rainbow", "ham_opacity": 0.5, "ham_var": ham_instance.hamogram_20m, "ham_color": "red", "short_name": "rainbow_20m_50pct_red"},
    ]

    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(__file__), "multiplot_ham_tests")
    os.makedirs(output_dir, exist_ok=True)

    for idx, v in enumerate(variants, 1):
        try:
            print_manager.test(f"\n--- {v['desc']} ---")
            setup_plot_options_for_ham_test()
            plt.options.window = '24:00:00'  # 24 hours window (±12h)
            plt.options.position = 'around'
            plt.options.color_mode = v["color_mode"]
            plt.options.hamify = True
            plt.options.ham_opacity = v["ham_opacity"]
            # Set HAM variable and color
            ham_var = v["ham_var"]
            ham_var = load_ham_data_for_all_dates(ham_var)
            if v["ham_color"]:
                ham_var.color = v["ham_color"]
            plt.options.ham_var = ham_var
            # Set a descriptive title
            plt.options.use_single_title = True
            # Apply custom margins if present
            if "margin_top" in v:
                plt.options.margin_top = v["margin_top"]
            if "margin_bottom" in v:
                plt.options.margin_bottom = v["margin_bottom"]
            margin_note = f" (margin_top={getattr(plt.options, 'margin_top', 'default')}, margin_bottom={getattr(plt.options, 'margin_bottom', 'default')})" if "margin_top" in v or "margin_bottom" in v else ""
            plt.options.single_title_text = f"Test {idx}{'.1' if v.get('short_name','').startswith('4.1') else ''}: {v['desc']}{margin_note}"
            # Create multiplot
            fig, axs = multiplot(plot_data)
            # Suppress display
            plt.close(fig)
            # Save to file with numeric ordering and short name
            if v.get('short_name','').startswith('4.1'):
                filename = "4.1_rainbow_tightmargins.png"
            else:
                filename = f"{idx}_{v['short_name']}.png"
            filepath = os.path.join(output_dir, filename)
            fig.savefig(filepath, dpi=200, bbox_inches='tight')
            print_manager.test(f"✅ {v['desc']} - Saved to {filepath}")
        except Exception as e:
            tb_str = traceback.format_exc()
            print_manager.error(f"❌ {v['desc']} - Exception: {e}")
            print_manager.error(f"Traceback: {tb_str}")
            pytest.fail(f"{v['desc']} failed: {e}")

if __name__ == "__main__":
    # Run tests directly if file is executed
    test_multiplot_with_ham_on_right_axis()
    test_multiplot_ham_with_positional_axis()
    test_multiplot_ham_extended_variants() 