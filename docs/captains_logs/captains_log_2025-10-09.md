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

## Custom Variables Refactoring Attempt & Data Accumulation Bug (ONGOING)

### Context
After fixing the variable replacement bug (see below), we discovered a second bug where custom variables accumulate data across multiple `plotbot()` calls with different time ranges instead of replacing it. This led to a major refactoring attempt of how custom variables interact with `get_data()`.

### Current Status: ❌ REFACTORING MAY BE WRONG APPROACH

**Test Results:**
```
First call:  trange1 → bn: 2746 points,  abs_bn_test: 2746 points ✅
Second call: trange2 → bn: 8240 points,  abs_bn_test: 10986 points ❌
                                                       (2746 + 8240 = accumulated!)
```

### What We Did (Possibly Overcomplicated)

**1. Split `ensure_ready()` into two methods:**
```python
# custom_variables.py
def get_source_variables(name):
    """Parse expression, return variables needed. NO DATA LOADING."""
    # Returns list like [mag_rtn_4sa.bn]

def evaluate(name, trange):
    """Evaluate lambda. Assumes data already loaded. NO get_data() call."""
    # Just evaluates: result = self.callables[name]()
```

**2. Changed plotbot_main.py flow:**
```python
# OLD (on GitHub, working for regular vars):
# Phase 1: Handle custom variables (load their sources)
# Phase 2: Handle regular variables (load them)

# NEW (what we implemented, might be wrong):
# Phase 1: Collect ALL variables needed (custom sources + regular)
# Phase 2: Load ALL data ONCE with get_data()
# Phase 2.5: Evaluate custom variables (no loading, just evaluate)
# Phase 3: Plot everything
```

**3. Added datetime_array copying in arithmetic operations:**
```python
# plot_manager.py _perform_operation()
# Copy datetime_array instead of sharing reference
datetime_arr_copy = self.datetime_array.copy() if hasattr(self, 'datetime_array') and self.datetime_array is not None else None
```

### Why This Might Be Wrong

**The hypothesis that led us down this path:**
- "Custom variables calling `get_data()` internally causes data_cubby to merge instead of replace"
- "We need to separate data loading from evaluation"

**But the REAL issue might be simpler:**
- Regular variables work FINE with the original architecture
- `data_cubby` is DESIGNED to merge time series data across calls
- Custom variables should probably just use the SAME flow as regular variables
- We may have broken something by trying to "fix" it

**What we should probably check instead:**
1. How did the original version on GitHub handle this?
2. Why do regular variables REPLACE data correctly but custom variables ACCUMULATE?
3. Is the issue in `data_cubby.update_global_instance()` deciding when to merge vs replace?
4. Are we storing custom variable results somewhere that persists across calls?

### Files Modified (This Refactoring)
- `plotbot/data_classes/custom_variables.py`: 
  - Added `get_source_variables()` method
  - Added `evaluate()` method  
  - Kept `ensure_ready()` for backward compatibility (calls both methods)
- `plotbot/plotbot_main.py`:
  - Changed Phase 1 to collect variables without evaluating
  - Added Phase 2.5 to evaluate custom variables after data load
- `plotbot/plot_manager.py`:
  - Added datetime_array copying in `_perform_operation()` (lines 960, 1080-1084)

### ⚠️ RECOMMENDATION: Consider Reverting & Simplifying

Before going further, we should:
1. **Look at GitHub version** of `plotbot_main.py` to see how it handled custom vs regular variables
2. **Understand why regular variables work** - they must be doing something right
3. **Find the minimal fix** instead of this complex refactoring
4. **Test with simpler architecture** - maybe custom variables just need a small tweak, not a rewrite

**The AI's confession:** My understanding of the data flow is probably shit. We added a lot of complexity when the answer might be much simpler. The original code worked for regular variables - we should learn from that instead of reinventing it.

---

## Variable Replacement Bug Fix (v3.63) ✅ ACTUALLY FIXED

### Problem
When a custom variable used a regular variable (e.g., `abs_bn = lambda: np.abs(plotbot.mag_rtn_4sa.bn)`), subsequent `plotbot()` calls would have the regular variable (`mag_rtn_4sa.bn`) incorrectly replaced by the custom variable (`abs_bn_test`).

**Test case:**
```python
custom_variable('abs_bn_test', lambda: np.abs(plotbot.mag_rtn_4sa.bn))
plotbot(trange1, mag_rtn_4sa.bn, 1)  # Works
plotbot(trange2, mag_rtn_4sa.bn, 1)  # bn is now abs_bn_test! ❌
```

### ROOT CAUSE FOUND AND FIXED! ✅

**The Bug:**
In `plot_manager.py`, `__array_finalize__()` (line 108) was SHARING the `plot_config` object reference between the source and result arrays:
```python
self.plot_config = getattr(obj, 'plot_config', None)  # ← SHARED REFERENCE!
```

When `np.abs(mag_rtn_4sa.bn)` created a new array, both `result` and `mag_rtn_4sa.bn` pointed to the SAME `plot_config` object.

Then when custom variables set metadata:
```python
result.class_name = 'custom_variables'  # Uses property setter
```

The setter modified `result.plot_config.class_name`, which was the SAME object as `mag_rtn_4sa.bn.plot_config`, corrupting both!

**The Fix:**
Modified `__array_finalize__()` to COPY the `plot_config` instead of sharing it:
```python
# 🐛 BUG FIX: COPY plot_config instead of sharing reference!
# Create a COPY of the plot_config
from .plot_config import plot_config
self.plot_config = plot_config(**obj_plot_config.__dict__)
```

**Result:**
✅ `mag_rtn_4sa.bn` no longer gets replaced by custom variables
✅ Each plot_manager has its own independent `plot_config`
✅ Metadata changes are isolated to the specific object

### Files Modified (Bug Fix)
- `plotbot/plot_manager.py`: Updated `__array_finalize__()` method (lines 108-118)

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

## Custom Variables Lambda Implementation & Stale Reference Investigation

### Context:
User reported "inconsistent behavior" bug with custom variables where `phi_B` (magnetic field angle) would:
1. Take values of `br` instead of its defined formula
2. Cause `br` to be overwritten by `phi_B` values when redefined

### Initial Diagnosis:
The core issue was **stale object references** combined with the **order of operations** in plotbot execution:

**The Problem:**
- Custom variables with NumPy functions (e.g., `np.arctan2()`, `np.degrees()`) were being evaluated in Phase 1 (before data loads)
- This caused them to calculate on empty `plot_manager` objects
- When `set_plot_config()` recreates `plot_manager` instances for standard variables (like `br`, `bn`), custom variables still held references to the OLD objects

**Why Standard Classes Don't Have This Issue:**
- Standard classes like `psp_mag_rtn_4sa` also recreate `plot_manager` objects in `set_plot_config()` (line 92)
- Users access them via `plotbot.mag_rtn_4sa.br`, which goes through the class instance
- Custom variables were different: users assign to local variables `phi_B = custom_variable(...)`, creating stale references

### Solution Implemented:
**Lambda-based evaluation** for complex NumPy expressions:

1. **When to use Lambda:**
   - Simple arithmetic (`+`, `-`, `*`, `/`): Regular syntax works
   - NumPy functions (`np.arctan2()`, `np.degrees()`, `np.sqrt()`): **Must use lambda**

2. **How Lambda Works:**
   ```python
   # Lambda ensures evaluation happens AFTER data loads
   phi_B = plotbot.custom_variable(
       'phi_B',
       lambda: np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
   )
   ```

3. **Execution Flow Changes in `plotbot_main.py`:**
   - **Phase 1** (lines 307-314): Create lambda custom variables but DON'T evaluate
   - **Phase 3** (lines 356-378): Load standard data (`br`, `bn`, etc.)
   - **Phase 4** (lines 432-438): NEW - Evaluate lambdas via `container.evaluate_lambdas()`
   - Phase 4 ensures lambdas are evaluated with fresh, populated data

4. **Lambda Evaluation Logic in `custom_variables.py`:**
   - `evaluate_lambdas()` method (lines 111-167):
     - Executes lambda to get result
     - Creates NEW `plot_manager` with calculated data
     - Copies plot attributes from old manager
     - Copies `datetime_array` and `.time` from source
     - Updates both `container.variables[name]` AND `plotbot.{name}` global alias

### Files Modified:
- `plotbot/data_classes/custom_variables.py`:
  - Added `evaluate_lambdas()` method
  - Fixed lambda path to NOT evaluate immediately
  - Added `__getattr__` to CustomVariablesContainer for dot notation access
- `plotbot/plotbot_main.py`:
  - Reordered phases: lambda evaluation moved to Phase 4 (after data load)
  - Added explicit lambda evaluation call
- `plotbot/__init__.py`:
  - Renamed `custom_vars` to `custom_variables` for consistency
- `debug_scripts/inconsistent-cells-FIXED.ipynb`:
  - Updated all cells to use lambda syntax
- `example_notebooks/plotbot_custom_variable_examples.ipynb`:
  - Added new section explaining lambda vs regular syntax
  - Added working examples with `phi_B`

### Remaining Issue - UNRESOLVED:
**Stale Local Variable References:**
- When user assigns `phi_B = custom_variable(...)`, the local variable `phi_B` points to the ORIGINAL empty `plot_manager`
- After lambda evaluation, `plotbot.phi_B` is updated to the NEW `plot_manager` with data
- But the local variable `phi_B` still points to the OLD empty one
- This is why `phi_B.data` fails after plotting, even though the plot worked (it used `plotbot.phi_B`)

**Why This Differs from Standard Classes:**
- `psp_mag_rtn_4sa.set_plot_config()` also creates NEW `plot_manager` objects (line 522-540)
- But users ALWAYS access via `plotbot.mag_rtn_4sa.br` (through the class instance)
- They never assign to local variables like `br = plotbot.mag_rtn_4sa.br`

**Potential Solutions to Consider:**
1. Document that lambda custom variables should ALWAYS be accessed via `plotbot.{name}`, not local variables
2. Return a proxy object that always resolves to the current `plotbot.{name}` version
3. Make `custom_variable()` return `None` and require `plotbot.{name}` access only
4. Find a way to update the local variable reference (not possible in Python without deep frame inspection)

### Testing Status:
- ✅ Lambda evaluation works correctly in `inconsistent-cells-FIXED.ipynb`
- ✅ Plots work when using `plotbot.phi_B` in plot arguments
- ❌ Accessing `.data` on local variable `phi_B` fails (stale reference)
- ✅ Accessing `.data` on `plotbot.phi_B` should work (not fully tested)

### Next Steps for Future AI:
1. Test if `plotbot.phi_B.data` works after lambda evaluation (should work)
2. Document the local variable limitation clearly
3. Consider architectural change to eliminate stale references
4. Update all example notebooks to use `plotbot.{name}` pattern

---

## Custom Variables Lambda: Fix Specific Variable Loading

### Problem:
Lambda-based custom variables were loading entire data classes instead of specific variables, causing shape mismatches in tests.

**Example:**
```python
custom_variable('abs_bn', lambda: np.abs(mag_rtn_4sa.bn))
```

Was loading **ALL** mag_rtn_4sa variables (br, bt, bn, bmag...) instead of just `bn`.

### Root Cause:
In `custom_variables.py` line 516, the regex pattern only captured class names:
```python
pattern = r'(?:plotbot\.)?(\w+)\.\w+'  # Only captures "mag_rtn_4sa" ❌
```

Then passed entire class instances to `get_data()`:
```python
get_data(trange, *classes_to_load)  # Loads ALL variables in class ❌
```

### Solution:
**Follow plotbot's natural pattern** - pass specific variables, not classes!

Changed regex to capture BOTH class AND variable names:
```python
pattern = r'(?:plotbot\.)?(\w+)\.(\w+)'  # Captures ("mag_rtn_4sa", "bn") ✅
```

Then get the specific variable object and pass it to `get_data()`:
```python
var = getattr(class_instance, var_name)  # Gets mag_rtn_4sa.bn
get_data(trange, *vars_to_load)  # Loads ONLY bn ✅
```

**This matches exactly how regular plotbot works:**
- When you call `plotbot(trange, mag_rtn_4sa.bn, 1)`, it passes the specific variable
- Even empty variables have the metadata `get_data()` needs (class_name, subclass_name, data_type)

### Files Modified:
- `plotbot/data_classes/custom_variables.py`: Lines 508-537 in `ensure_ready()` method

### Impact:
- Custom variables with lambdas now load only the exact variables they reference
- Prevents shape mismatches from loading different variable subsets
- More efficient - no unnecessary data loading

---

## Custom Variables Time Range Clipping & Variable Replacement Bug (ONGOING)

### Session Summary:
Fixed lambda variable loading to use specific variables (not classes), but uncovered two additional bugs:
1. ✅ **FIXED**: Custom variables weren't setting `requested_trange` → shape mismatches
2. ❌ **IN PROGRESS**: Variables get replaced by custom variables that use them (e.g., `bn` → `abs_bn`)

### Testing & Discovery:

**Tests Created:**
1. `test_custom_variable_stale_reference_fix.py` - Lambda evaluation ✅ PASSES
2. `test_custom_variable_core_concepts.py` - Fixed typo, now 8/8 pass ✅
3. `test_custom_variable_trange_clipping.py` - Stress test (multiple tranges, variables)
4. `test_bn_replacement_bug.py` - Minimal reproduction of current bug ❌

**Test Results:**
- All custom variable lambda tests pass ✅
- Time range clipping partially works ✅
- **BUG FOUND**: Variable replacement issue ❌

### Bug #1: requested_trange Not Set (FIXED ✅)

**Problem:** Custom variables didn't set `requested_trange`, causing `.data` to return full dataset instead of clipped data.

**Example:**
```python
# After plotbot(trange=['2020-01-29/18:00:00', '2020-01-29/18:10:00'], phi_B, 1)
phi_B.data.shape  # (65917,) ❌ Full dataset!
# Should be: (2746,) clipped to trange
```

**Fix Applied:**
Added `requested_trange` setting in two places in `custom_variables.py`:

1. **Lambda path** (line 560-564):
```python
# 🎯 CRITICAL: Set requested_trange for proper time clipping
if hasattr(result, 'requested_trange'):
    object.__setattr__(result, 'requested_trange', trange)
```

2. **Non-lambda path** (line 427-431):
```python
# 🎯 CRITICAL: Set requested_trange for proper time clipping (non-lambda path)
if hasattr(result, 'requested_trange'):
    object.__setattr__(result, 'requested_trange', trange)
```

3. **In plotbot_main.py** (line 420-424) - Ensure ALL plotted variables get correct trange:
```python
# 🎯 CRITICAL FIX: Ensure ALL variables being plotted have the correct requested_trange
if hasattr(var, 'requested_trange'):
    var.requested_trange = trange
```

**Status:** ✅ Custom variables now clip correctly

### Bug #2: Variable Replacement (CURRENT ISSUE ❌)

**Problem:** When a custom variable uses a regular variable (e.g., `abs_bn` uses `bn`), subsequent `plotbot()` calls have the regular variable **REPLACED** by the custom variable.

**Minimal Reproduction:**
```python
abs_bn = custom_variable('abs_bn_test', lambda: np.abs(mag_rtn_4sa.bn))

# First call - works fine
plotbot(trange1, mag_rtn_4sa.bn, 1, abs_bn, 2)  # ✅ OK

# Second call - bn is REPLACED!
plotbot(trange2, mag_rtn_4sa.bn, 1, abs_bn, 2)  # ❌ bn becomes abs_bn!
```

**Evidence from test output:**
```
First call:
  arg0: mag_rtn_4sa.bn (ID:6061290704) → axis 1  ✅

Second call:
  arg0: custom_variables.abs_bn_test (ID:6061290576) → axis 1  ❌ REPLACED!
```

**Impact:**
```
bn.data shape: (24719,) ← Old data from previous trange
abs_bn.data shape: (8240,) ← Correct for current trange
```

Result: Shape mismatches, incorrect plots

**Hypothesis:**
The `_make_globally_accessible()` function in `custom_variables.py` (line 598-631) might be overwriting `plotbot.bn` with the custom variable.

OR: Python is reusing object IDs when custom variables update, causing reference confusion.

### ROOT CAUSE FOUND AND FIXED! ✅

**The Bug:**
In `plot_manager.py`, `__array_finalize__()` (line 108) was SHARING the `plot_config` object reference between the source and result arrays:
```python
self.plot_config = getattr(obj, 'plot_config', None)  # ← SHARED REFERENCE!
```

When `np.abs(mag_rtn_4sa.bn)` created a new array, both `result` and `mag_rtn_4sa.bn` pointed to the SAME `plot_config` object.

Then when custom variables set metadata:
```python
result.class_name = 'custom_variables'  # Uses property setter
```

The setter modified `result.plot_config.class_name`, which was the SAME object as `mag_rtn_4sa.bn.plot_config`, corrupting both!

**The Fix:**
Modified `__array_finalize__()` to COPY the `plot_config` instead of sharing it:
```python
# Create a COPY of the plot_config
from .plot_config import plot_config
self.plot_config = plot_config(**obj_plot_config.__dict__)
```

**Result:**
✅ `mag_rtn_4sa.bn` no longer gets replaced by custom variables
✅ Each plot_manager has its own independent `plot_config`
✅ Metadata changes are isolated to the specific object

### Files Modified This Session:
- `plotbot/data_classes/custom_variables.py`: 
  - Lines 508-537: Fixed lambda to load specific variables (not classes)
  - Lines 427-431, 560-564: Added `requested_trange` setting
- `plotbot/plotbot_main.py`: 
  - Lines 420-424: Ensure all plotted vars get correct `requested_trange`
  - Lines 89-97: Added debug output for incoming args
  - Lines 406-409: Added debug output for plot_requests
- `tests/test_custom_variable_core_concepts.py`: Fixed typo (`custom_class` → `custom_variables`)
- `tests/test_custom_variable_trange_clipping.py`: Created comprehensive stress test
- `tests/test_bn_replacement_bug.py`: Created minimal bug reproduction

### Status:
**✅ COMPLETED:**
- Lambda variables load only specific variables (not entire classes)
- Custom variables set `requested_trange` for proper time clipping
- Test suite expanded with comprehensive coverage

**❌ BLOCKING ISSUE:**
- Variable replacement bug prevents multiple `plotbot()` calls with same variables
- Must fix before v3.64 release

---

## End of Session

