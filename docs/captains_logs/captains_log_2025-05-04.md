# Captain's Log: 2025-05-04

## 💥💥💥 MOST IMPORTANT UPDATE: DATA CUBBY & SNAPSHOTS OPERATIONAL! 💥💥💥

After significant debugging and refinement, the core `DataCubby` architecture, including the crucial `save_data_snapshot` and `load_data_snapshot` features, is **confirmed fully operational**. The system now correctly:

1.  Loads data from snapshots into the appropriate global instances.
2.  Respects loaded snapshot data, preventing unnecessary re-downloads (`get_data` logic fixed).
3.  Handles internal naming inconsistencies (`spe_sf0_pad` vs `epad`) gracefully during loading and tracker checks.

This represents a major step forward in data persistence and workflow efficiency for Plotbot!

## Major Updates & Learnings

### 1. Refined Data Flow for Merging Time Series in DataCubby

**Problem:** We encountered persistent issues where requesting data for multiple, non-contiguous time ranges resulted in only the last requested range being available for plotting. Initial fixes involving `deepcopy` in `DataCubby.stash` and checks in `get_data` were insufficient because the underlying data within the global data class instances (e.g., `mag_rtn_4sa`) was being overwritten *before* the merge logic could properly compare the old and new data.

**Solution & Current Logic:** Centralized the update and merge responsibility within the `DataCubby`, ensuring the global instances are always the single source of truth and are updated correctly.

**Detailed Flow:**
1.  **`get_data` Trigger:** When `get_data` determines data needs refreshing (based on `DataTracker` *and* a check of the actual data range currently in the `DataCubby`), it calls `import_data_function` to get the raw, newly imported data (`DataObject`).
2.  **Delegate to Cubby:** `get_data` then calls the *new* method `data_cubby.update_global_instance(data_type_string, raw_data_object)`. `get_data` no longer handles instance creation or updates directly.
3.  **`update_global_instance` Orchestration:**
    *   Retrieves the *existing global instance* (e.g., `mag_rtn_4sa`) using `data_cubby.grab()`.
    *   **If Global Instance is Empty:** Calls `global_instance.update(raw_data_object)`. This method (within the specific data class like `mag_rtn_4sa_class`) uses `calculate_variables` to process the raw data and `set_ploptions` to initialize the component `plot_manager` attributes (e.g., `.br`, `.bt`).
    *   **If Global Instance Has Data:**
        *   Processes the incoming `raw_data_object` into structured NumPy arrays (`new_times`, `new_raw_data`) using a *temporary* instance of the correct class type (leveraging its `calculate_variables` method).
        *   Calls the refactored `data_cubby._merge_arrays(existing_times, existing_raw_data, new_times, new_raw_data)`. This function now takes and returns arrays, performing the comparison and merge (currently handles non-overlapping cases via concatenation and stable sorting).
        *   If `_merge_arrays` returns successfully merged arrays, `update_global_instance` **directly updates** the `global_instance.datetime_array` and `global_instance.raw_data` attributes.
        *   **Crucially**, it then calls `global_instance.set_ploptions()`. This re-initializes all the component `plot_manager` attributes (e.g., `mag_rtn_4sa.br`) using the *newly updated/merged* main arrays residing on the `global_instance`.
4.  **Tracker Update:** `get_data` updates the `DataTracker` only *after* `update_global_instance` reports success.
5.  **Cleanup:** Removed the redundant `data_cubby.stash(self, ...)` calls from the `update()` methods within the specific data classes (`psp_mag_classes.py`, `psp_proton_classes.py`, `psp_electron_classes.py`) as the cubby now manages the storage lifecycle via `update_global_instance`.

**Expected Outcome:** This architecture ensures that data merging happens correctly by comparing new processed data against existing data *before* modifying the global instance. The `set_ploptions()` call after a successful merge guarantees that component attributes used by `multiplot` (like `mag_rtn_4sa.br.data`) reflect the up-to-date, merged data stored in the main global instance arrays.

**Clarification on `set_ploptions()` Role:**
*   `set_ploptions()` is **not** a `plot_manager` or `DataCubby` function. It is a method defined **within each specific data class** (e.g., `mag_rtn_4sa_class` in `psp_mag_classes.py`).
*   It is called by `DataCubby.update_global_instance` **after** the main data arrays (`global_instance.datetime_array`, `global_instance.raw_data`) have been updated (either initially or via merge).
*   Its primary purpose is to **re-initialize the component attributes** (e.g., `self.br`, `self.vt`) on the data class instance. It does this by creating *new* `plot_manager` instances for each component, passing them references to the correct subset of the *now-updated* main data arrays held within the global instance.
*   This ensures that accessing `mag_rtn_4sa.br` after an update/merge correctly retrieves the `plot_manager` containing the latest data.

**Simplified Flowcharts:**

**Chart 1: `get_data` Logic Flow**

```text
[ get_data(trange, var) ]
          |
          v
[ Needs Refresh? (Tracker + Cubby Check) ] 
          |         |
        (Yes)      (No)
          |         |
          v         v
[ import_data() ]  [ Use Existing Data ]
          |
          v
[ raw_data_obj ]
          |
          v
[ data_cubby.update_global_instance(type, raw_data_obj) ] --> To Chart 2
          |
          v
[ Update Succeeded? ]
          |         |
        (Yes)      (No)
          |         |
          v         v
[ Update Tracker ] [ Log Warning ]
```

**Chart 2: `DataCubby.update_global_instance` Internal Logic**

```text
[ update_global_instance(type, raw_data_obj) ] <-- From Chart 1
          |
          v
[ Grab Existing global_instance ]
          |
          v
[ Instance Empty? ]
          |         |
        (Yes)      (No)
          |         |
          v         v (Instance Has Data)
[ global_instance.update(raw_data_obj) ]      [ Create temp_instance ]
          |                                         |
          v (Inside .update())                      v
[ instance.calculate_variables() ]      [ temp_instance.calculate_variables(raw_data_obj) ]
          |                                         |
          v                                         v (Get new_times, new_raw_data)
[ instance.set_ploptions() ]                      |
          |                                         |
          v                                         v
[ Return Success ]                      [ _merge_arrays(global.data, new.data) ]
                                                  |
                                                  v
                                            [ merged_data? ]
                                                  |         |
                                                (Yes)      (No: Contained/Identical/Error)
                                                  |         |
                                                  v         v
                           [ Update global_instance arrays ]   [ Log Info / No Action ]
                                                  |
                                                  v
                                  [ global_instance.set_ploptions() ]
                                                  |
                                                  v
                                          [ Return Success ]
``` 

### 2. Clarification: Data Location, Plot Managers, and the Cubby

**Confusion Point:** It can be unclear where the data "lives" and how the `DataCubby`, global data instances (like `mag_rtn_4sa`), and `plot_manager` instances interact.

**Resolution & Structure:**

1.  **Where the Data Arrays Live:** The primary, complete, and potentially merged NumPy arrays for time (`.datetime_array`) and data components (`.raw_data` dictionary) reside **directly on the global data class instances** (e.g., the single `mag_rtn_4sa` object created at the module level in `psp_mag_classes.py`). Think of `mag_rtn_4sa` as the central data container for that specific data type.

2.  **Where `plot_manager` Instances Live:** The instances of the `plot_manager` class (which are *not* global themselves) exist as **attributes** on these global data class instances. For example:
    *   `mag_rtn_4sa.br` *is* a `plot_manager` instance.
    *   `proton.vt` *is* a different `plot_manager` instance.

3.  **What `plot_manager` Instances Hold:** A specific `plot_manager` instance (like `mag_rtn_4sa.br`) **does not store a copy of the data**. Instead, it holds:
    *   A **reference** pointing back to the relevant data array within the global instance's `.raw_data` dictionary (e.g., points to `mag_rtn_4sa.raw_data['br']`).
    *   A **reference** to the global instance's main `.datetime_array`.
    *   The specific plotting configuration (`ploptions`) for that component (color, labels, etc.).

4.  **The Role of `set_ploptions()`:** This method, defined *within* each data class (like `mag_rtn_4sa_class`), is called by the `DataCubby` after the global instance's main data arrays are updated. It **re-creates** the component attributes (like `.br`, `.vt`) as *new* `plot_manager` instances, ensuring their internal references point correctly to the latest data arrays on the global instance.

5.  **`DataCubby` Role (Registry/Facade):** The `DataCubby` does not hold the primary data. It acts as:
    *   A **Registry** to find the *single, global instances* (like `mag_rtn_4sa`) via `grab()`.
    *   A **Facade/Orchestrator** via `update_global_instance()` to manage the process of updating/merging data *onto* those global instances and triggering the `set_ploptions()` refresh.

**Design Pattern Analogy:**
*   Global Instances (`mag_rtn_4sa`, `proton`): Act like **Singletons** within the package.
*   `DataCubby`: Acts like a **Registry** + **Facade**.
*   `plot_manager` attributes on global instances: Use **Composition**.

This structure centralizes the master data on the global instances while using `plot_manager` attributes as configured access points, all managed by the `DataCubby`.

### 3. Exploration: Alternative Naming Conventions

We discussed potential alternative names for the core data handling and plotting components to improve clarity:

**Option 1: Focusing on Registry & Configuration**
*   `DataCubby` -> `DataRegistry` or `GlobalInstanceRegistry` (Emphasizes lookup)
*   `plot_manager` -> `PlotConfig` or `TraceConfig` (Emphasizes holding plot settings)
*   `set_ploptions` (method) -> `refresh_plot_configs` or `initialize_plot_configs` (Emphasizes recreating configs)
*   Data Class (Concept) -> `TimeSeriesData` or `InstrumentData` (Emphasizes data container role)

**Option 2: Focusing on Coordination & Views**
*   `DataCubby` -> `DataCoordinator` or `DataSourceManager` (Emphasizes orchestrating updates)
*   `plot_manager` -> `PlotView` or `ComponentPlotView` (Emphasizes providing a view onto data)
*   `set_ploptions` (method) -> `update_plot_views` or `sync_plot_views` (Emphasizes updating views)
*   Data Class (Concept) -> `DataSource` or `DataContainer` (Emphasizes representing a source)

No immediate changes were made, but this exploration helps clarify the roles of these components.

### 4. Feature Rollout & Refinement: Snapshot Loading & Data Persistence

*   **New Feature Implemented:** Successfully implemented and validated the data snapshot saving (`save_data_snapshot`) and loading (`load_data_snapshot`) functionality. The system can now reliably serialize the state of loaded data classes to `.pkl` files and restore them later.
*   **Core Logic Refinement:** Ensured the `get_data` function correctly interacts with the `DataTracker` and `DataCubby` after a snapshot is loaded.
    *   **Validation:** Confirmed that loading a snapshot correctly populates the `DataTracker`.
    *   **Integration Fix:** Corrected logic in `get_data` (changed `if needs_import or calculation_needed:` to `if calculation_needed:`) to ensure it respects the state reported by the `DataTracker` after a snapshot load, preventing unnecessary re-downloads/imports.
*   **Naming Consistency:** Resolved an internal naming inconsistency for EPAD data (`spe_sf0_pad` vs. `epad`). Implemented mapping within `get_data` to ensure the canonical key (`epad`/`epad_hr`) is consistently used for `DataTracker` and `DataCubby` interactions, while preserving the original name for download configuration lookups. This was crucial for the snapshot loading feature to work seamlessly with EPAD data.
*   **Configuration:** Added `data_snapshots/` directory to `.gitignore` to prevent committing large snapshot files.
*   **User Experience:** Added a user-facing status message (`print_manager.status`) with a 🚀 emoji to `load_data_snapshot` for clearer feedback on successful loading, including filename and processed keys.
*   **Minor Fixes:** Removed potentially unintended extra whitespace from a print statement in `data_tracker.py`. Identified and discussed the intentional use of `print_manager.status(" ")` for spacing in `plotbot_main.py`.
*   **Type Hinting:** Updated `print_manager.pyi` and `data_snapshot.pyi` stub files with new attributes/functions (`show_data_snapshot`, `load_data_snapshot`) related to these features.

## Issue Observed: Multiplot Rendering Anomaly (2025-05-05)

*   **Observation:** When using `multiplot`, particularly with positional x-axis mapping (e.g., R-Sun), some panels appear to render without the expected data lines, even though the preceding log messages indicate successful data loading and processing for the corresponding time ranges.
*   **Initial Suspicion:** Potential misalignment between the time-clipped data indices and the mapped positional x-axis values during the plotting stage in `multiplot.py`.
*   **Next Steps:** Investigate the data flow within the `multiplot` function's main plotting loop, specifically how positional `x_data` is generated and aligned with the `y_data` from the variable. 