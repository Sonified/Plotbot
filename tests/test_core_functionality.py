"""
Tests for core plotbot package functionality.

These tests should be run using 'conda run' within the 'plotbot_env' environment.

This file checks basic aspects like package initialization.

NOTES ON TEST OUTPUT:
- Use print_manager.test() for any debug information you want to see in test output
- Use print_manager.debug() for developer-level debugging details
- To see all print statements in test output, add the -s flag when running pytest:
  e.g., cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_core_functionality.py -v -s

To run all tests in this file:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_core_functionality.py -v

To run a specific test:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_core_functionality.py::test_plotbot_initialization_and_exports -v
"""

import pytest
import importlib

def test_plotbot_initialization_and_exports():
    """Tests if plotbot imports and if names in __all__ are accessible."""
    missing_exports = []
    try:
        # Step 1: Test basic import
        plotbot = importlib.import_module('plotbot')
        assert plotbot is not None, "Failed to import plotbot package."

        # Step 2: Check if __all__ is defined and is a list
        assert hasattr(plotbot, '__all__'), "plotbot package does not define __all__."
        assert isinstance(plotbot.__all__, list), "plotbot.__all__ is not a list."

        # Step 3: Check if all names in __all__ exist as attributes
        for name in plotbot.__all__:
            if not hasattr(plotbot, name):
                missing_exports.append(name)

        assert not missing_exports, f"Names in plotbot.__all__ not found as attributes: {', '.join(missing_exports)}"

    except ImportError as e:
        pytest.fail(f"Plotbot package failed during import: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during plotbot import/check: {e}")