# Captain's Log: 2025-05-07

## Bug Fix: Multiple Time Range Support in `save_data_snapshot`

- **Issue:** The `save_data_snapshot` function in `plotbot/data_snapshot.py` failed when using multiple time ranges via `trange_list` parameter. The test `test_advanced_snapshot_save` was failing because when saving data with multiple time ranges defined in `TEST_TRANGES_FOR_SAVE`, only the last time range's data was present in the final instance.

- **Root Cause Analysis:**
  1. In `save_data_snapshot`, when processing multiple time ranges using `trange_list`, each call to `plotbot_get_data` was overwriting the instance's data rather than merging it with previously loaded data.
  2. This happened because each time range was processed independently without accumulating data between iterations.
  3. Specifically, when iterating through time ranges, the global instance (e.g., `plotbot.mag_rtn`) was being reinitialized with only the current time range data, rather than having data merged from all time ranges.

- **Fix Implemented:**
  1. Modified the data loading process in `save_data_snapshot` to correctly accumulate data across multiple time ranges.
  2. Ensured consistent data length between `instance.time` and `instance.datetime_array` by properly synchronizing them after data merging operations.
  3. Improved handling of merged data to maintain internal consistency in data class instances.

- **Outcome:** The function now correctly accumulates data from all time ranges specified in `trange_list` before saving the snapshot. Tests confirm that data from all time ranges is properly included in the final snapshot.

*(Log remains open for further updates on 2025-05-07)* 