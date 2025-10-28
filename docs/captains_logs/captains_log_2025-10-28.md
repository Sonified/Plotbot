# Captain's Log - 2025-10-28

## v3.70 Feature: Added Temperature Calculations (eV) to WIND SWE H1 Class

### Summary
Added automatic temperature conversion from thermal speeds to electron volts (eV) for WIND SWE H1 data. Users can now directly access proton and alpha particle temperatures without needing to create custom variables.

### What Was Done

#### 1. Core Implementation (`wind_swe_h1_classes.py`)
- **Added 4 new temperature variables**:
  - `proton_t_par` - Proton parallel temperature (eV)
  - `proton_t_perp` - Proton perpendicular temperature (eV)
  - `proton_t_anisotropy` - Temperature anisotropy ratio (T_perp/T_par)
  - `alpha_t` - Alpha particle temperature (eV)

- **Temperature conversion formula**:
  ```
  T(eV) = [10^6 × W² × mass / (2 × k_B)] / 11,606
  ```
  - W is thermal speed in km/s
  - mass = m_p for protons, 4×m_p for alphas
  - m_p = 1.67×10^-27 kg
  - k_B = 1.38×10^-23 J/K
  - 11,606 K/eV conversion factor

- **Preserved all original thermal speed variables** (km/s):
  - `proton_wpar`, `proton_wperp`, `proton_anisotropy`, `alpha_w`

#### 2. Type Hints Updated
- Updated `wind_swe_h1_classes.pyi` stub file with all new temperature variables

#### 3. Documentation Updates
- **README.md**: Added temperature variable descriptions with units
- **README_Machine_Readable.md**: Updated WIND data class documentation
- **plotbot_wind_data_examples.ipynb**: 
  - Added new section demonstrating temperature plotting
  - Added explanatory comments about alpha data availability
  - Updated summary section

#### 4. Data Quality Notes
- Alpha particle data may be predominantly fill values (99,999.9 km/s) in some time periods
- Quality filtering correctly detects this and sets data to NaN
- This is expected behavior - alpha measurements are not always available
- Both `alpha_w` (thermal speed) and `alpha_t` (temperature) will be NaN when alpha data is unavailable
- Proton data remains valid and scientifically useful

### Technical Details

**Why eV instead of Kelvin?**
- Standard unit in plasma physics for temperature
- More intuitive for space physics applications
- Direct conversion using 1 eV = 11,606 K

**Data Flow**:
1. Import thermal speeds from CDF files (km/s)
2. Apply quality filtering (fit_flag, physical limits)
3. Calculate temperatures directly in eV
4. Store both thermal speeds and temperatures in `raw_data`
5. Create plot_manager instances with appropriate labels

### Files Modified
- `plotbot/data_classes/wind_swe_h1_classes.py` - Core implementation
- `plotbot/data_classes/wind_swe_h1_classes.pyi` - Type hints
- `plotbot/__init__.py` - Version bump to v3.70
- `README.md` - Documentation
- `README_Machine_Readable.md` - Quick reference
- `example_notebooks/plotbot_wind_data_examples.ipynb` - Usage examples

### Usage Example
```python
from plotbot import *

trange = ['2022-06-01 20:00:00', '2022-06-02 02:00:00']

# Plot temperatures (NEW!)
plotbot(trange, 
        wind_swe_h1.proton_t_par, 1,
        wind_swe_h1.proton_t_perp, 2,
        wind_swe_h1.proton_t_anisotropy, 3)

# Or plot thermal speeds (still available)
plotbot(trange,
        wind_swe_h1.proton_wpar, 1,
        wind_swe_h1.proton_wperp, 2)
```

### Next Steps
- Monitor user feedback on eV as the temperature unit
- Consider adding similar temperature calculations to other plasma instruments if requested
- Document temperature conversion formulas in scientific publications using Plotbot

### Git Information
- **Version**: v3.70
- **Commit Message**: "v3.70 Feature: Added temperature calculations (eV) to wind_swe_h1 class for proton and alpha particles"
- **Commit Hash**: 5f809f1
- **Date**: 2025-10-28
- **Status**: ✅ Successfully pushed to origin/main

---

## v3.72 Feature: Per-Axis Line Drawing API for Plot Annotations

### Summary
Implemented a clean method-based API for adding vertical and horizontal lines to plotbot figures. Users can now annotate specific axes with time markers or threshold lines using `ploptions.ax1.add_vertical_line()` and `add_horizontal_line()` methods.

### What Was Done

#### 1. Core Implementation (`ploptions.py`)

**Created `AxisOptions` class:**
- `add_vertical_line(time, color='black', style='--', width=1.0, label=None)` - Add time markers
- `add_horizontal_line(value, color='black', style='--', width=1.0, label=None)` - Add threshold lines
- `clear_vertical_lines()` - Remove all vertical lines from axis
- `clear_horizontal_lines()` - Remove all horizontal lines from axis
- `clear_all_lines()` - Clear both types of lines from axis

**Extended `PlotbotOptions` class:**
- Added explicit properties for axes 1-25: `ax1`, `ax2`, ... `ax25`
- Each axis gets its own `AxisOptions` instance for independent line management
- Lines persist until explicitly cleared or `ploptions.reset()` is called

#### 2. Integration (`plotbot_main.py`)

**Line rendering logic added before figure display:**
- Iterates through all axis options with lines defined
- Converts time strings to datetime objects for vertical lines
- Uses matplotlib's `axvline()` and `axhline()` for rendering
- Properly handles matplotlib date number conversion
- Includes error handling for invalid time formats or values

#### 3. Type Hints (`ploptions.pyi`)

**Created stub file for IDE autocomplete:**
- Full type signatures for all `AxisOptions` methods
- Property definitions for ax1-ax25
- Ensures proper IDE support and type checking

### Files Modified (3 files)
1. ✅ `plotbot/ploptions.py` - Core implementation (203 lines)
2. ✅ `plotbot/plotbot_main.py` - Line rendering integration
3. ✅ `plotbot/ploptions.pyi` - Type hints (NEW FILE)

### Usage Examples

**Basic Usage:**
```python
from plotbot import *

trange = ['2020-01-29/18:00:00', '2020-01-29/20:00:00']

# Add vertical time markers
ploptions.ax1.add_vertical_line('2020-01-29/18:30:00', color='k', style='--')
ploptions.ax1.add_vertical_line('2020-01-29/19:15:00', color='red', style='-')

# Add horizontal threshold lines
ploptions.ax2.add_horizontal_line(10.0, color='blue', style=':', width=2.0)
ploptions.ax2.add_horizontal_line(-5.0, color='green', style='--')

# Plot with annotations
plotbot(trange, mag_rtn_4sa.br, 1, mag_rtn_4sa.bt, 2)
```

**Multiple Lines & Styling:**
```python
# Add multiple vertical lines (e.g., event markers)
for event_time in event_times:
    ploptions.ax1.add_vertical_line(event_time, color='red', style='--', label='Event')

# Add horizontal threshold bands
ploptions.ax3.add_horizontal_line(100, color='orange', style='-', width=2.0, label='Upper Limit')
ploptions.ax3.add_horizontal_line(0, color='orange', style='-', width=2.0, label='Lower Limit')

plotbot(trange, mag_rtn_4sa.br, 1, mag_rtn_4sa.bt, 2, proton.vr, 3)
```

**Clearing Lines:**
```python
# Clear specific axis
ploptions.ax1.clear_vertical_lines()
ploptions.ax2.clear_all_lines()

# Reset everything
ploptions.reset()
```

### Technical Details

**Time Format Support:**
- Accepts datetime strings (parsed via `dateutil.parser`)
- Accepts datetime objects directly
- Automatically converts to matplotlib date numbers for rendering

**Line Style Options:**
- `'-'` - Solid line
- `'--'` - Dashed line (default)
- `':'` - Dotted line
- `'-.'` - Dash-dot line

**Per-Axis Independence:**
- Each axis maintains its own line list
- Lines don't interfere between axes
- Can have different line sets for different plots

**Label Support:**
- Optional `label` parameter for legend integration
- Useful for annotating what lines represent
- Works with matplotlib's standard legend system

### Design Philosophy

**Why Method-Based API?**
- Clean, discoverable syntax: `ploptions.ax1.add_vertical_line()`
- IDE autocomplete works perfectly
- Matches existing `ploptions` pattern
- Natural grouping by axis (ax1, ax2, etc.)

**Why Per-Axis Options?**
- Different axes often need different annotations
- Prevents clutter and confusion
- Allows precise control over which axes get which lines
- Scales to 25 axes without complexity

**Persistent Lines:**
- Lines stay active until explicitly cleared
- Enables reusing line definitions across multiple plots
- User has full control via `clear_*()` methods

### Benefits
✅ **Intuitive API** - Natural method calls, no magic strings  
✅ **Full Control** - Color, style, width, label all customizable  
✅ **Multiple Lines** - Add as many as needed per axis  
✅ **Flexible Time Format** - Strings or datetime objects  
✅ **Easy Cleanup** - Clear methods for each line type  
✅ **Type Safe** - Full type hints for IDE support  
✅ **Independent Axes** - Lines don't interfere between axes  

### Git Information
- **Version**: v3.72
- **Commit Message**: "v3.72 Feature: Added per-axis line drawing API (ploptions.ax1.add_vertical_line / add_horizontal_line) for annotating plots"
- **Commit Hash**: 55f65df
- **Date**: 2025-10-28
- **Status**: ✅ Successfully pushed to origin/main

---

## v3.73 Bugfix: Fixed WIND Data Local File Detection and X-Axis Formatting

### Summary
Fixed two bugs: (1) WIND data files were being re-downloaded even when they existed locally, and (2) x-axis labels showed repeated dates instead of times for short time ranges starting at midnight.

### Issues Fixed

#### Issue 1: WIND Data "Local Files Not Found" False Negative
**Problem:**
- User sees: `📡 Local files not found, proceeding with pyspedas download for wind_swe_h1`
- But files actually exist at `data/wind/swe/swe_h1/2022/wi_h1_swe_20220601_v01.cdf`
- Data is successfully imported, proving files exist
- This causes unnecessary confusion and potential re-downloads

**Root Cause:**
- `smart_check_local_pyspedas_files()` only checked for `'file_pattern'` key
- WIND data types use `'file_pattern_import'` instead
- PSP uses `'file_pattern'`, WIND uses `'file_pattern_import'`
- Smart check returned `None` → triggered "files not found" message

**Fix (`data_download_pyspedas.py`):**
```python
# OLD: Only checked for 'file_pattern'
if 'local_path' not in data_config or 'file_pattern' not in data_config:
    return None

# NEW: Check for either variant
if 'local_path' not in data_config:
    return None
if 'file_pattern' not in data_config and 'file_pattern_import' not in data_config:
    return None

# Priority: spdf_file_pattern > file_pattern > file_pattern_import
file_pattern = data_config.get('spdf_file_pattern', 
                              data_config.get('file_pattern', 
                                             data_config.get('file_pattern_import')))
```

#### Issue 2: X-Axis Shows "APR-26 APR-26 APR-26" Instead of Times
**Problem:**
- Time range: `['2021/04/26 00:00:00.000', '2021/04/26 00:01:00.000']` (1 minute)
- X-axis labels: `APR-26 APR-26 APR-26 APR-26 APR-26` (date repeated)
- Expected: `00:00:00 00:00:10 00:00:20 00:00:30 ...` (times)

**Root Cause:**
- Date formatter checked "is it midnight?" **before** checking "is it a short time range?"
- Logic: `if hour==0 and minute==0: show_date()` came first
- For ranges starting at `00:00:00`, it always showed the date

**Fix (`plotbot_main.py`):**
```python
# OLD: Check midnight first
if dt.hour == 0 and dt.minute == 0:
    return dt.strftime('%b-%d').upper()  # Always showed date at midnight
elif time_range_minutes <= 5:
    return dt.strftime('%H:%M:%S')

# NEW: Check time range duration first
if time_range_minutes <= 5:  # For ranges <= 5 minutes
    return dt.strftime('%H:%M:%S')  # Always show time (even at midnight)
elif time_range_minutes <= 1440:  # For ranges <= 1 day
    if dt.hour == 0 and dt.minute == 0:
        return dt.strftime('%b-%d').upper()
    else:
        return dt.strftime('%H:%M')
```

### Files Modified (3 files)
1. ✅ `plotbot/data_download_pyspedas.py` - Fixed WIND file pattern detection
2. ✅ `plotbot/plotbot_main.py` - Fixed x-axis time formatting logic
3. ✅ `plotbot/__init__.py` - Version bump to v3.73

### Before → After

**WIND Data Detection:**
```
BEFORE: 📡 Local files not found, proceeding with pyspedas download for wind_swe_h1
        ☑️ - CDF Data import complete (files were actually there!)

AFTER:  ✅ Smart check found 2 local wind_swe_h1 file(s):
           📁 /path/to/wi_h1_swe_20220601_v01.cdf
           📁 /path/to/wi_h1_swe_20220602_v01.cdf
        ✅ Using local wind_swe_h1 files (skipping pyspedas)
```

**X-Axis Formatting:**
```
BEFORE: APR-26  APR-26  APR-26  APR-26  APR-26

AFTER:  00:00:00  00:00:10  00:00:20  00:00:30  00:00:40  00:00:50  00:01:00
```

### Technical Details

**WIND vs PSP File Pattern Keys:**
- PSP: `'file_pattern'` → Used by Berkeley server
- WIND: `'file_pattern_import'` → Used for local imports
- Both valid, just different naming conventions
- Smart check now accepts both

**Time Formatting Priority:**
1. ≤5 minutes → Always `HH:MM:SS`
2. ≤1 day → `HH:MM` (except midnight → date)
3. >1 day → `HH:MM`

### Benefits
✅ **No More False "Files Not Found"** - WIND data correctly detected  
✅ **Faster Imports** - No unnecessary downloads  
✅ **Proper Time Labels** - Short ranges show actual times  
✅ **Works at Midnight** - No more date spam on x-axis  
✅ **Consistent Logic** - Same for PSP and WIND  

### Git Information
- **Version**: v3.73
- **Commit Message**: "v3.73 Bugfix: Fixed WIND data local file detection and x-axis time formatting for short time ranges at midnight"
- **Commit Hash**: [pending]
- **Date**: 2025-10-28
- **Status**: [preparing to push]

---

## v3.71 Feature: Added B_phi (Magnetic Field Azimuthal Angle) to PSP and WIND

### Summary
Added magnetic field azimuthal angle (φ_B) calculation and plotting capability to all PSP and WIND magnetic field classes. Implemented as scatter plots with configurable marker size for better visualization of field orientation.

### What Was Done

#### 1. Core Implementation - Added B_phi to 3 Classes

**PSP `mag_rtn_4sa` (4 samples/sec)**
- Formula: `b_phi = np.degrees(np.arctan2(br, bn)) + 180.0`
- RTN coordinates: angle in R-N plane

**PSP `mag_rtn` (high-resolution)**
- Formula: `b_phi = np.degrees(np.arctan2(br, bn)) + 180.0`
- RTN coordinates: angle in R-N plane

**WIND `wind_mfi_h2`**
- Formula: `b_phi = np.degrees(np.arctan2(bx, by)) + 180.0`
- GSE coordinates: angle in X-Y plane

#### 2. Plot Configuration Enhancement

**Added `marker_size` parameter to `plot_config`:**
- Default value: `marker_size=1.0`
- Allows dynamic adjustment of scatter point size
- Users can change via: `mag_rtn_4sa.b_phi.marker_size = 5`

**B_phi Plot Settings:**
- Type: `scatter` (not time_series)
- Color: `purple` 💜
- Marker size: `1` (tiny dots by default)
- Y-axis: φ_B (deg)

#### 3. Type Hints Updated
- Updated all `.pyi` stub files with `b_phi: plot_manager`

#### 4. Documentation Updates
- **README_Machine_Readable.md**: Added `.b_phi` to magnetic field components

### Files Modified (8 files)
1. `plotbot/plot_config.py` - Added `marker_size` parameter
2. `plotbot/data_classes/psp_mag_rtn_4sa.py` - Added b_phi calculation & plot_manager
3. `plotbot/data_classes/psp_mag_rtn.py` - Added b_phi calculation & plot_manager
4. `plotbot/data_classes/wind_mfi_classes.py` - Added b_phi calculation & plot_manager
5. `plotbot/data_classes/psp_mag_rtn_4sa.pyi` - Updated type hints
6. `plotbot/data_classes/psp_mag_rtn.pyi` - Updated type hints
7. `plotbot/data_classes/wind_mfi_classes.pyi` - Updated type hints
8. `README_Machine_Readable.md` - Updated documentation
9. `plotbot/__init__.py` - Version bump to v3.71

### Usage Example
```python
from plotbot import *

trange = ['2020-01-29', '2020-01-30']

# Plot azimuthal angle (default: tiny purple scatter points)
plotbot(trange, mag_rtn_4sa.b_phi, 1)

# Adjust marker size dynamically
mag_rtn_4sa.b_phi.marker_size = 5
plotbot(trange, mag_rtn_4sa.b_phi, 1)

# Available for all mag classes
plotbot(trange, mag_rtn.b_phi, 1)        # PSP hi-res
plotbot(trange, wind_mfi_h2.b_phi, 1)    # WIND
```

### Technical Details

**Why Scatter Plot?**
- Better visualization for discrete angle measurements
- Avoids artificial connections between non-continuous data
- Easier to see data gaps and quality issues

**Azimuthal Angle Convention:**
- PSP (RTN): arctan2(Br, Bn) measures angle from N-axis toward R-axis
- WIND (GSE): arctan2(Bx, By) measures angle from Y-axis toward X-axis
- +180° offset brings range to [0°, 360°] for easier interpretation

**Marker Size Feature:**
- New universal parameter for all scatter plots
- Can be adjusted per-variable like other plot properties
- Default of 1.0 provides good balance for most use cases

### Git Information
- **Version**: v3.71
- **Commit Message**: "v3.71 Feature: Added b_phi (magnetic field azimuthal angle) to PSP and WIND mag classes with scatter plot support"
- **Commit Hash**: d15911a
- **Date**: 2025-10-28
- **Status**: ✅ Successfully pushed to origin/main

