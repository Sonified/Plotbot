# Plotbot Modular Architecture Roadmap

## Overview

This document outlines the transition from individual data class files to a modular, metadata-driven architecture that can handle multiple satellite missions efficiently.

## Current vs. Proposed Architecture

### Current PSP Approach
```
psp_mag_rtn_4sa.py (683 lines)
├── mag_rtn_4sa_class
├── Hardcoded variable names (br, bt, bn, bmag)
├── Custom __getattr__ and __setattr__
├── Fixed plot options
└── Manual calculations

Usage: mag_rtn_4sa.br, mag_rtn_4sa.bmag
```

### New Modular Approach
```
dynamic_class_test.py (313 lines)
├── create_data_class() factory
├── Metadata-driven variables
├── Automatic property creation
├── Configurable calculations
└── Auto-generated .pyi stubs

Usage: wind.mag.gse.bx_gse, wind.mag.gse.bmag
```

## Key Benefits

### 1. **Reusability**
- Single factory works for any satellite/instrument
- Same code handles PSP, WIND, THEMIS, etc.
- Metadata defines behavior, not hardcoded logic

### 2. **Flexibility**
- Variable names from metadata, not code
- Easy to add new coordinate systems
- Configurable calculations via metadata

### 3. **Hierarchical Organization**
```python
# Instead of: psp_mag_rtn_4sa, wind_mag_gse
# Use: psp.mag.rtn.sa4, wind.mag.gse
```

### 4. **VS Code Support**
- Auto-generated .pyi stubs provide autocomplete
- Type hints for better development experience

## Implementation Files Created

### 1. Core Components

#### `dynamic_class_test.py`
- Factory function `create_data_class()`
- Metadata-driven class creation
- Automatic property generation
- Built-in calculations (add, magnitude)
- Auto .pyi stub generation

#### `modular_cdf_processor.py` 
- Generic CDF processor for any mission
- Configurable data extraction
- Multi-file handling
- Coordinate system abstraction

### 2. WIND Integration

#### `wind_mag_poc.py`
- Proof of concept for WIND magnetometer
- Uses pyspedas for download
- Demonstrates metadata structure
- Shows calculated variables (bmag)

#### `plotbot_wind_integration.py`
- Integration bridge to existing plotbot
- Hierarchical namespace demo
- Comparison with current approach

## Metadata Structure

### Variable Definition
```python
'bx_gse': {
    'description': 'Magnetic field X component in GSE coordinates',
    'units': 'nT',
    'cdf_var_name': 'BGSE',
    'component_index': 0,
    'plot_options': {
        'y_label': 'Bx (nT)',
        'legend_label': '$B_X$ (GSE)',
        'color': 'red'
    }
}
```

### Calculation Definition
```python
'bmag': {
    'inputs': ['bx_gse', 'by_gse', 'bz_gse'],
    'operation': 'magnitude',
    'plot_options': {
        'y_label': '|B| (nT)',
        'legend_label': '$|B|$',
        'color': 'black'
    }
}
```

## Integration Strategy

### **Architectural Foundation: Leveraging PySpedas**

Rather than reinventing data acquisition, Plotbot V3 will leverage `pyspedas` as the proven data loading backend while providing the interactive, object-oriented layer on top. This approach combines the best of both worlds:

- **PySpedas strengths**: Robust data downloading, 30+ mission support, standardized CDF handling
- **Plotbot strengths**: Interactive objects, rapid plotting, custom variables, integrated analysis tools

```python
# pyspedas handles data acquisition
raw_data = pyspedas.projects.wind.mfi(trange, datatype='h0')

# Plotbot V3 creates the interactive hierarchical interface
wind = create_data_class('wind', wind_metadata, raw_data)

# Best of both worlds
plotbot(trange, wind.mfi.h0_gse.bx, 1)  # Plotbot's rapid plotting
wind.mfi.h0_gse.bx.color = 'blue'       # Plotbot's interactivity
```

This architectural decision allows V3 to focus on what makes Plotbot unique rather than competing with established infrastructure.

### Phase 1: WIND Proof of Concept ✅
- [x] Create modular factory
- [x] WIND MFI integration
- [x] Demonstrate hierarchical naming
- [x] Show metadata-driven approach

### Phase 2: CDF Processing Framework
- [ ] Generic CDF processor for multiple missions
- [ ] Extended calculation operations
- [ ] Multi-file concatenation
- [ ] Error handling and validation

### Phase 3: Plotbot Integration
- [ ] Extend `get_data.py` for modular classes
- [ ] Update `data_download_pyspedas.py` mapping
- [ ] Integrate with `data_cubby`
- [ ] Add to `psp_data_types.py` pattern

### Phase 4: PSP Migration
- [ ] Convert `psp_mag_rtn_4sa.py` to metadata
- [ ] Migrate other PSP classes
- [ ] Implement `psp.mag.rtn.sa4` hierarchy
- [ ] Maintain backward compatibility

### Phase 5: Multi-Mission Support
- [ ] THEMIS integration
- [ ] MMS integration  
- [ ] STEREO integration
- [ ] Generic mission template

## File Organization

```
plotbot/
├── modular/
│   ├── __init__.py
│   ├── dynamic_factory.py         # Core factory
│   ├── cdf_processor.py           # CDF handling
│   ├── metadata/
│   │   ├── wind_metadata.py       # WIND configs
│   │   ├── psp_metadata.py        # PSP configs
│   │   └── themis_metadata.py     # THEMIS configs
│   └── stubs/                     # Auto-generated .pyi files
├── missions/
│   ├── wind/
│   │   ├── __init__.py
│   │   ├── mag.py                 # wind.mag namespace
│   │   └── swe.py                 # wind.swe namespace
│   └── psp/
│       ├── __init__.py
│       ├── mag.py                 # psp.mag namespace
│       └── fields.py              # psp.fields namespace
└── legacy/                        # Current classes during transition
```

## Usage Examples

### Current PSP Usage
```python
get_data(trange, mag_rtn_4sa)
plot(mag_rtn_4sa.br, mag_rtn_4sa.bt, mag_rtn_4sa.bn)
```

### New Hierarchical Usage
```python
get_data(trange, psp.mag.rtn.sa4)
plot(psp.mag.rtn.sa4.br, psp.mag.rtn.sa4.bt, psp.mag.rtn.sa4.bn)

get_data(trange, wind.mag.gse)
plot(wind.mag.gse.bx_gse, wind.mag.gse.by_gse, wind.mag.gse.bz_gse)
```

### Multi-Mission Comparison
```python
get_data(trange, psp.mag.rtn.sa4, wind.mag.gse)
plot(psp.mag.rtn.sa4.bmag, wind.mag.gse.bmag)
```

## Technical Advantages

### 1. **Reduced Code Duplication**
- Current: ~680 lines per data class
- Modular: ~50 lines metadata + shared factory

### 2. **Easier Maintenance**
- Bug fixes in factory benefit all missions
- Consistent behavior across instruments
- Centralized calculation logic

### 3. **Rapid Development**
- New missions require only metadata
- Automatic property and calculation creation
- Instant VS Code autocomplete support

### 4. **Backward Compatibility**
- Legacy imports can be maintained
- Gradual migration possible
- Existing user code continues working

## Next Steps

1. **Test WIND Integration**: Run the proof of concept
2. **Extend Factory**: Add more calculation operations
3. **Create Templates**: Standard metadata patterns
4. **Integrate with get_data**: Add modular class support
5. **Document Migration**: Guide for converting existing classes

## Questions to Consider

1. **Naming Convention**: Final decision on `psp.mag.rtn.sa4` vs alternatives
2. **Metadata Storage**: File-based vs embedded vs database
3. **Performance**: Impact of dynamic property creation
4. **Testing**: Unit test strategy for metadata-driven classes
5. **Documentation**: Auto-generated docs from metadata

This modular approach positions plotbot for easy multi-mission support while maintaining the power and flexibility users expect. 