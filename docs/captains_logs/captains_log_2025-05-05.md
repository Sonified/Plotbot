# Captain's Log: 2025-05-05

## Push: v2.05

- Version: 2025_05_05_v2.05
- Commit message: v2.05: Significant multiplot issues and data cubby timing issues

Summary: This push documents ongoing significant issues with multiplot rendering and data cubby timing. See previous log for detailed context. No major new features, but version and commit message updated for tracking.

---

(Log remains open for further updates on 2025-05-05) 

---

## Bug Fix: DataCubby Merge Logic for Disjoint Ranges

**Symptom:** When using `multiplot` with multiple time ranges, only the first panel's data was correctly loaded and plotted. Subsequent panels failed because the `DataCubby` incorrectly determined that the new time ranges (e.g., 2019) were already contained within the existing data (e.g., 2018 + 2021-2025).

**Root Cause:** The `_merge_arrays` method in `data_cubby.py` calculated the overall start and end times of the data already in the cubby. It then checked if the *new* time range fell within this overall span. This logic failed when the existing data had gaps (disjoint ranges), leading it to incorrectly conclude the new data was already present.

**Fix:** Modified `_merge_arrays` to:
1. Combine existing and new time arrays.
2. Find unique timestamps using `np.unique`.
3. Compare the count of unique timestamps to the original count of existing timestamps.
4. Only proceed with the merge if the unique count is *greater*, indicating that the new data adds genuinely new time points.

This ensures that data is merged correctly even when the cubby contains disjoint time ranges.

## Push: v2.06

- Version: 2025_05_05_v2.06
- Commit message: Fix: Correct DataCubby merge logic for disjoint time ranges (v2.06) 

---

## CRITICAL ISSUE: Multiplot Modifications & Code Discrepancy (Degrees from Perihelion)

**Objective:** Implement a new x-axis mode for `multiplot` showing degrees relative to perihelion longitude.

**Steps Taken:**
- Added perihelion time lookup functions to `utils.py`.
- Added new options (`use_degrees_from_perihelion`, `degrees_from_perihelion_range`, `degrees_from_perihelion_tick_step`, `tight_x_axis`) to `multiplot_options.py` (including stubs).
- Attempted numerous automated edits (`edit_file`) to modify `multiplot.py` to:
    - Calculate relative degrees using `calculate_degrees_from_perihelion`.
    - Align plotted data with calculated degrees using `pd.merge_asof`.
    - Add final axis formatting logic for the new mode.
    - Implement the `tight_x_axis` option.

**Problem:** Encountered a series of runtime errors (`ImportError`, `AttributeError`, `ValueError`, `UnboundLocalError`). While attempting to debug and fix these, particularly by inserting debug prints, it became apparent that the AI's internal representation of `plotbot/multiplot.py` may not match the actual file state. The user (Robert) reported that code structures referenced by the AI did not exist in his file.

**Additional Symptom:** User reports that plots generated using `use_degrees_from_perihelion=True` incorrectly display "Time" on the x-axis, while `x_axis_carrington_lon=True` functions correctly.

**Current Status:** High level of concern regarding the integrity of the recent modifications to `multiplot.py`. Trust has been eroded due to apparent code hallucination and persistent errors.

**Immediate Next Step:** Perform a full read of `plotbot/multiplot.py` to establish an accurate baseline of the code before proceeding with any further modifications or debugging for the "degrees from perihelion" feature. 

---

## Extended Diagnosis & Debug Plan: Degrees from Perihelion Axis Failure (2025-05-05 Cont.)

**Macro Goal:** Implement a user-selectable x-axis mode in `multiplot` that displays Carrington longitude relative to the longitude at the specific perihelion time for the encounter corresponding to each panel's center time. Zero degrees should represent the perihelion longitude.

**Micro Goal (Current):** Debug why setting `plt.options.use_degrees_from_perihelion = True` results in the x-axis defaulting to "Time" instead of showing "Degrees from Perihelion (°)", even though the related `plt.options.x_axis_carrington_lon = True` setting *does* correctly display longitude.

**History & Problems Encountered:**
1.  **Initial Implementation:** Added `PERIHELION_TIMES` dict and `get_perihelion_time` function to `utils.py`. Added new options (`use_degrees_from_perihelion`, range/tick options, `tight_x_axis`) to `multiplot_options.py` and `.pyi`.
2.  **`multiplot.py` Modification:** Attempted extensive modifications to `multiplot.py` via multiple `edit_file` calls to:
    *   Determine the axis mode based on options.
    *   Call `calculate_degrees_from_perihelion` from `utils.py`.
    *   Implement data alignment using `pd.merge_asof` between calculated degrees (and their corresponding times) and the original data slice.
    *   Add logic to the final axis formatting loop to handle ticks, labels, and limits for the new degree mode.
    *   Add logic for the `tight_x_axis` option.
3.  **Runtime Errors:** Encountered and fixed a series of errors:
    *   `ImportError` for `apply_right_axis_color` (removed import/call).
    *   `ImportError` for `ensure_datetime_objects` (replaced usage with `pd.to_datetime`, removed import).
    *   `AttributeError` for setting read-only properties (`using_positional_x_axis`, `active_positional_data_type`) (removed incorrect assignments).
    *   `ValueError` for ambiguous array truthiness (changed `if ham_var:` to `if ham_var is not None:`).
    *   `UnboundLocalError` for `panel_actually_uses_degrees` (initialized variable at start of loop).
4.  **Code Discrepancy/Hallucination:** During debugging, AI referenced code structures in `multiplot.py` that did not match the user's actual file, indicating a desynchronization or internal error. This necessitated reading the full file to re-establish a baseline.
5.  **Current Failure:** Despite resolving the explicit errors, setting `use_degrees_from_perihelion = True` still results in the x-axis being labeled "Time".

**Current Hypothesis & Potential Causes:**
The fallback to the "Time" axis suggests that the logic flow for the degrees-from-perihelion mode is failing at some point *before* the final axis formatting stage. Specifically:
*   **Failure Point 1: Perihelion Time Lookup:** The `get_perihelion_time(center_time)` call might be returning `None` for the 2025 dates used in the test, likely because the `PERIHELION_TIMES` dictionary in `utils.py` lacks entries for these future encounters. If `perihelion_time_str` is `None`, the `current_panel_use_degrees` flag is never set to `True`.
*   **Failure Point 2: Calculation:** The `calculate_degrees_from_perihelion(...)` function might be returning `None` or an array of all `NaN`s for the `relative_degrees`. This could happen if the underlying positional data file (`Parker_positional_data.npz`) does not contain trajectory data covering the requested time range (March 2025) or the (missing) perihelion time.
*   **Failure Point 3: Data Alignment:** The `pd.merge_asof(...)` call might fail to align the calculated `relative_degrees` with the original `data_slice`, resulting in an empty `merged_df`. This would trigger the fallback logic.
*   **Failure Point 4: Final Check (Less Likely):** The heuristic check in the final formatting loop (checking if plotted data *looks* like degrees) might incorrectly classify the data as non-degree-like, forcing a fallback to Time formatting. However, this usually only happens if one of the previous failure points occurred.

**Debugging Plan:**
To pinpoint the failure, we need to trace the execution path and intermediate values within the `multiplot.py` main loop, specifically for the plot type being used (likely `time_series` for `mag_rtn_4sa.br`).

**Action:** Insert targeted `print_manager.debug` statements inside the `if var.plot_type == 'time_series':` block, within the `if current_panel_use_degrees and perihelion_time_str:` condition.

1.  **Debug Print 1 (After Calculation):** Verify the output of `calculate_degrees_from_perihelion`.
    *   *Location:* Immediately after the line `output_times, relative_degrees = calculate_degrees_from_perihelion(...)` (approx. line 740).
    *   *Code:* 
    ```python
                                           # <<< DEBUG PRINT 1 >>>
                                           print_manager.debug(f"Panel {i+1} Calc Output - perihelion_time_str: {perihelion_time_str}") # Also print the perihelion time used
                                           print_manager.debug(f"Panel {i+1} Calc Output - output_times type: {type(output_times)}, len: {len(output_times) if output_times is not None else 'None'}")
                                           print_manager.debug(f"Panel {i+1} Calc Output - relative_degrees type: {type(relative_degrees)}, len: {len(relative_degrees) if relative_degrees is not None else 'None'}")
                                           if relative_degrees is not None and len(relative_degrees) > 0:
                                               print_manager.debug(f"Panel {i+1} Calc Output - degrees range: {np.nanmin(relative_degrees):.2f} to {np.nanmax(relative_degrees):.2f} (NaNs: {np.isnan(relative_degrees).sum()})")
                                           elif relative_degrees is None:
                                                print_manager.debug(f"Panel {i+1} Calc Output - relative_degrees is None")
                                           else: # Empty array
                                                print_manager.debug(f"Panel {i+1} Calc Output - relative_degrees is empty")
                                           # <<< END DEBUG PRINT 1 >>>
    ```

2.  **Debug Print 2 (After Alignment):** Verify the result of the `pd.merge_asof` alignment.
    *   *Location:* Immediately after the line `merged_df.dropna(subset=['data', 'x_data'], inplace=True)` (approx. line 755).
    *   *Code:*
    ```python
                                               # <<< DEBUG PRINT 2 >>>
                                               print_manager.debug(f"Panel {i+1} Merge Output - merged_df shape: {merged_df.shape}")
                                               if not merged_df.empty:
                                                   print_manager.debug(f"Panel {i+1} Merge Output - Final x_data type: {type(merged_df['x_data'].values)}, len: {len(merged_df['x_data'].values)}")
                                                   print_manager.debug(f"Panel {i+1} Merge Output - Final x_data range: {np.nanmin(merged_df['x_data'].values):.2f} to {np.nanmax(merged_df['x_data'].values):.2f}")
                                                   # Check panel_actually_uses_degrees status AFTER merge logic
                                                   print_manager.debug(f"Panel {i+1} Merge Output - panel_actually_uses_degrees flag: {panel_actually_uses_degrees}") 
                                               # <<< END DEBUG PRINT 2 >>>
    ```

**Next Steps:**
1.  Manually insert the debug print code blocks specified above into `plotbot/multiplot.py` at the indicated locations.
2.  Ensure `print_manager.show_debug = True` is set.
3.  Rerun the test script from `Examples_Multiplot.ipynb` that uses `plt.options.use_degrees_from_perihelion = True`.
4.  Analyze the debug output to identify where the process is failing or falling back to the time axis.

---

## Push: v2.07

- **Version:** 2025_05_05_v2.07
- **Commit message:** feat: Implement degrees from perihelion axis attempt & fixes (v2.07)

**Summary:** Pushing current state after numerous attempts to implement and debug the 'degrees from perihelion' feature in multiplot. This includes fixes for various runtime errors and additions to options/utils. The feature is still not fully working (defaults to Time axis). Next step is to analyze debug output from prints added in `multiplot.py`.

---

## Refactoring Plan: Degrees from Perihelion Axis

**Problem:** Implementation of the `use_degrees_from_perihelion` x-axis became overly complex, deviating from the simpler, working pattern established by `x_axis_carrington_lon`. This led to unexpected behavior (e.g., incorrect axis labels) and difficult debugging.

**Decision:** Revert the complex additions (like `utils.calculate_degrees_from_perihelion` and associated merge logic in `multiplot.py`) and refactor the feature following a clean plan.

**New Plan:** Documented in `docs/implementation_plans/perihelion_axis_plan_v2.md`. The core strategy is to treat the perihelion axis as a direct variation of the Carrington longitude axis, leveraging existing positional mapping and degree formatting logic within `multiplot.py` and `XAxisPositionalDataMapper`.

## Push: v2.08

- **Version:** 2025_05_05_v2.08
- **Commit message:** refactor: Clean plan for degrees from perihelion axis (v2.08)

**Summary:** Pushing the refined implementation plan (`perihelion_axis_plan_v2.md`) and updated version information before proceeding with the refactoring. 