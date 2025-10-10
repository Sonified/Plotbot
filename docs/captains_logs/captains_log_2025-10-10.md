# Captain's Log - 2025-10-10

## Session Summary
Major architectural simplification: Refactored custom variables to follow the br_norm pattern, where variables handle their own dependencies through recursive get_data() calls. Removed phase complexity from plotbot_main.py.

---

## Custom Variables Architecture Simplification ✅

### Problem Identified
The previous implementation had become overcomplicated with multiple phases:
- Phase 1: Collect all variables (custom sources + regular)
- Phase 2: Load standard data
- Phase 2.5: Evaluate custom variables
- Phase 3: Plot

This was too complex compared to how regular variables work: `plotbot(trange, mag_rtn_4sa.br, 1)` just works!

### Solution: Follow the br_norm Pattern

**Key Insight:** br_norm is a calculated variable that depends on other data (proton.sun_dist_rsun). It handles its own dependencies!

```python
# psp_mag_rtn_4sa.py - br_norm pattern
@property
def br_norm(self):
    if needs_calculation:
        self._calculate_br_norm()
    return self._br_norm_manager

def _calculate_br_norm(self):
    trange = self._current_operation_trange
    
    # FETCH DEPENDENCIES!
    get_data(trange, proton.sun_dist_rsun)  # ← Recursive get_data call
    
    # CALCULATE!
    br_norm = self.raw_data['br'] * (sun_dist_rsun ** 2)
    self.raw_data['br_norm'] = br_norm
```

### Changes Made

**1. custom_variables.py - evaluate() now loads dependencies**

```python
def evaluate(self, name, trange):
    """
    Evaluate a custom variable's lambda/expression.
    Loads dependencies automatically (like br_norm pattern).
    """
    # LOAD DEPENDENCIES! (Like br_norm does)
    source_vars = self.get_source_variables(name)
    if source_vars:
        from ..get_data import get_data
        get_data(trange, *source_vars)  # Recursive call!
    
    # Evaluate lambda
    result = self.callables[name]()
    
    # Set requested_trange for clipping
    if hasattr(result, 'requested_trange'):
        object.__setattr__(result, 'requested_trange', trange)
    
    # Store and make global
    self.variables[name] = result
    self._make_globally_accessible(name, result)
    
    return result
```

**2. get_data.py - Simple delegation to evaluate()**

```python
if data_type == 'custom_data_type':
    custom_var_name = custom_var_names.get('custom_data_type')
    
    # Get container
    container = data_cubby.grab('custom_variables')
    
    # Delegate to container.evaluate() - it handles dependencies itself!
    result = container.evaluate(custom_var_name, trange)
    
    # Mark as calculated
    global_tracker.update_calculated_range(trange, 'custom_data_type', custom_var_name)
    
    continue  # Done!
```

**3. plotbot_main.py - Drastically simplified**

```python
# Collect ALL variables (custom and regular - no difference!)
vars_to_load = []
for request in plot_requests:
    var = class_instance.get_subclass(request['subclass_name'])
    vars_to_load.append(var)

# Load EVERYTHING with ONE call (get_data handles dependencies!)
get_data(trange, *vars_to_load)

# Plot everything
# ... plotting code ...
```

NO MORE PHASES! Custom variables now work exactly like regular variables because get_data() handles their special needs internally.

**4. plot_manager.py - Fixed datetime_array copying in __array_finalize__**

```python
# 🐛 BUG FIX: Also copy datetime_array from source object's DIRECT attribute
# numpy ufuncs create new arrays where plot_config might not have datetime_array yet
if hasattr(obj, 'datetime_array'):
    src_datetime = getattr(obj, 'datetime_array', None)
    if src_datetime is not None:
        self.plot_config.datetime_array = src_datetime.copy() if hasattr(src_datetime, 'copy') else src_datetime
```

This ensures that numpy ufuncs like `np.abs()` preserve time information when creating new arrays.

**5. custom_variables.py - Fixed regex pattern**

Changed pattern from `r'(?:plotbot\.)?(\w+)\.(\w+)'` to `r'(?:pb|plotbot)\.(\w+)\.(\w+)'`

This correctly extracts `mag_rtn_4sa.bn` from `pb.mag_rtn_4sa.bn` instead of incorrectly extracting `pb.mag_rtn_4sa`.

**6. custom_variables.py - Added result clipping**

After lambda evaluation, clip the result to the requested trange:
```python
if hasattr(result, 'datetime_array') and result.datetime_array is not None:
    # Clip result to requested trange
    from ..plotbot_helpers import time_clip
    indices = time_clip(result.datetime_array, trange[0], trange[1])
    
    if len(indices) > 0:
        result.datetime_array = result.datetime_array[indices]
        # Clip data and time arrays...
```

### Test Results

**test_custom_variable_core_concepts.py:** ✅ 8/8 PASSED
- All core concept tests passing
- Lambda evaluation works
- Time range clipping works

**test_simplification.py:** ✅ PASSED (basic test)
- First call: bn=2746 points, abs_bn=2746 points ✅
- Second call: bn=5493 points, abs_bn=5493 points ✅
- Data correctly replaced (not accumulated) ✅

**inconsistent-cells-FIXED.ipynb:** ❌ PARTIAL FAILURE
- First plotbot() call: WORKS ✅
- Second plotbot() call (same trange, redefined phi_B): SHOWS "No Data Available" ❌
- Third plotbot() call (same trange): SHOWS "No Data Available" ❌

### Issue Not Yet Resolved

When calling plotbot() multiple times with the SAME trange but redefined custom variables:
1. First call works perfectly
2. Subsequent calls fail with "No Data Available" on the custom variable plot

**Hypothesis:** Tracker thinks data is already calculated, so evaluate() isn't being called again. Need to investigate:
- Is evaluate() being called on subsequent requests?
- Is global_tracker properly invalidating when variable is redefined?
- Is requested_trange being updated properly?

### Files Modified
- `plotbot/data_classes/custom_variables.py`:
  - Updated `evaluate()` docstring
  - Added dependency loading in lambda path (lines 566-585)
  - Added dependency loading in old-style path (lines 620-626)
  - Fixed regex pattern (line 520)
  - Added result clipping (lines 592-616)
- `plotbot/get_data.py`:
  - Added custom_data_type handler (lines 336-394)
  - Added custom_var_names tracking (line 222, 262-263)
- `plotbot/plotbot_main.py`:
  - Simplified to remove phase complexity (lines 305-366)
  - Single get_data() call for all variables
- `plotbot/plot_manager.py`:
  - Fixed datetime_array copying in `__array_finalize__()` (lines 120-125)

### Architecture Document Created
- `docs/plotbot_architecture_flow.html`: Visual explanation of how data flows through Plotbot, comparing regular variables, br_norm, and custom variables. Shows why the recursive pattern works.

### Known Issue: Multiple plotbot() Calls

The `inconsistent-cells-FIXED.ipynb` notebook works for the FIRST plotbot call but shows "No Data Available" on subsequent calls with different tranges. This suggests a tracking/caching issue that needs investigation.

**Hypothesis:** The global_tracker or variable update mechanism isn't properly handling multiple calls with different time ranges.

---

## Next Steps
- Investigate why subsequent plotbot() calls don't work
- Check if tracker is properly marking custom variables as needing recalculation
- Verify that evaluate() is being called on subsequent requests

---

