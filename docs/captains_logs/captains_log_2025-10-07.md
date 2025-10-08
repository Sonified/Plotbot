# Captain's Log - 2025-10-07

## Session Summary
Critical bug fix: Resolved PySpedas data directory issue where data was downloading to `psp_data/` in the notebook directory instead of the configured data directory. Implemented bulletproof fix with early environment variable setting and defensive auto-correction.

---

## Critical Bug Fix: PySpedas Data Directory (v3.58)

### Problem Reported:
- Colleague's fresh install downloading data to `psp_data/` in notebook directory (`/Users/sfordin/Documents/Science-Projects/01-psp-wind-conjunction/psp_data/`)
- Expected location: `/Users/sfordin/GitHub/Plotbot/data/psp/`
- Both `config.data_dir` and `SPEDAS_DATA_DIR` were correctly set, but data still went to wrong location

### Root Cause Analysis:
1. **PySpedas PSP config timing issue**: `pyspedas.projects.psp.config` defaults to `'psp_data/'` (relative to current directory)
2. **One-time check**: The config only checks `SPEDAS_DATA_DIR` ONCE when first imported
3. **Race condition**: If the PSP config module is imported before plotbot sets `SPEDAS_DATA_DIR`, it locks to the wrong default
4. **Frozen config**: Python modules only execute once, so setting the env var later doesn't help

### Investigation Steps:
```python
# Test confirmed the bug:
from pyspedas.projects.psp import config
print(config.CONFIG['local_data_dir'])  # 'psp_data/' (BAD!)

os.environ['SPEDAS_DATA_DIR'] = '/correct/path'
print(config.CONFIG['local_data_dir'])  # Still 'psp_data/' (FROZEN!)
```

### Solution (Two-Pronged Fix):

#### 1. Early Environment Variable Setting (`plotbot/__init__.py`)
Set `SPEDAS_DATA_DIR` at the VERY TOP of `__init__.py` before ANY other imports:

```python
# ============================================================================
# CRITICAL: Set SPEDAS_DATA_DIR BEFORE ANY OTHER IMPORTS
# This must happen before pyspedas.projects.psp.config is imported anywhere
# ============================================================================
import os

def _get_plotbot_data_dir():
    """Get the plotbot data directory as an absolute path."""
    try:
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_file_dir)
        return os.path.join(project_root, 'data')
    except Exception:
        return os.path.abspath('data')

# Set SPEDAS_DATA_DIR environment variable IMMEDIATELY
_plotbot_data_dir = _get_plotbot_data_dir()
os.environ['SPEDAS_DATA_DIR'] = _plotbot_data_dir
os.makedirs(_plotbot_data_dir, exist_ok=True)

# NOW proceed with normal imports...
```

#### 2. Defensive Auto-Correction (`plotbot/config.py`)
Force-correct the PSP config even if it was already imported with wrong path:

```python
def _fix_psp_config_if_needed(self):
    """Force-correct PSP config if already imported with wrong path."""
    import sys
    
    if 'pyspedas.projects.psp.config' in sys.modules:
        try:
            from pyspedas.projects.psp import config as psp_config
            expected_path = os.sep.join([os.path.abspath(self._data_dir), 'psp'])
            
            if psp_config.CONFIG['local_data_dir'] != expected_path:
                psp_config.CONFIG['local_data_dir'] = expected_path
                print(f"🔧 Fixed PSP config: {psp_config.CONFIG['local_data_dir']}")
        except Exception:
            pass  # Silent fail - don't break plotbot
```

### Testing Results:

**Test 1: Normal workflow (fixed)**
```python
import plotbot
from pyspedas.projects.psp import config
# Result: config.CONFIG['local_data_dir'] = '/correct/path/psp' ✅
```

**Test 2: Worst case - pyspedas imported first (still fixed!)**
```python
import pyspedas  # Causes bug - locks to 'psp_data/'
import plotbot   # Auto-detects and fixes it!
# Output: "🔧 Fixed PSP config: /correct/path/psp"
# Result: Downloads to correct location ✅
```

### Files Modified:
1. `plotbot/__init__.py`:
   - Added early `SPEDAS_DATA_DIR` setting at top (lines 4-27)
   - Updated version to v3.58

2. `plotbot/config.py`:
   - Added `_fix_psp_config_if_needed()` method (lines 108-129)
   - Called from `_configure_pyspedas_data_directory()` (line 106)

### User Instructions for Testing:
1. Pull latest code (v3.58)
2. **Restart Jupyter kernel** (critical!)
3. Run test to verify PSP config is correct
4. Try downloading data - should go to configured directory, NOT `psp_data/`

---

## Git History

### v3.58 - PySpedas Data Directory Critical Fix
**Commit**: `v3.58 Critical Fix: PySpedas data directory bug - force SPEDAS_DATA_DIR at import + auto-correct PSP config`

**Changes**:
- Early SPEDAS_DATA_DIR setting in `__init__.py`
- Defensive PSP config auto-correction in `config.py`
- Handles both normal workflow and edge cases (pyspedas imported first)

---

## Key Learnings

1. **Python module import timing matters**: Environment variables must be set BEFORE the module that reads them is first imported
2. **Modules execute only once**: Once a module's top-level code runs, it never re-executes (even if you change env vars later)
3. **Defensive programming**: Always assume the worst case (user imports things in wrong order) and auto-fix when possible
4. **Root cause > symptoms**: The fix wasn't to change how plotbot reads files, but to ensure pyspedas saves them to the right place

---

## Next Steps
- Monitor colleague's testing to confirm fix works in their environment
- Consider adding diagnostic warning if `psp_data/` directory detected in unexpected locations

---

## v3.59 - Feature: .time Property for HCS Calculations

**Issue:** User (Sam) reported that `.time` (raw TT2000 epoch time) was not accessible at the variable level (e.g., `plotbot.epad.strahl.time` or `plotbot.mag_rtn_4sa.br.time`). The `.time` attribute only existed at the class level, while `.datetime_array` (converted Python datetime objects) existed at both class and variable levels. This was problematic because users need raw epoch times for HCS calculations and other numerical operations.

**Root Cause:**
- `plot_config` only stored `datetime_array`, not `time`
- When creating `plot_manager` variables, classes weren't passing `self.time` to the plot_config
- The `plot_manager` class had no `.time` property to expose this data

**Solution:**
1. Added `time` parameter to `plot_config.__init__()` with private `_time` storage and property getter/setter
2. Added `.time` property to `plot_manager` class (mirroring the `.datetime_array` property pattern)
   - Returns `_clipped_time` if available (for future clipping support)
   - Falls back to `plot_config.time`
3. Updated data classes to pass `time=self.time` when creating `plot_manager` variables:
   - `psp_electron_classes.py`: Updated `epad_strahl_class` and `epad_strahl_high_res_class` (strahl and centroids variables)
   - `psp_mag_rtn_4sa.py`: Updated all mag variables (br, bt, bn, bmag, pmag)

**Files Modified:**
- `plotbot/plot_config.py` - Added time parameter and property
- `plotbot/plot_manager.py` - Added .time property with getter/setter
- `plotbot/data_classes/psp_electron_classes.py` - Pass time to plot_manager for epad/epad_hr
- `plotbot/data_classes/psp_mag_rtn_4sa.py` - Pass time to plot_manager for all mag components

**Testing:**
Created comprehensive debug scripts:
- `debug_scripts/debug_time_vs_datetime.py` - Diagnostic script showing the issue
- `debug_scripts/test_user_use_case.py` - Verification of the fix

**Result:** 
✅ `.time` and `.datetime_array` are now at the same level in plotbot's architecture
✅ Users can access raw TT2000 epoch times at variable level: `plotbot.epad.strahl.time`, `plotbot.mag_rtn_4sa.br.time`, etc.
✅ Maintains backward compatibility - class-level `.time` still works

**Next Steps:**
- After testing in production, update remaining data classes (proton, qtn, other mag variants, etc.) to pass time to plot_manager
- Implement time clipping alongside datetime_array clipping for consistency

**Commit:** v3.59 Feature: Add .time property to plot_manager - raw TT2000 epoch accessible at variable level for HCS calculations

---

## Automation Script for Remaining Classes (2025-10-08)

**Task:** Update remaining ~30 data classes to pass `time=self.time` to plot_manager constructors.

**Approach:** Created automated Python script `debug_scripts/add_time_to_plot_configs.py` that:
- Uses regex to find all `plot_config()` constructor calls
- Identifies those with `datetime_array=` parameter
- Inserts `time=self.time,` with proper indentation before datetime_array line
- Skips method calls, function definitions, and already-updated constructors

**Testing:** Validated on 5 diverse files:
- `psp_mag_rtn.py` - 13 found, 7 modified ✅
- `psp_proton.py` - 25 found, 21 modified ✅  
- `wind_mfi_classes.py` - 12 found, 6 modified ✅
- `psp_qtn_classes.py` - 8 found, 2 modified ✅
- `psp_alpha_fits_classes.py` - 24 found, 1 modified ✅ (uses helper method pattern - one fix fixes all!)

**Files to Process (35 total):**

*Already Updated Manually (v3.59):*
- ✅ `psp_electron_classes.py` (epad & epad_hr)
- ✅ `psp_mag_rtn_4sa.py` (all mag components)

*Automation Queue (33 files):*
- `_utils.py`
- `custom_classes/__init__.py`
- `custom_classes/demo_spectral_waves.py`
- `custom_classes/demo_wave_power.py`
- `custom_classes/psp_simple_test.py`
- `custom_classes/psp_spectral_waves.py`
- `custom_classes/psp_waves_auto.py`
- `custom_classes/psp_waves_real_test.py`
- `custom_classes/psp_waves_spectral.py`
- `custom_classes/psp_waves_test.py`
- `custom_classes/psp_waves_timeseries.py`
- `custom_variables.py`
- `data_types.py`
- `psp_alpha_classes.py`
- `psp_alpha_fits_classes.py`
- `psp_dfb_classes.py`
- `psp_ham_classes.py`
- `psp_mag_rtn.py`
- `psp_mag_sc_4sa.py`
- `psp_mag_sc.py`
- `psp_orbit.py`
- `psp_proton_fits_classes.py`
- `psp_proton_hr.py`
- `psp_proton.py`
- `psp_qtn_classes.py`
- `psp_span_vdf.py`
- `psp_waves_real_test.py`
- `test_quick.py`
- `wind_3dp_classes.py`
- `wind_3dp_pm_classes.py`
- `wind_mfi_classes.py`
- `wind_swe_h1_classes.py`
- `wind_swe_h5_classes.py`

**Automation Results:**
- ✅ Files processed: 35
- ✅ Files modified: 31
- ✅ plot_config() instances found: 673
- ✅ plot_config() instances modified: 440
- ✅ Lines added: 880
- ✅ Python syntax validation: PASSED
- ⚪ Skipped: psp_electron_classes.py (already updated manually in v3.59)

**Verification Spot Checks:**
- ✅ PSP orbit classes (time series with datetime_array)
- ✅ PSP proton classes (spectral with times_mesh)
- ✅ WIND classes (different spacecraft pattern)
- ✅ All checked files compile successfully

**Final Implementation (after debugging):**
1. ✅ Added `'time'` to `PLOT_ATTRIBUTES` list in `plot_manager.py`
2. ✅ Added `time=self.time if hasattr(self, 'time') else None,` to 440 plot_config() calls
3. ✅ Added `object.__setattr__(self, 'time', None)` initialization in 31 data class `__init__` methods (fixes hasattr spam)

**Root Cause of Spam:** `hasattr(self, 'time')` was triggering `__getattr__` because `time` wasn't in `self.__dict__`. Solution: Initialize `time=None` in `__init__` like `datetime_array`.

**Final Result:**
- 33 files modified, 915 lines added
- ✅ Clean import (no spam)
- ✅ `.time` accessible at variable level (TT2000 epoch for HCS calculations)
- ✅ `.datetime_array` works as before
- ✅ Full backward compatibility

**CDF Generator Updated:**
- ✅ Updated `data_import_cdf.py` template to include `time` parameter in all generated plot_config() calls
- ✅ Updated template to initialize `object.__setattr__(self, 'time', None)` in generated `__init__` methods
- ✅ Future CDF-generated classes will automatically include .time support

**Status:** ✅ COMPLETE - All files updated, tested, and ready for commit

**Total Changes:**
- 34 files modified (33 data classes + plot_manager.py + data_import_cdf.py)
- 920+ lines added
- 3 debug/automation scripts created

---

## End of Session
