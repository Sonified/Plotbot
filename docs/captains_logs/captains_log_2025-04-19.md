# Captain's Log - 2025-04-19

## Log Entries:

- **GitHub Push:**
  - Version: `2025_04_19_v1.00`
  - Commit Message: "Debug proton time range updates and data cubby merge logic."

- **Testing Time Range Merging Issue:**
  - Preparing to run `test_two_call_incorrect_merged_trange` in `tests/test_proton_trange_updates.py`.
  - **Objective:** Observe the `trange` parameter received by the `get_data` function (and subsequently by data download functions) during the second `plotbot` call. The second call plots `proton.sun_dist_rsun` and `mag_rtn_4sa.br_norm` for `TRANGE2_STR` after an initial call for `TRANGE1_STR`.
  - A temporary debug flag (`DEBUG_FORCE_STOP_IN_GET_DATA_CALL2`) is used in the test and `plotbot/get_data.py` to ensure `get_data` returns `None` during the problematic part of the second call. This facilitates full log capture by `capsys` by preventing premature test termination due to large download attempts.
  - Updated `plotbot/data_classes/psp_mag_rtn_4sa.pyi` to include `br_norm: plot_manager` for type hinting.

- **Deep Dive into `mag_rtn_4sa.br_norm` Time Range Issue in Multi-Call Scenarios:**
  - **Scenario:** When `plotbot` is called twice with different time ranges (e.g., `TRANGE1_STR` then `TRANGE2_STR`).
  - **Observed Problem:** During the second call (for `TRANGE2_STR`), the `mag_rtn_4sa.br_norm` component is not correctly reflecting `TRANGE2_STR`, leading to it not plotting or plotting incorrect data.
  - **Root Cause Analysis:**
    - When `mag_rtn_4sa.br_norm` is first accessed as a property during the second call, its parent `mag_rtn_4sa` object (retrieved from `DataCubby`) still holds the data from the first call (`TRANGE1_STR`).
    - This triggers the `_calculate_br_norm()` method. Inside this method, an internal `trange` is derived from the parent's `datetime_array` (which is currently `TRANGE1_STR`'s data). This internal `trange` is then used to call `get_data` for dependencies like `proton.sun_dist_rsun`.
    - Consequently, the `br_norm` data is calculated using `TRANGE1_STR` data and cached within `_br_norm_manager`.
    - Later in the second call, the main `get_data` process correctly updates the parent `mag_rtn_4sa` object in `DataCubby` to include/merge data for `TRANGE2_STR`.
    - However, when `mag_rtn_4sa.br_norm` is accessed again for plotting, the existing `_br_norm_manager` (still holding `TRANGE1_STR`-based data) is returned because the property logic does not currently detect that its cached data is stale relative to the updated parent object and the new plotting request for `TRANGE2_STR`.
  - **Evidence ("Smoking Gun"):** Log entries from `_calculate_br_norm` (specifically the `[BR_NORM_DEBUG] Created trange: [...]` print, which uses `print_manager.dependency_management`) show that during the *second* `plotbot` call, this internal `trange` is initially derived from the *first* call's time range. For `TRANGE1_STR = ['2023-09-28/...', ...]` and `TRANGE2_STR = ['2023-09-26/...', ...]`, we observed `[BR_NORM_DEBUG] Created trange: ['2023-09-28/00:00:00.140447', '2023-09-28/23:59:59.930447']` during the initial phase of the second call.
  - **Impact:** The `get_data` call made *by `_calculate_br_norm`* uses an incorrect time range based on the stale parent data, leading to `br_norm` being calculated with the wrong context. This incorrect `br_norm` is then used for plotting in the second call.

  - **Refined Understanding & Solution Path (2025-04-19 Evening):**
    - **Core Problem Confirmed:** The fundamental issue is that `_calculate_br_norm` (triggered by accessing the `br_norm` property) derives the time range for its dependencies (specifically `proton.sun_dist_rsun`) from its parent `mag_rtn_4sa` object's `datetime_array`. If this parent object is stale (e.g., holding data from `TRANGE1` when `TRANGE2` is being processed), `br_norm` is calculated using incorrect dependency data.
    - **Addressing the Stale Dependency Time Range:**
      - The `mag_rtn_4sa_class` needs to be explicitly informed of the *current plot request's time range* when `br_norm` is about to be calculated.
      - A new method, tentatively `set_current_plot_request_trange(self, trange)`, will be added to `mag_rtn_4sa_class`. This method will be called by the data retrieval or plotting logic before `br_norm` is accessed.
      - The `br_norm` property will use this stored "current request trange" to instruct `_calculate_br_norm`.
      - `_calculate_br_norm` will be modified to accept this `dependency_trange` and use it for its call to `get_data` for `proton.sun_dist_rsun`.
    - **Integration with DataTracker/DataCubby:** This approach ensures `br_norm`'s *internal calculation* is correct. How this interacts with `DataTracker` for caching `br_norm` itself, or how `DataCubby` merges `br_norm` data if it's modified, are subsequent considerations once the primary calculation integrity is restored. The immediate fix focuses on `_calculate_br_norm` fetching correct dependencies.
    - **Implication:** Code that orchestrates data fetching and component access (likely in `get_data.py` or `plot_manager.py`) will need to be modified to call the new `set_current_plot_request_trange` method on `mag_rtn_4sa` instances prior to accessing `br_norm`.

  - **Corrected Refined Understanding (2025-04-19 Late Evening - per Robert's guidance):**
    - **Core Insight:** The `mag_rtn_4sa_class.calculate_variables(self, imported_data)` method already correctly processes `imported_data` and sets `self.datetime_array` based on `imported_data.times`. This `self.datetime_array` accurately reflects the time range of the data just loaded/updated for the main `mag_rtn_4sa` object.
    - **The `br_norm` Property's Role:** The `br_norm` property needs to calculate its value using its parent's `self.datetime_array` as the basis for its dependency's (`proton.sun_dist_rsun`) time range. 
    - **Staleness and Recalculation:** The main challenge is ensuring `br_norm` recalculates when its parent `mag_rtn_4sa` object is updated (i.e., when `calculate_variables` has run with new `imported_data`). If the parent's `self.datetime_array` (or underlying `self.raw_data['br']`) changes, the cached `_br_norm_manager` becomes stale.
    - **Solution Path - Leveraging Existing Parent State:**
      1. When `mag_rtn_4sa_class.update()` (or a similar refresh mechanism like initial load via `__init__` followed by `calculate_variables`) completes, any cached `_br_norm_manager` should be invalidated (e.g., set to `None`).
      2. When the `@property def br_norm(self)` is subsequently accessed:
         - It checks if `_br_norm_manager` is invalid/stale.
         - If so, it calls `_calculate_br_norm()`.
         - `_calculate_br_norm()` will derive the `trange` for its `get_data(trange, proton.sun_dist_rsun)` call directly from the *current* `self.datetime_array` of its parent `mag_rtn_4sa` object. Since this `datetime_array` would have been recently updated by `calculate_variables`, it provides the correct time context for the `proton` dependency.
         - The `_br_norm_manager` is then populated with the newly calculated data.
    - **No Need for Explicit `dependency_trange` Parameter:** This approach means `_calculate_br_norm` does not need a special `dependency_trange` parameter passed to it. It inherently uses the (correctly updated) state of its parent object.

  - **Definitive Solution Path (2025-04-19 Night - Major Refinement): Treat `sun_dist_rsun` and `br_norm` as distinct, derived data types.**
    - **Core Problem:** The complexity arises from `br_norm` being a property within `mag_rtn_4sa_class` trying to manage its own dependencies (`proton.sun_dist_rsun`) and time context, which can conflict with the parent object's state and bypass `DataCubby`/`DataTracker` for `br_norm` itself.
    - **Solution: Elevate to First-Class Data Types:**
      1. **`psp_solar_distance` (New Derived Data Type):**
         - Defined in `psp_data_types.py` with a dependency on the primary proton data type (e.g., `spi_sf00_l3_mom`).
         - A new class (e.g., `PspSolarDistanceCalculator`) will have a `calculate_variables(self, imported_proton_data)` method to extract/calculate `sun_dist_rsun` and its `datetime_array`.
         - `get_data` will fetch the proton data, then call this calculator. The result is stashed in `DataCubby` and tracked by `DataTracker`.
      2. **`psp_br_norm_calculated` (New Derived Data Type):**
         - Defined in `psp_data_types.py` with dependencies on `mag_RTN_4sa` (for `br`) and the new `psp_solar_distance` type.
    - **Correction (2025-04-19 Late Night - per Robert's clarification):** `sun_dist_rsun` does NOT need to be its own top-level derived data type. It is calculated directly within `proton_class.calculate_variables()` and shares the proton object's time context. The refactor only needs to address `br_norm`.
    - **Revised Solution: Elevate `br_norm` to a First-Class Derived Data Type:**
      1. **`psp_br_norm_calculated` (New Derived Data Type):**
         - Defined in `psp_data_types.py`. Its dependencies will be `mag_RTN_4sa` (to get `Br` data) and the relevant primary proton data type (e.g., `spi_sf00_l3_mom`, to get `sun_dist_rsun` data).
         - A new class (e.g., `PspBrNormCalculator`) will have `calculate_variables(self, imported_mag_data, imported_proton_data)`.
         - This method will: extract `Br` and `mag_datetime_array` from `imported_mag_data`; extract `sun_dist_rsun` and `proton_datetime_array` from `imported_proton_data`; perform interpolation of `sun_dist_rsun` onto `mag_datetime_array`; calculate `br_norm`; and store the result with its own `datetime_array` (which would be the `mag_datetime_array`).
         - `get_data` will orchestrate fetching `mag_RTN_4sa` and the proton data for the target time range, then call the `PspBrNormCalculator`. The result is stashed in `DataCubby` and tracked by `DataTracker`.
    - **Advantages:**
      - Leverages the full power and correctness of `get_data`, `DataCubby`, and `DataTracker` for `br_norm` and its dependencies.
      - Ensures correct time context for all calculations.
      - Simplifies `mag_rtn_4sa_class` by removing `br_norm` property logic.
      - Clear, explicit dependency management handled by `get_data`.
    - **Implementation Steps:**
      - Update `psp_data_types.py`.
      - Create the new data calculation classes (`PspSolarDistanceCalculator`, `PspBrNormCalculator`).
      - Create the new data calculation class (`PspBrNormCalculator`).
      - Extend `get_data.py` to handle derived data types and their dependencies.

- **GitHub Push (Pre-Refactor Planning):**
  - Version: `2025_05_18_v2.42`
  - Commit Message: "Refactor br_norm: Plan to make br_norm a derived data type."
  - Details: Pushing the comprehensive discussion and decision to refactor `br_norm` handling by treating it as a distinct, derived data type. This includes updates to the captain's log detailing the refined approach. No functional code changes for `br_norm` are included in this push, only the planning and version increment.

- **Update plotting calls to use the new `psp_br_norm_calculated` type.**

- **Plan for `PspBrNormCalculator` and `get_data` for Dependencies (2025-04-19 Night):**
  - **`PspBrNormCalculator` Structure (`plotbot/data_classes/psp_br_norm.py`):**
    - `__init__(self, imported_data_bundle=None)`: If `imported_data_bundle` is provided, calls `self.calculate_variables()`.
    - `calculate_variables(self, imported_data_bundle)`:
      - Receives a dictionary `imported_data_bundle` (e.g., `{'mag_input': mag_object, 'proton_input': proton_object}`).
      - Extracts `Br` and `mag_datetime_array` from `imported_data_bundle['mag_input']`.
      - Extracts `sun_dist_rsun` and `proton_datetime_array` from `imported_data_bundle['proton_input']`.
      - Performs interpolation of `sun_dist_rsun` (from proton data) onto `mag_datetime_array`.
      - Calculates `br_norm`.
      - Sets `self.raw_data = {'br_norm': calculated_br_norm_array}`.
      - Sets `self.datetime_array` (based on `mag_datetime_array`).
      - Sets `self.time` (TT2000 of `self.datetime_array`).
    - Initializes `class_name = 'PspBrNormCalculator'`, `data_type = 'psp_br_norm_calculated'`.
    - Implements `set_ploptions()` for direct plotting of `br_norm`.
  - **`get_data.py` Logic for `has_dependencies: True`:**
    - When a requested `data_type` has `has_dependencies: True`:
      1. `get_data` looks up the `dependencies` dictionary in `psp_data_types.py`.
      2. For each dependency listed (e.g., `'mag_RTN_4sa'`, `'spi_sf00_l3_mom'`), `get_data` recursively calls itself to fetch/load that dependency for the same target `trange`.
      3. The fetched dependency objects are collected into a `dependency_bundle` dictionary, keyed by the keys specified in the `dependencies` entry (e.g., `'mag_input'`, `'proton_input'`).
      4. `get_data` then instantiates the specified `class_name` (e.g., `PspBrNormCalculator`).
      5. It calls the calculator's `calculate_variables(dependency_bundle)` method.
      6. The populated calculator instance is then stashed in `DataCubby` and returned.

