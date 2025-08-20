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
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'plotbot_interactive_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'height': 150 * num_subplots + 200,
                    'width': 1200,
                    'scale': 2
                }
            }
        ),
        
        # Control mode toggle button
        html.Div([
            html.Button(
                'Controls: Drag', 
                id='mode-toggle-btn',
                style={
                    'backgroundColor': '#3498db', 
                    'color': 'white', 
                    'border': 'none', 
                    'padding': '10px 20px', 
                    'marginTop': '15px',
                    'borderRadius': '5px',
                    'fontSize': '14px',
                    'cursor': 'pointer'
                }
            ),
            html.P("Drag: Pan + scroll zoom (time axis only) | Select: Box zoom | Double-click to reset", 
                   style={'fontSize': '12px', 'color': '#7f8c8d', 'marginTop': '5px', 'marginBottom': '0'})
        ], style={'textAlign': 'center', 'marginTop': 10}),
        
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
    
    # Mode toggle callback
    @app.callback(
        [Output('mode-toggle-btn', 'children'),
         Output('mode-toggle-btn', 'style'),
         Output('main-plot', 'figure')],
        [Input('mode-toggle-btn', 'n_clicks')],
        [State('main-plot', 'figure')]
    )
    def toggle_interaction_mode(n_clicks, current_figure):
        """Toggle between drag (pan) and select modes"""
        # More robust state management - check current dragmode instead of just click count
        current_dragmode = 'pan'  # Default
        if current_figure and 'layout' in current_figure and 'dragmode' in current_figure['layout']:
            current_dragmode = current_figure['layout']['dragmode']
        
        if n_clicks is None or n_clicks == 0:
            # Initial state - drag mode
            is_drag_mode = True
        else:
            # Toggle based on current state, not just click count
            is_drag_mode = current_dragmode == 'zoom'  # If currently zoom, switch to drag
        
        # Set mode based on logic
        if is_drag_mode:
            button_text = 'Controls: Drag'
            button_color = '#3498db'  # Blue
            dragmode = 'pan'
        else:
            button_text = 'Controls: Select'
            button_color = '#e67e22'  # Orange
            dragmode = 'zoom'
        
        button_style = {
            'backgroundColor': button_color, 
            'color': 'white', 
            'border': 'none', 
            'padding': '10px 20px', 
            'marginTop': '15px',
            'borderRadius': '5px',
            'fontSize': '14px',
            'cursor': 'pointer'
        }
        
        # Update figure dragmode while preserving other settings
        if current_figure:
            current_figure['layout']['dragmode'] = dragmode
            # Ensure these settings are preserved
            current_figure['layout']['hovermode'] = 'closest'
            
            # Configure axis behavior based on mode
            if dragmode == 'zoom':
                # In select/zoom mode: allow y-axis zooming for box selection
                for key in current_figure['layout']:
                    if key.startswith('yaxis'):
                        if current_figure['layout'][key] is None:
                            current_figure['layout'][key] = {}
                        current_figure['layout'][key]['fixedrange'] = False
            else:
                # In drag/pan mode: fix y-axis range to prevent scroll zoom
                for key in current_figure['layout']:
                    if key.startswith('yaxis'):
                        if current_figure['layout'][key] is None:
                            current_figure['layout'][key] = {}
                        current_figure['layout'][key]['fixedrange'] = True
        
        return button_text, button_style, current_figure
    
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
