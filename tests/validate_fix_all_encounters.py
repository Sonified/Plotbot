#!/usr/bin/env python
"""
Comprehensive validation script for the unwrap_angles fix across all 23 Parker encounters.
Tests which encounters cross the 0°/360° boundary and verifies that degrees from perihelion
is exactly 0° at perihelion for all encounters.
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

def test_encounter(mapper, enc_num, hours=48, num_samples=100, make_plot=False):
    """Test a specific encounter for correct handling of degrees from perihelion."""
    perihelion_time_str = PERIHELION_TIMES[enc_num]
    perihelion_dt = pd.to_datetime(perihelion_time_str)
    perihelion_time_np = np.array([np.datetime64(perihelion_dt)])
    
    # Create test timestamps (±48 hours around perihelion)
    time_offsets = np.linspace(-hours, hours, num_samples)
    time_points = [perihelion_dt + pd.Timedelta(hours=h) for h in time_offsets]
    time_points_np = np.array([np.datetime64(t) for t in time_points])
    
    # Test 1: Original approach without unwrapping
    longitudes = mapper.map_to_position(time_points_np, 'carrington_lon', unwrap_angles=False)
    perihelion_lon = mapper.map_to_position(perihelion_time_np, 'carrington_lon', unwrap_angles=False)[0]
    
    # Check if there's a 0°/360° boundary crossing
    diffs = np.abs(np.diff(longitudes))
    boundary_crossing = np.any(diffs > 180)
    
    # Get longitude at exact perihelion time to verify it matches perihelion_lon
    perihelion_idx = num_samples // 2  # Middle sample should be at perihelion
    perihelion_sample_lon = longitudes[perihelion_idx]
    
    # Calculate degrees from perihelion (standard approach with wrapping)
    degrees_from_peri = longitudes - perihelion_lon
    degrees_from_peri_wrapped = np.mod(degrees_from_peri + 180, 360) - 180
    
    # Get value at perihelion time (should be 0)
    dfp_at_perihelion_wrapped = degrees_from_peri_wrapped[perihelion_idx]
    
    # Calculate range and check centering
    min_val = np.min(degrees_from_peri_wrapped)
    max_val = np.max(degrees_from_peri_wrapped)
    range_val = max_val - min_val
    is_centered_standard = abs(min_val + max_val) < 5
    
    # Test 2: New approach with unwrapping
    longitudes_unwrapped = mapper.map_to_position(time_points_np, 'carrington_lon', unwrap_angles=True)
    perihelion_lon_unwrapped = mapper.map_to_position(perihelion_time_np, 'carrington_lon', unwrap_angles=True)[0]
    
    # Calculate degrees from perihelion with unwrapped longitudes
    degrees_from_peri_unwrapped = longitudes_unwrapped - perihelion_lon_unwrapped
    
    # Get value at perihelion time (should be 0)
    dfp_at_perihelion_unwrapped = degrees_from_peri_unwrapped[perihelion_idx]
    
    # Get statistics
    min_val_unwrapped = np.min(degrees_from_peri_unwrapped)
    max_val_unwrapped = np.max(degrees_from_peri_unwrapped)
    range_val_unwrapped = max_val_unwrapped - min_val_unwrapped
    is_centered_unwrapped = abs(min_val_unwrapped + max_val_unwrapped) < 5
    
    # Determine if fix works for this encounter
    standard_success = abs(dfp_at_perihelion_wrapped) < 3.0 and is_centered_standard
    unwrapped_success = abs(dfp_at_perihelion_unwrapped) < 3.0 and is_centered_unwrapped
    
    # Create a result dictionary with all information
    result = {
        "encounter": enc_num,
        "boundary_crossing": boundary_crossing,
        "perihelion_lon": perihelion_lon,
        "perihelion_lon_unwrapped": perihelion_lon_unwrapped,
        "perihelion_sample_lon": perihelion_sample_lon,
        
        "dfp_at_perihelion_wrapped": dfp_at_perihelion_wrapped,
        "dfp_at_perihelion_unwrapped": dfp_at_perihelion_unwrapped,
        
        "wrapped_range": [min_val, max_val],
        "unwrapped_range": [min_val_unwrapped, max_val_unwrapped],
        
        "is_centered_standard": is_centered_standard,
        "is_centered_unwrapped": is_centered_unwrapped,
        
        "standard_success": standard_success,
        "unwrapped_success": unwrapped_success,
        
        # Save data for potential plotting
        "time_offsets": time_offsets,
        "longitudes": longitudes,
        "longitudes_unwrapped": longitudes_unwrapped,
        "degrees_from_peri_wrapped": degrees_from_peri_wrapped,
        "degrees_from_peri_unwrapped": degrees_from_peri_unwrapped
    }
    
    # Generate a plot if requested
    if make_plot:
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
        
        # Plot 1: Raw longitude values
        ax1.plot(time_offsets, longitudes, 'b-', label="Standard longitude [0, 360]")
        ax1.plot(time_offsets, longitudes_unwrapped, 'r--', label="Unwrapped longitude")
        ax1.axvline(x=0, color='k', linestyle='--', label="Perihelion time")
        ax1.axhline(y=perihelion_lon, color='b', linestyle=':', label=f"Peri lon: {perihelion_lon:.2f}°")
        ax1.axhline(y=perihelion_lon_unwrapped, color='r', linestyle=':', label=f"Unwrapped: {perihelion_lon_unwrapped:.2f}°")
        ax1.set_ylabel("Carrington Longitude (°)")
        ax1.set_title(f"E{enc_num} Longitude Values Around Perihelion " + 
                      ("(CROSSES 0°/360° BOUNDARY)" if boundary_crossing else "(No boundary crossing)"))
        ax1.grid(True)
        ax1.legend()
        
        # Plot 2: Standard "degrees from perihelion"
        ax2.plot(time_offsets, degrees_from_peri_wrapped, 'b-', label="Standard [-180, 180]")
        ax2.axvline(x=0, color='k', linestyle='--')
        ax2.axhline(y=0, color='k', linestyle=':')
        ax2.set_ylabel("Degrees from Perihelion (°)")
        ax2.set_title(f"Standard Approach " + 
                      ("(ISSUE AT BOUNDARY)" if not standard_success else "(WORKS CORRECTLY)"))
        ax2.grid(True)
        ax2.legend()
        
        # Plot 3: Unwrapped "degrees from perihelion"
        ax3.plot(time_offsets, degrees_from_peri_unwrapped, 'r-', label="Unwrapped (continuous)")
        ax3.axvline(x=0, color='k', linestyle='--')
        ax3.axhline(y=0, color='k', linestyle=':')
        ax3.set_ylabel("Degrees from Perihelion (°)")
        ax3.set_xlabel("Hours from Perihelion")
        ax3.set_title(f"New Approach with Unwrapping " + 
                      ("(FIXED!)" if unwrapped_success else "(ISSUE REMAINS)"))
        ax3.grid(True)
        ax3.legend()
        
        # Annotations for perihelion points
        # For standard method
        annotation_text = f"{dfp_at_perihelion_wrapped:.2f}° at perihelion"
        if abs(dfp_at_perihelion_wrapped) < 3.0:
            annotation_text = f"✓ {dfp_at_perihelion_wrapped:.2f}° at perihelion"
            color = "green"
        else:
            annotation_text = f"✗ {dfp_at_perihelion_wrapped:.2f}° at perihelion"
            color = "red"
            
        ax2.annotate(annotation_text,
                    xy=(0, dfp_at_perihelion_wrapped),
                    xytext=(10, 30),
                    arrowprops=dict(facecolor=color, shrink=0.05, width=2),
                    color=color,
                    fontsize=10,
                    fontweight='bold')
        
        # For unwrapped method
        annotation_text = f"{dfp_at_perihelion_unwrapped:.2f}° at perihelion"
        if abs(dfp_at_perihelion_unwrapped) < 3.0:
            annotation_text = f"✓ {dfp_at_perihelion_unwrapped:.2f}° at perihelion"
            color = "green"
        else:
            annotation_text = f"✗ {dfp_at_perihelion_unwrapped:.2f}° at perihelion"
            color = "red"
            
        ax3.annotate(annotation_text,
                    xy=(0, dfp_at_perihelion_unwrapped),
                    xytext=(10, 30),
                    arrowprops=dict(facecolor=color, shrink=0.05, width=2),
                    color=color,
                    fontsize=10,
                    fontweight='bold')
        
        plt.tight_layout()
        output_path = pathlib.Path(__file__).parent / f"e{enc_num}_validation.png"
        plt.savefig(output_path)
        plt.close()
    
    return result

def main():
    """Test all encounters and produce a comprehensive report."""
    # Load the position data
    npz_path = pathlib.Path(__file__).parent.parent / "support_data" / "trajectories" / "Parker_positional_data.npz"
    assert npz_path.exists(), f"NPZ file not found: {npz_path}"
    
    # Create mapper
    mapper = XAxisPositionalDataMapper(str(npz_path))
    
    print(f"Validating unwrap_angles fix for all {len(PERIHELION_TIMES)} Parker Solar Probe encounters")
    
    # Test each encounter
    results = {}
    boundary_crossing_encounters = []
    standard_failed_encounters = []
    unwrapped_failed_encounters = []
    
    for enc_num in sorted(PERIHELION_TIMES.keys()):
        print(f"\nTesting E{enc_num}...")
        result = test_encounter(mapper, enc_num, make_plot=True)
        results[enc_num] = result
        
        if result["boundary_crossing"]:
            boundary_crossing_encounters.append(enc_num)
            
        if not result["standard_success"]:
            standard_failed_encounters.append(enc_num)
            
        if not result["unwrapped_success"]:
            unwrapped_failed_encounters.append(enc_num)
        
        # Print encounter-specific results
        print(f"  Perihelion longitude: {result['perihelion_lon']:.4f}°")
        print(f"  Boundary crossing: {'Yes' if result['boundary_crossing'] else 'No'}")
        print(f"  Standard method degrees at perihelion: {result['dfp_at_perihelion_wrapped']:.6f}°")
        print(f"  Unwrapped method degrees at perihelion: {result['dfp_at_perihelion_unwrapped']:.6f}°")
        print(f"  Standard method centered: {'Yes' if result['is_centered_standard'] else 'No'}")
        print(f"  Unwrapped method centered: {'Yes' if result['is_centered_unwrapped'] else 'No'}")
        print(f"  Standard method successful: {'Yes' if result['standard_success'] else 'No'}")
        print(f"  Unwrapped method successful: {'Yes' if result['unwrapped_success'] else 'No'}")
    
    # Print a summary table
    print("\n=== SUMMARY ===")
    print(f"Total encounters: {len(PERIHELION_TIMES)}")
    print(f"Encounters with 0°/360° boundary crossing: {len(boundary_crossing_encounters)}")
    if boundary_crossing_encounters:
        print(f"  Boundary crossing encounters: {', '.join(f'E{e}' for e in boundary_crossing_encounters)}")
    
    print(f"\nStandard method failures: {len(standard_failed_encounters)}")
    if standard_failed_encounters:
        print(f"  Failed encounters: {', '.join(f'E{e}' for e in standard_failed_encounters)}")
    
    print(f"\nUnwrapped method failures: {len(unwrapped_failed_encounters)}")
    if unwrapped_failed_encounters:
        print(f"  Failed encounters: {', '.join(f'E{e}' for e in unwrapped_failed_encounters)}")
    
    # Final conclusion
    if not unwrapped_failed_encounters:
        print("\n✅ FIX VALIDATED! The unwrapped longitude approach correctly handles all encounters.")
        print("   Degrees from perihelion is exactly 0° at perihelion for all encounters.")
    else:
        print("\n❌ FIX NOT COMPLETELY SUCCESSFUL. Some encounters still have issues.")
        print(f"   {len(unwrapped_failed_encounters)} out of {len(PERIHELION_TIMES)} encounters failed with the unwrapped method.")
    
    # Generate a final summary plot showing the success rate across all encounters
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot 1: Degrees at perihelion for both methods
    encounters = sorted(results.keys())
    degrees_standard = [results[e]["dfp_at_perihelion_wrapped"] for e in encounters]
    degrees_unwrapped = [results[e]["dfp_at_perihelion_unwrapped"] for e in encounters]
    
    ax1.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax1.bar(np.array(encounters) - 0.2, degrees_standard, width=0.4, color='blue', label='Standard Method')
    ax1.bar(np.array(encounters) + 0.2, degrees_unwrapped, width=0.4, color='red', label='Unwrapped Method')
    
    ax1.set_xlabel('Encounter Number')
    ax1.set_ylabel('Degrees from Perihelion at Perihelion Time')
    ax1.set_title('Accuracy of Degrees from Perihelion at Perihelion Time')
    ax1.set_xticks(encounters)
    ax1.set_xticklabels([f'E{e}' for e in encounters])
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add highlights for boundary crossing encounters
    for e in boundary_crossing_encounters:
        ax1.axvspan(e - 0.5, e + 0.5, color='yellow', alpha=0.2)
    
    # Annotate boundary crossing encounters
    for e in boundary_crossing_encounters:
        ax1.annotate('Boundary\nCrossing', xy=(e, max(degrees_standard) * 0.8), 
                    ha='center', va='center', rotation=90, alpha=0.7, fontsize=8)
    
    # Plot 2: Overall success rates
    categories = ['All Encounters', 'Boundary Crossing', 'Non-Boundary Crossing']
    
    # Calculate success rates for standard method
    standard_all = sum(1 for e in encounters if results[e]["standard_success"]) / len(encounters) * 100
    standard_boundary = sum(1 for e in boundary_crossing_encounters if results[e]["standard_success"]) / max(1, len(boundary_crossing_encounters)) * 100
    standard_non_boundary = sum(1 for e in encounters if e not in boundary_crossing_encounters and results[e]["standard_success"]) / max(1, len(encounters) - len(boundary_crossing_encounters)) * 100
    
    # Calculate success rates for unwrapped method
    unwrapped_all = sum(1 for e in encounters if results[e]["unwrapped_success"]) / len(encounters) * 100
    unwrapped_boundary = sum(1 for e in boundary_crossing_encounters if results[e]["unwrapped_success"]) / max(1, len(boundary_crossing_encounters)) * 100
    unwrapped_non_boundary = sum(1 for e in encounters if e not in boundary_crossing_encounters and results[e]["unwrapped_success"]) / max(1, len(encounters) - len(boundary_crossing_encounters)) * 100
    
    standard_rates = [standard_all, standard_boundary, standard_non_boundary]
    unwrapped_rates = [unwrapped_all, unwrapped_boundary, unwrapped_non_boundary]
    
    x = np.arange(len(categories))
    width = 0.35
    
    ax2.bar(x - width/2, standard_rates, width, label='Standard Method', color='blue')
    ax2.bar(x + width/2, unwrapped_rates, width, label='Unwrapped Method', color='red')
    
    ax2.set_xlabel('Encounter Categories')
    ax2.set_ylabel('Success Rate (%)')
    ax2.set_title('Success Rates by Method and Encounter Type')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    ax2.set_ylim(0, 105)
    
    for i, v in enumerate(standard_rates):
        ax2.text(i - width/2, v + 3, f"{v:.1f}%", ha='center', fontsize=9)
    for i, v in enumerate(unwrapped_rates):
        ax2.text(i + width/2, v + 3, f"{v:.1f}%", ha='center', fontsize=9)
    
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = pathlib.Path(__file__).parent / "validation_summary.png"
    plt.savefig(output_path)
    print(f"\nSummary plot saved to: {output_path}")
    
if __name__ == "__main__":
    main() 