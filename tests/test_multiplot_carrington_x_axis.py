import pytest
from plotbot import *

# Use the same fixture as in test_stardust.py to ensure plots are closed before/after
def setup_module(module):
    plt.close('all')
def teardown_module(module):
    plt.close('all')

@pytest.mark.mission("Multiplot Carrington Longitude X-Axis Test")
def test_multiplot_carrington_x_axis():
    """Test multiplot with Carrington longitude as the x-axis."""
    print_manager.enable_debug()
    plt.options.reset()
    plt.options.x_axis_carrington_lon = True
    plt.options.use_single_title = True
    plt.options.use_single_x_axis = True
    plt.options.window = '12:00:00.000'
    plt.options.position = 'around'
    plt.options.color_mode = 'default'
    plt.options.use_relative_time = False
    plt.options.x_axis_carrington_lat = False
    plt.options.x_axis_r_sun = False
    plt.options.use_degrees_from_perihelion = False
    # Use a short, known time range for test
    base_date = '2025-03-20/12:00:00.000'
    plot_variable = mag_rtn_4sa.br
    # Build plot_data for 3 consecutive days
    from datetime import datetime, timedelta
    base_dt = datetime.strptime(base_date, '%Y-%m-%d/%H:%M:%S.%f')
    plot_data = []
    for i in range(3):
        dt = base_dt + timedelta(days=i)
        plot_data.append((dt.strftime('%Y-%m-%d/%H:%M:%S.%f'), plot_variable))
    # Call multiplot
    fig, axs = multiplot(plot_data)
    # Check that figure and axes are created
    assert fig is not None, "multiplot should return a figure object."
    assert axs is not None, "multiplot should return axes."
    # Check that the x-axis label is Carrington Longitude (°) on the bottom axis
    x_label = axs[-1].get_xlabel()
    assert 'Carrington Longitude' in x_label, f"Expected Carrington Longitude in x-axis label, got: {x_label}"
    # Show the figure instead of closing it
    print("Showing multiplot with Carrington longitude x-axis. Close the plot window to continue the test.")
    plt.show()
    print_manager.show_debug = False 