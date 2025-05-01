# Captain's Log - May 1, 2025

## Session Goals

- Simplify `proton_fits_class.py` by reverting to commit `89aeb7d` and removing initial CWYN structures.
- Ensure basic FITS data loading and plotting works correctly for variables derivable solely from `sf00_fits`.
- Re-apply necessary fixes (like the `plot_manager.__array_finalize__` modification).

## Activities & Learnings

- **Debugging FITS Plotting Issue:** Investigated why `proton_fits.n_tot` was plotting with no data points despite data being present.
    - Identified and fixed an issue in `plot_manager.__array_finalize__` where assigning `self.plot_options = getattr(obj, 'plot_options', None)` was corrupting the `datetime_array` during numpy view/copy operations. Commenting out this assignment resolved the data loss between the data class and `plotbot_main`.
    - The plot *still* showed "0 points", indicating the remaining issue lies in the plotting logic itself (likely time range filtering).
- **Simplification of `proton_fits_class.py`:** After significant confusion caused by AI errors regarding file state and Git history, confirmed the following:
    - The complex Calculate What You Need (CWYN) refactoring attempt (involving `@property`, lazy-loading `__getattr__`, caching, and helper methods) introduced after commit `89aeb7d` was the likely source of instability and confusion.
    - Through a combination of manual debugging edits and mistaken AI file operations, the current working copy of `plotbot/data_classes/psp_proton_fits_classes.py` **is effectively equivalent to the state intended by reverting to commit `89aeb7d` and removing its initial CWYN structure lines**. 
    - This current state correctly handles CDF variable names (e.g., `Epoch`, `n_tot`) and uses a simpler, eager calculation model within `calculate_variables`, mirroring the working structure of `psp_mag_classes.py`.
    - Calculations requiring external dependencies (like `vsw_mach`) are currently stubbed out (assigned `None`) within `calculate_variables`.
- **Current Goal:** Stabilize the simplified `proton_fits_class` and resolve the remaining plotting issue ("0 points" error) by:
    1. Re-applying the necessary `plot_manager.__array_finalize__` fix (commenting out the line).
    2. Ensuring the state restoration loop in `proton_fits_class.update` is active.
    3. Cleaning up all temporary debug prints added during the previous session.
    4. Running the `test_plotbot_basic_fits_call` test to confirm basic plotting works.
    5. If the "0 points" issue persists, add targeted debugging *within the plotting function* (likely in `Plotbot.ipynb` based on earlier search) to inspect time filtering. 

### Continued FITS Plotting Debugging (`n_tot`) - May 2nd

We continued the deep dive into why `proton_fits.n_tot` fails to plot correctly in tests, specifically hitting `AssertionError: n_tot should have a populated datetime_array` in `tests/test_fits_cdf_server_integration.py::TestFitsCdfIntegration::test_plotbot_with_sf00_cdf_variable`.

**Key Learnings (Re-confirmed from prior sessions):**

1.  **Data Cubby Key Fix (Still Valid):** The fix in `plotbot/get_data.py` (around line 325) ensuring `data_cubby.stash` uses the `class_name` (e.g., `'proton_fits'`) instead of the `data_type` (e.g., `'sf00_fits'`) as the key is **correct and essential**. This prevents `plotbot_main` from grabbing an outdated instance from the cache. This fix remains in place.
2.  **Datetime `dtype` Fix (Still Valid):** The fix in `plotbot/data_classes/psp_proton_fits_classes.py` within `calculate_variables`, ensuring `self.datetime_array = np.array(datetime_list, dtype='datetime64[ns]')` is created with an explicit `dtype`, is **correct and essential**. This allows NumPy comparisons in functions like `time_clip` to work correctly. This fix remains in place.
3.  **State Restoration Logic (Still Valid):** The logic within the `proton_fits_class.update` method to *explicitly skip* restoring the `datetime_array` from the old state is crucial. It prevents the freshly calculated `datetime_array` (created by `calculate_variables` and passed to `set_ploptions`) from being overwritten by the potentially `None` value saved before the update. This fix also remains in place.

**New Comparison Test (`test_cdf_mag_fits_comparison.py`):**

To isolate potential underlying differences in the source data files, we created a new test: `tests/test_cdf_mag_fits_comparison.py`.

*   **Purpose:** Directly load and compare the structure and variable details of a "problematic" FITS CDF (`spp_swp_spi_sf00_fits_2024-04-01_v00.cdf`) and a "working" MAG CDF (`psp_fld_l2_mag_RTN_4_Sa_per_Cyc_20240327_v02.cdf`).
*   **How to run:** `conda run -n plotbot_env pytest -sv tests/test_cdf_mag_fits_comparison.py`
*   **Key Findings from Comparison:**
    *   **Time Variable Names Differ:** FITS uses `'Epoch'`, MAG uses `'epoch_mag_RTN_4_Sa_per_Cyc'`.
    *   **Time Variable Types Differ:** FITS `Epoch` is `CDF_EPOCH` (Type 31), MAG time is `CDF_TIME_TT2000` (Type 33). *Crucially, `cdflib.cdfepoch.to_datetime` is designed to handle both of these types.*
    *   **Data Variable Shapes Differ:** FITS `'n_tot'` is scalar (Shape `(N,)`). MAG `'psp_fld_l2_mag_RTN_4_Sa_per_Cyc'` is vector (Shape `(M, 3)`), representing (Br, Bt, Bn). The MAG class correctly handles this unpacking.
    *   **Data Variable Types Differ:** FITS `'n_tot'` raw data type is `int64`. MAG data components are `float32`.

**Current Hypothesis:**

The `int64` data type of the raw `n_tot` variable in the FITS CDF is the most likely remaining culprit. While Matplotlib *can* plot integers, some part of the processing pipeline within `proton_fits_class`, `ploptions`, `plot_manager`, or `plotbot_main` might be implicitly expecting float data for calculations or scaling, leading to the failure observed in the test assertion (where `var_pm.datetime_array` ends up empty or `None`).

**Update - The `y_limit` Mystery:**

Further detailed debugging within the `proton_fits_class.update` state restoration loop revealed something extremely unexpected:
- The `datetime_array` within the `n_tot` plot manager's `plot_options` object survives the `calculate_variables` and `set_ploptions` calls correctly.
- It also survives the restoration of *most* other attributes (like `plot_type`, `color`, `y_scale`, etc.) from the old state dictionary.
- However, the `datetime_array` becomes `None` *immediately after* the line `setattr(var.plot_options, 'y_limit', value)` executes during the restoration for `n_tot`.
- Skipping the restoration of `y_limit` (along with the already-skipped `datetime_array`) prevents the `datetime_array` from being lost and allows the test assertion `system_check("Has populated datetime_array", has_time, ...)` to pass.
- The underlying reason why setting `y_limit` via `setattr` on the `ploptions` instance wipes out the `_datetime_array` attribute is completely unclear, as there is no obvious code linkage between these attributes in `ploptions.py`.

**Revised Next Step:**

1.  Apply the pragmatic fix: Permanently modify the state restoration loop in `proton_fits_class.update` to explicitly skip restoring *both* `datetime_array` and `y_limit`.
2.  Clean up the extensive debug prints added.
3.  Re-run the `test_plotbot_with_sf00_cdf_variable` test. While the assertion about `datetime_array` presence should now pass, we need to investigate if the plot is *actually* generated correctly or if the original visual emptiness / "0 points" issue remains.
4.  If the plot is still empty, focus debugging efforts on the plotting functions themselves (e.g., `plotbot_main.py`'s scatter plot logic, potentially `plotbot_helpers.time_clip` again, or Matplotlib interactions).

**Previous Hypothesis Update:** The `int64` type for `n_tot` was *not* the cause of the `datetime_array` loss during state restoration, as forcing `float64` did not fix the issue. However, it *might* still be related to downstream plotting issues if the plot remains empty. 

**Comparison with HAM Tests & Refined Hypothesis:**

We ran the `tests/test_ham_freshness.py` suite to compare against a 'working' example (after fixing several `ValueError` bugs in `plot_manager.__new__` related to debug prints handling numpy arrays in boolean checks, which allowed the HAM tests to pass).

*   **HAM Success:**
    *   The HAM tests confirmed the core pipeline (`get_data` -> `update` -> `set_ploptions` -> `plot_manager` creation) works.
    *   `plot_manager.__new__` received valid data and `plot_options` with a pre-populated `datetime_array`.
    *   The `ham_class.update` method uses a simple state restoration loop (restoring all attributes).
    *   The tests primarily check the length of the data within the `plot_manager` instance itself (`len(var_plot_manager)`).

*   **FITS Failure Path (`n_tot`):**
    *   Logs confirm data loading (`calculate_variables`) and `plot_manager` creation (`set_ploptions` calling `plot_manager.__new__`) appear correct, with valid data and `plot_options.datetime_array` being passed and set.
    *   The `proton_fits_class.update` uses the complex state restoration skipping `datetime_array` and `y_limit`.
    *   Logs *within* the `update` method show `plot_options.datetime_array` **is valid** after the restoration loop finishes.
    *   However, the test assertion `assert len(var_pm.datetime_array) > 0` (where `var_pm = getattr(proton_fits, 'n_tot')`) fails because accessing the `datetime_array` *property* at that point returns `None`.

*   **The Lingering Contradiction & Hypothesis:** The `plot_options.datetime_array` associated with the `n_tot` `plot_manager` is valid at the end of the `proton_fits_class.update` method but appears to be `None` when accessed via the property getter (`return self.plot_options.datetime_array`) immediately afterwards in the test script. This suggests the value is being lost/nulled **between the end of the `update` method (or potentially the end of the plotting loop in `plotbot_main.py`) and the test script's check.** Possible culprits include the plotting code itself inadvertently modifying the object, an object identity issue with `data_cubby`, or a subtle bug in the `plot_manager.datetime_array` property getter under specific conditions. 

**Pushing to Remote:**

- **Version:** `2025-05-01_v1.01`
- **Commit Message:** `fix: Pass HAM tests after fixing plot_manager, update logs with y_limit discovery`
- **Summary:** Includes fixes to `plot_manager.__new__` debug prints allowing HAM tests to pass, documentation of the FITS vs HAM comparison, and the mysterious `y_limit` state restoration bug findings. 