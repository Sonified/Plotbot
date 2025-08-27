# plotbot/plotbot_interactive_vdf.py
# Interactive VDF plotting function for Plotbot

import sys
import os
import numpy as np
from typing import List
from dateutil.parser import parse

from .print_manager import print_manager
from .get_data import get_data
from .data_cubby import data_cubby
from .data_classes.psp_span_vdf import psp_span_vdf

def plotbot_interactive_vdf(trange, backend='auto', port=None, debug=None):
    """
    Interactive VDF plotting function for Plotbot with time slider functionality.
    
    This function creates an interactive web-based VDF plot that maintains Plotbot's 
    publication-ready styling while adding time navigation controls.
    
    Parameters
    ----------
    trange : list
        Time range in format ['YYYY-MM-DD/HH:MM:SS', 'YYYY-MM-DD/HH:MM:SS']
    backend : str, optional
        Backend to use ('auto', 'dash', 'matplotlib'). Default: 'auto' (uses dash)
    port : int, optional
        Port for Dash server. Default: None (uses 8051)
    debug : bool, optional
        Enable debug mode. Default: None (uses False)
    
    Returns
    -------
    dash.Dash or bool
        Dash app instance (interactive mode) or success status (matplotlib mode)
    
    Examples
    --------
    # Interactive VDF plot with time slider
    plotbot_interactive_vdf(['2020/01/29 17:00:00', '2020/01/29 19:00:00'])
    
    # Fallback to standard vdyes
    plotbot_interactive_vdf(trange, backend='matplotlib')
    """
    
    print_manager.status("🚀 plotbot_interactive_vdf() starting...")
    
    # Apply defaults
    if backend == 'auto':
        backend = 'dash'  # Always use dash for interactive VDF plots
    if port is None:
        port = 8051  # Use different port than main plotbot_interactive
    if debug is None:
        debug = False
    
    print_manager.debug(f"Using backend: {backend}, port: {port}, debug: {debug}")
    
    # Validate time range
    try:
        start_time = parse(trange[0].replace('/', ' '))
        end_time = parse(trange[1].replace('/', ' '))
        
        if start_time >= end_time:
            print(f"Oops! 🤗 Start time ({trange[0]}) must be before end time ({trange[1]})")
            return False
            
    except Exception as e:
        print(f"Oops! 🤗 Could not parse time range: {trange}. Error: {e}")
        return False
    
    # Fallback to standard vdyes if requested
    if backend == 'matplotlib':
        print_manager.status("📈 Using standard vdyes() backend...")
        from .vdyes import vdyes
        return vdyes(trange)
    
    # Check if interactive dependencies are available
    try:
        import dash
        import plotly.graph_objects as go
        from .plotbot_dash_vdf import create_vdf_dash_app, run_vdf_dash_app
    except ImportError as e:
        print_manager.error(f"❌ Interactive dependencies not available: {e}")
        print_manager.status("📈 Falling back to standard vdyes...")
        from .vdyes import vdyes
        return vdyes(trange)
    
    # Get VDF data using the same approach as vdyes() - bypass plotbot data system
    print_manager.status("📡 Downloading PSP SPAN-I VDF data using pyspedas...")
    
    import pyspedas
    import cdflib
    import pandas as pd
    
    # Download using proven pyspedas approach (exactly like vdyes())
    # First try local files only (no_update=True for fast local check)
    VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                              notplot=True, time_clip=True, downloadonly=True, get_support_data=True, 
                              no_update=True)
    
    # If no local files found, allow download
    if not VDfile:
        print_manager.status("📡 No local VDF files found, attempting download...")
        VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                                  notplot=True, time_clip=True, downloadonly=True, get_support_data=True, 
                                  no_update=False)
    else:
        print_manager.status("✅ Using cached VDF files (no download needed)")
    
    if not VDfile:
        print_manager.error("❌ No VDF files found for time range")
        print_manager.status("💡 Try a different time range with known VDF data")
        return False
        
    print_manager.status(f"📁 VDF file: {VDfile[0]}")
    
    # Process data using the same approach as vdyes()
    dat = cdflib.CDF(VDfile[0])
    
    # Get time array to determine available data
    epoch_cdf = dat.varget('Epoch')
    # Type: ignore for cdflib compatibility
    epoch_dt64 = cdflib.cdfepoch.to_datetime(epoch_cdf)  # type: ignore
    epoch = pd.to_datetime(epoch_dt64).to_pydatetime().tolist()
    
    # Filter time points to requested range
    start_dt = parse(trange[0].replace('/', ' '))
    end_dt = parse(trange[1].replace('/', ' '))
    
    time_mask = [(t >= start_dt and t <= end_dt) for t in epoch]
    available_times = [epoch[i] for i, mask in enumerate(time_mask) if mask]
    available_indices = [i for i, mask in enumerate(time_mask) if mask]
    
    n_times = len(available_times)
    print_manager.status(f"✅ VDF data loaded: {n_times} time points in requested range")
    
    if n_times == 0:
        print_manager.error("❌ No VDF data found in time range")
        print_manager.status(f"💡 Available time range: {epoch[0]} to {epoch[-1]}")
        return False
    
    print_manager.status(f"📅 Available VDF times: {available_times[0]} to {available_times[-1]}")
    
    # Create and run VDF Dash app
    try:
        print("🔍 DEBUG: About to create VDF Dash app...")
        print_manager.status("🎛️ Creating interactive VDF Dash application...")
        from .plotbot_dash_vdf import create_vdf_dash_app, run_vdf_dash_app
        app = create_vdf_dash_app(dat, available_times, available_indices, trange)
        
        print("🔍 DEBUG: Dash app created, about to launch...")
        print_manager.status("🌐 Launching interactive VDF plot...")
        app_thread = run_vdf_dash_app(app, port=port, debug=debug)
        
        print("🔍 DEBUG: VDF Dash app should be running!")
        print_manager.status("✅ plotbot_interactive_vdf() complete!")
        print_manager.status("📌 Use the time slider to navigate through VDF data!")
        print_manager.status(f"🌐 Running at: http://127.0.0.1:{port}")
        
        return app
        
    except Exception as e:
        print(f"🔍 DEBUG: Exception in VDF Dash creation: {str(e)}")
        print(f"🔍 DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"🔍 DEBUG: Full traceback:")
        traceback.print_exc()
        print_manager.error(f"❌ Failed to create interactive VDF plot: {str(e)}")
        print_manager.status("📈 Falling back to standard vdyes...")
        from .vdyes import vdyes
        return vdyes(trange)
