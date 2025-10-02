# plotbot/data_cubby.py

from .print_manager import print_manager, format_datetime_for_log
import numpy as np
import pandas as pd
from datetime import datetime
import sys
import inspect
import copy
import cdflib
from typing import Optional, List, Dict, Tuple, Any
import time as timer
from functools import wraps
import gc
from numba import jit, prange

def timer_decorator(timer_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = timer.perf_counter()
            result = func(*args, **kwargs)
            end_time = timer.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            print_manager.speed_test(f"⏱️ [{timer_name}] {func.__name__}: {duration_ms:.2f}ms")
            return result
        return wrapper
    return decorator

# --- Import Data Class Types for Mapping ---
# Assuming these classes are defined elsewhere and accessible
# We need the actual class types, not just the instances
from .data_classes.psp_mag_rtn_4sa import mag_rtn_4sa_class
from .data_classes.psp_mag_rtn import mag_rtn_class
from .data_classes.psp_mag_sc_4sa import mag_sc_4sa_class
from .data_classes.psp_mag_sc import mag_sc_class
from .data_classes.psp_electron_classes import epad_strahl_class, epad_strahl_high_res_class
from .data_classes.psp_proton import proton_class
from .data_classes.psp_proton_hr import proton_hr_class
# Note: proton_fits and ham are handled differently in get_data, so maybe not needed here?
# from .data_classes.psp_proton_fits_classes import proton_fits_class
from .data_classes.psp_ham_classes import ham_class, ham
# WIND satellite data classes
from .data_classes.wind_mfi_classes import wind_mfi_h2_class
from .data_classes.wind_3dp_classes import wind_3dp_elpd_class
from .data_classes.wind_3dp_pm_classes import wind_3dp_pm_class
from .data_classes.psp_alpha_classes import psp_alpha_class
from .data_classes.psp_qtn_classes import psp_qtn_class
from .data_classes.psp_dfb_classes import psp_dfb_class
from .data_classes.psp_orbit import psp_orbit_class
from .data_classes.psp_span_vdf import psp_span_vdf_class
from .data_classes.wind_swe_h5_classes import wind_swe_h5_class
from .data_classes.wind_swe_h1_classes import wind_swe_h1_class

from .data_import import DataObject # Import the type hint for raw data object

# print_manager.show_processing = True # SETTING THIS EARLY

class UltimateMergeEngine:
    """
    The most optimized array merging system in the known universe.
    Designed to handle billions of data points without breaking a sweat.
    """
    
    def __init__(self, chunk_size: int = 10_000_000, use_parallel: bool = True):
        self.chunk_size = chunk_size
        self.use_parallel = use_parallel
        self.stats = {
            'merges_performed': 0,
            'total_records_processed': 0,
            'total_time': 0.0,
            'avg_records_per_second': 0.0
        }
    
    @staticmethod
    @jit(nopython=True, parallel=True, cache=True)
    def _fast_unique_merge(arr1, arr2):
        """
        Ultra-fast numba-compiled unique merge of two sorted arrays.
        This is the secret sauce - compiled to machine code.
        """
        len1, len2 = len(arr1), len(arr2)
        max_len = len1 + len2
        result = np.empty(max_len, dtype=arr1.dtype)
        
        i = j = k = 0
        
        # Main merge loop - optimized for speed
        while i < len1 and j < len2:
            if arr1[i] < arr2[j]:
                result[k] = arr1[i]
                i += 1
            elif arr1[i] > arr2[j]:
                result[k] = arr2[j]
                j += 1
            else:  # Equal - take from arr2 (newer data)
                result[k] = arr2[j]
                i += 1
                j += 1
            k += 1
        
        # Copy remaining elements
        while i < len1:
            result[k] = arr1[i]
            i += 1
            k += 1
        
        while j < len2:
            result[k] = arr2[j]
            j += 1
            k += 1
        
        return result[:k]
    
    @staticmethod
    @jit(nopython=True, parallel=True, cache=True)
    def _fast_searchsorted_indices(sorted_times, target_times):
        """
        Lightning-fast searchsorted replacement using binary search.
        Parallelized across chunks for maximum throughput.
        """
        n = len(target_times)
        indices = np.empty(n, dtype=np.int64)
        
        for i in prange(n):
            # Binary search for each element
            left, right = 0, len(sorted_times)
            target = target_times[i]
            
            while left < right:
                mid = (left + right) // 2
                if sorted_times[mid] < target:
                    left = mid + 1
                else:
                    right = mid
            
            indices[i] = left
        
        return indices
    
    def _chunk_process_large_arrays(self, final_times, existing_times, existing_data, new_times, new_data):
        """
        Process massive arrays in chunks to avoid memory explosion.
        Uses streaming processing to handle datasets larger than RAM.
        """
        print_manager.datacubby(f"🚀 CHUNKED PROCESSING: {len(final_times):,} total records")
        
        # Pre-allocate result arrays for maximum efficiency
        merged_data = {}
        all_keys = set(existing_data.keys()) | set(new_data.keys())
        
        for key in all_keys:
            if key == 'all':
                continue
                
            # Determine array properties
            if key in existing_data and existing_data[key] is not None:
                sample_arr = existing_data[key]
            else:
                sample_arr = new_data[key]
            
            # Pre-allocate with correct shape and dtype
            if sample_arr.ndim > 1:
                shape = (len(final_times),) + sample_arr.shape[1:]
            else:
                shape = (len(final_times),)
            
            merged_data[key] = np.full(shape, np.nan, dtype=sample_arr.dtype)
        
        # Process existing data in chunks
        if len(existing_times) > 0:
            print_manager.datacubby("📥 Processing existing data...")
            
            chunk_count = (len(existing_times) - 1) // self.chunk_size + 1
            for chunk_idx in range(chunk_count):
                start_idx = chunk_idx * self.chunk_size
                end_idx = min(start_idx + self.chunk_size, len(existing_times))
                
                # Get indices for this chunk
                chunk_times = existing_times[start_idx:end_idx]
                chunk_indices = self._fast_searchsorted_indices(final_times, chunk_times)
                
                # Copy data for this chunk
                for key in existing_data.keys():
                    if key == 'all' or existing_data[key] is None:
                        continue
                    
                    chunk_data = existing_data[key][start_idx:end_idx]
                    merged_data[key][chunk_indices] = chunk_data
                
                if chunk_count > 1:
                    print_manager.datacubby(f"  Chunk {chunk_idx + 1}/{chunk_count} complete")
        
        # Process new data in chunks
        if len(new_times) > 0:
            print_manager.datacubby("📤 Processing new data...")
            
            chunk_count = (len(new_times) - 1) // self.chunk_size + 1
            for chunk_idx in range(chunk_count):
                start_idx = chunk_idx * self.chunk_size
                end_idx = min(start_idx + self.chunk_size, len(new_times))
                
                # Get indices for this chunk
                chunk_times = new_times[start_idx:end_idx]
                chunk_indices = self._fast_searchsorted_indices(final_times, chunk_times)
                
                # Copy data for this chunk (overwrites existing for duplicates)
                for key in new_data.keys():
                    if key == 'all' or new_data[key] is None:
                        continue
                    
                    chunk_data = new_data[key][start_idx:end_idx]
                    merged_data[key][chunk_indices] = chunk_data
                
                if chunk_count > 1:
                    print_manager.datacubby(f"  Chunk {chunk_idx + 1}/{chunk_count} complete")
        
        return merged_data
    
    def merge_arrays(self, existing_times, existing_raw_data, new_times, new_raw_data):
        """
        The ultimate merge function that can handle any dataset size.
        Auto-switches between strategies based on data size.
        """
        start_time = timer.perf_counter()
        
        print_manager.datacubby("\n🔥 ULTIMATE MERGE ENGINE ACTIVATED 🔥")
        
        # Input validation
        if new_times is None or len(new_times) == 0:
            print_manager.datacubby("❌ No new data to merge")
            return None, None
        
        if existing_times is None or len(existing_times) == 0:
            print_manager.datacubby("✨ First data load - no merge needed")
            return new_times, new_raw_data
        
        # Performance metrics
        existing_count = len(existing_times)
        new_count = len(new_times)
        total_potential = existing_count + new_count
        
        print_manager.datacubby(f"📊 MERGE STATS:")
        print_manager.datacubby(f"   Existing: {existing_count:,} records")
        print_manager.datacubby(f"   New: {new_count:,} records")
        print_manager.datacubby(f"   Potential total: {total_potential:,} records")
        
        # Quick overlap check to avoid unnecessary work
        if existing_times[-1] < new_times[0]:
            print_manager.datacubby("🚀 NO OVERLAP - Simple concatenation")
            final_times = np.concatenate([existing_times, new_times])
            
            merged_data = {}
            all_keys = set(existing_raw_data.keys()) | set(new_raw_data.keys())
            
            for key in all_keys:
                if key == 'all':
                    continue
                
                existing_arr = existing_raw_data.get(key)
                new_arr = new_raw_data.get(key)
                
                if existing_arr is not None and new_arr is not None:
                    merged_data[key] = np.concatenate([existing_arr, new_arr])
                elif existing_arr is not None:
                    merged_data[key] = existing_arr.copy()
                elif new_arr is not None:
                    merged_data[key] = new_arr.copy()
            
        else:
            # Full merge required
            print_manager.datacubby("🔄 OVERLAP DETECTED - Full merge required")
            
            # Use ultra-fast compiled merge for times
            print_manager.datacubby("⚡ Computing unique merged times...")
            final_times = self._fast_unique_merge(existing_times, new_times)
            unique_count = len(final_times)
            
            print_manager.datacubby(f"✅ Unique times: {unique_count:,} records ({total_potential - unique_count:,} duplicates removed)")
            
            # Choose strategy based on data size
            if unique_count > 50_000_000:  # 50M+ records
                print_manager.datacubby("🏭 INDUSTRIAL MODE: Using chunked processing")
                merged_data = self._chunk_process_large_arrays(
                    final_times, existing_times, existing_raw_data, new_times, new_raw_data
                )
            else:
                print_manager.datacubby("🏎️ SPEED MODE: Using vectorized processing")
                
                # Fast vectorized approach for smaller datasets
                existing_indices = self._fast_searchsorted_indices(final_times, existing_times)
                new_indices = self._fast_searchsorted_indices(final_times, new_times)
                
                merged_data = {}
                all_keys = set(existing_raw_data.keys()) | set(new_raw_data.keys())
                
                for key in all_keys:
                    if key == 'all':
                        continue
                    
                    existing_arr = existing_raw_data.get(key)
                    new_arr = new_raw_data.get(key)
                    
                    # Determine final array shape and dtype
                    if existing_arr is not None:
                        dtype = existing_arr.dtype
                        shape = (unique_count,) + existing_arr.shape[1:] if existing_arr.ndim > 1 else (unique_count,)
                    elif new_arr is not None:
                        dtype = new_arr.dtype
                        shape = (unique_count,) + new_arr.shape[1:] if new_arr.ndim > 1 else (unique_count,)
                    else:
                        # Both arrays are None - skip this key
                        print_manager.datacubby(f"⚠️ Skipping key '{key}' - both arrays are None")
                        continue
                    
                    # Pre-allocate with NaN for numerical types
                    if np.issubdtype(dtype, np.number):
                        final_array = np.full(shape, np.nan, dtype=dtype)
                    else:
                        final_array = np.empty(shape, dtype=dtype)
                    
                    # Vectorized assignment
                    if existing_arr is not None:
                        final_array[existing_indices] = existing_arr
                    if new_arr is not None:
                        final_array[new_indices] = new_arr  # Overwrites duplicates
                    
                    merged_data[key] = final_array
        
        # Reconstruct 'all' array if needed
        if all(key in merged_data for key in ['br', 'bt', 'bn']):
            merged_data['all'] = [merged_data['br'], merged_data['bt'], merged_data['bn']]
        
        # Force garbage collection for large merges
        if total_potential > 10_000_000:
            gc.collect()
        
        # Performance tracking
        end_time = timer.perf_counter()
        duration = end_time - start_time
        records_per_second = len(final_times) / duration if duration > 0 else 0
        
        self.stats['merges_performed'] += 1
        self.stats['total_records_processed'] += len(final_times)
        self.stats['total_time'] += duration
        self.stats['avg_records_per_second'] = self.stats['total_records_processed'] / self.stats['total_time']
        
        print_manager.datacubby(f"🏁 MERGE COMPLETE!")
        print_manager.datacubby(f"   Final records: {len(final_times):,}")
        print_manager.datacubby(f"   Duration: {duration:.2f}s")
        print_manager.datacubby(f"   Speed: {records_per_second:,.0f} records/sec")
        print_manager.datacubby(f"   Session total: {self.stats['total_records_processed']:,} records")
        print_manager.datacubby(f"   Session avg: {self.stats['avg_records_per_second']:,.0f} records/sec")
        
        return final_times, merged_data

# Global instance - replace your existing merge function
ultimate_merger = UltimateMergeEngine(chunk_size=5_000_000, use_parallel=True)

class data_cubby:
    """
    Enhanced data storage system that intelligently manages time series data
    with rigorous type checking and data integrity validation.
    """
    cubby = {}
    class_registry = {}
    subclass_registry = {}

    # --- Map data_type strings to their corresponding class types ---
    _CLASS_TYPE_MAP = {
        'mag_rtn_4sa': mag_rtn_4sa_class,
        'mag_rtn': mag_rtn_class,
        'mag_sc_4sa': mag_sc_4sa_class,
        'mag_sc': mag_sc_class,
        'spi_sf00_l3_mom': proton_class,
        'spi_af00_l3_mom': proton_hr_class,
        'spe_sf0_pad': epad_strahl_class,
        'spe_af0_pad': epad_strahl_high_res_class,
        'proton_hr': proton_hr_class,
        'epad': epad_strahl_class,
        'epad_hr': epad_strahl_high_res_class,
        'ham': ham_class,
        'sqtn_rfs_v1v2': psp_qtn_class,  # QTN (Quasi-Thermal Noise) electron density and temperature
        'psp_orbit_data': psp_orbit_class,   # PSP orbital/positional data
        'psp_orbit': psp_orbit_class,        # PSP orbital/positional data (cubby_key mapping)
        # PSP FIELDS DFB electric field spectra data types
        'dfb_ac_spec_dv12hg': psp_dfb_class,  # AC spectrum dv12 
        'dfb_ac_spec_dv34hg': psp_dfb_class,  # AC spectrum dv34
        'dfb_dc_spec_dv12hg': psp_dfb_class,  # DC spectrum dv12
        # WIND satellite data types
        'wind_mfi_h2': wind_mfi_h2_class,
        'wind_3dp_elpd': wind_3dp_elpd_class,
        'wind_3dp_pm': wind_3dp_pm_class,
    'spi_sf0a_l3_mom': psp_alpha_class,
        'wind_swe_h5': wind_swe_h5_class,
        'wind_swe_h1': wind_swe_h1_class,
        'psp_span_vdf': psp_span_vdf_class,  # PSP SPAN-I VDF data
        # Add other standard CDF types here as needed
    }

    @classmethod
    def _add_cdf_classes_to_map(cls):
        """
        Dynamically add CDF classes from custom_classes to the _CLASS_TYPE_MAP.
        This is called during module initialization to register auto-generated CDF classes.
        """
        try:
            import os
            from pathlib import Path
            import importlib
            
            # Get path to custom_classes directory
            current_dir = Path(__file__).parent
            custom_classes_dir = current_dir / "data_classes" / "custom_classes"
            
            if not custom_classes_dir.exists():
                return
            
            # Find all Python files in custom_classes (auto-generated CDF classes)
            cdf_class_files = list(custom_classes_dir.glob("*.py"))
            cdf_class_files = [f for f in cdf_class_files if not f.name.startswith("__")]
            
            for py_file in cdf_class_files:
                class_name = py_file.stem  # e.g., 'psp_waves_auto'
                
                try:
                    # Import the module dynamically
                    module = importlib.import_module(f"plotbot.data_classes.custom_classes.{class_name}")
                    
                    # Get the class (follows pattern: class_name + '_class')
                    class_type = getattr(module, f"{class_name}_class", None)
                    
                    if class_type:
                        # Add to the class type map
                        cls._CLASS_TYPE_MAP[class_name] = class_type
                        print_manager.datacubby(f"[CDF_REGISTRATION_DEBUG] Added CDF class to type map: {class_name} -> {class_type.__name__}")
                        print_manager.datacubby(f"[CDF_REGISTRATION_DEBUG] Full map now has {len(cls._CLASS_TYPE_MAP)} entries")
                    
                except Exception as e:
                    print_manager.warning(f"Failed to add CDF class {class_name} to type map: {e}")
                    
        except Exception as e:
            print_manager.warning(f"Failed to scan for CDF classes: {e}")

    def __init__(self):
        """
        Initialize the DataCubby instance.
        This is where we can register pre-existing global data instances
        that DataCubby needs to manage from the start.
        """
        print_manager.datacubby("DataCubby instance initializing...")
        
        # Stash the globally defined `ham` instance.
        # `ham` should be imported at the module level from .data_classes.psp_ham_classes
        # `self.stash` correctly calls the classmethod `stash`.
        try:
            global_ham_instance = globals().get('ham')
            if global_ham_instance is not None and isinstance(global_ham_instance, ham_class):
                self.stash(global_ham_instance, class_name='ham')
                print_manager.datacubby("Successfully stashed global 'ham' instance during DataCubby initialization.")
            else:
                # This warning helps diagnose if `ham` wasn't imported as expected before DataCubby instantiation.
                print_manager.warning("Global 'ham' instance for stashing not found or of incorrect type during DataCubby __init__. Expected 'ham' to be an instance of 'ham_class'.")
        except Exception as e:
            print_manager.error(f"CRITICAL STARTUP ERROR: Failed to stash global 'ham' instance during DataCubby __init__: {e}")
            # Depending on application design, one might want to re-raise e or handle it more severely.

    @classmethod
    def _get_class_type_from_string(cls, data_type_str):
        """Helper to get class type from string using the map."""
        result = cls._CLASS_TYPE_MAP.get(data_type_str.lower())
        print_manager.datacubby(f"[CLASS_TYPE_DEBUG] Looking up '{data_type_str}' -> '{data_type_str.lower()}' -> {result}")
        if not result:
            print_manager.datacubby(f"[CLASS_TYPE_DEBUG] Available keys in _CLASS_TYPE_MAP: {list(cls._CLASS_TYPE_MAP.keys())}")
        return result

    @classmethod
    def stash(cls, obj, class_name=None, subclass_name=None):
        """Store object with class and subclass tracking, intelligently merging time series data."""
        print_manager.datacubby("\n=== Stashing Debug (INSIDE DATA CUBBY)===")
        frame = inspect.currentframe().f_back
        caller_info = f"{frame.f_code.co_filename}:{frame.f_lineno}"
        print_manager.datacubby(f"STASH CALLER: {caller_info}")
        
        # Normalize case of class_name if provided
        if class_name:
            class_name = class_name.lower()
            
        identifier = f"{class_name}.{subclass_name}" if class_name and subclass_name else class_name
        print_manager.datacubby(f"Stashing with identifier: {identifier}")
        
        # Type check for incoming object
        print_manager.datacubby(f"STASH TYPE CHECK - Object type: {type(obj)}")
        
        # Debug datetime_array if present
        if hasattr(obj, 'datetime_array') and obj.datetime_array is not None:
            print_manager.datacubby(f"STASH INPUT - datetime_array type: {type(obj.datetime_array)}")
            if len(obj.datetime_array) > 0:
                print_manager.datacubby(f"STASH INPUT - datetime_array element type: {type(obj.datetime_array[0])}")
                print_manager.datacubby(f"STASH INPUT - datetime_array shape: {obj.datetime_array.shape}")
                print_manager.datacubby(f"STASH INPUT - datetime_array first few elements: {obj.datetime_array[:5]}")
                print_manager.datacubby(f"STASH INPUT - datetime_array range: {obj.datetime_array[0]} to {obj.datetime_array[-1]}")
            else:
                print_manager.datacubby(f"STASH INPUT - datetime_array is empty")
        else:
            print_manager.datacubby(f"STASH INPUT - No datetime_array attribute found")
            
        # Debug raw_data if present
        if hasattr(obj, 'raw_data') and obj.raw_data is not None:
            print_manager.datacubby(f"STASH INPUT - raw_data keys: {obj.raw_data.keys()}")
            for key, value in obj.raw_data.items():
                if isinstance(value, list):
                    print_manager.datacubby(f"STASH INPUT - raw_data[{key}] is a list of length {len(value)}")
                    if value and len(value) > 0:
                        for i, item in enumerate(value):
                            if hasattr(item, 'shape'):
                                print_manager.datacubby(f"STASH INPUT - raw_data[{key}][{i}] type: {type(item)}, shape: {item.shape}")
                            else:
                                print_manager.datacubby(f"STASH INPUT - raw_data[{key}][{i}] type: {type(item)}")
                elif hasattr(value, 'shape'):
                    print_manager.datacubby(f"STASH INPUT - raw_data[{key}] type: {type(value)}, shape: {value.shape}")
                else:
                    print_manager.datacubby(f"STASH INPUT - raw_data[{key}] type: {type(value)}")
        else:
            print_manager.datacubby(f"STASH INPUT - No raw_data attribute found")
        
        # Check if we already have this object and if it has time series data
        print_manager.datacubby(f"STASH MERGE CHECK - Looking for existing object with class_name: {class_name}")
        existing_obj = cls.class_registry.get(class_name)
        
        if existing_obj:
            print_manager.datacubby(f"STASH MERGE CHECK - Found existing object of type: {type(existing_obj)}")
            # Debug existing object datetime_array
            if hasattr(existing_obj, 'datetime_array') and existing_obj.datetime_array is not None:
                if len(existing_obj.datetime_array) > 0:
                    print_manager.datacubby(f"STASH MERGE CHECK - Existing datetime_array type: {type(existing_obj.datetime_array)}")
                    print_manager.datacubby(f"STASH MERGE CHECK - Existing datetime_array element type: {type(existing_obj.datetime_array[0])}")
                    print_manager.datacubby(f"STASH MERGE CHECK - Existing datetime_array shape: {existing_obj.datetime_array.shape}")
                    print_manager.datacubby(f"STASH MERGE CHECK - Existing datetime_array range: {existing_obj.datetime_array[0]} to {existing_obj.datetime_array[-1]}")
                else:
                    print_manager.datacubby(f"STASH MERGE CHECK - Existing datetime_array is empty")
            else:
                print_manager.datacubby(f"STASH MERGE CHECK - No existing datetime_array found")
        else:
            print_manager.datacubby(f"STASH MERGE CHECK - No existing object found")
            
        # Perform merge if both objects have datetime_array
        # Get a copy of the existing object for comparison
        existing_obj_copy = copy.deepcopy(existing_obj) if existing_obj else None

        # Perform merge with the copy
        if existing_obj_copy and hasattr(existing_obj_copy, 'datetime_array') and hasattr(obj, 'datetime_array'):
            if existing_obj_copy.datetime_array is not None and obj.datetime_array is not None:
                if len(existing_obj_copy.datetime_array) > 0 and len(obj.datetime_array) > 0:
                    print_manager.datacubby(f"STASH MERGE - Both objects have datetime_array, attempting to merge time series data for {class_name}")
                    
                    # Both existing and new object have time data - attempt to merge them using the copy
                    if cls._merge_arrays(existing_obj_copy.datetime_array, existing_obj_copy.raw_data, obj.datetime_array, obj.raw_data):
                        print_manager.datacubby(f"STASH MERGE - Successfully merged time series data for {class_name}")
                        
                        # Update class registry with the merged result
                        cls.cubby[identifier] = existing_obj_copy
                        if class_name:
                            cls.class_registry[class_name] = existing_obj_copy
                        if subclass_name:
                            cls.subclass_registry[subclass_name] = existing_obj_copy
                        
                        # Final type check for returned object (the merged copy)
                        print_manager.datacubby(f"STASH OUTPUT - Returned object type after merge: {type(existing_obj_copy)}")
                        if hasattr(existing_obj_copy, 'datetime_array') and existing_obj_copy.datetime_array is not None:
                            print_manager.datacubby(f"STASH OUTPUT - Final datetime_array type: {type(existing_obj_copy.datetime_array)}")
                            if len(existing_obj_copy.datetime_array) > 0:
                                print_manager.datacubby(f"STASH OUTPUT - Final datetime_array element type: {type(existing_obj_copy.datetime_array[0])}")
                                print_manager.datacubby(f"STASH OUTPUT - Final datetime_array shape: {existing_obj_copy.datetime_array.shape}")
                                print_manager.datacubby(f"STASH OUTPUT - Final datetime_array range: {existing_obj_copy.datetime_array[0]} to {existing_obj_copy.datetime_array[-1]}")
                        
                        # Return the existing object (the merged copy) since it now contains the merged data
                        print_manager.datacubby("=== End Stashing Debug (LEAVING DATA CUBBY)===\n")
                        return existing_obj_copy # Return the merged copy
                    else:
                        print_manager.datacubby(f"STASH MERGE - Merge attempt failed, proceeding with normal stashing of the new object")
                else:
                    print_manager.datacubby(f"STASH MERGE - One or both datetime_arrays are empty, skipping merge")
            else:
                print_manager.datacubby(f"STASH MERGE - One or both datetime_arrays are None, skipping merge")
        else:
            print_manager.datacubby(f"STASH MERGE - One or both objects missing datetime_array or no existing object, skipping merge")
        
        # If merge didn't happen or failed, proceed with normal stashing of the *new* object
        cls.cubby[identifier] = obj
        if class_name:
            cls.class_registry[class_name] = obj
            print_manager.datacubby(f"STASH STORE - Stored in class_registry: {class_name}")
            
        if subclass_name:
            cls.subclass_registry[subclass_name] = obj
            print_manager.datacubby(f"STASH STORE - Stored in subclass_registry: {subclass_name}")
        
        # Final type check for stored object
        print_manager.datacubby(f"STASH OUTPUT - Stored object type: {type(obj)}")
        if hasattr(obj, 'datetime_array') and obj.datetime_array is not None:
            print_manager.datacubby(f"STASH OUTPUT - Final datetime_array type: {type(obj.datetime_array)}")
            if len(obj.datetime_array) > 0:
                print_manager.datacubby(f"STASH OUTPUT - Final datetime_array element type: {type(obj.datetime_array[0])}")
                print_manager.datacubby(f"STASH OUTPUT - Final datetime_array shape: {obj.datetime_array.shape}")
                print_manager.datacubby(f"STASH OUTPUT - Final datetime_array range: {obj.datetime_array[0]} to {obj.datetime_array[-1]}")
            
        print_manager.datacubby("=== End Stashing Debug (LEAVING DATA CUBBY)===\n")
        return obj
    
    @classmethod
    def _merge_arrays(cls, existing_times, existing_raw_data, new_times, new_raw_data):
        """
        Ultra-optimized merge that can handle billions of data points.
        Now with 100% more awesome and machine-code compilation.
        """
        return ultimate_merger.merge_arrays(existing_times, existing_raw_data, new_times, new_raw_data)

    @classmethod
    def clear(cls):
        """
        Clear all data from the data cubby and re-initialize global class instances.
        
        This resets:
        - All stored class instances (and re-initializes them empty)
        - All class registrations
        - All subclass registrations
        - The global data tracker
        
        Useful for:
        - Starting fresh analysis
        - Freeing memory
        - Testing/debugging
        """
        print_manager.status("🧹 Clearing data cubby...")
        
        # Store list of classes that need re-initialization
        classes_to_reinit = []
        for key, instance in cls.cubby.items():
            if hasattr(instance, '__class__'):
                classes_to_reinit.append((key, instance.__class__))
        
        # Clear all storage dictionaries
        cls.cubby.clear()
        cls.class_registry.clear()
        cls.subclass_registry.clear()
        
        # Re-initialize the global class instances with empty data
        for key, class_type in classes_to_reinit:
            try:
                # Skip custom_class - it has special handling
                if key == 'custom_class':
                    # Re-create custom_class container
                    from .data_classes.custom_variables import CustomVariablesContainer
                    new_instance = CustomVariablesContainer()
                    cls.stash(new_instance, class_name=key)
                else:
                    # Create new empty instance for regular classes
                    new_instance = class_type(None)
                    # Re-register it
                    cls.stash(new_instance, class_name=key)
                print_manager.debug(f"✅ Re-initialized {key}")
            except Exception as e:
                print_manager.warning(f"⚠️  Could not re-initialize {key}: {e}")
                import traceback
                traceback.print_exc()
        
        # Clear the global tracker
        from .data_tracker import global_tracker
        global_tracker.imported_ranges.clear()
        global_tracker.calculated_ranges.clear()
        
        print_manager.status("✅ Data cubby cleared successfully!")
        print_manager.status("   - All class instances cleared and re-initialized")
        print_manager.status("   - All registrations cleared")
        print_manager.status("   - Global tracker reset")
    
    @classmethod
    def grab(cls, identifier):
        """Retrieve object by its identifier with enhanced type tracking."""
        print_manager.datacubby(f"\n=== Retrieving {identifier} from data_cubby ===")
        frame = inspect.currentframe().f_back
        caller_info = f"{frame.f_code.co_filename}:{frame.f_lineno}"
        print_manager.datacubby(f"GRAB CALLER: {caller_info}")
        
        # Normalize case of identifier if it's a string
        if isinstance(identifier, str):
            identifier = identifier.lower()
        # Convert the input identifier to lowercase
        identifier_lower = identifier.lower() if isinstance(identifier, str) else identifier

        # Check all dictionaries with both original and lowercase versions
        result = (cls.cubby.get(identifier) or 
                  cls.cubby.get(identifier_lower) or
                  cls.class_registry.get(identifier) or 
                  cls.class_registry.get(identifier_lower) or
                  cls.subclass_registry.get(identifier) or
                  cls.subclass_registry.get(identifier_lower))
        
        if result is not None:
            print_manager.datacubby(f"GRAB SUCCESS - Retrieved {identifier} with type {type(result)}")

            # STRATEGIC PRINT: Log state of object just before returning from GRAB
            dt_len_grab_return = len(result.datetime_array) if hasattr(result, 'datetime_array') and result.datetime_array is not None else "None_or_NoAttr"
            min_dt_grab_return = result.datetime_array[0] if dt_len_grab_return not in ["None_or_NoAttr", 0] else "N/A"
            max_dt_grab_return = result.datetime_array[-1] if dt_len_grab_return not in ["None_or_NoAttr", 0] else "N/A"
            print_manager.datacubby(f"[CUBBY_GRAB_RETURN_STATE] Object ID {id(result)} for key '{identifier}'. dt_len: {dt_len_grab_return}, min: {min_dt_grab_return}, max: {max_dt_grab_return}")

            # Debug datetime_array (Condensed & Formatted)
            if hasattr(result, 'datetime_array') and result.datetime_array is not None:
                if len(result.datetime_array) > 0:
                    start_dt = result.datetime_array[0]
                    end_dt = result.datetime_array[-1]

                    # Format datetimes using the imported helper
                    start_str = format_datetime_for_log(start_dt)
                    end_str = format_datetime_for_log(end_dt)

                    dt_summary = (
                        f"datetime_array type={type(result.datetime_array).__name__}, "
                        f"elem_type={type(start_dt).__name__}, "
                        f"shape={result.datetime_array.shape}, "
                        f"range={start_str} to {end_str}"
                    )
                    print_manager.datacubby(f"GRAB OUTPUT - {dt_summary}")
                else:
                    print_manager.datacubby(f"GRAB OUTPUT - datetime_array is empty")
            else:
                print_manager.datacubby(f"GRAB OUTPUT - No datetime_array attribute found")

            # Debug raw_data (Condensed)
            if hasattr(result, 'raw_data') and result.raw_data is not None:
                keys = list(result.raw_data.keys())
                summary_parts = [f"raw_data keys={keys}"]
                for key, value in result.raw_data.items():
                    shape_str = f"shape={getattr(value, 'shape', 'N/A')}"
                    if isinstance(value, list):
                        len_str = f"len={len(value)}"
                        if value and len(value) > 0 and hasattr(value[0], 'shape'):
                            elem_shape_str = f"elem_shape={getattr(value[0], 'shape', 'N/A')}"
                            summary_parts.append(f"{key}(list): {len_str}, {elem_shape_str}")
                        else:
                             summary_parts.append(f"{key}(list): {len_str}")
                    else:
                        summary_parts.append(f"{key}: type={type(value).__name__}, {shape_str}")
                print_manager.datacubby(f"GRAB OUTPUT - {' | '.join(summary_parts)}")
            else:
                print_manager.datacubby(f"GRAB OUTPUT - No raw_data attribute found")
        else:
            print_manager.datacubby(f"GRAB FAIL - Failed to retrieve {identifier}")
        
        print_manager.datacubby("=== End Retrieval Debug (LEAVING DATA CUBBY)===\n")
        return result

    @classmethod
    def get_all_keys(cls):
        """Get all keys from all registries for debugging."""
        result = {
            "cubby": list(cls.cubby.keys()),
            "class_registry": list(cls.class_registry.keys()),
            "subclass_registry": list(cls.subclass_registry.keys())
        }
        return result

    @classmethod
    def grab_component(cls, class_name, subclass_name):
        """
        Retrieve a component (subclass) from a class instance.
        
        Parameters
        ----------
        class_name : str
            Name of the class to retrieve from data_cubby
        subclass_name : str
            Name of the subclass/component to retrieve from the class
            
        Returns
        -------
        object or None
            The subclass object if found, otherwise None
        """
        print_manager.datacubby(f"\n=== Grabbing component {class_name}.{subclass_name} ===")
        frame = inspect.currentframe().f_back
        caller_info = f"{frame.f_code.co_filename}:{frame.f_lineno}"
        print_manager.datacubby(f"GRAB_COMPONENT CALLER: {caller_info}")
        
        # First get the class instance
        class_instance = cls.grab(class_name)
        if class_instance is None:
            print_manager.datacubby(f"GRAB_COMPONENT FAIL - Could not find class: {class_name}")
            print_manager.datacubby("=== End Component Grab Debug ===\n")
            return None
            
        # Check if the class has a get_subclass method
        if not hasattr(class_instance, 'get_subclass'):
            print_manager.datacubby(f"GRAB_COMPONENT FAIL - Class {class_name} has no get_subclass method")
            print_manager.datacubby("=== End Component Grab Debug ===\n")
            return None
            
        # Get the subclass from the class instance
        subclass = class_instance.get_subclass(subclass_name)
        if subclass is None:
            print_manager.datacubby(f"GRAB_COMPONENT FAIL - Could not find subclass: {subclass_name} in class {class_name}")
            print_manager.datacubby("=== End Component Grab Debug ===\n")
            return None
        
        print_manager.datacubby(f"GRAB_COMPONENT SUCCESS - Found component: {class_name}.{subclass_name} with type {type(subclass)}")
        
        # Debug subclass attributes
        if hasattr(subclass, 'datetime_array') and subclass.datetime_array is not None:
            print_manager.datacubby(f"GRAB_COMPONENT OUTPUT - datetime_array type: {type(subclass.datetime_array)}")
            if len(subclass.datetime_array) > 0:
                print_manager.datacubby(f"GRAB_COMPONENT OUTPUT - datetime_array element type: {type(subclass.datetime_array[0])}")
                print_manager.datacubby(f"GRAB_COMPONENT OUTPUT - datetime_array shape: {subclass.datetime_array.shape}")
                print_manager.datacubby(f"GRAB_COMPONENT OUTPUT - datetime_array range: {subclass.datetime_array[0]} to {subclass.datetime_array[-1]}")
            else:
                print_manager.datacubby(f"GRAB_COMPONENT OUTPUT - datetime_array is empty")
        else:
            print_manager.datacubby(f"GRAB_COMPONENT OUTPUT - No datetime_array attribute found")
        
        print_manager.datacubby("=== End Component Grab Debug ===\n")
        return subclass

    @classmethod
    def make_globally_accessible(cls, name, variable):
        """
        Make a variable accessible globally with the given name.
        
        Parameters
        ----------
        name : str
            The name to use for the variable in the global scope
        variable : object
            The variable to make globally accessible
        """
        try:
            import builtins
            from .print_manager import print_manager
            print_manager.datacubby(f"GLOBAL ACCESS - Making variable '{name}' globally accessible with ID {id(variable)}")
            
            # Debug variable type
            print_manager.datacubby(f"GLOBAL ACCESS - Variable type: {type(variable)}")
            if hasattr(variable, 'datetime_array') and variable.datetime_array is not None:
                print_manager.datacubby(f"GLOBAL ACCESS - datetime_array type: {type(variable.datetime_array)}")
                if len(variable.datetime_array) > 0:
                    print_manager.datacubby(f"GLOBAL ACCESS - datetime_array element type: {type(variable.datetime_array[0])}")
            
            setattr(builtins, name, variable)
            
            # Verify it was set correctly
            if hasattr(builtins, name):
                print_manager.datacubby(f"GLOBAL ACCESS SUCCESS - '{name}' globally accessible")
                return variable
            else:
                print_manager.datacubby(f"GLOBAL ACCESS FAIL - Failed to make '{name}' globally accessible")
                return variable
        except Exception as e:
            print_manager.datacubby(f"GLOBAL ACCESS ERROR - {str(e)}")
            return variable

    @classmethod
    @timer_decorator("TIMER_UPDATE_GLOBAL_INSTANCE")
    def update_global_instance(cls, 
                               data_type_str: str, 
                               imported_data_obj: DataObject, 
                               is_segment_merge: bool = False, 
                               original_requested_trange: Optional[List[str]] = None
                              ) -> bool:
        """
        Updates the global instance of a data type with new data.
        Handles merging if data already exists or populating if it's empty.

        Args:
            data_type_str (str): The string identifier for the data type (e.g., 'mag_rtn_4sa', 'spi_sf00_l3_mom').
            imported_data_obj (DataObject): The new data object (typically from import_data_function).
            is_segment_merge (bool): Flag indicating if this is a segment merge (not fully implemented yet).
            original_requested_trange (Optional[List[str]]): The original time range requested by the user/higher-level function.

        Returns:
            bool: True if the update was successful or deemed unnecessary, False otherwise.
        """
        pm = print_manager # Local alias
        pm.dependency_management(f"[CUBBY_UPDATE_ENTRY] Received call for '{data_type_str}'. Original trange: '{original_requested_trange}', type(original_requested_trange[0])='{type(original_requested_trange[0]) if original_requested_trange and len(original_requested_trange)>0 else 'N/A'}'")

        timer_entry = timer.perf_counter()
        if data_type_str == 'mag_RTN_4sa':
            print_manager.speed_test(f'[TIMER_MAG_5] DataCubby update: 0.00ms')
        elif data_type_str == 'psp_orbit_data':
            print_manager.speed_test(f'[TIMER_ORBIT_5] DataCubby update: 0.00ms')

        # --- Helper for time range validation (NEW) ---
        def _validate_trange_elements(trange_to_validate, context_msg=""):
            # Changed pm.error to pm.processing for this initial check
            if not isinstance(trange_to_validate, list) or len(trange_to_validate) != 2:
                pm.processing(f"VALIDATION_STRUCT_FAIL: Input trange for {context_msg} must be a list/tuple of two elements. Received: {trange_to_validate}")
                return False
            
            # Existing processing prints - will remain as is
            pm.processing(f"[VALIDATE_DEBUG_ENTRY] _validate_trange_elements received: {trange_to_validate} with types {[type(x) for x in trange_to_validate]}. Context: {context_msg}")

            # New diagnostic prints OUTSIDE the critical if block, using pm.processing as per new strict rule
            pm.processing(f"SCOPE_PROC_DEBUG: id(str) is {id(str)}, str is {str}")
            pm.processing(f"SCOPE_PROC_DEBUG: id(datetime) is {id(datetime)}, datetime is {datetime}")
            pm.processing(f"SCOPE_PROC_DEBUG: id(pd.Timestamp) is {id(pd.Timestamp)}, pd.Timestamp is {pd.Timestamp}")

            for i, item in enumerate(trange_to_validate):
                # Existing processing print - will remain as is
                pm.processing(f"[VALIDATE_DEBUG] Validating item '{item}' of type {type(item)}. Context: {context_msg}")
                # New diagnostic print OUTSIDE the critical if block, using pm.processing as per new strict rule
                pm.processing(f"ITEM_PROC_DEBUG: id(item) is {id(item)}, item is '{item}', type(item) is {type(item)}")

                if not isinstance(item, (str, datetime, pd.Timestamp)):
                    # ALL DIAGNOSTIC PRINTS *INSIDE THIS IF BLOCK* WILL BE PM.PROCESSING
                    pm.processing(f"IF_BLOCK_PROC_DEBUG: item is '{item}', type(item) is {type(item)}")
                    pm.processing(f"IF_BLOCK_PROC_DEBUG: isinstance(item, str) is {isinstance(item, str)}")
                    pm.processing(f"IF_BLOCK_PROC_DEBUG: isinstance(item, datetime) is {isinstance(item, datetime)}")
                    pm.processing(f"IF_BLOCK_PROC_DEBUG: isinstance(item, pd.Timestamp) is {isinstance(item, pd.Timestamp)}")
                    pm.processing(f"IF_BLOCK_PROC_DEBUG: id(str) is {id(str)}, id(datetime) is {id(datetime)}, id(pd.Timestamp) is {id(pd.Timestamp)}")

                    # Original error-causing lines, ensuring they are pm.processing
                    pm.processing("ERROR_TEST_AT_FAIL_POINT_PROCESSING") 
                    pm.processing(f"Error parsing/validating input time range for {context_msg}: Input trange elements must be strings or datetime/timestamp objects. Element {i} is {type(item)}.")
                    return False
            return True
        # --- End Helper ---

        if imported_data_obj is None and not is_segment_merge:
            pm.warning(f"[CUBBY_UPDATE_WARNING] imported_data_obj is None and not a segment merge for {data_type_str}. Update aborted.")
            return False

        # --- STEP 1: Get the target global instance --- 
        global_instance = None
        target_class_type = cls._get_class_type_from_string(data_type_str)
        pm.dependency_management(f"[CUBBY_UPDATE_DEBUG A] data_type_str: '{data_type_str}', target_class_type: '{target_class_type}'")

        if target_class_type:
            # Try to find an existing instance by its actual class type in the class_registry
            pm.datacubby(f"[INSTANCE_LOOKUP_DEBUG] Searching for instance of type {target_class_type} in class_registry with {len(cls.class_registry)} entries")
            for key, inst in cls.class_registry.items():
                pm.datacubby(f"[INSTANCE_LOOKUP_DEBUG] Checking key '{key}' -> {type(inst)} vs target {target_class_type}")
                if isinstance(inst, target_class_type):
                    global_instance = inst
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG B] Found matching instance by type in class_registry with key: '{key}', instance ID: {id(global_instance)}")
                    pm.datacubby(f"[INSTANCE_LOOKUP_DEBUG] ✅ MATCH FOUND by type lookup")
                    break
        else:
            pm.datacubby(f"[INSTANCE_LOOKUP_DEBUG] ❌ target_class_type is None for '{data_type_str}'")
        
        if global_instance is None:
            # Fallback: try direct key lookup in class_registry (old way, less robust for type matching)
            pm.datacubby(f"[INSTANCE_LOOKUP_DEBUG] Falling back to direct key lookup for '{data_type_str.lower()}'")
            global_instance = cls.class_registry.get(data_type_str.lower()) # Ensure lowercase for lookup
            if global_instance:
                pm.dependency_management(f"[CUBBY_UPDATE_DEBUG C] Found instance by direct key '{data_type_str.lower()}' in class_registry, instance ID: {id(global_instance)}")
                pm.datacubby(f"[INSTANCE_LOOKUP_DEBUG] ✅ MATCH FOUND by key lookup")
            else:
                pm.datacubby(f"[INSTANCE_LOOKUP_DEBUG] ❌ No instance found by key lookup either")
                #     pm.status(f"No instance found for {data_type_str}, creating a new one of type {target_class_type}")
                #     global_instance = target_class_type(None) # Initialize with no data
                #     cls.class_registry[data_type_str.lower()] = global_instance
                # else:
                return False

        pm.dependency_management(f"[CUBBY] Found target global instance: {type(global_instance).__name__} (ID: {id(global_instance)}) to update for data_type '{data_type_str}'")
        
        # --- STEP 2: EARLY CACHE CHECK - Bypass ALL processing if data is truly cached ---
        from .data_tracker import global_tracker
        if original_requested_trange and global_instance:
            # Check if this exact trange is already cached AND the instance has data
            if (not global_tracker.is_calculation_needed(original_requested_trange, data_type_str) and 
                hasattr(global_instance, 'datetime_array') and 
                global_instance.datetime_array is not None and 
                len(global_instance.datetime_array) > 0):
                
                pm.datacubby(f"🚀 CACHE HIT: Data for {data_type_str} trange {original_requested_trange} already cached. Skipping ALL processing!")
                pm.speed_test(f"[TIMER_CACHE_HIT] {data_type_str}: 0.00ms (pure cache)")
                pm.datacubby("=== End Global Instance Update (Cache Hit) ===\n")
                return True
        
        # --- STEP 3: Validate the original_requested_trange if provided (especially for proton) --- 
        # This is the "Cranky Timekeeper" point for proton data
        # Using data_type_str.lower() for reliable matching against common keys
        # Explicitly check for proton related keys: 'spi_sf00_l3_mom' (official CDF name) and 'proton' (common alias)
        if data_type_str.lower() == 'spi_sf00_l3_mom' or data_type_str.lower() == 'proton':
            if original_requested_trange:
                pm.dependency_management(f"[CUBBY_UPDATE_TRANGE_VALIDATION] Validating original_requested_trange for '{data_type_str}': {original_requested_trange}, Types: [{type(original_requested_trange[0]) if len(original_requested_trange)>0 else 'N/A'}, {type(original_requested_trange[1]) if len(original_requested_trange)>1 else 'N/A'}]")
                if not _validate_trange_elements(original_requested_trange, context_msg=data_type_str):
                    # Error already printed by _validate_trange_elements
                    return False # Stop update if validation fails
            else:
                pm.dependency_management(f"[CUBBY_UPDATE_TRANGE_VALIDATION] No original_requested_trange provided for '{data_type_str}', skipping explicit validation here.")

        # --- STEP 4: Determine if the global instance has existing data ---
        has_existing_data = False
        
        # Enhanced debug logging for has_existing_data evaluation
        global_instance_exists = global_instance is not None
        has_datetime_array_attr = hasattr(global_instance, 'datetime_array') if global_instance_exists else False
        datetime_array_not_none = (global_instance.datetime_array is not None) if (global_instance_exists and has_datetime_array_attr) else False
        datetime_array_length = len(global_instance.datetime_array) if (datetime_array_not_none) else 0
        
        pm.status(f"🔍 PATH ANALYSIS for '{data_type_str}' (class: {type(global_instance).__name__ if global_instance_exists else 'None'})")
        pm.status(f"   📊 datetime_array_exists: {has_datetime_array_attr}, not_none: {datetime_array_not_none}, length: {datetime_array_length}")
        
        if global_instance and hasattr(global_instance, 'datetime_array') and global_instance.datetime_array is not None and len(global_instance.datetime_array) > 0:
            has_existing_data = True

        pm.status(f"   ⚡ RESULT: has_existing_data = {has_existing_data}")
        pm.dependency_management(f"[CUBBY_UPDATE_DEBUG D] has_existing_data: {has_existing_data}")

        # --- STEP 5: Handle the update logic based on existing data ---
        if not has_existing_data or is_segment_merge:
            pm.status(f"   🔄 Taking UPDATE PATH for '{data_type_str}'")
            if is_segment_merge and has_existing_data:
                pm.datacubby(f"[CUBBY DEBUG] is_segment_merge is True, but instance for {data_type_str} already has data. Will overwrite with first segment via update().")
            elif not has_existing_data:
                pm.datacubby(f"Global instance for {data_type_str} is empty. Populating with new data via update()...")
            else: # is_segment_merge is True and no existing data
                pm.datacubby(f"Global instance for {data_type_str} is being initialized with the first segment via update()...")
            
            if hasattr(global_instance, 'update'):
                try:
                    # STRATEGIC PRINT H1
                    dt_len_before_instance_update = len(global_instance.datetime_array) if hasattr(global_instance, 'datetime_array') and global_instance.datetime_array is not None else "None_or_NoAttr"
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG H1] Instance (ID: {id(global_instance)}) BEFORE global_instance.update(). datetime_array len: {dt_len_before_instance_update}")
                    
                    print_manager.datacubby(f"Calling update() on global instance of {data_type_str} (ID: {id(global_instance)}). is_segment_merge={is_segment_merge}")
                    
                    start_time = timer.perf_counter()
                    try:
                        # Try the new signature first (with original_requested_trange)
                        global_instance.update(imported_data_obj, original_requested_trange=original_requested_trange)
                        print_manager.datacubby(f"Successfully called update() with original_requested_trange on global instance of {data_type_str}")
                    except TypeError as te:
                        # If that fails, fall back to the old signature (without original_requested_trange)
                        if "unexpected keyword argument" in str(te) or "takes" in str(te):
                            print_manager.datacubby(f"Falling back to simple update() signature for {data_type_str}")
                            global_instance.update(imported_data_obj)
                            print_manager.datacubby(f"Successfully called update() with simple signature on global instance of {data_type_str}")
                        else:
                            # Re-raise if it's a different TypeError
                            raise te
                    end_time = timer.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    print_manager.speed_test(f"[TIMER_INSTANCE_UPDATE] global_instance.update() for {data_type_str}: {duration_ms:.2f}ms")
                    
                    # STRATEGIC PRINT H2
                    dt_len_after_instance_update = len(global_instance.datetime_array) if hasattr(global_instance, 'datetime_array') and global_instance.datetime_array is not None else "None_or_NoAttr"
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG H2] Instance (ID: {id(global_instance)}) AFTER global_instance.update(). datetime_array len: {dt_len_after_instance_update}")
                    
                    pm.datacubby("✅ Instance updated successfully via .update() method.")
                    pm.datacubby("=== End Global Instance Update ===\n")
                    return True
                    
                except Exception as e:
                    pm.error(f"UPDATE GLOBAL ERROR - Error calling update() on instance: {e}")
                    import traceback
                    pm.error(traceback.format_exc())
                    pm.datacubby("=== End Global Instance Update ===\n")
                    return False
            else:
                pm.error(f"UPDATE GLOBAL ERROR - Global instance for '{data_type_str}' has no update method!")
                pm.datacubby("=== End Global Instance Update ===\n")
                return False
                
        # 5. Handle Instance with Existing Data (Merge Logic)
        else:
            # SPECIAL CASE: Orbit data should always be re-sliced to the requested trange
            # It's not downloaded CDF data that needs merging - it's a static lookup table
            if data_type_str.lower() == 'psp_orbit_data' or data_type_str.lower() == 'psp_orbit':
                pm.datacubby("Orbit data detected - forcing re-slice to requested trange instead of merge...")
                if hasattr(global_instance, 'update'):
                    try:
                        start_time = timer.perf_counter()
                        try:
                            # Force orbit data to re-slice by calling update with trange
                            global_instance.update(imported_data_obj, original_requested_trange=original_requested_trange)
                            pm.datacubby(f"Successfully re-sliced orbit data to trange: {original_requested_trange}")
                        except TypeError as te:
                            if "unexpected keyword argument" in str(te) or "takes" in str(te):
                                pm.datacubby(f"Falling back to simple update() signature for orbit data")
                                global_instance.update(imported_data_obj)
                            else:
                                raise te
                        end_time = timer.perf_counter()
                        duration_ms = (end_time - start_time) * 1000
                        print_manager.speed_test(f"[TIMER_ORBIT_SLICE] orbit data re-slice: {duration_ms:.2f}ms")
                        return True
                    except Exception as e:
                        pm.error(f"UPDATE ORBIT ERROR - Error re-slicing orbit data: {e}")
                        return False
                else:
                    pm.error(f"UPDATE ORBIT ERROR - Orbit instance has no update method!")
                    return False
            
        pm.status(f"   🔀 Taking MERGE PATH for '{data_type_str}'")
        pm.datacubby("Global instance has existing data. Attempting merge...")
        
        # STYLE_PRESERVATION: Before entering merge path
        pm.style_preservation(f"🔄 MERGE_PATH_ENTRY for '{data_type_str}' (class: {type(global_instance).__name__}, ID: {id(global_instance)})")
        if hasattr(global_instance, '__dict__'):
            from plotbot.plot_manager import plot_manager
            plot_managers = {k: v for k, v in global_instance.__dict__.items() if isinstance(v, plot_manager)}
            pm.style_preservation(f"   📊 Existing plot_managers: {list(plot_managers.keys())}")
            for pm_name, pm_obj in plot_managers.items():
                if hasattr(pm_obj, '_plot_state'):
                    color = getattr(pm_obj._plot_state, 'color', 'Not Set')
                    legend_label = getattr(pm_obj._plot_state, 'legend_label', 'Not Set') 
                    pm.style_preservation(f"   🎨 {pm_name}: color='{color}', legend_label='{legend_label}'")
                else:
                    pm.style_preservation(f"   ❌ {pm_name}: No _plot_state found")
        
        CorrectClass = cls._get_class_type_from_string(data_type_str)
        if not CorrectClass:
            pm.error(f"UPDATE GLOBAL ERROR - Cannot determine class type for '{data_type_str}' for merge.")
            pm.datacubby("=== End Global Instance Update ===\n")
            return False
                
        # Process the *new* raw data into structured arrays using a temporary instance
        try:
            pm.datacubby("Processing new imported data into temporary instance...")
            temp_new_processed = CorrectClass(None) # Create empty instance
            # We need to simulate the update process to get calculated vars
            if hasattr(temp_new_processed, 'calculate_variables'):
                pm.dependency_management(f"[CUBBY_UPDATE_DEBUG Merge Path - Pre-calc]: imported_data_obj ID: {id(imported_data_obj)}, .data ID: {id(imported_data_obj.data) if hasattr(imported_data_obj, 'data') else 'N/A'}, .data keys: {list(imported_data_obj.data.keys()) if hasattr(imported_data_obj, 'data') else 'N/A'} ***")
                temp_new_processed.calculate_variables(imported_data_obj)
            else:
                pm.warning(f"Temp instance for {data_type_str} lacks 'calculate_variables'. Merge might be incomplete.")
                # Attempt basic assignment if possible (might fail)
                temp_new_processed.datetime_array = np.array(cdflib.cdfepoch.to_datetime(imported_data_obj.times))
                temp_new_processed.raw_data = imported_data_obj.data # This is risky!
                     
            new_times = temp_new_processed.datetime_array
            new_raw_data = temp_new_processed.raw_data
            pm.datacubby("✅ New data processed.")
                
            # STRATEGIC PRINT M
            existing_dt_len_for_M = len(global_instance.datetime_array) if global_instance.datetime_array is not None else "None"
            existing_dt_range_for_M = (global_instance.datetime_array[0], global_instance.datetime_array[-1]) if existing_dt_len_for_M not in ["None", 0] else "N/A"
            new_dt_len_for_M = len(new_times) if new_times is not None else "None"
            new_dt_range_for_M = (new_times[0], new_times[-1]) if new_dt_len_for_M not in ["None", 0] else "N/A"
            pm.dependency_management(f"[CUBBY_UPDATE_DEBUG M] Before _merge_arrays. Existing (ID: {id(global_instance)}) dt_len: {existing_dt_len_for_M}, range: {existing_dt_range_for_M}. New (temp) dt_len: {new_dt_len_for_M}, range: {new_dt_range_for_M}")

        except Exception as e:
            pm.error(f"UPDATE GLOBAL ERROR - Failed to process new data in temp instance: {e}")
            import traceback
            pm.error(traceback.format_exc())
            pm.datacubby("=== End Global Instance Update ===\n")
            return False
                
        # Perform the array merge
        pm.datacubby("Calling _merge_arrays...")
        start_time = timer.perf_counter()
        merged_times, merged_raw_data = cls._merge_arrays(
            global_instance.datetime_array, global_instance.raw_data,
            new_times, new_raw_data
        )
        end_time = timer.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        print_manager.speed_test(f"[TIMER_MERGE_ARRAYS] _merge_arrays for {data_type_str}: {duration_ms:.2f}ms")
        
        # STYLE_PRESERVATION: After _merge_arrays() completes
        pm.style_preservation(f"✅ MERGE_ARRAYS_COMPLETE for '{data_type_str}' - merged_times: {len(merged_times) if merged_times is not None else 'None'}, merged_raw_data: {len(merged_raw_data) if merged_raw_data is not None else 'None'}")
        pm.style_preservation(f"   📊 Instance ID consistency check: {id(global_instance)} (should remain same throughout)")
            
        # Update the global instance ONLY if merge returned new data
        if merged_times is not None and merged_raw_data is not None:
            pm.dependency_management("[CUBBY DEBUG] Merge successful. Attempting to update global instance attributes...")
            
            # STYLE_PRESERVATION: Before manual attribute assignment  
            pm.style_preservation(f"📝 PRE_MANUAL_ASSIGNMENT for '{data_type_str}' (ID: {id(global_instance)})")
            pm.style_preservation(f"   📊 About to overwrite: datetime_array (len: {len(global_instance.datetime_array) if hasattr(global_instance, 'datetime_array') and global_instance.datetime_array is not None else 'None'}), raw_data (type: {type(global_instance.raw_data) if hasattr(global_instance, 'raw_data') else 'None'})")
            
            try:
                global_instance.datetime_array = merged_times
                global_instance.raw_data = merged_raw_data

                # STYLE_PRESERVATION: During datetime_array/raw_data assignment
                pm.style_preservation(f"✅ MANUAL_ASSIGNMENT_COMPLETE for '{data_type_str}' - datetime_array: {len(merged_times)}, raw_data updated")
                # STRATEGIC PRINT F
                pm.dependency_management(f"[CUBBY_UPDATE_DEBUG F] Instance (ID: {id(global_instance)}) AFTER assigning merged_times/raw_data. merged_times len: {len(merged_times)}, global_instance.datetime_array len: {len(global_instance.datetime_array) if global_instance.datetime_array is not None else 'None'}")

                # STEP 2: Reconstruct .time from .datetime_array (CRITICAL)
                pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] PRE-TIME-RECONSTRUCTION:")
                pm.dependency_management(f"    datetime_array len: {len(global_instance.datetime_array) if hasattr(global_instance, 'datetime_array') and global_instance.datetime_array is not None else 'None'}")
                pm.dependency_management(f"    current time len: {len(global_instance.time) if hasattr(global_instance, 'time') and global_instance.time is not None else 'None'}")
                if global_instance.datetime_array is not None and len(global_instance.datetime_array) > 0:
                    # OPTION: Convert to int64 directly from datetime64[ns] for self.time
                    # This is NOT TT2000 after the first load, but ensures length consistency and is fast.
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] Converting merged datetime_array (len {len(global_instance.datetime_array)}) directly to int64 for .time attribute.")
                    global_instance.time = global_instance.datetime_array.astype('datetime64[ns]').astype(np.int64)
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] POST-TIME-ASSIGNMENT (direct int64 cast):")
                    pm.dependency_management(f"    NEW time len: {len(global_instance.time) if global_instance.time is not None else 'None'}, shape: {global_instance.time.shape if hasattr(global_instance.time, 'shape') else 'N/A'}, dtype: {global_instance.time.dtype}")
                else:
                    global_instance.time = np.array([], dtype=np.int64) # Ensure correct dtype for empty
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] datetime_array was empty or None, set time to empty int64 array.")

                # STYLE PRESERVATION FIX: Save state, call set_plot_config(), restore state
                # This mirrors the pattern used in each class's update() method
                # We MUST call set_plot_config() because plot_managers hold views of the OLD arrays
                if hasattr(global_instance, 'set_plot_config'):
                    # STEP 1: Save current styling state from plot_managers
                    pm.style_preservation(f"💾 Saving plot_manager states before set_plot_config()")
                    current_state = {}
                    for subclass_name in merged_raw_data.keys():
                        if hasattr(global_instance, subclass_name):
                            var = getattr(global_instance, subclass_name)
                            if hasattr(var, '_plot_state'):
                                current_state[subclass_name] = dict(var._plot_state)
                                pm.style_preservation(f"   💾 Saved {subclass_name}: {var._plot_state}")
                    
                    # STEP 2: Recreate plot_managers with merged data
                    pm.style_preservation(f"🔧 Calling set_plot_config() to recreate plot_managers with merged data")
                    global_instance.set_plot_config()
                    
                    # STEP 3: Restore styling state to new plot_managers
                    pm.style_preservation(f"🔧 Restoring saved states to recreated plot_managers")
                    for subclass_name, state in current_state.items():
                        if hasattr(global_instance, subclass_name):
                            var = getattr(global_instance, subclass_name)
                            if hasattr(var, '_plot_state'):
                                var._plot_state.update(state)
                            # Also restore to plot_config attributes
                            for attr, value in state.items():
                                if hasattr(var.plot_config, attr):
                                    setattr(var.plot_config, attr, value)
                            pm.style_preservation(f"   🔧 Restored {subclass_name}: {state}")
                    
                    pm.style_preservation(f"✅ MERGE_COMPLETE for '{data_type_str}' - Styling preserved!")
                else:
                    pm.warning(f"Global instance for {data_type_str} has no set_plot_config(). Plot managers will have stale data!")
                
                dt_len_after_merge = len(global_instance.datetime_array) if hasattr(global_instance, 'datetime_array') and global_instance.datetime_array is not None else "None_or_NoAttr"
                min_dt_G = global_instance.datetime_array[0] if dt_len_after_merge not in ["None_or_NoAttr", 0] else "N/A"
                max_dt_G = global_instance.datetime_array[-1] if dt_len_after_merge not in ["None_or_NoAttr", 0] else "N/A"
                pm.dependency_management(f"[CUBBY_UPDATE_DEBUG G_POST_FINAL] Instance (ID: {id(global_instance)}) AFTER ALL MERGE LOGIC (before return True). datetime_array len: {dt_len_after_merge}, min: {min_dt_G}, max: {max_dt_G}")

                # STRATEGIC PRINT CHECK_REGISTRY
                instance_in_registry_check = cls.class_registry.get(data_type_str.lower()) # target_key is data_type_str.lower()
                if instance_in_registry_check is not None:
                    reg_len = len(instance_in_registry_check.datetime_array) if hasattr(instance_in_registry_check, 'datetime_array') and instance_in_registry_check.datetime_array is not None else "None_or_NoAttr"
                    reg_min_dt = instance_in_registry_check.datetime_array[0] if reg_len not in ["None_or_NoAttr", 0] else "N/A"
                    reg_max_dt = instance_in_registry_check.datetime_array[-1] if reg_len not in ["None_or_NoAttr", 0] else "N/A"
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG CHECK_REGISTRY] Instance in class_registry['{data_type_str.lower()}'] (ID: {id(instance_in_registry_check)}) state. dt_len: {reg_len}, min: {reg_min_dt}, max: {reg_max_dt}")
                    if instance_in_registry_check is not global_instance:
                        pm.warning(f"[CUBBY_UPDATE_DEBUG CHECK_REGISTRY] Instance in registry (ID: {id(instance_in_registry_check)}) is NOT THE SAME OBJECT as global_instance (ID: {id(global_instance)}) just updated!")
                else:
                    pm.dependency_management(f"[CUBBY_UPDATE_DEBUG CHECK_REGISTRY] Instance for key '{data_type_str.lower()}' NOT FOUND in class_registry after merge ops.")
                
                pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] Global instance fully updated (merge complete).")
                return True
            except Exception as e:
                # Using f-string for direct print of error
                pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] UPDATE GLOBAL ERROR - Failed during critical update steps for {data_type_str} global instance: {e}")
                import traceback
                # Using f-string for direct print of traceback
                pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] GOLD CUBBY TRACEBACK ***\n{traceback.format_exc()}")
                return False
        else:
            pm.dependency_management(f"[CUBBY_UPDATE_DEBUG] Merge not required or _merge_arrays returned None. Global instance remains unchanged from this merge op.")
            return False

class Variable:
    """
    A variable class that can hold data and metadata, 
    while also behaving like a numpy array.
    """
    def __init__(self, class_name, subclass_name):
        self.class_name = class_name
        self.subclass_name = subclass_name
        self.datetime_array = None
        self.time_values = None
        self.values = None
        self.data_type = None
        self.internal_id = id(self)  # Add an internal ID for unique identification
        
        print_manager.datacubby(f"VARIABLE INIT - Created Variable {class_name}.{subclass_name} with id {self.internal_id}")
    
    def __array__(self):
        """Return the values array when used in numpy operations."""
        print_manager.datacubby(f"VARIABLE __array__ - Converting Variable {self.class_name}.{self.subclass_name} to array")
        if self.values is None:
            import numpy as np
            return np.array([])  # Return empty array if values is None
        return self.values
    
    def __len__(self):
        """Return length of the values array."""
        if self.values is None:
            return 0
        try:
            return len(self.values)
        except TypeError:
            return 0  # Handle case where values doesn't support len()
    
    def __getitem__(self, key):
        """Support for indexing operations."""
        if self.values is None:
            raise ValueError("No values available in this variable.")
        return self.values[key]
    
    def __repr__(self):
        """String representation of the variable."""
        return f"<Variable {self.class_name}.{self.subclass_name}, type={self.data_type}, id={self.internal_id}>"

# Create global instance
data_cubby = data_cubby()
print('initialized data_cubby.')

# Add CDF classes to the type map after initialization
data_cubby._add_cdf_classes_to_map()
print('CDF classes added to data_cubby type map.')