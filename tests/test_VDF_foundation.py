# tests/test_VDF_foundation.py
"""
VDF Foundation Tests - Phase 1, Step 1.1

Tests basic VDF data downloading using pyspedas to validate
that the core VDF functionality works before plotbot integration.

Based on Jaye's PSP_SPAN-I_VDF_Plot_Tutorial_pypedasdownload.ipynb
"""

import pyspedas
import cdflib
import numpy as np
import os
import pytest

# Add test utilities if available
from tests.utils.test_helpers import system_check, phase

def test_vdf_l2_download():
    """Test downloading L2 VDF data using pyspedas.psp.spi()"""
    # Use Jaye's exact example parameters from notebook Cell 5
    trange = ['2020-01-29/00:00', '2020-01-30/00:00']
    
    # Download L2 VDF data (from Jaye's notebook)
    VDfile = pyspedas.psp.spi(
        trange, 
        datatype='spi_sf00_8dx32ex8a', 
        level='l2', 
        notplot=True, 
        time_clip=True, 
        downloadonly=True, 
        get_support_data=True
    )
    
    # Validation based on Jaye's notebook Cell 7
    assert len(VDfile) > 0, "No VDF files downloaded"
    assert VDfile[0].endswith('.cdf'), "Expected CDF file"
    
    # Open and validate CDF structure (Jaye's notebook Cell 7)
    dat = cdflib.CDF(VDfile[0])
    variables = dat._get_varnames()[1]  # Get zVariables
    
    # Expected variables from Jaye's notebook Cell 7 output
    expected_vars = ['Epoch', 'THETA', 'PHI', 'ENERGY', 'EFLUX', 'ROTMAT_SC_INST']
    for var in expected_vars:
        assert var in variables, f"Missing expected variable: {var}"
    
    # Test data shape (from Jaye's notebook Cell 15)
    theta = dat['THETA']
    phi = dat['PHI'] 
    energy = dat['ENERGY']
    eflux = dat['EFLUX']
    
    # Validate reshaping works (Jaye's approach: 8 phi × 32 energy × 8 theta)
    if len(theta.shape) > 1 and theta.shape[1] == 2048:  # 8*32*8 = 2048
        theta_reshaped = theta[0,:].reshape((8,32,8))
        assert theta_reshaped.shape == (8,32,8), f"Expected (8,32,8), got {theta_reshaped.shape}"

def test_vdf_l3_moments_download():
    """Test downloading L3 moment data for magnetic field"""
    # Use Jaye's parameters from notebook Cell 32
    trange = ['2020-01-29/00:00', '2020-01-30/00:00']
    
    # Download L3 moment data for magnetic field (from Jaye's notebook)
    MOMfile = pyspedas.psp.spi(
        trange,
        datatype='spi_sf00_l3_mom',
        level='l3',
        notplot=True,
        time_clip=True,
        downloadonly=True
    )
    
    # Validation based on Jaye's notebook Cell 33
    assert len(MOMfile) > 0, "No L3 moment files downloaded"
    
    dat = cdflib.CDF(MOMfile[0])
    variables = dat._get_varnames()[1]
    
    # Key variable for VDF processing (from Jaye's notebook Cell 35)
    assert 'MAGF_INST' in variables, "Missing MAGF_INST for field-aligned coordinates"
    assert 'Epoch' in variables, "Missing Epoch for time matching"

def test_vdf_basic_processing():
    """Test basic VDF data processing following Jaye's workflow"""
    # Download test data
    trange = ['2020-01-29/18:00', '2020-01-29/19:00']  # Smaller range for speed
    
    VDfile = pyspedas.psp.spi(
        trange, 
        datatype='spi_sf00_8dx32ex8a', 
        level='l2', 
        notplot=True, 
        time_clip=True, 
        downloadonly=True, 
        get_support_data=True
    )
    
    if len(VDfile) == 0:
        pytest.skip("No VDF data available for test range")
    
    # Test basic data loading and processing
    dat = cdflib.CDF(VDfile[0])
    
    # Load key variables (from Jaye's notebook Cell 10-14)
    epoch = dat['Epoch']
    theta = dat['THETA'] 
    phi = dat['PHI']
    energy = dat['ENERGY']
    eflux = dat['EFLUX']
    
    # Basic validation
    assert len(epoch) > 0, "No time data found"
    assert theta.shape == phi.shape == energy.shape == eflux.shape, "Variable shape mismatch"
    
    # Test reshaping (from Jaye's notebook Cell 15)
    if len(theta.shape) > 1 and theta.shape[1] == 2048:
        # Test first timestep
        theta_reshaped = theta[0,:].reshape((8,32,8))
        phi_reshaped = phi[0,:].reshape((8,32,8))
        energy_reshaped = energy[0,:].reshape((8,32,8))
        eflux_reshaped = eflux[0,:].reshape((8,32,8))
        
        # Validate shapes
        expected_shape = (8,32,8)
        assert theta_reshaped.shape == expected_shape, f"Theta shape: expected {expected_shape}, got {theta_reshaped.shape}"
        assert phi_reshaped.shape == expected_shape, f"Phi shape: expected {expected_shape}, got {phi_reshaped.shape}"
        assert energy_reshaped.shape == expected_shape, f"Energy shape: expected {expected_shape}, got {energy_reshaped.shape}"
        assert eflux_reshaped.shape == expected_shape, f"EFLUX shape: expected {expected_shape}, got {eflux_reshaped.shape}"
        
        print(f"✅ VDF basic processing validated")
        print(f"   Data shape: {theta.shape}")
        print(f"   Reshaped to: {theta_reshaped.shape}")
        print(f"   Time points: {len(epoch)}")

def test_vdf_imports_successful():
    """Test that all required packages import successfully"""
    try:
        import pyspedas
        import cdflib
        import numpy as np
        print("✅ All VDF foundation imports successful")
        print(f"   pyspedas version: {pyspedas.__version__ if hasattr(pyspedas, '__version__') else 'unknown'}")
    except ImportError as e:
        pytest.fail(f"Required package import failed: {e}")

if __name__ == "__main__":
    print("🧪 Running VDF Foundation Tests")
    print("=" * 50)
    
    # Run individual tests
    test_vdf_imports_successful()
    test_vdf_l2_download()
    test_vdf_l3_moments_download() 
    test_vdf_basic_processing()
    
    print("✅ All VDF foundation tests passed!")