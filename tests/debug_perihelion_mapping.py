import sys
import os
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Add parent directory to path to import plotbot modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from plotbot.x_axis_positional_data_helpers import XAxisPositionalDataMapper
from plotbot.utils import get_perihelion_time # Import the function
from plotbot.print_manager import print_manager # For debug messages

def test_perihelion_mapping_standalone():
    """
    Standalone test to verify the core logic for calculating 
    'Degrees from Perihelion' outside of the multiplot function.
    Mimics the steps intended within multiplot.
    """
    print_manager.status("--- Running Standalone Perihelion Mapping Test ---")

    # --- Configuration ---
    center_time_str = '2023-09-27 23:28:00.000' # E17 perihelion
    window_str = '24:00:00.000' # +/- 12 hours

    # --- Setup Mapper ---
    try:
        project_root = pathlib.Path(__file__).parent.parent
        data_path = project_root / "support_data" / "trajectories" / "Parker_positional_data.npz"
        if not data_path.exists():
            print_manager.error(f"Data file not found: {data_path}")
            return
        mapper = XAxisPositionalDataMapper(str(data_path))
        if not mapper.data_loaded:
            print_manager.error(f"Failed to load positional data.")
            return
        print_manager.status("Positional Data Mapper initialized.")
    except Exception as e:
        print_manager.error(f"Error initializing mapper: {e}")
        return

    # --- Time Slice Calculation ---
    center_dt = pd.Timestamp(center_time_str)
    half_window = pd.Timedelta(window_str) / 2
    start_dt = center_dt - half_window
    end_dt = center_dt + half_window
    # Create a dense time slice for smooth plotting
    time_slice_pd = pd.date_range(start_dt, end_dt, periods=1000) 
    time_slice_np = time_slice_pd.to_numpy()
    print_manager.debug(f"Generated time slice: {start_dt} to {end_dt}")

    # --- Get Perihelion Time and Longitude ---
    perihelion_time_str = get_perihelion_time(center_dt)
    if not perihelion_time_str:
        print_manager.error(f"Could not retrieve perihelion time for {center_dt}.")
        return

    try:
        perihelion_dt = datetime.strptime(perihelion_time_str, '%Y/%m/%d %H:%M:%S.%f')
        perihelion_time_np = np.array([np.datetime64(perihelion_dt)])
        print_manager.debug(f"Perihelion datetime object: {perihelion_dt}")
    except ValueError:
        print_manager.error(f"Could not parse perihelion time string: {perihelion_time_str}")
        return
        
    perihelion_lon_arr = mapper.map_to_position(perihelion_time_np, 'carrington_lon')

    if perihelion_lon_arr is None or len(perihelion_lon_arr) == 0 or np.isnan(perihelion_lon_arr[0]):
        print_manager.error("Failed to map perihelion time to a valid longitude.")
        return
    perihelion_lon_val = perihelion_lon_arr[0]
    print_manager.status(f"Successfully mapped Perihelion Time {perihelion_time_str} to Longitude: {perihelion_lon_val:.2f}°")

    # --- Map Time Slice to Longitude ---
    carrington_lons_slice = mapper.map_to_position(time_slice_np, 'carrington_lon')
    if carrington_lons_slice is None:
        print_manager.error("Failed to map time slice to Carrington Longitudes.")
        return
    print_manager.debug(f"Mapped time slice to {len(carrington_lons_slice)} Carrington Longitudes.")

    # --- Filter NaNs ---
    valid_lon_mask = ~np.isnan(carrington_lons_slice)
    num_valid_lons = np.sum(valid_lon_mask)
    if num_valid_lons == 0:
        print_manager.error("No valid Carrington Longitudes found in the mapped time slice.")
        return
        
    carrington_lons_slice_valid = carrington_lons_slice[valid_lon_mask]
    time_slice_np_valid = time_slice_np[valid_lon_mask] # Keep track of valid times
    print_manager.debug(f"Filtered NaNs: {num_valid_lons} valid longitude points remain.")
    print_manager.debug(f"Carrington Lon range for slice (valid points): {np.min(carrington_lons_slice_valid):.2f}° to {np.max(carrington_lons_slice_valid):.2f}°")


    # --- Calculate Relative Degrees ---
    relative_degrees = carrington_lons_slice_valid - perihelion_lon_val
    print_manager.debug(f"Calculated relative degrees (before wrap). Range: {np.min(relative_degrees):.2f}° to {np.max(relative_degrees):.2f}°")
    
    # --- Apply Wrap-around ---
    relative_degrees[relative_degrees > 180] -= 360
    relative_degrees[relative_degrees <= -180] += 360
    print_manager.debug(f"Applied wrap-around. Final Range: {np.min(relative_degrees):.2f}° to {np.max(relative_degrees):.2f}°")

    # --- NEW: Print intermediate values ---
    print_manager.status("\n--- Sampled Values (Time vs. Degrees from Perihelion) ---")
    num_samples = 10
    indices_to_sample = np.linspace(0, len(relative_degrees) - 1, num_samples, dtype=int)
    print(f"{'Timestamp':<30} | {'Degrees from Peri':>15}")
    print("-"*48)
    for idx in indices_to_sample:
        timestamp_str = pd.Timestamp(time_slice_np_valid[idx]).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] # Format timestamp
        degrees_val = relative_degrees[idx]
        print(f"{timestamp_str:<30} | {degrees_val:15.4f}°")
    print("-"*48)
    # --- END NEW SECTION ---

    # --- Create Dummy Y Data ---
    # Simple sine wave based on degrees for visualization
    y_data = np.sin(np.radians(relative_degrees)) * 5 

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(relative_degrees, y_data, marker='.', linestyle='-', markersize=2)
    
    # Add vertical line at 0 degrees
    ax.axvline(0, color='r', linestyle='--', linewidth=1, label='Perihelion (0°)')
    
    # Formatting
    ax.set_xlabel("Calculated Degrees from Perihelion (°)")
    ax.set_ylabel("Dummy Data (Sine Wave)")
    ax.set_title(f"Standalone Degrees from Perihelion Calculation\nCentered on E17 Perihelion ({center_time_str})")
    ax.grid(True)
    ax.legend()
    
    # Set reasonable limits centered around 0, e.g., +/- 30 or 60 degrees
    # Or use the calculated range if it's reasonable
    min_deg, max_deg = np.min(relative_degrees), np.max(relative_degrees)
    ax.set_xlim(min_deg - 5, max_deg + 5) # Add padding
    
    # Save the plot
    save_dir = project_root / "local_images"
    save_dir.mkdir(exist_ok=True)
    save_path = save_dir / "debug_perihelion_mapping.png"
    try:
        fig.savefig(save_path, dpi=150)
        print_manager.status(f"Plot saved to: {save_path}")
    except Exception as e:
        print_manager.error(f"Failed to save plot: {e}")
        
    plt.close(fig) # Close plot to free memory

if __name__ == "__main__":
    # <<< NEW: Enable necessary print manager flags >>>
    print_manager.show_debug = True
    print_manager.show_status = True # Alias for show_variable_basic
    print("Enabled print_manager debug and status messages for this run.") # Print to console
    # <<< END NEW >>>
    try:
        test_perihelion_mapping_standalone()
    except Exception as e:
        print(f"\n!!! AN ERROR OCCURRED: {e} !!!") # Log errors to console
        import traceback
        traceback.print_exc() # Print traceback to console

    print("Script finished. Output printed to console.")