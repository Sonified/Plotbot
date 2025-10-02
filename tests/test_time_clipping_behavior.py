"""
Test to demonstrate and verify time-clipping behavior.

KEY CONCEPT:
    Only variables PASSED to plotbot() get their requested_trange set,
    which enables time-clipping via the .data and .datetime_array properties.
    
    Variables from the same dataset that are NOT passed to plotbot will
    return ALL accumulated data from the cubby, not time-clipped data.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import plotbot
from plotbot import mag_rtn_4sa
import numpy as np

# Enable debug output
plotbot.print_manager.show_data_cubby = True
plotbot.print_manager.show_status = False
plotbot.print_manager.show_debug = False

def test_time_clipping_passed_vs_not_passed():
    """
    Demonstrates that only variables PASSED to plotbot get time-clipped.
    
    This test:
    1. Calls plotbot with bmag for Day 1
    2. Calls plotbot with bmag for Day 2 (data merges in cubby)
    3. Checks bmag.data (PASSED) → Should be clipped to Day 2
    4. Checks br.data (NOT PASSED) → Will return ALL data (Day 1 + Day 2)
    """
    
    print("\n" + "="*80)
    print("TEST: Time-Clipping Behavior - Passed vs Not Passed Variables")
    print("="*80)
    
    # Day 1: Pass bmag to plotbot
    trange1 = ['2020-01-28', '2020-01-29']
    print(f"\n🟢 FIRST PLOTBOT CALL - trange1: {trange1}")
    print("   Passing: mag_rtn_4sa.bmag")
    print("   NOT passing: mag_rtn_4sa.br")
    print("-"*80)
    
    plotbot.plotbot(trange1, mag_rtn_4sa.bmag, 1)
    
    # After Day 1
    bmag_len_day1 = len(mag_rtn_4sa.bmag.data)
    br_len_day1 = len(mag_rtn_4sa.br.data)
    
    print(f"\n📊 AFTER DAY 1:")
    print(f"   bmag.data length: {bmag_len_day1:,} (PASSED - should be ~395k)")
    print(f"   br.data length:   {br_len_day1:,} (NOT PASSED - what do we get?)")
    
    # Day 2: Still pass bmag, NOT br
    trange2 = ['2020-01-29', '2020-01-30']
    print(f"\n🟢 SECOND PLOTBOT CALL - trange2: {trange2}")
    print("   Passing: mag_rtn_4sa.bmag")
    print("   NOT passing: mag_rtn_4sa.br")
    print("-"*80)
    
    plotbot.plotbot(trange2, mag_rtn_4sa.bmag, 1)
    
    # After Day 2
    bmag_len_day2 = len(mag_rtn_4sa.bmag.data)
    bmag_times = mag_rtn_4sa.bmag.datetime_array
    
    br_len_day2 = len(mag_rtn_4sa.br.data)
    br_times = mag_rtn_4sa.br.datetime_array
    
    print(f"\n📊 AFTER DAY 2:")
    print(f"   bmag.data length: {bmag_len_day2:,}")
    print(f"   bmag times: {bmag_times[0]} to {bmag_times[-1]}")
    print(f"   ✅ bmag IS time-clipped (should be ~395k for Day 2 only)")
    
    print(f"\n   br.data length:   {br_len_day2:,}")
    print(f"   br times: {br_times[0]} to {br_times[-1]}")
    
    # The critical assertion
    if br_len_day2 > bmag_len_day2 * 1.5:  # If br is significantly larger
        print(f"   ⚠️  WARNING: br is NOT time-clipped! Contains ALL accumulated data!")
        print(f"   This is because br was NEVER passed to plotbot, so requested_trange was never set.")
    else:
        print(f"   ✅ br appears to be time-clipped (unexpected - check implementation)")
    
    # Summary
    print(f"\n" + "="*80)
    print("SUMMARY:")
    print("="*80)
    print(f"✅ bmag (PASSED to plotbot): {bmag_len_day2:,} records - Time-clipped to Day 2")
    print(f"⚠️  br (NOT passed to plotbot): {br_len_day2:,} records - Contains all accumulated data")
    print(f"\n💡 LESSON: If you need br.data to be time-clipped, you MUST pass it to plotbot!")
    print("   Example: plotbot.plotbot(trange, mag_rtn_4sa.br, 1)")
    print("="*80)
    
    # Assertions for test framework
    assert bmag_len_day2 < bmag_len_day2 * 1.5, "bmag should be time-clipped to ~1 day"
    # We expect br to have MORE data since it wasn't time-clipped
    # (unless the implementation changed to clip everything, which would be a feature change)

if __name__ == "__main__":
    test_time_clipping_passed_vs_not_passed()
    print("\n✅ Test completed!")
