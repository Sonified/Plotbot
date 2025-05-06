# Plotbot Package - Main import file
# This file allows users to do "import plotbot" and get access to all components

# Import main function
from plotbot_main import plotbot

# Import frequently used modules for convenient access
from print_manager import print_manager
from server_access import server_access
from .data_tracker import global_tracker
from ploptions import ploptions
from .data_cubby import data_cubby

# Import helper functions
# ... existing code ...

# Re-export everything
__all__ = [
    'plotbot',
    'print_manager',
    'server_access',
    'global_tracker',
    'ploptions',
    'data_cubby'
]

# Display Plotbot banner with version and commit info
print(colored("🤖 Plotbot Initialized", "blue"))
