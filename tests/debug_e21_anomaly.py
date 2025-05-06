#!/usr/bin/env python
"""
Detailed investigation of E21 anomaly in Carrington longitude data.
"""
import numpy as np
import pandas as pd
import pathlib
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Perihelion time for E21
E21_PERIHELION = '2024/09/30 05:15:00.000'

def main():
    """Detailed investigation of E21 longitude anomaly."""
    # Load the raw positional data
    npz_path = pathlib.Path(__file__).parent.parent / "support_data" / "trajectories" / "Parker_positional_data.npz"
    assert npz_path.exists(), f"NPZ file not found: {npz_path}"
    with np.load(npz_path) as data:
        times = pd.to_datetime(data['times'])
        carr_lon = data['carrington_lon']
    
    print(f"Raw data summary:")
    print(f"  Number of time points: {len(times)}")
    print(f"  Date range: {times[0]} to {times[-1]}")
    print(f"  Longitude range: {np.min(carr_lon):.4f}° to {np.max(carr_lon):.4f}°")
    print(f"  Time resolution: ~{(times[1] - times[0]).total_seconds() / 60:.1f} minutes")
    
    # Convert perihelion time to datetime
    peri_time = pd.to_datetime(E21_PERIHELION)
    
    # Determine perihelion longitude using interpolation
    perihelion_lon = np.interp(peri_time.timestamp(), 
                               [t.timestamp() for t in times], 
                               carr_lon)
    print(f"\nE21 Perihelion: {E21_PERIHELION}")
    print(f"Perihelion longitude: {perihelion_lon:.4f}°")
    
    # Define a time window around perihelion (±5 days)
    window_days = 5
    start_time = peri_time - pd.Timedelta(days=window_days)
    end_time = peri_time + pd.Timedelta(days=window_days)
    
    # Get raw data within this window
    mask = (times >= start_time) & (times <= end_time)
    window_times = times[mask]
    window_lons = carr_lon[mask]
    
    # Print data closest to perihelion
    print("\nRAW DATA POINTS AROUND PERIHELION (±24 hours):")
    print(f"{'Offset (hr)':>12} | {'Timestamp':>24} | {'Raw Longitude':>14}")
    print("-"*60)
    
    close_mask = (window_times >= peri_time - pd.Timedelta(hours=24)) & (window_times <= peri_time + pd.Timedelta(hours=24))
    close_times = window_times[close_mask]
    close_lons = window_lons[close_mask]
    
    for t, lon in zip(close_times, close_lons):
        offset = (t - peri_time).total_seconds() / 3600  # hours
        print(f"{offset:12.1f} | {t} | {lon:14.4f}")
    
    # Create interpolation function for more detailed study
    def interp_longitude(t):
        return np.interp(t.timestamp(), [t.timestamp() for t in times], carr_lon)
    
    # Generate a denser time grid for smooth plotting
    hour_offsets = np.linspace(-24*window_days, 24*window_days, 100)
    sample_times = [peri_time + pd.Timedelta(hours=h) for h in hour_offsets]
    sample_lons = [interp_longitude(t) for t in sample_times]
    
    # Calculate degrees from perihelion (raw and wrapped)
    deg_from_peri_raw = [lon - perihelion_lon for lon in sample_lons]
    deg_from_peri_wrapped = [np.mod(d + 180, 360) - 180 for d in deg_from_peri_raw]
    
    # Find points where longitude crosses 0/360
    discontinuities = []
    for i in range(1, len(sample_lons)):
        if abs(sample_lons[i] - sample_lons[i-1]) > 180:
            discontinuities.append(i)
    
    # Print info about discontinuities
    if discontinuities:
        print("\nDISCONTINUITIES DETECTED (Longitude crosses 0/360):")
        for idx in discontinuities:
            offset = hour_offsets[idx]
            t = sample_times[idx]
            print(f"  At offset {offset:.1f} hours ({t})")
            print(f"    Before: {sample_lons[idx-1]:.4f}°")
            print(f"    After:  {sample_lons[idx]:.4f}°")
    else:
        print("\nNo longitude discontinuities detected in this time window.")
    
    # Create a multi-panel visualization
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Plot 1: Raw Carrington Longitude
    axs[0].plot(hour_offsets, sample_lons, 'b-', linewidth=2)
    axs[0].axvline(x=0, color='r', linestyle='--')
    axs[0].axhline(y=perihelion_lon, color='r', linestyle='--')
    axs[0].set_ylabel('Carrington Longitude (°)')
    axs[0].set_title('Raw Carrington Longitude vs. Time')
    axs[0].grid(True)
    
    # Plot 2: Raw Degrees from Perihelion (unconstrained)
    axs[1].plot(hour_offsets, deg_from_peri_raw, 'g-', linewidth=2)
    axs[1].axvline(x=0, color='r', linestyle='--')
    axs[1].axhline(y=0, color='r', linestyle='--')
    axs[1].set_ylabel('Degrees from Perihelion\n(Unwrapped)')
    axs[1].set_title('Raw Difference (lon - perihelion_lon)')
    axs[1].grid(True)
    
    # Plot 3: Wrapped Degrees from Perihelion ([-180, 180])
    axs[2].plot(hour_offsets, deg_from_peri_wrapped, 'c-', linewidth=2)
    axs[2].axvline(x=0, color='r', linestyle='--')
    axs[2].axhline(y=0, color='r', linestyle='--')
    axs[2].set_ylabel('Degrees from Perihelion\n(Wrapped to [-180, 180])')
    axs[2].set_xlabel('Hours from Perihelion')
    axs[2].set_title('Wrapped Difference (mod to [-180, 180] range)')
    axs[2].grid(True)
    
    # Mark discontinuities
    for idx in discontinuities:
        axs[0].axvline(x=hour_offsets[idx], color='orange', alpha=0.5)
        axs[1].axvline(x=hour_offsets[idx], color='orange', alpha=0.5)
        axs[2].axvline(x=hour_offsets[idx], color='orange', alpha=0.5)
    
    # Mark every 24 hours for reference
    for day in range(-window_days, window_days+1):
        if day != 0:  # Skip perihelion which already has a line
            axs[0].axvline(x=day*24, color='gray', alpha=0.3, linestyle=':')
            axs[1].axvline(x=day*24, color='gray', alpha=0.3, linestyle=':')
            axs[2].axvline(x=day*24, color='gray', alpha=0.3, linestyle=':')
    
    plt.tight_layout()
    
    # Save the figure
    output_path = pathlib.Path(__file__).parent / "e21_longitude_anomaly.png"
    plt.savefig(output_path)
    print(f"\nPlot saved to: {output_path}")
    
    # Print summary and potential issues
    print("\nSUMMARY AND ANALYSIS:")
    print("1. Examining whether the data crosses the 0/360° boundary, which could cause wrapping issues")
    print("2. Checking if the raw longitude data has any unexpected patterns or jumps")
    print("3. Analyzing how the wrapping to [-180, 180] affects the distribution of points")
    
    # Calculate some key statistics
    start_lon = interp_longitude(start_time)
    end_lon = interp_longitude(end_time)
    total_change = end_lon - start_lon
    if abs(total_change) > 180:
        # Handle potential wrap-around
        if total_change > 0:
            total_change = total_change - 360
        else:
            total_change = total_change + 360
    
    print(f"\nTotal longitude change over {window_days*2} days: {total_change:.2f}°")
    print(f"Average rate: {total_change/(window_days*2*24):.4f}°/hour")
    
    # Check temporal relationships
    # Find the time where longitude = perihelion_longitude ± 0.1°
    perihelion_matches = []
    for i, lon in enumerate(sample_lons):
        if abs(lon - perihelion_lon) < 0.1 or abs(lon - perihelion_lon - 360) < 0.1 or abs(lon - perihelion_lon + 360) < 0.1:
            perihelion_matches.append((hour_offsets[i], sample_times[i], lon))
    
    if perihelion_matches:
        print("\nTimes when longitude equals perihelion longitude (±0.1°):")
        for offset, t, lon in perihelion_matches:
            print(f"  Offset: {offset:.1f} hours, Time: {t}, Longitude: {lon:.4f}°")
    else:
        print("\nNo other times found where longitude equals perihelion longitude (±0.1°)")
    
if __name__ == "__main__":
    main() 