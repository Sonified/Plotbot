"""
Plotbot V3: Hierarchical Modular Architecture

This package contains the revolutionary hierarchical modular architecture
for space physics data analysis.

Key Components:
- dynamic_class_test: Core dynamic class factory
- wind_mag_poc: WIND satellite proof of concept  
- modular_cdf_processor: Universal CDF processing
- plotbot_wind_integration: Integration bridge
"""

# Make key components easily accessible
from .dynamic_class_test import create_data_class
from .wind_mag_poc import get_wind_data, wind_mfi_metadata
from .modular_cdf_processor import CDFProcessor

__version__ = "3.0.0-dev"
__author__ = "Plotbot Development Team"

__all__ = [
    'create_data_class',
    'get_wind_data', 
    'wind_mfi_metadata',
    'CDFProcessor'
] 