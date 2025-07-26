import matplotlib.pyplot as mpl_plt
import os
import importlib
from pathlib import Path
import sys

from .print_manager import print_manager
from .data_cubby import data_cubby

# --- Import all data class instances for registration ---
from .data_classes.psp_mag_rtn_4sa import mag_rtn_4sa
from .data_classes.psp_mag_rtn import mag_rtn
from .data_classes.psp_mag_sc_4sa import mag_sc_4sa
from .data_classes.psp_mag_sc import mag_sc
from .data_classes.psp_electron_classes import epad, epad_hr
from .data_classes.psp_proton import proton
from .data_classes.psp_proton_hr import proton_hr
from .data_classes.psp_proton_fits_classes import proton_fits
from .data_classes.psp_alpha_fits_classes import alpha_fits
from .data_classes.psp_ham_classes import ham
from .data_classes.wind_mfi_classes import wind_mfi_h2
from .data_classes.wind_3dp_classes import wind_3dp_elpd
from .data_classes.wind_swe_h5_classes import wind_swe_h5
from .data_classes.wind_swe_h1_classes import wind_swe_h1
from .data_classes.wind_3dp_pm_classes import wind_3dp_pm
from .data_classes.psp_alpha_classes import psp_alpha
from .data_classes.psp_qtn_classes import psp_qtn
from .data_classes.psp_dfb_classes import psp_dfb
from .data_classes.psp_orbit import psp_orbit

# Keep track of initialization status
_is_initialized = False

def initialize():
    """
    Initializes the plotbot application. This function is called on package import.
    """
    global _is_initialized
    if _is_initialized:
        return

    def _auto_register_custom_classes():
        """
        Scans for custom classes, registers them with DataCubby,
        and injects them into the main plotbot module's namespace.
        """
        try:
            plotbot_module = sys.modules['plotbot']
        except KeyError:
            print_manager.warning("Could not find 'plotbot' module in sys.modules for auto-registration.")
            return

        custom_classes_dir = Path(__file__).parent / "data_classes" / "custom_classes"
        
        if not custom_classes_dir.exists():
            return
        
        for py_file in custom_classes_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            module_name = py_file.stem
            try:
                module = importlib.import_module(f"plotbot.data_classes.custom_classes.{module_name}")
                
                if hasattr(module, module_name):
                    class_instance = getattr(module, module_name)
                    data_cubby.stash(class_instance, class_name=module_name)
                    
                    plotbot_module.__dict__[module_name] = class_instance
                    if module_name not in plotbot_module.__all__:
                        plotbot_module.__all__.append(module_name)
                    
            except Exception as e:
                print_manager.warning(f"Failed to auto-register {module_name}: {e}")

    # --- Matplotlib Configuration ---
    mpl_plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'sans-serif'],
        'axes.labelweight': 'normal',
        'font.weight': 'normal',
        'mathtext.fontset': 'stix',
        'mathtext.default': 'regular'
    })

    # --- Data Registration ---
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
    data_cubby.stash(wind_mfi_h2, class_name='wind_mfi_h2')
    data_cubby.stash(wind_3dp_elpd, class_name='wind_3dp_elpd')
    data_cubby.stash(wind_3dp_pm, class_name='wind_3dp_pm')
    data_cubby.stash(psp_alpha, class_name='psp_alpha')
    data_cubby.stash(wind_swe_h5, class_name='wind_swe_h5')
    data_cubby.stash(wind_swe_h1, class_name='wind_swe_h1')
    data_cubby.stash(psp_qtn, class_name='psp_qtn')
    data_cubby.stash(psp_dfb, class_name='psp_dfb')
    data_cubby.stash(psp_orbit, class_name='psp_orbit')
    data_cubby.stash(psp_dfb, class_name='dfb_ac_spec_dv12hg')
    data_cubby.stash(psp_dfb, class_name='dfb_ac_spec_dv34hg')
    data_cubby.stash(psp_dfb, class_name='dfb_dc_spec_dv12hg')

    # --- Auto-register custom classes ---
    _auto_register_custom_classes()

    # --- Version printing ---
    from . import __version__, __commit_message__
    print(f"""
🤖 Plotbot Initialized
📈📉 Multiplot Initialized
   Version: {__version__}
   Commit: {__commit_message__}
""")

    _is_initialized = True 