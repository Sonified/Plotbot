# Captain's Log - 2025-09-10

## Version: v3.28

## Major Fix: Multiplot Constrained Layout Bug

### Problem Identified and Fixed:

**Critical Multiplot Layout Bug**
- **Problem**: The multiplot code was hardcoding `constrained_layout=False` in both subplot creation paths, completely ignoring the user's `plt.options.constrained_layout` setting
- **Impact**: Users could not control layout behavior, `title_y_position` didn't work properly, and title positioning was fundamentally broken
- **Root Cause**: Debug code that forced `constrained_layout=False` was left in production, overriding user preferences

### Technical Details:

**Before Fix:**
```python
# This was happening regardless of user setting:
fig, axs = plt.subplots(n_panels, 1, figsize=figsize, dpi=dpi, constrained_layout=False)
# Always applied manual margins, even when user wanted automatic layout
```

**After Fix:**
```python
# Now respects user setting:
fig, axs = plt.subplots(n_panels, 1, figsize=figsize, dpi=dpi, constrained_layout=options.constrained_layout)

if options.constrained_layout:
    # Let matplotlib handle spacing automatically
    pass
else:
    # Apply manual margins only when user wants manual control
    fig.subplots_adjust(...)
```

### User Impact:

**Fixed Issues:**
- `plt.options.constrained_layout = True` now works properly
- `title_y_position` now works intuitively when using constrained layout
- Users can choose between automatic and manual layout control
- Title positioning is no longer constrained by manual margin settings

**Two Working Modes Now Available:**
1. **Automatic Layout** (`constrained_layout=True`): matplotlib handles all spacing, intuitive title positioning
2. **Manual Layout** (`constrained_layout=False`): user controls margins and spacing manually

### Files Modified:
- `plotbot/multiplot.py`: Fixed both subplot creation blocks to respect user's constrained_layout setting
- Removed temporary debug prints that were added during investigation

### Commit Details:
- **Version**: v3.28
- **Commit Message**: "v3.28 Fix: Multiplot constrained_layout setting now properly respected, fixes title positioning"

This fix resolves a fundamental layout control issue that was preventing proper title positioning and layout customization in multiplot functions.

---

## Version: v3.29

## Minor Configuration Update

### Change Made:
- **Default Data Directory**: Updated `Plotbot.ipynb` to use `config.data_dir = 'default'` by default
- **Previous**: Custom data directory was uncommented 
- **Now**: Default data directory is active, custom is commented out

### Files Modified:
- `Plotbot.ipynb`: Changed default configuration to use standard data directory

### Commit Details:
- **Version**: v3.29
- **Commit Message**: "v3.29 Config: Set default data directory to 'default' in Plotbot.ipynb"
