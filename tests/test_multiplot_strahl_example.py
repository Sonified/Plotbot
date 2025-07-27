#!/usr/bin/env python3
"""
Test for multiplot that first shows a working example with mag_rtn_4sa.br,
and then shows the failing example with epad.strahl.
This allows for direct visual comparison and debugging.
"""

import sys
import os
import contextlib

# Add the plotbot directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import necessary plotbot components
from plotbot import epad, multiplot, plt, mag_rtn_4sa
from plotbot.data_cubby import data_cubby
from plotbot.print_manager import print_manager
from plotbot.get_data import get_data
from plotbot.plotbot_helpers import time_clip
import matplotlib.pyplot as mpl_plt
import matplotlib.colors as colors
import numpy as np
import matplotlib.colors as colors
import numpy as np
import pandas as pd

def test_standalone_spectral_plot():
    """
    Standalone test that uses the EXACT working spectral plotting code from plotbot_main.py
    """
    log_filepath = "tests/test_logs/spectral_test_output.txt"
    with open(log_filepath, 'w') as log_file:
        with contextlib.redirect_stdout(log_file), contextlib.redirect_stderr(log_file):
            print("Log file for standalone spectral plot test using plotbot_main.py code.")
            print("="*80)
            
            # --- Enable Test Prints ---
            print_manager.test_enabled = True
            print_manager.show_status = True
            print_manager.test("[TEST] Starting standalone spectral plot test using plotbot_main.py code")
            
            # --- Setup ---
            trange = ['2022-12-12/05:30:00.000', '2022-12-12/11:30:00.000']
            center_time = '2022-12-12/08:30:00.000'
            print_manager.test(f"[TEST] Time range: {trange[0]} to {trange[1]}")

            # --- Load Data Using get_data (like plotbot does) ---
            print_manager.test("[TEST] Loading data using get_data...")
            var = epad.strahl
            get_data(trange, var)
            print_manager.test("[TEST] Data loading complete")
            
            # --- Get Variable from DataCubby (like plotbot does) ---
            print_manager.test("[TEST] Getting variable from data_cubby...")
            epad_class = data_cubby.grab('epad')
            var = epad_class.get_subclass('strahl')
            print_manager.test(f"[TEST] Retrieved variable: {var.class_name}.{var.subclass_name}")
            
            # --- EXACT SPECTRAL PLOTTING CODE FROM plotbot_main.py ---
            if var.plot_type == 'spectral':
                print_manager.test("[TEST] Variable is spectral type - proceeding with plotbot_main.py code")
                
                # Create figure like plotbot does
                fig, ax = plt.subplots(1, 1, figsize=(12, 4))
                
                empty_plot = False
                
                #====================================================================
                # Verify data availability and validity (EXACT from plotbot_main.py)
                #====================================================================
                if var.datetime_array is None or len(var.datetime_array) == 0:
                    empty_plot = True
                    print_manager.test("[TEST] ERROR: No datetime array available (spectral)")
                    return False

                # Use raw datetime array for time clipping, not the property (which is now clipped)
                raw_datetime_array = var.plot_options.datetime_array if hasattr(var, 'plot_options') else var.datetime_array
                time_indices = time_clip(raw_datetime_array, trange[0], trange[1])  # Get time range indices
                if len(time_indices) == 0:
                    empty_plot = True
                    print_manager.test("[TEST] ERROR: No valid time indices found (spectral)")
                    return False
                
                print_manager.test(f"[TEST] Found {len(time_indices)} valid time indices")
                
                # Use all_data property for internal plotting (performance optimization)
                data = var.all_data  # Get full unclipped data for internal processing
                print_manager.test(f"[TEST] Data shape: {data.shape}")
                
                # For spectral data, ensure indices are valid for the data array
                max_valid_index = data.shape[0] - 1
                if len(time_indices) > 0 and time_indices[-1] > max_valid_index:
                    print_manager.test(f"[TEST] Adjusting time indices for spectral data: max index {time_indices[-1]} > data length {data.shape[0]}")
                    time_indices = time_indices[time_indices <= max_valid_index]
                    if len(time_indices) == 0:
                        empty_plot = True
                        print_manager.test("[TEST] ERROR: No valid time indices after adjustment (spectral)")
                        return False
                
                data_clipped = data[time_indices]  # Slice data for time range
                if np.all(np.isnan(data_clipped)):  # Check for all NaN values
                    empty_plot = True
                    print_manager.test("[TEST] ERROR: All data points in time window are NaN (spectral)")
                    return False
                    
                print_manager.test(f"[TEST] Data clipped shape: {data_clipped.shape}")
                    
                #====================================================================
                # Proceed with spectral plotting (EXACT from plotbot_main.py)
                #====================================================================
                if not empty_plot:  # Create spectral plot only if we have valid data
                    # For datetime_clipped, also handle potential mismatched dimensions
                    # Use raw datetime array for clipping to match time_indices calculation
                    if raw_datetime_array.ndim == 2:
                        # Keep 2D for pcolormesh compatibility with additional_data
                        datetime_clipped = raw_datetime_array[time_indices, :]
                    else:
                        datetime_clipped = raw_datetime_array[time_indices]
                    
                    print_manager.test(f"[TEST] Datetime clipped shape: {datetime_clipped.shape if hasattr(datetime_clipped, 'shape') else len(datetime_clipped)}")
                    
                    # Handle additional_data similarly
                    if hasattr(var, 'additional_data') and var.additional_data is not None:
                        additional_data_clipped = var.additional_data[time_indices] if len(var.additional_data) > max(time_indices) else var.additional_data
                        print_manager.test(f"[TEST] Additional data clipped shape: {additional_data_clipped.shape if hasattr(additional_data_clipped, 'shape') else len(additional_data_clipped)}")
                    else:
                        additional_data_clipped = None
                        print_manager.test("[TEST] No additional_data available")

                    ax.set_ylabel(var.y_label)  # Set y-axis properties
                    ax.set_yscale(var.y_scale)
                    if var.y_limit:
                        ax.set_ylim(var.y_limit)

                    # Configure color scaling
                    if var.colorbar_scale == 'log':  # Set up logarithmic color scaling
                        norm = colors.LogNorm(vmin=var.colorbar_limits[0], vmax=var.colorbar_limits[1]) if var.colorbar_limits else colors.LogNorm()
                    elif var.colorbar_scale == 'linear':  # Set up linear color scaling
                        norm = colors.Normalize(vmin=var.colorbar_limits[0], vmax=var.colorbar_limits[1]) if var.colorbar_limits else None
                    else:
                        norm = None

                    print_manager.test(f"[TEST] Color scale: {var.colorbar_scale}, limits: {var.colorbar_limits}")

                    # Create spectral plot (EXACT from plotbot_main.py)
                    if additional_data_clipped is not None:
                        print_manager.test("[TEST] Creating pcolormesh with additional_data")
                        im = ax.pcolormesh(  # Create 2D color plot
                            datetime_clipped,
                            additional_data_clipped,
                            data_clipped,
                            norm=norm,
                            cmap=var.colormap if hasattr(var, 'colormap') else None,
                            shading='auto'
                        )
                    else:
                        print_manager.test("[TEST] Creating pcolormesh with y_values")
                        # If no additional_data, create a simple y-axis based on data shape
                        y_values = np.arange(data_clipped.shape[1]) if data_clipped.ndim > 1 else np.arange(len(data_clipped))
                        print_manager.test(f"[TEST] Y values shape: {y_values.shape}")
                        im = ax.pcolormesh(  # Create 2D color plot
                            datetime_clipped,
                            y_values,
                            data_clipped,
                            norm=norm,
                            cmap=var.colormap if hasattr(var, 'colormap') else None,
                            shading='auto'
                        )
                    
                    print_manager.test("[TEST] pcolormesh created successfully")
                    
                    # Add and configure colorbar
                    pos = ax.get_position()  # Get plot position
                    cax = fig.add_axes([pos.x1 + 0.01, pos.y0, 0.02, pos.height])  # Create colorbar axes
                    cbar = plt.colorbar(im, cax=cax)  # Add colorbar
                    if hasattr(var, 'colorbar_label'):
                        cbar.set_label(var.colorbar_label)  # Set colorbar label if specified
                    
                    print_manager.test("[TEST] Colorbar added successfully")
                    
                    # Set title and show
                    ax.set_title("Standalone Spectral Plot Test (using plotbot_main.py code)")
                    ax.set_xlabel("Time")
                    
                    print_manager.test("[TEST] Showing plot...")
                    plt.show()
                    print_manager.test("[TEST] Plot displayed successfully")
                    
                    return True
                else:
                    print_manager.test("[TEST] ERROR: empty_plot flag was set")
                    return False
            else:
                print_manager.test(f"[TEST] ERROR: Variable plot_type is {var.plot_type}, not spectral")
                return False

def plot_br_example():
    """
    Generates and shows a working multiplot with mag_rtn_4sa.br.
    """
    print("\n================================================================================")
    print("PLOT 1: Generating working example with mag_rtn_4sa.br...")
    print("================================================================================\n")
    
    # --- Reset plotting options ---
    plt.options.reset()
    
    # --- Configure General Plot Options ---
    plt.options.width = 20
    plt.options.height_per_panel = 3
    plt.options.hspace = .5
    plt.options.use_single_title = True
    plt.options.single_title_text = "WORKING EXAMPLE: Br Around PSP HCS Crossings"
    plt.options.draw_vertical_line = True
    
    # --- Data Selection ---
    hcs_crossing_times = [
        '2022-12-12/08:30:00.000',
        '2023-06-22/01:30:00.000',
        '2023-06-22/04:45:00.000'
    ]
    plt.options.window = '06:00:00.000'
    plt.options.position = 'around'
    plot_variable = mag_rtn_4sa.br
    
    plot_data = [(time, plot_variable) for time in hcs_crossing_times]
    
    # --- Call Multiplot and Show ---
    plt.options.show_plot = True  # Ensure plot is configured to be shown
    multiplot(plot_data)
    mpl_plt.show()  # This will block until you close the plot window

def plot_strahl_example():
    """
    Generates and shows the multiplot with epad.strahl that is currently failing.
    This is for visual inspection.
    """
    print("\n================================================================================")
    print("PLOT 2: Generating failing example with epad.strahl for debugging...")
    print("================================================================================\n")

    # --- Reset plotting options ---
    plt.options.reset()

    # --- Enable debug and test prints to diagnose the issue ---
    print_manager.show_debug = True
    print_manager.show_status = True
    print_manager.test_enabled = True
    print_manager.test("[TEST] Test prints enabled for EPAD Strahl plot.")

    # --- Configure MINIMAL Plot Options ---
    plt.options.width = 20
    plt.options.height_per_panel = 3
    plt.options.use_single_title = True
    plt.options.single_title_text = "FAILING EXAMPLE: EPAD Strahl (Minimal Options)"
    plt.options.draw_vertical_line = True
    
    # --- Data Selection ---
    hcs_crossing_times = [
        '2022-12-12/08:30:00.000',
        '2023-06-22/01:30:00.000',
        '2023-06-22/04:45:00.000'
    ]
    plt.options.window = '06:00:00.000'
    plt.options.position = 'around'
    plot_variable = epad.strahl
    
    plot_data = [(time, plot_variable) for time in hcs_crossing_times]
    print_manager.test(f"[TEST] Created plot list with {len(plot_data)} panels.")

    # --- Call Multiplot and Show ---
    plt.options.show_plot = True 
    print_manager.test("[TEST] Calling multiplot...")
    multiplot(plot_data)
    print_manager.test("[TEST] Multiplot call complete. Now calling plt.show().")
    mpl_plt.show()  # This will block until you close the plot window


if __name__ == "__main__":
    # This block runs the three plotting functions sequentially.
    
    # Test 0: Standalone spectral plot test
    print("Starting standalone spectral plot test...")
    success = test_standalone_spectral_plot()
    
    if success:
        print("\n✅ Standalone test PASSED - spectral plotting works!")
    else:
        print("\n❌ Standalone test FAILED - spectral plotting broken at fundamental level!")
    
    print("\nScript finished.")

    print("\nScript finished.")