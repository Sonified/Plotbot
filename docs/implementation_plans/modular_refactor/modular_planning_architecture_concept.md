# Plotbot Modular Plotting Architecture Plan

## 🚀 Executive Summary

This document outlines a strategic refactor to create a **compositional plotting architecture** that preserves Plotbot's sophisticated space physics domain intelligence while enabling modular plot composition. The approach leverages matplotlib's proven layout capabilities while adding reusable plot components that can be combined in flexible ways.

## 🎯 Core Vision: Compositional Plot Components

Instead of monolithic plotting functions, we create **modular plot components** that can be prepared independently and rendered to any matplotlib axes. This enables mixing VDF plots, time series, hodograms, and spectral plots in arbitrary arrangements.

### Current State (Monolithic)
```python
# Each function creates complete figures
vdf_fig = vdyes(time)
ts_fig = plotbot(trange, var1, 1, var2, 2)
hodogram_fig = showdahodo(trange, var1, var2)

# Manual figure gluing required for composition
combined_fig = somehow_glue_them_together(vdf_fig, ts_fig)
```

### Proposed State (Compositional)
```python
# Prepare components with data and styling
vdf_component = VDFPlot(time).prepare()
ts_component = TimeSeriesPlot(trange, [var1, var2]).prepare()
hodogram_component = HodogramPlot(trange, var1, var2).prepare()

# Use matplotlib's proven layout system
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Render to specific axes
vdf_component.render_theta_plane(axes[0, 0])
vdf_component.render_phi_plane(axes[0, 1])
ts_component.render_to(axes[1, :])  # Span bottom row
```

## 🔍 Key Architectural Insights

### 1. **Leverage Matplotlib's Strengths**
- **Don't recreate** layout management (gridspec, subplots work great)
- **Do add** space physics domain intelligence and data preparation
- **Focus on** modular components that work with existing matplotlib patterns

### 2. **Separation of Concerns**
- **Data Preparation**: Loading, caching, time alignment, validation
- **Styling Configuration**: Colors, scales, labels, domain-specific defaults
- **Rendering**: Matplotlib plotting calls to specific axes
- **Layout**: Handled by matplotlib's existing tools

### 3. **Preserve Domain Expertise**
- Encounter-specific time range calculations
- Positional coordinate transformations (Carrington, degrees from perihelion)
- Space physics instrument knowledge
- Advanced color schemes and styling

## 📊 Comparison: Traditional vs Modular Approach

### Example 1: Simple Multi-Variable Time Series

#### Traditional PySpedas + Matplotlib (50+ lines)
```python
import pyspedas
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Manual data loading
psp_fields_vars = pyspedas.psp.fields(
    trange=['2020-01-29/12:00', '2020-01-29/18:00'],
    datatype='mag_rtn_4sa', level='l2'
)
psp_sweap_vars = pyspedas.psp.sweap(
    trange=['2020-01-29/12:00', '2020-01-29/18:00'], 
    datatype='spi_sf00_l3_mom', level='l3'
)

# Manual data extraction and time alignment
br_data = get_data('psp_fld_l2_mag_rtn_4sa_br')
temp_data = get_data('psp_swp_spi_sf00_l3_mom_TEMP')

# Manual time clipping (15+ lines of time parsing logic)
def clip_and_align(time_array, data_array, trange):
    # Handle different time formats, UTC conversion
    # Deal with gaps and NaN values
    pass

br_time, br_values = clip_and_align(br_data.times, br_data.y, trange)
temp_time, temp_values = clip_and_align(temp_data.times, temp_data.y, trange)

# Manual matplotlib setup and styling
fig = plt.figure(figsize=(12, 8))
gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1])

ax1 = fig.add_subplot(gs[0])
ax1.plot(br_time, br_values, color='red', linewidth=1.5)
ax1.set_ylabel('Br (nT)', fontsize=12)
ax1.set_title('PSP Magnetic Field and Plasma', fontsize=14)

ax2 = fig.add_subplot(gs[1], sharex=ax1)
ax2.plot(temp_time, temp_values, color='blue', linewidth=1.5)
ax2.set_ylabel('Temperature (K)', fontsize=12)
ax2.set_yscale('log')

# ... more manual plotting code
```

#### Plotbot Modular Approach (8 lines)
```python
from plotbot import *

trange = ['2020-01-29/12:00', '2020-01-29/18:00']

# Automatic data loading, domain intelligence, styling
fig, axes = plt.subplots(3, 1, sharex=True, figsize=(12, 8))

TimeSeriesPlot(trange, mag_rtn_4sa.br).render_to(axes[0])
TimeSeriesPlot(trange, proton.temperature).render_to(axes[1])
TimeSeriesPlot(trange, proton.anisotropy).render_to(axes[2])

plt.tight_layout()
```

### Example 2: Mixed Plot Types (VDF + Time Series)

#### Plotbot Modular Composition
```python
# Space physics domain expertise built in
time = '2020-01-29/18:10:00'
trange = ['2020-01-29/16:00', '2020-01-29/20:00']

# Intelligent layout for space physics
fig, axes = plt.subplots(4, 3, height_ratios=[1, 1, 1, 0.8], 
                        width_ratios=[1, 1, 1], figsize=(16, 12))

# VDF components understand velocity space, coordinates, colormaps
VDFPlot(time).render_theta_plane(axes[0, 0])
VDFPlot(time).render_phi_plane(axes[0, 1])
VDFPlot(time).render_collapsed(axes[0, 2])

# Time series spans bottom with automatic time coordination
TimeSeriesPlot(trange, mag_rtn_4sa.br).render_to(axes[1:, :])
```

## 🏗️ Proposed Architecture

### 1. **Plot Component Base Class**
```python
class PlotComponent:
    def __init__(self, trange, variables):
        self.trange = trange
        self.variables = variables
        self.data = None
        self.styling = None
    
    def prepare(self):
        """Load data, apply styling, return ready-to-render component"""
        self._load_data()
        self._apply_styling()
        return self
    
    def render_to(self, ax):
        """Render to specific matplotlib axes"""
        raise NotImplementedError
    
    def _load_data(self):
        """Handle data acquisition through get_data()"""
        pass
    
    def _apply_styling(self):
        """Apply domain-specific defaults and user customizations"""
        pass
```

### 2. **Specialized Plot Components**

#### TimeSeriesPlot
```python
class TimeSeriesPlot(PlotComponent):
    def __init__(self, trange, variables, axis_config=None):
        super().__init__(trange, variables)
        self.plot_type_handlers = {
            'time_series': TimeSeriesRenderer(),
            'scatter': ScatterRenderer(), 
            'spectral': SpectralRenderer()
        }
    
    def render_to(self, ax):
        """Render time series to specified axes"""
        for var in self.prepared_variables:
            handler = self.plot_type_handlers[var.plot_type]
            handler.render(ax, var, self.data[var])
```

#### VDFPlot  
```python
class VDFPlot(PlotComponent):
    def __init__(self, time, vdf_config=None):
        self.time = time
        self.vdf_config = vdf_config or VDFConfig()
    
    def render_theta_plane(self, ax):
        """Render VDF theta plane to specific axes"""
        pass
    
    def render_phi_plane(self, ax):
        """Render VDF phi plane to specific axes"""
        pass
    
    def render_collapsed(self, ax):
        """Render collapsed VDF to specific axes"""
        pass
```

#### EncounterPlot
```python
class EncounterPlot(PlotComponent):
    def __init__(self, encounter_time, variable, window='4h', position='around'):
        # Calculate encounter-specific time range
        self.trange = self._calculate_encounter_range(encounter_time, window, position)
        super().__init__(self.trange, [variable])
        self.encounter_time = encounter_time
    
    def _calculate_encounter_range(self, center_time, window, position):
        """Handle encounter-specific time range calculation"""
        # Preserve multiplot's sophisticated time range logic
        pass
```

### 3. **Data Acquisition Manager**
```python
class DataAcquisitionManager:
    @staticmethod
    def handle_custom_variables(variables, trange):
        """Extract common custom variable pattern from all functions"""
        custom_vars = []
        for var in variables:
            if var.data_type == 'custom_data_type':
                # Handle source variable downloading
                if hasattr(var, 'source_var') and var.source_var:
                    base_vars = [src for src in var.source_var 
                               if src.data_type != 'custom_data_type']
                    if base_vars:
                        get_data(trange, *base_vars)
                
                # Update custom variable
                if hasattr(var, 'update'):
                    var.update(trange)
                custom_vars.append(var)
        return custom_vars
    
    @staticmethod
    def load_regular_variables(variables, trange):
        """Centralize get_data() calls for regular variables"""
        regular_vars = [var for var in variables 
                       if var.data_type != 'custom_data_type']
        if regular_vars:
            get_data(trange, *regular_vars)
        return regular_vars
```

### 4. **Plot Type Renderers**
```python
class PlotTypeRenderer:
    def validate_data(self, var, trange):
        """Common validation patterns"""
        if var.datetime_array is None or len(var.datetime_array) == 0:
            raise ValueError(f"No datetime array for {var.class_name}.{var.subclass_name}")
        
        indices = time_clip(var.datetime_array, trange[0], trange[1])
        if len(indices) == 0:
            raise ValueError(f"No data in time range for {var.class_name}.{var.subclass_name}")
        
        return indices
    
    def render(self, ax, var, indices):
        raise NotImplementedError

class TimeSeriesRenderer(PlotTypeRenderer):
    def render(self, ax, var, indices):
        """Extract time series plotting logic from plotbot_main"""
        datetime_clipped = var.datetime_array[indices]
        data_clipped = var.all_data[indices]
        
        if var.all_data.ndim == 1:
            ax.plot(datetime_clipped, data_clipped,
                   label=var.legend_label, color=var.color,
                   linewidth=var.line_width, linestyle=var.line_style)
        else:
            # Handle vector quantities
            for i in range(data_clipped.shape[0]):
                ax.plot(datetime_clipped, data_clipped[i],
                       label=var.legend_label[i] if isinstance(var.legend_label, list) else var.legend_label,
                       color=var.color[i] if isinstance(var.color, list) else var.color)
        
        ax.set_ylabel(var.y_label)
        ax.set_yscale(var.y_scale)

class SpectralRenderer(PlotTypeRenderer):
    def render(self, ax, var, indices):
        """Extract spectral plotting logic from plotbot_main"""
        # Handle pcolormesh, colorbar creation, etc.
        pass
```

## 🔄 Migration Strategy

### Phase 1: Extract Plot Type System (Weeks 1-3)
1. **Week 1**: Create base PlotTypeRenderer classes
   - Extract validation patterns
   - Create TimeSeriesRenderer, ScatterRenderer, SpectralRenderer
   - Update plotbot_main.py to use renderer system

2. **Week 2**: Create DataAcquisitionManager
   - Extract custom variable handling pattern
   - Extract regular variable loading pattern
   - Update all three main functions to use unified manager

3. **Week 3**: Create common utilities
   - Extract time validation and parsing
   - Extract axis formatting functions
   - Create plotting_utils.py module

### Phase 2: Modular Components (Weeks 4-6)
1. **Week 4**: Create PlotComponent base class and TimeSeriesPlot
   - Implement prepare() and render_to() pattern
   - Test with simple time series cases

2. **Week 5**: Create specialized components
   - VDFPlot component with render_theta_plane(), render_phi_plane(), render_collapsed()
   - EncounterPlot component with encounter time range logic
   - HodogramPlot component

3. **Week 6**: Integration and testing
   - Test mixed plot type compositions
   - Performance benchmarking
   - Regression testing against existing functionality

### Phase 3: Advanced Features (Weeks 7-9)
1. **Week 7**: Multiplot refactor
   - Break multiplot() into 5 focused functions using component system
   - Preserve all sophisticated positional coordinate logic
   - Test encounter analysis workflows

2. **Week 8**: Configuration system
   - PlotConfiguration class for options management
   - ColorSchemeManager for rainbow/single-color modes
   - Preset system integration

3. **Week 9**: Documentation and polish
   - Update examples to show compositional patterns
   - Performance optimization
   - Comprehensive testing

## 💪 Benefits of Modular Architecture

### For Users
- **Flexible Composition**: Mix any plot types in any arrangement
- **Familiar Syntax**: Leverages matplotlib patterns users already know
- **Preserved Intelligence**: All space physics domain knowledge retained
- **Backward Compatibility**: Existing functions continue to work

### For Developers  
- **Testable Components**: Individual plot types can be unit tested
- **Reusable Logic**: Common patterns extracted and shared
- **Clear Separation**: Data, styling, and rendering concerns separated
- **Extensible**: New plot types can be added through clean interfaces

### For Maintenance
- **Smaller Functions**: Replace 2,288-line function with focused components
- **Isolated Changes**: Updates to one plot type don't affect others
- **Easier Debugging**: Clear boundaries between components
- **Performance Optimization**: Components can be optimized individually

## 🎯 Success Metrics

### Technical
- [ ] Functions under 200 lines each
- [ ] 90%+ test coverage on plot components
- [ ] No performance regression vs current implementation
- [ ] All existing examples work unchanged

### User Experience
- [ ] New composition examples documented
- [ ] Mixed plot type capabilities demonstrated
- [ ] VDF + time series integration working seamlessly
- [ ] Encounter analysis workflows preserved

### Maintainability
- [ ] Clear component boundaries established
- [ ] Shared utilities extracted and tested
- [ ] Domain logic separated from plotting mechanics
- [ ] Extension points for new plot types defined

## 🚀 Long-term Vision

This modular architecture enables:

1. **Plugin System**: Community-contributed plot types
2. **Interactive Components**: Web-based plotting with same components
3. **Automated Layouts**: AI-assisted plot arrangement based on data types
4. **Cross-Mission Support**: Easy extension to other space physics missions
5. **Export Flexibility**: Components can render to different backends (matplotlib, plotly, etc.)

The modular approach preserves Plotbot's sophisticated space physics intelligence while enabling unprecedented flexibility in plot composition and maintenance.
