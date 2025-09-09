# Stubs for plotbot.config
# -*- coding: utf-8 -*-

from typing import Optional, Any

# --- PlotbotConfig Class ---
class PlotbotConfig:
    # --- Public Attributes (with type hints) ---
    data_server: str # Options: 'dynamic', 'spdf', 'berkeley'
    data_dir: str # Configurable data directory path
    suppress_plots: bool # Plot display control
    pyspedas_data_dir: str # Legacy property for backwards compatibility
    # Add hints for any other future config attributes here
    # Example: default_plot_style: Optional[str]

    # --- Methods ---
    def __init__(self) -> None: ...

# --- Module-level Instances ---
config: PlotbotConfig

# Reminder: If you add functions or classes directly to the .py file, add their signatures here too, ending with '...'.
