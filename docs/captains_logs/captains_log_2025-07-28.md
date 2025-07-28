# Captain's Log 2025-07-28

## Updates:
- Moved `test_data_property_fixes.py`, `test_quick_spectral_fix.py`, `test_epad_debug.py`, and `test_epad_regression.py` from the root directory to the `tests/` directory.
- Renamed the moved test files with the prefix `test_07_28_` to group them: 
    - `test_07_28_data_property_fixes.py`
    - `test_07_28_quick_spectral_fix.py`
    - `test_07_28_epad_debug.py`
    - `test_07_28_epad_regression.py`
- Updated the `sys.path.insert` in `tests/test_07_28_quick_spectral_fix.py` to correctly reference the `plotbot` directory.
- Added `/files_from_Jaye/` to `.gitignore`. 
- Moved `migrate_psp_data.sh` to `local_tests_and_utils/`. 
- Confirmed `check_nans.py` is not used elsewhere in the codebase and remains in the root directory.
- Moved `wind_mag_poc_reference.py` to `wind_evaluation/` and refactored its relative import.
- Confirmed `wind_data_products_test.ipynb` and `wind_data_validation.ipynb` do not need refactoring after being moved to `wind_evaluation/`.
- Verified that the `data/` directory is correctly listed in `.gitignore`. 

## Git Push Details:
- **Version Tag**: 2025_07_28_v3.01
- **Commit Message**: v3.01 Refactor: Cleaned up and reorganized test and utility files, updated .gitignore.
- **Commit Hash**: e6d4206 

## Major Feature Implementation: use_degrees_from_center_times

### Overview
Implemented a new multiplot x-axis option `use_degrees_from_center_times` that allows plotting data with x-axis in degrees relative to user-provided center times, rather than absolute time or complex perihelion lookups. This is a **simpler alternative** to the existing `use_degrees_from_perihelion` feature.

### Key Differences from Perihelion Mode:
- **No database lookups required** - uses center_time directly as reference point
- **Simpler logic** - no complex perihelion time validation or fallback handling
- **User-controlled reference points** - each panel uses its own center_time as 0°
- **Cleaner implementation** - separate variables and logic paths from perihelion code

### Files That Require Changes for Similar Features:

When implementing new multiplot x-axis options similar to this, changes are needed in **4 key files**:

#### 1. `plotbot/multiplot_options.py` (Options Definition)
- **Purpose**: Define the user-facing options and their behavior
- **What to add**:
  - Property getter/setter with type hints 
  - Range property for axis limits (optional)
  - Mutual exclusion logic (disable conflicting options when enabled)
  - Backward compatibility aliases if needed

#### 2. `plotbot/multiplot_options.pyi` (IDE Type Hints)
- **Purpose**: Enable IDE syntax highlighting and autocompletion
- **What to add**:
  - Property stubs with proper type annotations
  - Both main properties and any compatibility aliases

#### 3. `plotbot/multiplot.py` (Core Implementation)
- **Purpose**: The main plotting logic and data transformation
- **What to add**:
  - Feature detection logic in positional_feature_requested check
  - Mode determination logic (set data_type, axis_label, units)
  - Panel-specific calculation logic for each plot type
  - X-axis formatting rules
  - X-axis limit handling

#### 4. Example notebook (Usage Documentation)
- **Purpose**: Show users how to use the new feature
- **What to include**:
  - Clear setup examples
  - Data structure examples  
  - Option configuration examples

### Specific Changes Made:

#### multiplot_options.py Changes:
```python
# Added new property with mutual exclusion
@property
def use_degrees_from_center_times(self) -> bool:
    # Disables conflicting options when enabled
    
@property  
def degrees_from_center_times_range(self) -> Optional[Tuple[float, float]]:
    # Optional fixed range for x-axis
```

#### multiplot.py Changes:
```python
# 1. Added to positional feature detection
positional_feature_requested = (
    # ... existing options ...
    getattr(options, 'use_degrees_from_center_times', False) # Added this line
)

# 2. Added mode determination
elif getattr(options, 'use_degrees_from_center_times', False):
    data_type = 'degrees_from_center_times'
    axis_label = "Degrees from Center Times (°)"
    units = "°"

# 3. Added panel-specific calculation logic  
elif using_positional_axis and getattr(options, 'use_degrees_from_center_times', False):
    # Simple logic - no complex lookups needed
    panel_uses_center_times_degrees = True
    center_time_reference_str = center_dt.strftime('%Y/%m/%d %H:%M:%S.%f')

# 4. Added plotting logic for each plot type (time_series, scatter, spectral)
elif panel_uses_center_times_degrees and center_time_reference_str and positional_mapper:
    # Calculate degrees relative to center_time longitude
    # Much simpler than perihelion - no database lookup needed

# 5. Added axis formatting support
elif current_axis_mode in ['degrees_from_perihelion', 'degrees_from_center_times', ...]:
    # Uses same angle formatter as other degree modes

# 6. Added axis limits support  
elif current_axis_mode == 'degrees_from_center_times' and options.degrees_from_center_times_range:
    ax.set_xlim(options.degrees_from_center_times_range)
```

### Implementation Structure for Future Features:

#### Pattern to Follow:
1. **Separate variables** - Don't reuse existing feature variables (like perihelion_time_str)
2. **Clear naming** - Use descriptive variable names that indicate the feature
3. **Mutual exclusion** - Disable conflicting options in setters
4. **Type hints** - Add to .pyi file for IDE support
5. **Independent logic** - Create separate elif branches rather than modifying existing ones
6. **Consistent formatting** - Reuse existing formatters where appropriate

#### Variable Naming Convention:
- Use feature-specific prefixes: `panel_uses_center_times_degrees` vs `current_panel_use_degrees`
- Reference variables: `center_time_reference_str` vs `perihelion_time_str`
- Clear boolean flags: `panel_actually_uses_degrees` (shared) + feature-specific setup flags

### Testing:
Created `plotbot_degrees_from_center_times_examples.ipynb` with:
- Array of center_times (user reference points)
- Simple configuration: `plt.options.use_degrees_from_center_times = True`
- Range option: `plt.options.degrees_from_center_times_range = (-60, 60)` (optional)

### Key Learnings:
1. **Keep it simple** - Don't over-engineer by reusing complex existing infrastructure
2. **Separate clearly** - Use distinct variables to avoid confusion later
3. **Document thoroughly** - Future developers need to understand the distinction
4. **Test IDE support** - .pyi files are crucial for user experience

This implementation provides a clean, simple alternative to perihelion mode while maintaining full feature parity for axis formatting, limits, and plotting options. 

## Git Push Details - v3.02:
- **Version Tag**: 2025_07_28_v3.02
- **Commit Message**: v3.02 Feature: Implemented use_degrees_from_center_times multiplot x-axis option with clean, simple implementation separate from perihelion code. 