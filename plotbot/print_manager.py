"""
Print manager for consistent output formatting across different modules.

This module provides structured logging levels and consistent formatting
to improve debugging and user feedback.
"""

import inspect
import datetime
import os
import logging
import numpy as np # Need numpy for datetime_as_string

# --- Custom Filter to Block Specific Pyspedas INFO Messages ---
class PyspedasInfoFilter(logging.Filter):
    """Filters out common, verbose INFO messages from pyspedas."""
    def filter(self, record):
        # Return False to block the message, True to allow it
        msg = record.getMessage()
        # --- DEBUG PRINT --- 
        # print(f"[Filter Check] Received log message: '{msg[:50]}...'") # Removed diagnostic
        # Block the specific INFO messages we want to hide
        should_block = False
        if "Searching for local files..." in msg:
            should_block = True
        if "No local files found for" in msg:
            should_block = True
        if "Downloading remote index:" in msg:
            should_block = True
        if "File is current:" in msg:
            should_block = True
        # Allow all other messages to pass
        return not should_block
# --- End Custom Filter ---

def format_datetime_for_log(dt):
    """Formats a datetime object (Python or numpy) for logging.
    Removes microseconds if all zero, otherwise uses millisecond precision.
    Returns the original input if formatting fails.
    """
    try:
        # Handle numpy.datetime64
        if isinstance(dt, np.datetime64):
            # Convert to string with nanoseconds first to check for all zeros
            # Use 's' unit to avoid auto-adding timezone if not present
            dt_str_ns = np.datetime_as_string(dt, unit='ns') 
            if dt_str_ns.endswith('000000000'): # Check for zero nanoseconds
                 # Format without microseconds
                 return np.datetime_as_string(dt, unit='s')
            elif dt_str_ns.endswith('000'): # Check for zero microseconds
                 # Format with millisecond precision
                 return np.datetime_as_string(dt, unit='ms')
            else: 
                 # Keep microsecond precision if microseconds are non-zero
                 return np.datetime_as_string(dt, unit='us')
                 
        # Handle Python datetime objects
        elif isinstance(dt, datetime.datetime):
            if dt.microsecond == 0:
                return dt.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                 # Format with millisecond precision
                 return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
                 
        # Handle strings (assume already partially formatted)
        elif isinstance(dt, str):
             if dt.endswith('.000000'):
                 return dt[:-7]
             elif dt.endswith('.000'): # Also handle if already ms
                 return dt[:-4] 
             # Add more specific string checks if needed (e.g., for 'YYYY-MM-DD/HH:MM:SS.ffffff')
             if '/' in dt and '.000000' in dt:
                 return dt.replace('.000000', '')
             return dt # Return string as is if no specific format matches
             
        # Return original object if type is not handled
        return dt
    except Exception as e:
        # Fallback: return the original input if any error occurs
        # Optionally log the error here if needed
        # print(f"[DEBUG] Error formatting datetime {dt}: {e}") 
        return dt

class print_manager_class:
    """
    Print manager class for consistent formatted output.
    
    This class provides methods for printing with different categories
    and severity levels, with the ability to enable/disable each type.
    
    Properties:
        show_debug: Enable/disable detailed technical diagnostic information
        show_custom_debug: Enable/disable custom variable operations debugging
        show_variable_testing: Enable/disable variable testing specific debugging
        show_variable_basic: Enable/disable basic user-facing variable info
        show_status: Alias for show_variable_basic
        show_error: Enable/disable error messages (recommended to keep enabled)
        show_time_tracking: Enable/disable time range tracking 
        show_test: Enable/disable test output
        show_data_cubby: Enable/disable data cubby specific debug output
        show_module_prefix: Enable/disable showing the module name prefix (e.g., [print_manager])
        show_processing: Enable/disable data processing status messages
        show_category_prefix: Enable/disable category prefixes like [DEBUG], [PROCESS], etc.
        show_warning: Enable/disable warning messages
        pyspedas_verbose: Enable/disable verbose INFO messages from pyspedas library (default: True)
    """
    
    # Turn on/off by type
    DEBUG = False
    WARNING = False
    ERROR = True     # Keep error enabled for safety
    VARIABLE_TESTING = False
    VARIABLE_BASIC = False
    MULTIPLOT = False
    MAIN_DEBUG = False
    DATA_CUBBY = False
    MANU_DATA_IN = False
    CUSTOM_DEBUG = False
    PV_TESTING = False
    ZARR_INTEGRATION = False  # Disabled by default; enable for Zarr debugging
    DEPENDENCY_MANAGEMENT = False # New style for dependency management prints
    
    # Colors for class-level access
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    DEFAULT = '\033[39m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    RESET = '\033[0m'
    
    def __init__(self):
        """Initialize the print manager with default settings."""
        # print("[PM_DEBUG] print_manager.__init__ called") # Remove print
        # Debug flags - enable/disable different categories
        self.debug_mode = False            # Detailed technical diagnostic information
        self.custom_debug_enabled = False  # Custom variable operations debugging
        self.variable_testing_enabled = False # Variable testing specific debugging
        self.variable_basic_enabled = False   # Basic user-facing variable info 
        self.error_enabled = True            # Error messages
        self.time_tracking_enabled = False    # Time range tracking
        self.test_enabled = False             # Test output
        self.module_prefix_enabled = False    # Show module name prefix 
        self.processing_enabled = False       # Show data processing status messages 
        self.category_prefix_enabled = False  # Show category prefixes 
        self.warning_enabled = False         # Show warning messages (renamed from warnings_enabled)
        self._pyspedas_verbose = False   # State variable for the pyspedas_verbose property
        self.pyspedas_filter_instance = None  # Instance of the PyspedasInfoFilter
        self.data_snapshot_enabled = False # <<< ADDED: Flag for snapshot messages
        self.dependency_management_enabled = False # Flag for dependency management prints
        # print(f"[RAW_PM_INIT] Initial self.processing_enabled: {self.processing_enabled}") # ADDED DIAGNOSTIC
        # print(f"[PM_DEBUG] __init__: Default _pyspedas_verbose = {self._pyspedas_verbose}") # Remove print
        
        # Print formatting prefixes
        self.debug_prefix = "[DEBUG] "
        self.custom_debug_prefix = "[CUSTOM_DEBUG] "
        self.variable_testing_prefix = "[VAR] "
        self.variable_basic_prefix = ""      # No prefix for basic user output
        self.error_prefix = "[ERROR] "
        self.time_tracking_prefix = "[TIME] "
        self.test_prefix = "[TEST] "         # Test output prefix
        self.processing_prefix = "[PROCESS] "  # Processing status prefix
        self.snapshot_prefix = "[SNAPSHOT] " # <<< ADDED: Prefix for snapshot messages
        self.dependency_management_prefix = "[DEPENDENCY] " # Prefix for dependency management prints
        
        # Severity levels
        self.level_warning = "[WARNING] "    # Warnings
        self.level_info = "[INFO] "          # Informational messages
        self.level_trace = "[TRACE] "        # Detailed tracing information
        
        # Component markers for structured logs
        self._component_markers = {
            'math': "[MATH] ",
            'data': "[DATA] ",
            'plot': "[PLOT] ",
            'recalc': "[RECALC] ",
            'import': "[IMPORT] ",
            'time': "[TIME] "
        }

        # --- DEBUG PRINT --- 
        # print("[print_manager.__init__] Calling initial _configure_pyspedas_logging") # Removed diagnostic
        # Initial configuration of pyspedas logging based on default flag
        self._configure_pyspedas_logging()

    def _configure_pyspedas_logging(self):
        """Applies or removes the filter for pyspedas INFO messages."""
        # print(f"[PM_DEBUG] _configure_pyspedas_logging: Called. Current self._pyspedas_verbose = {self._pyspedas_verbose}") # Remove print
        try:
            # --- REMOVED Import config and is_spdf_mode check ---
            # from . import config # Use relative import
            # is_spdf_mode = (config.data_server == 'spdf')
            # print(f"[PM_DEBUG] _configure_pyspedas_logging: Checked config.data_server = '{config.data_server}'. is_spdf_mode = {is_spdf_mode}") # Add print

            # --- REMOVED Early exit for non-SPDF mode ---
            # if not is_spdf_mode:
            #     # If not in SPDF mode, ensure filter is removed and level is default
            #     root_logger = logging.getLogger()
            #     if self.pyspedas_filter_instance is not None and self.pyspedas_filter_instance in root_logger.filters:
            #         root_logger.removeFilter(self.pyspedas_filter_instance)
            #     root_logger.setLevel(logging.WARNING) # Reset to default
            #     print("[PM_DEBUG] _configure_pyspedas_logging: Not SPDF mode. Ensured filter removed, level=WARNING.") # Add print
            #     return # Exit early, no SPDF-specific logging needed

            # --- Always proceed with verbose toggle logic, targeting root logger ---
            root_logger = logging.getLogger() # Get the root logger
            # print(f"[PM_DEBUG] _configure_pyspedas_logging: Current Root Level={logging.getLevelName(root_logger.level)}, Filters={root_logger.filters}") # Remove print

            if not self._pyspedas_verbose:
                # print("[PM_DEBUG] _configure_pyspedas_logging: Condition: self._pyspedas_verbose is False. Applying filter.") # Remove print
                # Suppress verbose info messages
                
                # --- Ensure filter instance exists --- 
                if self.pyspedas_filter_instance is None:
                    self.pyspedas_filter_instance = PyspedasInfoFilter()
                    # print("[PM_DEBUG] _configure_pyspedas_logging: Filter instance CREATED.") # Remove print
                
                # --- Add filter to ROOT logger --- 
                if self.pyspedas_filter_instance not in root_logger.filters:
                    root_logger.addFilter(self.pyspedas_filter_instance)
                    # print("[PM_DEBUG] _configure_pyspedas_logging: Filter ADDED to root logger.") # Remove print
                # else:
                    # print("[PM_DEBUG] _configure_pyspedas_logging: Filter already present on root logger.") # Remove print
                
                # Set ROOT level to INFO so the filter can catch messages
                root_logger.setLevel(logging.INFO)
                # print(f"[PM_DEBUG] _configure_pyspedas_logging: Set root logger level to INFO.") # Remove print
                
                # Use internal print for status to avoid recursion if self.debug uses logging
                # print("[PRINT_MANAGER_STATUS] Configured ROOT logging: Suppressed INFO (Level=INFO, Filter added).") # Remove print

            else:
                # print("[PM_DEBUG] _configure_pyspedas_logging: Condition: self._pyspedas_verbose is True. Removing filter.") # Remove print
                # Restore verbose info messages
                
                # --- Remove filter from ROOT logger --- 
                if self.pyspedas_filter_instance is not None and self.pyspedas_filter_instance in root_logger.filters:
                    root_logger.removeFilter(self.pyspedas_filter_instance)
                    # print("[PM_DEBUG] _configure_pyspedas_logging: Filter REMOVED from root logger.") # Remove print
                # else:
                    # print("[PM_DEBUG] _configure_pyspedas_logging: Filter not found on root logger or instance is None.") # Remove print
                
                # Set ROOT level to INFO to allow verbose messages through
                root_logger.setLevel(logging.INFO) 
                # print(f"[PM_DEBUG] _configure_pyspedas_logging: Set root logger level to INFO.") # Remove print
                
                # Use internal print for status
                # print("[PRINT_MANAGER_STATUS] Configured ROOT logging: Verbose (Level=INFO, Filter removed).") # Remove print
                
            # print(f"[PM_DEBUG] _configure_pyspedas_logging: END STATE: Root Level={logging.getLevelName(root_logger.level)}, Filters={root_logger.filters}") # Remove print

        except Exception as e:
            # Use internal print to avoid loop if print_manager itself fails
            print(f"[PRINT_MANAGER_ERROR] Failed to configure pyspedas logging: {e}")

    def _format_message(self, msg, component=None):
        """Format the message with appropriate markers based on where it was called from."""
        # Add component marker if specified (e.g., [MATH], [DATA], etc.)
        if component in self._component_markers:
            component_marker = self._component_markers[component]
            msg = f"{component_marker}{msg}"
        
        # Get the caller module name for context (if enabled)
        if self.module_prefix_enabled:
            caller_module = self._get_caller_module()
            caller_marker = f"[{caller_module}] " if caller_module else ""
            return f"{caller_marker}{msg}"
        else:
            return msg
    
    def debug(self, msg):
        """Print debug message if debug is enabled."""
        if self.debug_mode:
            prefix = self.debug_prefix if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}{msg}"))
            
    def error(self, msg):
        """Print error message (always enabled)."""
        if self.error_enabled:
            prefix = self.error_prefix if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}{msg}"))
            
    def warning(self, msg):
        """Print warning message (always enabled)."""
        if self.error_enabled and self.warning_enabled:  # Use same setting as error plus warning toggle
            prefix = self.level_warning if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}{msg}"))
            
    def custom_debug(self, msg):
        """Print custom variable debugging message if enabled."""
        if self.custom_debug_enabled:
            prefix = self.custom_debug_prefix if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}{msg}"))
            
    def variable_testing(self, msg):
        """Print variable testing debug message if enabled."""
        if self.variable_testing_enabled:
            prefix = self.variable_testing_prefix if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}{msg}"))
            
    def variable_basic(self, msg):
        """Print basic variable information message if enabled."""
        if self.variable_basic_enabled:
            prefix = self.variable_basic_prefix if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}{msg}"))
            
    # Component-specific logs for clearer debugging
    def math(self, msg, level="info"):
        """Log mathematics operations with appropriate level."""
        prefix = self._get_level_prefix(level)
        self.custom_debug(f"{prefix}{self._component_markers['math']}{msg}")
        
    def data(self, msg, level="info"):
        """Log data handling operations with appropriate level."""
        prefix = self._get_level_prefix(level)
        self.custom_debug(f"{prefix}{self._component_markers['data']}{msg}")
    
    def plot(self, msg, level="info"):
        """Log plotting operations with appropriate level."""
        prefix = self._get_level_prefix(level)
        self.custom_debug(f"{prefix}{self._component_markers['plot']}{msg}")
        
    def recalc(self, msg, level="info"):
        """Log recalculation operations with appropriate level."""
        prefix = self._get_level_prefix(level)
        self.custom_debug(f"{prefix}{self._component_markers['recalc']}{msg}")
    
    def import_log(self, msg, level="info"):
        """Log import operations with appropriate level."""
        prefix = self._get_level_prefix(level)
        self.custom_debug(f"{prefix}{self._component_markers['import']}{msg}")
    
    def time_tracking(self, msg):
        """Track and print time range related information for debugging."""
        if self.time_tracking_enabled:
            # Get caller function name for better context
            caller_frame = inspect.currentframe().f_back
            caller_function = caller_frame.f_code.co_name
            caller_lineno = caller_frame.f_lineno
            caller_file = os.path.basename(caller_frame.f_code.co_filename)
            
            location = f"{caller_file}:{caller_function}:{caller_lineno}"
            prefix = self.time_tracking_prefix if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}[{location}] {msg}"))
    
    def time_input(self, function_name, trange):
        """Track input time range to a function."""
        if self.time_tracking_enabled:
            prefix = self.time_tracking_prefix if self.category_prefix_enabled else ""
            if isinstance(trange, list) and len(trange) >= 2:
                print(self._format_message(f"{prefix}➡️ {function_name} INPUT: {trange[0]} to {trange[1]}"))
            else:
                print(self._format_message(f"{prefix}➡️ {function_name} INPUT: {trange}"))
    
    def time_output(self, function_name, trange):
        """Track output time range from a function."""
        if self.time_tracking_enabled:
            prefix = self.time_tracking_prefix if self.category_prefix_enabled else ""
            if isinstance(trange, list) and len(trange) >= 2:
                print(self._format_message(f"{prefix}⬅️ {function_name} OUTPUT: {trange[0]} to {trange[1]}"))
            else:
                print(self._format_message(f"{prefix}⬅️ {function_name} OUTPUT: {trange}"))
    
    def time_transform(self, function_name, input_trange, output_trange):
        """Track transformation of time range within a function."""
        if self.time_tracking_enabled:
            prefix = self.time_tracking_prefix if self.category_prefix_enabled else ""
            in_str = f"{input_trange[0]} to {input_trange[1]}" if isinstance(input_trange, list) and len(input_trange) >= 2 else str(input_trange)
            out_str = f"{output_trange[0]} to {output_trange[1]}" if isinstance(output_trange, list) and len(output_trange) >= 2 else str(output_trange)
            print(self._format_message(f"{prefix}🔄 {function_name} TRANSFORM: {in_str} → {out_str}"))
    
    def _get_level_prefix(self, level):
        """Get the prefix for the specified severity level."""
        if level == "warning":
            return self.level_warning
        elif level == "trace":
            return self.level_trace
        else:
            return self.level_info
    
    # Helper methods for common patterns
    def operation_start(self, operation, args=None):
        """Log the start of an operation with relevant arguments."""
        arg_str = f" with args: {args}" if args else ""
        self.custom_debug(f"Starting operation: {operation}{arg_str}")
        
    def operation_result(self, operation, result=None):
        """Log the result of an operation."""
        result_str = f": {result}" if result is not None else ""
        self.custom_debug(f"Completed operation: {operation}{result_str}")
    
    def array_info(self, name, array):
        """Log information about an array (shape, type, sample values)."""
        if hasattr(array, 'shape'):
            shape_info = f"shape={array.shape}"
        elif hasattr(array, '__len__'):
            shape_info = f"length={len(array)}"
        else:
            shape_info = "no shape info"
            
        type_info = f"type={type(array).__name__}"
        
        # Sample values (safely)
        if hasattr(array, '__len__') and len(array) > 0:
            try:
                if len(array) > 3:
                    sample = f"first 3 values=[{array[0]}, {array[1]}, {array[2]}...]"
                else:
                    sample = f"values={array}"
            except:
                sample = "cannot sample"
        else:
            sample = "empty or not indexable"
            
        self.custom_debug(f"Array '{name}': {shape_info}, {type_info}, {sample}")

    def datacubby(self, msg, color=None):
        """Print data cubby specific messages for backward compatibility, with optional color."""
        color_code = color if color else ''
        reset_code = self.RESET if color else ''
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print(f"{color_code}[CUBBY] {msg}{reset_code}")
        elif hasattr(self, 'show_data_cubby') and self.show_data_cubby:
            print(f"{color_code}[CUBBY] {msg}{reset_code}")
            
    # Properties for consistent naming convention
    @property
    def show_debug(self):
        """Get the current state of debug output."""
        return self.debug_mode
        
    @show_debug.setter
    def show_debug(self, value):
        """Set whether debug output is enabled."""
        self.debug_mode = value
        
    @property
    def show_status(self):
        """Get the current state of status output. Alias for show_variable_basic."""
        return self.variable_basic_enabled
        
    @show_status.setter
    def show_status(self, value):
        """Set whether status output is enabled. Alias for show_variable_basic."""
        self.variable_basic_enabled = value
        
    @property
    def show_variable_testing(self):
        """Get the current state of variable testing output."""
        return self.variable_testing_enabled
        
    @show_variable_testing.setter
    def show_variable_testing(self, value):
        """Set whether variable testing output is enabled."""
        self.variable_testing_enabled = value
        
    @property
    def show_variable_basic(self):
        """Get the current state of basic variable output."""
        return self.variable_basic_enabled
        
    @show_variable_basic.setter
    def show_variable_basic(self, value):
        """Set whether basic variable output is enabled."""
        self.variable_basic_enabled = value
        
    @property
    def show_custom_debug(self):
        """Get the current state of custom debug output."""
        return self.custom_debug_enabled
        
    @show_custom_debug.setter
    def show_custom_debug(self, value):
        """Set whether custom debug output is enabled."""
        self.custom_debug_enabled = value
        
    @property
    def show_time_tracking(self):
        """Get the current state of time tracking output."""
        return self.time_tracking_enabled
        
    @show_time_tracking.setter
    def show_time_tracking(self, value):
        """Set whether time tracking output is enabled."""
        self.time_tracking_enabled = value
        
    @property
    def show_test(self):
        """Get the current state of test output."""
        return self.test_enabled
        
    @show_test.setter
    def show_test(self, value):
        """Set whether test output is enabled."""
        self.test_enabled = value
        
    @property
    def show_error(self):
        """Get the current state of error output."""
        return self.error_enabled
        
    @show_error.setter
    def show_error(self, value):
        """Set whether error output is enabled (recommended to keep enabled)."""
        self.error_enabled = value
        
    @property
    def show_module_prefix(self):
        """Get the current state of the module prefix display."""
        return self.module_prefix_enabled
        
    @show_module_prefix.setter
    def show_module_prefix(self, value):
        """Set whether to show the module name prefix in output messages."""
        self.module_prefix_enabled = value
        
    @property
    def show_processing(self):
        """Get the current state of processing status message display."""
        return self.processing_enabled
        
    @show_processing.setter
    def show_processing(self, value):
        """Set whether to show data processing status messages."""
        self.processing_enabled = value
        # print(f"[RAW_PM_SETTER] show_processing setter. Value: {value}. self.processing_enabled is now: {self.processing_enabled}") # ADDED DIAGNOSTIC
        
    @property
    def show_category_prefix(self):
        """Get the current state of category prefix display."""
        return self.category_prefix_enabled
        
    @show_category_prefix.setter
    def show_category_prefix(self, value):
        """Set whether to show category prefixes like [DEBUG], [PROCESS], etc."""
        self.category_prefix_enabled = value
        
    @property
    def show_warning(self):
        """Get the current state of warning display."""
        return self.warning_enabled
        
    @show_warning.setter
    def show_warning(self, value):
        """Set whether to show warning messages."""
        self.warning_enabled = value
        
    @property
    def pyspedas_verbose(self):
        """Whether to allow pyspedas INFO messages to be shown."""
        return self._pyspedas_verbose
        
    @pyspedas_verbose.setter
    def pyspedas_verbose(self, value):
        """Set whether pyspedas INFO messages should be shown."""
        # print(f"[PM_DEBUG] pyspedas_verbose.setter: Received value={value}. Current self._pyspedas_verbose={self._pyspedas_verbose}") # Remove print
        if not isinstance(value, bool):
            print("[PRINT_MANAGER_WARNING] pyspedas_verbose must be set to True or False.")
            return
            
        if self._pyspedas_verbose != value:
            self._pyspedas_verbose = value # Update the state variable
            # print(f"[PM_DEBUG] pyspedas_verbose.setter: Updated self._pyspedas_verbose to {self._pyspedas_verbose}. Calling _configure_pyspedas_logging...") # Remove print
            self._configure_pyspedas_logging() # Reconfigure logging immediately
        # else:
             # print(f"[PM_DEBUG] pyspedas_verbose.setter: Value {value} is same as current. No change needed.") # Remove print
             # pass # pass removed as else block is now empty

    # Initialize show_data_cubby for backward compatibility
    show_data_cubby = False

    def status(self, msg):
        """Print status message for backward compatibility."""
        if self.variable_basic_enabled:
            print(self._format_message(f"{msg}"))

    def _get_caller_module(self):
        """Get the name of the module that called the print manager."""
        caller_frame = inspect.currentframe().f_back.f_back
        caller_module = inspect.getmodule(caller_frame)
        module_name = caller_module.__name__ if caller_module else "unknown"
        return module_name.replace("plotbot.", "")  # Simplify module name

    def test(self, msg):
        """Print test-specific diagnostic message if enabled."""
        if self.test_enabled:
            prefix = self.test_prefix if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}{msg}"))
            
    def enable_debug(self):
        """
        Enable all debug output.
        
        This is a convenience method that sets show_debug to True.
        """
        self.show_debug = True
        print("Debug mode enabled")
        
    def enable_test(self):
        """
        Enable only test output, disable other output types.
        
        This is used primarily during testing to focus output.
        """
        self.show_debug = False
        self.show_custom_debug = False
        self.show_variable_testing = False
        self.show_variable_basic = False
        self.show_time_tracking = False
        self.show_test = True
        print("Test-only mode enabled")

    def enable_data_cubby(self):
        """
        Enable data cubby debug output.
        
        This sets show_data_cubby to True for data cubby specific debugging.
        """
        self.show_data_cubby = True
        print("Data cubby debug output enabled")

    def processing(self, msg):
        """Print data processing status message if enabled."""
        # print(f"[RAW_PM_PROC_ENTRY] processing() called. msg: '{msg[:50]}...'. Current self.processing_enabled: {self.processing_enabled}") # ADDED DIAGNOSTIC
        if self.processing_enabled:
            # print(f"[RAW_PM_PROC_WILL_PRINT] processing_enabled is True. About to format/print msg: '{msg[:50]}...'") # ADDED DIAGNOSTIC
            prefix = self.processing_prefix if self.category_prefix_enabled else ""
            # print(self._format_message(f"{prefix}{msg}"))

    def zarr_integration(self, msg, color=None):
        """Print Zarr integration messages (magenta)."""
        if self.__class__.ZARR_INTEGRATION:
            print(f"{print_manager_class.MAGENTA}[ZARR] {msg}{print_manager_class.RESET}")

    def data_snapshot(self, msg):
        """Print data snapshot loading/saving messages if enabled."""
        if self.data_snapshot_enabled:
            prefix = self.snapshot_prefix if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}{msg}"))

    # <<< ADDED: Property for show_data_snapshot >>>
    @property
    def show_data_snapshot(self):
        """Get the current state of data snapshot message display."""
        return self.data_snapshot_enabled

    @show_data_snapshot.setter
    def show_data_snapshot(self, value):
        """Set whether to show data snapshot loading/saving messages."""
        self.data_snapshot_enabled = value
    # <<< END ADDED Property >>>

    def dependency_management(self, msg):
        """Print dependency management messages if enabled."""
        if self.dependency_management_enabled:
            prefix = self.dependency_management_prefix if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}{msg}"))

    @property
    def show_dependency_management(self):
        """Get the current state of dependency management output."""
        return self.dependency_management_enabled
        
    @show_dependency_management.setter
    def show_dependency_management(self, value):
        """Set whether dependency management output is enabled."""
        if not isinstance(value, bool):
            print("[PRINT_MANAGER_WARNING] show_dependency_management must be set to True or False.")
            return
        self.dependency_management_enabled = value

# Create a singleton instance
print_manager = print_manager_class()
