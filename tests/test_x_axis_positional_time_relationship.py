import sys
import os
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Add parent directory to path to import plotbot modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from plotbot.x_axis_positional_data_helpers import XAxisPositionalDataMapper

def plot_time_vs_longitude():
    """Create a plot showing the relationship between time and Carrington longitude"""
    
    # Get the path to the longitude data file
    project_root = pathlib.Path(__file__).parent.parent
    data_path = project_root / "support_data" / "trajectories" / "Parker_positional_data.npz"
    
    if not data_path.exists():
        print(f"ERROR: Data file not found at {data_path}")
        return
    
    print(f"Loading longitude data from: {data_path}")
    
    # Load the NPZ file directly to see the raw data
    data = np.load(str(data_path))
    
    # Check what arrays are in the file
    print(f"Arrays in NPZ file: {data.files}")
    
    # Extract the data using the correct array names
    times = data['times']
    longitudes = data['values']  # The file uses 'values' instead of 'longitudes'
    
    # Print column names if available
    if 'time_column_name' in data.files and 'value_column_name' in data.files:
        time_column_name = str(data['time_column_name'])
        value_column_name = str(data['value_column_name'])
        print(f"Time column name: {time_column_name}")
        print(f"Value column name: {value_column_name}")
    
    # Print some basic info about the data
    print(f"Time array shape: {times.shape}")
    print(f"Longitude array shape: {longitudes.shape}")
    print(f"Time range: {times[0]} to {times[-1]}")
    print(f"Longitude range: {np.min(longitudes):.2f}° to {np.max(longitudes):.2f}°")
    
    # Convert times to datetime
    datetime_array = np.array([pd.to_datetime(t) for t in times])
    
    # Find the Encounter 17 period (around 2023-09-27 23:28)
    center_date = pd.to_datetime("2023-09-27 23:28:00")
    
    # Define a 24-hour window around the center date
    start_date = center_date - pd.Timedelta(hours=12)
    end_date = center_date + pd.Timedelta(hours=12)
    
    # Find the indices of data points within our time range
    indices = np.where((datetime_array >= start_date) & (datetime_array <= end_date))[0]
    
    # Extract the data for our time range
    selected_times = datetime_array[indices]
    selected_longitudes = longitudes[indices]
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Plot 1: Time vs Longitude
    ax1.plot(selected_times, selected_longitudes, 'b-')
    ax1.set_ylabel('Carrington Longitude (deg)')
    ax1.set_title('Time vs Longitude (E17 Period)')
    ax1.grid(True)
    
    # Check if longitudes are wrapping around 0-360
    is_wrapping = np.any(np.diff(selected_longitudes) < -180)
    print(f"Longitude data appears to be wrapping around 0-360°: {is_wrapping}")
    
    # Check for large jumps in longitude
    lon_diffs = np.diff(selected_longitudes)
    large_jumps = np.where(np.abs(lon_diffs) > 10)[0]
    if len(large_jumps) > 0:
        print(f"Found {len(large_jumps)} large jumps (>10°) in longitude data")
        print(f"Jump locations: {large_jumps}")
        print(f"Jump sizes: {lon_diffs[large_jumps]}")
    
    # Plot 2: Time vs Longitude (unwrapped if needed)
    # This will show a continuous curve without the modulo 360° wrapping
    unwrapped_longitudes = np.copy(selected_longitudes)
    if is_wrapping:
        for i in range(1, len(unwrapped_longitudes)):
            if unwrapped_longitudes[i] - unwrapped_longitudes[i-1] < -180:
                # Add 360° to this and all following points when we wrap from 359° to 0°
                unwrapped_longitudes[i:] += 360
            elif unwrapped_longitudes[i] - unwrapped_longitudes[i-1] > 180:
                # Subtract 360° when we wrap from 0° to 359°
                unwrapped_longitudes[i:] -= 360
    
    ax2.plot(selected_times, unwrapped_longitudes, 'r-')
    ax2.set_ylabel('Carrington Longitude (unwrapped, deg)')
    ax2.set_xlabel('Time')
    ax2.grid(True)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig("time_vs_longitude_analysis.png")
    print("Created time_vs_longitude_analysis.png")
    
    # Option to create a plot showing the longitude data used by multiplot
    # Use the XAxisPositionalDataMapper class to simulate how multiplot would map times to longitudes
    mapper = XAxisPositionalDataMapper(str(data_path))
    
    # Generate a dense set of time points
    dense_times = pd.date_range(start=start_date, end=end_date, periods=1000)
    dense_times_np = dense_times.to_numpy()
    
    # Map to longitude
    mapped_longitudes = mapper.map_to_position(dense_times_np, 'carrington_lon')
    
    # Create a plot showing what multiplot would use
    plt.figure(figsize=(12, 6))
    plt.plot(dense_times, mapped_longitudes, 'g-', label='Mapped longitude')
    plt.xlabel('Time')
    plt.ylabel('Carrington Longitude (deg)')
    plt.title('Longitude Values Used By Multiplot')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("multiplot_longitude_mapping.png")
    print("Created multiplot_longitude_mapping.png")
    
    return selected_times, selected_longitudes, unwrapped_longitudes

if __name__ == "__main__":
    plot_time_vs_longitude() 