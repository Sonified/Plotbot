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
from .data_classes.psp_mag_rtn_4sa import mag_rtn_4sa, mag_rtn_4sa_class
from .data_classes.psp_mag_rtn import mag_rtn, mag_rtn_class
from .data_classes.psp_mag_sc_4sa import mag_sc_4sa, mag_sc_4sa_class
from .data_classes.psp_mag_sc import mag_sc, mag_sc_class
from .data_classes.psp_electron_classes import epad, epad_hr, epad_strahl_class, epad_strahl_high_res_class
from .data_classes.psp_proton import proton, proton_class
from .data_classes.psp_proton_hr import proton_hr, proton_hr_class
from .data_classes.psp_proton_fits_classes import proton_fits # Import the FITS class
from .data_classes.psp_ham_classes import ham, ham_class # ADDED: Import the HAM class instance and class

# --- Explicitly Register Global Instances with DataCubby --- #
data_cubby.stash(mag_rtn_4sa, class_name='mag_rtn_4sa')
data_cubby.stash(mag_rtn, class_name='mag_rtn')
data_cubby.stash(mag_sc_4sa, class_name='mag_sc_4sa')
data_cubby.stash(mag_sc, class_name='mag_sc')
data_cubby.stash(epad, class_name='epad')
data_cubby.stash(epad_hr, class_name='epad_hr')
data_cubby.stash(proton, class_name='proton')
data_cubby.stash(proton_hr, class_name='proton_hr')
data_cubby.stash(proton_fits, class_name='proton_fits')
data_cubby.stash(ham, class_name='ham')
print_manager.datacubby("Registered global data instances with DataCubby.")
# ---------------------------------------------------------- #

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
from . import data_snapshot  # Import data_snapshot

# --- Import the function from showda_holes.py ---
from .showda_holes import showda_holes

# --- CLASS_NAME_MAPPING for test utilities and data integrity checks ---
CLASS_NAME_MAPPING = {
    'mag_rtn_4sa': {
        'data_type': 'mag_RTN_4sa',
        'class_type': mag_rtn_4sa_class,
        'components': ['br', 'bt', 'bn', 'bmag', 'pmag', 'all'],
        'primary_component': 'br'
    },
    'mag_rtn': {
        'data_type': 'mag_RTN',
        'class_type': mag_rtn_class,
        'components': ['br', 'bt', 'bn', 'bmag', 'pmag', 'all'],
        'primary_component': 'br'
    },
    'mag_sc_4sa': {
        'data_type': 'mag_SC_4sa',
        'class_type': mag_sc_4sa_class,
        'components': ['bx', 'by', 'bz', 'bmag', 'pmag', 'all'],
        'primary_component': 'bx'
    },
    'mag_sc': {
        'data_type': 'mag_SC',
        'class_type': mag_sc_class,
        'components': ['bx', 'by', 'bz', 'bmag', 'pmag', 'all'],
        'primary_component': 'bx'
    },
    'epad_strahl': {
        'data_type': 'spe_sf0_pad',
        'class_type': epad_strahl_class,
        'components': ['strahl'],
        'primary_component': 'strahl'
    },
    'epad_strahl_high_res': {
        'data_type': 'spe_af0_pad',
        'class_type': epad_strahl_high_res_class,
        'components': ['strahl'],
        'primary_component': 'strahl'
    },
    'proton': {
        'data_type': 'spi_sf00_l3_mom',
        'class_type': proton_class,
        'components': ['anisotropy'],
        'primary_component': 'anisotropy'
    },
    'proton_hr': {
        'data_type': 'spi_af00_L3_mom',
        'class_type': proton_hr_class,
        'components': ['anisotropy'],
        'primary_component': 'anisotropy'
    },
    'ham': {
        'data_type': 'ham',
        'class_type': ham_class,
        'components': ['hamogram_30s'],
        'primary_component': 'hamogram_30s'
    },
}

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
    'config',         # ADDED config to __all__
    'data_snapshot',  # Add data_snapshot to __all__
    'CLASS_NAME_MAPPING',  # Add CLASS_NAME_MAPPING to __all__
    'showda_holes'      # Add showda_holes to __all__
]

# Colors for printing
BLUE = '\033[94m'
RESET = '\033[0m'

# --- Version Info ---
# Increment this version number each time significant changes are pushed.
# Format: YYYY_MM_DD_vMajor.Minor (Minor increments by 0.01 usually)
COMMIT_MESSAGE = "Refactor: v2.37 Split psp_proton_classes.py and created .pyi files"
__version__ = "2025_05_17_v2.37"

# Print version information on import
print(f"   Version: {__version__}")
print(f"   Commit: {COMMIT_MESSAGE}")

# --- Final Print Message ---
print(f"\n{BLUE}🤖 Plotbot Initialized{RESET}")

# Note: Previous logic had this at the end of plotbot_main.py, moved here 
#       to ensure it prints after all imports in __init__ are processed.