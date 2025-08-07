#!/usr/bin/env python3
"""
FIXED bounds comparison using EXACT working approach from test_jaye_exact_replication.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import matplotlib.ticker as ticker
import matplotlib.cm as cm
import pyspedas
import cdflib
import bisect
import pandas as pd
from datetime import datetime

def extract_and_process_vdf_timeslice_EXACT(dat, tSliceIndex):
    """EXACT copy from test_jaye_exact_replication.py"""
    
    # Extract slice data exactly like Jaye (Cell 13)
    epochSlice = dat['Epoch'][tSliceIndex]
    thetaSlice = dat['THETA'][tSliceIndex, :]
    phiSlice = dat['PHI'][tSliceIndex, :]
    energySlice = dat['ENERGY'][tSliceIndex, :]
    efluxSlice = dat['EFLUX'][tSliceIndex, :]
    
    # Reshape to (8, 32, 8) exactly like Jaye (Cell 15)
    thetaReshaped = thetaSlice.reshape((8, 32, 8))
    phiReshaped = phiSlice.reshape((8, 32, 8))
    energyReshaped = energySlice.reshape((8, 32, 8))
    efluxReshaped = efluxSlice.reshape((8, 32, 8))
    
    # Jaye's exact VDF calculation (Cell 17)
    mass_p = 0.010438870  # proton mass in eV/c^2 where c = 299792 km/s
    charge_p = 1          # proton charge in eV
    
    # Define VDF
    numberFlux = efluxReshaped / energyReshaped
    vdf = numberFlux * (mass_p**2) / ((2E-5) * energyReshaped)
    
    # Convert to velocity units in each energy channel
    vel = np.sqrt(2 * charge_p * energyReshaped / mass_p)
    
    # Jaye's exact coordinate conversion (Cell 19)
    vx = vel * np.cos(np.radians(phiReshaped)) * np.cos(np.radians(thetaReshaped))
    vy = vel * np.sin(np.radians(phiReshaped)) * np.cos(np.radians(thetaReshaped))
    vz = vel * np.sin(np.radians(thetaReshaped))
    
    return {
        'epoch': epochSlice,
        'vdf': vdf,
        'vel': vel,
        'vx': vx,
        'vy': vy,
        'vz': vz,
        'thetaReshaped': thetaReshaped,
        'phiReshaped': phiReshaped,
        'energyReshaped': energyReshaped
    }

def jaye_exact_theta_plane_processing(data):
    """EXACT copy of Jaye's theta plane processing from test_jaye_exact_replication.py"""
    
    # Jaye's exact theta plane processing (Cell 26)
    theta_cut = 0
    
    phi_plane = data['phiReshaped'][theta_cut, :, :]
    theta_plane = data['thetaReshaped'][theta_cut, :, :]
    energy_plane = data['energyReshaped'][theta_cut, :, :]
    vel_plane = np.sqrt(2 * 1 * energy_plane / 0.010438870)  # Jaye's constants
    
    df_theta = np.nansum(data['vdf'], axis=0)
    
    vx_plane_theta = vel_plane * np.cos(np.radians(phi_plane)) * np.cos(np.radians(theta_plane))
    vy_plane_theta = vel_plane * np.sin(np.radians(phi_plane)) * np.cos(np.radians(theta_plane))
    vz_plane_theta = vel_plane * np.sin(np.radians(theta_plane))
    
    return vx_plane_theta, vz_plane_theta, df_theta

def jaye_exact_phi_plane_processing(data):
    """Process phi plane following Jaye's approach but summing over theta (axis=2)"""
    
    # Phi plane processing - sum over theta direction (axis=2)
    # Use middle theta slice to get coordinate reference (like theta plane uses middle phi)
    theta_middle = 4  # Middle theta bin (0-7 range)
    
    phi_plane = data['phiReshaped'][:, :, theta_middle]
    theta_plane = data['thetaReshaped'][:, :, theta_middle] 
    energy_plane = data['energyReshaped'][:, :, theta_middle]
    vel_plane = np.sqrt(2 * 1 * energy_plane / 0.010438870)  # Jaye's constants
    
    df_phi = np.nansum(data['vdf'], axis=2)  # Sum over theta direction to get phi plane
    
    vx_plane_phi = vel_plane * np.cos(np.radians(phi_plane)) * np.cos(np.radians(theta_plane))
    vy_plane_phi = vel_plane * np.sin(np.radians(phi_plane)) * np.cos(np.radians(theta_plane))
    vz_plane_phi = vel_plane * np.sin(np.radians(theta_plane))
    
    return vx_plane_phi, vy_plane_phi, df_phi

def calculate_smart_bounds_FIXED(vx, vy, vdf_data, padding_x=100, padding_y=100):
    """
    Calculate smart plot bounds based on data edges with padding.
    Uses separate x and y padding values for flexible bounds control.
    """
    print(f"🔍 Smart bounds: Finding data edges...")
    
    # Find where we have any valid data (not NaN, not zero)
    valid_mask = np.isfinite(vdf_data) & (vdf_data > 0)
    
    if not np.any(valid_mask):
        print("⚠️  No valid data found, using fallback bounds")
        return (0, 500), (-600, 600)
    
    # Find the actual edges of the data in velocity space
    vx_data = vx[valid_mask]
    vy_data = vy[valid_mask]
    
    x_min_data, x_max_data = np.min(vx_data), np.max(vx_data)
    y_min_data, y_max_data = np.min(vy_data), np.max(vy_data)
    
    print(f"📊 Data edges: X=[{x_min_data:.0f}, {x_max_data:.0f}], Y=[{y_min_data:.0f}, {y_max_data:.0f}]")
    
    # Add padding beyond the data edges
    x_min = x_min_data - padding_x
    x_max = x_max_data + padding_x
    y_min = y_min_data - padding_y
    y_max = y_max_data + padding_y
    
    xlim = (x_min, x_max)
    ylim = (y_min, y_max)
    
    print(f"🎯 Smart bounds with padding: X=[{xlim[0]:.0f}, {xlim[1]:.0f}], Y=[{ylim[0]:.0f}, {ylim[1]:.0f}]")
    
    return xlim, ylim

def create_1d_projections(vx_plane_theta, vz_plane_theta, df_theta):
    """
    Create 1D side views by summing along each axis to find bulk data and outliers.
    This helps identify straggler data points affecting smart bounds.
    """
    print("📊 Creating 1D side views to identify bulk data vs outliers...")
    
    # Create velocity bins for analysis
    vx_flat = vx_plane_theta.flatten()
    vz_flat = vz_plane_theta.flatten()
    vdf_flat = df_theta.flatten()
    
    # Remove NaN and zero values
    valid_mask = np.isfinite(vdf_flat) & (vdf_flat > 0)
    vx_valid = vx_flat[valid_mask]
    vz_valid = vz_flat[valid_mask] 
    vdf_valid = vdf_flat[valid_mask]
    
    if len(vdf_valid) == 0:
        print("❌ No valid data for projections")
        return
    
    # Create velocity bins
    n_bins = 50
    vx_bins = np.linspace(np.min(vx_valid), np.max(vx_valid), n_bins)
    vz_bins = np.linspace(np.min(vz_valid), np.max(vz_valid), n_bins)
    
    # Sum VDF data into velocity bins (creating 1D projections)
    vx_projection = np.zeros(n_bins-1)
    vz_projection = np.zeros(n_bins-1)
    
    for i in range(n_bins-1):
        # X projection: sum all VDF data in this vx bin
        vx_mask = (vx_valid >= vx_bins[i]) & (vx_valid < vx_bins[i+1])
        if np.any(vx_mask):
            vx_projection[i] = np.sum(vdf_valid[vx_mask])
        
        # Z projection: sum all VDF data in this vz bin  
        vz_mask = (vz_valid >= vz_bins[i]) & (vz_valid < vz_bins[i+1])
        if np.any(vz_mask):
            vz_projection[i] = np.sum(vdf_valid[vz_mask])
    
    # Calculate bin centers for plotting
    vx_centers = (vx_bins[:-1] + vx_bins[1:]) / 2
    vz_centers = (vz_bins[:-1] + vz_bins[1:]) / 2
    
    # Find where bulk of data is (above certain percentile threshold)
    vx_threshold = np.percentile(vx_projection[vx_projection > 0], 10)  # 10th percentile of non-zero data
    vz_threshold = np.percentile(vz_projection[vz_projection > 0], 10)
    
    vx_bulk_mask = vx_projection >= vx_threshold
    vz_bulk_mask = vz_projection >= vz_threshold
    
    if np.any(vx_bulk_mask):
        vx_bulk_range = (np.min(vx_centers[vx_bulk_mask]), np.max(vx_centers[vx_bulk_mask]))
    else:
        vx_bulk_range = (np.min(vx_centers), np.max(vx_centers))
        
    if np.any(vz_bulk_mask):
        vz_bulk_range = (np.min(vz_centers[vz_bulk_mask]), np.max(vz_centers[vz_bulk_mask]))
    else:
        vz_bulk_range = (np.min(vz_centers), np.max(vz_centers))
    
    print(f"📈 Vx side view: bulk data from {vx_bulk_range[0]:.0f} to {vx_bulk_range[1]:.0f} km/s")
    print(f"📈 Vz side view: bulk data from {vz_bulk_range[0]:.0f} to {vz_bulk_range[1]:.0f} km/s")
    
    # Create 1D side view plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))
    
    # Vx side view (top-left)
    ax1.semilogy(vx_centers, vx_projection + 1e-30, 'b-', linewidth=2, label='VDF side view')
    ax1.axhline(vx_threshold, color='red', linestyle='--', alpha=0.7, label=f'Bulk threshold (10%)')
    ax1.axvspan(vx_bulk_range[0], vx_bulk_range[1], alpha=0.2, color='green', label='Bulk data range')
    ax1.set_xlabel('$v_x$ (km/s)')
    ax1.set_ylabel('Summed VDF (log scale)')
    ax1.set_title('Vx Side View (summed across Vz)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Vz side view (top-right)
    ax2.semilogy(vz_centers, vz_projection + 1e-30, 'r-', linewidth=2, label='VDF side view')
    ax2.axhline(vz_threshold, color='red', linestyle='--', alpha=0.7, label=f'Bulk threshold (10%)')
    ax2.axvspan(vz_bulk_range[0], vz_bulk_range[1], alpha=0.2, color='green', label='Bulk data range')
    ax2.set_xlabel('$v_z$ (km/s)')
    ax2.set_ylabel('Summed VDF (log scale)')
    ax2.set_title('Vz Side View (summed across Vx)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Original 2D plot for reference (bottom-left)
    cs3 = ax3.contourf(vx_plane_theta, vz_plane_theta, df_theta, 
                      locator=ticker.LogLocator(), cmap=cm.cool)
    ax3.set_xlabel('$v_x$ km/s')
    ax3.set_ylabel('$v_z$ km/s')
    ax3.set_title("Original 2D VDF (for reference)")
    ax3.grid(True, alpha=0.3)
    
    # Zoomed 2D plot using bulk ranges (bottom-right)
    cs4 = ax4.contourf(vx_plane_theta, vz_plane_theta, df_theta, 
                      locator=ticker.LogLocator(), cmap=cm.cool)
    
    # Add padding to bulk ranges - separate padding for theta plane
    theta_x_smart_padding = 100  # User requested separate padding values
    theta_y_smart_padding = 100
    bulk_xlim = (vx_bulk_range[0] - theta_x_smart_padding, vx_bulk_range[1] + theta_x_smart_padding)
    bulk_ylim = (vz_bulk_range[0] - theta_y_smart_padding, vz_bulk_range[1] + theta_y_smart_padding)
    
    ax4.set_xlim(bulk_xlim)
    ax4.set_ylim(bulk_ylim)
    ax4.set_xlabel('$v_x$ km/s')
    ax4.set_ylabel('$v_z$ km/s')
    ax4.set_title("Zoomed to Bulk Data + Padding")
    ax4.grid(True, alpha=0.3)
    
    plt.subplots_adjust(hspace=0.25, wspace=0.25)  # Legends back on plots
    plt.savefig('tests/Images/VDF_1d_side_views.png', dpi=150, bbox_inches='tight')
    print("✅ Saved: tests/Images/VDF_1d_side_views.png")
    
    return vx_bulk_range, vz_bulk_range, bulk_xlim, bulk_ylim

def create_FIXED_bounds_comparison():
    """Create comparison using EXACT working processing from test_jaye_exact_replication.py"""
    
    print("🚀 Creating FIXED bounds comparison...")
    print("📡 Downloading data EXACTLY like working script...")
    
    # Download VDF data using Jaye's exact method
    trange = ['2020-01-29/00:00', '2020-01-30/00:00']
    VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                              notplot=True, time_clip=True, downloadonly=True, get_support_data=True)
    
    if not VDfile:
        print("❌ No VDF files downloaded")
        return
        
    print(f"📁 Downloaded: {VDfile[0]}")
    
    # Process data using EXACT working approach
    dat = cdflib.CDF(VDfile[0])
    
    # Get time array (Jaye's Cell 11)
    epoch_dt64 = cdflib.cdfepoch.to_datetime(dat.varget('Epoch'))
    epoch = pd.to_datetime(epoch_dt64).to_pydatetime().tolist()
    
    # Find target time slice (Jaye's exact time)
    target_time = datetime(2020, 1, 29, 18, 10, 2)
    tSliceIndex = bisect.bisect_left(epoch, target_time)
    
    print(f"Desired timeslice: {target_time}")
    print(f"time Index: {tSliceIndex}")
    print(f"Time of closest data point: {epoch[tSliceIndex]}")
    
    # Process VDF data using EXACT working approach
    vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, tSliceIndex)
    
    # Get both theta and phi planes using EXACT working approach
    vx_plane_theta, vz_plane_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
    vx_plane_phi, vy_plane_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
    
    print(f"✅ VDF data processed: time={epoch[tSliceIndex]}")
    print(f"   Theta VDF range: {np.nanmin(df_theta):.2e} to {np.nanmax(df_theta):.2e}")
    print(f"   Phi VDF range: {np.nanmin(df_phi):.2e} to {np.nanmax(df_phi):.2e}")
    
    # Check velocity ranges
    print(f"🔍 Velocity ranges:")
    print(f"   Theta plane - Vx: {np.nanmin(vx_plane_theta):.0f} to {np.nanmax(vx_plane_theta):.0f}, Vz: {np.nanmin(vz_plane_theta):.0f} to {np.nanmax(vz_plane_theta):.0f}")
    print(f"   Phi plane - Vx: {np.nanmin(vx_plane_phi):.0f} to {np.nanmax(vx_plane_phi):.0f}, Vy: {np.nanmin(vy_plane_phi):.0f} to {np.nanmax(vy_plane_phi):.0f}")
    
    # CREATE 1D SIDE VIEWS FIRST to analyze bulk data (use theta plane for reference)
    print("\n" + "="*60)
    vx_bulk_range, vz_bulk_range, bulk_xlim, bulk_ylim = create_1d_projections(
        vx_plane_theta, vz_plane_theta, df_theta)
    print("="*60 + "\n")
    
    # Calculate bulk bounds for phi plane (simplified, no plot generation)
    print("📊 Calculating bulk bounds for phi plane...")
    
    # Find valid data for phi plane (flatten arrays first)
    vx_flat_phi = vx_plane_phi.flatten()
    vy_flat_phi = vy_plane_phi.flatten()
    df_flat_phi = df_phi.flatten()
    
    valid_mask_phi = np.isfinite(df_flat_phi) & (df_flat_phi > 0)
    vx_valid_phi = vx_flat_phi[valid_mask_phi]
    vy_valid_phi = vy_flat_phi[valid_mask_phi]
    vdf_valid_phi = df_flat_phi[valid_mask_phi]
    
    if len(vdf_valid_phi) > 0:
        # Create velocity bins for phi plane
        n_bins = 50
        vx_bins_phi = np.linspace(np.min(vx_valid_phi), np.max(vx_valid_phi), n_bins)
        vy_bins_phi = np.linspace(np.min(vy_valid_phi), np.max(vy_valid_phi), n_bins)
        
        # Sum VDF data into velocity bins
        vx_projection_phi = np.zeros(n_bins-1)
        vy_projection_phi = np.zeros(n_bins-1)
        
        for i in range(n_bins-1):
            # X projection for phi plane
            vx_mask = (vx_valid_phi >= vx_bins_phi[i]) & (vx_valid_phi < vx_bins_phi[i+1])
            if np.any(vx_mask):
                vx_projection_phi[i] = np.sum(vdf_valid_phi[vx_mask])
            
            # Y projection for phi plane
            vy_mask = (vy_valid_phi >= vy_bins_phi[i]) & (vy_valid_phi < vy_bins_phi[i+1])
            if np.any(vy_mask):
                vy_projection_phi[i] = np.sum(vdf_valid_phi[vy_mask])
        
        # Calculate bin centers
        vx_centers_phi = (vx_bins_phi[:-1] + vx_bins_phi[1:]) / 2
        vy_centers_phi = (vy_bins_phi[:-1] + vy_bins_phi[1:]) / 2
        
        # Find bulk data (above 10th percentile threshold)
        vx_threshold_phi = np.percentile(vx_projection_phi[vx_projection_phi > 0], 10)
        vy_threshold_phi = np.percentile(vy_projection_phi[vy_projection_phi > 0], 10)
        
        vx_bulk_mask_phi = vx_projection_phi >= vx_threshold_phi
        vy_bulk_mask_phi = vy_projection_phi >= vy_threshold_phi
        
        if np.any(vx_bulk_mask_phi):
            vx_bulk_range_phi = (np.min(vx_centers_phi[vx_bulk_mask_phi]), np.max(vx_centers_phi[vx_bulk_mask_phi]))
        else:
            vx_bulk_range_phi = (np.min(vx_centers_phi), np.max(vx_centers_phi))
            
        if np.any(vy_bulk_mask_phi):
            vy_bulk_range_phi = (np.min(vy_centers_phi[vy_bulk_mask_phi]), np.max(vy_centers_phi[vy_bulk_mask_phi]))
        else:
            vy_bulk_range_phi = (np.min(vy_centers_phi), np.max(vy_centers_phi))
            
        # Add padding (200 km/s for phi plane as requested)
        phi_x_smart_padding = 200
        phi_y_smart_padding = 200
        bulk_xlim_phi = (vx_bulk_range_phi[0] - phi_x_smart_padding, vx_bulk_range_phi[1] + phi_x_smart_padding)
        bulk_ylim_phi = (vy_bulk_range_phi[0] - phi_y_smart_padding, vy_bulk_range_phi[1] + phi_y_smart_padding)
        
        print(f"📈 Phi plane bulk data: X=[{vx_bulk_range_phi[0]:.0f}, {vx_bulk_range_phi[1]:.0f}], Y=[{vy_bulk_range_phi[0]:.0f}, {vy_bulk_range_phi[1]:.0f}]")
    else:
        # Fallback bounds
        bulk_xlim_phi = (-700, 0)
        bulk_ylim_phi = (-500, 500)
        print("⚠️ No valid phi plane data, using fallback bounds")
    
    # INTELLIGENT ZERO CLIPPING: If bulk data doesn't cross 0 but padding pushes past 0, clip at 0
    print("🧠 Applying intelligent zero clipping...")
    
    # For theta plane - check if BULK DATA crosses zero
    theta_bulk_data_crosses_zero = (vx_bulk_range[0] < 0 < vx_bulk_range[1])
    if not theta_bulk_data_crosses_zero and vx_bulk_range[1] < 0 and bulk_xlim[1] > 0:
        # Bulk data is entirely negative but padding pushed past zero - clip at zero
        original_upper = bulk_xlim[1]
        bulk_xlim = (bulk_xlim[0], 0)
        print(f"   📐 Theta plane: Clipped x-axis at 0 (bulk data {vx_bulk_range[0]:.0f} to {vx_bulk_range[1]:.0f} entirely negative, padding pushed to {original_upper:.0f})")
    
    # For phi plane - check if BULK DATA crosses zero  
    phi_bulk_data_crosses_zero = (vx_bulk_range_phi[0] < 0 < vx_bulk_range_phi[1])
    if not phi_bulk_data_crosses_zero and vx_bulk_range_phi[1] < 0 and bulk_xlim_phi[1] > 0:
        # Bulk data is entirely negative but padding pushed past zero - clip at zero
        original_upper = bulk_xlim_phi[1]
        bulk_xlim_phi = (bulk_xlim_phi[0], 0)
        print(f"   📐 Phi plane: Clipped x-axis at 0 (bulk data {vx_bulk_range_phi[0]:.0f} to {vx_bulk_range_phi[1]:.0f} entirely negative, padding pushed to {original_upper:.0f})")
    
    # Create 2x2 comparison plot matrix with better spacing
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    plt.subplots_adjust(hspace=0.25, wspace=0.25)  # Happy medium spacing
    
    # Jaye's bounds from his notebook Cell 39 & 41 - KEEP THESE EXACT
    jaye_xlim_theta = (-800, 0)    # EXACT from Jaye's notebook Cell 39 & 41
    jaye_ylim_theta = (-400, 400)  # EXACT from Jaye's notebook Cell 41
    jaye_xlim_phi = (-800, 0)      # EXACT from Jaye's notebook Cell 41  
    jaye_ylim_phi = (-200, 600)    # EXACT from Jaye's notebook Cell 41
    
    # TOP ROW: Jaye's Original Bounds
    print("📈 Creating plots with Jaye's EXACT original bounds...")
    
    # Top-left: Theta plane with Jaye's bounds
    cs1 = ax1.contourf(vx_plane_theta, vz_plane_theta, df_theta, 
                      locator=ticker.LogLocator(), cmap=cm.cool)
    cbar1 = fig.colorbar(cs1, ax=ax1)
    cbar1.set_label(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$')
    
    ax1.set_xlim(jaye_xlim_theta)
    ax1.set_ylim(jaye_ylim_theta)
    ax1.set_xlabel('$v_x$ km/s')
    ax1.set_ylabel('$v_z$ km/s')
    ax1.set_title("Jaye's Bounds - Theta Plane (vx-vz)")
    ax1.grid(True, alpha=0.3)
    
    # Top-right: Phi plane with Jaye's bounds
    cs2 = ax2.contourf(vx_plane_phi, vy_plane_phi, df_phi, 
                      locator=ticker.LogLocator(), cmap=cm.cool)
    cbar2 = fig.colorbar(cs2, ax=ax2)
    cbar2.set_label(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$')
    
    ax2.set_xlim(jaye_xlim_phi)
    ax2.set_ylim(jaye_ylim_phi)
    ax2.set_xlabel('$v_x$ km/s')
    ax2.set_ylabel('$v_y$ km/s')
    ax2.set_title("Jaye's Bounds - Phi Plane (vx-vy)")
    ax2.grid(True, alpha=0.3)
    
    # BOTTOM ROW: Smart Bounds
    print("📈 Creating plots with bulk-based smart bounds...")
    
    # Bottom-left: Theta plane with smart bounds
    cs3 = ax3.contourf(vx_plane_theta, vz_plane_theta, df_theta, 
                      locator=ticker.LogLocator(), cmap=cm.cool)
    cbar3 = fig.colorbar(cs3, ax=ax3)
    cbar3.set_label(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$')
    
    ax3.set_xlim(bulk_xlim)  # Use bulk_xlim from create_1d_projections
    ax3.set_ylim(bulk_ylim)  # Use bulk_ylim from create_1d_projections
    ax3.set_xlabel('$v_x$ km/s')
    ax3.set_ylabel('$v_z$ km/s')
    ax3.set_title("BULK-Based Smart Bounds - Theta Plane (vx-vz)")
    ax3.grid(True, alpha=0.3)
    
    # Bottom-right: Phi plane with smart bounds
    cs4 = ax4.contourf(vx_plane_phi, vy_plane_phi, df_phi, 
                      locator=ticker.LogLocator(), cmap=cm.cool)
    cbar4 = fig.colorbar(cs4, ax=ax4)
    cbar4.set_label(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$')
    
    ax4.set_xlim(bulk_xlim_phi)
    ax4.set_ylim(bulk_ylim_phi)
    ax4.set_xlabel('$v_x$ km/s')
    ax4.set_ylabel('$v_y$ km/s')
    ax4.set_title("BULK-Based Smart Bounds - Phi Plane (vx-vy)")
    ax4.grid(True, alpha=0.3)
    
    # Print bounds comparison
    print(f"📏 Jaye's EXACT bounds (theta):      X={jaye_xlim_theta}, Y={jaye_ylim_theta}")
    print(f"📏 Jaye's EXACT bounds (phi):        X={jaye_xlim_phi}, Y={jaye_ylim_phi}")
    print(f"📏 BULK-based bounds (theta plane):  X=({bulk_xlim[0]:.0f}, {bulk_xlim[1]:.0f}), Y=({bulk_ylim[0]:.0f}, {bulk_ylim[1]:.0f}) [100km/s padding]")
    print(f"📏 BULK-based bounds (phi plane):    X=({bulk_xlim_phi[0]:.0f}, {bulk_xlim_phi[1]:.0f}), Y=({bulk_ylim_phi[0]:.0f}, {bulk_ylim_phi[1]:.0f}) [200km/s padding]")
    
    # Don't use tight_layout since we manually set spacing with subplots_adjust
    plt.savefig('tests/Images/VDF_theta_phi_bounds_comparison.png', dpi=150, bbox_inches='tight')
    print("✅ Saved: tests/Images/VDF_theta_phi_bounds_comparison.png")
    
    plt.show()

if __name__ == "__main__":
    create_FIXED_bounds_comparison()