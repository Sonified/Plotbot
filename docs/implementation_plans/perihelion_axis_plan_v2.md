# Implementation Plan: Degrees from Perihelion Axis (v2 - Clean Approach)

**Date:** 2025-05-05

**Status: Complete (2025-05-05)**

- The degrees-from-perihelion axis is now fully implemented and behaves identically to the Carrington longitude axis in all respects (ticks, labels, limits, wrap-around, etc.).
- The implementation strictly follows the Carrington longitude logic, with the only difference being a longitude shift so that 0° aligns with perihelion.
- The axis formatting logic now uses a robust flag (`panel_actually_uses_degrees`) to ensure correct degree formatting, avoiding unreliable heuristics.
- All relevant tests pass (see `tests/test_degrees_from_perihelion.py`).
- See Captain's Log 2025-05-05 for details on the debugging and lessons learned.

**Key Lessons Learned:**
- Do not overcomplicate: Mirroring the Carrington longitude logic directly is the most robust and maintainable approach.
- Avoid redundant calculation functions; always use the positional data mapping infrastructure already in place.
- Use explicit flags to track axis mode for formatting, rather than inferring from data or options.
- Test with both automated scripts and visual inspection to confirm axis behavior matches expectations.

**Goal:** Implement `use_degrees_from_perihelion` as a new, mutually exclusive x-axis mode in `multiplot`, behaving identically to `x_axis_carrington_lon` in terms of axis formatting (ticks, labels), but with the plotted longitude values shifted so 0° corresponds to the longitude at the encounter's perihelion time.

**Core Strategy:** Leverage the existing, proven logic for the `x_axis_carrington_lon` option as the direct template. Avoid introducing unnecessary complexity or redundant calculation functions.

**Assumptions:**
*   The implementation will start from the current state of the codebase, assuming standard functionality is working.
*   `plotbot/utils.py` contains the `PERIHELION_TIMES` dictionary and the `get_perihelion_time` function.
*   `plotbot/x_axis_positional_data_helpers.py` contains the `XAxisPositionalDataMapper` class which correctly loads and maps times to `carrington_lon`.

**Note on Mutual Exclusivity:** The various positional x-axis options (`r_sun`, `carrington_lon`, `carrington_lat`, `degrees_from_perihelion`) and the `use_relative_time` option are designed to be mutually exclusive. Only one of these can define the primary x-axis scaling and labeling for a given plot. Enabling one via `plt.options` automatically disables the others (handled by the property setters in `multiplot_options.py`).

**Detailed Steps:**

1.  **[✅ Completed]** Modify `plotbot/multiplot_options.py` (and `.pyi`):
    *   Add the new boolean option: `use_degrees_from_perihelion` (default `False`).
    *   Implement its `@property` and `@setter`. The setter **must** disable other conflicting x-axis modes (`x_axis_carrington_lon`, `x_axis_carrington_lat`, `x_axis_r_sun`, `use_relative_time`) when set to `True`, mirroring the behavior of the existing positional setters.
    *   Add `degrees_from_perihelion_range` (Optional `Tuple[float, float]`, default `None`) for setting fixed axis limits.
    *   Add `degrees_from_perihelion_tick_step` (Optional `float`, default `None`) for setting fixed tick steps.

2.  **Modify `plotbot/multiplot.py`:**
    *   **Initialization Section (Start of `multiplot` function):**
        *   Ensure the `positional_feature_requested` check correctly includes `options.use_degrees_from_perihelion`.
        *   If `positional_feature_requested` is true, set `using_positional_axis = True`.
        *   In the block that determines the initial `data_type`, `axis_label`, etc., add conditions for all four positional modes to ensure structural consistency. *(Note: The `values_array` assignment here is primarily for structural clarity; the actual mapping uses the `time_slice` later.)*
            ```python
            if getattr(options, 'use_degrees_from_perihelion', False):
                print_manager.debug("--> Mode Determination: use_degrees_from_perihelion is True.")
                data_type = 'degrees_from_perihelion'
                axis_label = "Degrees from Perihelion (°)"
                units = "°"
                # Setters in options class handle disabling others
            elif options.x_axis_carrington_lon:
                print_manager.debug("--> Mode Determination: x_axis_carrington_lon is True.")
                data_type = 'carrington_lon'
                # values_array = positional_mapper.longitude_values # Consistency check
                axis_label = "Carrington Longitude (°)"
                units = "°"
            elif options.x_axis_r_sun:
                print_manager.debug("--> Mode Determination: x_axis_r_sun is True.")
                data_type = 'r_sun'
                # values_array = positional_mapper.radial_values # Consistency check
                axis_label = "Radial Distance (R_sun)"
                units = "R_sun"
            elif options.x_axis_carrington_lat:
                print_manager.debug("--> Mode Determination: x_axis_carrington_lat is True.")
                data_type = 'carrington_lat'
                # values_array = positional_mapper.latitude_values # Consistency check
                axis_label = "Carrington Latitude (°)"
                units = "°"
            else:
                 # ... fallback to time ...
            ```
    *   **Panel Loop (Data Preparation - Inside `for i, (center_time, var) in enumerate(plot_list):`)**
        *   Initialize `panel_actually_uses_degrees = False` at the beginning of the loop iteration.
        *   Call `get_perihelion_time(center_time)` to get `perihelion_time_str`.
        *   Determine `current_panel_use_degrees = True` only if `options.use_degrees_from_perihelion` is True, `using_positional_axis` is True, and `perihelion_time_str` is not None.
        *   **Inside the sections where `x_data` is determined (for time_series, scatter, spectral, default plots):**
            *   Add an `if current_panel_use_degrees:` block.
            *   Inside this block:
                1.  Map the panel's `time_slice` to standard Carrington longitudes:
                    `carrington_lons_slice = positional_mapper.map_to_position(time_slice, 'carrington_lon')`
                2.  Map the single `perihelion_dt` (parsed from `perihelion_time_str`) to its longitude:
                    `perihelion_lon_val = positional_mapper.map_to_position(np.array([np.datetime64(perihelion_dt)]), 'carrington_lon')[0]` (Handle potential `None` return).
                3.  Calculate relative degrees:
                    `relative_degrees = carrington_lons_slice - perihelion_lon_val`
                4.  Apply wrap-around:
                    `relative_degrees[relative_degrees > 180] -= 360`
                    `relative_degrees[relative_degrees <= -180] += 360`
                5.  Set the x-data for plotting: `x_data = relative_degrees`
                6.  Set the panel flag: `panel_actually_uses_degrees = True`
                7.  Store the flag on the axis: `axs[i]._panel_actually_used_degrees = True`
            *   Else (if not `current_panel_use_degrees`): Proceed with the existing logic for standard positional mapping (`carrington_lon`, `r_sun`, etc.) using `positional_mapper.map_to_position(time_slice, data_type)` or fallback to time axis.
    *   **Final Formatting Loop (Near end of `multiplot` function):**
        *   In the mode detection logic, determine `current_axis_mode` based primarily on the `getattr(ax, '_panel_actually_used_degrees', False)` flag, falling back to check standard positional options if the flag is False.
        *   Ensure the `elif` block that handles degree formatting explicitly includes `degrees_from_perihelion`:
            ```python
            elif current_axis_mode == 'degrees_from_perihelion' or current_axis_mode == 'carrington_lon' or current_axis_mode == 'carrington_lat':
                print_manager.debug(f"Axis {i}: Entering DEGREE formatting block ({current_axis_mode}).")
                # TICK LOCATOR: Use options.degrees_from_perihelion_tick_step if mode is perihelion, otherwise use MaxNLocator based on positional_tick_density (as done for carrington_lon).
                # FORMATTER: Use the *exact same* degree_formatter function for all degree modes.
                # LIMITS: Use options.degrees_from_perihelion_range if mode is perihelion, otherwise use options.x_axis_positional_range. Handle auto-scaling if range is None.
                # LABEL: Already handled by the label setting logic based on current_axis_mode.
            elif current_axis_mode == 'r_sun':
                 # ... separate formatting logic for r_sun ...
            ```
        *   Rely on the flag set during data preparation (and the active `plt.options`) rather than heuristics based on data values.

3.  **Refine `plotbot/utils.py`:**
    *   Ensure `get_perihelion_time` is robust. Consider removing any functions made redundant by this plan (like `calculate_degrees_from_perihelion` if it exists).

**Verification:**
*   Use `test_degrees_from_perihelion.py` (with `use_degrees_from_perihelion = True`) to confirm the axis label, ticks, and data range are correct.
*   Use `Examples_Multiplot.ipynb` with `x_axis_carrington_lon = True` and then separately with `use_degrees_from_perihelion = True` to visually compare and ensure consistent degree formatting.
*   Verify that setting `use_degrees_from_perihelion = True` correctly disables `use_relative_time`.

This plan directly addresses the requirements, leverages existing working code, and minimizes complexity, leading to a more robust and maintainable solution. 

---

## Synopsis for Future Reference:

*   **Goal:** Add an x-axis mode showing degrees relative to perihelion longitude (0° = perihelion).
*   **Core Principle:** This is fundamentally a *shifted Carrington longitude*. The implementation should reuse the existing degree-formatting logic from the `x_axis_carrington_lon` option.
*   **Key Files & Roles:**
    *   `plotbot/multiplot_options.py`: Defines the user-facing option (`use_degrees_from_perihelion`) and ensures it's mutually exclusive with other x-axis modes. Contains `MultiplotOptions` class.
    *   `plotbot/x_axis_positional_data_helpers.py`: Contains `XAxisPositionalDataMapper`, which handles loading the `Parker_positional_data.npz` file and provides the core function (`map_to_position`) to convert times to positional coordinates (including `carrington_lon`). **This class should be used for all positional lookups.**
    *   `plotbot/utils.py`: Contains the `PERIHELION_TIMES` dictionary and `get_perihelion_time` function to look up the reference perihelion time for a given encounter/date.
    *   `plotbot/multiplot.py`: The main plotting function. This is where the core logic resides:
        *   Reads the options.
        *   Uses `XAxisPositionalDataMapper` to get standard longitudes for the time slice.
        *   Uses `XAxisPositionalDataMapper` again to get the specific longitude for the perihelion time.
        *   Calculates the difference (relative degrees) and handles wrap-around.
        *   Uses these relative degrees as the `x_data` when plotting.
        *   In the final formatting loop, applies the *same* tick/label formatting as `carrington_lon` when this mode is active.
*   **Relevant Tests:**
    *   `tests/test_degrees_from_perihelion.py`: Should be the primary script to verify this specific feature works correctly (checks label, ticks, data range).
    *   `tests/multiplot_tests/test_x_axis_positional_standalone.py` & `test_single_x_axis_positional.py`: Serve as examples of how the *standard* positional axes (like `carrington_lon`) are intended to work and look, providing a baseline for comparison.
    *   `Examples_Multiplot.ipynb`: Useful for visual inspection and integration testing with various options.
*   **Rationale for Simplicity:** This plan aligns with the existing, robust pattern for positional axes, making the code cleaner, more maintainable, and easier to understand by integrating the new feature cleanly rather than adding complex, separate logic.