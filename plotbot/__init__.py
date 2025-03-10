# plotbot package
# This file exports all components to make them available when importing the package

# Import and configure matplotlib first to ensure consistent styling
import matplotlib.pyplot as plt
import numpy as np

# Set global font settings for consistent plotting appearance
plt.rcParams.update({
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

# Import audification module
from .audifier import audifier

# Import main plotting function
# Use relative import to avoid confusion with the function name
from .plotbot_main import plotbot
from .showdahodo import showdahodo
from .multiplot import multiplot
from .multiplot_options import MultiplotOptions

# Specify what gets imported with `from plotbot import *`
__all__ = [
    'plt',           # Make matplotlib.pyplot directly available
    'np',            # Make numpy directly available
    'plotbot',
    'showdahodo', 
    'multiplot',
    'MultiplotOptions',
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
    'audifier'
] 