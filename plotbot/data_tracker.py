from datetime import datetime, timezone
from dateutil.parser import parse
from .print_manager import print_manager

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
    def is_calculation_needed(self, trange, data_type):
        """Determine if calculations are needed for the specified time range."""
        if not self._is_action_needed(trange, data_type, self.calculated_ranges, "calculated"):  # Check if range is already covered
            print_manager.status(f"{data_type} variables already calculated for the time range: {trange[0]} to {trange[1]}")  # Inform user if already done
        return self._is_action_needed(trange, data_type, self.calculated_ranges, "calculated")   # Return True if calculations needed

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
    def update_calculated_range(self, trange, data_type):
        """Record a new calculated time range for a specific data type."""
        self._update_range(trange, data_type, self.calculated_ranges)   # Use internal method to update calculated ranges

    #====================================================================
    # FUNCTION: get_calculated_range, Retrieves full range of calculations
    #====================================================================
    def get_calculated_range(self, data_type):
        """Retrieve the full calculated time range for a data type."""
        if data_type not in self.calculated_ranges:                     # Check if we have any calculations for this type
            return None                                                 # Return None if no calculations exist
        ranges = self.calculated_ranges[data_type]                      # Get list of all calculated ranges
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
# Create global tracker instance for application-wide range tracking
#====================================================================
global_tracker = DataTracker()                         # Single instance used throughout application
print('initialized global_tracker') 