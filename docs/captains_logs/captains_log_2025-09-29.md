# Captain's Log - September 29, 2025

## Micromamba Installer PATH Order Bug Fix

### Problem
Micromamba installer failed with "micromamba not found" error despite successful Homebrew installation. The installer would install micromamba correctly but couldn't find it when trying to use it.

### Root Cause
**PATH ordering bug** in `install_scripts/3_setup_env_micromamba.sh`:
```bash
# WRONG ORDER:
export MAMBA_EXE="$(brew --prefix micromamba)/bin/micromamba"  # Line 8 - uses brew
export PATH="$HOME/homebrew/bin:$PATH"                          # Line 12 - adds brew to PATH
```

The script tried to run `brew --prefix micromamba` **before** adding brew to PATH. If the script ran in a fresh shell context where brew wasn't already in PATH, the command would fail silently, setting `$MAMBA_EXE` to an empty or invalid value.

### Why It Was Intermittent
- **Worked for some users**: Those who already had brew in their PATH from previous terminal sessions
- **Failed for others**: Fresh shell contexts without brew in PATH (like the friend's installation)

### Solution
Fixed the ordering - add brew to PATH **before** trying to use it:
```bash
# CORRECT ORDER:
export PATH="$HOME/homebrew/bin:$PATH"                          # Line 7 - adds brew to PATH first
export MAMBA_EXE="$(brew --prefix micromamba)/bin/micromamba"  # Line 11 - uses brew
```

### Files Updated
- `install_scripts/3_setup_env_micromamba.sh` - Fixed PATH ordering

### Status: Fixed
Classic shell scripting bug - trying to use a command before ensuring it's available in PATH.

---

## Git Push v3.49

**Commit Message**: `v3.49 Fix: Micromamba installer PATH ordering bug - add brew to PATH before using it`

**Changes**:
- Fixed PATH ordering bug in `3_setup_env_micromamba.sh`
- Brew is now added to PATH before attempting to use `brew --prefix micromamba`
- Resolves intermittent "micromamba not found" errors during installation

**Version**: v3.49

---

## Critical CDF Class Investigation: Multi-File Loading & Styling Preservation

### Problem Summary
Investigated whether dynamically-generated CDF classes properly load data from multiple files (different dates) and preserve custom styling through merge operations.

### Test Setup
- **Test Files**: Two PSP_Waves CDF files (2021-04-29 and 2023-06-22)
- **Test Script**: `debug_cdf_multi_file.py`
- **Variables**: `wavePower_LH`, `wavePower_RH`
- **Custom Styling**: Blue/red colors set before first load
- **Comparison**: Tested against proven working class (mag_rtn_4sa)

### Key Findings

#### ✅ Multi-File Loading WORKS
1. **Smart file detection**: System correctly identified both CDF files in directory
2. **Time-based filtering**: Properly selected the right file for each time range:
   - `2021-04-29/06:00-12:00` → Loaded `PSP_wavePower_2021-04-29_v1.3.cdf` ✅
   - `2023-06-22/06:00-12:00` → Loaded `PSP_wavePower_2023-06-22_v1.3.cdf` ✅
3. **Metadata extraction**: Both files loaded with correct datetime arrays and variables
4. **File overlap detection**: Smart scan correctly identifies time overlap (24.0h) vs no overlap

#### ❌ Styling Loss in BOTH Paths (Critical Bug)

**CDF Classes (psp_waves_test):**
```
🎨 Set custom styling: LH=blue, RH=red
✅ UPDATE_ENTRY: Saves and restores styling correctly
⚠️  FINAL_STYLE_LOSS detected in wavePower_LH!
⚠️  FINAL_STYLE_LOSS detected in wavePower_RH!
📊 After first load: LH=blue ✅, RH=blue ❌ (should be red!)
```

**Proven Classes (mag_rtn_4sa):**
```
🎨 Set custom styling: br=purple
✅ UPDATE path preserves purple correctly
🔀 MERGE_PATH_ENTRY: Shows purple styling exists
⚠️  STYLE_LOSS detected in br!
📊 After merge: br=forestgreen (default color, not purple!)
```

**Shocking Discovery**: The merge path loses styling for **ALL classes**, not just CDF classes!

#### ❌ Shape Mismatch Error (Critical Bug)
Third load from same file (2021) crashed with:
```python
ValueError: shape mismatch: value array of shape (395425,) could not be broadcast 
to indexing result of shape (98856,)
```

**Location**: `plotbot/data_cubby.py` line 324 in `ultimate_merger.merge_arrays()`
**Cause**: When merging data from a file that was already loaded, index calculation is incorrect

### Root Causes Identified

1. **Styling Preservation Bug**: 
   - `update()` method saves and restores styling correctly ✅
   - But immediately after restoration, styling is lost ❌
   - Likely happens during `set_plot_config()` recreation of plot_managers
   - Affects ALL classes (CDF and manually written)

2. **Merge Path Never Tested with Styling**:
   - Previous tests only checked UPDATE path behavior
   - MERGE path has never preserved custom styling correctly
   - September 26 investigation incorrectly concluded only CDF classes affected

3. **Shape Mismatch in Merge**:
   - Ultimate merger incorrectly calculates array indices
   - Fails when trying to merge overlapping data from same source
   - Critical bug affecting any repeated time range loads

### Files Involved
- **`plotbot/data_cubby.py`**: 
  - Line 324: Shape mismatch in merge operation
  - Styling loss during `set_plot_config()` call
- **`plotbot/data_import_cdf.py`**: CDF-generated class template (victim, not cause)
- **`debug_cdf_multi_file.py`**: Comprehensive test revealing all issues

### Next Steps (Priority Order)
1. **FIX CRITICAL**: Shape mismatch in ultimate_merger (crashes system)
2. **FIX CRITICAL**: Styling preservation in merge path (affects all classes)
3. **FIX HIGH**: Styling preservation in update path for CDF classes
4. **VERIFY**: Test all fixes with both CDF and manually-written classes

### Status: Critical Investigation Complete
**Conclusion**: Multi-file CDF loading works perfectly ✅, but styling preservation is broken system-wide ❌, and merge operation has critical shape mismatch bug ❌

---

## Critical Fix: Shape Mismatch Crash in CDF Import

### The Bug
**File**: `plotbot/data_import.py` line 1129
**Cause**: Backwards logic for determining which variables need time filtering

```python
# WRONG (before):
if len(var_shape) == 0 or (len(var_shape) == 1 and var_shape[0] <= 1000):
    # Treated as metadata - NO time filtering
    
# This was backwards! Dim_Sizes=[] means RECORD-VARYING (time-dependent)
```

**The CDF Attribute Meaning:**
- `Dim_Sizes = []` → **Record-varying** (changes with time) → MUST filter ✅
- `Dim_Sizes = [n]` → **Non-record-varying** (static metadata) → DON'T filter ✅

**Result of Bug:**
- Requested 6 hours → Got 6 hours of datetime_array but 24 hours of data
- `datetime_array.length` (49,428) ≠ `raw_data['variable'].length` (197,713)
- Shape mismatch when merging: trying to assign 395,425 values to 98,856 index positions
- **CRASH!**

### The Fix
```python
# CORRECT (after):
is_metadata = len(var_shape) > 0 and var_shape[0] <= 1000

if is_metadata:
    # Static metadata - load full array (no filtering)
else:
    # Time-dependent - MUST apply time filtering!
```

### Testing
✅ Third load (2021-04-29/14:00-18:00) now completes successfully
✅ No shape mismatch crash
✅ Arrays properly sized and aligned

### Files Modified
- `plotbot/data_import.py` lines 1128-1144

### Status: FIXED ✅

---

## Git Push v3.50

**Commit Message**: `v3.50 Critical Fix: CDF import time filtering bug causing shape mismatch crashes - reversed Dim_Sizes logic`

**Changes**:
- Fixed critical bug in CDF import that was treating time-dependent variables as metadata
- Reversed logic: Dim_Sizes=[] means record-varying (MUST filter), Dim_Sizes=[n] means static metadata (DON'T filter)
- Resolves shape mismatch crashes when loading overlapping time ranges from same CDF file
- Organized debug scripts into new `debug_scripts/` folder
- Moved shape_mismatch_analysis.md to `docs/` folder for documentation

**Version**: v3.50

---

## Styling Preservation Fix: Merge Path

### Problem
User-customized styling (colors, labels) was being lost during merge operations when loading overlapping or new time ranges.

**Example:**
```python
mag_rtn_4sa.br.color = "purple"  # Set custom color
plotbot(trange1, mag_rtn_4sa.br, 1)  # First load - purple ✅
plotbot(trange2, mag_rtn_4sa.br, 1)  # Second load - green (default) ❌
```

### Root Cause Analysis

**Architecture Review:**
- Plotbot's core philosophy: Persistent global class instances
- Users set styling directly on global instances
- Two data loading paths:
  1. **UPDATE PATH**: Instance has no data → calls `instance.update()` ✅
  2. **MERGE PATH**: Instance has data → merges arrays then calls `set_plot_config()` ❌

**The Bug:**
- `set_plot_config()` recreates plot_managers from scratch
- Wiped out all user customizations (colors, labels, etc.)
- Only happened during MERGE path (new/overlapping time ranges)
- Didn't happen during UPDATE path or cache hits

**Why it wasn't obvious:**
- First load: UPDATE path → no problem
- Same time range: Cache hit, skips everything → no problem  
- Different/overlapping range: MERGE path → styling lost!

### The Fix
**Applied "Option 3 - Save/Restore Pattern":**

Implemented the same pattern that classes use in their own `update()` methods: save styling state, recreate plot_managers, restore styling state.

**Why we MUST call set_plot_config():**
- Plot_managers create numpy **views** of data arrays
- When we do: `global_instance.raw_data = merged_raw_data`
- Plot_managers still hold views of the **OLD** arrays!
- We must recreate them to point to the new merged data

**The Solution:**
```python
# STEP 1: Save styling state from current plot_managers
current_state = {}
for subclass_name in merged_raw_data.keys():
    if hasattr(global_instance, subclass_name):
        var = getattr(global_instance, subclass_name)
        if hasattr(var, '_plot_state'):
            current_state[subclass_name] = dict(var._plot_state)

# STEP 2: Recreate plot_managers with merged data
global_instance.set_plot_config()  # Now they point to merged arrays

# STEP 3: Restore styling state to new plot_managers
for subclass_name, state in current_state.items():
    if hasattr(global_instance, subclass_name):
        var = getattr(global_instance, subclass_name)
        var._plot_state.update(state)
        for attr, value in state.items():
            if hasattr(var.plot_config, attr):
                setattr(var.plot_config, attr, value)
```

**This pattern:**
- ✅ Recreates plot_managers with merged data (fixes stale views)
- ✅ Preserves user styling (saves/restores state)
- ✅ Mirrors the class's own `update()` method pattern

### Testing
Created `debug_scripts/test_styling_preservation.py` to verify fix.

**Results:**
```
Before fix:
  After first load: color=purple ✅
  After merge: color=forestgreen ❌ (reverted to default)

After fix:
  After first load: color=purple ✅
  After merge: color=purple ✅ (PRESERVED!)
```

### Files Modified
- `plotbot/data_cubby.py` lines 1139-1192 (save/restore pattern in merge path)
- `plotbot/data_import_cdf.py` lines 978-1067 (updated generator template with style preservation logging)
- `debug_scripts/test_styling_preservation.py` (new test file)

### Generator Improvement
Updated the CDF class generator template to include comprehensive style preservation logging in the `update()` method. All future auto-generated CDF classes will now have:
- Entry/exit logging with operation type
- Before/after state capture visualization
- Save/restore operation tracking
- Final verification with warnings if styling is lost

This debugging infrastructure helped identify the bug and will prevent future regressions.

### Status: FIXED ✅
Styling now persists correctly across merge operations while maintaining full data functionality.

---

## Git Push v3.51

**Commit Message**: `v3.51 Fix: Styling preservation in merge path - save/restore pattern + improved CDF generator template`

**Changes**:
- Fixed styling preservation in data_cubby merge path using save/restore pattern
- Properly recreates plot_managers with merged data (fixes stale array views)
- Preserves user customizations (colors, labels) through state save/restore
- Updated CDF class generator to include comprehensive style preservation logging
- All future auto-generated CDF classes will have built-in debugging hooks

**Version**: v3.51
