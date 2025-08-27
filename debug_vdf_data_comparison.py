#!/usr/bin/env python3
"""
EXACT VDF Data Comparison Test
Compares the IDENTICAL processed VDF data between matplotlib (vdyes) and Plotly approaches.
This will identify the exact transpose/orientation issue.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import plotly.graph_objects as go
import plotly.offline as pyo
import sys
import os

# Add tests directory to path
sys.path.append('tests')
from test_VDF_smart_bounds_debug import (
    extract_and_process_vdf_timeslice_EXACT,
    jaye_exact_theta_plane_processing, 
    jaye_exact_phi_plane_processing
)

# Import plotbot data loading
import pyspedas
import cdflib
import pandas as pd
from dateutil.parser import parse

def load_vdf_data(trange):
    """Load VDF data using exact vdyes.py approach"""
    print(f"📡 Loading VDF data for {trange}")
    
    # Download using exact vdyes approach
    VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                              notplot=True, time_clip=True, downloadonly=True, get_support_data=True, 
                              no_update=True)
    
    if not VDfile:
        VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                                  notplot=True, time_clip=True, downloadonly=True, get_support_data=True, 
                                  no_update=False)
    
    if not VDfile:
        raise ValueError(f"No VDF files found for {trange}")
    
    dat = cdflib.CDF(VDfile[0])
    epoch_dt64 = cdflib.cdfepoch.to_datetime(dat.varget('Epoch'))
    epoch = pd.to_datetime(epoch_dt64).to_pydatetime().tolist()
    
    # Find first time slice
    start_dt = parse(trange[0].replace('/', ' '))
    end_dt = parse(trange[1].replace('/', ' '))
    time_mask = [(t >= start_dt and t <= end_dt) for t in epoch]
    available_indices = [i for i, mask in enumerate(time_mask) if mask]
    
    if not available_indices:
        raise ValueError(f"No time points found in range {trange}")
    
    time_index = available_indices[0]
    print(f"✅ Using time index {time_index}: {epoch[time_index]}")
    
    return dat, time_index

def process_vdf_data(dat, time_index):
    """Process VDF data using EXACT same functions as vdyes.py"""
    print(f"⚙️ Processing VDF data with time index {time_index}")
    
    # Use EXACT same processing as vdyes.py
    vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, time_index)
    vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
    vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
    
    print(f"✅ VDF processing complete:")
    print(f"   Theta shapes: vx={vx_theta.shape}, vz={vz_theta.shape}, df={df_theta.shape}")
    print(f"   Phi shapes: vx={vx_phi.shape}, vy={vy_phi.shape}, df={df_phi.shape}")
    print(f"   Theta VDF range: {np.nanmin(df_theta):.2e} to {np.nanmax(df_theta):.2e}")
    print(f"   Phi VDF range: {np.nanmin(df_phi):.2e} to {np.nanmax(df_phi):.2e}")
    
    return vdf_data, vx_theta, vz_theta, df_theta, vx_phi, vy_phi, df_phi

def create_matplotlib_plot(vx_theta, vz_theta, df_theta, vx_phi, vy_phi, df_phi):
    """Create matplotlib plot using EXACT vdyes.py approach"""
    print("📊 Creating matplotlib plot (vdyes.py approach)")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor='white')
    
    # Theta plane - EXACT vdyes.py approach
    cs1 = ax1.contourf(vx_theta, vz_theta, df_theta, 
                      locator=ticker.LogLocator(), cmap='cool')
    ax1.set_xlabel('$v_x$ km/s')
    ax1.set_ylabel('$v_z$ km/s')
    ax1.set_title('θ-plane (matplotlib)')
    
    # Print coordinate info
    print(f"   Matplotlib Theta:")
    print(f"     vx_theta range: [{np.nanmin(vx_theta):.1f}, {np.nanmax(vx_theta):.1f}]")
    print(f"     vz_theta range: [{np.nanmin(vz_theta):.1f}, {np.nanmax(vz_theta):.1f}]")
    print(f"     df_theta range: [{np.nanmin(df_theta):.2e}, {np.nanmax(df_theta):.2e}]")
    
    # Phi plane - EXACT vdyes.py approach
    cs2 = ax2.contourf(vx_phi, vy_phi, df_phi,
                      locator=ticker.LogLocator(), cmap='cool')
    ax2.set_xlabel('$v_x$ km/s')
    ax2.set_ylabel('$v_y$ km/s')
    ax2.set_title('φ-plane (matplotlib)')
    
    print(f"   Matplotlib Phi:")
    print(f"     vx_phi range: [{np.nanmin(vx_phi):.1f}, {np.nanmax(vx_phi):.1f}]")
    print(f"     vy_phi range: [{np.nanmin(vy_phi):.1f}, {np.nanmax(vy_phi):.1f}]")
    print(f"     df_phi range: [{np.nanmin(df_phi):.2e}, {np.nanmax(df_phi):.2e}]")
    
    plt.tight_layout()
    plt.savefig('matplotlib_vdf_reference.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return fig

def create_plotly_plot_current_approach(vx_theta, vz_theta, df_theta, vx_phi, vy_phi, df_phi):
    """Create Plotly plot using our CURRENT (broken) approach"""
    print("📊 Creating Plotly plot (current broken approach)")
    
    # Current approach (has orientation issues)
    def create_broken_contour(vx, vy, vdf_data, title):
        # This is what we're currently doing (WRONG)
        x_coords = np.linspace(np.min(vx), np.max(vx), vx.shape[1])
        y_coords = np.linspace(np.min(vy), np.max(vy), vy.shape[0])
        
        print(f"   Plotly {title} (BROKEN):")
        print(f"     x_coords range: [{np.min(x_coords):.1f}, {np.max(x_coords):.1f}]")
        print(f"     y_coords range: [{np.min(y_coords):.1f}, {np.max(y_coords):.1f}]")
        print(f"     vdf_data range: [{np.nanmin(vdf_data):.2e}, {np.nanmax(vdf_data):.2e}]")
        
        return go.Contour(
            x=x_coords,
            y=y_coords, 
            z=vdf_data,
            colorscale='Blues',
            showscale=True,
            line=dict(width=0)
        )
    
    fig = go.Figure()
    
    # Add theta plane
    theta_contour = create_broken_contour(vx_theta, vz_theta, df_theta, "Theta")
    fig.add_trace(theta_contour)
    
    fig.update_layout(
        title="Plotly VDF - Current BROKEN Approach",
        xaxis_title="vx (km/s)",
        yaxis_title="vz (km/s)",
        width=600,
        height=500
    )
    
    pyo.plot(fig, filename='plotly_vdf_broken.html', auto_open=False)
    print("   Saved broken Plotly plot to: plotly_vdf_broken.html")
    
    return fig

def analyze_coordinate_differences(vx_theta, vz_theta, df_theta):
    """Analyze exactly how coordinates should be extracted"""
    print("🔍 COORDINATE ANALYSIS:")
    print(f"   Input grid shapes: vx={vx_theta.shape}, vz={vz_theta.shape}, df={df_theta.shape}")
    
    # Matplotlib expects 2D coordinate grids
    print(f"   Matplotlib contourf() gets 2D grids directly:")
    print(f"     vx_theta[0,:] = {vx_theta[0,:5]} ... (first 5 elements)")
    print(f"     vz_theta[:,0] = {vz_theta[:5,0]} ... (first 5 elements)")
    
    # Plotly expects 1D coordinate vectors
    print(f"   Plotly go.Contour() needs 1D vectors:")
    print(f"     Should x = vx_theta[0,:] (X vector)")
    print(f"     Should y = vz_theta[:,0] (Y vector)")
    print(f"     But Z data must match this grid!")
    
    # Check if coordinates are consistent
    x_consistent = np.allclose(vx_theta[0,:], vx_theta[-1,:])
    y_consistent = np.allclose(vz_theta[:,0], vz_theta[:,-1])
    
    print(f"   Grid consistency check:")
    print(f"     X coordinates consistent across rows: {x_consistent}")
    print(f"     Y coordinates consistent across columns: {y_consistent}")
    
    if not x_consistent:
        print(f"     ⚠️ X coordinates vary by row! First/last row diff: {np.max(np.abs(vx_theta[0,:] - vx_theta[-1,:])):.2f}")
    
    if not y_consistent:
        print(f"     ⚠️ Y coordinates vary by column! First/last col diff: {np.max(np.abs(vz_theta[:,0] - vz_theta[:,-1])):.2f}")

def create_plotly_plot_fixed_approach(vx_theta, vz_theta, df_theta, vx_phi, vy_phi, df_phi):
    """Create Plotly plot using FIXED approach based on analysis"""
    print("📊 Creating Plotly plot (FIXED approach)")
    
    def create_fixed_contour(vx, vy, vdf_data, title):
        # FIXED approach - use actual coordinate vectors from grids
        if vx.ndim == 2 and vy.ndim == 2:
            # Extract coordinate vectors from 2D grids (like matplotlib does)
            x_coords = vx[0, :]  # X vector from first row
            y_coords = vy[:, 0]  # Y vector from first column
        else:
            x_coords = vx
            y_coords = vy
        
        print(f"   Plotly {title} (FIXED):")
        print(f"     x_coords shape: {x_coords.shape}, range: [{np.min(x_coords):.1f}, {np.max(x_coords):.1f}]")
        print(f"     y_coords shape: {y_coords.shape}, range: [{np.min(y_coords):.1f}, {np.max(y_coords):.1f}]")
        print(f"     vdf_data shape: {vdf_data.shape}, range: [{np.nanmin(vdf_data):.2e}, {np.nanmax(vdf_data):.2e}]")
        
        # Clean data for plotting
        z_plot = vdf_data.copy()
        z_plot[z_plot <= 0] = np.nan
        
        return go.Contour(
            x=x_coords,
            y=y_coords,
            z=z_plot,
            colorscale='Blues',
            showscale=True,
            line=dict(width=0),
            contours_coloring='heatmap'  # Try filled contours like matplotlib
        )
    
    # Create subplot figure
    from plotly.subplots import make_subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['θ-plane (Plotly FIXED)', 'φ-plane (Plotly FIXED)'],
        horizontal_spacing=0.1
    )
    
    # Add theta plane
    theta_contour = create_fixed_contour(vx_theta, vz_theta, df_theta, "Theta")
    fig.add_trace(theta_contour, row=1, col=1)
    
    # Add phi plane  
    phi_contour = create_fixed_contour(vx_phi, vy_phi, df_phi, "Phi")
    fig.add_trace(phi_contour, row=1, col=2)
    
    fig.update_layout(
        title="Plotly VDF - FIXED Approach",
        width=1000,
        height=500
    )
    
    fig.update_xaxes(title_text="vx (km/s)", row=1, col=1)
    fig.update_yaxes(title_text="vz (km/s)", row=1, col=1)
    fig.update_xaxes(title_text="vx (km/s)", row=1, col=2)
    fig.update_yaxes(title_text="vy (km/s)", row=1, col=2)
    
    pyo.plot(fig, filename='plotly_vdf_fixed.html', auto_open=False)
    print("   Saved FIXED Plotly plot to: plotly_vdf_fixed.html")
    
    return fig

def main():
    """Run the complete VDF data comparison test"""
    print("🚀 VDF Data Comparison Test - Matplotlib vs Plotly")
    print("=" * 60)
    
    # Use same time range as working examples
    trange = ['2020-01-29/18:00:00.000', '2020-01-29/18:05:00.000']
    
    try:
        # 1. Load VDF data (exact vdyes.py approach)
        dat, time_index = load_vdf_data(trange)
        
        # 2. Process VDF data (IDENTICAL processing)
        vdf_data, vx_theta, vz_theta, df_theta, vx_phi, vy_phi, df_phi = process_vdf_data(dat, time_index)
        
        # 3. Analyze coordinate structure
        analyze_coordinate_differences(vx_theta, vz_theta, df_theta)
        
        # 4. Create matplotlib reference (EXACT vdyes.py approach)
        matplotlib_fig = create_matplotlib_plot(vx_theta, vz_theta, df_theta, vx_phi, vy_phi, df_phi)
        
        # 5. Create Plotly plot with current broken approach
        broken_plotly_fig = create_plotly_plot_current_approach(vx_theta, vz_theta, df_theta, vx_phi, vy_phi, df_phi)
        
        # 6. Create Plotly plot with FIXED approach
        fixed_plotly_fig = create_plotly_plot_fixed_approach(vx_theta, vz_theta, df_theta, vx_phi, vy_phi, df_phi)
        
        print("\n" + "=" * 60)
        print("✅ COMPARISON COMPLETE!")
        print("📁 Files generated:")
        print("   - matplotlib_vdf_reference.png (working matplotlib)")
        print("   - plotly_vdf_broken.html (current broken approach)")
        print("   - plotly_vdf_fixed.html (proposed fix)")
        print("\n🔍 Open these files to compare visually!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
