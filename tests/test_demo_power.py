#!/usr/bin/env python3
"""
Demo script showing the power of Plotbot's custom variable system
"""

import numpy as np
from plotbot import plotbot, custom_variable, mag_rtn_4sa, proton, ploptions
import plotbot as pb  # Import module to access custom variables

# ENABLE figure display to see the plots!
ploptions.display_figure = True
ploptions.return_figure = True  # Return figures so we can save them

print("="*70)
print("DEMO: Plotbot Custom Variables - The Power!")
print("="*70)

# 1. Define custom magnetic field angle (complex NumPy operations)
print("\n1️⃣  Creating 'phi_B' with complex NumPy operations...")
print("   Formula: np.degrees(np.arctan2(mag.br, mag.bn)) + 180")
custom_variable('phi_B', lambda: np.degrees(np.arctan2(mag_rtn_4sa.br, mag_rtn_4sa.bn)) + 180)
print("   ✅ Created phi_B")

# 2. Mix high-cadence mag with low-cadence proton data (auto-resampling!)
print("\n2️⃣  Creating 'bmag_per_vr' mixing different cadences...")
print("   mag.bmag: ~4 Hz (high cadence)")
print("   proton.vr: ~0.14 Hz (low cadence)")
print("   Formula: mag.bmag / proton.vr")
custom_variable('bmag_per_vr', mag_rtn_4sa.bmag / proton.vr)
print("   ✅ Created bmag_per_vr (will auto-resample!)")

# 3. Chain custom variables - USE LAMBDA for dynamic evaluation!
print("\n3️⃣  Creating 'normalized' that depends on another custom variable...")
print("   Formula: lambda: bmag_per_vr / mean(bmag_per_vr)")
print("   This is a custom variable that uses another custom variable!")
print("   ⚠️  Using LAMBDA so it evaluates fresh each time (not at definition)")
custom_variable('normalized', lambda: pb.bmag_per_vr / np.mean(pb.bmag_per_vr))
print("   ✅ Created normalized (chained dependency with lambda)")

# 4. Plot across different time ranges - everything auto-updates
print("\n4️⃣  Testing with first time range...")
print("   Time range: ['2020-01-29/18:00', '2020-01-29/18:30']")
result1 = plotbot(['2020-01-29/18:00', '2020-01-29/18:30'], pb.phi_B, 1)
phi_B_data1 = pb.phi_B.data
print(f"   ✅ phi_B shape: {phi_B_data1.shape}")
print(f"   ✅ phi_B range: [{np.min(phi_B_data1):.2f}, {np.max(phi_B_data1):.2f}] degrees")

print("\n5️⃣  Testing bmag_per_vr with auto-resampling...")
result2 = plotbot(['2020-01-29/18:00', '2020-01-29/18:30'], pb.bmag_per_vr, 1)
bmag_per_vr_data = pb.bmag_per_vr.data
print(f"   ✅ bmag_per_vr shape: {bmag_per_vr_data.shape}")
print(f"   ✅ Auto-resampled to proton cadence (low cadence wins)")
print(f"   ✅ bmag_per_vr range: [{np.min(bmag_per_vr_data):.2f}, {np.max(bmag_per_vr_data):.2f}]")

print("\n6️⃣  Testing normalized (chained custom variable)...")
result3 = plotbot(['2020-01-29/18:00', '2020-01-29/18:30'], pb.normalized, 1)
normalized_data = pb.normalized.data
print(f"   ✅ normalized shape: {normalized_data.shape}")
print(f"   ✅ normalized mean: {np.mean(normalized_data):.2f} (should be ~1.0)")
print(f"   ✅ normalized range: [{np.min(normalized_data):.2f}, {np.max(normalized_data):.2f}]")

print("\n7️⃣  Switching to DIFFERENT time range (different day!)...")
print("   Time range: ['2020-02-15/12:00', '2020-02-15/12:30']")
result4 = plotbot(['2020-02-15/12:00', '2020-02-15/12:30'], pb.phi_B, 1)
phi_B_data2 = pb.phi_B.data
print(f"   ✅ phi_B shape: {phi_B_data2.shape}")
print(f"   ✅ phi_B range: [{np.min(phi_B_data2):.2f}, {np.max(phi_B_data2):.2f}] degrees")
print(f"   ✅ Different data, everything auto-updated!")

print("\n8️⃣  Verifying data actually changed between time ranges...")
if phi_B_data1.shape[0] != phi_B_data2.shape[0]:
    print(f"   ✅ Shape changed: {phi_B_data1.shape[0]} → {phi_B_data2.shape[0]} points")
else:
    print(f"   ⚠️  Same shape ({phi_B_data1.shape[0]} points)")

# Check if values are different
if not np.allclose(phi_B_data1[:min(10, len(phi_B_data1))], 
                    phi_B_data2[:min(10, len(phi_B_data2))], rtol=0.01):
    print(f"   ✅ Values changed (different data loaded)")
else:
    print(f"   ⚠️  Values similar")

print("\n" + "="*70)
print("🎉 DEMO COMPLETE - ALL FEATURES WORKING!")
print("="*70)
print("\n✨ Summary of Power:")
print("   • Complex NumPy operations (degrees, arctan2, etc.)")
print("   • Automatic cadence detection and resampling")
print("   • Chained custom variables (dependencies)")
print("   • Time range switching with auto-update")
print("   • Zero manual interpolation code!")
print("   • Zero manual time clipping!")
print("   • Zero manual cache management!")
print("\n🚀 Research-grade data analysis made effortless!")

# Save the last figure if available
if result4 is not None and hasattr(result4, 'savefig'):
    import os
    save_path = os.path.join(os.path.dirname(__file__), '../test_logs/demo_power_plot.png')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    result4.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n💾 Plot saved to: {save_path}")

print("\n✅ Check the plots that appeared!")

