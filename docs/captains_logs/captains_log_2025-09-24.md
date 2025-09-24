# Captain's Log - 2025-09-24

## Critical Bug Fix: PySpedas Data Directory Configuration

### Problem Discovered
- **Issue**: Users experiencing "no data for that time period" errors when running plotbot examples
- **Root Cause**: PySpedas data directory mismatch
  - PySpedas was creating data in `psp_data/` (top level directory)
  - Plotbot was looking for data in `data/psp/` (organized subdirectory)
  - SPEDAS_DATA_DIR environment variable was **never being set** during initialization

### Investigation Process
- Discovered through user installation help session
- User's plotbot had empty data_cubby (all NoneType values)
- Data download was working but saving to wrong location
- Confirmed bug with direct testing of PlotbotConfig class

### Technical Details
**Bug Location**: `plotbot/config.py` line 25
```python
# DO NOT set environment variable on init - true lazy loading!
```

**The Problem**:
1. ✅ `PlotbotConfig.__init__()` correctly set `_data_dir` to `/Users/.../Plotbot/data/`
2. ❌ But `_configure_pyspedas_data_directory()` was **never called** during initialization
3. ❌ SPEDAS_DATA_DIR environment variable remained `NOT SET`
4. ❌ PySpedas ignored Plotbot's data_dir setting and used default behavior
5. ❌ Data saved to `psp_data/` but Plotbot looked in `data/psp/`

### Solution Implemented
**File**: `plotbot/config.py`
**Change**: Added one critical line to `__init__()` method:

```python
# CRITICAL FIX: Configure PySpedas data directory on initialization
# This ensures SPEDAS_DATA_DIR is set before any PySpedas imports
self._configure_pyspedas_data_directory()
```

### Verification
**Before Fix**:
```
Config data_dir: data
SPEDAS_DATA_DIR: NOT SET
```

**After Fix**:
```
Config data_dir: data
SPEDAS_DATA_DIR: /Users/robertalexander/GitHub/Plotbot/data
```

### Impact
- **Fixes**: New user installations will now work correctly by default
- **Resolves**: Data directory mismatch causing "no data" errors
- **Ensures**: PySpedas creates `data/psp/` instead of `psp_data/`
- **Maintains**: All existing functionality for users who manually set data_dir

### Lessons Learned
- "Lazy loading" approach broke basic functionality
- Environment variables must be set before library imports, not after
- Default behavior should work out-of-the-box for new users
- Testing installation from scratch reveals configuration issues

### Micromamba Installer Overhaul (v3.40)

**Additional Critical Fixes Applied:**
- **NASA Network Compatibility**: Added Jaye's anaconda-avoiding flags to all micromamba commands
  - `--no-rc --override-channels -c conda-forge --channel-priority strict`
  - Eliminates all contact with `repo.anaconda.com`
  - Uses only conda-forge servers (government network friendly)
- **Path Corrections**: Fixed remaining micromamba path inconsistencies
- **Case Sensitivity**: Resolved directory path case issues in installers

**Testing Results:**
- ✅ Micromamba installer now completes without anaconda warnings
- ✅ All packages install from conda-forge only
- ✅ Environment creation successful on restricted networks
- ✅ Plotbot development package installation working

### Git Commit
**Version**: v3.40  
**Commit Message**: "v3.40 Critical Fix: Complete micromamba installer overhaul - NASA network compatible with anaconda-avoiding flags"

### Next Steps
- Test installer on fresh system with network restrictions
- Monitor for any regressions from changes
- Consider creating installation verification script
