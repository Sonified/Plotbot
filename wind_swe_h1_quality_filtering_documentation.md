# WIND SWE H1 Data Quality Filtering Implementation

## Overview

This document describes the data quality filtering implemented for WIND Solar Wind Experiment (SWE) H1 proton/alpha thermal speed data in Plotbot. This represents a **major departure** from Plotbot's normal "take data and plot it" philosophy.

## Why Quality Filtering is Necessary

### The Problem
WIND SWE H1 thermal speed data contains significant quality issues that make raw data scientifically misleading:

1. **Alpha thermal speeds are 100% fill values**: All measurements are 99,999.9 km/s (3x the speed of light!)
2. **Proton thermal speeds contain fill values**: Data jumps between realistic ~50 km/s and unphysical ~100,000 km/s
3. **Quality flags indicate poor fits**: `fit_flag=10` represents worst quality data (36% of all measurements)

### Real Data Analysis (2022-06-01, 817 measurements)
```
fit_flag distribution: {0: 2, 1: 84, 2: 130, 3: 230, 5: 23, 6: 54, 10: 294}
Alpha_W: 100% fill values (99,999.9 km/s)
Proton speeds: 29 measurements > 1000 km/s (clearly unphysical)
```

Without filtering, plots show meaningless jumps between ~50 km/s and 100,000 km/s, making scientific interpretation impossible.

## Filtering Implementation

### 1. Quality Flag Filtering
```python
# *** ADJUSTABLE PARAMETER: fit_flag_threshold ***
fit_flag_threshold = 6  # Accept fit_flag 0-6, reject 10. Change to 3 for stricter filtering.

quality_mask = (fit_flag_data <= fit_flag_threshold)
```

**Quality Flag Meanings:**
- `fit_flag 0-1`: Best quality (very rare: only 2-84 points per day)
- `fit_flag 2-3`: Good quality (most reliable data)  
- `fit_flag 5-6`: Moderate quality (acceptable for science)
- `fit_flag 10`: Worst quality (36% of data, often but not always bad)

**Recommendation**: Use `fit_flag_threshold = 6` for general use, `= 3` for high-quality analysis only.

### 2. Physical Limits Filtering
```python
# *** ADJUSTABLE PARAMETERS: thermal_speed_min, thermal_speed_max ***
thermal_speed_min = 5.0    # km/s - Minimum realistic thermal speed. Increase to 10.0 for stricter filtering.
thermal_speed_max = 1000.0 # km/s - Maximum realistic thermal speed. Decrease to 200.0 for stricter filtering.

physical_mask = (thermal_speed >= thermal_speed_min) & (thermal_speed < thermal_speed_max)
```

**Physical Justification:**
- Typical proton thermal speeds in solar wind: 10-100 km/s
- Fill values in WIND data: 99,999.9 km/s (clearly unphysical)
- Very low values (< 5 km/s): likely instrumental issues

**Recommendations:**
- Conservative filtering: `min=5.0, max=1000.0 km/s`
- Strict filtering: `min=10.0, max=200.0 km/s`

### 3. Alpha Particle Special Handling
```python
# *** ADJUSTABLE PARAMETER: fill_value_threshold ***
fill_value_threshold = 0.9  # Fraction of fill values to trigger complete rejection. Lower to 0.5 for less strict.

fill_mask = np.abs(alpha_w_data - 99999.9) < 0.1
fill_fraction = np.sum(fill_mask) / len(alpha_w_data)

if fill_fraction > fill_value_threshold:
    alpha_w_data = np.full_like(alpha_w_data, np.nan)  # Set all to NaN
```

**Alpha Data Status**: Currently (2022) all alpha thermal speeds are fill values. This may change in different time periods or future data versions.

## Implementation Details

### Data Preservation Strategy
- **Time grid preserved**: Bad data replaced with `NaN`, not removed
- **Transparency maintained**: All filtering steps logged with counts
- **Reversible**: Raw data untouched, filtering applied during processing

### Filtering Combination
```python
# Combine quality flag and physical limits
if quality_mask is not None:
    combined_mask = quality_mask & physical_mask
else:
    combined_mask = physical_mask

# Apply filtering: replace bad data with NaN
filtered_data = np.where(combined_mask, raw_data, np.nan)
```

## Results

### Before Filtering
- Thermal speeds: Jump between ~50 km/s and 100,000 km/s
- Alpha speeds: Constant 99,999.9 km/s (meaningless)
- Scientific interpretation: Impossible

### After Filtering
- Proton parallel: ~22-65 km/s (physically reasonable)
- Proton perpendicular: ~25-75 km/s (physically reasonable)  
- Proton anisotropy: ~0.8-1.5 (typical solar wind values)
- Alpha speeds: All NaN (honest representation of no data)

## Adjustable Parameters Summary

| Parameter | Default | Purpose | Adjust for |
|-----------|---------|---------|------------|
| `fit_flag_threshold` | 6 | Quality flag cutoff | Stricter: 3, Looser: 10 |
| `thermal_speed_min` | 5.0 km/s | Minimum physical speed | Conservative: 10.0 |
| `thermal_speed_max` | 1000.0 km/s | Maximum physical speed | Strict: 200.0 |
| `fill_value_threshold` | 0.9 | Alpha fill value fraction | Less strict: 0.5 |

## Scientific Impact

This filtering transforms WIND SWE H1 data from scientifically misleading to scientifically useful while maintaining complete transparency about what data was excluded and why.

The implementation preserves Plotbot's philosophy of data transparency while acknowledging that some datasets require quality filtering to be scientifically meaningful.

---
*Implementation: WIND SWE H1 class in plotbot/data_classes/wind_swe_h1_classes.py*  
*Contact: [Your contact info here]* 