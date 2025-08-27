#!/usr/bin/env python3
"""
Direct comparison of VDF data processing to identify why Plotly is missing so much data.
Compare the exact same VDF data slice using matplotlib vs Plotly approaches.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sys
import os

# Add tests directory to path for proven VDF processing functions
sys.path.append('tests')

try:
    from test_VDF_smart_bounds_debug import (
        extract_and_process_vdf_timeslice_EXACT,
        jaye_exact_theta_plane_processing, 
        jaye_exact_phi_plane_processing
    )
except ImportError:
    print("❌ Cannot import VDF processing functions")
    sys.exit(1)

# Import plotbot for VDF data loading
sys.path.append('.')
import plotbot
import pyspedas
import cdflib

def load_vdf_data():
    """Load VDF data using the exact same approach as vdyes()"""
    trange = ['2020/01/29 18:00:00.000', '2020/01/29 18:30:00.000']
    
    # Download using proven approach
    VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                              notplot=True, time_clip=True, downloadonly=True, 
                              get_support_data=True, no_update=True)
    
    if not VDfile:
        print("❌ No VDF files found")
        return None
        
    print(f"📁 Using VDF file: {VDfile[0]}")
    
    # Process data
    dat = cdflib.CDF(VDfile[0])
    
    # Get first time slice
    time_index = 0
    vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, time_index)
    
    # Get theta and phi plane data
    vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
    vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
    
    return {
        'vx_theta': vx_theta, 'vz_theta': vz_theta, 'df_theta': df_theta,
        'vx_phi': vx_phi, 'vy_phi': vy_phi, 'df_phi': df_phi,
        'vdf_data': vdf_data
    }

def analyze_vdf_data_coverage(data):
    """Analyze exactly how much VDF data we have and where it is"""
    
    print("\n" + "="*80)
    print("VDF DATA ANALYSIS - THETA PLANE")
    print("="*80)
    
    vx_theta, vz_theta, df_theta = data['vx_theta'], data['vz_theta'], data['df_theta']
    
    print(f"📊 Theta plane shapes:")
    print(f"   vx_theta: {vx_theta.shape}")
    print(f"   vz_theta: {vz_theta.shape}")  
    print(f"   df_theta: {df_theta.shape}")
    
    print(f"\n🔍 VDF data coverage:")
    finite_mask = np.isfinite(df_theta) & (df_theta > 0)
    finite_count = np.sum(finite_mask)
    total_count = df_theta.size
    
    print(f"   Total grid points: {total_count}")
    print(f"   Finite & positive VDF values: {finite_count} ({100*finite_count/total_count:.1f}%)")
    print(f"   VDF value range: {np.nanmin(df_theta):.2e} to {np.nanmax(df_theta):.2e}")
    
    print(f"\n📍 Coordinate ranges:")
    print(f"   VX range: {np.nanmin(vx_theta):.1f} to {np.nanmax(vx_theta):.1f} km/s")
    print(f"   VZ range: {np.nanmin(vz_theta):.1f} to {np.nanmax(vz_theta):.1f} km/s")
    
    # Check coordinate uniformity
    x_uniform = np.allclose(vx_theta[0, :], vx_theta[-1, :], rtol=1e-3)
    y_uniform = np.allclose(vz_theta[:, 0], vz_theta[:, -1], rtol=1e-3)
    print(f"\n🔧 Grid uniformity:")
    print(f"   X coordinates uniform: {x_uniform}")
    print(f"   Z coordinates uniform: {y_uniform}")
    
    if not x_uniform:
        x_var = np.max(vx_theta[0, :]) - np.min(vx_theta[-1, :])
        print(f"   X coordinate variation: {abs(x_var):.1f} km/s")
    if not y_uniform:
        y_var = np.max(vz_theta[:, 0]) - np.min(vz_theta[:, -1])
        print(f"   Z coordinate variation: {abs(y_var):.1f} km/s")
    
    print("\n" + "="*80)
    print("VDF DATA ANALYSIS - PHI PLANE")
    print("="*80)
    
    vx_phi, vy_phi, df_phi = data['vx_phi'], data['vy_phi'], data['df_phi']
    
    print(f"📊 Phi plane shapes:")
    print(f"   vx_phi: {vx_phi.shape}")
    print(f"   vy_phi: {vy_phi.shape}")  
    print(f"   df_phi: {df_phi.shape}")
    
    finite_mask_phi = np.isfinite(df_phi) & (df_phi > 0)
    finite_count_phi = np.sum(finite_mask_phi)
    total_count_phi = df_phi.size
    
    print(f"\n🔍 VDF data coverage:")
    print(f"   Total grid points: {total_count_phi}")
    print(f"   Finite & positive VDF values: {finite_count_phi} ({100*finite_count_phi/total_count_phi:.1f}%)")
    print(f"   VDF value range: {np.nanmin(df_phi):.2e} to {np.nanmax(df_phi):.2e}")
    
    print(f"\n📍 Coordinate ranges:")
    print(f"   VX range: {np.nanmin(vx_phi):.1f} to {np.nanmax(vx_phi):.1f} km/s")
    print(f"   VY range: {np.nanmin(vy_phi):.1f} to {np.nanmax(vy_phi):.1f} km/s")

def create_matplotlib_reference(data):
    """Create matplotlib reference plot exactly like vdyes()"""
    vx_theta, vz_theta, df_theta = data['vx_theta'], data['vz_theta'], data['df_theta']
    vx_phi, vy_phi, df_phi = data['vx_phi'], data['vy_phi'], data['df_phi']
    
    # Create matplotlib plot with EXACT vdyes() approach
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor='white')
    
    # Theta plane with EXACT matplotlib approach
    cs1 = ax1.contourf(vx_theta, vz_theta, df_theta, 
                      locator=ticker.LogLocator(), cmap='cool')
    ax1.set_xlabel('Vx km/s')
    ax1.set_ylabel('Vz km/s') 
    ax1.set_title('θ-plane (matplotlib contourf)')
    
    # Phi plane with EXACT matplotlib approach  
    cs2 = ax2.contourf(vx_phi, vy_phi, df_phi,
                      locator=ticker.LogLocator(), cmap='cool')
    ax2.set_xlabel('Vx km/s')
    ax2.set_ylabel('Vy km/s')
    ax2.set_title('φ-plane (matplotlib contourf)')
    
    # Add colorbar
    plt.colorbar(cs1, ax=ax1, label='f (cm² s sr eV)⁻¹')
    plt.colorbar(cs2, ax=ax2, label='f (cm² s sr eV)⁻¹')
    
    plt.tight_layout()
    plt.savefig('matplotlib_vdf_reference_full.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ Matplotlib reference plot saved as 'matplotlib_vdf_reference_full.png'")

def test_plotly_interpolation(data):
    """Test the exact Plotly interpolation approach that's losing data"""
    from scipy.interpolate import griddata
    
    print("\n" + "="*80)
    print("PLOTLY INTERPOLATION TEST - THETA PLANE")
    print("="*80)
    
    vx_theta, vz_theta, df_theta = data['vx_theta'], data['vz_theta'], data['df_theta']
    
    # Clean VDF data (same as current Plotly approach)
    vdf_plot = df_theta.copy()
    vdf_plot[vdf_plot <= 0] = np.nan
    vdf_plot[~np.isfinite(vdf_plot)] = np.nan
    
    print(f"🧹 After cleaning:")
    finite_count = np.sum(np.isfinite(vdf_plot))
    print(f"   Finite values: {finite_count}/{vdf_plot.size} ({100*finite_count/vdf_plot.size:.1f}%)")
    
    # Get coordinate ranges
    x_min, x_max = np.nanmin(vx_theta), np.nanmax(vx_theta)
    y_min, y_max = np.nanmin(vz_theta), np.nanmax(vz_theta)
    
    print(f"📍 Coordinate ranges for interpolation:")
    print(f"   X: {x_min:.1f} to {x_max:.1f} km/s")
    print(f"   Y: {y_min:.1f} to {y_max:.1f} km/s")
    
    # Create regular grid (current Plotly approach)
    n_points = 50
    x_coords = np.linspace(x_min, x_max, n_points)
    y_coords = np.linspace(y_min, y_max, n_points)
    
    # Flatten for interpolation
    points = np.column_stack((vx_theta.ravel(), vz_theta.ravel()))
    values = vdf_plot.ravel()
    
    # Remove NaN values
    valid_mask = np.isfinite(values)
    points_valid = points[valid_mask]
    values_valid = values[valid_mask]
    
    print(f"🔄 Interpolation input:")
    print(f"   Valid points: {len(values_valid)}/{len(values)} ({100*len(values_valid)/len(values):.1f}%)")
    print(f"   Value range: {np.min(values_valid):.2e} to {np.max(values_valid):.2e}")
    
    # Interpolate
    X_reg, Y_reg = np.meshgrid(x_coords, y_coords)
    Z_reg = griddata(points_valid, values_valid, (X_reg, Y_reg), method='linear', fill_value=np.nan)
    
    print(f"📊 Interpolation output:")
    finite_interp = np.sum(np.isfinite(Z_reg))
    print(f"   Finite values: {finite_interp}/{Z_reg.size} ({100*finite_interp/Z_reg.size:.1f}%)")
    print(f"   Value range: {np.nanmin(Z_reg):.2e} to {np.nanmax(Z_reg):.2e}")
    
    # Calculate data loss
    original_coverage = 100 * finite_count / vdf_plot.size
    interpolated_coverage = 100 * finite_interp / Z_reg.size
    
    print(f"\n⚠️ DATA LOSS ANALYSIS:")
    print(f"   Original grid coverage: {original_coverage:.1f}%")
    print(f"   Interpolated grid coverage: {interpolated_coverage:.1f}%")
    print(f"   Effective data density change: {interpolated_coverage/original_coverage:.2f}x")

if __name__ == "__main__":
    print("🔍 Loading VDF data for comprehensive analysis...")
    
    data = load_vdf_data()
    if data is None:
        sys.exit(1)
    
    # Analyze the raw VDF data coverage 
    analyze_vdf_data_coverage(data)
    
    # Create matplotlib reference
    create_matplotlib_reference(data)
    
    # Test Plotly interpolation approach
    test_plotly_interpolation(data)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("Check 'matplotlib_vdf_reference_full.png' to see what the data SHOULD look like")
    print("Compare this to your current Plotly output to see the data loss")
