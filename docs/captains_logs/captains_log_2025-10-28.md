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
- **Date**: 2025-10-28

