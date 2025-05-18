import numpy as np
import types
import pathlib
import pytest
import matplotlib.pyplot as plt
from datetime import datetime
from plotbot import mag_rtn_4sa_class

# Import plotbot and mag_rtn_4sa for integration test
try:
    from plotbot import mag_rtn_4sa, plt as plotbot_plt
    from plotbot.plotbot_main import plotbot
except ImportError as e:
    mag_rtn_4sa = None
    plotbot = None
    plotbot_plt = plt

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
def test_plotbot_br_norm_smoke():
    """Integration test: plot mag_rtn_4sa.br_norm with plotbot and check for figure."""
    if mag_rtn_4sa is None or plotbot is None:
        pytest.skip("Plotbot or mag_rtn_4sa not importable.")
    # Use a short time range for speed
    TRANGE = ['2023-09-28/06:00:00.000', '2023-09-28/07:00:00.000']
    plotbot_plt.close('all')
    fig = None
    try:
        # Plot br_norm using plotbot
        plotbot(TRANGE, mag_rtn_4sa.br_norm, 1)
        # Check if a figure was created
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        assert fig is not None, "plotbot should have created a figure for br_norm."
    finally:
        if fig is not None:
            plotbot_plt.close(fig)
        else:
            plotbot_plt.close('all') 