"""
Modular CDF Processor
A reusable module for processing CDF files from any satellite mission using metadata
"""

import numpy as np
import cdflib
import pyspedas
from collections import namedtuple
from typing import Dict, List, Optional, Any, Union

# Generic data container
DataObject = namedtuple('DataObject', ['times', 'data'])

class CDFProcessor:
    """Generic CDF processor that can handle any mission using metadata"""
    
    def __init__(self, mission_config: Dict[str, Any]):
        """
        Initialize with mission-specific configuration
        
        Parameters:
        -----------
        mission_config : dict
            Configuration containing:
            - pyspedas_function: function to call for download
            - time_var: name of time variable in CDF (default: 'Epoch')
            - data_mapping: dict mapping variable names to CDF extraction info
        """
        self.config = mission_config
        self.time_var = mission_config.get('time_var', 'Epoch')
        
    def download_data(self, trange: List[str], **kwargs) -> Optional[List[str]]:
        """Download data using pyspedas"""
        try:
            pyspedas_func = self.config['pyspedas_function']
            
            # Default pyspedas parameters
            default_params = {
                'trange': trange,
                'downloadonly': True,
                'notplot': True,
                'time_clip': True
            }
            
            # Merge with mission-specific parameters
            params = {**default_params, **self.config.get('pyspedas_params', {}), **kwargs}
            
            # Call the pyspedas function
            result = pyspedas_func(**params)
            
            return result if result else None
            
        except Exception as e:
            print(f"Download failed: {e}")
            return None
    
    def extract_variable_from_cdf(self, cdf_file: cdflib.CDF, var_config: Dict[str, Any]) -> np.ndarray:
        """Extract a variable from CDF file based on configuration"""
        
        cdf_var_name = var_config['cdf_var_name']
        data = cdf_file.varget(cdf_var_name)
        
        # Handle component extraction (e.g., BGSE[0] for Bx)
        if 'component_index' in var_config:
            if data.ndim > 1:
                data = data[:, var_config['component_index']]
            else:
                raise ValueError(f"Cannot extract component {var_config['component_index']} from 1D data")
        
        # Handle scaling/calibration if specified
        if 'scale_factor' in var_config:
            data = data * var_config['scale_factor']
            
        if 'offset' in var_config:
            data = data + var_config['offset']
            
        return data
    
    def load_cdf_data(self, file_paths: Union[str, List[str]], metadata: Dict[str, Any]) -> Optional[DataObject]:
        """Load data from CDF files using metadata"""
        
        if not file_paths:
            return None
            
        # Handle single file or list of files
        if isinstance(file_paths, str):
            file_paths = [file_paths]
            
        all_times = []
        all_data = {}
        
        for file_path in file_paths:
            try:
                cdf = cdflib.CDF(file_path)
                
                # Extract time data
                times = cdf.varget(self.time_var)
                all_times.append(times)
                
                # Extract each variable according to metadata
                for var_name, var_config in metadata['variables'].items():
                    try:
                        data = self.extract_variable_from_cdf(cdf, var_config)
                        
                        if var_name not in all_data:
                            all_data[var_name] = []
                        all_data[var_name].append(data)
                        
                    except Exception as e:
                        print(f"Failed to extract {var_name}: {e}")
                        
                cdf.close()
                
            except Exception as e:
                print(f"Failed to load {file_path}: {e}")
                continue
        
        if not all_times:
            return None
            
        # Concatenate data from multiple files
        combined_times = np.concatenate(all_times)
        combined_data = {}
        
        for var_name, data_list in all_data.items():
            if data_list:
                combined_data[var_name] = np.concatenate(data_list)
        
        return DataObject(times=combined_times, data=combined_data)
    
    def process_data(self, trange: List[str], metadata: Dict[str, Any], **kwargs) -> Optional[DataObject]:
        """Complete processing pipeline: download -> load -> return data"""
        
        # Step 1: Download
        file_paths = self.download_data(trange, **kwargs)
        if not file_paths:
            return None
            
        # Step 2: Load from CDF
        data_obj = self.load_cdf_data(file_paths, metadata)
        
        return data_obj

# Mission-specific configurations
MISSION_CONFIGS = {
    'wind_mfi': {
        'pyspedas_function': pyspedas.wind.mfi,
        'pyspedas_params': {'datatype': 'h0'},
        'time_var': 'Epoch',
        'description': 'WIND Magnetic Field Investigation'
    },
    'themis_fgm': {
        'pyspedas_function': pyspedas.themis.fgm,
        'pyspedas_params': {'probe': 'd'},  # Default probe
        'time_var': 'Epoch',
        'description': 'THEMIS Fluxgate Magnetometer'
    },
    'psp_fields': {
        'pyspedas_function': pyspedas.psp.fields,
        'pyspedas_params': {'datatype': 'mag_rtn_4_sa_per_cyc', 'level': 'l2'},
        'time_var': 'Epoch',
        'description': 'PSP FIELDS Magnetometer'
    }
}

# Example usage for different missions
def create_wind_processor():
    """Create a processor for WIND MFI data"""
    return CDFProcessor(MISSION_CONFIGS['wind_mfi'])

def create_themis_processor(probe='d'):
    """Create a processor for THEMIS FGM data"""
    config = MISSION_CONFIGS['themis_fgm'].copy()
    config['pyspedas_params'] = {'probe': probe}
    return CDFProcessor(config)

def create_psp_processor():
    """Create a processor for PSP FIELDS data"""
    return CDFProcessor(MISSION_CONFIGS['psp_fields'])

# Example metadata for different coordinate systems
COORDINATE_SYSTEM_METADATA = {
    'wind_gse': {
        'variables': {
            'bx_gse': {
                'cdf_var_name': 'BGSE',
                'component_index': 0,
                'description': 'Magnetic field X component in GSE coordinates',
                'units': 'nT',
                'plot_options': {'color': 'red', 'legend_label': '$B_X$ (GSE)'}
            },
            'by_gse': {
                'cdf_var_name': 'BGSE',
                'component_index': 1,
                'description': 'Magnetic field Y component in GSE coordinates',
                'units': 'nT',
                'plot_options': {'color': 'green', 'legend_label': '$B_Y$ (GSE)'}
            },
            'bz_gse': {
                'cdf_var_name': 'BGSE',
                'component_index': 2,
                'description': 'Magnetic field Z component in GSE coordinates',
                'units': 'nT',
                'plot_options': {'color': 'blue', 'legend_label': '$B_Z$ (GSE)'}
            }
        },
        'calculations': {
            'bmag': {
                'inputs': ['bx_gse', 'by_gse', 'bz_gse'],
                'operation': 'magnitude',
                'plot_options': {'color': 'black', 'legend_label': '$|B|$'}
            }
        }
    },
    
    'psp_rtn': {
        'variables': {
            'br': {
                'cdf_var_name': 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc',
                'component_index': 0,
                'description': 'Magnetic field radial component',
                'units': 'nT',
                'plot_options': {'color': 'forestgreen', 'legend_label': '$B_R$'}
            },
            'bt': {
                'cdf_var_name': 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc',
                'component_index': 1,
                'description': 'Magnetic field tangential component',
                'units': 'nT',
                'plot_options': {'color': 'orange', 'legend_label': '$B_T$'}
            },
            'bn': {
                'cdf_var_name': 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc',
                'component_index': 2,
                'description': 'Magnetic field normal component',
                'units': 'nT',
                'plot_options': {'color': 'dodgerblue', 'legend_label': '$B_N$'}
            }
        },
        'calculations': {
            'bmag': {
                'inputs': ['br', 'bt', 'bn'],
                'operation': 'magnitude',
                'plot_options': {'color': 'black', 'legend_label': '$|B|$'}
            }
        }
    }
}

# Demonstration function
def demonstrate_modular_approach():
    """Show how the modular approach works for different missions"""
    
    print("=== Modular CDF Processor Demo ===\n")
    
    # Example 1: WIND data
    print("1. WIND MFI Configuration:")
    wind_processor = create_wind_processor()
    print(f"   Mission: {wind_processor.config['description']}")
    print(f"   Function: {wind_processor.config['pyspedas_function'].__name__}")
    print(f"   Params: {wind_processor.config['pyspedas_params']}")
    
    # Example 2: THEMIS data
    print("\n2. THEMIS FGM Configuration:")
    themis_processor = create_themis_processor('d')
    print(f"   Mission: {themis_processor.config['description']}")
    print(f"   Function: {themis_processor.config['pyspedas_function'].__name__}")
    print(f"   Params: {themis_processor.config['pyspedas_params']}")
    
    # Example 3: PSP data
    print("\n3. PSP FIELDS Configuration:")
    psp_processor = create_psp_processor()
    print(f"   Mission: {psp_processor.config['description']}")
    print(f"   Function: {psp_processor.config['pyspedas_function'].__name__}")
    print(f"   Params: {psp_processor.config['pyspedas_params']}")
    
    # Show metadata flexibility
    print("\n4. Coordinate System Flexibility:")
    print(f"   WIND GSE variables: {list(COORDINATE_SYSTEM_METADATA['wind_gse']['variables'].keys())}")
    print(f"   PSP RTN variables: {list(COORDINATE_SYSTEM_METADATA['psp_rtn']['variables'].keys())}")
    
    print("\n5. Usage Pattern:")
    usage_example = '''
    # Generic usage for any mission:
    processor = create_wind_processor()  # or themis, psp, etc.
    metadata = COORDINATE_SYSTEM_METADATA['wind_gse']
    data_obj = processor.process_data(trange, metadata)
    
    # Create dynamic class
    dynamic_class = create_data_class('WindMFI', metadata)
    instance = dynamic_class(data_obj)
    
    # Use the data
    plot(instance.bx_gse, instance.by_gse, instance.bz_gse)
    '''
    print(usage_example)

if __name__ == "__main__":
    demonstrate_modular_approach() 