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
- **Date**: 2025-10-28
- **Status**: Ready to push

