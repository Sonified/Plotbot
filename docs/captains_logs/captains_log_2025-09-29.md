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
