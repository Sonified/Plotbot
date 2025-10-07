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

