import plotbot as pb
import os
import shutil
import sys
import glob # Import glob for finding test files
import plotbot.data_tracker as dt
import plotbot.data_cubby as dc
import pytest
import numpy as np

# Define the MAIN storage directory - Tests will operate here
storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data_cubby')

def setup_function():
    """Ensures main storage dir exists and cleans ONLY specific test files/dirs within it."""
    print(f"\nDEBUG: Setup using MAIN storage directory: {storage_dir}")

    # 1. Ensure the main storage directory exists - NEVER DELETE IT
    try:
        os.makedirs(storage_dir, exist_ok=True)
        print(f"DEBUG: Ensured MAIN storage directory exists: {storage_dir}")
    except OSError as e:
        print(f"ERROR: Failed to create MAIN storage directory {storage_dir}: {e}")
        
    # 2. Clean ONLY specific known test artifacts within the main directory
    index_path = os.path.join(storage_dir, 'data_cubby_index.json')
    # Specific PKL directory and pattern for mag_rtn_4sa daily tests
    test_pkl_dir = os.path.join(storage_dir, 'psp_data', 'fields', 'l2', 'mag_rtn_4_per_cycle') 
    test_pkl_pattern = os.path.join(test_pkl_dir, 'psp_fld_l2_mag_rtn_4_sa_per_cyc_202409*_v*.pkl') # More general pattern for test dates

    # Remove specific index file
    try:
        if os.path.exists(index_path):
            os.remove(index_path)
            print(f"DEBUG: Removed test index file: {index_path}")
    except OSError as e:
        print(f"DEBUG: Error removing test index file {index_path}: {e}")

    # Remove specific PKL files matching the pattern
    try:
        for f in glob.glob(test_pkl_pattern):
            os.remove(f)
            print(f"DEBUG: Removed test PKL file: {f}")
        # Clean the specific directory if it exists (careful not to delete parent dirs)
        if os.path.exists(test_pkl_dir):
             # Check if directory is empty after removing files - only remove if truly empty? 
             # Safer to just ensure it exists and let teardown handle removal if needed
             print(f"DEBUG: Test PKL directory checked: {test_pkl_dir}")
    except OSError as e:
        print(f"DEBUG: Error removing test PKL files {test_pkl_pattern}: {e}")
        
    # 3. Clean in-memory caches (DataCubby and global_tracker)
    print("DEBUG: Clearing in-memory data_cubby state...")
    dc.cubby.clear()
    try:
        pb.data_cubby.use_pkl_storage = False # Ensure it starts disabled
        print("DEBUG: Reset use_pkl_storage to False via setter.")
        pb.data_cubby.set_storage_directory(storage_dir) 
        print(f"DEBUG: Reset DataCubby storage directory to main: {storage_dir}")
    except Exception as e:
        print(f"DEBUG: Error during DataCubby memory reset: {e}")

    print("DEBUG: Clearing global_tracker state...")
    try:
        tracker = getattr(pb, 'global_tracker', None) or getattr(dt, 'global_tracker', None)
        if tracker:
            tracker.imported_ranges.clear()
            tracker.calculated_ranges.clear()
            print("DEBUG: Cleared global_tracker imported_ranges and calculated_ranges.")
        else:
            print("DEBUG: global_tracker not found.")
    except AttributeError:
        print("DEBUG: Error clearing global_tracker (AttributeError).")

def teardown_function():
    """Clean up SPECIFIC test files/dirs from MAIN directory after test run."""
    print(f"\nDEBUG: Cleaning up specific test files from MAIN directory: {storage_dir}")
    index_path = os.path.join(storage_dir, 'data_cubby_index.json')
    test_pkl_dir = os.path.join(storage_dir, 'psp_data', 'fields', 'l2', 'mag_rtn_4_per_cycle')
    test_pkl_pattern = os.path.join(test_pkl_dir, 'psp_fld_l2_mag_rtn_4_sa_per_cyc_202409*_v*.pkl') # General pattern

    # Remove specific index file
    try:
        if os.path.exists(index_path):
            os.remove(index_path)
            print(f"DEBUG: Teardown removed test index file: {index_path}")
    except OSError as e:
        print(f"DEBUG: Teardown error removing test index file {index_path}: {e}")

    # Remove specific PKL files matching the pattern
    try:
        files_removed_count = 0
        for f in glob.glob(test_pkl_pattern):
            os.remove(f)
            files_removed_count += 1
            print(f"DEBUG: Teardown removed test PKL file: {f}")
        if files_removed_count > 0:
             # Optionally remove the directory IF EMPTY and known to be test-specific
             # Be cautious with rmdir
             try:
                  if os.path.exists(test_pkl_dir) and not os.listdir(test_pkl_dir):
                      # Potentially remove intermediate dirs if empty too?
                      # For now, just try removing the leaf dir
                      # os.rmdir(test_pkl_dir) 
                      # print(f"DEBUG: Teardown removed empty test PKL directory: {test_pkl_dir}")
                      pass # Decide if removing the directory is safe/desired
             except OSError as rmdir_e:
                  print(f"DEBUG: Teardown error removing directory {test_pkl_dir}: {rmdir_e}")
        else:
             print(f"DEBUG: No matching PKL files found for pattern {test_pkl_pattern} during teardown.")
             
    except OSError as e:
        print(f"DEBUG: Teardown error removing test PKL files {test_pkl_pattern}: {e}")

    # Reset storage setting after test
    try:
         pb.data_cubby.use_pkl_storage = False
         print("DEBUG: Teardown reset use_pkl_storage to False.")
    except Exception as e:
         print(f"DEBUG: Error resetting use_pkl_storage in teardown: {e}")


@pytest.mark.daily_pkl # Add a marker for easier selective running
def test_save_multi_day_creates_daily_pkls(capsys):
    """Test that calling get_data for a multi-day range creates separate daily PKL files."""
    print("\n--- Starting test_save_multi_day_creates_daily_pkls ---")

    # --- Setup for this specific test ---
    pb.data_cubby.set_storage_directory(storage_dir)
    print(f"DEBUG: Ensured storage directory is set to MAIN: {storage_dir}")

    print("DEBUG: Enabling PKL storage for the test.")
    pb.data_cubby.use_pkl_storage = True
    assert pb.data_cubby.use_pkl_storage is True, "Failed to enable PKL storage"

    pb.print_manager.show_status = True
    pb.print_manager.show_debug = True # Enable debug prints for detailed logs

    # --- Define Time Range (2 days) and Variable ---
    trange = ['2024-09-28/00:00:00.000', '2024-09-29/23:59:59.999']
    variable_type = pb.mag_rtn_4sa # Use the class type to trigger download/import
    print(f"DEBUG: Test time range: {trange}")

    # --- Trigger Data Loading and Saving ---
    # Clear captured output before the call
    _ = capsys.readouterr() 
    print(f"DEBUG: Calling pb.get_data for {variable_type.__name__}...")
    try:
        pb.get_data(trange, variable_type) 
    except Exception as e:
        print(f"DEBUG: get_data call failed with error: {e}")
        pytest.fail(f"get_data call failed during test: {e}")

    print("DEBUG: pb.get_data call finished.")
    captured = capsys.readouterr()
    print("\n--- Captured STDOUT for get_data call ---")
    print(captured.out)
    print("--- End Captured STDOUT ---")
    
    # --- Verification ---
    # 1. Check base storage directory and index file
    assert os.path.exists(storage_dir), f"Storage directory {storage_dir} should exist."
    index_path = os.path.join(storage_dir, 'data_cubby_index.json')
    print(f"DEBUG: Checking for index file: {index_path}")
    assert os.path.exists(index_path), "data_cubby_index.json was not created."

    # 2. Check for the specific daily PKL files
    expected_pkl_dir = os.path.join(storage_dir, 'psp_data', 'fields', 'l2', 'mag_rtn_4_per_cycle')
    
    # Define expected filenames based on the dates in trange and known pattern
    # IMPORTANT: Assumes the version number might vary, uses glob pattern
    expected_file_day1_pattern = os.path.join(expected_pkl_dir, 'psp_fld_l2_mag_rtn_4_sa_per_cyc_20240928_v*.pkl')
    expected_file_day2_pattern = os.path.join(expected_pkl_dir, 'psp_fld_l2_mag_rtn_4_sa_per_cyc_20240929_v*.pkl')

    print(f"DEBUG: Checking for Day 1 PKL pattern: {expected_file_day1_pattern}")
    found_day1 = glob.glob(expected_file_day1_pattern)
    assert len(found_day1) > 0, f"Expected daily PKL file for Day 1 (pattern: {expected_file_day1_pattern}) was not found."
    print(f"DEBUG: Found Day 1 PKL file(s): {found_day1}")

    print(f"DEBUG: Checking for Day 2 PKL pattern: {expected_file_day2_pattern}")
    found_day2 = glob.glob(expected_file_day2_pattern)
    assert len(found_day2) > 0, f"Expected daily PKL file for Day 2 (pattern: {expected_file_day2_pattern}) was not found."
    print(f"DEBUG: Found Day 2 PKL file(s): {found_day2}")
    
    # 3. Optional: Check file sizes (basic integrity)
    if found_day1:
        file_size1 = os.path.getsize(found_day1[0])
        print(f"DEBUG: Day 1 PKL file size: {file_size1} bytes")
        assert file_size1 > 1000, f"Day 1 PKL file {found_day1[0]} seems too small ({file_size1} bytes)." # Expecting decent size for a day
    if found_day2:
        file_size2 = os.path.getsize(found_day2[0])
        print(f"DEBUG: Day 2 PKL file size: {file_size2} bytes")
        assert file_size2 > 1000, f"Day 2 PKL file {found_day2[0]} seems too small ({file_size2} bytes)."

    print("--- Finished test_save_multi_day_creates_daily_pkls --- ") 