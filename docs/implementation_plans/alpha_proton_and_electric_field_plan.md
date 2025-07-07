# Alpha/Proton Derived Variables & Electric Field Spectra Implementation Plan

*Implementation roadmap for completing PSP alpha-proton analysis capabilities and electric field spectral data integration*

## Executive Summary

This document outlines the implementation plan for two interconnected PSP data analysis capabilities:
1. **Alpha/Proton Derived Variables** - Computing density ratios and drift speeds between alpha particles and protons
2. **Electric Field Spectra Classes** - Adding PSP FIELDS electric field AC/DC spectral data integration

## Current State Assessment

### ✅ Completed Infrastructure
- **PSP QTN Integration** - `psp_qtn.density` and `psp_qtn.temperature` fully operational (v2.74)
- **Alpha Particle Classes** - `psp_alpha_classes.py` with basic alpha particle data integration
- **Proton Classes** - Multiple proton data classes (`proton`, `proton_hr`, `proton_fits`)
- **Electric Field Exploration** - Notebooks showing AC/DC spectrum data structure analysis

### 🔄 In Progress / Missing
- **Alpha/Proton Derived Variables** - Three key variables need implementation
- **Electric Field Data Classes** - Need structured classes for AC/DC spectra
- **Implementation Sequence** - Clear priority order for development

## Phase 1: Alpha/Proton Derived Variables (PRIORITY)

### 1.1 Required Variables

**Variable 1: `na_div_np` - Alpha/Proton Density Ratio**
```python
# Formula: na_div_np = DENS_alpha / (DENS_proton_core + DENS_proton_beam)
# Usage: alpha_fits.na_div_np or similar access pattern
```

**Variable 2: `ap_drift` - Alpha-Proton Drift Speed**
```python
# Formula: ap_drift = |VEL_alpha - VEL_proton| (vector magnitude)
# Use VEL_RTN_SUN coordinate system for both species
# Units: km/s
```

**Variable 3: `ap_drift_va` - Drift Speed Normalized by Alfvén Speed**
```python
# Formula: ap_drift_va = ap_drift / v_alfven
# Where: v_alfven = 21.8 * |MAGF_INST| / sqrt(DENS_proton + DENS_alpha)
# Dimensionless ratio
```

### 1.2 Implementation Strategy

**Data Handling Approach:**
- **Interpolation Required** - Downsample/interpolate proton data to alpha cadence
- **Coordinate System** - Use `VEL_RTN_SUN` for consistent velocity comparisons
- **Magnetic Field** - Use `|MAGF_INST|` for Alfvén speed calculations
- **Density Sources** - Combine proton core + beam densities vs alpha density

**Dependencies Integration (CRITICAL):**
- **Follow the "Sticky Note" System** from `dependencies_best_practices_plan.md`
- **Data Class Initialization:** Add `object.__setattr__(self, '_current_operation_trange', None)` in `__init__`
- **Update Method:** Modify `update()` method signature to accept `original_requested_trange: Optional[List[str]] = None`
- **Store Time Range:** `object.__setattr__(self, '_current_operation_trange', original_requested_trange)` in `update()`
- **Data Cubby Integration:** Ensure `data_cubby.update_global_instance()` passes `original_requested_trange`
- **Dependency Calculations:** Use `self._current_operation_trange` for all `get_data()` calls
- **Error Handling:** Graceful failure when `_current_operation_trange` is None
- **Interpolation Strategy:** Use consistent time range for both alpha and proton data fetching

### 1.3 Code Implementation Locations

**Option A: Extend Existing Alpha Classes (RECOMMENDED)**
```python
# In psp_alpha_classes.py or psp_alpha_fits_classes.py
# Following dependencies_best_practices_plan.md patterns

@property
def na_div_np(self):
    """Alpha/proton density ratio with lazy loading and dependency management."""
    if not hasattr(self, '_na_div_np_manager'):
        # Create placeholder manager
        self._na_div_np_manager = plot_manager(
            np.array([]),
            plot_options=ploptions(...)
        )
    
    # Check if calculation is needed
    if self.raw_data.get('na_div_np') is None:
        success = self._calculate_alpha_proton_derived()
        if success and self.raw_data.get('na_div_np') is not None:
            # Update manager with calculated data
            self._na_div_np_manager = plot_manager(
                self.raw_data['na_div_np'],
                plot_options=self._na_div_np_manager.plot_options
            )
    
    return self._na_div_np_manager

@property  
def ap_drift(self):
    """Alpha-proton drift speed with lazy loading and dependency management."""
    if not hasattr(self, '_ap_drift_manager'):
        self._ap_drift_manager = plot_manager(np.array([]), plot_options=ploptions(...))
    
    if self.raw_data.get('ap_drift') is None:
        success = self._calculate_alpha_proton_derived()
        if success and self.raw_data.get('ap_drift') is not None:
            self._ap_drift_manager = plot_manager(
                self.raw_data['ap_drift'],
                plot_options=self._ap_drift_manager.plot_options
            )
    
    return self._ap_drift_manager

@property
def ap_drift_va(self):
    """Drift speed normalized by Alfvén speed with lazy loading and dependency management."""
    if not hasattr(self, '_ap_drift_va_manager'):
        self._ap_drift_va_manager = plot_manager(np.array([]), plot_options=ploptions(...))
    
    if self.raw_data.get('ap_drift_va') is None:
        success = self._calculate_alpha_proton_derived()
        if success and self.raw_data.get('ap_drift_va') is not None:
            self._ap_drift_va_manager = plot_manager(
                self.raw_data['ap_drift_va'], 
                plot_options=self._ap_drift_va_manager.plot_options
            )
    
    return self._ap_drift_va_manager

def _calculate_alpha_proton_derived(self):
    """Calculate alpha-proton derived variables using dependency best practices."""
    from plotbot.get_data import get_data
    from plotbot import proton  # or proton_fits, depending on source
    
    # CRITICAL: Use the stored operation trange for dependencies
    trange_for_dependencies = None
    if hasattr(self, '_current_operation_trange') and self._current_operation_trange is not None:
        trange_for_dependencies = self._current_operation_trange
        print_manager.dependency_management(f"Using _current_operation_trange: {trange_for_dependencies}")
    else:
        print_manager.error("Cannot determine time range for dependencies: _current_operation_trange is None")
        self.raw_data.update({'na_div_np': None, 'ap_drift': None, 'ap_drift_va': None})
        return False
    
    # Fetch proton data with correct time range
    get_data(trange_for_dependencies, proton.density)
    get_data(trange_for_dependencies, proton.vr)  # or VEL_RTN_SUN components
    get_data(trange_for_dependencies, proton.vt)
    get_data(trange_for_dependencies, proton.vn)
    get_data(trange_for_dependencies, proton.bmag)  # for Alfvén speed
    
    # Validation
    if not proton.density.data or len(proton.density.data) == 0:
        print_manager.error(f"Proton dependency data unavailable for trange {trange_for_dependencies}")
        self.raw_data.update({'na_div_np': None, 'ap_drift': None, 'ap_drift_va': None})
        return False
    
    # Interpolate proton data to alpha cadence
    # (Implementation details for interpolation)
    
    # Calculate derived variables
    # na_div_np = alpha_density / (proton_density_core + proton_density_beam)
    # ap_drift = |VEL_alpha - VEL_proton| vector magnitude  
    # v_alfven = 21.8 * |B| / sqrt(proton_density + alpha_density)
    # ap_drift_va = ap_drift / v_alfven
    
    # Store results
    self.raw_data.update({
        'na_div_np': calculated_ratio,
        'ap_drift': calculated_drift,
        'ap_drift_va': calculated_normalized_drift
    })
    
    return True
```

**Option B: Create New Derived Variables Class**
```python
# New file: psp_alpha_proton_derived.py
class alpha_proton_derived_class:
    """Class for alpha-proton comparative analysis variables."""
    # Handles interpolation, drift calculations, and ratio computations
```

## Phase 2: Electric Field Spectra Classes

### 2.1 Class Structure Design

**NEW CLASS FILE: `plotbot/data_classes/psp_dfb_classes.py`**
*Following patterns from `wind_3dp_classes.py` and `wind_mfi_classes.py`*

**Single Class: `psp_dfb` (Following space_cowboi42's Convention)**
```python
# File: plotbot/data_classes/psp_dfb_classes.py
class psp_dfb_class:
    """PSP FIELDS Digital Fields Board (DFB) electric field spectra data."""
    # Mirror structure of wind_3dp_elpd_class and wind_mfi_h2_class
    
    # Variables follow space_cowboi42's naming convention:
    # - ac_spec_dv12: AC spectrum from antenna pair 12
    # - ac_spec_dv34: AC spectrum from antenna pair 34  
    # - dc_spec_dv12: DC spectrum from antenna pair 12 (only available configuration)
    
    # Example access:
    # psp_dfb.ac_spec_dv12  → AC spectrum data from dv12 antennas
    # psp_dfb.ac_spec_dv34  → AC spectrum data from dv34 antennas  
    # psp_dfb.dc_spec_dv12  → DC spectrum data from dv12 antennas
    
    def __init__(self, imported_data):
        # Follow wind_3dp_elpd_class pattern exactly
        object.__setattr__(self, 'class_name', 'psp_dfb')
        object.__setattr__(self, 'data_type', 'psp_dfb') 
        object.__setattr__(self, 'subclass_name', None)
        object.__setattr__(self, 'raw_data', {
            'ac_spec_dv12': None,     # AC spectrum dv12
            'ac_spec_dv34': None,     # AC spectrum dv34
            'dc_spec_dv12': None,     # DC spectrum dv12 (only available)
            'ac_freq_bins_dv12': None,  # Frequency bins for AC dv12
            'ac_freq_bins_dv34': None,  # Frequency bins for AC dv34  
            'dc_freq_bins_dv12': None,  # Frequency bins for DC dv12
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'times_mesh_ac_dv12', None)  # For spectral plotting
        object.__setattr__(self, 'times_mesh_ac_dv34', None)
        object.__setattr__(self, 'times_mesh_dc_dv12', None)
        object.__setattr__(self, '_current_operation_trange', None)
        
    def calculate_variables(self, imported_data):
        """Extract electric field spectra from PySpedas CDF data."""
        # ⭐️ THIS IS THE SPECIAL MATH FROM e10_iaw.ipynb ⭐️
        
        # STEP 1: Extract raw spectral data from PySpedas variables
        # Following exact e10_iaw.ipynb implementation patterns:
        
        # AC Spectrum Processing (dv12 and dv34):
        ac_data_dv12 = get_data('psp_fld_l2_dfb_ac_spec_dV12hg')
        if ac_data_dv12:
            ac_times_dv12 = ac_data_dv12.times        # Time array
            ac_freq_vals_dv12 = ac_data_dv12.v        # Frequency values (54 bins)
            ac_vals_dv12 = ac_data_dv12.y             # Spectral data [N_time x 54]
            
            # Time mesh creation for spectral plotting:
            datetime_ac_dv12 = time_datetime(ac_times_dv12)
            times_ac_repeat_dv12 = np.repeat(np.expand_dims(datetime_ac_dv12,1), 54, 1)
            
        ac_data_dv34 = get_data('psp_fld_l2_dfb_ac_spec_dV34hg')
        if ac_data_dv34:
            # Same pattern for dv34...
            
        # DC Spectrum Processing (dv12 only - dv34 not available):
        dc_data_dv12 = get_data('psp_fld_l2_dfb_dc_spec_dV12hg') 
        if dc_data_dv12:
            dc_times_dv12 = dc_data_dv12.times        # Time array
            dc_freq_vals_dv12 = dc_data_dv12.v        # Frequency values
            dc_vals_dv12 = dc_data_dv12.y             # Spectral data
            
            # Time mesh for DC plotting:
            datetime_dc_dv12 = time_datetime(dc_times_dv12)
            times_dc_repeat_dv12 = np.repeat(np.expand_dims(datetime_dc_dv12,1), 54, 1)
            
        # STEP 2: Store processed data in raw_data dictionary
        self.raw_data = {
            'ac_spec_dv12': ac_vals_dv12,               # [N_time x 54] spectral data
            'ac_freq_bins_dv12': ac_freq_vals_dv12,     # [54] frequency bins
            'ac_spec_dv34': ac_vals_dv34,               # [N_time x 54] spectral data  
            'ac_freq_bins_dv34': ac_freq_vals_dv34,     # [54] frequency bins
            'dc_spec_dv12': dc_vals_dv12,               # [N_time x 54] spectral data
            'dc_freq_bins_dv12': dc_freq_vals_dv12,     # [54] frequency bins
        }
        
        # STEP 3: Store time meshes for spectral plotting (wind_3dp_elpd pattern)
        self.times_mesh_ac_dv12 = times_ac_repeat_dv12
        self.times_mesh_ac_dv34 = times_ac_repeat_dv34  
        self.times_mesh_dc_dv12 = times_dc_repeat_dv12
        
    def set_ploptions(self):
        """Set up plotting options - follow wind_3dp_elpd_class pattern for spectral data"""
        # Create plot_manager instances for each spectrum with proper spectral plotting
```

**Variable Structure:**
```python
class psp_dfb_class:
    # AC Spectrum Variables
    ac_spec_dv12: plot_manager  # AC spectrum from antenna pair 1-2
    ac_spec_dv34: plot_manager  # AC spectrum from antenna pair 3-4
    
    # DC Spectrum Variables  
    dc_spec_dv12: plot_manager  # DC spectrum from antenna pair 1-2
    # Note: dc_spec_dv34 not available (server limitation confirmed)
```

### 2.2 Data Structure Analysis

**From e10_iaw.ipynb Analysis:**
```python
# AC Spectrum Structure (Confirmed from notebook):
Variable                                    Type            Shape
epoch_ac_spec_dV12hg                       TIME_TT2000     [N_time]
psp_fld_l2_dfb_ac_spec_dV12hg_frequency_bins  FLOAT       [54]        # Frequency bins
psp_fld_l2_dfb_ac_spec_dV12hg              FLOAT           [N_time x 54]  # Spectral data

# DC Spectrum Structure (Confirmed from notebook):
epoch_dc_spec_dV12hg                       TIME_TT2000     [N_time]  
psp_fld_l2_dfb_dc_spec_dV12hg_frequency_bins  FLOAT       [54]        # Frequency bins
psp_fld_l2_dfb_dc_spec_dV12hg              FLOAT           [N_time x 54]  # Spectral data

# Key Implementation Notes from e10_iaw.ipynb:
# - Frequency axis has 54 bins (confirmed)
# - Data accessed via get_data() returns .times, .v (frequencies), .y (spectra)
# - Time manipulation: np.repeat(np.expand_dims(datetime_ac,1), 54, 1) for plotting
# - "Instead of degrees on the y axis we have frequency"
```

**PySpedas Integration (Exact e10_iaw.ipynb Implementation):**
```python
# From e10_iaw.ipynb - Tested working implementation
# Specify time range in the form ['yyyy-mm-dd/hh:mm:ss','yyyy-mm-dd/hh:mm:ss']
trange = ['2021-11-25','2021-11-26']

# Download AC spectrum data
dfb_ac_datatype = 'dfb_ac_spec'  # AC spectrum
dfb_ac_vars = pyspedas.psp.fields(trange=trange, datatype=dfb_ac_datatype, level='l2', time_clip=True)

# Download DC spectrum data  
dfb_dc_datatype = 'dfb_dc_spec'  # DC spectrum
dfb_dc_vars = pyspedas.psp.fields(trange=trange, datatype=dfb_dc_datatype, level='l2', time_clip=True)

# Note: This creates CDF variables that can be accessed via get_data()
# Available variables: 
# - 'psp_fld_l2_dfb_ac_spec_dV12hg' and 'psp_fld_l2_dfb_ac_spec_dV34hg'
# - 'psp_fld_l2_dfb_dc_spec_dV12hg' (dv34 not available for DC)
```

### 2.3 Plotting Integration

**Data Access (⭐️ THIS is how we access the electric field spectra):**
```python
# From e10_iaw.ipynb - Exact implementation reference
# Specify time range in the form ['yyyy-mm-dd/hh:mm:ss','yyyy-mm-dd/hh:mm:ss']
trange = ['2021-11-25','2021-11-26']
dfb_ac_datatype = 'dfb_ac_spec'  # AC spectrum
dfb_ac_vars = pyspedas.psp.fields(trange=trange, datatype=dfb_ac_datatype, level='l2', time_clip=True)

# For DC spectrum:
dfb_dc_datatype = 'dfb_dc_spec'  # DC spectrum  
dfb_dc_vars = pyspedas.psp.fields(trange=trange, datatype=dfb_dc_datatype, level='l2', time_clip=True)
```

**Spectrogram Plotting (⭐️ THIS is how we plot it):**
```python
# From e10_iaw.ipynb - Exact plotting implementation
# Instead of degrees on the y axis we have frequency
ac_data = get_data('psp_fld_l2_dfb_ac_spec_dV12hg')
ac_times = ac_data.times
ac_freq_vals = ac_data.v          # Frequency values (54 bins)
ac_vals = ac_data.y               # Spectral data
datetime_ac = time_datetime(ac_times)
times_ac_repeat = np.repeat(np.expand_dims(datetime_ac,1), 54, 1)

# For DC spectrum (dv12 only - dv34 not available):
dc_data = get_data('psp_fld_l2_dfb_dc_spec_dV12hg')
dc_times = dc_data.times
dc_freq_vals = dc_data.v          # Frequency values
dc_vals = dc_data.y               # Spectral data  
datetime_dc = time_datetime(dc_times)
times_dc_repeat = np.repeat(np.expand_dims(datetime_dc,1), 54, 1)

# Key data structure:
# ac_data.times: Time array
# ac_data.v: Frequency bins [54 elements] 
# ac_data.y: Spectral data [N_time x 54]
```

**Variable Names from CDF Files:**
```python
# AC Spectrum Variables:
'psp_fld_l2_dfb_ac_spec_dV12hg'              # AC spectrum dv12 data
'psp_fld_l2_dfb_ac_spec_dV12hg_frequency_bins'  # AC spectrum dv12 frequencies
'psp_fld_l2_dfb_ac_spec_dV34hg'              # AC spectrum dv34 data  
'psp_fld_l2_dfb_ac_spec_dV34hg_frequency_bins'  # AC spectrum dv34 frequencies

# DC Spectrum Variables:
'psp_fld_l2_dfb_dc_spec_dV12hg'              # DC spectrum dv12 data
'psp_fld_l2_dfb_dc_spec_dV12hg_frequency_bins'  # DC spectrum dv12 frequencies
# Note: dv34 not available for DC spectrum (server limitation confirmed)
```

## Implementation-First Development Strategy

Following the preferred workflow: **Code First → Push → Tests → Push → Validate**. We'll use the successful pattern from `test_psp_mag_br_norm.py` for comprehensive validation after implementation.

### Test File: `test_alpha_proton_electric_field.py`

**Location:** `tests/test_alpha_proton_electric_field.py`
**Log Output:** `tests/test_logs/test_alpha_proton_electric_field.txt`

```python
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
    from plotbot import alpha_fits, proton, mag_rtn_4sa, plt as plotbot_plt, plotbot
    # For Phase 2: from plotbot import psp_dfb
except ImportError as e:
    alpha_fits = None
    proton = None
    plotbot = None
    plotbot_plt = plt

# Test log file path
log_file = os.path.join(os.path.dirname(__file__), "test_logs", "test_alpha_proton_electric_field.txt")

# ============================================================================
# PHASE 1 TESTS: Alpha/Proton Derived Variables
# ============================================================================

@pytest.mark.mission("Alpha/Proton Dependency Management")
def test_alpha_fits_dependency_infrastructure():
    """Test that alpha_fits class has proper dependency management infrastructure."""
    if alpha_fits is None:
        pytest.skip("alpha_fits not importable.")
    
    # Create minimal test instance
    TRANGE = ['2023-09-28/06:00:00.000', '2023-09-28/07:00:00.000']
    
    # Test that _current_operation_trange is properly initialized
    # This test should FAIL initially, then PASS after implementation
    alpha_instance = alpha_fits  # Get the global instance
    assert hasattr(alpha_instance, '_current_operation_trange'), \
        "alpha_fits must have _current_operation_trange attribute for dependency management"
    
    print(f"alpha_fits._current_operation_trange: {getattr(alpha_instance, '_current_operation_trange', 'NOT_FOUND')}")

@pytest.mark.mission("Alpha/Proton na_div_np Property")
def test_na_div_np_property_lazy_loading():
    """Test na_div_np property exists and implements lazy loading correctly."""
    if alpha_fits is None:
        pytest.skip("alpha_fits not importable.")
    
    # Test property existence
    assert hasattr(alpha_fits, 'na_div_np'), "alpha_fits must have na_div_np property"
    
    # Test that it returns a plot_manager instance
    na_div_np_attr = alpha_fits.na_div_np
    assert na_div_np_attr is not None, "alpha_fits.na_div_np should not be None"
    assert hasattr(na_div_np_attr, 'data'), "na_div_np should have .data attribute (plot_manager pattern)"
    
    print(f"na_div_np type: {type(na_div_np_attr)}")
    print(f"na_div_np.data type: {type(na_div_np_attr.data) if hasattr(na_div_np_attr, 'data') else 'NO_DATA_ATTR'}")

@pytest.mark.mission("Alpha/Proton ap_drift Property") 
def test_ap_drift_property_lazy_loading():
    """Test ap_drift property exists and implements lazy loading correctly."""
    if alpha_fits is None:
        pytest.skip("alpha_fits not importable.")
    
    assert hasattr(alpha_fits, 'ap_drift'), "alpha_fits must have ap_drift property"
    
    ap_drift_attr = alpha_fits.ap_drift
    assert ap_drift_attr is not None, "alpha_fits.ap_drift should not be None"
    assert hasattr(ap_drift_attr, 'data'), "ap_drift should have .data attribute (plot_manager pattern)"
    
    print(f"ap_drift type: {type(ap_drift_attr)}")
    print(f"ap_drift.data type: {type(ap_drift_attr.data) if hasattr(ap_drift_attr, 'data') else 'NO_DATA_ATTR'}")

@pytest.mark.mission("Alpha/Proton ap_drift_va Property")
def test_ap_drift_va_property_lazy_loading():
    """Test ap_drift_va property exists and implements lazy loading correctly."""
    if alpha_fits is None:
        pytest.skip("alpha_fits not importable.")
    
    assert hasattr(alpha_fits, 'ap_drift_va'), "alpha_fits must have ap_drift_va property"
    
    ap_drift_va_attr = alpha_fits.ap_drift_va  
    assert ap_drift_va_attr is not None, "alpha_fits.ap_drift_va should not be None"
    assert hasattr(ap_drift_va_attr, 'data'), "ap_drift_va should have .data attribute (plot_manager pattern)"
    
    print(f"ap_drift_va type: {type(ap_drift_va_attr)}")
    print(f"ap_drift_va.data type: {type(ap_drift_va_attr.data) if hasattr(ap_drift_va_attr, 'data') else 'NO_DATA_ATTR'}")

@pytest.mark.mission("Alpha/Proton Integration Test")
def test_plotbot_alpha_proton_integration(capsys):
    """Integration test: plot alpha/proton derived variables with plotbot and verify data."""
    if alpha_fits is None or proton is None or plotbot is None:
        pytest.skip("Required classes not importable for integration test.")
    
    TRANGE = ['2023-09-28/06:00:00.000', '2023-09-28/07:00:00.000']
    plotbot_plt.close('all')
    fig = None
    
    print(f"\nRequesting alpha/proton derived variables for trange: {TRANGE}")
    print("Panel 1: alpha_fits.na_div_np")
    print("Panel 2: alpha_fits.ap_drift") 
    print("Panel 3: alpha_fits.ap_drift_va")
    
    try:
        # Request plotbot to load/plot the derived variables
        plotbot(TRANGE, 
                alpha_fits.na_div_np, 1,
                alpha_fits.ap_drift, 2, 
                alpha_fits.ap_drift_va, 3)
        
        fig_num = plt.gcf().number
        fig = plt.figure(fig_num)
        assert fig is not None, "plotbot should have created a figure."
        assert len(fig.axes) == 3, "Figure should have 3 panels for the 3 derived variables."
        
        # === Data Verification ===
        print("\nVerifying computed alpha/proton derived variables...")
        
        # Test na_div_np data
        na_div_np_data = alpha_fits.na_div_np.data
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
        ap_drift_data = alpha_fits.ap_drift.data
        assert isinstance(ap_drift_data, np.ndarray), "ap_drift.data should be numpy array"
        assert len(ap_drift_data) > 0, "ap_drift.data should not be empty"
        
        # Physical validation for drift speed
        valid_drifts = ap_drift_data[~np.isnan(ap_drift_data)]
        if len(valid_drifts) > 0:
            assert np.all(valid_drifts >= 0), "ap_drift should be non-negative (magnitude)"
            drift_median = np.median(valid_drifts)
            assert 0 <= drift_median <= 1000, f"ap_drift median {drift_median} km/s outside expected range [0, 1000]"
        
        # Test ap_drift_va data
        ap_drift_va_data = alpha_fits.ap_drift_va.data
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
    if alpha_fits is None or proton is None or plotbot is None:
        pytest.skip("Required classes not importable for dependency test.")
    
    # Test different time ranges to ensure no contamination
    TRANGE1 = ['2023-09-28/06:00:00.000', '2023-09-28/07:00:00.000'] 
    TRANGE2 = ['2023-09-29/06:00:00.000', '2023-09-29/07:00:00.000']
    
    print(f"Testing dependency isolation between {TRANGE1} and {TRANGE2}")
    
    # Load first time range
    plotbot(TRANGE1, alpha_fits.na_div_np, 1)
    data1 = alpha_fits.na_div_np.data.copy() if hasattr(alpha_fits.na_div_np, 'data') else None
    
    # Load second time range  
    plotbot(TRANGE2, alpha_fits.na_div_np, 1)
    data2 = alpha_fits.na_div_np.data.copy() if hasattr(alpha_fits.na_div_np, 'data') else None
    
    # Verify data changed (no contamination)
    if data1 is not None and data2 is not None:
        assert not np.array_equal(data1, data2), \
            "Data should be different for different time ranges (no contamination)"
        print("✅ Dependency time range isolation verified")
    else:
        print("⚠️  Could not verify isolation (data None)")
    
    plotbot_plt.close('all')

# ============================================================================
# PHASE 2 TESTS: Electric Field Spectra Classes (When Implemented)
# ============================================================================

@pytest.mark.mission("Electric Field DFB Class Structure")
def test_psp_dfb_class_initialization():
    """Test PSP DFB class initialization and variable structure (space_cowboi42 convention)."""
    try:
        from plotbot import psp_dfb
    except ImportError:
        pytest.skip("psp_dfb not yet implemented (Phase 2)")
    
    # Test class structure following space_cowboi42's naming convention
    assert hasattr(psp_dfb, 'ac_spec_dv12'), "DFB should have ac_spec_dv12 variable"
    assert hasattr(psp_dfb, 'ac_spec_dv34'), "DFB should have ac_spec_dv34 variable"
    assert hasattr(psp_dfb, 'dc_spec_dv12'), "DFB should have dc_spec_dv12 variable"
    
    # Verify dc_spec_dv34 is NOT available (server limitation)
    assert not hasattr(psp_dfb, 'dc_spec_dv34'), "dc_spec_dv34 should not exist (server limitation)"
    
    print("PSP DFB class structure verified following space_cowboi42 convention")

@pytest.mark.mission("Electric Field DFB Integration")  
def test_psp_dfb_plotbot_integration():
    """Test PSP DFB integration with plotbot for electric field spectra."""
    try:
        from plotbot import psp_dfb
    except ImportError:
        pytest.skip("psp_dfb not yet implemented (Phase 2)")
    
    TRANGE = ['2021-11-25/00:00:00.000', '2021-11-26/00:00:00.000']
    plotbot_plt.close('all')
    
    print(f"Testing DFB spectra for trange: {TRANGE}")
    
    try:
        # Test plotting AC and DC spectra (following e10_iaw.ipynb implementation)
        # Using space_cowboi42's naming convention with exact data access pattern
        plotbot(TRANGE, 
                psp_dfb.ac_spec_dv12, 1,  # Maps to 'psp_fld_l2_dfb_ac_spec_dV12hg'
                psp_dfb.ac_spec_dv34, 2,  # Maps to 'psp_fld_l2_dfb_ac_spec_dV34hg'
                psp_dfb.dc_spec_dv12, 3)  # Maps to 'psp_fld_l2_dfb_dc_spec_dV12hg'
        
        fig = plt.gcf()
        assert fig is not None, "plotbot should create figure for DFB spectra"
        assert len(fig.axes) == 3, "Should have 3 panels for AC dv12, AC dv34, DC dv12"
        
        print("✅ PSP DFB plotbot integration successful")
        
    except Exception as e:
        print(f"DFB integration test error: {e}")
        pytest.fail(f"DFB integration failed: {e}")
    finally:
        plotbot_plt.close('all')

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
```

### Implementation-First Workflow

**Development Cycle:**
1. **Implement Code** → Add properties, calculations, infrastructure
2. **Push to Server** → Deploy changes for initial validation
3. **Create Tests** → Write comprehensive validation tests (using template)
4. **Push to GitHub** → Commit tests to repository  
5. **Run & Validate** → Execute tests and verify all functionality

**Test Categories (for validation after implementation):**
- **🏗️ Infrastructure Tests** - Dependency management, property structure
- **🔬 Calculation Tests** - Mathematical correctness, physical validation
- **🔗 Integration Tests** - plotbot integration, data flow verification  
- **🛡️ Isolation Tests** - Time range contamination prevention

**Running the Tests (After Implementation):**
```bash
# Run all alpha/proton tests
python -m pytest tests/test_alpha_proton_electric_field.py -v -s

# Run specific test categories
python -m pytest tests/test_alpha_proton_electric_field.py -k "dependency" -v -s
python -m pytest tests/test_alpha_proton_electric_field.py -k "integration" -v -s

# Follow test logs in real-time
tail -f tests/test_logs/test_alpha_proton_electric_field.txt
```

**Expected Test States:**
- **Before Implementation:** Tests should **SKIP** (classes/properties not available)
- **After Implementation:** Tests should **PASS** (full functionality working)
- **After Phase 2:** Electric field tests turn from SKIP → PASS

## Implementation Sequence & Priorities

### 🎯 Phase 1: Alpha/Proton Variables (IMPLEMENTATION-FIRST)
**Why Priority:** Self-contained, unlocks other analysis capabilities, builds on existing infrastructure

**EXTEND EXISTING CLASS FILE: `plotbot/data_classes/psp_alpha_fits_classes.py`**
*Add derived variables to existing alpha particle class, following wind_3dp/wind_mfi patterns*

**Steps:**
1. **Infrastructure setup** - Add dependency management to alpha class (`_current_operation_trange`)  
2. **Property implementation** - Add `na_div_np`, `ap_drift`, `ap_drift_va` properties with lazy loading
3. **Calculation logic** - Implement `_calculate_alpha_proton_derived()` method
4. **Push to server** - Deploy changes for initial validation
5. **Create tests** - Write comprehensive validation tests using `test_alpha_proton_electric_field.py` template
6. **Push to GitHub** - Commit tests to repository
7. **Run tests** - Execute and verify all functionality with realistic data ranges

### ⚡ Phase 2: Electric Field Classes (SECOND)
**Why After Phase 1:** More complex, requires new data type definitions, easier to bolt in after core variables work

**Steps:**
1. **Update `data_types.py`** - Add `dfb_ac_spec` and `dfb_dc_spec` entries (see details below)
2. **Create `plotbot/data_classes/psp_dfb_classes.py`** - New class file following wind patterns
3. **Implement `psp_dfb_class`** - Single class with ac_spec_dv12/dv34 and dc_spec_dv12 variables
4. **Add calculate_variables()** - Extract spectral data using e10_iaw.ipynb math patterns
5. **Add PySpedas integration** - Following existing PSP data class patterns
6. **Test download → processing → plotting pipeline**

#### Required `data_types.py` Updates

**Add these new entries to `data_types.py`:**
```python
'dfb_ac_spec': {
    'mission': 'psp',
    'data_sources': ['berkeley', 'spdf'],
    'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/dfb_ac_spec/',
    'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'dfb_ac_spec'),
    'password_type': 'mag',  # FIELDS instrument uses mag password type
    'file_pattern': r'psp_fld_{data_level}_dfb_ac_spec_{date_str}_v(\d{{2}})\.cdf',
    'file_pattern_import': r'psp_fld_{data_level}_dfb_ac_spec_{date_str}_v*.cdf',
    'data_level': 'l2',
    'file_time_format': 'daily',
    'data_vars': [
        'psp_fld_l2_dfb_ac_spec_dV12hg',               # AC spectrum dv12 data
        'psp_fld_l2_dfb_ac_spec_dV12hg_frequency_bins', # AC spectrum dv12 frequencies
        'psp_fld_l2_dfb_ac_spec_dV34hg',               # AC spectrum dv34 data  
        'psp_fld_l2_dfb_ac_spec_dV34hg_frequency_bins'  # AC spectrum dv34 frequencies
    ],
},
'dfb_dc_spec': {
    'mission': 'psp',
    'data_sources': ['berkeley', 'spdf'],
    'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/dfb_dc_spec/',
    'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'dfb_dc_spec'),
    'password_type': 'mag',  # FIELDS instrument uses mag password type
    'file_pattern': r'psp_fld_{data_level}_dfb_dc_spec_{date_str}_v(\d{{2}})\.cdf',
    'file_pattern_import': r'psp_fld_{data_level}_dfb_dc_spec_{date_str}_v*.cdf',
    'data_level': 'l2',
    'file_time_format': 'daily',
    'data_vars': [
        'psp_fld_l2_dfb_dc_spec_dV12hg',               # DC spectrum dv12 data (only available)
        'psp_fld_l2_dfb_dc_spec_dV12hg_frequency_bins'  # DC spectrum dv12 frequencies
        # Note: dv34 not available for DC spectrum (confirmed server limitation)
    ],
},
```

### 📊 Phase 3: Integration & Validation
**Combined Analysis Capabilities:**
- Multi-panel plots combining alpha/proton ratios with electric field spectra
- Correlation analysis between drift speeds and wave activity
- Integration with existing PSP data classes (magnetic field, QTN, etc.)

## Data Sources & Server Information

**Alpha/Proton Data:**
- Already integrated through existing PSP SPAN-i data classes
- Uses established Berkeley/SPDF server pathways

**Electric Field Spectra:**
- **AC Spectrum:** `https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/l2/dfb_ac_spec/`
- **DC Spectrum:** `https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/l2/dfb_dc_spec/`
- **Note:** DC only has dv12 configuration (dv34 not available on server)

## Technical Considerations

### Dependencies Management
- **MUST Follow** `dependencies_best_practices_plan.md` "Sticky Note" System exactly
- **Required Infrastructure Changes:**
  - Alpha data class `__init__`: Add `_current_operation_trange = None`
  - Alpha data class `update()`: Accept and store `original_requested_trange` parameter
  - Verify `data_cubby.py` passes `original_requested_trange` to alpha class
- **Property-Based Lazy Loading:** All derived variables as `@property` with plot_manager instances
- **Dependency Time Range:** Use `self._current_operation_trange` for ALL `get_data()` calls
- **No Fallback Logic:** Remove any fallback to `self.datetime_array` for dependency trange

### Data Cadence Handling
- **Alpha Data:** ~30-second cadence
- **Proton Data:** Variable cadence (regular vs high-resolution)  
- **Electric Field:** High-frequency spectral data
- **Solution:** Robust interpolation utilities with time range validation

### Performance Optimization
- Cache interpolated datasets to avoid repeated computation
- Use Numba optimization for vector calculations where applicable
- Implement progressive loading for large spectral datasets

## Success Criteria

### Phase 1 Success Metrics (Implementation-First Validation)

**Run Tests:** `python -m pytest tests/test_alpha_proton_electric_field.py -v -s` (after implementation)

- [ ] **🏗️ Infrastructure Tests PASS:**
  - [ ] `test_alpha_fits_dependency_infrastructure()` - `_current_operation_trange` properly implemented
  - [ ] `test_na_div_np_property_lazy_loading()` - Property exists with plot_manager structure
  - [ ] `test_ap_drift_property_lazy_loading()` - Property exists with plot_manager structure  
  - [ ] `test_ap_drift_va_property_lazy_loading()` - Property exists with plot_manager structure
- [ ] **🔗 Integration Tests PASS:**
  - [ ] `test_plotbot_alpha_proton_integration()` - Full plotbot integration works
  - [ ] All 3 panels plot successfully in plotbot
  - [ ] Data verification shows realistic scientific values
- [ ] **🛡️ Isolation Tests PASS:**
  - [ ] `test_dependency_time_range_isolation()` - No time range contamination
  - [ ] Different time ranges produce different data (no sticky data)
- [ ] **🔬 Physical Validation (via integration test):**
  - [ ] `na_div_np` median in range [0.001, 0.5] (typically 0.02-0.08)
  - [ ] `ap_drift` median in range [0, 1000] km/s (typically 50-200 km/s)
  - [ ] `ap_drift_va` median in range [0, 10] (typically 0.1-2.0)
- [ ] **📊 Test Output Verification:**
  - [ ] Test logs saved to `tests/test_logs/test_alpha_proton_electric_field.txt`
  - [ ] No pytest failures, all tests either PASS or SKIP (for unimplemented features)
  - [ ] Print outputs show proper dependency management flow

### Phase 2 Success Metrics  
- [ ] AC spectrum class producing spectrograms matching notebook examples
- [ ] DC spectrum class handling single-configuration data correctly
- [ ] Frequency bins and spectral data properly structured
- [ ] Integration with `plotbot()` function for easy access
- [ ] Server download automation working reliably

### Combined Analysis Capabilities
- [ ] Multi-panel plots: alpha/proton variables + electric field spectra
- [ ] Cross-validation with QTN density measurements
- [ ] Performance acceptable for routine scientific analysis
- [ ] Documentation and examples for scientific users

## References

- **CRITICAL DEPENDENCY GUIDE:** `dependencies_best_practices_plan.md` - The "Sticky Note" System
  - **Must implement:** Property-based lazy loading (Pattern 4)
  - **Must implement:** Dependency calculation template (Pattern 3) 
  - **Must implement:** Data class initialization and update patterns (Patterns 1 & 2)
- **Notebook Examples:** `e10_iaw.ipynb` for electric field implementation
  - **Data Access:** "⭐️ THIS is how we access the electric field spectra" cell
  - **Plotting:** "⭐️ THIS is how we plot it, instead of degrees on the y axis we have frequency" cell
- **Exploration Work:** `electric_field_ac_integration.ipynb`, `electric_field_dc_integration.ipynb`
- **Recent FIELDS Example:** `captains_log_2025-06-30.md` QTN implementation patterns
- **Successful Dependency Implementation:** `br_norm` time range issue resolution (documented in dependency guide)

## File Creation/Modification Summary

### 📁 **Files to be Modified/Created:**

**Phase 1 - Alpha/Proton Variables:**
- **MODIFY:** `plotbot/data_classes/psp_alpha_fits_classes.py` 
  - Add `na_div_np`, `ap_drift`, `ap_drift_va` properties 
  - Add `_calculate_alpha_proton_derived()` method
  - Add dependency management infrastructure
- **CREATE:** `tests/test_alpha_proton_electric_field.py` (comprehensive test suite)

**Phase 2 - Electric Field Classes:**
- **MODIFY:** `plotbot/data_classes/data_types.py`
  - Add `dfb_ac_spec` and `dfb_dc_spec` entries
- **CREATE:** `plotbot/data_classes/psp_dfb_classes.py` 
  - New class following wind_3dp/wind_mfi patterns
  - Implement calculate_variables() with e10_iaw.ipynb math
  - Spectral plotting capabilities

## Immediate Next Actions

### 🔧 **Step 1: Implement Alpha/Proton Derived Variables (START HERE)**
```bash
# Target: Add na_div_np, ap_drift, ap_drift_va properties to alpha class
# Focus on: plotbot/data_classes/psp_alpha_fits_classes.py
# Follow: dependencies_best_practices_plan.md "Sticky Note" patterns
```

### 🚀 **Step 2: Push to Server for Initial Validation**
```bash
# After implementing the properties and calculation logic
# Deploy to server to verify basic functionality works
```

### 🧪 **Step 3: Create Comprehensive Tests**
```bash
# Create the test file from the template above
# Copy the full test code from this plan into:
tests/test_alpha_proton_electric_field.py
```

### 📤 **Step 4: Push Tests to GitHub**
```bash
# Commit comprehensive test suite to repository
git add tests/test_alpha_proton_electric_field.py
git commit -m "Add alpha/proton derived variables test suite"
git push
```

### 📋 **Step 5: Run & Validate**
```bash
# The complete implementation-first validation:
cd /path/to/plotbot
python -m pytest tests/test_alpha_proton_electric_field.py -v -s  # Should mostly PASS
# → Review any failures, adjust implementation
# → Re-run tests until all Phase 1 tests PASS
```

---

*Created: 2025-01-XX*  
*Status: Implementation Plan - Ready for Implementation-First Development*  
*Priority: Phase 1 (Alpha/Proton Variables) → Phase 2 (Electric Field Classes)*  
*Next Action: Implement alpha/proton derived variables following dependencies best practices* 