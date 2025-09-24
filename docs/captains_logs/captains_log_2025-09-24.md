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

## Major Architecture Refactor: The Great Rename (v3.41)

### Accomplishment
- **Mission Complete**: Successfully renamed `ploptions` → `plot_config` across entire codebase
- **Goal**: Free up the `ploptions` name for user-facing global options module
- **Scope**: 107 files changed, 2944 insertions, 2030 deletions

### Technical Implementation
**Automated Codebase-Wide Replacement**:
1. ✅ **File renamed**: `ploptions.py` → `plot_config.py`
2. ✅ **Class renamed**: `ploptions` → `plot_config`  
3. ✅ **Parameters**: `plot_options=` → `plot_config=`
4. ✅ **Attributes**: `.plot_options` → `.plot_config`
5. ✅ **Imports**: `from plotbot.ploptions` → `from plotbot.plot_config`
6. ✅ **Functions**: `retrieve_ploption_snapshot` → `retrieve_plot_config_snapshot`

### Critical Bug Fixes
- **plot_manager.py**: Fixed parameter name mismatches after automated rename
- **Syntax Warnings**: Fixed invalid escape sequences in LaTeX strings (`\odot` → `r'\odot'`)

### Strategic Impact
- **Architecture**: Enables modular plotting system with composable figures
- **User Experience**: Clears path for clean `ploptions.return_figure`/`ploptions.display_figure` API
- **Future Development**: Sets foundation for modular vdyes with plotbot integration

### Verification
- ✅ Core system imports successfully
- ✅ No SyntaxWarnings remaining  
- ✅ All internal references updated correctly
- ✅ Ready for next phase: user-facing ploptions module

### Git Commit
**Version**: v3.41  
**Commit Message**: "v3.41 Major Refactor: Complete ploptions→plot_config rename across codebase - frees ploptions name for user-facing global options"  
**Hash**: c62b101

## Critical VDF File Selection Fix (v3.42)

### Problem Identified
- **Issue**: Colleague experiencing wrong file selection in vdyes()
- **Root Cause**: PySpedas returning both l2 and l3 files, but vdyes blindly taking first file (`VDfile[0]`)
- **Data Error**: l3 files contain moments data (density, temperature), NOT velocity distribution functions

### Technical Analysis
**File Type Distinction**:
- **l2 files** (`spi_sf00_l2_8dx32ex8a`): Raw velocity distribution function data ✅ (Required for vdyes)
- **l3 files** (`spi_sf00_L3_mom`): Processed moments data ❌ (Wrong data type for VDF plotting)

### Solution Implemented
**File**: `plotbot/vdyes.py`
**Changes**:
1. **Debug Logging**: Show ALL files returned by pyspedas
2. **Smart Filtering**: Only select l2 files, never l3
3. **Clear Errors**: Explicit error messages when l3 files found instead of l2
4. **No Fallback**: Never attempt to use l3 files for VDF data

### New Logic
```python
# Debug: Show ALL files returned by pyspedas
l2_files = [f for f in VDfile if 'spi_sf00_l2_8dx32ex8a' in f and 'l3' not in f]

if l2_files:
    selected_file = l2_files[0]  # Use first l2 file
else:
    raise ValueError("VDF data requires l2 files! l3 contains moments, not velocity distributions.")
```

### Git Commit
**Version**: v3.42  
**Commit Message**: "v3.42 Critical Fix: VDF file selection - ensure vdyes always uses l2 files (VDF data) never l3 files (moments only)"  
**Hash**: 7391ced

## PySpedas Parameter Bug Fix (v3.43)

### Critical Discovery
- **Issue**: Jaye's system only finding l3 files despite `level='l2'` parameter
- **Root Cause**: `no_update=True` completely **ignores** the `level='l2'` parameter!
- **PySpedas Behavior**: When `no_update=True`, it returns ANY matching local files regardless of level specification

### Technical Analysis
**Buggy Logic**:
```python
# BAD: no_update=True ignores level='l2' completely
VDfile = pyspedas.psp.spi(..., level='l2', no_update=True)  # Returns l3 files anyway!
```

**Fixed Logic**:
```python
# GOOD: no_update=False respects level='l2' parameter
VDfile = pyspedas.psp.spi(..., level='l2', no_update=False)  # Only returns l2 files
```

### Solution Implemented
**File**: `plotbot/vdyes.py`
**Critical Change**: Removed two-stage download approach, always use `no_update=False`

**Before** (Broken):
- First try: `no_update=True` (ignored level parameter)
- Second try: `no_update=False` (but only if first failed)

**After** (Fixed):
- Single call: `no_update=False` (always respects level parameter)

### Git Commit
**Version**: v3.43  
**Commit Message**: "v3.43 Critical Fix: PySpedas no_update parameter bug - no_update=True ignores level='l2' causing wrong file selection"  
**Hash**: 2a8d34f
