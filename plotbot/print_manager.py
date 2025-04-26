"""
Print manager for consistent output formatting across different modules.

This module provides structured logging levels and consistent formatting
to improve debugging and user feedback.
"""

import inspect
import datetime
import os
import logging

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

class print_manager_class:
    """
    Print manager class for consistent formatted output.
    
    This class provides methods for printing with different categories
    and severity levels, with the ability to enable/disable each type.
    
    Properties:
        show_debug: Enable/disable detailed technical diagnostic information
        show_custom_debug: Enable/disable custom variable operations debugging
        show_derived: Legacy alias for show_custom_debug
        show_variable_testing: Enable/disable variable testing specific debugging
        show_variable_basic: Enable/disable basic user-facing variable info
        show_status: Alias for show_variable_basic
        show_error: Enable/disable error messages (recommended to keep enabled)
        show_time_tracking: Enable/disable time range tracking 
        show_test: Enable/disable test output
        show_datacubby: Enable/disable data cubby specific debug output
        show_module_prefix: Enable/disable showing the module name prefix (e.g., [print_manager])
        show_processing: Enable/disable data processing status messages
        show_category_prefix: Enable/disable category prefixes like [DEBUG], [PROCESS], etc.
        show_warnings: Enable/disable warning messages
        pyspedas_verbose: Enable/disable verbose INFO messages from pyspedas library (default: True)
    """
    
    def __init__(self):
        """Initialize the print manager with default settings."""
        # Debug flags - enable/disable different categories
        self.debug_mode = False            # Detailed technical diagnostic information
        self.custom_debug_enabled = False  # Custom variable operations debugging
        self.derived_enabled = False       # Legacy alias for custom_debug_enabled
        self.variable_testing_enabled = False # Variable testing specific debugging
        self.variable_basic_enabled = False   # Basic user-facing variable info 
        self.error_enabled = False            # Error messages (always keep this enabled)
        self.time_tracking_enabled = False    # Time range tracking (enabled by default)
        self.test_enabled = False             # Test output (enabled by default)
        self.module_prefix_enabled = False    # Show module name prefix (enabled by default)
        self.processing_enabled = False       # Show data processing status messages (enabled by default)
        self.category_prefix_enabled = False  # Show category prefixes (enabled by default)
        self.warnings_enabled = False         # Show warning messages (enabled by default)
        self._pyspedas_verbose = False        # Control pyspedas INFO logging (default: now False)
        self._pyspedas_filter_instance = None # Store the filter instance
        
        # Print formatting prefixes
        self.debug_prefix = "[DEBUG] "
        self.custom_debug_prefix = "[CUSTOM_DEBUG] "
        self.derived_prefix = "[DERIVED] "   # Legacy alias for custom_debug_prefix
        self.variable_testing_prefix = "[VAR] "
        self.variable_basic_prefix = ""      # No prefix for basic user output
        self.error_prefix = "[ERROR] "
        self.time_tracking_prefix = "[TIME] "
        self.test_prefix = "[TEST] "         # Test output prefix
        self.processing_prefix = "[PROCESS] "  # Processing status prefix
        
        # Severity levels
        self.level_critical = "[CRITICAL] "  # Critical errors/warnings
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
        # --- DEBUG PRINT --- 
        # print(f"[Configure Logging] Running with self._pyspedas_verbose = {self._pyspedas_verbose}") # Removed diagnostic
        try:
            # --- Target both pyspedas logger AND root logger --- 
            pyspedas_logger = logging.getLogger('pyspedas')
            root_logger = logging.getLogger() # Get the root logger
            # --- DEBUG PRINT --- 
            # print(f"[Configure Logging] Got logger: {pyspedas_logger.name}, Level: {logging.getLevelName(pyspedas_logger.level)}, Propagate: {pyspedas_logger.propagate}, Filters: {pyspedas_logger.filters}") # Removed diagnostic
            # print(f"[Configure Logging] Got root logger: Level: {logging.getLevelName(root_logger.level)}, Filters: {root_logger.filters}, Handlers: {root_logger.handlers}") # Removed diagnostic

            if not self._pyspedas_verbose:
                # Suppress verbose info messages
                # print("[Configure Logging] Action: Trying to ADD filter to ROOT, set ROOT level INFO") # Removed diagnostic
                
                # --- Ensure filter instance exists --- 
                if self._pyspedas_filter_instance is None:
                    self._pyspedas_filter_instance = PyspedasInfoFilter()
                    # print("[Configure Logging]   Created filter instance.") # Removed diagnostic
                
                # --- Add filter to ROOT logger --- 
                if self._pyspedas_filter_instance not in root_logger.filters:
                    root_logger.addFilter(self._pyspedas_filter_instance)
                    # print("[Configure Logging]   Filter ADDED to ROOT logger.") # Removed diagnostic
                # else:
                    # print("[Configure Logging]   Filter already present on ROOT logger.") # Removed diagnostic
                
                # Set ROOT level to INFO so the filter can catch messages
                # We might need a handler on the root logger if none exists, 
                # but let's try level and filter first.
                root_logger.setLevel(logging.INFO)
                
                # Optionally keep configuring the specific pyspedas logger too?
                # For now, let's focus on the root logger as the source.
                # pyspedas_logger.setLevel(logging.INFO)
                # pyspedas_logger.propagate = False # Keep propagation off if root handles it
                
                self.debug("Configured ROOT logging: Suppressed INFO (Level=INFO, Filter added).")
                # --- DEBUG PRINT --- 
                # print(f"[Configure Logging] END STATE (Suppress): Root Level={logging.getLevelName(root_logger.level)}, Root Filters={root_logger.filters}") # Removed diagnostic
            else:
                # Restore verbose info messages
                # print("[Configure Logging] Action: Trying to REMOVE filter from ROOT, reset ROOT level") # Removed diagnostic
                
                # --- Remove filter from ROOT logger --- 
                if self._pyspedas_filter_instance is not None and self._pyspedas_filter_instance in root_logger.filters:
                    root_logger.removeFilter(self._pyspedas_filter_instance)
                    # print("[Configure Logging]   Filter REMOVED from ROOT logger.") # Removed diagnostic
                
                # Reset ROOT level to default (WARNING is common)
                root_logger.setLevel(logging.WARNING) 
                
                # Reset specific pyspedas logger too
                # pyspedas_logger.setLevel(logging.NOTSET)
                # pyspedas_logger.propagate = True
                
                self.debug("Configured ROOT logging: Verbose (Level=WARNING, Filter removed).")
                # --- DEBUG PRINT --- 
                # print(f"[Configure Logging] END STATE (Verbose): Root Level={logging.getLevelName(root_logger.level)}, Root Filters={root_logger.filters}") # Removed diagnostic

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
        elif "CRITICAL" in str(msg) or "DBG-CRITICAL" in str(msg):
            # Always print critical debug messages regardless of debug mode
            if self.module_prefix_enabled:
                print(f"[print_manager] [CRITICAL DEBUG] {msg}")
            else:
                print(f"[CRITICAL DEBUG] {msg}")
            
    def error(self, msg):
        """Print error message (always enabled)."""
        if self.error_enabled:
            prefix = self.error_prefix if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}{msg}"))
            
    def warning(self, msg):
        """Print warning message (always enabled)."""
        if self.error_enabled and self.warnings_enabled:  # Use same setting as error plus warnings toggle
            prefix = self.level_warning if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}{msg}"))
            
    def derived(self, msg):
        """Legacy method - print custom variable debugging message if enabled."""
        self.custom_debug(msg)
            
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
        if level == "critical":
            return self.level_critical
        elif level == "warning":
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

    def datacubby(self, msg):
        """Print data cubby specific messages for backward compatibility."""
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print(f"[CUBBY] {msg}")
        elif hasattr(self, 'show_datacubby') and self.show_datacubby:
            print(f"[CUBBY] {msg}")
            
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
    def show_derived(self):
        """Legacy property - get the current state of custom debug output."""
        return self.custom_debug_enabled
        
    @show_derived.setter
    def show_derived(self, value):
        """Legacy property - set whether custom debug output is enabled."""
        self.custom_debug_enabled = value
        self.derived_enabled = value  # Update both for consistency
        
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
        
    @property
    def show_category_prefix(self):
        """Get the current state of category prefix display."""
        return self.category_prefix_enabled
        
    @show_category_prefix.setter
    def show_category_prefix(self, value):
        """Set whether to show category prefixes like [DEBUG], [PROCESS], etc."""
        self.category_prefix_enabled = value
        
    @property
    def show_warnings(self):
        """Get the current state of warnings display."""
        return self.warnings_enabled
        
    @show_warnings.setter
    def show_warnings(self, value):
        """Set whether to show warning messages."""
        self.warnings_enabled = value
        
    @property
    def pyspedas_verbose(self):
        """Get the current state of pyspedas verbose INFO logging."""
        return self._pyspedas_verbose
        
    @pyspedas_verbose.setter
    def pyspedas_verbose(self, value):
        """Set whether pyspedas INFO messages should be shown."""
        # --- DEBUG PRINT --- 
        # print(f"[Setter Call] pyspedas_verbose trying to set to: {value} (Current: {self._pyspedas_verbose})") # Removed diagnostic
        if not isinstance(value, bool):
            print("[PRINT_MANAGER_WARNING] pyspedas_verbose must be set to True or False.")
            return
            
        if self._pyspedas_verbose != value:
            self._pyspedas_verbose = value
            self._configure_pyspedas_logging() # Reconfigure logging immediately

    # Initialize show_datacubby for backward compatibility
    show_datacubby = False

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
        self.show_derived = False  # Legacy alias
        self.show_variable_testing = False
        self.show_variable_basic = False
        self.show_time_tracking = False
        self.show_test = True
        print("Test-only mode enabled")

    def enable_datacubby(self):
        """
        Enable data cubby debug output.
        
        This sets show_datacubby to True for data cubby specific debugging.
        """
        self.show_datacubby = True
        print("Data cubby debug output enabled")

    def processing(self, msg):
        """Print data processing status message if enabled."""
        if self.processing_enabled:
            prefix = self.processing_prefix if self.category_prefix_enabled else ""
            print(self._format_message(f"{prefix}{msg}"))

# Create a singleton instance
print_manager = print_manager_class()
