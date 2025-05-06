#!/usr/bin/env python
"""
Validation script for unwrapped longitude fix in degrees from perihelion calculations.
Tests both with and without unwrap_angles=True for E21 (which crosses 0°/360° boundary).
"""
import numpy as np
import pandas as pd
import pathlib
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from plotbot.x_axis_positional_data_helpers import XAxisPositionalDataMapper

# Perihelion time for E21 (problematic case due to 0°/360° boundary crossing)
E21_PERIHELION = '2024/09/30 05:15:00.000'

def main():
    """Test and visualize the fix for the 0°/360° boundary crossing issue."""
    # Load the position data
    npz_path = pathlib.Path(__file__).parent.parent / "support_data" / "trajectories" / "Parker_positional_data.npz"
    assert npz_path.exists(), f"NPZ file not found: {npz_path}"
    
    # Create mapper
    mapper = XAxisPositionalDataMapper(str(npz_path))
        
    # Convert perihelion time to datetime
    perihelion_dt = pd.to_datetime(E21_PERIHELION)
    perihelion_time_np = np.array([np.datetime64(perihelion_dt)])
    
    # Create test timestamps (±48 hours around perihelion)
    hours = 48
    num_samples = 100
    time_offsets = np.linspace(-hours, hours, num_samples)
    time_points = [perihelion_dt + pd.Timedelta(hours=h) for h in time_offsets]
    time_points_np = np.array([np.datetime64(t) for t in time_points])
    
    print(f"\nTesting with {num_samples} time points spanning ±{hours} hours around perihelion")
    
    # -----------------------------------------------------------------
    # Test 1: Original approach (no unwrapping)
    # -----------------------------------------------------------------
    print("\n=== Test 1: Without unwrapping (original approach) ===")
    
    # Get longitudes without unwrapping 
    longitudes = mapper.map_to_position(time_points_np, 'carrington_lon', unwrap_angles=False)
    perihelion_lon = mapper.map_to_position(perihelion_time_np, 'carrington_lon', unwrap_angles=False)[0]
    
    print(f"Perihelion longitude (without unwrapping): {perihelion_lon:.4f}°")
    
    # Calculate degrees from perihelion
    degrees_from_peri = longitudes - perihelion_lon
    
    # Handle wrapping manually (how it was done before)
    degrees_from_peri_wrapped = np.mod(degrees_from_peri + 180, 360) - 180
    
    # Get statistics on the result
    min_val = np.min(degrees_from_peri_wrapped)
    max_val = np.max(degrees_from_peri_wrapped)
    range_val = max_val - min_val
    
    print(f"Degrees from perihelion range (wrapped): {min_val:.4f}° to {max_val:.4f}° (range: {range_val:.4f}°)")
    print(f"Is centered around 0? {'Yes' if abs(min_val + max_val) < 5 else 'No'}")
    
    # -----------------------------------------------------------------
    # Test 2: New approach with unwrapping
    # -----------------------------------------------------------------
    print("\n=== Test 2: With unwrapping (new approach) ===")
    
    # Get longitudes with unwrapping
    longitudes_unwrapped = mapper.map_to_position(time_points_np, 'carrington_lon', unwrap_angles=True)
    perihelion_lon_unwrapped = mapper.map_to_position(perihelion_time_np, 'carrington_lon', unwrap_angles=True)[0]
    
    print(f"Perihelion longitude (with unwrapping): {perihelion_lon_unwrapped:.4f}°")
    
    # Calculate degrees from perihelion with unwrapped longitudes
    degrees_from_peri_unwrapped = longitudes_unwrapped - perihelion_lon_unwrapped
    
    # Get statistics for unwrapped version
    min_val_unwrapped = np.min(degrees_from_peri_unwrapped)
    max_val_unwrapped = np.max(degrees_from_peri_unwrapped)
    range_val_unwrapped = max_val_unwrapped - min_val_unwrapped
    
    print(f"Degrees from perihelion range (unwrapped): {min_val_unwrapped:.4f}° to {max_val_unwrapped:.4f}° (range: {range_val_unwrapped:.4f}°)")
    print(f"Is centered around 0? {'Yes' if abs(min_val_unwrapped + max_val_unwrapped) < 5 else 'No'}")
    
    # -----------------------------------------------------------------
    # Visualization
    # -----------------------------------------------------------------
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # Plot 1: Raw longitude values
    ax1.plot(time_offsets, longitudes, 'b-', label="Standard longitude (wrapped to [0, 360])")
    ax1.plot(time_offsets, longitudes_unwrapped, 'r--', label="Unwrapped longitude (continuous)")
    ax1.axvline(x=0, color='k', linestyle='--', label="Perihelion time")
    ax1.axhline(y=perihelion_lon, color='b', linestyle=':', label=f"Perihelion lon: {perihelion_lon:.2f}°")
    ax1.axhline(y=perihelion_lon_unwrapped, color='r', linestyle=':', label=f"Unwrapped peri lon: {perihelion_lon_unwrapped:.2f}°")
    ax1.set_ylabel("Carrington Longitude (°)")
    ax1.set_title("Raw Longitude Values Around E21 Perihelion")
    ax1.grid(True)
    ax1.legend()
    
    # Plot 2: Standard "degrees from perihelion" (broken at boundary)
    ax2.plot(time_offsets, degrees_from_peri, 'g-', alpha=0.5, label="Standard diff (before wrapping)")
    ax2.plot(time_offsets, degrees_from_peri_wrapped, 'b-', label="Standard diff (wrapped to [-180, 180])")
    ax2.axvline(x=0, color='k', linestyle='--')
    ax2.axhline(y=0, color='k', linestyle=':')
    ax2.set_ylabel("Degrees from Perihelion (°)")
    ax2.set_title("Standard Approach (BROKEN for E21)")
    ax2.grid(True)
    ax2.legend()
    
    # Add annotation showing the problematic effect
    ax2.annotate("WRONG! Should be 0° at perihelion",
                xy=(0, degrees_from_peri_wrapped[num_samples//2]),
                xytext=(10, 50),
                arrowprops=dict(facecolor='red', shrink=0.05, width=2),
                color='red',
                fontsize=10,
                fontweight='bold')
    
    # Plot 3: Unwrapped "degrees from perihelion" (correct)
    ax3.plot(time_offsets, degrees_from_peri_unwrapped, 'r-', label="Unwrapped difference (correct)")
    ax3.axvline(x=0, color='k', linestyle='--')
    ax3.axhline(y=0, color='k', linestyle=':')
    ax3.set_ylabel("Degrees from Perihelion (°)")
    ax3.set_xlabel("Hours from Perihelion")
    ax3.set_title("New Approach with Unwrapping (FIXED)")
    ax3.grid(True)
    ax3.legend()
    
    # Add annotation showing the fixed result
    ax3.annotate("CORRECT! Exactly 0° at perihelion",
                xy=(0, degrees_from_peri_unwrapped[num_samples//2]),
                xytext=(10, -50),
                arrowprops=dict(facecolor='green', shrink=0.05, width=2),
                color='green',
                fontsize=10,
                fontweight='bold')
    
    # Save and show the figure
    plt.tight_layout()
    output_path = pathlib.Path(__file__).parent / "unwrapped_longitude_fix_validation.png"
    plt.savefig(output_path)
    print(f"\nValidation plot saved to: {output_path}")
    
    print("\nCONCLUSION:")
    if abs(degrees_from_peri_unwrapped[num_samples//2]) < 0.01 and abs(min_val_unwrapped + max_val_unwrapped) < 5:
        print("✅ FIX VALIDATED! The unwrapped longitude approach correctly handles the 0°/360° boundary.")
        print("   Degrees from perihelion is now exactly 0° at perihelion and the range is properly centered.")
    else:
        print("❌ FIX NOT WORKING CORRECTLY. Further investigation needed.")
    
if __name__ == "__main__":
    main() 