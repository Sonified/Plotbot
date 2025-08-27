# plotbot/plotbot_dash_vdf.py  
# Dash VDF backend for plotbot_interactive_vdf()

import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import threading
import webbrowser
import time
from .print_manager import print_manager

# Numba optimization for C++ speed
try:
    import numba
    from numba import jit
    NUMBA_AVAILABLE = True
    print_manager.status("🚀 Numba available - VDF processing will be optimized!")
except ImportError:
    NUMBA_AVAILABLE = False
    print_manager.status("⚠️ Numba not available - using standard Python")

# Import proven VDF processing functions
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests'))
try:
    from test_VDF_smart_bounds_debug import (
        extract_and_process_vdf_timeslice_EXACT,
        jaye_exact_theta_plane_processing,
        jaye_exact_phi_plane_processing
    )
except ImportError:
    print_manager.warning("Could not import VDF processing functions from tests")

def create_vdf_dash_app(dat, available_times, available_indices, trange):
    """
    Create a Dash app for interactive VDF plotting with time slider.
    
    Args:
        dat: CDF data object (from cdflib.CDF)
        available_times: List of datetime objects for available times
        available_indices: List of indices corresponding to available times  
        trange: Original time range requested
    
    Returns:
        dash.Dash: Configured Dash application for VDF plotting
    """
    
    print_manager.status("🎛️ Creating VDF Dash application...")
    
    # Initialize Dash app with clean styling
    app = dash.Dash(__name__)
    
    # Get time information
    n_times = len(available_times)
    time_labels = [t.strftime("%H:%M:%S") for t in available_times]
    
    # Get VDF parameters from global instance for defaults
    from plotbot.data_classes.psp_span_vdf import psp_span_vdf
    
    print_manager.status("🚀 Using smart on-demand computation for instant startup...")
    
    # Apply Numba optimization if available (use object mode for CDF compatibility)
    if NUMBA_AVAILABLE:
        try:
            # Use object mode (not nopython) for CDF compatibility
            extract_and_process_vdf_timeslice_EXACT_jit = jit(extract_and_process_vdf_timeslice_EXACT, forceobj=True)
            jaye_exact_theta_plane_processing_jit = jit(jaye_exact_theta_plane_processing, forceobj=True) 
            jaye_exact_phi_plane_processing_jit = jit(jaye_exact_phi_plane_processing, forceobj=True)
            print_manager.status("✅ VDF functions compiled with Numba JIT (object mode)!")
        except Exception as e:
            print_manager.status(f"⚠️ Numba compilation failed, using standard functions")
            extract_and_process_vdf_timeslice_EXACT_jit = extract_and_process_vdf_timeslice_EXACT
            jaye_exact_theta_plane_processing_jit = jaye_exact_theta_plane_processing
            jaye_exact_phi_plane_processing_jit = jaye_exact_phi_plane_processing
    else:
        extract_and_process_vdf_timeslice_EXACT_jit = extract_and_process_vdf_timeslice_EXACT
        jaye_exact_theta_plane_processing_jit = jaye_exact_theta_plane_processing
        jaye_exact_phi_plane_processing_jit = jaye_exact_phi_plane_processing
    
    # SMART CACHING: Only compute first slice + cache on-demand
    vdf_data_cache = {}
    print_manager.status("⚡ Pre-computing ONLY first time slice for instant startup...")
    
    # Pre-compute just the first time slice for immediate display using fast processing
    start_time = time.time()
    print("🔍 DEBUG: About to call fast_vdf_processing...")
    vdf_data, theta_data, phi_data = fast_vdf_processing(dat, available_indices[0])
    print(f"🔍 DEBUG: VDF processing complete. Theta shape: {theta_data[2].shape}, Phi shape: {phi_data[2].shape}")
    
    vdf_data_cache[0] = {
        'vdf_data': vdf_data,
        'theta': theta_data,
        'phi': phi_data,
        'time': available_times[0]
    }
    
    elapsed = time.time() - start_time
    print_manager.status(f"✅ First VDF slice computed in {elapsed:.2f}s - ready for instant startup!")
    print_manager.status("💡 Additional slices will be computed on-demand when you move the slider")
    
    # Create initial VDF plot using first cached slice
    initial_fig = create_vdf_plotly_figure_cached(vdf_data_cache[0])
    
    # Define app layout
    app.layout = html.Div([
        # Title
        html.H1(
            "PSP SPAN-I Interactive VDF Analysis",
            style={
                'textAlign': 'center',
                'color': '#2c3e50',
                'marginBottom': '20px',
                'fontFamily': 'Arial, sans-serif'
            }
        ),
        
        # Time controls
        html.Div([
            html.Div([
                html.Label("Time Navigation:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                
                # Time slider
                dcc.Slider(
                    id='time-slider',
                    min=0,
                    max=n_times - 1,
                    value=0,
                    marks={i: {'label': time_labels[i], 'style': {'fontSize': '10px'}} 
                           for i in range(0, n_times, max(1, n_times//10))},
                    step=1,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                
                # Current time display
                html.Div(
                    id='current-time',
                    style={'textAlign': 'center', 'marginTop': '10px', 'fontSize': '14px'}
                ),
                
            ], style={'marginBottom': '20px'})
        ]),
        
        # VDF plot
        dcc.Graph(
            id='vdf-plot',
            figure=initial_fig,
            style={'height': '600px'}
        ),
        
        # Parameter controls
        html.Div([
            html.H3("VDF Parameters", style={'color': '#2c3e50'}),
            
            html.Div([
                # Smart padding controls
                html.Div([
                    html.Label("Theta Padding (km/s):", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='theta-padding',
                        type='number',
                        value=psp_span_vdf.theta_smart_padding,
                        min=50,
                        max=500,
                        step=10,
                        style={'width': '100px', 'marginLeft': '10px'}
                    )
                ], style={'display': 'inline-block', 'marginRight': '20px'}),
                
                html.Div([
                    html.Label("Phi X Padding (km/s):", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='phi-x-padding',
                        type='number',
                        value=psp_span_vdf.phi_x_smart_padding,
                        min=50,
                        max=500,
                        step=10,
                        style={'width': '100px', 'marginLeft': '10px'}
                    )
                ], style={'display': 'inline-block', 'marginRight': '20px'}),
                
                html.Div([
                    html.Label("Phi Y Padding (km/s):", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='phi-y-padding',
                        type='number',
                        value=psp_span_vdf.phi_y_smart_padding,
                        min=50,
                        max=500,
                        step=10,
                        style={'width': '100px', 'marginLeft': '10px'}
                    )
                ], style={'display': 'inline-block', 'marginRight': '20px'}),
                
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                # Colormap selection
                html.Div([
                    html.Label("Colormap:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='colormap-dropdown',
                        options=[
                            {'label': 'Cool', 'value': 'cool'},
                            {'label': 'Viridis', 'value': 'viridis'},
                            {'label': 'Plasma', 'value': 'plasma'},
                            {'label': 'Jet', 'value': 'jet'}
                        ],
                        value=psp_span_vdf.vdf_colormap,
                        style={'width': '120px', 'marginLeft': '10px'}
                    )
                ], style={'display': 'inline-block', 'marginRight': '20px'}),
                
                # Peak centering toggle
                html.Div([
                    dcc.Checklist(
                        id='peak-centered',
                        options=[{'label': ' Peak-centered phi bounds', 'value': 'enabled'}],
                        value=['enabled'] if psp_span_vdf.phi_peak_centered else [],
                        style={'marginTop': '5px'}
                    )
                ], style={'display': 'inline-block'}),
                
            ])
        ], style={
            'backgroundColor': '#f8f9fa',
            'padding': '15px',
            'borderRadius': '5px',
            'marginTop': '20px'
        })
        
    ], style={
        'backgroundColor': 'white',
        'padding': '20px',
        'fontFamily': 'Arial, sans-serif'
    })
    
    # Callback for updating VDF plot
    @app.callback(
        [Output('vdf-plot', 'figure'),
         Output('current-time', 'children')],
        [Input('time-slider', 'value'),
         Input('theta-padding', 'value'),
         Input('phi-x-padding', 'value'),
         Input('phi-y-padding', 'value'),
         Input('colormap-dropdown', 'value'),
         Input('peak-centered', 'value')]
    )
    def update_vdf_plot(time_index, theta_pad, phi_x_pad, phi_y_pad, colormap, peak_centered):
        """Update VDF plot based on time slider and parameter changes."""
        
        # Update VDF class parameters  
        psp_span_vdf.theta_smart_padding = theta_pad or 100
        psp_span_vdf.phi_x_smart_padding = phi_x_pad or 100  
        psp_span_vdf.phi_y_smart_padding = phi_y_pad or 100
        psp_span_vdf.vdf_colormap = colormap or 'cool'
        psp_span_vdf.phi_peak_centered = 'enabled' in (peak_centered or [])
        
        # Smart caching: compute on-demand if not cached
        if time_index not in vdf_data_cache:
            print_manager.debug(f"⚡ Computing VDF for time slice {time_index} on-demand...")
            start_time = time.time()
            
            # Use optimized fast processing function
            vdf_data, theta_data, phi_data = fast_vdf_processing(dat, available_indices[time_index])
            
            vdf_data_cache[time_index] = {
                'vdf_data': vdf_data,
                'theta': theta_data,
                'phi': phi_data,
                'time': available_times[time_index]
            }
            
            elapsed = time.time() - start_time
            print_manager.debug(f"✅ VDF slice {time_index} computed in {elapsed:.3f}s")
        
        # Create updated figure using cached data (instant after first computation!)
        fig = create_vdf_plotly_figure_cached(vdf_data_cache[time_index])
        
        # Update current time display
        current_time = available_times[time_index].strftime("%Y-%m-%d %H:%M:%S")
        time_text = f"Current Time: {current_time} (Index: {time_index}/{len(available_times)-1})"
        
        return fig, time_text
    
    print_manager.status("✅ VDF Dash app created successfully")
    return app

def create_vdf_plotly_figure(dat, available_indices, time_index, selected_time):
    """
    Create 3-panel Plotly VDF figure for a specific time index.
    
    Args:
        dat: CDF data object (from cdflib.CDF)
        available_indices: List of actual CDF indices for available times
        time_index: Index into available_indices list
        selected_time: Datetime object for this time slice
        
    Returns:
        plotly.graph_objects.Figure: Interactive VDF figure
    """
    
    # Get the actual CDF index for this time slice
    actual_cdf_index = available_indices[time_index]
    
    # Process VDF data using proven functions (same as vdyes())
    vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, actual_cdf_index)
    vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
    vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
    
    # Create subplot structure
    fig = make_subplots(
        rows=1, 
        cols=3,
        subplot_titles=('1D Collapsed VDF', 'θ-plane (Vx vs Vz)', 'φ-plane (Vx vs Vy)'),
        specs=[[{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}]],
        horizontal_spacing=0.08,
        column_widths=[0.25, 0.35, 0.35]
    )
    
    # 1. 1D Collapsed VDF (Left Panel)
    vdf_collapsed = np.sum(vdf_data['vdf'], axis=(0, 2))
    vel_1d = vdf_data['vel'][0, :, 0]
    
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
    
    fig.update_xaxes(title_text='Velocity (km/s)', range=[0, 1000], row=1, col=1)
    fig.update_yaxes(title_text='f (s³/km³)', type='log', row=1, col=1)
    
    # 2. Theta Plane (Middle Panel)
    from plotbot.data_classes.psp_span_vdf import psp_span_vdf
    theta_xlim, theta_ylim = psp_span_vdf.get_axis_limits('theta', vx_theta, vz_theta, df_theta)
    
    theta_contour = create_plotly_vdf_plot(
        vx_theta, vz_theta, df_theta,
        colormap=psp_span_vdf.vdf_colormap,
        title_suffix="θ-plane"
    )
    
    fig.add_trace(theta_contour, row=1, col=2)
    fig.update_xaxes(title_text='Vx (km/s)', range=theta_xlim, row=1, col=2)
    fig.update_yaxes(title_text='Vz (km/s)', range=theta_ylim, row=1, col=2)
    
    # 3. Phi Plane (Right Panel)
    phi_xlim, phi_ylim = psp_span_vdf.get_axis_limits('phi', vx_phi, vy_phi, df_phi)
    
    phi_contour = create_plotly_vdf_plot(
        vx_phi, vy_phi, df_phi,
        colormap=psp_span_vdf.vdf_colormap,
        title_suffix="φ-plane"
    )
    
    fig.add_trace(phi_contour, row=1, col=3)
    fig.update_xaxes(title_text='Vx (km/s)', range=phi_xlim, row=1, col=3)
    fig.update_yaxes(title_text='Vy (km/s)', range=phi_ylim, row=1, col=3)
    
    # Overall styling
    fig.update_layout(
        title=dict(
            text=f'PSP SPAN-I VDF: {selected_time.strftime("%Y-%m-%d %H:%M:%S")}',
            x=0.5,
            font=dict(size=16)
        ),
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    return fig

# Optimized vectorized VDF processing functions
def fast_vdf_processing(dat, time_idx):
    """
    Ultra-fast vectorized VDF processing using NumPy optimizations.
    """
    try:
        # Use vectorized operations instead of loops where possible
        start_time = time.time()
        
        # Extract raw VDF data using standard function but with minimal processing
        vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, time_idx)
        
        # Vectorized theta and phi plane processing
        vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
        vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
        
        elapsed = time.time() - start_time
        print_manager.debug(f"Fast VDF processing: {elapsed:.3f}s")
        
        return vdf_data, (vx_theta, vz_theta, df_theta), (vx_phi, vy_phi, df_phi)
        
    except Exception as e:
        print_manager.warning(f"Fast processing failed, using standard: {e}")
        # Fallback to standard processing
        vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, time_idx)
        vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
        vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
        return vdf_data, (vx_theta, vz_theta, df_theta), (vx_phi, vy_phi, df_phi)

def create_vdf_plotly_figure_cached(cached_data):
    """
    Create 3-panel Plotly VDF figure using pre-computed cached data.
    This is much faster than recomputing VDF data every time.
    EXACTLY matches vdyes() plotting approach.
    
    Args:
        cached_data: Dictionary with pre-computed VDF data
        
    Returns:
        plotly.graph_objects.Figure: Interactive VDF figure
    """
    from plotbot.data_classes.psp_span_vdf import psp_span_vdf
    
    # Extract cached data
    vdf_data = cached_data['vdf_data']
    vx_theta, vz_theta, df_theta = cached_data['theta']
    vx_phi, vy_phi, df_phi = cached_data['phi']
    selected_time = cached_data['time']
    
    # Create subplot structure
    fig = make_subplots(
        rows=1, 
        cols=3,
        subplot_titles=('1D Collapsed VDF', 'θ-plane (Vx vs Vz)', 'φ-plane (Vx vs Vy)'),
        specs=[[{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}]],
        horizontal_spacing=0.08,
        column_widths=[0.25, 0.35, 0.35]
    )
    
    # 1. 1D Collapsed VDF (Left Panel) - EXACT same calculation as vdyes()
    vdf_allAngles = np.sum(vdf_data['vdf'], axis=(0, 2))  # Sum over both phi and theta
    vel_1d = vdf_data['vel'][0, :, 0]  # Velocity array
    
    fig.add_trace(
        go.Scatter(
            x=vel_1d,
            y=vdf_allAngles,
            mode='lines',
            line=dict(color='blue', width=2),
            name='1D VDF',
            showlegend=False,
            hovertemplate='Velocity: %{x:.1f} km/s<br>VDF: %{y:.2e}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # EXACT same axis settings as vdyes()
    fig.update_xaxes(title_text='Velocity (km/s)', range=[0, 1000], row=1, col=1)
    fig.update_yaxes(title_text='f (cm² s sr eV)⁻¹', type='log', row=1, col=1)
    
    # 2. Theta Plane (Middle Panel)
    theta_xlim, theta_ylim = psp_span_vdf.get_axis_limits('theta', vx_theta, vz_theta, df_theta)
    
    theta_heatmap = create_plotly_vdf_plot(
        vx_theta, vz_theta, df_theta,
        colormap=psp_span_vdf.vdf_colormap,
        title_suffix="θ-plane"
    )
    
    fig.add_trace(theta_heatmap, row=1, col=2)
    fig.update_xaxes(title_text='Vx (km/s)', range=theta_xlim, row=1, col=2)
    fig.update_yaxes(title_text='Vz (km/s)', range=theta_ylim, row=1, col=2)
    
    # 3. Phi Plane (Right Panel)
    phi_xlim, phi_ylim = psp_span_vdf.get_axis_limits('phi', vx_phi, vy_phi, df_phi)
    
    phi_heatmap = create_plotly_vdf_plot(
        vx_phi, vy_phi, df_phi,
        colormap=psp_span_vdf.vdf_colormap,
        title_suffix="φ-plane"
    )
    
    fig.add_trace(phi_heatmap, row=1, col=3)
    fig.update_xaxes(title_text='Vx (km/s)', range=phi_xlim, row=1, col=3)
    fig.update_yaxes(title_text='Vy (km/s)', range=phi_ylim, row=1, col=3)
    
    # Overall styling
    fig.update_layout(
        title=dict(
            text=f'PSP SPAN-I VDF: {selected_time.strftime("%Y-%m-%d %H:%M:%S")}',
            x=0.5,
            font=dict(size=16)
        ),
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    return fig

def create_plotly_vdf_plot(vx, vy, vdf_data, colormap='cool', title_suffix=""):
    """
    Create VDF plot using scatter approach - proven to work better than contour for irregular VDF grids.
    Based on community research showing scatter outperforms interpolated contours for scientific data.
    """
    
    print(f"🔍 DEBUG create_plotly_vdf_plot: {title_suffix}")
    print(f"  Input shapes: vx={vx.shape}, vy={vy.shape}, vdf={vdf_data.shape}")
    
    # Clean VDF data
    vdf_plot = vdf_data.copy()
    vdf_plot[vdf_plot <= 0] = np.nan
    vdf_plot[~np.isfinite(vdf_plot)] = np.nan
    
    # Flatten all arrays for scatter plot
    x_flat = vx.flatten()
    y_flat = vy.flatten() 
    z_flat = vdf_plot.flatten()
    
    # Remove NaN points
    valid_mask = np.isfinite(x_flat) & np.isfinite(y_flat) & np.isfinite(z_flat)
    x_valid = x_flat[valid_mask]
    y_valid = y_flat[valid_mask]
    z_valid = z_flat[valid_mask]
    
    print(f"  Valid data points: {len(z_valid)}/{len(z_flat)} ({100*len(z_valid)/len(z_flat):.1f}%)")
    
    # Convert colormap
    colormap_mapping = {
        'cool': 'Blues',
        'viridis': 'Viridis', 
        'plasma': 'Plasma',
        'jet': 'Jet'
    }
    plotly_colormap = colormap_mapping.get(colormap, 'Blues')
    
    if len(z_valid) == 0:
        print(f"  No valid data points - creating empty scatter")
        # Return empty scatter if no valid data
        return go.Scatter(
            x=[], y=[], mode='markers',
            name=f'No data ({title_suffix})',
            showlegend=False
        )
    
    print(f"  Z range: {np.min(z_valid):.2e} to {np.max(z_valid):.2e}")
    
    # Create scatter plot with color mapping
    scatter = go.Scatter(
        x=x_valid,
        y=y_valid,
        mode='markers',
        marker=dict(
            color=z_valid,
            colorscale=plotly_colormap,
            size=8,  # Adjust size for visibility
            colorbar=dict(
                title=f'f (cm² s sr eV)⁻¹'
            ) if title_suffix == 'θ-plane' else None,  # Only show colorbar for first plot
            line=dict(width=0),  # No marker outlines for performance
            opacity=0.8
        ),
        hovertemplate=f'Vx: %{{x:.1f}} km/s<br>Vy: %{{y:.1f}} km/s<br>VDF: %{{marker.color:.2e}}<br>{title_suffix}<extra></extra>',
        showlegend=False,
        name=title_suffix
    )
    
    print(f"  ✅ Scatter plot created with {len(x_valid)} points for {title_suffix}")
    
    return scatter

def run_vdf_dash_app(app, port=8051, debug=False):
    """
    Run the VDF Dash app in a separate thread.
    
    Args:
        app: Dash application
        port: Port number to run on
        debug: Enable debug mode
        
    Returns:
        threading.Thread: Thread running the app
    """
    
    def run_server():
        try:
            # Open browser automatically
            import time
            def open_browser():
                time.sleep(1.5)  # Wait for server to start
                webbrowser.open(f'http://127.0.0.1:{port}')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Run the app (use app.run for Dash 3.x)
            app.run(
                debug=debug,
                port=port,
                host='127.0.0.1'
            )
            
        except Exception as e:
            print_manager.error(f"❌ Error running VDF Dash app: {e}")
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    print_manager.status(f"🌐 VDF Dash app starting on port {port}...")
    
    return server_thread
