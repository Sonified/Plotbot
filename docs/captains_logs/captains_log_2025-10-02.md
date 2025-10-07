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

## Major Feature: data_cubby.clear() Method (v3.55)

### Problem:
- No way to clear all stored data and reset the cubby to a fresh state
- Useful for loops where you want to force fresh downloads each iteration
- Needed for testing/debugging or freeing memory

### Solution:
Implemented `data_cubby.clear()` class method that:
1. **Stores class types** before clearing (to know what to re-initialize)
2. **Clears all storage dictionaries** (`cubby`, `class_registry`, `subclass_registry`)
3. **Re-initializes class instances** with empty data using `class_type(None)`
   - Regular classes: Re-initialized with `None` → automatically converted to `np.array([], dtype=np.float64)` by v3.53 fix
   - Custom variables: Re-creates `CustomVariablesContainer()` fresh
4. **Clears global tracker** (`imported_ranges`, `calculated_ranges`)

**Files modified:**
- `plotbot/data_cubby.py` - Added `clear()` class method with proper re-initialization logic

### Key Implementation Details:
```python
@classmethod
def clear(cls):
    # Store class types to re-initialize
    classes_to_reinit = []
    for key, instance in cls.cubby.items():
        if hasattr(instance, '__class__'):
            classes_to_reinit.append((key, instance.__class__))
    
    # Clear everything
    cls.cubby.clear()
    cls.class_registry.clear()
    cls.subclass_registry.clear()
    
    # Re-initialize with empty data
    for key, class_type in classes_to_reinit:
        if key == 'custom_class':
            new_instance = CustomVariablesContainer()
        else:
            new_instance = class_type(None)  # Uses v3.53 empty array fix!
        cls.stash(new_instance, class_name=key)
    
    # Clear tracker
    global_tracker.imported_ranges.clear()
    global_tracker.calculated_ranges.clear()
```

### Usage:
```python
# In a loop - force fresh downloads each iteration
for date in dates:
    plotbot.data_cubby.clear()
    
    # Re-create custom variables after clear
    phi_B = plotbot.custom_variable('phi_B', 
        np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
    )
    phi_B.plot_type = 'scatter'
    
    plotbot.plotbot(trange, plotbot.mag_rtn_4sa.bmag, 1, phi_B, 2)
```

### Important Note:
When `clear()` is called:
- All data is removed from memory
- Custom variables must be re-created (old references become invalid)
- Fresh downloads will occur for all subsequent `plotbot()` calls
- Use sparingly - defeats the purpose of the data cubby's caching!

### Bug Fixes:
- Fixed typo: `CustomVariableContainer` → `CustomVariablesContainer`
- Added better error handling with warnings and stack traces for failed re-initializations

---

## Version History

### v3.55 - data_cubby.clear() Method
**Commit:** `v3.55 Feature: data_cubby.clear() method to reset all data and re-initialize class instances with empty arrays`

**Changes:**
- `plotbot/data_cubby.py`: Implemented `clear()` class method with proper re-initialization
- Leverages v3.53 empty initialization fix for seamless reset

**Git Operations:**
```bash
git add plotbot/data_cubby.py
git add plotbot/__init__.py
git add docs/captains_logs/captains_log_2025-10-02.md
git commit -m "v3.55 Feature: data_cubby.clear() method to reset all data and re-initialize class instances with empty arrays"
git push
git rev-parse --short HEAD | pbcopy
```

---

---

## Known Issues / Future Work

**Note:** Will migrate Jaye's to-do list to a dedicated document in `docs/` for better tracking of feature requests and improvements.

### Bug: config.data_dir Not Respected on First Use
**Reported by:** Sam (collaborator)

**Issue:**
Data was downloaded to a different directory than the one set in `config.data_dir`. Had to explicitly re-set the path to fix:
```python
plotbot.config.data_dir = '/Users/sfordin/Documents/Science-Projects/01-psp-wind-conjunction/data'
```

**Potential causes to investigate:**
1. Initial `config.data_dir` setting may not be propagating to download functions
2. PySpedas might be using its own default path instead of respecting plotbot's config
3. Timing issue - config set after download logic initializes
4. Path validation/normalization issue

**Files to check:**
- `plotbot/config.py` - How data_dir is initialized and accessed
- `plotbot/data_download_pyspedas.py` - How download path is determined
- `plotbot/get_data.py` - How config.data_dir is passed to download functions

**Workaround for users:**
Explicitly set `plotbot.config.data_dir = 'desired/path'` at the start of notebooks/scripts.

**Priority:** Medium - has workaround but should be fixed for better UX

---

## End of Session
Session closed: 2025-10-02
Major breakthroughs: Empty initialization (v3.53) + Scatter plot fixes (v3.54) + Data cubby clear method (v3.55)

