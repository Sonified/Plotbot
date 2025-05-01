import sys
from pathlib import Path
import traceback
import numpy as np
import matplotlib.pyplot as plt
import cdflib

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import custom modules
from plotbot.data_import import import_data_function, DataObject

# Define paths for the test CDF file
TEST_DATA_DIR = Path(__file__).parent / 'test_data'
CDF_DIR = TEST_DATA_DIR / 'psp_cdf_fits'
CDF_SF00_FILE = CDF_DIR / 'spp_swp_spi_sf00_fits_2024-04-01_v00.cdf'

# Enable verbose output
import logging
logging.basicConfig(level=logging.DEBUG)

def debug_cdf_import():
    """Trace through the CDF import process to identify the issue with datetime_array handling"""
    
    print("\n=== DEBUGGING CDF IMPORT PROCESS ===")
    
    # STEP 1: Verify the test file exists
    print(f"\n--- Step 1: Checking test file ---")
    print(f"Test file path: {CDF_SF00_FILE}")
    print(f"File exists: {CDF_SF00_FILE.exists()}")
    
    # STEP 2: Manually read the CDF file with cdflib
    print(f"\n--- Step 2: Direct CDF reading with cdflib ---")
    try:
        cdf = cdflib.CDF(CDF_SF00_FILE)
        epoch_data = cdf.varget('Epoch')
        epoch_datetime = cdflib.cdfepoch.to_datetime(epoch_data)
        n_tot = cdf.varget('n_tot')
        
        print(f"Epoch data type: {type(epoch_data)}")
        print(f"Epoch data shape: {epoch_data.shape}")
        print(f"First 3 Epoch values: {epoch_data[:3]}")
        print(f"Epoch datetime type: {type(epoch_datetime)}")
        print(f"First 3 datetime values: {epoch_datetime[:3]}")
        print(f"n_tot shape: {n_tot.shape}")
        print(f"First 3 n_tot values: {n_tot[:3]}")
    except Exception as e:
        print(f"ERROR in direct CDF reading: {e}")
        traceback.print_exc()
    
    # STEP 3: Use the import_data_function to create a DataObject
    print(f"\n--- Step 3: Using import_data_function ---")
    try:
        # Configure similar parameters as in the test
        trange = ['2024-04-01/00:00:00', '2024-04-01/23:59:59']
        data_type = 'sf00_fits'
        
        print(f"Calling import_data_function with trange={trange}, data_type={data_type}")
        
        # Import the data
        result = import_data_function(trange, data_type, remote_file_path=str(CDF_SF00_FILE))
        
        print(f"Result type: {type(result)}")
        if result is not None:
            print(f"Has 'times' attribute: {hasattr(result, 'times')}")
            if hasattr(result, 'times'):
                print(f"Times type: {type(result.times)}")
                print(f"Times shape: {getattr(result.times, 'shape', 'unknown')}")
                print(f"First 3 times: {result.times[:3] if len(result.times) >= 3 else result.times}")
            
            print(f"Has 'data' attribute: {hasattr(result, 'data')}")
            if hasattr(result, 'data'):
                print(f"Data type: {type(result.data)}")
                print(f"Data keys: {list(result.data.keys()) if isinstance(result.data, dict) else 'not a dict'}")
                
                if 'n_tot' in result.data:
                    print(f"n_tot type: {type(result.data['n_tot'])}")
                    print(f"n_tot shape: {getattr(result.data['n_tot'], 'shape', 'unknown')}")
                    print(f"First 3 n_tot values: {result.data['n_tot'][:3] if len(result.data['n_tot']) >= 3 else result.data['n_tot']}")
    except Exception as e:
        print(f"ERROR in import_data_function: {e}")
        traceback.print_exc()
    
    # STEP 4: Manually create a DataObject and instantiate proton_fits_class
    print(f"\n--- Step 4: Manual proton_fits_class instantiation ---")
    try:
        from plotbot.data_classes.psp_proton_fits_classes import proton_fits_class
        
        # Manually create a DataObject with the data from the CDF
        # This is essentially what import_data_function should do
        data_dict = {
            'Epoch': epoch_data,
            'n_tot': n_tot,
            # Add other required variables as needed
        }
        
        # Create the DataObject manually
        data_obj = DataObject(times=epoch_data, data=data_dict)
        
        print(f"DataObject created successfully.")
        print(f"DataObject times shape: {getattr(data_obj.times, 'shape', 'unknown')}")
        print(f"DataObject has n_tot: {'n_tot' in data_obj.data}")
        
        # Instantiate proton_fits_class with the DataObject
        instance = proton_fits_class(data_obj)
        
        print(f"proton_fits_class instantiated successfully.")
        print(f"Has datetime_array: {hasattr(instance, 'datetime_array')}")
        if hasattr(instance, 'datetime_array'):
            print(f"datetime_array is None: {instance.datetime_array is None}")
            if instance.datetime_array is not None:
                print(f"datetime_array shape: {instance.datetime_array.shape}")
                print(f"First 3 datetime values: {instance.datetime_array[:3]}")
        
        print(f"Has n_tot in raw_data: {'n_tot' in instance.raw_data}")
        if 'n_tot' in instance.raw_data:
            print(f"n_tot is None: {instance.raw_data['n_tot'] is None}")
            if instance.raw_data['n_tot'] is not None:
                print(f"n_tot shape: {instance.raw_data['n_tot'].shape}")
                print(f"First 3 n_tot values: {instance.raw_data['n_tot'][:3]}")
        
        # Access the plot_manager for n_tot
        if hasattr(instance, 'n_tot'):
            print(f"Has n_tot plot_manager: {hasattr(instance, 'n_tot')}")
            print(f"n_tot plot_manager type: {type(instance.n_tot)}")
            print(f"n_tot plot_manager has datetime_array: {hasattr(instance.n_tot, 'datetime_array')}")
            if hasattr(instance.n_tot, 'datetime_array'):
                print(f"n_tot datetime_array is None: {instance.n_tot.datetime_array is None}")
        
    except Exception as e:
        print(f"ERROR in manual instantiation: {e}")
        traceback.print_exc()
    
    print("\n=== END DEBUGGING CDF IMPORT ===")

if __name__ == '__main__':
    debug_cdf_import() 