# WIND Data Integration Implementation Plan

## Overview
This document outlines the strategy for integrating WIND satellite data into Plotbot while maintaining the current architecture and leveraging the simplified pyspedas-only download pathway.

## Current State Analysis

### Architecture Strengths
- **Unified Configuration**: `psp_data_types.py` serves as single source of truth
- **Established Patterns**: Data classes, plot managers, and stub files follow consistent patterns
- **Working Infrastructure**: Download, import, caching, and plotting systems are proven
- **PySpedas Integration**: `data_download_pyspedas.py` already handles SPDF downloads

### WIND Data Advantages
- **Simplified Downloads**: Only pyspedas pathway needed (no Berkeley server complexity)
- **Public Data**: No authentication requirements
- **Standard Formats**: CDF files following space physics conventions
- **Mature Mission**: Well-documented, stable data products

## PSP/WIND Data Product Overlap Analysis

### Substantial Overlap - Can Reuse Existing Styling ✅

**Magnetic Field Data (WIND MFI ↔ PSP FIELDS)**
- **WIND**: `BGSE` (vector B in GSE), `BF1` (|B|)  
- **PSP**: `br/bt/bn` (RTN), `bx/by/bz` (SC), `bmag`
- **Reusable**: Colors (`'black'` for |B|, `'red'`/`'blue'`/`'purple'` for components), labels (`'B (nT)'`, `'|B| (nT)'`), scales (`'linear'`)
- **Only difference**: Coordinate system labels (`$B_X$`, `$B_Y$`, `$B_Z$` vs `$B_R$`, `$B_T$`, `$B_N$`)

**Proton Moments (WIND SWE_H1 + 3DP_PM ↔ PSP SPAN-i)**
- **WIND**: `Proton_Wpar_nonlin`, `Proton_Wperp_nonlin`, `P_VELS`, `P_DENS`, `P_TEMP`
- **PSP**: `t_par`, `t_perp`, `vr/vt/vn`, `density`, `temperature`
- **Reusable**: Temperature colors (`'magenta'`), density colors (`'blue'`), velocity colors (`'red'`, `'green'`, `'blue'`), anisotropy calculation (`Wperp/Wpar`)

**Electron Data (WIND 3DP_ELPD ↔ PSP SPAN-e EPAD)**
- **WIND**: `FLUX` vs `PANGLE` (pitch angle distributions)
- **PSP**: `strahl` pitch angle distributions  
- **Reusable**: Spectrogram styling, colormap approaches, pitch angle axis handling

### New WIND-Specific Products 🆕

**Alpha Particles** (Major new product type)
- **WIND**: `Alpha_W_Nonlin`, `A_DENS`, `A_TEMP`
- **PSP**: No dedicated alpha particle class currently
- **Need**: New styling, colors, labels for alpha particles

**Data Quality Flags**
- **WIND**: `fit_flag`, `VALID`
- **PSP**: Quality flags exist but aren't typically plotted as variables

### Coverage Assessment
**~80% overlap** where WIND mirrors PSP products and we can reuse styling. Main new product type is alpha particles.

## Implementation Strategy: Unified Data Types Approach (v2.x)

### Why This Approach  
1. **Quick Implementation**: Get WIND working fast for immediate use
2. **Minimal Code Changes**: Leverages existing infrastructure with ~8 import statement changes
3. **Non-Breaking**: All existing PSP names stay exactly the same (mag_rtn_4sa, proton, epad)
4. **Maintains Working Patterns**: Preserves proven architecture for v2.x iteration
5. **Reuses PSP Styling**: Leverage 80% overlap in magnetic field, proton, electron products
6. **Simplified WIND Entries**: Much cleaner than PSP due to pyspedas-only pathway

### V3.0 Transition Considerations

**WIND as V3 Testbed Strategy:**
- WIND could serve as an excellent testbed for v3.x dynamic approaches before applying to PSP
- **Advantages**: Simpler (pyspedas-only), clean slate (no legacy users), good validation platform
- **V3 Approach**: Dynamic configuration with separated styling files, flexible classes, dependency management
- **Implementation Path**: v2.x WIND first (quick wins), then v3.x WIND prototype, then apply learnings to PSP

**Server Complexity Considerations:**
- PSP has complex Berkeley/SPDF dual-server logic that needs careful v3 design
- WIND's pyspedas-only approach removes this complexity for prototyping
- Multi-server handling strategies need broader architectural conversations

**Recommended Approach**: Implement WIND with v2.x patterns now for immediate utility, then use WIND as v3 transition vehicle later.

## Phase 1: Core Infrastructure Updates

### 1.1 Rename and Restructure Data Types File
```bash
# File operation
mv plotbot/data_classes/psp_data_types.py plotbot/data_classes/data_types.py
```

### 1.2 Update Import Statements
**Files requiring import changes (8 total):**
- `plotbot/get_data.py`
- `plotbot/data_import.py` 
- `plotbot/data_download_pyspedas.py`
- `plotbot/data_download_helpers.py`
- `plotbot/data_snapshot.py`
- `plotbot/data_download_berkeley.py`
- `plotbot/zarr_storage.py`
- `plotbot/plotbot_main.py`

**Change pattern:**
```python
# FROM:
from .data_classes.psp_data_types import data_types

# TO:
from .data_classes.data_types import data_types
```

### 1.3 Add Mission Identification
Update data types structure to include mission metadata:
```python
data_types = {
    # PSP entries (keep existing names unchanged!)
    'mag_RTN_4sa': {
        'mission': 'psp',                    # Add mission field
        'data_source': 'berkeley_and_spdf',  # Existing complexity
        # ... all existing fields stay the same
    },
    'spi_sf00_l3_mom': {
        'mission': 'psp',                    # Add mission field  
        # ... all existing fields stay the same
    },
    
    # WIND entries (new, simplified)
    'wind_mfi_h2': {
        'mission': 'wind',
        'data_source': 'pyspedas_only',      # Simplified!
        'local_path': os.path.join('data', 'wind', 'mfi', 'h2'),
        'pyspedas_datatype': 'mfi_h2',
        'pyspedas_func': 'pyspedas.wind.mfi',
        'data_level': 'h2',
        'file_time_format': 'daily',
        'data_vars': ['BGSE', 'BF1'],
    }
}
```

## Phase 2: WIND Data Types Definition

### 2.1 WIND Data Products to Implement
Based on `wind-data-products-list.md`:

**Magnetic Field Investigation (MFI)**
```python
'wind_mfi_h2': {
    'mission': 'wind',
    'data_source': 'pyspedas_only',
    'local_path': os.path.join('data', 'wind', 'mfi', 'h2'),
    'pyspedas_datatype': 'mfi_h2',
    'pyspedas_func': 'pyspedas.wind.mfi',
    'data_level': 'h2', 
    'file_time_format': 'daily',
    'data_vars': ['EPOCH', 'BGSE', 'BF1'],
}
```

**Solar Wind Experiment (SWE)**
```python
'wind_swe_h1': {
    'mission': 'wind',
    'data_source': 'pyspedas_only',
    'local_path': os.path.join('data', 'wind', 'swe', 'h1'),
    'pyspedas_datatype': 'swe_h1',
    'pyspedas_func': 'pyspedas.wind.swe',
    'data_level': 'h1',
    'file_time_format': 'daily', 
    'data_vars': ['EPOCH', 'Proton_Wpar_nonlin', 'Proton_Wperp_nonlin', 'Alpha_W_Nonlin', 'fit_flag'],
}

'wind_swe_h5': {
    'mission': 'wind',
    'data_source': 'pyspedas_only',
    'local_path': os.path.join('data', 'wind', 'swe', 'h5'),
    'pyspedas_datatype': 'swe_h5',
    'pyspedas_func': 'pyspedas.wind.swe',
    'data_level': 'h5',
    'file_time_format': 'daily',
    'data_vars': ['Epoch', 'T_elec'],
}
```

**3D Plasma Analyzer (3DP)**
```python
'wind_3dp_elpd': {
    'mission': 'wind', 
    'data_source': 'pyspedas_only',
    'local_path': os.path.join('data', 'wind', '3dp', 'elpd'),
    'pyspedas_datatype': '3dp_elpd',
    'pyspedas_func': 'pyspedas.wind.threedp',
    'data_level': 'l2',
    'file_time_format': 'daily',
    'data_vars': ['EPOCH', 'FLUX', 'PANGLE'],
}

'wind_3dp_pm': {
    'mission': 'wind',
    'data_source': 'pyspedas_only', 
    'local_path': os.path.join('data', 'wind', '3dp', 'pm'),
    'pyspedas_datatype': '3dp_pm',
    'pyspedas_func': 'pyspedas.wind.threedp',
    'data_level': 'l2',
    'file_time_format': 'daily',
    'data_vars': ['EPOCH', 'P_VELS', 'P_DENS', 'P_TEMP', 'A_DENS', 'A_TEMP', 'VALID'],
}
```

## Phase 3: WIND Data Classes

### 3.1 File Structure
```
plotbot/data_classes/
├── data_types.py                    # Renamed, unified config
├── wind_mfi_classes.py              # WIND magnetic field
├── wind_mfi_classes.pyi             # Type hints
├── wind_swe_classes.py              # WIND solar wind experiment
├── wind_swe_classes.pyi             # Type hints  
├── wind_3dp_classes.py              # WIND 3D plasma analyzer
├── wind_3dp_classes.pyi             # Type hints
└── (existing PSP files...)
```

### 3.2 WIND MFI Class Example
Following PSP magnetic field class patterns:
```python
# wind_mfi_classes.py
class wind_mfi_h2_class:
    def __init__(self, imported_data):
        object.__setattr__(self, 'class_name', 'wind_mfi_h2')
        object.__setattr__(self, 'data_type', 'wind_mfi_h2')
        object.__setattr__(self, 'subclass_name', None)
        object.__setattr__(self, 'raw_data', {
            'bgse': None,    # Vector B in GSE coordinates
            'bx': None,      # X component
            'by': None,      # Y component  
            'bz': None,      # Z component
            'bmag': None,    # |B| magnitude
            'all': None,     # All components together
        })
        # ... rest follows PSP pattern

    def calculate_variables(self, imported_data):
        # Extract BGSE vector and BF1 magnitude from CDF
        # Calculate components: bx, by, bz = bgse[:, 0], bgse[:, 1], bgse[:, 2]
        # Store in raw_data dict
        
    def set_ploptions(self):
        # Create plot_manager instances for each component
        # Set appropriate labels, colors, units for WIND data
```

### 3.3 Global Instance Creation
```python
# In wind_mfi_classes.py
wind_mfi_h2 = wind_mfi_h2_class(None)

# In __init__.py
from .data_classes.wind_mfi_classes import wind_mfi_h2
from .data_classes.wind_swe_classes import wind_swe_h1, wind_swe_h5
from .data_classes.wind_3dp_classes import wind_3dp_elpd, wind_3dp_pm
```

## Phase 4: Integration Updates

### 4.1 Update get_data.py
**Add WIND imports:**
```python
# Import WIND data classes
from .data_classes.wind_mfi_classes import wind_mfi_h2
from .data_classes.wind_swe_classes import wind_swe_h1, wind_swe_h5
from .data_classes.wind_3dp_classes import wind_3dp_elpd, wind_3dp_pm
```

**Add mission detection logic:**
```python
# In data type processing loop (around line 240)
if data_type.startswith('wind_'):
    # WIND data types use simplified pyspedas-only pathway
    cubby_key = data_type  # Direct mapping for WIND
    # Skip Berkeley server logic entirely
```

### 4.2 Update data_download_pyspedas.py
**Extend PYSPEDAS_MAP:**
```python
PYSPEDAS_MAP = {
    # Existing PSP entries...
    
    # WIND entries (much simpler!)
    'wind_mfi_h2': {
        'pyspedas_datatype': 'mfi_h2',
        'pyspedas_func': pyspedas.wind.mfi,
        'kwargs': {'level': 'h2'}
    },
    'wind_swe_h1': {
        'pyspedas_datatype': 'swe_h1', 
        'pyspedas_func': pyspedas.wind.swe,
        'kwargs': {'level': 'h1'}
    },
    # ... more WIND entries
}
```

### 4.3 Update data_cubby.py
**Add WIND class mappings:**
```python
_CLASS_TYPE_MAP = {
    # Existing entries...
    
    # WIND entries
    'wind_mfi_h2': wind_mfi_h2_class,
    'wind_swe_h1': wind_swe_h1_class,
    'wind_swe_h5': wind_swe_h5_class,
    'wind_3dp_elpd': wind_3dp_elpd_class,
    'wind_3dp_pm': wind_3dp_pm_class,
}
```

## Phase 5: Testing Strategy

### 5.1 Unit Tests
- Test WIND data type configuration loading
- Test WIND class instantiation and data processing
- Test pyspedas download pathway for WIND data
- Test plotting with WIND variables

### 5.2 Integration Tests  
- Test mixed PSP/WIND plotting: `plotbot(trange, mag_rtn_4sa.br, wind_mfi_h2.bx)`
- Test data cubby with WIND instances
- Test time range handling with WIND data

### 5.3 Example Usage
```python
import plotbot
from plotbot import *

# Example: Compare PSP and WIND magnetic fields
trange = ['2020-01-01', '2020-01-02']
plotbot(trange,
        mag_rtn_4sa.br, 1,        # PSP radial B (existing name unchanged!)
        wind_mfi_h2.bx, 2)        # WIND B_x component (new)
```

## Phase 6: Documentation Updates

### 6.1 README.md Updates
- Add WIND to supported missions list
- Update data structure documentation
- Add WIND variable examples
- Update installation/setup instructions if needed

### 6.2 Example Notebooks
- Create WIND-specific examples
- Create PSP/WIND comparison examples
- Update main Plotbot.ipynb with WIND usage

## Implementation Timeline

### Week 1: Infrastructure
- [ ] Rename data types file and update imports
- [ ] Add mission metadata to configuration
- [ ] Test PSP functionality still works

### Week 2: WIND Data Types
- [ ] Define all WIND data type configurations
- [ ] Test pyspedas downloads for WIND data
- [ ] Verify data storage in unified `data/` structure

### Week 3: WIND Classes
- [ ] Create wind_mfi_classes.py and .pyi
- [ ] Create wind_swe_classes.py and .pyi  
- [ ] Create wind_3dp_classes.py and .pyi
- [ ] Test individual class functionality

### Week 4: Integration & Testing
- [ ] Update get_data.py and related modules
- [ ] Create comprehensive test suite
- [ ] Test mixed PSP/WIND workflows
- [ ] Update documentation

## Future Considerations

### V3.0 Refactor Compatibility
This approach provides a solid foundation for the planned v3.0 dynamic refactor by:
- Establishing mission-aware configuration patterns
- Demonstrating multi-mission data class patterns
- Validating unified data storage approach

### Additional Missions
The patterns established here will make it straightforward to add:
- ACE (Advanced Composition Explorer)
- THEMIS (Time History of Events and Macroscale Interactions during Substorms)
- MMS (Magnetospheric Multiscale Mission)
- Other pyspedas-supported missions

## Success Criteria

### Technical Milestones
- [ ] All existing PSP functionality preserved
- [ ] WIND data successfully downloads via pyspedas
- [ ] WIND variables plot correctly
- [ ] Mixed PSP/WIND analysis workflows function
- [ ] Performance remains acceptable

### User Experience
- [ ] Same familiar plotbot() function works with WIND data
- [ ] Existing PSP variable names unchanged (mag_rtn_4sa.br, proton.density, etc.)
- [ ] Intuitive WIND variable naming (wind_mfi_h2.bx follows wind_instrument_level.component pattern)
- [ ] Clear documentation and examples
- [ ] Smooth learning curve from PSP to WIND usage

---
*Document created: 2025-01-27*  
*Status: Planning phase*  
*Target completion: 4 weeks* 