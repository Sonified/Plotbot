# Captain's Log - 2025-10-09

## Session Summary
Critical bug fix: Resolved EPAD data repetition issue where each 12-channel measurement was repeated 12 times element-wise, caused by incorrect handling of 2D datetime meshgrids in time clipping logic.

---

## Critical Bug Fix: EPAD Data Repetition (v3.63)

### Problem Reported:
Colleague reported that when accessing `.epad.strahl.data`, each 12-channel measurement was repeated 12 times element-wise:
- Expected data shape: `(43, 12)` - 43 time steps, 12 pitch angles  
- Actual data shape: `(516, 12)` - where 516 = 43 × 12 (each measurement repeated 12 times)
- **Time shape**: `(43,)` ✅ Correct  
- **plot_manager shape**: `(43, 12)` ✅ Correct
- **`.data` property shape**: `(516, 12)` ❌ Wrong!

### Root Cause Analysis:

**The Bug**: In `plot_manager.py`, the `clip_to_original_trange()` and `_clip_datetime_array()` methods incorrectly handled 2D datetime arrays (meshgrids).

For EPAD strahl data:
- `datetime_array` = `times_mesh` with shape `(43, 12)` - a 2D meshgrid where each row contains the same datetime repeated 12 times
- When calling `pd.to_datetime(datetime_array, utc=True)` on a 2D array, **pandas flattens it to 1D**, giving 516 values
- This created a 1D time_mask with 516 elements (43 unique times × 12 repeats)
- The indexing logic then incorrectly expanded the data to match the flattened mask

**Example of the bug:**
```python
datetime_array.shape  # (43, 12) - meshgrid
datetime_array_pd = pd.to_datetime(datetime_array, utc=True)  # Flattens to 516 elements!
time_mask = (datetime_array_pd >= start) & (datetime_array_pd <= end)  # 516 elements
time_indices = np.where(time_mask)[0]  # 516 indices!
data[time_indices, ...]  # Tries to index (43, 12) array with 516 indices -> chaos!
```

### Solution:

**Fix in `clip_to_original_trange()` and `_clip_datetime_array()`:**

Added 2D datetime array detection and extraction of time axis before creating time mask:

```python
# 🐛 BUG FIX: Handle 2D datetime arrays (meshgrids) correctly
# For 2D datetime arrays (e.g., epad times_mesh), extract just the time axis
if datetime_array.ndim == 2:
    # For meshgrids, times are along axis 0, repeated across axis 1
    # Extract first column to get unique time values
    datetime_array_1d = datetime_array[:, 0]
    print_manager.debug(f"🔍 [DEBUG] Detected 2D datetime_array {datetime_array.shape}, extracting time axis: {datetime_array_1d.shape}")
else:
    datetime_array_1d = datetime_array

datetime_array_pd = pd.to_datetime(datetime_array_1d, utc=True)
# Now time_mask has correct length (43, not 516)
```

**Why this works:**
- For 2D meshgrids, times vary along axis 0 (rows), with each row having identical times repeated
- Extracting first column `[:, 0]` gives us the unique time values `(43,)` 
- Time mask now correctly has 43 elements, matching the data's time axis
- Indexing `data[time_indices, ...]` correctly selects 43 rows, preserving the 12 columns

### Files Modified:
- `plotbot/plot_manager.py`:
  - Updated `clip_to_original_trange()` method (lines 228-236)
  - Updated `_clip_datetime_array()` method (lines 188-195)

### Testing Results:

**Before fix:**
```python
epad.strahl.shape: (43, 12)          # plot_manager correct
epad.strahl.data.shape: (516, 12)    # .data property WRONG
# Each measurement repeated 12 times element-wise
```

**After fix:**
```python
epad.strahl.shape: (43, 12)          # plot_manager correct  
epad.strahl.data.shape: (43, 12)     # .data property CORRECT! ✅
First row != Second row              # No repetition! ✅
```

### Impact:
- Affects all data types using 2D datetime meshgrids (EPAD, DFB spectrograms, HAM, etc.)
- Critical fix for spectral data analysis
- No impact on 1D time series data (mag, proton moments, etc.)

---

## Key Learnings

1. **Pandas flattens multidimensional arrays**: `pd.to_datetime()` on 2D arrays silently flattens to 1D
2. **Meshgrids have redundant time information**: For spectral data, time varies along axis 0, with values repeated across axis 1
3. **Extract time axis explicitly**: Always check array dimensionality and extract the time axis before creating masks
4. **Test with actual data shapes**: Unit tests with 1D arrays wouldn't catch this 2D-specific bug

---

## Next Steps
- Monitor for similar issues in other data classes using 2D datetime arrays
- Consider adding explicit shape validation in plot_manager initialization

---

## End of Session

