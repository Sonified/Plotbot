#!/usr/bin/env python3
"""
VDF Parameter System Demo - Show 3-panel plots comparing Jaye's original vs our new system
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import matplotlib.ticker as ticker
import matplotlib.cm as cm
import sys
import os

# Add the test directory to Python path so we can import the working functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our working smart bounds functions
from test_VDF_smart_bounds_debug import (
    extract_and_process_vdf_timeslice_EXACT,
    jaye_exact_theta_plane_processing, 
    jaye_exact_phi_plane_processing,
    calculate_smart_bounds_FIXED
)

# Import the VDF data class with our new parameter system
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from plotbot.data_classes.psp_span_vdf import psp_span_vdf_class

import pyspedas
import cdflib
import bisect
import pandas as pd
from datetime import datetime

def create_triple_plot_jaye_original(vdf_data, vx_theta, vz_theta, df_theta, vx_phi, vy_phi, df_phi, target_time):
    """Create 3-panel plot with Jaye's EXACT original bounds"""
    
    # Jaye's EXACT bounds from his notebook
    jaye_xlim_theta = (-800, 0)    # Cell 39 theta plane
    jaye_ylim_theta = (-400, 400)  # Cell 39 theta plane  
    jaye_xlim_phi = (-800, 0)      # Cell 41 phi plane
    jaye_ylim_phi = (-200, 600)    # Cell 41 phi plane
    
    # Use Jaye's exact gridspec layout (Cell 41)
    import matplotlib.gridspec as gridspec
    fig = plt.figure(figsize=(18, 6))
    gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 0.05], wspace=0.4)
    
    ax1 = fig.add_subplot(gs[0])  # 1D line plot
    ax2 = fig.add_subplot(gs[1])  # θ-plane
    ax3 = fig.add_subplot(gs[2])  # φ-plane
    cax = fig.add_subplot(gs[3])  # colorbar
    
    # 1D collapsed VDF (left panel) - Jaye's Cell 21 approach, NO TITLE
    vdf_allAngles = np.sum(vdf_data['vdf'], axis=(0,2))  # Sum over both phi and theta (Jaye's exact approach)
    vel_1d = vdf_data['vel'][0,:,0]  # Velocity array (Jaye's approach)
    ax1.plot(vel_1d, vdf_allAngles, 'b-', linewidth=2)
    ax1.set_yscale('log')
    ax1.set_xlim(0, 1000)  # Jaye's exact limits
    ax1.set_xlabel('Velocity (km/s)')
    ax1.set_ylabel(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$')  # Jaye's exact label
    # NO TITLE - just like Jaye's
    
    # 2D Theta plane (middle panel) - Jaye's exact title
    cs2 = ax2.contourf(vx_theta, vz_theta, df_theta, 
                      locator=ticker.LogLocator(), cmap=cm.cool)
    ax2.set_xlim(jaye_xlim_theta)
    ax2.set_ylim(jaye_ylim_theta)
    ax2.set_xlabel('$v_x$ km/s')
    ax2.set_ylabel('$v_z$ km/s')
    ax2.set_title('$\\theta$-plane')  # Jaye's exact title format
    
    # 2D Phi plane (right panel) - Jaye's exact title
    cs3 = ax3.contourf(vx_phi, vy_phi, df_phi,
                      locator=ticker.LogLocator(), cmap=cm.cool)
    ax3.set_xlim(jaye_xlim_phi)
    ax3.set_ylim(jaye_ylim_phi)
    ax3.set_xlabel('$v_x$ km/s')
    ax3.set_ylabel('$v_y$ km/s')
    ax3.set_title('$\\phi$-plane')  # Jaye's exact title format
    
    # Single colorbar in dedicated axis (Jaye's approach)
    cbar = fig.colorbar(cs2, cax=cax)
    cbar.set_label(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$')
    
    # No tight_layout needed with gridspec
    epoch_str = target_time.strftime("%Y-%m-%d %H:%M:%S")
    fig.suptitle(f'PSP SPAN-I VDF - Jaye\'s Original Settings\n{epoch_str}', y=1.02, fontsize=14)
    
    return fig

def create_triple_plot_parameter_system(vdf_data, vx_theta, vz_theta, df_theta, vx_phi, vy_phi, df_phi, target_time):
    """Create 3-panel plot with our new parameter system"""
    
    # Create VDF data class instance with our parameter system
    vdf_class = psp_span_vdf_class(None)  # Initialize empty
    
    # Update parameters to use smart bounds
    vdf_class.update_plot_params(
        enable_smart_padding=True,
        theta_x_smart_padding=100,  # From our tested values
        theta_y_smart_padding=100,
        phi_x_smart_padding=200,    # From our tested values  
        phi_y_smart_padding=200,
        enable_zero_clipping=True
    )
    
    # Calculate smart bounds using our parameter system
    theta_xlim, theta_ylim = vdf_class.calculate_smart_bounds(vx_theta, vz_theta, df_theta, 'theta')
    phi_xlim, phi_ylim = vdf_class.calculate_smart_bounds(vx_phi, vy_phi, df_phi, 'phi')
    
    # Use Jaye's exact gridspec layout (Cell 41)
    import matplotlib.gridspec as gridspec
    fig = plt.figure(figsize=(18, 6))
    gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 0.05], wspace=0.4)
    
    ax1 = fig.add_subplot(gs[0])  # 1D line plot
    ax2 = fig.add_subplot(gs[1])  # θ-plane
    ax3 = fig.add_subplot(gs[2])  # φ-plane
    cax = fig.add_subplot(gs[3])  # colorbar
    
    # 1D collapsed VDF (left panel) - Jaye's Cell 21 approach, NO TITLE
    vdf_allAngles = np.sum(vdf_data['vdf'], axis=(0,2))  # Sum over both phi and theta (Jaye's exact approach)
    vel_1d = vdf_data['vel'][0,:,0]  # Velocity array (Jaye's approach)
    ax1.plot(vel_1d, vdf_allAngles, 'r-', linewidth=2)
    ax1.set_yscale('log')
    ax1.set_xlim(0, 1000)  # Jaye's exact limits
    ax1.set_xlabel('Velocity (km/s)')
    ax1.set_ylabel(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$')  # Jaye's exact label
    # NO TITLE - just like Jaye's
    
    # 2D Theta plane with smart bounds (middle panel) - Clean title
    cs2 = ax2.contourf(vx_theta, vz_theta, df_theta, 
                      locator=ticker.LogLocator(), cmap=cm.cool)
    ax2.set_xlim(theta_xlim)
    ax2.set_ylim(theta_ylim)
    ax2.set_xlabel('$v_x$ km/s')
    ax2.set_ylabel('$v_z$ km/s')
    ax2.set_title('$\\theta$-plane')  # Clean title like Jaye's
    
    # 2D Phi plane with smart bounds (right panel) - Clean title
    cs3 = ax3.contourf(vx_phi, vy_phi, df_phi,
                      locator=ticker.LogLocator(), cmap=cm.cool)
    ax3.set_xlim(phi_xlim)
    ax3.set_ylim(phi_ylim)
    ax3.set_xlabel('$v_x$ km/s')
    ax3.set_ylabel('$v_y$ km/s')
    ax3.set_title('$\\phi$-plane')  # Clean title like Jaye's
    
    # Single colorbar in dedicated axis (Jaye's approach)
    cbar = fig.colorbar(cs2, cax=cax)
    cbar.set_label(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$')
    
    # No tight_layout needed with gridspec
    epoch_str = target_time.strftime("%Y-%m-%d %H:%M:%S")
    fig.suptitle(f'PSP SPAN-I VDF - New Parameter System\n{epoch_str}', y=1.02, fontsize=14)
    
    # Print the bounds comparison
    print("\n" + "="*60)
    print("📏 BOUNDS COMPARISON:")
    print(f"   Jaye's theta bounds:     X=(-800, 0),    Y=(-400, 400)")
    print(f"   Smart theta bounds:      X={theta_xlim}, Y={theta_ylim}")
    print(f"   Jaye's phi bounds:       X=(-800, 0),    Y=(-200, 600)")
    print(f"   Smart phi bounds:        X={phi_xlim},   Y={phi_ylim}")
    print("="*60)
    
    return fig

def test_vdf_parameter_system_comparison():
    """
    Main test function - Create two 3-panel plots side by side:
    1. Jaye's original settings
    2. Our new parameter system
    """
    
    print("🚀 VDF Parameter System Demo")
    print("📡 Downloading PSP SPAN-I data...")
    
    # Download data using our working approach
    trange = ['2020-01-29/00:00', '2020-01-30/00:00']
    VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                              notplot=True, time_clip=True, downloadonly=True, get_support_data=True)
    
    if not VDfile:
        print("❌ No VDF files downloaded")
        return
        
    print(f"📁 Downloaded: {VDfile[0]}")
    
    # Process data using our working approach
    dat = cdflib.CDF(VDfile[0])
    
    # Get time array
    epoch_dt64 = cdflib.cdfepoch.to_datetime(dat.varget('Epoch'))
    epoch = pd.to_datetime(epoch_dt64).to_pydatetime().tolist()
    
    # Find Jaye's exact time slice
    target_time = datetime(2020, 1, 29, 18, 10, 2)
    tSliceIndex = bisect.bisect_left(epoch, target_time)
    
    print(f"🎯 Target time: {target_time}")
    print(f"📍 Found: {epoch[tSliceIndex]} (index {tSliceIndex})")
    
    # Process VDF data using working functions
    vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, tSliceIndex)
    
    # Get theta and phi plane data using working functions
    vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
    vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
    
    print(f"✅ VDF processing complete")
    print(f"   Time: {epoch[tSliceIndex]}")
    print(f"   Theta VDF range: {np.nanmin(df_theta):.2e} to {np.nanmax(df_theta):.2e}")
    print(f"   Phi VDF range: {np.nanmin(df_phi):.2e} to {np.nanmax(df_phi):.2e}")
    
    # Create Figure 1: Jaye's Original Settings (3-panel)
    print("\n📊 Creating Figure 1: Jaye's Original Settings...")
    fig1 = create_triple_plot_jaye_original(vdf_data, vx_theta, vz_theta, df_theta, vx_phi, vy_phi, df_phi, target_time)
    plt.savefig('tests/Images/VDF_triple_plot_jaye_original.png', dpi=150, bbox_inches='tight')
    print("✅ Saved: tests/Images/VDF_triple_plot_jaye_original.png")
    
    # Create Figure 2: Our New Parameter System (3-panel)
    print("\n📊 Creating Figure 2: New Parameter System...")
    fig2 = create_triple_plot_parameter_system(vdf_data, vx_theta, vz_theta, df_theta, vx_phi, vy_phi, df_phi, target_time)
    plt.savefig('tests/Images/VDF_triple_plot_parameter_system.png', dpi=150, bbox_inches='tight')
    print("✅ Saved: tests/Images/VDF_triple_plot_parameter_system.png")
    
    print("\n🎉 Demo complete! Two separate windows should be open:")
    print("   1. Jaye's Original Settings (3-panel)")
    print("   2. New Parameter System (3-panel)")
    print("\nCompare the bounds and zoom levels between the two approaches.")
    
    plt.show()

if __name__ == "__main__":
    test_vdf_parameter_system_comparison()