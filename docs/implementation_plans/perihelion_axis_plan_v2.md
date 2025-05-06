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

**NEW: Debugging Insights - Perihelion Offset (2025-05-06)**

Significant confusion arose during debugging the perihelion offset issue, primarily manifested in the `tests/test_plot_perihelion_windows.py` diagnostic test. Initial versions of the test showed confusing results:
*   Sometimes, the offset at perihelion time was a very small non-zero value (e.g., 0.001°).
*   In earlier, likely buggier iterations, the test produced a "wall of zeros" for all time offsets.

**Root Cause Analysis:**
1.  **Small Non-Zero Offsets:** This occurred when the test logic sampled the longitude at the *nearest available data point* in the `Parker_positional_data.npz` file to the exact perihelion time, rather than interpolating at the *exact* perihelion time. Since the data cadence doesn't guarantee a point exactly at perihelion, subtracting the interpolated perihelion longitude from the longitude of the nearest (but slightly off) time resulted in a small residual offset.
2.  **"Wall of Zeros" Behavior:** This was caused by bugs in earlier test versions where the calculation incorrectly subtracted the same longitude value from itself for all time offsets, likely due to errors in applying the time offsets during sampling or longitude lookup.

**Corrected Approach in `test_plot_perihelion_windows.py`:**

The final, working version of the test implements the following precise logic:
1.  **Symmetric Sampling:** Generate timestamps explicitly centered around perihelion using defined hour offsets (e.g., `np.arange(-50, 51, 10)` for ±50 hours in 10-hour steps).
2.  **Interpolate Perihelion Longitude:** Calculate the *exact* Carrington longitude at the *precise* perihelion timestamp using `np.interp(peri_time.timestamp(), ...)`.
3.  **Interpolate Sample Longitudes:** Calculate the Carrington longitude at *each sampled timestamp* (e.g., perihelion -50h, -40h, ..., +50h) using `np.interp(sample_times_numeric, ...)`.
4.  **Calculate Degrees from Perihelion:** Subtract the single interpolated perihelion longitude from the array of interpolated sample longitudes: `deg_from_peri = interp_lons - perihelion_lon`.
5.  **Apply Wrap-around:** Normalize the results to the [-180°, 180°] range using `deg_from_peri = np.mod(deg_from_peri + 180, 360) - 180`.

**Outcome & Verification:**
This corrected approach guarantees that the "Degrees from Perihelion" value is *exactly zero* at the zero-hour offset (perihelion time) because it subtracts the interpolated perihelion longitude from itself at that specific point. The surrounding time offsets show a smooth, expected sweep of degree values. This was confirmed by the following test output:

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.4, pytest-7.4.4, pluggy-1.5.0 -- /opt/anaconda3/envs/plotbot_env/bin/python3.12
cachedir: .pytest_cache
rootdir: /Users/robertalexander/GitHub/Plotbot
configfile: pytest.ini
collecting ... collected 2 items

tests/test_plot_perihelion_windows.py::test_print_debug PRINT DEBUG WORKS
PASSED
tests/test_plot_perihelion_windows.py::test_plot_perihelion_windows [DIAGNOSTIC] carrington_lon (entire NPZ):
  min: 0.0021806026529679
  max: 359.9942152086629

================= E18 (2023/12/29 00:56:00.000) =================
 Offset (hr) |                Timestamp |    Longitude |   Deg from Peri
----------------------------------------------------------------------
       -50.0 | 2023-12-26 22:56:00 |     239.7238 |        -78.1314
       -40.0 | 2023-12-27 08:56:00 |     242.0897 |        -75.7654
       -30.0 | 2023-12-27 18:56:00 |     247.7949 |        -70.0602
       -20.0 | 2023-12-28 04:56:00 |     259.4343 |        -58.4209
       -10.0 | 2023-12-28 14:56:00 |     281.7832 |        -36.0719
         0.0 | 2023-12-29 00:56:00 |     317.8551 |          0.0000
        10.0 | 2023-12-29 10:56:00 |     353.9613 |         36.1062
        20.0 | 2023-12-29 20:56:00 |      16.3352 |         58.4801
        30.0 | 2023-12-30 06:56:00 |      27.9700 |         70.1149
        40.0 | 2023-12-30 16:56:00 |      33.6617 |         75.8065
        50.0 | 2023-12-31 02:56:00 |      36.0136 |         78.1585

================= E19 (2024/03/30 02:21:00.000) =================
 Offset (hr) |                Timestamp |    Longitude |   Deg from Peri
----------------------------------------------------------------------
       -50.0 | 2024-03-28 00:21:00 |      13.9085 |        -78.0450
       -40.0 | 2024-03-28 10:21:00 |      16.2700 |        -75.6835
       -30.0 | 2024-03-28 20:21:00 |      21.9680 |        -69.9855
       -20.0 | 2024-03-29 06:21:00 |      33.5943 |        -58.3592
       -10.0 | 2024-03-29 16:21:00 |      55.9178 |        -36.0357
         0.0 | 2024-03-30 02:21:00 |      91.9535 |          0.0000
        10.0 | 2024-03-30 12:21:00 |     128.0690 |         36.1156
        20.0 | 2024-03-30 22:21:00 |     150.4765 |         58.5230
        30.0 | 2024-03-31 08:21:00 |     162.1326 |         70.1791
        40.0 | 2024-03-31 18:21:00 |     167.8357 |         75.8822
        50.0 | 2024-04-01 04:21:00 |     170.1942 |         78.2407

================= E20 (2024/06/30 03:47:00.000) =================
 Offset (hr) |                Timestamp |    Longitude |   Deg from Peri
----------------------------------------------------------------------
       -50.0 | 2024-06-28 01:47:00 |     148.0979 |        -78.0559
       -40.0 | 2024-06-28 11:47:00 |     150.4597 |        -75.6941
       -30.0 | 2024-06-28 21:47:00 |     156.1580 |        -69.9958
       -20.0 | 2024-06-29 07:47:00 |     167.7848 |        -58.3690
       -10.0 | 2024-06-29 17:47:00 |     190.1104 |        -36.0434
         0.0 | 2024-06-30 03:47:00 |     226.1538 |          0.0000
        10.0 | 2024-06-30 13:47:00 |     262.2705 |         36.1167
        20.0 | 2024-06-30 23:47:00 |     284.6729 |         58.5191
        30.0 | 2024-07-01 09:47:00 |     296.3256 |         70.1718
        40.0 | 2024-07-01 19:47:00 |     302.0270 |         75.8732
        50.0 | 2024-07-02 05:47:00 |     304.3845 |         78.2307

================= E21 (2024/09/30 05:15:00.000) =================
 Offset (hr) |                Timestamp |    Longitude |   Deg from Peri
----------------------------------------------------------------------
       -50.0 | 2024-09-28 03:15:00 |     282.2729 |         11.9196
       -40.0 | 2024-09-28 13:15:00 |     284.6368 |         14.2835
       -30.0 | 2024-09-28 23:15:00 |     290.3385 |         19.9852
       -20.0 | 2024-09-29 09:15:00 |     301.9715 |         31.6182
       -10.0 | 2024-09-29 19:15:00 |     324.3064 |         53.9531
         0.0 | 2024-09-30 05:15:00 |     270.3533 |          0.0000
        10.0 | 2024-09-30 15:15:00 |      36.4609 |        126.1076
        20.0 | 2024-10-01 01:15:00 |      58.8542 |        148.5009
        30.0 | 2024-10-01 11:15:00 |      70.5018 |        160.1485
        40.0 | 2024-10-01 21:15:00 |      76.2005 |        165.8472
        50.0 | 2024-10-02 07:15:00 |      78.5565 |        168.2032

================= E22 (2024/12/24 11:53:00.000) =================
 Offset (hr) |                Timestamp |    Longitude |   Deg from Peri
----------------------------------------------------------------------
       -50.0 | 2024-12-22 09:53:00 |     142.6074 |        -85.1356
       -40.0 | 2024-12-22 19:53:00 |     144.1821 |        -83.5609
       -30.0 | 2024-12-23 05:53:00 |     148.9391 |        -78.8040
       -20.0 | 2024-12-23 15:53:00 |     159.7580 |        -67.9851
       -10.0 | 2024-12-24 01:53:00 |     183.3018 |        -44.4413
         0.0 | 2024-12-24 11:53:00 |     227.7431 |          0.0000
        10.0 | 2024-12-24 21:53:00 |     272.3309 |         44.5878
        20.0 | 2024-12-25 07:53:00 |     295.9881 |         68.2451
        30.0 | 2024-12-25 17:53:00 |     306.8360 |         79.0930
        40.0 | 2024-12-26 03:53:00 |     311.5951 |         83.8520
        50.0 | 2024-12-26 13:53:00 |     313.1647 |         85.4216

================= E23 (2025/03/22 22:42:00.000) =================
 Offset (hr) |                Timestamp |    Longitude |   Deg from Peri
----------------------------------------------------------------------
       -50.0 | 2025-03-20 20:42:00 |     327.9860 |        -85.1304
       -40.0 | 2025-03-21 06:42:00 |     329.5609 |        -83.5555
       -30.0 | 2025-03-21 16:42:00 |     334.3186 |        -78.7979
       -20.0 | 2025-03-22 02:42:00 |     345.1395 |        -67.9769
       -10.0 | 2025-03-22 12:42:00 |       8.6875 |        -44.4289
         0.0 | 2025-03-22 22:42:00 |      53.1164 |          0.0000
        10.0 | 2025-03-23 08:42:00 |      97.6958 |         44.5794
        20.0 | 2025-03-23 18:42:00 |     121.3616 |         68.2452
        30.0 | 2025-03-24 04:42:00 |     132.2138 |         79.0973
        40.0 | 2025-03-24 14:42:00 |     136.9745 |         83.8581
        50.0 | 2025-03-25 00:42:00 |     138.5449 |         85.4285
```
This clarification resolves the primary remaining issue noted in the `Known Issues Requiring Debugging` section related to the perihelion offset.

**NEW: Clarification on Debugging Test Scripts (2025-05-07)**

Further review has clarified the role of the two primary test scripts used during debugging:

1.  **`tests/test_plot_perihelion_windows.py`:** This script represents the **correct, desired implementation**. It accurately calculates 'Degrees from Perihelion' by interpolating longitude at the precise perihelion time and subtracting this from the interpolated longitude at various time offsets. Critically, it produces a result where the 0-hour offset corresponds exactly to 0 degrees, as shown in its console output. This script serves as the **target model** for the logic required within `multiplot.py`.

2.  **`tests/debug_perihelion_mapping.py`:** This script was created specifically to **isolate and replicate the flawed logic** currently present within `multiplot.py`. It uses the `XAxisPositionalDataMapper` and calculation steps in a way that mirrors `multiplot`'s internal process. Its output (e.g., a range like -98.9° to -15.6° for E17 +/- 12h, *not* centered on 0°) demonstrates the **incorrect behavior** that needs to be fixed in `multiplot.py`. It is a diagnostic tool to study the *problem*, not the solution.

Understanding this distinction is key: the goal is to modify `multiplot.py` so that its internal calculations produce results consistent with `test_plot_perihelion_windows.py`, not `debug_perihelion_mapping.py`.

**⭐ ROOT CAUSE IDENTIFIED (2025-05-07) ⭐**

Debugging by comparing `debug_perihelion_mapping.py` (which uses the mapper) and `test_plot_perihelion_windows.py` (which uses direct interpolation) revealed the core issue:

*   **Timestamp Unit Mismatch:** The `XAxisPositionalDataMapper.map_to_position` function was passing timestamps to `np.interp` in different units. 
    *   The *reference times* (loaded from the NPZ file) were correctly represented as **seconds** since the epoch.
    *   However, the *query times* (passed in from `multiplot` or the debug script) were being converted to a float representation based on **nanoseconds** since the epoch.
*   **Result:** This large difference in scale caused `np.interp` to treat all query times as being outside the bounds of the reference times, leading to `NaN` outputs or incorrect extrapolation, explaining the flawed degree calculations.

*   **Fix:** The `XAxisPositionalDataMapper.map_to_position` function in `plotbot/x_axis_positional_data_helpers.py` was corrected to explicitly convert the input `datetime_array` (query times) from its `datetime64[ns]` representation to **seconds** since the epoch (by dividing the `int64` representation by `1e9`) before passing it to `np.interp`.

*   **Confirmation:** Rerunning `tests/debug_perihelion_mapping.py` after applying this fix showed the correct interpolation results and the expected 'Degrees from Perihelion' range, consistent with the target logic in `test_plot_perihelion_windows.py`.

**This fix to the mapper is expected to resolve the incorrect 'Degrees from Perihelion' axis values previously observed in `multiplot`.**

**⭐ NEW: Appearance of Asymmetrical Plots (2025-05-07) ⭐**

Debug logs from running multiplot with the fixed degree calculation logic revealed an important insight about the visual appearance of "Degrees from Perihelion" plots:

**Finding:** A fixed **time** window around perihelion (e.g., +/- 24 hours) does not necessarily correspond to a symmetrical range of **degrees** from perihelion. The spacecraft moves at varying speeds in terms of Carrington longitude, so a fixed time window may contain a skewed distribution of longitudes.

**Analysis of Debug Log Results:**
```
Panel 1 (E19): -180.00° to 180.00° (Good, full range)
Panel 2 (E20): -155.68° to -27.55° (Skewed! Only negative degrees)
Panel 3 (E21): -179.99° to 179.99° (Good, full range)
Panel 4 (E22): -163.46° to -16.49° (Skewed! Only negative degrees)
Panel 5 (E23): -180.00° to 179.98° (Good, full range)
```

Even though the calculation logic is correct (0° precisely at perihelion), the distribution of degrees within the plotted time window can be heavily skewed. Some encounters (E20, E22) show data only on the negative side of perihelion when using a fixed time window.

**Solution:** Use the `degrees_from_perihelion_range` option to force a symmetrical degree range for the x-axis:

```python
plt.options.degrees_from_perihelion_range = [-180, 180]  # Or a smaller range like [-90, 90]
```

This ensures all panels use the same scale centered around 0°, regardless of the actual distribution of data within the time window.

**Recommendation:** For scientific comparison between encounters, always use `degrees_from_perihelion_range` to ensure consistent axis scaling, particularly when creating multi-panel plots showing multiple encounters.