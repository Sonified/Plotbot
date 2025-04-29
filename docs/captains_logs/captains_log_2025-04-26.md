# Captain's Log - April 26, 2025

## Activities & Learnings

- Basic plot tests in `tests/test_all_plot_basics.py` passed successfully.
- Staging and pushing numerous untracked/modified files that were missed in a previous commit.
  - Commit message: "chore: Add untracked files and update tests" 
- Reverted `Plotbot.ipynb` to the version from two commits prior (`origin/main~1`) to restore the correct content after an accidental overwrite.
  - Pushing this correct version with commit message: "fix: Revert Plotbot.ipynb to previous working version" 
- Fixed Pyspedas verbosity issue where INFO logs appeared even when `print_manager.pyspedas_verbose` was `False`. Corrected logic in `print_manager._configure_pyspedas_logging` to always apply/remove the filter based on the flag, regardless of `config.data_server`. Cleaned up diagnostic prints.
- Cleaned up main `Plotbot.ipynb` and created two new example notebooks: `Plotbot_Examples_Multiplot.ipynb` and `Plotbot_Examples_Custom_Variables.ipynb`.

## PKL Saving Fixes

- **Issue:** Encountered several issues with the daily PKL saving mechanism (`data_cubby.save_to_disk`) when testing (`test_pkl_integrity_and_cache_load`).
- **Fixes:**
    - Resolved a `NameError` in `get_data.py` related to the conditional stash logic introduced previously.
    - Corrected `__getattr__` methods in `psp_mag_classes.py` to properly raise `AttributeError`, preventing a `RecursionError` during `copy.deepcopy` needed for daily PKL creation.
    - Fixed case-insensitive regex matching (`flags=re.IGNORECASE`) for source CDF filenames within `save_to_disk` in `data_cubby.py`.
    - Corrected the `re.sub` pattern in `save_to_disk` to properly remove the `.cdf` extension when generating PKL filenames.
- **Outcome:** The `test_pkl_integrity_and_cache_load` now passes, confirming that daily PKL files are saved correctly, named appropriately, and loaded from cache as expected.

## Regex Debugging Saga (April 28, 2025)

- **Goal:** Test PKL saving for 6-hourly files (using `mag_RTN`) and ensure data spanning multiple days saves into separate daily PKLs (`test_pkl_saving_two_days`).
- **Initial Problem:** The integration test `test_pkl_saving_mag_rtn_hourly` started failing with `AssertionError: data_cubby_index.json was not created`. Debug output pointed to a failure in `save_to_disk` matching the source filename `psp_fld_l2_mag_RTN_2024092912_v02.cdf`.
- **Refactoring `save_to_disk`:** Instead of hardcoded daily/hourly regex, modified `save_to_disk` to dynamically build regex patterns based on the `file_pattern` and `file_time_format` specified in `plotbot/data_classes/psp_data_types.py`. This is a permanent architectural improvement.
- **Regex Mystery:** Despite the refactor pulling the correct pattern string (`psp_fld_l2_mag_RTN_(20\d{10})_v(\d{2})\.cdf`), the `re.search` call *still* reported "NO MATCH" for the filename within `save_to_disk`.
- **Mocking `test_pkl_saving_mag_rtn_hourly`:** To speed up testing and isolate `save_to_disk`, modified the test to mock the data import step (`import_data_function`) using `@patch`. This involved several steps to get the mock working correctly:
    - Identifying the correct patch target (`plotbot.get_data.import_data_function` after checking `plotbot_main.py` and `get_data.py`).
    - Correctly initializing the mock `DataObject` (it's a `namedtuple` requiring args at creation).
    - Ensuring the mock `DataObject` used TT2000 (`int64`) times, not `datetime64[ns]`, to avoid errors in downstream `cdflib` calls within `calculate_variables`.
- **The Breakthrough:** Realized the dynamically built regex pattern for 6-hourly data was incorrectly defined in `save_to_disk`. It used `(20\d{10})` (expecting 12 digits total: `20` + 10) instead of the correct `(20\d{8})` (expecting 10 digits total: `20` + 8) to match `YYYYMMDDHH` format like `2024092912`.
- **The Fix:** Corrected the `date_group` definition for `file_time_format == '6-hour'` inside `save_to_disk` to use `r'(20\d{8})'`.
- **Current Status:** With the regex fix, the mocked test `test_pkl_saving_mag_rtn_hourly` now passes. The specific regex matching issue is resolved.
- **Next Step:** Return to the original goal of verifying multi-day PKL splitting. Run the test `test_pkl_saving_two_days` to ensure it correctly saves data from 2024-09-28 and 2024-09-29 into separate daily PKL files using the fixed `save_to_disk` logic.

## Regex Case-Sensitivity Fix (April 28, 2025 - Continued)

- **Problem Follow-up:** The `test_pkl_saving_two_days` test failed with `AssertionError: data_cubby_index.json was not created`. Debug logs showed the dynamically generated regex pattern (mixed case from config) was not matching the actual lowercase SPDF filenames (`psp_fld_l2_mag_rtn_4_sa_per_cyc...cdf`).
- **The Fix:** Modified `save_to_disk` in `plotbot/data_cubby.py` to use the `re.IGNORECASE` flag when compiling the dynamic regex pattern (`re.compile(pattern_template, re.IGNORECASE)`).
- **Outcome:** The `test_pkl_saving_two_days` test now passes, confirming that PKL saving correctly handles case differences in filenames and saves data spanning multiple days into separate daily PKLs.

--- Pushing Changes (April 28, 2025) ---
- **Version Tag:** `2025-04-28_v1.01`
- **Commit Message:** `fix: Correct PKL save regex case sensitivity`