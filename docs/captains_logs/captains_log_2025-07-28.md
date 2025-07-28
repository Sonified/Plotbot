# Captain's Log 2025-07-28

## Updates:
- Moved `test_data_property_fixes.py`, `test_quick_spectral_fix.py`, `test_epad_debug.py`, and `test_epad_regression.py` from the root directory to the `tests/` directory.
- Renamed the moved test files with the prefix `test_07_28_` to group them: 
    - `test_07_28_data_property_fixes.py`
    - `test_07_28_quick_spectral_fix.py`
    - `test_07_28_epad_debug.py`
    - `test_07_28_epad_regression.py`
- Updated the `sys.path.insert` in `tests/test_07_28_quick_spectral_fix.py` to correctly reference the `plotbot` directory.
- Added `/files_from_Jaye/` to `.gitignore`. 
- Moved `migrate_psp_data.sh` to `local_tests_and_utils/`. 
- Confirmed `check_nans.py` is not used elsewhere in the codebase and remains in the root directory.
- Moved `wind_mag_poc_reference.py` to `wind_evaluation/` and refactored its relative import.
- Confirmed `wind_data_products_test.ipynb` and `wind_data_validation.ipynb` do not need refactoring after being moved to `wind_evaluation/`.
- Verified that the `data/` directory is correctly listed in `.gitignore`. 