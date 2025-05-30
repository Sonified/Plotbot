# To run tests from the project root directory and see print output in the console:
# conda run -n plotbot_env python -m pytest tests/test_showdahodo.py -vv -s
# To run a specific test (e.g., test_single_custom_variable) and see print output:
# conda run -n plotbot_env python -m pytest tests/test_showdahodo.py::test_single_custom_variable -vv -s
# The '-s' flag ensures that print statements are shown in the console during test execution.

"""
Tests for showdahodo (hodogram) functionality in Plotbot.

This file contains tests for creating and manipulating hodogram plots,
including tests for single and dual custom variables.

NOTES ON TEST OUTPUT:
- Use print_manager.test() for any debug information you want to see in test output
- Use print_manager.debug() for developer-level debugging details
- To see all print statements in test output, add the -s flag when running pytest:
  e.g., cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_showdahodo.py -v -s

To run all tests in this file:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_showdahodo.py -v

To run a specific test:
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_showdahodo.py::test_single_custom_variable -v
"""
import pytest
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add parent directory to path to import plotbot modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plotbot import mag_rtn_4sa, proton, epad, proton_fits
from plotbot.data_classes.custom_variables import custom_variable
from plotbot.showdahodo import showdahodo
from plotbot.test_pilot import phase, system_check
from plotbot.print_manager import print_manager
from plotbot.data_cubby import data_cubby

@pytest.fixture
def test_environment():
    """Setup and teardown for tests"""
    # Enable test output mode
    print_manager.enable_test()
    print_manager.enable_debug()
    
    # Standard time range for all tests - same as in the Jupyter notebook example
    trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
    
    # Print the time range for debugging
    print_manager.debug(f"Test time range: {trange}")
    print_manager.debug(f"Time range type: {type(trange)}")
    print_manager.debug(f"Start time: {trange[0]}, type: {type(trange[0])}")
    print_manager.debug(f"End time: {trange[1]}, type: {type(trange[1])}")
    
    # Verify time range format
    try:
        start_dt = datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f')
        end_dt = datetime.strptime(trange[1], '%Y-%m-%d/%H:%M:%S.%f')
        print_manager.debug(f"Parsed start time: {start_dt}")
        print_manager.debug(f"Parsed end time: {end_dt}")
        print_manager.debug("Time range format is valid")
    except ValueError as e:
        print_manager.debug(f"Time range format validation error: {str(e)}")
    
    yield trange
    
    # Cleanup - close all plots
    plt.close('all')

def verify_plot_has_data(fig, ax):
    """Verify that the provided plot contains actual data points"""
    # Get all children of the axis
    children = ax.get_children()
    
    # Find scatter plots in the children
    scatter_plots = [child for child in children if isinstance(child, plt.matplotlib.collections.PathCollection)]
    
    # Debug info about collected plots
    print_manager.debug(f"Found {len(scatter_plots)} scatter plot collections")
    
    # Check if any scatter plots have data points
    has_data = False
    for i, scatter in enumerate(scatter_plots):
        # Get the paths in the scatter plot
        paths = scatter.get_paths()
        print_manager.debug(f"Scatter plot {i+1} has {len(paths)} data points")
        if len(paths) > 0:
            has_data = True
            break
    
    # Enhanced colorbar detection - check multiple ways
    has_colorbar = False
    
    # Method 1: Check direct children of figure
    for child in fig.get_children():
        if isinstance(child, plt.matplotlib.colorbar.Colorbar):
            has_colorbar = True
            print_manager.debug("Found colorbar in figure children")
            break
    
    # Method 2: Check axes in the figure
    if not has_colorbar:
        for ax_obj in fig.axes:
            if hasattr(ax_obj, 'colorbar') and ax_obj.colorbar is not None:
                has_colorbar = True
                print_manager.debug("Found colorbar via axes.colorbar property")
                break
            if isinstance(ax_obj, plt.matplotlib.colorbar.ColorbarBase):
                has_colorbar = True
                print_manager.debug("Found ColorbarBase axes")
                break
    
    # Method 3: Check if there are multiple axes (main plot + colorbar)
    if not has_colorbar and len(fig.axes) > 1:
        print_manager.debug(f"Multiple axes found ({len(fig.axes)}), assuming one is a colorbar")
        has_colorbar = True
    
    print_manager.debug(f"Plot has colorbar: {has_colorbar}")
    
    return has_data, has_colorbar, len(scatter_plots)

def get_colorbar(fig):
    """Helper function to get the colorbar from a figure"""
    for ax in fig.axes:
        if isinstance(ax, plt.matplotlib.colorbar.Colorbar):
            return ax
    return None

@pytest.mark.mission("Basic Showdahodo Functionality")
def test_basic_functionality(test_environment):
    """Test the basic functionality of showdahodo with standard variables"""
    
    print("\n================================================================================")
    print("TEST #1: Basic Showdahodo Functionality")
    print("Verifies that showdahodo works with standard variables")
    print("================================================================================\n")
    
    # Get the time range from the fixture
    trange = test_environment
    
    # Additional debugging for trange format
    print_manager.debug(f"Test time range: {trange}")
    print_manager.debug(f"Time range type: {type(trange)}")
    print_manager.debug(f"Start time: {trange[0]}, type: {type(trange[0])}")
    print_manager.debug(f"End time: {trange[1]}, type: {type(trange[1])}")
    
    phase(1, "Creating basic hodogram plot")
    # Create a basic hodogram plot with standard variables
    print_manager.debug("About to call showdahodo with standard variables")
    fig, ax = showdahodo(trange, mag_rtn_4sa.br, epad.centroids)
    print_manager.debug("Showdahodo call completed")
    
    # Verify plot was created
    system_check(
        "Plot Creation",
        fig is not None and ax is not None,
        "Showdahodo should return figure and axis objects"
    )
    
    # Verify plot has data
    has_data, has_colorbar, scatter_count = verify_plot_has_data(fig, ax)
    
    system_check(
        "Plot Data Verification",
        has_data,
        f"Plot should contain data points. Found: {scatter_count} scatter collections with data: {has_data}"
    )
    
    system_check(
        "Colorbar Verification",
        has_colorbar,
        "Plot should have a colorbar"
    )
    
    # Verify axis labels are set correctly
    system_check(
        "X-Axis Label",
        ax.get_xlabel() == mag_rtn_4sa.br.legend_label,
        f"X-axis label should be '{mag_rtn_4sa.br.legend_label}', found '{ax.get_xlabel()}'"
    )
    
    system_check(
        "Y-Axis Label",
        ax.get_ylabel() == epad.centroids.legend_label,
        f"Y-axis label should be '{epad.centroids.legend_label}', found '{ax.get_ylabel()}'"
    )
    
    # Verify title contains the time range
    title = ax.get_title()
    system_check(
        "Plot Title",
        trange[0] in title and trange[1] in title,
        f"Plot title should contain time range. Title: '{title}'"
    )

@pytest.mark.mission("Single Custom Variable in Showdahodo")
def test_single_custom_variable(test_environment):
    """Test using a single custom variable in showdahodo"""
    
    print("\n================================================================================")
    print("TEST #3: Single Custom Variable in Showdahodo")
    print("Verifies that showdahodo works with one custom variable")
    print("================================================================================\n")
    
    # Get the time range from the fixture
    trange = test_environment
    
    # First make a basic showdahodo call to load the required data
    phase(1, "Loading data with basic showdahodo call")
    print_manager.debug("Loading data with standard variables first")
    fig_init, ax_init = showdahodo(trange, mag_rtn_4sa.br, proton.anisotropy)
    print_manager.debug("Initial data loading complete")
    plt.close(fig_init)  # Close the initial figure
    
    phase(2, "Creating custom variable")
    # Create TAoverB custom variable
    ta_over_b = custom_variable('TAoverB', proton.anisotropy / mag_rtn_4sa.bmag)
    
    # Set some properties
    ta_over_b.y_label = "Temperature Anisotropy / |B|"
    ta_over_b.legend_label = "TAoverB"
    
    # Print some diagnostics
    print_manager.test(f"Custom variable data_type: {ta_over_b.data_type}")
    print_manager.test(f"Custom variable class_name: {ta_over_b.class_name}")
    
    phase(3, "Creating hodogram with custom variable as x-axis")
    # Create hodogram with custom variable
    fig1, ax1 = showdahodo(trange, ta_over_b, mag_rtn_4sa.br)
    
    # Verify plot was created
    system_check(
        "Plot Creation with Custom X-Axis",
        fig1 is not None and ax1 is not None,
        "Showdahodo should return figure and axis objects"
    )
    
    # Verify plot has data
    has_data1, has_colorbar1, scatter_count1 = verify_plot_has_data(fig1, ax1)
    
    system_check(
        "Plot Data Verification with Custom X-Axis",
        has_data1,
        f"Plot should contain data points. Found: {scatter_count1} scatter collections with data: {has_data1}"
    )
    
    # Verify axis labels
    system_check(
        "X-Axis Label with Custom Variable",
        ax1.get_xlabel() == ta_over_b.legend_label,
        f"X-axis label should be '{ta_over_b.legend_label}', found '{ax1.get_xlabel()}'"
    )
    
    phase(4, "Creating hodogram with custom variable as y-axis")
    # Create hodogram with custom variable on y-axis
    fig2, ax2 = showdahodo(trange, mag_rtn_4sa.br, ta_over_b)
    
    # Verify plot has data
    has_data2, has_colorbar2, scatter_count2 = verify_plot_has_data(fig2, ax2)
    
    system_check(
        "Plot Data Verification with Custom Y-Axis",
        has_data2,
        f"Plot should contain data points. Found: {scatter_count2} scatter collections with data: {has_data2}"
    )
    
    # Verify axis labels
    system_check(
        "Y-Axis Label with Custom Variable",
        ax2.get_ylabel() == ta_over_b.legend_label,
        f"Y-axis label should be '{ta_over_b.legend_label}', found '{ax2.get_ylabel()}'"
    )

@pytest.mark.mission("Dual Custom Variables in Showdahodo")
def test_dual_custom_variables(test_environment):
    """Test using two custom variables in showdahodo"""
    
    print("\n================================================================================")
    print("TEST #4: Dual Custom Variables in Showdahodo")
    print("Verifies that showdahodo works with two custom variables")
    print("================================================================================\n")
    
    # Get the time range from the fixture
    trange = test_environment
    
    phase(1, "Creating two custom variables")
    # Create first custom variable
    ta_over_b = custom_variable('TAoverB', proton.anisotropy / mag_rtn_4sa.bmag)
    ta_over_b.legend_label = "TAoverB"
    
    # Create second custom variable
    br_squared = custom_variable('BrSquared', mag_rtn_4sa.br * mag_rtn_4sa.br)
    br_squared.legend_label = "BrSquared"
    
    phase(2, "Creating hodogram with both custom variables")
    # Create hodogram with both custom variables
    fig, ax = showdahodo(trange, ta_over_b, br_squared)
    
    # Verify plot was created
    system_check(
        "Plot Creation with Dual Custom Variables",
        fig is not None and ax is not None,
        "Showdahodo should return figure and axis objects"
    )
    
    # Verify plot has data
    has_data, has_colorbar, scatter_count = verify_plot_has_data(fig, ax)
    
    system_check(
        "Plot Data Verification with Dual Custom Variables",
        has_data,
        f"Plot should contain data points. Found: {scatter_count} scatter collections with data: {has_data}"
    )
    
    # Verify axis labels
    system_check(
        "X-Axis Label with First Custom Variable",
        ax.get_xlabel() == ta_over_b.legend_label,
        f"X-axis label should be '{ta_over_b.legend_label}', found '{ax.get_xlabel()}'"
    )
    
    system_check(
        "Y-Axis Label with Second Custom Variable",
        ax.get_ylabel() == br_squared.legend_label,
        f"Y-axis label should be '{br_squared.legend_label}', found '{ax.get_ylabel()}'"
    )

@pytest.mark.mission("Repeated Custom Variables Plot in Showdahodo")
def test_repeated_custom_variables_plot(test_environment):
    """Test creating and plotting custom variables twice in succession"""
    
    print("\n================================================================================")
    print("TEST #5: Repeated Custom Variables Plot in Showdahodo")
    print("Verifies that creating and plotting custom variables works twice in succession")
    print("================================================================================\n")
    
    # Get the time range from the fixture
    trange = test_environment
    
    phase(1, "First plot with custom variables")
    # Create first set of custom variables with names matching labels
    ta_over_b1 = custom_variable('TAoverB_First', proton.anisotropy / mag_rtn_4sa.bmag)
    ta_over_b1.legend_label = "TAoverB_First"
    
    br_squared1 = custom_variable('BrSquared_First', mag_rtn_4sa.br * mag_rtn_4sa.br)
    br_squared1.legend_label = "BrSquared_First"
    
    # Create first hodogram
    fig1, ax1 = showdahodo(trange, ta_over_b1, br_squared1)
    
    # Verify first plot has data
    has_data1, has_colorbar1, scatter_count1 = verify_plot_has_data(fig1, ax1)
    
    system_check(
        "First Plot Data Verification",
        has_data1,
        f"First plot should contain data points. Found: {scatter_count1} scatter collections with data: {has_data1}"
    )
    
    # Save the first plot's data point count
    first_plot_scatter_count = scatter_count1
    
    phase(2, "Second plot with newly created custom variables")
    # Create second set of custom variables with names matching labels
    ta_over_b2 = custom_variable('TAoverB_Second', proton.anisotropy / mag_rtn_4sa.bmag)
    ta_over_b2.legend_label = "TAoverB_Second"
    
    br_squared2 = custom_variable('BrSquared_Second', mag_rtn_4sa.br * mag_rtn_4sa.br)
    br_squared2.legend_label = "BrSquared_Second"
    
    # Create second hodogram
    fig2, ax2 = showdahodo(trange, ta_over_b2, br_squared2)
    
    # Verify second plot has data
    has_data2, has_colorbar2, scatter_count2 = verify_plot_has_data(fig2, ax2)
    
    system_check(
        "Second Plot Data Verification",
        has_data2,
        f"Second plot should contain data points. Found: {scatter_count2} scatter collections with data: {has_data2}"
    )
    
    # Verify both plots have similar data point counts
    system_check(
        "Consistent Data Between Plots",
        scatter_count1 == scatter_count2,
        f"Both plots should have similar data point counts. First: {scatter_count1}, Second: {scatter_count2}"
    )
    
    # Verify axis labels on second plot
    system_check(
        "X-Axis Label on Second Plot",
        ax2.get_xlabel() == ta_over_b2.legend_label,
        f"X-axis label should be '{ta_over_b2.legend_label}', found '{ax2.get_xlabel()}'"
    )
    
    system_check(
        "Y-Axis Label on Second Plot",
        ax2.get_ylabel() == br_squared2.legend_label,
        f"Y-axis label should be '{br_squared2.legend_label}', found '{ax2.get_ylabel()}'"
    )

@pytest.mark.mission("Standard Variable as Color in Showdahodo")
def test_standard_variable_as_color(test_environment):
    """Test using a standard variable as the color variable in showdahodo"""
    
    print("\n================================================================================")
    print("TEST #5.5: Standard Variable as Color in Showdahodo")
    print("Verifies that showdahodo works with a standard variable for coloring")
    print("================================================================================\n")
    
    # Get the time range from the fixture
    trange = test_environment
    
    # Make sure test mode is enabled
    print_manager.enable_test()
    
    phase(1, "Creating hodogram with standard variable as color")
    
    # Just verify that bn has the attributes we expect for the test
    print_manager.debug(f"Color variable class: {mag_rtn_4sa.bn.class_name}")
    print_manager.debug(f"Color variable subclass: {mag_rtn_4sa.bn.subclass_name}")
    print_manager.debug(f"Color variable legend_label: {mag_rtn_4sa.bn.legend_label}")
    
    # Call showdahodo with a color variable directly
    fig, ax = showdahodo(trange, mag_rtn_4sa.br, mag_rtn_4sa.bt, color_var=mag_rtn_4sa.bn)
    
    # Verify plot was created
    system_check(
        "Plot Creation with Standard Color Variable",
        fig is not None and ax is not None,
        "Showdahodo should return figure and axis objects"
    )
    
    # Verify plot has data
    has_data, has_colorbar, scatter_count = verify_plot_has_data(fig, ax)
    
    system_check(
        "Plot Data Verification with Standard Color Variable",
        has_data,
        f"Plot should contain data points. Found: {scatter_count} scatter collections with data: {has_data}"
    )
    
    system_check(
        "Colorbar Verification",
        has_colorbar,
        "Plot should have a colorbar for the standard variable"
    )
    
    # Verify colorbar label matches the variable's legend_label
    if has_colorbar:
        colorbar = get_colorbar(fig)
        if colorbar and hasattr(colorbar, 'ax') and hasattr(colorbar.ax, 'get_ylabel'):
            actual_label = colorbar.ax.get_ylabel()
            expected_label = mag_rtn_4sa.bn.legend_label
            print(f">>> Expected colorbar label: '{expected_label}'")
            print(f">>> Actual colorbar label: '{actual_label}'")
            
            system_check(
                "Colorbar Label Verification",
                actual_label == expected_label,
                f"Colorbar label should be '{expected_label}', found '{actual_label}'"
            )

@pytest.mark.mission("Custom Variable as Color in Showdahodo")
def test_custom_variable_as_color(test_environment):
    """Test using a custom variable as the color variable in showdahodo"""
    
    print("\n================================================================================")
    print("TEST #6: Custom Variable as Color in Showdahodo")
    print("Verifies that showdahodo works with a custom variable for coloring")
    print("================================================================================\n")
    
    # Get the time range from the fixture
    trange = test_environment
    print_manager.show_test = True
    
    phase(1, "Creating custom variable for coloring")
    # Create custom variable with name matching label
    ta_over_b = custom_variable('TAoverB_Color', proton.anisotropy / mag_rtn_4sa.bmag)
    ta_over_b.legend_label = "TAoverB_Color"
    
    # Print diagnostics about variables
    print_manager.debug(f"Custom variable name: {ta_over_b.name}")
    print_manager.debug(f"Custom variable legend_label: {ta_over_b.legend_label}")
    print_manager.debug(f"X-axis variable: {mag_rtn_4sa.br.class_name}.{mag_rtn_4sa.br.subclass_name}")
    print_manager.debug(f"Y-axis variable: {mag_rtn_4sa.bt.class_name}.{mag_rtn_4sa.bt.subclass_name}")
    print_manager.debug(f"Color variable type: {type(ta_over_b)}")
    
    # Debug print_manager settings
    print(f">>> print_manager.show_test before showdahodo: {print_manager.show_test}")
    
    phase(2, "Creating hodogram with custom variable as color")
    # Create hodogram with custom variable as color
    try:
        fig, ax = showdahodo(trange, mag_rtn_4sa.br, mag_rtn_4sa.bt, color_var=ta_over_b)
        print_manager.debug("showdahodo call successful")
    except Exception as e:
        print_manager.debug(f"Error in showdahodo call: {str(e)}")
        raise e
    
    # Direct print of debug info to see it regardless of print_manager settings
    print(f">>> print_manager.show_test after showdahodo: {print_manager.show_test}")
    
    # Verify plot was created
    system_check(
        "Plot Creation with Custom Color Variable",
        fig is not None and ax is not None,
        "Showdahodo should return figure and axis objects"
    )
    
    # Verify plot has data
    has_data, has_colorbar, scatter_count = verify_plot_has_data(fig, ax)
    
    system_check(
        "Plot Data Verification with Custom Color Variable",
        has_data,
        f"Plot should contain data points. Found: {scatter_count} scatter collections with data: {has_data}"
    )
    
    system_check(
        "Colorbar Verification",
        has_colorbar,
        "Plot should have a colorbar for the custom variable"
    )
    
    # Verify colorbar label matches the variable's legend_label
    if has_colorbar:
        colorbar = get_colorbar(fig)
        if colorbar and hasattr(colorbar, 'ax') and hasattr(colorbar.ax, 'get_ylabel'):
            actual_label = colorbar.ax.get_ylabel()
            expected_label = ta_over_b.legend_label
            print(f">>> Expected colorbar label: '{expected_label}'")
            print(f">>> Actual colorbar label: '{actual_label}'")
            
            system_check(
                "Colorbar Label Verification",
                actual_label == expected_label,
                f"Colorbar label should be '{expected_label}', found '{actual_label}'"
            )

@pytest.mark.mission("Custom Variable as Z-Axis in 3D Showdahodo")
def test_custom_variable_as_z_axis(test_environment):
    """Test using a custom variable as the z-axis variable in a 3D showdahodo plot"""
    
    print("\n================================================================================")
    print("TEST #7: Custom Variable as Z-Axis in 3D Showdahodo")
    print("Verifies that showdahodo works with a custom variable for the z-axis in 3D plots")
    print("================================================================================\n")
    
    # Get the time range from the fixture
    trange = test_environment
    
    phase(1, "Creating custom variable for z-axis")
    # Create custom variable with name matching label
    br_squared = custom_variable('BrSquared_ZAxis', mag_rtn_4sa.br * mag_rtn_4sa.br)
    br_squared.legend_label = "BrSquared_ZAxis"
    
    phase(2, "Creating 3D hodogram with custom variable as z-axis")
    # Create 3D hodogram with custom variable as z-axis
    fig, ax = showdahodo(trange, mag_rtn_4sa.br, mag_rtn_4sa.bt, var3=br_squared)
    
    # Verify plot was created
    system_check(
        "3D Plot Creation with Custom Z-Axis Variable",
        fig is not None and ax is not None,
        "Showdahodo should return figure and axis objects"
    )
    
    # Verify plot has data
    has_data, has_colorbar, scatter_count = verify_plot_has_data(fig, ax)
    
    system_check(
        "3D Plot Data Verification with Custom Z-Axis Variable",
        has_data,
        f"Plot should contain data points. Found: {scatter_count} scatter collections with data: {has_data}"
    )
    
    # Verify axis labels (including z-axis)
    system_check(
        "Z-Axis Label with Custom Variable",
        ax.get_zlabel() == br_squared.legend_label,
        f"Z-axis label should be '{br_squared.legend_label}', found '{ax.get_zlabel()}'"
    )

@pytest.mark.mission("All Custom Variables in 3D Showdahodo")
def test_all_custom_variables_3d(test_environment):
    """Test using all custom variables in a 3D showdahodo plot (x, y, z, and color)"""
    
    print("\n================================================================================")
    print("TEST #8: All Custom Variables in 3D Showdahodo")
    print("Verifies that showdahodo works with custom variables for all dimensions")
    print("================================================================================\n")
    
    # Get the time range from the fixture
    trange = test_environment
    
    phase(1, "Creating multiple custom variables for all dimensions")
    # Create custom variables for each dimension with names matching labels
    ta_over_b = custom_variable('TAoverB_XAxis', proton.anisotropy / mag_rtn_4sa.bmag)
    ta_over_b.legend_label = "TAoverB_XAxis"
    
    br_squared = custom_variable('BrSquared_YAxis', mag_rtn_4sa.br * mag_rtn_4sa.br)
    br_squared.legend_label = "BrSquared_YAxis"
    
    bt_squared = custom_variable('BtSquared_ZAxis', mag_rtn_4sa.bt * mag_rtn_4sa.bt)
    bt_squared.legend_label = "BtSquared_ZAxis"
    
    bn_squared = custom_variable('BnSquared_Color', mag_rtn_4sa.bn * mag_rtn_4sa.bn)
    bn_squared.legend_label = "BnSquared_Color"
    
    phase(2, "Creating 3D hodogram with all custom variables")
    # Create 3D hodogram with all custom variables
    fig, ax = showdahodo(trange, ta_over_b, br_squared, var3=bt_squared, color_var=bn_squared)
    
    # Verify plot was created
    system_check(
        "3D Plot Creation with All Custom Variables",
        fig is not None and ax is not None,
        "Showdahodo should return figure and axis objects"
    )
    
    # Verify plot has data
    has_data, has_colorbar, scatter_count = verify_plot_has_data(fig, ax)
    
    system_check(
        "3D Plot Data Verification with All Custom Variables",
        has_data,
        f"Plot should contain data points. Found: {scatter_count} scatter collections with data: {has_data}"
    )
    
    # Verify axis labels
    system_check(
        "X-Axis Label in All-Custom Plot",
        ax.get_xlabel() == ta_over_b.legend_label,
        f"X-axis label should be '{ta_over_b.legend_label}', found '{ax.get_xlabel()}'"
    )
    
    system_check(
        "Y-Axis Label in All-Custom Plot",
        ax.get_ylabel() == br_squared.legend_label,
        f"Y-axis label should be '{br_squared.legend_label}', found '{ax.get_ylabel()}'"
    )
    
    system_check(
        "Z-Axis Label in All-Custom Plot",
        ax.get_zlabel() == bt_squared.legend_label,
        f"Z-axis label should be '{bt_squared.legend_label}', found '{ax.get_zlabel()}'"
    )

@pytest.mark.mission("Proton FITS Variables in Showdahodo")
def test_proton_fits_variables(test_environment):
    """Test using two variables from the proton_fits class in showdahodo"""

    print("\n================================================================================")
    print("TEST #9: Proton FITS Variables in Showdahodo")
    print("Verifies that showdahodo works with two variables from the proton_fits class")
    print("================================================================================\n")

    # Define a specific time range for this test
    trange = ['2024-09-30/12:00:00.000', '2024-09-30/13:00:00.000']
    print_manager.test(f"Using specific trange for this test: {trange}")

    # Phase 1: Trigger data loading for proton_fits for the trange
    # Use existing attributes from the proton_fits instance
    var1 = proton_fits.beta_ppar_pfits # Example: Parallel beta
    var2 = proton_fits.vdrift_va_pfits # Example: Normalized drift speed

    # Check if variables were retrieved (basic check)
    if var1 is None or var2 is None:
        pytest.fail("Failed to retrieve proton_fits variables. Ensure they are initialized.")

    print_manager.test(f"Using X variable: {var1.class_name}.{var1.subclass_name} ({var1.legend_label})")
    print_manager.test(f"Using Y variable: {var2.class_name}.{var2.subclass_name} ({var2.legend_label})")

    # Phase 2: Creating hodogram with both proton_fits variables
    phase(2, "Creating hodogram with Proton FITS variables")
    # Create hodogram directly using the attributes
    fig, ax = showdahodo(trange, var1, var2)

    # Verify plot was created
    system_check(
        "Plot Creation with Proton FITS Variables",
        fig is not None and ax is not None,
        "Showdahodo should return figure and axis objects"
    )

    # Verify plot has data
    has_data, has_colorbar, scatter_count = verify_plot_has_data(fig, ax)

    system_check(
        "Plot Data Verification with Proton FITS Variables",
        has_data,
        f"Plot should contain data points. Found: {scatter_count} scatter collections with data: {has_data}"
    )

    # Verify axis labels using the legend_label attribute
    system_check(
        "X-Axis Label with First Proton FITS Variable",
        ax.get_xlabel() == var1.legend_label,
        f"X-axis label should be '{var1.legend_label}', found '{ax.get_xlabel()}'"
    )

    system_check(
        "Y-Axis Label with Second Proton FITS Variable",
        ax.get_ylabel() == var2.legend_label,
        f"Y-axis label should be '{var2.legend_label}', found '{ax.get_ylabel()}'"
    )

if __name__ == "__main__":
    # This allows running the test directly
    test_environment_fixture = test_environment.__wrapped__()
    trange = next(test_environment_fixture)
    
    try:
        test_basic_functionality(trange)
        test_single_custom_variable(trange)
        test_dual_custom_variables(trange)
        test_repeated_custom_variables_plot(trange)
        test_standard_variable_as_color(trange)
        test_custom_variable_as_color(trange)
        test_custom_variable_as_z_axis(trange)
        test_all_custom_variables_3d(trange)
        test_proton_fits_variables(trange)
        
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
    finally:
        try:
            next(test_environment_fixture)  # Run teardown
        except StopIteration:
            pass 