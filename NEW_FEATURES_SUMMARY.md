# New Features Summary: r_hand_single_color & HAM Bar Width Fix

## Overview
Two new features were added to Plotbot:
1. **`r_hand_single_color`** - Option to specify a single color for right axis elements in rainbow mode
2. **HAM Bar Width Fix** - Improved bar width calculation for sparse HAM data

---

## Feature 1: `r_hand_single_color` Option

### Purpose
Allows users to specify a single hex color for all right axis elements (labels, ticks, spines, plot data) when using rainbow mode, instead of using the panel's rainbow color.

### Code Locations

#### 1. Property Definition (`plotbot/multiplot_options.py`)

**Location:** Lines 317, 873-880

```python
# In reset() method (line 317):
self.r_hand_single_color = None  # New: Single color for right axis in rainbow mode (hex color string)

# Property definition (lines 873-880):
@property
def r_hand_single_color(self) -> Optional[str]:
    """Single color for right axis elements in rainbow mode (hex color string, e.g., '#FF0000')."""
    return self.__dict__.get('r_hand_single_color', None)

@r_hand_single_color.setter
def r_hand_single_color(self, value: Optional[str]):
    self.__dict__['r_hand_single_color'] = value
```

#### 2. Right Axis Color Logic (`plotbot/multiplot.py`)

**Location:** Lines 664-669

```python
# Determine right axis color: use r_hand_single_color if set in rainbow mode, otherwise use panel_color
right_axis_color = None
if options.color_mode == 'rainbow' and hasattr(options, 'r_hand_single_color') and options.r_hand_single_color is not None:
    right_axis_color = options.r_hand_single_color
elif panel_color is not None:
    right_axis_color = panel_color
```

#### 3. HAM Data Plot Color (`plotbot/multiplot.py`)

**Location:** Lines 1749-1756

```python
# Get color - use r_hand_single_color if set in rainbow mode, otherwise panel color, right axis color, or ham_var's color
if options.color_mode == 'rainbow' and hasattr(options, 'r_hand_single_color') and options.r_hand_single_color is not None:
    plot_color = options.r_hand_single_color
elif panel_color is not None:
    plot_color = panel_color
elif hasattr(axis_options, 'r') and axis_options.r.color is not None:
    plot_color = axis_options.r.color
else:
    plot_color = ham_var.color
```

#### 4. Non-HAM Right Axis Plot Color (`plotbot/multiplot.py`)

**Location:** Lines 851-852

```python
if options.color_mode == 'rainbow' and hasattr(options, 'r_hand_single_color') and options.r_hand_single_color is not None:
    plot_color = options.r_hand_single_color
```

#### 5. Right Axis Element Styling (`plotbot/multiplot.py`)

**Location:** Lines 820-831, 844-847, 1854-1865

```python
# Applied in multiple locations for:
# - Y-axis label color
# - Y-axis tick colors
# - Spine colors

if right_axis_color is not None:
    # Set y-axis label color and font weight
    ax2.yaxis.label.set_color(right_axis_color)
    if hasattr(options, 'bold_y_axis_label') and options.bold_y_axis_label:
        ax2.yaxis.label.set_weight('bold')
    else:
        ax2.yaxis.label.set_weight('normal')
    # Set tick color and label size
    ax2.tick_params(axis='y', colors=right_axis_color, which='both', labelsize=options.y_tick_label_font_size)
    # Set all spines to right axis color
    for spine in ax2.spines.values():
        spine.set_color(right_axis_color)
```

### Usage Example

```python
from plotbot import *

plt.options.reset()
plt.options.color_mode = 'rainbow'
plt.options.hamify = True
plt.options.ham_var = ham.n_ham
plt.options.ham_opacity = 0.2

# NEW: Set single color for right axis in rainbow mode
plt.options.r_hand_single_color = '#363737'  # Very dark grey
# Or use matplotlib color names:
# plt.options.r_hand_single_color = 'dimgrey'  # #696969
# plt.options.r_hand_single_color = '#A9A9A9'  # Lighter dark grey

plot_data = [('2022-02-27/05:32:33.000', mag_rtn_4sa.br)]
multiplot(plot_data)
```

---

## Feature 2: HAM Bar Width Fix

### Purpose
Fixes inconsistent bar widths when HAM data is sparse. Previously, bars could become extremely wide (1.5-2 hours) when there were few data points. Now uses robust calculation with reasonable bounds.

### Code Location

**File:** `plotbot/multiplot.py`  
**Location:** Lines 1811-1827

```python
# Calculate bar width based on data spacing with robust handling for sparse data
if len(x_data) > 1:
    # Calculate median spacing between consecutive points
    median_spacing = np.median(np.diff(x_data))
    # Calculate average spacing based on time range (more stable for sparse data)
    time_range = np.nanmax(x_data) - np.nanmin(x_data)
    avg_spacing = time_range / max(len(x_data) - 1, 1) if len(x_data) > 1 else median_spacing
    # Use the smaller of median or average spacing (prevents huge bars with sparse data)
    # This ensures bars don't get too wide when data is sparse
    base_width = min(median_spacing, avg_spacing) * 0.8
    # Set reasonable bounds: 
    # - Minimum: 0.01 hours (prevents invisible bars)
    # - Maximum: 5% of time range or 0.2 hours, whichever is smaller
    #   This prevents bars from being too wide even with very sparse data
    max_width = min(time_range * 0.05, 0.2)
    bar_width = max(0.01, min(base_width, max_width))
    print_manager.debug(f"Panel {i+1}: HAM bar width: {bar_width:.4f} hours (median_spacing={median_spacing:.4f}, avg_spacing={avg_spacing:.4f}, time_range={time_range:.4f}, n_points={len(x_data)}, max_width={max_width:.4f})")
else:
    bar_width = 0.1
```

### How It Works

1. **Calculates two spacing metrics:**
   - `median_spacing`: Median time difference between consecutive points
   - `avg_spacing`: Average spacing based on time range / number of points

2. **Uses the smaller value** to prevent huge bars with sparse data

3. **Applies bounds:**
   - **Minimum:** 0.01 hours (prevents invisible bars)
   - **Maximum:** min(5% of time range, 0.2 hours)
   - For a 12-hour window: max = min(0.6 hours, 0.2 hours) = **0.2 hours**

4. **Result:** Consistent bar widths across panels, even with varying data density

### Before vs After

**Before:**
- E11/E12: Thin bars (dense data, ~2235 points)
- E15: Medium bars (16 points)
- E23: **INSANELY wide bars (1.5-2 hours)** with only 3 points

**After:**
- All panels: Consistent bar widths
- Maximum bar width capped at 0.2 hours (or 5% of time range)
- Bars remain visible but don't dominate the plot

---

## Files Modified

1. **`plotbot/multiplot_options.py`**
   - Added `r_hand_single_color` initialization in `reset()` (line 317)
   - Added `r_hand_single_color` property with getter/setter (lines 873-880)

2. **`plotbot/multiplot.py`**
   - Added right axis color determination logic (lines 664-669)
   - Updated HAM plot color logic (lines 1749-1756)
   - Updated non-HAM right axis plot color (lines 851-852)
   - Applied `right_axis_color` to all right axis elements (lines 820-831, 844-847, 1854-1865)
   - Fixed HAM bar width calculation (lines 1811-1827)

---

## Testing

See example usage in:
- `example_notebooks/plotbot_multiplot_ham_example.ipynb` (line 68)

The notebook demonstrates:
- Setting `r_hand_single_color` to `'#363737'` (very dark grey)
- Using rainbow mode with HAM data
- Consistent bar widths across multiple panels with varying data density

---

## Related Options

- `ham_opacity` - Controls transparency of HAM bars (similar location, line 316)
- `color_mode` - Must be set to `'rainbow'` for `r_hand_single_color` to take effect
- `hamify` - Must be `True` to enable HAM plotting
- `ham_var` - The HAM variable to plot (e.g., `ham.n_ham`)

