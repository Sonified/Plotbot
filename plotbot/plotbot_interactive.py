# plotbot/plotbot_interactive.py
# Interactive plotting function for Plotbot

import sys
import os
from typing import List
from collections import defaultdict

from .print_manager import print_manager
from .get_data import get_data
from .data_cubby import data_cubby
from .plotbot_helpers import parse_axis_spec, debug_plot_variable
from .time_utils import TimeRangeTracker
from .plotbot_interactive_options import pbi

def plotbot_interactive(trange, *args, backend='auto', port=None, debug=None):
    """
    Interactive plotting function for Plotbot with click-to-VDF functionality.
    
    This function creates an interactive web-based plot that maintains Plotbot's 
    publication-ready styling while adding interactivity. Click on any data point 
    to generate a VDF analysis using vdyes().
    
    Parameters
    ----------
    trange : list
        Time range in format ['YYYY-MM-DD/HH:MM:SS', 'YYYY-MM-DD/HH:MM:SS']
    *args : object pairs
        Variable and axis pairs (e.g., mag_rtn_4sa.br, 1, proton.anisotropy, 2)
    backend : str, optional
        Backend to use ('auto', 'dash', 'matplotlib'). Default: 'auto' (uses pbi.enabled)
    port : int, optional
        Port for Dash server. Default: None (uses pbi.port)
    debug : bool, optional
        Enable debug mode. Default: None (uses pbi.debug)
    
    Returns
    -------
    dash.Dash or bool
        Dash app instance (interactive mode) or success status (matplotlib mode)
    
    Examples
    --------
    # Interactive plot with click-to-VDF
    plotbot_interactive(trange, mag_rtn_4sa.br, 1, epad.strahl, 2)
    
    # Fallback to standard plotbot
    plotbot_interactive(trange, mag_rtn_4sa.br, 1, backend='matplotlib')
    """
    
    print_manager.status("🚀 plotbot_interactive() starting...")
    
    # Apply global options if parameters not explicitly provided
    if backend == 'auto':
        backend = 'dash'  # Always use dash for interactive plots
    if port is None:
        port = 8050  # Default port
    if debug is None:
        debug = False  # Default debug
    
    print_manager.debug(f"Using backend: {backend}, port: {port}, debug: {debug}")
    
    # Check display mode
    if pbi.options.web_display:
        print_manager.status(f"🌐 Web display enabled - will open in browser")
    else:
        print_manager.status(f"📊 Inline display enabled - will show in Jupyter/VS Code")
    
    # Validate time range
    try:
        from dateutil.parser import parse
        from datetime import timezone
        
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
        
        if start_time >= end_time:
            print(f"Oops! 🤗 Start time ({trange[0]}) must be before end time ({trange[1]})")
            return False
            
    except Exception as e:
        print(f"Oops! 🤗 Could not parse time range: {trange}. Error: {e}")
        return False
    
    # Validate argument pairs
    if len(args) % 2 != 0:
        print("\nOops! 🤗 Arguments must be in pairs of (data, axis_number).")
        print("Example: plotbot_interactive(trange, mag_rtn_4sa.br, 1, proton.anisotropy, 2)")
        return False
    
    # Fallback to standard plotbot if requested
    if backend == 'matplotlib':
        print_manager.status("📈 Using standard matplotlib backend...")
        from .plotbot_main import plotbot
        return plotbot(trange, *args)
    
    # Check if interactive dependencies are available
    try:
        import dash
        import plotly.graph_objects as go
        from .plotbot_dash import create_dash_app, run_dash_app
    except ImportError as e:
        print_manager.error(f"❌ Interactive dependencies not available: {e}")
        print_manager.status("📈 Falling back to standard plotbot...")
        from .plotbot_main import plotbot
        return plotbot(trange, *args)
    
    # Process variables and build data structures
    plot_requests = []
    required_data_types = set()
    
    for i in range(0, len(args), 2):
        var = args[i]
        axis_spec = args[i+1]
        
        # Validate variable
        if not hasattr(var, 'data_type'):
            print(f"\nOops! 🤗 Argument {i+1} doesn't look like a plottable data object.")
            print("Each odd-numbered argument must be a data class (e.g., mag_rtn_4sa.br)")
            return False
        
        # Validate axis specification
        if not isinstance(axis_spec, (int, str)):
            print(f"\nOops! 🤗 Axis specification at position {i+2} must be a number or string.")
            print("Example: 1 for left axis, '1r' for right axis")
            return False
        
        # Store request
        plot_requests.append({
            'data_type': var.data_type,
            'class_name': var.class_name,
            'subclass_name': var.subclass_name,
            'axis_spec': axis_spec
        })
        
        required_data_types.add(var.data_type)
        
        print_manager.variable_testing(f"Processing variable: {var.class_name}.{var.subclass_name}")
    
    # Print data summary
    for data_type in required_data_types:
        print_manager.status(f"🛰️ {data_type} - acquiring data...")
    
    # Handle custom variables (if any)
    custom_vars = []
    for request in plot_requests:
        if request['data_type'] == 'custom_data_type':
            class_instance = data_cubby.grab(request['class_name'])
            if class_instance:
                var = class_instance.get_subclass(request['subclass_name'])
                if var is not None:
                    custom_vars.append((var, request['subclass_name']))
    
    # Process custom variables and their source data
    for var, name in custom_vars:
        if hasattr(var, 'source_var') and var.source_var is not None:
            base_vars = []
            for src_var in var.source_var:
                if (hasattr(src_var, 'class_name') and 
                    src_var.class_name != 'custom_class' and 
                    src_var.data_type != 'custom_data_type'):
                    base_vars.append(src_var)
            
            if base_vars:
                print_manager.status(f"📤 Custom variable '{name}' requires data for calculation")
                get_data(trange, *base_vars)
                
                if hasattr(var, 'update'):
                    updated_var = var.update(trange)
                    if updated_var is not None:
                        print_manager.status(f"✅ Successfully updated variable '{name}'")
    
    # Load regular variables
    regular_vars = []
    for request in plot_requests:
        if request['data_type'] != 'custom_data_type':
            class_instance = data_cubby.grab(request['class_name'])
            if class_instance:
                var = class_instance.get_subclass(request['subclass_name'])
                if var is not None:
                    regular_vars.append(var)
    
    # Get data for regular variables
    if regular_vars:
        print_manager.status(f"📥 Acquiring data for {len(regular_vars)} variables...")
        TimeRangeTracker.set_current_trange(trange)
        get_data(trange, *regular_vars)
    
    # Prepare plot variables
    plot_vars = []
    for request in plot_requests:
        class_instance = data_cubby.grab(request['class_name'])
        var = class_instance.get_subclass(request['subclass_name'])
        
        if var is not None:
            plot_vars.append((var, request['axis_spec']))
            debug_plot_variable(var, request, print_manager)
    
    # Create and run Dash app
    try:
        print_manager.status("🎛️ Creating interactive Dash application...")
        app = create_dash_app(plot_vars, trange)
        
        print_manager.status("🌐 Launching interactive plot...")
        inline_mode = not pbi.options.web_display  # False = browser, True = inline
        app_thread = run_dash_app(app, port=port, debug=debug, inline=inline_mode)
        
        print_manager.status("✅ plotbot_interactive() complete!")
        print_manager.status("📌 Click on any data point to generate VDF analysis!")
        print_manager.status(f"🌐 Running at: http://127.0.0.1:{port}")
        
        return app
        
    except Exception as e:
        print_manager.error(f"❌ Failed to create interactive plot: {str(e)}")
        print_manager.status("📈 Falling back to standard plotbot...")
        from .plotbot_main import plotbot
        return plotbot(trange, *args)
