# Captain's Log - 2025-04-24

**Session Start:**
 
*   Reviewed `README.md`, `docs/pyspedas_code_integration.md`, and the empty `docs/pyspedas_download.ipynb`.
*   Closed the previous log (`captains_log_2025-04-23.md`).
*   Ready for next steps on `pyspedas` integration. 

**Key Files & Plans:**

*   `docs/pyspedas_code_integration.md`: Outlines the strategy and steps for integrating `pyspedas` into Plotbot for data acquisition from CDAWeb.
*   `docs/pyspedas_download_examples.py`: Contains example `pyspedas` function calls for downloading various PSP data products (FIELDS MAG, SPAN-i, SPAN-e).

**Pyspedas Integration Testing:**

*   Created `tests/test_pyspedas_download.py` to test `pyspedas` download functionality (`downloadonly=True`).
*   This test verifies if `pyspedas` downloads files to the expected local directory structure (matching the current Berkeley structure defined in `psp_data_types.py`) and uses a consistent base filename pattern.
*   Uses the `no_update` loop strategy and parameters from `docs/pyspedas_download_examples.py`.
*   Refactored the test to use the standard `test_pilot` structure (`@pytest.mark.mission`, `phase`, `system_check`). 

**Pyspedas Test Learnings (Summary):**

*   Ran `tests/test_pyspedas_download.py` focusing on `downloadonly=True` behavior.
*   **Key Finding:** `pyspedas` functions return the relative path(s) of downloaded/local files, eliminating the need for unreliable `glob` checks immediately after long downloads.
*   Confirmed `pyspedas` download directory structure matches Berkeley expectations.
*   Confirmed base filenames match (case-insensitive).
*   Identified consistent case mismatches (e.g., `l3` vs `L3`) between `pyspedas` output and Berkeley patterns, but confirmed Plotbot's file search is already case-insensitive.
*   Confirmed long download times for some data types explain previous test failures.
*   The `no_update` loop is slightly less performant than the default `pyspedas` check.
*   **See `docs/pyspedas_code_integration.md` section 8 for detailed notes and implications.** 

**Offline Pyspedas Behavior Test:**

*   Added a new test `test_offline_download_behavior` to `tests/test_pyspedas_download.py`.
*   **Goal:** Compare standard `pyspedas` download check (`downloadonly=True`) vs. the `no_update=[True, False]` loop strategy when offline.
*   **Procedure:**
    1.  Ensure file exists locally (online).
    2.  Prompt user to disconnect internet.
    3.  Attempt standard check (now commented out).
    4.  Attempt `no_update` loop check.
    5.  Compare results.
*   **Key Finding:**
    *   The standard `pyspedas` check (even with `downloadonly=True`) attempts to contact the remote index when called. When offline, this fails silently (returns `[]`), making it unreliable for checking local files offline. This test phase was commented out after confirming this failure.
    *   The `no_update=[True, False]` loop strategy works correctly offline. Specifically, the `no_update=True` call immediately and quickly identifies the local file without attempting network access.
*   **Conclusion:** The `no_update=True` check is the reliable method for checking local `pyspedas` files when offline. 

---

**Git Push:**
*   Version Tag: `2025_04_24_v1.00`
*   Commit Message: `Feat: Add offline pyspedas check test & update plan`

## Entry 2025-04-24 (Continued)

**Summary:**
- Refactored data download functionality:
    - Renamed `plotbot/data_download.py` to `plotbot/data_download_berkeley.py`.
    - Renamed the core Berkeley download function from `download_new_psp_data` to `download_berkeley_data`.
    - Updated imports and function calls in `get_data.py`, `multiplot.py`, `audifier.py`, `showdahodo.py`, and `plotbot_main.py` to use the new module and function names.
    - Added placeholder comments (`# TODO`) regarding future configuration server checks.
    - Created a new file `plotbot/data_download_pyspedas.py` with a basic structure for the SPDF download function (`download_spdf_data`), including `PYSPEDAS_MAP`.
- Created a new, fast smoke test file `tests/test_all_plot_basics.py`.
- This test includes basic checks for `plotbot`, `multiplot`, and `showdahodo` using only `mag_rtn_4sa` data for a short interval.
- Debugged `tests/test_all_plot_basics.py`, specifically adjusting assertions for `plotbot` (doesn't return fig/axs) and `multiplot` (handles single-panel return types flexibly) until all tests passed.

**GitHub Push:**
- **Commit Message:** `Refactor: Rename data download modules and functions, add basic plot test`
- **Version Tag:** `2025_04_24_v1.01` 

## Entry 2025-04-24 (Attempt 2 at Config Logic)

**Summary:**
- **Failed Attempt:** Attempted to integrate the `config.data_server` logic into `get_data.py`. The implementation incorrectly modified the core existing logic instead of creating a simple conditional fork for the download step.
- **Clarification of Correct Approach:** The intended next step is to modify `get_data.py` *minimally*. Within the main loop processing standard data types, the single call to `download_berkeley_data` should be replaced by an `if/elif/else` block based on `config.data_server`. This block will conditionally call either `download_spdf_data` or `download_berkeley_data` (or try SPDF then Berkeley for `dynamic` mode), leaving the surrounding data checking and import logic unchanged.

**Status:** Code reverted. Ready to re-attempt the config logic implementation correctly. 

## Entry 2025-04-24 (Continued... Again)

**Summary:**
- Implemented conditional data download logic in `plotbot/get_data.py`:
    - Added import for `plotbot.config` and `plotbot.data_download_pyspedas.download_spdf_data`.
    - Replaced the direct call to `download_berkeley_data` with an `if/elif/else` block based on `config.data_server` (defaulting to `'dynamic'`).
    - This block conditionally calls `download_spdf_data` or `download_berkeley_data`.
- Created `plotbot/config.py` file with the `data_server` configuration variable and documentation.
- Verified the changes by running `tests/test_all_plot_basics.py` and `tests/test_showdahodo.py::test_basic_functionality`, both passed successfully.
- Updated `docs/pyspedas_code_integration.md` to reflect the completion of Step 3 (Dispatch Logic modification). 

**GitHub Push:**
- **Commit Message:** `Feat: Implement conditional download logic in get_data`
- **Version Tag:** `2025_04_24_v1.02` 

## Entry 2025-04-24 (Configuration Refactor)

**Current Task:** Refactoring the configuration system. The goal is to move the data type definitions (currently a dictionary in `plotbot/data_classes/psp_data_types.py`) into a dedicated `PlotbotConfig` class. This class will manage the configuration and provide a structured way to access and potentially modify settings (like the `data_server` mode needed for testing). The aim is to make this accessible globally, likely via `plotbot.config`. 

## Entry 2025-04-24 (Berkeley vs SPDF Variable Comparison)

**Summary:**
- Added a new test `test_compare_berkeley_spdf_vars` to `tests/test_pyspedas_download.py`.
- **Goal:** Verify that the internal variable names within CDF files are consistent, regardless of whether the file originates from Berkeley or SPDF.
- **Process:**
    - The test uses a helper function `_get_internal_vars` to run `plotbot` in both `'berkeley'` and `'spdf'` modes for a set of test variables (`mag_rtn_4sa.br`, `mag_sc_4sa.bx`, `proton.vr`, `epad.strahl`).
    - It finds the relevant CDF files loaded/downloaded by `plotbot` for each mode.
    - It extracts the list of all variable names from the CDFs using `cdflib`.
    - It compares the variable lists between the two modes for each data type.
- **Debugging:** Required multiple rounds of debugging to fix:
    - Import conflicts (`plotbot` module vs function).
    - Incorrect glob patterns in `_find_cdf_files` (double `_v*` wildcard, missing `{data_level}` formatting, missing `{date_str}` formatting).
    - Incorrect `cdflib` usage (using non-existent `.varnames()` instead of `cdf_info()` + `.rVariables` / `.zVariables`).
    - Type mismatch in comparison logic (`list` vs `set`).
- **Result:** The test now passes, confirming that for the tested data types, the internal CDF variable names are identical between the Berkeley-style and SPDF-style files.

**GitHub Push:**
- **Commit Message:** `Test: Add and pass Berkeley vs SPDF variable comparison test`
- **Version Tag:** `2025_04_24_v1.03` 