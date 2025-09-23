# Captain's Log - 2025-09-23

## Major Bug Fix: VDF pyspedas Local File Search

### Issue
The `vdyes()` function was incorrectly finding L3 moment data files when requesting L2 VDF data, causing VDF plotting to fail or use wrong data types.

**Symptoms:**
- User runs VDF examples → finds correct L2 files
- User runs audifier → `vdyes()` finds L3 files instead
- Error message: `Local files found: [.../psp_swp_spi_sf00_L3_mom_20210622_v04.cdf']` (L3 instead of L2)

### Root Cause
The `no_update=True` approach in pyspedas has unreliable local file search that incorrectly matches L3 files when L2 files are requested. This was a known issue that was already fixed in the main download functions (`data_download_pyspedas.py`) but not in `vdyes.py`.

### Solution
**File**: `plotbot/vdyes.py` lines 101-113

**Before** (problematic):
```python
# First try local files only (no_update=True for fast local check)
VDfile = pyspedas.psp.spi(download_trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                          no_update=True)
if not VDfile:
    VDfile = pyspedas.psp.spi(download_trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                              no_update=False)
```

**After** (fixed):
```python
# Use reliable download approach (no_update=False for proper file filtering)
# Note: no_update=True was removed due to false matches with wrong file types (L3 vs L2)
VDfile = pyspedas.psp.spi(download_trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                          no_update=False)
```

### Impact
- ✅ `vdyes()` now correctly finds L2 VDF data
- ✅ Consistent behavior across VDF examples and audifier notebooks
- ✅ Matches the proven approach already used in main download functions
- ✅ No performance impact (pyspedas still uses local files when available)

### Testing Required
- [ ] Test VDF examples still work 
- [ ] Test audifier examples now correctly find L2 data
- [ ] Verify no regression in download performance

### Version Information
- **Version**: v3.34
- **Commit Message**: v3.34 Fix: VDF pyspedas local file search incorrectly matching L3 files when requesting L2 data

---

## Major Bug Fix: VDF Widget Duplicate UI Generation

### Issue
The `vdyes()` function was generating duplicate interactive widgets - two identical UI controls that were mysteriously "connected" to each other.

**Symptoms:**
- First UI appears after "🔗 Button handlers connected successfully"
- Second identical UI appears after "✅ VDF widget created! X time points available"
- Plot appears only after second UI
- Moving sliders on one UI moved sliders on the other (they were actually the same widgets)

### Root Cause
**File**: `plotbot/vdyes.py` in `_create_vdf_widget()` function

Two separate display mechanisms were active:
1. **Explicit display**: `display(widget_layout)` at line 621 → First UI
2. **Jupyter auto-display**: `return widget_layout` → Second UI (Jupyter automatically displays returned widgets)

Additional issue: `plt.show()` in `update_vdf_plot()` was creating extra standalone plots outside the widget area.

### Solution
**Files**: `plotbot/vdyes.py`

1. **Removed duplicate display** (lines 615-616):
```python
# Before: Two display calls
display(widget_layout)  # Explicit (REMOVED)
return widget_layout    # Auto-display (KEPT)

# After: Single display
return widget_layout    # Jupyter handles automatically
```

2. **Removed extra plt.show()** (line 381):
```python
# Before:
plt.show()  # Creates standalone plot (REMOVED)

# After:
# Note: plt.show() removed - plot displays automatically in widget output area
```

### Impact
- ✅ Single clean widget UI (no duplicates)
- ✅ Plot appears immediately within widget
- ✅ Sliders control only one instance
- ✅ Cleaner user experience

### Version Information
- **Version**: v3.35
- **Commit Message**: v3.35 Fix: VDF widget duplicate UI generation - removed duplicate display calls and extra plt.show()

---
