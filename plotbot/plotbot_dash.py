# plotbot/plotbot_dash.py
# Dash backend for plotbot_interactive()

import numpy as np
import pandas as pd
from datetime import datetime, timezone
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, callback, State
import threading
import webbrowser
from .print_manager import print_manager
from .vdyes import vdyes

def create_spectral_heatmap(fig, var, axis_num):
    """
    Create spectral data as Plotly heatmap in figure (e.g., EPAD strahl).
    
    Args:
        fig: Plotly figure object
        var: Variable with spectral data
        axis_num: Subplot number (1-based)
    """
    try:
        # Extract spectral data arrays
        z_data = var.data  # 2D spectral data (time x energy/pitch_angle)
        
        # Get time coordinates - for spectral data, this might be 2D mesh
        if hasattr(var, 'datetime_array') and var.datetime_array is not None:
            if var.datetime_array.ndim == 2:
                # Use first column for time coordinates
                x_data = var.datetime_array[:, 0]
            else:
                x_data = var.datetime_array
        else:
            x_data = np.arange(z_data.shape[0])
        
        # Get y-axis coordinates (e.g., pitch angles, energies)
        if hasattr(var, 'additional_data') and var.additional_data is not None:
            y_data = var.additional_data
            
            # DEBUG: Let's see what we're actually getting - USE STATUS SO IT SHOWS UP
            print_manager.status(f"🔍 [SPECTRAL DEBUG] Y-axis data type: {type(y_data)}")
            print_manager.status(f"🔍 [SPECTRAL DEBUG] Y-axis data shape: {y_data.shape if hasattr(y_data, 'shape') else 'no shape'}")
            print_manager.status(f"🔍 [SPECTRAL DEBUG] Y-axis data values (first 10): {y_data[:10] if hasattr(y_data, '__getitem__') else y_data}")
            print_manager.status(f"🔍 [SPECTRAL DEBUG] Y-axis data dtype: {y_data.dtype if hasattr(y_data, 'dtype') else 'no dtype'}")
            if hasattr(y_data, 'ndim'):
                print_manager.status(f"🔍 [SPECTRAL DEBUG] Y-axis data dimensions: {y_data.ndim}D")
                if y_data.ndim > 1:
                    print_manager.status(f"🔍 [SPECTRAL DEBUG] First row: {y_data[0, :] if y_data.ndim == 2 else 'N/A'}")
                    print_manager.status(f"🔍 [SPECTRAL DEBUG] We have 2D data! Using first row for y-axis...")
                    y_data = y_data[0, :]  # Use first row if 2D
            
            print_manager.status(f"🔍 [SPECTRAL DEBUG] Final y_data for plotting: {y_data}")
        else:
            y_data = np.arange(z_data.shape[1])
            print_manager.debug(f"🔍 [SPECTRAL DEBUG] No y-axis data found, using indices: {y_data}")
        
        # Handle colorscale and normalization
        colorscale = 'Jet'  # Default
        if hasattr(var, 'colormap'):
            # Map matplotlib colormaps to Plotly colorscales
            cmap_mapping = {
                'jet': 'Jet',
                'viridis': 'Viridis',
                'plasma': 'Plasma',
                'inferno': 'Inferno',
                'magma': 'Magma',
                'hot': 'Hot',
                'cool': 'Blues',
                'rainbow': 'Rainbow'
            }
            colorscale = cmap_mapping.get(var.colormap, 'Jet')
        
        # Handle colorbar scale (log/linear)
        zmin = None
        zmax = None
        colorbar_scale = getattr(var, 'colorbar_scale', 'linear')
        
        if hasattr(var, 'colorbar_limits') and var.colorbar_limits is not None:
            zmin, zmax = var.colorbar_limits
        
        # For logarithmic scale, ensure positive values and proper range
        if colorbar_scale == 'log':
            # Ensure data is positive for log scale
            z_plot_data = np.where(z_data.T <= 0, 1e-10, z_data.T)
            
            # Auto-calculate log limits if not provided
            if zmin is None or zmax is None:
                finite_data = z_plot_data[np.isfinite(z_plot_data) & (z_plot_data > 0)]
                if len(finite_data) > 0:
                    if zmin is None:
                        zmin = np.percentile(finite_data, 1)  # 1st percentile
                    if zmax is None:
                        zmax = np.percentile(finite_data, 99)  # 99th percentile
                else:
                    zmin, zmax = 1e-10, 1.0
        else:
            z_plot_data = z_data.T
        
        # Create heatmap trace
        trace = go.Heatmap(
            x=x_data,
            y=y_data,
            z=z_plot_data,
            colorscale=colorscale,
            zmin=zmin,
            zmax=zmax,
            showscale=True,
            colorbar=dict(
                title=dict(
                    text=getattr(var, 'colorbar_label', 'Log Flux') if colorbar_scale == 'log' else getattr(var, 'colorbar_label', ''),
                    side='right'
                ),
                # TEMPORARILY REVERT: Let's fix y-axis first, then positioning
                tickmode='auto'
            ),
            hovertemplate='Time: %{x}<br>' +
                         'Pitch Angle: %{y:.0f}°<br>' +  # Clean pitch angle display
                         'Value: %{z:.3e}<br>' +
                         '<extra></extra>'
        )
        
        # Add trace to subplot
        fig.add_trace(trace, row=axis_num, col=1)
        
        # Set y-axis label - clean formatting for spectral data
        if hasattr(var, 'y_label') and var.y_label:
            # Clean up y-axis label formatting
            y_label_clean = var.y_label
            # Remove newlines and extra formatting for cleaner display
            y_label_clean = y_label_clean.replace('\\n', ' ').replace('\n', ' ')
            # For pitch angle data, use simple format
            if 'pitch' in y_label_clean.lower() or 'angle' in y_label_clean.lower():
                y_label_clean = 'Pitch Angle (degrees)'
            fig.update_yaxes(title_text=y_label_clean, row=axis_num, col=1)
        
        print_manager.status(f"✅ Created spectral heatmap for {getattr(var, 'subclass_name', 'spectral data')}")
        
    except Exception as e:
        print_manager.error(f"❌ Failed to create spectral heatmap: {str(e)}")
        # Fallback to empty subplot
        fig.add_annotation(
            text=f"Spectral data error: {str(e)}",
            x=0.5, y=0.5,
            xref=f"x{axis_num} domain",
            yref=f"y{axis_num} domain",
            showarrow=False,
            row=axis_num, col=1
        )

def create_dash_app(plot_vars, trange):
    """
    Create a Dash app with publication-ready styling that matches Plotbot's matplotlib aesthetic.
    
    Args:
        plot_vars: List of (variable, axis_spec) tuples
        trange: Time range for the plot
    
    Returns:
        dash.Dash: Configured Dash application
    """
    
    print_manager.status("🎛️ Creating interactive Dash application...")
    
    # Initialize Dash app with clean white styling
    app = dash.Dash(__name__)
    
    # Group variables by axis
    from collections import defaultdict
    from .plotbot_helpers import parse_axis_spec
    
    axis_vars = defaultdict(list)
    for var, axis_spec in plot_vars:
        axis_num, is_right = parse_axis_spec(axis_spec)
        axis_vars[axis_num].append((var, is_right))
    
    num_subplots = len(axis_vars)
    subplot_titles = [f"Panel {i}" for i in range(1, num_subplots + 1)]
    
    # Create figure with subplots
    fig = make_subplots(
        rows=num_subplots, cols=1,
        shared_xaxes=True,
        subplot_titles=subplot_titles,
        vertical_spacing=0.08,
        specs=[[{"secondary_y": True}] for _ in range(num_subplots)]
    )
    
    # Publication-ready theme matching matplotlib
    plotly_theme = {
        'layout': {
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'font': {'family': 'Arial, Helvetica, sans-serif', 'size': 12, 'color': 'black'},
            'xaxis': {
                'gridcolor': '#E5E5E5',
                'gridwidth': 1,
                'zeroline': False,
                'linecolor': 'black',
                'linewidth': 1,
                'mirror': True,
                'tickfont': {'size': 10},
                'title': {'font': {'size': 12}}
            },
            'yaxis': {
                'gridcolor': '#E5E5E5',
                'gridwidth': 1,
                'zeroline': False,
                'linecolor': 'black',
                'linewidth': 1,
                'mirror': True,
                'tickfont': {'size': 10},
                'title': {'font': {'size': 12}}
            },
        }
    }
    
    # Apply publication styling
    fig.update_layout(plotly_theme['layout'])
    fig.update_layout(
        height=150 * num_subplots + 200,  # Dynamic height based on panels
        showlegend=True,
        legend=dict(
            orientation="v",      # Vertical legend
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.02,              # Position to the right of the plot
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1,
            font=dict(size=10)
        ),
        # Configure scientific plot interactions
        dragmode='pan'  # Click and drag = panning
    )
    
    # Track colors for consistency with matplotlib
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    color_index = 0
    
    # Add traces for each variable
    for axis_num, vars_list in axis_vars.items():
        for var, is_right in vars_list:
            if hasattr(var, 'data') and var.data is not None:
                # Check if this is spectral data
                plot_type = getattr(var, 'plot_type', 'time_series')
                
                if plot_type == 'spectral':
                    # Handle spectral data with heatmap
                    create_spectral_heatmap(fig, var, axis_num)
                else:
                    # Handle time series data (original code)
                    if hasattr(var, 'datetime_array') and var.datetime_array is not None:
                        times = var.datetime_array
                    else:
                        times = np.arange(len(var.data))
                    
                    # Get variable name for legend with proper formatting
                    var_name = getattr(var, 'y_label', getattr(var, 'subclass_name', 'Variable'))
                    
                    # Clean up common formatting issues
                    if var_name:
                        # Replace LaTeX-style formatting with proper Unicode symbols
                        var_name = var_name.replace('$T_\\perp/T_\\parallel$', 'T⊥/T∥')
                        var_name = var_name.replace('$T_\\perp$', 'T⊥')
                        var_name = var_name.replace('$T_\\parallel$', 'T∥')
                        var_name = var_name.replace('T_\\perp/T_\\parallel', 'T⊥/T∥')
                        var_name = var_name.replace('T_\\perp', 'T⊥')
                        var_name = var_name.replace('T_\\parallel', 'T∥')
                        var_name = var_name.replace('\\perp', '⊥')
                        var_name = var_name.replace('\\parallel', '∥')
                        var_name = var_name.replace('$', '')  # Remove remaining LaTeX delimiters
                    
                    # Create trace
                    trace = go.Scatter(
                        x=times,
                        y=var.data,
                        mode='lines',
                        name=var_name,
                        line=dict(color=colors[color_index % len(colors)], width=1),
                        hovertemplate='<b>%{fullData.name}</b><br>' +
                                    'Time: %{x}<br>' +
                                    'Value: %{y:.3f}<br>' +
                                    '<extra></extra>'
                    )
                    
                    # Add trace to correct subplot and y-axis
                    fig.add_trace(trace, row=axis_num, col=1, secondary_y=is_right)
                    color_index += 1
            
            # Set axis labels with proper formatting
            if hasattr(var, 'y_label') and var.y_label:
                # Clean up y-axis label formatting
                y_label_clean = var.y_label
                y_label_clean = y_label_clean.replace('$T_\\perp/T_\\parallel$', 'T⊥/T∥')
                y_label_clean = y_label_clean.replace('$T_\\perp$', 'T⊥')
                y_label_clean = y_label_clean.replace('$T_\\parallel$', 'T∥')
                y_label_clean = y_label_clean.replace('T_\\perp/T_\\parallel', 'T⊥/T∥')
                y_label_clean = y_label_clean.replace('T_\\perp', 'T⊥')
                y_label_clean = y_label_clean.replace('T_\\parallel', 'T∥')
                y_label_clean = y_label_clean.replace('\\perp', '⊥')
                y_label_clean = y_label_clean.replace('\\parallel', '∥')
                y_label_clean = y_label_clean.replace('$', '')
                
                if is_right:
                    fig.update_yaxes(title_text=y_label_clean, row=axis_num, col=1, secondary_y=True)
                else:
                    fig.update_yaxes(title_text=y_label_clean, row=axis_num, col=1, secondary_y=False)
    
    # Set x-axis label for bottom subplot
    fig.update_xaxes(title_text="Time", row=num_subplots, col=1)
    
    # Configure all axes to have proper borders but restrict y-axis scroll zoom
    for i in range(1, num_subplots + 1):
        fig.update_yaxes(
            fixedrange=True,  # Prevent y-axis scroll zoom but allow panning in drag mode
            linecolor='black',
            linewidth=1,
            mirror=True,
            row=i, col=1
        )
        fig.update_xaxes(
            linecolor='black',
            linewidth=1,
            mirror=True,
            row=i, col=1
        )
    
    # Main app layout
    app.layout = html.Div([
        html.Div([
            html.H1("🤖 Plotbot Interactive", 
                   style={'textAlign': 'center', 'marginBottom': 30, 'color': '#2c3e50'}),
            html.P(f"Time Range: {trange[0]} to {trange[1]}", 
                   style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': 20}),
        ]),
        
        dcc.Graph(
            id='main-plot',
            figure=fig,
            style={'height': f'{150 * num_subplots + 200}px'},
            config={
                'displayModeBar': True,
                'scrollZoom': True,  # Enable two-finger scrolling for zoom
                'doubleClick': 'reset',  # Double-click to reset zoom
                # RESTORE STANDARD PLOTLY TOOLBAR - remove the custom restrictions
                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],  # Keep pan2d available
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'plotbot_interactive_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'height': 150 * num_subplots + 200,
                    'width': 1200,
                    'scale': 2
                }
            }
        ),
        
        # VDF panel (initially hidden)
        html.Div(id='vdf-panel', children=[
            html.H3("🎯 VDF Analysis", style={'color': '#2c3e50'}),
            html.Div(id='vdf-content'),
            html.Button('Close VDF', id='close-vdf-btn', 
                       style={'backgroundColor': '#e74c3c', 'color': 'white', 
                             'border': 'none', 'padding': '10px 20px', 'marginTop': '10px'})
        ], style={'display': 'none', 'marginTop': 30, 'padding': 20, 
                 'backgroundColor': '#f8f9fa', 'border': '1px solid #dee2e6'}),
        
        # Status messages
        html.Div(id='status-message', style={'marginTop': 20, 'textAlign': 'center'})
    ], style={'padding': 20, 'fontFamily': 'Arial, Helvetica, sans-serif'})
    
    # Click callback for VDF integration
    @app.callback(
        [Output('vdf-panel', 'style'),
         Output('vdf-content', 'children'),
         Output('status-message', 'children')],
        [Input('main-plot', 'clickData'),
         Input('close-vdf-btn', 'n_clicks')],
        [State('vdf-panel', 'style')]
    )
    def handle_plot_click(clickData, close_clicks, current_style):
        """Handle clicks on the main plot to show VDF data"""
        from dash import callback_context
        
        # Determine which input triggered the callback
        if not callback_context.triggered:
            return {'display': 'none'}, "", ""
        
        trigger_id = callback_context.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'close-vdf-btn':
            return {'display': 'none'}, "", ""
        
        elif trigger_id == 'main-plot' and clickData:
            try:
                # Extract clicked time
                clicked_time = clickData['points'][0]['x']
                print_manager.status(f"🎯 VDF requested for time: {clicked_time}")
                
                # Create a small time window around the clicked point
                from dateutil.parser import parse
                from datetime import timedelta
                
                if isinstance(clicked_time, str):
                    click_dt = parse(clicked_time)
                else:
                    click_dt = clicked_time
                
                # Create 10-minute window around click
                start_time = click_dt - timedelta(minutes=5)
                end_time = click_dt + timedelta(minutes=5)
                
                vdf_trange = [
                    start_time.strftime('%Y-%m-%d/%H:%M:%S.000'),
                    end_time.strftime('%Y-%m-%d/%H:%M:%S.000')
                ]
                
                try:
                    # Call vdyes to generate VDF
                    print_manager.status(f"🔄 Generating VDF for time window: {vdf_trange}")
                    vdf_result = vdyes(vdf_trange)
                    
                    # Create VDF content panel
                    panel_style = {
                        'display': 'block', 
                        'marginTop': 30, 
                        'padding': 20, 
                        'backgroundColor': '#f8f9fa', 
                        'border': '1px solid #dee2e6'
                    }
                    
                    vdf_content = html.Div([
                        html.P(f"📊 VDF generated for: {clicked_time}", 
                               style={'fontWeight': 'bold', 'color': '#2c3e50'}),
                        html.P(f"⏰ Time window: {vdf_trange[0]} to {vdf_trange[1]}", 
                               style={'color': '#7f8c8d', 'fontSize': '12px'}),
                        html.P("🎯 VDF widget should appear in your Jupyter environment", 
                               style={'color': '#27ae60'})
                    ])
                    
                    status_msg = html.P(f"✅ VDF generated for {clicked_time}", 
                                       style={'color': '#27ae60', 'fontWeight': 'bold'})
                    
                    return panel_style, vdf_content, status_msg
                    
                except Exception as e:
                    print_manager.error(f"❌ VDF generation failed: {str(e)}")
                    error_content = html.P(f"❌ VDF generation failed: {str(e)}", 
                                          style={'color': '#e74c3c'})
                    return current_style, error_content, ""
                    
            except Exception as e:
                print_manager.error(f"❌ Click handling failed: {str(e)}")
                return current_style, "", ""
        
        return current_style, "", ""
    
    # REMOVED: Custom mode toggle callback - now using standard Plotly toolbar
    print_manager.status("✅ Dash app created successfully!")
    return app

def run_dash_app(app, port=8050, debug=False, inline=False):
    """Run the Dash app either inline (Jupyter) or in browser"""
    
    if inline:
        # Use modern Dash inline display (not deprecated jupyter-dash)
        try:
            # Run inline in Jupyter/VS Code using modern Dash
            app.run(debug=debug, port=port, mode='inline', height=600)
            print_manager.status(f"📊 Interactive plot displayed inline")
            return app
            
        except Exception as e:
            print_manager.warning(f"Inline mode failed: {e}, falling back to browser mode")
            inline = False
    
    if not inline:
        # Original browser-based approach
        def run_app():
            app.run(debug=debug, port=port, host='127.0.0.1')
        
        # Start app in background thread
        app_thread = threading.Thread(target=run_app, daemon=True)
        app_thread.start()
        
        # Give server time to start
        import time
        time.sleep(2)
        
        # Open browser
        try:
            webbrowser.open(f'http://127.0.0.1:{port}')
            print_manager.status(f"🌐 Browser opened at http://127.0.0.1:{port}")
        except Exception as e:
            print_manager.warning(f"Could not open browser automatically: {e}")
            print_manager.status(f"🌐 Please open http://127.0.0.1:{port} manually")
        
        return app_thread
