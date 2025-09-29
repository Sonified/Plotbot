# Shape Mismatch Analysis

## From Debug Output - Tracing the Shape Mismatch

### First Load (2021-04-29/06:00-12:00) - UPDATE PATH
```
✅ UPDATE_EXIT for psp_waves_test - Final state verification:
[CUBBY_GRAB_RETURN_STATE] dt_len: 49428
   datetime_array: 49428 points  ← FILTERED to 6 hour window
   raw_data keys: ['wavePower_LH', 'wavePower_RH']
   wavePower_LH: shape=(197713,)  ← FULL FILE DATA (not filtered!)
   wavePower_RH: shape=(197713,)  ← FULL FILE DATA (not filtered!)
```

**BUG IDENTIFIED**: 
- `datetime_array` = 49,428 points (correctly filtered to requested time range)
- `raw_data['wavePower_LH']` = 197,713 points (ENTIRE file, not filtered!)

### Second Load (2023-06-22/06:00-12:00) - MERGE PATH
```
[CUBBY] Processing new imported data into temporary instance...
   New data datetime_array: 49428 points (filtered)
   New data raw_data: 197712 points (FULL FILE - not filtered!)

🔥 ULTIMATE MERGE ENGINE:
   Existing: 49,428 records (datetime_array length)
   New: 49,428 records (datetime_array length)
   Final records: 98,856 (no overlap, simple concat)

SUCCESS - Why?
- No time overlap between 2021 and 2023 files
- Simple concatenation path (line 251-268)
- Just concatenates arrays: existing_arr + new_arr
- Doesn't use indices, so shape mismatch doesn't matter YET
```

### Third Load (2021-04-29/14:00-18:00) - MERGE PATH with OVERLAP
```
Attempting to merge:
- Existing datetime_array: 98,856 points (from first two loads)
- Existing raw_data['wavePower_LH']: 395,425 points (197713 + 197712 - unfiltered!)
- New datetime_array: ~33,000 points (4 hour window, filtered)
- New raw_data['wavePower_LH']: 197,713 points (FULL FILE - not filtered!)

Merge calculation:
1. final_times = merge of datetime arrays → ~131,000 unique points
2. existing_indices = searchsorted(final_times, existing_times)
   → Returns 98,856 indices (based on datetime_array length)
3. existing_arr = raw_data['wavePower_LH'] 
   → Has 395,425 points (accumulated unfiltered data)

Line 324: final_array[existing_indices] = existing_arr
   ❌ CRASH: Trying to assign 395,425 values to 98,856 index positions
```

## ROOT CAUSE

**The CDF import is NOT time-filtering the raw_data arrays!**

Looking at the import debug output:
```python
Loading wavePower_LH as metadata variable (no time filtering)
Loading wavePower_RH as metadata variable (no time filtering)
```

The comment literally says "no time filtering"! This is the bug.

## Why It Works Sometimes

1. **First load**: No merge needed, so shape mismatch doesn't surface
2. **Second load (no overlap)**: Uses simple concatenation path, doesn't use indices
3. **Third load (with overlap)**: Uses index-based merge → CRASHES because:
   - Indices calculated from filtered datetime_array
   - Data arrays contain unfiltered full-file data
   - Shape mismatch!

## The Fix

The CDF import code needs to:
1. Load the full time array from the file
2. Filter it to the requested time range
3. **Apply the SAME time filter to ALL data variables**
4. Store only the time-filtered data in raw_data

Current behavior:
- ✅ Filters datetime_array correctly
- ❌ Stores full unfiltered data in raw_data

This creates a fundamental inconsistency where:
- `datetime_array.length` ≠ `raw_data['variable'].length`

This violates the core assumption of the merge system that these should ALWAYS be the same length!
