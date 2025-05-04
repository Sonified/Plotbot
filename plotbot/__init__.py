# plotbot package
# This file exports all components to make them available when importing the package

# Import and configure matplotlib first to ensure consistent styling
import matplotlib.pyplot as mpl_plt
import numpy as np

# Set global font settings for consistent plotting appearance
mpl_plt.rcParams.update({
    'font.family': 'Arial',
    'font.sans-serif': ['Arial'],
    'axes.labelweight': 'normal',
    'font.weight': 'normal',
    'mathtext.fontset': 'stix',
    'mathtext.rm': 'Arial',
    'mathtext.it': 'Arial:italic',
    'mathtext.bf': 'Arial:bold'
})

# Import core components
from .print_manager import print_manager
from .server_access import server_access 
from .data_tracker import global_tracker
from .ploptions import ploptions
from .data_cubby import data_cubby
from .plot_manager import plot_manager
from .config import config

# Import helper functions needed for export
from .plotbot_helpers import time_clip

# Import data classes and their instances (Updated Paths)
from .data_classes.psp_mag_classes import mag_rtn_4sa, mag_rtn, mag_sc_4sa, mag_sc
from .data_classes.psp_electron_classes import epad, epad_hr
from .data_classes.psp_proton_classes import proton, proton_hr
from .data_classes.psp_proton_fits_classes import proton_fits # Import the FITS class
from .data_classes.psp_ham_classes import ham # ADDED: Import the HAM class instance

# Import custom variables system
from .data_classes.custom_variables import custom_variable, CustomVariablesContainer

# Import test_pilot for testing - safely importing the test functions
# (test_pilot handles the fallback if pytest is not available)
from .test_pilot import run_missions, phase, system_check

# Add a method to debug custom variables
def debug_custom_variables():
    """Print information about all custom variables."""
    print_manager.variable_testing("--- DEBUG: Custom Variables ---")
    custom_instance = data_cubby.grab('custom_class')
    if custom_instance is None:
        print_manager.variable_testing("No custom class found in data_cubby")
        return
    
    if hasattr(custom_instance, 'variables'):
        vars_dict = custom_instance.variables
        var_names = list(vars_dict.keys())
    else:
        attrs = [attr for attr in dir(custom_instance) if not attr.startswith('__')]
        var_names = attrs
        vars_dict = {attr: getattr(custom_instance, attr) for attr in attrs}
    
    if not var_names:
        print_manager.variable_testing("No custom variables found")
        return
    
    print_manager.variable_testing(f"Found {len(var_names)} custom variables: {', '.join(var_names)}")
    for name, var in vars_dict.items():
        print_manager.variable_testing(f"Variable: {name}")
        print_manager.variable_testing(f"  Type: {type(var)}")
        if hasattr(var, 'data_type'):
            print_manager.variable_testing(f"  Data type: {var.data_type}")
        if hasattr(var, 'class_name'):
            print_manager.variable_testing(f"  Class name: {var.class_name}")
        if hasattr(var, 'subclass_name'):
            print_manager.variable_testing(f"  Subclass name: {var.subclass_name}")
        if hasattr(var, 'shape'):
            print_manager.variable_testing(f"  Shape: {var.shape}")
        if hasattr(var, '__array__'):
            try:
                print_manager.variable_testing(f"  First few values: {var[:5]}")
            except Exception as e:
                print_manager.variable_testing(f"  Could not get values: {str(e)}")
    print_manager.variable_testing("--- End DEBUG ---")

# Create custom variables instance
custom_vars = CustomVariablesContainer()

# Debug custom variables initially
print_manager.variable_testing("Initial custom variables state:")
debug_custom_variables()

# Import audification module
from .audifier import audifier

# Import our enhanced plt with options support
from .multiplot_options import plt

# Import main plotting functions
from .plotbot_main import plotbot
from .showdahodo import showdahodo
from .multiplot import multiplot
from .multiplot_options import MultiplotOptions
from .get_data import get_data

# Specify what gets imported with `from plotbot import *`
__all__ = [
    'plt',           # Now provides our enhanced plt with options support
    'np',            # Make numpy directly available
    'plotbot',
    'showdahodo', 
    'multiplot',
    'MultiplotOptions',
    'get_data',      # New function to get data without plotting
    'print_manager', 
    'server_access',
    'global_tracker',
    'ploptions',
    'data_cubby',
    'plot_manager',
    'mag_rtn_4sa', 
    'mag_rtn', 
    'mag_sc_4sa', 
    'mag_sc',
    'epad',
    'epad_hr',       # ADD epad_hr
    'proton',
    'proton_hr',     # ADD proton_hr
    'proton_fits',   # Add proton_fits to __all__
    'ham',           # ADDED: Add ham to __all__
    'audifier',
    'custom_variable',  # Using custom_variable instead of new_variable
    'debug_custom_variables',  # Add debug function for custom variables
    'run_missions',   # Add test_pilot functions
    'phase',
    'system_check',
    'time_clip',      # ADDED time_clip helper function
    'config'          # ADDED config to __all__
]

# Colors for printing
BLUE = '\033[94m'
RESET = '\033[0m'

COMMIT_MSG = "v2.00: Zarr time coverage logic is still flawed—this version does NOT reliably use Zarr cache if file boundaries don't exactly match request (2025_05_04_v2.00). Needs further work."
print(f'{BLUE}   Version: 2025_05_04_v2.00{RESET}')
print("Commit: v2.00: Zarr time coverage logic is still flawed—this version does NOT reliably use Zarr cache if file boundaries don't exactly match request (2025_05_04_v2.00). Needs further work.") # Updated commit message 

# --- Final Print Message ---
print(f"\n{BLUE}🤖 Plotbot Initialized{RESET}")

# Note: Previous logic had this at the end of plotbot_main.py, moved here 
#       to ensure it prints after all imports in __init__ are processed.