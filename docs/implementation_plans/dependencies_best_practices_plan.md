# Plotbot Dependencies Best Practices Plan

*AI-Optimized Guide for Implementing Variables with Dependencies*

## Executive Summary

This document provides a systematic approach for implementing variables that depend on data from other sources in Plotbot, based on lessons learned from the `br_norm` implementation. The core principle is ensuring dependencies use the exact same time range as the user's original request through a "sticky note" system.

## Problem Definition

### The br_norm Time Range Issue

**Problem**: Dependencies were using incorrect time ranges, causing:
- Loading unnecessary data for broader merged time ranges
- Performance degradation
- Stale or incorrect dependency data
- Data contamination between sequential requests

**Root Cause**: Broken information chain where the user's original time range wasn't passed to dependency calculation methods.

**Before Fix Flow**:
```
plotbot(trange, mag_rtn_4sa.br_norm) 
→ get_data(trange, mag_rtn_4sa) 
→ data_cubby.update_global_instance() [trange NOT passed]
→ mag_rtn_4sa.update() [no trange knowledge]
→ br_norm property accessed
→ _calculate_br_norm() [uses merged datetime_array for dependency trange]
→ get_data(wide_merged_range, proton.sun_dist_rsun) [WRONG RANGE]
```

## Solution Architecture: The "Sticky Note" System

### Core Concept
Pass the original user time range (`original_requested_trange`) through every step of the data pipeline:

**Fixed Flow**:
```
plotbot(trange, mag_rtn_4sa.br_norm) 
→ get_data(trange, mag_rtn_4sa) 
→ data_cubby.update_global_instance(original_requested_trange=trange)
→ mag_rtn_4sa.update(original_requested_trange=trange)
→ store as _current_operation_trange
→ br_norm property accessed
→ _calculate_br_norm() [uses _current_operation_trange]
→ get_data(exact_user_trange, proton.sun_dist_rsun) [CORRECT RANGE]
```

## Implementation Patterns

### Pattern 1: Data Class Initialization
```python
def __init__(self, imported_data):
    object.__setattr__(self, '_current_operation_trange', None)
    # ... other initialization
```

### Pattern 2: Update Method Signature
```python
def update(self, imported_data, original_requested_trange: Optional[List[str]] = None):
    # Store the trange for dependency calculations
    object.__setattr__(self, '_current_operation_trange', original_requested_trange)
    
    if original_requested_trange:
        print_manager.dependency_management(f"Stored _current_operation_trange: {self._current_operation_trange}")
    
    # Continue with update logic...
```

### Pattern 3: Dependency Calculation Template
```python
def _calculate_dependent_variable(self):
    """Template for dependency calculations."""
    # CRITICAL: Check for stored operation trange
    trange_for_dependencies = None
    if hasattr(self, '_current_operation_trange') and self._current_operation_trange is not None:
        trange_for_dependencies = self._current_operation_trange
        print_manager.dependency_management(f"Using _current_operation_trange: {trange_for_dependencies}")
    else:
        print_manager.error("Cannot determine time range for dependencies: _current_operation_trange is None")
        self.raw_data['dependent_var'] = None
        return False
    
    # Fetch dependencies with correct time range
    get_data(trange_for_dependencies, dependency_source)
    
    # Validation
    if not dependency_source.data or len(dependency_source.data) == 0:
        print_manager.error(f"Dependency data unavailable for trange {trange_for_dependencies}")
        self.raw_data['dependent_var'] = None
        return False
    
    # Perform calculation
    result = perform_calculation(self.raw_data['base_var'], dependency_source.data)
    self.raw_data['dependent_var'] = result
    
    return True
```

### Pattern 4: Property-Based Lazy Loading
```python
@property
def dependent_variable(self):
    """Property for dependent variable with lazy loading."""
    if not hasattr(self, '_dependent_var_manager'):
        # Create placeholder manager
        self._dependent_var_manager = plot_manager(
            np.array([]),
            plot_options=ploptions(...)
        )
    
    # Check if calculation is needed
    if self.raw_data.get('dependent_var') is None:
        success = self._calculate_dependent_variable()
        if success and self.raw_data.get('dependent_var') is not None:
            # Update manager with calculated data
            self._dependent_var_manager = plot_manager(
                self.raw_data['dependent_var'],
                plot_options=self._dependent_var_manager.plot_options
            )
    
    return self._dependent_var_manager
```

### Pattern 5: Data Cubby Integration
```python
# In data_cubby.py update_global_instance method
try:
    # Try new signature with original_requested_trange
    global_instance.update(imported_data_obj, original_requested_trange=original_requested_trange)
    print_manager.datacubby(f"Successfully called update() with original_requested_trange")
except TypeError as te:
    # Fall back to old signature for backward compatibility
    if "unexpected keyword argument" in str(te) or "takes" in str(te):
        print_manager.datacubby(f"Falling back to simple update() signature")
        global_instance.update(imported_data_obj)
    else:
        raise te
```

## Specific Use Cases

### Use Case 1: Single-Source Dependencies (br_norm pattern)
For variables requiring one external dependency:
- Store `_current_operation_trange` in update()
- Use stored trange in calculation method
- Validate dependency data before calculation
- Handle graceful failure with proper logging

### Use Case 2: Multi-Source Dependencies (Alfvén speed pattern)
For variables requiring multiple external dependencies:
```python
def _calculate_alfven_speed(self):
    trange = self._current_operation_trange
    if not trange:
        return False
    
    # Fetch all required dependencies
    get_data(trange, mag_field_source)
    get_data(trange, proton_density_source)
    get_data(trange, alpha_density_source)
    
    # Validate all dependencies
    required_data = [mag_field_source.data, proton_density_source.data, alpha_density_source.data]
    if not all(data is not None and len(data) > 0 for data in required_data):
        print_manager.error("Missing required dependency data for Alfvén speed calculation")
        return False
    
    # Calculate with interpolation if needed
    # ... implementation
    return True
```

### Use Case 3: Cross-Satellite Dependencies (drift speed pattern)
For variables requiring data from different satellites:
```python
def _calculate_drift_speed(self):
    trange = self._current_operation_trange
    
    # Fetch velocity data from different satellites/instruments
    get_data(trange, alpha_velocity_source)
    get_data(trange, proton_velocity_source)
    
    # Handle different cadences with interpolation
    # ... implementation with time alignment
    return True
```

## Required Code Modifications

### Files That Must Be Modified:
1. **All data class files** (`plotbot/data_classes/*.py`):
   - Add `_current_operation_trange = None` in `__init__`
   - Update `update()` method signature
   - Store `original_requested_trange` as `_current_operation_trange`

2. **Dependency calculation methods**:
   - Check for `_current_operation_trange` existence
   - Use `_current_operation_trange` for `get_data` calls
   - Remove fallback to `self.datetime_array` for dependency trange
   - Add error handling for missing trange

3. **data_cubby.py**:
   - Ensure `update_global_instance` passes `original_requested_trange`
   - Add try-except for backward compatibility

4. **Type hint files** (`.pyi` files):
   - Add `_current_operation_trange: Optional[List[str]]`
   - Update method signatures

### Critical Implementation Points:

1. **Strict Trange Enforcement**: Remove fallback mechanisms that use merged datetime arrays
2. **Error Handling**: Gracefully handle missing trange or dependency data
3. **Logging**: Comprehensive logging for debugging dependency issues
4. **Backward Compatibility**: Support classes not yet updated with try-except blocks

## Testing Strategy

### Required Test Categories:

1. **Trange Accuracy Tests**:
```python
def test_dependency_uses_exact_trange():
    with patch('plotbot.get_data') as mock_get_data:
        captured_trange = []
        mock_get_data.side_effect = lambda trange, *args: captured_trange.append(trange.copy())
        
        specific_trange = ['2023-09-28/00:00:00.000', '2023-09-28/23:59:59.999']
        plotbot(specific_trange, mag_rtn_4sa.br_norm)
        
        assert captured_trange[-1] == specific_trange
```

2. **Sequential Request Tests**:
```python
def test_no_data_contamination():
    # Request 1
    trange1 = ['2023-09-26/00:00:00.000', '2023-09-26/23:59:59.999']
    result1 = plotbot(trange1, mag_rtn_4sa.br_norm)
    
    # Request 2 - different range
    trange2 = ['2023-09-28/00:00:00.000', '2023-09-28/23:59:59.999']
    result2 = plotbot(trange2, mag_rtn_4sa.br_norm)
    
    # Verify no contamination
    assert result1 != result2  # Should be different data
```

3. **Lazy Loading Tests**:
```python
def test_lazy_loading_behavior():
    # Verify calculation only happens when accessed
    # Verify multiple accesses don't recalculate
    # Verify proper cache invalidation on update
```

4. **Error Handling Tests**:
```python
def test_graceful_dependency_failure():
    # Test behavior when dependency data unavailable
    # Test behavior when trange is None
    # Test behavior when interpolation fails
```

## Common Issues & Solutions

### Issue 1: `_current_operation_trange` is None
**Cause**: Time range not passed through pipeline
**Solution**: Check `data_cubby.update_global_instance` implementation

### Issue 2: Dependencies loading too much data
**Cause**: Still using fallback logic
**Solution**: Remove fallback to `self.datetime_array`

### Issue 3: TypeError on update method
**Cause**: Class not updated for new signature
**Solution**: Add try-except in data_cubby

### Issue 4: Stale dependency data
**Cause**: Dependencies not re-fetched for new trange
**Solution**: Clear cached data on update

## Performance Considerations

1. **Lazy Loading**: Only calculate dependencies when actually needed
2. **Caching**: Cache results but invalidate on time range changes
3. **Interpolation**: Optimize interpolation algorithms for large datasets
4. **Parallel Fetching**: Consider fetching multiple dependencies in parallel

## Future Extensions

### For Alfvén Speed Implementation:
```python
def _calculate_alfven_speed(self):
    trange = self._current_operation_trange
    if not trange:
        return False
    
    # Multi-source dependency pattern
    dependencies = {
        'mag_field': alpha_data.mag_field,
        'proton_density': proton_data.density,
        'alpha_density': alpha_data.density
    }
    
    # Fetch all dependencies
    for source in dependencies.values():
        get_data(trange, source)
    
    # Validate and calculate
    # ... implementation
```

### For Alpha/Proton Ratio:
```python
def _calculate_density_ratio(self):
    # Handle different cadences
    # Implement proper interpolation
    # Consider error propagation
```

### For Drift Speed:
```python
def _calculate_drift_speed(self):
    # Vector mathematics
    # Multi-dimensional interpolation
    # Handle coordinate system differences
```

## Implementation Checklist

- [ ] Add `_current_operation_trange` to all data classes
- [ ] Update all `update()` method signatures
- [ ] Modify dependency calculation methods
- [ ] Update data_cubby integration
- [ ] Add comprehensive error handling
- [ ] Remove fallback mechanisms
- [ ] Update type hints and documentation
- [ ] Implement test suites
- [ ] Verify backward compatibility
- [ ] Performance testing with large datasets

## Success Metrics

1. **Performance**: Dependencies load only requested time range data
2. **Accuracy**: No data contamination between requests
3. **Reliability**: Graceful handling of missing dependencies
4. **Maintainability**: Clear patterns for new dependency implementations

This plan provides the foundation for implementing any variable with dependencies in Plotbot, ensuring correct time range handling and optimal performance. 