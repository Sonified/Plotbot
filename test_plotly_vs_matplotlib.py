#!/usr/bin/env python3
"""
Test Plotly vs matplotlib with exact same VDF data
"""

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from matplotlib import ticker
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

def test_plotly_contour_with_vdf_data():
    """Test Plotly contour plotting with real VDF data"""
    
    # Get the exact same data as our debug script
    trange = ['2020-01-29/18:00:00.000', '2020-01-29/18:15:00.000']
    
    VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                              notplot=True, time_clip=True, downloadonly=True, get_support_data=True, 
                              no_update=True)
    
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
    
    # Process first time slice
    time_idx = available_indices[0]
    vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, time_idx)
    vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
    vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
    
    print("🔬 Testing Plotly vs matplotlib with EXACT same data...")
    print(f"Theta data: shape {df_theta.shape}, range {np.nanmin(df_theta):.2e} to {np.nanmax(df_theta):.2e}")
    print(f"Theta finite: {np.sum(np.isfinite(df_theta))}/{df_theta.size}")
    print(f"Theta non-zero: {np.sum(df_theta > 0)}/{df_theta.size}")
    
    # TEST 1: Matplotlib contourf (working reference)
    print("\n📊 Test 1: Matplotlib contourf...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    try:
        cs1 = ax1.contourf(vx_theta, vz_theta, df_theta, locator=ticker.LogLocator())
        ax1.set_title('Matplotlib contourf (WORKING)')
        ax1.set_xlabel('Vx (km/s)')
        ax1.set_ylabel('Vz (km/s)')
        plt.colorbar(cs1, ax=ax1)
        print("✅ Matplotlib contourf successful!")
    except Exception as e:
        ax1.text(0.5, 0.5, f'Failed: {e}', ha='center', va='center', transform=ax1.transAxes)
        print(f"❌ Matplotlib failed: {e}")
    
    # TEST 2: Simple pcolormesh for comparison
    try:
        im2 = ax2.pcolormesh(vx_theta, vz_theta, df_theta, shading='auto')
        ax2.set_title('Matplotlib pcolormesh')
        plt.colorbar(im2, ax=ax2)
        print("✅ Matplotlib pcolormesh successful!")
    except Exception as e:
        print(f"❌ Matplotlib pcolormesh failed: {e}")
    
    plt.tight_layout()
    plt.savefig('matplotlib_comparison.png', dpi=300, bbox_inches='tight')
    print("💾 Saved matplotlib_comparison.png")
    
    # TEST 3: Plotly Contour (our current approach)
    print("\n🌐 Test 3: Plotly Contour...")
    
    # Prepare data exactly like our current code
    vdf_plot = df_theta.copy()
    vdf_plot[vdf_plot <= 0] = np.nan
    vdf_plot[~np.isfinite(vdf_plot)] = np.nan
    
    print(f"After cleaning: finite={np.sum(np.isfinite(vdf_plot))}, range={np.nanmin(vdf_plot):.2e} to {np.nanmax(vdf_plot):.2e}")
    
    # Calculate logarithmic contour levels like matplotlib
    valid_data = vdf_plot[np.isfinite(vdf_plot)]
    if len(valid_data) > 0:
        vmin = np.nanmin(valid_data)
        vmax = np.nanmax(valid_data)
        print(f"Valid data: {len(valid_data)} points, range {vmin:.2e} to {vmax:.2e}")
        
        if vmin > 0 and vmax > vmin:
            log_min = np.floor(np.log10(vmin))
            log_max = np.ceil(np.log10(vmax))
            log_levels = np.arange(log_min, log_max + 0.5, 0.5)  # Half-decade intervals
            contour_levels = 10**log_levels
            contour_levels = contour_levels[(contour_levels >= vmin) & (contour_levels <= vmax)]
            print(f"Contour levels: {len(contour_levels)} levels from {contour_levels[0]:.2e} to {contour_levels[-1]:.2e}")
        else:
            contour_levels = None
            print("❌ Cannot create log levels: vmin <= 0 or vmax <= vmin")
    else:
        contour_levels = None
        print("❌ No valid data for contour levels")
    
    # Create Plotly figure
    try:
        if contour_levels is not None and len(contour_levels) > 1:
            fig_plotly = go.Figure()
            
            contour = go.Contour(
                x=vx_theta[0, :],  # X coordinates
                y=vz_theta[:, 0],  # Y coordinates  
                z=vdf_plot,  # VDF data
                colorscale='Blues',
                showscale=True,
                line=dict(width=0),  # No contour lines, filled only
                contours=dict(
                    start=np.log10(contour_levels[0]),
                    end=np.log10(contour_levels[-1]),
                    size=(np.log10(contour_levels[-1]) - np.log10(contour_levels[0])) / len(contour_levels)
                ),
                connectgaps=False
            )
            
            fig_plotly.add_trace(contour)
            fig_plotly.update_layout(
                title='Plotly Contour Test',
                xaxis_title='Vx (km/s)',
                yaxis_title='Vz (km/s)',
                width=600, height=500
            )
            
            fig_plotly.write_html('plotly_contour_test.html')
            print("✅ Plotly contour created! Saved as plotly_contour_test.html")
            
        else:
            print("❌ Plotly contour failed: no valid contour levels")
            
    except Exception as e:
        print(f"❌ Plotly contour failed: {e}")
    
    # TEST 4: Plotly Heatmap (alternative approach)
    print("\n🔥 Test 4: Plotly Heatmap...")
    try:
        fig_heatmap = go.Figure()
        
        heatmap = go.Heatmap(
            x=vx_theta[0, :],  # X coordinates
            y=vz_theta[:, 0],  # Y coordinates
            z=vdf_plot,  # VDF data
            colorscale='Blues',
            showscale=True,
            connectgaps=False
        )
        
        fig_heatmap.add_trace(heatmap)
        fig_heatmap.update_layout(
            title='Plotly Heatmap Test',
            xaxis_title='Vx (km/s)',
            yaxis_title='Vz (km/s)',
            width=600, height=500
        )
        
        fig_heatmap.write_html('plotly_heatmap_test.html')
        print("✅ Plotly heatmap created! Saved as plotly_heatmap_test.html")
        
    except Exception as e:
        print(f"❌ Plotly heatmap failed: {e}")
    
    # TEST 5: Data preprocessing investigation  
    print("\n🔍 Test 5: Data preprocessing analysis...")
    
    print("Raw data analysis:")
    print(f"  Total points: {df_theta.size}")
    print(f"  Zero values: {np.sum(df_theta == 0)}")
    print(f"  Non-zero values: {np.sum(df_theta > 0)}")
    print(f"  Finite values: {np.sum(np.isfinite(df_theta))}")
    print(f"  Min non-zero: {np.min(df_theta[df_theta > 0]):.2e}")
    print(f"  Max value: {np.max(df_theta):.2e}")
    
    # Check if the issue is with zero handling
    print("\nZero value investigation:")
    df_theta_no_zeros = df_theta.copy()
    df_theta_no_zeros[df_theta_no_zeros == 0] = np.nan
    print(f"  After removing zeros: {np.sum(np.isfinite(df_theta_no_zeros))} finite values")
    
    return {
        'vx_theta': vx_theta,
        'vz_theta': vz_theta, 
        'df_theta': df_theta,
        'vx_phi': vx_phi,
        'vy_phi': vy_phi,
        'df_phi': df_phi
    }

if __name__ == "__main__":
    test_data = test_plotly_contour_with_vdf_data()
    print("\n✅ Comparison complete!")
    print("📁 Check these files:")
    print("   - matplotlib_comparison.png (working reference)")
    print("   - plotly_contour_test.html (our current approach)")
    print("   - plotly_heatmap_test.html (alternative approach)")
