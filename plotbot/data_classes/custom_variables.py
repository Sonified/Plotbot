import numpy as np
import types
from ..print_manager import print_manager
# from ..data_cubby import data_cubby # Moved inside functions
from ..data_tracker import global_tracker
from ..plotbot_helpers import time_clip

# List to hold custom variables
custom_variables_list = []

class CustomVariablesContainer:
    """
    Container for custom variables that follows the standard variable pattern
    used by other Plotbot classes.
    """
    
    def __init__(self):
        """Initialize the container"""
        # Dictionary to store variables by name
        self.variables = {}
        
        # Dictionary to store source variable references
        self.sources = {}
        
        # Dictionary to store operations
        self.operations = {}
        
        # Class name for data_cubby registration
        self.class_name = 'custom_class'
        
        # Register this instance in data_cubby
        from ..data_cubby import data_cubby
        data_cubby.stash(self, class_name='custom_class')
        print_manager.custom_debug("✨ Custom variables system initialized")
    
    def get_subclass(self, subclass_name):
        """
        Retrieve a specific variable by name.
        This matches the pattern used by other Plotbot classes.
        """
        if subclass_name not in self.variables:
            print_manager.custom_debug(f"Custom variable '{subclass_name}' not found")
            return None
        
        return self.variables[subclass_name]
    
    def register(self, name, variable, sources, operation):
        """
        Register a custom variable with its sources and operation
        
        Parameters
        ----------
        name : str
            Name of the variable
        variable : plot_manager
            The variable object
        sources : list
            List of source variables
        operation : str
            Operation type ('add', 'sub', 'mul', 'div')
        """
        # Store the variable
        self.variables[name] = variable
        
        # Store references to source variables for updates
        self.sources[name] = sources
        self.operations[name] = operation
        
        # Set variable metadata with more explicit naming
        object.__setattr__(variable, 'class_name', 'custom_class')
        object.__setattr__(variable, 'subclass_name', name)
        object.__setattr__(variable, 'data_type', 'custom_data_type')
        
        # Keep the existing y_label and legend_label values
        # They should already be set by the custom_variable function
        
                # Add an update method that routes to this container
        def update_method(self, trange):
            """Update method that routes to container"""
            from ..data_cubby import data_cubby
            custom_container = data_cubby.grab('custom_class')
            if custom_container:
                result = custom_container.update(name, trange)
                if result is not None:
                    return result
            return self
        
        object.__setattr__(variable, 'update', types.MethodType(update_method, variable))
        
        # Make the variable globally accessible
        self._make_globally_accessible(name, variable)
            
        print_manager.custom_debug(f"Registered custom variable: {name}")
        return variable
    
    def update(self, name, trange):
        """
        Update a custom variable for a new time range
        
        Parameters
        ----------
        name : str
            Name of the variable to update
        trange : list
            New time range [start, end]
            
        Returns
        -------
        plot_manager
            Updated variable
        """
        print_manager.custom_debug(f"Updating custom variable: {name}")
        
        # Get the variable and its sources
        variable = self.variables.get(name)
        sources = self.sources.get(name, [])
        operation = self.operations.get(name)
        
        if variable is None:
            print_manager.custom_debug(f"Custom variable '{name}' not found")
            return None
        
        if not sources:
            print_manager.custom_debug(f"No source variables for {name}")
            return variable
            
        if not operation:
            print_manager.custom_debug(f"No operation defined for {name}")
            return variable
            
        # Check if update is needed using data_tracker with variable-specific caching
        if not global_tracker.is_calculation_needed(trange, 'custom_data_type', name):
            print_manager.custom_debug(f"Calculation not needed for {name} - using cached data")
            return variable
        
        # Get fresh data for all source variables
        fresh_sources = []
        for src in sources:
            if hasattr(src, 'class_name') and hasattr(src, 'subclass_name'):
                # Get fresh reference from data_cubby
                from ..data_cubby import data_cubby
                fresh_src = data_cubby.grab_component(src.class_name, src.subclass_name)
                if fresh_src is not None:
                    # Ensure the source variable has data for this timerange
                    # This should already be done by plotbot, but we double check
                    if (hasattr(fresh_src, 'datetime_array') and fresh_src.datetime_array is not None and 
                        len(fresh_src.datetime_array) > 0):
                        # Check if source variable's time range covers our requested time range
                        src_start = np.datetime64(fresh_src.datetime_array[0])
                        src_end = np.datetime64(fresh_src.datetime_array[-1])
                        
                        try:
                            # Parse the requested time range
                            from datetime import datetime
                            req_start = np.datetime64(datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f'))
                            req_end = np.datetime64(datetime.strptime(trange[1], '%Y-%m-%d/%H:%M:%S.%f'))
                            
                            # Check if source covers the time range with a small buffer
                            buffer = np.timedelta64(10, 's')
                            if src_start - buffer > req_start or src_end + buffer < req_end:
                                print_manager.custom_debug(f"Source variable {src.class_name}.{src.subclass_name} doesn't fully cover requested time range")
                                print_manager.custom_debug(f"  Source: {src_start} to {src_end}")
                                print_manager.custom_debug(f"  Requested: {req_start} to {req_end}")
                                
                                # Instead of giving up, use whatever part of the time range is available
                                # This allows us to handle partial time range matches
                                overlap_start = max(src_start, req_start)
                                overlap_end = min(src_end, req_end)
                                print_manager.custom_debug(f"  Using overlapping range: {overlap_start} to {overlap_end}")
                                
                                # If the overlap is too small, we might still fail during calculation
                                if overlap_start >= overlap_end:
                                    print_manager.custom_debug(f"  ⚠️ No overlap between source and requested time ranges")
                                    # Continue anyway - other sources may have better coverage
                            else:
                                print_manager.custom_debug(f"Source variable time range verified: {src.class_name}.{src.subclass_name}")
                        except Exception as e:
                            print_manager.custom_debug(f"Error checking time range: {str(e)}")
                    
                    fresh_sources.append(fresh_src)
                    print_manager.custom_debug(f"Got fresh data for {src.class_name}.{src.subclass_name}")
                else:
                    print_manager.custom_debug(f"Could not get fresh data for {src.class_name}.{src.subclass_name}")
                    return variable
        
        # Check if we have the right number of sources for the operation
        # Scalar operations (like variable + 10) need 1 source, binary operations need 2
        expected_sources = 1 if operation in ['add', 'sub', 'mul', 'div'] and hasattr(variable, 'scalar_value') else 2
        
        if len(fresh_sources) < expected_sources:
            print_manager.custom_debug(f"Not enough fresh sources for {name}: got {len(fresh_sources)}, expected {expected_sources}")
            print_manager.custom_debug(f"Operation: {operation}, has scalar_value: {hasattr(variable, 'scalar_value')}")
            return variable
            
        # Import time_clip for time range handling
        from datetime import datetime
        
        # Determine the common time range - important for operations
        try:
            # Get start/end times for target range
            req_start = datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f')
            req_end = datetime.strptime(trange[1], '%Y-%m-%d/%H:%M:%S.%f')
            
            # Check if sources have data specifically in this time range
            source1_indices = None
            source2_indices = None
            
            if hasattr(fresh_sources[0], 'datetime_array') and fresh_sources[0].datetime_array is not None:
                source1_indices = time_clip(fresh_sources[0].datetime_array, trange[0], trange[1])
                print_manager.custom_debug(f"Source 1 has {len(source1_indices)} data points in requested time range")
            
            # For scalar operations, we only need to check the first source
            if len(fresh_sources) > 1:
                if hasattr(fresh_sources[1], 'datetime_array') and fresh_sources[1].datetime_array is not None:
                    source2_indices = time_clip(fresh_sources[1].datetime_array, trange[0], trange[1])
                    print_manager.custom_debug(f"Source 2 has {len(source2_indices)} data points in requested time range")
            
            # Only proceed if we have data points for the operation
            # For scalar operations, only check source 1; for binary operations, check both
            if source1_indices is None or len(source1_indices) == 0:
                print_manager.custom_debug(f"⚠️ Source 1 has no data points in requested time range")
                print_manager.custom_debug(f"Using original variable - cannot update for new time range")
                return variable
            
            if len(fresh_sources) > 1 and (source2_indices is None or len(source2_indices) == 0):
                print_manager.custom_debug(f"⚠️ Source 2 has no data points in requested time range")
                print_manager.custom_debug(f"Using original variable - cannot update for new time range")
                return variable
        except Exception as e:
            print_manager.custom_debug(f"Error checking for data in time range: {str(e)}")
        
        # Apply the operation with fresh data
        result = None
        try:
            # Handle scalar operations (1 source + scalar value) vs binary operations (2 sources)
            if hasattr(variable, 'scalar_value') and len(fresh_sources) == 1:
                # Scalar operation: apply scalar to the source variable
                scalar_val = variable.scalar_value
                print_manager.custom_debug(f"Applying scalar operation: {operation} with scalar value {scalar_val}")
                
                if operation == 'add':
                    result = fresh_sources[0] + scalar_val
                elif operation == 'sub':
                    result = fresh_sources[0] - scalar_val
                elif operation == 'mul':
                    result = fresh_sources[0] * scalar_val
                elif operation == 'div':
                    result = fresh_sources[0] / scalar_val
            else:
                # Binary operation: apply between two source variables
                print_manager.custom_debug(f"Applying binary operation: {operation} between two variables")
                
                if operation == 'add':
                    result = fresh_sources[0] + fresh_sources[1]
                elif operation == 'sub':
                    result = fresh_sources[0] - fresh_sources[1]
                elif operation == 'mul':
                    result = fresh_sources[0] * fresh_sources[1]
                elif operation == 'div':
                    result = fresh_sources[0] / fresh_sources[1]
                
            if result is None:
                print_manager.custom_debug(f"Operation failed for {name}")
                return variable
                
            # Additional check - verify the result has data in our target time range
            if hasattr(result, 'datetime_array') and result.datetime_array is not None:
                result_indices = time_clip(result.datetime_array, trange[0], trange[1])
                if len(result_indices) == 0:
                    print_manager.custom_debug(f"⚠️ Result has no data points in requested time range")
                    print_manager.custom_debug(f"Using original variable - cannot update for new time range")
                    return variable
                else:
                    print_manager.custom_debug(f"Result has {len(result_indices)} data points in requested time range")
        except Exception as e:
            print_manager.custom_debug(f"Error during variable operation: {str(e)}")
            return variable
        
        # Debug the datetime arrays
        if hasattr(variable, 'datetime_array') and variable.datetime_array is not None and len(variable.datetime_array) > 0:
            print_manager.custom_debug(f"Original datetime_array start: {variable.datetime_array[0]}")
        else:
            print_manager.custom_debug(f"Original variable has no datetime_array or it's empty")
            
        if hasattr(fresh_sources[0], 'datetime_array') and fresh_sources[0].datetime_array is not None and len(fresh_sources[0].datetime_array) > 0:
            print_manager.custom_debug(f"Source 1 datetime_array start: {fresh_sources[0].datetime_array[0]}")
        else:
            print_manager.custom_debug(f"Source 1 has no datetime_array or it's empty")
            
        if len(fresh_sources) > 1:
            if hasattr(fresh_sources[1], 'datetime_array') and fresh_sources[1].datetime_array is not None and len(fresh_sources[1].datetime_array) > 0:
                print_manager.custom_debug(f"Source 2 datetime_array start: {fresh_sources[1].datetime_array[0]}")
            else:
                print_manager.custom_debug(f"Source 2 has no datetime_array or it's empty")
        else:
            print_manager.custom_debug(f"Scalar operation - no second source variable")
            
        if hasattr(result, 'datetime_array') and result.datetime_array is not None and len(result.datetime_array) > 0:
            print_manager.custom_debug(f"Result datetime_array start: {result.datetime_array[0]}")
        else:
            print_manager.custom_debug(f"Result has no datetime_array or it's empty")
        
        # Store the old variable in the same dictionary slot
        self.variables[name] = result
        
        # Update metadata on the new variable
        object.__setattr__(result, 'class_name', 'custom_class')
        object.__setattr__(result, 'subclass_name', name)
        object.__setattr__(result, 'data_type', 'custom_data_type')
        
        # Preserve the subclass_name-based labels
        object.__setattr__(result, 'y_label', name)
        object.__setattr__(result, 'legend_label', name)
        
        # Add an update method that routes to this container
        def update_method(self, trange):
            """Update method that routes to container"""
            from ..data_cubby import data_cubby
            custom_container = data_cubby.grab('custom_class')
            if custom_container:
                result = custom_container.update(name, trange)
                if result is not None:
                    return result
            return self
            
        object.__setattr__(result, 'update', types.MethodType(update_method, result))
        
        # Make sure the result is globally accessible (replaces the old reference)
        self._make_globally_accessible(name, result)
        
        # Update data_tracker to record this calculation with variable-specific tracking
        global_tracker.update_calculated_range(trange, 'custom_data_type', name)
        
        # Copy all styling attributes from the original variable to preserve appearance
        styling_attributes = [
            'color', 'line_style', 'line_width', 'marker', 'marker_size', 
            'alpha', 'zorder', 'y_scale', 'y_limit', 'colormap', 
            'colorbar_scale', 'colorbar_limits', 'legend_label_override'
        ]
        
        # Try both methods for obtaining the original variable with styling
        # 1. Directly from the passed variable first as it might have fresh styling
        original_styles = {}
        if variable is not None:
            for attr in styling_attributes:
                if hasattr(variable, attr) and getattr(variable, attr) is not None:
                    original_styles[attr] = getattr(variable, attr)
                    print_manager.custom_debug(f"Found style from variable: {attr}={original_styles[attr]}")
        
        # 2. Try from global namespace (it might have more styles set)
        try:
            import importlib
            plotbot_module = importlib.import_module('plotbot')
            if hasattr(plotbot_module, name):
                global_var = getattr(plotbot_module, name)
                for attr in styling_attributes:
                    if (attr not in original_styles or original_styles[attr] is None) and \
                       hasattr(global_var, attr) and getattr(global_var, attr) is not None:
                        original_styles[attr] = getattr(global_var, attr)
                        print_manager.custom_debug(f"Found style from global: {attr}={original_styles[attr]}")
        except Exception as e:
            print_manager.custom_debug(f"Note: Could not check global namespace for styles: {str(e)}")
        
        # Apply all found styles to the result
        for attr, value in original_styles.items():
            try:
                print_manager.custom_debug(f"Preserving style attribute {attr}={value}")
                object.__setattr__(result, attr, value)
            except Exception as e:
                print_manager.custom_debug(f"Could not preserve style {attr}: {str(e)}")
        
        print_manager.custom_debug(f"Successfully updated {name}")
        return result
    
    def _make_globally_accessible(self, name, variable):
        """
        Make the variable globally accessible under the plotbot namespace.
        Sanitizes the name to ensure it's a valid Python identifier.
        """
        import importlib
        import re

        # Sanitize the name: replace spaces and other invalid chars with underscores
        # Remove leading/trailing underscores and collapse multiple underscores
        sanitized_name = re.sub(r'[^0-9a-zA-Z_]', '_', name)
        sanitized_name = re.sub(r'_+$', '', sanitized_name) # Remove trailing underscores
        sanitized_name = re.sub(r'^_+]', '', sanitized_name) # Remove leading underscores
        sanitized_name = re.sub(r'__+', '_', sanitized_name) # Collapse multiple underscores
        
        # Ensure it doesn't start with a number (prepend underscore if needed)
        if sanitized_name[0].isdigit():
            sanitized_name = '_' + sanitized_name
            
        # Handle empty name after sanitization (should not happen with valid input)
        if not sanitized_name:
            print_manager.error(f"Could not create a valid global name for custom variable '{name}'")
            return

        try:
            # Dynamically import the plotbot module
            plotbot_module = importlib.import_module('plotbot')
            
            # Add the variable to the module's namespace using the sanitized name
            setattr(plotbot_module, sanitized_name, variable)
            print_manager.custom_debug(f"Made '{name}' globally accessible as plotbot.{sanitized_name}")
            
        except Exception as e:
            print_manager.error(f"Failed to make custom variable '{name}' globally accessible as '{sanitized_name}': {e}")

def custom_variable(name, expression):
    """
    Create a custom variable with the given name and expression
    
    Parameters
    ----------
    name : str
        Name for the variable
    expression : plot_manager
        The expression result (e.g., proton.anisotropy / mag_rtn_4sa.bmag)
        
    Returns
    -------
    plot_manager
        The registered custom variable
        
    Examples
    --------
    >>> custom_variable('TAoverB', proton.anisotropy / mag_rtn_4sa.bmag)
    >>> custom_variable('SumField', mag_rtn_4sa.br + mag_rtn_4sa.bt)
    """

    # <<< ADDED DEBUG PRINT >>>
    expr_has_data = hasattr(expression, 'datetime_array') and expression.datetime_array is not None and len(expression.datetime_array) > 0
    expr_data_points = len(expression.datetime_array) if expr_has_data else 0
    print_manager.debug(f"DEBUG custom_variable: Incoming expression for '{name}' already has data? {expr_has_data} ({expr_data_points} points)")
    # <<< END ADDED DEBUG PRINT >>>

    # Clear any existing calculation cache for this variable name
    global_tracker.clear_calculation_cache('custom_data_type', name)
    
    # Analyze the expression to see if it needs special handling
    # For expressions from plot_manager, we need to extract source_vars
    if hasattr(expression, 'source_var') or hasattr(expression, 'source_vars'):
        # Log debug info
        print_manager.debug(f"Expression type: {type(expression)}")
        print_manager.debug(f"Expression has source_var: {hasattr(expression, 'source_var')}")
        
        if hasattr(expression, 'source_var') and expression.source_var is not None:
            print_manager.debug(f"Source var is None: {expression.source_var is None}")
            
            if isinstance(expression.source_var, list):
                print_manager.debug(f"Source var type: {type(expression.source_var)}")
                print_manager.debug(f"Source var length: {len(expression.source_var)}")
    
    # Get the container (import data_cubby locally to avoid circular imports)
    from ..data_cubby import data_cubby
    container = data_cubby.grab('custom_class')
    if container is None:
        container = CustomVariablesContainer()
        data_cubby.stash(container, class_name='custom_class')
    
    # Get source variables and operation type
    sources = []
    operation = 'div'  # Default to division as most custom vars are ratios
    
    # Extract sources from expression
    if hasattr(expression, 'source_var') and expression.source_var is not None:
        # First try using source_var directly
        for src in expression.source_var:
            if hasattr(src, 'class_name') and hasattr(src, 'subclass_name'):
                sources.append(src)
                print_manager.custom_debug(f"Added source variable: {src.class_name}.{src.subclass_name}")
        
        # Get operation type if available
        if hasattr(expression, 'operation'):
            operation = expression.operation
            print_manager.custom_debug(f"Using operation: {operation}")
    
    # If no sources found but it's likely a division, try to infer from class name
    if not sources and hasattr(expression, 'operation') and expression.operation == 'div':
        # Try to get proton.anisotropy and mag_rtn_4sa.bmag (common case)
        try:
            from . import proton, mag_rtn_4sa
            sources = [proton.anisotropy, mag_rtn_4sa.bmag]
            print_manager.custom_debug(f"Using inferred sources for division: proton.anisotropy / mag_rtn_4sa.bmag")
        except (ImportError, AttributeError):
            print_manager.custom_debug(f"Could not infer sources")
    
    print_manager.custom_debug(f"Found {len(sources)} source variables")
    
    # First set the subclass_name, then use it for y_label and legend_label
    object.__setattr__(expression, 'subclass_name', name)
    object.__setattr__(expression, 'y_label', expression.subclass_name)
    object.__setattr__(expression, 'legend_label', expression.subclass_name)
    
    # Register the variable with the container
    variable = container.register(name, expression, sources, operation)
    
    return variable

def test_custom_variables():
    """
    Test function for custom variables
    
    This runs a quick example of creating and using custom variables
    """
    import datetime
    import numpy as np
    
    print_manager.custom_debug("Running custom variables test")
    
    # Create a custom variable
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x)
    
    # Create a plot_manager object for testing
    from ..plot_manager import plot_manager
    from ..ploptions import ploptions
    
    # Create proper plot options
    plot_options = ploptions(
        data_type="test",
        class_name="test", 
        subclass_name="sin",
        plot_type="time_series"
    )
    
    # Create the variable with required arguments
    sin_var = plot_manager(y, plot_options)
    sin_var.datetime_array = [datetime.datetime.now() + datetime.timedelta(minutes=i) for i in range(len(y))]
    
    # Set source info for testing
    sin_var.source_var = [sin_var]
    sin_var.operation = 'custom'
    
    # Create custom variable
    custom_variable('test_sin', sin_var)
    
    print_manager.custom_debug("Custom variables test completed")
    return True 

def recalculate_custom_variables():
    """
    Iterates through registered custom variables and recalculates their values
    based on potentially updated source variables.
    """
    from ..print_manager import print_manager # Moved import
    from ..data_cubby import data_cubby # Moved import
    from ..plot_manager import plot_manager # Needed for isinstance check

    print_manager.custom_debug("[CUSTOM VAR] Starting recalculation process...")
    recalculation_needed = False 