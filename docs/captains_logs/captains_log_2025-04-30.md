# Captain's Log - April 30, 2025

## Activities & Learnings 

-   **Proton FITS Naming Convention & Type Hints:** Aligned naming conventions for several `proton_fits_class` attributes where the attribute name included a `_pfits` suffix (e.g., `vdrift_va_pfits`, `valfven_pfits`, `vsw_mach_pfits`, `beta_ppar_pfits`, `beta_pperp_pfits`) while the internal `var_name` did not. Updated the `psp_proton_fits_classes.pyi` stub file to match the actual attribute names used in `psp_proton_fits_classes.py`. This ensures correct type hinting for these attributes. Also adjusted the attribute name for absolute heat flux to `abs_qz_p` in both the `.py` and `.pyi` files for consistency and user preference. 

-   **Multiplot Global Y-Limit Fix & Testing:** Refactored `MultiplotOptions` in `multiplot_options.py` and `multiplot_options.pyi` to correctly handle setting a global y-limit using `plt.options.set_global_y_limit()`. The previous implementation failed because it only applied limits to axes existing at the time of the call, not axes created dynamically during the `multiplot` run. The fix involves storing the global limit and applying it within `_get_axis_options` when a new `AxisOptions` instance is created. Ran all tests in `test_multiplot.py` and `test_stardust.py` successfully, confirming the fix didn't introduce regressions.

-   **Longitude X-Axis Preparation & Test Cleanup:** Made several preparatory changes to support plotting against Carrington Longitude in `multiplot`. This included:
    -   Adding the Parker Solar Probe Carrington Longitude data file (`Parker-CARR-LON.npz`) to `support_data/trajectories/`.
    -   Updating `utils.py` (details pending, but modifications made as part of this effort).
    -   Creating `pytest.ini` to filter specific Matplotlib `UserWarnings` during tests, improving output clarity for future testing including this feature.

### Git Push ###
Version: 2025-04-30_v1.14
Commit Message: feat: Align proton fits naming & type hints (2025-04-30_v1.14)

### Git Push ###
Version: 2025-04-30_v1.15
Commit Message: fix: Correct multiplot global y-limit logic (2025-04-30_v1.15)

### Git Push ###
Version: 2025-04-30_v1.16
Commit Message: chore: Prepare for longitude x-axis (add data, utils, filter warnings) (2025-04-30_v1.16)

## Refactoring Plan: FITS CDF Data & Targeted CWYN (May 1, 2025)

**Goal:** Update `proton_fits_class` and `alpha_fits_class` to use the new CDF-based data source for `sf00_fits` and `sf01_fits`. Implement a targeted "Calculate What You Need" (CWYN) approach using `@property` for variables in `proton_fits_class` that have external dependencies (`vsw_mach`, `vdrift_va_p2-p1_apfits`, `|vdrift|_va_p2-p1_apfits`), while preserving the existing structure for other variables.

**Steps:**

1.  **Update Data Types:** (DONE) Modified `psp_data_types.py` to point `sf00_fits` and `sf01_fits` to the new CDF URLs, local paths, file patterns, and data variables.

2.  **Refactor `proton_fits_class` (Targeted CWYN):**
    *   Keep `calculate_variables` for eager calculations using only internal `spi_sf00_fits` data.
    *   Ensure `__init__` defines keys in `self.raw_data` for *all* variables present in the `spi_sf00_fits` CDF (including unknowns like `*_v`, `epad_strahl_centroid`, etc.) so they are extracted if present.
    *   Add a `_cwyn_cache` dictionary.
    *   Implement `@property` methods for:
        *   `vsw_mach`: Fetches `spi_sf00_l3_mom` via `data_cubby` on demand, performs alignment and calculation. Caches result.
        *   **Alignment Strategy:** Linear interpolation (`scipy.interpolate.interp1d`) will be used to align the solar wind speed data from `spi_sf00_l3_mom` onto the `proton_fits_class` time base (`self.time`). Based on the robust structure of `showdahodo.downsample_time_based`, this will include NaN handling and conversion to numeric time (`mdates.date2num`). Crucially, it will use `bounds_error=False` and `fill_value=np.nan` to prevent extrapolation outside the valid moments data range.
        *   `vdrift_va_p2-p1_apfits`: Fetches `na` (alpha density) from `alpha_fits` via `data_cubby` on demand, calculates `valfven_apfits` (needs `na` and `n_tot`), then calculates the normalized drift. Caches result.
        *   **Alignment Note:** Per scientist confirmation, `spi_sf00_fits` (proton) and `spi_sf01_fits` (alpha) data are pre-aligned. Therefore, **no interpolation of `na` is required** before calculation.
        *   `|vdrift|_va_p2-p1_apfits`: Similar to above, but takes the absolute value. Caches result.
    *   **Encapsulation:** The interpolation logic will be placed in a private helper method within the class (e.g., `_interpolate_to_self_time`) for clarity and potential reuse.
    *   **Dependency Handling:** `@property` methods will log a warning/error and return `None`/`NaN`s if dependencies (`spi_sf00_l3_mom`, `alpha_fits`) cannot be retrieved.
    *   Minimally adapt `set_ploptions` to handle these specific CWYN variables (likely just needs to ensure they are included in the loop that creates `plot_manager` instances).
    *   Specifically, ensure `set_ploptions` creates attributes using the desired **PlotBot Names** (e.g., `self.vsw_mach_pfits`, `self.vdrift_va_p2p1_apfits`) and connects them to the appropriate data source (either `self.raw_data` entries or the new `@property` methods).
    *   **Mixed Variable Plot Definitions:** Add new `plot_manager` instances for `vdrift_va_p2p1_apfits` and `abs_vdrift_va_p2p1_apfits`. Since no plot definitions for these *specific calculated variables* (using `Va` incorporating alpha density) were found in the provided `zip_fits_vars.py` snippet, we will **adapt the plot style** from the most conceptually similar variable, `vdrift_va_pfits` (which used `Va` with only proton density). This involves using its color, marker, etc., as a placeholder.
    *   **Action Item:** Note added to "Questions for Scientist" to confirm the desired `ploptions` (styles/labels) for `vdrift_va_p2p1_apfits` and `abs_vdrift_va_p2p1_apfits` with Jaye.
    *   **Example `plot_manager` Definitions (Adapting Style) for `set_ploptions`:**

      ```python
      # 35. vdrift_va_p2p1_apfits (Normalized drift using Va including alphas)
      self.vdrift_va_p2p1_apfits = plot_manager(
          data_source=lambda: self.vdrift_va_p2p1_apfits, # Link to @property
          plot_options=ploptions(
              var_name='vdrift_va_p2p1_apfits', # Internal property name
              data_type='proton_fits',
              class_name='proton_fits',
              subclass_name='vdrift_va_p2p1_apfits', # PlotBot attribute name
              plot_type='scatter',
              y_label=r'$V_{drift}/V_A$',
              legend_label=r'$Vd_{p2-p1}/V_{A,ap}$$', # Adapted label
              color='navy',                  # Adapted style
              y_scale='linear',
              marker_style='*',              # Adapted style
              marker_size=5,                 # Adapted style
              alpha=0.7,                     # Adapted style
              y_limit=None
          )
      )

      # 36. abs_vdrift_va_p2p1_apfits (Absolute normalized drift using Va including alphas)
      self.abs_vdrift_va_p2p1_apfits = plot_manager(
          data_source=lambda: self.abs_vdrift_va_p2p1_apfits, # Link to @property
          plot_options=ploptions(
              var_name='abs_vdrift_va_p2p1_apfits', # Internal property name
              data_type='proton_fits',
              class_name='proton_fits',
              subclass_name='abs_vdrift_va_p2p1_apfits', # PlotBot attribute name
              plot_type='scatter',
              y_label=r'$|V_{drift}|/V_A$',
              legend_label=r'$|Vd_{p2-p1}|/V_{A,ap}$$', # Adapted label
              color='navy',                   # Adapted style
              y_scale='linear',
              marker_style='*',               # Adapted style
              marker_size=5,                  # Adapted style
              alpha=0.7,                      # Adapted style
              y_limit=None
          )
      )
      ```

3.  **Testing:** Adapt `test_fits_cdf_server_integration.py` and potentially other tests to verify the new behavior of both classes.

4.  **Refactor `alpha_fits_class`:** Refactor using the standard eager approach (update `calculate_variables` and `set_ploptions` based on the new `spi_sf01_fits` CDF data).
    *   Ensure `__init__` defines keys in `self.raw_data` for *all* variables present in the `spi_sf01_fits` CDF (including unknowns like `Epoch_1`, `*_v`, etc.) so they are extracted if present.
    *   Ensure `set_ploptions` assigns the correct PlotBot attribute names for alpha parameters.

## Context for Next Session

**Objective:** Implement the refactoring plan outlined above ("Refactoring Plan: FITS CDF Data & Targeted CWYN").

**Current Code State (Relevant Files):**

*   `plotbot/data_classes/psp_data_types.py`: The `sf00_fits` and `sf01_fits` data types have been successfully updated to point to the new CDF data source and list the expected variables available directly from those CDFs.
*   `plotbot/data_classes/psp_proton_fits_classes.py`: This file is currently in a state *prior* to the CWYN refactoring attempts. It includes the `calculate_variables` method which was updated to correctly extract variables from the new CDF format (using CDF names like `Epoch`, `Tpar_tot`, etc.) and performs internal calculations for derived quantities like Alfven speed, Betas, etc. (everything except `vsw_mach` which relies on external data).
*   `tests/test_fits_cdf_server_integration.py`: Contains a test (`test_compare_cdf_csv_variables`) useful for comparing CDF variables against old CSV headers. The necessary test CDF files (`spp_swp_spi_sf00_fits_2024-04-01_v00.cdf` and `spp_swp_spi_sf01_fits_2024-04-01_v00.cdf`) have been manually added to `tests/test_data/psp_cdf_fits/`.

**New CDF Variable Lists (from test run):**

*   **SF00 (`sf00_fits`) CDF Variables (45):**
    ```
    ['B_SC', 'B_inst', 'B_inst_v', 'Epoch', 'Temp_tot', 'Tpar1', 'Tpar2', 'Tpar_tot', 'Tperp1', 'Tperp1_dpar', 'Tperp2', 'Tperp2_dpar', 'Tperp_tot', 'Trat1', 'Trat1_dpar', 'Trat2', 'Trat2_dpar', 'Trat_tot', 'bhat_inst', 'bhat_inst_v', 'chi_p', 'epad_strahl_centroid', 'n_tot', 'np1', 'np1_dpar', 'np2', 'np2_dpar', 'ps_ht1', 'ps_ht2', 'qz_p', 'qz_p_par', 'qz_p_perp', 'vcm', 'vcm_mag', 'vcm_mag_v', 'vcm_v', 'vdrift', 'vdrift_dpar', 'vp1', 'vp1_dpar', 'vp1_mag', 'vp1_v', 'vp2', 'vp2_mag', 'vp2_v']
    ```
*   **SF01 (`sf01_fits`) CDF Variables (18):**
    ```
    ['B_SC_a', 'B_inst_a', 'B_inst_a_v', 'Epoch', 'Epoch_1', 'Tpara', 'Tperpa', 'Tperpa_dpar', 'Trata', 'Trata_dpar', 'chi_a', 'na', 'na_dpar', 'va', 'va_dpar', 'va_v', 'vp2_mag', 'vp2_mag_v']
    ```

**Key Task:** Proceed with **Step 2** of the refactoring plan documented above: Modify `proton_fits_class.py` to implement the targeted CWYN pattern for `vsw_mach` and the mixed alpha-dependent normalized drift variables (`vdrift_va_p2-p1_apfits`, `|vdrift|_va_p2-p1_apfits`), including adding the `_cwyn_cache`, creating the necessary `@property` methods, and minimally adapting `set_ploptions`. 

### Final Refactoring Plan (Target State):

1.  **`psp_data_types.py` (DONE):** Updated `'sf00_fits'` and `'sf01_fits'` entries to point to CDFs and list variables directly available.
2.  **`proton_fits_class.py` (NEXT):** Implement targeted CWYN.
    *   Keep `calculate_variables` for eager calculations using only internal `spi_sf00_fits` data.
    *   Ensure `__init__` defines keys in `self.raw_data` for *all* variables present in the `spi_sf00_fits` CDF (including unknowns like `*_v`, `epad_strahl_centroid`, etc.) so they are extracted if present.
    *   Add a `_cwyn_cache` dictionary.
    *   Implement `@property` methods for:
        *   `vsw_mach`: Fetches `spi_sf00_l3_mom` via `data_cubby` on demand, performs alignment and calculation. Caches result.
        *   **Alignment Strategy:** Linear interpolation (`scipy.interpolate.interp1d`) will be used to align the solar wind speed data from `spi_sf00_l3_mom` onto the `proton_fits_class` time base (`self.time`). Based on the robust structure of `showdahodo.downsample_time_based`, this will include NaN handling and conversion to numeric time (`mdates.date2num`). Crucially, it will use `bounds_error=False` and `fill_value=np.nan` to prevent extrapolation outside the valid moments data range.
        *   `vdrift_va_p2-p1_apfits`: Fetches `na` (alpha density) from `alpha_fits` via `data_cubby` on demand, calculates `valfven_apfits` (needs `na` and `n_tot`), then calculates the normalized drift. Caches result.
        *   **Alignment Note:** Per scientist confirmation, `spi_sf00_fits` (proton) and `spi_sf01_fits` (alpha) data are pre-aligned. Therefore, **no interpolation of `na` is required** before calculation.
        *   `|vdrift|_va_p2-p1_apfits`: Similar to above, but takes the absolute value. Caches result.
    *   **Encapsulation:** The interpolation logic will be placed in a private helper method within the class (e.g., `_interpolate_to_self_time`) for clarity and potential reuse.
    *   **Dependency Handling:** `@property` methods will log a warning/error and return `None`/`NaN`s if dependencies (`spi_sf00_l3_mom`, `alpha_fits`) cannot be retrieved.
    *   Minimally adapt `set_ploptions` to handle these specific CWYN variables (likely just needs to ensure they are included in the loop that creates `plot_manager` instances).
    *   Specifically, ensure `set_ploptions` creates attributes using the desired **PlotBot Names** (e.g., `self.vsw_mach_pfits`, `self.vdrift_va_p2p1_apfits`) and connects them to the appropriate data source (either `self.raw_data` entries or the new `@property` methods).
    *   **Mixed Variable Plot Definitions:** Add new `plot_manager` instances for `vdrift_va_p2p1_apfits` and `abs_vdrift_va_p2p1_apfits`. Since exact matches for these calculated names were not found in the provided `zip_fits_vars.py` snippet, **adapt the plot style** from related variables like `vdrift_va_pfits` (e.g., color='navy', marker='*', size=5).
    *   **Example `plot_manager` Definitions (Adapting Style) for `set_ploptions`:**

      ```python
      # 35. vdrift_va_p2p1_apfits (Normalized drift using Va including alphas)
      self.vdrift_va_p2p1_apfits = plot_manager(
          data_source=lambda: self.vdrift_va_p2p1_apfits, # Link to @property
          plot_options=ploptions(
              var_name='vdrift_va_p2p1_apfits', # Internal property name
              data_type='proton_fits',
              class_name='proton_fits',
              subclass_name='vdrift_va_p2p1_apfits', # PlotBot attribute name
              plot_type='scatter',
              y_label=r'$V_{drift}/V_A$',
              legend_label=r'$Vd_{p2-p1}/V_{A,ap}$$', # Adapted label
              color='navy',                  # Adapted style
              y_scale='linear',
              marker_style='*',              # Adapted style
              marker_size=5,                 # Adapted style
              alpha=0.7,                     # Adapted style
              y_limit=None
          )
      )

      # 36. abs_vdrift_va_p2p1_apfits (Absolute normalized drift using Va including alphas)
      self.abs_vdrift_va_p2p1_apfits = plot_manager(
          data_source=lambda: self.abs_vdrift_va_p2p1_apfits, # Link to @property
          plot_options=ploptions(
              var_name='abs_vdrift_va_p2p1_apfits', # Internal property name
              data_type='proton_fits',
              class_name='proton_fits',
              subclass_name='abs_vdrift_va_p2p1_apfits', # PlotBot attribute name
              plot_type='scatter',
              y_label=r'$|V_{drift}|/V_A$',
              legend_label=r'$|Vd_{p2-p1}|/V_{A,ap}$$', # Adapted label
              color='navy',                   # Adapted style
              y_scale='linear',
              marker_style='*',               # Adapted style
              marker_size=5,                  # Adapted style
              alpha=0.7,                      # Adapted style
              y_limit=None
          )
      )
      ```

3.  **Testing:** Adapt `test_fits_cdf_server_integration.py` and potentially other tests to verify the new behavior of both classes.
4.  **Refactor `alpha_fits_class`:** Refactor using the standard eager approach (update `calculate_variables` and `set_ploptions` based on the new `spi_sf01_fits` CDF data).
    *   Ensure `__init__` defines keys in `self.raw_data` for *all* variables present in the `spi_sf01_fits` CDF (including unknowns like `Epoch_1`, `*_v`, etc.) so they are extracted if present.
    *   Ensure `set_ploptions` assigns the correct PlotBot attribute names for alpha parameters.

### Proton Variable Sources (`proton_fits_class` - Post-Refactor):

This clarifies where each variable originates or how it's calculated in the *target* implementation after refactoring `proton_fits_class`.

**Directly Extracted from `spi_sf00_fits` CDF:**

*   `Epoch` (used for `time` and `datetime_array`)
*   `np1`
*   `np2`
*   `Tperp1`
*   `Tperp2`
*   `Trat1`
*   `Trat2`
*   `vdrift` (Scalar)
*   `vp1` (Vector: x, y, z)
*   `B_inst` (Vector: x, y, z)
*   `B_SC` (Vector: x, y, z)
*   `chi_p` (CDF name `chi`)
*   `Tpar1`
*   `Tpar2`
*   `Tpar_tot`
*   `Tperp_tot`
*   `Temp_tot`
*   `n_tot`
*   `vp2` (Vector: x, y, z)
*   `vcm` (Vector: x, y, z)
*   `bhat_inst` (Vector: x, y, z)
*   `qz_p`
*   `vp1_mag`
*   `vcm_mag`
*   `vp2_mag`
*   `B_mag` (Note: Check if *always* present; calculation fallback exists)
*   `epad_strahl_centroid` (If present)
*   `ps_ht1` (If present)
*   `ps_ht2` (If present)
*   `qz_p_par` (If present)
*   `qz_p_perp` (If present)
*   *Uncertainties (`*_dpar`) and potential vector component duplicates (`*_v`) from CDF...*

**Calculated Internally (Eagerly in `calculate_variables`):**

*   `valfven` (using `B_mag`, `n_tot`) - *PlotBot Name: `valfven_pfits`*
*   `beta_ppar` (using `Tpar_tot`, `n_tot`, `B_mag`) - *PlotBot Name: `beta_ppar_pfits`*
*   `beta_pperp` (using `Tperp_tot`, `n_tot`, `B_mag`) - *PlotBot Name: `beta_pperp_pfits`*
*   `beta_p_tot` (using `beta_ppar`, `beta_pperp`)
*   `ham_param` (using `Tperp1`, `Tperp2`, `Trat_tot`)
*   `np2_np1_ratio` (using `np1`, `np2`) - *PlotBot Name: `np2/np1`*
*   `vdrift_abs` (using `vdrift`) - *PlotBot Name: `|vdrift|`*
*   `vdrift_va` (using `vdrift`, `valfven`) - *PlotBot Name: `vdrift_va_pfits`*
*   `chi_p_norm` (using `chi_p`)
*   `Vcm_mach` (using `vcm_mag`, `valfven`)
*   `Vp1_mach` (using `vp1_mag`, `valfven`)
*   `abs_qz_p` (using `qz_p`) - *PlotBot Name: `|qz_p|`*
*   `|vdrift|_va_p2-p1_apfits` (Requires fetching `alpha_fits` for `na`, calculating `valfven_apfits`, then `abs(vdrift)/valfven_apfits`)

*(Note: The variable `qz_p` has a complex formula in the spreadsheet but is directly available in the CDF, so we use the CDF version.)*

*(Note: Unknown variables like `*_v`, `epad_strahl_centroid`, `ps_ht1`, `ps_ht2`, `Epoch_1` will be loaded into `raw_data` if present in the CDFs, but are not currently used in calculations or plotting.)*

### Questions for Scientist (Regarding CDF Contents):

*   Are the variables ending in `_v` (e.g., `B_inst_v`, `vcm_v`) simply the same values as their non-`_v` counterparts, or do they represent something different (like variance or an alternative calculation)?
*   What do `epad_strahl_centroid`, `ps_ht1`, and `ps_ht2` represent? Are they needed for standard analysis or plotting?
*   What is `Epoch_1`? Is it different from `Epoch`?
*   What are the preferred `ploptions` (plot styles, labels, etc.) for the newly calculated mixed drift variables `vdrift_va_p2p1_apfits` and `abs_vdrift_va_p2p1_apfits` (which use Alfven speed calculated with both proton and alpha densities)? We have temporarily adapted the style from `vdrift_va_pfits`.

### Current Status & Next Steps:

*   `psp_data_types.py` updated.
*   `proton_fits_class.py` is ready for targeted CWYN implementation.
*   **NEXT:** Implement Step 2: Modify `proton_fits_class.py` to add the `_cwyn_cache`, implement the three `@property` methods (`vsw_mach`, `vdrift_va_p2-p1_apfits`, `|vdrift|_va_p2-p1_apfits`) with dependency fetching and calculation logic, and adapt `set_ploptions`.
    *   This includes implementing the alignment logic for `vsw_mach` (linear interpolation, no extrapolation, using `vsw` from `spi_sf00_l3_mom`) within a private helper method.
    *   The mixed drift calculations will use `na` from `alpha_fits` directly (no alignment needed).
    *   Crucially, `set_ploptions` will assign the final **PlotBot Names** (e.g., `self.vsw_mach_pfits`) as attributes, linking them to the appropriate internal data (`raw_data` or `@property`), and will add entries for the new mixed variables based on old definitions.
    *   Since exact plot definitions for the new mixed variables were not found, their style will be adapted from related variables (e.g., `vdrift_va_pfits`). Example definitions are documented under Step 2.
    *   A note has been added to ask Jaye for the definitive plot options.
*   Then proceed to Step 3 (testing) and Step 4 (refactor `alpha_fits_class`).

### Debugging `plot_manager` and `proton_fits` Integration (May 1, 2025)

- **Problem:** The `test_plotbot_basic_fits_call` test was passing, but the plot generated showed no data for `proton_fits.n_tot`, despite debug prints showing data being loaded.
- **Debugging Steps:** Added extensive debug prints in `plotbot_main`, `plot_manager` (`__new__`, `__array_finalize__`, `__getattr__`), and `proton_fits_class` (`update`, `set_ploptions`).
- **`__array_finalize__` Issue Identified:** Traced the loss of `datetime_array` on the `n_tot` plot_manager instance back to the `plot_options` assignment within `plot_manager.__array_finalize__`. When numpy creates internal views/copies, this assignment was unexpectedly overwriting or corrupting the `plot_options` (including `datetime_array`).
- **Fix:** Commenting out the line `self.plot_options = getattr(obj, 'plot_options', None)` (or the conditional version tried earlier) within `__array_finalize__` resolved the issue of `datetime_array` being lost between the data class update and retrieval in `plotbot_main`. The data and `datetime_array` were confirmed to persist correctly on the `n_tot` object when retrieved.
- **Remaining Issue:** Despite the fix ensuring `n_tot` had its data and `datetime_array` when passed to the plotting stage, the final plot output still indicated "points=0 (no data in range)". This suggests the problem now lies *within the plotting logic itself* – specifically, how it filters or interprets the data/time arrays based on the requested time range just before calling `plt.scatter`.
- **Complexity Concerns:** The recent refactoring of `proton_fits_class` to use a complex Calculate What You Need (CWYN) approach (with properties, caching, dependency fetching helpers, and lazy loading via `__getattr__`) has significantly deviated from the simpler, eager calculation model used in working classes like `psp_mag_classes.py`. This complexity might be contributing to the current plotting issue or making it harder to debug.

### Git Branch Creation (May 1, 2025)

Creating a new branch `proton_fits_class_refactor` to isolate the CWYN refactoring work. The initial commit will include the structural setup (sub-step 1).

### CWYN Implementation Clarifications:

Based on discussion, the specific implementation details for the `@property` methods in `proton_fits_class.py` are as follows:

1.  **Fetching Dependencies:**
    *   The `@property` methods will access the main `PlotBot` instance (expected to be available as `self.plotbot` within the class instance).
    *   The `data_cubby` instance will be accessed via `self.plotbot.data_cubby`.
    *   Dependencies will be fetched using the `data_cubby`'s mechanism, likely `self.plotbot.data_cubby.grab('key')`, where `'key'` is the standard PlotBot data type name (e.g., `'spi_sf00_l3_mom'`, `'sf01_fits'`).

2.  **`spi_sf00_l3_mom` Structure:**
    *   The time variable for `spi_sf00_l3_mom` data is `Epoch`.
    *   The relevant solar wind speed variable is expected to be `vp` (magnitude). If `vp` is not directly available on the fetched object, the magnitude will be calculated from the `V_rtn` vector components.

3.  **Interpolation Helper:**
    *   Instead of replicating `showdahodo.downsample_time_based`, **`scipy.interpolate.interp1d` will be used directly** for aligning the `spi_sf00_l3_mom` data to the `proton_fits` time base (`self.raw_data['Epoch']`).
    *   The interpolation will use `kind='linear'`, `bounds_error=False`, and `fill_value=np.nan` to handle time mismatches and prevent extrapolation.

These clarifications will guide the implementation of Step 2 in the refactoring plan.

### Implementation Sub-steps for `proton_fits_class` CWYN (May 1, 2025):

Following the plan, the implementation of Step 2 will proceed in these stages:

1.  **Initialize Structure:** Add `_cwyn_cache = {}` and `self.plotbot = None` to `__init__`. Add necessary imports (`numpy`, `scipy.interpolate`, `matplotlib.dates`, `logging`). **(DONE)**
2.  **Add Interpolation Helper:** Implement the private `_interpolate_to_self_time(self, source_time, source_data)` method using `scipy.interpolate.interp1d` with `kind='linear'`, `bounds_error=False`, and `fill_value=np.nan`. **(DONE)**
3.  **Implement `@property vsw_mach`:** Create the property, including cache check, dependency fetch (`spi_sf00_l3_mom`), checking for `vp` or calculating magnitude from `V_rtn`, calling the interpolation helper, performing the Mach number calculation (`vp / valfven`), caching the result, and error handling. **(DONE)**
3.5. **Refactor CWYN Boilerplate (Helper Method):** Create a private helper `_check_cwyn_cache_and_prereqs(self, cache_key, required_internal_keys)` to handle the common logic for checking the `_cwyn_cache` and validating prerequisites (`self.plotbot`, `self.time`, required `self.raw_data` entries). Update existing properties (`vsw_mach`, `vdrift_va_p2p1_apfits`) to use this helper. **(DONE)**
3.6. **Refactor Dependency Fetching (Helper Method):** Create a second private helper `_fetch_and_validate_dependency(self, cache_key, cubby_key, required_dependency_vars)` to handle fetching the external dependency instance from `data_cubby`, extracting specified variables (checking `raw_data` then attributes), and performing basic validation. Update properties (`vsw_mach`, `vdrift_va_p2p1_apfits`) to use this helper. **(DONE)**
4.  **Implement `@property abs_vdrift_va_p2p1_apfits`:** Create the property, similar to the above but taking the absolute value of the result (`abs(vdrift / valfven_apfits)`), caching, and error handling. **(DONE)**
5.  **Adjust `calculate_variables`:** Remove the placeholder logic/assignment for `vsw_mach`, `vdrift_va_p2p1_apfits`, and `abs_vdrift_va_p2p1_apfits` as these are now handled by properties. **(DONE)**
6.  **Implement Lazy `plot_manager` Instantiation:** Apply the new plan: Modify `set_ploptions` to store CWYN `ploptions` and enhance `__getattr__` to create `plot_manager` instances on first access.

### Refactor Helper Method (`_create_fits_scatter_ploptions`) (May 1, 2025):

*   **Goal:** Update the `_create_fits_scatter_ploptions` helper in `psp_proton_fits_classes.py` to match the more flexible parameter pattern used in `psp_alpha_fits_classes.py` (`_create_alpha_scatter_ploptions`). This involves adding optional parameters for `marker_style`, `marker_size`, `alpha`, `y_scale`, and `y_limit` with appropriate defaults. **(DONE)**

### Clarification: How Data Classes Access `DataCubby`

A question arose regarding how data class instances (like `proton_fits_class`) gain access to the main `PlotBot` instance and, consequently, its `DataCubby` to fetch dependencies (e.g., accessing `self.plotbot.data_cubby.grab('key')` within an `@property` method).

The mechanism is **Dependency Injection**, orchestrated by the `DataCubby` itself:

1.  **Request Initiation:** When PlotBot needs data (e.g., triggered by a user request like `plt.data = 'sf00_fits'`), the request is ultimately handled by the `DataCubby`.
2.  **Instance Creation:** If the requested data (for a specific time range) isn't already cached within `DataCubby`, the `DataCubby` determines the appropriate class to handle it (e.g., `proton_fits_class` for `'sf00_fits'`). It then instantiates this class.
3.  **Reference Passing:** Crucially, during the instantiation (`__init__` call) of the data class (e.g., `proton_fits_class(init_args...)`), the `DataCubby` passes a reference to the main `PlotBot` instance (or potentially a reference to itself, the `DataCubby`) as one of the arguments.
4.  **Reference Storage:** The `__init__` method of the data class (`proton_fits_class`) receives this reference and stores it as an instance attribute (e.g., `self.plotbot = plotbot_instance_passed_in`).
5.  **Accessing Dependencies:** Now, methods within the `proton_fits_class` instance (like the `@property` methods we're planning) can access the stored `self.plotbot` attribute. From there, they can reach the `DataCubby` via `self.plotbot.data_cubby` and use its methods (like `grab()`) to fetch any *other* data required for their calculations (e.g., fetching `'sf01_fits'` to get alpha density).

This pattern ensures that data classes remain focused on their specific data type but have a controlled way to access the broader application context (`PlotBot` and its `DataCubby`) when they need to resolve dependencies on other datasets.

**Note on CWYN Cache Invalidation:** The internal cache (`self._cwyn_cache`) used by the `@property` methods is intentionally simple (an instance-level dictionary). Cache invalidation primarily relies on the `DataCubby`'s behavior. When a new time range is requested, `DataCubby` typically creates a *new* instance of the data class (e.g., `proton_fits_class`), automatically discarding the old instance and its cache. Therefore, explicit invalidation logic within the data class itself is not required for handling time range changes. However, this relies on the assumption that `DataCubby` instantiates fresh objects per request/time range. Invalidation due to updates in the *source data files* (e.g., newer versions of CDFs for the same time period) would depend on `DataCubby` detecting these changes and triggering a reload, which would again likely lead to a new instance. If `DataCubby` lacks this source-update detection, the `_cwyn_cache` (like `DataCubby`'s own cache) could potentially hold stale data under those specific circumstances.

### Addressing the `set_ploptions`/CWYN Issue (May 1, 2025)

The previous comparison identified that the `plot_manager` constructor needs data at initialization, which conflicts with the lazy calculation goal of the CWYN properties. The `data_source=lambda:` approach in `set_ploptions` is incorrect.

A revised approach using lazy initialization via `__getattr__` will be implemented:

**Plan:**

1.  **Modify `set_ploptions()`:**
    *   Remove the direct creation of `plot_manager` instances for CWYN variables (`vsw_mach_pfits`, `vdrift_va_p2p1_apfits`, `abs_vdrift_va_p2p1_apfits`).
    *   Instead, create and store *only* their `ploptions` configurations in a new internal dictionary, e.g., `self._cwyn_ploptions = { 'vsw_mach_pfits': ploptions(...), ... }`.

2.  **Enhance `__getattr__(self, name)`:**
    *   Intercept attribute access.
    *   Check if `name` corresponds to a key in `self._cwyn_ploptions`.
    *   If it is a CWYN variable:
        *   Call the corresponding `@property` method (e.g., `getattr(self, property_name)`) to trigger the calculation and get the actual data array.
        *   Create the `plot_manager` instance using this data array and the stored `ploptions` from `self._cwyn_ploptions[name]`.
        *   Cache the newly created `plot_manager` instance directly as an attribute on `self` using `setattr(self, name, pm)`.
        *   Return the new `plot_manager` instance.
    *   If `name` is not a CWYN variable, proceed with the existing `__getattr__` logic (listing available attributes, raising `AttributeError`).
    *   Ensure the available attributes listed in the error message include the keys from `_cwyn_ploptions`.

**Benefits:**
*   Implements true lazy calculation for CWYN variables.
*   Keeps configuration in `set_ploptions`.
*   Minimal changes needed to the `@property` methods themselves.

**(Implementation of this plan replaces the previous incorrect Step 6)**

### Comparison: `proton_fits_class` vs. `proton_class` (May 1, 2025)

A comparison between the newly refactored `proton_fits_class` and the existing `proton_class` reveals key differences in their data handling strategies:

*   **Data Source & Calculation Model:**
    *   `proton_class`: Relies solely on `spi_sf00_l3_mom` input. Performs all calculations eagerly within `calculate_variables`.
    *   `proton_fits_class`: Uses the `sf00_fits` CDF as its primary source. Calculates variables derived *only* from this source eagerly in `calculate_variables`. Uses a **mixed Calculate What You Need (CWYN)** approach for variables requiring external data (`spi_sf00_l3_mom`, `sf01_fits`).
*   **Dependency Management:**
    *   `proton_class`: No external dependencies required beyond its primary input.
    *   `proton_fits_class`: Manages external dependencies via `@property` methods (`vsw_mach`, `vdrift_va_p2p1_apfits`, `abs_vdrift_va_p2p1_apfits`) which utilize helper methods (`_check_cwyn_cache_and_prereqs`, `_fetch_and_validate_dependency`) to fetch data from `data_cubby` and cache results lazily.
*   **Identified Issue:**
    *   The current implementation in `proton_fits_class.set_ploptions` attempts to link `plot_manager` instances to the CWYN properties using a `data_source=lambda: self.property_name` argument.
    *   **Problem:** The `plot_manager.__new__` method does *not* accept a `data_source` argument. It requires the actual data array at initialization.
    *   **Next Step:** This linkage mechanism needs to be redesigned. Potential solutions involve modifying the `@property` methods to create/cache the `plot_manager` instance upon first calculation, or exploring other ways to defer `plot_manager` creation or update its data after the property is evaluated.

### Implementation Sub-steps for `proton_fits_class` CWYN (May 1, 2025):

Following the plan, the implementation of Step 2 will proceed in these stages:

1.  **Initialize Structure:** Add `_cwyn_cache = {}` and `self.plotbot = None` to `__init__`. Add necessary imports (`numpy`, `scipy.interpolate`, `matplotlib.dates`, `logging`). **(DONE)**
2.  **Add Interpolation Helper:** Implement the private `_interpolate_to_self_time(self, source_time, source_data)` method using `scipy.interpolate.interp1d` with `kind='linear'`, `bounds_error=False`, and `fill_value=np.nan`. **(DONE)**
3.  **Implement `@property vsw_mach`:** Create the property, including cache check, dependency fetch (`spi_sf00_l3_mom`), checking for `vp` or calculating magnitude from `V_rtn`, calling the interpolation helper, performing the Mach number calculation (`vp / valfven`), caching the result, and error handling. **(DONE)**
3.5. **Refactor CWYN Boilerplate (Helper Method):** Create a private helper `_check_cwyn_cache_and_prereqs(self, cache_key, required_internal_keys)` to handle the common logic for checking the `_cwyn_cache` and validating prerequisites (`self.plotbot`, `self.time`, required `self.raw_data` entries). Update existing properties (`vsw_mach`, `vdrift_va_p2p1_apfits`) to use this helper. **(DONE)**
3.6. **Refactor Dependency Fetching (Helper Method):** Create a second private helper `_fetch_and_validate_dependency(self, cache_key, cubby_key, required_dependency_vars)` to handle fetching the external dependency instance from `data_cubby`, extracting specified variables (checking `raw_data` then attributes), and performing basic validation. Update properties (`vsw_mach`, `vdrift_va_p2p1_apfits`) to use this helper. **(DONE)**
4.  **Implement `@property abs_vdrift_va_p2p1_apfits`:** Create the property, similar to the above but taking the absolute value of the result (`abs(vdrift / valfven_apfits)`), caching, and error handling. **(DONE)**
5.  **Adjust `calculate_variables`:** Remove the placeholder logic/assignment for `vsw_mach`, `vdrift_va_p2p1_apfits`, and `abs_vdrift_va_p2p1_apfits` as these are now handled by properties. **(DONE)**
6.  **Implement Lazy `plot_manager` Instantiation:** Apply the new plan: Modify `set_ploptions` to store CWYN `ploptions` and enhance `__getattr__` to create `plot_manager` instances on first access.

### Refactor Helper Method (`_create_fits_scatter_ploptions`) (May 1, 2025):

*   **Goal:** Update the `_create_fits_scatter_ploptions` helper in `psp_proton_fits_classes.py` to match the more flexible parameter pattern used in `psp_alpha_fits_classes.py` (`_create_alpha_scatter_ploptions`). This involves adding optional parameters for `marker_style`, `marker_size`, `alpha`, `y_scale`, and `y_limit` with appropriate defaults. **(DONE)**

### May 1st, 2025 - FITS CDF Integration Debugging

- **Identified Download Issue:** Ran into `ValueError: invalid literal for int()` during download attempt for `sf00_fits`. The root cause was in `plotbot/data_download_helpers.py` (`process_file_listing`). The regex for FITS files captures the date as group 1 and version as group 2, but the code assumed the version was always group 1.
- **Fixed Downloader:** Modified `process_file_listing` to check the number of captured groups. If 1 group, use group 1 for version; if 2+ groups, use group 2. This handles both old and new filename patterns.
- **Identified Importer Scope Issue:** Encountered `UnboundLocalError: cannot access local variable 'config'` in `plotbot/data_import.py`. The `config` variable (holding settings from `psp_data_types.py`) was only being defined within the `if data_type == 'ham':` block, making it unavailable to the subsequent `else` block used for CDF imports.
- **Fixed Importer Scope:** Moved the `config = psp_data_types[data_type]` assignment earlier in `import_data_function`, before the `if/else` split, making it accessible to both branches.
- **Simplified FITS Path:** Updated the `local_path` for `sf00_fits` in `plotbot/data_classes/psp_data_types.py` to remove the redundant `/cdf_files/` directory segment, resulting in a cleaner local path: `psp_data/sweap/spi_fits/sf00/p2/v00/`. Confirmed the file wasn't actually present in the old incorrect location, so no deletion was needed.
- **Stardust Test Issue:** Encountered `TypeError: len() of unsized object` and `RecursionError` when running `test_stardust.py::test_stardust_fits_group_1`. This seems related to the test fixture (`stardust_sf00_test_data`) manually calling `proton_fits_instance.update()` without ensuring the instance has a valid `.plotbot` reference, which is needed for CWYN properties. Attempted a fix by assigning the reference within the fixture, but the recursion error persisted.
- **Decision:** Pausing debugging of the Stardust FITS test for now. Proceeding with pushing the downloader and importer fixes as they appear functional based on manual testing and the progress in the `test_fits_cdf_server_integration.py` test.

***

**Session Closed: April 30, 2025**

***