# plotbot/plotbot_dash_vdf.py  
# Dash VDF backend for plotbot_interactive_vdf()

import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import threading
import webbrowser
import time
from scipy.spatial import Delaunay
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

# Try to import VDF processing functions
VDF_FUNCTIONS_AVAILABLE = False

# Define placeholder functions first with proper type hints
def extract_and_process_vdf_timeslice_EXACT(*args, **kwargs):
    """Placeholder function that raises ImportError."""
    if not VDF_FUNCTIONS_AVAILABLE:  # This will always be False initially
        raise ImportError("VDF processing functions not available")
    return {}  # Dummy return to satisfy type checker

def jaye_exact_theta_plane_processing(*args, **kwargs):
    """Placeholder function that raises ImportError."""
    if not VDF_FUNCTIONS_AVAILABLE:
        raise ImportError("VDF processing functions not available")
    return None, None, None  # Dummy return to satisfy type checker
    
def jaye_exact_phi_plane_processing(*args, **kwargs):
    """Placeholder function that raises ImportError."""  
    if not VDF_FUNCTIONS_AVAILABLE:
        raise ImportError("VDF processing functions not available")
    return None, None, None  # Dummy return to satisfy type checker

try:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests'))
    from test_VDF_smart_bounds_debug import (  # type: ignore
        extract_and_process_vdf_timeslice_EXACT,
        jaye_exact_theta_plane_processing,
        jaye_exact_phi_plane_processing
    )
    VDF_FUNCTIONS_AVAILABLE = True
except ImportError:
    print_manager.warning("Could not import VDF processing functions from tests")
    VDF_FUNCTIONS_AVAILABLE = False

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
    print(f"🔍 DEBUG: VDF processing complete. Theta shape: {theta_data[2].shape}, Phi shape: {phi_data[2].shape}")  # type: ignore
    
    vdf_data_cache[0] = {
        'vdf_data': vdf_data,
        'theta': theta_data,
        'phi': phi_data,
        'time': available_times[0]
    }
    
    elapsed = time.time() - start_time
    print_manager.status(f"✅ First VDF slice computed in {elapsed:.2f}s - ready for instant startup!")
    print_manager.status("💡 Additional slices will be computed on-demand when you move the slider")
    
    # Create initial VDF plot using first cached slice with new Mesh3d approach
    initial_fig = create_vdf_plotly_figure_mesh3d(vdf_data_cache[0], 'mesh3d')
    
    # Define app layout
    app.layout = html.Div([
        # Title
        html.H1(
            "PSP SPAN-I Interactive VDF Analysis",
            style={
                'textAlign': 'center',
                'color': '#2c3e50',
                'marginBottom': '10px',
                'fontFamily': 'Arial, sans-serif'
            }
        ),
        
        # Current Implementation Details
        html.Div([
            html.P([
                "NEW: Mesh3d triangulation preserves ALL original PSP particle measurement points! ",
                "Compare with interpolated contours (data loss from regridding) and raw scatter (no structure)."
            ], style={
                'textAlign': 'center', 'margin': '0 0 10px 0', 
                'color': '#34495e', 'fontSize': '13px', 'fontStyle': 'italic'
            }),
            html.P("Visualization Methods Available:", style={
                'textAlign': 'center', 'fontWeight': 'bold', 'margin': '0', 
                'color': '#34495e', 'fontSize': '14px'
            }),
            html.Ul([
                html.Li("⚡ Mesh3d: Delaunay triangulation with original coordinates as vertices (NO data loss!)"),
                html.Li("🔧 Interpolated: Smart gap filling + high-resolution grids (some data loss from regridding)"),
                html.Li("🎯 Scatter: Raw measurement points (all data, but no structure visualization)"),
                html.Li("🕰️ Real-time updates: Time slider explores particle distribution evolution")
            ], style={
                'textAlign': 'left', 'margin': '10px auto', 'maxWidth': '800px',
                'fontSize': '12px', 'color': '#2c3e50', 'lineHeight': '1.4'
            })
        ], style={
            'background': '#e8f4fd', 'border': '1px solid #bee5eb', 
            'borderRadius': '5px', 'padding': '10px', 'margin': '0 20px 20px 20px'
        }),
        
        # Visualization mode toggle
        html.Div([
            html.Label("Visualization Mode:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.RadioItems(
                id='viz-mode-toggle',
                options=[
                    {'label': ' ⚡ Mesh3d Triangulation (preserves ALL data)', 'value': 'mesh3d'},
                    {'label': ' 🔧 Interpolated Contours (regridded)', 'value': 'interpolate'},
                    {'label': ' 🎯 Raw Scatter Points (no structure)', 'value': 'scatter'}
                ],
                value='mesh3d',
                style={'marginBottom': '20px'},
                labelStyle={'marginRight': '15px', 'display': 'inline-block'}
            )
        ], style={
            'textAlign': 'center', 'margin': '0 20px 20px 20px',
            'padding': '10px', 'background': '#f8f9fa', 'borderRadius': '5px'
        }),
        
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
    
    # FIXED CALLBACK with proper error handling and debugging
    @app.callback(
        [Output('vdf-plot', 'figure'),
         Output('current-time', 'children')],
        [Input('time-slider', 'value'),
         Input('viz-mode-toggle', 'value')],
        prevent_initial_call=False
    )
    def update_vdf_plot(time_index, viz_mode):
        """Update VDF plot - FIXED VERSION with extensive debugging."""
        print(f"🔥 CALLBACK FIRED: time_index={time_index}, viz_mode={viz_mode}")  # Simple debug line
        
        try:
            # IMMEDIATE DEBUG - print to console
            print("=" * 50)
            print(f"🔍 CALLBACK TRIGGERED!")
            print(f"🔍 time_index = {time_index} (type: {type(time_index)})")
            print(f"🔍 viz_mode = {viz_mode} (type: {type(viz_mode)})")
            print("=" * 50)
            
            debug_msg = f"🔄 Callback: time_index={time_index}, viz_mode={viz_mode}"
            print_manager.status(debug_msg)
            
            # Validate inputs
            if time_index is None:
                time_index = 0
            if viz_mode is None:
                viz_mode = 'interpolate'
                
            time_index = int(time_index)
            
            # Ensure time_index is in valid range
            if time_index < 0 or time_index >= len(available_times):
                time_index = 0
            
            # Smart caching: compute on-demand if not cached
            if time_index not in vdf_data_cache:
                print_manager.status(f"⚡ Computing VDF for time slice {time_index}...")
                start_time = time.time()
                
                try:
                    vdf_data, theta_data, phi_data = fast_vdf_processing(dat, available_indices[time_index])
                    
                    vdf_data_cache[time_index] = {
                        'vdf_data': vdf_data,
                        'theta': theta_data,
                        'phi': phi_data,
                        'time': available_times[time_index]
                    }
                    
                    elapsed = time.time() - start_time
                    print_manager.status(f"✅ VDF slice {time_index} computed in {elapsed:.3f}s")
                    
                except Exception as e:
                    error_msg = f"❌ Failed to compute VDF slice {time_index}: {e}"
                    print_manager.error(error_msg)
                    print(f"ERROR in VDF processing: {e}")
                    import traceback
                    traceback.print_exc()
                    # Use first cached slice as fallback
                    time_index = 0
            
            # Create updated figure using new Mesh3d approach
            fig = create_vdf_plotly_figure_mesh3d(vdf_data_cache[time_index], viz_mode)
            
            # Update time display
            current_time = available_times[time_index].strftime("%Y-%m-%d %H:%M:%S")
            time_text = f"Current Time: {current_time} (Index: {time_index}/{len(available_times)-1}) Mode: {viz_mode}"
            
            print(f"✅ Callback executed successfully! Time={time_index}, Mode={viz_mode}")
            return fig, time_text
            
        except Exception as e:
            error_msg = f"❌ Callback error: {e}"
            print_manager.error(error_msg)
            print(f"CALLBACK ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error figure
            error_fig = go.Figure()
            error_fig.add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
            
            return error_fig, f"Error: {str(e)}"
    
    print_manager.status("✅ VDF Dash app created successfully")
    return app

def run_vdf_dash_app(app, port=8051, debug=False):
    """
    Run the VDF Dash app in a separate thread - FIXED VERSION.
    """
    import threading
    import webbrowser
    import time
    
    def run_server():
        try:
            print_manager.status(f"🚀 Starting Dash server on port {port}...")
            # Use app.run (run_server is obsolete in newer Dash versions)
            app.run(
                debug=debug,
                port=port,
                host='127.0.0.1',
                use_reloader=False,  # Critical: prevents thread issues
                dev_tools_hot_reload=False  # Prevents callback issues
            )
        except Exception as e:
            print_manager.error(f"❌ Error running VDF Dash server: {e}")
            import traceback
            traceback.print_exc()
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Give server time to start
    time.sleep(2)
    
    # Open browser
    try:
        webbrowser.open(f'http://127.0.0.1:{port}')
        print_manager.status(f"🌐 Opened browser to http://127.0.0.1:{port}")
    except Exception as e:
        print_manager.warning(f"Could not open browser automatically: {e}")
        print_manager.status(f"📌 Manually open: http://127.0.0.1:{port}")
    
    return server_thread

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
    if not VDF_FUNCTIONS_AVAILABLE:
        raise ImportError("VDF processing functions not available - cannot create VDF plot")
    
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

# Optimized vectorized VDF processing functions with debug support
def test_vdf_imports():
    """Test if VDF processing functions can be imported."""
    return VDF_FUNCTIONS_AVAILABLE

def fast_vdf_processing(dat, time_idx):
    """Ultra-fast VDF processing using imported functions."""
    if not VDF_FUNCTIONS_AVAILABLE:
        raise ImportError("VDF processing functions not available")
        
    try:
        # Use pre-imported functions
        start_time = time.time()
        vdf_data = extract_and_process_vdf_timeslice_EXACT(dat, time_idx)
        vx_theta, vz_theta, df_theta = jaye_exact_theta_plane_processing(vdf_data)
        vx_phi, vy_phi, df_phi = jaye_exact_phi_plane_processing(vdf_data)
        
        elapsed = time.time() - start_time
        print(f"VDF processing: {elapsed:.3f}s")
        
        return vdf_data, (vx_theta, vz_theta, df_theta), (vx_phi, vy_phi, df_phi)
        
    except Exception as e:
        print(f"VDF processing failed: {e}")
        raise

def create_vdf_plotly_figure_cached(cached_data, viz_mode='interpolate'):
    """
    Create 3-panel Plotly VDF figure using pre-computed cached data.
    This is much faster than recomputing VDF data every time.
    EXACTLY matches vdyes() plotting approach.
    
    Args:
        cached_data: Dictionary with pre-computed VDF data
        viz_mode: 'interpolate' for contours, 'scatter' for raw points
        
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
        title_suffix="θ-plane",
        viz_mode=viz_mode
    )
    
    fig.add_trace(theta_heatmap, row=1, col=2)
    fig.update_xaxes(title_text='Vx (km/s)', range=theta_xlim, row=1, col=2)
    fig.update_yaxes(title_text='Vz (km/s)', range=theta_ylim, row=1, col=2)
    
    # 3. Phi Plane (Right Panel)
    phi_xlim, phi_ylim = psp_span_vdf.get_axis_limits('phi', vx_phi, vy_phi, df_phi)
    
    phi_heatmap = create_plotly_vdf_plot(
        vx_phi, vy_phi, df_phi,
        colormap=psp_span_vdf.vdf_colormap,
        title_suffix="φ-plane",
        viz_mode=viz_mode
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

def create_plotly_vdf_plot(vx, vy, vdf_data, colormap='cool', title_suffix="", viz_mode='interpolate'):
    """
    Create VDF plot using either contour interpolation or raw scatter points.
    
    Args:
        viz_mode: 'interpolate' for contours (current), 'scatter' for raw points
    """
    
    print(f"🔍 DEBUG create_plotly_vdf_plot: {title_suffix} (Mode: {viz_mode})")
    print(f"  Input shapes: vx={vx.shape}, vy={vy.shape}, vdf={vdf_data.shape}")
    
    # Clean VDF data
    vdf_plot = vdf_data.copy()
    vdf_plot[vdf_plot <= 0] = np.nan
    vdf_plot[~np.isfinite(vdf_plot)] = np.nan
    
    # Convert colormap
    colormap_mapping = {
        'cool': 'Blues',
        'viridis': 'Viridis', 
        'plasma': 'Plasma',
        'jet': 'Jet'
    }
    plotly_colormap = colormap_mapping.get(colormap, 'Blues')
    
    # 🎯 SCATTER MODE: Plot raw data points directly (no interpolation!)
    if viz_mode == 'scatter':
        print(f"  🎯 Using SCATTER mode - plotting raw data points directly")
        
        # Flatten coordinates and VDF data
        x_flat = vx.ravel()
        y_flat = vy.ravel()
        vdf_flat = vdf_plot.ravel()
        
        # Remove invalid data points
        valid_mask = np.isfinite(vdf_flat) & (vdf_flat > 0)
        x_valid = x_flat[valid_mask]
        y_valid = y_flat[valid_mask]
        vdf_valid = vdf_flat[valid_mask]
        
        print(f"    Raw data points: {len(vdf_valid)}/{len(vdf_flat)} valid")
        print(f"    VDF range: {np.min(vdf_valid):.2e} to {np.max(vdf_valid):.2e}")
        
        # Create scatter plot with color mapping
        return go.Scatter(
            x=x_valid,
            y=y_valid,
            mode='markers',
            marker=dict(
                color=vdf_valid,
                colorscale=plotly_colormap,
                size=4,
                opacity=0.8,
                colorbar=dict(title="f (cm² s sr eV)⁻¹"),
                line=dict(width=0)  # No marker outlines for cleaner look
            ),
            name=f'VDF {title_suffix}',
            showlegend=False,
            hovertemplate=f'{title_suffix}<br>Vx: %{{x:.1f}} km/s<br>Vy: %{{y:.1f}} km/s<br>VDF: %{{marker.color:.2e}}<extra></extra>'
        )
    
    # Check if coordinates are uniform (regular grid)
    x_uniform = np.allclose(vx[0, :], vx[-1, :], rtol=1e-3) if vx.ndim == 2 else True
    y_uniform = np.allclose(vy[:, 0], vy[:, -1], rtol=1e-3) if vy.ndim == 2 else True
    
    print(f"  Coordinate uniformity: X={x_uniform}, Y={y_uniform}")
    
    if x_uniform and y_uniform:
        # Regular grid - use coordinates directly
        print(f"  Using regular grid approach")
        x_coords = vx[0, :] if vx.ndim == 2 else vx
        y_coords = vy[:, 0] if vy.ndim == 2 else vy
        z_data = vdf_plot
        
    else:
        # Irregular grid - interpolate to regular grid using research-recommended approach
        print(f"  🔧 Irregular grid detected - interpolating to regular grid")
        
        # Get coordinate ranges
        x_min, x_max = np.nanmin(vx), np.nanmax(vx)
        y_min, y_max = np.nanmin(vy), np.nanmax(vy)
        
        print(f"    X range: {x_min:.1f} to {x_max:.1f} km/s")
        print(f"    Y range: {y_min:.1f} to {y_max:.1f} km/s")
        
        # Research-recommended high resolution for better data preservation
        grid_resolution = 100  # Higher resolution than default 50
        x_coords = np.linspace(x_min, x_max, grid_resolution)
        y_coords = np.linspace(y_min, y_max, grid_resolution)
        
        # Interpolate VDF data onto regular grid
        from scipy.interpolate import griddata
        
        # Flatten the irregular coordinate grids and VDF data
        points = np.column_stack((vx.ravel(), vy.ravel()))
        values = vdf_plot.ravel()
        
        # Remove NaN values
        valid_mask = np.isfinite(values)
        points_valid = points[valid_mask]
        values_valid = values[valid_mask]
        
        print(f"    Valid points for interpolation: {len(values_valid)}/{len(values)}")
        
        if len(values_valid) > 3:  # Need at least 3 points for interpolation
            # Create regular grid
            X_reg, Y_reg = np.meshgrid(x_coords, y_coords)
            
            # Interpolate onto regular grid using research-recommended approach
            # Try 'nearest' first for better data preservation, fallback to 'linear'
            z_data = griddata(points_valid, values_valid, (X_reg, Y_reg), method='nearest', fill_value=np.nan)
            
            # If too sparse, try linear interpolation
            nearest_coverage = np.sum(np.isfinite(z_data)) / z_data.size
            if nearest_coverage < 0.1:  # Less than 10% coverage
                print(f"    Nearest interpolation sparse ({nearest_coverage:.1%}), trying linear...")
                z_data = griddata(points_valid, values_valid, (X_reg, Y_reg), method='linear', fill_value=np.nan)
            print(f"    ✅ Interpolated to {grid_resolution}x{grid_resolution} regular grid")
        else:
            print(f"    ⚠️ Not enough valid points, creating empty contour")
            return go.Contour(x=[], y=[], z=[], colorscale=plotly_colormap, showscale=False)
    
    # Final data validation
    finite_count = np.sum(np.isfinite(z_data))
    total_count = z_data.size
    print(f"  Final data: {finite_count}/{total_count} finite values")
    print(f"  Z range: {np.nanmin(z_data):.2e} to {np.nanmax(z_data):.2e}")
    
    # Create Plotly Contour with proper settings to match matplotlib contourf
    contour = go.Contour(
        x=x_coords,
        y=y_coords, 
        z=z_data,
        colorscale=plotly_colormap,
        showscale=True if title_suffix == 'θ-plane' else False,  # Only show colorbar for first plot
        line=dict(width=0),  # No contour lines, just fills like contourf
        contours_coloring='heatmap',  # Fill contours like matplotlib contourf
        hovertemplate=f'Vx: %{{x:.1f}} km/s<br>Vy: %{{y:.1f}} km/s<br>VDF: %{{z:.2e}}<br>{title_suffix}<extra></extra>',
        connectgaps=True,  # Connect across small gaps
        colorbar=dict(
            title=f'f (cm² s sr eV)⁻¹'
        ) if title_suffix == 'θ-plane' else None
    )
    
    print(f"  ✅ Contour plot created for {title_suffix}")
    
    return contour

def get_plotly_colormap(matplotlib_name):
    """Convert matplotlib colormap names to Plotly equivalents."""
    mapping = {
        'cool': 'blues',
        'viridis': 'viridis', 
        'plasma': 'plasma',
        'jet': 'jet',
        'hot': 'hot'
    }
    return mapping.get(matplotlib_name, 'blues')

def create_plotly_vdf_plot_mesh3d(vx, vy, vdf_data, colormap='cool', title_suffix=""):
    """
    Create VDF plot using Mesh3d - preserves ALL original data points with PROPER grid structure.
    Uses structured grid triangulation instead of destroying the natural VDF grid.
    
    Args:
        vx, vy: Velocity coordinate arrays (regular grid from VDF processing)
        vdf_data: VDF values at each coordinate
        colormap: Colormap name
        title_suffix: Plot title suffix
    
    Returns:
        plotly trace for use in subplots
    """
    
    print(f"Creating FIXED Mesh3d plot for {title_suffix}")
    print(f"  Input shapes: vx={vx.shape}, vy={vy.shape}, vdf={vdf_data.shape}")
    
    # Clean data - remove invalid points
    vdf_clean = vdf_data.copy()
    vdf_clean[vdf_clean <= 0] = np.nan
    vdf_clean[~np.isfinite(vdf_clean)] = np.nan
    
    # Check if we have a regular grid structure
    if vx.ndim == 2 and vy.ndim == 2:
        print(f"  ✅ Regular grid detected: {vx.shape[0]}×{vx.shape[1]} points")
        
        # Use the NATURAL GRID STRUCTURE instead of destroying it with Delaunay
        ny, nx = vx.shape
        
        # Create triangle indices for the regular grid (like matplotlib contourf does internally)
        triangles = []
        x_flat = vx.ravel()
        y_flat = vy.ravel()
        vdf_flat = vdf_clean.ravel()
        
        # Create triangulation based on grid structure (preserves smoothness)
        for i in range(ny - 1):
            for j in range(nx - 1):
                # Each grid cell becomes 2 triangles
                # Lower triangle
                p1 = i * nx + j
                p2 = i * nx + (j + 1)
                p3 = (i + 1) * nx + j
                
                # Upper triangle  
                p4 = i * nx + (j + 1)
                p5 = (i + 1) * nx + (j + 1)
                p6 = (i + 1) * nx + j
                
                # Only add triangles where all points have valid data
                if (np.isfinite(vdf_flat[p1]) and np.isfinite(vdf_flat[p2]) and np.isfinite(vdf_flat[p3])):
                    triangles.append([p1, p2, p3])
                if (np.isfinite(vdf_flat[p4]) and np.isfinite(vdf_flat[p5]) and np.isfinite(vdf_flat[p6])):
                    triangles.append([p4, p5, p6])
        
        triangles = np.array(triangles)
        print(f"  ✅ Created {len(triangles)} grid-structured triangles (preserves smoothness)")
        
        # Keep only valid points
        valid_mask = np.isfinite(vdf_flat)
        print(f"  Valid data points: {np.sum(valid_mask)}/{len(vdf_flat)}")
        
    else:
        print(f"  ⚠️ Irregular data - falling back to Delaunay triangulation")
        # Flatten and triangulate as before for irregular data
        x_flat = vx.ravel()
        y_flat = vy.ravel()
        vdf_flat = vdf_clean.ravel()
        
        valid_mask = np.isfinite(vdf_flat) & (vdf_flat > 0)
        x_valid = x_flat[valid_mask]
        y_valid = y_flat[valid_mask]
        
        if len(x_valid) < 3:
            return go.Scatter(x=[], y=[], mode='markers', showlegend=False)
        
        points = np.column_stack([x_valid, y_valid])
        try:
            tri = Delaunay(points)
            triangles = tri.simplices
        except:
            return go.Scatter(x=x_valid, y=y_valid, mode='markers', showlegend=False)
    
    # Convert colormap
    plotly_colormap = get_plotly_colormap(colormap)
    
    # Create Mesh3d plot with proper grid triangulation
    mesh = go.Mesh3d(
        x=x_flat,
        y=y_flat,
        z=np.zeros(len(x_flat)),   # 2D plot, so z=0
        i=triangles[:, 0],         # Triangle vertex indices from grid structure
        j=triangles[:, 1],
        k=triangles[:, 2],
        intensity=vdf_flat,        # Color by VDF values
        colorscale=plotly_colormap,
        showscale=True if title_suffix == 'θ-plane' else False,
        flatshading=False,         # Smooth shading preserves VDF structure
        lighting=dict(             # Disable 3D lighting effects
            ambient=1.0,
            diffuse=0.0,
            specular=0.0,
            roughness=1.0,
            fresnel=0.0
        ),
        colorbar=dict(
            title=dict(text="f (cm² s sr eV)⁻¹")
        ) if title_suffix == 'θ-plane' else None,
        hovertemplate=f'{title_suffix}<br>Vx: %{{x:.1f}} km/s<br>Vy: %{{y:.1f}} km/s<br>VDF: %{{intensity:.2e}}<extra></extra>',
        name=f'VDF {title_suffix}',
        showlegend=False
    )
    
    print(f"  ✅ Grid-structured Mesh3d plot created for {title_suffix}")
    
    return mesh

def create_vdf_plotly_figure_mesh3d(cached_data, viz_mode='mesh3d'):
    """
    Replace your create_vdf_plotly_figure_cached() function with this Mesh3d version.
    Preserves ALL original particle data points.
    
    Args:
        cached_data: Dictionary with pre-computed VDF data
        viz_mode: 'mesh3d' for triangulated mesh, 'scatter' for points, 'interpolate' for contours
        
    Returns:
        plotly.graph_objects.Figure: Interactive VDF figure
    """
    from plotbot.data_classes.psp_span_vdf import psp_span_vdf
    
    # Extract cached data
    vdf_data = cached_data['vdf_data']
    vx_theta, vz_theta, df_theta = cached_data['theta']
    vx_phi, vy_phi, df_phi = cached_data['phi']
    selected_time = cached_data['time']
    
    # Choose subplot specs based on visualization mode
    if viz_mode == 'mesh3d':
        # Use 3D scenes for Mesh3d plots
        subplot_specs = [{"type": "scatter"}, {"type": "scene"}, {"type": "scene"}]
    else:
        # Use regular 2D scatter plots for other modes
        subplot_specs = [{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}]
    
    # Create subplot structure
    fig = make_subplots(
        rows=1, 
        cols=3,
        subplot_titles=('1D Collapsed VDF', 'θ-plane (Vx vs Vz)', 'φ-plane (Vx vs Vy)'),
        specs=[subplot_specs],
        horizontal_spacing=0.08,
        column_widths=[0.25, 0.35, 0.35]
    )
    
    # 1. 1D Collapsed VDF (Left Panel) - Same as before
    vdf_allAngles = np.sum(vdf_data['vdf'], axis=(0, 2))
    vel_1d = vdf_data['vel'][0, :, 0]
    
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
    
    fig.update_xaxes(title_text='Velocity (km/s)', range=[0, 1000], row=1, col=1)
    fig.update_yaxes(title_text='f (cm² s sr eV)⁻¹', type='log', row=1, col=1)
    
    # 2. Theta Plane (Middle Panel)
    theta_xlim, theta_ylim = psp_span_vdf.get_axis_limits('theta', vx_theta, vz_theta, df_theta)
    
    if viz_mode == 'mesh3d':
        theta_plot = create_plotly_vdf_plot_mesh3d(
            vx_theta, vz_theta, df_theta,
            colormap=psp_span_vdf.vdf_colormap,
            title_suffix="θ-plane"
        )
        fig.add_trace(theta_plot, row=1, col=2)
        
        # Configure 3D scene to look like 2D plot
        fig.update_scenes(
            xaxis=dict(title='Vx (km/s)', range=theta_xlim),
            yaxis=dict(title='Vz (km/s)', range=theta_ylim),
            zaxis=dict(visible=False, range=[-0.1, 0.1]),  # Hide Z axis
            camera=dict(eye=dict(x=0, y=0, z=3)),          # Top-down view
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.01),            # Flatten to 2D
            row=1, col=2
        )
    else:
        # Use existing interpolate/scatter methods
        theta_plot = create_plotly_vdf_plot(
            vx_theta, vz_theta, df_theta,
            colormap=psp_span_vdf.vdf_colormap,
            title_suffix="θ-plane",
            viz_mode=viz_mode
        )
        fig.add_trace(theta_plot, row=1, col=2)
        fig.update_xaxes(title_text='Vx (km/s)', range=theta_xlim, row=1, col=2)
        fig.update_yaxes(title_text='Vz (km/s)', range=theta_ylim, row=1, col=2)
    
    # 3. Phi Plane (Right Panel)
    phi_xlim, phi_ylim = psp_span_vdf.get_axis_limits('phi', vx_phi, vy_phi, df_phi)
    
    if viz_mode == 'mesh3d':
        phi_plot = create_plotly_vdf_plot_mesh3d(
            vx_phi, vy_phi, df_phi,
            colormap=psp_span_vdf.vdf_colormap,
            title_suffix="φ-plane"
        )
        fig.add_trace(phi_plot, row=1, col=3)
        
        # Configure 3D scene to look like 2D plot
        fig.update_scenes(
            xaxis=dict(title='Vx (km/s)', range=phi_xlim),
            yaxis=dict(title='Vy (km/s)', range=phi_ylim),
            zaxis=dict(visible=False, range=[-0.1, 0.1]),   # Hide Z axis
            camera=dict(eye=dict(x=0, y=0, z=3)),           # Top-down view  
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.01),             # Flatten to 2D
            row=1, col=3
        )
    else:
        # Use existing interpolate/scatter methods
        phi_plot = create_plotly_vdf_plot(
            vx_phi, vy_phi, df_phi,
            colormap=psp_span_vdf.vdf_colormap,
            title_suffix="φ-plane",
            viz_mode=viz_mode
        )
        fig.add_trace(phi_plot, row=1, col=3)
        fig.update_xaxes(title_text='Vx (km/s)', range=phi_xlim, row=1, col=3)
        fig.update_yaxes(title_text='Vy (km/s)', range=phi_ylim, row=1, col=3)
    
    # Overall styling
    title_text = f'PSP SPAN-I VDF'
    if viz_mode == 'mesh3d':
        title_text += ' (Mesh3d - All Data Preserved)'
    elif viz_mode == 'scatter':
        title_text += ' (Raw Scatter Points)'
    else:
        title_text += ' (Interpolated Contours)'
    title_text += f': {selected_time.strftime("%Y-%m-%d %H:%M:%S")}'
    
    fig.update_layout(
        title=dict(
            text=title_text,
            x=0.5,
            font=dict(size=16)
        ),
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    return fig

def run_vdf_dash_app_main(app, port=8051, debug=False):
    """
    Run the VDF Dash app in a separate thread - Main version.
    
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
