# Captain's Log: 2025-05-06

## Bug Fix & Refinement: Vertical Line Placement in "Degrees from Perihelion" Mode

- **Issue:** The vertical line (controlled by `options.draw_vertical_line`) was not appearing at `x=0` when the x-axis was set to "Degrees from Perihelion" mode (`options.use_degrees_from_perihelion = True`), unless `options.use_relative_time = True` was also explicitly set. The desired behavior is for the line to be at `x=0` automatically in degrees mode, irrespective of the `use_relative_time` setting.

- **Root Cause Analysis:**
    1.  The initial logic for drawing the vertical line in `plotbot/multiplot.py` (around line 1708) conditioned drawing at `x=0` on *both* `panel_is_degrees_mode` AND `options.use_relative_time` being true.
    2.  Several layers of option interaction in `plotbot/multiplot_options.py` (within setters for `use_degrees_from_perihelion`, `use_relative_time`, and other positional axis modes, as well as the `reset()` method) were causing `options.use_relative_time` to be `False` when `multiplot()` was called with `use_degrees_from_perihelion = True`, even if the user attempted to set `use_relative_time = True` in their notebook.

- **Fixes Implemented:**
    1.  **`plotbot/multiplot_options.py`:**
        *   Modified the `@use_degrees_from_perihelion.setter`: It no longer automatically sets `_use_relative_time` to `False`.
        *   Modified the `@use_relative_time.getter`: It now correctly allows `_use_relative_time` to be `True` if `use_degrees_from_perihelion` is the active "positional-like" mode (by only returning `False` if other specific positional axes like `_x_axis_r_sun` are active).
        *   Modified the `@use_relative_time.setter`: When enabling relative time, it now only disables other specific positional axes (`_x_axis_r_sun`, etc.) if `use_degrees_from_perihelion` is *not* also active.
    2.  **`plotbot/multiplot.py` (around line 1715):**
        *   Simplified the vertical line drawing logic. If `options.draw_vertical_line` is true, the `x_coord_for_line` is set to `0.0` if `panel_is_degrees_mode` (i.e., `axs[i]._panel_actually_used_degrees`) is true. Otherwise, it defaults to `center_dt`. This makes the line placement at `x=0` in degrees mode independent of the `options.use_relative_time` state for this specific feature.

- **Outcome:** The vertical line now correctly appears at `x=0` when `options.use_degrees_from_perihelion = True` and `options.draw_vertical_line = True`, without requiring `options.use_relative_time = True` to be set by the user. The debug logs confirm `options.use_relative_time` remains `False` (as per its default after reset if not explicitly set by user for other purposes), but the vertical line is still correctly placed due to the direct check for `panel_is_degrees_mode`.

---
## Push: v2.23

- **Version Tag:** `2025_05_06_v2.23`
- **Commit Message:** `fix: Vertical line at x=0 in degrees_from_perihelion mode (v2.23)`

Summary: This push includes fixes to ensure the vertical line in `multiplot` correctly appears at `x=0` when the x-axis is in "Degrees from Perihelion" mode, independent of the `use_relative_time` setting. This involved changes to both `plotbot/multiplot_options.py` (to correctly manage interacting option states) and `plotbot/multiplot.py` (to simplify the vertical line drawing logic).

(Log remains open for further updates on 2025-05-06)
--- 