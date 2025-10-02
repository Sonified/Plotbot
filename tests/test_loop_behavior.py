"""
Simple test to understand why loop keeps showing same data
"""
import plotbot
from plotbot import mag_rtn_4sa, data_cubby
import numpy as np

print("="*80)
print("TESTING LOOP BEHAVIOR - 3 CONSECUTIVE DAYS")
print("="*80)

# Test 3 consecutive days
days = [
    ['2020-01-28/00:00:00', '2020-01-29/00:00:00'],  # Day 1
    ['2020-01-29/00:00:00', '2020-01-30/00:00:00'],  # Day 2  
    ['2020-01-30/00:00:00', '2020-01-31/00:00:00'],  # Day 3
]

for i, trange in enumerate(days, 1):
    print(f"\n{'='*80}")
    print(f"ITERATION {i}: Requesting {trange}")
    print(f"{'='*80}")
    
    # Call plotbot
    plotbot.plotbot(trange, mag_rtn_4sa.br)
    
    # Check what's actually in the data after the call
    print(f"\n📊 DATA IN CUBBY AFTER CALL:")
    
    # Get the instance
    instance = data_cubby.grab('mag_rtn_4sa')
    
    if instance and hasattr(instance, 'datetime_array') and instance.datetime_array is not None:
        dt_array = instance.datetime_array
        
        if len(dt_array) > 0:
            print(f"  Total points:  {len(dt_array)}")
            print(f"  First time:    {dt_array[0]}")
            print(f"  Last time:     {dt_array[-1]}")
            print(f"  Date range:    {str(dt_array[0])[:10]} to {str(dt_array[-1])[:10]}")
            
            # Check br data too
            if hasattr(instance, 'raw_data') and 'br' in instance.raw_data:
                br_data = instance.raw_data['br']
                print(f"  BR data len:   {len(br_data)}")
                print(f"  BR first val:  {br_data[0] if len(br_data) > 0 else 'N/A'}")
        else:
            print(f"  ❌ datetime_array is empty!")
    else:
        print(f"  ❌ No instance or datetime_array found!")
    
    # Also check what the clipped version has
    print(f"\n📈 CLIPPED DATA (what gets plotted):")
    if hasattr(mag_rtn_4sa.br, '_clipped_datetime_array') and mag_rtn_4sa.br._clipped_datetime_array is not None:
        clipped_dt = mag_rtn_4sa.br._clipped_datetime_array
        if len(clipped_dt) > 0:
            print(f"  Clipped points: {len(clipped_dt)}")
            print(f"  First time:     {clipped_dt[0]}")
            print(f"  Last time:      {clipped_dt[-1]}")
        else:
            print(f"  ❌ Clipped array is empty!")
    else:
        print(f"  No clipped data (using full array)")

print(f"\n{'='*80}")
print("TEST COMPLETE")
print(f"{'='*80}")
print("\n📝 EXPECTED BEHAVIOR:")
print("  Each iteration should show DIFFERENT date ranges")
print("  Iteration 1: Jan 28")
print("  Iteration 2: Jan 29") 
print("  Iteration 3: Jan 30")
print("\n🐛 BUG BEHAVIOR:")
print("  All iterations show the SAME date (probably Jan 28)")

