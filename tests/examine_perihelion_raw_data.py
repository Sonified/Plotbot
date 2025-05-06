#!/usr/bin/env python
"""
Script for examining raw positional data around perihelion times
to better understand longitude behavior and degrees from perihelion.
"""
import sys
import os
import pathlib

# Add the project root to the Python path to make plotbot module importable
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
# Import the new helper class
from plotbot.x_axis_positional_data_helpers import XAxisPositionalDataMapper

# Define perihelion times for all encounters
PERIHELION_TIMES = {
    1: '2018/11/06 03:27:00.000', 2: '2019/04/04 22:39:00.000', 3: '2019/09/01 17:50:00.000',
    4: '2020/01/29 09:37:00.000', 5: '2020/06/07 08:23:00.000', 6: '2020/09/27 09:16:00.000',
    7: '2021/01/17 17:40:00.000', 8: '2021/04/29 08:48:00.000', 9: '2021/08/09 19:11:00.000',
    10: '2021/11/21 08:23:00.000', 11: '2022/02/25 15:38:00.000', 12: '2022/06/01 22:51:00.000',
    13: '2022/09/06 06:04:00.000', 14: '2022/12/11 13:16:00.000', 15: '2023/03/17 20:30:00.000',
    16: '2023/06/22 03:46:00.000', 17: '2023/09/27 23:28:00.000', 18: '2023/12/29 00:56:00.000',
    19: '2024/03/30 02:21:00.000', 20: '2024/06/30 03:47:00.000', 21: '2024/09/30 05:15:00.000',
    22: '2024/12/24 11:53:00.000', 23: '2025/03/22 22:42:00.000',
}

def main():
    """Examine the raw positional data around perihelion times."""
    # Load the position data
    npz_path = pathlib.Path(__file__).parent.parent / "support_data" / "trajectories" / "Parker_positional_data.npz"
    assert npz_path.exists(), f"NPZ file not found: {npz_path}"
    
    # Create positional data mapper for unwrapped longitude
    mapper = XAxisPositionalDataMapper(str(npz_path))
    
    # Load data for the old (direct) method too
    with np.load(npz_path) as data:
        times = pd.to_datetime(data['times'])
        carr_lon = data['carrington_lon']
    
    # Look at a subset of encounters - choose ones known to be interesting
    # Include problematic encounters (like E21 that crosses 0°/360° boundary)
    encounters = [17, 21]
    
    for enc in encounters:
        peri_time = pd.to_datetime(PERIHELION_TIMES[enc])
        print(f"\n{'='*30} E{enc} ({PERIHELION_TIMES[enc]}) {'='*30}")
        
        # Create numpy datetime64 array for the perihelion time
        peri_time_np = np.array([np.datetime64(peri_time)])
        
        # Method 1: Direct interpolation (old approach)
        # Determine perihelion longitude using direct interpolation
        perihelion_lon_direct = np.interp(peri_time.timestamp(), 
                                  [t.timestamp() for t in times], 
                                  carr_lon)
        print(f"Perihelion longitude (direct interp): {perihelion_lon_direct:.4f}°")
        
        # Method 2: Using the mapper (new approach)
        perihelion_lon_unwrapped = mapper.map_to_position(peri_time_np, 'carrington_lon', unwrap_angles=True)[0]
        print(f"Perihelion longitude (unwrapped): {perihelion_lon_unwrapped:.4f}°\n")
        
        # Generate test samples in a +/- 48 hour window
        hours = 48  # +/- this many hours
        num_samples = 15
        hour_offsets = np.linspace(-hours, hours, num_samples)
        
        # Create sample times centered on perihelion
        sample_times = [peri_time + pd.Timedelta(hours=dt) for dt in hour_offsets]
        sample_times_np = np.array([np.datetime64(t) for t in sample_times])
        
        # Method 1: Direct interpolation (old approach)
        sample_times_numeric = [t.timestamp() for t in sample_times]
        interp_lons_direct = np.interp(sample_times_numeric, [t.timestamp() for t in times], carr_lon)
        
        # Method 2: Using the mapper (new approach)
        interp_lons_unwrapped = mapper.map_to_position(sample_times_np, 'carrington_lon', unwrap_angles=True)
        
        # Calculate degrees from perihelion - old approach
        deg_from_peri_direct = interp_lons_direct - perihelion_lon_direct
        # Apply wrap-around to keep values in [-180, 180] range (old approach)
        deg_from_peri_wrapped = np.mod(deg_from_peri_direct + 180, 360) - 180
        
        # Calculate degrees from perihelion - new approach with unwrapped longitudes
        deg_from_peri_unwrapped = interp_lons_unwrapped - perihelion_lon_unwrapped
        
        # Data table output
        print(f"{'Hour Offset':>12} | {'Direct Lon':>12} | {'Unwrapped Lon':>15} | {'Wrapped Deg':>12} | {'Unwrapped Deg':>15}")
        print("-"*80)
        for i, dt in enumerate(hour_offsets):
            print(f"{dt:12.1f} | {interp_lons_direct[i]:12.4f} | {interp_lons_unwrapped[i]:15.4f} | {deg_from_peri_wrapped[i]:12.4f} | {deg_from_peri_unwrapped[i]:15.4f}")
        
        # Calculate rate of change (deg/hour) using central differences for unwrapped degrees
        # Note: We use adjacent points (i+1, i-1) for better accuracy
        rates = np.zeros_like(hour_offsets)
        
        # For first point, use forward difference
        rates[0] = (deg_from_peri_unwrapped[1] - deg_from_peri_unwrapped[0]) / (hour_offsets[1] - hour_offsets[0])
        
        # For middle points, use central difference
        for i in range(1, len(rates) - 1):
            rates[i] = (deg_from_peri_unwrapped[i+1] - deg_from_peri_unwrapped[i-1]) / (hour_offsets[i+1] - hour_offsets[i-1])
        
        # For last point, use backward difference
        rates[-1] = (deg_from_peri_unwrapped[-1] - deg_from_peri_unwrapped[-2]) / (hour_offsets[-1] - hour_offsets[-2])
        
        # Print mean rate
        print(f"\nMean rotation rate: {np.mean(rates):.4f} deg/hour")
        print(f"Rate at perihelion: {rates[num_samples//2]:.4f} deg/hour")
        
        # Plot comparison of wrapped vs unwrapped
        fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        
        # Plot 1: Raw Longitudes
        axs[0].plot(hour_offsets, interp_lons_direct, 'b-', marker='o', label='Direct Longitude [0, 360°]')
        axs[0].plot(hour_offsets, interp_lons_unwrapped, 'r--', marker='x', label='Unwrapped Longitude')
        axs[0].axvline(x=0, color='k', linestyle='--', label='Perihelion')
        axs[0].axhline(y=perihelion_lon_direct, color='b', linestyle=':', label=f'Direct Peri Lon: {perihelion_lon_direct:.2f}°')
        axs[0].axhline(y=perihelion_lon_unwrapped, color='r', linestyle=':', label=f'Unwrapped Peri Lon: {perihelion_lon_unwrapped:.2f}°')
        axs[0].set_ylabel('Carrington Longitude (°)')
        axs[0].set_title(f'E{enc} - Raw Longitude Values Around Perihelion')
        axs[0].grid(True)
        axs[0].legend()
        
        # Plot 2: Degrees from Perihelion
        axs[1].plot(hour_offsets, deg_from_peri_wrapped, 'b-', marker='o', label='Wrapped [-180, 180°]')
        axs[1].plot(hour_offsets, deg_from_peri_unwrapped, 'r--', marker='x', label='Unwrapped (continuous)')
        axs[1].axvline(x=0, color='k', linestyle='--')
        axs[1].axhline(y=0, color='k', linestyle=':')
        axs[1].set_xlabel('Hours from Perihelion')
        axs[1].set_ylabel('Degrees from Perihelion (°)')
        axs[1].set_title(f'E{enc} - Degrees from Perihelion Comparison')
        axs[1].grid(True)
        axs[1].legend()
        
        plt.tight_layout()
        output_file = pathlib.Path(__file__).parent / f"e{enc}_perihelion_data_analysis.png"
        plt.savefig(output_file)
        print(f"Plot saved to: {output_file}")
        
if __name__ == "__main__":
    main() 