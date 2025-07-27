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
*   **Version:** `2025_05_21_v2.49`
*   **Commit Message:** `v2.49 Fix: Correct plot_manager truthiness evaluation to prevent ValueError.`

## Data Visualization Note: positional_data_overview.png

* Observed that the Carrington longitude plot (top panel) in `local_images/positional_data_overview.png` appears zoomed out. It's difficult to determine from this overview whether the longitude data is wrapping as expected, or if there is a plotting/visualization issue. This may warrant a closer look or a more zoomed-in plot for clarity in future analyses. 

## Debugging `print_manager` and `pm.processing` visibility

**Objective:** Understand why `pm.processing` calls were not appearing in the console output, particularly from within `plotbot/data_cubby.py`.

**Test Command Used:**
```
python -m pytest -s tests/test_plotbot.py -k "test_simple_plot_truthiness_error"
```

**Learnings:**
*   **`-s` flag for `pytest`:** This flag is crucial. It disables `pytest`'s default behavior of capturing output. With `-s`, all print statements (including those from `print_manager`) are displayed directly in the console during the test run. Without it, these prints would be hidden unless the test failed.
*   **`print_manager.show_processing = True`:** For `pm.processing()` calls to actually print, the `print_manager` instance's `show_processing` attribute (or its internal `processing_enabled` flag) must be `True`.
    *   We initially set this at the top of `plotbot/data_cubby.py`.
    *   We then discovered it was also being set to `True` within `tests/test_plotbot.py`.
    *   When the line in `data_cubby.py` was commented out, the `pm.processing` calls *still* appeared in the console output when running the test. This confirmed that the setting in `tests/test_plotbot.py` was taking effect and enabling the processing prints for the duration of the test.
*   **Conclusion for `data_cubby.py` prints:** The combination of setting `print_manager.show_processing = True` (in the test setup or the module itself) AND using the `-s` flag with `pytest` allows us to see `pm.processing` messages from `data_cubby.py` in the console during tests. 