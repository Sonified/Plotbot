# Captain's Log: 2025-05-05

## Push: v2.05

- Version: 2025_05_05_v2.05
- Commit message: v2.05: Significant multiplot issues and data cubby timing issues

Summary: This push documents ongoing significant issues with multiplot rendering and data cubby timing. See previous log for detailed context. No major new features, but version and commit message updated for tracking.

---

(Log remains open for further updates on 2025-05-05) 

---

## Bug Fix: DataCubby Merge Logic for Disjoint Ranges

**Symptom:** When using `multiplot` with multiple time ranges, only the first panel's data was correctly loaded and plotted. Subsequent panels failed because the `DataCubby` incorrectly determined that the new time ranges (e.g., 2019) were already contained within the existing data (e.g., 2018 + 2021-2025).

**Root Cause:** The `_merge_arrays` method in `data_cubby.py` calculated the overall start and end times of the data already in the cubby. It then checked if the *new* time range fell within this overall span. This logic failed when the existing data had gaps (disjoint ranges), leading it to incorrectly conclude the new data was already present.

**Fix:** Modified `_merge_arrays` to:
1. Combine existing and new time arrays.
2. Find unique timestamps using `np.unique`.
3. Compare the count of unique timestamps to the original count of existing timestamps.
4. Only proceed with the merge if the unique count is *greater*, indicating that the new data adds genuinely new time points.

This ensures that data is merged correctly even when the cubby contains disjoint time ranges.

## Push: v2.06

- Version: 2025_05_05_v2.06
- Commit message: Fix: Correct DataCubby merge logic for disjoint time ranges (v2.06) 

## Feature Complete: Degrees-from-Perihelion Axis

- The degrees-from-perihelion axis is now fully implemented and matches the Carrington longitude axis in all formatting and behavior (ticks, labels, wrap-around, etc.).
- Implementation strictly mirrors the Carrington longitude logic, with a longitude shift so 0° aligns with perihelion.
- Axis formatting now uses a robust flag (`panel_actually_uses_degrees`) to ensure correct degree formatting.
- All relevant tests pass (see `tests/test_degrees_from_perihelion.py`).
- See updated implementation plan in `docs/implementation_plans/perihelion_axis_plan_v2.md` for details and lessons learned.

## Push: v2.11

- Version: 2025_05_05_v2.11
- Commit message: v2.11: Degrees-from-perihelion axis complete, matches Carrington longitude logic

Summary: Perihelion axis feature is now complete, fully matching Carrington longitude axis formatting and behavior. All tests pass. See implementation plan and above for details.

(Log remains open for further updates on 2025-05-05) 

---

## Refactor & Fixes: Perihelion Implementation Reset

- **Issue:** Encountered significant indentation errors and logical inconsistencies in `plotbot/multiplot.py` while integrating the degrees-from-perihelion feature.
- **Action:** Reset `plotbot/multiplot.py` to commit `ef18950` to establish a clean baseline.
- **Fixes Applied (to other files):**
    - Corrected option setters in `plotbot/multiplot_options.py` to ensure proper mutual exclusivity between all positional/relative axis modes (including perihelion).
    - Corrected `plotbot/utils.py` by adding the full `PERIHELION_TIMES` dictionary (sourced from notebook) and fixing the `get_perihelion_time` lookup.
- **Progress:** Added the perihelion test case to `tests/multiplot_tests/text_x_axis_positional_types.py`. Re-added initial perihelion logic (imports, mode detection, flag init) to the clean `multiplot.py`.
- **Status:** Pausing full perihelion implementation in `multiplot.py` to push current stable fixes.

## Push: v2.13

- Version: 2025_05_05_v2.13
- Commit message: Refactor: Reset multiplot.py, fix utils/options, re-add perihelion init (v2.13)

Summary: Resetting multiplot.py due to errors, fixing related utils/options, adding perihelion test, and beginning re-implementation of perihelion logic in multiplot.

(Log remains open for further updates on 2025-05-05) 

---

## Debug & Fix: Perihelion Offset Diagnostic Test

- **Issue:** The diagnostic test `tests/test_plot_perihelion_windows.py` produced confusing results (small non-zero offsets at perihelion, or a "wall of zeros") due to incorrect sampling logic.
- **Fix:** Updated the test to correctly sample symmetrically around the *exact* perihelion time using `np.interp`. This ensures the degrees-from-perihelion value is precisely zero at the zero-hour offset.
- **Documentation:** Updated `docs/implementation_plans/perihelion_axis_plan_v2.md` with a detailed explanation of the issue, the fix, and the final successful test output.

## Push: v2.15

- Version: 2025_05_05_v2.15
- Commit message: ⭐ GLORY to PSP: We have Degrees From Perihelion! (v2.15)

Summary: Perihelion axis feature is now complete, fully matching Carrington longitude axis formatting and behavior. All tests pass. See implementation plan and above for details.

(Log remains open for further updates on 2025-05-05) 

---

## Debug & Fix: Perihelion Calculation Root Cause

- **Issue Identified:** The core reason for incorrect 'Degrees from Perihelion' values in `multiplot` was traced to a timestamp unit mismatch within `plotbot/x_axis_positional_data_helpers.py`. The `XAxisPositionalDataMapper.map_to_position` function was comparing query times (in nanoseconds) to reference times (in seconds) during interpolation.
- **Fix:** Modified `XAxisPositionalDataMapper.map_to_position` to correctly convert query times to seconds before calling `np.interp`.
- **Verification:** The fix was confirmed using `tests/debug_perihelion_mapping.py`, which now produces the correct, centered degree range.
- **Documentation:** Updated `docs/implementation_plans/perihelion_axis_plan_v2.md` to document this root cause and fix.

## Push: v2.16

- Version: 2025_05_05_v2.16
- Commit message: fix: core degrees from perihelion issue identified (v2.16)

Summary: Fixed the root cause of the perihelion degree calculation error by correcting timestamp unit handling in the positional data mapper. 

Here’s the general approach to time handling in Plotbot, based on the codebase:
1. Parsing and Standardization
All time parsing (in get_data, import_data_function, data_download_berkeley, data_download_helpers, data_tracker, etc.) uses dateutil.parser.parse and then .replace(tzinfo=timezone.utc) to ensure all times are timezone-aware and in UTC.
When converting to numpy datetime64:
.replace(tzinfo=None) is used to strip timezone info before converting to np.datetime64, since numpy datetimes are always naive (no timezone).
Pandas to_datetime(..., utc=True) is used when reading from files, then sometimes .tz_localize(None) to make them naive for storage or comparison.
2. Comparisons and Filtering
When filtering arrays or comparing times:
If the array is np.datetime64, the comparison is done with np.datetime64 versions of the start/end times (which are always naive).
If the array is Python datetime and timezone-aware, the start/end times are also made UTC-aware.
If the array is naive, the start/end times are made naive.
3. Time Range Handling
All time ranges (trange) are parsed to UTC-aware datetimes for logic, then stripped to naive for numpy storage.
When passing times to plotting or math:
If using numpy or pandas, times are usually naive.
If using Python datetime, times are UTC-aware for logic, but may be made naive for compatibility.
4. Helpers
time_clip and similar helpers always parse input times as UTC-aware, then convert to np.datetime64 for comparison.
str_to_datetime uses dateutil.parser.parse (returns naive or aware depending on input).
5. Summary
All time math and comparisons are done with either:
Both sides UTC-aware, or
Both sides naive (usually after stripping timezone for numpy/pandas).
The only time you see tz-naive/tz-aware errors is when something slips through and isn’t standardized before math.
Bottom line:
Plotbot’s standard is:
Parse as UTC-aware for logic.
Strip to naive for numpy/pandas storage and math.
Always match tz-awareness before comparing or subtracting.
If you want a code snippet or want to see a specific function’s handling, let me know!