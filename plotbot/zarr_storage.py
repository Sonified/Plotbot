# plotbot/zarr_storage.py

import os
import xarray as xr
import numpy as np
import zarr
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
import pandas as pd
import cdflib
import time

from .print_manager import print_manager
from .data_tracker import global_tracker
from .data_classes.psp_data_types import data_types

def extract_bin_array_for_optimized_storage(arr, n_times, var_name, context):
    """Reduce axis arrays to 1D bin arrays for Zarr storage/loading. Raises if not valid."""
    if isinstance(arr, np.ndarray):
        if arr.ndim == 2:
            if np.allclose(arr, arr[0]):  # Check if every row is the same
                print(f"[DEBUG][ZARR][{context}] Reducing {var_name} from 2D meshgrid to 1D bin array")
                return arr[0]  # Take the first row (the bin array)
            else:
                raise ValueError(f"[ZARR][{context}] {var_name} is 2D but not all rows are identical. Refusing to use as axis array.")
        elif arr.ndim == 1:
            if arr.shape[0] == n_times:  # If the array is 1D and its length matches n_times (number of time steps)
                if np.allclose(arr, arr[0]):  # If all values are the same
                    print(f"[DEBUG][ZARR][{context}] Reducing {var_name} from 1D time series to single bin value array")
                    return np.array([arr[0]])  # Save just the unique value
                else:
                    raise ValueError(f"[ZARR][{context}] {var_name} is 1D and matches time length but values are not identical. Refusing to use as axis array.")
            # else: it's a valid 1D bin array (length = n_bins)
            return arr
        else:
            raise ValueError(f"[ZARR][{context}] {var_name} has unexpected ndim={arr.ndim}. Refusing to use as axis array.")
    return arr

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
        start_total = time.time()
        print_manager.zarr_integration(f"Storing data for {data_type}")
        print_manager.zarr_integration(f"datetime_array length: {len(class_instance.datetime_array)}")
        print_manager.zarr_integration(f"raw_data keys: {list(class_instance.raw_data.keys())}")
        # Debug print for pitch_angle before saving
        if hasattr(class_instance, 'pitch_angle'):
            print(f"[STORE] class_instance.pitch_angle: type={type(class_instance.pitch_angle)}, shape={getattr(class_instance.pitch_angle, 'shape', None)}, value={class_instance.pitch_angle}")
        for k, v in class_instance.raw_data.items():
            print(f"[STORE] raw_data[{k}]: type={type(v)}, shape={getattr(v, 'shape', None)}")
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
            t0 = time.time()
            print_manager.zarr_integration(f"[store_data] Creating data_vars from class_instance.raw_data")
            data_vars = {}
            coords = {}
            coords['time'] = class_instance.datetime_array
            if 'pitch_angle' in class_instance.raw_data and class_instance.raw_data['pitch_angle'] is not None:
                coords['pitch_angle'] = class_instance.raw_data['pitch_angle']
            for var_name, data in class_instance.raw_data.items():
                if data is None or var_name == 'all':
                    continue
                # Do not add pitch_angle as a data_var if it's already a coordinate
                if var_name == 'pitch_angle' and 'pitch_angle' in coords:
                    continue
                # Assign dims based on variable name and shape
                if var_name == 'strahl' and data.ndim == 2:
                    dims = ('time', 'pitch_angle')
                elif var_name == 'centroids' and data.ndim == 1:
                    dims = ('time',)
                elif var_name == 'pitch_angle' and data.ndim == 1:
                    dims = ('pitch_angle',)
                else:
                    # Fallback: auto dims
                    dims = tuple([f"dim_{i}" for i in range(data.ndim)])
                data_vars[var_name] = (dims, data)
            t1 = time.time()
            print(f"[TIMER][ZARR] prepare data_vars/coords: {t1 - t0:.3f} s")
            print(f"[STORE] datetime_array: {class_instance.datetime_array[:5]} ... total: {len(class_instance.datetime_array)}")
            # Merge axis array coords and time coord
            coords['time'] = class_instance.datetime_array
            ds = xr.Dataset(
                data_vars=data_vars,
                coords=coords
            )

            # Add tt2000 times directly to the dataset if available
            if hasattr(class_instance, 'time') and class_instance.time is not None:
                # Ensure the time coordinate exists for alignment
                if 'time' in ds.coords:
                    ds['tt2000'] = xr.DataArray(class_instance.time, dims=['time'], coords={'time': ds.time})
                    print_manager.zarr_integration("[STORE] Added 'tt2000' variable to Zarr dataset.")
                else:
                     print_manager.warning("[STORE] 'time' coordinate missing, cannot align tt2000.")
            else:
                print_manager.warning("[STORE] Could not find 'time' attribute in class_instance to store as tt2000.")

            t2 = time.time()
            print(f"[TIMER][ZARR] create xarray.Dataset: {t2 - t1:.3f} s")
            print(f"[STORE] Dataset variables: {list(ds.data_vars)}")
            print(f"[STORE] Dataset coordinates: {list(ds.coords)}")
            
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
            t3 = time.time()
            print(f"[TIMER][ZARR] chunking logic: {t3 - t2:.3f} s")
            
            # Create zarr path based on data_type and file format
            zarr_path = self._get_zarr_path(data_type, class_instance.datetime_array[0], file_time_format)
            os.makedirs(os.path.dirname(zarr_path), exist_ok=True)
            
            # Apply compression
            encoding = {var: {} for var in ds.data_vars}  # No compression initially
            
            # Save to zarr
            ds.chunk(chunks).to_zarr(zarr_path, mode='w', encoding=encoding)
            t4 = time.time()
            print(f"[TIMER][ZARR] save to Zarr: {t4 - t3:.3f} s")
            print_manager.zarr_integration(f"Checking if Zarr file exists: {os.path.exists(zarr_path)}")
            if os.path.exists(zarr_path):
                print_manager.zarr_integration(f"Zarr directory contents: {os.listdir(zarr_path)}")
            print_manager.zarr_integration(f"[store_data] Data saved to Zarr store")
            print_manager.status(f"✅ Saved {data_type} data to {zarr_path}")
            print(f"[TIMER][ZARR] TOTAL store_data duration: {t4 - start_total:.3f} s")
            return True
            
        except Exception as e:
            print_manager.zarr_integration(f"[store_data] Exception: {e}")
            print_manager.error(f"Error saving {data_type} to Zarr: {e}")
            return False
            
    def load_data(self, data_type, trange):
        """Load data from Zarr stores for given time range"""
        print_manager.zarr_integration(f"[load_data] Called for data_type={data_type}, trange={trange}")
        start_total = time.time()
        # Parse time range
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
        # Get configuration for this data type
        config = data_types.get(data_type, {})
        file_time_format = config.get('file_time_format', 'daily')
        print_manager.zarr_integration(f"[load_data] file_time_format={file_time_format}")
        t0 = time.time()
        zarr_paths = self._find_zarr_paths(data_type, start_time, end_time, file_time_format)
        t1 = time.time()
        print(f"[TIMER][ZARR] find zarr paths: {t1 - t0:.3f} s")
        print_manager.zarr_integration(f"[load_data] zarr_paths: {zarr_paths}")
        if not zarr_paths:
            print_manager.debug(f"No Zarr data found for {data_type} in range {trange}")
            return None
        print_manager.zarr_integration(f"[load_data] Loading {len(zarr_paths)} Zarr stores")
        try:
            t2 = time.time()
            datasets = []
            for path in zarr_paths:
                if os.path.exists(path):
                    ds = xr.open_zarr(path)
                    datasets.append(ds)
            t3 = time.time()
            print(f"[TIMER][ZARR] load datasets: {t3 - t2:.3f} s")
            if not datasets:
                return None
            if len(datasets) == 1:
                combined = datasets[0]
            else:
                combined = xr.concat(datasets, dim='time')
            t4 = time.time()
            print(f"[TIMER][ZARR] concatenate datasets: {t4 - t3:.3f} s")
            # Add requested debug print for combined dataset size
            if data_type == 'mag_RTN_4sa':
                print(f"[DEBUG][ZARR][LOAD] mag_RTN_4sa dataset size: {len(combined.time)} timestamps")

            # Define the inner class here
            class LoadedData:
                def __init__(self, ds):
                    print_manager.zarr_integration("[DEBUG][ZARR][LOAD] Entered LoadedData.__init__")
                    self.datetime_array = ds.time.values
                    print_manager.zarr_integration("[DEBUG][ZARR][LOAD] datetime_array loaded")

                    # --- TT2000 Handling --- 
                    # Fast path: Load pre-computed TT2000 if it exists in the Zarr store
                    if 'tt2000' in ds:
                        self.times = ds.tt2000.values
                        print_manager.zarr_integration("[DEBUG][ZARR][LOAD] TT2000 times loaded directly from Zarr.")
                    else:
                        # Slow fallback path: Compute TT2000 if not found (should only happen on first load)
                        print_manager.warning("[DEBUG][ZARR][LOAD] TT2000 not found in Zarr, calculating fallback...")
                        try:
                            dt_series = pd.to_datetime(self.datetime_array, errors='coerce') 
                            valid_dt_series = dt_series.dropna()
                            if len(valid_dt_series) == 0:
                                 raise ValueError("No valid datetime values for TT2000 calculation.")
                            dt_components = [
                                [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, int(dt.microsecond / 1000)] 
                                for dt in valid_dt_series
                            ]
                            computed_times = cdflib.cdfepoch.compute_tt2000(dt_components)
                            self.times = np.full(len(dt_series), np.nan, dtype='int64') 
                            self.times[dt_series.notna()] = computed_times
                            print_manager.zarr_integration(f"[DEBUG][ZARR][LOAD] TT2000 times calculated (fallback) for {len(computed_times)} timestamps.")
                        except Exception as e:
                             print_manager.error(f"[ERROR][ZARR][LOAD] Failed TT2000 fallback: {e}")
                             self.times = None
                    # --- End TT2000 Handling ---
                    
                    self.raw_data = {}
                    print_manager.zarr_integration('[DEBUG][ZARR][LOAD] raw_data dict initialized')
                    
                    # Load main data variables (excluding tt2000 if loaded directly)
                    for var_name in ds.data_vars:
                        if var_name != 'tt2000': 
                            print_manager.zarr_integration(f"[DEBUG][ZARR][LOAD] Attempting to load var: {var_name}")
                            self.raw_data[var_name] = ds[var_name].values
                            print_manager.zarr_integration(f"[DEBUG][ZARR][LOAD] Finished loading var: {var_name}")
                            print_manager.zarr_integration(f"[DEBUG][ZARR][LOAD] Loaded var '{var_name}': type={type(self.raw_data[var_name])}, shape={getattr(self.raw_data[var_name], 'shape', 'N/A')}")
                    print_manager.zarr_integration("[DEBUG][ZARR][LOAD] Data vars loaded into raw_data")
                    
                    # Also check ds.coords for axis arrays saved as coordinates
                    for coord_name in ['pitch_angle', 'energy_vals', 'theta_vals', 'phi_vals']:
                        if coord_name in ds.coords and coord_name not in self.raw_data:
                            arr = ds.coords[coord_name].values
                            self.raw_data[coord_name] = arr
                            if data_type == 'spe_sf0_pad':
                                print(f"[DEBUG][ZARR][LOAD] Loaded coord '{coord_name}': type={type(arr)}, shape: {getattr(arr, 'shape', None)}")
                    print('[DEBUG][ZARR][LOAD] Coords loaded into raw_data')
                    self.data = self.raw_data  # Patch: add data attribute for compatibility
                    print('[DEBUG][ZARR][LOAD] self.data assigned')
                    # Patch: stack br, bt, bn for mag_rtn
                    if data_type == 'mag_RTN' and all(k in self.data for k in ['br', 'bt', 'bn']):
                        self.data['psp_fld_l2_mag_RTN'] = np.stack([
                            self.data['br'],
                            self.data['bt'],
                            self.data['bn']
                        ], axis=1)
                        print('[DEBUG][ZARR][LOAD] psp_fld_l2_mag_RTN stacked')
                    # Patch: stack br, bt, bn for mag_rtn_4sa
                    if data_type == 'mag_RTN_4sa' and all(k in self.data for k in ['br', 'bt', 'bn']):
                        self.data['psp_fld_l2_mag_RTN_4_Sa_per_Cyc'] = np.stack([
                            self.data['br'],
                            self.data['bt'],
                            self.data['bn']
                        ], axis=1)
                        print('[DEBUG][ZARR][LOAD] psp_fld_l2_mag_RTN_4_Sa_per_Cyc stacked')
                    # Patch: stack bx, by, bz for mag_sc
                    if data_type == 'mag_SC' and all(k in self.data for k in ['bx', 'by', 'bz']):
                        self.data['psp_fld_l2_mag_SC'] = np.stack([
                            self.data['bx'],
                            self.data['by'],
                            self.data['bz']
                        ], axis=1)
                        print('[DEBUG][ZARR][LOAD] psp_fld_l2_mag_SC stacked')
                    # Patch: map strahl/centroids for epad.strahl
                    if data_type == 'spe_sf0_pad':
                        if 'strahl' in self.data:
                            self.data['EFLUX_VS_PA_E'] = self.data['strahl']
                            print('[DEBUG][ZARR][LOAD] EFLUX_VS_PA_E mapped from strahl')
                        # Do NOT map centroids to PITCHANGLE; only set PITCHANGLE if a static bin array is present
                        if 'pitch_angle' in self.data:
                            self.data['PITCHANGLE'] = self.data['pitch_angle']
                            print('[DEBUG][ZARR][LOAD] PITCHANGLE mapped from pitch_angle')
                    print(f"[LOAD] LoadedData.raw_data keys: {list(self.raw_data.keys())}")
                    print(f"[LOAD] LoadedData.datetime_array: {self.datetime_array[:5]} ... total: {len(self.datetime_array)}")
                    print(f"[LOAD] All coordinates after loading:")
                    for coord in ds.coords:
                        arr = ds.coords[coord].values
                        print(f"  - {coord}: shape={arr.shape}, first 5 values={arr[:5] if hasattr(arr, '__getitem__') else arr}")
                    # Reconstruct times_mesh and pitch_mesh for spectral plotting if needed
                    if data_type in ['spe_sf0_pad', 'spe_af0_pad'] and 'strahl' in self.raw_data:
                        print('[DEBUG][ZARR][LOAD] Entering meshgrid reconstruction block')
                        # Convert datetime values to numeric for plotting compatibility
                        if np.issubdtype(self.datetime_array.dtype, np.datetime64):
                            numeric_times = (self.datetime_array - self.datetime_array[0]) / np.timedelta64(1, 's')
                            print('[DEBUG][ZARR][LOAD] numeric_times created from datetime64')
                        else:
                            numeric_times = (pd.to_datetime(self.datetime_array) - pd.to_datetime(self.datetime_array[0])).total_seconds()
                            print('[DEBUG][ZARR][LOAD] numeric_times created using pd.to_datetime')
                        pitch_angle = self.raw_data['pitch_angle']
                        time_mesh, pitch_mesh = np.meshgrid(
                            numeric_times,
                            pitch_angle,
                            indexing='ij'
                        )
                        print('[DEBUG][ZARR][LOAD] np.meshgrid completed')
                        self.times_mesh = time_mesh
                        self.pitch_mesh = pitch_mesh
                        if 'pitch_mesh' not in self.raw_data:
                            self.raw_data['pitch_mesh'] = pitch_mesh
                        print(f"[DEBUG][ZARR][LOAD] times_mesh shape: {self.times_mesh.shape}, pitch_mesh shape: {self.pitch_mesh.shape}, dtype: {self.times_mesh.dtype}")
                        print(f"[DEBUG][ZARR][LOAD] First 5 rows of times_mesh: {self.times_mesh[:5]}")
                        print(f"[DEBUG][ZARR][LOAD] First 5 rows of pitch_mesh: {self.pitch_mesh[:5]}")
            # --- Now, time the instantiation outside the class definition ---
            t5_init = time.time() # Start timer for init
            loaded = LoadedData(combined) # Instantiate the class
            t6_init = time.time() # End timer for init
            print(f"[TIMER][ZARR] LoadedData __init__: {t6_init - t5_init:.3f} s") 
            # --- End Timing --- 
            
            t7 = time.time()
            print(f"[TIMER][ZARR] TOTAL load_data duration: {t7 - start_total:.3f} s")
            return loaded
        except Exception as e:
            print_manager.error(f"Error loading Zarr data for {data_type}: {e}")
            # Optionally re-raise or return a specific error indicator
            return None # Indicate failure
            
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