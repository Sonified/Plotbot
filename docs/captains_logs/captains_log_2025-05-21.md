    # Captain's Log - 2025-05-21

## Plotbot Initialization and `test_pilot` Refactor

**Issue:** Jaye encountered a `FileNotFoundError` when importing `plotbot`. This error originated from `test_pilot.py` (which was being imported by `plotbot/__init__.py`) attempting to create a log file.

**Troubleshooting & Learning:**
*   The `test_pilot.py` module and its functions (`run_missions`, `phase`, `system_check`) are intended for development and running `plotbot`'s internal tests.
*   These components are not required for the standard, day-to-day use of `plotbot` for plotting or data analysis.
*   Importing `test_pilot` in the main `__init__.py` unnecessarily coupled this testing utility to the core library import, leading to issues for users not actively engaged in testing.

**Resolution:**
*   Removed the direct import of `run_missions`, `phase`, and `system_check` from `test_pilot.py` within the main `plotbot/__init__.py` file.
*   Removed these three functions from the `__all__` list in `plotbot/__init__.py`.

**Outcome:**
*   `test_pilot.py` is no longer loaded automatically when `plotbot` is imported for regular use.
*   This directly resolves the `FileNotFoundError` encountered by the colleague and makes the library more robust for end-users.
*   `test_pilot.py` will now only be loaded when test scripts explicitly import it, ensuring a cleaner separation between the library's usage and its testing infrastructure.

**Git Push:**
*   Version: `2025_05_21_v2.48`
*   Commit Message: `v2.48 Refactor: Decouple test_pilot from main plotbot import to fix user FileNotFoundError.` 