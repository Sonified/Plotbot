# To run tests from the project root directory:
# conda run -n plotbot_env python -m pytest tests/test_all_plot_basics.py -vv
# To run a specific test (e.g., test_plotbot_basic):
# conda run -n plotbot_env python -m pytest tests/test_all_plot_basics.py::test_plotbot_basic -vv

"""
Basic smoke tests for core plotting functions (plotbot, multiplot, showdahodo).
Designed to be lightning fast using only mag_rtn_4sa data for a short interval.
"""
import pytest
import os
import sys
import matplotlib.pyplot as plt
import numpy as np # Added numpy import
from datetime import datetime

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import plotbot components safely
try:
    from plotbot import mag_rtn_4sa, plt as plotbot_plt # Use plotbot's plt for options
    from plotbot.plotbot_main import plotbot
    from plotbot.multiplot import multiplot
    from plotbot.showdahodo import showdahodo
    from plotbot.test_pilot import phase, system_check
    from plotbot.print_manager import print_manager
except ImportError as e:
    print(f"Failed to import Plotbot components: {e}")
    # Define dummy functions if imports fail to allow file parsing
    def plotbot(*args, **kwargs): pass
    def multiplot(*args, **kwargs): pass
    def showdahodo(*args, **kwargs): pass
    class dummy_plt:
        class options:
            def reset(self): pass
        def close(self, *args): pass
        # Add dummy Axes for isinstance check
        class Axes: pass
    plotbot_plt = dummy_plt()
    class dummy_mag:
        br = None; bt = None; bn = None
    mag_rtn_4sa = dummy_mag()

# --- Test Configuration ---
# Use the date from pyspedas tests, but only for 1 hour
TRANGE = ['2023-09-28/06:00:00.000', '2023-09-28/07:00:00.000']
# Center time for multiplot (within the TRANGE)
CENTER_TIME = '2023-09-28/06:30:00.000'

@pytest.fixture(autouse=True)
def setup_test():
    """Ensure plots are closed before and after each test."""
    plotbot_plt.close('all')
    yield
    plotbot_plt.close('all')

@pytest.mark.mission("Basic Plotbot Test (mag_rtn_4sa)")
def test_plotbot_basic():
    """Basic test for plotbot with mag_rtn_4sa data."""
    # print_manager.enable_debug() # Temporarily enable full debug output
    print("\n=== Testing plotbot ===")
    fig = None # Initialize fig to None
    try:
        phase(1, "Calling plotbot with Br, Bt, Bn")
        # plotbot_plt.options.reset() # Reset options if needed
        # plotbot calls plt.show() and doesn't return fig/axs
        plotbot(TRANGE,
                mag_rtn_4sa.br, 1,
                mag_rtn_4sa.bt, 2,
                mag_rtn_4sa.bn, 3)

        phase(2, "Verifying plotbot call completed")
        # Check if any figures were created by plotbot (indirect check)
        fig_num = plt.gcf().number # Get the current figure number
        fig = plt.figure(fig_num) # Get the figure object itself

        system_check("Plotbot Call Completed", True, "plotbot call should complete without error.")
        system_check("Plotbot Figure Exists (Indirect Check)", fig is not None and fig_num is not None, "plotbot should have created a figure.")

    except Exception as e:
        pytest.fail(f"Plotbot test failed: {e}")
    finally:
        # Ensure we attempt to close even if verification failed slightly
        if fig is not None:
             plotbot_plt.close(fig)
        else:
             # If we couldn't get fig, close all as a fallback
             plotbot_plt.close('all')

@pytest.mark.mission("Basic Multiplot Test (mag_rtn_4sa)")
def test_multiplot_basic():
    """Basic test for multiplot with mag_rtn_4sa data."""
    print("\n=== Testing multiplot ===")
    fig = None # Initialize fig to None
    axs = None # Initialize axs
    try:
        phase(1, "Setting up multiplot options")
        plotbot_plt.options.reset()
        plotbot_plt.options.window = '1:00:00.000' # Match TRANGE duration
        plotbot_plt.options.position = 'around'
        plotbot_plt.options.use_single_title = True
        plotbot_plt.options.single_title_text = "Multiplot Basic Test"

        phase(2, "Defining plot data and calling multiplot")
        # Multiplot expects a list of (center_time, variable) tuples
        # Only one unique center_time is provided, so only ONE axis (panel) is expected.
        plot_data = [
            (CENTER_TIME, mag_rtn_4sa.br),
            (CENTER_TIME, mag_rtn_4sa.bt),
            (CENTER_TIME, mag_rtn_4sa.bn)
        ]
        fig, axs = multiplot(plot_data)
        print(f"DEBUG: Type of axs returned by multiplot: {type(axs)}")

        phase(3, "Verifying multiplot output")
        system_check("Multiplot Figure Created", fig is not None, "multiplot should return a figure object.")

        # Check if axs was returned and seems valid (either single Axes or list/array)
        axes_valid = False
        if axs is not None:
            try:
                # Check if it behaves like a list/array of Axes
                if hasattr(axs, '__len__') and len(axs) > 0 and isinstance(axs[0], plt.Axes):
                    axes_valid = True
                # Check if it behaves like a single Axes object
                elif isinstance(axs, plt.Axes):
                    axes_valid = True
            except Exception as e:
                 print(f"DEBUG: Error checking axs type: {e}") # Debug potential errors during check
                 axes_valid = False # Assume invalid if check fails

        system_check("Multiplot Axes Returned", axes_valid, f"multiplot should return valid Axes object(s). Got type: {type(axs)}")

    except Exception as e:
        pytest.fail(f"Multiplot test failed: {e}")
    finally:
        if fig is not None:
            plotbot_plt.close(fig)

@pytest.mark.mission("Basic Showdahodo Test (mag_rtn_4sa)")
def test_showdahodo_basic():
    """Basic test for showdahodo with mag_rtn_4sa data."""
    print("\n=== Testing showdahodo ===")
    fig = None # Initialize fig to None
    try:
        phase(1, "Calling showdahodo with Bt vs Br")
        # showdahodo uses a direct time range
        fig, ax = showdahodo(TRANGE, mag_rtn_4sa.bt, mag_rtn_4sa.br) # X = Bt, Y = Br

        phase(2, "Verifying showdahodo output")
        system_check("Showdahodo Figure Created", fig is not None, "showdahodo should return a figure object.")
        system_check("Showdahodo Axis Created", ax is not None, "showdahodo should return an axis object.")
        # Add more specific checks if needed

    except Exception as e:
        pytest.fail(f"Showdahodo test failed: {e}")
    finally:
        if fig is not None:
            plotbot_plt.close(fig)

# Allow running the test directly
if __name__ == "__main__":
    print("Running basic plot tests directly...")
    pytest.main(['-v', '-s', __file__])
    print("Finished running basic plot tests.") 