# Plotbot V3: Hierarchical Modular Architecture

**Status:** 🚀 **Revolutionary Design Phase** - Creating the Universal Space Physics Data Standard

## 1. Vision Statement

Plotbot V3 introduces a **revolutionary hierarchical naming structure** that will fundamentally change how space physics data analysis works. Instead of flat, mission-specific naming conventions, V3 implements an infinitely scalable hierarchical system that can handle any mission, any instrument, any resolution, from any era.

## 2. The Universal Hierarchical Structure

### **4-Level Hierarchy (Revised):**
```
mission.instrument.product.variable
```

This revised structure uses a more direct mapping to existing data product names, making the transition more intuitive for users while maintaining the benefits of hierarchical organization.

### **Examples:**

**Parker Solar Probe:**
- `psp.mag.rtn_4sa.br` (standard resolution mag_rtn_4sa product)
- `psp.mag.rtn.br` (higher resolution mag_rtn product)
- `psp.fields.sc_4sa.ex` (electric field in spacecraft coordinates)

**WIND Satellite:**
- `wind.mfi.h0_gse.bx` (3-second resolution in GSE coordinates)
- `wind.mfi.h1_gse.bx` (higher resolution if available)
- `wind.swe.h5.t_elec` (electron temperature from quadrature analysis)

**MMS Constellation:**
- `mms1.fgm.srvy_gse.bx` (survey mode in GSE coordinates)
- `mms1.fgm.brst_gse.bx` (burst mode)
- `mms2.fpi.fast_gse.density` (fast plasma investigation)

**THEMIS:**
- `themis.fgm.l2_gse.bx` (Level 2 processing in GSE coordinates)

**Future Missions:**
- `artemis1.mag.survey_selene.bx` (Lunar missions)
- `maven.mag.survey_mso.bx` (Mars missions)
- `juno.mag.perijove_jso.bx` (Jupiter missions)
- `starlink.plasma.fast_geo.density` (Commercial constellations)

## 3. Backward Compatibility Strategy

### **Current plotbot usage:**
```python
plotbot(trange, mag_rtn_4sa.br, 1)
```

### **V3 usage:**
```python
plotbot(trange, psp.mag.rtn_4sa.br, 1)
```

### **Transition approach:**
- V3 supports both syntaxes during transition period
- `mag_rtn_4sa.br` automatically maps to `psp.mag.rtn_4sa.br`
- Warning messages guide users to new syntax
- Full backward compatibility for 2+ years

## 4. Technical Implementation

### **4.1 Metadata-Driven Architecture**

Each mission gets a comprehensive metadata structure:

```python
mission_metadata = {
    'mission': 'wind',
    'instruments': {
        'mfi': {  # Magnetic Field Investigation
            'description': 'Fluxgate Magnetometer',
            'coordinate_systems': {
                'gse': {
                    'description': 'Geocentric Solar Ecliptic',
                    'resolutions': {
                        'h0_gse': {  # 3-second resolution in GSE
                            'cadence': '3s',
                            'description': '3-second averages in GSE coordinates',
                            'variables': {
                                'bx': {
                                    'description': 'X-component magnetic field',
                                    'units': 'nT',
                                    'calculations': None
                                },
                                'by': {...},
                                'bz': {...},
                                'bmag': {
                                    'description': 'Magnetic field magnitude',
                                    'units': 'nT',
                                    'calculations': {
                                        'operation': 'magnitude',
                                        'inputs': ['bx', 'by', 'bz']
                                    }
                                }
                            }
                        },
                        'h1': {  # Higher resolution
                            'cadence': '0.1s',
                            'description': 'High resolution',
                            'variables': {...}
                        }
                    }
                }
            }
        }
    }
}
```

### **4.2 Dynamic Class Factory**

The `create_data_class()` factory generates mission hierarchies:

```python
# Generate the full hierarchy
wind = create_mission_hierarchy('wind', wind_metadata)

# Usage
plotbot(trange, wind.mfi.h0_gse.bx, 1)
```

### **4.3 Plot Integration**

The existing plotbot infrastructure automatically handles hierarchical variables:

```python
# All of these work identically in plotbot
plotbot(trange, psp.mag.rtn_4sa.br, 1)
plotbot(trange, wind.mfi.h0_gse.bx, 1) 
plotbot(trange, mms1.fgm.brst_gse.bx, 1)
plotbot(trange, themis.fgm.l2_gse.bx, 1)
```

## 5. Revolutionary Impact

### **5.1 Infinite Scalability**
- **Any Mission**: Past, present, future missions plug right in
- **Any Instrument**: Magnetometers, plasma, particles, fields, waves
- **Any Resolution**: Survey, burst, high-res, real-time
- **Any Coordinate System**: Spacecraft, planetary, heliospheric
- **Any Variable**: Components, magnitudes, derived quantities

### **5.2 Intuitive Understanding**
```python
# Immediately obvious what this is:
artemis.mag.survey_selene.bx  # Artemis magnetometer X-component in lunar coordinates
maven.swia.fast_mso.velocity  # MAVEN Solar Wind Ion Analyzer velocity in Mars coordinates
```

### **5.3 Cross-Mission Analysis**
```python
# Compare magnetic fields across missions
plotbot(trange, [
    psp.mag.rtn_4sa.bmag,
    wind.mfi.h0_gse.bmag, 
    themis.fgm.l2_gse.bmag
], 1)
```

## 6. Implementation Roadmap

### **Phase 1: Core Infrastructure (Current)**
- ✅ Dynamic class factory (`create_data_class()`)
- ✅ Metadata-driven variable creation
- ✅ Automatic calculations (magnitude, etc.)
- ✅ VS Code autocomplete support (.pyi stubs)
- ✅ WIND proof of concept

### **Phase 2: Mission Integration**
- [ ] Convert existing PSP classes to hierarchical
- [ ] Add THEMIS support
- [ ] Add MMS support
- [ ] Add WIND full support

### **Phase 3: Ecosystem Integration**
- [ ] Pyspedas integration layer
- [ ] CDAWeb automatic metadata extraction
- [ ] Mission plugin system
- [ ] Community contribution framework

### **Phase 4: Community Adoption**
- [ ] Documentation and tutorials
- [ ] Migration tools for existing code
- [ ] Conference presentations
- [ ] Publication in space physics journals

## 7. Why This Will Change Everything

### **7.1 Current State (Chaos)**
Every mission has different conventions:
- MMS: `'mms1_fgm_b_gse_srvy_l2'`
- THEMIS: `'thd_fgs_gse'`
- PSP: `mag_rtn_4sa.br`
- WIND: `'wi_h0_mfi_BGSE'`

### **7.2 V3 State (Universal Standard)**
Consistent, intuitive hierarchy:
- MMS: `mms1.fgm.srvy_gse.bx`
- THEMIS: `themis.fgm.l2_gse.bx`
- PSP: `psp.mag.rtn_4sa.br`
- WIND: `wind.mfi.h0_gse.bx`

### **7.3 Community Benefits**
- **Students**: Immediate understanding of data structure
- **Researchers**: Easy cross-mission comparisons
- **Developers**: Standardized plugin development
- **Data Centers**: Unified metadata standards

## 8. Technical Files & Architecture

### **Core Files:**
- `dynamic_class_test.py` - Dynamic class factory
- `modular_cdf_processor.py` - Universal CDF processing
- `wind_mag_poc.py` - WIND proof of concept
- `plotbot_wind_integration.py` - Integration example

### **Documentation:**
- `MODULAR_ARCHITECTURE_ROADMAP.md` - Implementation details
- `wind_modular_demo.ipynb` - Interactive demonstration

### **File Organization:**
```
plotbot_v3/                    # New modular architecture
├── dynamic_class_test.py      # Core factory
├── modular_cdf_processor.py   # Universal processor  
├── wind_mag_poc.py           # WIND implementation
├── plotbot_wind_integration.py # Integration bridge
└── mission_configs/          # Mission metadata
    ├── wind_config.py
    ├── psp_config.py
    └── mms_config.py

wind_modular_demo.ipynb       # Top-level demo notebook
```

## 9. Call to Action

**This is our moonshot moment.** 🌙

Plotbot V3 isn't just an upgrade - it's the foundation for the next generation of space physics data analysis. We're creating the standard that the entire community will use for decades to come.

**The revolution starts now.**

---

*Plotbot V3: Because the universe is hierarchical, and so should our data analysis.* 