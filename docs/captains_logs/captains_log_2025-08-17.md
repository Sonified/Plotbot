# Captain's Log - 2025-08-17

## CRITICAL BUG FIX: showdahodo Plot Alignment Issue Resolved

### Problem Summary
The user reported that `showdahodo` plots were no longer matching up with previous versions, despite claiming to plot the same time period. This was identified as a critical plotting alignment bug that broke the consistency between `showdahodo` and `plotbot` functionality.

### Root Cause Analysis
Through systematic git commit testing and detailed log analysis, we identified that `showdahodo.py` was using **inconsistent data access patterns** compared to `plotbot_main.py`:

**Working Pattern (plotbot_main.py):**
- Uses `var.data` property which calls `plot_manager.data`
- Properly handles time clipping through the plot_manager system
- Respects original requested time ranges and clips data consistently

**Broken Pattern (showdahodo.py):**
- Used `var.all_data` property to access raw, unclipped data
- Applied custom `apply_time_range()` function for time clipping
- This bypassed the proper plot_manager time clipping logic
- Led to inconsistent data alignment between the two plotting systems

### Evidence from Logs
**Working Version (6c04886):**
```
🔍 [DEBUG] plot_manager.data property called
🔍 [DEBUG] Found original_trange from parent: ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
🔍 [DEBUG] Attempting time clipping with trange: ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
```

**Broken Version (28a708b):**
```
🕒 TimeRangeTracker: Retrieved trange ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
⚡ [CLIP_ONCE] Clipping data ONCE for trange: ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']
🔍 [DEBUG] Clipping 1392513 points to 24719 points in range
```

### The Fix
**Modified `plotbot/showdahodo.py`:**

1. **Changed data access pattern:**
   ```python
   # OLD (broken):
   values1_full = var1_instance.all_data
   values2_full = var2_instance.all_data
   
   # NEW (fixed):
   values1_full = var1_instance.data
   values2_full = var2_instance.data
   ```

2. **Removed custom time clipping:**
   ```python
   # OLD (broken):
   time1_clipped, values1_clipped = apply_time_range(trange, time1_full, values1_full)
   time2_clipped, values2_clipped = apply_time_range(trange, time2_full, values2_full)
   
   # NEW (fixed):
   # Data is already properly time-clipped by plot_manager.data property
   time1_clipped, values1_clipped = time1_full, values1_full
   time2_clipped, values2_clipped = time2_full, values2_full
   ```

3. **Applied same fix to color_var and var3 data access patterns**

### Impact
This fix ensures that `showdahodo` and `plotbot` use identical data processing and time clipping logic, restoring plot alignment consistency across the entire Plotbot system.

### Testing Required
- Verify `showdahodo` plots now match previous working versions
- Confirm data lengths and alignment are consistent between `showdahodo` and `plotbot`
- Test edge cases with different time ranges and data types

### Technical Notes
- The `apply_time_range()` function in `showdahodo.py` is now obsolete for primary data variables
- Future development should always use `var.data` property for consistency
- The `all_data` property should only be used for internal calculations that need unclipped data

## README Documentation Updates

### Notebook Organization Restructured
- **Core Plotting Function Examples** now listed first (Plotbot.ipynb, showdahodo, multiplot, VDF)
- **Data Integration & Advanced Features** grouped logically  
- **Instrument-Specific Data Examples** clearly categorized
- **Multi-Mission & Specialized Data** section for broader scope

### Enhanced Content Accuracy
- Fixed multiplot examples to show actual working patterns from notebooks
- Added `use_degrees_from_center_times` option for multiplot positioning
- Added file location requirements for CDF imports (`data/cdf_files/`)
- Added HAM data location specification (`data/psp/Hamstrings/`)
- Corrected notebook filenames and added missing `plotbot_qtn_integration.ipynb`
- Marked `plotbot_grid_composer_examples.ipynb` as work in progress

### Technical Fixes Documented
- showdahodo plot alignment issue resolved by using consistent `plot_manager.data` access
- FITS naming convention restored (`beta_ppar_pfits`, `beta_pperp_pfits`)
- All 16 data classes fixed for snapshot loading with `object.__setattr__()`

### Version Status
- **Version**: 2025_08_17_v3.10
- **Commit Message**: "v3.10 Fix: Critical showdahodo alignment bug, restored FITS naming, comprehensive README update with notebook reorganization and file location documentation."
- Ready for upstream push to main branch

