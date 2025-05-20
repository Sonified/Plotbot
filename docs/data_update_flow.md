# Understanding Data Updates in Plotbot

This document outlines the process by which data is loaded, updated, and accessed within the Plotbot system, focusing on the interaction between `get_data`, the `DataCubby`, `global_tracker`, and the `.update()` methods of data classes.

## Core Data Loading and Update Flow

When a request is made to plot data for a specific time range (`trange`) and set of variables, the following sequence of events typically occurs:

1.  **`get_data(trange, *variables)` Invocation:**
    *   This is the primary entry point for requesting data.
    *   Its main responsibility is to ensure that the data for the specified `trange` and variables is available and up-to-date in the system's memory.

2.  **`global_tracker` Consultation:**
    *   `get_data` first consults the `global_tracker` (an instance of `DataTracker`).
    *   The tracker maintains a record of which `data_type`s (e.g., `'mag_RTN_4sa'`, `'spi_sf00_l3_mom'`) have been loaded or calculated for which time ranges.
    *   `global_tracker.is_calculation_needed(trange, data_type_key)` determines if new data needs to be fetched/calculated or if existing cached data is sufficient for the requested `trange`.

3.  **Data Fetching/Import (if needed):**
    *   If the `global_tracker` indicates that data for the `trange` is missing or needs a refresh (`calculation_needed == True`):
        *   **Downloading:** `get_data` may trigger download functions (e.g., `download_berkeley_data`, `download_spdf_data`) to retrieve the necessary raw data files from remote servers if they aren't already available locally.
        *   **Importing:** `import_data_function(trange, data_type)` is called. This function reads the data from the local files (CDF, CSV, etc.) for the specified `trange` and `data_type`, and packages it into a temporary `DataObject` instance.

4.  **`DataCubby` and Global Instance Update:**
    *   The `DataObject` returned by `import_data_function` is then passed to `data_cubby.update_global_instance(cubby_key, data_object)`.
    *   The `DataCubby` acts as a central repository or manager for the main, persistent data class instances (e.g., `plotbot.mag_rtn_4sa`, `plotbot.proton`).
    *   **Crucially, it is within `data_cubby.update_global_instance` that the `.update(data_object)` method of the relevant global data class instance is called.** For example, `plotbot.mag_rtn_4sa.update(data_object_for_mag)` would be invoked.

5.  **Data Class `.update()` Method:**
    *   The `.update()` method within a specific data class (e.g., `mag_rtn_4sa_class.update()`) is responsible for taking the new data from the passed `DataObject` and populating its internal attributes. This typically involves:
        *   Updating its primary `datetime_array`.
        *   Updating its `raw_data` dictionary (e.g., `self.raw_data['br']`, `self.raw_data['density']`).
        *   Re-initializing its associated `plot_manager` instances for each component via `self.set_ploptions()` to reflect the new data and time range.

6.  **`global_tracker` Update:**
    *   If the `DataCubby` successfully updates the global instance, `get_data` then informs the `global_tracker` that the `trange` for that `data_type_key` has been successfully processed (`global_tracker.update_calculated_range(trange, cubby_key)`).

## Updating Calculated Properties (e.g., `mag_rtn_4sa.br_norm`)

Calculated properties, like `mag_rtn_4sa.br_norm`, are not directly updated by the `get_data` -> `DataCubby` flow in the same way as base data components.

*   **Dependency:** These properties derive their values from the data stored in their parent object (e.g., `br_norm` depends on `mag_rtn_4sa.datetime_array` and `mag_rtn_4sa.raw_data['br']`, as well as potentially data from other objects like `proton.sun_dist_rsun`).
*   **Lazy Calculation & Caching:** They are often implemented as Python `@property` methods. The calculation might be performed only when the property is first accessed (lazy loading) and potentially cached for subsequent accesses.
*   **Refresh Mechanism:** For a calculated property to reflect changes in its underlying dependencies (e.g., when the parent `mag_rtn_4sa` object receives new data for a different `trange`), a mechanism is needed to invalidate its cached value and force a recalculation.
    *   **Invalidation in Parent's `.update()`:** A common pattern is to include logic within the parent class's `.update()` method to explicitly clear any cached data or managers related to its calculated properties. For example, `mag_rtn_4sa_class.update()` would set `self._br_norm_manager = None` and `self.raw_data['br_norm'] = None`.
    *   **Recalculation on Next Access:** When the calculated property (e.g., `mag_rtn_4sa.br_norm`) is accessed again (e.g., by the plotting routines), its `@property` logic detects that its cached data is missing (because it was invalidated). It then re-runs its internal calculation method (e.g., `_calculate_br_norm()`), which will now use the (updated) data from its parent object.

## Summary

*   `get_data` orchestrates the data loading process.
*   `global_tracker` avoids redundant operations.
*   `DataCubby` manages the update of persistent global data instances by calling their respective `.update()` methods.
*   The `.update()` methods of data classes refresh their core data arrays.
*   Calculated properties are refreshed by invalidating their caches when their parent objects are updated, leading to a recalculation upon next access.