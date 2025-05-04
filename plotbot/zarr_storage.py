# plotbot/zarr_storage.py

import os
import xarray as xr
import numpy as np
import zarr
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
import pandas as pd
import cdflib

from .print_manager import print_manager
from .data_tracker import global_tracker
from .data_classes.psp_data_types import data_types

class ZarrStorage:
    """Zarr-based persistent storage that follows the natural cadence of PSP data"""
    
    def __init__(self, base_dir="./data_cubby"):
        print_manager.zarr_integration(f"[ZarrStorage.__init__] Initializing with base_dir={base_dir}")
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        print_manager.zarr_integration(f"[ZarrStorage.__init__] Directory created: {base_dir}")
        
    def store_data(self, class_instance, data_type, trange):
        """Store processed data to Zarr using the natural cadence of the data"""
        print_manager.zarr_integration(f"[store_data] Called for data_type={data_type}, trange={trange}")
        print_manager.zarr_integration(f"Storing data for {data_type}")
        print_manager.zarr_integration(f"datetime_array length: {len(class_instance.datetime_array)}")
        print_manager.zarr_integration(f"raw_data keys: {list(class_instance.raw_data.keys())}")
        if not hasattr(class_instance, 'raw_data') or not hasattr(class_instance, 'datetime_array'):
            print_manager.warning(f"Cannot store {data_type}: missing required attributes")
            return False
            
        if class_instance.datetime_array is None or len(class_instance.datetime_array) == 0:
            print_manager.warning(f"No data to store for {data_type}")
            return False
            
        # Get configuration for this data type
        config = data_types.get(data_type, {})
        file_time_format = config.get('file_time_format', 'daily')
        print_manager.zarr_integration(f"[store_data] file_time_format={file_time_format}")
            
        # Create dataset from class instance
        try:
            print_manager.zarr_integration(f"[store_data] Creating data_vars from class_instance.raw_data")
            data_vars = {}
            for var_name, data in class_instance.raw_data.items():
                if data is None or var_name == 'all':
                    continue
                # Debug print for spe_sf0_pad
                if data_type == 'spe_sf0_pad':
                    print(f"[DEBUG][ZARR][STORE] Saving var '{var_name}': type={type(data)}, shape={getattr(data, 'shape', None)}")
                # Try to get plot_manager for this variable
                pm = getattr(class_instance, var_name, None)
                dims = ['time']
                if hasattr(pm, 'plot_options'):
                    po = pm.plot_options
                    if getattr(po, 'plot_type', None) == 'spectral':
                        # Try to infer second axis name
                        second_axis = None
                        if hasattr(po, 'additional_data') and po.additional_data is not None:
                            second_axis = getattr(po, 'y_label', 'axis_1')
                            # Try to extract a clean name from y_label
                            if isinstance(second_axis, str):
                                # Use the first word or a cleaned version
                                second_axis = second_axis.split('\n')[0].strip().lower().replace(' ', '_')
                            else:
                                second_axis = 'axis_1'
                        else:
                            second_axis = 'axis_1'
                        dims = ['time', second_axis]
                # Fallback for 2D arrays if no plot_manager
                elif isinstance(data, np.ndarray) and data.ndim == 2:
                    dims = ['time', 'axis_1']
                print(f"[STORE] var_name: {var_name}, data shape: {np.shape(data)}, dims: {dims}")
                data_vars[var_name] = (dims, data)
            print(f"[STORE] datetime_array: {class_instance.datetime_array[:5]} ... total: {len(class_instance.datetime_array)}")
            ds = xr.Dataset(
                data_vars=data_vars,
                coords={'time': class_instance.datetime_array}
            )
            print(f"[STORE] Dataset variables: {list(ds.data_vars)}")
            
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
            encoding = {var: {} for var in ds.data_vars}  # No compression initially
            
            # Save to zarr
            ds.chunk(chunks).to_zarr(zarr_path, mode='w', encoding=encoding)
            print_manager.zarr_integration(f"Checking if Zarr file exists: {os.path.exists(zarr_path)}")
            if os.path.exists(zarr_path):
                print_manager.zarr_integration(f"Zarr directory contents: {os.listdir(zarr_path)}")
            print_manager.zarr_integration(f"[store_data] Data saved to Zarr store")
            print_manager.status(f"✅ Saved {data_type} data to {zarr_path}")
            return True
            
        except Exception as e:
            print_manager.zarr_integration(f"[store_data] Exception: {e}")
            print_manager.error(f"Error saving {data_type} to Zarr: {e}")
            return False
            
    def load_data(self, data_type, trange):
        """Load data from Zarr stores for given time range"""
        print_manager.zarr_integration(f"[load_data] Called for data_type={data_type}, trange={trange}")
        # Parse time range
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
        
        # Get configuration for this data type
        config = data_types.get(data_type, {})
        file_time_format = config.get('file_time_format', 'daily')
        print_manager.zarr_integration(f"[load_data] file_time_format={file_time_format}")
        
        # Find all zarr stores in the time range
        zarr_paths = self._find_zarr_paths(data_type, start_time, end_time, file_time_format)
        print_manager.zarr_integration(f"[load_data] zarr_paths: {zarr_paths}")
        
        if not zarr_paths:
            print_manager.debug(f"No Zarr data found for {data_type} in range {trange}")
            return None
            
        # Load and concatenate all relevant zarr stores
        print_manager.zarr_integration(f"[load_data] Loading {len(zarr_paths)} Zarr stores")
        
        try:
            print_manager.zarr_integration(f"[load_data] Looping through zarr_paths")
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
            print(f"[LOAD] Loaded dataset variables: {list(combined.data_vars)}")
            print(f"[LOAD] Loaded time: {combined.time.values[:5]} ... total: {len(combined.time.values)}")
            
            # Create a LoadedData object that mimics the class structure
            class LoadedData:
                def __init__(self, ds):
                    self.datetime_array = ds.time.values
                    # Convert to TT2000 for compatibility
                    dt_series = pd.to_datetime(ds.time.values)
                    dt_components = [[dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, int(dt.microsecond / 1000)] for dt in dt_series]
                    self.times = cdflib.cdfepoch.compute_tt2000(dt_components)
                    self.raw_data = {}
                    for var_name in ds.data_vars:
                        self.raw_data[var_name] = ds[var_name].values
                        # Debug print for spe_sf0_pad
                        if data_type == 'spe_sf0_pad':
                            print(f"[DEBUG][ZARR][LOAD] Loaded var '{var_name}': type={type(self.raw_data[var_name])}, shape={getattr(self.raw_data[var_name], 'shape', None)}")
                    self.data = self.raw_data  # Patch: add data attribute for compatibility
                    # Patch: stack br, bt, bn for mag_rtn
                    if data_type == 'mag_RTN' and all(k in self.data for k in ['br', 'bt', 'bn']):
                        self.data['psp_fld_l2_mag_RTN'] = np.stack([
                            self.data['br'],
                            self.data['bt'],
                            self.data['bn']
                        ], axis=1)
                    # Patch: stack br, bt, bn for mag_rtn_4sa
                    if data_type == 'mag_RTN_4sa' and all(k in self.data for k in ['br', 'bt', 'bn']):
                        self.data['psp_fld_l2_mag_RTN_4_Sa_per_Cyc'] = np.stack([
                            self.data['br'],
                            self.data['bt'],
                            self.data['bn']
                        ], axis=1)
                    # Patch: stack bx, by, bz for mag_sc
                    if data_type == 'mag_SC' and all(k in self.data for k in ['bx', 'by', 'bz']):
                        self.data['psp_fld_l2_mag_SC'] = np.stack([
                            self.data['bx'],
                            self.data['by'],
                            self.data['bz']
                        ], axis=1)
                    # Patch: map strahl/centroids for epad.strahl
                    if data_type == 'spe_sf0_pad':
                        if 'strahl' in self.data:
                            self.data['EFLUX_VS_PA_E'] = self.data['strahl']
                        if 'centroids' in self.data:
                            self.data['PITCHANGLE'] = self.data['centroids']
                    print(f"[LOAD] LoadedData.raw_data keys: {list(self.raw_data.keys())}")
                    print(f"[LOAD] LoadedData.datetime_array: {self.datetime_array[:5]} ... total: {len(self.datetime_array)}")
            loaded = LoadedData(combined)
            return loaded
            
        except Exception as e:
            print_manager.zarr_integration(f"[load_data] Exception: {e}")
            print_manager.error(f"Error loading Zarr data for {data_type}: {e}")
            return None
            
    def _get_zarr_path(self, data_type, timestamp, file_time_format):
        """Generate zarr path based on data type and timestamp"""
        print_manager.zarr_integration(f"[_get_zarr_path] Called for data_type={data_type}, timestamp={timestamp}, file_time_format={file_time_format}")
        dt = timestamp
        if isinstance(dt, np.datetime64):
            dt = pd.Timestamp(dt).to_pydatetime()
        # Normalize data_type for consistent file paths
        normalized_data_type = data_type.lower()
        if file_time_format == 'daily':
            # Store daily data in year/month/day.zarr
            zarr_path = os.path.join(self.base_dir, normalized_data_type, 
                               f"{dt.year}", 
                               f"{dt.month:02d}", 
                               f"{dt.day:02d}.zarr")
        elif file_time_format == '6-hour':
            # Store 6-hour data in year/month/day_hour.zarr
            hour = (dt.hour // 6) * 6  # Round to nearest 6-hour block
            zarr_path = os.path.join(self.base_dir, normalized_data_type, 
                               f"{dt.year}", 
                               f"{dt.month:02d}", 
                               f"{dt.day:02d}_{hour:02d}.zarr")
        else:
            # Default path
            zarr_path = os.path.join(self.base_dir, normalized_data_type, 
                              f"{dt.year}_{dt.month:02d}_{dt.day:02d}.zarr")
        print_manager.zarr_integration(f"[_get_zarr_path] Returning path")
        return zarr_path
    
    def _find_zarr_paths(self, data_type, start_time, end_time, file_time_format):
        """Find all zarr paths for a data type within the time range"""
        print_manager.zarr_integration(f"[_find_zarr_paths] Called for data_type={data_type}, start_time={start_time}, end_time={end_time}, file_time_format={file_time_format}")
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
        
        print_manager.zarr_integration(f"[_find_zarr_paths] Returning paths: {zarr_paths}")
        return zarr_paths
        
    def _convert_to_import_format(self, ds, data_type):
        """Convert xarray Dataset to the format expected by the update method"""
        print_manager.zarr_integration(f"[_convert_to_import_format] Called for data_type={data_type}")
        # Create a structure matching what the update methods expect
        class ImportedData:
            def __init__(self):
                self.times = None
                self.data = {}
                
        imported_data = ImportedData()
        
        # Convert Zarr time (numpy.datetime64) to TT2000 for compatibility with class expectations
        # Convert to pandas datetime, then to components, then to TT2000
        dt_series = pd.to_datetime(ds.time.values)
        dt_components = [[dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, int(dt.microsecond / 1000)] for dt in dt_series]
        imported_data.times = cdflib.cdfepoch.compute_tt2000(dt_components)
        
        # Handle variables based on data_type
        if data_type == 'mag_rtn_4sa':
            # Always create 3D array from br, bt, bn if present
            if all(v in ds for v in ['br', 'bt', 'bn']):
                field_data = np.stack([
                    ds['br'].values,
                    ds['bt'].values,
                    ds['bn'].values
                ], axis=1)
                imported_data.data['psp_fld_l2_mag_RTN_4_Sa_per_Cyc'] = field_data
            else:
                # Fallback: try to load any available variable
                for v in ds.data_vars:
                    imported_data.data[v] = ds[v].values
                
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
                
        print_manager.zarr_integration(f"[_convert_to_import_format] Returning imported_data with keys: {list(imported_data.data.keys())}")
        return imported_data
    
__all__ = ['ZarrStorage']