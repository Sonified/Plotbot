# Captain's Log - 2025-04-21: CWYN Phase 1 Plan

**Goal:** Implement a "Calculate What You Need" (CWYN) approach for standard data variables to improve efficiency by only calculating and storing the specific variables requested by the user, rather than all possible variables for a given data type. This focuses on optimizing the calculation step within the current data import and storage architecture.

**Key Modules Involved:**

*   `plotbot/get_data.py`
*   `plotbot/data_classes/psp_*.py` (e.g., `psp_mag_classes.py`)
*   `plotbot/data_tracker.py` (Usage remains the same)
*   `plotbot/data_cubby.py` (Usage remains the same)
*   `plotbot/data_import.py` (Usage remains the same)

**Proposed Changes:**

1.  **Identify Needed Subclasses (`get_data.py`):**
    *   Enhance `get_data` to not only identify the required `data_types` but also the specific *subclass names* (variable names like `'bmag'`, `'anisotropy'`) requested by the user for each standard data type.
    *   Store this information, perhaps as a dictionary like `needs = {'mag_rtn_4sa': ['bmag'], 'proton': ['anisotropy']}`.

2.  **Pass Needs to `update` (`get_data.py`):**
    *   Modify the call to the class instance's `update` method within `get_data` to include the list of needed subclass names for that specific `data_type`.
    *   Example: `instance.update(data_obj, needed_subclasses=needs.get(data_type, []))`

3.  **Modify Class `update` Method (e.g., `psp_mag_classes.py`):**
    *   Update the signature of the `update` method in the data classes to accept the optional `needed_subclasses` list (defaulting to an empty list or None).
    *   Pass this list along when calling `self.calculate_variables`.
    *   **Crucial Change:** If `update` is called because a variable needs calculation *but* the raw data import isn't needed (Scenario B: raw data covers time, but specific variable wasn't calculated yet), ensure `update` can trigger `calculate_variables` using the *existing* data within the instance (e.g., `self.field`, `self.datetime_array`) instead of requiring a fresh `imported_data` object. This might involve passing `None` for `imported_data` and having `calculate_variables` handle it.

4.  **Refactor `calculate_variables` Method (e.g., `psp_mag_classes.py`):**
    *   Modify the `calculate_variables` signature to accept `needed_subclasses`.
    *   Keep the loading of essential base raw data (e.g., `self.field`, `self.time`) if `imported_data` is provided. If `imported_data` is `None`, use the existing `self.field` etc.
    *   Wrap the calculation for each specific derived quantity (e.g., `bmag`, `pmag`) in a conditional block.
    *   The condition should check:
        *   Is this variable explicitly in `needed_subclasses`?
        *   Is a variable that *depends* on this one in `needed_subclasses`? (e.g., calculating `pmag` requires `bmag`).
        *   Has this variable *already* been calculated and stored in `self.raw_data` during a previous step within this `update` call (to avoid redundant calculation if multiple needed variables share a dependency)?
    *   Only perform the calculation if necessary based on the above checks.
    *   Store the result *only* in the corresponding key in `self.raw_data` (e.g., `self.raw_data['bmag'] = calculated_bmag`) if the calculation was performed. Do not clear out previously calculated variables from other calls.

5.  **Caching (`data_cubby` & `data_tracker`):**
    *   No changes needed. `data_cubby` still holds the single instance. `data_tracker` still tracks the time ranges for which raw data *import* has occurred. The caching of *calculated results* happens implicitly within the `self.raw_data` dictionary of the instance stored in the cubby.

**Expected Outcome:**

*   When `get_data` is called, the underlying `calculate_variables` method will only compute the specifically requested variables and their direct dependencies for the given time range.
*   Subsequent calls for *different* variables within the *same* cached time range will trigger `calculate_variables` again, but it will compute only the newly requested variables using the already-loaded raw data.
*   Computational efficiency is improved, especially for data types with many derivable quantities.
*   The data loading mechanism (`import_data_function`) remains unchanged – it still loads data based on the source file granularity for the entire requested `trange`.

**Refactoring & Cleanup (Post-Session Wrap-up):**

1.  **FITS Calculation Code:** Moved the unused, intermediate refactoring script `calculate_proton_fits.py` from `plotbot/calculations/` to `Jaye_Fits_Code/Jaye_fits_integration/calculations/` to keep it with related historical code.
2.  **Documentation Update:** Added a comment to the top of the moved `calculate_proton_fits.py` clarifying its origin (derived from `calculate_fits_derived.py`) and its current status (not directly used by `proton_fits_class`).
3.  **Directory Renaming:** Standardized directory naming conventions by renaming several folders to lowercase:
    *   `Docs` -> `docs`
    *   `Captains_Log` -> `captains_log` (Note: User moved this into `docs/`)
    *   `Refactoring_Log` -> `refactoring_log`
    *   `Example_Images` -> `example_images`
4.  **Documentation Path Update:** Corrected a path reference within `captains_log_2025_04_20.md` to reflect the new lowercase `docs/captains_logs/` directory name.
5.  **Test Runner:** Discussed the utility of `run_tests.py` and decided to keep it as a documented convenience script.

**Refactoring Plan (Post-Session):**

*   Detailed the `pyspedas`/CDAWeb integration plan in `docs/CDAWeb_Server_Integration.md`.
*   Adopted an audit-first approach, using `pyspedas` with `downloadonly=True` and `notplot=True`.
*   Key next steps identified: Ensure `pyspedas` is added to the environment/installer, then perform the critical audit comparing SPDF-downloaded CDF variable names against current expectations.
*   Created `docs/to_do_list.md` to track outstanding tasks, including lower-priority environment updates.

**Git Push:**
*   Version: `2025_04_21_v1.00`
*   Commit: `Refactor: Plan SPDF integration, fix FITS import bug, add comments`

---
**LOG CLOSED** 