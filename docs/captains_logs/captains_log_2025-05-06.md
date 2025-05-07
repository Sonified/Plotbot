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

## Captain's Log - Plotbot - 2025-05-06

**Primary Objective:** Refactor the `Magnetic_Hole_Finder` workflow to improve modularity and enable efficient data snapshotting of multiple time ranges for `mag_RTN` data.

**Summary of Activities & Current Status:**

1.  **Major Refactoring of `Magnetic_Hole_Finder`:**
    *   The core magnetic hole detection logic, previously in `Magnetic_Hole_Finder.ipynb`, was moved to `magnetic_hole_finder/magnetic_hole_finder_core.py`.
    *   This new module includes:
        *   `HoleFinderSettings` class: Consolidates all configurable parameters for the detection algorithm and its output generation.
        *   `detect_magnetic_holes_and_generate_outputs()`: The new primary function called from the notebook. It takes `trange`, `base_save_dir`, and a `HoleFinderSettings` instance. It handles subdirectory setup, data preparation (using helpers from `magnetic_hole_finder/data_management.py`), calls an internal `_detect_magnetic_holes_logic()` for the core algorithm, and then orchestrates outputs (plots, markers, audio using helpers from `.plotting`, `.MH_format_output`, `.data_audification`) based on settings, saving them to the run-specific subdirectory. It also saves a settings/summary JSON.
    *   The `Magnetic_Hole_Finder.ipynb` notebook is now a lean command center for defining `BASE_SAVE_DIRECTORY`, `TIME_RANGE_TO_ANALYZE`, instantiating/customizing `HoleFinderSettings`, and calling `detect_magnetic_holes_and_generate_outputs()`.

2.  **Integration with Plotbot's Data System (`plotbot.get_data`, `DataCubby`):**
    *   `magnetic_hole_finder/data_management.py` (`download_and_prepare_high_res_mag_data`) was refactored to use `plotbot.get_data()` with the global `plotbot.mag_rtn` instance. This resolved earlier data unpacking errors.
    *   `__init__` methods in `plotbot/data_classes/psp_mag_classes.py` (e.g., `mag_rtn_class`) were updated to set `self.class_name` and `self.data_type`, fixing "attribute not found" issues from `plotbot.get_data`.
    *   Time string parsing in `magnetic_hole_finder/time_management.py` was updated to use `dateutil.parser.parse` for flexibility, resolving `strptime` `ValueError`s.

3.  **Enhancement of `plotbot/data_snapshot.py` (`save_data_snapshot` function):**
    *   **Feature Request:** Enable `save_data_snapshot` to populate multiple global Plotbot data instances (e.g., `plotbot.mag_rtn`) across a list of specified time ranges before creating the snapshot.
    *   **Implementation:** A `trange_list` parameter was added. If provided along with a `classes` list (of global Plotbot instances), the function now calls `plotbot.get_data(t_range, class_instance)` for each combination to load/merge data via `DataCubby` before saving.
    *   **Reference Commit for "Original" `data_snapshot.py` (before `trange_list` feature):** `34c642c`. This can be used for diffing to review the state of `plotbot/data_snapshot.py` prior to this specific enhancement.

4.  **Current Challenge: "LEN MISMATCH" and `IndexError` during Snapshotting:**
    *   **Problem:** When using the enhanced `save_data_snapshot` with `trange_list` to populate `plotbot.mag_rtn` over multiple time intervals, the `_identify_data_segments` function (if `auto_split=True`) within `plotbot/data_snapshot.py` fails with an `IndexError`.
    *   **Root Cause Identified:** This is preceded by a critical log: `[SNAPSHOT CRITICAL] _identify_data_segments: LEN MISMATCH! .time len: X, .datetime_array len: Y for instance type mag_rtn_class.` This indicates the global `plotbot.mag_rtn` instance becomes internally inconsistent after `plotbot.get_data` (utilizing `DataCubby`) processes multiple time ranges. Specifically, its TT2000 `self.time` array and its Python/Numpy `self.datetime_array` acquire different lengths.
    *   **Suspected Area:** The inconsistency likely arises from how `DataCubby.update_global_instance` interacts with `mag_rtn_class.update / calculate_variables`. While `DataCubby` merges `datetime_array` and `raw_data`, its attempts to ensure `self.time` and `self.field` are also consistently updated with the fully merged data appear to be either incomplete or are being subsequently undone by the class's own update methods when called.

**Next Steps (Post "Reboot" of Assistant):**

1.  **Verify `plotbot/data_snapshot.py`:** Confirm its stability. The primary new feature is the `trange_list` population loop. The `_identify_data_segments` and `_create_filtered_instance` functions within it are secondary to the core issue and may need to be temporarily simplified or disabled if they continue to hit errors due to inconsistent input objects.
2.  **Focused Debugging on Data Consistency (Primary Goal):**
    *   The main target is ensuring the global `plotbot.mag_rtn` instance (and similar data classes) remains internally consistent (`len(self.time) == len(self.datetime_array)`) after multiple data chunks are loaded and merged via `plotbot.get_data()` and `DataCubby`.
    *   **Files to Instrument with Prints:**
        *   `plotbot/data_classes/psp_mag_classes.py`: Specifically, the `__init__`, `update`, and `calculate_variables` methods of `mag_rtn_class`.
        *   `plotbot/data_cubby.py`: The `update_global_instance` method (and potentially `_merge_arrays` if necessary).
    *   **Information to Log:** Object IDs (`id(self)`), and the lengths/shapes of `.time`, `.datetime_array`, `.field`, and key components in `.raw_data` at critical points: before/after attribute assignments, before/after method calls (like `calculate_variables`), and particularly within `DataCubby.update_global_instance` before and after merging and attribute re-assignments. 

## Captain's Log - Plotbot - 2025-05-06 (Continued)

**In-depth Update on "LEN MISMATCH" and Snapshotting Issue:**

**Continuing from Previous Log:** The primary outstanding issue is an `IndexError` within `plotbot/data_snapshot.py` (specifically in `_identify_data_segments`) when `save_data_snapshot` is called with `auto_split=True` after populating `plotbot.mag_rtn` across multiple time ranges using the new `trange_list` feature.

**Core Problem - Data Inconsistency:**
*   The root cause is a **"LEN MISMATCH"** within the global `plotbot.mag_rtn` instance. After processing multiple time ranges, `plotbot.mag_rtn.time` (TT2000 format, expected to be updated/merged) ends up with a length corresponding to only the *last processed data chunk* (e.g., 233,202 elements). In contrast, `plotbot.mag_rtn.datetime_array` (Python/Numpy datetime objects) and `plotbot.mag_rtn.raw_data` components (like `br`, `bt`, `bn`) are correctly merged by `DataCubby._merge_arrays` and reflect the total number of data points across all processed time ranges (e.g., 8,143,326 elements).
*   The `IndexError` in `_identify_data_segments` is a direct symptom of this: it derives indices based on the longer `datetime_array` and then attempts to apply these to the shorter, inconsistent `time` array.

**Detailed Analysis of Suspected Interaction:**

1.  **`mag_rtn_class.calculate_variables(imported_data)`:** This method (in `plotbot/data_classes/psp_mag_classes.py`) fundamentally *overwrites* `self.time`, `self.datetime_array`, `self.field`, and `self.raw_data` based *only* on the single `imported_data` object (representing one data chunk) it receives.

2.  **`mag_rtn_class.update(imported_data)`:** This method calls `self.calculate_variables(imported_data)`, thus propagating the overwrite behavior.

3.  **`DataCubby.update_global_instance(data_type_str, imported_data_obj)`:**
    *   **Initial Load (Empty Global Instance):** Calls `global_instance.update(imported_data_obj)`. This correctly populates the instance with the first chunk, and all time/data arrays are consistent.
    *   **Subsequent Loads (Merge Path):**
        *   `DataCubby` correctly uses its `_merge_arrays` helper to combine the existing `global_instance.datetime_array` and `global_instance.raw_data` with the new data chunk's corresponding arrays.
        *   It then directly assigns these merged arrays back to `global_instance.datetime_array` and `global_instance.raw_data`.
        *   **Crucially, a fix was implemented here to also update `global_instance.time` (by converting the *entire* `merged_datetime_array` back to TT2000 using `cdflib.cdfepoch.from_datetime`) and to reconstruct `global_instance.field` from the merged raw components.**
        *   After these direct assignments, `DataCubby` does *not* (and should not) call `global_instance.update()` again, as this would undo the merge. It does call `global_instance.set_ploptions()`, which correctly uses the merged `datetime_array` and `raw_data`.

**Hypothesis for Persistent "LEN MISMATCH":**
The persistence of the "LEN MISMATCH" *despite* the explicit update to `global_instance.time` and `global_instance.field` in `DataCubby.update_global_instance` suggests one of the following:
    a.  There's a subtle flaw in the logic or execution of the `global_instance.time = cdflib.cdfepoch.from_datetime(merged_times_dt64)` line or the field reconstruction within `DataCubby` (e.g., an exception being caught silently, or an unexpected return value from `cdflib` for very large arrays).
    b.  Some other part of the `plotbot.get_data` lifecycle, after `DataCubby.update_global_instance` completes, might be inadvertently triggering a call to `mag_rtn_class.update()` or `mag_rtn_class.calculate_variables()` with only the latest data chunk, thus re-introducing the inconsistency by overwriting the carefully merged `.time` attribute.
    c.  The `print_manager` or other logging/debugging utilities, when inspecting the `global_instance` at various stages, might be inadvertently triggering method calls or attribute calculations that lead to this state if not handled carefully by the class's `__getattr__` or `__getattribute__`. (Less likely to cause persistent data modification, but possible for temporary states).

**Status of `plotbot/data_snapshot.py` `trange_list` Feature:**
*   The feature to allow `save_data_snapshot` to accept a `trange_list` and call `plotbot.get_data` to populate instances before saving is implemented.
*   The `IndexError` it's encountering is a symptom of the upstream data inconsistency in the `plotbot.mag_rtn` object it receives.
*   The `_identify_data_segments` and `_create_filtered_instance` helper functions within `data_snapshot.py` are secondary to this core data consistency problem. If their input object (`plotbot.mag_rtn`) were internally consistent, they should function as intended (or their own bugs could be addressed separately).
*   **Reference Commit for `data_snapshot.py` (before `trange_list` feature and before recent attempts to debug its helpers):** `34c642c`.

**Next Steps (Post "Reboot" of Assistant):**
The highest priority is to resolve the "LEN MISMATCH" in the global `plotbot.mag_rtn` instance.
1.  **Meticulous Print-Based Debugging:**
    *   **Target `plotbot/data_cubby.py` (`update_global_instance`):** Add detailed prints immediately before and after the line `global_instance.time = cdflib.cdfepoch.from_datetime(merged_times_dt64)`. Log the length of `merged_times_dt64` and the length of `global_instance.time` right after the assignment. Log any exceptions specifically from this block. Do the same for `global_instance.field` reconstruction.
    *   **Target `plotbot/data_classes/psp_mag_classes.py` (`mag_rtn_class`):** Add prints at the entry and exit of `update()` and `calculate_variables()`, logging `id(self)` and the lengths of `self.time` and `self.datetime_array`. This will help identify if/when these methods are unexpectedly called or if `calculate_variables` is the point where `self.time` is being reset to a shorter length after `DataCubby` has done its merge.
    *   **Target `plotbot/get_data.py`:** After `DataCubby.update_global_instance` is called and returns, immediately inspect and log the lengths of `.time` and `.datetime_array` of the relevant global instance (e.g., `plotbot.mag_rtn`) to see its state as `get_data` finishes with it.

This detailed tracing should illuminate exactly where and why `plotbot.mag_rtn.time` becomes inconsistent with `plotbot.mag_rtn.datetime_array`. 

---
## Session Update: Data Consistency for Multi-Trange Snapshots (Continued from detailed LEN MISMATCH saga)

**TL;DR:** Resolved a persistent `IndexError` in `plotbot/data_snapshot.py` when creating snapshots from multiple time ranges (`trange_list`). The root cause was an internal inconsistency within data class instances (e.g., `plotbot.mag_rtn`) where the `.time` (TT2000 `int64`) attribute was not being correctly updated/synchronized after `.datetime_array` (`datetime64[ns]`) and `.raw_data` were merged by `DataCubby`. The fix involved ensuring that after a merge operation in `DataCubby.update_global_instance`, `.time` is robustly regenerated to match the length of `.datetime_array` by casting `.datetime_array` to `int64` (representing nanoseconds since Unix epoch), rather than attempting a complex and problematic conversion back to true TT2000 for the merged array. This ensures length consistency for internal operations, with the understanding that `.time` is only guaranteed to be true TT2000 upon initial load from a single CDF, and becomes an `int64` epoch time after merges.

**Detailed Breakdown of the Debugging Journey & Fix:**

1.  **Initial Problem:** When using `save_data_snapshot` with the `trange_list` feature to populate a global instance like `plotbot.mag_rtn` from multiple CDF files, the `_identify_data_segments` function would often raise an `IndexError`. This was preceded by a "LEN MISMATCH" error, indicating `plotbot.mag_rtn.time` and `plotbot.mag_rtn.datetime_array` had different lengths.

2.  **Investigation into `DataCubby.update_global_instance`:**
    *   We found that while `_merge_arrays` correctly combined `datetime_array` (NumPy `datetime64`) and `raw_data` components, the subsequent step to update the `global_instance.time` (meant to be TT2000 `int64`) and `global_instance.field` was problematic.
    *   **`cdflib.cdfepoch.compute_tt2000()` Challenges:**
        *   Attempting to call `compute_tt2000` with a direct NumPy `datetime64` array (e.g., the merged `global_instance.datetime_array`) resulted in `cdflib` returning a 0-D scalar array (effectively only converting the first timestamp).
        *   Changing the input to `compute_tt2000` to be a list of Python `datetime.datetime` objects (converted from the `datetime64` array) led to a `TypeError` inside `cdflib` because it expected a list of *date component lists* (e.g., `[[year, month, day,...], ...]`).
        *   Correctly formatting the input as a list of date component lists would have been extremely slow for large arrays (millions of points) due to Python loops for list creation and `cdflib` potentially iterating.
    *   These `cdflib` issues often caused the `try...except` block in `update_global_instance` (where `.time` and `.field` were to be reconstructed) to fail silently or exit prematurely, leaving `.time` and `.field` stale and shorter than the correctly merged `.datetime_array` and `.raw_data`.

3.  **Analysis of `b91bd7c` and Old Snapshots:**
    *   Examination of how Plotbot likely operated at commit `b91bd7c` (and an old snapshot file provided by Robert) revealed that this inconsistency (`.time` being shorter than `.datetime_array` after merges) was likely a pre-existing latent issue.
    *   The system "worked" for plotting because plots primarily used the correctly merged `.datetime_array` and `.raw_data`.
    *   The `trange_list` feature and more rigorous checks in `_identify_data_segments` simply exposed this latent inconsistency, leading to the `IndexError`.

4.  **The Pragmatic Solution Implemented:**
    *   **Primary Time Representation for Internal Ops:** Acknowledged that for internal consistency and operations (especially after merges), `self.datetime_array` (`datetime64[ns]`) is the most robust and performant time representation.
    *   **Simplified `.time` Attribute After Merges:**
        *   In `DataCubby.update_global_instance`, after `global_instance.datetime_array` and `global_instance.raw_data` are updated with merged data, `global_instance.time` is now set as: 
            `global_instance.time = global_instance.datetime_array.astype('datetime64[ns]').astype(np.int64)`
        *   This ensures `global_instance.time` is always an `int64` array with the same length as `global_instance.datetime_array`.
        *   **Important Consequence:** After a merge operation in `DataCubby`, `global_instance.time` no longer strictly represents TT2000 values. Instead, it holds nanoseconds since the Unix epoch (consistent with how `datetime64[ns]` is often interpreted when cast to `int64`). True TT2000 values in `.time` are only guaranteed upon initial load from a single CDF via the class's `calculate_variables` method.
    *   **Field Reconstruction:** `global_instance.field` is reconstructed based on the now consistently-lengthed `raw_data` and `datetime_array`.
    *   **Order of Operations:** Ensured that these critical attribute reconstructions (`.time`, `.field`) happen *before* `global_instance.set_ploptions()` is called within `DataCubby`, preventing `KeyError`s that were previously halting the update process.
    *   **`ensure_internal_consistency()` Method:** This method in the data classes (e.g., `mag_rtn_class`) was also updated to use this direct `astype(np.int64)` approach for `self.time` if it detects an inconsistency. In the successful test run, `DataCubby` made the instance consistent, so `ensure_internal_consistency` reported no changes needed, which is ideal.

5.  **Outcome:**
    *   The `TypeError` and `KeyError` within `DataCubby.update_global_instance` were resolved.
    *   `.time`, `.datetime_array`, `.raw_data`, and `.field` are now all consistent in length after merge operations.
    *   The "LEN MISMATCH" error in `_identify_data_segments` is gone.
    *   The `IndexError` when applying segment masks is resolved.
    *   Snapshots of multi-trange data can now be created successfully and efficiently.

This approach prioritizes operational stability, performance for internal operations, and length consistency for critical array attributes, while accepting a change in the precise meaning of the `.time` attribute after data merging operations. The primary time representation for plotting and user interaction (`.datetime_array`) remains accurate `datetime64[ns]`. 

---
## Push: v2.24

- **Version Tag:** `2025_05_06_v2.24`
- **Commit Message:** `Refactor: Improve DataCubby and data class consistency for multi-trange ops (v2.24)`

Summary: This push includes extensive debugging and fixes to `DataCubby`, data class internal consistency (`ensure_internal_consistency`), and `load_data_snapshot` to robustly handle multi-trange data processing, particularly for snapshot creation and loading. Key changes involve ensuring `.time` attributes are consistently managed (now as int64 ns post-merge in DataCubby) and that data loading (`import_data_function`) correctly identifies and processes files for specified time ranges. Addressed `KeyError`s during snapshot loading by ensuring `SimpleDataObject` (used by `load_data_snapshot`) correctly reconstructs the expected primary field key for `calculate_variables`. Corrected case sensitivity issues for `mag_RTN_4sa` config lookup. Added a comprehensive end-to-end test script (`tests/test_plotbot_core_pipeline.py`).

*(Log remains open for further updates on 2025-05-06)* 