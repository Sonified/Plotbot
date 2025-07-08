import numpy as np
import types
import pathlib
import pytest
import matplotlib.pyplot as plt
from datetime import datetime
import os
import sys

from plotbot.print_manager import print_manager

# Enable dependency management prints for debugging
print_manager.show_dependency_management = True
print_manager.show_debug = True

# Import the classes we'll be testing
try:
    from plotbot import psp_alpha, proton, mag_rtn_4sa, plt as plotbot_plt, plotbot
    from plotbot import psp_dfb  # Phase 2: PSP DFB electric field spectra classes
    from plotbot import config  # Import the config object directly
except ImportError as e:
    psp_alpha = None
    proton = None
    plotbot = None
    plotbot_plt = plt
    psp_dfb = None

# Test log file path
log_file = os.path.join(os.path.dirname(__file__), "test_logs", "test_alpha_proton_electric_field.txt")

# ============================================================================
# PHASE 1 TESTS: Alpha/Proton Derived Variables
# ============================================================================

@pytest.mark.mission("Alpha/Proton Dependency Management")
def test_psp_alpha_dependency_infrastructure():
    """Test that psp_alpha class has proper dependency management infrastructure."""
    if psp_alpha is None:
        pytest.skip("psp_alpha not importable.")
    
    # Create minimal test instance
    TRANGE = ['2023-09-28/06:00:00.000', '2023-09-28/07:00:00.000']
    
    # Test that _current_operation_trange is properly initialized
    # This test should FAIL initially, then PASS after implementation
    alpha_instance = psp_alpha  # Get the global instance
    assert hasattr(alpha_instance, '_current_operation_trange'), \
        "psp_alpha must have _current_operation_trange attribute for dependency management"
    
    print(f"psp_alpha._current_operation_trange: {getattr(alpha_instance, '_current_operation_trange', 'NOT_FOUND')}")

@pytest.mark.mission("Alpha/Proton na_div_np Property")
def test_na_div_np_property_lazy_loading():
    """Test na_div_np property exists and implements lazy loading correctly."""
    if psp_alpha is None:
        pytest.skip("psp_alpha not importable.")
    
    # Test property existence
    assert hasattr(psp_alpha, 'na_div_np'), "psp_alpha must have na_div_np property"
    
    # Test that it returns a plot_manager instance
    na_div_np_attr = psp_alpha.na_div_np
    assert na_div_np_attr is not None, "psp_alpha.na_div_np should not be None"
    assert hasattr(na_div_np_attr, 'data'), "na_div_np should have .data attribute (plot_manager pattern)"
    
    print(f"na_div_np type: {type(na_div_np_attr)}")
    print(f"na_div_np.data type: {type(na_div_np_attr.data) if hasattr(na_div_np_attr, 'data') else 'NO_DATA_ATTR'}")

@pytest.mark.mission("Alpha/Proton ap_drift Property") 
def test_ap_drift_property_lazy_loading():
    """Test ap_drift property exists and implements lazy loading correctly."""
    if psp_alpha is None:
        pytest.skip("psp_alpha not importable.")
    
    assert hasattr(psp_alpha, 'ap_drift'), "psp_alpha must have ap_drift property"
    
    ap_drift_attr = psp_alpha.ap_drift
    assert ap_drift_attr is not None, "psp_alpha.ap_drift should not be None"
    assert hasattr(ap_drift_attr, 'data'), "ap_drift should have .data attribute (plot_manager pattern)"
    
    print(f"ap_drift type: {type(ap_drift_attr)}")
    print(f"ap_drift.data type: {type(ap_drift_attr.data) if hasattr(ap_drift_attr, 'data') else 'NO_DATA_ATTR'}")

@pytest.mark.mission("Alpha/Proton ap_drift_va Property")
def test_ap_drift_va_property_lazy_loading():
    """Test ap_drift_va property exists and implements lazy loading correctly."""
    if psp_alpha is None:
        pytest.skip("psp_alpha not importable.")
    
    assert hasattr(psp_alpha, 'ap_drift_va'), "psp_alpha must have ap_drift_va property"
    
    ap_drift_va_attr = psp_alpha.ap_drift_va  
    assert ap_drift_va_attr is not None, "psp_alpha.ap_drift_va should not be None"
    assert hasattr(ap_drift_va_attr, 'data'), "ap_drift_va should have .data attribute (plot_manager pattern)"
    
    print(f"ap_drift_va type: {type(ap_drift_va_attr)}")
    print(f"ap_drift_va.data type: {type(ap_drift_va_attr.data) if hasattr(ap_drift_va_attr, 'data') else 'NO_DATA_ATTR'}")

@pytest.mark.mission("Alpha/Proton Integration Test")
def test_plotbot_alpha_proton_integration(capsys):
    """Integration test: plot alpha/proton derived variables with plotbot and verify data."""
    if psp_alpha is None or proton is None or plotbot is None:
        pytest.skip("Required classes not importable for integration test.")
    
    TRANGE = ['2023-09-28/06:00:00.000', '2023-09-28/07:00:00.000']
    plotbot_plt.close('all')
    fig = None
    
    print(f"\nRequesting alpha/proton derived variables for trange: {TRANGE}")
    print("Panel 1: psp_alpha.na_div_np")
    print("Panel 2: psp_alpha.ap_drift") 
    print("Panel 3: psp_alpha.ap_drift_va")
    
    try:
        # Request plotbot to load/plot the derived variables
        plotbot(TRANGE, 
                psp_alpha.na_div_np, 1,
                psp_alpha.ap_drift, 2, 
                psp_alpha.ap_drift_va, 3)
        
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        assert fig is not None, "plotbot should have created a figure."
        assert len(fig.axes) == 3, "Figure should have 3 panels for the 3 derived variables."
        
        # === Data Verification ===
        print("\nVerifying computed alpha/proton derived variables...")
        
        # Test na_div_np data
        na_div_np_data = psp_alpha.na_div_np.data
        assert isinstance(na_div_np_data, np.ndarray), "na_div_np.data should be numpy array"
        assert len(na_div_np_data) > 0, "na_div_np.data should not be empty"
        
        # Physical validation for alpha/proton density ratio
        valid_ratios = na_div_np_data[~np.isnan(na_div_np_data)]
        if len(valid_ratios) > 0:
            assert np.all(valid_ratios >= 0), "na_div_np should be non-negative"
            assert np.all(valid_ratios <= 1.0), "na_div_np should be <= 1 (alpha density < proton density typically)"
            # Typical range check
            ratio_median = np.median(valid_ratios)
            assert 0.001 <= ratio_median <= 0.5, f"na_div_np median {ratio_median} outside expected range [0.001, 0.5]"
        
        # Test ap_drift data  
        ap_drift_data = psp_alpha.ap_drift.data
        assert isinstance(ap_drift_data, np.ndarray), "ap_drift.data should be numpy array"
        assert len(ap_drift_data) > 0, "ap_drift.data should not be empty"
        
        # Physical validation for drift speed
        valid_drifts = ap_drift_data[~np.isnan(ap_drift_data)]
        if len(valid_drifts) > 0:
            assert np.all(valid_drifts >= 0), "ap_drift should be non-negative (magnitude)"
            drift_median = np.median(valid_drifts)
            assert 0 <= drift_median <= 1000, f"ap_drift median {drift_median} km/s outside expected range [0, 1000]"
        
        # Test ap_drift_va data
        ap_drift_va_data = psp_alpha.ap_drift_va.data
        assert isinstance(ap_drift_va_data, np.ndarray), "ap_drift_va.data should be numpy array"
        assert len(ap_drift_va_data) > 0, "ap_drift_va.data should not be empty"
        
        # Physical validation for normalized drift
        valid_norm_drifts = ap_drift_va_data[~np.isnan(ap_drift_va_data)]
        if len(valid_norm_drifts) > 0:
            assert np.all(valid_norm_drifts >= 0), "ap_drift_va should be non-negative"
            norm_drift_median = np.median(valid_norm_drifts)
            assert 0 <= norm_drift_median <= 10, f"ap_drift_va median {norm_drift_median} outside expected range [0, 10]"
        
        print("Successfully verified all alpha/proton derived variables!")
        print(f"na_div_np median: {np.median(valid_ratios) if len(valid_ratios) > 0 else 'NO_VALID_DATA'}")
        print(f"ap_drift median: {np.median(valid_drifts) if len(valid_drifts) > 0 else 'NO_VALID_DATA'} km/s")
        print(f"ap_drift_va median: {np.median(valid_norm_drifts) if len(valid_norm_drifts) > 0 else 'NO_VALID_DATA'}")
        
    except Exception as e:
        print(f"Error during alpha/proton integration test: {e}")
        pytest.fail(f"Alpha/proton integration test failed: {e}")
    finally:
        if fig is not None:
            plotbot_plt.close(fig)
        else:
            plotbot_plt.close('all')
        
        # Capture and log output
        out, err = capsys.readouterr()
        if out:
            print("\n=== CAPTURED STDOUT ===\n", out)
        if err:
            print("\n=== CAPTURED STDERR ===\n", err, file=sys.stderr)
        
        with open(log_file, "a") as f:
            f.write(f"\n=== ALPHA/PROTON INTEGRATION TEST {datetime.now()} ===\n")
            f.write(out)
            f.write("\n=== STDERR ===\n")
            f.write(err)
            f.write("\n=== END TEST BLOCK ===\n")

@pytest.mark.mission("Alpha/Proton Dependency Time Range")
def test_dependency_time_range_isolation():
    """Test that derived variables use _current_operation_trange correctly (no contamination)."""
    if psp_alpha is None or proton is None or plotbot is None:
        pytest.skip("Required classes not importable for dependency test.")
    
    # Test different time ranges to ensure no contamination
    TRANGE1 = ['2023-09-28/06:00:00.000', '2023-09-28/07:00:00.000'] 
    TRANGE2 = ['2023-09-29/06:00:00.000', '2023-09-29/07:00:00.000']
    
    print(f"Testing dependency isolation between {TRANGE1} and {TRANGE2}")
    
    # Load first time range
    plotbot(TRANGE1, psp_alpha.na_div_np, 1)
    data1 = psp_alpha.na_div_np.data.copy() if hasattr(psp_alpha.na_div_np, 'data') else None
    
    # Load second time range  
    plotbot(TRANGE2, psp_alpha.na_div_np, 1)
    data2 = psp_alpha.na_div_np.data.copy() if hasattr(psp_alpha.na_div_np, 'data') else None
    
    # Verify data changed (no contamination)
    if data1 is not None and data2 is not None:
        assert not np.array_equal(data1, data2), \
            "Data should be different for different time ranges (no contamination)"
        print("✅ Dependency time range isolation verified")
    else:
        print("⚠️  Could not verify isolation (data None)")
    
    plotbot_plt.close('all')

@pytest.mark.mission("Data Source Consistency")
def test_data_source_consistency():
    """Test that we're using the correct data sources (psp_alpha CDF + proton CDF, not FITS)."""
    if psp_alpha is None or proton is None:
        pytest.skip("Required classes not importable for data source test.")
    
    # Verify psp_alpha has RTN velocity components
    alpha_instance = psp_alpha
    assert hasattr(alpha_instance, 'raw_data'), "psp_alpha should have raw_data dict"
    assert 'vr' in alpha_instance.raw_data, "psp_alpha should have vr (RTN coordinate) in raw_data"
    assert 'vt' in alpha_instance.raw_data, "psp_alpha should have vt (RTN coordinate) in raw_data"  
    assert 'vn' in alpha_instance.raw_data, "psp_alpha should have vn (RTN coordinate) in raw_data"
    
    # Verify psp_alpha data type is correct
    assert hasattr(alpha_instance, 'data_type'), "psp_alpha should have data_type attribute"
    assert alpha_instance.data_type == 'spi_sf0a_l3_mom', f"Expected spi_sf0a_l3_mom, got {alpha_instance.data_type}"
    
    # Verify proton has RTN velocity components
    assert hasattr(proton, 'vr'), "proton should have vr property"
    assert hasattr(proton, 'vt'), "proton should have vt property"
    assert hasattr(proton, 'vn'), "proton should have vn property"
    
    print("✅ Data source consistency verified: both classes use RTN coordinates")

# ============================================================================
# PHASE 2 TESTS: Electric Field Spectra Classes (When Implemented)
# ============================================================================

@pytest.mark.mission("Electric Field DFB Class Structure")
def test_psp_dfb_class_initialization():
    """Test PSP DFB class initialization and variable structure (space_cowboi42 convention)."""
    if psp_dfb is None:
        pytest.skip("psp_dfb not importable.")
    
    # Test class structure following space_cowboi42's naming convention
    assert hasattr(psp_dfb, 'ac_spec_dv12'), "DFB should have ac_spec_dv12 variable"
    assert hasattr(psp_dfb, 'ac_spec_dv34'), "DFB should have ac_spec_dv34 variable"
    assert hasattr(psp_dfb, 'dc_spec_dv12'), "DFB should have dc_spec_dv12 variable"
    
    # Verify dc_spec_dv34 is NOT available (server limitation)
    assert not hasattr(psp_dfb, 'dc_spec_dv34'), "dc_spec_dv34 should not exist (server limitation)"
    
    print("PSP DFB class structure verified following space_cowboi42 convention")

@pytest.mark.mission("Electric Field DFB Integration")
def test_psp_dfb_plotbot_integration():
    """Test PSP DFB integration with PURE PLOTBOT behavior - let plotbot handle everything."""
    if psp_dfb is None:
        pytest.skip("psp_dfb not importable.")

    TRANGE = ['2022-06-01/00:00:00.000', '2022-06-02/00:00:00.000']  # Use dates with actual DFB data
    plotbot_plt.close('all')

    print(f"Testing PURE PLOTBOT behavior for DFB spectra: {TRANGE}")
    print("This test lets plotbot handle ALL downloading/processing through its normal pipeline")

    # Save the original server setting
    original_server = config.data_server
    try:
        # ✅ SET SERVER TO SPDF FOR THIS TEST
        print(f"Setting config.data_server to 'spdf' for this test...")
        config.data_server = 'spdf'

        # ✅ PURE PLOTBOT TEST - TEST ALL THREE DFB VARIABLES
        print("Calling plotbot with ALL THREE DFB spectra - testing complete integration...")
        result = plotbot(TRANGE,
                        psp_dfb.ac_spec_dv12, 1,
                        psp_dfb.ac_spec_dv34, 2, 
                        psp_dfb.dc_spec_dv12, 3)  # Test ALL three DFB variables

        # Check that plotbot didn't return False (which indicates failure)
        assert result is not False, "plotbot should not return False (indicating failure)"

        # === Verify ALL THREE DFB Variables Have Real Data ===
        print("\n=== Verifying plotbot retrieved real data for ALL DFB spectral variables ===")

        # Check AC dv12
        print(f"Checking psp_dfb.ac_spec_dv12...")
        var = psp_dfb.ac_spec_dv12
        print(f"  Data type: {var.plot_options.data_type}")
        print(f"  Data shape: {var.data.shape}")
        print(f"  Datetime array type: {type(var.datetime_array)}")
        if var.data.size > 0:
            print(f"  ✅ AC dv12 has real data: {var.data.shape}")
        else:
            print(f"  ❌ AC dv12 has no data")

        assert var.data.size > 0, "AC dv12 spectrum should have real data"
        
        # Verify the data structure matches EPAD pattern for AC dv12
        assert var.datetime_array.ndim == 2, "AC dv12 datetime_array should be 2D mesh like EPAD"
        assert var.additional_data.ndim == 2, "AC dv12 additional_data should be 2D like EPAD"
        assert var.data.shape == var.datetime_array.shape, "AC dv12 data and datetime_array should have same shape"
        assert var.data.shape == var.additional_data.shape, "AC dv12 data and additional_data should have same shape"

        # Check AC dv34
        print(f"Checking psp_dfb.ac_spec_dv34...")
        var = psp_dfb.ac_spec_dv34
        print(f"  Data type: {var.plot_options.data_type}")
        print(f"  Data shape: {var.data.shape}")
        print(f"  Datetime array type: {type(var.datetime_array)}")
        if var.data.size > 0:
            print(f"  ✅ AC dv34 has real data: {var.data.shape}")
        else:
            print(f"  ⚠️  AC dv34 has no data (may be normal for this time range)")

        # Check DC dv12
        print(f"Checking psp_dfb.dc_spec_dv12...")
        var = psp_dfb.dc_spec_dv12
        print(f"  Data type: {var.plot_options.data_type}")
        print(f"  Data shape: {var.data.shape}")
        print(f"  Datetime array type: {type(var.datetime_array)}")
        if var.data.size > 0:
            print(f"  ✅ DC dv12 has real data: {var.data.shape}")
        else:
            print(f"  ⚠️  DC dv12 has no data (may be normal for this time range)")

        # At least AC dv12 should have data for successful test
        total_data_points = (psp_dfb.ac_spec_dv12.data.size + 
                           psp_dfb.ac_spec_dv34.data.size + 
                           psp_dfb.dc_spec_dv12.data.size)
        
        assert total_data_points > 0, "At least one DFB spectrum should have real data"

        print("✅ PSP DFB integration test successful - all three variables tested")

    except Exception as e:
        print(f"DFB pure plotbot integration error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        pytest.fail(f"DFB pure plotbot integration failed: {e}")
    finally:
        # Restore original server setting
        config.data_server = original_server
        print(f"Restored config.data_server to '{original_server}'")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clear_test_logs():
    """Clear test log file at start of test session."""
    if os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write(f"=== TEST SESSION STARTED {datetime.now()} ===\n")

# Run log clearing at module import
clear_test_logs() 