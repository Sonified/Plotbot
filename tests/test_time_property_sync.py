# tests/test_time_property_sync.py
# Test that .time, .datetime_array, and .data stay in sync across trange changes
# To run: conda run -n plotbot_env python tests/test_time_property_sync.py

"""
Tests the fix for .time property not updating when trange changes.
Previously, .time would return stale data while .data and .datetime_array updated correctly.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import plotbot as pb

print("=" * 60)
print("Testing .time property sync with .data and .datetime_array")
print("=" * 60)

# Test 1: First trange (2 days)
print("\n1. First trange: 2 days (12/23-12/25)")
trange1 = ['12/23/2024-00:00:000', '12/25/2024-00:00:000']
pb.plotbot(trange1, pb.proton.v_sw, 1)

time1 = pb.proton.v_sw.time
data1 = pb.proton.v_sw.data
datetime1 = pb.proton.v_sw.datetime_array

print(f"   .time size: {time1.size}")
print(f"   .data size: {data1.size}")
print(f"   .datetime_array size: {datetime1.size}")
print(f"   datetime range: {datetime1[0]} to {datetime1[-1]}")

assert time1.size == data1.size == datetime1.size, f"❌ FAIL: Sizes don't match after first trange!"
print("   ✅ All sizes match after first trange")

# Test 2: Second trange (1.5 days, SHORTER)
print("\n2. Second trange: 1.5 days (12/23 12:00-12/25)")
trange2 = ['12/23/2024-12:00:000', '12/25/2024-00:00:000']
pb.plotbot(trange2, pb.proton.v_sw, 1)

time2 = pb.proton.v_sw.time
data2 = pb.proton.v_sw.data
datetime2 = pb.proton.v_sw.datetime_array

print(f"   .time size: {time2.size}")
print(f"   .data size: {data2.size}")
print(f"   .datetime_array size: {datetime2.size}")
print(f"   datetime range: {datetime2[0]} to {datetime2[-1]}")

# Check sizes match
if time2.size == data2.size == datetime2.size:
    print("   ✅ All sizes match after second trange")
else:
    print(f"   ❌ FAIL: Sizes don't match!")
    print(f"      Expected all to be {data2.size}")
    print(f"      Got time={time2.size}, data={data2.size}, datetime={datetime2.size}")
    sys.exit(1)

# Check size decreased (shorter time range)
if time2.size < time1.size:
    print(f"   ✅ Size decreased as expected ({time1.size} → {time2.size})")
else:
    print(f"   ❌ FAIL: Size should have decreased!")
    print(f"      First trange: {time1.size} points")
    print(f"      Second trange: {time2.size} points")
    sys.exit(1)

# Check datetime starts at 12:00 not 00:00
if "12:00" in str(datetime2[0]):
    print(f"   ✅ Datetime starts at 12:00 as expected")
else:
    print(f"   ❌ FAIL: Datetime should start at 12:00!")
    print(f"      Got: {datetime2[0]}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ SUCCESS! .time property stays in sync with .data and .datetime_array")
print("=" * 60)
