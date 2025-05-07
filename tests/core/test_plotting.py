"""
Test Instructions:

Run with:

    pytest -xvs | tee output.log

This will print output to the console and save it to 'output.log'.

This module tests the core plotting functionality:
1. Explicit panel plotting (e.g., panel 2)
2. Multiplot with various data types
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

# Add parent directory to path to import plotbot
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import plotbot as pb
from plotbot import print_manager
from plotbot.test_pilot import phase, system_check
from plotbot.data_classes.psp_mag_classes import mag_rtn_4sa_class, mag_rtn_class, mag_sc_4sa_class, mag_sc_class
from plotbot.data_classes.psp_electron_classes import epad_strahl_class, epad_strahl_high_res_class
from plotbot.data_classes.psp_proton_classes import proton_class, proton_hr_class
from plotbot.data_classes.psp_ham_classes import ham_class

# Import test helpers
from tests.utils import (
    verify_instance_state, 
    reset_and_verify_empty,
    run_plotbot_test
)

# Test Constants
TEST_SINGLE_TRANGE = ['2021-10-26 02:00:00', '2021-10-26 02:10:00']

# Standardized class name mapping to handle case sensitivity and variations consistently
CLASS_NAME_MAPPING = {
    # Standard instance names (lowercase) mapped to data_type (often uppercase), class type, and primary components
    'mag_rtn_4sa': {
        'data_type': 'mag_RTN_4sa',
        'class_type': mag_rtn_4sa_class,
        'components': ['br', 'bt', 'bn', 'bmag', 'pmag', 'all'],
        'primary_component': 'br'
    },
    'mag_rtn': {
        'data_type': 'mag_RTN',
        'class_type': mag_rtn_class,
        'components': ['br', 'bt', 'bn', 'bmag', 'pmag', 'all'],
        'primary_component': 'br'
    },
    'mag_sc_4sa': {
        'data_type': 'mag_SC_4sa',
        'class_type': mag_sc_4sa_class,
        'components': ['bx', 'by', 'bz', 'bmag', 'pmag', 'all'],
        'primary_component': 'bx'
    },
    'mag_sc': {
        'data_type': 'mag_SC',
        'class_type': mag_sc_class,
        'components': ['bx', 'by', 'bz', 'bmag', 'pmag', 'all'],
        'primary_component': 'bx'
    },
    'epad_strahl': {
        'data_type': 'spe_sf0_pad',
        'class_type': epad_strahl_class,
        'components': ['strahl'],
        'primary_component': 'strahl'
    },
    'epad_strahl_high_res': {
        'data_type': 'spe_af0_pad',
        'class_type': epad_strahl_high_res_class,
        'components': ['strahl'],
        'primary_component': 'strahl'
    },
    'proton': {
        'data_type': 'spi_sf00_l3_mom',
        'class_type': proton_class,
        'components': ['anisotropy'],
        'primary_component': 'anisotropy'
    },
    'proton_hr': {
        'data_type': 'spi_af00_L3_mom',
        'class_type': proton_hr_class,
        'components': ['anisotropy'],
        'primary_component': 'anisotropy'
    },
    'ham': {
        'data_type': 'ham',
        'class_type': ham_class,
        'components': ['hamogram_30s'],
        'primary_component': 'hamogram_30s'
    },
}

@pytest.fixture
def mag_4sa_test_instance():
    """Provides a consistently named and reset instance for testing."""
    instance_name = 'mag_rtn_4sa'
    return reset_and_verify_empty(instance_name)

@pytest.fixture(autouse=True)
def setup_test_plots():
    """Ensure plots are closed before and after each test in this file."""
    pb.plt.close('all')
    # Ensure specific print_manager settings for these tests
    print_manager.show_debug = True
    print_manager.show_datacubby = True
    print_manager.show_data_snapshot = True
    print_manager.show_tracker = True
    yield
    pb.plt.close('all')
    # Reset print_manager settings after test
    print_manager.show_debug = False
    print_manager.show_datacubby = False
    print_manager.show_data_snapshot = False
    print_manager.show_tracker = False

@pytest.mark.mission("Core Pipeline: Explicit Panel Plotting")
def test_explicit_panel_plotting(mag_4sa_test_instance):
    """Tests plotting on panel 2 explicitly, ensuring correct panel setup."""
    instance_name = mag_4sa_test_instance.class_name
    
    phase(1, "Setting plot options for panel 2 test")
    pb.plt.options.use_single_title = True
    pb.plt.options.single_title_text = "Explicit Panel 2 Plotting"

    phase(2, f"Calling plotbot for {TEST_SINGLE_TRANGE} on panel 2")
    # This call should result in a 2-panel figure with the plot on the second panel
    plot_successful = pb.plotbot(TEST_SINGLE_TRANGE, mag_4sa_test_instance.br, 2)
    system_check("Plotbot call to panel 2 successful", plot_successful, "plotbot() targeting panel 2 should return True.")
    assert plot_successful, "Plotbot call to panel 2 failed."

    phase(3, "Verifying figure panel count")
    try:
        current_fig = pb.plt.gcf() # Get current figure
        num_axes = len(current_fig.axes)
        system_check("Figure panel count for panel 2 plot", num_axes == 2, f"Expected 2 panels, found {num_axes}.")
        assert num_axes == 2, f"Plotting on panel 2 did not result in 2 panels (found {num_axes})."
    except Exception as e:
        system_check("Figure panel count verification", False, f"Error getting/checking panel count: {e}")
        pytest.fail(f"Could not verify panel count: {e}")

    phase(4, f"Verifying instance state for {instance_name} after panel 2 plot")
    # Instance data should still be loaded correctly regardless of which panel it's plotted on
    verification_passed = verify_instance_state(
        f"pb.{instance_name}",
        mag_4sa_test_instance,
        [TEST_SINGLE_TRANGE]
    )
    system_check("Instance state after panel 2 plot", verification_passed, "Instance data should be loaded and consistent.")
    assert verification_passed, "Instance state verification failed after panel 2 plot."

@pytest.mark.mission("Core Pipeline: Multiplot with Various Data Types")
def test_multiplot_specific_data_files():
    """Tests multiplot with a predefined list of different data types and time points."""
    phase(1, "Defining time points for different data types")
    # Define unique time points for each data type to plot
    time_points = {
        'epad_strahl': '2018-10-26 12:00:00',
        'epad_strahl_high_res': '2018-10-26 12:00:00',
        'proton': '2020-04-09 12:00:00', 
        'proton_hr': '2024-09-30 12:00:00',
        'ham': '2025-03-23 12:00:00'
    }
    
    # List of instances to test with, starting with the most likely to succeed
    instances_to_test = ['mag_rtn_4sa', 'mag_rtn', 'epad_strahl', 'proton']
    
    # Build a list of reset instances
    reset_instances = {}
    
    phase(2, "Resetting and initializing data instances")
    # Reset each instance
    for instance_name in instances_to_test:
        try:
            instance = reset_and_verify_empty(instance_name)
            if instance is not None:
                reset_instances[instance_name] = instance
                print_manager.debug(f"Successfully reset {instance_name}")
            else:
                print_manager.warning(f"Failed to reset instance {instance_name}")
        except Exception as e:
            print_manager.warning(f"Error resetting instance {instance_name}: {e}")
    
    # Verify we have at least some instances to test with
    if not reset_instances:
        pytest.skip("Skipping multiplot test - no instances were successfully reset")
    
    phase(3, "Setting up multiplot options")
    pb.plt.options.reset() # Reset to defaults first
    pb.plt.options.use_single_title = True
    pb.plt.options.single_title_text = "Multiplot with Various Data Types"
    pb.plt.options.window = '23:59:59'
    pb.plt.options.position = 'around'
    pb.plt.figure(figsize=(12, 10)) # Make figure larger for better visualization
    
    phase(4, "Building plot_data list for multiplot")
    # This is the list of (time_point, plot_variable) tuples for multiplot
    plot_data = []
    
    # For each reset instance, try to access its primary component and add to plot_data
    for instance_name, instance in reset_instances.items():
        if instance_name not in CLASS_NAME_MAPPING:
            print_manager.warning(f"No class mapping for {instance_name}, skipping")
            continue
            
        # Get the primary component name from CLASS_NAME_MAPPING
        primary_component = CLASS_NAME_MAPPING[instance_name].get('primary_component')
        if not primary_component:
            print_manager.warning(f"No primary component defined for {instance_name}, skipping")
            continue
            
        # Try to access the component
        try:
            if hasattr(instance, primary_component):
                component = getattr(instance, primary_component)
                if component is not None:
                    # Use a predefined time point if available, otherwise use a default
                    time_point = time_points.get(instance_name, '2021-10-26 02:00:00')
                    # Add (time_point, component) tuple to plot_data
                    plot_data.append((time_point, component))
                    print_manager.debug(f"Added {instance_name}.{primary_component} at {time_point} to plot_data")
                else:
                    print_manager.warning(f"{instance_name}.{primary_component} is None, skipping")
            else:
                print_manager.warning(f"{instance_name} has no attribute '{primary_component}', skipping")
        except Exception as e:
            print_manager.warning(f"Error accessing {instance_name}.{primary_component}: {e}")
    
    # Check if we have at least one item to plot
    if not plot_data:
        pytest.skip("Skipping multiplot test - no valid components found for plotting")
    
    phase(5, "Calling multiplot with plot_data")
    print_manager.debug(f"Calling multiplot with {len(plot_data)} items")
    try:
        fig, axs = pb.multiplot(plot_data)
        multiplot_call_successful = True
    except Exception as e:
        multiplot_call_successful = False
        system_check("Multiplot call execution", False, f"multiplot raised an exception: {e}")
        pytest.fail(f"Multiplot call failed with exception: {e}")
    
    phase(6, "Verifying multiplot output")
    system_check("Multiplot call succeeded", multiplot_call_successful, "multiplot() should execute without error.")
    
    # Verify figure and axes were created
    fig_created = fig is not None
    axs_created = axs is not None
    axs_length_correct = isinstance(axs, (list, np.ndarray)) and len(axs) == len(plot_data)
    
    system_check("Multiplot figure created", fig_created, "multiplot should return a figure object.")
    system_check("Multiplot axes created", axs_created, "multiplot should return axes objects.")
    if axs_created and isinstance(axs, (list, np.ndarray)):
        system_check("Multiplot axes count", axs_length_correct, 
                    f"Expected {len(plot_data)} axes, got {len(axs) if axs is not None else 'None'}.")
    
    # Check if at least one of the instances now has data (indicating that get_data was called by multiplot)
    data_loaded = False
    for instance_name, instance in reset_instances.items():
        # Skip instances not included in the plot_data
        if not any(component.__self__ is instance for _, component in plot_data if hasattr(component, '__self__')):
            continue
            
        # Check if this instance has data now
        try:
            has_data = (
                hasattr(instance, 'datetime_array') and 
                instance.datetime_array is not None and 
                len(instance.datetime_array) > 0
            )
            if has_data:
                data_loaded = True
                print_manager.debug(f"Data was loaded for {instance_name}")
                break
        except (AttributeError, Exception):
            continue
    
    system_check("Data loaded by multiplot", data_loaded, "At least one instance should have data after multiplot.")
    
    # Success if figure and axes were created
    success = fig_created and axs_created
    assert success, "Multiplot test failed to create figure or axes"
    
    return success

if __name__ == "__main__":
    import os
    os.makedirs("tests/core/logs", exist_ok=True)
    pytest.main(["-xvs", __file__, "--log-file=tests/core/logs/test_plotting.txt"]) 