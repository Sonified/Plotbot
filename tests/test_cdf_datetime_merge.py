import pytest
import os
import glob
import cdflib
import numpy as np
import random
from dateutil.parser import parse
import pandas as pd # Useful for Timestamp comparisons if needed

# Add project root to sys.path to allow importing plotbot modules if necessary later
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# We might need print_manager later for consistent output
from plotbot.print_manager import print_manager

# --- Constants ---
# Adjust this path if your data is located elsewhere relative to the test file
# Using an absolute path based on the test file's location
_test_dir = os.path.dirname(__file__)
_project_root = os.path.abspath(os.path.join(_test_dir, '..'))
TEST_CDF_DIR = os.path.join(_project_root, 'psp_data', 'fields', 'l2', 'mag_rtn_4_per_cycle')

TIME_VARIABLE_NAMES = ['Epoch', 'epoch', 'time', 'Time', 'epoch_mag_RTN_4_Sa_per_Cyc'] # Added correct name
# Define the specific data variable we want to test with
DATA_VARIABLE_NAME_BR = 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc' # Adjust if needed based on CDF structure

# --- Helper Function ---
def _load_datetime_from_cdf(filepath):
    """Loads the primary time variable from a CDF file and returns a numpy datetime64 array."""
    print_manager.status(f"--- Loading CDF: {os.path.basename(filepath)} ---")
    try:
        with cdflib.CDF(filepath) as cdf_file:
            cdf_info = cdf_file.cdf_info()
            
            # Try common time variable names (including the newly found one)
            time_var_name = None
            # Correct way to access variable lists from CDFInfo
            # Try accessing as attributes instead of dictionary keys
            available_vars = []
            if hasattr(cdf_info, 'zVariables'):
                available_vars.extend(list(cdf_info.zVariables))
            if hasattr(cdf_info, 'rVariables'):
                 available_vars.extend(list(cdf_info.rVariables))
            
            # available_vars = list(cdf_info['zVariables']) + list(cdf_info['rVariables']) # Old incorrect way
            for name in TIME_VARIABLE_NAMES:
                if name in available_vars:
                    time_var_name = name
                    break
            
            if not time_var_name:
                # Use the correct variable list in the warning
                print_manager.warning(f"Could not find a recognized time variable in {filepath}. Available: {available_vars}")
                return None
            
            print_manager.debug(f"Found time variable: '{time_var_name}'")
            times_tt2000 = cdf_file.varget(time_var_name)
            
            if times_tt2000 is None:
                print_manager.warning(f"Time variable '{time_var_name}' returned None from varget in {filepath}")
                return None
            # Ensure it's iterable and check length after potential conversion
            if not hasattr(times_tt2000, '__len__') or len(times_tt2000) == 0:
                print_manager.warning(f"Time variable '{time_var_name}' is empty or not iterable in {filepath}")
                return None

            print_manager.debug(f"Read {len(times_tt2000)} time values (type: {type(times_tt2000[0])}). Converting to datetime64[ns]...")
            
            # Convert TT2000 to datetime64[ns]
            # Pass the numpy array directly if it's already tt2000 epoch, or list otherwise
            datetime_array = cdflib.cdfepoch.to_datetime(times_tt2000) # Use python datetime objects
            # Convert python datetime to numpy datetime64[ns]
            datetime_array_np = np.array(datetime_array, dtype='datetime64[ns]')
            
            print_manager.debug(f"Conversion successful. Shape: {datetime_array_np.shape}, Dtype: {datetime_array_np.dtype}")
            print_manager.status(f"--- Successfully loaded datetime array from {os.path.basename(filepath)} --- ")
            return datetime_array_np
            
    except Exception as e:
        # Check if it might be a CDF-related error by checking the exception type name or message if needed
        if "CDF" in type(e).__name__ or "cdflib" in str(e).lower():
             print_manager.error(f"cdflib processing error for {filepath}: {e}")
        else:
             print_manager.error(f"General error loading or processing CDF file {filepath}: {e}")
        import traceback
        print_manager.error(traceback.format_exc())
        return None

def _load_time_and_data_from_cdf(filepath, data_var_name):
    """Loads time and a specified data variable from a CDF file.

    Returns a tuple: (datetime_array_np, data_array_np) or (None, None) on failure.
    """
    print_manager.status(f"--- Loading Time & Data ({data_var_name}) from CDF: {os.path.basename(filepath)} ---")
    datetime_array_np = None
    data_array_np = None
    try:
        with cdflib.CDF(filepath) as cdf_file:
            cdf_info = cdf_file.cdf_info()
            available_vars = []
            if hasattr(cdf_info, 'zVariables'): available_vars.extend(list(cdf_info.zVariables))
            if hasattr(cdf_info, 'rVariables'): available_vars.extend(list(cdf_info.rVariables))

            # Load Time Variable
            time_var_name = None
            for name in TIME_VARIABLE_NAMES:
                if name in available_vars:
                    time_var_name = name
                    break
            if not time_var_name:
                print_manager.warning(f"TIME LOAD FAILED: Could not find time variable in {filepath}. Available: {available_vars}")
                return None, None

            times_tt2000 = cdf_file.varget(time_var_name)
            if times_tt2000 is None or not hasattr(times_tt2000, '__len__') or len(times_tt2000) == 0:
                print_manager.warning(f"TIME LOAD FAILED: Time variable '{time_var_name}' is None or empty in {filepath}")
                return None, None

            datetime_array = cdflib.cdfepoch.to_datetime(times_tt2000)
            datetime_array_np = np.array(datetime_array, dtype='datetime64[ns]')
            print_manager.debug(f"  Time loaded: '{time_var_name}', Shape: {datetime_array_np.shape}")

            # Load Data Variable
            if data_var_name not in available_vars:
                 print_manager.warning(f"DATA LOAD FAILED: Specified data variable '{data_var_name}' not found in {filepath}. Available: {available_vars}")
                 return datetime_array_np, None # Return time if loaded, but no data

            data_array = cdf_file.varget(data_var_name)
            if data_array is None:
                 print_manager.warning(f"DATA LOAD FAILED: Data variable '{data_var_name}' returned None from varget in {filepath}")
                 return datetime_array_np, None
            if not hasattr(data_array, '__len__') or len(data_array) == 0:
                 print_manager.warning(f"DATA LOAD FAILED: Data variable '{data_var_name}' is empty or not iterable in {filepath}")
                 return datetime_array_np, None

            # Ensure data is a numpy array (it usually is from cdflib, but good practice)
            data_array_np = np.array(data_array)
            print_manager.debug(f"  Data loaded: '{data_var_name}', Shape: {data_array_np.shape}, Dtype: {data_array_np.dtype}")

            # Final Check: Length Mismatch
            if len(datetime_array_np) != len(data_array_np):
                print_manager.error(f"LENGTH MISMATCH in {filepath}: Time ({len(datetime_array_np)}) vs Data '{data_var_name}' ({len(data_array_np)}). Cannot proceed reliably.")
                return None, None # Treat mismatch as failure

            print_manager.status(f"--- Successfully loaded Time & Data from {os.path.basename(filepath)} --- ")
            return datetime_array_np, data_array_np

    except Exception as e:
        print_manager.error(f"General error loading time/data from {filepath}: {e}")
        import traceback
        print_manager.error(traceback.format_exc())
        return None, None

# --- Test Functions ---

# Test 1: Basic Datetime Extraction
def test_extract_single_datetime():
    """Test extracting datetime array from a single known CDF file."""
    print("\n===== TEST 1: Basic Datetime Extraction =====")
    print(f"Searching for CDFs in: {TEST_CDF_DIR}")
    if not os.path.isdir(TEST_CDF_DIR):
        pytest.skip(f"CDF directory not found: {TEST_CDF_DIR}")
        return

    cdf_files = glob.glob(os.path.join(TEST_CDF_DIR, "**", "*.cdf"), recursive=True)
    if not cdf_files:
        pytest.skip(f"No CDF files found in {TEST_CDF_DIR}")
        return

    # Pick the first file found for simplicity
    test_file = cdf_files[0]
    print(f"Attempting to load datetime from: {os.path.basename(test_file)}")

    datetime_array = _load_datetime_from_cdf(test_file)

    assert datetime_array is not None, f"Failed to load datetime array from {test_file}"
    assert len(datetime_array) > 0, "Loaded datetime array is empty"
    assert isinstance(datetime_array, np.ndarray), "Loaded array is not a numpy array"
    assert datetime_array.dtype == 'datetime64[ns]', f"Loaded array has incorrect dtype: {datetime_array.dtype}"

    print(f"Successfully loaded array. Shape: {datetime_array.shape}, Dtype: {datetime_array.dtype}")
    print(f"First timestamp: {datetime_array[0]}")
    print(f"Last timestamp: {datetime_array[-1]}")
    print("===== TEST 1 PASSED =====")

# Test 2: Random Pair Comparison
def test_random_pair_comparison():
    """Loads datetimes from two random, different CDFs and compares their ranges."""
    print("\n===== TEST 2: Random Pair Comparison =====")
    print(f"Searching for CDFs in: {TEST_CDF_DIR}")
    if not os.path.isdir(TEST_CDF_DIR):
        pytest.skip(f"CDF directory not found: {TEST_CDF_DIR}")
        return

    cdf_files = sorted(glob.glob(os.path.join(TEST_CDF_DIR, "**", "*.cdf"), recursive=True))
    if len(cdf_files) < 2:
        pytest.skip(f"Need at least 2 CDF files for comparison, found {len(cdf_files)} in {TEST_CDF_DIR}")
        return

    print(f"Found {len(cdf_files)} CDF files. Creating numerical list:")
    file_map = {i: os.path.basename(f) for i, f in enumerate(cdf_files)}
    for i, fname in file_map.items():
        print(f"  {i}: {fname}")

    # --- Select two DIFFERENT random indices --- 
    # Use random.sample to ensure two unique indices are chosen
    random_indices = random.sample(range(len(cdf_files)), 2)
    index1, index2 = sorted(random_indices) # Ensure index1 < index2 for easier comparison later
    
    file1_path = cdf_files[index1]
    file2_path = cdf_files[index2]
    print(f"\nSelected random file indices: {index1} ({file_map[index1]}) and {index2} ({file_map[index2]})")

    # --- Load datetime arrays --- 
    dt_array1 = _load_datetime_from_cdf(file1_path)
    dt_array2 = _load_datetime_from_cdf(file2_path)

    # Handle potential loading failures
    if dt_array1 is None or dt_array2 is None:
        pytest.fail("Failed to load one or both datetime arrays for comparison.")
        return # Added return for clarity, though pytest.fail exits
    if len(dt_array1) == 0 or len(dt_array2) == 0:
         pytest.fail("One or both loaded datetime arrays are empty.")
         return

    # --- Perform Comparisons --- 
    start1, end1 = dt_array1[0], dt_array1[-1]
    start2, end2 = dt_array2[0], dt_array2[-1]

    print("\n--- Comparing Timestamps --- ")
    print(f"Array 1 ({file_map[index1]}): {start1} to {end1}")
    print(f"Array 2 ({file_map[index2]}): {start2} to {end2}")

    # Perform the crucial comparisons (like in the merge logic)
    comparison_start1_lt_start2 = start1 < start2
    comparison_end1_lt_start2 = end1 < start2
    comparison_start1_gt_end2 = start1 > end2
    
    print(f"Comparison: start1 < start2 ? {comparison_start1_lt_start2}")
    print(f"Comparison: end1 < start2 ? {comparison_end1_lt_start2}") # This determines if range 1 is entirely before range 2
    print(f"Comparison: start1 > end2 ? {comparison_start1_gt_end2}") # This determines if range 1 is entirely after range 2

    # --- Verify against Numerical Order --- 
    # Since we sorted the indices (index1 < index2), we expect array1 to be chronologically earlier
    print("\n--- Verifying Chronological Order vs Numerical Index --- ")
    print(f"Numerical check: index1 ({index1}) < index2 ({index2})? True")
    print(f"Temporal check based on comparison: end1 < start2 ? {comparison_end1_lt_start2}")
    
    # Assertion: Since the files are sorted by name (usually chronological), 
    # and index1 < index2, we expect the end of file 1 to be before the start of file 2.
    # This assumes daily files with no gaps/overlap for this specific assertion.
    # A more robust check might just compare start times.
    assert comparison_start1_lt_start2, f"Assertion Failed: Start time of file {index1} ({start1}) should be before start time of file {index2} ({start2}) based on sorted indices."
    # Optionally, assert end1 < start2 if you are sure files represent distinct, sequential days
    # assert comparison_end1_lt_start2, f"Assertion Failed: End time of file {index1} ({end1}) should be before start time of file {index2} ({start2}) for sequential daily files."

    print("Comparison results are consistent with the numerical order of the files.")
    print("===== TEST 2 PASSED =====")

# Test 3: Two Array Merge
def test_two_array_merge():
    """Loads two random, non-overlapping CDFs and merges their datetime arrays."""
    print("\n===== TEST 3: Two Array Merge =====")
    print(f"Searching for CDFs in: {TEST_CDF_DIR}")
    if not os.path.isdir(TEST_CDF_DIR):
        pytest.skip(f"CDF directory not found: {TEST_CDF_DIR}")
        return

    cdf_files = sorted(glob.glob(os.path.join(TEST_CDF_DIR, "**", "*.cdf"), recursive=True))
    if len(cdf_files) < 2:
        pytest.skip(f"Need at least 2 CDF files for merge test, found {len(cdf_files)} in {TEST_CDF_DIR}")
        return

    print(f"Found {len(cdf_files)} CDF files.")

    # --- Select two DIFFERENT random indices --- 
    random_indices = random.sample(range(len(cdf_files)), 2)
    index1, index2 = sorted(random_indices)
    file1_path = cdf_files[index1]
    file2_path = cdf_files[index2]
    print(f"Selected random file indices for merge: {index1} ({os.path.basename(file1_path)}) and {index2} ({os.path.basename(file2_path)})")

    # --- Load datetime arrays --- 
    dt_array1 = _load_datetime_from_cdf(file1_path)
    dt_array2 = _load_datetime_from_cdf(file2_path)

    if dt_array1 is None or dt_array2 is None or len(dt_array1) == 0 or len(dt_array2) == 0:
        pytest.fail("Failed to load one or both datetime arrays for merge.")
        return
        
    original_len1 = len(dt_array1)
    original_len2 = len(dt_array2)
    original_start1 = dt_array1[0]
    original_end1 = dt_array1[-1]
    original_start2 = dt_array2[0]
    original_end2 = dt_array2[-1]
    print(f"Array 1 original length: {original_len1}, Range: {original_start1} to {original_end1}")
    print(f"Array 2 original length: {original_len2}, Range: {original_start2} to {original_end2}")

    # --- Merge Logic (Simplified non-overlapping case) --- 
    print("\n--- Performing Merge (Concatenate & Sort) --- ")
    # Assuming non-overlapping as we selected different indices from sorted list
    merged_array = np.concatenate([dt_array1, dt_array2])
    print(f"Concatenated array length: {len(merged_array)}")
    sort_indices = np.argsort(merged_array)
    merged_array_sorted = merged_array[sort_indices]
    print(f"Sorted merged array length: {len(merged_array_sorted)}")

    # --- Verification --- 
    expected_len = original_len1 + original_len2
    merged_start = merged_array_sorted[0]
    merged_end = merged_array_sorted[-1]

    print("\n--- Verifying Merge Results --- ")
    print(f"Expected Length: {expected_len}, Actual Length: {len(merged_array_sorted)}")
    print(f"Expected Start: {original_start1}, Actual Start: {merged_start}") # Assuming index1 < index2
    print(f"Expected End: {original_end2}, Actual End: {merged_end}")     # Assuming index1 < index2

    assert len(merged_array_sorted) == expected_len, "Merged array length is incorrect."
    # Compare start/end times. Allow for slight precision differences if necessary, but direct compare should work for datetime64
    assert merged_start == original_start1, "Merged array start time does not match expected start time."
    assert merged_end == original_end2, "Merged array end time does not match expected end time."
    # Verify sorting
    assert np.all(merged_array_sorted[:-1] <= merged_array_sorted[1:]), "Merged array is not sorted correctly."

    print("Merge verification successful.")
    print("===== TEST 3 PASSED =====")

# Test 4: Three Array Merge Placement
def test_three_array_merge_placement():
    """Loads three CDFs (allowing repeats), merges the first two,
       and determines the placement of the third relative to the merged result.
       Runs the core logic multiple times for robustness.
    """
    print("\n===== TEST 4: Three Array Merge Placement (Running 100 Iterations) =====")
    print(f"Searching for CDFs in: {TEST_CDF_DIR}")
    if not os.path.isdir(TEST_CDF_DIR):
        pytest.skip(f"CDF directory not found: {TEST_CDF_DIR}")
        return

    cdf_files = sorted(glob.glob(os.path.join(TEST_CDF_DIR, "**", "*.cdf"), recursive=True))
    if len(cdf_files) < 3: # Need at least 3 for meaningful placement, even if they repeat
        pytest.skip(f"Need at least 3 CDF files (even if repeated) for this test, found {len(cdf_files)} in {TEST_CDF_DIR}")
        return

    print(f"Found {len(cdf_files)} CDF files. Creating numerical list:")
    file_map = {i: os.path.basename(f) for i, f in enumerate(cdf_files)}
    for i, fname in file_map.items():
         print(f"  {i}: {fname}") # Print only once at the start

    num_iterations = 100
    for iteration in range(1, num_iterations + 1):
        print(f"\n--- Iteration {iteration}/{num_iterations} ---")

        # --- Select Three Files (Allowing Repeats for the third one) ---
        # Ensure first two are different for a meaningful initial merge
        idx1, idx2 = random.sample(range(len(cdf_files)), 2)
        idx3 = random.choice(range(len(cdf_files))) # Third can be same as 1 or 2

        # Ensure idx1 is always the smaller index for consistent ordering
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1 # Swap them

        file1 = cdf_files[idx1]
        file2 = cdf_files[idx2]
        file3 = cdf_files[idx3]

        print(f"Selected initial pair: {idx1} ({file_map[idx1]}) and {idx2} ({file_map[idx2]})")

        # --- Load and Merge Initial Pair ---
        array1 = _load_datetime_from_cdf(file1)
        array2 = _load_datetime_from_cdf(file2)

        if array1 is None or array2 is None:
            print("Skipping iteration due to loading failure.")
            continue # Skip this iteration if loading failed

        # Basic merge (assuming non-overlap for this part, consistent with test 3)
        merged_array = np.sort(np.concatenate((array1, array2)))
        merged_start = merged_array[0]
        merged_end = merged_array[-1]
        print(f"Merged initial pair ({idx1}, {idx2}). Range: {merged_start} to {merged_end}")

        # --- Load Third Array ---
        print(f"Selected third file: {idx3} ({file_map[idx3]}) ")
        array3 = _load_datetime_from_cdf(file3)
        if array3 is None:
            print("Skipping iteration due to loading failure for third file.")
            continue

        start3 = array3[0]
        end3 = array3[-1]
        print(f"Third array ({idx3}) Range: {start3} to {end3}")


        # --- Determine Placement of Third Array ---
        print("\n--- Determining Placement of Third Array --- ")
        placement = "Undetermined"
        # Check edge cases first
        if end3 < merged_start:
            placement = "Entirely Before"
        elif start3 > merged_end:
            placement = "Entirely After"
        elif start3 == merged_start and end3 == merged_end:
             placement = "Identical" # Should only happen if idx3 is idx1 or idx2 and they are adjacent days
        elif start3 >= merged_start and end3 <= merged_end:
            placement = "Contained Within" # Covers identical start/end too if not caught above
        elif start3 < merged_start and end3 > merged_end:
            placement = "Enveloping"
        elif start3 < merged_start and end3 >= merged_start and end3 <= merged_end:
             placement = "Overlapping Start"
        elif start3 >= merged_start and start3 <= merged_end and end3 > merged_end:
             placement = "Overlapping End"
        elif start3 < merged_start and end3 < merged_start: # Should be covered by "Entirely Before"
             placement = "Error - Should be Before"
        elif start3 > merged_end and end3 > merged_end: # Should be covered by "Entirely After"
            placement = "Error - Should be After"
        else:
             placement = f"Unknown/Complex Overlap (start3={start3}, end3={end3}, merged_start={merged_start}, merged_end={merged_end})"


        print(f"Determined Placement: {placement}")

        # --- Compare Placement with Numerical Indices ---
        # This comparison is less direct now as idx3 can be anywhere relative to idx1/idx2
        print("\n--- Comparing Placement with Numerical Indices --- ")
        numerical_placement_guess = "Ambiguous (repeats allowed)"
        if idx3 < idx1:
            numerical_placement_guess = "Numerically Before Initial Pair"
        elif idx3 > idx2:
            numerical_placement_guess = "Numerically After Initial Pair"
        elif idx3 == idx1 or idx3 == idx2:
            numerical_placement_guess = "Numerically Same as One of Initial Pair"
        elif idx1 < idx3 < idx2:
             numerical_placement_guess = "Numerically Between Initial Pair"

        print(f"Numerical Placement Guess: {numerical_placement_guess}")

        # Basic assertion: Ensure a placement category was determined
        assert placement != "Undetermined" and not placement.startswith("Error")

    print(f"\n===== Completed {num_iterations} iterations of TEST 4 =====")

# Test 5: Three Array Sampled Merge Verification
def test_three_array_sampled_merge_verification():
    """Loads three random CDFs, takes variable-length samples from the start,
       merges them, and verifies internal consistency by checking sample endpoints.
    """
    print("\n===== TEST 5: Three Array Sampled Merge Verification =====")
    print(f"Searching for CDFs in: {TEST_CDF_DIR}")
    if not os.path.isdir(TEST_CDF_DIR):
        pytest.skip(f"CDF directory not found: {TEST_CDF_DIR}")
        return

    cdf_files = sorted(glob.glob(os.path.join(TEST_CDF_DIR, "**", "*.cdf"), recursive=True))
    if len(cdf_files) < 3:
        pytest.skip(f"Need at least 3 CDF files for this test, found {len(cdf_files)} in {TEST_CDF_DIR}")
        return

    print(f"Found {len(cdf_files)} CDF files.")
    file_map = {i: os.path.basename(f) for i, f in enumerate(cdf_files)}

    # --- Select Three Files (Allowing Repeats) ---
    indices = random.choices(range(len(cdf_files)), k=3) # Use choices to allow repeats
    print(f"Selected file indices: {indices} ({[file_map[i] for i in indices]}) ")

    # --- Load Full Arrays and Create Samples ---
    sample_info = [] # List to store tuples: (original_index, sample_array, sample_end_time, sample_length)
    all_samples_list = []

    for i, idx in enumerate(indices):
        filepath = cdf_files[idx]
        print(f"--- Processing File {i+1} (Index {idx}: {file_map[idx]}) ---")
        full_array = _load_datetime_from_cdf(filepath)
        if full_array is None or len(full_array) == 0:
            pytest.fail(f"Failed to load or empty array for index {idx}: {file_map[idx]}")
            return

        # Choose a random sample length (at least 1)
        max_len = len(full_array)
        sample_length = random.randint(1, max_len)
        sample_array = full_array[:sample_length]
        sample_end_time = sample_array[-1]

        print(f"  Full length: {max_len}")
        print(f"  Sample length chosen: {sample_length}")
        print(f"  Sample range: {sample_array[0]} to {sample_end_time}")

        sample_info.append((idx, sample_array, sample_end_time, sample_length))
        all_samples_list.append(sample_array)

    # --- Merge Sample Arrays ---
    print("\n--- Merging Sample Arrays --- ")
    if not all_samples_list:
         pytest.fail("No samples were collected.")
         return

    concatenated_samples = np.concatenate(all_samples_list)
    final_merged_array = np.sort(concatenated_samples)
    print(f"Total concatenated length: {len(concatenated_samples)}")
    print(f"Final sorted merged array length: {len(final_merged_array)}")

    # --- Basic Verification --- 
    expected_total_length = sum(info[3] for info in sample_info)
    print(f"Expected total length: {expected_total_length}")
    assert len(final_merged_array) == expected_total_length, "Final merged length does not match sum of sample lengths."
    print("Basic length verification PASSED.")

    # --- Detailed Verification (Check Endpoints) --- 
    print("\n--- Detailed Verification: Checking Sample Endpoints in Merged Array --- ")
    # Sort the sample_info based on the start time of each SAMPLE array
    # We need a key function that accesses the first element of the sample array (info[1][0])
    # Handle potential empty sample array edge case (though randint(1, max_len) prevents this)
    try:
        sorted_sample_info = sorted(sample_info, key=lambda info: info[1][0])
    except IndexError:
         pytest.fail("Attempted to sort based on an empty sample array.")
         return

    print("Chronological order of samples (based on start time):")
    for idx, _, _, length in sorted_sample_info:
        print(f"  Index: {idx} ({file_map[idx]}), Length: {length}")

    current_offset = 0
    verification_passed = True
    for idx, sample_array, expected_end_time, sample_length in sorted_sample_info:
        expected_end_index = current_offset + sample_length - 1
        if expected_end_index >= len(final_merged_array):
             print(f"ERROR: Calculated end index {expected_end_index} is out of bounds for merged array length {len(final_merged_array)}.")
             verification_passed = False
             break # No point continuing if index is wrong

        actual_end_time = final_merged_array[expected_end_index]

        print(f"  Verifying sample from index {idx} ({file_map[idx]}):")
        print(f"    Sample Length: {sample_length}")
        print(f"    Expected End Index in Merged Array: {expected_end_index}")
        print(f"    Expected End Timestamp (from sample): {expected_end_time}")
        print(f"    Actual Timestamp at Index {expected_end_index}: {actual_end_time}")

        if actual_end_time == expected_end_time:
            print("    Timestamp MATCHES. Verification PASSED for this sample.")
        else:
            print("    Timestamp MISMATCH. Verification FAILED for this sample.")
            # Add more debug if needed: print the slice around the expected index
            context_slice_start = max(0, expected_end_index - 2)
            context_slice_end = min(len(final_merged_array), expected_end_index + 3)
            print(f"      Context in merged array [{context_slice_start}:{context_slice_end}]: {final_merged_array[context_slice_start:context_slice_end]}")
            verification_passed = False
            # Optional: break on first failure or let it check all?
            # break 

        # Update offset for the next sample
        current_offset += sample_length

    assert verification_passed, "Detailed endpoint verification failed for one or more samples."
    print("\nDetailed endpoint verification PASSED for all samples.")
    print("===== TEST 5 PASSED =====")

# Test 6: Three Array Data Merge Verification
def test_six_array_data_merge_verification():
    """Loads three random CDFs (time + data), takes variable-length samples,
       merges them using time-based sort indices, and verifies internal consistency
       by checking both time and data endpoints. Runs multiple iterations.
    """
    print("\n===== TEST 6: Three Array Data+Time Merge Verification (Running 20 Iterations) =====")
    print(f"Searching for CDFs in: {TEST_CDF_DIR}")
    if not os.path.isdir(TEST_CDF_DIR):
        pytest.skip(f"CDF directory not found: {TEST_CDF_DIR}")
        return

    cdf_files = sorted(glob.glob(os.path.join(TEST_CDF_DIR, "**", "*.cdf"), recursive=True))
    if len(cdf_files) < 3: # Still need at least 3 files total, even if sampling from the same one multiple times
        pytest.skip(f"Need at least 3 CDF files available for this test, found {len(cdf_files)} in {TEST_CDF_DIR}")
        return

    print(f"Found {len(cdf_files)} CDF files. Testing with data var: {DATA_VARIABLE_NAME_BR}")
    file_map = {i: os.path.basename(f) for i, f in enumerate(cdf_files)}

    num_iterations = 20 # Set number of iterations
    overall_verification_passed = True # Track overall success

    for iteration in range(1, num_iterations + 1):
        print(f"\n--- Iteration {iteration}/{num_iterations} ---")
        iteration_passed = True # Track success for this iteration

        # --- Select Three Files (Allowing Repeats) ---
        indices = random.choices(range(len(cdf_files)), k=3)
        print(f"Selected file indices: {indices} ({[file_map[i] for i in indices]}) ")

        # --- Load Full Arrays (Time & Data) and Create Samples ---
        sample_info = []
        all_time_samples_list = []
        all_data_samples_list = []
        load_failed = False

        for i, idx in enumerate(indices):
            filepath = cdf_files[idx]
            print(f"  --- Processing File {i+1} (Index {idx}: {file_map[idx]}) ---")
            full_time_array, full_data_array = _load_time_and_data_from_cdf(filepath, DATA_VARIABLE_NAME_BR)

            if full_time_array is None or full_data_array is None or len(full_time_array) == 0:
                print(f"    LOAD FAILED or empty array for index {idx}. Skipping this iteration.")
                load_failed = True
                break # Stop processing files for this iteration

            max_len = len(full_time_array)
            sample_length = random.randint(1, max_len)
            sample_time_array = full_time_array[:sample_length]
            sample_data_array = full_data_array[:sample_length]
            sample_end_time = sample_time_array[-1]
            sample_end_data = sample_data_array[-1]

            print(f"    Full length: {max_len}")
            print(f"    Sample length chosen: {sample_length}")
            print(f"    Sample time range: {sample_time_array[0]} to {sample_end_time}")
            # print(f"    Sample data range (first/last): {sample_data_array[0]} / {sample_end_data}") # Can be verbose

            sample_info.append((idx, sample_time_array, sample_data_array, sample_end_time, sample_end_data, sample_length))
            all_time_samples_list.append(sample_time_array)
            all_data_samples_list.append(sample_data_array)

        if load_failed:
            overall_verification_passed = False # Mark overall as failed if any iteration fails loading
            continue # Move to the next iteration

        # --- Merge Sample Arrays ---
        print("\n  --- Merging Sample Arrays (Time + Data) --- ")
        concatenated_time_samples = np.concatenate(all_time_samples_list)
        concatenated_data_samples = np.concatenate(all_data_samples_list)
        sort_indices = np.argsort(concatenated_time_samples)
        final_merged_time_array = concatenated_time_samples[sort_indices]
        final_merged_data_array = concatenated_data_samples[sort_indices]
        print(f"  Final merged array length: {len(final_merged_time_array)}")

        # --- Basic Verification ---
        expected_total_length = sum(info[5] for info in sample_info)
        print(f"  Expected total length: {expected_total_length}")
        if not (len(final_merged_time_array) == expected_total_length and len(final_merged_data_array) == expected_total_length):
            print("  ERROR: Basic length verification FAILED.")
            iteration_passed = False
            overall_verification_passed = False
            continue # Skip detailed check if basic length fails

        print("  Basic length verification PASSED.")

        # --- Detailed Verification ---
        print("\n  --- Detailed Verification: Checking Sample Endpoints --- ")
        try:
            sorted_sample_info = sorted(sample_info, key=lambda info: info[1][0])
        except IndexError:
            print("  ERROR: Attempted to sort based on an empty sample time array. Skipping detailed check.")
            iteration_passed = False
            overall_verification_passed = False
            continue

        current_offset = 0
        detailed_verification_passed_this_iter = True
        for idx, _, _, expected_end_time, expected_end_data, sample_length in sorted_sample_info:
            expected_end_index = current_offset + sample_length - 1
            if expected_end_index >= len(final_merged_time_array):
                 print(f"    ERROR: Calculated end index {expected_end_index} out of bounds for merged array length {len(final_merged_time_array)}.")
                 detailed_verification_passed_this_iter = False
                 break

            actual_end_time = final_merged_time_array[expected_end_index]
            actual_end_data = final_merged_data_array[expected_end_index]

            time_match = (actual_end_time == expected_end_time)
            if isinstance(expected_end_data, (float, np.floating)):
                data_match = np.isclose(actual_end_data, expected_end_data, rtol=1e-09, atol=1e-09)
            else:
                data_match = np.array_equal(actual_end_data, expected_end_data)

            if time_match and data_match:
                print(f"    Sample {idx} (len {sample_length}): Time & Data MATCH at index {expected_end_index}.")
            else:
                print(f"    Sample {idx} (len {sample_length}): MISMATCH DETECTED at index {expected_end_index}.")
                if not time_match: print(f"      Time: Expected {expected_end_time}, Got {actual_end_time}")
                if not data_match: print(f"      Data: Expected {expected_end_data}, Got {actual_end_data}")
                detailed_verification_passed_this_iter = False
                # break # Optional: Stop on first failure within an iteration

            current_offset += sample_length

        if not detailed_verification_passed_this_iter:
            print("  Detailed endpoint verification FAILED for this iteration.")
            iteration_passed = False
            overall_verification_passed = False
        else:
            print("  Detailed endpoint verification PASSED for this iteration.")

    # Final assertion after all iterations
    print(f"\n===== Completed {num_iterations} iterations of TEST 6 =====")
    assert overall_verification_passed, "One or more iterations failed during Test 6."
    print("Overall verification PASSED for all iterations.")
    print("===== TEST 6 PASSED =====\n") # Add newline for separation

# Test 7: Three Array Separate Component Merge Verification
def test_seven_separate_component_merge():
    """Loads three random CDFs (time + vector data), splits vector data
       into br, bt, bn components, takes variable-length samples of time and
       each component, merges them using time-based sort indices, and verifies
       internal consistency by checking endpoints of time, br, bt, and bn.
       Runs multiple iterations.
    """
    print("\n===== TEST 7: Three Array Separate Component Merge Verification (Running 40 Iterations) =====")
    print(f"Searching for CDFs in: {TEST_CDF_DIR}")
    if not os.path.isdir(TEST_CDF_DIR):
        pytest.skip(f"CDF directory not found: {TEST_CDF_DIR}")
        return

    cdf_files = sorted(glob.glob(os.path.join(TEST_CDF_DIR, "**", "*.cdf"), recursive=True))
    if len(cdf_files) < 3:
        pytest.skip(f"Need at least 3 CDF files available for this test, found {len(cdf_files)} in {TEST_CDF_DIR}")
        return

    print(f"Found {len(cdf_files)} CDF files. Testing with vector var: {DATA_VARIABLE_NAME_BR}")
    file_map = {i: os.path.basename(f) for i, f in enumerate(cdf_files)}

    num_iterations = 40 # Increase to 40 iterations
    overall_verification_passed = True # Track overall success

    for iteration in range(1, num_iterations + 1):
        print(f"\n--- Iteration {iteration}/{num_iterations} ---")
        iteration_passed = True

        # --- Select Three Files (Allowing Repeats) ---
        indices = random.choices(range(len(cdf_files)), k=3)
        print(f"Selected file indices: {indices} ({[file_map[i] for i in indices]}) ")

        # --- Load Full Arrays, Split Components, and Create Samples ---
        # Store tuple: (idx, s_time, s_br, s_bt, s_bn, e_time, e_br, e_bt, e_bn, length)
        sample_info = []
        all_time_samples = []
        all_br_samples = []
        all_bt_samples = []
        all_bn_samples = []
        load_failed = False

        for i, idx in enumerate(indices):
            filepath = cdf_files[idx]
            print(f"  --- Processing File {i+1} (Index {idx}: {file_map[idx]}) ---")
            full_time_array, full_vector_data = _load_time_and_data_from_cdf(filepath, DATA_VARIABLE_NAME_BR)

            if full_time_array is None or full_vector_data is None or len(full_time_array) == 0:
                print(f"    LOAD FAILED or empty array for index {idx}. Skipping this iteration.")
                load_failed = True
                break

            # Check shape - expecting (N, 3) for BR, BT, BN
            if len(full_vector_data.shape) != 2 or full_vector_data.shape[1] != 3:
                 print(f"    UNEXPECTED DATA SHAPE for index {idx}: {full_vector_data.shape}. Expected (N, 3). Skipping iteration.")
                 load_failed = True
                 break

            # Split into components
            full_br_array = full_vector_data[:, 0]
            full_bt_array = full_vector_data[:, 1]
            full_bn_array = full_vector_data[:, 2]

            max_len = len(full_time_array)
            sample_length = random.randint(1, max_len)

            # Sample Time and EACH component
            sample_time = full_time_array[:sample_length]
            sample_br = full_br_array[:sample_length]
            sample_bt = full_bt_array[:sample_length]
            sample_bn = full_bn_array[:sample_length]

            # Record end values
            end_time = sample_time[-1]
            end_br = sample_br[-1]
            end_bt = sample_bt[-1]
            end_bn = sample_bn[-1]

            print(f"    Full length: {max_len}")
            print(f"    Sample length chosen: {sample_length}")
            print(f"    Sample time range: {sample_time[0]} to {end_time}")
            print(f"    End Values: Br={end_br:.2f}, Bt={end_bt:.2f}, Bn={end_bn:.2f}")

            sample_info.append((idx, sample_time, sample_br, sample_bt, sample_bn, end_time, end_br, end_bt, end_bn, sample_length))
            all_time_samples.append(sample_time)
            all_br_samples.append(sample_br)
            all_bt_samples.append(sample_bt)
            all_bn_samples.append(sample_bn)

        if load_failed:
            overall_verification_passed = False
            continue

        # --- Merge Sample Arrays (Time and Components Synchronized) ---
        print("\n  --- Merging Sample Arrays (Time + Br + Bt + Bn) --- ")
        cat_time = np.concatenate(all_time_samples)
        cat_br = np.concatenate(all_br_samples)
        cat_bt = np.concatenate(all_bt_samples)
        cat_bn = np.concatenate(all_bn_samples)

        sort_indices = np.argsort(cat_time, kind='stable')

        merged_time = cat_time[sort_indices]
        merged_br = cat_br[sort_indices]
        merged_bt = cat_bt[sort_indices]
        merged_bn = cat_bn[sort_indices]

        print(f"  Final merged array length: {len(merged_time)}")

        # --- Basic Verification ---
        expected_total_length = sum(info[9] for info in sample_info) # Index 9 is length
        print(f"  Expected total length: {expected_total_length}")
        lengths_match = (
            len(merged_time) == expected_total_length and
            len(merged_br) == expected_total_length and
            len(merged_bt) == expected_total_length and
            len(merged_bn) == expected_total_length
        )
        if not lengths_match:
            print("  ERROR: Basic length verification FAILED for one or more arrays.")
            iteration_passed = False
            overall_verification_passed = False
            continue

        print("  Basic length verification PASSED.")

        # --- Detailed Verification ---
        print("\n  --- Detailed Verification: Checking Sample Endpoints (Time, Br, Bt, Bn) --- ")
        try:
            # Sort samples by start time (info[1] is sample_time)
            sorted_sample_info = sorted(sample_info, key=lambda info: info[1][0])
        except IndexError:
            print("  ERROR: Attempted to sort based on an empty sample time array.")
            iteration_passed = False
            overall_verification_passed = False
            continue

        current_offset = 0
        detailed_verification_passed_this_iter = True
        for idx, _, _, _, _, exp_end_time, exp_end_br, exp_end_bt, exp_end_bn, sample_len in sorted_sample_info:
            exp_end_idx = current_offset + sample_len - 1
            if exp_end_idx >= len(merged_time):
                 print(f"    ERROR: Calculated end index {exp_end_idx} out of bounds for merged array length {len(merged_time)}.")
                 detailed_verification_passed_this_iter = False
                 break

            act_end_time = merged_time[exp_end_idx]
            act_end_br = merged_br[exp_end_idx]
            act_end_bt = merged_bt[exp_end_idx]
            act_end_bn = merged_bn[exp_end_idx]

            time_match = (act_end_time == exp_end_time)
            # Assume br, bt, bn are floats for comparison
            # Handle NaNs explicitly: NaN == NaN should be True for this test
            br_match = (np.isnan(act_end_br) and np.isnan(exp_end_br)) or np.isclose(act_end_br, exp_end_br, rtol=1e-09, atol=1e-09, equal_nan=True)
            bt_match = (np.isnan(act_end_bt) and np.isnan(exp_end_bt)) or np.isclose(act_end_bt, exp_end_bt, rtol=1e-09, atol=1e-09, equal_nan=True)
            bn_match = (np.isnan(act_end_bn) and np.isnan(exp_end_bn)) or np.isclose(act_end_bn, exp_end_bn, rtol=1e-09, atol=1e-09, equal_nan=True)

            if time_match and br_match and bt_match and bn_match:
                print(f"    Sample {idx} (len {sample_len}): Time, Br, Bt, Bn MATCH at index {exp_end_idx}.")
            else:
                print(f"    Sample {idx} (len {sample_len}): MISMATCH DETECTED at index {exp_end_idx}.")
                if not time_match: print(f"      Time: Exp={exp_end_time}, Act={act_end_time}")
                if not br_match: print(f"      Br:   Exp={exp_end_br:.4f}, Act={act_end_br:.4f}")
                if not bt_match: print(f"      Bt:   Exp={exp_end_bt:.4f}, Act={act_end_bt:.4f}")
                if not bn_match: print(f"      Bn:   Exp={exp_end_bn:.4f}, Act={act_end_bn:.4f}")
                detailed_verification_passed_this_iter = False
                # break

            current_offset += sample_len

        if not detailed_verification_passed_this_iter:
            print("  Detailed endpoint verification FAILED for this iteration.")
            iteration_passed = False
            overall_verification_passed = False
        else:
            print("  Detailed endpoint verification PASSED for this iteration.")

    # Final assertion after all iterations
    print(f"\n===== Completed {num_iterations} iterations of TEST 7 =====")
    assert overall_verification_passed, "One or more iterations failed during Test 7."
    print("Overall verification PASSED for all iterations.")
    print("===== TEST 7 PASSED =====\n") 