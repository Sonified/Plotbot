# plotbot/config.py
"""
Global configuration settings for Plotbot.
"""

class PlotbotConfig:
    """
    Manages global configuration settings for Plotbot.
    """
    def __init__(self):
# --- Data Server Selection ---
        self.data_server = 'dynamic'
"""
Controls which data source is prioritized.
Options:
    'dynamic': (Default) Try SPDF/CDAWeb first via pyspedas.
               If data is unavailable there, fall back to Berkeley server.
    'spdf':    Use SPDF/CDAWeb (pyspedas) exclusively. No fallback.
    'berkeley': Use Berkeley server exclusively. No pyspedas calls.
"""

# --- Other Future Configuration Settings Can Go Here --- 
        # Example: self.default_plot_style = 'seaborn-v0_8-darkgrid'

# Create a single, global instance of the configuration
config = PlotbotConfig() 