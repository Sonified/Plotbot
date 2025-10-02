# Captain's Log - 2025-10-02

## Session Summary
Major breakthrough: Implemented robust empty initialization for `plot_manager` to enable custom variables to be defined before data is loaded, eliminating the need for pre-loading workarounds.

---

## Major Feature: Empty plot_manager Initialization (v3.53)

### Problem:
- Custom variables using numpy operations (e.g., `np.arctan2(br, bn)`) would crash if defined before data was loaded
- Users had to pre-load data, create custom variables, then close figures - clunky workflow
- Error: `AttributeError: 'NoneType' object has no attribute 'arctan2'`
- This broke the ideal workflow: define custom variables once outside loops

### Solution:
**Single-line fix in `plot_manager.__new__()`:**
```python
# Handle None input by converting to empty float64 array
if input_array is None:
    input_array = np.array([], dtype=np.float64)
```

**Files modified:**
- `plotbot/plot_manager.py` - Added None-to-empty-array conversion in `__new__()` method (lines 30-33)

### Why This Works:
1. **Empty arrays are numpy-compatible**: `np.arctan2([], [])` returns `[]` (shape `(0,)`)
2. **No contamination**: Empty arrays don't merge with real data - they're completely replaced
3. **Universal fix**: Works for all data classes (mag, epad, proton, etc.) without modifying each one
4. **No special syntax needed**: Users don't need lambdas or callbacks

### Testing:
**Test 1: Empty initialization + numpy operations**
```python
pm = plot_manager(None, plot_config=cfg)
# Result: shape=(0,), dtype=float64
result = np.degrees(np.arctan2(pm, pm)) + 180
# Result: shape=(0,), dtype=float64 ✓
```

**Test 2: Empty → Real data (no merge contamination)**
```python
# Step 1: Create with empty data
phi_B = np.degrees(np.arctan2(empty_br, empty_bn)) + 180  # shape=(0,)

# Step 2: Load real data
plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bn, 2)

# Step 3: Compute with real data
phi_B_real = np.degrees(np.arctan2(real_br, real_bn)) + 180  # shape=(32958,)

# Result: Empty array did NOT contaminate real data ✓
```

### Impact:
**Before:**
```python
# Clunky workaround - pre-load data
plotbot.ploptions.display_figure = False
plotbot.plotbot(init_trange, plotbot.mag_rtn_4sa.bmag, 1)
plt.close('all')  # Close hidden figure

# NOW create custom variable
phi_B = plotbot.custom_variable('phi_B', 
    np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
)

# Loop through dates...
```

**After:**
```python
# Clean workflow - define before data loads!
phi_B = plotbot.custom_variable('phi_B', 
    np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
)

# Loop through dates - phi_B auto-updates with each trange!
for date in dates:
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.bmag, 1, plotbot.epad.strahl, 2, phi_B, 3)
```

### User Experience Improvements:
- ✅ Define custom variables once, outside loops
- ✅ No pre-loading required
- ✅ No lambda syntax needed
- ✅ No plt.close() workarounds
- ✅ Cleaner, more intuitive code
- ✅ Custom variables automatically update for each time range

---

## Learnings

### Initialization Strategy Testing
- Tested multiple initialization approaches:
  - `np.array([], dtype=np.float64)` ✓ (chosen)
  - `np.array([])` ✓ (works but less explicit)
  - `np.array([np.nan])` ✓ (works but adds data point)
  - `np.array(None, dtype=object)` ✗ (fails with numpy ufuncs)
- Empty float64 arrays are the cleanest: no data, no contamination, full numpy compatibility

### Design Principles
- **Fix at the source**: One change in `plot_manager` fixes all data classes
- **Robustness over special syntax**: Users shouldn't need lambdas or callbacks for simple operations
- **Test merge behavior**: Always verify empty initialization doesn't contaminate real data

---

## Version History

### v3.53 - Empty plot_manager Initialization
**Commit:** `v3.53 Feature: Robust empty initialization - plot_manager converts None to empty float64 arrays for numpy compatibility`

**Changes:**
- `plotbot/plot_manager.py`: Added None-handling in `__new__()` to convert None inputs to `np.array([], dtype=np.float64)`

**Git Operations:**
```bash
git add plotbot/plot_manager.py
git add plotbot/__init__.py
git add docs/captains_logs/captains_log_2025-10-02.md
git commit -m "v3.53 Feature: Robust empty initialization - plot_manager converts None to empty float64 arrays for numpy compatibility"
git push
git rev-parse --short HEAD | pbcopy
```

---

## Major Bug Fix: Scatter Plot Attributes Not Preserved (v3.54)

### Problem:
- Custom variables with `plot_type='scatter'` were being plotted as line plots
- Attributes like `plot_type`, `marker_style`, and `y_label` were not preserved when custom variables updated
- Root cause: `styling_attributes` list in `custom_variables.py` was missing critical attributes

### Solution:
Added missing attributes to `styling_attributes` list (line 335-339):
- Added `'plot_type'` - preserves scatter vs time_series designation
- Added `'marker_style'` - attribute used by scatter plot rendering
- Added `'y_label'` - preserves axis labels

**Files modified:**
- `plotbot/data_classes/custom_variables.py` - Updated styling_attributes list
- `plotbot/plotbot_main.py` - Removed temporary debug prints

### Testing:
Verified with `phi_B` custom variable:
```python
phi_B = plotbot.custom_variable('phi_B', 
    np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
)
phi_B.plot_type = 'scatter'
phi_B.marker_style = 'o'
phi_B.marker_size = 3
phi_B.color = 'purple'
```
Result: ✅ Correctly renders as purple scatter plot, attributes preserved across updates

---

## Version History

### v3.54 - Scatter Plot Attribute Preservation Fix
**Commit:** `v3.54 Fix: Preserve plot_type and scatter attributes in custom variable updates`

**Changes:**
- `plotbot/data_classes/custom_variables.py`: Added `plot_type`, `marker_style`, `y_label` to styling_attributes
- `plotbot/plotbot_main.py`: Removed debug prints

---

## End of Session
Session closed: 2025-10-02
Major breakthroughs: Empty initialization (v3.53) + Scatter plot fixes (v3.54)

