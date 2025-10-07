"""
Debug script to understand .time vs .datetime_array issue

The problem:
- .time should contain raw epoch time (TT2000 nanoseconds) for HCS calculations
- .datetime_array contains converted Python datetime objects for plotting
- User needs BOTH, but .time is not accessible on variables
"""

import sys
import os
import numpy as np

# Add plotbot to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotbot

def test_time_access():
    """Test where .time is stored and accessible"""
    
    print("\n" + "="*80)
    print("TIME vs DATETIME_ARRAY DEBUG TEST")
    print("="*80)
    
    # Define time range
    trange = ['2020-01-29/18:00:00', '2020-01-29/20:00:00']
    
    print(f"\n1. Requested time range: {trange[0]} to {trange[1]}")
    
    # Download data
    print("\n2. Calling plotbot to download data...")
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.epad.strahl, 2)
    
    print("\n" + "="*80)
    print("3. TESTING EPAD TIME ACCESS")
    print("="*80)
    
    # Test CLASS level access
    print("\n   A. CLASS LEVEL (plotbot.epad):")
    try:
        epad_time = np.array(plotbot.epad.time) if hasattr(plotbot.epad, 'time') else None
        if epad_time is not None and len(epad_time) > 0:
            print(f"   ✅ plotbot.epad.time exists")
            print(f"      Shape: {epad_time.shape}")
            print(f"      Type: {type(epad_time[0]) if len(epad_time) > 0 else 'N/A'}")
            print(f"      First value: {epad_time[0]}")
            print(f"      Last value: {epad_time[-1]}")
        elif epad_time is not None:
            print(f"   ⚠️  plotbot.epad.time exists but is EMPTY!")
            print(f"      Shape: {epad_time.shape}")
        else:
            print(f"   ❌ plotbot.epad.time does NOT exist")
    except Exception as e:
        print(f"   ❌ Error accessing plotbot.epad.time: {e}")
    
    try:
        epad_datetime = np.array(plotbot.epad.datetime_array) if hasattr(plotbot.epad, 'datetime_array') else None
        if epad_datetime is not None and len(epad_datetime) > 0:
            print(f"\n   ✅ plotbot.epad.datetime_array exists")
            print(f"      Shape: {epad_datetime.shape}")
            print(f"      First value: {epad_datetime[0]}")
            print(f"      Last value: {epad_datetime[-1]}")
        elif epad_datetime is not None:
            print(f"\n   ⚠️  plotbot.epad.datetime_array exists but is EMPTY!")
        else:
            print(f"\n   ❌ plotbot.epad.datetime_array does NOT exist")
    except Exception as e:
        print(f"   ❌ Error accessing plotbot.epad.datetime_array: {e}")
    
    # Test VARIABLE level access
    print("\n   B. VARIABLE LEVEL (plotbot.epad.strahl):")
    try:
        strahl_time = np.array(plotbot.epad.strahl.time) if hasattr(plotbot.epad.strahl, 'time') else None
        if strahl_time is not None and len(strahl_time) > 0:
            print(f"   ✅ plotbot.epad.strahl.time exists")
            print(f"      Shape: {strahl_time.shape}")
            print(f"      Type: {type(strahl_time[0]) if len(strahl_time) > 0 else 'N/A'}")
            print(f"      First value: {strahl_time[0]}")
        elif strahl_time is not None:
            print(f"   ⚠️  plotbot.epad.strahl.time exists but is EMPTY!")
        else:
            print(f"   ❌ plotbot.epad.strahl.time does NOT exist")
    except Exception as e:
        print(f"   ❌ Error accessing plotbot.epad.strahl.time: {e}")
    
    try:
        strahl_datetime = np.array(plotbot.epad.strahl.datetime_array)
        print(f"\n   ✅ plotbot.epad.strahl.datetime_array exists")
        print(f"      Shape: {strahl_datetime.shape}")
        print(f"      First value: {strahl_datetime[0] if len(strahl_datetime) > 0 else 'N/A'}")
        if strahl_datetime.ndim > 1:
            print(f"      ⚠️  Multi-dimensional! This is times_mesh for spectral data")
    except Exception as e:
        print(f"   ❌ Error accessing plotbot.epad.strahl.datetime_array: {e}")
    
    print("\n" + "="*80)
    print("4. TESTING MAG_RTN_4SA TIME ACCESS")
    print("="*80)
    
    # Test mag_rtn_4sa
    print("\n   A. CLASS LEVEL (plotbot.mag_rtn_4sa):")
    try:
        mag_time = np.array(plotbot.mag_rtn_4sa.time) if hasattr(plotbot.mag_rtn_4sa, 'time') else None
        if mag_time is not None and len(mag_time) > 0:
            print(f"   ✅ plotbot.mag_rtn_4sa.time exists")
            print(f"      Shape: {mag_time.shape}")
            print(f"      Type: {type(mag_time[0]) if len(mag_time) > 0 else 'N/A'}")
            print(f"      First value: {mag_time[0]}")
            print(f"      Last value: {mag_time[-1]}")
        elif mag_time is not None:
            print(f"   ⚠️  plotbot.mag_rtn_4sa.time exists but is EMPTY!")
        else:
            print(f"   ❌ plotbot.mag_rtn_4sa.time does NOT exist")
    except Exception as e:
        print(f"   ❌ Error accessing plotbot.mag_rtn_4sa.time: {e}")
    
    print("\n   B. VARIABLE LEVEL (plotbot.mag_rtn_4sa.br):")
    try:
        br_time = np.array(plotbot.mag_rtn_4sa.br.time) if hasattr(plotbot.mag_rtn_4sa.br, 'time') else None
        if br_time is not None and len(br_time) > 0:
            print(f"   ✅ plotbot.mag_rtn_4sa.br.time exists")
            print(f"      Shape: {br_time.shape}")
            print(f"      First value: {br_time[0]}")
        elif br_time is not None:
            print(f"   ⚠️  plotbot.mag_rtn_4sa.br.time exists but is EMPTY!")
        else:
            print(f"   ❌ plotbot.mag_rtn_4sa.br.time does NOT exist")
    except Exception as e:
        print(f"   ❌ Error accessing plotbot.mag_rtn_4sa.br.time: {e}")
    
    try:
        br_datetime = np.array(plotbot.mag_rtn_4sa.br.datetime_array)
        print(f"\n   ✅ plotbot.mag_rtn_4sa.br.datetime_array exists")
        print(f"      Shape: {br_datetime.shape}")
        print(f"      First value: {br_datetime[0]}")
        print(f"      Last value: {br_datetime[-1]}")
    except Exception as e:
        print(f"   ❌ Error accessing plotbot.mag_rtn_4sa.br.datetime_array: {e}")
    
    print("\n" + "="*80)
    print("SUMMARY & DIAGNOSIS")
    print("="*80)
    print("\n📋 EXPECTED BEHAVIOR:")
    print("   - .time should contain raw TT2000 epoch time (int64 nanoseconds)")
    print("   - .datetime_array should contain Python datetime objects")
    print("   - BOTH should be accessible at CLASS and VARIABLE levels")
    print("   - BOTH should be properly clipped to the requested time range")
    
    print("\n🔍 ACTUAL BEHAVIOR:")
    print("   - .time exists on CLASS but may be full cache (not clipped)")
    print("   - .time does NOT exist on VARIABLE (plot_manager)")
    print("   - .datetime_array exists on VARIABLE and is clipped")
    
    print("\n💡 ROOT CAUSE:")
    print("   - plot_config only stores 'datetime_array', not 'time'")
    print("   - When setting up variables, raw epoch .time is not passed to plot_manager")
    print("   - Users need .time for HCS calculations and other numerical operations")
    
    print("\n✅ PROPOSED SOLUTION:")
    print("   1. Add 'time' parameter to plot_config (raw epoch time)")
    print("   2. Update all data classes to pass self.time to plot_manager")
    print("   3. Add .time property to plot_manager (like datetime_array)")
    print("   4. Ensure .time gets clipped along with data and datetime_array")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    test_time_access()

