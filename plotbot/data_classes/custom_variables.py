# custom_variables.py
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
        self.class_name = 'custom_variables'
        
        # Register this instance in data_cubby
        from ..data_cubby import data_cubby
        data_cubby.stash(self, class_name='custom_variables')
        print_manager.custom_debug("✨ Custom variables system initialized")
    
    def __getattr__(self, name):
        """
        Enable dot notation access to variables (like mag_rtn_4sa.br).
        Always returns the CURRENT value from self.variables, so updates are automatically visible.
        """
        # Avoid recursion for internal attributes - but these should be accessed normally
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        # Return variable from dictionary (this automatically gets updated values!)
        if 'variables' in self.__dict__ and name in self.variables:
            return self.variables[name]
        
        raise AttributeError(f"Custom variable '{name}' not found. Use custom_variable() to create it.")
    
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
        object.__setattr__(variable, 'class_name', 'custom_variables')
        object.__setattr__(variable, 'subclass_name', name)
        object.__setattr__(variable, 'data_type', 'custom_data_type')
        
        # Keep the existing y_label and legend_label values
        # They should already be set by the custom_variable function
        
                # Add an update method that routes to this container
        def update_method(self, trange):
            """Update method that routes to container"""
            from ..data_cubby import data_cubby
            custom_container = data_cubby.grab('custom_variables')
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
    
    def evaluate_lambdas(self):
        """
        Evaluate all lambda-based custom variables after their source data has loaded.
        This should be called AFTER regular data is loaded in plotbot().
        """
        from ..plot_manager import plot_manager
        import numpy as np
        
        if not hasattr(self, 'callables'):
            return  # No lambda variables to evaluate
        
        for name in list(self.callables.keys()):
            if name not in self.variables:
                continue
            
            var = self.variables[name]
            print_manager.debug(f"Evaluating lambda for '{name}' after source data loaded")
            
            try:
                # Execute the lambda
                result = self.callables[name]()
                print_manager.debug(f"[Lambda Eval] Result type: {type(result)}, has __array__: {hasattr(result, '__array__')}")
                
                if hasattr(result, '__array__'):
                    var_data = np.asarray(result)
                    print_manager.debug(f"[Lambda Eval] var_data shape: {var_data.shape}")
                    
                    # Create new plot_manager with data
                    new_var = plot_manager(var_data, plot_config=var.plot_config)
                    print_manager.debug(f"[Lambda Eval] new_var created, shape: {new_var.shape}")
                    
                    # Copy plot attributes from old var
                    for attr in plot_manager.PLOT_ATTRIBUTES:
                        if hasattr(var, attr):
                            setattr(new_var, attr, getattr(var, attr))
                    
                    # CRITICAL: Copy time/datetime_array from result 
                    # (Lambda operations on plot_managers preserve datetime_array)
                    if hasattr(result, 'datetime_array'):
                        object.__setattr__(new_var, 'datetime_array', result.datetime_array)
                        print_manager.debug(f"[Lambda Eval] Copied datetime_array with {len(result.datetime_array)} points")
                    
                    # Copy .time from source (arithmetic operations don't preserve it)
                    if hasattr(result, 'source_var') and result.source_var:
                        first_source = result.source_var[0]
                        if hasattr(first_source, 'time') and first_source.time is not None:
                            object.__setattr__(new_var, 'time', first_source.time)
                            print_manager.debug(f"[Lambda Eval] Copied .time from source")
                    
                    # Update container (this updates plotbot.custom_variables.phi_B via __getattr__)
                    self.variables[name] = new_var
                    print_manager.debug(f"[Lambda Eval] Updated self.variables[{name}]")
                    
                    # Update global alias (plotbot.phi_B)
                    self._make_globally_accessible(name, new_var)
                    print_manager.debug(f"[Lambda Eval] Updated global plotbot.{name}")
                    
                    print_manager.debug(f"✅ Lambda '{name}' evaluated, shape: {var_data.shape}")
                    
            except Exception as e:
                print_manager.warning(f"Failed to evaluate lambda '{name}': {e}")
                import traceback
                traceback.print_exc()
    
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
        
        # LAMBDA VARIABLES: Evaluate lambda to get fresh result
        if operation == 'lambda' and hasattr(self, 'callables') and name in self.callables:
            print_manager.custom_debug(f"Evaluating lambda for '{name}'")
            try:
                # Execute lambda with fresh data
                result = self.callables[name]()
                
                # Update stored variable
                self.variables[name] = result
                
                # Set metadata
                object.__setattr__(result, 'class_name', 'custom_variables')
                object.__setattr__(result, 'subclass_name', name)
                object.__setattr__(result, 'data_type', 'custom_data_type')
                object.__setattr__(result, 'y_label', name)
                object.__setattr__(result, 'legend_label', name)
                
                # Make globally accessible
                self._make_globally_accessible(name, result)
                
                # Update tracker
                global_tracker.update_calculated_range(trange, 'custom_data_type', name)
                
                print_manager.custom_debug(f"✅ Lambda evaluation complete for '{name}'")
                return result
                
            except Exception as e:
                print_manager.error(f"❌ Error evaluating lambda for '{name}': {e}")
                import traceback
                traceback.print_exc()
                return variable
        
        # NON-LAMBDA VARIABLES
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
        object.__setattr__(result, 'class_name', 'custom_variables')
        object.__setattr__(result, 'subclass_name', name)
        object.__setattr__(result, 'data_type', 'custom_data_type')
        
        # Preserve the subclass_name-based labels
        object.__setattr__(result, 'y_label', name)
        object.__setattr__(result, 'legend_label', name)
        
        # 🎯 CRITICAL: Set requested_trange for proper time clipping (non-lambda path)
        # This ensures .data property clips to the requested time range
        if hasattr(result, 'requested_trange'):
            object.__setattr__(result, 'requested_trange', trange)
            print_manager.custom_debug(f"Set requested_trange on '{name}' (non-lambda): {trange}")
        
        # Add an update method that routes to this container
        def update_method(self, trange):
            """Update method that routes to container"""
            from ..data_cubby import data_cubby
            custom_container = data_cubby.grab('custom_variables')
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
            'plot_type', 'color', 'line_style', 'line_width', 'marker', 'marker_size', 'marker_style',
            'alpha', 'zorder', 'y_scale', 'y_limit', 'y_label', 'colormap', 
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
    
    def get_source_variables(self, name):
        """
        Parse a custom variable's expression and return the source variables needed.
        Does NOT load any data - just identifies what's needed.
        
        Returns: list of plot_manager objects that need data loaded
        """
        import inspect
        import re
        
        print_manager.custom_debug(f"🔧 [GET_SOURCE] Getting source variables for '{name}'")
        
        if name not in self.variables:
            print_manager.error(f"Custom variable '{name}' not found")
            return []
        
        operation = self.operations.get(name)
        
        # LAMBDA VARIABLES: Parse to find variable references
        if operation == 'lambda' and hasattr(self, 'callables') and name in self.callables:
            lambda_func = self.callables[name]
            source_code = inspect.getsource(lambda_func).strip()
            print_manager.custom_debug(f"🔧 [GET_SOURCE] Lambda source: {source_code}")
            
            # Match patterns like: pb.mag_rtn_4sa.bn or plotbot.mag_rtn_4sa.bn
            # We need to match THREE parts and take the last two (class.variable)
            pattern = r'(?:pb|plotbot)\.(\w+)\.(\w+)'
            matches = re.findall(pattern, source_code)
            print_manager.custom_debug(f"🔧 [GET_SOURCE] Found variable references: {matches}")
            
            # Get the variable objects
            vars_to_load = []
            from ..data_cubby import data_cubby
            for class_name, var_name in matches:
                # class_name is now mag_rtn_4sa, var_name is bn ✅
                print_manager.custom_debug(f"🔧 [GET_SOURCE] Getting {class_name}.{var_name}...")
                class_instance = data_cubby.grab(class_name)
                if class_instance:
                    var = getattr(class_instance, var_name, None)
                    if var is not None:
                        print_manager.custom_debug(f"🔧 [GET_SOURCE] Found {class_name}.{var_name} (ID:{id(var)})")
                        vars_to_load.append(var)
            
            return vars_to_load
        
        # OLD-STYLE VARIABLES: Use source_var attribute
        elif hasattr(self.variables[name], 'source_var') and self.variables[name].source_var is not None:
            return [v for v in self.variables[name].source_var 
                    if hasattr(v, 'class_name') and v.class_name != 'custom_variables']
        
        return []
    
    def evaluate(self, name, trange):
        """
        Evaluate a custom variable's lambda/expression.
        Loads dependencies automatically (like br_norm pattern).
        
        Returns the ready-to-plot plot_manager or None if it fails.
        """
        import inspect
        import re
        
        print_manager.custom_debug(f"🔧 [EVALUATE] Evaluating '{name}' for trange {trange}")
        
        if name not in self.variables:
            print_manager.error(f"Custom variable '{name}' not found")
            return None
        
        operation = self.operations.get(name)
        print_manager.custom_debug(f"🔧 [EVALUATE] operation='{operation}'")
        print_manager.custom_debug(f"🔧 [EVALUATE] Checking lambda condition...")
        print_manager.custom_debug(f"🔧 [EVALUATE] operation=='lambda': {operation == 'lambda'}")
        print_manager.custom_debug(f"🔧 [EVALUATE] hasattr(self, 'callables'): {hasattr(self, 'callables')}")
        print_manager.custom_debug(f"🔧 [EVALUATE] name in self.callables: {name in self.callables if hasattr(self, 'callables') else False}")
        
        # LAMBDA VARIABLES: Evaluate the lambda (data already loaded!)
        if operation == 'lambda' and hasattr(self, 'callables') and name in self.callables:
            print_manager.custom_debug(f"🔧 [EVALUATE] ✅ ENTERED LAMBDA PATH!")
            try:
                # LOAD DEPENDENCIES! (Like br_norm does)
                source_vars = self.get_source_variables(name)
                if source_vars:
                    from ..get_data import get_data
                    print_manager.custom_debug(f"🔧 [EVALUATE] Loading {len(source_vars)} dependencies...")
                    get_data(trange, *source_vars)  # Recursive call!
                    print_manager.custom_debug(f"🔧 [EVALUATE] Dependencies loaded")
                    
                    # Set requested_trange on source variables so they clip correctly!
                    for src_var in source_vars:
                        if hasattr(src_var, 'requested_trange'):
                            src_var.requested_trange = trange
                            print_manager.custom_debug(f"🔧 [EVALUATE] Set requested_trange on {src_var.class_name}.{src_var.subclass_name}")
                
                print_manager.custom_debug(f"🔧 [EVALUATE] Evaluating lambda for '{name}'...")
                result = self.callables[name]()
                print_manager.custom_debug(f"🔧 [EVALUATE] Lambda evaluation result (ID:{id(result)}, type:{type(result).__name__})")
                
                # DEBUG: Check result's datetime_array
                if hasattr(result, 'datetime_array') and result.datetime_array is not None:
                    print_manager.custom_debug(f"🔧 [EVALUATE] Result datetime_array length (BEFORE clip): {len(result.datetime_array)}")
                    
                    # 🎯 CRITICAL: Clip result to requested trange!
                    # The lambda operates on full merged arrays, but we only want data for THIS trange
                    from ..plotbot_helpers import time_clip
                    indices = time_clip(result.datetime_array, trange[0], trange[1])
                    print_manager.custom_debug(f"🔧 [EVALUATE] Clipping to trange, found {len(indices)} points")
                    
                    if len(indices) > 0:
                        # Clip datetime_array
                        result.datetime_array = result.datetime_array[indices]
                        
                        # Clip the actual data
                        if hasattr(result, 'plot_config') and hasattr(result.plot_config, 'data'):
                            if result.plot_config.data.ndim == 1:
                                result.plot_config.data = result.plot_config.data[indices]
                            else:
                                result.plot_config.data = result.plot_config.data[indices, ...]
                        
                        # Clip time if present
                        if hasattr(result, 'time') and result.time is not None:
                            result.time = result.time[indices]
                        
                        print_manager.custom_debug(f"🔧 [EVALUATE] Result clipped to {len(result.datetime_array)} points")
                
                # Preserve user-defined attributes from old variable
                old_var = self.variables[name]
                style_attrs = ['color', 'y_label', 'legend_label', 'plot_type', 'y_scale', 
                              'line_style', 'marker_size', 'marker_style', 'line_width']
                for attr in style_attrs:
                    if hasattr(old_var, attr):
                        old_value = getattr(old_var, attr)
                        object.__setattr__(result, attr, old_value)
                
                # Update stored variable with result
                print_manager.custom_debug(f"🔧 [EVALUATE] Updating self.variables['{name}'] from ID:{id(self.variables[name])} to ID:{id(result)}")
                self.variables[name] = result
                
                # Set metadata
                object.__setattr__(result, 'class_name', 'custom_variables')
                object.__setattr__(result, 'subclass_name', name)
                object.__setattr__(result, 'data_type', 'custom_data_type')
                
                # 🎯 CRITICAL: Set requested_trange for proper time clipping
                if hasattr(result, 'requested_trange'):
                    object.__setattr__(result, 'requested_trange', trange)
                    print_manager.custom_debug(f"🔧 [EVALUATE] Set requested_trange on '{name}': {trange}")
                
                # Update global reference
                print_manager.custom_debug(f"🔧 [EVALUATE] Making '{name}' globally accessible...")
                self._make_globally_accessible(name, result)
                
                print_manager.custom_debug(f"🔧 [EVALUATE] ✅ Lambda '{name}' ready, returning (ID:{id(result)})")
                return result
                
            except Exception as e:
                print_manager.error(f"Failed to evaluate lambda '{name}': {e}")
                return None
        
        # OLD-STYLE VARIABLES: Just update (data already loaded!)
        elif self.sources.get(name):
            print_manager.custom_debug(f"🔧 [EVALUATE] Old-style variable '{name}', calling update...")
            
            # Load sources first
            source_vars = self.get_source_variables(name)
            if source_vars:
                from ..get_data import get_data
                print_manager.custom_debug(f"🔧 [EVALUATE] Loading {len(source_vars)} dependencies for old-style var...")
                get_data(trange, *source_vars)
                print_manager.custom_debug(f"🔧 [EVALUATE] Dependencies loaded")
            
            return self.update(name, trange)
        
        # Already ready - just return it
        print_manager.custom_debug(f"🔧 [EVALUATE] Variable '{name}' already ready")
        return self.variables[name]

    def ensure_ready(self, name, trange):
        """
        BACKWARD COMPATIBILITY: Old method that does both steps.
        New code should use get_source_variables() + evaluate() separately.
        
        This loads data AND evaluates - kept for compatibility but discouraged.
        """
        from ..get_data import get_data
        
        print_manager.custom_debug(f"🔧 [ENSURE_READY] (deprecated) Called for '{name}'")
        
        # Step 1: Get source variables
        source_vars = self.get_source_variables(name)
        
        # Step 2: Load data if needed
        if source_vars:
            print_manager.custom_debug(f"🔧 [ENSURE_READY] Loading {len(source_vars)} source variables...")
            get_data(trange, *source_vars)
        
        # Step 3: Evaluate
        return self.evaluate(name, trange)
    
    def _make_globally_accessible(self, name, variable):
        """
        Make the variable globally accessible under the plotbot namespace.
        Sanitizes the name to ensure it's a valid Python identifier.
        """
        import importlib
        import re

        print_manager.custom_debug(f"🔧 [MAKE_GLOBAL] Making '{name}' globally accessible (ID:{id(variable)})")
        
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
            
            # Check if we're overwriting something
            if hasattr(plotbot_module, sanitized_name):
                old_obj = getattr(plotbot_module, sanitized_name)
                print_manager.custom_debug(f"🔧 [MAKE_GLOBAL] ⚠️ OVERWRITING plotbot.{sanitized_name} (old ID:{id(old_obj)}) with new (ID:{id(variable)})")
                if hasattr(old_obj, 'class_name') and hasattr(old_obj, 'subclass_name'):
                    print_manager.custom_debug(f"🔧 [MAKE_GLOBAL] ⚠️ OLD was: {old_obj.class_name}.{old_obj.subclass_name}")
                if hasattr(variable, 'class_name') and hasattr(variable, 'subclass_name'):
                    print_manager.custom_debug(f"🔧 [MAKE_GLOBAL] ⚠️ NEW is: {variable.class_name}.{variable.subclass_name}")
            
            # Add the variable to the module's namespace using the sanitized name
            setattr(plotbot_module, sanitized_name, variable)
            print_manager.custom_debug(f"🔧 [MAKE_GLOBAL] ✅ Made '{name}' globally accessible as plotbot.{sanitized_name} (ID:{id(variable)})")
            
        except Exception as e:
            print_manager.error(f"Failed to make custom variable '{name}' globally accessible as '{sanitized_name}': {e}")

def custom_variable(name, expression):
    """
    Create a custom variable with the given name and expression
    
    The variable is accessible via:
    - plotbot.{name}  (always current - updated on each calculation)
    - plotbot.custom_variables.{name}  (always current - goes through container)
    
    Parameters
    ----------
    name : str
        Name for the variable
    expression : callable or plot_manager
        Either a lambda function for lazy evaluation:
            lambda: np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
        Or a direct expression (evaluated immediately):
            proton.anisotropy / mag_rtn_4sa.bmag
        
    Returns
    -------
    plot_manager
        The registered variable. Set attributes immediately if needed, but 
        always access via plotbot.{name} for plotting to avoid stale references.
        
    Examples
    --------
    >>> custom_variable('phi_B', lambda: ...).color = 'purple'  # ✅ Immediate styling
    >>> plotbot(trange, plotbot.phi_B, 1)  # ✅ Always use plotbot.{name} for plotting
    """

    # Get the container (import data_cubby locally to avoid circular imports)
    from ..data_cubby import data_cubby
    from ..plot_manager import plot_manager
    from ..plot_config import plot_config
    
    container = data_cubby.grab('custom_variables')
    if container is None:
        container = CustomVariablesContainer()
        data_cubby.stash(container, class_name='custom_variables')
    
    # Check if expression is a callable (lambda function)
    if callable(expression):
        print_manager.debug(f"Custom variable '{name}' uses lambda - will evaluate lazily")
        
        # Store the callable for lazy evaluation
        if not hasattr(container, 'callables'):
            container.callables = {}
        container.callables[name] = expression
        
        # Create a placeholder plot_manager
        placeholder_config = plot_config(
            data_type='custom_data_type',
            class_name='custom_variables',
            subclass_name=name,
            plot_type='time_series',
            time=None,  # Lambda will provide fresh time when evaluated
            datetime_array=None
        )
        placeholder = plot_manager(np.array([]), plot_config=placeholder_config)
        placeholder.y_label = name
        placeholder.legend_label = name
        
        # Register the placeholder and return it
        variable = container.register(name, placeholder, sources=[], operation='lambda')
        return variable  # Return so users can set attributes like phi_B.color = 'red'
    
    # Otherwise, handle as before (immediate evaluation)
    expr_has_data = hasattr(expression, 'datetime_array') and expression.datetime_array is not None and len(expression.datetime_array) > 0
    expr_data_points = len(expression.datetime_array) if expr_has_data else 0
    print_manager.debug(f"DEBUG custom_variable: Incoming expression for '{name}' already has data? {expr_has_data} ({expr_data_points} points)")

    # Clear any existing calculation cache for this variable name
    global_tracker.clear_calculation_cache('custom_data_type', name)
    
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
    
    return variable  # Return so users can set attributes like my_var.color = 'red'

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
    from ..plot_config import plot_config
    
    # Create proper plot options
    plot_options = plot_config(
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