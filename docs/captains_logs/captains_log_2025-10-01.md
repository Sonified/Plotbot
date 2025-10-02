# Captain's Log - 2025-10-01

## Session Summary
Working session focused on fixing a critical case sensitivity bug affecting data downloads and datetime handling.

---

## Major Bug Fixes

### Case Sensitivity Bug in data_types Dictionary (v3.52)
**Problem:**
- User's collaborator (Sam) reported "1970-Jan-02" dates appearing in scatter plots
- Investigation revealed MAG data was not downloading/loading
- Root cause: `data_types` dictionary uses mixed-case keys (e.g., `'mag_RTN_4sa'`), but code was performing case-sensitive lookups with lowercase keys (e.g., `'mag_rtn_4sa'`)
- Lookups failed → No config found → No download → Empty arrays → Default epoch dates (1970)

**Solution:**
- Created `get_data_type_config()` helper function in `plotbot/data_classes/data_types.py` for case-insensitive lookups
- Updated all `data_types.get()` calls across the codebase to use `get_data_type_config()`
- Files modified:
  - `plotbot/data_classes/data_types.py` - Added `get_data_type_config()` function and updated `get_local_path()`
  - `plotbot/get_data.py` - Updated all dictionary lookups to use case-insensitive helper
  - `plotbot/data_download_pyspedas.py` - Updated to use `get_data_type_config()`
  - `plotbot/zarr_storage.py` - Updated to use `get_data_type_config()`

**Testing:**
- Created diagnostic notebooks to verify the fix:
  - `debug_scripts/mag_diagnostic_FIXED.ipynb` - Comprehensive diagnostic showing successful data loading
  - Test confirmed: 32,958 MAG data points loaded correctly with proper datetime range (2020-01-29 18:00 to 19:59)
- Verified case-insensitive lookup works for all case variations: `'mag_rtn_4sa'`, `'mag_RTN_4sa'`, `'MAG_RTN_4SA'`

**Impact:**
- Fixes data download failures for all data types with case mismatches
- Resolves "1970-Jan-02" datetime issue reported by collaborator
- Makes system more robust and user-friendly

---

## Learnings

### Jupyter Notebook Cell Caching
- Jupyter notebooks cache imported modules even after restarting the kernel
- When updating Python files that notebooks import, users must restart the kernel to see changes
- Consider adding a note in diagnostic notebooks about kernel restart requirements

### Debugging Strategy
- Started with broad diagnostic (comprehensive_plotbot_diagnostic.ipynb)
- Narrowed to specific subsystem (mag_download_diagnostic.ipynb)
- Created simple test to isolate the issue (test_case_sensitivity.py)
- This layered approach successfully identified the root cause

---

## Code Updates

### Version: v3.52
**Commit Message:** v3.52 Fix: Case sensitivity bug in data_types dictionary lookups - added get_data_type_config() for case-insensitive matching

**Update:** Added mag_diagnostic_FIXED.ipynb with output cells showing successful data loading

**Files Changed:**
- plotbot/__init__.py
- plotbot/data_classes/data_types.py
- plotbot/get_data.py
- plotbot/data_download_pyspedas.py
- plotbot/zarr_storage.py

**New Diagnostic Tools:**
- debug_scripts/mag_diagnostic_FIXED.ipynb
- debug_scripts/comprehensive_plotbot_diagnostic.ipynb
- debug_scripts/mag_download_diagnostic.ipynb

---

## Next Steps
- Share mag_diagnostic_FIXED.ipynb with Sam to verify his setup works
- Sam should be able to run his original code without "1970-Jan-02" errors after pulling this fix
- Consider standardizing all data_types keys to lowercase to prevent future case sensitivity issues

---

## Major Bug Discovery: Trange Boundary Handling (v3.53 in progress)

### Problem Found
After fixing the case sensitivity bug, discovered TWO related issues with time range handling:

1. **Sam's Issue**: MAG downloaded extra day of data
   - trange `['2020-01-28/00:00:00', '2020-01-29/00:00:00']` should download ONLY Jan 28
   - But MAG downloaded Jan 28 AND Jan 29 (791,013 points spanning 2 days)
   - EPAD correctly downloaded only Jan 28 (6,179 points for 1 day)

2. **User's Issue**: Data cubby stuck on first day in loops
   - When looping through multiple days, data cubby returns the SAME data every time
   - Object IDs remain identical across different trange requests
   - Loop changes trange but gets same Jan 28 data repeatedly

### Root Cause (Issue #1 - FIXED)
In `/Users/robertalexander/GitHub/Plotbot/plotbot/data_download_pyspedas.py`:

**Bug in `_get_dates_for_download()` and `_get_dates_in_range()`:**
```python
while current_date <= end_date:  # ❌ Includes end_date even when time is 00:00
    dates.append(current_date.strftime('%Y%m%d'))
    current_date += delta
```

When `trange = ['2020-01-28/00:00:00', '2020-01-29/00:00:00']`:
- Loop sees end_date = 2020-01-29
- Uses `<=` so it downloads BOTH 01-28 AND 01-29
- But 00:00:00 on 01-29 means "start of day" not "include this day"

**Fix:**
Check if end time is midnight (00:00:00) and exclude that day:
```python
is_end_midnight = (end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0)
while current_date < end_date or (current_date == end_date and not is_end_midnight):
    dates.append(current_date.strftime('%Y%m%d'))
    current_date += delta
```

### Root Cause (Issue #2 - IN PROGRESS)
Investigating why data cubby returns cached data when it should load new data for non-overlapping time ranges.

**Files Modified (v3.53):**
- `plotbot/data_download_pyspedas.py` - Fixed `_get_dates_for_download()` and `_get_dates_in_range()`

---

## End of Session

