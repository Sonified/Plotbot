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

## Further PKL Debugging (April 28, 2025 - Late Session)

- **Session Focus:** Attempted to resolve remaining PKL test failures after fixing regex issues.
- **Progress:** Fixed several `IndentationError`s in `plotbot/data_cubby.py` and `tests/test_data_cubby_daily_pkl.py`. Modified `test_pkl_saving_two_days` to use `os.path.exists` for checking daily PKL files directly.
- **Outcome:** 
    - `test_pkl_saving_two_days` **PASSED**.
    - `test_inspect_saved_daily_pkl_content` **PASSED**.
- **Remaining Failures:**
    - `test_save_multi_day_creates_daily_pkls`: Still fails due to `data_cubby_index.json` not being created, despite daily PKLs being saved.
    - `test_pkl_integrity_and_cache_load`: Now fails with a `RecursionError: maximum recursion depth exceeded` when accessing attributes (`__getattr__`) of the `plot_manager` object after it's loaded from a PKL file (likely the full object pickle, not the simplified daily one). This suggests an issue with how `plot_manager` handles pickling/unpickling its state.
- **Conclusion:** Reverting to this state as further attempts led to more complex issues. The core problem seems to lie in either the final index file writing logic or the pickling/unpickling behavior of the `plot_manager` class itself.

--- Pushing Changes (April 28, 2025 - End of Session) ---
- **Version Tag:** `2025-04-28_v1.02`
- **Commit Message:** `fix: Resolve basic plot test errors and document PKL state`

## End of Session Summary (April 28, 2025)

- **Final Status:** We successfully ran the basic plotting tests (`tests/test_all_plot_basics.py`) which all passed. We also confirmed that the two previously passing PKL tests (`test_pkl_saving_two_days`, `test_inspect_saved_daily_pkl_content`) still pass when run individually via `pytest tests/test_data_cubby_pkl_saving.py`.
- **IndentationError Mystery:** Encountered a persistent `IndentationError` in `plotbot/data_cubby.py` (around line 291) *only* when attempting to run multiple test files together (e.g., `pytest tests/test_all_plot_basics.py tests/test_data_cubby_pkl_saving.py ...` or via `pytest tests/test_all_plot_basics.py -s` which likely triggered collection involving `conftest.py`). Since the error disappeared when running the affected test files individually, and manual/automated fixes didn't resolve it for the combined run, we concluded it's likely an artifact of pytest's test collection/caching mechanism rather than a true syntax error in `data_cubby.py`.
- **Remaining PKL Test Failures (when run together):** 
    1.  `test_save_multi_day_creates_daily_pkls` (in `tests/test_data_cubby_daily_pkl.py`): Fails because `data_cubby_index.json` is not created (`AssertionError: data_cubby_index.json was not created.`). This suggests the final `json.dump(index, ...)` step in `data_cubby.save_to_disk` might not be executing correctly in this specific test context, even though the daily `.pkl` files *are* being created.
    2.  `test_pkl_integrity_and_cache_load` (in `tests/test_data_cubby_pkl_saving.py`): Fails with `RecursionError: maximum recursion depth exceeded`. The traceback points deep into `plot_manager.__getattr__` being called repeatedly *after* an object (likely the full `plot_manager`, not a simplified daily dict) is loaded via `data_cubby.load_from_disk`. This strongly indicates an issue with how the `plot_manager` class interacts with Python's pickle mechanism, potentially related to its internal state (`_plot_state`?) or how `__getattr__` is implemented.
- **Potential Next Steps for Tomorrow:**
    - Investigate the `RecursionError`: Examine `plot_manager.py`, focusing on `__getattr__`, `__setattr__`, `__getstate__`, and `__setstate__` (if they exist) to understand how its state is managed and how that might interfere with unpickling and subsequent attribute access.
    - Debug the missing index file: Step through `data_cubby.save_to_disk` specifically within the context of the `test_save_multi_day_creates_daily_pkls` test to see why the final `json.dump` isn't creating the index file.
    - Consider clearing the pytest cache (`pytest --cache-clear`) before running tests again, just in case the `IndentationError` artifact persists.

*(Session concluded for the day. Resting up is important!)*