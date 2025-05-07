# Test Suite for Plotbot Data Handling
*Main Objective:* Verify that Plotbot correctly handles data loading, merging, plotting, and snapshot handling.

[ ] **Test Suite Completed**

## Test Data Loading
[x] **test_initial_data_load** - Plots the first load; passes if data import is successful. (Skipped as per Robert's request)
[x] **test_cached_data_retrieval** - Plots from cache; passes if the cached data matches the original data source. (Skipped as per Robert's request)

## Test Data Merging
[x] **test_partial_overlap_merge** - Merges overlapping data; passes if the timeline remains continuous.
[x] **test_merge_arrays_directly** - Directly merges arrays; passes if order and continuity are preserved.
[x] **test_plotbot_calls_with_overlapping_time_ranges** - Merges data from sequential, overlapping plotbot() calls; passes if final data is consistent and complete.

## Test Plotting
[ ] **test_explicit_panel_plotting** - Plots on specific panels; passes if each panel receives the correct data series.
[ ] **test_multiplot_specific_data_files** - Multi-panel plotting; passes if all panels are correctly synchronized to the data range.

## Test Snapshot Handling
[x] **test_simple_snapshot_save** - Saves a basic snapshot; passes if the file is created successfully.
[x] **test_simple_snapshot_load_verify_plot** - Loads and re-plots a snapshot; passes if the plot matches the saved data.
[x] **test_advanced_snapshot_save** - Saves complex snapshots; passes if all components are correctly saved.
[ ] **test_advanced_snapshot_load_verify_plot** - Loads complex snapshots; passes if the plot matches the original data.

---

### Run Instructions:
All tests use the matplotlib Agg backend to suppress plot windows during automated runs.
Execute the tests using the following command: