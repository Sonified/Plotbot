# Plotbot Package - Main import file
# This file allows users to do "import plotbot" and get access to all components

# Import main function
from plotbot_main import plotbot

# Import frequently used modules for convenient access
from print_manager import print_manager
from server_access import server_access
from data_tracker import global_tracker
from ploptions import ploptions

# Import data classes
from psp_mag_classes import mag_rtn_4sa, mag_rtn, mag_sc_4sa, mag_sc
from psp_electron_classes import epad
from psp_proton_classes import proton

# Re-export everything
__all__ = [
    'plotbot',
    'print_manager',
    'server_access',
    'global_tracker',
    'ploptions',
    'mag_rtn_4sa',
    'mag_rtn',
    'mag_sc_4sa',
    'mag_sc',
    'epad',
    'proton'
]

# Display Plotbot banner with version and commit info
print(colored("🤖 Plotbot Initialized", "blue"))