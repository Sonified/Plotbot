import numpy as np
import types
import pathlib
import pytest
import matplotlib.pyplot as plt
from datetime import datetime
import os
import sys

from plotbot import mag_rtn_4sa_class
from plotbot.print_manager import print_manager

# Enable dependency management prints
print_manager.show_dependency_management = True

# Import plotbot, mag_rtn_4sa, and proton for integration test
try:
    from plotbot import mag_rtn_4sa, proton, plt as plotbot_plt, plotbot
except ImportError as e:
    mag_rtn_4sa = None
    proton = None
    plotbot = None
    plotbot_plt = plt

# Path for the log file
log_file = os.path.join(os.path.dirname(__file__), "test_logs", "test_psp_mag_br_norm.txt")

def test_mag_rtn_4sa_br_norm_initialization():
    # Try to use real Parker_positional_data.npz if available
    npz_path = pathlib.Path(__file__).parent.parent / "support_data" / "trajectories" / "Parker_positional_data.npz"
    if not npz_path.exists():
        pytest.skip(f"Parker_positional_data.npz not found at {npz_path}, skipping real Rsun test.")

    # Load Rsun times and values
    with np.load(npz_path) as data:
        times = data['times']
        r_sun = data['r_sun']
        # Use the first two times for a minimal test
        test_times = times[:2]
        # Create fake mag data for those times
        mag_data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])

    class MockImportedData:
        def __init__(self):
            self.times = test_times
            self.data = {'psp_fld_l2_mag_RTN_4_Sa_per_Cyc': mag_data}

    imported_data = MockImportedData()
    mag = mag_rtn_4sa_class(imported_data)

    # Check that br_norm attribute exists and is a plot_manager (or at least not None)
    assert hasattr(mag, 'br_norm'), "mag_rtn_4sa_class should have a 'br_norm' attribute"
    assert mag.br_norm is not None, "mag_rtn_4sa_class.br_norm should not be None"

    # Check that raw_data['br_norm'] exists and is a numpy array
    assert 'br_norm' in mag.raw_data, "'br_norm' should be in mag_rtn_4sa_class.raw_data"
    assert isinstance(mag.raw_data['br_norm'], np.ndarray), "mag_rtn_4sa_class.raw_data['br_norm'] should be a numpy array"

    # Assert that at least one value is not NaN (i.e., Rsun interpolation worked)
    assert np.any(~np.isnan(mag.raw_data['br_norm'])), "br_norm should contain at least one non-NaN value when Rsun data is available"

    # Print for debug
    print("br_norm array:", mag.raw_data['br_norm'])
    print("br_norm plot_manager:", mag.br_norm)

@pytest.mark.mission("Plotbot Integration Test (br_norm)")
def test_plotbot_br_norm_smoke(capsys):
    """Integration test: plot mag_rtn_4sa.br_norm with plotbot and check for figure AND data."""
    print_manager.show_debug = True # Enable debug prints for this test
    if mag_rtn_4sa is None or proton is None or plotbot is None:
        pytest.skip("Plotbot, mag_rtn_4sa, or proton not importable.")
    
    TRANGE = ['2023-09-28/00:00:00.000', '2023-09-29/00:00:00.000'] # 1 day
    plotbot_plt.close('all')
    fig = None
    
    print(f"\nRequesting plots for trange: {TRANGE}")
    print("Panel 1: mag_rtn_4sa.br")
    print("Panel 2: proton.sun_dist_rsun")
    print("Panel 3: mag_rtn_4sa.br_norm")

    try:
        plotbot(TRANGE, mag_rtn_4sa.br, 1, proton.sun_dist_rsun, 2, mag_rtn_4sa.br_norm, 3)
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        assert fig is not None, "plotbot should have created a figure."
        assert len(fig.axes) == 3, "Figure should have 3 panels for the 3 variables."

        # === Data Verification (focus on br_norm as it's the most complex) ===
        print("\nVerifying data in mag_rtn_4sa.br_norm...")
        assert hasattr(mag_rtn_4sa, 'br_norm'), "mag_rtn_4sa instance should have 'br_norm' attribute."
        br_norm_attr = mag_rtn_4sa.br_norm 
        assert br_norm_attr is not None, "mag_rtn_4sa.br_norm should not be None."
        assert hasattr(br_norm_attr, 'data'), "mag_rtn_4sa.br_norm should have a '.data' attribute."
        br_norm_data_content = br_norm_attr.data
        assert br_norm_data_content is not None, "mag_rtn_4sa.br_norm.data should not be None."
        assert isinstance(br_norm_data_content, np.ndarray), "mag_rtn_4sa.br_norm.data should be a numpy array."
        assert len(br_norm_data_content) > 0, "mag_rtn_4sa.br_norm.data should not be empty."
        print(f"mag_rtn_4sa.br_norm.data shape: {br_norm_data_content.shape}")
        print(f"mag_rtn_4sa.br_norm.data head: {br_norm_data_content[:5]}")
        print("test_plotbot_br_norm_smoke: Successfully verified data in mag_rtn_4sa.br_norm")
        # === End Data Verification ===

    except AttributeError as ae:
        print(f"AttributeError during test_plotbot_br_norm_smoke: {ae}. This likely means br_norm is not accessible.")
        pytest.fail(f"AttributeError during test_plotbot_br_norm_smoke: {ae}. This likely means br_norm is not accessible.")
    except Exception as e:
        print(f"Error during test_plotbot_br_norm_smoke: {e}")
        pytest.fail(f"Error during test_plotbot_br_norm_smoke: {e}")
    finally:
        if fig is not None:
            plotbot_plt.close(fig)
        else:
            plotbot_plt.close('all')
        # Capture all output
        out, err = capsys.readouterr()

        # First, print to console (so tee can capture it if active)
        if out:
            print("\n=== CAPTURED STDOUT (via print) ===\n", out)
        if err:
            print("\n=== CAPTURED STDERR (via print) ===\n", err, file=sys.stderr) # Print errors to stderr

        # Then, write to the dedicated log file
        with open(log_file, "a") as f:
            f.write("\n=== CAPTURED STDOUT (direct write) ===\n")
            f.write(out)
            f.write("\n=== CAPTURED STDERR (direct write) ===\n")
            f.write(err)
            f.write("\n=== END CAPSYS BLOCK ===\n")

@pytest.mark.mission("Plotbot Data Verification (mag_rtn_4sa.br)")
def test_plotbot_br_data_verification():
    """Test that mag_rtn_4sa.br returns actual data when plotted with plotbot."""
    if mag_rtn_4sa is None or plotbot is None:
        pytest.skip("Plotbot or mag_rtn_4sa not importable for data verification test.")
    
    TRANGE = ['2023-09-28/06:00:00.000', '2023-09-28/07:00:00.000']
    plotbot_plt.close('all') # Close any existing plots
    
    print(f"\nRequesting mag_rtn_4sa.br for trange: {TRANGE}")
    
    try:
        # Request plotbot to load/plot the data
        plotbot(TRANGE, mag_rtn_4sa.br, 1) # Panel 1
        
        # Verify data presence
        assert hasattr(mag_rtn_4sa, 'br'), "mag_rtn_4sa instance should have 'br' attribute after plotbot call."
        assert mag_rtn_4sa.br is not None, "mag_rtn_4sa.br should not be None."
        
        # Crucially, check the .data attribute as per plot_manager.py
        assert hasattr(mag_rtn_4sa.br, 'data'), "mag_rtn_4sa.br should have a '.data' attribute."
        br_data_content = mag_rtn_4sa.br.data
        assert br_data_content is not None, "mag_rtn_4sa.br.data should not be None."
        
        # Check that data has content
        assert isinstance(br_data_content, np.ndarray), "mag_rtn_4sa.br.data should be a numpy array."
        assert len(br_data_content) > 0, "mag_rtn_4sa.br.data should not be empty."
        
        print(f"mag_rtn_4sa.br.data shape: {br_data_content.shape}")
        print(f"mag_rtn_4sa.br.data head: {br_data_content[:5]}")
        
        print("test_plotbot_br_data_verification: Successfully verified data in mag_rtn_4sa.br")
        
    except Exception as e:
        print(f"Error during test_plotbot_br_data_verification: {e}")
        pytest.fail(f"Error during test_plotbot_br_data_verification: {e}")
    finally:
        plotbot_plt.close('all') # Clean up plots 