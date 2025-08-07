#!/usr/bin/env python3
"""
Type hints for vdyes module.
"""

from typing import Optional, Any, Union, Dict
from matplotlib.figure import Figure

def vdyes(trange: list[str]) -> Figure:
    """
    VDF plotting - the fine way! (renamed to vdyes)
    Uses Plotbot's class-based parameter system.
    
    Args:
        trange: Time range for VDF plotting (e.g., ['2020/01/29 00:00:00.000', '2020/01/30 00:00:00.000'])
    
    Returns:
        matplotlib.figure.Figure: The 3-panel VDF plot
        
    Example Usage:
        # Set parameters on the class instance (Plotbot way)
        psp_span_vdf.theta_x_smart_padding = 150
        psp_span_vdf.enable_zero_clipping = False
        psp_span_vdf.theta_x_axis_limits = (-800, 0)  # Use Jaye's bounds
        
        # Generate plot with trange (pure Plotbot pattern)
        fig = vdyes(['2020/01/29 00:00:00.000', '2020/01/30 00:00:00.000'])
    """
    ...