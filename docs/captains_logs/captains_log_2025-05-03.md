# Captain's Log: 2025-05-03

## Major Updates

### 1. Multiplot: HAM as Right Axis Option
- Integrated HAM data as a right axis (twinx) option in multiplot.
- All right axis elements (label, ticks, tick labels, spines, and legend) now fully support rainbow color mode, matching the left axis and panel color.
- Legend label and border also colorized in rainbow mode for visual consistency.

### 2. Multiplot Examples Expanded
- Added two new HAM plot examples to `Multiplot_Examples.ipynb` to demonstrate the new right axis HAM integration and rainbow styling.

### 3. Multiplot Preset Beautification
- Improved multiplot preset settings:
    - Increased default tick length for better visibility.
    - Ensured all border, tick, and label settings are visually consistent and modern.
    - Cleaned up legend appearance and color logic.

### 4. Testing
- Ran the full stardust test suite (`tests/test_stardust.py`).
- All tests passed, confirming that multiplot, HAM integration, and all new styling features are stable.

---

## Version Control Update (2025_05_03_v1.10)
- **Pushed to main branch.**
- **Commit Message:** feat: v1.10: Add Zarr file management test suite, document new data pipeline groundwork (2025_05_03_v1.10)
- **Version Tag:** 2025_05_03_v1.10
- **Git hash copied to clipboard.**
- This is now the latest version and the new mainline.

- v1.9 (HAM multiplot integration, beautified defaults) is now the mainline. 

### 5. Zarr File Management Test Suite Added
- Created `tests/test_zarr_file_io.py` to thoroughly test Zarr file read/write, directory mirroring, and CDF-to-Zarr conversion.
- Tests include:
    - Mirroring directory structure for dummy files.
    - Writing/reading single and multi-column Zarr files.
    - Importing CDF files and verifying magnetic field components.
    - Simulated PSP chunk Zarr save and reload.
    - Checking CDF file coverage and mirroring to Zarr.
- Each test prints headers and first 5 rows before/after save, and includes a note to document learnings in the captain's log.
- This suite lays the groundwork for robust Zarr-based data management in Plotbot.

### 6. Refactoring Out Legacy 'Derived' Data Class and Terminology
- Decided to remove the legacy 'derived' data class and all related code paths, as these are no longer used and have been replaced by the 'custom' variable system.
- The detailed process and rationale for this refactor are documented in `docs/refactoring_log/derived_to_custom_refactoring.py`.
- This refactor will help streamline the codebase and reduce confusion between old and new systems.
- **Next Task:** Continue searching for and removing any remaining references or 'ghosts' of the old 'derived' code to further simplify and modernize the codebase.

### 7. Next Refactoring Steps: Remove All Remaining Legacy 'derived' Code
- Begin systematically removing all remaining references and code paths related to the legacy 'derived' variable system.
- **Key files and actions:**
    - `data_cubby.py`: Remove special handling for 'derived' in `grab` and `grab_component` methods.
    - `get_data.py`: Remove the 'derived' data type check and any related comments.
    - `plot_manager.py`: Update any default plot options or metadata that still use 'derived' to use 'custom_class'/'custom_data_type' or a generic placeholder.
    - `print_manager.py`: Optionally, remove or further document legacy 'derived' debug methods and properties.
- Confirmed: `custom_variables.py` is fully decoupled from any legacy derived system.
- As each change is made, document the removal and any findings in this captain's log.

## Next Steps
- **Push these changes to the repository.**
- **Copy the git hash to clipboard after push.**
- **Review README** for any major learnings or changes to document.
- **Begin cleanup of legacy derived variable code and plan Zarr integration.**

### Recent Actions
- **Removed all legacy 'derived' variable handling from `data_cubby.py`** (grab and grab_component methods). This included special-case debug and time validation logic that is no longer used.
    - Ran `tests/test_all_plot_basics.py` after the change; all tests passed, confirming no impact on core plotting or data retrieval.
- **Removed the legacy 'derived' data type check from `get_data.py`.** This check was a vestige of the old system and is no longer needed.
    - Ran `tests/test_all_plot_basics.py` after the change; all tests passed, confirming no impact on core plotting or data retrieval.
- **Removed the last fallback and error handling for 'derived' plot_options in `plot_manager.py`.** Now, plot_manager requires explicit plot_options and will raise an error if not provided, eliminating all legacy 'derived' code paths.
    - Condensed debug prints for plot_options to a single line and improved [CUBBY] output formatting for clarity.
    - Ran `tests/test_all_plot_basics.py` and `tests/test_custom_variables.py` to confirm all changes are stable and the codebase is now fully explicit and clean regarding variable instantiation and plot options.
- **Completed the final sweep to remove all legacy 'derived' code, methods, properties, and type stubs from the codebase.** This included:
    - Purging all 'derived' debug methods, properties, and aliases from `print_manager.py` and its .pyi stub.
    - Cleaning up PLOT_ATTRIBUTES and related comments in `plot_manager.py`.
    - Updating all test and documentation language to use 'custom variable' instead of 'derived variable'.
    - Verified that no code, test, or type stub references the legacy 'derived' system.
    - Ran `tests/test_plotbot.py` and `tests/test_stardust.py`; all tests passed, confirming the codebase is now fully modernized and explicit in its custom variable handling.

## Version Control Update (2025_05_03_v1.92)
- **Pushed to main branch.**
- **Commit Message:** refactor: v1.92: Remove all legacy derived code, update tests and stubs to custom variable system
- **Version Tag:** 2025_05_03_v1.92
- **Git hash copied to clipboard.**

## Version Control Update (2025_05_03_v1.93)
- **Pushed to main branch.**
- **Commit Message:** fix: v1.93: Add missed changes from previous commit (unsaved files now included)
- **Version Tag:** 2025_05_03_v1.93
- **Details:** This commit includes notebook and code changes that were not saved/staged in the previous push.
- **Git hash copied to clipboard.**

### 8. Installer Script Flexibility & README Consistency Fix
- Updated `install_scripts/2_setup_env.sh` to robustly source conda from all common install locations, making the installer script portable and reliable for all users regardless of their conda setup.
- Fixed all README references to use the correct lowercase `install_scripts` folder, preventing case-sensitivity errors on macOS and Linux.
- Verified that all script-to-script calls already use the correct lowercase folder.
- No changes needed in the scripts themselves beyond the universal conda sourcing block.

## Version Control Update (2025_05_03_v1.94)
- **Pushed to main branch.**
- **Commit Message:** fix: v1.94: Make installer script universally robust to conda location, fix README folder casing
- **Version Tag:** 2025_05_03_v1.94
- **Git hash copied to clipboard.** 

### 9. Zarr/Xarray Chunking Dependency: Dask Required (DONE)
- Discovered during the Zarr integration test suite that xarray/zarr chunking requires the 'dask' library to be installed.
- Action: Add 'dask' to both the environment (conda/pip) and requirements files to ensure all Zarr-based tests and features work out of the box.
- This will prevent ImportError: chunk manager 'dask' is not available errors during Zarr file operations. 

### 10. CDF-to-Zarr Mirroring Test: Full Success
- Ran `test6_cdf_to_zarr_mirroring` in `tests/test_zarr_file_io.py`.
- The test:
    - Found all expected CDF files for the test range.
    - Created Zarr files in `data_cubby` with perfectly mirrored paths and filenames.
    - Loaded data back from Zarr and confirmed it matches the original CDF data.
    - Verified every CDF file has a corresponding Zarr file in the mirrored structure.
- **Result:** Test passed with no errors. This proves the core Zarr file management and mirroring logic is robust and matches the intended pipeline.
- This is a major validation for the Zarr integration effort—future work can confidently build on this foundation. 