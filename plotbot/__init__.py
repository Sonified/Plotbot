# plotbot package
# This file exports all components to make them available when importing the package

# START IMPORT TIMING
from .import_timer import start_timing, time_import, time_block, end_timing
start_timing("plotbot_full_initialization")

import os

# Import and configure matplotlib first to ensure consistent styling
mpl_plt = time_import('matplotlib.pyplot')
np = time_import('numpy')

# Set global font settings for consistent plotting appearance
mpl_plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'sans-serif'],
    'axes.labelweight': 'normal',
    'font.weight': 'normal',
    'mathtext.fontset': 'stix',
    'mathtext.default': 'regular'
})

# Import core components
with time_block("core_components"):
    from .print_manager import print_manager
    from .server_access import server_access 
    from .data_tracker import global_tracker
    from .plot_config import plot_config
    from .data_cubby import data_cubby
    from .plot_manager import plot_manager
    from .config import config

# Import helper functions needed for export
from .plotbot_helpers import time_clip

# Import data classes and their instances (Updated Paths)
with time_block("psp_data_classes"):
    from .data_classes.psp_mag_rtn_4sa import mag_rtn_4sa, mag_rtn_4sa_class
    from .data_classes.psp_mag_rtn import mag_rtn, mag_rtn_class
    from .data_classes.psp_mag_sc_4sa import mag_sc_4sa, mag_sc_4sa_class
    from .data_classes.psp_mag_sc import mag_sc, mag_sc_class
    from .data_classes.psp_electron_classes import epad, epad_hr, epad_strahl_class, epad_strahl_high_res_class
    from .data_classes.psp_proton import proton, proton_class
    from .data_classes.psp_proton_hr import proton_hr, proton_hr_class
    from .data_classes.psp_proton_fits_classes import proton_fits # Import the FITS class
    from .data_classes.psp_alpha_fits_classes import alpha_fits, alpha_fits_class # Import the alpha FITS class
    from .data_classes.psp_ham_classes import ham, ham_class # ADDED: Import the HAM class instance and class

# WIND satellite data classes
with time_block("wind_data_classes"):
    from .data_classes.wind_mfi_classes import wind_mfi_h2, wind_mfi_h2_class
    from .data_classes.wind_3dp_classes import wind_3dp_elpd, wind_3dp_elpd_class
    from .data_classes.wind_swe_h5_classes import wind_swe_h5, wind_swe_h5_class
    from .data_classes.wind_swe_h1_classes import wind_swe_h1, wind_swe_h1_class
    from .data_classes.wind_3dp_pm_classes import wind_3dp_pm, wind_3dp_pm_class
    from .data_classes.psp_alpha_classes import psp_alpha, psp_alpha_class
    from .data_classes.psp_qtn_classes import psp_qtn, psp_qtn_class
    from .data_classes.psp_dfb_classes import psp_dfb, psp_dfb_class
    from .data_classes.psp_orbit import psp_orbit, psp_orbit_class
    from .data_classes.psp_span_vdf import psp_span_vdf, psp_span_vdf_class

# ==============================================================================
# Custom Class Imports (auto-generated)
# To add new classes: run cdf_to_plotbot('path/to/file.cdf') and this will be updated
# ------------------------------------------------------------------------------
from .data_classes.custom_classes.demo_spectral_waves import demo_spectral_waves, demo_spectral_waves_class
from .data_classes.custom_classes.demo_wave_power import demo_wave_power, demo_wave_power_class
from .data_classes.custom_classes.psp_simple_test import psp_simple_test, psp_simple_test_class
from .data_classes.custom_classes.psp_spectral_waves import psp_spectral_waves, psp_spectral_waves_class
from .data_classes.custom_classes.psp_waves_auto import psp_waves_auto, psp_waves_auto_class
from .data_classes.custom_classes.psp_waves_real_test import psp_waves_real_test, psp_waves_real_test_class
from .data_classes.custom_classes.psp_waves_spectral import psp_waves_spectral, psp_waves_spectral_class
from .data_classes.custom_classes.psp_waves_test import psp_waves_test, psp_waves_test_class
from .data_classes.custom_classes.psp_waves_timeseries import psp_waves_timeseries, psp_waves_timeseries_class
# ------------------------------------------------------------------------------
# ==============================================================================

# Import custom generated classes explicitly for type hinting and IDE support
from .data_classes.custom_classes.psp_waves_timeseries import psp_waves_timeseries, psp_waves_timeseries_class
from .data_classes.custom_classes.psp_waves_spectral import psp_waves_spectral, psp_waves_spectral_class


# --- Explicitly Register Global Instances with DataCubby --- #
with time_block("data_cubby_registration"):
    data_cubby.stash(mag_rtn_4sa, class_name='mag_rtn_4sa')
    data_cubby.stash(mag_rtn, class_name='mag_rtn')
    data_cubby.stash(mag_sc_4sa, class_name='mag_sc_4sa')
    data_cubby.stash(mag_sc, class_name='mag_sc')
    data_cubby.stash(epad, class_name='epad')
    data_cubby.stash(epad_hr, class_name='epad_hr')
    data_cubby.stash(proton, class_name='proton')
    data_cubby.stash(proton_hr, class_name='proton_hr')
    data_cubby.stash(proton_fits, class_name='proton_fits')
    data_cubby.stash(alpha_fits, class_name='alpha_fits')
    data_cubby.stash(ham, class_name='ham')
    # Register WIND satellite instances
    data_cubby.stash(wind_mfi_h2, class_name='wind_mfi_h2')
    data_cubby.stash(wind_3dp_elpd, class_name='wind_3dp_elpd')
    data_cubby.stash(wind_3dp_pm, class_name='wind_3dp_pm')
    data_cubby.stash(psp_alpha, class_name='psp_alpha')
    data_cubby.stash(wind_swe_h5, class_name='wind_swe_h5')
    data_cubby.stash(wind_swe_h1, class_name='wind_swe_h1')
    data_cubby.stash(psp_span_vdf, class_name='psp_span_vdf')
    data_cubby.stash(psp_qtn, class_name='psp_qtn')
    data_cubby.stash(psp_dfb, class_name='psp_dfb')
    data_cubby.stash(psp_orbit, class_name='psp_orbit')
    # Register individual DFB data types to the same psp_dfb instance
    data_cubby.stash(psp_dfb, class_name='dfb_ac_spec_dv12hg')
    data_cubby.stash(psp_dfb, class_name='dfb_ac_spec_dv34hg')
    data_cubby.stash(psp_dfb, class_name='dfb_dc_spec_dv12hg')

# --- Auto-register Custom CDF Classes --- #
def _auto_register_custom_classes():
    """Automatically scan and register all classes in data_classes/custom_classes/"""
    import os
    import importlib
    from pathlib import Path
    
    custom_classes_dir = Path(__file__).parent / "data_classes" / "custom_classes"
    
    if not custom_classes_dir.exists():
        return
    
    # Find all .py files in custom_classes directory
    for py_file in custom_classes_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue  # Skip __init__.py etc.
            
        module_name = py_file.stem
        try:
            # Import the module
            module = importlib.import_module(f"plotbot.data_classes.custom_classes.{module_name}")
            
            # Look for class instance (follows pattern: module_name = module_name_class(None))
            if hasattr(module, module_name):
                class_instance = getattr(module, module_name)
                data_cubby.stash(class_instance, class_name=module_name)
                print_manager.datacubby(f"Auto-registered custom class: {module_name}")

                # --- THIS IS THE CRITICAL FIX ---
                # Inject the class instance into the main plotbot module's globals
                globals()[module_name] = class_instance
                # Also add to __all__ so it can be imported with `from plotbot import *`
                if module_name not in __all__:
                    __all__.append(module_name)
                print_manager.debug(f"Exposed '{module_name}' as a global plotbot class.")
                
        except Exception as e:
            print_manager.warning(f"Failed to auto-register {module_name}: {e}")

# Auto-register any custom CDF classes
with time_block("auto_register_custom_classes"):
    _auto_register_custom_classes()

print_manager.datacubby("Registered global data instances with DataCubby.")
# ---------------------------------------------------------- #

# Import custom variables system
with time_block("custom_variables"):
    from .data_classes.custom_variables import custom_variable, CustomVariablesContainer

# Import test_pilot for testing - safely importing the test functions
# (test_pilot handles the fallback if pytest is not available)
#from .test_pilot import run_missions, phase, system_check

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

# Import audification module and audifier instance
audifier_module = time_import('audifier', from_module='plotbot')
from .audifier import audifier

# Import ploptions for figure control
from .ploptions import ploptions

# Import our enhanced plt with options support
with time_block("enhanced_plt"):
    from .multiplot_options import plt

# Import main plotting functions
with time_block("main_plotting_functions"):
    from .plotbot_main import plotbot
    from .plotbot_interactive import plotbot_interactive
    from .plotbot_interactive_options import pbi
    from .plotbot_interactive_vdf import plotbot_interactive_vdf
    from .showdahodo import showdahodo
    from .multiplot import multiplot
    from .multiplot_options import MultiplotOptions
    from .get_data import get_data
    from .vdyes import vdyes
    from . import data_snapshot  # Import data_snapshot
    from .simple_snapshot import save_simple_snapshot, load_simple_snapshot

# --- Import the function from showda_holes.py ---
from .showda_holes import showda_holes

# --- Import CDF functions for direct access ---
with time_block("cdf_functions"):
    from .data_import_cdf import cdf_to_plotbot, scan_cdf_directory
    from .vdyes import vdyes

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
    'psp_qtn': {
        'data_type': 'sqtn_rfs_v1v2',
        'class_type': psp_qtn_class,
        'components': ['density', 'temperature'],
        'primary_component': 'density'
    },
    'psp_orbit': {
        'data_type': 'psp_orbit_data',
        'class_type': psp_orbit_class,
        'components': ['r_sun', 'carrington_lon', 'carrington_lat', 'heliocentric_distance_au', 'orbital_speed'],
        'primary_component': 'r_sun'
    },
    'psp_dfb': {
        'data_type': 'dfb_ac_spec_dv12hg',  # Primary data type (AC spectra dv12)
        'class_type': psp_dfb_class,
        'components': ['ac_spec_dv12', 'ac_spec_dv34', 'dc_spec_dv12'],
        'primary_component': 'ac_spec_dv12'
    },
    # Map all DFB data types to the same psp_dfb class instance
    'dfb_ac_spec_dv12hg': {
        'data_type': 'dfb_ac_spec_dv12hg',
        'class_type': psp_dfb_class,
        'components': ['ac_spec_dv12'],
        'primary_component': 'ac_spec_dv12'
    },
    'dfb_ac_spec_dv34hg': {
        'data_type': 'dfb_ac_spec_dv34hg',
        'class_type': psp_dfb_class,
        'components': ['ac_spec_dv34'],
        'primary_component': 'ac_spec_dv34'
    },
    'dfb_dc_spec_dv12hg': {
        'data_type': 'dfb_dc_spec_dv12hg',
        'class_type': psp_dfb_class,
        'components': ['dc_spec_dv12'],
        'primary_component': 'dc_spec_dv12'
    },
}

# Specify what gets imported with `from plotbot import *`
__all__ = [
    'plt',           # Now provides our enhanced plt with options support
    'np',            # Make numpy directly available
    'plotbot',
    'plotbot_interactive',  # Interactive plotting with click-to-VDF functionality
    'plotbot_interactive_vdf',  # Interactive VDF plotting with time slider
    'pbi',           # Interactive plotting options
    'ploptions',     # Global plotbot figure control options
    'showdahodo', 
    'multiplot',
    'vdyes',         # PSP SPAN-I VDF plotting function
    'MultiplotOptions',
    'get_data',      # New function to get data without plotting
    'print_manager', 
    'server_access',
    'global_tracker',
    'plot_config',
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
    'alpha_fits',    # Add alpha_fits to __all__
    'ham',           # ADDED: Add ham to __all__
    'wind_mfi_h2',   # WIND satellite magnetic field data
    'wind_3dp_elpd', # WIND satellite electron pitch-angle distributions
    'wind_3dp_pm',   # WIND satellite ion plasma moments
    'wind_swe_h5',   # WIND satellite electron temperature
    'wind_swe_h1',   # WIND satellite proton/alpha thermal speeds
    'psp_alpha',     # PSP alpha particle moments
    'psp_qtn',       # PSP quasi-thermal noise (electron density and temperature)
    'psp_dfb',       # PSP FIELDS electric field AC/DC spectra
    'psp_orbit',     # PSP orbital/positional data
    'psp_span_vdf',  # PSP SPAN-I velocity distribution functions
    'audifier',
    'custom_variable',  # Using custom_variable instead of new_variable
    'debug_custom_variables',  # Add debug function for custom variables
    'time_clip',      # ADDED time_clip helper function
    'config',         # ADDED config to __all__
    'data_snapshot',  # Add data_snapshot to __all__
    'save_simple_snapshot',
    'load_simple_snapshot',
    'cdf_to_plotbot',       # CDF class generation function
    'scan_cdf_directory',   # CDF directory scanning function
    'CLASS_NAME_MAPPING',  # Add CLASS_NAME_MAPPING to __all__
    'showda_holes',      # Add showda_holes to __all__
    
    # --- AUTO-GENERATED CUSTOM CLASS __all__ ENTRIES ---
    'demo_spectral_waves',  # Custom generated class
    'demo_wave_power',  # Custom generated class
    'psp_simple_test',  # Custom generated class
    'psp_spectral_waves',  # Custom generated class
    'psp_waves_auto',  # Custom generated class
    'psp_waves_real_test',  # Custom generated class
    'psp_waves_spectral',  # Custom generated class
    'psp_waves_timeseries',  # Custom generated class
    # --- END AUTO-GENERATED __all__ ENTRIES ---

    # --- AUTO-GENERATED CUSTOM CLASS __ALL__ ENTRIES ---
    'demo_spectral_waves',  # Custom generated class
    'demo_wave_power',  # Custom generated class
    'psp_simple_test',  # Custom generated class
    'psp_spectral_waves',  # Custom generated class
    'psp_waves_auto',  # Custom generated class
    'psp_waves_real_test',  # Custom generated class
    'psp_waves_spectral',  # Custom generated class
    'psp_waves_test',  # Custom generated class
    'psp_waves_timeseries',  # Custom generated class
# --- END AUTO-GENERATED __ALL__ ENTRIES ---
]

# Colors for printing
BLUE = '\033[94m'
RESET = '\033[0m'

#------------------------------------------------------------------------------
# Version, Date, and Welcome Message for Plotbot
#------------------------------------------------------------------------------
__version__ = "2025_10_02_v3.55"

# Commit message for this version
__commit_message__ = "v3.55 Feature: data_cubby.clear() method to reset all data and re-initialize class instances with empty arrays"

# Print the version and commit message
print(f"""
🤖 Plotbot Initialized
📈📉 Multiplot Initialized
   Version: {__version__}
   Commit: {__commit_message__}
""")

# END IMPORT TIMING AND GENERATE REPORT
end_timing()

# Note: Previous logic had this at the end of plotbot_main.py, moved here 
#       to ensure it prints after all imports in __init__ are processed.