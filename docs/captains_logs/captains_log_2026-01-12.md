# Captain's Log: 2026-01-12

## Version 3.79: br_norm Performance Fix with TimeRangeTracker Caching

### Overview
Fixed critical performance issue where br_norm property triggered redundant calculations on every access, even when already calculated for current time range. Implemented TimeRangeTracker caching pattern matching plot_manager's approach.

---

## Problem

After implementing scatter plot functionality (v3.77), users noticed significant performance regression when plotting br_norm in multiplot:
- **Original baseline**: ~5 minutes for 20 panels × 6 days
- **After scatter work**: 8.5 minutes (70% slower!)
- **Root cause**: br_norm property getter called `_calculate_br_norm()` on EVERY property access

### Why This Happened

The br_norm property is accessed multiple times per panel:
- Loop 1: Variable loading and data_cubby merging (~3 accesses)
- Loop 2: Plotting with time windows (~14 accesses for datetime_array, subclass_name, etc.)
- **Total per panel**: ~17 property accesses × 20 panels = **340 redundant calculations**

Each calculation triggered:
1. `_calculate_br_norm()` → expensive scipy interpolation
2. `get_data(proton.sun_dist_rsun)` → function call overhead
3. get_data() returned early from cache, but overhead still added 2-3 minutes

The scatter work didn't introduce the bug - it revealed a pre-existing architectural issue by making br_norm multiplot more common.

---

## Solution

### Implemented TimeRangeTracker Caching Pattern

Added trange caching to br_norm property getter, matching the elegant pattern already used by plot_manager:

```python
# 🚀 PERFORMANCE FIX: Only calculate br_norm if trange changed or br_norm doesn't exist yet
current_trange = TimeRangeTracker.get_current_trange()
cached_trange = getattr(self, '_br_norm_calculated_for_trange', None)

br_norm_needs_calculation = (
    self.raw_data.get('br_norm') is None or  # br_norm not calculated yet
    current_trange != cached_trange           # trange changed since last calculation
)

if br_norm_needs_calculation:
    success = self._calculate_br_norm()
    if success:
        # Cache the trange this calculation was for
        object.__setattr__(self, '_br_norm_calculated_for_trange', current_trange)
else:
    # Already calculated for current trange, skip recalculation
    success = True
```

### How It Works

1. **First property access**: No cached trange → calculates br_norm → caches trange
2. **Subsequent accesses (same trange)**: Cached trange matches → returns immediately
3. **New panel (different trange)**: Cached trange doesn't match → recalculates

This matches plot_manager's pattern from [plot_manager.py:239-240](plotbot/plot_manager.py#L239-L240):
```python
# Only clip if the trange has actually changed
if getattr(self, '_requested_trange', None) == value:
    return  # No change, don't reclip
```

---

## Files Modified

- `plotbot/data_classes/psp_mag_rtn_4sa.py`:
  - Lines 227-250: Added TimeRangeTracker caching to br_norm property
  - Caches `_br_norm_calculated_for_trange` when calculation succeeds
  - Checks cached trange before calling `_calculate_br_norm()`

- `plotbot/data_classes/psp_mag_rtn.py`:
  - Lines 490-511: Same TimeRangeTracker caching pattern
  - Ensures both mag_rtn classes use consistent approach

- `tests/test_br_norm_performance.py`: New test file verifying the fix

---

## Testing

### Test Results (20 panels × 6 days each)

**Before fix**: 8.5 minutes
**After fix**: 3m 44s ✨

**Performance improvement**: 56% faster than broken version, 25% faster than original 5-minute baseline!

### Breakdown per panel:
- **Loop 1**: 1 calculation when br_norm first accessed → caches trange
- **Loop 1 + Loop 2**: ~16 additional property accesses, all skip recalculation
- **Total**: 1 calculation + 16 cached checks = minimal overhead

The remaining "already calculated" messages from get_data() are just cache lookups, which are very fast.

---

## Key Learnings

### The Calculated Property Pattern

When implementing calculated properties (like br_norm) that depend on external data:
1. **Cache the trange**: Store the time range calculation was performed for
2. **Check before recalculating**: Compare current trange to cached trange
3. **Only recalculate when necessary**: When trange changes or data doesn't exist

This pattern prevents redundant expensive operations while maintaining data freshness.

### TimeRangeTracker Is The Source of Truth

The elegant data_cubby architecture already had TimeRangeTracker for this exact purpose:
- `TimeRangeTracker.set_current_trange(trange)` → stores current context
- `TimeRangeTracker.get_current_trange()` → retrieves current context
- Compare cached trange to current → know if recalculation needed

We just needed to leverage it in br_norm property getter, same as plot_manager does.

### Property Access Overhead Matters at Scale

Even if individual operations return early from cache:
- 340 property accesses × (function entry + cache check + return) = measurable overhead
- At 20-panel scale, milliseconds add up to minutes
- Caching eliminates the overhead entirely after first calculation

---

## Architectural Insight

This fix revealed that **any calculated property** in the codebase should follow this pattern:

**GOOD** (with trange caching):
```python
@property
def calculated_value(self):
    current_trange = TimeRangeTracker.get_current_trange()
    if self._calculated_trange != current_trange:
        self._calculate()  # Expensive operation
        self._calculated_trange = current_trange
    return self._result
```

**BAD** (without trange caching):
```python
@property
def calculated_value(self):
    if self._result is None:
        self._calculate()  # Runs on EVERY access until result exists
    return self._result
```

The br_norm issue was a "BAD" pattern - checking if result exists, not if it's valid for CURRENT time range.

---

**v3.79 Performance: br_norm caching with TimeRangeTracker**

---
