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
