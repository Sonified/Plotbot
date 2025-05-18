# Plotbot Data Flow: From User Call to Plotted Data

This document outlines the typical sequence of events when a user makes a call to the main `plotbot()` function to generate a plot.

1.  **User Initiates Plot (`plotbot_main.py`)**
    *   The user calls `plotbot(trange, var1, axis1, var2, axis2, ...)` specifying a time range (`trange`) and pairs of data variables (e.g., `proton.density`, `mag_rtn.br`) and their target plot axes. These `var` arguments are typically `plot_manager` instances associated with specific attributes of data class instances.
    *   `plotbot_main.py` parses these arguments.

2.  **Data Orchestration (`get_data.py`)**
    *   `plotbot_main.py` calls `get_data(trange, *list_of_requested_plot_managers)`.
    *   **Identifying Required Data Products:**
        *   `get_data()` iterates through each `plot_manager` instance (`var`) passed in `*list_of_requested_plot_managers`.
        *   For each `var`, it inspects attributes like `var.data_type` (e.g., `'spi_sf00_l3_mom'`) and `var.subclass_name` (e.g., `'density'`).
        *   It collects all unique main `data_type` strings into a set (e.g., `required_data_types = {'spi_sf00_l3_mom', 'mag_RTN'}`). This means if multiple variables from the `proton` class are requested, its underlying `data_type` (`spi_sf00_l3_mom`) is only listed once.
        *   The specific `subclass_name`s are primarily used for logging within `get_data` at this stage.
    *   **Processing Loop per Data Product:** `get_data()` then enters a loop, iterating through each unique `data_type` in `required_data_types`.
        *   **Cache Check (`global_tracker`):** For the current `data_type` (e.g., `'spi_sf00_l3_mom'`) and the given `trange`, `get_data()` consults `global_tracker.is_calculation_needed()`. This checks if this entire data product has already been fully processed (downloaded, raw data imported, and class calculations run) for this time range in the current session.
            *   If `global_tracker` indicates the data product is already processed and up-to-date, `get_data()` may skip further processing for *this entire `data_type`*, relying on the existing data within the corresponding global class instance (e.g., `proton` instance).
        *   **Data Download (e.g., `data_download_berkeley.py`, `data_download_pyspedas.py`):** If the data product is not locally available or needs refreshing, `get_data()` can invoke download functions. These fetch the raw data files (e.g., CDFs for `spi_sf00_l3_mom`) associated with that `data_type`.
        *   **Raw Data Import (`data_import.py`):**
            *   `get_data()` calls `import_data_function(trange, current_data_type)` (e.g., `import_data_function(trange, 'spi_sf00_l3_mom')`).
            *   `import_data_function()` reads *all defined raw variables* for that `current_data_type` from the local files. For example, for `spi_sf00_l3_mom`, it would attempt to extract `Epoch`, `VEL_RTN_SUN`, `DENS`, `TEMP`, `MAGF_INST`, `T_TENSOR_INST`, `SUN_DIST`, etc., from the CDF, as defined in its configuration in `psp_data_types.py`.
            *   It returns a `DataObject` containing `times` (TT2000) and `data` (a dictionary of *all these raw variable arrays* that were successfully read).

3.  **Instance Update (`data_cubby.py`)**
    *   Back in `get_data.py` (still within the loop for the `current_data_type`), the `DataObject` is passed to `data_cubby.update_global_instance(target_key, imported_data_obj)`. The `target_key` is derived from `current_data_type` (e.g., `'proton'`).
    *   `data_cubby.update_global_instance()` retrieves the global instance (e.g., `proton` instance of `proton_class`).
    *   It calls `proton_instance.update(imported_data_obj)`.

4.  **Data Class Processing (e.g., `psp_proton.py` - `proton_class`)**
    *   **`YourDataClass.update(self, imported_data_obj)`:**
        *   This method receives the `imported_data_obj` which contains *all raw variables* for its associated data product.
        *   Calls `self.calculate_variables(imported_data_obj)`.
        *   Then calls `self.set_ploptions()`.
    *   **`YourDataClass.calculate_variables(self, imported_data_obj)`:**
        *   Takes the comprehensive `imported_data_obj`.
        *   This method proceeds to calculate *all* its defined scientific variables (e.g., `vr`, `vt`, `anisotropy`, `sun_dist_rsun`) from the raw data provided, storing them in `self.raw_data`.
        *   The instance's primary time array, `self.datetime_array` (NumPy array of Python datetime objects), is also set here, usually derived from `imported_data_obj.times`.
    *   **`YourDataClass.set_ploptions(self)`:**
        *   Initializes `plot_manager` objects for all variables (e.g., `self.vr`, `self.sun_dist_rsun`).
        *   Each `plot_manager` (e.g., `self.sun_dist_rsun`) is given its corresponding data array from `self.raw_data` (e.g., `self.raw_data['sun_dist_rsun']`) and all associated plotting metadata.

5.  **Plotting (`plotbot_main.py` continued)**
    *   `plotbot_main.py` retrieves the `plot_manager` instances for the user-requested variables (e.g., `proton.sun_dist_rsun` refers to `proton_instance.sun_dist_rsun` which is a `plot_manager` containing the fully calculated data).
    *   It uses the data from these `plot_manager` instances to construct the plots.

**Summary of Data States:**

*   **Remote Server:** Original raw data files (CDFs).
*   **Local Filesystem:** Downloaded raw data files (CDFs, CSVs).
*   **`DataObject` (from `data_import.py`):** Contains raw data arrays (e.g., `SUN_DIST`) as read from files for a given data product.
*   **Data Class Instance (`proton_instance` after `calculate_variables` and `set_ploptions`):**
    *   `self.datetime_array`: Processed time array.
    *   `self.raw_data['sun_dist_rsun']`: Contains the calculated `sun_dist_rsun` array.
    *   `self.sun_dist_rsun` (the attribute): Is a `plot_manager` instance whose `.data` attribute holds the calculated `sun_dist_rsun` array.

This current flow ensures that when a data product (like `spi_sf00_l3_mom` for the `proton` class) is processed, all its associated variables (including `sun_dist_rsun`) are calculated and made available through their respective `plot_manager` attributes. 