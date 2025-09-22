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
        # --- Data Directory Configuration ---
        # With lazy loading, this can be set anytime before pyspedas functions are used
        # CRITICAL FIX: Use absolute path to work correctly from any subdirectory
        self._data_dir = self._get_default_data_dir()  # Private attribute, use property for public access
        """
        Base directory for all data downloads. Both PySpedas and Berkeley downloads
        will use this directory. PySpedas will create subdirectories within this path 
        for different missions (e.g., {data_dir}/psp/, {data_dir}/wind/).
        
        With lazy loading, this can be changed anytime before calling VDF functions.
        The environment variable is only set when the user explicitly changes data_dir.
        """
        
        # DO NOT set environment variable on init - true lazy loading!
        
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

    @property
    def data_dir(self):
        """
        Get the current data directory path.
        
        Returns:
            str: Current data directory path
        """
        return self._data_dir
    
    @data_dir.setter 
    def data_dir(self, value):
        """
        Set the data directory path and automatically configure pyspedas.
        
        This setter automatically updates the SPEDAS_DATA_DIR environment variable
        so that when pyspedas is eventually loaded (lazy loading), it will use 
        the correct data directory.
        
        Args:
            value (str): New data directory path, or 'default' for original behavior
        """
        if value == 'default':
            new_dir = 'data'
        else:
            new_dir = value
            
        old_dir = self._data_dir
        self._data_dir = new_dir
        
        # Immediately update PySpedas configuration
        self._configure_pyspedas_data_directory()
        
        # User feedback
        if old_dir != new_dir:
            print(f"📁 Plotbot data directory changed: {old_dir} → {new_dir}")
            print(f"🔧 SPEDAS_DATA_DIR updated for pyspedas compatibility")
    
    @property
    def pyspedas_data_dir(self):
        """
        Legacy property for backwards compatibility.
        Returns the current data_dir value.
        """
        return self._data_dir

    def _configure_pyspedas_data_directory(self):
        """
        Configure PySpedas data directory via environment variable.
        
        With lazy loading, this can be called anytime before pyspedas functions
        are used. The environment variable will be read when pyspedas is imported.
        """
        # Convert to absolute path to ensure PySpedas uses the correct directory
        # regardless of the current working directory
        abs_data_dir = os.path.abspath(self._data_dir)
        os.environ['SPEDAS_DATA_DIR'] = abs_data_dir
        
        # Create the directory if it doesn't exist
        os.makedirs(abs_data_dir, exist_ok=True)
        
    def _get_default_data_dir(self):
        """
        Get the default data directory as an absolute path relative to the project root.
        
        This ensures the data directory works correctly regardless of which subdirectory
        the code is run from (e.g., running from example_notebooks/).
        
        Returns:
            str: Absolute path to the default data directory
        """
        try:
            # Get the directory containing this file (plotbot/config.py)
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to get the project root (from plotbot/ to Plotbot/)
            project_root = os.path.dirname(current_file_dir)
            # Return absolute path to data directory
            return os.path.join(project_root, 'data')
        except Exception:
            # Fallback: use 'data' relative to current working directory
            return 'data'
        
# --- Other Future Configuration Settings Can Go Here --- 
        # Example: self.default_plot_style = 'seaborn-v0_8-darkgrid'

# Create a single, global instance of the configuration
# This will automatically set the PySpedas data directory
config = PlotbotConfig() 