# Plotbot - AI Quick Reference

**Mission**: Rapid space physics data visualization, audification, and analysis tool for multiple spacecraft, currently featuring Parker Solar Probe and WIND. Created by Dr. Jaye Verniero & Dr. Robert Alexander for publication-ready scientific plotting.

**Philosophy**: Class-based architecture enabling intuitive data access (`mag_rtn.br`), automatic downloading, and seamless integration of multi-mission space physics data.

## Core Functions
- `plotbot(trange, var, axis, ...)` - Time series plotting with auto-download
- `plotbot_interactive(trange, var, axis, ...)` - Web interactive plots, click-to-VDF
- `multiplot(plot_list)` - Multi-panel time analysis across encounters  
- `showdahodo(trange, x_var, y_var)` - Hodogram/scatter plots for variable relationships
- `vdyes(trange)` - VDF plotting (theta/phi/collapsed distributions)
- `audifier(var, trange)` - Audio generation for sonification
- `showda_holes(trange, x, y)` - Magnetic hole analysis (experimental)

## Class-Based Data Access Pattern
```python
import plotbot; from plotbot import *
trange = ['2020-01-29/18:00:00', '2020-01-29/20:00:00']
plotbot(trange, mag_rtn_4sa.br, 1, proton.anisotropy, 2)
# Data classes are pre-instantiated, variables access via dot notation
```

## PSP Data Classes  
**Magnetic Field**: `mag_rtn_4sa` (4 samples/sec), `mag_rtn` (hi-res), `mag_sc_4sa`, `mag_sc`  
- Components: `.br`, `.bt`, `.bn`, `.bmag`, `.pmag`, `.all`

**Plasma**: `proton` (std), `proton_hr` (hi-res), `psp_alpha`  
- Moments: `.density`, `.temperature`, `.anisotropy`, `.v_sw`, `.pressure`
- Velocity: `.vr`, `.vt`, `.vn` (RTN coordinates)
- Flux spectrograms: `.energy_flux`, `.theta_flux`, `.phi_flux`

**Electrons**: `epad` (std), `epad_hr` (hi-res)  
- Data: `.strahl` (pitch angle spectrogram)

**FIELDS**: `psp_dfb` (electric field spectra), `psp_qtn` (electron density/temp)  
- DFB: `.ac_spec_dv12`, `.ac_spec_dv34`, `.dc_spec_dv12`
- QTN: `.density`, `.temperature`

**Orbit**: `psp_orbit` - Position: `.r_sun`, `.carrington_lon`, `.carrington_lat`
**VDF**: `psp_span_vdf` - Velocity distribution functions

## WIND Data Classes
**Magnetic**: `wind_mfi_h2` - `.bx`, `.by`, `.bz`, `.bmag` (GSE coordinates)  
**Plasma**: `wind_3dp_pm` (ion moments), `wind_swe_h1` (thermal speeds), `wind_swe_h5` (electron temp)  
**Electrons**: `wind_3dp_elpd` (pitch angle distributions)

## Customization & Variables
```python
# Custom derived variables
custom_var = custom_variable('name', proton.anisotropy / mag_rtn_4sa.bmag)
# Plot styling (class-based)
mag_rtn_4sa.br.color = 'blue'
mag_rtn_4sa.br.y_scale = 'log'
```

## Data Management & Caching
- `get_data(trange, data_type)` - Download without plotting
- `save_simple_snapshot('file.pkl')` - Persistent cache
- `load_simple_snapshot('file.pkl')` - Restore cache
- Smart download system with auto-fallback

## CDF Integration
```python
scan_cdf_directory('data/cdf_files/')  # Auto-generate classes
cdf_to_plotbot('file.cdf')            # Single file processing
# Generated classes work identically to built-in classes
```

## Server Configuration
```python
config.data_server = 'dynamic'    # SPDF first, Berkeley fallback (default)
config.data_server = 'spdf'       # SPDF/CDAWeb only (public data)
config.data_server = 'berkeley'   # Berkeley server only (latest data)
```

## Class-Based Debug Output
```python
print_manager.show_status = True     # Basic status messages
print_manager.show_debug = True      # Full debug output  
```

## Interactive Features
- `pbi.enabled = True; pbi.port = 8050` - Web interface config
- `plotbot_interactive_vdf(trange)` - VDF time slider widget
- Dependencies: dash, plotly, jupyter-dash

## Testing
```bash
# Master test suite (comprehensive functionality check)
conda run -n plotbot_env python -m pytest tests/test_stardust.py -vv -s

# Specific test 
conda run -n plotbot_env python -m pytest tests/test_stardust.py::test_stardust_plotbot_basic -vv -s
```

## File Structure
- `data/psp/`, `data/wind/` - Mission data (auto-download)
- `data/cdf_files/` - Custom CDF files → auto-generated classes
- `data_snapshots/` - Cached calculations  
- `plotbot/data_classes/` - Class definitions, `data_types.py` config
- `tests/` - Comprehensive test suite with space-themed output
- Notebooks: `plotbot_*_examples.ipynb` (primary learning method)

## Environment & Dependencies  
**Setup**: `conda env create -f environment.yml && conda activate plotbot_env`  
**Core**: Python 3.12.4, numpy 1.26.4, matplotlib 3.9.2, pandas 2.2.2, scipy 1.15.2  
**Space Physics**: cdflib, pyspedas (multi-mission support)  
**Interactive**: dash, plotly, jupyter-dash, ipywidgets  
**IDE Setup**: Automatic during install (creates `.vscode/settings.json`)

## Version & Multi-Mission Support
**Multi-Mission**: PSP (complete FIELDS, SWEAP support), WIND (MFI, SWE, 3DP), extensible framework for additional missions
