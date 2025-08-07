# tests/test_VDF_processing.py

"""
VDF Data Processing Core Tests - Phase 2, Step 2.1

Tests core VDF calculations from Jaye's PSP_SPAN-I_VDF_Plot_Tutorial_pypedasdownload.ipynb
notebook Cells 9-20. Implements and validates the core data processing pipeline.

Reference Source: files_from_Jaye/PSP_SPAN-I_VDF_Plot_Tutorial_pypedasdownload.ipynb
- Cell 9: Variable definitions
- Cell 11: Time conversion and slicing  
- Cell 13-15: Data reshaping (8,32,8)
- Cell 17: VDF calculation from eflux
- Cell 19: Velocity coordinate conversion
"""

import numpy as np
import cdflib
import pandas as pd
import bisect
from datetime import datetime, timedelta
import pytest

# Add test utilities if available
from tests.utils.test_helpers import system_check, phase

def test_vdf_data_extraction():
    """Test extracting VDF data from CDF files (Jaye's Cells 9-11)"""
    # Download test data first
    import pyspedas
    trange = ['2020-01-29/00:00', '2020-01-30/00:00']
    VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                              notplot=True, time_clip=True, downloadonly=True, get_support_data=True)
    
    # Extract variables (Jaye's Cell 9)
    dat = cdflib.CDF(VDfile[0])
    epoch_ns = dat['Epoch']
    theta = dat['THETA']
    phi = dat['PHI']
    energy = dat['ENERGY']
    eflux = dat['EFLUX']
    
    # Test time conversion (Jaye's Cell 11)
    epoch_dt64 = cdflib.cdfepoch.to_datetime(dat.varget('Epoch'))
    epoch = pd.to_datetime(epoch_dt64).to_pydatetime().tolist()
    
    # Validate basic properties
    assert len(epoch) > 0, "No time data extracted"
    assert theta.shape[1] == 2048, f"Expected 2048 elements (8*32*8), got {theta.shape[1]}"
    assert phi.shape == theta.shape, "Phi and theta should have same shape"
    assert energy.shape == theta.shape, "Energy and theta should have same shape"
    assert eflux.shape == theta.shape, "Eflux and theta should have same shape"
    
    print(f"✅ VDF data extraction: {len(epoch)} time points, {theta.shape} array shape")

def test_vdf_timeslice_selection():
    """Test finding closest timeslice (Jaye's Cell 11)"""
    # Create mock time array
    base_time = datetime(2020, 1, 29, 18, 0, 0)
    epoch = [base_time + timedelta(seconds=i*7) for i in range(100)]  # 7-sec SPAN-I cadence
    
    # Test Jaye's bisect approach
    target_time = datetime(2020, 1, 29, 18, 10, 2)
    tSliceIndex = bisect.bisect_left(epoch, target_time)
    
    # Validation
    assert 0 <= tSliceIndex < len(epoch), "Time index out of bounds"
    time_diff = abs((epoch[tSliceIndex] - target_time).total_seconds())
    assert time_diff <= 7, f"Selected time too far from target: {time_diff}s"
    
    print(f"✅ Time slice selection: index {tSliceIndex}, time diff {time_diff:.1f}s")

def test_vdf_array_reshaping():
    """Test reshaping arrays to (8,32,8) (Jaye's Cell 15)"""
    # Create mock data with correct dimensions (2048 = 8*32*8)
    mock_data = np.random.rand(100, 2048)  # 100 time steps, 2048 elements each
    
    # Test reshaping for single timeslice (Jaye's approach)
    tSliceIndex = 50
    dataSlice = mock_data[tSliceIndex, :]
    dataReshaped = dataSlice.reshape((8, 32, 8))
    
    # Validation
    assert dataReshaped.shape == (8, 32, 8), f"Expected (8,32,8), got {dataReshaped.shape}"
    assert dataReshaped.size == 2048, "Reshaped array should preserve all elements"
    assert np.allclose(dataReshaped.flatten(), dataSlice), "Reshaping should preserve values"
    
    print(f"✅ Array reshaping: {dataSlice.shape} → {dataReshaped.shape}")

def test_vdf_calculation():
    """Test VDF calculation from energy flux (Jaye's Cell 17)"""
    # Mock data with realistic energy and eflux values
    energy = np.random.uniform(100, 10000, (8, 32, 8))  # eV
    eflux = np.random.uniform(1e4, 1e8, (8, 32, 8))     # Energy flux units
    
    # Jaye's VDF calculation
    mass_p = 0.010438870  # proton mass in eV/c^2 where c = 299792 km/s
    charge_p = 1          # proton charge in eV
    
    numberFlux = eflux / energy
    vdf = numberFlux * (mass_p**2) / ((2E-5) * energy)
    
    # Validation
    assert vdf.shape == energy.shape, "VDF should have same shape as input arrays"
    assert np.all(vdf >= 0), "VDF values should be non-negative"
    assert not np.any(np.isnan(vdf)), "VDF should not contain NaN values"
    assert not np.any(np.isinf(vdf)), "VDF should not contain infinite values"
    
    # Check units are reasonable (typical VDF values)
    vdf_median = np.median(vdf)
    vdf_min = np.min(vdf)
    vdf_max = np.max(vdf)
    
    # For now, just check that values are reasonable and positive
    # TODO: Verify exact VDF range against Jaye's notebook results
    assert vdf_median > 0, f"VDF median should be positive: {vdf_median}"
    assert vdf_median < 1e20, f"VDF median seems too high: {vdf_median}"
    
    print(f"VDF range: [{vdf_min:.2e}, {vdf_max:.2e}], median: {vdf_median:.2e}")
    
    print(f"✅ VDF calculation: median value {vdf_median:.2e}, range [{np.min(vdf):.2e}, {np.max(vdf):.2e}]")

def test_velocity_coordinate_conversion():
    """Test conversion to velocity coordinates (Jaye's Cell 19)"""
    # Mock energy and angle data
    energy = np.random.uniform(100, 10000, (8, 32, 8))
    theta = np.random.uniform(-45, 45, (8, 32, 8))    # degrees
    phi = np.random.uniform(-180, 180, (8, 32, 8))    # degrees
    
    # Jaye's velocity calculation
    mass_p = 0.010438870
    charge_p = 1
    vel = np.sqrt(2 * charge_p * energy / mass_p)
    
    # Jaye's coordinate conversion
    vx = vel * np.cos(np.radians(phi)) * np.cos(np.radians(theta))
    vy = vel * np.sin(np.radians(phi)) * np.cos(np.radians(theta))
    vz = vel * np.sin(np.radians(theta))
    
    # Validation
    assert vx.shape == energy.shape, "vx should match input array shape"
    assert vy.shape == energy.shape, "vy should match input array shape"
    assert vz.shape == energy.shape, "vz should match input array shape"
    
    # Check velocity magnitudes are reasonable (100-5000 km/s for solar wind)
    vel_magnitude = np.sqrt(vx**2 + vy**2 + vz**2)
    assert np.allclose(vel_magnitude, vel), "Velocity magnitude should match original vel"
    
    vel_median = np.median(vel)
    assert 100 < vel_median < 5000, f"Velocity median seems unrealistic: {vel_median} km/s"
    
    print(f"✅ Velocity conversion: median {vel_median:.0f} km/s, range [{np.min(vel):.0f}, {np.max(vel):.0f}] km/s")

def test_complete_processing_pipeline():
    """Test complete VDF processing pipeline end-to-end"""
    # Download real data for complete test
    import pyspedas
    trange = ['2020-01-29/00:00', '2020-01-30/00:00']
    VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                              notplot=True, time_clip=True, downloadonly=True, get_support_data=True)
    
    # Step 1: Extract data (Cell 9)
    dat = cdflib.CDF(VDfile[0])
    epoch_dt64 = cdflib.cdfepoch.to_datetime(dat.varget('Epoch'))
    epoch = pd.to_datetime(epoch_dt64).to_pydatetime().tolist()
    
    # Step 2: Select time slice (Cell 11)
    target_time = datetime(2020, 1, 29, 18, 10, 2)
    tSliceIndex = bisect.bisect_left(epoch, target_time)
    if tSliceIndex >= len(epoch):
        tSliceIndex = len(epoch) - 1
    
    # Step 3: Extract arrays for selected time (Cell 13)
    theta = dat['THETA'][tSliceIndex, :]
    phi = dat['PHI'][tSliceIndex, :]
    energy = dat['ENERGY'][tSliceIndex, :]
    eflux = dat['EFLUX'][tSliceIndex, :]
    
    # Step 4: Reshape to (8,32,8) (Cell 15)
    thetaReshaped = theta.reshape((8, 32, 8))
    phiReshaped = phi.reshape((8, 32, 8))
    energyReshaped = energy.reshape((8, 32, 8))
    efluxReshaped = eflux.reshape((8, 32, 8))
    
    # Step 5: Calculate VDF (Cell 17)
    mass_p = 0.010438870
    charge_p = 1
    numberFlux = efluxReshaped / energyReshaped
    vdf = numberFlux * (mass_p**2) / ((2E-5) * energyReshaped)
    
    # Step 6: Convert to velocity coordinates (Cell 19)
    vel = np.sqrt(2 * charge_p * energyReshaped / mass_p)
    vx = vel * np.cos(np.radians(phiReshaped)) * np.cos(np.radians(thetaReshaped))
    vy = vel * np.sin(np.radians(phiReshaped)) * np.cos(np.radians(thetaReshaped))
    vz = vel * np.sin(np.radians(thetaReshaped))
    
    # Final validation
    assert vdf.shape == (8, 32, 8), "Final VDF should have correct shape"
    assert vx.shape == (8, 32, 8), "Velocity components should have correct shape"
    assert np.all(vdf >= 0), "VDF should be non-negative"
    assert not np.any(np.isnan(vdf)), "VDF should not contain NaN"
    
    vdf_median = np.median(vdf)
    vel_median = np.median(vel)
    
    print(f"✅ Complete pipeline: time {epoch[tSliceIndex]}")
    print(f"   VDF median: {vdf_median:.2e}")
    print(f"   Velocity median: {vel_median:.0f} km/s")
    print(f"   Data shape: {vdf.shape}")
    
    # Return processed data for potential further testing
    return {
        'vdf': vdf,
        'vx': vx, 'vy': vy, 'vz': vz,
        'vel': vel,
        'theta': thetaReshaped,
        'phi': phiReshaped,
        'energy': energyReshaped,
        'epoch': epoch[tSliceIndex]
    }

if __name__ == "__main__":
    # Run key tests for manual verification
    print("🧪 Running VDF Processing Core Tests...")
    test_vdf_timeslice_selection()
    test_vdf_array_reshaping()
    test_vdf_calculation()
    test_velocity_coordinate_conversion()
    test_vdf_data_extraction()
    test_complete_processing_pipeline()
    print("🎉 All VDF processing tests completed!")