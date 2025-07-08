# plotbot/config.py
"""
Global configuration settings for Plotbot.
"""
import os

class PlotbotConfig:
    """
    Manages global configuration settings for Plotbot.
    """
    def __init__(self):
        # --- PySpedas Data Directory Configuration ---
        # CRITICAL: Must be set BEFORE pyspedas is imported anywhere
        # PySpedas caches configuration at import time, so environment variables
        # set after import have no effect
        self.pyspedas_data_dir = 'data'
        """
        Base directory for PySpedas downloads. PySpedas will create subdirectories
        within this path for different missions (e.g., data/psp/, data/wind/).
        This must be set before pyspedas is imported anywhere in the codebase.
        """
        
        # Apply the PySpedas configuration immediately
        self._configure_pyspedas_data_directory()
        
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

        # --- Plot Display Control ---
        self.suppress_plots = False
        """If True, plotbot() will skip calling plt.show(). Useful for tests."""

    def _configure_pyspedas_data_directory(self):
        """
        Configure PySpedas data directory via environment variable.
        MUST be called before pyspedas is imported anywhere.
        """
        os.environ['SPEDAS_DATA_DIR'] = self.pyspedas_data_dir
        
# --- Other Future Configuration Settings Can Go Here --- 
        # Example: self.default_plot_style = 'seaborn-v0_8-darkgrid'

# Create a single, global instance of the configuration
# This will automatically set the PySpedas data directory
config = PlotbotConfig() 