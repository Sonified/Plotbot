#!/usr/bin/env python3
"""
Test script to verify timer instrumentation works for both orbit and mag data
as outlined in the orbit vs mag performance investigation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import plotbot as pb
import numpy as np
import time

def test_orbit_data_timing():
    """Test orbit data loading and plotting with timing instrumentation."""
    print("\n" + "="*80)
    print("🛰️  TESTING ORBIT DATA TIMING (First Run)")
    print("="*80)
    
    # Define test time range
    trange = ['2021-11-01/00:00:00', '2021-11-01/04:00:00']
    
    # First run - expected to need data loading
    print(f"First run with trange: {trange}")
    pb.plotbot(trange, pb.psp_orbit.r_sun, 1)
    
    print("\n" + "="*80)
    print("🛰️  TESTING ORBIT DATA TIMING (Second Run)")
    print("="*80)
    
    # Second run - expected to use cached data
    print(f"Second run with same trange: {trange}")
    pb.plotbot(trange, pb.psp_orbit.r_sun, 1)

def test_mag_data_timing():
    """Test magnetic field data loading and plotting with timing instrumentation."""
    print("\n" + "="*80)
    print("🧲  TESTING MAGNETIC FIELD DATA TIMING (First Run)")
    print("="*80)
    
    # Define test time range
    trange = ['2021-11-01/00:00:00', '2021-11-01/04:00:00']
    
    # First run - expected to need data loading
    print(f"First run with trange: {trange}")
    pb.plotbot(trange, pb.mag_rtn_4sa.br, 1)
    
    print("\n" + "="*80)
    print("🧲  TESTING MAGNETIC FIELD DATA TIMING (Second Run)")
    print("="*80)
    
    # Second run - expected to use cached data
    print(f"Second run with same trange: {trange}")
    pb.plotbot(trange, pb.mag_rtn_4sa.br, 1)

def main():
    """Main test function."""
    print("🔍 Timer Instrumentation Test")
    print("This test runs both orbit and mag data through the timing instrumentation")
    print("to collect performance data as outlined in the investigation document.")
    
    try:
        # Test orbit data timing
        test_orbit_data_timing()
        
        # Wait a moment between tests
        time.sleep(2)
        
        # Test magnetic field data timing
        test_mag_data_timing()
        
        print("\n" + "="*80)
        print("✅ Timer instrumentation test completed successfully!")
        print("Check the output above for timing data in the format:")
        print("⏱️ [TIMER_NAME] function_name: XXX.XXms")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 