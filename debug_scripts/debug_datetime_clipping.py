"""
Debug script to reproduce and fix the datetime_array clipping issue.

Issue: After calling plotbot() with a specific time range, accessing
mag_rtn_4sa.datetime_array returns the full cached data instead of the 
clipped data for the requested time range.
"""

import sys
import os
import numpy as np

# Add plotbot to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotbot
from plotbot import *

def test_datetime_clipping():
    """Test if datetime_array is properly clipped after plotbot call"""
    
    print("\n" + "="*80)
    print("DATETIME ARRAY CLIPPING DEBUG TEST")
    print("="*80)
    
    # Define a simple time range (subset of encounter 4)
    trange = ['2020-01-29/18:00:00', '2020-01-29/20:00:00']
    
    print(f"\n1. Requested time range: {trange[0]} to {trange[1]}")
    
    # Call plotbot to download and plot data
    print("\n2. Calling plotbot to download and plot data...")
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1)
    
    # Now try to access the datetime array like the user does
    print("\n3. Accessing datetime arrays...")
    
    # Check what the user is trying to access (CLASS level)
    class_datetime = np.array(plotbot.mag_rtn_4sa.datetime_array)
    print(f"\n   CLASS level (mag_rtn_4sa.datetime_array):")
    print(f"   - Length: {len(class_datetime)}")
    if len(class_datetime) > 0:
        print(f"   - First timestamp: {class_datetime[0]}")
        print(f"   - Last timestamp: {class_datetime[-1]}")
    
    # Check the VARIABLE level (what actually gets clipped)
    var_datetime = np.array(plotbot.mag_rtn_4sa.br.datetime_array)
    print(f"\n   VARIABLE level (mag_rtn_4sa.br.datetime_array):")
    print(f"   - Length: {len(var_datetime)}")
    if len(var_datetime) > 0:
        print(f"   - First timestamp: {var_datetime[0]}")
        print(f"   - Last timestamp: {var_datetime[-1]}")
    
    # Get the actual data arrays
    class_br = np.array(plotbot.mag_rtn_4sa.br.data)  # This uses .data property which is clipped
    print(f"\n   BR data via .data property (clipped):")
    print(f"   - Length: {len(class_br)}")
    
    # The problem: datetime arrays don't match!
    print("\n4. ANALYSIS:")
    if len(class_datetime) != len(var_datetime):
        print(f"   ❌ PROBLEM CONFIRMED!")
        print(f"   - Class datetime array has {len(class_datetime)} points (FULL CACHE)")
        print(f"   - Variable datetime array has {len(var_datetime)} points (CLIPPED)")
        print(f"   - Data array has {len(class_br)} points (CLIPPED)")
        print(f"\n   The user is accessing mag_rtn_4sa.datetime_array which returns the")
        print(f"   FULL cached data, not the clipped data for the requested time range.")
        print(f"\n   SOLUTION: User should access mag_rtn_4sa.br.datetime_array instead,")
        print(f"   or we need to add a mechanism to store clipped datetime on the class.")
    else:
        print(f"   ✅ Arrays match - no issue detected")
    
    print("\n" + "="*80)
    return class_datetime, var_datetime, class_br


def test_correct_approach():
    """Show the correct way to access clipped datetime arrays"""
    
    print("\n" + "="*80)
    print("CORRECT APPROACH FOR ACCESSING CLIPPED DATA")
    print("="*80)
    
    trange = ['2020-01-29/18:00:00', '2020-01-29/20:00:00']
    
    print(f"\nTime range: {trange[0]} to {trange[1]}")
    print("\nCalling plotbot...")
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1)
    
    print("\n✅ CORRECT WAY:")
    print("   tB = np.array(plotbot.mag_rtn_4sa.br.datetime_array)  # Access via VARIABLE")
    print("   Br = np.array(plotbot.mag_rtn_4sa.br.data)           # Use .data property")
    
    tB_correct = np.array(plotbot.mag_rtn_4sa.br.datetime_array)
    Br_correct = np.array(plotbot.mag_rtn_4sa.br.data)
    
    print(f"\n   Result: {len(tB_correct)} time points, {len(Br_correct)} data points")
    print(f"   Time range: {tB_correct[0]} to {tB_correct[-1]}")
    
    print("\n❌ INCORRECT WAY (what user is doing):")
    print("   tB = np.array(plotbot.mag_rtn_4sa.datetime_array)  # Access via CLASS")
    print("   Br = np.array(plotbot.mag_rtn_4sa.br.data)")
    
    tB_incorrect = np.array(plotbot.mag_rtn_4sa.datetime_array)
    Br_incorrect = np.array(plotbot.mag_rtn_4sa.br.data)
    
    print(f"\n   Result: {len(tB_incorrect)} time points, {len(Br_incorrect)} data points")
    print(f"   ⚠️  MISMATCH! datetime array is full cache, data is clipped")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    # Run the debug test
    class_dt, var_dt, br_data = test_datetime_clipping()
    
    # Show the correct approach
    test_correct_approach()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\nThe issue is that mag_rtn_4sa.datetime_array is at the CLASS level and")
    print("contains all cached data, while mag_rtn_4sa.br.datetime_array is at the")
    print("VARIABLE level and is properly clipped to the requested time range.")
    print("\nTwo possible solutions:")
    print("1. User changes code to access mag_rtn_4sa.br.datetime_array (recommended)")
    print("2. We add a mechanism to store clipped datetime on the class after plotting")
    print("="*80 + "\n")

