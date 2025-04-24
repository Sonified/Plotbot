# plotbot/config.py
"""
Global configuration settings for Plotbot.
"""

# --- Data Server Selection ---
data_server = 'dynamic'
"""
Controls which data source is prioritized.
Options:
    'dynamic': (Default) Try SPDF/CDAWeb first via pyspedas.
               If data is unavailable there, fall back to Berkeley server.
    'spdf':    Use SPDF/CDAWeb (pyspedas) exclusively. No fallback.
    'berkeley': Use Berkeley server exclusively. No pyspedas calls.
"""

# --- Other Future Configuration Settings Can Go Here --- 