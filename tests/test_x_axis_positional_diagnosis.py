import sys
import os
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Add parent directory to path to import plotbot modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import plotbot as pb
from plotbot.multiplot_options import plt as pbplt
from plotbot.multiplot import multiplot
from plotbot.x_axis_positional_data_helpers import XAxisPositionalDataMapper

def diagnose_longitude_ticks():
    """Diagnose why the longitude ticks appear to cycle up and down"""
    
    # Set up the exact same scenario as in the problematic plot
    pbplt.options.reset()
    pbplt.options.use_longitude_x_axis = True
    pbplt.options.window = '24:00:00.000'
    
    # Use a high tick density to see the pattern clearly
    pbplt.options.longitude_tick_density = 4
    
    # Load data for the period
    center_time = '2023-09-27 23:28:00.000'  # E17 perihelion
    time_range = [
        '2023-09-27 12:00:00.000',  # 12 hours before
        '2023-09-28 12:00:00.000'   # 12 hours after
    ]
    
    print(f"Loading data for period: {time_range[0]} to {time_range[1]}")
    pb.get_data(time_range, pb.mag_rtn_4sa.br)
    
    # Create plot data - single panel with BR
    plot_data = [(center_time, pb.mag_rtn_4sa.br)]
    
    # Create the plot
    fig, axes = multiplot(plot_data)
    
    # Get the tick values and labels
    axis = axes[0]
    tick_positions = axis.get_xticks()
    tick_labels = [t.get_text() for t in axis.get_xticklabels()]
    
    print("\n=== X-AXIS TICK ANALYSIS ===")
    print(f"Number of ticks: {len(tick_positions)}")
    print(f"Tick positions: {tick_positions}")
    print(f"Tick labels: {tick_labels}")
    
    # Get the line data
    lines = axis.get_lines()
    if lines:
        x_data = lines[0].get_xdata()
        print(f"\nX-data type: {type(x_data)}")
        print(f"X-data shape: {x_data.shape}")
        print(f"X-data range: {np.min(x_data):.2f} to {np.max(x_data):.2f}")
        print(f"First 10 x-values: {x_data[:10]}")
        
        # Print diff between consecutive values to check for anomalies
        x_diffs = np.diff(x_data)
        print(f"\nDiffs between consecutive x-values:")
        print(f"Min diff: {np.min(x_diffs):.4f}")
        print(f"Max diff: {np.max(x_diffs):.4f}")
        print(f"Mean diff: {np.mean(x_diffs):.4f}")
        
        # Check if values are strictly increasing
        is_increasing = np.all(x_diffs > 0)
        print(f"X-values are strictly increasing: {is_increasing}")
        
        if not is_increasing:
            # Find the locations where values decrease
            decrease_indices = np.where(x_diffs <= 0)[0]
            print(f"Found {len(decrease_indices)} locations where x-values decrease")
            if len(decrease_indices) > 0:
                for idx in decrease_indices[:5]:  # Show first 5
                    print(f"At index {idx}: {x_data[idx]} -> {x_data[idx+1]} (diff: {x_diffs[idx]:.4f})")
    
    # Save the plot for inspection
    plt.savefig("longitude_xaxis_diagnosis.png")
    print("\nSaved plot to longitude_xaxis_diagnosis.png")

    # Now create a plot showing the relationship between the time stamps and longitude values
    # for the actual data being plotted
    if hasattr(pb.mag_rtn_4sa.br, 'datetime_array'):
        print("\n=== ANALYZING MAPPED VALUES ===")
        datetime_array = pb.mag_rtn_4sa.br.datetime_array
        
        # Convert to matplotlib dates for comparison
        mpl_dates = np.array([pd.Timestamp(dt).to_pydatetime() for dt in datetime_array])
        
        # Use the LongitudeMapper directly to see what's happening
        project_root = pathlib.Path(__file__).parent.parent
        data_path = project_root / "support_data" / "trajectories" / "Parker_positional_data.npz"
        
        mapper = XAxisPositionalDataMapper(str(data_path))
        longitudes = mapper.map_to_position(datetime_array, 'carrington_lon')
        
        # Find the points within our time range
        start_time = pd.to_datetime(time_range[0])
        end_time = pd.to_datetime(time_range[1])
        indices = np.where(
            (pd.DatetimeIndex(datetime_array) >= start_time) & 
            (pd.DatetimeIndex(datetime_array) <= end_time)
        )[0]
        
        selected_times = np.array(datetime_array)[indices]
        selected_longitudes = longitudes[indices]
        
        # Sort the data by longitude
        sorted_indices = np.argsort(selected_longitudes)
        sorted_longitudes = selected_longitudes[sorted_indices]
        sorted_times = selected_times[sorted_indices]
        
        # Plot the sorted and unsorted data
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Unsorted (natural time order)
        ax1.plot(selected_longitudes, 'b-', label='Longitudes in time order')
        ax1.set_ylabel('Longitude (deg)')
        ax1.set_title('Longitude Values vs Array Index (time order)')
        ax1.grid(True)
        ax1.legend()
        
        # Sorted by longitude value
        ax2.plot(sorted_longitudes, 'r-', label='Longitudes (sorted)')
        ax2.set_ylabel('Longitude (deg)')
        ax2.set_xlabel('Array Index (sorted by longitude)')
        ax2.set_title('Longitude Values vs Array Index (sorted by longitude)')
        ax2.grid(True)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig("longitude_mapping_analysis.png")
        print("Saved additional analysis to longitude_mapping_analysis.png")
        
if __name__ == "__main__":
    diagnose_longitude_ticks() 