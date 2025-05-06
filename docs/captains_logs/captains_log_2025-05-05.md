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