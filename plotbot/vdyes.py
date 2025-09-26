#Safe code for saving plots:#!/usr/bin/env python3
"""
vdyes - VDF plotting the fine way!
Plotbot module for PSP SPAN-I VDF plotting using our proven working approach.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import matplotlib.cm as cm
from datetime import datetime, timedelta
import sys
import os
import cdflib
import bisect
import pandas as pd
import warnings

# Suppress expected VDF plotting warnings about zero values in log scale
warnings.filterwarnings('ignore', message='Log scale: values of z <= 0 have been masked')
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
warnings.filterwarnings('ignore', message='.*values of z <= 0.*')

# Ensure matplotlib uses white backgrounds (especially important for dark themes)
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['savefig.facecolor'] = 'white'

def vdyes(trange, *variables, force_static=False):
    """
    VDF plotting - the fine way! (renamed from VDFine)
    Enhanced version that can create composite plots with plotbot data.
    Uses Plotbot's class-based parameter system like epad.strahl.colorbar_limits.
    
    Automatically switches between static plot and interactive widget based on available data:
    - Static Mode: Single time point found → 3-panel VDF plot  
    - Widget Mode: Multiple time points found → Interactive time slider with controls
    - Composite Mode: Variables provided → VDF plot + plotbot time series below
    
    Args:
        trange: Time range for VDF plotting (e.g., ['2020/01/29 00:00:00.000', '2020/01/30 00:00:00.000'])
        *variables: Optional plotbot variables to create composite plot (NEW!)
        force_static: Force static mode even when multiple time points available (default: False)
    
    Returns:
        matplotlib.figure.Figure: The VDF plot or composite plot (static mode)
        ipywidgets.Widget: Interactive VDF widget (widget mode)
        
    Logic:
        1. Download VDF data for the requested trange
        2. Count available time points in the data
        3. If variables provided → create composite VDF + plotbot plot
        4. If 1 time point → static plot of that time slice
        5. If >1 time points → interactive widget with time slider
        
    Example Usage:
        # Set parameters on the class instance (Plotbot way)
        psp_span_vdf.theta_x_smart_padding = 150
        psp_span_vdf.enable_zero_clipping = False
        psp_span_vdf.theta_x_axis_limits = (-800, 0)  # Use Jaye's bounds
        
        # VDF only - Single time found → Static plot
        fig = vdyes(['2020/01/29 18:10:00.000', '2020/01/29 18:10:30.000'])
        
        # VDF only - Multiple times found → Interactive widget  
        widget = vdyes(['2020/01/29 17:00:00.000', '2020/01/29 19:00:00.000'])
        
        # NEW: Composite VDF + plotbot time series
        fig = vdyes(['2020/01/29 17:00:00.000', '2020/01/29 19:00:00.000'], mag_rtn_4sa.br)
        fig = vdyes(trange, [mag_rtn_4sa.br, mag_rtn_4sa.bt])  # Multiple variables
    """
    
    from .print_manager import print_manager
    from .data_classes.psp_span_vdf import psp_span_vdf
    from .ploptions import ploptions
    
    print_manager.status(f"🚀 vdyes() - Processing trange: {trange}")
    
    # Check if this is a composite plot request
    if variables:
        print_manager.status(f"🎯 Composite mode: Creating VDF + plotbot plot with {len(variables)} variable(s)")
        return _create_composite_vdf_plotbot_plot(trange, variables)
    
    print_manager.status("📊 VDF-only mode: Creating standard VDF plot")
    
    # Import our proven working VDF processing functions
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests'))
    try:
        from test_VDF_smart_bounds_debug import (
            extract_and_process_vdf_timeslice_EXACT,
            jaye_exact_theta_plane_processing, 
            jaye_exact_phi_plane_processing
        )
    except ImportError:
        raise ImportError("Cannot import proven VDF processing functions from test_VDF_smart_bounds_debug.py")
    
    print_manager.status("📡 Downloading PSP SPAN-I data using proven pyspedas approach...")
    
    # Convert single timestamp to download range for pyspedas (which requires 2-element trange)
    download_trange = trange
    if len(trange) == 1:
        # Create a small time window around the single timestamp for download
        from dateutil.parser import parse
        from datetime import timedelta
        target_dt = parse(trange[0].replace('/', ' '))
        start_dt = target_dt - timedelta(hours=1)  # 1 hour before
        end_dt = target_dt + timedelta(hours=1)    # 1 hour after
        download_trange = [start_dt.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3], 
                          end_dt.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]]
        print_manager.status(f"🎯 Single timestamp: expanding to download range {download_trange}")
    
    # SMART APPROACH: Check for local l2 file first, only download if missing
    from pathlib import Path
    from dateutil.parser import parse
    from .config import config
    
    # Parse date from trange to construct expected file path
    target_date = parse(download_trange[0].replace('/', ' '))
    year_str = str(target_date.year)
    date_str = target_date.strftime('%Y%m%d')
    
    # Construct expected l2 VDF file path (following PSP data structure)
    expected_l2_path = Path(config.data_dir) / "psp/sweap/spi/l2/spi_sf00_8dx32ex8a" / year_str / f"psp_swp_spi_sf00_l2_8dx32ex8a_{date_str}_v04.cdf"
    
    if expected_l2_path.exists():
        print_manager.status(f"✅ Using local l2 VDF file: {expected_l2_path}")
        VDfile = [str(expected_l2_path)]
    else:
        print_manager.status(f"📡 l2 VDF file not found locally, downloading: {expected_l2_path}")
        # Import pyspedas here for lazy loading
        import pyspedas
        
        # CRITICAL: no_update=False is required! 
        # no_update=True ignores the level='l2' parameter and returns ANY matching files
        VDfile = pyspedas.psp.spi(download_trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                                  notplot=True, time_clip=True, downloadonly=True, get_support_data=True, 
                                  no_update=False)  # Must be False to respect level='l2'!
        
        if not VDfile:
            raise ValueError(f"No VDF files downloaded for trange: {trange}")
    
    # Debug: Show what files we're working with
    print_manager.status(f"📁 Working with {len(VDfile)} file(s):")
    for i, file_path in enumerate(VDfile):
        print_manager.status(f"   [{i}] {file_path}")
    
    # CRITICAL FIX: Ensure we only work with l2 files (l3 files don't contain VDF data!)
    l2_files = [f for f in VDfile if 'spi_sf00_l2_8dx32ex8a' in f and 'l3' not in f]
    
    if l2_files:
        selected_file = l2_files[0]  # Use first l2 file
        print_manager.status(f"✅ Selected l2 VDF file: {selected_file}")
    else:
        # No l2 VDF files found - this is an error condition
        l3_files = [f for f in VDfile if 'l3' in f]
        if l3_files:
            raise ValueError(f"❌ VDF Error: Only l3 files found ({l3_files}), but VDF data requires l2 files! l3 contains moments, not velocity distributions.")
        else:
            raise ValueError(f"❌ VDF Error: No l2 VDF files found in {VDfile}. VDF plotting requires 'spi_sf00_l2_8dx32ex8a' files.")
    
    # Process data using EXACT working approach
    dat = cdflib.CDF(selected_file)
    
    # Get time array to determine mode
    epoch_dt64 = cdflib.cdfepoch.to_datetime(dat.varget('Epoch'))
    epoch = pd.to_datetime(epoch_dt64).to_pydatetime().tolist()
    
    # Handle single timestamp vs time range
    from dateutil.parser import parse
    
    if len(trange) == 1:
        # Single timestamp - find closest time slice
        target_dt = parse(trange[0].replace('/', ' '))
        
        # Find the closest time point
        time_diffs = [abs((t - target_dt).total_seconds()) for t in epoch]
        closest_index = time_diffs.index(min(time_diffs))
        
        available_times = [epoch[closest_index]]
        available_indices = [closest_index]
        
        print_manager.status(f"🎯 Single timestamp mode: Found closest time slice at {epoch[closest_index]}")
        
    else:
        # Time range - filter time points to requested range
        start_dt = parse(trange[0].replace('/', ' '))
        end_dt = parse(trange[1].replace('/', ' '))
        
        # Find time points within the requested range
        time_mask = [(t >= start_dt and t <= end_dt) for t in epoch]
        available_times = [epoch[i] for i, mask in enumerate(time_mask) if mask]
        available_indices = [i for i, mask in enumerate(time_mask) if mask]
    
    n_time_points = len(available_times)
    
    print_manager.status(f"📊 Found {n_time_points} time points in trange: {trange}")
    
    # Decide mode based on available data
    if n_time_points == 0:
        raise ValueError(f"No VDF data found in time range {trange}")
    elif n_time_points == 1 or force_static:
        print_manager.status(f"📈 Static mode: {n_time_points} time point(s) → single VDF plot")
        return _create_static_vdf_plot(dat, available_indices[0], epoch)
    else:
        print_manager.status(f"🎛️ Widget mode: {n_time_points} time points → interactive time slider")
        return _create_vdf_widget(dat, available_times, available_indices, trange)

def _create_static_vdf_plot(dat, time_index, epoch):
    """Create a static 3-panel VDF plot for a single time slice."""
    from .print_manager import print_manager
    from .data_classes.psp_span_vdf import psp_span_vdf
    
    # Import VDF processing functions
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests'))
    from test_VDF_smart_bounds_debug import (
        extract_and_process_vdf_timeslice_EXACT,
        jaye_exact_theta_plane_processing, 
        jaye_exact_phi_plane_processing
    )
    
    # Process VDF data using EXACT working functions
    vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, time_index)
    
    # Get theta and phi plane data using EXACT working functions
    vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
    vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
    
    print_manager.status(f"✅ VDF processing complete")
    print_manager.status(f"   Time: {epoch[time_index]}")
    print_manager.status(f"   Theta VDF range: {np.nanmin(df_theta):.2e} to {np.nanmax(df_theta):.2e}")
    print_manager.status(f"   Phi VDF range: {np.nanmin(df_phi):.2e} to {np.nanmax(df_phi):.2e}")
    
    # Use global VDF instance (Plotbot pattern)
    vdf_class = psp_span_vdf
    print_manager.status("📡 Using global PSP SPAN VDF instance")
    
    # Parameters are now read directly from class attributes (Plotbot way)
    print_manager.status(f"🎛️ VDF Parameters: smart_padding={vdf_class.enable_smart_padding}, "
                        f"theta_padding={vdf_class.theta_smart_padding}, "
                        f"colormap={vdf_class.vdf_colormap}")
    
    # Use working parameter hierarchy (manual limits > smart bounds > Jaye's defaults)
    theta_xlim, theta_ylim = vdf_class.get_axis_limits('theta', vx_theta, vz_theta, df_theta)
    phi_xlim, phi_ylim = vdf_class.get_axis_limits('phi', vx_phi, vy_phi, df_phi)
    
    print_manager.status("📊 Creating 3-panel VDF plot using proven approach...")
    print(f"🎛️ VDF Text Scaling: {vdf_class.vdf_text_scaling}")
    
    # Use proven gridspec layout with explicit white backgrounds
    fig = plt.figure(figsize=(vdf_class.vdf_figure_width, vdf_class.vdf_figure_height), facecolor='white')
    fig.patch.set_facecolor('white')  # Ensure figure background is white
    gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 0.05], wspace=0.4)
    
    ax1 = fig.add_subplot(gs[0], facecolor='white')  # 1D line plot
    ax2 = fig.add_subplot(gs[1], facecolor='white')  # θ-plane
    ax3 = fig.add_subplot(gs[2], facecolor='white')  # φ-plane
    cax = fig.add_subplot(gs[3], facecolor='white')  # colorbar
    
    # 1D collapsed VDF (left panel) - Exact approach from working tests
    vdf_allAngles = np.sum(vdf_data['vdf'], axis=(0,2))  # Sum over both phi and theta
    vel_1d = vdf_data['vel'][0,:,0]  # Velocity array
    ax1.plot(vel_1d, vdf_allAngles, 'b-', linewidth=2)
    ax1.set_yscale('log')
    ax1.set_xlim(0, 1000)
    ax1.set_xlabel('Velocity (km/s)', fontsize=12 * vdf_class.vdf_text_scaling)
    ax1.set_ylabel(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$', fontsize=12 * vdf_class.vdf_text_scaling)
    ax1.tick_params(axis='both', labelsize=10 * vdf_class.vdf_text_scaling)
    
    # 2D Theta plane with smart bounds (middle panel)
    cs2 = ax2.contourf(vx_theta, vz_theta, df_theta, 
                      locator=ticker.LogLocator(), cmap=vdf_class.vdf_colormap)
    ax2.set_xlim(theta_xlim)
    ax2.set_ylim(theta_ylim)
    ax2.set_xlabel('$v_x$ km/s', fontsize=12 * vdf_class.vdf_text_scaling)
    ax2.set_ylabel('$v_z$ km/s', fontsize=12 * vdf_class.vdf_text_scaling)
    ax2.set_title('$\\theta$-plane', fontsize=14 * vdf_class.vdf_text_scaling)
    ax2.tick_params(axis='both', labelsize=10 * vdf_class.vdf_text_scaling)
    
    # 2D Phi plane with smart bounds (right panel)
    cs3 = ax3.contourf(vx_phi, vy_phi, df_phi,
                      locator=ticker.LogLocator(), cmap=vdf_class.vdf_colormap)
    ax3.set_xlim(phi_xlim)
    ax3.set_ylim(phi_ylim)
    ax3.set_xlabel('$v_x$ km/s', fontsize=12 * vdf_class.vdf_text_scaling)
    ax3.set_ylabel('$v_y$ km/s', fontsize=12 * vdf_class.vdf_text_scaling)
    ax3.set_title('$\\phi$-plane', fontsize=14 * vdf_class.vdf_text_scaling)
    ax3.tick_params(axis='both', labelsize=10 * vdf_class.vdf_text_scaling)
    
    # Single colorbar in dedicated axis
    cbar = fig.colorbar(cs2, cax=cax)
    cbar.set_label(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$', fontsize=12 * vdf_class.vdf_text_scaling)
    cbar.ax.tick_params(labelsize=10 * vdf_class.vdf_text_scaling)
    
    # Add figure title
    epoch_str = epoch[time_index].strftime("%Y-%m-%d %H:%M:%S")
    fig.suptitle(f'PSP SPAN-I VDF - vdyes() Static Plot\n{epoch_str}', y=1.02,
                fontsize=16 * vdf_class.vdf_text_scaling)
    
    print_manager.status(f"✅ vdyes() static plot complete! Plot created for {epoch[time_index]}")
    print_manager.status(f"   🎯 Theta bounds: X={theta_xlim}, Y={theta_ylim}")  
    print_manager.status(f"   🎯 Phi bounds: X={phi_xlim}, Y={phi_ylim}")
    
    return fig


def _create_vdf_widget(dat, available_times, available_indices, trange):
    """Create interactive VDF widget with time slider based on Hopf explorer patterns."""
    from .print_manager import print_manager
    from .data_classes.psp_span_vdf import psp_span_vdf
    
    # Check if running in Jupyter environment
    try:
        from IPython.display import display
        import ipywidgets as widgets
        from ipywidgets import IntSlider, Button, HBox, VBox, Output, Layout, Label
    except ImportError:
        print_manager.error("❌ Widget mode requires Jupyter environment with ipywidgets")
        print_manager.status("📈 Falling back to static plot with first time point...")
        return _create_static_vdf_plot(dat, available_indices[0], available_times)
    
    print_manager.status(f"🎛️ Creating VDF widget with {len(available_times)} time points...")
    
    # Import VDF processing functions
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests'))
    from test_VDF_smart_bounds_debug import (
        extract_and_process_vdf_timeslice_EXACT,
        jaye_exact_theta_plane_processing, 
        jaye_exact_phi_plane_processing
    )
    
    # Create output widget for plots - remove all default styling
    vdf_output = widgets.Output()
    
    # Time slider without description (we'll add our own label)
    # Start at index 1 instead of 0 for better user experience
    time_slider = IntSlider(
        value=min(1, len(available_times) - 1),  # Start at 1 if possible, else 0
        min=0,
        max=len(available_times) - 1,
        step=1,
        description='',  # No built-in description
        layout=Layout(width='400px')
    )
    
    # Labels with consistent width for alignment
    time_label_desc = Label(value="Time:", layout=Layout(width='50px'))
    initial_time_index = min(1, len(available_times) - 1)
    time_display = Label(value=available_times[initial_time_index].strftime("%Y-%m-%d %H:%M:%S"), layout=Layout(width='200px'))
    
    # Step controls with matching width
    step_label_desc = Label(value="Step:", layout=Layout(width='50px'))
    left_arrow_button = Button(description="◀", button_style="", layout=Layout(width='40px'))
    right_arrow_button = Button(description="▶", button_style="", layout=Layout(width='40px'))
    
    # Status label for messages (with bold "Status" text using widget styling)
    status_label = Label(value="Status: Ready", layout=Layout(width='900px', margin='5px'))
    status_label.style.font_weight = 'bold'
    
    # Save buttons (like Hopf explorer save infrastructure) - wider buttons for better usability
    save_current_button = Button(description="Save Current Image", button_style="success", layout=Layout(width='180px'))
    save_all_button = Button(description="Render All Images", button_style="info", layout=Layout(width='180px'))
    set_directory_button = Button(description="Change Save Directory", button_style="primary", layout=Layout(width='200px'))
    
    # Global variables for save directory
    save_directory = [None]  # Use list to make it mutable in nested functions
    
    def setup_default_save_directory():
        """Set up default save directory with vdf_plots subfolder"""
        if save_directory[0] is None:
            # Create vdf_plots subfolder in current directory
            default_dir = os.path.join(os.getcwd(), 'vdf_plots')
            os.makedirs(default_dir, exist_ok=True)  # Create if doesn't exist
            save_directory[0] = default_dir
            status_label.value = f"Status: 📁 Created VDF plots folder: {save_directory[0]} (images will save here)"
    
    def update_vdf_plot(time_index):
        """Update VDF plot for given time index"""
        with vdf_output:
            vdf_output.clear_output(wait=True)
            
            # Process VDF data
            vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, available_indices[time_index])
            vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
            vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
            
            # Use global VDF instance (Plotbot pattern)
            vdf_class = psp_span_vdf
            theta_xlim, theta_ylim = vdf_class.get_axis_limits('theta', vx_theta, vz_theta, df_theta)
            phi_xlim, phi_ylim = vdf_class.get_axis_limits('phi', vx_phi, vy_phi, df_phi)
            
            # Create 3-panel plot with explicit white backgrounds
            fig = plt.figure(figsize=(vdf_class.vdf_figure_width, vdf_class.vdf_figure_height), facecolor='white')
            fig.patch.set_facecolor('white')  # Ensure figure background is white
            gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 0.05], wspace=0.4)
            
            ax1 = fig.add_subplot(gs[0], facecolor='white')  # 1D line plot
            ax2 = fig.add_subplot(gs[1], facecolor='white')  # θ-plane
            ax3 = fig.add_subplot(gs[2], facecolor='white')  # φ-plane
            cax = fig.add_subplot(gs[3], facecolor='white')  # colorbar
            
            # 1D collapsed VDF (left panel)
            vdf_allAngles = np.sum(vdf_data['vdf'], axis=(0,2))
            vel_1d = vdf_data['vel'][0,:,0]
            ax1.plot(vel_1d, vdf_allAngles, 'b-', linewidth=2)
            ax1.set_yscale('log')
            ax1.set_xlim(0, 1000)
            ax1.set_xlabel('Velocity (km/s)', fontsize=12 * vdf_class.vdf_text_scaling)
            ax1.set_ylabel(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$', fontsize=12 * vdf_class.vdf_text_scaling)
            ax1.tick_params(axis='both', labelsize=10 * vdf_class.vdf_text_scaling)
            
            # 2D Theta plane (middle panel)
            cs2 = ax2.contourf(vx_theta, vz_theta, df_theta, 
                              locator=ticker.LogLocator(), cmap=vdf_class.vdf_colormap)
            ax2.set_xlim(theta_xlim)
            ax2.set_ylim(theta_ylim)
            ax2.set_xlabel('$v_x$ km/s', fontsize=12 * vdf_class.vdf_text_scaling)
            ax2.set_ylabel('$v_z$ km/s', fontsize=12 * vdf_class.vdf_text_scaling)
            ax2.set_title('$\\theta$-plane', fontsize=14 * vdf_class.vdf_text_scaling)
            ax2.tick_params(axis='both', labelsize=10 * vdf_class.vdf_text_scaling)
            
            # 2D Phi plane (right panel)
            cs3 = ax3.contourf(vx_phi, vy_phi, df_phi,
                              locator=ticker.LogLocator(), cmap=vdf_class.vdf_colormap)
            ax3.set_xlim(phi_xlim)
            ax3.set_ylim(phi_ylim)
            ax3.set_xlabel('$v_x$ km/s', fontsize=12 * vdf_class.vdf_text_scaling)
            ax3.set_ylabel('$v_y$ km/s', fontsize=12 * vdf_class.vdf_text_scaling)
            ax3.set_title('$\\phi$-plane', fontsize=14 * vdf_class.vdf_text_scaling)
            ax3.tick_params(axis='both', labelsize=10 * vdf_class.vdf_text_scaling)
            
            # Colorbar
            cbar = fig.colorbar(cs2, cax=cax)
            cbar.set_label(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$', fontsize=12 * vdf_class.vdf_text_scaling)
            cbar.ax.tick_params(labelsize=10 * vdf_class.vdf_text_scaling)
            
            # Title with time
            time_str = available_times[time_index].strftime("%Y-%m-%d %H:%M:%S")
            fig.suptitle(f'PSP SPAN-I VDF Widget - {time_str}', y=1.02, fontsize=16 * vdf_class.vdf_text_scaling)
            
            # Display the specific figure object instead of plt.show()
            display(fig)
            plt.close(fig)  # Clean up to prevent memory leaks
            
            # Update time label
            time_display.value = time_str
    
    def on_time_slider_change(change):
        """Handle time slider changes"""
        time_str = available_times[change['new']].strftime("%Y-%m-%d %H:%M:%S")
        status_label.value = f"Status: Displaying time {time_str}"
        update_vdf_plot(change['new'])
    
    def on_left_arrow_click(b):
        """Handle left arrow click - go to previous time step"""
        current_index = time_slider.value
        if current_index > 0:
            time_slider.value = current_index - 1
            # The slider observer will handle the plot update
        else:
            status_label.value = "Status: Already at first time step"
    
    def on_right_arrow_click(b):
        """Handle right arrow click - go to next time step"""
        current_index = time_slider.value
        if current_index < len(available_times) - 1:
            time_slider.value = current_index + 1
            # The slider observer will handle the plot update
        else:
            status_label.value = "Status: Already at last time step"
    
    def on_save_current_click(b):
        """Save current image"""
        setup_default_save_directory()
        
        # Save current plot with human-readable filename
        current_time = available_times[time_slider.value]
        filename = f"VDF_{current_time.strftime('%Y-%m-%d_%Hh_%Mm_%Ss')}.png"
        filepath = os.path.join(save_directory[0], filename)
        
        status_label.value = f"Status: 💾 Saving {filename}..."
        
        # Create plot and save
        time_index = time_slider.value
        vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, available_indices[time_index])
        vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
        vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
        
        vdf_class = psp_span_vdf
        theta_xlim, theta_ylim = vdf_class.get_theta_square_bounds(vx_theta, vz_theta, df_theta)
        phi_xlim, phi_ylim = vdf_class.get_axis_limits('phi', vx_phi, vy_phi, df_phi)
        
        # Create complete 3-panel plot with explicit white backgrounds
        fig = plt.figure(figsize=(vdf_class.vdf_figure_width, vdf_class.vdf_figure_height), facecolor='white')
        fig.patch.set_facecolor('white')  # Ensure figure background is white
        gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 0.05], wspace=0.4)
        
        ax1 = fig.add_subplot(gs[0], facecolor='white')  # 1D line plot
        ax2 = fig.add_subplot(gs[1], facecolor='white')  # θ-plane
        ax3 = fig.add_subplot(gs[2], facecolor='white')  # φ-plane
        cax = fig.add_subplot(gs[3], facecolor='white')  # colorbar
        
        # 1D collapsed VDF (left panel)
        vdf_allAngles = np.sum(vdf_data['vdf'], axis=(0,2))
        vel_1d = vdf_data['vel'][0,:,0]
        ax1.plot(vel_1d, vdf_allAngles, 'b-', linewidth=2)
        ax1.set_yscale('log')
        ax1.set_xlim(0, 1000)
        ax1.set_xlabel('Velocity (km/s)', fontsize=12 * vdf_class.vdf_text_scaling)
        ax1.set_ylabel(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$', fontsize=12 * vdf_class.vdf_text_scaling)
        ax1.tick_params(axis='both', labelsize=10 * vdf_class.vdf_text_scaling)
        
        # 2D Theta plane (middle panel)
        cs2 = ax2.contourf(vx_theta, vz_theta, df_theta, 
                          locator=ticker.LogLocator(), cmap=vdf_class.vdf_colormap)
        ax2.set_xlim(theta_xlim)
        ax2.set_ylim(theta_ylim)
        ax2.set_xlabel('$v_x$ km/s', fontsize=12 * vdf_class.vdf_text_scaling)
        ax2.set_ylabel('$v_z$ km/s', fontsize=12 * vdf_class.vdf_text_scaling)
        ax2.set_title('$\\theta$-plane', fontsize=14 * vdf_class.vdf_text_scaling)
        ax2.tick_params(axis='both', labelsize=10 * vdf_class.vdf_text_scaling)
        
        # 2D Phi plane (right panel)
        cs3 = ax3.contourf(vx_phi, vy_phi, df_phi,
                          locator=ticker.LogLocator(), cmap=vdf_class.vdf_colormap)
        ax3.set_xlim(phi_xlim)
        ax3.set_ylim(phi_ylim)
        ax3.set_xlabel('$v_x$ km/s', fontsize=12 * vdf_class.vdf_text_scaling)
        ax3.set_ylabel('$v_y$ km/s', fontsize=12 * vdf_class.vdf_text_scaling)
        ax3.set_title('$\\phi$-plane', fontsize=14 * vdf_class.vdf_text_scaling)
        ax3.tick_params(axis='both', labelsize=10 * vdf_class.vdf_text_scaling)
        
        # Colorbar
        cbar = fig.colorbar(cs2, cax=cax)
        cbar.set_label(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$', fontsize=12 * vdf_class.vdf_text_scaling)
        cbar.ax.tick_params(labelsize=10 * vdf_class.vdf_text_scaling)
        
        # Title with time
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        fig.suptitle(f'PSP SPAN-I VDF - {time_str}', y=1.02, fontsize=16 * vdf_class.vdf_text_scaling)
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        status_label.value = f"Status: ✅ Complete! Saved to {filepath}"
    
    def on_save_all_click(b):
        """Render and save all time slices"""
        setup_default_save_directory()
        status_label.value = f"Status: 🎬 Rendering {len(available_times)} VDF images..."
        for i, time_obj in enumerate(available_times):
            filename = f"VDF_{time_obj.strftime('%Y-%m-%d_%Hh_%Mm_%Ss')}.png"
            filepath = os.path.join(save_directory[0], filename)
            
            status_label.value = f"Status: 🎬 Saving {filepath} ({i+1}/{len(available_times)})"
            
            # Process and save each time slice
            vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, available_indices[i])
            vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
            vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
            
            vdf_class = psp_span_vdf
            theta_xlim, theta_ylim = vdf_class.get_theta_square_bounds(vx_theta, vz_theta, df_theta)
            phi_xlim, phi_ylim = vdf_class.get_axis_limits('phi', vx_phi, vy_phi, df_phi)
            
            # Create complete 3-panel plot for each time slice with explicit white backgrounds
            fig = plt.figure(figsize=(vdf_class.vdf_figure_width, vdf_class.vdf_figure_height), facecolor='white')
            fig.patch.set_facecolor('white')  # Ensure figure background is white
            gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 0.05], wspace=0.4)
            
            ax1 = fig.add_subplot(gs[0], facecolor='white')  # 1D line plot
            ax2 = fig.add_subplot(gs[1], facecolor='white')  # θ-plane
            ax3 = fig.add_subplot(gs[2], facecolor='white')  # φ-plane
            cax = fig.add_subplot(gs[3], facecolor='white')  # colorbar
            
            # 1D collapsed VDF (left panel)
            vdf_allAngles = np.sum(vdf_data['vdf'], axis=(0,2))
            vel_1d = vdf_data['vel'][0,:,0]
            ax1.plot(vel_1d, vdf_allAngles, 'b-', linewidth=2)
            ax1.set_yscale('log')
            ax1.set_xlim(0, 1000)
            ax1.set_xlabel('Velocity (km/s)')
            ax1.set_ylabel(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$')
            
            # 2D Theta plane (middle panel)
            cs2 = ax2.contourf(vx_theta, vz_theta, df_theta, 
                              locator=ticker.LogLocator(), cmap=vdf_class.vdf_colormap)
            ax2.set_xlim(theta_xlim)
            ax2.set_ylim(theta_ylim)
            ax2.set_xlabel('$v_x$ km/s')
            ax2.set_ylabel('$v_z$ km/s')
            ax2.set_title('$\\theta$-plane')
            
            # 2D Phi plane (right panel)
            cs3 = ax3.contourf(vx_phi, vy_phi, df_phi,
                              locator=ticker.LogLocator(), cmap=vdf_class.vdf_colormap)
            ax3.set_xlim(phi_xlim)
            ax3.set_ylim(phi_ylim)
            ax3.set_xlabel('$v_x$ km/s')
            ax3.set_ylabel('$v_y$ km/s')
            ax3.set_title('$\\phi$-plane')
            
            # Colorbar
            cbar = fig.colorbar(cs2, cax=cax)
            cbar.set_label(f'f $(cm^2 \\ s \\ sr \\ eV)^{-1}$')
            
            # Title with time
            time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
            fig.suptitle(f'PSP SPAN-I VDF - {time_str}', y=1.02, fontsize=14)
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            if (i + 1) % 10 == 0:
                status_label.value = f"Status: 🎬 Progress: {i + 1}/{len(available_times)} images saved"
        
        status_label.value = f"Status: ✅ Complete! All {len(available_times)} images saved to {save_directory[0]}"
    
    def on_set_directory_click(b):
        """Set save directory (emulating audifier pattern)"""
        from tkinter import Tk, filedialog
        
        status_label.value = "Status: 📁 Opening save directory dialog... Look for a 'Python' app in your dock/taskbar!"
        
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        try:
            selected_dir = filedialog.askdirectory(title="Select VDF Save Directory")
            
            if selected_dir:
                save_directory[0] = selected_dir
                status_label.value = f"Status: ✅ Save directory set: {selected_dir}"
            else:
                status_label.value = "Status: ❌ No directory selected"
                
        finally:
            root.quit()  # Stop the mainloop
            root.destroy()
    
    # Connect save button handlers (these don't auto-fire)
    save_current_button.on_click(on_save_current_click)
    save_all_button.on_click(on_save_all_click)
    set_directory_button.on_click(on_set_directory_click)
    
    # Connect step arrow button handlers
    left_arrow_button.on_click(on_left_arrow_click)
    right_arrow_button.on_click(on_right_arrow_click)
    
    # Debug: Confirm button connections
    print("🔗 Button handlers connected successfully")
    
    # Connect slider observer immediately (like Hopf explorer)
    time_slider.observe(on_time_slider_change, names='value')
    
    # Create widget layout with proper alignment using consistent column widths
    time_controls = HBox([time_label_desc, time_slider, time_display], layout=Layout(justify_content="flex-start", margin='5px'))
    step_controls = HBox([step_label_desc, left_arrow_button, right_arrow_button], layout=Layout(justify_content="flex-start", margin='5px'))
    save_controls = HBox([set_directory_button, save_current_button, save_all_button], layout=Layout(justify_content="flex-start", margin='5px'))
    
    widget_layout = VBox([
        time_controls,
        step_controls,
        save_controls,
        status_label,
        vdf_output
    ], layout=Layout(padding='0px'))
    
    # Note: Widget will auto-display when returned (Jupyter behavior)
    # Removed explicit display() call to prevent duplicate UI
    
    # Make initial plot call for the starting slider position
    initial_index = min(1, len(available_times) - 1)
    update_vdf_plot(initial_index)
    
    print_manager.status(f"✅ VDF widget created! {len(available_times)} time points available")
    print_manager.status(f"   Time range: {available_times[0]} to {available_times[-1]}")
    print_manager.status(f"   💾 Save location: Will create './vdf_plots/' - Click 'Change Save Directory' button above to choose different folder")
    
    return widget_layout


def _create_composite_vdf_plotbot_plot(trange, variables):
    """Create composite plot with VDF on top and plotbot time series below."""
    from .print_manager import print_manager
    from .data_classes.psp_span_vdf import psp_span_vdf
    from .ploptions import ploptions
    
    print_manager.status("🎨 Creating composite VDF + plotbot plot...")
    
    # First, create VDF plot (force static mode for composite)
    print_manager.status("📊 Step 1: Creating VDF plot...")
    vdf_fig = vdyes(trange, force_static=True)  # Recursive call without variables
    
    # Configure ploptions to get plotbot figure without displaying
    original_display = ploptions.display_figure
    original_return = ploptions.return_figure
    
    ploptions.display_figure = False  # Don't show plotbot plot
    ploptions.return_figure = True    # Do return the figure
    
    try:
        # Import plotbot here to avoid circular imports
        from .plotbot_main import plotbot
        
        print_manager.status("📈 Step 2: Creating plotbot time series...")
        
        # Create plotbot plot - pass all variables as separate arguments with axis numbers
        if len(variables) == 1:
            # Single variable
            plotbot_fig = plotbot(trange, variables[0], 1)
        else:
            # Multiple variables - use old syntax with axis numbers
            args = [trange]
            for i, var in enumerate(variables):
                args.extend([var, i+1])  # var1 -> axis 1, var2 -> axis 2, etc.
            plotbot_fig = plotbot(*args)
            
    finally:
        # Restore original ploptions
        ploptions.display_figure = original_display
        ploptions.return_figure = original_return
    
    print_manager.status("🔗 Step 3: Combining VDF and plotbot plots...")
    
    # Use image buffer approach to combine figures (avoids matplotlib artist issues)
    import io
    import matplotlib.pyplot as plt
    
    # Just glue the images together - no fancy subplot nonsense
    import numpy as np
    
    # Render both figures to image arrays
    buf1 = io.BytesIO()
    vdf_fig.savefig(buf1, format='png', dpi=150, bbox_inches='tight')
    buf1.seek(0)
    img1 = plt.imread(buf1)
    buf1.close()
    
    buf2 = io.BytesIO()
    plotbot_fig.savefig(buf2, format='png', dpi=150, bbox_inches='tight')
    buf2.seek(0)
    img2 = plt.imread(buf2)
    buf2.close()
    
    # Fixed scaling approach - VDF at 100%, plotbot scales to match VDF width
    vdf_scale_factor = 1  # VDF at 100% of original size
    
    from PIL import Image
    
    # Scale images proportionally 
    def resize_proportionally(img, target_width):
        pil_img = Image.fromarray((img * 255).astype(np.uint8))
        original_width, original_height = pil_img.size
        
        # Calculate new height to preserve aspect ratio
        scale_factor = target_width / original_width
        new_height = int(original_height * scale_factor)
        
        # Resize with proper aspect ratio
        pil_img = pil_img.resize((target_width, new_height), Image.Resampling.LANCZOS)
        return np.array(pil_img) / 255.0
    
    # VDF gets scaled to 90% of its original size
    vdf_target_width = int(img1.shape[1] * vdf_scale_factor)
    img1_final = resize_proportionally(img1, vdf_target_width)
    
    # Plotbot gets scaled to match VDF's new width
    img2_final = resize_proportionally(img2, vdf_target_width)
    
    # Now concatenate images vertically (VDF on top, plotbot below)
    combined_img = np.vstack([img1_final, img2_final])
    
    # Create simple figure to display concatenated image
    composite_fig, ax = plt.subplots(figsize=(12, 10))
    ax.imshow(combined_img)
    ax.axis('off')
    composite_fig.tight_layout(pad=0)
    
    # Clean up individual figures
    plt.close(vdf_fig)
    plt.close(plotbot_fig)
    
    print_manager.status("✅ Composite plot complete!")
    
    return composite_fig
