#!/usr/bin/env python3
"""
Deep debugging script to compare VDF data between vdyes() and plotbot_interactive_vdf()
"""

import numpy as np
import matplotlib.pyplot as plt
from plotbot import vdyes, plotbot_interactive_vdf
import sys
import os

# Add tests directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests'))
from test_VDF_smart_bounds_debug import (
    extract_and_process_vdf_timeslice_EXACT,
    jaye_exact_theta_plane_processing,
    jaye_exact_phi_plane_processing
)

import pyspedas
import cdflib
import pandas as pd
from dateutil.parser import parse

def debug_vdyes_data_flow():
    """Debug the exact data flow in vdyes() for comparison"""
    
    trange = ['2020-01-29/18:00:00.000', '2020-01-29/18:15:00.000']
    print("🔍 DEBUGGING vdyes() data flow...")
    
    # Replicate vdyes() data loading exactly
    VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                              notplot=True, time_clip=True, downloadonly=True, get_support_data=True, 
                              no_update=True)
    
    if not VDfile:
        VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                                  notplot=True, time_clip=True, downloadonly=True, get_support_data=True, 
                                  no_update=False)
    
    print(f"📁 VDF file: {VDfile[0]}")
    
    # Process data using the same approach as vdyes()
    dat = cdflib.CDF(VDfile[0])
    
    # Get time array
    epoch_dt64 = cdflib.cdfepoch.to_datetime(dat.varget('Epoch'))
    epoch = pd.to_datetime(epoch_dt64).to_pydatetime().tolist()
    
    # Filter time points to requested range
    start_dt = parse(trange[0].replace('/', ' '))
    end_dt = parse(trange[1].replace('/', ' '))
    
    time_mask = [(t >= start_dt and t <= end_dt) for t in epoch]
    available_times = [epoch[i] for i, mask in enumerate(time_mask) if mask]
    available_indices = [i for i, mask in enumerate(time_mask) if mask]
    
    print(f"✅ Found {len(available_times)} time points")
    print(f"📅 Time range: {available_times[0]} to {available_times[-1]}")
    
    # Process first time slice with EXACT same functions
    time_idx = available_indices[0]
    print(f"\n🔬 Processing time slice {time_idx}: {available_times[0]}")
    
    # Step 1: Extract VDF data
    print("Step 1: extract_and_process_vdf_timeslice_EXACT...")
    vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, time_idx)
    
    print(f"   VDF data keys: {list(vdf_data.keys())}")
    print(f"   VDF shape: {vdf_data['vdf'].shape}")
    print(f"   VDF range: {np.nanmin(vdf_data['vdf']):.2e} to {np.nanmax(vdf_data['vdf']):.2e}")
    print(f"   Velocity shape: {vdf_data['vel'].shape}")
    print(f"   Velocity range: {np.nanmin(vdf_data['vel']):.1f} to {np.nanmax(vdf_data['vel']):.1f}")
    
    # Step 2: Theta plane processing
    print("\nStep 2: jaye_exact_theta_plane_processing...")
    vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
    
    print(f"   Theta VX shape: {vx_theta.shape}")
    print(f"   Theta VZ shape: {vz_theta.shape}")
    print(f"   Theta DF shape: {df_theta.shape}")
    print(f"   Theta VX range: {np.nanmin(vx_theta):.1f} to {np.nanmax(vx_theta):.1f}")
    print(f"   Theta VZ range: {np.nanmin(vz_theta):.1f} to {np.nanmax(vz_theta):.1f}")
    print(f"   Theta DF range: {np.nanmin(df_theta):.2e} to {np.nanmax(df_theta):.2e}")
    print(f"   Theta DF finite values: {np.sum(np.isfinite(df_theta))}/{df_theta.size}")
    
    # Step 3: Phi plane processing  
    print("\nStep 3: jaye_exact_phi_plane_processing...")
    vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
    
    print(f"   Phi VX shape: {vx_phi.shape}")
    print(f"   Phi VY shape: {vy_phi.shape}")
    print(f"   Phi DF shape: {df_phi.shape}")
    print(f"   Phi VX range: {np.nanmin(vx_phi):.1f} to {np.nanmax(vx_phi):.1f}")
    print(f"   Phi VY range: {np.nanmin(vy_phi):.1f} to {np.nanmax(vy_phi):.1f}")
    print(f"   Phi DF range: {np.nanmin(df_phi):.2e} to {np.nanmax(df_phi):.2e}")
    print(f"   Phi DF finite values: {np.sum(np.isfinite(df_phi))}/{df_phi.size}")
    
    # Step 4: 1D VDF
    print("\nStep 4: 1D VDF calculation...")
    vdf_allAngles = np.sum(vdf_data['vdf'], axis=(0, 2))  # Sum over both phi and theta
    vel_1d = vdf_data['vel'][0, :, 0]  # Velocity array
    
    print(f"   1D VDF shape: {vdf_allAngles.shape}")
    print(f"   1D VDF range: {np.nanmin(vdf_allAngles):.2e} to {np.nanmax(vdf_allAngles):.2e}")
    print(f"   1D Vel shape: {vel_1d.shape}")
    print(f"   1D Vel range: {np.nanmin(vel_1d):.1f} to {np.nanmax(vel_1d):.1f}")
    
    # Create matplotlib plots to compare
    print("\n📊 Creating matplotlib comparison plots...")
    
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(15, 10))
    
    # Row 1: Data inspection
    ax1.plot(vel_1d, vdf_allAngles, 'b-', linewidth=2)
    ax1.set_yscale('log')
    ax1.set_xlim(0, 1000)
    ax1.set_title('1D VDF')
    ax1.set_xlabel('Velocity (km/s)')
    ax1.set_ylabel('f')
    
    # Theta plane raw data
    im2 = ax2.pcolormesh(vx_theta, vz_theta, df_theta, shading='auto')
    ax2.set_title(f'Theta Raw Data\n{np.sum(np.isfinite(df_theta))} finite values')
    ax2.set_xlabel('Vx (km/s)')
    ax2.set_ylabel('Vz (km/s)')
    plt.colorbar(im2, ax=ax2)
    
    # Phi plane raw data
    im3 = ax3.pcolormesh(vx_phi, vy_phi, df_phi, shading='auto')
    ax3.set_title(f'Phi Raw Data\n{np.sum(np.isfinite(df_phi))} finite values')
    ax3.set_xlabel('Vx (km/s)')
    ax3.set_ylabel('Vy (km/s)')
    plt.colorbar(im3, ax=ax3)
    
    # Row 2: Actual matplotlib contourf plots
    ax4.plot(vel_1d, vdf_allAngles, 'b-', linewidth=2)
    ax4.set_yscale('log')
    ax4.set_xlim(0, 1000)
    ax4.set_title('1D VDF (matplotlib)')
    
    # Theta plane contourf (like vdyes)
    try:
        from matplotlib import ticker
        cs5 = ax5.contourf(vx_theta, vz_theta, df_theta, locator=ticker.LogLocator())
        ax5.set_title('Theta contourf (like vdyes)')
        ax5.set_xlabel('Vx (km/s)')
        ax5.set_ylabel('Vz (km/s)')
        plt.colorbar(cs5, ax=ax5)
    except Exception as e:
        ax5.text(0.5, 0.5, f'Theta contourf failed:\n{str(e)}', ha='center', va='center', transform=ax5.transAxes)
        ax5.set_title('Theta contourf FAILED')
    
    # Phi plane contourf (like vdyes)
    try:
        cs6 = ax6.contourf(vx_phi, vy_phi, df_phi, locator=ticker.LogLocator())
        ax6.set_title('Phi contourf (like vdyes)')
        ax6.set_xlabel('Vx (km/s)')
        ax6.set_ylabel('Vy (km/s)')
        plt.colorbar(cs6, ax=ax6)
    except Exception as e:
        ax6.text(0.5, 0.5, f'Phi contourf failed:\n{str(e)}', ha='center', va='center', transform=ax6.transAxes)
        ax6.set_title('Phi contourf FAILED')
    
    plt.tight_layout()
    plt.savefig('vdf_debug_comparison.png', dpi=300, bbox_inches='tight')
    print("💾 Saved debug plot to vdf_debug_comparison.png")
    
    return {
        'vdf_data': vdf_data,
        'theta': (vx_theta, vz_theta, df_theta),
        'phi': (vx_phi, vy_phi, df_phi),
        '1d': (vel_1d, vdf_allAngles),
        'dat': dat,
        'time_idx': time_idx
    }

if __name__ == "__main__":
    debug_data = debug_vdyes_data_flow()
    print("\n✅ Debug complete! Check vdf_debug_comparison.png")
    print("\n🔍 Key findings:")
    
    vdf_data, theta, phi, vdf_1d = debug_data['vdf_data'], debug_data['theta'], debug_data['phi'], debug_data['1d']
    vx_theta, vz_theta, df_theta = theta
    vx_phi, vy_phi, df_phi = phi
    vel_1d, vdf_allAngles = vdf_1d
    
    print(f"   1D VDF: {len(vel_1d)} points, range {np.nanmin(vdf_allAngles):.2e} to {np.nanmax(vdf_allAngles):.2e}")
    print(f"   Theta: {df_theta.shape}, finite: {np.sum(np.isfinite(df_theta))}, range: {np.nanmin(df_theta):.2e} to {np.nanmax(df_theta):.2e}")
    print(f"   Phi: {df_phi.shape}, finite: {np.sum(np.isfinite(df_phi))}, range: {np.nanmin(df_phi):.2e} to {np.nanmax(df_phi):.2e}")
