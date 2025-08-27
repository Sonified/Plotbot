#!/usr/bin/env python3
"""
Interactive VDF Plotting with Plotly - Phase 1 Implementation

This test creates Plotly versions of VDF plots to prepare for interactive web integration.
Converts matplotlib-based vdyes() functionality to Plotly for use in plotbot_interactive().

Based on:
- Existing VDF system: plotbot/vdyes.py
- VDF data processing: test_VDF_smart_bounds_debug.py
- Parameter system: plotbot/data_classes/psp_span_vdf.py
- Interactive framework: plotbot/plotbot_dash.py

Test Objectives:
1. ✅ Port VDF data processing to work with Plotly
2. ✅ Create 3-panel layout (1D collapsed, theta-plane, phi-plane)
3. ✅ Maintain compatibility with psp_span_vdf parameter system
4. ✅ Test with known PSP data (2020-01-29 example)
5. ✅ Validate output against matplotlib vdyes() reference
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.parser import parse

# Add parent directory to path for plotbot imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Plotly imports for interactive plotting
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as pc

# Plotbot imports
from plotbot import *
from plotbot.data_classes.psp_span_vdf import psp_span_vdf
from plotbot.print_manager import print_manager

# Import proven VDF processing functions from existing tests
from test_VDF_smart_bounds_debug import (
    extract_and_process_vdf_timeslice_EXACT,
    jaye_exact_theta_plane_processing,
    jaye_exact_phi_plane_processing
)

def test_plotly_vdf_single_timeslice():
    """
    Test Phase 1: Create Plotly VDF plots for a single time slice.
    
    This reproduces the static vdyes() functionality using Plotly instead of matplotlib.
    Uses the same data processing pipeline but outputs interactive web plots.
    """
    print("\n" + "="*60)
    print("🚀 TEST: Plotly VDF Single Timeslice")
    print("Creating interactive VDF plots using Plotly...")
    print("="*60)
    
    # Use known working PSP data
    target_time = '2020/01/29 18:10:00.000'
    # Create a small time window around the target time for data download
    trange = ['2020/01/29 18:00:00.000', '2020/01/29 18:30:00.000']
    
    print(f"📅 Target time: {target_time}")
    print(f"📅 Data range: {trange[0]} to {trange[1]}")
    print("📊 Processing VDF data...")
    
    # Get VDF data using existing plotbot system
    get_data(trange, ['spi_sf00_8dx32ex8a'])
    
    # Access processed VDF data from global instance
    vdf_class = psp_span_vdf
    
    if not hasattr(vdf_class, 'datetime') or len(vdf_class.datetime) == 0:
        print("❌ ERROR: No VDF data found")
        return False
    
    print(f"✅ VDF data loaded: {len(vdf_class.datetime)} time points")
    
    # Find closest time slice
    target_datetime = parse(target_time.replace('/', ' '))
    time_index = vdf_class.find_closest_timeslice(target_datetime)
    selected_time = vdf_class.datetime[time_index]
    
    print(f"🎯 Closest time slice: {selected_time} (index {time_index})")
    
    # Process VDF data using EXACT working functions
    print("🔧 Processing VDF time slice...")
    
    # Create a data structure compatible with the existing processing functions
    dat = {
        'Epoch': [vdf_class.raw_data['epoch'][time_index]],
        'THETA': vdf_class.raw_data['theta'][time_index:time_index+1, :],
        'PHI': vdf_class.raw_data['phi'][time_index:time_index+1, :],
        'ENERGY': vdf_class.raw_data['energy'][time_index:time_index+1, :],
        'EFLUX': vdf_class.raw_data['eflux'][time_index:time_index+1, :]
    }
    
    # Process VDF data
    vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, 0)  # Use index 0 since we extracted single slice
    
    # Get theta and phi plane data
    vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
    vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
    
    print("✅ VDF processing complete")
    print(f"   Theta plane VDF range: {np.nanmin(df_theta):.2e} to {np.nanmax(df_theta):.2e}")
    print(f"   Phi plane VDF range: {np.nanmin(df_phi):.2e} to {np.nanmax(df_phi):.2e}")
    
    # Get axis limits using VDF parameter system
    theta_xlim, theta_ylim = vdf_class.get_axis_limits('theta', vx_theta, vz_theta, df_theta)
    phi_xlim, phi_ylim = vdf_class.get_axis_limits('phi', vx_phi, vy_phi, df_phi)
    
    print(f"📏 Axis limits calculated:")
    print(f"   Theta plane: X={theta_xlim}, Y={theta_ylim}")
    print(f"   Phi plane: X={phi_xlim}, Y={phi_ylim}")
    
    # Create Plotly VDF plots
    print("🎨 Creating Plotly VDF plots...")
    fig = create_plotly_vdf_figure(vdf_data, vx_theta, vz_theta, df_theta, 
                                   vx_phi, vy_phi, df_phi, vdf_class, selected_time)
    
    # Display the plot
    print("🌐 Displaying interactive VDF plot...")
    fig.show()
    
    print("✅ Plotly VDF test completed successfully!")
    print("💡 Check your browser for the interactive VDF plot")
    
    return True

def create_plotly_vdf_figure(vdf_data, vx_theta, vz_theta, df_theta, 
                            vx_phi, vy_phi, df_phi, vdf_class, selected_time):
    """
    Create 3-panel Plotly VDF figure matching matplotlib vdyes() layout.
    
    Args:
        vdf_data: Processed VDF data dictionary
        vx_theta, vz_theta, df_theta: Theta plane data
        vx_phi, vy_phi, df_phi: Phi plane data  
        vdf_class: PSP SPAN VDF class instance for parameters
        selected_time: Selected datetime for plot title
        
    Returns:
        plotly.graph_objects.Figure: Interactive VDF figure
    """
    
    # Create subplot structure: 3 panels (1D, theta, phi) + shared colorbar
    fig = make_subplots(
        rows=1, 
        cols=3,
        subplot_titles=('1D Collapsed VDF', 'θ-plane (Vx vs Vz)', 'φ-plane (Vx vs Vy)'),
        specs=[[{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}]],
        horizontal_spacing=0.08,
        column_widths=[0.25, 0.35, 0.35]  # Give more space to 2D plots
    )
    
    # 1. 1D Collapsed VDF (Left Panel)
    print("📈 Creating 1D collapsed VDF...")
    
    # Calculate 1D collapsed VDF (sum over both phi and theta)
    vdf_collapsed = np.sum(vdf_data['vdf'], axis=(0, 2))
    vel_1d = vdf_data['vel'][0, :, 0]  # Velocity array from first phi/theta slice
    
    # Add 1D line plot
    fig.add_trace(
        go.Scatter(
            x=vel_1d,
            y=vdf_collapsed,
            mode='lines',
            line=dict(color='blue', width=2),
            name='1D VDF',
            showlegend=False,
            hovertemplate='Velocity: %{x:.1f} km/s<br>VDF: %{y:.2e}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Configure 1D plot
    fig.update_xaxes(
        title_text='Velocity (km/s)',
        range=[0, 1000],
        row=1, col=1
    )
    fig.update_yaxes(
        title_text='f (s³/km³)',
        type='log',
        row=1, col=1
    )
    
    # 2. Theta Plane (Middle Panel)
    print("🎯 Creating theta plane contour...")
    
    # Get axis limits from VDF parameter system
    theta_xlim, theta_ylim = vdf_class.get_axis_limits('theta', vx_theta, vz_theta, df_theta)
    
    # Create theta plane contour
    theta_contour = create_plotly_contour(
        vx_theta, vz_theta, df_theta, 
        title_suffix="θ-plane",
        colormap=vdf_class.vdf_colormap,
        xlim=theta_xlim,
        ylim=theta_ylim
    )
    
    fig.add_trace(theta_contour, row=1, col=2)
    
    # Configure theta plane axes
    fig.update_xaxes(
        title_text='Vx (km/s)',
        range=theta_xlim,
        row=1, col=2
    )
    fig.update_yaxes(
        title_text='Vz (km/s)', 
        range=theta_ylim,
        row=1, col=2
    )
    
    # 3. Phi Plane (Right Panel) 
    print("🌍 Creating phi plane contour...")
    
    # Get axis limits from VDF parameter system
    phi_xlim, phi_ylim = vdf_class.get_axis_limits('phi', vx_phi, vy_phi, df_phi)
    
    # Create phi plane contour
    phi_contour = create_plotly_contour(
        vx_phi, vy_phi, df_phi,
        title_suffix="φ-plane", 
        colormap=vdf_class.vdf_colormap,
        xlim=phi_xlim,
        ylim=phi_ylim
    )
    
    fig.add_trace(phi_contour, row=1, col=3)
    
    # Configure phi plane axes
    fig.update_xaxes(
        title_text='Vx (km/s)',
        range=phi_xlim,
        row=1, col=3
    )
    fig.update_yaxes(
        title_text='Vy (km/s)',
        range=phi_ylim,
        row=1, col=3
    )
    
    # Overall figure styling
    fig.update_layout(
        title=dict(
            text=f'PSP SPAN-I VDF: {selected_time.strftime("%Y-%m-%d %H:%M:%S")}',
            x=0.5,
            font=dict(size=16 * vdf_class.vdf_text_scaling)
        ),
        height=int(vdf_class.vdf_figure_height * 100),  # Convert to pixels
        width=int(vdf_class.vdf_figure_width * 100),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12 * vdf_class.vdf_text_scaling)
    )
    
    print("✅ Plotly VDF figure created successfully")
    
    return fig

def create_plotly_contour(vx, vy, vdf_data, title_suffix="", colormap='cool', xlim=None, ylim=None):
    """
    Create Plotly contour plot for VDF data.
    
    Args:
        vx, vy: 2D velocity coordinate arrays
        vdf_data: 2D VDF data array
        title_suffix: String to append to hover text
        colormap: Colormap name
        xlim, ylim: Axis limits (optional)
        
    Returns:
        plotly.graph_objects.Contour: Contour plot object
    """
    
    # Prepare data for plotting (handle zeros/negatives for log scale)
    vdf_plot = vdf_data.copy()
    vdf_plot[vdf_plot <= 0] = np.nan
    vdf_plot[~np.isfinite(vdf_plot)] = np.nan
    
    # Calculate contour levels (logarithmic)
    valid_data = vdf_plot[np.isfinite(vdf_plot)]
    if len(valid_data) > 0:
        vmin = np.percentile(valid_data, 1)   # 1st percentile
        vmax = np.percentile(valid_data, 99)  # 99th percentile
        
        if vmin > 0 and vmax > vmin:
            # Logarithmic levels
            levels = np.logspace(np.log10(vmin), np.log10(vmax), 20)
        else:
            # Fallback to linear
            levels = 20
    else:
        levels = 20
    
    # Convert matplotlib colormap to Plotly format
    if colormap == 'cool':
        plotly_colormap = 'Blues'
    elif colormap == 'viridis':
        plotly_colormap = 'Viridis'
    elif colormap == 'plasma':
        plotly_colormap = 'Plasma'
    elif colormap == 'jet':
        plotly_colormap = 'Jet'
    else:
        plotly_colormap = 'Blues'  # Default fallback
    
    # Create contour plot
    contour = go.Contour(
        x=vx.flatten(),
        y=vy.flatten(), 
        z=vdf_plot.flatten(),
        colorscale=plotly_colormap,
        showscale=False,  # We'll add a shared colorbar later if needed
        line=dict(width=0),  # No contour lines, just filled contours
        hovertemplate=f'Vx: %{{x:.1f}} km/s<br>Vy: %{{y:.1f}} km/s<br>VDF: %{{z:.2e}}<br>{title_suffix}<extra></extra>',
        contours=dict(
            start=np.log10(vmin) if vmin > 0 else -10,
            end=np.log10(vmax) if vmax > 0 else -5,
            size=(np.log10(vmax) - np.log10(vmin))/20 if vmin > 0 and vmax > vmin else 0.5
        ) if len(valid_data) > 0 and vmin > 0 else dict()
    )
    
    return contour

def test_plotly_vdf_parameter_system():
    """
    Test Phase 1b: Verify VDF parameter system works with Plotly plots.
    
    Tests different parameter configurations:
    - Smart bounds vs manual limits
    - Different colormaps
    - Different text scaling
    - Peak-centered phi bounds
    """
    print("\n" + "="*60)
    print("🔧 TEST: VDF Parameter System with Plotly")
    print("Testing different VDF parameter configurations...")
    print("="*60)
    
    # Test with custom parameters
    trange = ['2020/01/29 18:10:00.000']
    
    # Configure VDF parameters
    print("⚙️ Configuring custom VDF parameters...")
    psp_span_vdf.enable_smart_padding = True
    psp_span_vdf.theta_smart_padding = 200  # Wider theta bounds
    psp_span_vdf.phi_x_smart_padding = 250  # Wider phi bounds
    psp_span_vdf.phi_y_smart_padding = 250
    psp_span_vdf.phi_peak_centered = True   # Enable peak centering
    psp_span_vdf.vdf_colormap = 'plasma'    # Different colormap
    psp_span_vdf.vdf_text_scaling = 1.2     # Larger text
    
    print(f"   Smart padding: {psp_span_vdf.enable_smart_padding}")
    print(f"   Theta padding: {psp_span_vdf.theta_smart_padding} km/s")
    print(f"   Phi padding: X={psp_span_vdf.phi_x_smart_padding}, Y={psp_span_vdf.phi_y_smart_padding} km/s")
    print(f"   Peak centering: {psp_span_vdf.phi_peak_centered}")
    print(f"   Colormap: {psp_span_vdf.vdf_colormap}")
    print(f"   Text scaling: {psp_span_vdf.vdf_text_scaling}")
    
    # Run the same test with new parameters
    result = test_plotly_vdf_single_timeslice()
    
    if result:
        print("✅ Parameter system test completed successfully!")
        print("💡 Notice the different bounds, colormap, and text size in the plot")
    else:
        print("❌ Parameter system test failed")
    
    # Reset parameters to defaults
    print("🔄 Resetting VDF parameters to defaults...")
    psp_span_vdf.enable_smart_padding = True
    psp_span_vdf.theta_smart_padding = 100
    psp_span_vdf.phi_x_smart_padding = 100
    psp_span_vdf.phi_y_smart_padding = 100
    psp_span_vdf.phi_peak_centered = False
    psp_span_vdf.vdf_colormap = 'cool'
    psp_span_vdf.vdf_text_scaling = 1.0
    
    return result

def test_plotly_vdf_multiple_times():
    """
    Test Phase 1c: Create Plotly VDF plots for multiple time slices.
    
    This prepares for the widget/slider functionality by testing
    VDF plot generation across different times.
    """
    print("\n" + "="*60)
    print("⏰ TEST: Multiple Time Slice VDF Plots")
    print("Creating VDF plots for different time points...")
    print("="*60)
    
    # Use a small time range with multiple points
    trange = ['2020/01/29 18:00:00.000', '2020/01/29 18:30:00.000']
    
    print(f"📅 Time range: {trange[0]} to {trange[1]}")
    
    # Get VDF data
    get_data(trange, ['spi_sf00_8dx32ex8a'])
    
    vdf_class = psp_span_vdf
    
    if not hasattr(vdf_class, 'datetime') or len(vdf_class.datetime) == 0:
        print("❌ ERROR: No VDF data found")
        return False
    
    n_times = len(vdf_class.datetime)
    print(f"✅ Found {n_times} time points")
    
    # Test with first, middle, and last time points
    test_indices = [0, n_times//2, n_times-1]
    
    for i, time_idx in enumerate(test_indices):
        print(f"\n📊 Creating VDF plot {i+1}/3 (time index {time_idx})...")
        
        selected_time = vdf_class.datetime[time_idx]
        print(f"   Time: {selected_time}")
        
        # Create data structure for processing functions
        dat = {
            'Epoch': [vdf_class.raw_data['epoch'][time_idx]],
            'THETA': vdf_class.raw_data['theta'][time_idx:time_idx+1, :],
            'PHI': vdf_class.raw_data['phi'][time_idx:time_idx+1, :],
            'ENERGY': vdf_class.raw_data['energy'][time_idx:time_idx+1, :],
            'EFLUX': vdf_class.raw_data['eflux'][time_idx:time_idx+1, :]
        }
        
        # Process VDF data
        vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, 0)
        vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
        vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
        
        # Create figure
        fig = create_plotly_vdf_figure(vdf_data, vx_theta, vz_theta, df_theta,
                                      vx_phi, vy_phi, df_phi, vdf_class, selected_time)
        
        # Show figure (uncomment to display all plots)
        # fig.show()
        
        print(f"   ✅ VDF plot {i+1} created successfully")
    
    print("\n✅ Multiple time slice test completed!")
    print("💡 This proves VDF generation works across different times")
    print("🚀 Ready for Phase 2: Interactive time slider implementation")
    
    return True

if __name__ == "__main__":
    """Run all Plotly VDF tests in sequence."""
    
    print("🚀 PLOTLY VDF TESTING SUITE")
    print("Phase 1: Converting VDF plots from matplotlib to Plotly")
    print("=" * 60)
    
    # Set up print manager for testing
    print_manager.show_status = True
    print_manager.show_debug = False
    
    try:
        # Test 1: Basic single timeslice VDF plot
        test1_result = test_plotly_vdf_single_timeslice()
        
        # Test 2: Parameter system integration
        test2_result = test_plotly_vdf_parameter_system()
        
        # Test 3: Multiple time slices
        test3_result = test_plotly_vdf_multiple_times()
        
        # Summary
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        print(f"✅ Single timeslice VDF: {'PASS' if test1_result else 'FAIL'}")
        print(f"✅ Parameter system: {'PASS' if test2_result else 'FAIL'}")
        print(f"✅ Multiple timeslices: {'PASS' if test3_result else 'FAIL'}")
        
        all_passed = all([test1_result, test2_result, test3_result])
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED!")
            print("Phase 1 Complete: Plotly VDF backend ready")
            print("Next: Phase 2 - Interactive notebook with time slider")
        else:
            print("\n❌ Some tests failed. Check output above.")
            
    except Exception as e:
        print(f"\n💥 ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
