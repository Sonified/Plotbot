# Captain's Log - October 11, 2025

## Session Summary
Identified and fixed critical "stale clipped data" issue in direct expression custom variables where source `plot_manager` objects retained mismatched `_clipped_data` from previous test cases with different time ranges, causing arithmetic operations to fail with shape mismatches.

---

## Stale Clipped Data Fix - Direct Expression Custom Variables ✅

### Problem Identified
When running the comprehensive custom variable stress test (Edge Cases 7, 8, 9), direct expression custom variables like `bmag * br * bn` were failing with errors:
- `operands could not be broadcast together with shapes (8239,) (4120,)`
- `x and y arrays must be equal in length along interpolation axis`

**Root Cause:**
Direct expressions evaluate **immediately at definition time** (e.g., `custom_variable('three_same', bmag * br * bn)`). At this moment:
1. Source variables (`bmag`, `br`, `bn`) have accumulated raw data from multiple `plotbot()` calls
2. BUT they also have `_clipped_data` from **different previous test cases with different tranges**
3. When `.data` property is accessed during arithmetic, it returns **stale clipped data** with mismatched sizes:
   - `bmag._clipped_data` = 8239 points (from trange `['2020-01-29/18:00:00', '2020-01-29/18:30:00']`)
   - `br._clipped_data` = 4120 points (from trange `['2020-01-29/20:00:00', '2020-01-29/20:15:00']`)
4. Arithmetic operation tries to multiply arrays with different shapes → **BOOM** 💥

### Solution Implemented
Modified `plot_manager._perform_operation()` to **clear stale clipped data** before performing arithmetic operations:

```python
# 🐛 CRITICAL FIX: Clear stale clipped data before performing operations
# When operations happen at definition time (direct expressions), source variables
# may have stale _clipped_data from previous test cases with different tranges.
# Clearing requested_trange ensures .data returns the full accumulated array consistently.
print_manager.custom_debug(f"[MATH] Clearing stale clipped data before operation")
if hasattr(self, '_requested_trange') and self._requested_trange is not None:
    print_manager.custom_debug(f"[MATH]   Clearing self.requested_trange (was: {self._requested_trange})")
    self._requested_trange = None
    self._clipped_data = None
    self._clipped_datetime_array = None
if hasattr(other, '_requested_trange') and other._requested_trange is not None:
    print_manager.custom_debug(f"[MATH]   Clearing other.requested_trange (was: {other._requested_trange})")
    other._requested_trange = None
    other._clipped_data = None
    other._clipped_datetime_array = None
```

**Why This Works:**
1. At definition time, operations now use **full accumulated arrays** consistently (no stale clips)
2. Later, when `custom_variables.update()` is called with the actual trange, it:
   - Sets `requested_trange` correctly on all source variables
   - Performs resampling if needed
   - Applies the operation on properly clipped, aligned data
3. The clearing is **temporary** and doesn't affect normal plotbot operation

### Files Modified
- `plotbot/plot_manager.py`: Added stale clip clearing in `_perform_operation()` (lines ~1126-1140)
- `plotbot/__init__.py`: Updated version to v3.66
- `tests/test_custom_variable_trange_clipping.py`: Disabled debug output for cleaner test runs

### Test Results
**ALL COMPREHENSIVE STRESS TESTS PASSING ✅**
- Edge Case 1-6: ✅ (Rapid switching, cache invalidation, chained vars, redefinition, lambdas, resampling)
- Edge Case 7 (3 same-cadence): ✅ `bmag * br * bn` → 8239 points
- Edge Case 8 (4 mixed-cadence): ✅ `(bmag + br) / (vr + vt)` → 257 points (resampled)
- Edge Case 9 (3 all-different): ✅ `br * anisotropy * centroids` → 129 points (resampled to slowest EPAD)

---

## Architecture Understanding - Data Accumulation vs Time Clipping

### Key Insight
The `plot_manager` design intentionally allows:
1. **Data Accumulation**: Raw arrays grow across multiple `plotbot()` calls (performance optimization)
2. **Time Clipping**: `requested_trange` and `_clipped_data` provide views into the accumulated data

This is **by design** and works perfectly for normal plotbot operations. The issue only appeared when:
- Direct expressions evaluate at definition time
- Source variables have stale clips from previous operations
- Arithmetic tries to operate on mismatched clipped views

The fix ensures arithmetic operations at definition time use consistent data (full arrays), then proper clipping happens during `update()`.

---

## Pushed to GitHub ✅

**Version:** v3.66  
**Commit Message:** "v3.66 Fix: Stale clipped data in direct expression custom variables - clear clipped views before arithmetic operations"  
**Date:** October 11, 2025

### Changes Included
- Fixed stale clipped data issue in `plot_manager._perform_operation()`
- All comprehensive custom variable tests passing
- Removed debug output for cleaner test execution

---

## Next Steps
1. Monitor for any edge cases where clearing clipped data might cause issues
2. Consider if lambda variables need similar protection (currently they don't have this issue due to lazy evaluation)
3. Document the data accumulation vs clipping architecture for future reference

