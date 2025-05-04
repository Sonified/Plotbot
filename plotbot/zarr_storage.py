# plotbot/zarr_storage.py

import os
import xarray as xr
import numpy as np
import zarr
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse

from .print_manager import print_manager
from .data_tracker import global_tracker
from .data_classes.psp_data_types import data_types

class ZarrStorage:
    """Zarr-based persistent storage that follows the natural cadence of PSP data"""
    
    def __init__(self, base_dir="./zarr_storage"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
    def store_data(self, class_instance, data_type, trange):
        """Store processed data to Zarr using the natural cadence of the data"""
        if not hasattr(class_instance, 'raw_data') or not hasattr(class_instance, 'datetime_array'):
            print_manager.warning(f"Cannot store {data_type}: missing required attributes")
            return False
            
        if class_instance.datetime_array is None or len(class_instance.datetime_array) == 0:
            print_manager.warning(f"No data to store for {data_type}")
            return False
            
        # Get configuration for this data type
        config = data_types.get(data_type, {})
        file_time_format = config.get('file_time_format', 'daily')
            
        # Create dataset from class instance
        try:
            # Create variables dictionary from raw_data
            data_vars = {}
            for var_name, data in class_instance.raw_data.items():
                if data is None or var_name == 'all':
                    continue
                data_vars[var_name] = (['time'], data)
                
            # Create dataset
            ds = xr.Dataset(
                data_vars=data_vars,
                coords={'time': class_instance.datetime_array}
            )
            
            # Determine chunking based on data cadence
            if file_time_format == 'daily':
                # For daily files, chunk by the entire day
                chunks = {'time': -1}  # One chunk per time dimension
            elif file_time_format == '6-hour':
                # For 6-hour files, chunk by the 6-hour period
                chunks = {'time': -1}  # One chunk per file's worth of data
            else:
                # Default chunking
                chunks = {'time': -1}
                
            # Create zarr path based on data_type and file format
            zarr_path = self._get_zarr_path(data_type, class_instance.datetime_array[0], file_time_format)
            os.makedirs(os.path.dirname(zarr_path), exist_ok=True)
            
            # Apply compression
            encoding = {var: {'compressor': zarr.Blosc(cname='zstd', clevel=5, shuffle=2)} 
                        for var in ds.data_vars}
            
            # Save to zarr
            ds.chunk(chunks).to_zarr(zarr_path, mode='w', encoding=encoding)
            print_manager.status(f"✅ Saved {data_type} data to {zarr_path}")
            return True
            
        except Exception as e:
            print_manager.error(f"Error saving {data_type} to Zarr: {e}")
            return False
            
    def load_data(self, data_type, trange):
        """Load data from Zarr stores for given time range"""
        # Parse time range
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
        
        # Get configuration for this data type
        config = data_types.get(data_type, {})
        file_time_format = config.get('file_time_format', 'daily')
        
        # Find all zarr stores in the time range
        zarr_paths = self._find_zarr_paths(data_type, start_time, end_time, file_time_format)
        
        if not zarr_paths:
            print_manager.debug(f"No Zarr data found for {data_type} in range {trange}")
            return None
            
        # Load and concatenate all relevant zarr stores
        print_manager.debug(f"Loading {len(zarr_paths)} Zarr stores for {data_type}")
        
        try:
            datasets = []
            for path in zarr_paths:
                if os.path.exists(path):
                    ds = xr.open_zarr(path)
                    datasets.append(ds)
            
            if not datasets:
                return None
                
            # Concatenate datasets if more than one
            if len(datasets) == 1:
                combined = datasets[0]
            else:
                combined = xr.concat(datasets, dim='time')
            
            # Convert to imported_data format for the update method
            return self._convert_to_import_format(combined, data_type)
            
        except Exception as e:
            print_manager.error(f"Error loading Zarr data for {data_type}: {e}")
            return None
            
    def _get_zarr_path(self, data_type, timestamp, file_time_format):
        """Generate zarr path based on data type and timestamp"""
        dt = timestamp
        if isinstance(dt, np.datetime64):
            dt = pd.Timestamp(dt).to_pydatetime()
            
        if file_time_format == 'daily':
            # Store daily data in year/month/day.zarr
            return os.path.join(self.base_dir, data_type, 
                               f"{dt.year}", 
                               f"{dt.month:02d}", 
                               f"{dt.day:02d}.zarr")
        elif file_time_format == '6-hour':
            # Store 6-hour data in year/month/day_hour.zarr
            hour = (dt.hour // 6) * 6  # Round to nearest 6-hour block
            return os.path.join(self.base_dir, data_type, 
                               f"{dt.year}", 
                               f"{dt.month:02d}", 
                               f"{dt.day:02d}_{hour:02d}.zarr")
        else:
            # Default path
            return os.path.join(self.base_dir, data_type, 
                              f"{dt.year}_{dt.month:02d}_{dt.day:02d}.zarr")
    
    def _find_zarr_paths(self, data_type, start_time, end_time, file_time_format):
        """Find all zarr paths for a data type within the time range"""
        zarr_paths = []
        
        if file_time_format == 'daily':
            # Generate daily paths
            current_date = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            while current_date <= end_time:
                zarr_path = self._get_zarr_path(data_type, current_date, file_time_format)
                zarr_paths.append(zarr_path)
                current_date += timedelta(days=1)
                
        elif file_time_format == '6-hour':
            # Generate 6-hour paths
            current_date = start_time.replace(
                hour=(start_time.hour // 6) * 6, 
                minute=0, second=0, microsecond=0
            )
            while current_date <= end_time:
                zarr_path = self._get_zarr_path(data_type, current_date, file_time_format)
                zarr_paths.append(zarr_path)
                current_date += timedelta(hours=6)
        
        return zarr_paths
        
    def _convert_to_import_format(self, ds, data_type):
        """Convert xarray Dataset to the format expected by the update method"""
        # Create a structure matching what the update methods expect
        class ImportedData:
            def __init__(self):
                self.times = None
                self.data = {}
                
        imported_data = ImportedData()
        
        # Convert times to the expected format
        imported_data.times = np.array([np.datetime64(t) for t in ds.time.values])
        
        # Handle variables based on data_type
        if data_type == 'mag_rtn_4sa':
            # Create 3D array from components
            if all(v in ds for v in ['br', 'bt', 'bn']):
                field_data = np.stack([
                    ds['br'].values,
                    ds['bt'].values,
                    ds['bn'].values
                ], axis=1)
                imported_data.data['psp_fld_l2_mag_RTN_4_Sa_per_Cyc'] = field_data
                
        elif data_type == 'mag_rtn':
            if all(v in ds for v in ['br', 'bt', 'bn']):
                field_data = np.stack([
                    ds['br'].values,
                    ds['bt'].values,
                    ds['bn'].values
                ], axis=1)
                imported_data.data['psp_fld_l2_mag_RTN'] = field_data
                
        elif data_type == 'mag_sc_4sa':
            if all(v in ds for v in ['bx', 'by', 'bz']):
                field_data = np.stack([
                    ds['bx'].values,
                    ds['by'].values,
                    ds['bz'].values
                ], axis=1)
                imported_data.data['psp_fld_l2_mag_SC_4_Sa_per_Cyc'] = field_data
                
        elif data_type == 'mag_sc':
            if all(v in ds for v in ['bx', 'by', 'bz']):
                field_data = np.stack([
                    ds['bx'].values,
                    ds['by'].values,
                    ds['bz'].values
                ], axis=1)
                imported_data.data['psp_fld_l2_mag_SC'] = field_data
        
        # Add additional data_types as needed
                
        return imported_data
    
__all__ = ['ZarrStorage']