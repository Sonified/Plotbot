# Implementation Plan: Degrees from Perihelion Axis (v2 - Clean Approach)

**Date:** 2025-05-05

**Status: Implementation Complete - Debugging Required (2025-05-06)**

- After resetting `multiplot.py` to `ef18950` and re-verifying, confirmed that the necessary perihelion calculation logic for all plot types (`time_series`, `scatter`, `spectral`, `else`) was already present (likely from pre-revert edits that persisted unexpectedly).
- Supporting changes (imports, initial mode detection, flags, perihelion time lookup) are in place.
- Fixes in `utils.py` (PERIHELION_TIMES) and `multiplot_options.py` (setters) are complete.
- Final formatting loop logic in `multiplot.py` correctly handles the perihelion mode.
- All tests in `tests/multiplot_tests/text_x_axis_positional_types.py` pass, including the perihelion test.
- **Known Issues Requiring Debugging:**
    1.  **Perihelion Offset:** The 'Degrees from Perihelion' axis mapping is inaccurate. Plots centered on perihelion time do not show 0° at the center as expected (e.g., showing ~60° instead).
    2.  **Standard Positional Axis Errors:** Visual inspection reveals issues with standard positional axes:
        *   Carrington Latitude labels show incorrect/uniform values.
        *   Carrington Longitude scaling/range behaves erratically between plots.
- **Reference Commit:** Commit `c0faf61` is noted as a potential reference point for investigating the previously working logic for standard positional axes (Lat, Lon, R_sun).
- **Next Step:** Debug the positional axis implementation within `multiplot.py`, addressing both the perihelion offset and the standard axis errors. Comparing logic to commit `c0faf61` may be helpful.

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
    *   Add options: `use_degrees_from_perihelion`, `degrees_from_perihelion_range`, `degrees_from_perihelion_tick_step`.
    *   Update setters for all positional modes to ensure mutual exclusivity (including disabling perihelion mode).

2.  **Modify `plotbot/multiplot.py` (Based on `ef18950` baseline):**
    *   **[✅ Completed]** **Initialization Section:**
        *   Ensure `positional_feature_requested` check includes `options.use_degrees_from_perihelion`.
        *   Set `using_positional_axis = True` correctly.
        *   Update mode determination block (`if/elif`) to prioritize `use_degrees_from_perihelion`.
    *   **[✅ Completed]** **Panel Loop (Setup):**
        *   Initialize `panel_actually_uses_degrees`, `perihelion_time_str`, `current_panel_use_degrees`.
        *   Call `get_perihelion_time` and set `current_panel_use_degrees`.
    *   **[✅ Completed]** **Panel Loop (Data Preparation - Inside `for i, (center_time, var) in enumerate(plot_list):`)**
        *   **[✅ Completed]** **`if var.plot_type == 'time_series':` block:** Perihelion calculation logic present.
        *   **[✅ Completed]** **`elif var.plot_type == 'scatter':` block:** Perihelion calculation logic present.
        *   **[✅ Completed]** **`elif var.plot_type == 'spectral':` block:** Perihelion calculation logic present.
        *   **[✅ Completed]** **`else:` (default plot type) block:** Perihelion calculation logic present.
    *   **[✅ Completed]** **Final Formatting Loop:**
        *   Determine `current_axis_mode` using `panel_actually_uses_degrees` flag and initial `data_type`.
        *   Update degree formatting `elif` to include `degrees_from_perihelion`.
        *   Add checks for `degrees_from_perihelion_range` and `degrees_from_perihelion_tick_step`.
        *   Ensure label setting uses the initial `axis_label`.

3.  **[✅ Completed]** **Refine `plotbot/utils.py`:**
    *   Ensure `PERIHELION_TIMES` dictionary is complete and correct.
    *   Ensure `get_perihelion_time` function works correctly.

**Verification:**
*   **[✅ Passing (Automated)]** Use `tests/multiplot_tests/text_x_axis_positional_types.py` to confirm basic label/range for all modes.
*   **[🚧 TODO]** Debug the perihelion longitude calculation offset issue in `multiplot.py`.
*   **[🚧 TODO]** Debug the standard positional axis (Lat, Lon) label/scaling issues in `multiplot.py`. Comparing with commit `c0faf61` logic may help.
*   **[🚧 TODO]** Visually verify plots using `Examples_Multiplot.ipynb` after debugging is complete.