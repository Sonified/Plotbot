from .print_manager import print_manager
import numpy as np  # Needed for array handling in debug printing
import os
import pickle
import json
import re
import pandas as pd
from datetime import datetime

class data_cubby:
    cubby = {}
    class_registry = {}
    subclass_registry = {}
    _use_pkl_storage = False # Internal flag, default to False
    print(f"DEBUG: data_cubby class defined. Initial _use_pkl_storage: {_use_pkl_storage}")
    base_pkl_directory = None
    
    @property
    def use_pkl_storage(self):
        """Gets the current state of pickle storage usage."""
        return self.__class__._use_pkl_storage

    @use_pkl_storage.setter
    def use_pkl_storage(self, value: bool):
        """Sets whether to use pickle storage and handles setup/teardown."""
        cls = self.__class__  # Get the class
        print(f"DEBUG: data_cubby.use_pkl_storage setter called with value: {value}")
        print(f"DEBUG: Current cls._use_pkl_storage before change: {cls._use_pkl_storage}")

        if cls._use_pkl_storage == value:
            print_manager.debug(f"Data Cubby: use_pkl_storage already set to {value}. No change.")
            return # No change

        cls._use_pkl_storage = value
        print_manager.status(f"Data Cubby: Persistent storage {'enabled' if value else 'disabled'}.")

        if value:
            # Setup logic when enabling storage
            if cls.base_pkl_directory is None:
                # Default location in the project root directory
                project_root = os.path.dirname(os.path.dirname(__file__))
                cls.base_pkl_directory = os.path.join(project_root, 'data_cubby')
                print_manager.debug(f"Data Cubby: Defaulting storage directory to {cls.base_pkl_directory}")

            if not os.path.exists(cls.base_pkl_directory):
                try:
                    os.makedirs(cls.base_pkl_directory, exist_ok=True)
                    print_manager.debug(f"Data Cubby: Created storage directory {cls.base_pkl_directory}")
                except OSError as e:
                    print_manager.error(f"Data Cubby: Failed to create storage directory {cls.base_pkl_directory}: {e}")
                    cls._use_pkl_storage = False # Revert setting if directory creation fails
                    return

            print_manager.status(f"Data Cubby: Persistent storage using base directory: {cls.base_pkl_directory}")
            print("DEBUG: Setter is now calling load_from_disk...")
            self.load_from_disk() # Attempt to load existing data
        # else: Optional: Add logic here if something needs to happen when storage is disabled.

    @classmethod
    def set_storage_directory(cls, directory: str):
        """Explicitly sets the storage directory. Does not enable/disable storage."""
        abs_directory = os.path.abspath(directory) # Ensure absolute path
        cls.base_pkl_directory = abs_directory
        print_manager.status(f"Data Cubby: Base storage directory set to: {cls.base_pkl_directory}")

        # If storage is currently enabled, ensure the new directory exists
        if cls._use_pkl_storage:
            if not os.path.exists(cls.base_pkl_directory):
                try:
                    os.makedirs(cls.base_pkl_directory, exist_ok=True)
                    print_manager.debug(f"Data Cubby: Created new storage directory {cls.base_pkl_directory}")
                except OSError as e:
                    print_manager.error(f"Data Cubby: Failed to create new storage directory {cls.base_pkl_directory}: {e}")
                    # Decide if we should disable storage or just warn? For now, warn.
                    print_manager.warning(f"Data Cubby: Storage remains enabled, but directory {cls.base_pkl_directory} could not be created.")
            # Optional: Consider if loading from the new directory should happen automatically.
            # cls.load_from_disk() # Potentially load data if the directory changes while enabled

    @classmethod
    def _get_storage_path_for_object(cls, obj, identifier=None):
        """Determine storage path based *only* on the identifier and psp_data_types.py config."""
        print_manager.debug(f"--> _get_storage_path called with identifier: {identifier}") # DEBUG
        from .data_classes.psp_data_types import data_types
        
        # Default fallback path
        storage_path = os.path.join(cls.base_pkl_directory, 'general')
        path_derived = False # Flag to track if we found a specific path
        
        # Use the identifier directly as the key for psp_data_types
        if identifier and identifier in data_types:
            print_manager.debug(f"    Identifier '{identifier}' found in data_types.") # DEBUG
            config = data_types[identifier]
            if 'local_path' in config:
                configured_path = config['local_path']
                if isinstance(configured_path, str) and '{data_level}' in configured_path:
                    data_level = config.get('data_level', 'l2')
                    configured_path = configured_path.format(data_level=data_level)
                
                # Join directly with base_pkl_directory (keeping psp_data/ prefix)
                storage_path = os.path.join(cls.base_pkl_directory, configured_path)
                path_derived = True
                print_manager.debug(f"    Derived storage path from config: {storage_path}") # DEBUG
            else:
                print_manager.debug(f"    Identifier '{identifier}' found, but no 'local_path' in config. Using default.") # DEBUG
        else:
            print_manager.debug(f"    Identifier '{identifier}' not found in data_types config. Using default path.") # DEBUG
            
        # Ensure the final directory exists (either derived or default)
        try:
            os.makedirs(storage_path, exist_ok=True)
            print_manager.debug(f"    Ensured directory exists: {storage_path}") # DEBUG
        except OSError as e:
            print_manager.error(f"    Failed to create storage directory {storage_path}: {e}")
            # Fallback to general on directory creation error
            if path_derived: # Only try creating general if the derived path failed
                 storage_path = os.path.join(cls.base_pkl_directory, 'general')
                 try:
                     os.makedirs(storage_path, exist_ok=True)
                     print_manager.warning(f"    Fell back to and created default directory: {storage_path}")
                 except OSError as e2:
                     print_manager.error(f"    FATAL: Failed to create even default storage directory {storage_path}: {e2}")
                     # If even general fails, maybe raise error or return None?
                     # For now, returning the path that failed.
                     return storage_path # Return the path that failed creation
            else: # If general was already the target and failed.
                 print_manager.error(f"    FATAL: Failed to create default storage directory {storage_path}: {e}")
                 return storage_path # Return the path that failed creation
                 
        return storage_path

    @classmethod
    def save_to_disk(cls, identifier_to_save: str = None, obj_to_save=None) -> bool:
        """
        Save state to disk.

        Args:
            identifier_to_save (str, optional): The specific identifier to save. 
                                               If None, saves everything in the cubby. Defaults to None.
            obj_to_save (object, optional): The specific object instance to save. If provided, 
                                            it's used instead of fetching from the registry. Defaults to None.

        Returns:
            bool: True if saving was successful (or partially successful), False otherwise.
        """
        print(f"DEBUG: Attempting save_to_disk...")

        if not cls._use_pkl_storage or cls.base_pkl_directory is None:
            print_manager.debug("Data Cubby: Skipping save_to_disk (storage disabled or directory not set).")
            print("DEBUG: save_to_disk skipped (storage disabled or no directory).")
            return False

        print(f"DEBUG: save_to_disk proceeding. Directory: {cls.base_pkl_directory}")
        
        # Ensure base directory exists
        try:
            os.makedirs(cls.base_pkl_directory, exist_ok=True)
            print(f"DEBUG: Ensured base directory exists: {cls.base_pkl_directory}")
        except Exception as e:
            print_manager.error(f"Could not create base directory {cls.base_pkl_directory}: {e}")
            print(f"DEBUG: save_to_disk failed to create base directory: {str(e)}")
            return False

        # Load or create index file
        index_path = os.path.join(cls.base_pkl_directory, 'data_cubby_index.json')
        index = {'cubby': {}, 'class_registry': {}, 'subclass_registry': {}} # Default structure
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    index = json.load(f)
                # Ensure all top-level keys exist
                for key in ['cubby', 'class_registry', 'subclass_registry']:
                    if key not in index:
                        index[key] = {}
                print(f"DEBUG: Loaded existing index from {index_path}")
            except json.JSONDecodeError:
                print_manager.warning(f"Index file {index_path} is corrupted. Starting fresh.")
            except Exception as e:
                 print_manager.warning(f"Could not load index file {index_path}: {e}. Starting fresh.")
        else:
             print(f"DEBUG: No existing index file found at {index_path}. Creating new one.")

        success = True # Assume success initially
        saved_something = False # Flag to track if any object was actually saved

        # Import data types config HERE to ensure it's available
        from .data_classes.psp_data_types import data_types

        try: # Wrap the main saving logic
            # Determine which objects to save
            items_to_process = {}
            if identifier_to_save:
                if obj_to_save is not None:
                    items_to_process[identifier_to_save] = obj_to_save # Use the passed object
                    print(f"DEBUG: save_to_disk will save provided object with identifier: {identifier_to_save}")
                else:
                    # Find the object in any of the registries
                    obj = cls.cubby.get(identifier_to_save) or \
                          cls.class_registry.get(identifier_to_save) or \
                          cls.subclass_registry.get(identifier_to_save)
                    if obj is not None:
                        items_to_process[identifier_to_save] = obj
                        print(f"DEBUG: save_to_disk found object in registry for identifier: {identifier_to_save}")
                    else:
                         print(f"DEBUG: Object with identifier '{identifier_to_save}' not found in any registry.")
                         success = False # Can't save if not found
            else:
                # Save everything if no specific identifier is given
                items_to_process.update(cls.cubby)
                items_to_process.update(cls.class_registry)
                items_to_process.update(cls.subclass_registry)
                print(f"DEBUG: save_to_disk will save all {len(items_to_process)} stashed objects.")

            # Iterate and save each object
            for identifier, obj in items_to_process.items():
                try:
                    # --- Determine Storage Path ---
                    # Get the dedicated storage path (moved outside the potential daily loop)
                    storage_path = cls._get_storage_path_for_object(obj, identifier)

                    # --- Filename Determination & Saving Logic (Modified for Daily Files) ---
                    if hasattr(obj, 'source_filenames') and obj.source_filenames:
                        print_manager.debug(f"Object {identifier} has {len(obj.source_filenames)} source filenames. Processing daily.")
                        
                        # Ensure datetime_array exists and is usable for filtering
                        if not (hasattr(obj, 'datetime_array') and isinstance(obj.datetime_array, np.ndarray) and obj.datetime_array.size > 0):
                             print_manager.error(f"Cannot process daily PKLs for {identifier}: Missing or invalid datetime_array.")
                             success = False
                             continue # Skip to the next identifier

                        # Convert datetime_array to Pandas Timestamps for easier filtering (once)
                        try:
                             # FIX: Handle both naive and timezone-aware arrays correctly
                             # Convert raw array to pandas DatetimeIndex
                             dt_index = pd.to_datetime(obj.datetime_array, unit='ns')
                             
                             # Check if timezone-aware or naive
                             if dt_index.tz is None:
                                 # Naive: Localize to UTC
                                 timestamps_utc = dt_index.tz_localize('UTC')
                                 print_manager.debug(f"Localized naive datetime_array to UTC for {identifier}")
                             else:
                                 # Already aware: Convert to UTC
                                 timestamps_utc = dt_index.tz_convert('UTC')
                                 print_manager.debug(f"Converted timezone-aware datetime_array to UTC for {identifier}")
                             
                        except Exception as ts_err:
                             print_manager.error(f"Error converting datetime_array to Timestamps for {identifier}: {ts_err}")
                             success = False
                             continue # Skip to next identifier

                        # Loop through each source filename to create daily PKLs
                        for source_file_full_path in obj.source_filenames:
                             try:
                                 print(f"DEBUG_SAVE: Processing source file: {source_file_full_path}")
                                 source_filename_base = os.path.basename(source_file_full_path)
                                 print(f"DEBUG_SAVE: repr(source_filename_base): {repr(source_filename_base)}")

                                 # --- NEW: Dynamically build regex from psp_data_types.py ---
                                 if identifier not in data_types:
                                     print_manager.warning(f"Identifier '{identifier}' not found in psp_data_types.py. Cannot determine file pattern. Skipping PKL for {source_filename_base}.")
                                     continue

                                 config = data_types[identifier]
                                 pattern_template = config.get('file_pattern')
                                 file_time_format = config.get('file_time_format', 'daily') # Default to daily
                                 data_level = config.get('data_level', 'l2') # Default to l2

                                 if not pattern_template:
                                     print_manager.warning(f"No 'file_pattern' defined for identifier '{identifier}' in psp_data_types.py. Skipping PKL for {source_filename_base}.")
                                     continue

                                 # Prepare substitutions for the pattern template
                                 date_group = r'(\d{8})' # Regex group for YYYYMMDD
                                 if file_time_format == '6-hour':
                                      # Corrected to expect 8 digits after '20' (10 total) for YYYYMMDDHH
                                      date_group = r'(20\d{8})'  # Regex group for YYYYMMDDHH (10 digits total, starting with 20)
                                      pattern_template = pattern_template.replace('{date_hour_str}', date_group)
                                 else: # daily or other formats assumed to use date_str
                                      pattern_template = pattern_template.replace('{date_str}', date_group)

                                 # Substitute other placeholders
                                 pattern_template = pattern_template.replace('{data_level}', data_level)
                                 # Make sure version group is standard (d{2}) - removing f-string curly braces from config
                                 pattern_template = pattern_template.replace(r'(\d{{2}})', r'(\d{2})')

                                 # Escape regex special characters just in case (though pattern should be raw string)
                                 # pattern_template = re.escape(pattern_template) # Let's NOT escape for now, assume config pattern is correct regex

                                 # Compile and Match ---
                                 # FIX: Use re.IGNORECASE flag
                                 dynamic_pattern_compiled = re.compile(pattern_template, re.IGNORECASE)
                                 print(f"DEBUG_RE: Compiled dynamic pattern for '{identifier}': {dynamic_pattern_compiled.pattern}")
                                 final_match = dynamic_pattern_compiled.search(source_filename_base)

                                 # --- END NEW Regex Logic ---

                                 # Check the final result from the dynamic pattern
                                 if not final_match:
                                     print(f"DEBUG_SAVE: Dynamic Regex NO MATCH for {source_filename_base} using pattern {dynamic_pattern_compiled.pattern}")
                                     print_manager.warning(f"Could not extract date/version from source filename: {source_filename_base}. Skipping this file for daily PKL.")
                                     continue

                                 # --- Use final_match from here on --- 
                                 # FIX: Extract full date/date-hour string from group 1
                                 full_date_str = final_match.group(1)
                                 # Use only YYYYMMDD for daily mask filtering regardless of source pattern
                                 date_str_for_mask = full_date_str[:8]
                                 version_str = f"v{final_match.group(2)}"
                                 # FIX: Use the full captured date string (group 1) in re.sub
                                 # Use final_match variable here too
                                 # IMPORTANT: Construct the removal pattern carefully based on the dynamic match
                                 # We know the date part is group(1) and version is group(2)
                                 date_version_part_str = final_match.group(0) # Get the full matched part (e.g., _YYYYMMDDHH_v01.cdf)
                                 # Need to escape it before using in re.sub
                                 escaped_date_version_part = re.escape(date_version_part_str)
                                 # Replace the full matched part to get the base name
                                 base_name = re.sub(escaped_date_version_part + '$', '', source_filename_base)
                                 # base_name = re.sub(r'(_' + full_date_str + r'_v\\d{2})\\.cdf$', '', source_filename_base, flags=re.IGNORECASE) # Old way

                                 # Construct the daily PKL filename
                                 # Use the full date string (YYYYMMDD or YYYYMMDDHH) for the PKL filename itself
                                 print(f"DEBUG_SAVE: Extracted date/hour={full_date_str}, version={version_str}, base={base_name}")
                                 daily_filename = f"{base_name}_{full_date_str}_{version_str}.pkl"
                                 daily_obj_path = os.path.join(storage_path, daily_filename)
                                 print_manager.debug(f"Target daily PKL path: {daily_obj_path}")

                                 # --- Filter Data for the Current Day ---
                                 # Use YYYYMMDD part for day boundaries
                                 current_day = pd.to_datetime(date_str_for_mask, format='%Y%m%d').tz_localize('UTC')
                                 next_day = current_day + pd.Timedelta(days=1)
                                 
                                 # Create mask based on the full timestamps array
                                 print_manager.debug(f"DEBUG_SAVE: Checking mask. Object time range: {timestamps_utc.min()} to {timestamps_utc.max()}") # DEBUG
                                 print_manager.debug(f"DEBUG_SAVE: Mask range: {current_day} to {next_day}") # DEBUG
                                 day_mask = (timestamps_utc >= current_day) & (timestamps_utc < next_day)

                                 if not np.any(day_mask):
                                    print(f"DEBUG_SAVE: Day mask is EMPTY for {date_str_for_mask}")
                                    print_manager.debug(f"No data found for date {date_str_for_mask} ({current_day.date()}) in {identifier}. Skipping PKL for this day.")
                                    continue

                                 # --- Create a Subset Object for the Day ---
                                 # Use deepcopy to avoid modifying the original object in memory
                                 import copy
                                 daily_obj = copy.deepcopy(obj)

                                 # Apply the mask to the datetime_array and time array
                                 daily_obj.datetime_array = obj.datetime_array[day_mask]
                                 if hasattr(daily_obj, 'time') and isinstance(daily_obj.time, np.ndarray):
                                      daily_obj.time = daily_obj.time[day_mask] # Assuming 'time' is the TT2000 array

                                 # Apply the mask to data arrays within raw_data or plot_manager attributes
                                 # This requires knowing how data is stored (raw_data dict vs plot_manager)
                                 if hasattr(daily_obj, 'raw_data') and isinstance(daily_obj.raw_data, dict):
                                      for key, data_array in daily_obj.raw_data.items():
                                          if isinstance(data_array, np.ndarray) and data_array.shape[0] == len(day_mask): # Check if first dimension matches mask length
                                              try:
                                                   # Handle different dimensions correctly
                                                   if data_array.ndim == 1:
                                                       daily_obj.raw_data[key] = data_array[day_mask]
                                                   elif data_array.ndim > 1:
                                                        # Assume time is the first dimension
                                                        daily_obj.raw_data[key] = data_array[day_mask, ...]
                                                   else: # 0-dim array?
                                                        daily_obj.raw_data[key] = data_array # Keep as is if 0-dim
                                              except IndexError:
                                                   print_manager.warning(f"IndexError applying mask to {key} for {date_str_for_mask}. Shape: {data_array.shape}. Mask sum: {np.sum(day_mask)}")
                                                   # Decide on fallback? Fill with NaNs? Skip? For now, skip modification for this key.
                                              except Exception as mask_err:
                                                   print_manager.warning(f"Error applying mask to raw_data key '{key}' for {date_str_for_mask}: {mask_err}")
                                                   # Fallback?
                                 # Also update plot_manager instances if they hold the data directly
                                 for attr_name in dir(daily_obj):
                                      attr_value = getattr(daily_obj, attr_name)
                                      if type(attr_value).__name__ == 'plot_manager': # Check type without import
                                          # Assuming plot_manager itself holds the data array
                                          if isinstance(attr_value._data, np.ndarray) and attr_value._data.shape[0] == len(day_mask):
                                               try:
                                                   if attr_value._data.ndim == 1:
                                                        attr_value._data = attr_value._data[day_mask]
                                                   elif attr_value._data.ndim > 1:
                                                        attr_value._data = attr_value._data[day_mask, ...]
                                                   # Update internal shape if necessary
                                                   if hasattr(attr_value, '_shape'):
                                                        attr_value._shape = attr_value._data.shape
                                               except IndexError:
                                                    print_manager.warning(f"IndexError applying mask to plot_manager {attr_name} for {date_str_for_mask}. Shape: {attr_value._data.shape}. Mask sum: {np.sum(day_mask)}")
                                               except Exception as pm_mask_err:
                                                     print_manager.warning(f"Error applying mask to plot_manager '{attr_name}' for {date_str_for_mask}: {pm_mask_err}")


                                 # Update the source_filenames in the daily object to only the current file
                                 daily_obj.source_filenames = [source_file_full_path]

                                 # --- Save the Daily Subset Object ---
                                 print(f"DEBUG_SAVE: >>> Attempting pickle.dump to {daily_obj_path}")
                                 print_manager.debug(f"Saving daily object for {identifier} ({date_str_for_mask}) to {daily_obj_path}")
                                 try: # <-- Add try/except around pickle.dump
                                     with open(daily_obj_path, 'wb') as f:
                                          pickle.dump(daily_obj, f)
                                     saved_something = True # Mark that we saved at least one daily file
                                 except Exception as pickle_err:
                                      print_manager.error(f"ERROR during pickle.dump for {daily_obj_path}: {pickle_err}")
                                      success = False # Mark overall save as failed if pickling fails

                                 # --- Index Update (Skipped for now in daily loop) ---
                                 # We need to decide how to handle the index for multiple files per identifier.
                                 # For now, we won't update the index inside this loop.
                                 # rel_path = os.path.relpath(daily_obj_path, cls.base_pkl_directory)
                                 # index['cubby'][identifier] = rel_path # This would overwrite! Needs rethinking.

                             except Exception as daily_err:
                                 print_manager.error(f"Error processing daily PKL for {source_filename_base}: {daily_err}")
                                 import traceback
                                 print_manager.debug(traceback.format_exc())
                                 success = False # Mark failure if any day fails

                    else:
                        # --- Original Logic for Objects Without source_filenames or with only one ---
                        # (This part handles cases like FITS, HAM, or single-file CDF loads)
                        print_manager.debug(f"Object {identifier} has no or single source_filename. Using standard save logic.")
                        filename = f"{identifier.replace('.', '_')}_default.pkl" # Default fallback filename
                        version_str = "vXX" # Placeholder

                        # Determine filename using timestamp if no source_filename
                        date_str = None
                        if hasattr(obj, 'datetime_array') and isinstance(obj.datetime_array, np.ndarray) and obj.datetime_array.size > 0:
                            try:
                                if np.issubdtype(obj.datetime_array.dtype, np.datetime64):
                                    first_timestamp = pd.Timestamp(obj.datetime_array[0]) # Use pandas Timestamp
                                    date_str = first_timestamp.strftime('%Y%m%d')
                                else:
                                    print_manager.debug(f"datetime_array for {identifier} is not of type datetime64.")
                            except Exception as date_err:
                                print_manager.warning(f"Could not extract date from datetime_array for {identifier}: {date_err}")

                        # Use identifier and date string to generate a name
                        if date_str:
                            # Check psp_data_types for a pattern to mimic (less ideal than source filename)
                            from .data_classes.psp_data_types import data_types # Local import
                            if identifier in data_types and 'file_pattern_import' in data_types[identifier]:
                                pattern = data_types[identifier]['file_pattern_import']
                                # Try to extract the prefix before the date/version part
                                # Adapt pattern based on expected format (daily vs hourly)
                                time_format = data_types[identifier].get('file_time_format', 'daily')
                                date_placeholder = '{date_str}' if time_format == 'daily' else '{date_hour_str}'
                                
                                # Build regex dynamically (Example - needs refinement based on actual patterns)
                                # Assuming pattern like prefix_{date}_v*.cdf or prefix_{date}{hour}_v*.cdf
                                date_part_regex = r'(\d{8})' if time_format == 'daily' else r'(\d{10})' # Capture YYYYMMDD or YYYYMMDDHH
                                
                                # --- FIX: Provide necessary keys to pattern.format ---
                                format_args = {'data_level': data_types[identifier].get('data_level', 'l2')}
                                if time_format == '6-hour':
                                    hour_str = first_timestamp.strftime('%H') # Get hour
                                    block_start_hour = (int(hour_str) // 6) * 6 # Calculate 6-hour block start
                                    date_hour_str = f"{date_str}{block_start_hour:02d}"
                                    format_args['date_hour_str'] = date_hour_str # Add date_hour_str if needed
                                elif time_format == 'daily':
                                     format_args['date_str'] = date_str # Add date_str if needed for daily
                                # Add other potential placeholders as needed
                                
                                # Now format the pattern with the correct arguments
                                try:
                                    formatted_pattern = pattern.format(**format_args)
                                except KeyError as fmt_err:
                                     print_manager.error(f"KeyError formatting pattern '{pattern}' for {identifier}: {fmt_err}. Missing key?")
                                     formatted_pattern = None # Skip prefix extraction if formatting fails
                                
                                prefix_match = None
                                if formatted_pattern:
                                     prefix_match = re.match(rf"(.*?)_{date_part_regex}.*_v.*\.cdf", formatted_pattern)
                                # --- END FIX ---

                                if prefix_match:
                                    prefix = prefix_match.group(1)
                                    # If file_time_format is 6-hourly, use date+hour for filename to match potential CDF file granularity
                                    if time_format == '6-hour':
                                         hour_str = first_timestamp.strftime('%H') # Get hour
                                         block_start_hour = (int(hour_str) // 6) * 6 # Calculate 6-hour block start
                                         date_hour_str = f"{date_str}{block_start_hour:02d}"
                                         filename = f"{prefix}_{date_hour_str}_{version_str}.pkl" # Use date+hour block
                                         print_manager.debug(f"Constructed fallback filename from pattern/timestamp (6-hourly): {filename}")
                                    else: # Daily format
                                         filename = f"{prefix}_{date_str}_{version_str}.pkl" # Use only date
                                         print_manager.debug(f"Constructed fallback filename from pattern/timestamp (daily): {filename}")
                                else:
                                    filename = f"{identifier.replace('.', '_')}_{date_str}_{version_str}.pkl"
                                    print_manager.debug(f"Constructed fallback filename from identifier/timestamp (pattern parse failed): {filename}")
                            else:
                                filename = f"{identifier.replace('.', '_')}_{date_str}_{version_str}.pkl"
                                print_manager.debug(f"Constructed fallback filename from identifier/timestamp (no pattern): {filename}")

                        else:
                            # If no date, just use identifier (or the initial default)
                            filename = f"{identifier.replace('.', '_')}_nodate_{version_str}.pkl"
                            print_manager.debug(f"Using identifier-based fallback filename (no date): {filename}")
                        # --- End Fallback Filename Logic ---

                        # Use the determined storage_path and filename
                        obj_path = os.path.join(storage_path, filename)

                        print_manager.debug(f"Saving object '{identifier}' (single file) to {obj_path}")
                        try: # <-- Add try/except around pickle.dump
                            with open(obj_path, 'wb') as f:
                                pickle.dump(obj, f)
                            saved_something = True
                        except Exception as pickle_err:
                            print_manager.error(f"ERROR during pickle.dump for {obj_path}: {pickle_err}")
                            success = False # Mark overall save as failed if pickling fails

                        # --- Update index entry (Standard Logic) ---
                        rel_path = os.path.relpath(obj_path, cls.base_pkl_directory)
                        if identifier in cls.cubby: index['cubby'][identifier] = rel_path
                        elif identifier in cls.class_registry: index['class_registry'][identifier] = rel_path
                        elif identifier in cls.subclass_registry: index['subclass_registry'][identifier] = rel_path
                        # -----------------------------------------
                except Exception as e:
                    print_manager.error(f"Error saving object '{identifier}' to disk: {str(e)}")
                    print(f"DEBUG: Failed saving object '{identifier}': {str(e)}")
                    import traceback
                    print_manager.debug(traceback.format_exc()) # Add traceback
                    success = False # Mark overall success as False if any object fails

            # --- Save the updated index file (only if something was potentially saved) ---
            # Moved index saving outside the identifier loop, should happen only once at the end.
            # if saved_something or not identifier_to_save: # Save index if we processed anything or if doing a full save
            #     try:
            #         with open(index_path, 'w') as f:
            #             json.dump(index, f, indent=2)
            #         print_manager.debug(f"Updated index file: {index_path}")
            #     except Exception as e:
            #         print_manager.error(f"Error writing index file {index_path}: {e}")
            #         success = False
            # --- End Moved Index Saving Block ---

            # --- Final Status Update (after identifier loop) ---
            # Moved outside the loop
            # if success and saved_something:
            #     status_msg = f"Successfully saved object '{identifier_to_save}'" if identifier_to_save else "Successfully saved data_cubby state"
            #     print_manager.storage_status(f"{status_msg} to {cls.base_pkl_directory}") # Use storage_status
            #     print(f"DEBUG: save_to_disk successful for '{identifier_to_save or 'All'}'.")
            # elif not success:
            #      print(f"DEBUG: save_to_disk had errors for '{identifier_to_save or 'All'}'.")
            # else: # Success but saved_nothing (e.g. specific object not found)
            #      print(f"DEBUG: save_to_disk did not save anything for '{identifier_to_save}'.")
            # --- End Moved Status Update ---

            # --- New location for Index Saving and Status Update (After identifier loop) ---
            if saved_something: # Only update index if something was actually saved (daily or single)
                 try:
                      with open(index_path, 'w') as f:
                           json.dump(index, f, indent=2)
                      print_manager.debug(f"Final index file update: {index_path}")
                 except Exception as e:
                      print_manager.error(f"Error writing final index file {index_path}: {e}")
                      success = False # Mark failure if index writing fails

            if success and saved_something:
                 status_msg = f"Successfully saved object(s) for '{identifier_to_save}'" if identifier_to_save else "Successfully saved data_cubby state"
                 print_manager.storage_status(f"{status_msg} to {cls.base_pkl_directory}") # Use storage_status
                 print(f"DEBUG: save_to_disk finished successfully for '{identifier_to_save or 'All'}'.")
            elif not success:
                 print(f"DEBUG: save_to_disk finished with errors for '{identifier_to_save or 'All'}'.")
            else: # success but saved_nothing
                 print(f"DEBUG: save_to_disk finished but did not save anything for '{identifier_to_save}'.")
            # --- End New Index/Status Location ---

            return success

        except Exception as e: # Catch broader errors during setup/processing list creation
            print_manager.error(f"General error during save_to_disk for '{identifier_to_save or 'All'}': {str(e)}")
            print(f"DEBUG: save_to_disk failed with general error: {str(e)}")
            return False

    @classmethod
    def load_from_disk(cls) -> bool:
        """Load state from disk"""
        print("DEBUG: Attempting load_from_disk...")

        if not cls._use_pkl_storage or cls.base_pkl_directory is None:
            print_manager.debug("Data Cubby: Skipping load_from_disk (storage disabled or directory not set).")
            print("DEBUG: load_from_disk skipped (storage disabled or no directory).")
            return False

        # Check if index file exists
        index_path = os.path.join(cls.base_pkl_directory, 'data_cubby_index.json')
        print(f"DEBUG: load_from_disk checking for index file: {index_path}")

        if not os.path.exists(index_path):
            print_manager.storage_status("No existing data_cubby cache found (no index file)") # Use storage_status
            print("DEBUG: load_from_disk found no index file.")
            return False

        print("DEBUG: load_from_disk found index file. Proceeding to load.")

        try:
            # Load the index
            with open(index_path, 'r') as f:
                index = json.load(f)
                
            load_success_flag = True # Track overall success

            # Load objects from cubby
            print_manager.debug("--- Loading objects from cubby index ---")
            if 'cubby' in index: # Check if key exists
                for identifier, rel_path in index['cubby'].items():
                    obj_path = os.path.join(cls.base_pkl_directory, rel_path)
                    print_manager.debug(f"Attempting to load [cubby]: {identifier} from {obj_path}") # DEBUG PRINT
                    if os.path.exists(obj_path):
                        try: # Add try/except around individual loads
                            with open(obj_path, 'rb') as f:
                                obj = pickle.load(f)
                                cls.cubby[identifier] = obj
                                print_manager.debug(f"---> Successfully loaded [cubby]: {identifier}") # DEBUG PRINT
                        except Exception as load_err:
                            print_manager.error(f"ERROR loading pickle file {obj_path} for [cubby] {identifier}: {load_err}")
                            load_success_flag = False # Mark failure
                    else:
                        print_manager.warning(f"Missing pickle file referenced in index [cubby]: {obj_path}")
                        load_success_flag = False # Mark failure # Also mark failure if file is missing

            # Load objects from class_registry
            print_manager.debug("--- Loading objects from class_registry index ---")
            if 'class_registry' in index: # Check if key exists
                for class_name, rel_path in index['class_registry'].items():
                    # Avoid reloading if already loaded via cubby
                    if class_name in cls.cubby:
                        print_manager.debug(f"Skipping load [class_registry]: {class_name} (already in cubby)")
                        continue
                    obj_path = os.path.join(cls.base_pkl_directory, rel_path)
                    print_manager.debug(f"Attempting to load [class_registry]: {class_name} from {obj_path}") # DEBUG PRINT
                    if os.path.exists(obj_path):
                        try: # Add try/except around individual loads
                            with open(obj_path, 'rb') as f:
                                obj = pickle.load(f)
                                cls.class_registry[class_name] = obj
                                print_manager.debug(f"---> Successfully loaded [class_registry]: {class_name}") # DEBUG PRINT
                        except Exception as load_err:
                            print_manager.error(f"ERROR loading pickle file {obj_path} for [class_registry] {class_name}: {load_err}")
                            load_success_flag = False # Mark failure
                    else:
                        print_manager.warning(f"Missing pickle file referenced in index [class_registry]: {obj_path}")
                        load_success_flag = False # Mark failure # Also mark failure if file is missing

            # Load objects from subclass_registry
            print_manager.debug("--- Loading objects from subclass_registry index ---")
            if 'subclass_registry' in index: # Check if key exists
                for subclass_name, rel_path in index['subclass_registry'].items():
                     # Avoid reloading if already loaded via cubby or class_registry
                    if subclass_name in cls.cubby or subclass_name in cls.class_registry:
                        print_manager.debug(f"Skipping load [subclass_registry]: {subclass_name} (already loaded)")
                        continue
                    obj_path = os.path.join(cls.base_pkl_directory, rel_path)
                    print_manager.debug(f"Attempting to load [subclass_registry]: {subclass_name} from {obj_path}") # DEBUG PRINT
                    if os.path.exists(obj_path):
                        try: # Add try/except around individual loads
                            with open(obj_path, 'rb') as f:
                                obj = pickle.load(f)
                                cls.subclass_registry[subclass_name] = obj
                                print_manager.debug(f"---> Successfully loaded [subclass_registry]: {subclass_name}") # DEBUG PRINT
                        except Exception as load_err:
                            print_manager.error(f"ERROR loading pickle file {obj_path} for [subclass_registry] {subclass_name}: {load_err}")
                            load_success_flag = False # Mark failure
                    else:
                        print_manager.warning(f"Missing pickle file referenced in index [subclass_registry]: {obj_path}")
                        load_success_flag = False # Mark failure # Also mark failure if file is missing

            if load_success_flag:
                print_manager.storage_status(f"Successfully loaded data_cubby state from {cls.base_pkl_directory}") # Use storage_status
                print("DEBUG: load_from_disk successful.")
                return True
            else:
                print_manager.warning(f"Load from disk completed BUT encountered errors loading/finding some pickle files.")
                print("DEBUG: load_from_disk finished with errors.")
                return False # Return False if any individual load failed OR file missing

        except json.JSONDecodeError:
             print_manager.error(f"Error loading data_cubby: Index file {index_path} is corrupted.")
             print(f"DEBUG: load_from_disk failed with JSONDecodeError")
             return False
        except KeyError as e:
             print_manager.error(f"Error loading data_cubby: Index file {index_path} is missing expected key: {e}")
             print(f"DEBUG: load_from_disk failed with KeyError in index")
             return False
        except Exception as e: # Catch other broad errors during index loading/parsing
            print_manager.error(f"Error loading data_cubby from disk: {str(e)}")
            print(f"DEBUG: load_from_disk failed with general error: {str(e)}")
            import traceback
            print_manager.debug(traceback.format_exc()) # Use debug
            return False

    @classmethod
    def stash(cls, obj, class_name=None, subclass_name=None):
        """Store object with class and subclass tracking."""
        print_manager.debug(f"\n=== Stashing Debug (INSIDE DATA CUBBY) for {class_name}.{subclass_name or ''} ===") # Use debug
        identifier = f"{class_name}.{subclass_name}" if class_name and subclass_name else class_name
        if not identifier:
             # Fallback needed if only obj is provided?
             # Potentially use object's class name, but could be ambiguous.
             # For now, require at least class_name for stashing.
             print_manager.error("Stash requires at least a class_name to form an identifier.")
             return obj # Return object without stashing/saving
             
        print_manager.debug(f"Stashing with identifier: {identifier}") # Use debug
        
        # Debug print object attributes before stashing
        print_manager.debug(f"Attributes before stash:")
        for attr in dir(obj):
            if not attr.startswith('__'):
                try:
                    value = getattr(obj, attr, 'not set')
                    # Check type name for plot_manager to avoid circular import if necessary
                    is_plot_manager = type(value).__name__ == 'plot_manager'
                    
                    # Limit preview for lists/arrays AND plot_manager
                    if is_plot_manager:
                        # Concise representation for plot_manager
                        pm_id = f" for {value.plot_options.data_type}.{value.plot_options.subclass_name}" if hasattr(value, 'plot_options') else ""
                        preview = f"<plot_manager instance{pm_id}>"
                    elif isinstance(value, (list, np.ndarray)):
                        # Show first 2 elements only for other lists/arrays
                        preview = repr(value[:2]) + ('...' if len(value) > 2 else '')
                    elif callable(value):
                        preview = f"<callable {attr}>" # Don't print full repr of methods
                    else:
                        # Limit length of other representations too
                        preview = repr(value)
                        if len(preview) > 80:
                            preview = preview[:80] + '...'
                    print_manager.debug(f"- {attr}: {preview}")
                except Exception as e:
                     print_manager.debug(f"- {attr}: <Error getting attribute: {e}>")
            
        cls.cubby[identifier] = obj
        if class_name:
            cls.class_registry[class_name] = obj
            print_manager.debug(f"Stored in class_registry: {class_name}")
            
        if subclass_name:
            cls.subclass_registry[subclass_name] = obj
            print_manager.debug(f"Stored in subclass_registry: {subclass_name}")
            
        print_manager.debug("=== End Stashing Debug (LEAVING DATA CUBBY)===\n") # Use debug
        
        print(f"DEBUG: Stash checking cls._use_pkl_storage: {cls._use_pkl_storage}")
        # Save to disk if persistence is enabled (uses the internal flag)
        if cls._use_pkl_storage:
            print_manager.debug(f"Data Cubby: Calling save_to_disk specifically for {identifier}") # Use debug
            cls.save_to_disk(identifier_to_save=identifier) # Pass the specific identifier
            
        return obj

    @classmethod
    def grab(cls, identifier):
        """Retrieve object by its identifier."""
        print_manager.debug(f"\n=== Retrieving {identifier} from data_cubby ===") # Use debug
        
        # Special handling for derived variables
        if identifier == 'derived':
            print_manager.custom_debug(f"Looking for derived variables container")
            if identifier in cls.cubby:
                derived_obj = cls.cubby[identifier]
                
                # Collect all attributes into a single list for a consolidated print
                attrs_info = []
                for attr in dir(derived_obj):
                    if not attr.startswith('__'):
                        attr_value = getattr(derived_obj, attr)
                        attr_info = f"{attr}: {type(attr_value).__name__}"
                        
                        if hasattr(attr_value, 'shape'):
                            attr_info += f" (shape: {attr_value.shape}"
                            if len(attr_value) > 0:
                                attr_info += f", first: {attr_value[0]}"
                            attr_info += ")"
                        attrs_info.append(attr_info)
                
                # Print all attributes in a single line
                print_manager.custom_debug(f"Found derived object with attributes: {', '.join(attrs_info)}")
        
        result = (cls.cubby.get(identifier) or 
                 cls.class_registry.get(identifier) or 
                 cls.subclass_registry.get(identifier))
        
        if result is not None:
            print_manager.debug(f"✅ Successfully retrieved {identifier}") # Use debug
        else:
            print_manager.debug(f"❌ Failed to retrieve {identifier}") # Use debug
        
        if result is not None:
            # Print plot options for any component that has them
            print_manager.datacubby(f"\nPlot Options for {identifier}:")
            for attr_name in dir(result):
                if not attr_name.startswith('__'):  # Skip private attributes
                    var = getattr(result, attr_name)
                    if hasattr(var, 'plot_options'):  # Only print if it has plot options
                        print_manager.datacubby(f"\n{attr_name} plot options:")
                        for opt_name, value in vars(var.plot_options).items():
                            if not opt_name.startswith('_'):
                                # ALWAYS truncate arrays/lists to 10 items
                                if isinstance(value, (list, np.ndarray)):
                                    if isinstance(value, np.ndarray):
                                        preview = str(value.flatten()[:10]) + "..."
                                    else:
                                        preview = str(value[:10]) + "..."
                                    print_manager.datacubby(f"  {opt_name}: {preview}")
                                else:
                                    print_manager.datacubby(f"  {opt_name}: {value}")
        
        print_manager.debug("=== End Retrieval Debug (LEAVING DATA CUBBY)===\n") # Use debug
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
        print_manager.custom_debug(f"Grabbing component: {class_name}.{subclass_name}")
        # First get the class instance
        class_instance = cls.grab(class_name)
        if class_instance is None:
            print_manager.custom_debug(f"Could not find class: {class_name}")
            return None
            
        # Check if the class has a get_subclass method
        if not hasattr(class_instance, 'get_subclass'):
            print_manager.custom_debug(f"Class {class_name} has no get_subclass method")
            return None
            
        # Get the subclass from the class instance
        subclass = class_instance.get_subclass(subclass_name)
        if subclass is None:
            print_manager.custom_debug(f"Could not find subclass: {subclass_name} in class {class_name}")
            return None
        
        # CRITICAL FIX: Check datetime_array of derived variables for debugging purposes
        if class_name == 'derived' and subclass is not None:
            if hasattr(subclass, 'datetime_array') and subclass.datetime_array is not None:
                if len(subclass.datetime_array) > 0:
                    dt_start = subclass.datetime_array[0]
                    dt_end = subclass.datetime_array[-1]
                    print_manager.custom_debug(f"Retrieved derived variable {subclass_name} with time range: {dt_start} to {dt_end}")
                    
                    # If this is a known problematic variable (TAoverB, NewVar), add more debug info
                    if subclass_name in ['TAoverB', 'NewVar']:
                        import numpy as np
                        current_year = np.datetime64('now').astype('datetime64[Y]').astype(int) + 1970
                        dt_year = np.datetime64(dt_start).astype('datetime64[Y]').astype(int) + 1970
                        
                        if dt_year != current_year:
                            print_manager.custom_debug(f"⚠️ WARNING: Derived variable {subclass_name} has datetime from year {dt_year}")
                            print_manager.custom_debug(f"This may be a cached variable with outdated time range")
                            
                            # Flag it as potentially needing recalculation
                            subclass._needs_time_validation = True
            
        print_manager.custom_debug(f"Found component: {class_name}.{subclass_name}")
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
            print_manager.variable_testing(f"Making variable '{name}' globally accessible with ID {id(variable)}")
            setattr(builtins, name, variable)
            
            # Verify it was set correctly
            if hasattr(builtins, name):
                print_manager.variable_testing(f"Successfully made '{name}' globally accessible")
                return variable
            else:
                print_manager.variable_testing(f"Failed to make '{name}' globally accessible")
                return variable
        except Exception as e:
            from .print_manager import print_manager
            print_manager.variable_testing(f"Error making variable globally accessible: {str(e)}")
            return variable

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
    
    def __array__(self):
        """Return the values array when used in numpy operations."""
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
print(f"DEBUG: Global data_cubby instance created. Class _use_pkl_storage is now: {data_cubby._use_pkl_storage}")

# Example of how to enable: data_cubby.use_pkl_storage = True
# Example of how to set dir: data_cubby.set_storage_directory('/path/to/custom/cubby')