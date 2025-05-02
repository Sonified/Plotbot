# Captain's Log - 2025-05-01

---

*   **Bug Fix: SPDF Data Download Completeness:** Resolved an issue where the SPDF download mechanism (used in `spdf` and `dynamic` modes) would incorrectly stop if *any* local file matching the data type was found within the requested time range, even if the local files didn't cover the *entire* range. This could lead to incomplete datasets being loaded. The fix involved removing the initial local-only check (`no_update=True`) in `plotbot/data_download_pyspedas.py`, ensuring that the function now always proceeds to the `no_update=False` check, which correctly assesses local files against the required range and downloads missing data or newer versions from the server as needed. 

*   **Enhancement: Case-Insensitive Server Config:** Modified `plotbot/get_data.py` to handle the `config.data_server` setting (`'spdf'`, `'berkeley'`, `'dynamic'`) in a case-insensitive manner. It now converts the value to lowercase before checking it, preventing potential issues caused by inconsistent capitalization in the configuration. 

*   **Bug Fix: Longitude Mapping Axis Issues:** Fixed a critical issue where enabling longitude mapping (`use_longitude_x_axis=True`) would sometimes show no data on the plot or display time values on the x-axis instead of longitude values. The fixes include:
    * Better handling of datetime formats in the `LongitudeMapper` class
    * Explicit disabling of `use_longitude_x_axis` if the longitude data fails to load
    * Auto-disabling of `use_relative_time` when longitude mapping is active (these features conflict)
    * Improved x-axis formatting for longitude display, including proper tick placement and limits
    * Additional diagnostic information to troubleshoot longitude mapping issues
    * Added a test utility that can verify longitude mapping functionality independently

*   **Enhancement: Robust Longitude Data Type Conversion:** Enhanced the `map_to_longitude` method to handle different datetime formats by attempting automatic conversion to `numpy.datetime64`, making the function more robust to different input data types.

*   **Feature: Enhanced Positional X-Axis Support for Multiplots:** Implemented comprehensive support for using different positional data types on the x-axis in multi-panel plots:
    * Added support for three positional x-axis options: 
      * Carrington longitude (degrees)
      * Radial distance (solar radii / R_sun)
      * Carrington latitude (degrees)
    * Created a mutually exclusive API where setting one option automatically disables others
    * Implemented read-only properties to check which option is active
    * Added `x_axis_positional_range` property to allow setting fixed ranges for the x-axis
    * Implemented smart range handling for both single and multiple x-axis modes:
      * Common x-axis: applies the same range to all panels 
      * Separate axes: each panel has its own range based on its data
    * Added `positional_tick_density` property to control the number of ticks on positional x-axes
    * Fixed `reset()` method to properly reset all positional x-axis properties
    * Created diagnostic utilities:
      * `analyze_positional_data_ranges.py`: Analyzes ranges for different encounters
      * `demo_x_axis_positional_options.py`: Demonstrates how to use the new options
    * Created comprehensive test suite to verify positional x-axis functionality

*   **Enhancement: Added default settings to the plot to optimize display (multiplot)**

---

*   **Version Update:** Updated version number from `2025_05_01_v1.16` to `2025_05_02_v1.17` to reflect the new positional x-axis functionality. Updated documentation in README.md with examples of how to use the new positional x-axis options.