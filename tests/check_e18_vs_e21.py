#!/usr/bin/env python
"""
Compare E18 (normal case) vs E21 (problematic case) to understand the boundary crossing issue.
"""
import numpy as np
import pandas as pd
import pathlib
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Perihelion times 
PERIHELION_TIMES = {
    18: '2023/12/29 00:56:00.000',  # Normal case
    21: '2024/09/30 05:15:00.000',  # Problematic case
}

def main():
    """Compare E18 vs E21 longitude behavior near perihelion."""
    # Load the raw positional data
    npz_path = pathlib.Path(__file__).parent.parent / "support_data" / "trajectories" / "Parker_positional_data.npz"
    assert npz_path.exists(), f"NPZ file not found: {npz_path}"
    with np.load(npz_path) as data:
        times = pd.to_datetime(data['times'])
        carr_lon = data['carrington_lon']
    
    print(f"Raw data summary:")
    print(f"  Number of time points: {len(times)}")
    print(f"  Time resolution: ~{(times[1] - times[0]).total_seconds() / 60:.1f} minutes")
    
    # Create a figure for comparison
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    
    # Process both encounters
    for i, enc in enumerate([18, 21]):
        peri_time = pd.to_datetime(PERIHELION_TIMES[enc])
        
        print(f"\n{'='*20} E{enc} ANALYSIS {'='*20}")
        print(f"Perihelion time: {PERIHELION_TIMES[enc]}")
        
        # Get raw data within ±24 hours window
        window_hours = 24
        start_time = peri_time - pd.Timedelta(hours=window_hours)
        end_time = peri_time + pd.Timedelta(hours=window_hours)
        
        # Get NPZ data points within this window
        mask = (times >= start_time) & (times <= end_time)
        window_times = times[mask]
        window_lons = carr_lon[mask]
        
        # Calculate hours from perihelion for each data point
        hour_offsets = [(t - peri_time).total_seconds() / 3600 for t in window_times]
        
        # Standard perihelion longitude calculation (direct np.interp call)
        perihelion_lon_std = np.interp(peri_time.timestamp(), 
                                     [t.timestamp() for t in times], 
                                     carr_lon)
        
        print(f"Standard interpolated perihelion longitude: {perihelion_lon_std:.4f}°")
        
        # Find the closest data point to perihelion
        closest_idx = np.argmin(np.abs(window_times - peri_time))
        closest_time = window_times[closest_idx]
        closest_lon = window_lons[closest_idx]
        time_diff = (closest_time - peri_time).total_seconds() / 60  # minutes
        
        print(f"Closest data point:")
        print(f"  Time: {closest_time} ({time_diff:.1f} minutes from perihelion)")
        print(f"  Longitude: {closest_lon:.4f}°")
        
        # Find data points immediately before and after perihelion
        before_mask = window_times < peri_time
        after_mask = window_times > peri_time
        
        if any(before_mask):
            before_time = window_times[before_mask][-1]
            before_lon = window_lons[before_mask][-1]
            print(f"Point immediately before perihelion:")
            print(f"  Time: {before_time} ({(before_time - peri_time).total_seconds() / 60:.1f} minutes)")
            print(f"  Longitude: {before_lon:.4f}°")
        
        if any(after_mask):
            after_time = window_times[after_mask][0]
            after_lon = window_lons[after_mask][0]
            print(f"Point immediately after perihelion:")
            print(f"  Time: {after_time} ({(after_time - peri_time).total_seconds() / 60:.1f} minutes)")
            print(f"  Longitude: {after_lon:.4f}°")
        
        # Check if we cross the 0/360° boundary near perihelion
        crosses_boundary = False
        for j in range(1, len(window_lons)):
            if abs(window_lons[j] - window_lons[j-1]) > 180:
                crosses_boundary = True
                cross_time = window_times[j]
                cross_time_diff = (cross_time - peri_time).total_seconds() / 3600  # hours
                print(f"BOUNDARY CROSSING DETECTED:")
                print(f"  At time: {cross_time} ({cross_time_diff:.2f} hours from perihelion)")
                print(f"  From {window_lons[j-1]:.4f}° to {window_lons[j]:.4f}°")
                break
        
        if not crosses_boundary:
            print("No 0/360° boundary crossing detected in the ±24 hour window.")
        
        # Plot raw longitude data
        axs[i, 0].plot(hour_offsets, window_lons, 'o-', markersize=4)
        axs[i, 0].axvline(x=0, color='r', linestyle='--')
        axs[i, 0].set_title(f"E{enc} - Raw Carrington Longitude")
        axs[i, 0].set_ylabel("Longitude (°)")
        axs[i, 0].grid(True)
        
        # Generate denser sample points for smooth interpolation plot
        sample_hours = np.linspace(-window_hours, window_hours, 200)
        sample_times = [peri_time + pd.Timedelta(hours=h) for h in sample_hours]
        sample_times_sec = [t.timestamp() for t in sample_times]
        
        # Handle boundary crossing properly for visualization
        times_sec = [t.timestamp() for t in window_times]
        
        # For visualization, shift all longitudes above 180° down by 360° if needed
        if crosses_boundary:
            # Find where the discontinuity occurs
            for j in range(1, len(window_lons)):
                if window_lons[j] < 90 and window_lons[j-1] > 270:
                    # Shift all points below the discontinuity up by 360°
                    offset_lons = window_lons.copy()
                    for k in range(j, len(offset_lons)):
                        offset_lons[k] += 360
                    
                    # Direct interpolation will still be wrong (misleading!)
                    direct_interp = np.interp(peri_time.timestamp(), times_sec, window_lons)
                    
                    # Corrected interpolation accounting for boundary
                    corrected_interp = np.interp(peri_time.timestamp(), times_sec, offset_lons)
                    corrected_interp = corrected_interp % 360
                    
                    print("\nINTERPOLATION ANALYSIS WITH BOUNDARY CORRECTION:")
                    print(f"  Uncorrected direct interpolation: {direct_interp:.4f}°")
                    print(f"  Corrected interpolation: {corrected_interp:.4f}°")
                    print(f"  Difference: {abs(direct_interp - corrected_interp):.4f}°")
                    
                    # Plot offset longitudes for better visualization
                    axs[i, 1].plot(hour_offsets, offset_lons, 'o-', markersize=4, color='green', 
                                  label="Shifted longitudes (boundary corrected)")
                    
                    # Interpolate in the offset space for better visualization
                    offset_interp = np.interp(sample_times_sec, times_sec, offset_lons)
                    axs[i, 1].plot(sample_hours, offset_interp, '--', color='purple', 
                                  label="Interpolation with boundary correction")
                    break
        
        # Direct interpolation
        direct_interp = np.interp(sample_times_sec, times_sec, window_lons)
        
        # Plot interpolation results
        axs[i, 1].plot(sample_hours, direct_interp, '-', color='blue', 
                      label="Standard interpolation")
        axs[i, 1].axvline(x=0, color='r', linestyle='--')
        axs[i, 1].axhline(y=perihelion_lon_std, color='r', linestyle='--', 
                         label=f"Interpolated perihelion lon: {perihelion_lon_std:.2f}°")
        axs[i, 1].set_title(f"E{enc} - Interpolation Analysis")
        axs[i, 1].set_ylabel("Longitude (°)")
        axs[i, 1].legend()
        axs[i, 1].grid(True)
    
    # Set common labels
    for ax in axs[-1, :]:
        ax.set_xlabel("Hours from Perihelion")
    
    axs[0, 0].set_title("E18 - Raw Carrington Longitude (No boundary crossing)")
    axs[1, 0].set_title("E21 - Raw Carrington Longitude (Crosses 0°/360° boundary)")
    
    axs[0, 1].set_title("E18 - Interpolation Analysis (Well-behaved)")
    axs[1, 1].set_title("E21 - Interpolation Analysis (Misleading due to boundary)")
    
    plt.tight_layout()
    plt.savefig("e18_vs_e21_comparison.png")
    print("\nComparison plot saved to: e18_vs_e21_comparison.png")
    
    print("\nCONCLUSION:")
    print("1. E18 has no boundary crossing, so standard interpolation works correctly.")
    print("2. E21 crosses the 0°/360° boundary VERY CLOSE to perihelion, causing:")
    print("   - Standard np.interp gives completely wrong perihelion longitude")
    print("   - Degrees from perihelion calculations are severely skewed")
    print("   - Need to handle the circular nature of longitude properly")
    
if __name__ == "__main__":
    main() 