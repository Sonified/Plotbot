# Plotbot Integration with pyspedas/CDAWeb

## 1. Goal

Refactor Plotbot's data acquisition pipeline to utilize `pyspedas` for accessing NASA's CDAWeb data archive as the primary data source. The existing Berkeley server access will be maintained as a fallback, primarily for accessing the most recent data not yet available on CDAWeb or potentially for private data access modes.

## 2. Motivation

*   **Standardization:** Leverage `pyspedas`, a widely used library in the heliophysics community, for data loading.
*   **Efficiency:** Potentially simplify data acquisition, as `pyspedas` may handle fetching and loading data for a specific time range directly, possibly eliminating the need for manual file stitching required with the current Berkeley approach.
*   **Accessibility:** Easily access the extensive public Parker Solar Probe data archive available through CDAWeb.
*   **Maintainability:** Aligning with standard tools may improve long-term maintainability.

## 3. Core Challenges & Design Considerations

### 3.1. Server Selection Strategy

**(Updated based on discussion)** How will Plotbot decide whether to query CDAWeb (via `pyspedas`) or the Berkeley server for a given time range (`trange`)?

We will implement a `Data_server` option to control this behavior. This could be managed via a global configuration setting (e.g., `plotbot.config.data_server`) or passed as a parameter. The options are:

*   **`'spdf'`**:
    *   Always attempt to download data using `pyspedas` from the SPDF/CDAWeb server first.
    *   If `pyspedas` reports that data is not available for the requested `trange` (requires specific error/status checking), the process stops for that data type. No fallback to Berkeley occurs.
*   **`'berkeley'`**:
    *   Exclusively use the existing data download and processing logic that targets the Berkeley server.
    *   `pyspedas` is not used in this mode.
*   **`'dynamic' (Proposed Default):**
    *   First, attempt to download data using `pyspedas` from SPDF/CDAWeb.
    *   If `pyspedas` successfully downloads data covering the `trange`, use that data.
    *   If `pyspedas` reports that data is not available for the *entire* requested `trange` (or fails with a relevant error):
        *   Fall back to the existing Berkeley server download logic.
        *   This will include prompting for credentials if accessing potentially non-public time ranges, as per current behavior.

*Implementation Note:* A global setting like `plotbot.config.data_server = 'spdf'` seems like a reasonable starting point for managing this option, prioritizing the public CDAWeb archive by default. This would likely involve creating a new `plotbot/config.py` module to store such settings.

### 3.2. `pyspedas` Integration Details

*   **Invocation:** Where will `pyspedas` load functions (e.g., `pyspedas.psp.fields(...)`, `pyspedas.psp.spi(...)`) be called? Likely within `get_data.py` or a new dedicated module (e.g., `pyspedas_downloader.py`) called by `get_data.py`.
*   **Usage Mode:** Based on Jaye's note, `pyspedas` will be used *strictly* for downloading files. Calls will include `notplot=True` and `downloadonly=True`. Plotbot's existing `data_import.py` logic will handle reading the downloaded CDFs.
*   **Data Loading Mechanism:** `pyspedas` downloads CDF files locally for the specified `trange`. The exact location and structure of these downloads need to be confirmed during implementation (Step 4.1) to ensure they align with Plotbot's expected `psp_data/` structure and can be found by `data_import.py`.
*   **Error Handling:** How will failures in `pyspedas` downloading (e.g., data not found, network issues) be handled? Should it automatically trigger a fallback to Berkeley when in `'dynamic'` mode?

### 3.3. Data Adaptation Layer (Simplified)

Since `pyspedas` will only be used for downloading (`notplot=True`, `downloadonly=True`), a complex adaptation layer to convert `pytplot` variables is **not required**. 
The primary challenge shifts to ensuring that `plotbot/data_import.py` (which uses `cdflib`) can correctly locate and parse the variable names within the CDF files downloaded by `pyspedas`. This involves:
*   **Variable Name Consistency:** Confirming that the variable names within the CDF files downloaded from CDAWeb (via `pyspedas`) match the names expected by Plotbot (currently defined in the `data_vars` list within `psp_data_types.py`). Adjustments to `data_vars` might be needed if names differ.
*   **File Location:** Ensuring `data_import.py` and `check_local_files` can find the files in the location where `pyspedas` downloads them.

### 3.4. Unified Local Storage & File Management

*   **Requirement:** If `pyspedas` *does* download files, they must be stored within the existing `psp_data/` directory structure, consistent with the Berkeley downloads.
*   **Potential Conflicts:** Need a strategy for handling cases where both Berkeley and `pyspedas` might provide files for overlapping times (e.g., different version numbers like `_v02.cdf` vs. `_v04.cdf`). The file searching logic (`check_local_files`, potentially modified `case_insensitive_file_search`) must robustly handle:
    *   Update file searching logic (e.g., in `plotbot/data_download_helpers.py`'s `check_local_files` or similar) to be case-insensitive.
    *   Implement logic to select the "best" file if multiple versions exist (e.g., prefer highest version number from *either* source for a given date/time block).

### 3.5. Conditional File Stitching

*   The current logic in `data_import.py` (specifically `import_data_function` and its helpers) assumes multiple daily/sub-daily files might need to be found, loaded, and concatenated ("stitched") to cover the requested `trange`.
*   **Investigation needed:** Does `pyspedas` (with `downloadonly=True`) download a single file covering the `trange`, or multiple files similar to the Berkeley structure? 
*   If `pyspedas` downloads multiple files, the existing stitching logic in `data_import.py` will still be necessary and should work correctly, provided the file finding logic is updated.
*   If `pyspedas` downloads a single aggregated file, the stitching logic would naturally be skipped when only that file is found for the `trange`.

## 4. Proposed Refactoring Steps (Revised: Minimal, Audit-First Approach)

0.  **Step 0: Update Environment & Installer:**
    *   **Priority:** Must be done before coding/testing the download logic.
    *   Add `pyspedas` to the `environment.yml` file.
    *   Update the installation scripts (`Install_Scripts/`) if necessary to ensure the environment is created correctly with `pyspedas` included.

1.  **Step 1: Audit `pyspedas` Download & Variable Names:**
    *   **Priority:** This step is crucial before major code changes.
    *   Determine the exact `pyspedas` function calls and arguments needed for download-only (e.g., `pyspedas.psp.fields` with `datatype`, `trange`, `notplot=True`, `downloadonly=True`).
    *   Confirm the default local download path and filename conventions used by `pyspedas` for PSP data.
    *   **CRITICAL:** Download sample CDF files for key data types (MAG, SPI, SPE) using the intended `pyspedas` download-only commands.
    *   Inspect the variable names *inside* these downloaded CDFs (using `cdflib` or similar tools).
    *   Compare these variable names against the corresponding `data_vars` lists currently defined in `plotbot/data_classes/psp_data_types.py` for Berkeley files.
    *   Note any discrepancies.
    *   Confirm `pyspedas` download behavior for multi-day/multi-block time ranges (single vs. multiple files).

2.  **Step 2: Implement `_trigger_spdf_download` Function:**
    *   Based on findings from Step 1, create this new function (likely in a new file, e.g., `plotbot/spdf_download.py`).
    *   Input: `trange`, Plotbot `data_type` key (e.g., `'mag_RTN_4sa'`).
    *   Internal Logic:
        *   Map the Plotbot `data_type` key to the required `pyspedas` `datatype` string (this mapping can be internal to this function initially, e.g., a simple dictionary).
        *   Call the appropriate `pyspedas` function with `downloadonly=True`, `notplot=True`, and potentially configure the download path if needed to align with Plotbot's structure.
        *   **Optimization for Offline Use:** Use the `no_update` parameter pattern to ensure reliable checking for local files when potentially offline. The `no_update=True` check MUST be performed first. If it returns the file path, the process can stop (file found locally). Only if `no_update=True` fails to return the file should `no_update=False` be attempted (which triggers the download if online). This is crucial because the standard check (omitting `no_update` or using only `no_update=False`) fails when offline, as it attempts network access even with `downloadonly=True`.
            
            Here's a more detailed example illustrating how the result might be captured and used:
            ```python
            # Example logic structure (ensure downloadonly=True, notplot=True etc. are included)
            file_path = None
            try:
                for no_update_flag in [True, False]: # Check local first, then attempt download
                    print(f"Attempting pyspedas call with no_update={no_update_flag}...")
                    returned_data = pyspedas_func(..., no_update=no_update_flag, ...)
                    if returned_data: # Check if list is not empty and contains path
                        file_path = returned_data[0]
                        print(f"File path found/obtained with no_update={no_update_flag}.")
                        break # Exit loop once file is found/downloaded
                if not file_path:
                     print("File not found locally or via download attempt.")
            except Exception as e:
                print(f"Error during pyspedas check/download: {e}")
                # Handle error appropriately

            # Proceed using file_path if found
            ```

            The original concise structure focusing on the loop itself was:
            ```python
            try:
                for no_update in [True, False]:  # First try local, then try download
                    # Assign returned value if needed, e.g.:
                    # returned_data = pyspedas.psp.fields(
                    pyspedas.psp.fields(
                        trange=trange,
                        datatype='mag_rtn_4_sa_per_cyc', # Example datatype
                        level='l2',
                        time_clip=True,
                        get_support_data=True,
                        downloadonly=True, # Crucial
                        notplot=True,      # Crucial
                        no_update=no_update
                    )
                    # Add logic here to check the returned value and potentially break
            except Exception as e:
                pass # Add appropriate error handling / loop breaking logic
            ```
        *   Handle `pyspedas` errors (e.g., data not found, download failure).
    *   Output: Return a status indicating success or failure of the download attempt.

3.  **Step 3: Modify `get_data` Dispatch Logic:**
    *   Keep `get_data` as the main entry point.
    *   Inside `get_data`, locate the section where downloads are triggered if `check_local_files` indicates missing files.
    *   Add conditional logic based on `plotbot.config.data_server`:
        *   If mode is `'spdf'`: Call `_trigger_spdf_download`. If it fails, do not proceed to Berkeley.
        *   If mode is `'berkeley'`: Call `download_new_psp_data` (existing Berkeley function).
        *   If mode is `'dynamic'`: Call `_trigger_spdf_download`. If it returns a failure status indicating data not found, *then* call `download_new_psp_data`.
    *   The subsequent call to `import_data_function` (which loads data from local files) remains in place and should execute after the conditional download attempts.

4.  **Step 4: Adjust File Finding Logic (If Necessary):**
    *   Based on the download location confirmed in Step 1, ensure `check_local_files` (in `data_download_helpers.py`) and `import_data_function` (in `data_import.py`) are looking in the correct local directories to find files downloaded by either Berkeley or SPDF/`pyspedas`.
    *   Ensure the logic handling multiple versions or case-insensitivity works for both potential sources.

5.  **Step 5: Testing:**
    *   Implement initial tests within a new file: `tests/test_spdf_download.py`.
    *   Test functionality with `data_server` set to `'spdf'`, `'berkeley'`, and `'dynamic'`.
    *   Test with time ranges that should succeed and fail on SPDF.
    *   Test with time ranges requiring Berkeley access (recent data).

6.  **Step 6: Contingency - Address Variable Name Discrepancies (IF NEEDED):**
    *   **Only if Step 1 reveals significant differences** in variable names between SPDF and Berkeley CDFs:
        *   Modify `plotbot/data_classes/psp_data_types.py`: Formally add the `pyspedas_datatype` key and potentially add separate `spdf_data_vars` lists or a mapping structure if names differ significantly.
        *   Modify `import_data_function`: Add logic to detect the likely source of a CDF file (e.g., based on filename convention or path) and use the appropriate list of variable names (`data_vars` vs. `spdf_data_vars`) when extracting data with `cdflib`.

## 5. Key Modules to Modify (Initial Minimal Plan)

*   `plotbot/get_data.py` (Core logic, server selection, dispatcher)
*   Potentially a new module: `plotbot/spdf_download.py` (SPDF download logic)
*   `plotbot/config.py` (New file for server setting)
*   `plotbot/data_download.py` (Existing Berkeley download logic)
*   `plotbot/data_download_helpers.py` (File finding adjustments)
*   `plotbot/data_import.py` (Minor adjustments for file finding, *major changes only if variable names differ*)
*   `plotbot/data_classes/psp_data_types.py` (*Changes only if variable names differ*)
*   `tests/` (Add new test cases)

## 6. Example `pyspedas` Calls

*(Robert to add specific, ideal pyspedas call examples here for different instruments/data products)*


## 7. CDAWeb File Naming Conventions (from pyspedas logs)

Pyspedas name conventions, we need to make sure these align with Berkely files:
16-Oct-24 09:24:28: Downloading remote index: https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/mag_rtn_4_per_cycle/2023/
16-Oct-24 09:24:29: File is current: psp_data/fields/l2/mag_rtn_4_per_cycle/2023/psp_fld_l2_mag_rtn_4_sa_per_cyc_20230928_v02.cdf
16-Oct-24 09:24:29: Downloading remote index: https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/mag_sc_4_per_cycle/2023/
16-Oct-24 09:24:30: File is current: psp_data/fields/l2/mag_sc_4_per_cycle/2023/psp_fld_l2_mag_sc_4_sa_per_cyc_20230928_v02.cdf
16-Oct-24 09:24:30: Downloading remote index: https://spdf.gsfc.nasa.gov/pub/data/psp/sweap/spi/l3/spi_sf00_l3_mom/2023/
16-Oct-24 09:24:31: File is current: psp_data/sweap/spi/l3/spi_sf00_l3_mom/2023/psp_swp_spi_sf00_l3_mom_20230928_v04.cdf
16-Oct-24 09:24:31: Downloading remote index: https://spdf.gsfc.nasa.gov/pub/data/psp/sweap/spe/l3/spe_sf0_pad/2023/
16-Oct-24 09:24:32: File is current: psp_data/sweap/spe/l3/spe_sf0_pad/2023/psp_swp_spe_sf0_l3_pad_20230928_v04.cdf



Example data download calls:
#In RTN coordinates
#specify time range in the form ['yyyy-mm-dd/hh:mm:ss','yyyy-mm-dd/hh:mm:ss']
# trange = ['2023-09-28/06:32:00.000', '2023-09-28/06:45:00.000']
trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']

#note that full resolution would be 'mag_rtn', but only download for short time periods, as it makes plotting very slow
mag_rtn_4sa_datatype = 'mag_rtn_4_sa_per_cyc' #mag
# mag_datatype = 'mag_rtn'

#later we will add the ability to dynamically change to high-resolution magnetometer data
mag_rtn_4sa_vars = pyspedas.psp.fields(trange=trange, datatype=mag_rtn_4sa_datatype, level='l2', time_clip=True,get_support_data=True)

#note that full resolution would be 'mag_sc', but only download for short time periods, as it makes plotting very slow
mag_sc_4sa_datatype = 'mag_sc_4_sa_per_cyc' #mag

#later we will add the ability to dynamically change to high-resolution magnetometer data
mag_sc_4sa_vars = pyspedas.psp.fields(trange=trange, datatype=mag_sc_4sa_datatype, level='l2', time_clip=True,get_support_data=True)

#specify span-i data type to plot
spi_datatype='spi_sf00_l3_mom' #protons sf means survey cadence, l3 means level 3, mom means moment, 00 means protons
spi_vars = pyspedas.psp.spi(trange=trange, datatype=spi_datatype, level='l3', time_clip=True)

#loading electron data
spe_datatype = 'spe_sf0_pad' #electrons
spe_vars = pyspedas.psp.spe(trange=trange, datatype=spe_datatype, level='l3', time_clip=True,get_support_data=True)

#loading high resolution electron data
# Specify the path to your high-resolution electron CDF file
electrons_cdf_file_path = '/Users/robertalexander/Dropbox/__Collaborations/_NASA/__MH_Investigation/Downloaded_PSP_Data/High_Resolution_Electrons/psp_swp_spe_af0_L3_pad_20230928_v04.cdf'

# Load the high-resolution electron CDF file
electrons_cdf_file = cdflib.CDF(electrons_cdf_file_path)

## 8. Test Results & Key Learnings (From `tests/test_pyspedas_download.py`)

Initial testing using `downloadonly=True` provided several critical insights:

*   **Return Value is Key:** The `pyspedas` data loading functions (`fields`, `spi`, `spe`) successfully return a list containing the *relative path* to the file(s) they downloaded or found locally, even when `downloadonly=True` is used. This is crucial because it bypasses the need for potentially unreliable `glob` searches immediately after the function call, especially given the long download times observed for some data types.
    *   Example Return: `['psp_data/fields/l2/mag_rtn_4_per_cycle/2023/psp_fld_l2_mag_rtn_4_sa_per_cyc_20230928_v02.cdf']`
*   **Directory Structure Matches:** The directory structure where `pyspedas` saves downloaded files (relative to the `psp_data` root) perfectly matches the structure defined in `plotbot/data_classes/psp_data_types.py` based on the Berkeley server layout.
    *   Verification involved comparing the absolute path derived from the `pyspedas` return value against the expected absolute path constructed using the config and `WORKSPACE_ROOT`.
*   **Base Filename Matches (Case-Insensitive):** The core components of the filename (instrument, level, data product, date) match the expected patterns *when compared case-insensitively*. The version number (`_vXX`) is correctly handled.
*   **Case Mismatch Identified:** There is a consistent case difference between the filenames returned by `pyspedas` and the patterns expected from the Berkeley config (`psp_data_types.py`):
    *   `pyspedas` returns paths with lowercase components (e.g., `l2`, `l3`, `rtn`, `sc`, `sa`, `cyc`).
    *   Berkeley patterns use mixed case (e.g., `L2`, `L3`, `RTN`, `SC`, `Sa`, `Cyc`).
*   **Plotbot File Search is Case-Insensitive:** A check of `data_download_helpers.py` (`case_insensitive_file_search`) and `data_import.py` confirmed that Plotbot's existing logic for finding local files already performs case-insensitive comparisons. Therefore, the case mismatch in filenames should *not* prevent Plotbot from finding/loading files downloaded by `pyspedas`.
*   **Long Download Times Confirmed:** Manual testing and test failures confirmed that some data types (e.g., `mag_rtn`) involve downloading large multi-GB files, taking several minutes. `time_clip=True` does *not* appear to prevent the download of the entire file block.
*   **`no_update` Loop Performance:** The performance test showed that using the `no_update=[True, False]` loop is slightly *slower* than letting `pyspedas` perform its default check when the file is already local. The default check is efficient.

**Implications for Integration:**

1.  The core data acquisition logic (in `get_data.py` or a new `spdf_download.py`) should rely on the **return value** of the `pyspedas` function (when using `downloadonly=True`) to get the path to the needed file, rather than using `glob`.
2.  The comparison logic for paths needs to handle the **relative path** returned by `pyspedas` and convert it to absolute if needed for internal consistency.
3.  While the case mismatch in filenames is noted, no immediate code change is needed in the file *searching* logic due to its existing case-insensitivity.
4.  The `no_update` loop strategy **is the required method** for reliably checking for local files when potentially offline. The standard `pyspedas` check (even with `downloadonly=True`) fails offline as it still attempts network access. While the initial `no_update=True` check is slightly slower than the standard check *when online and the file exists*, its offline reliability is essential for Plotbot's intended use cases.
