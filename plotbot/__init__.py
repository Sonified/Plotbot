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
    'mathtext.fontset': 'custom',
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

# Import data classes and their instances
from .psp_mag_classes import mag_rtn_4sa, mag_rtn, mag_sc_4sa, mag_sc
from .psp_electron_classes import epad
from .psp_proton_classes import proton

# Import derived variable support
from .derived_variable import derived_class, store_data

# Add a method to debug derived variables
def debug_derived():
    """Print information about all derived variables."""
    print_manager.variable_testing("--- DEBUG: Derived Variables ---")
    derived_instance = data_cubby.grab('derived')
    if derived_instance is None:
        print_manager.variable_testing("No derived class found in data_cubby")
        return
    
    attrs = [attr for attr in dir(derived_instance) if not attr.startswith('__')]
    if not attrs:
        print_manager.variable_testing("No derived variables found")
        return
    
    print_manager.variable_testing(f"Found {len(attrs)} derived variables: {', '.join(attrs)}")
    for attr in attrs:
        var = getattr(derived_instance, attr)
        print_manager.variable_testing(f"Variable: {attr}")
        print_manager.variable_testing(f"  Type: {type(var)}")
        if hasattr(var, 'data_type'):
            print_manager.variable_testing(f"  Data type: {var.data_type}")
        if hasattr(var, 'class_name'):
            print_manager.variable_testing(f"  Class name: {var.class_name}")
        if hasattr(var, 'subclass_name'):
            print_manager.variable_testing(f"  Subclass name: {var.subclass_name}")
        if hasattr(var, 'is_derived'):
            print_manager.variable_testing(f"  Is derived: {var.is_derived}")
        if hasattr(var, 'shape'):
            print_manager.variable_testing(f"  Shape: {var.shape}")
        if hasattr(var, '__array__'):
            print_manager.variable_testing(f"  First few values: {var[:5]}")
    print_manager.variable_testing("--- End DEBUG ---")

# Create derived class instance
derived = derived_class()

# Make sure it's stashed in data_cubby
data_cubby.stash(derived, 'derived')

# Debug derived variables
print_manager.variable_testing("Initial derived class state:")
debug_derived()

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
    'proton',
    'audifier',
    'store_data',
    'derived'
]