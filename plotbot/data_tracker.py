from datetime import datetime, timezone
from dateutil.parser import parse
from .print_manager import print_manager

# Temporary cache to store lists of CDF filenames associated with a specific download/import operation.
# Key: tuple(data_type, tuple(trange))
# Value: list[str] (list of SPDF-cased CDF filenames)
_downloaded_cdf_cache = {}

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
        # Validate time range and ensure UTC timezone
        try:
            start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
            end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
        except ValueError as e:
            print(f"Error parsing time range: {e}")
            return

        if data_type in ranges_dict:                                     # If we have existing ranges for this data
            for stored_start, stored_end in ranges_dict[data_type]:      # Check each stored time range
                if start_time >= stored_start and end_time <= stored_end: # If requested range is fully contained
                    return False                                          # No action needed - already covered

        return True                                                      # Action needed if no containing range found

    #====================================================================
    # FUNCTION: _update_range (Internal), Updates stored time ranges
    #====================================================================
    def _update_range(self, trange, data_type, ranges_dict):
        """Update the stored time ranges for a specific data type."""
        # Validate time range and ensure UTC timezone
        try:
            start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
            end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
        except ValueError as e:
            print(f"Error parsing time range: {e}")
            return

        if data_type not in ranges_dict:                                # If first range for this data type
            ranges_dict[data_type] = []                                 # Initialize empty list for ranges

        ranges_dict[data_type].append((start_time, end_time))          # Store new time range as tuple

    #====================================================================
    # FUNCTION: print_imported_ranges, Displays all tracked import ranges
    #====================================================================
    def print_imported_ranges(self):
        """Display all imported time ranges by data type."""
        for data_type, ranges in self.imported_ranges.items():          # Iterate through all tracked data types
            print(f"{data_type}: {ranges}")                             # Print ranges for each type
            
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

# --- Functions to manage the temporary CDF filename cache ---

def store_downloaded_cdfs(data_type, trange, cdf_filenames):
    """Stores the list of downloaded CDF filenames for a given data_type and trange."""
    key = (data_type, tuple(trange)) # Ensure trange is a tuple for dict key
    _downloaded_cdf_cache[key] = cdf_filenames
    print_manager.debug(f"Stored {len(cdf_filenames)} CDF names for {key}: {cdf_filenames[:3]}...")

def retrieve_downloaded_cdfs(data_type, trange):
    """Retrieves the list of downloaded CDF filenames for a given data_type and trange.
    
    Returns None if no entry is found.
    Removes the entry after retrieval to prevent stale data.
    """
    key = (data_type, tuple(trange)) # Ensure trange is a tuple for lookup
    filenames = _downloaded_cdf_cache.pop(key, None) # Use pop to get and remove
    if filenames is not None:
        print_manager.debug(f"Retrieved {len(filenames)} CDF names for {key}: {filenames[:3]}...")
    else:
        print_manager.debug(f"No stored CDF names found for {key}.")
    return filenames

def clear_downloaded_cdf_cache():
    """Clears the entire temporary CDF filename cache."""
    global _downloaded_cdf_cache
    count = len(_downloaded_cdf_cache)
    _downloaded_cdf_cache = {}
    print_manager.debug(f"Cleared temporary CDF filename cache (removed {count} entries).")

# --- End CDF filename cache functions --- 