# Modular Planning Architecture Complexity

## 🎯 The Core Challenge

We want to add modularity to Plotbot without breaking its fundamental elegance. The tension is between **preserving simple syntax** for common cases while **enabling complex composition** for advanced use cases.

## 💔 **The Elegance Problem**

### Current Beautiful Syntax
```python
plotbot(trange, var1, var2, var3)  # Three panels, automatic - ELEGANT
```

### Initial Modular Proposal (TERRIBLE)
```python
fig, axes = plt.subplots(3, 1, sharex=True, figsize=(12, 8))
TimeSeriesPlot(trange, var1).render_to(axes[0])
TimeSeriesPlot(trange, var2).render_to(axes[1])  
TimeSeriesPlot(trange, var3).render_to(axes[2])
```

**Problem**: Made the common case 5x more verbose to solve edge cases. Classic architecture mistake.

## 🤔 **Integration Reality Check**

### The Real Use Case
```python
# VDF at top, time series below in a REAL matplotlib grid
fig = plt.figure()
gs = gridspec.GridSpec(4, 2, height_ratios=[1, 1, 1, 0.8])

# How do we elegantly fill specific grid positions?
# VDF panels (top row)
??? # Need VDF components in gs[0, 0], gs[0, 1]

# Time series below  
??? # Need plotbot elegance in gs[1, :], gs[2, :]
```

### Composer Abstraction Issues
```python
# This doesn't actually integrate with matplotlib gridspec
composer = PlotComposer()
composer.add_vdf(time)
composer.add_timeseries(trange, [var1, var2])
fig = composer.render()  # How does this respect existing grid layouts?
```

**Problem**: Creating another abstraction layer that doesn't play nicely with matplotlib's proven grid system.

## 💡 **Axes-Aware Approach**

### Core Insight
Make existing functions **axes-aware** rather than creating new composition abstractions.

### Proposed Implementation
```python
# Simple case - unchanged, creates own figure
plotbot(trange, var1, var2, var3)

# Grid composition - pass existing axes  
fig = plt.figure()
gs = gridspec.GridSpec(4, 2, height_ratios=[1, 1, 1, 0.8])

# VDF in top positions
vdyes(time, axes=[fig.add_subplot(gs[0, 0]),  # theta plane
                  fig.add_subplot(gs[0, 1]),  # phi plane  
                  fig.add_subplot(gs[0, 2])])  # collapsed

# Time series in bottom positions  
plotbot(trange, var1, var2, axes=[fig.add_subplot(gs[1, :]), 
                                  fig.add_subplot(gs[2, :])])
```

### Function Signature Changes
```python
def plotbot(trange, *args, axes=None, **kwargs):
    """
    If axes=None: Create figure automatically (current behavior)
    If axes=list: Render to provided axes instead
    """
    
def vdyes(time_or_trange, axes=None, **kwargs):
    """
    If axes=None: Create figure with 3 panels automatically  
    If axes=list: Render theta/phi/collapsed to provided axes
    """
    
def multiplot(plot_list, axes=None, **kwargs):
    """
    If axes=None: Create figure with N panels automatically
    If axes=list: Render each encounter to provided axes
    """
```

## ✅ **Benefits of Axes-Aware Approach**

1. **Preserves Elegance**: Simple cases unchanged
2. **Leverages Matplotlib**: Uses proven gridspec system
3. **No New Abstractions**: Builds on existing patterns
4. **Gradual Migration**: Can be implemented incrementally
5. **Flexible Composition**: Any function can go anywhere in grid

## 🔄 **Implementation Strategy**

### Phase 1: Add Axes Parameter (Weeks 1-2)
```python
def plotbot(trange, *args, axes=None, **kwargs):
    if axes is None:
        # Current behavior - create figure automatically
        fig, axes = plt.subplots(num_panels, 1, sharex=True)
    else:
        # New behavior - use provided axes
        fig = axes[0].get_figure()
    
    # Rest of function unchanged - plot to axes array
    for i, (var, axis_spec) in enumerate(parsed_args):
        # Plot to axes[i] instead of axs[i]
```

### Phase 2: Extend to Other Functions (Weeks 3-4)
```python
def vdyes(time_or_trange, axes=None, **kwargs):
    if axes is None:
        # Current behavior - create 3-panel figure
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    else:
        # New behavior - use provided axes
        if len(axes) != 3:
            raise ValueError("vdyes requires exactly 3 axes for theta/phi/collapsed")
        fig = axes[0].get_figure()
    
    # Render to specific axes
    render_theta_plane(axes[0], vdf_data)
    render_phi_plane(axes[1], vdf_data)  
    render_collapsed(axes[2], vdf_data)
```

### Phase 3: Advanced Grid Patterns (Weeks 5-6)
```python
# Enable complex layouts
def create_space_physics_layout():
    """Create common space physics grid layouts"""
    fig = plt.figure(figsize=(16, 12))
    
    # VDF + time series layout
    gs = gridspec.GridSpec(4, 3, height_ratios=[1, 1, 1, 0.8])
    
    vdf_axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    ts_axes = [fig.add_subplot(gs[i, :]) for i in range(1, 4)]
    
    return fig, {'vdf': vdf_axes, 'timeseries': ts_axes}

# Usage
fig, layout = create_space_physics_layout()
vdyes(time, axes=layout['vdf'])
plotbot(trange, var1, var2, axes=layout['timeseries'][:2])
```

## 🎯 **Key Design Principles**

1. **Backward Compatibility**: All existing code continues to work
2. **Optional Complexity**: Advanced features are opt-in
3. **Matplotlib Native**: Leverage existing, proven layout systems
4. **Incremental Adoption**: Can migrate functions one at a time
5. **Clear Boundaries**: Each function handles its own data/styling

## 🚧 **Implementation Challenges**

### 1. Axis Count Validation
```python
# How do we handle mismatched axes counts?
plotbot(trange, var1, var2, var3, axes=[ax1, ax2])  # 3 vars, 2 axes?

# Options:
# A) Error immediately
# B) Auto-create additional axes
# C) Combine variables on available axes
```

### 2. Shared Axis Properties
```python
# Current plotbot shares x-axis automatically
fig, axs = plt.subplots(3, 1, sharex=True)

# With provided axes, how do we handle sharing?
plotbot(trange, var1, var2, var3, axes=[ax1, ax2, ax3])  # These might not be shared
```

### 3. Figure-Level Properties
```python
# Current functions set figure titles, adjust layouts
fig.suptitle("Multi-Panel Analysis")
plt.tight_layout()

# With provided axes, who owns figure-level settings?
```

## 💭 **Open Questions**

1. **Should axes parameter accept single axis for single-variable plots?**
   ```python
   plotbot(trange, var1, axes=ax)  # Single axis
   plotbot(trange, var1, var2, axes=[ax1, ax2])  # Multiple axes
   ```

2. **How do we handle figure return values?**
   ```python
   # Current
   fig = plotbot(trange, var1, var2)  # Returns figure
   
   # With provided axes  
   result = plotbot(trange, var1, var2, axes=[ax1, ax2])  # Return what?
   ```

3. **Should we extract common gridspec patterns?**
   ```python
   # Helper functions for common layouts?
   axes = create_vdf_timeseries_layout()
   axes = create_encounter_comparison_layout(n_encounters=5)
   ```

## 🎯 **Success Criteria**

- [ ] All existing plotbot calls work unchanged
- [ ] VDF + time series composition works elegantly
- [ ] Multiplot encounter logic preserved with axes parameter
- [ ] No performance regression
- [ ] Clear documentation for new axes parameter
- [ ] Examples showing complex grid compositions

## 🚀 **Next Steps**

1. **Prototype axes parameter in plotbot_main.py**
2. **Test with simple VDF + time series composition**
3. **Identify edge cases and design solutions**
4. **Extend to vdyes and multiplot**
5. **Create example gallery of grid compositions**

This approach maintains Plotbot's elegance while enabling the modular composition we need for complex space physics analysis workflows.

