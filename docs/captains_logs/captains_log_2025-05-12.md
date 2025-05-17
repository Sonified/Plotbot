# Captain's Log: 2025-05-12

## Bug Fix: Magnetic Hole Finder Data Slicing with Caching

- **Issue:** When running the `Magnetic_Hole_Finder.ipynb` notebook repeatedly, the `detect_magnetic_holes_and_generate_outputs` function (via `download_and_prepare_high_res_mag_data`) appeared to process the *entire* cached time range from the `global_plotbot_mag_rtn` instance, rather than just the small `trange` specified in the notebook cell (e.g., `['2023-03-17 21:10:15', '2023-03-17 21:10:20']`).
- **Root Cause:** The `download_and_prepare_high_res_mag_data` function in `magnetic_hole_finder/data_management.py` correctly utilized the cached `global_plotbot_mag_rtn` instance (as intended) when the requested `trange` was covered by the cached data. However, it failed to *slice* the data arrays (times, Br, Bt, Bn, Bmag) obtained from the global instance down to the *specific* requested `trange` before returning them. It returned the full arrays from the cache.
- **Fix Implemented:** Added explicit data clipping within `download_and_prepare_high_res_mag_data`. After retrieving data (either freshly downloaded or from the cached `global_plotbot_mag_rtn`), the code now uses a helper function (`clip_to_original_time_range`) to filter `datetime_array`, `br`, `bt`, `bn`, and `bmag` to include only data points strictly within the `extended_trange` (which is the `trange` passed into the function, including padding).
- **Outcome:** The function now correctly returns only the data relevant to the requested time interval, even when using cached data. This ensures the magnetic hole detection operates on the intended, smaller time slice, matching the behavior when data is freshly downloaded. The caching mechanism remains functional, speeding up subsequent runs over the same or overlapping intervals, but the data provided to the analysis step is correctly bounded.

*(Log remains open for further updates on 2025-05-12)*

## Push: v2.28

- **Version Tag:** `2025_05_12_v2.28`
- **Commit Message:** `Fix: Correctly slice cached data in magnetic hole finder (v2.28)`
- **Branch:** `data_cubby_refactor` (Assuming this is the current branch)
- **Summary:** Pushed fix for magnetic hole finder issue where cached data wasn't being sliced correctly to the requested `trange`. The code now returns only the relevant time slice, whether data is cached or freshly downloaded.

## Push: v2.29

- **Version Tag:** `2025_05_12_v2.29`
- **Commit Message:** `Add SUN_DIST to spi_sf00_l3_mom data_vars (v2.29)`
- **Summary:** Added `SUN_DIST` to the `data_vars` list for the `spi_sf00_l3_mom` data type in `plotbot/data_classes/psp_data_types.py`.

## Push: v2.30

- **Version Tag:** `2025_05_12_v2.30`
- **Commit Message:** `Standardize plotbot.ipynb (v2.30)`
- **Summary:** Pushed updates to `plotbot.ipynb` for standardization.

*(Log remains open for further updates on 2025-05-12)*

## Future Work / Next Steps

- **Multiplot Bug:** Multiplot is currently broken when using 'ham' data with `plt.options.x_axis_carrington_lon = True`. The x-axis incorrectly displays time instead of Carrington longitude, and the visuals are not plotted correctly. This needs to be investigated and fixed.
- **Normalized Br Variable:** Add a new variable for normalized Br. This requires `psp_mag_classes.py` to fetch `SUN_DIST` data from the proton data type (`spi_sf00_l3_mom`), apply linear interpolation to match the magnetic field timestamps, and then calculate the normalized value using the formula: `Br_norm = Br * (Rsun^2)`. 