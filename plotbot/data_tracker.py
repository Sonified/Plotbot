# data_tracker.py

from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
from .print_manager import print_manager
import pandas as pd
import numpy as np # Ensure numpy is imported

class DataTracker:
    """Tracks imported and calculated data ranges to prevent redundant operations."""
    
    def __init__(self):
        self.imported_ranges = {}      # Dictionary storing time ranges of imported data, keyed by data type (e.g., 'mag_RTN')
        self.calculated_ranges = {}     # Dictionary storing time ranges of calculated variables, keyed by data type
    
    #====================================================================
    # FUNCTION: is_import_needed, Checks if data needs to be imported
    #====================================================================
    def is_import_needed(self, trange, data_type):
        """Check if import is needed based on trange and cached data"""
        if data_type not in self.imported_ranges:
            return True

        # Convert request times to datetime using flexible parser
        try:
            start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
            end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
        except ValueError as e:
            print(f"Error parsing time range: {e}")
            return True  # If we can't parse, assume import is needed
        
        # Check if any stored range covers our request
        for stored_start, stored_end in self.imported_ranges[data_type]:
            if start_time >= stored_start and end_time <= stored_end:
                return False  # Found a range that covers our request
                
        return True  # No stored range covers our request

    #====================================================================
    # FUNCTION: is_calculation_needed, Verifies if calculations are required
    #====================================================================
    def is_calculation_needed(self, trange, data_type, variable_name=None):
        """
        Determine if calculations are needed for the specified time range.
        
        Parameters
        ----------
        trange : list
            Time range [start, end]
        data_type : str
            Type of data (e.g., 'custom_data_type')
        variable_name : str, optional
            Specific variable name for more granular tracking
            
        Returns
        -------
        bool
            True if calculation is needed, False otherwise
        """
        # Create a specific cache key if variable_name is provided
        cache_key = f"{data_type}_{variable_name}" if variable_name else data_type
        
        if not self._is_action_needed(trange, cache_key, self.calculated_ranges, "calculated"):
            print_manager.status(f"{cache_key} already calculated for the time range: {trange[0]} to {trange[1]}")
            return False
        return True

    #====================================================================
    # FUNCTION: update_imported_range, Records newly imported data ranges
    #====================================================================
    def update_imported_range(self, trange, data_type):
        """Record a new imported time range for a specific data type."""
        
        # Validate time range and ensure UTC timezone
        try:
            start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
            end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
        except ValueError as e:
            print(f"Error parsing time range: {e}")
            return
        
        if data_type not in self.imported_ranges:                       # Create new list for data type if not exists
            self.imported_ranges[data_type] = []                        # Initialize empty list to store time ranges
        
        self.imported_ranges[data_type].append((start_time, end_time))  # Add new time range tuple to tracking list

    #====================================================================
    # FUNCTION: update_calculated_range, Records newly calculated data ranges
    #====================================================================
    def update_calculated_range(self, trange, data_type, variable_name=None):
        """
        Record a new calculated time range for a specific data type.
        
        Parameters
        ----------
        trange : list
            Time range [start, end]
        data_type : str
            Type of data (e.g., 'custom_data_type')
        variable_name : str, optional
            Specific variable name for more granular tracking
        """
        # Create a specific cache key if variable_name is provided
        cache_key = f"{data_type}_{variable_name}" if variable_name else data_type
        
        self._update_range(trange, cache_key, self.calculated_ranges)   # Use internal method to update calculated ranges
        
        # For backward compatibility, also update the general data_type entry
        if variable_name and cache_key != data_type:
            self._update_range(trange, data_type, self.calculated_ranges)

    #====================================================================
    # FUNCTION: get_calculated_range, Retrieves full range of calculations
    #====================================================================
    def get_calculated_range(self, data_type, variable_name=None):
        """
        Retrieve the full calculated time range for a data type.
        
        Parameters
        ----------
        data_type : str
            Type of data
        variable_name : str, optional
            Specific variable name
            
        Returns
        -------
        tuple
            (earliest_start, latest_end) or None if no calculations exist
        """
        # Create a specific cache key if variable_name is provided
        cache_key = f"{data_type}_{variable_name}" if variable_name else data_type
        
        if cache_key not in self.calculated_ranges:                     # Check if we have any calculations for this type
            return None                                                 # Return None if no calculations exist
        ranges = self.calculated_ranges[cache_key]                      # Get list of all calculated ranges
        if not ranges:                                                 # If list exists but is empty
            return None                                                # Return None for no calculations
        earliest_start = min(r[0] for r in ranges)                    # Find earliest start time across all ranges
        latest_end = max(r[1] for r in ranges)                        # Find latest end time across all ranges
        return (earliest_start, latest_end)                           # Return tuple of full time coverage

    #====================================================================
    # FUNCTION: _is_action_needed (Internal), Checks for existing coverage
    #====================================================================
    def _is_action_needed(self, trange, data_type, ranges_dict, action_type):
        """Determine if an action is needed by checking existing time ranges."""
        # --- Enhanced debug prints for incoming trange (can be removed after debugging) ---
        print_manager.processing(f"[DataTracker][Pre-Check DEBUG] _is_action_needed for {data_type}, trange: {trange}, type: {type(trange)}")
        if isinstance(trange, (list, tuple)) and len(trange) == 2:
            if not all(isinstance(t, (str, datetime, np.datetime64)) for t in trange):
                print_manager.processing(f"[DataTracker] Error: Invalid type in trange elements: {[type(t) for t in trange]}. Expected str, np.datetime64 or datetime.")
                return True # Default to action needed if type is invalid
            print_manager.processing(f"[DataTracker][Pre-Check DEBUG] trange[0] type: {type(trange[0])}, trange[1] type: {type(trange[1])}")
        else:
            print_manager.processing(f"[DataTracker] Error: Invalid trange format or length: {trange}. Expected list/tuple of 2 elements.")
            return True # Default to action needed if format is invalid

        # --- Specific EPAD Debugging ---
        if data_type == 'epad':
            print_manager.processing(f"[DataTracker][EPAD_DEBUG] _is_action_needed called for EPAD.")
            print_manager.processing(f"[DataTracker][EPAD_DEBUG]   Action type: {action_type}")
            print_manager.processing(f"[DataTracker][EPAD_DEBUG]   Requested trange: {trange}")
            print_manager.processing(f"[DataTracker][EPAD_DEBUG]   Using ranges_dict: {'calculated_ranges' if ranges_dict is self.calculated_ranges else 'imported_ranges' if ranges_dict is self.imported_ranges else 'unknown_dict'}")
            current_epad_ranges = ranges_dict.get(data_type, [])
            print_manager.processing(f"[DataTracker][EPAD_DEBUG]   Currently stored ranges for EPAD: {current_epad_ranges}")

        # Convert trange elements to datetime objects for comparison
        try:
            if isinstance(trange, (list, tuple)) and len(trange) == 2:
                if isinstance(trange[0], str):
                    # Parse strings
                    start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
                    end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
                elif isinstance(trange[0], (datetime, pd.Timestamp, np.datetime64)):
                    # Convert to Python datetime objects, ensuring UTC
                    if isinstance(trange[0], np.datetime64):
                        # Convert numpy.datetime64 to pandas Timestamp then to python datetime
                        start_time = pd.Timestamp(trange[0]).to_pydatetime()
                        end_time = pd.Timestamp(trange[1]).to_pydatetime()
                    else: # Already datetime or pd.Timestamp
                        start_time = trange[0]
                        end_time = trange[1]

                    # Ensure UTC for all datetime-like objects
                    if start_time.tzinfo is None:
                        start_time = start_time.replace(tzinfo=timezone.utc)
                    else:
                        start_time = start_time.astimezone(timezone.utc)
                    
                    if end_time.tzinfo is None:
                        end_time = end_time.replace(tzinfo=timezone.utc)
                    else:
                        end_time = end_time.astimezone(timezone.utc)
                else:
                    raise ValueError(f"Input trange elements must be strings, datetime, pd.Timestamp, or np.datetime64. Got: {type(trange[0])}")
            else:
                raise ValueError("Input trange must be a list/tuple of length 2")
        except Exception as e: # Catch parsing errors too
            print_manager.processing(f"[DataTracker][Is Action Needed] Error parsing/validating input time range for {data_type}: {e}")
            return True # Assume action needed if parse/validation fails

        # --- Specific EPAD Debugging ---
        if data_type == 'epad':
            print_manager.debug(f"[DataTracker][EPAD_DEBUG]   Converted requested start_dt: {start_time}, end_dt: {end_time}")

        for existing_start, existing_end in ranges_dict.get(data_type, []):
            # --- Specific EPAD Debugging ---
            if data_type == 'epad':
                print_manager.debug(f"[DataTracker][EPAD_DEBUG]     Comparing with existing range: [{existing_start}, {existing_end}]")
                is_after_start = start_time >= existing_start
                is_before_end = end_time <= existing_end
                print_manager.debug(f"[DataTracker][EPAD_DEBUG]       start_request_dt ({start_time}) >= existing_start ({existing_start})? {is_after_start}")
                print_manager.debug(f"[DataTracker][EPAD_DEBUG]       end_request_dt ({end_time}) <= existing_end ({existing_end})? {is_before_end}")

            if start_time >= existing_start and end_time <= existing_end:
                # --- Specific EPAD Debugging ---
                if data_type == 'epad':
                    print_manager.debug(f"[DataTracker][EPAD_DEBUG]   Fully contained in existing range. Returning False (no action needed).")
                return False  # Requested range is fully contained within an existing range

        # --- Specific EPAD Debugging ---
        if data_type == 'epad':
            print_manager.debug(f"[DataTracker][EPAD_DEBUG]   Not contained in any existing range. Returning True (action needed).")

        return True # No existing range fully contains the requested range

    #====================================================================
    # FUNCTION: _update_range (Internal), Updates stored time ranges
    #====================================================================
    def _update_range(self, trange, data_type, ranges_dict):
        """Update the stored time ranges, merging overlapping/adjacent ones."""
        # --- Handle input trange (string list/tuple or datetime tuple) ---
        try:
            if isinstance(trange, (list, tuple)) and len(trange) == 2:
                if isinstance(trange[0], str):
                    # Parse strings
                    new_start = parse(trange[0]).replace(tzinfo=timezone.utc)
                    new_end = parse(trange[1]).replace(tzinfo=timezone.utc)
                elif isinstance(trange[0], (datetime, pd.Timestamp, np.datetime64)):
                    # Convert to Python datetime objects, ensuring UTC
                    if isinstance(trange[0], np.datetime64):
                        new_start = pd.Timestamp(trange[0]).to_pydatetime()
                        new_end = pd.Timestamp(trange[1]).to_pydatetime()
                    else: # Already datetime or pd.Timestamp
                        new_start = trange[0]
                        new_end = trange[1]

                    # Ensure UTC for all datetime-like objects
                    if new_start.tzinfo is None:
                        new_start = new_start.replace(tzinfo=timezone.utc)
                    else:
                        new_start = new_start.astimezone(timezone.utc)
                    
                    if new_end.tzinfo is None:
                        new_end = new_end.replace(tzinfo=timezone.utc)
                    else:
                        new_end = new_end.astimezone(timezone.utc)
                else:
                    raise ValueError(f"Input trange elements must be strings, datetime, pd.Timestamp, or np.datetime64. Got: {type(trange[0])}")
            else:
                 raise ValueError("Input trange must be a list/tuple of length 2")

            if new_start >= new_end:
                print_manager.warning(f"Skipping invalid range for {data_type}: {trange}")
                return
        except Exception as e: # Catch parsing errors too
            print_manager.processing(f"[DataTracker][Update Range] Error parsing/validating input time range for {data_type}: {e}")
            return
        # --- End input handling ---

        if data_type not in ranges_dict:
            ranges_dict[data_type] = []

        # Add the new range
        ranges_dict[data_type].append((new_start, new_end))

        # Sort ranges by start time
        ranges_dict[data_type].sort(key=lambda x: x[0])

        # Merge overlapping or adjacent ranges
        merged_ranges = []
        if not ranges_dict[data_type]:
            return # Should not happen if we just added one, but safety check

        current_start, current_end = ranges_dict[data_type][0]

        for next_start, next_end in ranges_dict[data_type][1:]:
            # Check if the next range overlaps or is adjacent to the current merged range
            if next_start <= current_end:
                # Merge by extending the current end time if the next range ends later
                current_end = max(current_end, next_end)
            else:
                # No overlap, the current merged range is final
                merged_ranges.append((current_start, current_end))
                # Start a new merged range
                current_start, current_end = next_start, next_end

        # Add the last merged range
        merged_ranges.append((current_start, current_end))

        # Replace the old list with the merged list
        ranges_dict[data_type] = merged_ranges
        print_manager.debug(f"Updated and merged ranges for {data_type}: {ranges_dict[data_type]}")

    #====================================================================
    # FUNCTION: print_imported_ranges, Displays all tracked import ranges
    #====================================================================
    def print_imported_ranges(self):
        """Display all imported time ranges by data type."""
        for data_type, ranges in self.imported_ranges.items():          # Iterate through all tracked data types
            print_manager.debug(f"{data_type}: {ranges}")                             # Print ranges for each type
            
    #====================================================================
    # FUNCTION: clear_calculation_cache, Clears calculation cache for type
    #====================================================================
    def clear_calculation_cache(self, data_type=None, variable_name=None):
        """
        Clear calculation cache for a specific data type and/or variable.
        
        Parameters
        ----------
        data_type : str, optional
            Type of data to clear, or None to clear all
        variable_name : str, optional
            Specific variable name, or None to clear all for the data_type
        """
        if data_type is None:
            # Clear all calculation caches
            self.calculated_ranges = {}
            print_manager.processing("Cleared all calculation caches")
            return
            
        if variable_name is None:
            # Clear all caches for this data_type including variable-specific ones
            keys_to_clear = []
            for key in self.calculated_ranges.keys():
                if key == data_type or key.startswith(f"{data_type}_"):
                    keys_to_clear.append(key)
                    
            for key in keys_to_clear:
                del self.calculated_ranges[key]
                
            print_manager.processing(f"Cleared calculation cache for {data_type} and all related variables")
            return
            
        # Clear only the specific variable cache
        cache_key = f"{data_type}_{variable_name}"
        if cache_key in self.calculated_ranges:
            del self.calculated_ranges[cache_key]
            print_manager.processing(f"Cleared calculation cache for {cache_key}")

#====================================================================
# Create global tracker instance for application-wide range tracking
#====================================================================
global_tracker = DataTracker()                         # Single instance used throughout application
print('initialized global_tracker') 