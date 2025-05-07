# Plotbot Test Suite

This directory contains tests for the Plotbot application, focusing on both unit tests and integration tests.

## Test Structure

The test suite is organized into the following directories:

- `core/`: Core functionality tests
  - `test_data_loading.py`: Tests for initial data loading and caching
  - `test_snapshot_handling.py`: Tests for saving and loading snapshots
  - `test_data_merging.py`: Tests for data merging and overlap handling
  - `test_plotting.py`: Tests for plotting functionality and multiplot

- `utils/`: Test utilities and helpers
  - `test_helpers.py`: Reusable functions for testing data integrity and verifying state

## Key Testing Approach

The Plotbot test suite focuses on verifying the **data integrity** at each step of the pipeline, rather than just checking if a plot appears. This means:

1. Validating internal data consistency (datetime_array, time, raw_data, field)
2. Checking data within DataCubby registries
3. Confirming Global Tracker state
4. Ensuring data is correctly merged, filtered, and processed

The `verify_instance_state` function in `utils/test_helpers.py` performs detailed validation of:
- Datetime array integrity (sorted, unique times)
- Time attribute consistency with datetime_array
- Raw data component length matching datetime_array
- Field attribute correctness for the data type

## Running Tests

You can run the full test suite with:

```bash
pytest tests/
```

Run specific test modules with:

```bash
pytest tests/core/test_data_loading.py
pytest tests/core/test_snapshot_handling.py
pytest tests/core/test_data_merging.py
pytest tests/core/test_plotting.py
```

Run tests with verbose output:

```bash
pytest -xvs tests/core/test_data_loading.py
```

## Test Constants

The test suite uses standard time ranges for consistent testing across modules:

- Basic single range: '2021-10-26 02:00:00' to '2021-10-26 02:10:00'
- Multiple ranges for advanced testing
- Partially overlapping ranges for merge testing 