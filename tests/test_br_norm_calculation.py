#!/usr/bin/env python3
# tests/test_br_norm_calculation.py

import pytest
import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import interpolate
import os
import sys
import traceback

# Import from plotbot
from plotbot import print_manager, config, get_data
from plotbot import plt as plotbot_plt  # Import our enhanced plt with options
import plotbot.data_classes.psp_mag_rtn_4sa as mag_class
import plotbot.data_classes.psp_proton as proton_class
from plotbot.test_pilot import phase, system_check  # Test helpers from test_stardust

# Enable necessary debugging
print_manager.show_datacubby = True
print_manager.show_dependency_management = True
print_manager.show_debug = True  # Enable for detailed debugging
print_manager.show_status = True

# Configure data server
config.data_server = 'berkeley'  # Options: 'default', 'spdf', 'berkeley'

# Test time ranges
SHORT_TRANGE = ['2021/04/26 00:00:00', '2021/04/26 06:00:00']
LONG_TRANGE = ['2021/04/26 00:00:00', '2021/04/27 00:00:00']

# Images directory path - use the existing Images directory
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'Images')
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

@pytest.fixture(autouse=True)
def setup_test_plots():
    """Ensure plots are closed before and after each test."""
    plt.close('all')
    yield
    plt.close('all')

def interpolate_sun_dist_to_mag_data(proton_datetime_array, proton_sun_dist_data, mag_datetime_array):
    """
    Function to properly interpolate sun distance data to match magnetometer time array.
    Handles scalar values by creating an appropriate array.
    
    Based on best practices from showdahodo.py's downsample_time_based function
    
    Parameters:
    -----------
    proton_datetime_array : numpy.ndarray
        Array of datetime objects from proton data
    proton_sun_dist_data : numpy.ndarray or scalar
        Sun distance data in Rsun, could be scalar or array
    mag_datetime_array : numpy.ndarray
        Array of datetime objects from magnetometer data (target timeline)
    
    Returns:
    --------
    numpy.ndarray
        Interpolated sun distance values at magnetometer timestamps
    """
    print(f"DEBUG: interpolate_sun_dist_to_mag_data function called")
    print(f"DEBUG: proton_datetime_array type: {type(proton_datetime_array)}, shape: {getattr(proton_datetime_array, 'shape', 'N/A')}")
    print(f"DEBUG: proton_sun_dist_data type: {type(proton_sun_dist_data)}, shape: {getattr(proton_sun_dist_data, 'shape', 'N/A')}, ndim: {getattr(proton_sun_dist_data, 'ndim', 'N/A')}")
    print(f"DEBUG: mag_datetime_array type: {type(mag_datetime_array)}, shape: {getattr(mag_datetime_array, 'shape', 'N/A')}")
    
    # Handle scalar sun_dist_data (shape=() or ndim=0)
    if np.isscalar(proton_sun_dist_data) or getattr(proton_sun_dist_data, 'ndim', 0) == 0:
        print(f"DEBUG: Detected scalar value in sun_dist_data: {proton_sun_dist_data}")
        # Create a uniform array with the scalar value at all mag timestamps
        return np.full(len(mag_datetime_array), proton_sun_dist_data, dtype=float)
    
    try:
        # Check for sufficient data points for interpolation
        if len(proton_datetime_array) < 2:
            if len(proton_datetime_array) == 1 and len(mag_datetime_array) > 0:
                # If we only have one point, replicate it for all target times
                print(f"DEBUG: Only one proton data point, replicating for all mag times")
                return np.full(len(mag_datetime_array), proton_sun_dist_data[0], dtype=float)
            print(f"WARNING: Insufficient proton data for interpolation")
            return np.full(len(mag_datetime_array), np.nan)
        
        # Convert datetime arrays to numeric timestamps for interpolation
        try:
            proton_time_numeric = mdates.date2num(proton_datetime_array)
            mag_time_numeric = mdates.date2num(mag_datetime_array)
            print(f"DEBUG: Converted datetimes to numeric values for interpolation")
        except Exception as e:
            print(f"ERROR: Failed to convert datetimes using mdates.date2num: {e}")
            # Fallback to timestamp conversion
            try:
                proton_time_numeric = proton_datetime_array.astype(np.int64) // 10**9
                mag_time_numeric = mag_datetime_array.astype(np.int64) // 10**9
                print(f"DEBUG: Used fallback timestamp conversion")
            except Exception as e2:
                print(f"ERROR: Failed both datetime conversion methods: {e2}")
                return np.full(len(mag_datetime_array), np.nan)
        
        # Handle NaN values in the sun distance data
        valid_mask = ~np.isnan(proton_sun_dist_data)
        valid_count = np.sum(valid_mask)
        
        if not np.any(valid_mask):
            print(f"ERROR: No valid sun distance data (all NaNs)")
            return np.full(len(mag_datetime_array), np.nan)
            
        if not np.all(valid_mask):
            print(f"WARNING: Found NaN values in sun_dist_data - cleaning before interpolation")
            proton_time_numeric = proton_time_numeric[valid_mask]
            proton_sun_dist_clean = proton_sun_dist_data[valid_mask]
                
            # Re-check if we have enough points after removing NaNs
            if len(proton_time_numeric) < 2:
                if len(proton_time_numeric) == 1:
                    # If we only have one point, replicate it for all target times
                    print(f"DEBUG: Only one valid proton data point after NaN removal")
                    return np.full(len(mag_datetime_array), proton_sun_dist_clean[0], dtype=float)
                print(f"WARNING: Insufficient valid proton data after NaN removal")
                return np.full(len(mag_datetime_array), np.nan)
        else:
            # If no NaNs, just use the original data
            proton_sun_dist_clean = proton_sun_dist_data
        
        # Use scipy's interp1d for interpolation (exactly as in showdahodo.py)
        try:
            # Create interpolation function
            f = interpolate.interp1d(
                proton_time_numeric, 
                proton_sun_dist_clean,
                kind='linear',
                bounds_error=False,
                fill_value='extrapolate'
            )
            
            # Apply interpolation function to mag timestamps
            sun_dist_interp = f(mag_time_numeric)
            print(f"DEBUG: scipy.interpolate.interp1d successful")
            return sun_dist_interp
        except Exception as interp_error:
            print(f"WARNING: scipy.interpolate.interp1d failed: {interp_error}, falling back to np.interp")
            # Fall back to numpy's interp if scipy fails
            try:
                sun_dist_interp = np.interp(mag_time_numeric, proton_time_numeric, proton_sun_dist_clean)
                print(f"DEBUG: np.interp fallback successful")
                return sun_dist_interp
            except Exception as np_interp_error:
                print(f"ERROR: All interpolation methods failed: {np_interp_error}")
                return np.full(len(mag_datetime_array), np.nan)
            
    except Exception as e:
        print(f"ERROR: Unexpected error in interpolation: {e}")
        import traceback
        print(traceback.format_exc())
        return np.full(len(mag_datetime_array), np.nan)

def calculate_br_norm(br_data, sun_dist_interp_rsun):
    """
    Calculate the normalized radial magnetic field (Br*R²)
    
    Parameters:
    -----------
    br_data : numpy.ndarray
        Radial magnetic field component in nT
    sun_dist_interp_rsun : numpy.ndarray
        Interpolated sun distance in Rsun
    
    Returns:
    --------
    numpy.ndarray
        Normalized radial magnetic field (nT*AU²)
    """
    # Convert Rsun to AU (1 AU ≈ 215.03 Rsun)
    rsun_to_au_conversion_factor = 215.03286764414261
    
    # Calculate Br normalized by R²
    # Br [nT] * (R [Rsun] / conversion)² = Br * R² [nT*AU²]
    br_norm = br_data * ((sun_dist_interp_rsun / rsun_to_au_conversion_factor) ** 2)
    
    return br_norm

@pytest.mark.mission("br_norm: Short Timerange Test")
def test_short_timerange():
    """Test br_norm calculation with a short time range"""
    print("\n=== TEST SHORT TIMERANGE ===")
    
    phase(1, "Getting proton sun distance data")
    print(f"Using short time range: {SHORT_TRANGE}")
    
    # Step 1: Get proton sun distance data only
    print("\nSTEP 1: Getting proton sun distance data...")
    get_data(SHORT_TRANGE, proton_class.proton.sun_dist_rsun)
    
    # Examine the proton sun_dist_rsun data
    print(f"Proton datetime_array length: {len(proton_class.proton.datetime_array)}")
    print(f"Proton sun_dist_rsun.data type: {type(proton_class.proton.sun_dist_rsun.data)}")
    print(f"Proton sun_dist_rsun.data shape: {getattr(proton_class.proton.sun_dist_rsun.data, 'shape', 'N/A')}")
    print(f"Proton sun_dist_rsun.data ndim: {getattr(proton_class.proton.sun_dist_rsun.data, 'ndim', 'N/A')}")
    
    # Store the proton data for reuse
    proton_datetime_array = proton_class.proton.datetime_array
    proton_sun_dist_data = proton_class.proton.sun_dist_rsun.data
    
    assert proton_datetime_array is not None, "Proton datetime_array should not be None"
    assert len(proton_datetime_array) > 0, "Proton datetime_array should not be empty"
    assert proton_sun_dist_data is not None, "Proton sun_dist_rsun.data should not be None"
    
    phase(2, "Getting magnetometer Br data")
    # Step 2: Get magnetometer Br data
    print("\nSTEP 2: Getting magnetometer Br data...")
    get_data(SHORT_TRANGE, mag_class.mag_rtn_4sa.br)
    
    # Examine the mag Br data
    print(f"Mag datetime_array length: {len(mag_class.mag_rtn_4sa.datetime_array)}")
    print(f"Mag br.data type: {type(mag_class.mag_rtn_4sa.br.data)}")
    print(f"Mag br.data shape: {mag_class.mag_rtn_4sa.br.data.shape}")
    
    # Store the mag data for reuse
    mag_datetime_array = mag_class.mag_rtn_4sa.datetime_array
    br_data = mag_class.mag_rtn_4sa.br.data
    
    assert mag_datetime_array is not None, "Mag datetime_array should not be None"
    assert len(mag_datetime_array) > 0, "Mag datetime_array should not be empty"
    assert br_data is not None, "Mag br.data should not be None"
    assert len(br_data) > 0, "Mag br.data should not be empty"
    
    phase(3, "Interpolating sun distance to match mag timeline")
    # Step 3: Interpolate sun distance to mag time series
    print("\nSTEP 3: Interpolating sun distance to match mag timeline...")
    sun_dist_interp = interpolate_sun_dist_to_mag_data(
        proton_datetime_array,
        proton_sun_dist_data,
        mag_datetime_array
    )
    
    print(f"Interpolated sun_dist shape: {sun_dist_interp.shape}")
    assert sun_dist_interp is not None, "Interpolated sun_dist should not be None"
    assert len(sun_dist_interp) == len(mag_datetime_array), "Interpolated sun_dist should match mag_datetime_array length"
    
    phase(4, "Calculating br_norm")
    # Step 4: Calculate br_norm
    print("\nSTEP 4: Calculating br_norm...")
    br_norm_data = calculate_br_norm(br_data, sun_dist_interp)
    
    print(f"Calculated br_norm shape: {br_norm_data.shape}")
    assert br_norm_data is not None, "br_norm_data should not be None"
    assert len(br_norm_data) == len(mag_datetime_array), "br_norm_data should match mag_datetime_array length"
    
    phase(5, "Creating and saving plots")
    # Step 5: Plot the results
    print("\nSTEP 5: Plotting results...")
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # Plot Br
    axes[0].plot(mag_datetime_array, br_data, 'b-', label='Br [nT]')
    axes[0].set_ylabel('Br [nT]')
    axes[0].legend()
    axes[0].grid(True)
    
    # Plot Sun Distance
    axes[1].plot(mag_datetime_array, sun_dist_interp, 'r-', label='Sun Distance [Rsun]')
    axes[1].set_ylabel('Sun Distance [Rsun]')
    axes[1].legend()
    axes[1].grid(True)
    
    # Plot Br_norm
    axes[2].plot(mag_datetime_array, br_norm_data, 'g-', label='Br·R² [nT·AU²]')
    axes[2].set_ylabel('Br·R² [nT·AU²]')
    axes[2].set_xlabel('Time')
    axes[2].legend()
    axes[2].grid(True)
    
    plt.tight_layout()
    filename = os.path.join(IMAGES_DIR, 'br_norm_short_timerange.png')
    plt.savefig(filename)
    print(f"Plot saved to: {filename}")
    plt.close()
    
    system_check("Short Timerange br_norm Calculation", True, "Successfully calculated br_norm for short timerange")
    
    return {
        'br_data': br_data,
        'sun_dist_interp': sun_dist_interp,
        'br_norm_data': br_norm_data,
        'mag_datetime_array': mag_datetime_array
    }

@pytest.mark.mission("br_norm: Long Timerange Test")
def test_long_timerange():
    """Test br_norm calculation with a longer time range"""
    print("\n=== TEST LONG TIMERANGE ===")
    
    phase(1, "Getting proton sun distance data")
    print(f"Using long time range: {LONG_TRANGE}")
    
    # Step 1: Get proton sun distance data only
    print("\nSTEP 1: Getting proton sun distance data...")
    get_data(LONG_TRANGE, proton_class.proton.sun_dist_rsun)
    
    # Examine the proton sun_dist_rsun data
    print(f"Proton datetime_array length: {len(proton_class.proton.datetime_array)}")
    print(f"Proton sun_dist_rsun.data type: {type(proton_class.proton.sun_dist_rsun.data)}")
    print(f"Proton sun_dist_rsun.data shape: {getattr(proton_class.proton.sun_dist_rsun.data, 'shape', 'N/A')}")
    print(f"Proton sun_dist_rsun.data ndim: {getattr(proton_class.proton.sun_dist_rsun.data, 'ndim', 'N/A')}")
    
    # Store the proton data for reuse
    proton_datetime_array = proton_class.proton.datetime_array
    proton_sun_dist_data = proton_class.proton.sun_dist_rsun.data
    
    assert proton_datetime_array is not None, "Proton datetime_array should not be None"
    assert len(proton_datetime_array) > 0, "Proton datetime_array should not be empty"
    assert proton_sun_dist_data is not None, "Proton sun_dist_rsun.data should not be None"
    
    phase(2, "Getting magnetometer Br data")
    # Step 2: Get magnetometer Br data
    print("\nSTEP 2: Getting magnetometer Br data...")
    get_data(LONG_TRANGE, mag_class.mag_rtn_4sa.br)
    
    # Examine the mag Br data
    print(f"Mag datetime_array length: {len(mag_class.mag_rtn_4sa.datetime_array)}")
    print(f"Mag br.data type: {type(mag_class.mag_rtn_4sa.br.data)}")
    print(f"Mag br.data shape: {mag_class.mag_rtn_4sa.br.data.shape}")
    
    # Store the mag data for reuse
    mag_datetime_array = mag_class.mag_rtn_4sa.datetime_array
    br_data = mag_class.mag_rtn_4sa.br.data
    
    assert mag_datetime_array is not None, "Mag datetime_array should not be None"
    assert len(mag_datetime_array) > 0, "Mag datetime_array should not be empty"
    assert br_data is not None, "Mag br.data should not be None"
    assert len(br_data) > 0, "Mag br.data should not be empty"
    
    phase(3, "Interpolating sun distance to match mag timeline")
    # Step 3: Interpolate sun distance to mag time series
    print("\nSTEP 3: Interpolating sun distance to match mag timeline...")
    sun_dist_interp = interpolate_sun_dist_to_mag_data(
        proton_datetime_array,
        proton_sun_dist_data,
        mag_datetime_array
    )
    
    print(f"Interpolated sun_dist shape: {sun_dist_interp.shape}")
    assert sun_dist_interp is not None, "Interpolated sun_dist should not be None"
    assert len(sun_dist_interp) == len(mag_datetime_array), "Interpolated sun_dist should match mag_datetime_array length"
    
    phase(4, "Calculating br_norm")
    # Step 4: Calculate br_norm
    print("\nSTEP 4: Calculating br_norm...")
    br_norm_data = calculate_br_norm(br_data, sun_dist_interp)
    
    print(f"Calculated br_norm shape: {br_norm_data.shape}")
    assert br_norm_data is not None, "br_norm_data should not be None"
    assert len(br_norm_data) == len(mag_datetime_array), "br_norm_data should match mag_datetime_array length"
    
    phase(5, "Creating and saving plots")
    # Step 5: Plot the results
    print("\nSTEP 5: Plotting results...")
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # Plot Br
    axes[0].plot(mag_datetime_array, br_data, 'b-', label='Br [nT]')
    axes[0].set_ylabel('Br [nT]')
    axes[0].legend()
    axes[0].grid(True)
    
    # Plot Sun Distance
    axes[1].plot(mag_datetime_array, sun_dist_interp, 'r-', label='Sun Distance [Rsun]')
    axes[1].set_ylabel('Sun Distance [Rsun]')
    axes[1].legend()
    axes[1].grid(True)
    
    # Plot Br_norm
    axes[2].plot(mag_datetime_array, br_norm_data, 'g-', label='Br·R² [nT·AU²]')
    axes[2].set_ylabel('Br·R² [nT·AU²]')
    axes[2].set_xlabel('Time')
    axes[2].legend()
    axes[2].grid(True)
    
    plt.tight_layout()
    filename = os.path.join(IMAGES_DIR, 'br_norm_long_timerange.png')
    plt.savefig(filename)
    print(f"Plot saved to: {filename}")
    plt.close()
    
    system_check("Long Timerange br_norm Calculation", True, "Successfully calculated br_norm for long timerange")
    
    return {
        'br_data': br_data,
        'sun_dist_interp': sun_dist_interp,
        'br_norm_data': br_norm_data,
        'mag_datetime_array': mag_datetime_array
    }

@pytest.mark.mission("br_norm: Compare Custom vs Plotbot br_norm")
def test_compare_to_plotbot():
    """Compare our custom calculation to the full plotbot calculation"""
    print("\n=== COMPARE TO PLOTBOT ===")
    
    phase(1, "Getting custom br_norm calculation")
    # Use the same time range as test_proton_r_sun.py
    trange = ['2021/04/26 00:00:00.000', '2021/04/27 00:00:00.000']
    
    # Get the data with plotbot's built-in functions
    from plotbot import plotbot, mag_rtn_4sa
    
    # First get our custom calculation 
    print("Getting our custom calculation results...")
    custom_results = test_long_timerange()
    
    phase(2, "Getting br_norm from plotbot")
    # Now get the br_norm from plotbot
    print("\nGetting br_norm using plotbot...")
    get_data(trange, mag_rtn_4sa.br_norm)
    
    # Verify that we have the br_norm data
    assert hasattr(mag_rtn_4sa, 'br_norm'), "mag_rtn_4sa should have br_norm attribute after get_data call"
    assert hasattr(mag_rtn_4sa.br_norm, 'data'), "mag_rtn_4sa.br_norm should have data attribute"
    assert mag_rtn_4sa.br_norm.data is not None, "mag_rtn_4sa.br_norm.data should not be None"
    assert len(mag_rtn_4sa.br_norm.data) > 0, "mag_rtn_4sa.br_norm.data should not be empty"
    
    phase(3, "Comparing results")
    # Compare results
    print("\nComparing results...")
    print(f"Custom br_norm shape: {custom_results['br_norm_data'].shape}")
    print(f"Plotbot br_norm shape: {mag_rtn_4sa.br_norm.data.shape}")
    
    # Calculate stats on the difference
    try:
        diff = custom_results['br_norm_data'] - mag_rtn_4sa.br_norm.data
        mean_abs_diff = np.mean(np.abs(diff))
        max_abs_diff = np.max(np.abs(diff))
        rel_diff_pct = 100 * np.mean(np.abs(diff) / np.abs(custom_results['br_norm_data']))
        
        print(f"Difference stats:")
        print(f"  Mean absolute difference: {mean_abs_diff}")
        print(f"  Max absolute difference: {max_abs_diff}")
        print(f"  Relative difference (%): {rel_diff_pct}")
        
        # Add assertions to verify the differences are within acceptable limits
        assert mean_abs_diff < 1.0, f"Mean absolute difference ({mean_abs_diff}) should be less than 1.0"
        assert rel_diff_pct < 5.0, f"Relative difference ({rel_diff_pct}%) should be less than 5%"
        
        phase(4, "Creating and saving comparison plot")
        # Plot comparison
        print("\nPlotting comparison...")
        fig, axes = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
        
        # Plot both br_norm calculations
        axes[0].plot(custom_results['mag_datetime_array'], custom_results['br_norm_data'], 'b-', label='Custom br_norm')
        axes[0].plot(mag_rtn_4sa.datetime_array, mag_rtn_4sa.br_norm.data, 'r--', label='Plotbot br_norm')
        axes[0].set_ylabel('Br·R² [nT·AU²]')
        axes[0].legend()
        axes[0].grid(True)
        
        # Plot the difference
        axes[1].plot(custom_results['mag_datetime_array'], diff, 'g-', label='Difference')
        axes[1].set_ylabel('Difference [nT·AU²]')
        axes[1].set_xlabel('Time')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        filename = os.path.join(IMAGES_DIR, 'br_norm_comparison.png')
        plt.savefig(filename)
        print(f"Comparison plot saved to: {filename}")
        plt.close()
        
        system_check("br_norm Comparison", True, f"Successfully compared custom and plotbot br_norm with relative difference of {rel_diff_pct:.2f}%")
    except Exception as e:
        print(f"Error in comparison: {e}")
        print(traceback.format_exc())
        pytest.fail(f"Failed to compare custom and plotbot br_norm: {e}") 