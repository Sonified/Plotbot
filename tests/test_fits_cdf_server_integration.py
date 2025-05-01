import pytest
import cdflib
import pandas as pd
from pathlib import Path
import os

# Define paths relative to the test file location or project root
# Assuming tests run from project root
TEST_DATA_DIR = Path(__file__).parent / 'test_data'
CDF_DIR = TEST_DATA_DIR / 'psp_cdf_fits'
LOCAL_CSV_DIR_BASE = Path('psp_data/sweap/spi_fits') # Relative to project root

# Example CDF files (Manually added by user)
CDF_SF00_FILE = CDF_DIR / 'spp_swp_spi_sf00_fits_2024-04-01_v00.cdf'
CDF_SF01_FILE = CDF_DIR / 'spp_swp_spi_sf01_fits_2024-04-01_v00.cdf'

# Example local CSV files (adjust date/path as needed)
# Using the 2024-09-30 files we found
LOCAL_CSV_SF00_FILE = LOCAL_CSV_DIR_BASE / 'sf00/p2/v00/2024/09/spp_swp_spi_sf00_2024-09-30_v00.csv'
LOCAL_CSV_SF01_FILE = LOCAL_CSV_DIR_BASE / 'sf01/p3/v00/2024/09/spp_swp_spi_sf01_2024-09-30_v00.csv'

# Reinstated skipif checks for CDF files
@pytest.mark.skipif(not CDF_SF00_FILE.exists(), reason=f"Test CDF file not found: {CDF_SF00_FILE}")
@pytest.mark.skipif(not CDF_SF01_FILE.exists(), reason=f"Test CDF file not found: {CDF_SF01_FILE}")
@pytest.mark.skipif(not LOCAL_CSV_SF00_FILE.exists(), reason=f"Test CSV file not found: {LOCAL_CSV_SF00_FILE}")
@pytest.mark.skipif(not LOCAL_CSV_SF01_FILE.exists(), reason=f"Test CSV file not found: {LOCAL_CSV_SF01_FILE}")
class TestFitsCdfIntegration:

    def test_placeholder(self):
        """Placeholder test to ensure the file runs."""
        assert True

    def test_compare_cdf_csv_variables(self):
        """Compares variable names from manually added CDFs and column headers from local CSVs."""
        print("\n--- Comparing SF00 Variables ---")
        
        # Read SF00 CDF Variables
        try:
            cdf_sf00 = cdflib.CDF(CDF_SF00_FILE)
            cdf_sf00_vars = list(cdf_sf00.cdf_info().zVariables) + list(cdf_sf00.cdf_info().rVariables)
            print(f"CDF SF00 Variables ({len(cdf_sf00_vars)}):\n{sorted(cdf_sf00_vars)}")
        except Exception as e:
            pytest.fail(f"Failed to read SF00 CDF variables from {CDF_SF00_FILE}: {e}")

        # Read SF00 CSV Headers
        try:
            csv_sf00_headers = pd.read_csv(LOCAL_CSV_SF00_FILE, nrows=0).columns.tolist()
            print(f"\nCSV SF00 Headers ({len(csv_sf00_headers)}):\n{sorted(csv_sf00_headers)}")
        except Exception as e:
            pytest.fail(f"Failed to read SF00 CSV headers: {e}")

        # --- Comparison for SF00 (Placeholder) ---
        # TODO: Add assertions later based on comparison
        print("\n[SF00 Comparison Pending]")
        
        print("\n\n--- Comparing SF01 Variables ---")
        
        # Read SF01 CDF Variables
        try:
            cdf_sf01 = cdflib.CDF(CDF_SF01_FILE)
            cdf_sf01_vars = list(cdf_sf01.cdf_info().zVariables) + list(cdf_sf01.cdf_info().rVariables)
            print(f"CDF SF01 Variables ({len(cdf_sf01_vars)}):\n{sorted(cdf_sf01_vars)}")
            
            # --- START TEMPORARY CODE TO INSPECT EPOCH vs EPOCH_1 ---
            print("\n--- Inspecting Epoch vs Epoch_1 ---")
            epoch_data = cdf_sf01.varget('Epoch')
            epoch1_data = cdf_sf01.varget('Epoch_1')
            
            if epoch_data is not None:
                print(f"Epoch (Type: {type(epoch_data)}, Shape: {epoch_data.shape}, DType: {epoch_data.dtype}):")
                print(f"  First 5 values: {epoch_data[:5]}")
                # Optional: Convert to datetime
                # epoch_dt = cdflib.cdfepoch.to_datetime(epoch_data[:5])
                # print(f"  First 5 datetimes: {epoch_dt}")
            else:
                print("Epoch data not found.")
                
            if epoch1_data is not None:
                print(f"\nEpoch_1 (Type: {type(epoch1_data)}, Shape: {epoch1_data.shape}, DType: {epoch1_data.dtype}):")
                print(f"  First 5 values: {epoch1_data[:5]}")
                # Optional: Convert to datetime
                # epoch1_dt = cdflib.cdfepoch.to_datetime(epoch1_data[:5])
                # print(f"  First 5 datetimes: {epoch1_dt}")
            else:
                print("Epoch_1 data not found.")
            print("--- END TEMPORARY CODE --- \n")
            # --- END TEMPORARY CODE ---
            
        except Exception as e:
            pytest.fail(f"Failed to read SF01 CDF variables from {CDF_SF01_FILE}: {e}")

        # Read SF01 CSV Headers
        try:
            csv_sf01_headers = pd.read_csv(LOCAL_CSV_SF01_FILE, nrows=0).columns.tolist()
            print(f"\nCSV SF01 Headers ({len(csv_sf01_headers)}):\n{sorted(csv_sf01_headers)}")
        except Exception as e:
            pytest.fail(f"Failed to read SF01 CSV headers: {e}")
            
        # --- Comparison for SF01 (Placeholder) ---
        # TODO: Add assertions later based on comparison
        print("\n[SF01 Comparison Pending]")

        # Keep test passing for now until we analyze output
        assert True 

    @pytest.mark.skipif(not CDF_SF00_FILE.exists(), reason=f"Test CDF file not found: {CDF_SF00_FILE}")
    def test_plotbot_with_sf00_cdf_variable(self):
        """Tests plotting a single variable directly from the sf00_fits CDF via plotbot."""
        print("\n--- Testing plotbot with sf00_fits CDF variable (proton_fits.n_tot) ---")
        
        # Need plotbot and the specific object instance
        from plotbot import plotbot as pb, proton_fits, plt
        from plotbot.test_pilot import phase, system_check
        from plotbot.config import config # Import config
        from plotbot.print_manager import print_manager # Import print_manager
        import numpy as np
        import cdflib # For examining CDF directly
        from plotbot.data_cubby import data_cubby

        print_manager.enable_debug() # <--- Enable debug logging

        # Add monkey patching to trace data flow
        original_grab = data_cubby.grab
        def traced_grab(identifier):
            result = original_grab(identifier)
            print(f"\n*** TRACE: data_cubby.grab('{identifier}') called ***")
            if result is not None:
                print(f"Result type: {type(result)}")
                if hasattr(result, 'datetime_array'):
                    print(f"datetime_array present: {result.datetime_array is not None}")
                    if result.datetime_array is not None:
                        print(f"datetime_array length: {len(result.datetime_array)}")
                        print(f"datetime_array type: {type(result.datetime_array)}")
                        print(f"First few values: {result.datetime_array[:3] if len(result.datetime_array) >= 3 else result.datetime_array}")
            else:
                print(f"Result is None")
            return result
        
        # Patch data_cubby.grab
        data_cubby.grab = traced_grab
        
        # Add direct examination of CDF file
        print("\n*** DIRECT EXAMINATION OF TEST CDF FILE ***")
        try:
            cdf = cdflib.CDF(CDF_SF00_FILE)
            epoch_data = cdf.varget('Epoch')
            print(f"CDF Epoch data type: {type(epoch_data)}")
            print(f"CDF Epoch data shape: {epoch_data.shape}")
            
            # Convert to datetime for comparison
            epoch_datetime = cdflib.cdfepoch.to_datetime(epoch_data)
            print(f"CDF datetime type: {type(epoch_datetime)}")
            print(f"CDF datetime first few: {epoch_datetime[:3]}")
            
            # Check n_tot
            n_tot = cdf.varget('n_tot')
            print(f"CDF n_tot shape: {n_tot.shape}")
            print(f"CDF n_tot first few: {n_tot[:3]}")
        except Exception as e:
            print(f"Error examining CDF directly: {e}")
            
        # Trace import_data_function
        from plotbot.data_import import import_data_function
        original_import_data = import_data_function
        def traced_import_data(*args, **kwargs):
            print(f"\n*** TRACE: import_data_function called with args={args}, kwargs={kwargs} ***")
            result = original_import_data(*args, **kwargs)
            print(f"import_data_function result type: {type(result)}")
            if hasattr(result, 'times'):
                print(f"Result has times attribute: {result.times is not None}")
                if result.times is not None:
                    print(f"times length: {len(result.times)}")
                    print(f"times type: {type(result.times)}")
                    print(f"times first few: {result.times[:3] if len(result.times) >= 3 else result.times}")
                    
            if hasattr(result, 'data'):
                print(f"Result has data attribute: {result.data is not None}")
                if isinstance(result.data, dict):
                    print(f"data keys: {list(result.data.keys())}")
                    if 'n_tot' in result.data:
                        print(f"n_tot in data: {result.data['n_tot'] is not None}")
                        if result.data['n_tot'] is not None:
                            print(f"n_tot length: {len(result.data['n_tot'])}")
                            print(f"n_tot first few: {result.data['n_tot'][:3] if len(result.data['n_tot']) >= 3 else result.data['n_tot']}")
            return result
            
        # Apply the patch
        import plotbot.data_import
        plotbot.data_import.import_data_function = traced_import_data
        
        # Trace proton_fits.update
        from plotbot.data_classes.psp_proton_fits_classes import proton_fits_class
        original_update = proton_fits_class.update
        def traced_update(self, imported_data):
            print(f"\n*** TRACE: proton_fits_class.update called ***")
            print(f"imported_data type: {type(imported_data)}")
            if hasattr(imported_data, 'times'):
                print(f"imported_data has times: {imported_data.times is not None}")
                print(f"times type: {type(imported_data.times)}")
                if imported_data.times is not None:
                    print(f"times length: {len(imported_data.times)}")
                    print(f"First few times: {imported_data.times[:3] if len(imported_data.times) >= 3 else imported_data.times}")
            
            if hasattr(imported_data, 'data'):
                print(f"imported_data has data: {imported_data.data is not None}")
                if isinstance(imported_data.data, dict):
                    print(f"data keys: {list(imported_data.data.keys())}")
                    if 'n_tot' in imported_data.data:
                        print(f"n_tot present: {imported_data.data['n_tot'] is not None}")
                        if imported_data.data['n_tot'] is not None:
                            print(f"n_tot length: {len(imported_data.data['n_tot'])}")
            
            # Call original method
            result = original_update(self, imported_data)
            
            # Check state after update
            print(f"After update, datetime_array is None: {self.datetime_array is None}")
            if self.datetime_array is not None:
                print(f"datetime_array length: {len(self.datetime_array)}")
                print(f"First few datetime values: {self.datetime_array[:3] if len(self.datetime_array) >= 3 else self.datetime_array}")
            
            return result
            
        # Apply the patch
        proton_fits_class.update = traced_update
        
        # Trace proton_fits_class.calculate_variables
        original_calculate = proton_fits_class.calculate_variables
        def traced_calculate(self, imported_data):
            print(f"\n*** TRACE: proton_fits_class.calculate_variables called ***")
            print(f"imported_data type: {type(imported_data)}")
            
            # Check imported_data before calling original
            if hasattr(imported_data, 'times'):
                print(f"BEFORE: imported_data has times: {imported_data.times is not None}")
                if imported_data.times is not None:
                    print(f"BEFORE: times length: {len(imported_data.times)}")
            
            if hasattr(imported_data, 'data'):
                print(f"BEFORE: imported_data has data: {imported_data.data is not None}")
                if isinstance(imported_data.data, dict):
                    print(f"BEFORE: data keys: {list(imported_data.data.keys())}")
            
            # Call original method
            result = original_calculate(self, imported_data)
            
            # Check state after calculate_variables
            print(f"AFTER: self.time is None: {self.time is None}")
            if self.time is not None:
                print(f"AFTER: self.time length: {len(self.time)}")
                
            print(f"AFTER: self.datetime_array is None: {self.datetime_array is None}")
            if self.datetime_array is not None:
                print(f"AFTER: datetime_array length: {len(self.datetime_array)}")
                
            if hasattr(self, 'raw_data'):
                if 'n_tot' in self.raw_data:
                    print(f"AFTER: self.raw_data['n_tot'] is None: {self.raw_data['n_tot'] is None}")
                    if self.raw_data['n_tot'] is not None:
                        print(f"AFTER: n_tot length: {len(self.raw_data['n_tot'])}")
            
            return result
            
        # Apply the patch
        proton_fits_class.calculate_variables = traced_calculate
 
        original_server = config.data_server # Store original server setting
        trange = ['2024-04-01/00:00:00', '2024-04-01/23:59:59']
        variable_to_test = proton_fits.n_tot # Example: Total proton density from CDF

        try:
            # --- Temporarily force Berkeley server --- 
            print(f"Original data_server: {original_server}")
            config.data_server = 'berkeley'
            print(f"Temporarily setting data_server to: {config.data_server}")
            # -----------------------------------------
            
            phase(1, "Calling plotbot with proton_fits.n_tot")
            plt.options.use_single_title = True
            plt.options.single_title_text = "TEST: Plotting proton_fits.n_tot from CDF"
            
            # Before plotbot call, check proton_fits state
            print(f"\nBEFORE plotbot: proton_fits has datetime_array: {hasattr(proton_fits, 'datetime_array')}")
            if hasattr(proton_fits, 'datetime_array'):
                print(f"BEFORE plotbot: datetime_array is None: {proton_fits.datetime_array is None}")
                if proton_fits.datetime_array is not None:
                    print(f"BEFORE plotbot: datetime_array length: {len(proton_fits.datetime_array)}")
            
            # Make the plotbot call
            pb(trange, variable_to_test, 1)
            
            phase(2, "Verifying data loaded for proton_fits.n_tot")
            
            # After plotbot call, check proton_fits state again
            print(f"\nAFTER plotbot: proton_fits has datetime_array: {hasattr(proton_fits, 'datetime_array')}")
            if hasattr(proton_fits, 'datetime_array'):
                print(f"AFTER plotbot: datetime_array is None: {proton_fits.datetime_array is None}")
                if proton_fits.datetime_array is not None:
                    print(f"AFTER plotbot: datetime_array length: {len(proton_fits.datetime_array)}")
            
            # Re-fetch the instance to ensure we have the updated state
            # Note: Depending on how plotbot updates instances, simply using
            # variable_to_test might also work, but fetching is safer.
            updated_instance = proton_fits 
            # Access the plot_manager instance via the subclass_name
            var_pm = getattr(updated_instance, variable_to_test.subclass_name, None)
            
            print(f"\nplot_manager for {variable_to_test.subclass_name} exists: {var_pm is not None}")
            if var_pm is not None:
                print(f"var_pm type: {type(var_pm)}")
                print(f"var_pm has datetime_array: {hasattr(var_pm, 'datetime_array')}")
                if hasattr(var_pm, 'datetime_array'):
                    print(f"var_pm.datetime_array is None: {var_pm.datetime_array is None}")
                    if var_pm.datetime_array is not None:
                        print(f"var_pm.datetime_array length: {len(var_pm.datetime_array)}")
                
                print(f"var_pm has data: {hasattr(var_pm, 'data')}")
                if hasattr(var_pm, 'data'):
                    print(f"var_pm.data is None: {var_pm.data is None}")
                    if var_pm.data is not None:
                        try:
                            data_len = len(var_pm.data)
                            print(f"var_pm.data length: {data_len}")
                        except TypeError:
                            print(f"var_pm.data is unsized (TypeError on len()). Type: {type(var_pm.data)}")
                            # Optionally, print the value itself if it's small/printable
                            # print(f"var_pm.data value: {var_pm.data}")
            
            system_check("Variable plot_manager exists", var_pm is not None,
                           f"Could not find attribute {variable_to_test.subclass_name} on proton_fits instance after plotbot call.")
            if var_pm is None: pytest.fail("Test failed: variable plot_manager attribute not found.")
            
            # Check attributes on the plot_manager instance
            has_time = hasattr(var_pm, 'datetime_array') and var_pm.datetime_array is not None and len(var_pm.datetime_array) > 0
            
            has_data = hasattr(var_pm, 'data') and var_pm.data is not None
            
            system_check("Has populated datetime_array", has_time,
                           f"{variable_to_test.subclass_name} should have a populated datetime_array.")
            system_check("Has data", has_data,
                           f"{variable_to_test.subclass_name} should have data attribute.")

            if not has_time or not has_data:
                 pytest.fail("Test failed: Missing or empty time/data array.")
            
            data_len = len(var_pm.data) if isinstance(var_pm.data, (np.ndarray, list)) else 0
            time_len = len(var_pm.datetime_array) # Already checked it's not None and > 0

            system_check("Data array is populated", data_len > 0,
                           f"{variable_to_test.subclass_name} data array should not be empty (Length: {data_len}).")
            system_check("Time array length matches data length (if data is array)", 
                           (not isinstance(var_pm.data, np.ndarray) or time_len == data_len),
                           f"{variable_to_test.subclass_name} time ({time_len}) and data ({data_len}) array lengths should match.")
                           
            # Simple check: ensure not ALL data is NaN (allowing for some NaNs)
            if data_len > 0 and isinstance(var_pm.data, np.ndarray):
                is_all_nan = np.all(np.isnan(var_pm.data))
                system_check("Data is not all NaN", not is_all_nan,
                               f"{variable_to_test.subclass_name} data should not be entirely NaN.")

            # Test passes if plotbot runs and data seems loaded
            assert True 
            
        except Exception as e:
            pytest.fail(f"plotbot call failed during test: {e}")
        finally:
            # --- Restore original server setting --- 
            config.data_server = original_server
            print(f"Restored data_server to: {config.data_server}")
            
            # Restore original methods to avoid affecting other tests
            data_cubby.grab = original_grab
            plotbot.data_import.import_data_function = original_import_data
            proton_fits_class.update = original_update
            proton_fits_class.calculate_variables = original_calculate

    @pytest.mark.skipif(not CDF_SF01_FILE.exists(), reason=f"Test CDF file not found: {CDF_SF01_FILE}")
    def test_plotbot_with_sf01_cdf_variable(self):
        """Tests plotting a single variable directly from the sf01_fits CDF via plotbot."""
        print("\n--- Testing plotbot with sf01_fits CDF variable (proton_fits.n_tot) ---")
        
        # Need plotbot and the specific object instance
        from plotbot import plotbot as pb, proton_fits, plt
        from plotbot.test_pilot import phase, system_check
        import numpy as np

        trange = ['2024-04-01/00:00:00', '2024-04-01/23:59:59']
        variable_to_test = proton_fits.n_tot # Example: Total proton density from CDF

        phase(1, "Calling plotbot with proton_fits.n_tot")
        plt.options.use_single_title = True
        plt.options.single_title_text = "TEST: Plotting proton_fits.n_tot from CDF"
        try:
            pb(trange, variable_to_test, 1)
        except Exception as e:
            pytest.fail(f"plotbot call failed: {e}")

        phase(2, "Verifying data loaded for proton_fits.n_tot")
        
        # Re-fetch the instance to ensure we have the updated state
        # Note: Depending on how plotbot updates instances, simply using
        # variable_to_test might also work, but fetching is safer.
        updated_instance = proton_fits 
        var_data = getattr(updated_instance, variable_to_test.subclass_name, None)
        
        system_check("Variable instance exists", var_data is not None,
                       f"Could not find attribute {variable_to_test.subclass_name} on proton_fits instance after plotbot call.")
        if var_data is None: pytest.fail("Test failed: variable attribute not found.")
        
        has_time = hasattr(var_data, 'datetime_array') and var_data.datetime_array is not None
        has_data = hasattr(var_data, 'data') and var_data.data is not None
        
        system_check("Has datetime_array", has_time,
                       f"{variable_to_test.subclass_name} should have datetime_array.")
        system_check("Has data", has_data,
                       f"{variable_to_test.subclass_name} should have data attribute.")

        if not has_time or not has_data:
             pytest.fail("Test failed: Missing time or data array.")
        
        data_len = len(var_data.data) if isinstance(var_data.data, (np.ndarray, list)) else 0
        time_len = len(var_data.datetime_array) if isinstance(var_data.datetime_array, (np.ndarray, list)) else 0

        system_check("Data array is populated", data_len > 0,
                       f"{variable_to_test.subclass_name} data array should not be empty (Length: {data_len}).")
        system_check("Time array is populated", time_len > 0,
                       f"{variable_to_test.subclass_name} datetime_array should not be empty (Length: {time_len}).")
                       
        # Simple check: ensure not ALL data is NaN (allowing for some NaNs)
        if data_len > 0:
            is_all_nan = np.all(np.isnan(var_data.data))
            system_check("Data is not all NaN", not is_all_nan,
                           f"{variable_to_test.subclass_name} data should not be entirely NaN.")

        # Test passes if plotbot runs and data seems loaded
        assert True 

    # --- NEW SIMPLIFIED TEST --- 
    @pytest.mark.skipif(not CDF_SF00_FILE.exists(), reason=f"Test CDF file not found: {CDF_SF00_FILE}")
    def test_plotbot_basic_fits_call(self):
        """Simplified test calling plotbot with a single FITS variable."""
        print("\n--- Simplified plotbot test with sf00_fits (proton_fits.n_tot) ---")
        
        # Import the actual plotbot function and necessary components
        from plotbot.plotbot_main import plotbot as plotbot_func
        from plotbot import proton_fits, plt as plotbot_plt
        from plotbot.config import config # Import config
        from plotbot.print_manager import print_manager
        import matplotlib.pyplot as actual_plt # To check figure existence
        
        print_manager.enable_debug() 
        
        trange = ['2024-04-01/00:00:00', '2024-04-01/23:59:59']
        variable = proton_fits.n_tot
        original_server = config.data_server
        fig = None
        
        try:
            # Temporarily set server to Berkeley 
            config.data_server = 'berkeley'
            print(f"Set server to: {config.data_server}")
            
            print(f"Calling plotbot_func with trange={trange}, variable={variable}")
            
            # Call the plotbot function directly with 3 variables
            plotbot_func(trange, 
                         proton_fits.n_tot, 1,
                         proton_fits.np1, 2,
                         proton_fits.beta_ppar_pfits, 3
                         )
            
            print("plotbot_func call completed.")
            
            # Check if a figure was created
            fig_num = actual_plt.gcf().number
            fig = actual_plt.figure(fig_num)
            
            assert fig is not None, "Plotbot function should have created a figure."
            print(f"Figure {fig_num} created successfully.")
            
            # Save the figure for visual inspection
            save_path = Path(__file__).parent / "test_plot_basic_fits_call.png"
            actual_plt.savefig(save_path)
            print(f"Plot saved to: {save_path}")
            
        except Exception as e:
            pytest.fail(f"Simplified plotbot test failed: {e}")
        finally:
            # Restore server setting
            config.data_server = original_server
            print(f"Restored server to: {config.data_server}")
            # Close the plot
            if fig is not None:
                plotbot_plt.close(fig)
            else:
                plotbot_plt.close('all') # Fallback