"""
Wind Magnetometer Proof of Concept
Demonstrates modular approach for WIND satellite data integration into plotbot
"""
import numpy as np
import pyspedas
import cdflib
from collections import namedtuple

# Import our dynamic class factory
from ..dynamic_class_test import create_data_class, SimplePlotManager

# Mock import for plotbot components (replace with actual imports)
class MockPrintManager:
    def status(self, msg): print(f"STATUS: {msg}")
    def debug(self, msg): print(f"DEBUG: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

print_manager = MockPrintManager()

# Metadata for WIND MFI data
wind_mfi_metadata = {
    'instrument_short': 'wind',
    'datatype_name': 'mfi_h0', 
    'variables': {
        'bx_gse': {
            'description': 'Magnetic field X component in GSE coordinates',
            'units': 'nT',
            'cdf_var_name': 'BGSE',  # Maps to BGSE[0] in CDF
            'component_index': 0,
            'plot_options': {
                'y_label': 'Bx (nT)',
                'legend_label': '$B_X$ (GSE)',
                'color': 'red'
            }
        },
        'by_gse': {
            'description': 'Magnetic field Y component in GSE coordinates', 
            'units': 'nT',
            'cdf_var_name': 'BGSE',
            'component_index': 1,
            'plot_options': {
                'y_label': 'By (nT)', 
                'legend_label': '$B_Y$ (GSE)',
                'color': 'green'
            }
        },
        'bz_gse': {
            'description': 'Magnetic field Z component in GSE coordinates',
            'units': 'nT', 
            'cdf_var_name': 'BGSE',
            'component_index': 2,
            'plot_options': {
                'y_label': 'Bz (nT)',
                'legend_label': '$B_Z$ (GSE)', 
                'color': 'blue'
            }
        }
    },
    'calculations': {
        'bmag': {
            'inputs': ['bx_gse', 'by_gse', 'bz_gse'],
            'operation': 'magnitude',
            'plot_options': {
                'y_label': '|B| (nT)',
                'legend_label': '$|B|$',
                'color': 'black'
            }
        }
    }
}

def download_wind_data(trange):
    """Download WIND MFI data using pyspedas"""
    try:
        print_manager.status(f"Downloading WIND MFI data for {trange}")
        
        # Download data using pyspedas
        vars_loaded = pyspedas.wind.mfi(
            trange=trange,
            datatype='h0',  # 3-second resolution
            downloadonly=True,
            notplot=True,
            time_clip=True
        )
        
        if vars_loaded:
            print_manager.status(f"Downloaded files: {vars_loaded}")
            return vars_loaded
        else:
            print_manager.error("No files downloaded")
            return None
            
    except Exception as e:
        print_manager.error(f"Download failed: {e}")
        return None

def load_wind_cdf_data(file_paths, trange):
    """Load data from downloaded CDF files"""
    TestDataObject = namedtuple('TestDataObject', ['times', 'data'])
    
    try:
        if not file_paths:
            return None
            
        # Use first file for now (could combine multiple files)
        cdf_file = file_paths[0] if isinstance(file_paths, list) else file_paths
        
        print_manager.debug(f"Loading CDF file: {cdf_file}")
        
        # Read CDF file
        cdf = cdflib.CDF(cdf_file)
        
        # Get time data (TT2000 format)
        epoch = cdf.varget('Epoch')
        
        # Get magnetic field data (BGSE variable contains [Bx, By, Bz])
        bgse = cdf.varget('BGSE')  # Shape should be (n_times, 3)
        
        # cdf.close()  # Not needed with cdflib, handled automatically
        
        # Extract components
        bx_gse = bgse[:, 0]
        by_gse = bgse[:, 1] 
        bz_gse = bgse[:, 2]
        
        # Package data
        data_dict = {
            'bx_gse': bx_gse,
            'by_gse': by_gse,
            'bz_gse': bz_gse
        }
        
        print_manager.status(f"Loaded {len(epoch)} data points")
        return TestDataObject(times=epoch, data=data_dict)
        
    except Exception as e:
        print_manager.error(f"Failed to load CDF data: {e}")
        return None

def get_wind_data(trange):
    """Main function to get WIND data (mimics plotbot's get_data interface)"""
    # Step 1: Download data
    file_paths = download_wind_data(trange)
    if not file_paths:
        return None
        
    # Step 2: Load data from CDF files
    data_obj = load_wind_cdf_data(file_paths, trange)
    if not data_obj:
        return None
        
    # Step 3: Create dynamic class instance
    WindMFI = create_data_class('WindMFI', wind_mfi_metadata)
    wind_instance = WindMFI(data_obj)
    
    return wind_instance

# Test the proof of concept
if __name__ == "__main__":
    print("=== WIND Magnetometer Proof of Concept ===")
    
    # Test with a small time range
    test_trange = ['2020-01-01', '2020-01-02']
    
    try:
        wind_data = get_wind_data(test_trange)
        
        if wind_data:
            print("\n✅ Success! WIND data loaded into dynamic class")
            print(f"Class name: {wind_data.class_name}")
            print(f"Data type: {wind_data.data_type}")
            print(f"Available variables: {list(wind_data._metadata['variables'].keys())}")
            print(f"Available calculations: {list(wind_data._metadata['calculations'].keys())}")
            
            # Test accessing variables
            print(f"\nBx data shape: {wind_data.bx_gse.data.shape}")
            print(f"By data shape: {wind_data.by_gse.data.shape}")
            print(f"Bz data shape: {wind_data.bz_gse.data.shape}")
            print(f"Bmag data shape: {wind_data.bmag.data.shape}")
            
            # Test plot options
            print(f"\nBx color: {wind_data.bx_gse.plot_options['color']}")
            print(f"Bmag legend: {wind_data.bmag.plot_options['legend_label']}")
            
        else:
            print("❌ Failed to load WIND data")
            
    except Exception as e:
        print(f"❌ Error in proof of concept: {e}")
        import traceback
        traceback.print_exc() 