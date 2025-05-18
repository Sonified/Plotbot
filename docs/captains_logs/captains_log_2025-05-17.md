# Captain's Log: 2025-05-17

## Bug Fix & Refactor: `data_type` Attribute Initialization

- **Issue:** A recurring error, `'data_type' is not a recognized attribute, friend!`, was observed. This typically occurred when methods like `update` or `__getattr__` were called on data class instances where the `data_type` attribute had not yet been set.
- **Root Cause:** The `data_type` attribute, while intended to be a core identifier for data classes, was not being explicitly initialized in the `__init__` method of several classes. Access attempts before it was dynamically set (e.g., during an update operation or by some other mechanism) would lead to an `AttributeError`.
- **Fix Implemented:**
    - Added explicit initialization of the `data_type` attribute in the `__init__` method for all affected data classes. This was done using `object.__setattr__(self, 'data_type', 'your_data_type_string_here')` to ensure the attribute is set when an instance is created.
    - Affected classes and their initialized `data_type` strings:
        - `plotbot/data_classes/psp_proton_classes.py`:
            - `proton_class`: `'spi_sf00_l3_mom'`
            - `proton_hr_class`: `'spi_af00_l3_mom'`
        - `plotbot/data_classes/psp_proton_fits_classes.py`:
            - `proton_fits_class`: `'psp_fld_l3_sf0_fit'`
        - `plotbot/data_classes/psp_alpha_fits_classes.py`:
            - `alpha_fits_class`: `'psp_fld_l3_sf1_fit'`
        - `plotbot/data_classes/psp_electron_classes.py`:
            - `epad_strahl_class`: `'spe_sf0_pad'`
            - `epad_strahl_high_res_class`: `'spe_hires_pad'`
        - `plotbot/data_classes/psp_ham_classes.py`:
            - `ham_class`: `'ham'`
- **Learning:** Ensured that essential identifying attributes like `data_type` are initialized directly in `__init__` to prevent `AttributeError` issues, especially when complex attribute access patterns (like those in `__getattr__` or instance update methods) are involved.

*(Log remains open for further updates on 2025-05-17)*

## Push: v2.31

- **Version Tag:** `2025_05_12_v2.31`
- **Commit Message:** `Fix: Initialize data_type in data classes to resolve attribute errors (v2.31)`
- **Summary:** Addressed attribute errors by explicitly initializing `data_type` in all relevant data classes (`psp_proton_classes`, `psp_proton_fits_classes`, `psp_alpha_fits_classes`, `psp_electron_classes`, `psp_ham_classes`). 

## Refactor Plan: Split `psp_mag_classes.py` and Update Imports

**Goal:** To improve maintainability and reduce complexity by splitting the monolithic `plotbot/data_classes/psp_mag_classes.py` file into individual files for each magnetic field data class and a shared utility file. This will also involve updating all necessary import statements across the codebase.

**Detailed Steps:**

**Phase 1: File and Class Restructuring**

1.  **Create Utility File (`_utils.py`):**
    *   File: `plotbot/data_classes/_utils.py` (Already created)
    *   Action: Move the `_format_setattr_debug(name, value)` function from `psp_mag_classes.py` into this file.
    *   Imports for `_utils.py`: `import numpy as np`, `import pandas as pd`.

2.  **Refactor `mag_rtn_4sa_class`:**
    *   New File: `plotbot/data_classes/psp_mag_rtn_4sa.py` (Already created)
    *   Action: Move the `mag_rtn_4sa_class` definition and its global instance creation (`mag_rtn_4sa = mag_rtn_4sa_class(None)`) from `psp_mag_classes.py` into `psp_mag_rtn_4sa.py`.
    *   Imports for `psp_mag_rtn_4sa.py`: `import numpy as np`, `import pandas as pd`, `import cdflib`, `from datetime import datetime, timedelta, timezone`, `import logging`, `from plotbot.print_manager import print_manager`, `from plotbot.plot_manager import plot_manager`, `from plotbot.ploptions import ploptions, retrieve_ploption_snapshot`, `from ._utils import _format_setattr_debug`.

3.  **Refactor `mag_rtn_class`:**
    *   New File: `plotbot/data_classes/psp_mag_rtn.py` (Already created)
    *   Action: Move `mag_rtn_class` definition and `mag_rtn = mag_rtn_class(None)` into `psp_mag_rtn.py`.
    *   Imports for `psp_mag_rtn.py`: (Same as `psp_mag_rtn_4sa.py`).

4.  **Refactor `mag_sc_4sa_class`:**
    *   New File: `plotbot/data_classes/psp_mag_sc_4sa.py` (Already created)
    *   Action: Move `mag_sc_4sa_class` definition and `mag_sc_4sa = mag_sc_4sa_class(None)` into `psp_mag_sc_4sa.py`.
    *   Imports for `psp_mag_sc_4sa.py`: (Same as `psp_mag_rtn_4sa.py`).

5.  **Refactor `mag_sc_class`:**
    *   New File: `plotbot/data_classes/psp_mag_sc.py` (Already created)
    *   Action: Move `mag_sc_class` definition and `mag_sc = mag_sc_class(None)` into `psp_mag_sc.py`.
    *   Imports for `psp_mag_sc.py`: (Same as `psp_mag_rtn_4sa.py`).

6.  **Cleanup `psp_mag_classes.py`:**
    *   Action: After all classes and the utility function are moved, `plotbot/data_classes/psp_mag_classes.py` should be empty of class definitions. It can then be deleted.

**Phase 2: Update Imports and Codebase Adjustments**

1.  **Create/Update `plotbot/data_classes/__init__.py`:**
    *   Purpose: To re-export the classes and instances from their new individual files, maintaining the `from plotbot.data_classes import ...` import pattern.
    *   Content:
        ```python
        # plotbot/data_classes/__init__.py
        from .psp_mag_rtn_4sa import mag_rtn_4sa_class, mag_rtn_4sa
        from .psp_mag_rtn import mag_rtn_class, mag_rtn
        from .psp_mag_sc_4sa import mag_sc_4sa_class, mag_sc_4sa
        from .psp_mag_sc import mag_sc_class, mag_sc
        # ... (Ensure other existing data class imports from this __init__ are preserved)

        __all__ = [
            'mag_rtn_4sa_class', 'mag_rtn_4sa',
            'mag_rtn_class', 'mag_rtn',
            'mag_sc_4sa_class', 'mag_sc_4sa',
            'mag_sc_class', 'mag_sc',
            # ... (Ensure __all__ is updated accordingly, preserving existing entries)
        ]
        ```

2.  **Update `plotbot/__init__.py`:**
    *   File: `plotbot/__init__.py`
    *   Action: Change the import line for magnetic field classes.
        *   **From:** `from .data_classes.psp_mag_classes import mag_rtn_4sa, mag_rtn, mag_sc_4sa, mag_sc, mag_rtn_4sa_class, mag_rtn_class, mag_sc_4sa_class, mag_sc_class`
        *   **To:** `from .data_classes import mag_rtn_4sa, mag_rtn, mag_sc_4sa, mag_sc, mag_rtn_4sa_class, mag_rtn_class, mag_sc_4sa_class, mag_sc_class` (This relies on `plotbot/data_classes/__init__.py` correctly exporting these names).
    *   Verify that `CLASS_NAME_MAPPING` in this file still functions correctly with the re-exported class names.

3.  **Global Import Scan and Update (Anticipated Files):**
    *   Review and update imports in any file that might be directly importing from `plotbot.data_classes.psp_mag_classes`. This is less likely if `plotbot/__init__.py` and `plotbot/data_classes/__init__.py` were the primary points of import.
    *   Potential files to check (this list might not be exhaustive and depends on actual usage, but these are common places where data classes might be referenced):
        *   `plotbot/plotbot_main.py`
        *   `plotbot/get_data.py`
        *   `plotbot/data_cubby.py` (especially for type hints or direct class references if any)
        *   Any test files in the `tests/` directory that specifically import or use these magnetic field classes (e.g., `tests/test_proton_r_sun.py` if it ever used mag classes directly, or other specific mag tests).
        *   Any Jupyter notebooks or example scripts if they import directly.

**Next Steps after this log update:** Push these changes (creation of empty files) and the updated log to GitHub. Then, reset the AI assistant to begin the refactoring with a clean slate, following this plan.

## Push: v2.32

- **Version Tag:** `2025_05_17_v2.32`
- **Commit Message:** `Refactor: Prepare for psp_mag_classes.py split by creating new files and plan (v2.32)`
- **Summary:** Created new empty files (`_utils.py`, `psp_mag_rtn_4sa.py`, `psp_mag_rtn.py`, `psp_mag_sc_4sa.py`, `psp_mag_sc.py`) in `plotbot/data_classes/` and documented the detailed refactoring plan in this log. This prepares for splitting the monolithic `psp_mag_classes.py`. 

## Refactor: `psp_mag_classes.pyi` Split

- **Summary:** Split the contents of `plotbot/data_classes/psp_mag_classes.pyi` into new individual stub files:
    - `plotbot/data_classes/psp_mag_rtn_4sa.pyi`
    - `plotbot/data_classes/psp_mag_rtn.pyi`
    - `plotbot/data_classes/psp_mag_sc_4sa.pyi`
    - `plotbot/data_classes/psp_mag_sc.pyi`
- The original `plotbot/data_classes/psp_mag_classes.pyi` was deleted.
- This completes the first part of Phase 1 for the stub files, aligning with the refactor plan.

## Push: v2.33

- **Version Tag:** `2025_05_17_v2.33`
- **Commit Message:** `Refactor: Split psp_mag_classes.pyi into individual stub files (v2.33)`
- **Summary:** Moved type hint definitions from the monolithic `psp_mag_classes.pyi` to separate files (`psp_mag_rtn_4sa.pyi`, `psp_mag_rtn.pyi`, `psp_mag_sc_4sa.pyi`, `psp_mag_sc.pyi`) and deleted the original. This is part of the larger `psp_mag_classes.py` refactor.

## Push: v2.34

- **Version Tag:** `2025_05_17_v2.34`
- **Commit Message:** `Docs: Corrected v2.32 entry in captain\'s log (v2.34)`
- **Summary:** Pushed a correction to the captain's log to accurately reflect the v2.32 push details. Updated `plotbot/__init__.py` with the new version and commit message.

*(Log remains open for further updates on 2025-05-17)* 

## Refactor: `psp_mag_classes.py` Content Migration and Deletion

- **Summary:** Completed Phase 1 (File and Class Restructuring) of the `psp_mag_classes.py` refactor plan:
    - Moved the `_format_setattr_debug` function to `plotbot/data_classes/_utils.py`.
    - Moved `mag_rtn_4sa_class` and its instance to `plotbot/data_classes/psp_mag_rtn_4sa.py`.
    - Moved `mag_rtn_class` and its instance to `plotbot/data_classes/psp_mag_rtn.py`.
    - Moved `mag_sc_4sa_class` and its instance to `plotbot/data_classes/psp_mag_sc_4sa.py`.
    - Moved `mag_sc_class` and its instance to `plotbot/data_classes/psp_mag_sc.py`.
    - All necessary imports were added to the new files.
- The original `plotbot/data_classes/psp_mag_classes.py` file, now empty of substantive code, has been deleted.
- The next steps will involve Phase 2: Updating imports across the codebase, particularly in `plotbot/data_classes/__init__.py` and `plotbot/__init__.py`, and then testing.

## Push: v2.35

- **Version Tag:** `2025_05_17_v2.35`
- **Commit Message:** `Refactor: Finalized splitting of psp_mag_classes.py content; deleted original file (v2.35)`
- **Summary:** Moved all class definitions and the utility function from `psp_mag_classes.py` into their respective new files (`_utils.py`, `psp_mag_rtn_4sa.py`, `psp_mag_rtn.py`, `psp_mag_sc_4sa.py`, `psp_mag_sc.py`). The original `psp_mag_classes.py` was then deleted. This completes the primary file restructuring for the magnetic field data classes.

*(Log remains open for further updates on 2025-05-17)*

## Refactor: Update Imports Post `psp_mag_classes.py` Split

- **Summary:** Completed Phase 2 (Update Imports and Codebase Adjustments) of the `psp_mag_classes.py` refactor plan.
    - Corrected import statements in `plotbot/__init__.py` to directly import magnetic field classes and instances from their new specific files (e.g., `from .data_classes.psp_mag_rtn_4sa import mag_rtn_4sa, mag_rtn_4sa_class`).
    - Confirmed that `plotbot/data_classes/__init__.py` was not needed and should not be created for these direct imports. Deleted the erroneously created `plotbot/data_classes/__init__.py`.
    - Updated import statements in the following files to reflect the new locations of the magnetic field data classes:
        - `plotbot/get_data.py`
        - `plotbot/plotbot_main.py`
        - `plotbot/data_snapshot.py`
        - `plotbot/data_cubby.py`
        - `tests/test_psp_mag_br_norm.py`
        - `tests/test_zarr_file_io.py`
        - `tests/test_e2e_snapshot_workflow.py`
        - `tests/test_stardust.py`
        - `tests/test_audifier.py`
        - `tests/test_snapshot_save_load.py`
    - Ran tests (specifically `tests/test_proton_r_sun.py` and `tests/test_stardust.py`) to confirm the import changes were successful and did not introduce regressions.
    - Refactored `tests/test_proton_r_sun.py` to be pytest-compatible by renaming `main()` to `test_proton_r_sun_plot()` and removing the `if __name__ == '__main__':` block.
- **Outcome:** All direct usages of `plotbot.data_classes.psp_mag_classes` have been updated. The codebase now correctly imports magnetic field data classes from their new, individual modules within `plotbot/data_classes/`. 

## Refactor: `psp_proton_classes.py` Split and `.pyi` Creation

- **Summary:** Continued the modularization effort by splitting `plotbot/data_classes/psp_proton_classes.py` into individual files for each proton data class:
    - `proton_class` and its instance `proton` were moved to `plotbot/data_classes/psp_proton.py`.
    - `proton_hr_class` and its instance `proton_hr` were moved to `plotbot/data_classes/psp_proton_hr.py`.
    - Necessary imports were added to these new files.
    - The original `plotbot/data_classes/psp_proton_classes.py` was deleted.
- **Import Updates:** Adjusted import statements across the codebase to reflect these changes. Files updated include:
    - `plotbot/__init__.py`
    - `plotbot/data_cubby.py`
    - `plotbot/get_data.py`
    - `plotbot/plotbot_main.py`
    - `plotbot/data_classes/psp_proton_fits_classes.py`
    - `tests/test_snapshot_save_load.py`
    - `tests/core/test_plotting.py`
- **Stub Files:** Created new `.pyi` stub files for the new proton class files:
    - `plotbot/data_classes/psp_proton.pyi`
    - `plotbot/data_classes/psp_proton_hr.pyi`
- **Outcome:** The proton data classes are now in their own modules, improving organization. All import errors related to this change have been resolved.

## Push: v2.37

- **Version Tag:** `2025_05_17_v2.37`
- **Commit Message:** `Refactor: v2.37 Split psp_proton_classes.py and created .pyi files`
- **Summary:** Successfully split `psp_proton_classes.py` into `psp_proton.py` and `psp_proton_hr.py`, updated all relevant imports across the codebase, and generated corresponding `.pyi` stub files. 

*(Log remains open for further updates on 2025-05-17)* 

## Debugging: Empty Plot from `test_proton_r_sun.py`

- **Issue:** An empty plot window is appearing when `tests/test_proton_r_sun.py` is run.
- **Initial Misdiagnosis (AI Slip-up):** Initially, the AI focused on the `mag_rtn_4sa_class` instantiation in `psp_mag_rtn_4sa.py` as a potential cause for an empty plot, suspecting the `plot_manager` might display on init.
- **Correction:** Robert correctly pointed out that `tests/test_proton_r_sun.py` makes an explicit `plotbot()` call, which is the direct source of the plot. The emptiness of the plot suggests data is not being loaded or processed correctly for the variables passed to `plotbot()` within the test's time range.
- **Next Steps:**
    1. Run `pytest -s tests/test_proton_r_sun.py` to capture the standard output, which includes numerous debug prints.
    2. Analyze this output to understand the data loading and processing flow, and identify why the plot variables (`mag_rtn_4sa.br`, `mag_rtn_4sa.pmag`, `proton.sun_dist_rsun`, `mag_rtn_4sa.br_norm`) might be empty or invalid when `plotbot()` is called.
- **Note to Future AI Self:** When a test script is explicitly mentioned as causing a plot, investigate the test script's plotting calls *first*, before looking at class instantiations, especially if the test script contains its own `plotbot` or similar high-level plotting function calls. Don't get sidetracked by general class behaviors if a more direct cause is apparent in the test execution flow.

- **Resolution (2025-05-17):**
    - The `ValueError` was traced to the `y_label` for `br_norm` in `plotbot/data_classes/psp_mag_rtn_4sa.py`. The original label `'$B_R \\cdot R^2$ (nT AU$^2$)'` caused a mathtext parsing error.
    - **Fix 1:** Changed the label to `'$B_R \cdot R^2$' + ' (nT AU$^2$)'` to separate the math expression from the units text. This resolved the `ValueError` and the plot displayed correctly.
    - **Fix 2:** Subsequent test runs revealed `SyntaxWarning: invalid escape sequence '\\c'` due to `\cdot` in regular strings. All relevant matplotlib labels in `psp_mag_rtn_4sa.py` (including those for `br`, `bt`, `bn`, `bmag`, `pmag`, and all instances of `br_norm` labels) were updated to use raw strings (e.g., `r'$B_R \cdot R^2$'`). This resolved the syntax warnings.
    - The test `tests/test_proton_r_sun.py` now passes cleanly without errors or warnings.

*(Log remains open for further updates on 2025-05-17)* 

## Push: v2.38

- **Version Tag:** `2025_05_17_v2.38`
- **Commit Message:** `Fix: Correct Matplotlib labels in psp_mag_rtn_4sa.py to resolve plot error (v2.38)`
- **Summary:** Corrected Matplotlib `y_label` and `legend_label` formatting in `plotbot/data_classes/psp_mag_rtn_4sa.py`. This fixed a `ValueError` in `test_proton_r_sun.py` caused by mathtext parsing issues and resolved subsequent `SyntaxWarning`s by using raw strings for LaTeX sequences. The test now passes cleanly.

*(Log remains open for further updates on 2025-05-17)* 