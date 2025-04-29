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

--- Pushing Changes ---
- **Version Tag:** `2025_04_26_v1.11`
- **Commit Message:** `fix: Correct Pyspedas verbosity & cleanup notebooks`
  