# Captain's Log: 2026-01-08

## Version 3.77: Dual-Axis Multiplot Feature + Critical Bug Fix

### Overview
Implemented dual-axis multiplot functionality (plotting two variables in same panel with separate y-axes) and fixed critical pre-existing bug where single-variable multiplot crashed with stale variable references.

---

## Changes Made

### 1. Dual-Axis Multiplot Feature

**Problem:** User's colleague asked about syntax for plotting two variables (like tperp and tpar) in the same multiplot panel with separate y-axes. Feature code existed but was partially broken.

**Solution:** Fixed and completed dual-axis implementation in multiplot.

#### Key Implementation Details:

**Syntax:**
```python
plot_data = [(time, [var1, var2]) for time in times]
plt.options.second_variable_on_right_axis = True
multiplot(plot_data)
```

**Bugs Fixed:**
1. **ham_var reference error** (line 901): Code tried to access `ham_var` in dual-axis path, changed to use `single_var`
2. **Relative time conversion never executed**: Conversion code was indented INSIDE `if using_positional_axis` block at TWO locations:
   - Right axis (lines 868-885)
   - Left axis (lines 991-1008)

   When `using_positional_axis = False`, these blocks were skipped, leaving x_data as nanosecond timestamps instead of converting to hours (-6 to +6). **CRITICAL FIX: Outdented both blocks to execute regardless of positional axis.**

3. **List handling in Loop 2**: Added proper data loading for list variables in Loop 2 (lines 749-773) with variable refresh from data_cubby to avoid stale references.

### 2. Critical Bug Fix: Stale Variable References (Pre-existing on main)

**Problem:** Single-variable multiplot crashed with "index 0 is out of bounds" when plotting multiple panels. This was a **pre-existing bug on main branch**, not introduced by dual-axis work.

**Root Cause:** When Loop 1 merges data across panels, data_cubby calls `set_plot_config()` which creates BRAND NEW variable instances (new br/bt/bn objects). References stored in `plot_list` from Loop 1 point to OLD instances with empty/stale data.

**Solution:** Added variable refresh logic in Loop 2 for single-variable path (lines 1044-1060), matching the approach used for dual-axis lists. Before plotting each panel, grab the refreshed variable from data_cubby to ensure we have the live instance with current data.

**Code Added:**
```python
# CRITICAL FIX: Refresh single variable reference
print(f"DEBUG Loop 2: Panel {i+1} - Loading data for single variable '{var.subclass_name}', trange {trange}")
from .time_utils import TimeRangeTracker
TimeRangeTracker.set_current_trange(trange)
get_data(trange, var)

# Grab refreshed variable from data_cubby
class_instance = data_cubby.grab(var.class_name)
if class_instance:
    refreshed_var = class_instance.get_subclass(var.subclass_name)
    if refreshed_var is not None:
        var = refreshed_var
```

### 3. Architecture Insight: Two-Loop Multiplot Pattern

This work revealed the fundamental multiplot architecture:

**Loop 1 (lines ~358-534):** Data loading and preparation
- For single variables: Loads data, merges across panels via data_cubby
- For lists: Passes through UNCHANGED to Loop 2 (no loading in Loop 1)

**Loop 2 (lines ~627+):** Plotting with time_clip for each panel
- Applies time windowing to pre-loaded data
- NOW: Also refreshes variables from data_cubby to avoid stale references

**Data Cubby Pattern:** Single instance per class that gets overwritten on each get_data call. When merge happens, `set_plot_config` creates NEW variable instances, breaking old references stored in plot_list.

**Solution:** Always refresh variable references in Loop 2 from data_cubby before plotting each panel.

---

## Files Modified

- `plotbot/__init__.py` - Version bump to v3.77
- `plotbot/multiplot.py` - Dual-axis fixes + variable refresh logic
- `tests/test_multiplot_right_axis.py` - Dual-axis test with perihelion examples
- `tests/test_single_variable_multiplot.py` - Single-variable test to verify fix
- `example_notebooks/plotbot_multiplot_examples.ipynb` - Notebook testing updates

---

## Testing

Created two comprehensive test files:

### Test 1: Dual-Axis Multiplot
```bash
python tests/test_multiplot_right_axis.py
```
✅ Plots br (left axis) and bt (right axis) for 4 encounters (E7-E10)
✅ Each panel shows ~197k data points per variable
✅ Relative time conversion works correctly
✅ Perihelion-based time windows (±6 hours)

### Test 2: Single-Variable Multiplot
```bash
python tests/test_single_variable_multiplot.py
```
✅ Plots br for 7 encounters (E12-E18)
✅ Each panel shows ~395k data points
✅ Variable refresh prevents stale reference crash
✅ All panels render correctly

---

## Key Learnings

### Bug Discovery Process
Initially thought dual-axis work broke single-variable multiplot. Extensive debugging revealed:
1. Dual-axis test worked perfectly
2. Single-variable test crashed with same error
3. Switched to main branch → **same crash**
4. Confirmed: pre-existing bug on main, not our fault

### The Stale Reference Problem
When data_cubby merges data and calls `set_plot_config`, it creates NEW instances. This is a **fundamental architectural issue** that affects ANY code path storing variable references across get_data calls. The fix (refresh from data_cubby in Loop 2) works for both single-variable and list cases.

### Indentation Bug Was Critical
The relative time conversion being indented inside the positional axis block meant it literally never executed when `using_positional_axis = False`. Data plotted at nanosecond x-values (1610883600013101568) instead of hours (-6.00 to 6.00), causing invisible plots off-screen. This bug existed in the codebase but was hidden because positional axis mode was more commonly used.

---

## Notes

This update delivers the requested dual-axis feature AND fixes a critical pre-existing multiplot bug. Both features now work correctly:

- **Dual-axis**: Plot two variables with separate y-axes in same panel
- **Single-variable**: Multiple panels with proper data refresh (no more crashes)

The debugging journey was intense but revealed fundamental architectural insights about how multiplot handles variable references across loops.

**v3.77 Feature: Dual-axis multiplot + Bugfix: Fixed stale variable reference bug**

---
