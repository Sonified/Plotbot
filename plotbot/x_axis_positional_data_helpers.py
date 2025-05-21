# plotbot/x_axis_positional_data_helpers.py
import numpy as np
import pandas as pd
from .print_manager import print_manager
import pathlib # Import pathlib

class XAxisPositionalDataMapper:
    """Helper class to map timestamps to Parker Solar Probe positional data values."""
    
    def __init__(self, data_path):
        """
        Initializes the XAxisPositionalDataMapper.

        Args:
            data_path (str): Path to the NPZ file containing positional data.
                            Can be relative or absolute. If relative, it's
                            interpreted relative to the caller's working directory.
        """
        self.data_path = data_path
        self.times_numeric = None
        self.longitude_values = None
        self.radial_values = None
        self.latitude_values = None
        self.data_loaded = False # Flag to track loading status
        self.load_data()

    def _resolve_path(self) -> str:
        """Resolves the potentially relative path to an absolute path."""
        # Intended to be robust whether called from main script dir or within plotbot
        # Assumes data_path is relative to project root if not absolute
        path = pathlib.Path(self.data_path)
        if not path.is_absolute():
            # Try resolving relative to current working directory first
            resolved_path = pathlib.Path.cwd() / path
            if resolved_path.exists():
                 return str(resolved_path.resolve())
            else:
                # Fallback: Assume relative to the plotbot package structure?
                # This might be needed if run from deep within tests, but often CWD is safer.
                # For simplicity, we'll primarily rely on CWD or absolute paths.
                print_manager.warning(f"Relative path {path} not found relative to CWD. Trying as is.")
                return str(path) # Return original relative path if CWD relative fails
        return str(path.resolve()) # Return resolved absolute path

    def load_data(self):
        """Load positional data from NPZ file."""
        resolved_path = self._resolve_path()
        print_manager.processing(f"Attempting to load Parker Solar Probe positional data from {resolved_path}...")
        try:
            print_manager.status(f"Loading Parker Solar Probe positional data from {resolved_path}")
            # Use the resolved path to load data
            with np.load(resolved_path) as data:
                # Extract data - expect 'times', 'r_sun', 'carrington_lon', and 'carrington_lat' arrays
                times_raw = data['times']
                self.radial_values = data['r_sun'] if 'r_sun' in data else None
                self.longitude_values = data['carrington_lon'] if 'carrington_lon' in data else None
                self.latitude_values = data['carrington_lat'] if 'carrington_lat' in data else None

            # Convert raw times (likely strings or np.datetime64) to python datetimes (naive UTC)
            # This is crucial for consistent conversion to numeric representation
            datetime_array_pd = pd.to_datetime(times_raw, utc=True).tz_convert(None)

            # Convert pandas Timestamps to numpy datetime64 array first for consistency
            datetime_array_np = datetime_array_pd.to_numpy()

            # Convert numpy datetime64 array to numeric timestamps (seconds since epoch)
            # This is the format needed for np.interp
            # astype(np.int64) gives nanoseconds, divide by 1e9 for seconds
            self.times_numeric = datetime_array_np.astype(np.int64) / 1e9

            # Log what data was loaded
            data_types = []
            if self.radial_values is not None:
                data_types.append("radial")
            if self.longitude_values is not None:
                data_types.append("longitude")
            if self.latitude_values is not None:
                data_types.append("latitude")
                
            print_manager.status(f"-> Loaded {len(self.times_numeric)} positional data points with types: {', '.join(data_types)}")
            self.data_loaded = True
            if self.data_loaded and self.times_numeric is not None and len(self.times_numeric) > 0:
                ref_start_time = pd.to_datetime(self.times_numeric[0] * 1e9)
                ref_end_time = pd.to_datetime(self.times_numeric[-1] * 1e9)
                print_manager.processing(f"SUCCESS: Positional data loaded. Mapper Time Range: {ref_start_time} to {ref_end_time}")
            elif self.data_loaded:
                print_manager.processing("SUCCESS: Positional data loaded, but times_numeric array is None or empty.")
            return True
        except FileNotFoundError:
             print_manager.error(f"ERROR: Positional data file not found at {resolved_path}")
             print_manager.processing(f"FAILURE: Positional data file not found at {resolved_path}")
             self.data_loaded = False
             return False
        except Exception as e:
            print_manager.error(f"ERROR: Failed to load or process positional data from {resolved_path}: {e}")
            print_manager.processing(f"FAILURE: Failed to load or process positional data from {resolved_path}: {e}")
            self.data_loaded = False
            return False

    def map_to_position(self, datetime_array, data_type='longitude', unwrap_angles=False):
        """
        Maps an array of datetime objects (numpy.datetime64) to their
        corresponding positional values using interpolation.

        Args:
            datetime_array: NumPy array of numpy.datetime64 objects.
            data_type: Type of positional data to map to ('radial', 'longitude', or 'latitude')
            unwrap_angles: If True, keep angular values unwrapped when crossing the 0°/360° boundary.
                          For "degrees from perihelion" calculations, set this to True. Default: False.

        Returns:
            NumPy array of positional values, or None if mapping fails.
        """
        print_manager.processing(f"[MAP_TO_POSITION_ENTRY] Called for data_type: {data_type}. Input datetime_array length: {len(datetime_array) if datetime_array is not None else 'None'}")
        if datetime_array is not None and len(datetime_array) > 5:
            print_manager.processing(f"  Input datetime_array (first 3): {datetime_array[:3]}")
            print_manager.processing(f"  Input datetime_array (last 3): {datetime_array[-3:]}")
        elif datetime_array is not None:
            print_manager.processing(f"  Input datetime_array: {datetime_array}")

        if not self.data_loaded or self.times_numeric is None:
            print_manager.warning("Positional data not properly loaded, cannot map to positions.")
            return None

        # Determine which data array to use based on data_type
        if data_type == 'r_sun':
            positional_values = self.radial_values
            data_units = "R_sun"
        elif data_type == 'carrington_lon':
            positional_values = self.longitude_values
            data_units = "deg"
        elif data_type == 'carrington_lat':
            positional_values = self.latitude_values
            data_units = "deg"
        else:
            print_manager.warning(f"Invalid data_type: {data_type}. Must be 'r_sun', 'carrington_lon', or 'carrington_lat'.")
            return None
            
        if positional_values is None:
            print_manager.warning(f"No {data_type} data available in the loaded positional data file.")
            return None

        # Ensure input is always a numpy array, even if a single datetime64 is passed
        if not isinstance(datetime_array, np.ndarray) or datetime_array.ndim == 0:
             try:
                 # Attempt to convert scalar or 0-dim array to 1-element array
                 datetime_array = np.array([datetime_array])
                 print_manager.debug(f"Converted scalar/0-dim input to 1-element array. New shape: {datetime_array.shape}")
             except Exception as e:
                 print_manager.warning(f"Could not convert input {type(datetime_array)} to a NumPy array: {e}")
                 return None

        # Try to convert different datetime types to numpy.datetime64 if needed
        if not np.issubdtype(datetime_array.dtype, np.datetime64):
            print_manager.debug(f"Input array has dtype {datetime_array.dtype}, attempting to convert to datetime64")
            try:
                # First try pandas conversion which handles many formats
                datetime_array = pd.to_datetime(datetime_array).to_numpy()
                print_manager.status(f"Successfully converted input to datetime64 format")
            except Exception as e:
                print_manager.warning(f"Failed to convert input to datetime64: {str(e)}")
                return None

        if len(datetime_array) == 0:
            print_manager.debug("Input datetime_array is empty, returning empty positional array.")
            return np.array([]) # Return empty array for empty input

        try:
            # Ensure reference arrays are float64 for interpolation
            ref_times_numeric = self.times_numeric.astype(np.float64)
            query_times_numeric = datetime_array.astype('datetime64[ns]').astype(np.int64) / 1e9
            
            # --- DEBUG: Print interpolation inputs ---
            print_manager.debug(f"[Interp Debug] ref_times_numeric: dtype={ref_times_numeric.dtype}, min={ref_times_numeric.min()}, max={ref_times_numeric.max()}, sample={ref_times_numeric[:3]}")
            print_manager.debug(f"[Interp Debug] query_times_numeric: dtype={query_times_numeric.dtype}, min={query_times_numeric.min()}, max={query_times_numeric.max()}, sample={query_times_numeric[:3]}")
            # Print first and last reference/query times as dates
            ref_first = pd.to_datetime(ref_times_numeric[0]*1e9)
            ref_last = pd.to_datetime(ref_times_numeric[-1]*1e9)
            query_first = pd.to_datetime(query_times_numeric[0]*1e9)
            query_last = pd.to_datetime(query_times_numeric[-1]*1e9)
            print_manager.debug(f"[Interp Debug] ref_times: {ref_first} to {ref_last}")
            print_manager.debug(f"[Interp Debug] query_times: {query_first} to {query_last}")
            
            # --- SPECIAL HANDLING FOR CARRINGTON LONGITUDE (CIRCULAR ANGLE) ---
            # This prevents interpolation issues when crossing the 0°/360° boundary
            if data_type == 'carrington_lon':
                # Make a copy of the original reference values
                ref_values = positional_values.astype(np.float64).copy()
                
                # Check for 0°/360° boundary crossings in reference data
                # Look for large jumps between adjacent points (greater than 180°)
                jumps = np.abs(np.diff(ref_values))
                
                if np.any(jumps > 180):
                    print_manager.debug("*** DETECTED 0°/360° BOUNDARY CROSSING IN LONGITUDE DATA ***")
                    print_manager.debug(f"Found {np.sum(jumps > 180)} boundary crossings")

                    # Need to "unwrap" the longitude to create a continuous sequence
                    # This is similar to np.unwrap for phase angles, but customized for longitude
                    unwrapped = np.zeros_like(ref_values)
                    unwrapped[0] = ref_values[0]  # Start with first point
                    offset = 0
                    
                    # Process each point, adjusting by 360° when a boundary is crossed
                    for i in range(1, len(ref_values)):
                        diff = ref_values[i] - ref_values[i-1]
                        if diff > 180:  # Crossing from near 360° to near 0°
                            offset -= 360
                        elif diff < -180:  # Crossing from near 0° to near 360°
                            offset += 360
                        unwrapped[i] = ref_values[i] + offset
                    
                    # For debugging, show original vs unwrapped for sample points
                    print_manager.debug("Unwrapping longitude data for interpolation:")
                    n_sample = min(5, len(ref_values))
                    print_manager.debug(f"  Original (first {n_sample}): {ref_values[:n_sample]}")
                    print_manager.debug(f"  Unwrapped (first {n_sample}): {unwrapped[:n_sample]}")
                    
                    # Check if unwrapping makes sense by calculating max/min
                    orig_range = np.max(ref_values) - np.min(ref_values)
                    unwrap_range = np.max(unwrapped) - np.min(unwrapped)
                    print_manager.debug(f"  Original range: {orig_range:.2f}°")
                    print_manager.debug(f"  Unwrapped range: {unwrap_range:.2f}°")
                    
                    # Use unwrapped values for interpolation
                    interp_values = np.interp(
                        query_times_numeric, 
                        ref_times_numeric, 
                        unwrapped,  # Use unwrapped longitude for continuous interpolation
                        left=np.nan, 
                        right=np.nan
                    )
                    
                    if not unwrap_angles:
                        # Wrap back to [0, 360) range for regular longitude plotting
                        interp_values = np.mod(interp_values, 360)
                else:
                    # No boundary crossing detected - use regular interpolation
                    interp_values = np.interp(
                        query_times_numeric, 
                        ref_times_numeric, 
                        ref_values,
                        left=np.nan, 
                        right=np.nan
                    )
            else:
                # For non-angular data, use regular interpolation
                interp_values = np.interp(
                    query_times_numeric, 
                    ref_times_numeric, 
                    positional_values.astype(np.float64),
                    left=np.nan, 
                    right=np.nan
                )

            # --- DEBUG: Print interpolation output ---
            print_manager.debug(f"  [Mapper Debug] np.interp output (first 5): {interp_values[:5]}")
            # --- END DEBUG ---
            print_manager.processing(f"[MAP_TO_POSITION_EXIT] Returning interp_values. Length: {len(interp_values) if interp_values is not None else 'None'}")
            if interp_values is not None and len(interp_values) > 5:
                print_manager.processing(f"  Output interp_values (first 3): {interp_values[:3]}")
                print_manager.processing(f"  Output interp_values (last 3): {interp_values[-3:]}")
            elif interp_values is not None:
                print_manager.processing(f"  Output interp_values: {interp_values}")
            return interp_values
        except Exception as e:
            print_manager.error(f"Error during interpolation for {data_type}: {e}")
            return None

print('Positional Data Helper Initialized')

# Backward compatibility aliases
PositionalDataMapper = XAxisPositionalDataMapper
LongitudeMapper = XAxisPositionalDataMapper

# Utility function for command-line testing
def test_positional_mapping(data_path=None, date_str=None, data_type='carrington_lon'):
    """
    Utility function to test positional mapping from the command line.
    
    Args:
        data_path (str, optional): Path to positional data file. Uses default if None.
        date_str (str, optional): Date string to test mapping for. Uses current time if None.
        data_type (str, optional): Type of positional data to test ('r_sun', 'carrington_lon', or 'carrington_lat').
    """
    import sys
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta
    
    # Get data path from arguments if not provided
    if data_path is None and len(sys.argv) > 1:
        data_path = sys.argv[1]
    
    # Get test date from arguments if not provided
    if date_str is None and len(sys.argv) > 2:
        date_str = sys.argv[2]
        
    # Get data type from arguments if not provided
    if data_type == 'carrington_lon' and len(sys.argv) > 3:
        data_type = sys.argv[3]
    
    # Initialize mapper with specified or default path
    if data_path:
        mapper = XAxisPositionalDataMapper(data_path)
    else:
        # Use default path
        current_dir = pathlib.Path(__file__).parent.resolve()
        default_path = str(current_dir / "../support_data/trajectories/Parker_positional_data.npz")
        mapper = XAxisPositionalDataMapper(default_path)
    
    if not mapper.data_loaded:
        print("Failed to load positional data!")
        return
    
    # Create test timestamps
    if date_str:
        # Parse the provided date string
        center_date = pd.to_datetime(date_str)
    else:
        # Use recent default date for testing
        center_date = pd.to_datetime("2023-09-27 23:28:00.000")  # Enc 17 perihelion
    
    # Create a range of test dates around the center date
    dates = []
    for i in range(-12, 13, 1):  # -12 to +12 hours
        dates.append(center_date + timedelta(hours=i))
    
    test_dates = np.array(dates)
    print(f"Testing {len(test_dates)} dates from {test_dates[0]} to {test_dates[-1]}")
    
    # Test mapping
    positional_values = mapper.map_to_position(test_dates, data_type)
    
    if positional_values is None:
        print("Mapping failed!")
        return
    
    print(f"Successfully mapped {len(positional_values)} points")
    
    # Get appropriate units for y-axis label
    if data_type == 'r_sun':
        y_label = "Radial Distance (R_sun)"
    elif data_type == 'carrington_lon':
        y_label = "Carrington Longitude (deg)"
    elif data_type == 'carrington_lat':
        y_label = "Carrington Latitude (deg)"
    else:
        y_label = f"{data_type.capitalize()} Value"
    
    # Plot the result
    plt.figure(figsize=(10, 6))
    plt.plot(test_dates, positional_values, 'b-o')
    plt.title(f"Timestamp to {data_type.capitalize()} Mapping Test")
    plt.xlabel("Date")
    plt.ylabel(y_label)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{data_type}_mapping_test.png")
    print(f"Saved plot to {data_type}_mapping_test.png")
    plt.show()

# Run the test if this module is executed directly
if __name__ == "__main__":
    # Default to longitude for backward compatibility
    test_positional_mapping() 