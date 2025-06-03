# Captain's Log - 2025-05-29

## Summary of Session

- **Data Download Test (`test_data_download_from_berkeley`) Fixes:**
    - Identified that the parameterized test was failing for `mag_RTN_4sa` because it was incorrectly trying to access a `.bx` component instead of a valid RTN component like `.br`.
    - Corrected the parameterization for `mag_RTN_4sa` in `tests/test_data_download.py` to use `br`.
    - The initial assertion logic in the test was based on checking the length of the data array in the `plot_manager_instance`. This proved unreliable as different plot types might have differently structured data (e.g., scalar, multi-dimensional) that doesn't respond well to a simple `len()` check, or where `len() == 0` doesn't mean plotting failed.
    - Refactored the test's assertion: The test now primarily verifies that the `plotbot()` call completes without error (implying plotting was successful) and that the expected data files were actually downloaded locally. This is done by a new helper function `verify_downloaded_files_exist`.
    - Updated the instructional comments at the top of `tests/test_data_download.py` to provide clearer guidance on running individual parameterized tests using the `-k` flag and their `test_id_suffix`.

- **Proton Data Loading Optimization (br_norm Dependency Fix - User-Provided Definitive Explanation):**
    - **The Core Problem:** The excessive loading of `proton.sun_dist_rsun` (a dependency for `mag_rtn_4sa.br_norm`) occurred because `mag_rtn_4sa_class._current_operation_trange` was being set to `None`. This forced `_calculate_br_norm` (within `psp_mag_rtn_4sa.py`) to use its internal fallback logic, which derived the dependency time range from the wide, merged `self.datetime_array` of the `mag_rtn_4sa` instance, instead of the specific user-requested time range for the current operation.

    - **The Broken Chain (BEFORE THE FIX):**
        1.  **`plotbot_main.py`**: Called `get_data` with the correct user `trange`.
        2.  **`get_data.py`**: Called `data_cubby.update_global_instance`, correctly passing the `trange` as `original_requested_trange`.
        3.  **`data_cubby.py` (THE BUG):** In the `update_global_instance` method, when calling the specific data class's update method (e.g., for `mag_rtn_4sa`), the call was made *without* the `original_requested_trange` parameter:
            ```python
            # In data_cubby.py -> update_global_instance (Simplified representation of the problematic call path)
            global_instance.update(imported_data_obj)  # ❌ original_requested_trange was MISSING
            ```
        4.  **`mag_rtn_4sa_class.update()`**: Received `original_requested_trange` as `None` (its default value because it wasn't passed from `data_cubby.py`). This resulted in `self._current_operation_trange` being set to `None`.
        5.  **`_calculate_br_norm()` (in `psp_mag_rtn_4sa.py`)**: Checked `self._current_operation_trange`, found it was `None`, and then executed its fallback logic, using the full `self.datetime_array` to fetch dependencies.

    - **The Exact Fix (The Change Made):**
        - The single most critical change was modifying the call within **`data_cubby.py`'s `update_global_instance` method** to correctly pass the `original_requested_trange` to the data class's `update` method.
            ```python
            # In data_cubby.py -> update_global_instance (Simplified representation of the FIXED call path)
            # The call was changed from:
            # global_instance.update(imported_data_obj)
            # TO (conceptual change, actual implementation involved a try-except block):
            global_instance.update(imported_data_obj, original_requested_trange=original_requested_trange)
            ```

    - **The Fixed Chain (AFTER THE FIX):**
        1.  **`plotbot_main.py` & `get_data.py`**: Remained the same, correctly passing `original_requested_trange`.
        2.  **`data_cubby.py` (FIXED):** The `update_global_instance` method was modified. The call to the data class's `update` method now includes `original_requested_trange`:
            ```python
            # Actual implementation in the fixed data_cubby.py:
            try:
                global_instance.update(imported_data_obj, original_requested_trange=original_requested_trange)
            except TypeError as te: # Handle classes not expecting original_requested_trange
                if "unexpected keyword argument" in str(te) or "takes" in str(te):
                    global_instance.update(imported_data_obj)
                else:
                    raise te
            ```
            For `mag_rtn_4sa` (which *does* accept `original_requested_trange`), this call now successfully goes through the `try` block, passing the parameter.
        3.  **`mag_rtn_4sa_class.update()`**: Now receives the correct `original_requested_trange` (e.g., the specific user trange like `['2023-09-29/00:00:00.000', '2023-09-29/23:59:59.999']`). This correctly sets `self._current_operation_trange`.
        4.  **`_calculate_br_norm()` (in `psp_mag_rtn_4sa.py`)**: Now finds `self._current_operation_trange` populated with the specific user trange. The condition `if hasattr(self, '_current_operation_trange') and self._current_operation_trange is not None:` becomes true, and `trange_for_dependencies` is set to this specific, narrow range. The problematic internal fallback in `_calculate_br_norm` is no longer reached for this reason.

    - **Secondary Improvement (Robustness in `_calculate_br_norm`):** Independently, the internal fallback logic within `_calculate_br_norm` (the one that used `self.datetime_array`) was also removed. This makes `_calculate_br_norm` more robust: if `_current_operation_trange` were `None`, an error occurs rather than incorrect data loading.

- **Data Download Midnight Handling:**
    - Corrected logic in `plotbot/data_download_berkeley.py` to ensure that requests ending at midnight (e.g., 'YYYY-MM-DD 00:00:00') correctly adjust the end time to the very end of the previous day (23:59:59.999999). This prevents missing the last segment of data for the intended final day or incorrectly starting to look for data on the specified midnight day itself.

- **Repository Cleanup:**
    - Moved large notebook file `Eall_ham_v0.ipynb` to the `local_tests_and_utils/` directory, which is gitignored. This prevents the file from being tracked and included in the main repository, reducing clone/download size for other users.

- **Git Push:**
    - Version: `v2.52` (Date: 2025-05-29)
    - Commit Message: `v2.52 Fix: Corrected data download tests, proton class update logic for trange, and midnight handling in downloads.`

- **Git Push:**
    - Version: `v2.53` (Date: 2025-05-29)
    - Commit Message: `v2.53 Chore: Moved Eall_ham_v0.ipynb to gitignored local_tests_and_utils directory.`

- **Git Push (Log Update):**
    - Version: `v2.54` (Date: 2025-05-29)
    - Commit Message: `v2.54 Docs: Precisely updated Captain's Log re: br_norm dependency fix mechanism.`

- **Git Push (Final Log Update):**
    - Version: `v2.55` (Date: 2025-05-29)
    - Commit Message: `v2.55 Docs: Final precise clarification of br_norm dependency fix in Captain's Log.`

- **Git Push (User-Provided Definitive Log Update):**
    - Version: `v2.57` (Date: 2025-05-29)
    - Commit Message: `v2.57 Docs: User-provided definitive clarification of br_norm dependency fix (data_cubby.py parameter omission).`

- **Git Push (Corrected Version - Definitive Log Update):**
    - Version: `v2.54` (Date: 2025-05-29)
    - Commit Message: `v2.54 Docs: User-provided definitive clarification of br_norm dependency fix (data_cubby.py parameter omission).`

## Issues Encountered & Debugging

- **Excessive Data Loading for `br_norm` Dependencies (User-Provided Definitive Root Cause & Resolution):**
    - **Problem:** `proton.sun_dist_rsun` (dependency for `mag_rtn_4sa.br_norm`) was loaded for wider time ranges than the specific user request.
    - **Definitive Cause:** The primary bug was in `plotbot/data_cubby.py`'s `update_global_instance` method. In the execution path relevant to `mag_rtn_4sa`, the call to `global_instance.update()` was previously made *without* passing the `original_requested_trange` parameter. This caused `mag_rtn_4sa_class._current_operation_trange` to be `None`.
    - Consequently, `_calculate_br_norm` in `psp_mag_rtn_4sa.py`, finding `_current_operation_trange` as `None`, would trigger its own internal fallback logic, deriving a wide dependency time range from the `mag_rtn_4sa` instance's full (potentially merged) `datetime_array`.
    - **Resolution:**
        1.  **Corrected `data_cubby.py`:** The call `global_instance.update()` within `data_cubby.py` was modified to correctly pass `original_requested_trange=original_requested_trange`. This was implemented within a `try-except TypeError` block to also gracefully handle other data classes that might not (yet) accept this new parameter. For `mag_rtn_4sa`, this ensures it receives the specific `trange`.
        2.  **Strengthened `_calculate_br_norm()`:** The internal fallback logic within `_calculate_br_norm` (the one that used `self.datetime_array`) was removed. This ensures that if `_current_operation_trange` is `None`, an error occurs rather than incorrect data loading.

## Next Steps

- Ensure the `try-except TypeError` block in `data_cubby.py` correctly handles all data classes, allowing those that expect `original_requested_trange` to receive it, and those that don't to update via the fallback without error.
- Confirm `mag_rtn_4sa_class.update()` and other relevant classes correctly process the passed `original_requested_trange`.
- Maintain test coverage for non-contiguous time ranges and `br_norm` calculations.

## Audit of Data Class Attribute Handling and "Sticky Note" Adoption (Snapshot Context) - 2025-05-29 Continued

Following an investigation into snapshot loading behaviors and `setattr` warnings, an audit of data classes was performed to clarify attribute handling and the adoption of the "sticky note" (`original_requested_trange`) logic.

**1. Adoption of "Sticky Note" (`original_requested_trange`) Logic:**

This "sticky note" system is crucial for ensuring that data classes, especially those with dependencies (like `mag_rtn_4sa.br_norm`), operate on the precise time range of the current user request. This prevents fetching or processing data for overly broad or incorrect time windows. The following classes have been explicitly updated to accept and utilize `original_requested_trange` in their `update` methods, primarily to set an internal `_current_operation_trange` attribute for accurate dependency fetching:

*   `mag_rtn_4sa_class` (as detailed in `psp_mag_rtn_4sa.py`)
*   `proton_class` (as detailed in `psp_proton.py`)
*   `epad_strahl_class` (representing `epad`, in `psp_electron_classes.py`)
*   `epad_strahl_high_res_class` (representing `epad_hr`, in `psp_electron_classes.py`)

This mechanism was a key fix detailed in the log entries for 2025-05-19 and its correct functioning was re-confirmed on 2025-05-29. Data classes not yet updated to accept `original_requested_trange` will be handled by the `except TypeError` block in `data_cubby.py` (meaning their `update()` method will be called without this specific time range parameter).

**2. Summary of `__getattr__` and `__setattr__` Behaviors for Key Data Classes:**

The way classes handle attribute getting and setting directly impacts snapshot restoration, especially when the `load_simple_snapshot` function attempts to copy attributes from a pickled object's `__dict__`.

*   **`mag_rtn_4sa_class` (`psp_mag_rtn_4sa.py`):**
    *   `__getattr__`: If an attribute is not found directly, it provides a "friend" message suggesting valid keys from its `raw_data`.
    *   `__setattr__`: Employs a whitelist. It allows setting for specific core attributes (like `datetime`, `datetime_array`, `raw_data`, `time`, `field`) or any key already present in its `raw_data` dictionary. Attempts to set other attributes are prevented, and a "friend" message is issued.

*   **`proton_class` (`psp_proton.py`):**
    *   `__getattr__`: If an attribute isn't found directly, it issues a warning and suggests available keys from its `raw_data`.
    *   `__setattr__`: More permissive than `mag_rtn_4sa`. It has an extensive whitelist of explicitly settable attributes. For attributes not on this list, it prints a warning but still allows the attribute to be set using `object.__setattr__`.

*   **`epad_strahl_class` & `epad_strahl_high_res_class` (`psp_electron_classes.py`):**
    *   These classes (representing `epad` and `epad_hr` respectively) have similar, strict handlers.
    *   `__getattr__`: Prints a "helper!" message and a "friend" error if an attribute is unrecognized, suggesting valid keys from `raw_data`.
    *   `__setattr__`: Strict. Allows setting only for a specific list of attributes (e.g., `datetime`, `datetime_array`, `raw_data`, `time`, `field`, `times_mesh`, `energy_index`, and importantly, `data_type` after recent discussion) or keys present in `raw_data`. Attempts to set other attributes are prevented, with a "helper!" and "friend" message. The previous omission of `data_type` from this whitelist was the cause of warnings during snapshot loading.

*   **`ham_class` (`psp_ham_classes.py`):**
    *   `__getattr__`: If an attribute is not a recognized `plot_manager` instance (or an internal `_` attribute), it raises an `AttributeError` with a custom message listing available plot managers.
    *   `__setattr__`: Most permissive among the audited classes. It simply calls `super().__setattr__(name, value)`, allowing any attribute to be set without restriction from its `__setattr__` method.

**Implications for Snapshot Restoration:**
The varied `__setattr__` behaviors are critical in the context of `load_simple_snapshot`:
*   The generic attribute copying loop in `load_simple_snapshot` (even after being improved to only iterate over keys present in the snapshot) can still conflict with strict `__setattr__` methods if an attribute from the saved object's `__dict__` is not on the class's whitelist.
*   This highlights the need for:
    *   Ensuring whitelists in custom `__setattr__` methods are comprehensive for all attributes that are part of the saved state and *should* be restored (e.g., the `data_type` for `epad` classes).
    *   Ideally, implementing robust `restore_from_snapshot(self, loaded_instance_dict)` methods within each data class. These methods would have explicit knowledge of which attributes to restore and how, potentially bypassing or carefully interacting with the class's own `__setattr__` for foundational attributes.

The recent fix to `load_simple_snapshot` (iterating only over keys present in the snapshot) has correctly stopped attempts to restore data for classes not actually saved (like the `mag_rtn_4sa` example from earlier). For classes *that are* saved, managing the interaction between their `__setattr__` and the attributes in the pickled `__dict__` is crucial.

## Snapshot Loading Refinement - `epad` `data_type` Warning Resolved - 2025-05-29 Continued

**Problem:**
Even after refining `load_simple_snapshot` to only process keys present in the snapshot file, a warning "`'data_type'` is not a recognized attribute, friend!" was still appearing specifically for `epad` (electron) data.

**Cause Analysis:**
*   The `epad_strahl_class` (and `epad_strahl_high_res_class`) uses a `restore_from_snapshot` method. This method iterates through the `__dict__` of the pickled object and uses `setattr(self, key, value)` to restore each attribute.
*   The `__init__` method of these electron classes correctly sets `object.__setattr__(self, 'data_type', 'spe_sf0_pad')` (or similar for high-res), meaning `'data_type'` is part of the pickled `__dict__`.
*   However, the custom `__setattr__` method in these electron classes had a whitelist of settable attributes that *did not* include `'data_type'`.
*   Therefore, when `restore_from_snapshot` called `setattr(self, 'data_type', ...)` , the custom `__setattr__` rejected it, causing the warning.
*   Other classes like `proton_class` did not show this warning because their `__setattr__` whitelist *did* include `'data_type'`, or like `ham_class`, had a permissive `__setattr__`.

**Resolution:**
*   The `__setattr__` methods within `epad_strahl_class` and `epad_strahl_high_res_class` (in `plotbot/data_classes/psp_electron_classes.py`) were modified.
*   The string `'data_type'` was added to the list of explicitly allowed attribute names in their respective `__setattr__` whitelists.

**Outcome:**
With `'data_type'` now recognized by the `__setattr__` methods of the electron classes, the `restore_from_snapshot` process no longer triggers the warning. Snapshot loading for `epad` data is now clean. This confirms the importance of ensuring `__setattr__` whitelists are consistent with attributes intended for restoration via methods like `restore_from_snapshot`.

## Git Push - 2025-06-02

*   **Version:** `2025_06_02_v2.56`
*   **Commit Message:** `v2.56 Fix: Refined snapshot loading logic and epad attribute handling for cleaner restores.` 