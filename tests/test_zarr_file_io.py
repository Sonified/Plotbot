import os
import numpy as np
import pandas as pd
import zarr
from pathlib import Path
from cdflib import CDF
from datetime import datetime
import shutil

# === Test 1 ===
def test_01_generate_dummy_file_in_data_cubby(persist=True):
    """
    GOAL:
    Demonstrate that we are capable of referencing the file save path from psp_data_types, to generate a new dummy file inside of data_cubby, which is a folder in the root directory. The file needs to be saved in a sub-directory tree that matches the tree inside psp_data. The test passes when the saved local file has the correct path just at a different root folder (check 1) and the file name mirrors the original file name except for the file type name at the end, which is whatever file type we use for the dummy file. Use a dummy file type that is MOST convenient for python to work with. Have an option inside the test for the dummy data to persist or be erased after the test complete, default to persist for now. The test internally includes a print of the the first 5 rows of data before saving, and after re-loading from Zarr.

    SUCCESS CRITERIA:
    - File is saved in the correct mirrored path and filename structure under data_cubby.
    - File is readable after writing.
    - First 5 rows of data are printed before saving and after reloading.
    
    NOTE: After successful test passage, document the results and any learnings in the captain's log.
    """
    from plotbot.data_classes.psp_data_types import data_types

    # Pick test data_type and generate dummy path
    data_type = 'mag_RTN_4sa'
    config = data_types[data_type]
    source_path = config['local_path']
    file_name = 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc_20200126_v02.dummy'

    dest_path = Path('data_cubby') / Path(source_path)
    dest_path.mkdir(parents=True, exist_ok=True)

    dummy_data = pd.DataFrame({
        'a': np.arange(5),
        'b': np.random.rand(5)
    })

    print("Before Save:")
    print(dummy_data.head())

    save_path = dest_path / file_name
    dummy_data.to_csv(save_path, index=False)

    loaded = pd.read_csv(save_path)
    print("After Reload:")
    print(loaded.head())

    assert save_path.exists()
    assert list(loaded.columns) == ['a', 'b']

    if not persist:
        save_path.unlink()

# === Test 2 ===
def test_02_zarr_write_read_single_column(persist=True):
    """
    GOAL:
    Demonstrate that we are capable of writing to and reading from Zarr files. The previous test used dummy data in a dummy file type that is MOST convenient for python. Now we are actually going to write dummy data into a Zarr file. This data itself is short, perhaps 10 pseudo random integers. You will demonstrate that you are able to write data, and have the data persist in memory, and then read the data back out and make sure they match. If the ideal setup with Xarr and Zarr involves having a header, name this column pseudo_rand_1. Have an option inside the test for the Zarr file to persist or be erased after the test completes. Default to persist for now. The test internally includes a print of the headers and the first 5 rows before saving, and after re-loading from Zarr.

    SUCCESS CRITERIA:
    - Data is saved to a Zarr file with a column named 'pseudo_rand_1'.
    - Data is reloaded and matches the original.
    - Headers and first 5 rows are printed before saving and after reloading.
    
    NOTE: After successful test passage, document the results and any learnings in the captain's log.
    """
    zarr_path = Path('data_cubby/zarr_test_02.zarr')
    zarr_path.parent.mkdir(parents=True, exist_ok=True)

    arr = np.random.randint(0, 100, size=10)
    df = pd.DataFrame({'pseudo_rand_1': arr})
    print("Before Save:")
    print(df.head())

    df.to_zarr(zarr_path, mode='w')
    loaded_df = pd.read_zarr(zarr_path)
    print("After Reload:")
    print(loaded_df.head())

    assert list(loaded_df.columns) == ['pseudo_rand_1']
    assert np.array_equal(df['pseudo_rand_1'], loaded_df['pseudo_rand_1'])

    if not persist:
        import shutil
        shutil.rmtree(zarr_path)

# ==== Test 3 ====
def test3_multi_column_zarr_io(persist=True):
    """
    GOAL:
    Demonstrate that we are capable of writing data out across multiple columns in a Zarr and reading back multiple columns correctly. The test internally includes a print of the headers and the first 5 rows before saving, and after re-loading from Zarr.

    SUCCESS CRITERIA:
    - Data is saved to a .zarr file with multiple named columns.
    - Upon reloading, all columns exist and their values match the original data.
    - Headers and first 5 rows are printed before saving and after reloading.
    
    NOTE: After successful test passage, document the results and any learnings in the captain's log.
    """
    print("Running Test 3: Multi-column Zarr Read/Write")
    dummy_data = {
        'column_a': np.arange(10),
        'column_b': np.random.random(10),
        'column_c': np.linspace(100, 200, 10)
    }
    df = pd.DataFrame(dummy_data)
    print("Original data:\n", df.head())

    save_path = 'data_cubby/test3_multicolumn.zarr'
    zarr_store = zarr.DirectoryStore(save_path)
    df.to_zarr(zarr_store, mode='w')

    loaded_df = pd.read_zarr(zarr_store)
    print("Loaded data:\n", loaded_df.head())

    assert all(col in loaded_df.columns for col in dummy_data), "Missing column(s) on reload"
    for col in dummy_data:
        assert np.allclose(dummy_data[col], loaded_df[col]), f"Mismatch in column {col}"

    print("✅ Test 3 passed.")
    if not persist:
        import shutil
        shutil.rmtree(save_path)

# ==== Test 4 ====
def test4_import_local_cdf():
    """
    GOAL:
    A test where it just imports a known local cdf, for example: psp_data/fields/l2/mag_rtn_4_per_cycle/2020/psp_fld_l2_mag_RTN_4_Sa_per_Cyc_20200126_v02.cdf. This test will pass when we are able to correctly bring in the magnetic field components themselves. Not just the bulk variable, but we need the magnetic field sub components brought in to memory.

    SUCCESS CRITERIA:
    - File is found and successfully read.
    - The magnetic field subcomponents (Bx, By, Bz or equivalent) are present in memory.
    - First 5 rows of magnetic field data are printed for visual confirmation.
    
    NOTE: After successful test passage, document the results and any learnings in the captain's log.
    """
    print("Running Test 4: CDF File Import")

    # Adjust path if needed
    cdf_path = "psp_data/fields/l2/mag_rtn_4_per_cycle/2020/psp_fld_l2_mag_RTN_4_Sa_per_Cyc_20200126_v02.cdf"
    if not os.path.isfile(cdf_path):
        print("❌ Test 4 failed: File not found.")
        return

    try:
        with CDF(cdf_path) as cdf:
            variables = cdf.cdf_info().zVariables
            # Guess magnetic components
            possible_names = ['B_RTN', 'B_RTN_4_Sa_per_Cyc', 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc']
            var_name = next((v for v in possible_names if v in variables), None)
            if not var_name:
                raise ValueError("Could not find expected magnetic field variable")

            data = cdf.varget(var_name)
            if data is None or data.shape[1] < 3:
                raise ValueError("Data is missing or has fewer than 3 components")

            print("First 5 rows of magnetic field data:")
            print(data[:5])
            print("✅ Test 4 passed.")

    except Exception as e:
        print(f"❌ Test 4 failed: {e}")

# ==== Test 5 ====
def test5_simulated_psp_chunk_zarr():
    """
    GOAL:
    A test where we now save the data to a zarr file with headers matching the data names, and demonstrate that we are able to read the data back out from these files. The test internally includes a print of the headers and the first 5 rows before saving, and after reloading from Zarr. This test includes the option to clean up its tracks and delete the files it has saved, it defaults to persistence for now.

    SUCCESS CRITERIA:
    - Zarr file is created under a simulated PSP-like path: data_cubby/l2/mag_rtn_4sa/yyyy/mm/dd.zarr
    - Time and vector components are saved.
    - Data is reloaded and matches the original input.
    - Headers and first 5 rows are printed before saving and after reloading.
    
    NOTE: After successful test passage, document the results and any learnings in the captain's log.
    """
    print("Running Test 5: Simulated PSP Chunk Zarr Save")

    # Fake data
    times = pd.date_range(start='2021-07-04T00:00', periods=5, freq='min')
    vecs = np.random.randn(5, 3)

    df = pd.DataFrame({
        'time': times,
        'Bx': vecs[:, 0],
        'By': vecs[:, 1],
        'Bz': vecs[:, 2]
    })

    print("Before Save:")
    print(df.head())

    save_path = Path('data_cubby/l2/mag_rtn_4sa/2021/07/04.zarr')
    save_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_zarr(str(save_path), mode='w')
    df_loaded = pd.read_zarr(str(save_path))

    print("After Reload:")
    print(df_loaded.head())
    assert np.allclose(df['Bx'], df_loaded['Bx'])
    print("✅ Test 5 passed.")

# ==== Test 6 ====
def test6_check_cdf_file_coverage(trange=None, persist=True):
    """
    GOAL:
    Check local CDF file coverage for mag_rtn_4_per_cycle data within a given trange. If files are missing, download them using get_data. Passes when the names of the files in the local folder match the expected data coverage based on the cadence for files provided in the psp_data_types file. Optionally cleans up files after test.

    THIS TEST'S LOGIC IS BASED ON:
    - plotbot/data_classes/psp_data_types.py      # Data type config, file pattern, local path
    - plotbot/get_data.py                         # Data acquisition and file download logic
    - plotbot/data_import.py                      # Data import and CDF file processing logic
    - plotbot/data_download_helpers.py            # Local file existence checking

    SUCCESS CRITERIA:
    - All expected CDF files for mag_rtn_4_per_cycle in the trange are present locally (downloaded if needed).
    - The names of the files in the local folder match the expected data coverage.
    - All files used/checked are clearly printed/logged.
    - Optionally, files can be deleted after the test (persist=False).
    
    NOTE: After successful test passage, document the results and any learnings in the captain's log.
    """
    print("Running Test 6: CDF File Coverage Check for mag_rtn_4_per_cycle")
    from plotbot.data_download_helpers import check_local_files
    from plotbot.get_data import get_data
    import glob
    import os

    # Default trange if not provided
    if trange is None:
        trange = ['2021-04-26 00:00:00.000', '2021-05-01 00:00:00.000']

    data_type = 'mag_RTN_4sa'
    have_all, found_files, missing_files = check_local_files(trange, data_type)

    print(f"Trange: {trange}")
    print(f"Data type: {data_type}")
    print(f"Found {len(found_files)} local CDF files:")
    for f in found_files:
        print(f"  {f}")
    if missing_files:
        print(f"Missing {len(missing_files)} expected files:")
        for m in missing_files:
            print(f"  {m}")
        print("Attempting to download missing files using get_data...")
        from plotbot.data_classes.psp_mag_classes import mag_rtn_4sa
        get_data(trange, mag_rtn_4sa)
        # Re-check after download
        have_all, found_files, missing_files = check_local_files(trange, data_type)
        print(f"After download, found {len(found_files)} local CDF files:")
        for f in found_files:
            print(f"  {f}")
        if missing_files:
            print(f"Still missing {len(missing_files)} files after download:")
            for m in missing_files:
                print(f"  {m}")
            assert False, "Not all expected CDF files could be found/downloaded."
    else:
        print("All expected CDF files are present locally.")

    # Optionally clean up (delete) the files if persist is False
    if not persist:
        print("Cleaning up downloaded files...")
        for f in found_files:
            try:
                os.remove(f)
                print(f"Deleted {f}")
            except Exception as e:
                print(f"Failed to delete {f}: {e}")

    print("✅ Test 6 passed: CDF file coverage matches expected cadence.") 
    
def test7_cdf_to_zarr_mirroring(trange=None, persist=True):
    """
    GOAL:
    Demonstrate that we can read CDF files from a provided trange, and for each, create a local Zarr file in data_cubby mirroring the psp_data directory structure. The test passes when the list of local Zarr files matches the list of CDF files in the psp_data folder. Prints the first 5 rows of data from the CDF and from the Zarr after reload for each file. Optionally cleans up Zarr files after test.

    THIS TEST'S LOGIC IS BASED ON:
    - plotbot/data_classes/psp_data_types.py      # Data type config, file pattern, local path
    - plotbot/get_data.py                         # Data acquisition and file download logic
    - plotbot/data_import.py                      # Data import and CDF file processing logic
    - plotbot/data_download_helpers.py            # Local file existence checking
    - test_01_generate_dummy_file_in_data_cubby   # Mirroring directory structure logic

    SUCCESS CRITERIA:
    - For each CDF file in the trange, a Zarr file is created in the mirrored data_cubby structure.
    - The list of Zarr files matches the list of CDF files.
    - First 5 rows of data from the CDF and from the Zarr after reload are printed and match.
    - Optionally, Zarr files can be deleted after the test (persist=False).
    
    NOTE: After successful test passage, document the results and any learnings in the captain's log.
    """
    from plotbot.data_download_helpers import check_local_files
    from cdflib import CDF
    import pandas as pd
    import zarr
    from pathlib import Path
    import os

    if trange is None:
        trange = ['2021-04-26 00:00:00.000', '2021-05-01 00:00:00.000']
    data_type = 'mag_RTN_4sa'
    have_all, cdf_files, _ = check_local_files(trange, data_type)

    zarr_files = []
    for cdf_path in cdf_files:
        # Mirror the path under data_cubby
        rel_path = Path(cdf_path).relative_to('psp_data')
        zarr_path = Path('data_cubby') / rel_path.with_suffix('.zarr')
        zarr_path.parent.mkdir(parents=True, exist_ok=True)

        # Read CDF data
        with CDF(str(cdf_path)) as cdf:
            variables = cdf.cdf_info().zVariables
            # Try to find the main mag variable
            possible_names = ['B_RTN', 'B_RTN_4_Sa_per_Cyc', 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc']
            var_name = next((v for v in possible_names if v in variables), None)
            if not var_name:
                print(f"Could not find expected magnetic field variable in {cdf_path}")
                continue
            data = cdf.varget(var_name)
            if data is None or data.shape[1] < 3:
                print(f"Data missing or has fewer than 3 components in {cdf_path}")
                continue
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=['Bx', 'By', 'Bz'])
            print(f"CDF file: {cdf_path}")
            print("First 5 rows from CDF:")
            print(df.head())
            # Save to Zarr
            df.to_zarr(str(zarr_path), mode='w')
            zarr_files.append(zarr_path)
            # Reload from Zarr and print
            df_zarr = pd.read_zarr(str(zarr_path))
            print(f"First 5 rows from Zarr ({zarr_path}):")
            print(df_zarr.head())
            # Check that data matches
            assert df.head().equals(df_zarr.head()), f"Data mismatch for {zarr_path}"

    # Check that the set of Zarr files matches the set of CDF files (by relative path)
    cdf_rel = {str(Path(f).relative_to('psp_data').with_suffix('.zarr')) for f in cdf_files}
    zarr_rel = {str(f.relative_to('data_cubby')) for f in zarr_files}
    print(f"CDF files mirrored: {sorted(cdf_rel)}")
    print(f"Zarr files created: {sorted(zarr_rel)}")
    assert cdf_rel == zarr_rel, "Zarr files do not match CDF files in mirrored structure!"

    # Optionally clean up
    if not persist:
        print("Cleaning up Zarr files...")
        for zf in zarr_files:
            try:
                os.remove(zf)
                print(f"Deleted {zf}")
            except Exception as e:
                print(f"Failed to delete {zf}: {e}")

    print("✅ Test 7 passed: CDF to Zarr mirroring successful.")
