# Captain's Log - September 26, 2025

## Investigation: CDF Class Styling Preservation Issue

### Problem Summary
Auto-generated CDF classes lose custom styling (colors, labels) during merge operations in `data_cubby`, while manually written classes preserve their styling correctly.

### Key Files Involved
- **`plotbot/data_cubby.py`** - Contains merge path logic that may not call `update()` for CDF classes
- **`plotbot/data_import_cdf.py`** - Template generation for auto-generated CDF classes
- **`plotbot/data_classes/custom_classes/psp_waves_test.py`** - Auto-generated test case showing the issue
- **`plotbot/data_classes/psp_mag_rtn.py`** - Reference class with proper state preservation
- **`debug_path_comparison.py`** - Test script confirming all classes take identical paths (UPDATE → MERGE)

### Investigation Findings
1. **Path Analysis**: ALL classes (mag_rtn, mag_rtn_4sa, mag_sc_4sa, proton.anisotropy, psp_waves_test) take identical paths:
   - First load: UPDATE PATH (calls `update()` ✅)
   - Subsequent loads: MERGE PATH (does not call `update()` ❌)

2. **Styling Behavior**: Despite identical paths, only CDF classes lose styling during merge operations
   - Manual classes (mag_rtn, proton, etc.) preserve their inherent colors/labels
   - Auto-generated CDF classes lose custom styling after merge

3. **Root Cause**: Issue is specific to CDF class template implementation, not universal to merge path

### Next Steps
- Add debug logging to CDF class `update()` method to trace state preservation
- Compare state handling between manual classes and auto-generated CDF classes during merge operations
- Focus investigation on why CDF template state preservation differs from manual classes

### Status: Active Investigation
The issue is isolated to auto-generated CDF classes, not a system-wide merge path problem.

---

## Micromamba Installer Path Fix

### Problem
Friend's installation failed with:
```
❌ Error: Failed to install micromamba.
❌ Error: Micromamba initialization failed with code 1.
```

Micromamba was installed successfully via Homebrew, but our installer script couldn't find it at the expected path.

### Root Cause
- **Homebrew installed micromamba correctly** at `/Users/sfordin/homebrew/Cellar/micromamba/2.3.2/`
- **Path mismatch**: Script was looking for hardcoded paths instead of asking Homebrew directly
- **Over-engineering**: Used defensive programming with path arrays instead of trusting Homebrew

### Solution
Simplified path detection by asking Homebrew directly:
```bash
# Before: Hardcoded path arrays and defensive checks
# After: Ask Homebrew where it put micromamba
MICROMAMBA_PATH="$(brew --prefix micromamba)/bin/micromamba"
```

### Files Updated
- `install_scripts/1_init_micromamba.sh` - Use `brew --prefix micromamba`
- `install_scripts/3_setup_env_micromamba.sh` - Simplified path detection
- `install_scripts/4_register_kernel_micromamba.sh` - Same simplification
- `install_scripts/install_micromamba.sh` - Use direct `micromamba` command
- `install_scripts/debug_micromamba.sh` - Simplified

### Status: Fixed
Cleaner, more reliable approach that trusts Homebrew's installation instead of defensive path hunting.

### Problem
Friend reported installation failure during micromamba setup:
```
❌ Error: Failed to install micromamba.
❌ Error: Micromamba initialization failed with code 1.
```

### Root Cause  
- **Over-engineering**: Used hardcoded path arrays instead of asking Homebrew directly
- **Path mismatch**: Script assumed specific installation paths rather than trusting Homebrew

### Solution Implemented
**Much simpler approach** - Ask Homebrew directly where it installed micromamba:
```bash
# Before: Complex path arrays and defensive checks
# After: Simple and reliable
MICROMAMBA_PATH="$(brew --prefix micromamba)/bin/micromamba"
```

This approach:
- **Trusts Homebrew** instead of defensive programming
- **Always accurate** since we ask Homebrew directly
- **Much cleaner** code without hardcoded path arrays

### Status: Fixed  
Cleaner, more reliable installer that works with any Homebrew configuration.

---

## Git Push v3.48

**Commit Message**: `v3.48 Fix: Micromamba installer path detection - robust failsafe approach with brew --prefix fallbacks`

**Changes**:
- Fixed micromamba installer path detection issues
- Implemented robust failsafe approach: `brew --prefix micromamba` → `command -v` → hardcoded fallbacks
- Updated all installer scripts for better compatibility across different Homebrew configurations
- Cleaner code that trusts Homebrew while providing safety nets

**Version**: v3.48
