# Captain's Log: 2026-01-09

## Version 3.78: Fixed .time Property Not Updating

### Overview
Fixed critical bug where `.time` property returned stale data when trange changed, while `.data` and `.datetime_array` updated correctly. This caused size mismatches when users accessed these properties after plotting with different time ranges.

---

## Problem

User reported that after running `plotbot()` with two different time ranges without restarting kernel:
- First trange (2 days): `.time` = 77,493 points ✅
- Second trange (1.5 days): `.time` = 77,493 points ❌ (STALE!)
- Second trange (1.5 days): `.data` = 63,821 points ✅ (correct)

Result: Size mismatch between `.time` and `.data`, breaking user's ballistic mapping code.

**Root Cause:** The `_clipped_time` cache was checked in the `.time` property getter (line 483) but **never populated** in the `requested_trange` setter. It was a leftover cache variable from v3.74 lazy clipping implementation that was incomplete.

---

## Solution

### 1. Created New Helper Method
Added `_clip_datetime_array_with_indices()` that returns both:
- Clipped datetime array
- Indices used for clipping

This allows us to use the **same indices** to clip both `datetime_array` and `time` arrays, ensuring perfect synchronization.

### 2. Updated requested_trange Setter
```python
# BUGFIX: Also clip .time using same indices as datetime_array
if self.plot_config.time is not None and time_indices is not None:
    self._clipped_time = self.plot_config.time[time_indices]
else:
    self._clipped_time = None
```

Also added `self._clipped_time = None` to the setter's clear section (line 235).

### 3. Kept .time Property Unchanged
The `.time` property already had lazy clipping logic and cache check - we just needed to populate the cache properly.

---

## Testing

Created `tests/test_time_property_sync.py` that verifies:
- First trange: All three properties match (77,493 points) ✅
- Second trange: All three properties update correctly (63,821 points) ✅
- Datetime starts at 12:00 as expected ✅

Verified fix in user's actual notebook - all properties now stay in sync.

---

## Technical Details

The `.time` property contains TT2000 epoch timestamps (integer nanoseconds), while `.datetime_array` contains numpy datetime64 objects. Both must be clipped using the **same time indices** to stay synchronized.

The fix ensures that when `requested_trange` is set:
1. Datetime array is clipped and indices are extracted
2. Those same indices clip the time array (TT2000 format)
3. Both cached values are returned by their respective properties
4. Lazy clipping auto-updates if TimeRangeTracker detects trange change

---

## Files Modified

- `plotbot/plot_manager.py`:
  - Line 235: Added `_clipped_time = None` to clear cached time
  - Lines 263-268: Added time clipping using same indices as datetime_array
  - Lines 347-387: New `_clip_datetime_array_with_indices()` method
  - Lines 491-493: Kept cache check in `.time` property (now works!)
- `tests/test_time_property_sync.py`: New test file verifying the fix

---

## Key Learnings

### Incomplete Cache Implementation
The `_clipped_time` cache was added in v3.74 lazy clipping but never implemented. The getter checked for it, but the setter never populated it. This is a reminder to always implement **both** getter and setter logic for cached properties.

### Index Reuse Pattern
When multiple arrays need to be clipped to the same time range, extract the indices once and reuse them. This ensures perfect synchronization and is more efficient than re-computing the mask for each array.

### Format Differences Don't Matter
TT2000 (int64 nanoseconds) and datetime64 arrays can be clipped using the same integer indices. The indices represent positions in the array, not time values.

---

**v3.78 Bugfix: Fixed .time property not updating when trange changes**

---
