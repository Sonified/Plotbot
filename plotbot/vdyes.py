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
import pyspedas
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

def vdyes(trange, force_static=False):
    """
    VDF plotting - the fine way! (renamed from VDFine)
    Uses Plotbot's class-based parameter system like epad.strahl.colorbar_limits.
    
    Automatically switches between static plot and interactive widget based on available data:
    - Static Mode: Single time point found → 3-panel VDF plot  
    - Widget Mode: Multiple time points found → Interactive time slider with controls
    
    Args:
        trange: Time range for VDF plotting (e.g., ['2020/01/29 00:00:00.000', '2020/01/30 00:00:00.000'])
        force_static: Force static mode even when multiple time points available (default: False)
    
    Returns:
        matplotlib.figure.Figure: The 3-panel VDF plot (static mode)
        ipywidgets.Widget: Interactive VDF widget (widget mode)
        
    Logic:
        1. Download VDF data for the requested trange
        2. Count available time points in the data
        3. If 1 time point → static plot of that time slice
        4. If >1 time points → interactive widget with time slider
        
    Example Usage:
        # Set parameters on the class instance (Plotbot way)
        psp_span_vdf.theta_x_smart_padding = 150
        psp_span_vdf.enable_zero_clipping = False
        psp_span_vdf.theta_x_axis_limits = (-800, 0)  # Use Jaye's bounds
        
        # Single time found → Static plot
        fig = vdyes(['2020/01/29 18:10:00.000', '2020/01/29 18:10:30.000'])
        
        # Multiple times found → Interactive widget  
        widget = vdyes(['2020/01/29 17:00:00.000', '2020/01/29 19:00:00.000'])
    """
    
    from .print_manager import print_manager
    from .data_classes.psp_span_vdf import psp_span_vdf
    
    print_manager.status(f"🚀 vdyes() - Processing trange: {trange}")
    
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
    
    # Download using proven pyspedas approach (exactly like our working tests)
    VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                              notplot=True, time_clip=True, downloadonly=True, get_support_data=True)
    
    if not VDfile:
        raise ValueError(f"No VDF files downloaded for trange: {trange}")
        
    print_manager.status(f"📁 Downloaded: {VDfile[0]}")
    
    # Process data using EXACT working approach
    dat = cdflib.CDF(VDfile[0])
    
    # Get time array to determine mode
    epoch_dt64 = cdflib.cdfepoch.to_datetime(dat.varget('Epoch'))
    epoch = pd.to_datetime(epoch_dt64).to_pydatetime().tolist()
    
    # Filter time points to requested trange
    from dateutil.parser import parse
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
    
    # Time slider (like Hopf explorer time controls)
    time_slider = IntSlider(
        value=0,
        min=0,
        max=len(available_times) - 1,
        step=1,
        description='Time:',
        layout=Layout(width='600px'),
        style={'description_width': '50px'}
    )
    
    # Time display label
    time_label = Label(value=available_times[0].strftime("%Y-%m-%d %H:%M:%S"))
    
    # Status label for messages
    status_label = Label(value="Status: Ready", layout=Layout(width='900px', margin='5px'))
    
    # Save buttons (like Hopf explorer save infrastructure)
    save_current_button = Button(description="Save Current Image", button_style="success", layout=Layout(width='150px'))
    save_all_button = Button(description="Render All Images", button_style="info", layout=Layout(width='150px'))
    set_directory_button = Button(description="Change Save Directory", button_style="primary", layout=Layout(width='150px'))
    
    # Global variables for save directory
    save_directory = [None]  # Use list to make it mutable in nested functions
    
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
            
            plt.show()
            
            # Update time label
            time_label.value = time_str
    
    def on_time_slider_change(change):
        """Handle time slider changes"""
        time_str = available_times[change['new']].strftime("%Y-%m-%d %H:%M:%S")
        status_label.value = f"Status: Displaying time {time_str}"
        update_vdf_plot(change['new'])
    
    def on_save_current_click(b):
        """Save current image"""
        if save_directory[0] is None:
            # Default to current working directory (where Jupyter notebook is running)
            save_directory[0] = os.getcwd()
            status_label.value = f"Status: 📁 Using default save directory: {save_directory[0]}"
        
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
        status_label.value = f"Status: 🎬 Rendering {len(available_times)} VDF images..."
        
        if save_directory[0] is None:
            # Default to current working directory (where Jupyter notebook is running)
            save_directory[0] = os.getcwd()
            status_label.value = f"Status: 📁 Using default save directory: {save_directory[0]}"
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
    
    # Debug: Confirm button connections
    print("🔗 Button handlers connected successfully")
    
    # Connect slider observer immediately (like Hopf explorer)
    time_slider.observe(on_time_slider_change, names='value')
    
    # Create widget layout
    time_controls = HBox([time_slider, time_label], layout=Layout(justify_content="flex-start", margin='5px'))
    save_controls = HBox([set_directory_button, save_current_button, save_all_button], layout=Layout(justify_content="flex-start", margin='5px'))
    
    widget_layout = VBox([
        time_controls,
        save_controls,
        status_label,
        vdf_output
    ], layout=Layout(padding='0px'))
    
    # Auto-display widget in Jupyter (like Hopf explorer)
    try:
        from IPython import get_ipython
        from IPython.display import display
        
        if get_ipython() is not None and hasattr(get_ipython(), 'kernel'):
            display(widget_layout)
    except (ImportError, AttributeError):
        pass
    
    # Make ONE explicit plot call at the very end (Hopf explorer pattern)
    update_vdf_plot(0)
    
    print_manager.status(f"✅ VDF widget created! {len(available_times)} time points available")
    print_manager.status(f"   Time range: {available_times[0]} to {available_times[-1]}")
    print_manager.status(f"   💾 Save location: Current directory ({os.getcwd()}) - Use 'Change Save Directory' to modify")
    
    return widget_layout
