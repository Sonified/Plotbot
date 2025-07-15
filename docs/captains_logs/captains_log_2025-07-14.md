# Captain's Log - 2025-07-14

## Major Fix: Custom Variables Scalar Operations

### Problem Identified
Custom variables system was failing for scalar operations like `proton.anisotropy + 10`. The issue was traced to the update method in `plotbot/data_classes/custom_variables.py` which incorrectly expected 2 source variables for ALL operations.

**Debug Evidence:**
- `[MATH] Error during scalar add: unsupported operand type(s) for +: 'NoneType' and 'int'`
- `Not enough fresh sources for anisotropy_plus_ten`
- Custom variables would create but not plot any data

### Root Cause Analysis
The custom variables update method had three critical flaws:

1. **Incorrect source count validation**: Line 185 checked `if len(fresh_sources) < 2:` for all operations
2. **Wrong operation application**: Always tried to access `fresh_sources[1]` even for scalar operations  
3. **Faulty time range validation**: Assumed 2 sources for all data coverage checks

### Solution Implemented
Modified `plotbot/data_classes/custom_variables.py` to distinguish between scalar and binary operations:

**Key Changes:**
- **Smart source detection**: `expected_sources = 1 if operation in ['add', 'sub', 'mul', 'div'] and hasattr(variable, 'scalar_value') else 2`
- **Conditional operation handling**: Separate logic paths for scalar vs binary operations
- **Proper data validation**: Only check required number of sources for time range coverage

### Testing Results
Created comprehensive test suite `tests/test_custom_variables_working.py` with 6 test cases:

✅ **All 6 Tests PASSED:**
1. Simple scalar addition (`proton.anisotropy + 10`)
2. Variable division (`proton.anisotropy / mag_rtn_4sa.bmag`)
3. Complex chained expressions
4. Global accessibility verification
5. Time range adaptation
6. Comprehensive integration

### Debug Output Validation
**Before Fix:**
```
[MATH] Error during scalar add: unsupported operand type(s) for +: 'NoneType' and 'int'
Not enough fresh sources for anisotropy_plus_ten
```

**After Fix:**
```
Applying scalar operation: add with scalar value 10
Source 1 has 3090 data points in requested time range
Result has 3090 data points in requested time range
📈 Plotting custom_class.anisotropy_plus_ten
```

### Impact
- **Scalar operations now work**: `custom_variable('name', proton.anisotropy + 10)`
- **Binary operations preserved**: Division, multiplication still function correctly
- **Full plotting integration**: Variables display properly in plotbot and multiplot
- **Time range flexibility**: Updates correctly for different time ranges
- **Global accessibility**: Variables available as `plotbot.variable_name`

### Technical Achievement
This fix enables the elegant custom variable syntax originally intended:
```python
custom_variable('anisotropy_plus_ten', proton.anisotropy + 10)
custom_variable('ratio_var', proton.anisotropy / mag_rtn_4sa.bmag)
```

Both scalar and binary operations now work seamlessly with proper data handling, interpolation, and plotting integration.

---

## Version: v2.86
- **Commit Message**: "v2.86 CUSTOM VARIABLES FIX: Scalar operations now work - enables proton.anisotropy + 10 syntax"
- **Files Modified**: 
  - `plotbot/data_classes/custom_variables.py` - Fixed scalar operation handling
  - `tests/test_custom_variables_working.py` - Added comprehensive test suite
  - `plotbot/__init__.py` - Updated version and commit message
- **Achievement**: Custom variables now support both scalar and binary operations with proper plotting integration
- **Reality Check**: FULLY FUNCTIONAL - all 6 test cases pass, elegant syntax works as intended
- **Status**: Ready for deployment with complete custom variables functionality 