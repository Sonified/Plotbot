# Multi-Satellite Data Storage Implementation Plan

## Overview
Plotbot needs to be refactored to consolidate data storage and standardize how different data sources are organized, particularly to resolve path inconsistencies and support multiple satellite missions.

## Current State Analysis

### Existing PSP Data Storage
- **Current Location**: `psp_data/` folder (legacy structure)
- **Data Sources**: 
  - Berkeley SSL server (password-protected)
  - SPDF via pyspedas
  - Local CSV files (FITS, Hamstrings)

### Path Configuration Issues Identified
1. **Legacy PSP paths**: Currently hardcoded in `plotbot/data_classes/psp_data_types.py`
2. **Pyspedas inconsistency**: 
   - Historical downloads appear to go to `psp_data/`
   - Recent downloads creating `psp/` folder instead
   - Unclear what drives this behavior difference

### Multi-Mission Goals
- Support for WIND, ACE, and other missions beyond PSP
- Unified data folder structure for all missions
- Maintain Berkeley server integration for password-protected PSP data
- Leverage pyspedas for missions that support it

## Current Data Organization

### PSP Data Structure (Current)
```
psp_data/
├── fields/
│   └── l2/
│       ├── mag_rtn/
│       ├── mag_rtn_4_per_cycle/
│       ├── mag_sc/
│       └── mag_sc_4_per_cycle/
├── sweap/
│   ├── spe/l3/
│   └── spi/l3/
│       ├── spi_sf00_l3_mom/
│       └── spi_af00_l3_mom/
└── Hamstrings/
```

### Pyspedas Data Structure (Observed)
```
data/
├── psp/  # Recent downloads creating this structure
│   └── [unknown_pyspedas_structure]/
└── wind/
    └── [wind_data_from_pyspedas]/
```

## Implementation Challenges

### 1. Path Standardization
- Need to understand pyspedas default download behavior
- Decide on unified folder structure: `data/` vs mission-specific folders
- Update all hardcoded paths in `psp_data_types.py`

### 2. Multi-Mission Support
- Extend beyond PSP to WIND, ACE, etc.
- Each mission may have different:
  - Data levels (L1, L2, L3)
  - Instrument naming conventions
  - File patterns and structures

### 3. Data Source Integration
- **Berkeley server**: Custom authentication, specific to PSP
- **Pyspedas**: Standard for most missions, no auth required
- **Local files**: CSV, processed data, custom formats

## Proposed Refactor Strategy

### Phase 1: Investigation
1. **Understand pyspedas behavior**:
   - Test downloads to see where files actually go
   - Check pyspedas configuration options for download paths
   - Document actual vs. expected behavior

2. **Audit existing data locations**:
   - Map all current PSP data locations
   - Identify what's in `data/psp/` vs `psp_data/`
   - Determine migration needs

### Phase 2: Path Standardization
1. **Choose unified structure**:
   ```
   data/
   ├── psp/
   ├── wind/
   ├── ace/
   └── [other_missions]/
   ```

2. **Update configuration files**:
   - Modify `psp_data_types.py` paths to point to `data/psp/` instead of `psp_data/`
   - Create mission-agnostic path handling
   - Implement fallback logic for legacy locations

### Phase 3: Multi-Mission Extension
1. **Create mission-specific data type files**:
   - `wind_data_types.py`
   - `ace_data_types.py`
   - etc.

2. **Unified data loading interface**:
   - Mission detection from data type names
   - Automatic source selection (Berkeley vs pyspedas)
   - Consistent data access patterns across missions

## Next Steps
1. **Immediate**: Investigate pyspedas download behavior and path conventions
2. **Short-term**: Document current data locations and inconsistencies
3. **Medium-term**: Implement unified data folder structure
4. **Long-term**: Extend to multi-mission support

## Technical Questions to Resolve
1. Why does pyspedas create `psp/` vs `psp_data/` folders?
2. Can pyspedas download paths be configured/standardized?
3. What's the best migration strategy for existing data?
4. How to handle backward compatibility during transition?

## Related Files
- `plotbot/data_classes/psp_data_types.py` - Current PSP path configuration
- `plotbot/data_download_pyspedas.py` - Pyspedas integration
- `plotbot/data_download_berkeley.py` - Berkeley server authentication

---
*Document created: 2025-01-27*
*Status: Planning phase* 