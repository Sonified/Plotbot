import pytest
import cdflib
import numpy as np
import pandas as pd
import copy
from datetime import datetime

# --- Configuration ---
CDF_FILE_PATH = "/Users/robertalexander/GitHub/Plotbot/psp_data/sweap/spi_fits/sf00/p2/v00/2024/spp_swp_spi_sf00_fits_2024-04-01_v00.cdf"
NUM_ITERATIONS = 10 # Adjust as needed - not literally millions, but enough to stress test
VARIABLE_TIME = 'Epoch'
VARIABLE_DATA = 'n_tot'

# --- Mock Objects/Structures ---

# Simulate the main data class instance (like proton_fits)
class MockDataClass:
    def __init__(self, name):
        self.name = name
        self.datetime_array = None
        self.raw_data = {VARIABLE_DATA: None}
        self._plot_state = {} # Simulate plot state storage
        print(f"[{self.name}] MockDataClass Initialized (id={id(self)})")

    def calculate_variables(self, cdf_file, time_var, data_var):
        print(f"[{self.name}] Running calculate_variables...")
        try:
            times_raw = cdf_file.varget(time_var)
            data_raw = cdf_file.varget(data_var)
            print(f"  Raw times type: {type(times_raw)}, shape: {getattr(times_raw, 'shape', 'N/A')}")
            print(f"  Raw data type: {type(data_raw)}, shape: {getattr(data_raw, 'shape', 'N/A')}")

            if times_raw is None:
                print("  ERROR: Raw times are None!")
                return False

            # --- Time Conversion (Crucial Step) ---
            print(f"  Attempting time conversion: cdflib.cdfepoch.to_datetime...")
            datetime_list = cdflib.cdfepoch.to_datetime(times_raw)
            print(f"    to_datetime output type: {type(datetime_list)}, len: {len(datetime_list) if isinstance(datetime_list, list) else 'N/A'}")

            print(f"  Attempting time conversion: np.array(..., dtype='datetime64[ns]')...")
            try:
                # The conversion method we suspect is needed
                self.datetime_array = np.array(datetime_list, dtype='datetime64[ns]')
                print(f"    SUCCESS: np.array dtype={self.datetime_array.dtype}, shape={self.datetime_array.shape}")
                print(f"    First 3 values: {self.datetime_array[:3]}")
            except Exception as e:
                print(f"    FAILED np.array conversion: {e}")
                # Fallback or alternative conversion for comparison
                try:
                    print(f"    Attempting fallback: pd.to_datetime -> .to_numpy()")
                    pd_dt = pd.to_datetime(datetime_list)
                    self.datetime_array = pd_dt.to_numpy()
                    print(f"    Fallback SUCCESS: dtype={self.datetime_array.dtype}, shape={self.datetime_array.shape}")
                except Exception as e_alt:
                    print(f"    Fallback FAILED: {e_alt}")
                    self.datetime_array = None
                    return False

            # --- Data Assignment ---
            self.raw_data[data_var] = data_raw
            print(f"  Assigned raw_data['{data_var}'] shape: {getattr(self.raw_data[data_var], 'shape', 'N/A')}")
            
            # Simulate setting initial plot state based on calculated data
            self._plot_state['datetime_array'] = self.datetime_array
            self._plot_state['data'] = self.raw_data[data_var]
            print(f"  Set initial _plot_state (datetime_array id={id(self._plot_state.get('datetime_array'))}, data id={id(self._plot_state.get('data'))})")


            return True
        except Exception as e:
            print(f"  ERROR in calculate_variables: {e}")
            return False

    def update(self, cdf_file, time_var, data_var, restore_logic='skip_datetime'):
        """Simulates the update process including state restoration"""
        print(f"[{self.name}] Running update (restore_logic='{restore_logic}')...")
        
        # 1. Store current state (simulate storing potentially "old" or initial state)
        # In a real scenario, this might happen before calculate_variables
        # Here we simulate storing the state *before* this specific update call
        # Let's create a plausible "old" state where datetime_array might be None initially
        old_state_to_restore = copy.deepcopy(self._plot_state) if self._plot_state else {'datetime_array': None, 'data': None, 'some_other_option': 'value1'}
        print(f"  Simulating OLD state to restore: { {k: type(v) for k, v in old_state_to_restore.items()} }")
        print(f"  OLD state datetime_array is None: {old_state_to_restore.get('datetime_array') is None}")
        
        # 2. Calculate new variables (overwrites self.datetime_array, self.raw_data)
        print(f"  Calling calculate_variables within update...")
        calc_success = self.calculate_variables(cdf_file, time_var, data_var)
        if not calc_success:
            print("  Update failed during calculate_variables.")
            return False
        
        print(f"  AFTER calculate_variables in update: self.datetime_array id={id(self.datetime_array)}, len={len(self.datetime_array) if self.datetime_array is not None else 'None'}")

        # 3. Simulate State Restoration (The other crucial step)
        print(f"  Simulating state restoration using logic: '{restore_logic}'...")
        if restore_logic == 'skip_datetime':
            print("    Restoring state, EXCLUDING datetime_array...")
            state_copy = dict(old_state_to_restore)
            if 'datetime_array' in state_copy:
                del state_copy['datetime_array'] # Remove from copy
            self._plot_state.update(state_copy) # Update with modified copy
            # Restore individual OTHER attributes (already skipped datetime in update above)
            for attr, value in old_state_to_restore.items():
                 if attr != 'datetime_array':
                      self._plot_state[attr] = value # Simple dict update simulation
        elif restore_logic == 'restore_all':
             print("    Restoring state, INCLUDING datetime_array...")
             self._plot_state.update(old_state_to_restore) # Blindly restore everything
        else: # 'none' or other
            print("    Skipping state restoration.")
            
        print(f"  AFTER state restoration: self._plot_state keys: {list(self._plot_state.keys())}")
        restored_dt = self._plot_state.get('datetime_array')
        print(f"  AFTER state restoration: _plot_state['datetime_array'] id={id(restored_dt)}, is None={restored_dt is None}, len={len(restored_dt) if restored_dt is not None else 'N/A'}")
        print(f"  AFTER state restoration: Is _plot_state['datetime_array'] SAME OBJECT as self.datetime_array? {restored_dt is self.datetime_array}")

        return True


# Simulate Data Cubby
class MockDataCubby:
    def __init__(self):
        self._storage = {}
        print("[DataCubby] Initialized.")

    def stash(self, obj, key, use_deepcopy=False):
        print(f"[DataCubby] Stashing object id={id(obj)} under key='{key}' (deepcopy={use_deepcopy})")
        if use_deepcopy:
            self._storage[key] = copy.deepcopy(obj)
            print(f"  Stashed DEEP COPY id={id(self._storage[key])}")
        else:
            self._storage[key] = obj # Store reference
            print(f"  Stashed REFERENCE id={id(self._storage[key])}")


    def grab(self, key):
        print(f"[DataCubby] Grabbing key='{key}'")
        obj = self._storage.get(key)
        if obj:
             print(f"  Retrieved object id={id(obj)}")
        else:
             print(f"  Key '{key}' not found!")
        return obj

    def clear(self):
        print("[DataCubby] Clearing storage.")
        self._storage = {}

# --- Test Function ---

def run_massive_test(iteration, cubby, restore_logic, use_deepcopy_stash):
    print(f"\n{'='*10} Iteration {iteration}/{NUM_ITERATIONS} (restore='{restore_logic}', deepcopy={use_deepcopy_stash}) {'='*10}")

    # --- 1. Load CDF ---
    print("\n--- Phase 1: Load CDF ---")
    try:
        cdf = cdflib.CDF(CDF_FILE_PATH)
        print(f"Successfully loaded CDF: {CDF_FILE_PATH}")
        epoch_info = cdf.varinq(VARIABLE_TIME)
        ntot_info = cdf.varinq(VARIABLE_DATA)
        print(f"Var '{VARIABLE_TIME}' Info: {epoch_info}")
        print(f"Var '{VARIABLE_DATA}' Info: {ntot_info}")
    except Exception as e:
        print(f"FATAL: Could not load CDF file: {e}")
        pytest.fail(f"Iteration {iteration}: Failed to load CDF.")
        return # Stop this iteration

    # --- 2. Initial Data Processing ---
    print("\n--- Phase 2: Initial Processing & Stash ---")
    mock_instance = MockDataClass(f"Instance_Iter{iteration}")
    calc_success = mock_instance.calculate_variables(cdf, VARIABLE_TIME, VARIABLE_DATA)
    if not calc_success:
         pytest.fail(f"Iteration {iteration}: Initial calculate_variables failed.")
         return

    # Initial check
    assert mock_instance.datetime_array is not None, f"Iter {iteration}: datetime_array is None after initial calc!"
    assert len(mock_instance.datetime_array) > 0, f"Iter {iteration}: datetime_array is empty after initial calc!"
    assert mock_instance.raw_data[VARIABLE_DATA] is not None, f"Iter {iteration}: n_tot is None after initial calc!"
    print("Initial calculation checks PASSED.")

    cubby.stash(mock_instance, f"test_key_{iteration}", use_deepcopy=use_deepcopy_stash)

    # --- 3. Grab and Simulate Update ---
    print("\n--- Phase 3: Grab and Simulate Update/Restore ---")
    grabbed_instance = cubby.grab(f"test_key_{iteration}")
    if grabbed_instance is None:
        pytest.fail(f"Iteration {iteration}: Failed to grab instance from cubby.")
        return
        
    print(f"Grabbed instance id={id(grabbed_instance)}")
    print(f"Is grabbed instance SAME OBJECT as original? {grabbed_instance is mock_instance}")

    # Simulate an update call on the grabbed instance
    update_success = grabbed_instance.update(cdf, VARIABLE_TIME, VARIABLE_DATA, restore_logic=restore_logic)
    if not update_success:
         pytest.fail(f"Iteration {iteration}: Update simulation failed (restore='{restore_logic}').")
         return
         
    # --- 4. Final Checks (Crucial) ---
    print("\n--- Phase 4: Final Checks ---")
    final_dt_array = grabbed_instance._plot_state.get('datetime_array')
    final_data = grabbed_instance._plot_state.get('data')

    print(f"Final check on grabbed_instance (id={id(grabbed_instance)}) _plot_state:")
    print(f"  _plot_state['datetime_array'] id = {id(final_dt_array)}")
    print(f"  _plot_state['datetime_array'] is None = {final_dt_array is None}")
    print(f"  _plot_state['datetime_array'] len = {len(final_dt_array) if final_dt_array is not None else 'N/A'}")
    print(f"  _plot_state['data'] id = {id(final_data)}")
    print(f"  _plot_state['data'] is None = {final_data is None}")
    print(f"  _plot_state['data'] shape = {getattr(final_data, 'shape', 'N/A')}")
    
    # THE KEY ASSERTION based on our problem: datetime_array should exist and be populated *after* update/restore
    assert final_dt_array is not None, f"Iter {iteration} (restore='{restore_logic}', deepcopy={use_deepcopy_stash}): Final datetime_array in _plot_state is None!"
    assert len(final_dt_array) > 0, f"Iter {iteration} (restore='{restore_logic}', deepcopy={use_deepcopy_stash}): Final datetime_array in _plot_state is empty!"
    # Also check data for good measure
    assert final_data is not None, f"Iter {iteration} (restore='{restore_logic}', deepcopy={use_deepcopy_stash}): Final data in _plot_state is None!"

    print(f"Iteration {iteration} PASSED.")


# --- Pytest Execution ---

# Create a single cubby instance for all tests
mock_cubby = MockDataCubby()

# Define different test cases using parametrize for different scenarios
@pytest.mark.parametrize("restore_logic", ['skip_datetime', 'restore_all', 'none'])
@pytest.mark.parametrize("use_deepcopy_stash", [False, True])
def test_combinations(restore_logic, use_deepcopy_stash):
    """Runs the massive test multiple times for different configurations."""
    for i in range(1, NUM_ITERATIONS + 1):
         mock_cubby.clear() # Clear cubby for each iteration to ensure isolation
         run_massive_test(i, mock_cubby, restore_logic, use_deepcopy_stash) 