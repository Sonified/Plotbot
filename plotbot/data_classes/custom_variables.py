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
        from ..plot_manager import plot_manager
        from ..plot_config import plot_config as plot_config_class
        
        print_manager.custom_debug(f"🔍 [UPDATE] Updating custom variable '{name}' for trange {trange}")
        
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
        
        # STEP 6: Cadence Check - Get fresh data for all source variables
        print_manager.custom_debug(f"🔍 [STEP 6] Checking source variable cadences...")
        fresh_sources = []
        source_lengths = []
        for idx, src in enumerate(sources, 1):
            if hasattr(src, 'class_name') and hasattr(src, 'subclass_name'):
                # Get fresh reference from data_cubby
                from ..data_cubby import data_cubby
                fresh_src = data_cubby.grab_component(src.class_name, src.subclass_name)
                
                if fresh_src and hasattr(fresh_src, 'datetime_array') and fresh_src.datetime_array is not None:
                    src_len = len(fresh_src.datetime_array)
                    source_lengths.append(src_len)
                    print_manager.custom_debug(f"🔍 [STEP 6.{idx}] Source {src.class_name}.{src.subclass_name}: {src_len} points")
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
                            from dateutil.parser import parse
                            req_start = np.datetime64(parse(trange[0]))
                            req_end = np.datetime64(parse(trange[1]))
                            
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
        
        # STEP 6 Summary: Check if sources have different cadences
        if len(source_lengths) > 1 and len(set(source_lengths)) > 1:
            print_manager.custom_debug(f"🔍 [STEP 6] ⚠️ Different cadences detected: {source_lengths}")
            print_manager.custom_debug(f"🔍 [STEP 6] Resampling will be needed")
        elif len(source_lengths) > 0:
            print_manager.custom_debug(f"🔍 [STEP 6] All sources have same cadence: {source_lengths[0]} points")
        
        # Check if we have the right number of sources for the operation
        # Scalar operations (like variable + 10) need 1 source, binary operations need 2
        # Numpy ufuncs (like np.abs) also need 1 source (MOST of them - arctan2 needs 2)
        
        # List of unary ufuncs that only need 1 source
        unary_ufuncs = ['absolute', 'abs', 'sqrt', 'square', 'log', 'log10', 'exp', 
                        'sin', 'cos', 'tan', 'arcsin', 'arccos', 'arctan',
                        'degrees', 'radians', 'negative', 'reciprocal', 'sign',
                        'ceil', 'floor', 'round']
        
        # Determine expected sources based on operation type
        if operation in unary_ufuncs:
            expected_sources = 1
        elif operation in ['add', 'sub', 'mul', 'div'] and hasattr(variable, 'scalar_value'):
            expected_sources = 1  # Scalar arithmetic
        elif operation in ['arctan2']:
            expected_sources = 2  # Binary ufunc
        elif operation in ['add', 'sub', 'mul', 'div']:
            expected_sources = 2  # Binary arithmetic
        else:
            # Unknown operation - check based on actual sources available
            expected_sources = len(fresh_sources)
            print_manager.custom_debug(f"🔍 [STEP 6] Unknown operation '{operation}', using {expected_sources} sources")
        
        if len(fresh_sources) < expected_sources:
            print_manager.custom_debug(f"🔍 [STEP 6] ❌ Not enough fresh sources: got {len(fresh_sources)}, expected {expected_sources}")
            print_manager.custom_debug(f"🔍 [STEP 6] Operation: {operation}, has scalar_value: {hasattr(variable, 'scalar_value')}")
            return variable
            
        # Import time_clip for time range handling
        from datetime import datetime
        
        # Determine the common time range - important for operations
        try:
            # Get start/end times for target range
            from dateutil.parser import parse
            req_start = parse(trange[0])
            req_end = parse(trange[1])
            
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
        
        # STEP 7: Resampling (if cadences differ)
        print_manager.custom_debug(f"🔍 [STEP 7] Checking if resampling needed...")
        
        # Check if all sources have the same cadence
        if len(fresh_sources) > 1:
            cadences = [len(src.data) for src in fresh_sources]
            print_manager.custom_debug(f"🔍 [STEP 7] Source cadences: {cadences}")
            
            if len(set(cadences)) > 1:
                # Different cadences detected - need to resample
                print_manager.custom_debug(f"🔍 [STEP 7] ⚠️  Different cadences detected: {cadences}")
                print_manager.custom_debug(f"🔍 [STEP 7] Resampling to lowest cadence...")
                
                # Find the source with the lowest cadence (fewest points)
                min_cadence_idx = cadences.index(min(cadences))
                target_times = fresh_sources[min_cadence_idx].datetime_array
                
                print_manager.custom_debug(f"🔍 [STEP 7] Target cadence: {len(target_times)} points from source {min_cadence_idx}")
                
                # Resample all other sources to match target_times
                resampled_sources = []
                for i, src in enumerate(fresh_sources):
                    if i == min_cadence_idx:
                        # This is already at target cadence
                        resampled_sources.append(src)
                    else:
                        # Need to resample this source
                        print_manager.custom_debug(f"🔍 [STEP 7] Resampling source {i} from {len(src.data)} to {len(target_times)} points")
                        
                        # Use scipy interpolation (inspired by showdahodo.py)
                        import matplotlib.dates as mdates
                        from scipy import interpolate
                        
                        # Convert datetime arrays to numeric for interpolation
                        src_time_numeric = mdates.date2num(src.datetime_array)
                        target_time_numeric = mdates.date2num(target_times)
                        
                        # Linear interpolation
                        f = interpolate.interp1d(
                            src_time_numeric, src.data,
                            kind='linear',
                            bounds_error=False,
                            fill_value='extrapolate'
                        )
                        
                        resampled_data = f(target_time_numeric)
                        
                        # Create new plot_manager with resampled data
                        from ..plot_config import plot_config as plot_config_class
                        from ..plot_manager import plot_manager
                        
                        new_config = plot_config_class(**src.plot_config.__dict__)
                        new_config.datetime_array = target_times
                        new_config.time = target_times  # Update time array too
                        
                        resampled_pm = plot_manager(resampled_data, plot_config=new_config)
                        resampled_sources.append(resampled_pm)
                        
                        print_manager.custom_debug(f"🔍 [STEP 7] ✓ Resampled source {i}")
                
                # Replace fresh_sources with resampled versions
                fresh_sources = resampled_sources
                print_manager.custom_debug(f"🔍 [STEP 7] ✓ All sources now have matching cadence: {len(target_times)} points")
            else:
                print_manager.custom_debug(f"🔍 [STEP 7] All sources have same cadence ({cadences[0]} points), no resampling needed")
        else:
            print_manager.custom_debug(f"🔍 [STEP 7] Single source, no resampling needed")
        
        # STEP 8: Apply the operation with fresh data
        print_manager.custom_debug(f"🔍 [STEP 8] Applying operation: {operation}")
        result = None
        try:
            # Handle scalar operations (1 source + scalar value) vs binary operations (2 sources) vs ufunc operations
            if hasattr(variable, 'scalar_value') and variable.scalar_value is not None and len(fresh_sources) == 1:
                # Scalar operation: apply scalar to the source variable
                scalar_val = variable.scalar_value
                print_manager.custom_debug(f"🔍 [STEP 8] Scalar operation: {operation} with value {scalar_val} (.data)")
                
                # Map operation to numpy function
                operation_map = {
                    'add': np.add,
                    'sub': np.subtract,
                    'mul': np.multiply,
                    'div': np.true_divide,
                    'pow': np.power,
                    'floordiv': np.floor_divide,
                    'mod': np.mod,
                }
                
                if operation in operation_map:
                    result_array = operation_map[operation](fresh_sources[0].data, scalar_val)
                else:
                    print_manager.error(f"Unsupported scalar operation: {operation}")
                    return variable
                
                # Wrap in plot_manager
                source_config = fresh_sources[0].plot_config
                new_config = plot_config_class(**source_config.__dict__)
                if not hasattr(new_config, 'datetime_array') or new_config.datetime_array is None:
                    new_config.datetime_array = fresh_sources[0].datetime_array
                if not hasattr(new_config, 'time') or new_config.time is None:
                    # Copy time from source's plot_config (raw TT2000 epoch times)
                    source_time = fresh_sources[0].plot_config.time if hasattr(fresh_sources[0].plot_config, 'time') else None
                    new_config.time = source_time
                    print_manager.custom_debug(f"🔍 [STEP 8] Copied time from source (scalar): {type(source_time)}, is None: {source_time is None}")
                result = plot_manager(result_array, plot_config=new_config)
                print_manager.custom_debug(f"🔍 [STEP 8] ✓ Wrapped scalar arithmetic result")
                
            elif operation in ['arctan2', 'degrees', 'radians', 'sin', 'cos', 'tan', 'arcsin', 'arccos', 'sqrt', 'abs', 'log', 'log10', 'exp']:
                # Ufunc operation: apply numpy ufunc to source(s)
                print_manager.custom_debug(f"🔍 [STEP 8] Ufunc operation: {operation} on {len(fresh_sources)} source(s) (.data)")
                
                if operation == 'arctan2' and len(fresh_sources) == 2:
                    result_array = np.arctan2(fresh_sources[0].data, fresh_sources[1].data)
                elif operation == 'degrees' and len(fresh_sources) == 1:
                    result_array = np.degrees(fresh_sources[0].data)
                elif operation == 'radians' and len(fresh_sources) == 1:
                    result_array = np.radians(fresh_sources[0].data)
                elif operation == 'sin' and len(fresh_sources) == 1:
                    result_array = np.sin(fresh_sources[0].data)
                elif operation == 'cos' and len(fresh_sources) == 1:
                    result_array = np.cos(fresh_sources[0].data)
                elif operation == 'tan' and len(fresh_sources) == 1:
                    result_array = np.tan(fresh_sources[0].data)
                elif operation == 'arcsin' and len(fresh_sources) == 1:
                    result_array = np.arcsin(fresh_sources[0].data)
                elif operation == 'arccos' and len(fresh_sources) == 1:
                    result_array = np.arccos(fresh_sources[0].data)
                elif operation == 'sqrt' and len(fresh_sources) == 1:
                    result_array = np.sqrt(fresh_sources[0].data)
                elif operation == 'abs' and len(fresh_sources) == 1:
                    result_array = np.abs(fresh_sources[0].data)
                elif operation == 'log' and len(fresh_sources) == 1:
                    result_array = np.log(fresh_sources[0].data)
                elif operation == 'log10' and len(fresh_sources) == 1:
                    result_array = np.log10(fresh_sources[0].data)
                elif operation == 'exp' and len(fresh_sources) == 1:
                    result_array = np.exp(fresh_sources[0].data)
                else:
                    print_manager.error(f"Unsupported ufunc operation '{operation}' with {len(fresh_sources)} sources")
                    return variable
                
                # Wrap in plot_manager
                source_config = fresh_sources[0].plot_config
                new_config = plot_config_class(**source_config.__dict__)
                if not hasattr(new_config, 'datetime_array') or new_config.datetime_array is None:
                    new_config.datetime_array = fresh_sources[0].datetime_array
                if not hasattr(new_config, 'time') or new_config.time is None:
                    # Copy time from source's plot_config (raw TT2000 epoch times)
                    source_time = fresh_sources[0].plot_config.time if hasattr(fresh_sources[0].plot_config, 'time') else None
                    new_config.time = source_time
                result = plot_manager(result_array, plot_config=new_config)
                print_manager.custom_debug(f"🔍 [STEP 8] ✓ Wrapped ufunc result")
                
            elif len(fresh_sources) >= 2:
                # Multi-source operation: map operation name to numpy function
                operation_map = {
                    'add': np.add,
                    'sub': np.subtract,
                    'mul': np.multiply,
                    'div': np.true_divide,
                    'pow': np.power,
                    'floordiv': np.floor_divide,
                    'mod': np.mod,
                }
                
                if operation in operation_map:
                    print_manager.custom_debug(f"🔍 [STEP 8] Multi-source {operation}: {len(fresh_sources)} variables (.data)")
                    
                    # Start with the first source
                    result_array = fresh_sources[0].data
                    
                    # Chain the operation across all remaining sources
                    np_func = operation_map[operation]
                    for i in range(1, len(fresh_sources)):
                        print_manager.custom_debug(f"🔍 [STEP 8.{i}] Applying {operation} with source {i}")
                        result_array = np_func(result_array, fresh_sources[i].data)
                    
                    # Wrap in plot_manager
                    source_config = fresh_sources[0].plot_config
                    new_config = plot_config_class(**source_config.__dict__)
                    if not hasattr(new_config, 'datetime_array') or new_config.datetime_array is None:
                        new_config.datetime_array = fresh_sources[0].datetime_array
                    if not hasattr(new_config, 'time') or new_config.time is None:
                        # Copy time from source's plot_config (raw TT2000 epoch times)
                        source_time = fresh_sources[0].plot_config.time if hasattr(fresh_sources[0].plot_config, 'time') else None
                        new_config.time = source_time
                        print_manager.custom_debug(f"🔍 [STEP 8] Copied time from source: {type(source_time)}, is None: {source_time is None}")
                    result = plot_manager(result_array, plot_config=new_config)
                    print_manager.custom_debug(f"🔍 [STEP 8] ✓ Wrapped multi-source arithmetic result ({len(fresh_sources)} sources)")
            
            # Handle numpy ufuncs (captured from __array_ufunc__)
            if result is None and len(fresh_sources) >= 1:
                print_manager.custom_debug(f"🔍 [STEP 8] Checking for numpy ufunc: '{operation}'")
                # Map operation names to numpy functions
                ufunc_map = {
                    'absolute': np.abs,
                    'abs': np.abs,
                    'sqrt': np.sqrt,
                    'square': np.square,
                    'log': np.log,
                    'log10': np.log10,
                    'exp': np.exp,
                    'sin': np.sin,
                    'cos': np.cos,
                    'tan': np.tan,
                    'arcsin': np.arcsin,
                    'arccos': np.arccos,
                    'arctan': np.arctan,
                    'arctan2': np.arctan2,
                    'degrees': np.degrees,
                    'radians': np.radians,
                    'negative': np.negative,
                    'reciprocal': np.reciprocal,
                    'sign': np.sign,
                    'ceil': np.ceil,
                    'floor': np.floor,
                    'round': np.round,
                }
                
                if operation in ufunc_map:
                    ufunc = ufunc_map[operation]
                    print_manager.custom_debug(f"🔍 [STEP 8] ✓ Found ufunc: np.{operation}")
                    
                    # Apply unary ufunc
                    if len(fresh_sources) == 1:
                        # STEP 8.1: Verify source data integrity BEFORE applying ufunc
                        src_raw_len = len(fresh_sources[0].view(np.ndarray))
                        src_data_len = len(fresh_sources[0].data) if hasattr(fresh_sources[0], 'data') else src_raw_len
                        src_dt_len = len(fresh_sources[0].datetime_array) if hasattr(fresh_sources[0], 'datetime_array') and fresh_sources[0].datetime_array is not None else 0
                        print_manager.custom_debug(f"🔍 [STEP 8.1] Source data integrity check:")
                        print_manager.custom_debug(f"🔍 [STEP 8.1]   Raw array length: {src_raw_len} (accumulated history)")
                        print_manager.custom_debug(f"🔍 [STEP 8.1]   .data length: {src_data_len} (clipped view)")
                        print_manager.custom_debug(f"🔍 [STEP 8.1]   datetime_array length: {src_dt_len}")
                        
                        # STEP 8.2: Compare requested trange vs actual data trange
                        print_manager.custom_debug(f"🔍 [STEP 8.2] Time range comparison:")
                        print_manager.custom_debug(f"🔍 [STEP 8.2]   REQUESTED: {trange[0]} to {trange[1]}")
                        if src_dt_len > 0:
                            src_first = fresh_sources[0].datetime_array[0]
                            src_last = fresh_sources[0].datetime_array[-1]
                            print_manager.custom_debug(f"🔍 [STEP 8.2]   ACTUAL: {src_first} to {src_last}")
                            print_manager.custom_debug(f"🔍 [STEP 8.2]   datetime points in range: {src_dt_len}")
                        
                        # STEP 8.3: Use .data property to get clipped view (not raw accumulated array!)
                        print_manager.custom_debug(f"🔍 [STEP 8.3] Using .data property for time-clipped view")
                        if src_data_len == src_dt_len:
                            print_manager.custom_debug(f"🔍 [STEP 8.3] ✓ .data is properly clipped ({src_data_len} points)")
                        else:
                            print_manager.custom_debug(f"🔍 [STEP 8.3] ⚠️ .data vs datetime mismatch: {src_data_len} vs {src_dt_len}")
                        
                        # STEP 8.4: Apply ufunc to CLIPPED data
                        print_manager.custom_debug(f"🔍 [STEP 8.4] Applying unary ufunc: {ufunc.__name__} to .data (clipped)")
                        result_array = ufunc(fresh_sources[0].data)  # ✅ Use .data for clipped view!
                        
                        # STEP 8.5: Wrap result in plot_manager with correct datetime_array
                        res_data_len = len(result_array) if hasattr(result_array, '__len__') else 0
                        print_manager.custom_debug(f"🔍 [STEP 8.5] Result integrity check:")
                        print_manager.custom_debug(f"🔍 [STEP 8.5]   Result array length: {res_data_len}")
                        print_manager.custom_debug(f"🔍 [STEP 8.5]   Expected (datetime): {src_dt_len}")
                        if res_data_len == src_dt_len:
                            print_manager.custom_debug(f"🔍 [STEP 8.5] ✓ Result matches expected size")
                        else:
                            print_manager.custom_debug(f"🔍 [STEP 8.5] ❌ Result size mismatch!")
                        
                        # STEP 8.6: Wrap in plot_manager, COPYING source's plot_config
                        print_manager.custom_debug(f"🔍 [STEP 8.6] Wrapping result in plot_manager (copying source config)")
                        
                        # Copy the source's plot_config to preserve metadata
                        source_config = fresh_sources[0].plot_config
                        new_config = plot_config_class(**source_config.__dict__)
                        
                        # Ensure time attribute exists (copy from source or set to None)
                        if not hasattr(new_config, 'time') or new_config.time is None:
                            # Copy time from source's plot_config (raw TT2000 epoch times)
                            source_time = fresh_sources[0].plot_config.time if hasattr(fresh_sources[0].plot_config, 'time') else None
                            new_config.time = source_time
                        
                        # Ensure datetime_array is copied
                        if not hasattr(new_config, 'datetime_array') or new_config.datetime_array is None:
                            new_config.datetime_array = fresh_sources[0].datetime_array if hasattr(fresh_sources[0], 'datetime_array') else None
                        
                        # Create plot_manager with result data but source's datetime/time
                        result = plot_manager(result_array, plot_config=new_config)
                        dt_len = len(result.datetime_array) if hasattr(result, 'datetime_array') and result.datetime_array is not None else 0
                        print_manager.custom_debug(f"🔍 [STEP 8.6] ✓ Wrapped result (datetime: {dt_len} points)")
                    # Apply binary ufunc (e.g., arctan2)
                    elif len(fresh_sources) == 2:
                        print_manager.custom_debug(f"🔍 [STEP 8] Applying binary ufunc to two sources (.data)")
                        result_array = ufunc(fresh_sources[0].data, fresh_sources[1].data)  # ✅ Use .data for both sources!
                        
                        # Wrap in plot_manager with first source's config
                        source_config = fresh_sources[0].plot_config
                        new_config = plot_config_class(**source_config.__dict__)
                        result = plot_manager(result_array, plot_config=new_config)
                        print_manager.custom_debug(f"🔍 [STEP 8] ✓ Wrapped binary result (datetime: {len(result.datetime_array)} points)")
                    
                    if result is not None:
                        print_manager.custom_debug(f"🔍 [STEP 8] ✅ Ufunc replay successful!")
                else:
                    print_manager.custom_debug(f"🔍 [STEP 8] ⚠️ Unknown operation '{operation}' - cannot replay")
                
            if result is None:
                print_manager.custom_debug(f"🔍 [STEP 8] ❌ Operation failed for {name}")
                return variable
            
            # STEP 8 continued: Verify result (defensive checks)
            print_manager.custom_debug(f"🔍 [STEP 8] ✓ Operation complete")
            try:
                if hasattr(result, 'datetime_array') and result.datetime_array is not None:
                    print_manager.custom_debug(f"🔍 [STEP 8] Result has {len(result.datetime_array)} points")
                    if len(result.datetime_array) > 0 and hasattr(result, '__len__'):
                        try:
                            data_preview = result[:min(3, len(result))] if len(result) > 0 else []
                            print_manager.custom_debug(f"🔍 [STEP 8] First 3 values: {data_preview}")
                        except:
                            pass  # Skip preview if slicing fails
            except Exception as e:
                print_manager.custom_debug(f"🔍 [STEP 8] Could not verify result: {e}")
                # Don't fail - just continue
        except Exception as e:
            print_manager.custom_debug(f"Error during variable operation: {str(e)}")
            import traceback
            print_manager.custom_debug(f"Full traceback:\n{traceback.format_exc()}")
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
        
        # STEP 9: Store the old variable in the same dictionary slot
        print_manager.custom_debug(f"🔍 [STEP 9] Storing result in container.variables...")
        self.variables[name] = result
        print_manager.custom_debug(f"🔍 [STEP 9] Stored '{name}' with ID: {id(result)}")
        
        # Update metadata on the new variable
        object.__setattr__(result, 'class_name', 'custom_variables')
        object.__setattr__(result, 'subclass_name', name)
        object.__setattr__(result, 'data_type', 'custom_data_type')
        
        # Preserve the subclass_name-based labels
        object.__setattr__(result, 'y_label', name)
        object.__setattr__(result, 'legend_label', name)
        
        # 🎯 CRITICAL: Set requested_trange for proper time clipping (non-lambda path)
        # This ensures .data property clips to the requested time range
        # BUT: Skip this for ufunc results - they're already properly sized!
        if hasattr(result, 'requested_trange'):
            # Verify result's internal data size matches datetime_array
            result_data_len = len(result.view(np.ndarray))
            result_datetime_len = len(result.datetime_array) if hasattr(result, 'datetime_array') and result.datetime_array is not None else 0
            
            print_manager.custom_debug(f"🔍 [requested_trange] Result data: {result_data_len}, datetime: {result_datetime_len}")
            
            if result_data_len == result_datetime_len:
                print_manager.custom_debug(f"🔍 [requested_trange] Sizes match - result is already properly sized, skipping trange clip")
            else:
                print_manager.custom_debug(f"🔍 [requested_trange] Size mismatch - setting requested_trange to clip")
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
        
        # STEP 10: Update data_tracker to record this calculation with variable-specific tracking
        print_manager.custom_debug(f"🔍 [STEP 10] Updating tracker for trange: {trange}")
        global_tracker.update_calculated_range(trange, 'custom_data_type', name)
        print_manager.custom_debug(f"🔍 [STEP 10] ✓ Tracker updated")
        
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
        
        # STEP 11: Variable Verification
        print_manager.custom_debug(f"🔍 [STEP 11] Verifying final variable state...")
        if hasattr(result, 'data'):
            print_manager.custom_debug(f"🔍 [STEP 11] ✓ Has .data property")
        if hasattr(result, 'datetime_array'):
            dt_len = len(result.datetime_array) if result.datetime_array is not None else 0
            print_manager.custom_debug(f"🔍 [STEP 11] ✓ Has .datetime_array ({dt_len} points)")
        if hasattr(result, 'time'):
            time_len = len(result.time) if result.time is not None else 0
            print_manager.custom_debug(f"🔍 [STEP 11] ✓ Has .time ({time_len} points)")
        
        # STEP 12: Set requested_trange (done in plotbot_main.py)
        print_manager.custom_debug(f"🔍 [STEP 12] requested_trange will be set by plotbot_main.py")
        
        print_manager.custom_debug(f"✅ Successfully updated {name}")
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
            try:
                lambda_func = self.callables[name]
                source_code = inspect.getsource(lambda_func).strip()
                print_manager.custom_debug(f"🔧 [GET_SOURCE] Lambda source: {source_code}")
                
                # Match patterns like: pb.mag_rtn_4sa.bn or plotbot.mag_rtn_4sa.bn or mag_rtn_4sa.bn (no prefix)
                # We need to match class.variable with optional plotbot/pb prefix
                pattern = r'(?:(?:pb|plotbot)\.)?(\w+)\.(\w+)'
                matches = re.findall(pattern, source_code)
                
                # Filter out numpy functions and other non-plotbot variables
                # Only keep matches that look like plotbot data class patterns
                filtered_matches = []
                for class_name, var_name in matches:
                    # Skip if it's a numpy function or other common patterns
                    if class_name not in ['np', 'numpy', 'plt', 'matplotlib']:
                        filtered_matches.append((class_name, var_name))
                matches = filtered_matches
                print_manager.custom_debug(f"🔧 [GET_SOURCE] Found variable references: {matches}")
            except (OSError, TypeError) as e:
                # inspect.getsource() fails in interactive contexts (notebooks, -c flag)
                # This is OK - lambda will evaluate without pre-loading deps
                print_manager.custom_debug(f"🔧 [GET_SOURCE] Cannot parse lambda in interactive context")
                print_manager.custom_debug(f"🔧 [GET_SOURCE] Lambda will evaluate and load dependencies on-the-fly")
                return []  # Let evaluate() continue - dependencies will load when lambda executes
            
            # Get the variable objects
            # STEP 2: Dependency Identification
            print_manager.custom_debug(f"🔍 [STEP 2] Identified {len(matches)} source variables from lambda")
            
            vars_to_load = []
            from ..data_cubby import data_cubby
            for class_name, var_name in matches:
                # class_name is now mag_rtn_4sa, var_name is bn ✅
                print_manager.custom_debug(f"🔍 [STEP 2] Source: {class_name}.{var_name}")
                class_instance = data_cubby.grab(class_name)
                if class_instance:
                    var = getattr(class_instance, var_name, None)
                    if var is not None:
                        vars_to_load.append(var)
            
            print_manager.custom_debug(f"🔍 [STEP 2] Total sources to load: {len(vars_to_load)}")
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
        
        # STEP 3: Time Range Request
        print_manager.custom_debug(f"🔍 [STEP 3] Evaluating '{name}' for trange {trange}")
        
        if name not in self.variables:
            print_manager.error(f"Custom variable '{name}' not found")
            return None
        
        operation = self.operations.get(name)
        print_manager.custom_debug(f"🔍 [STEP 3] Operation type: {operation}")
        print_manager.custom_debug(f"🔧 [EVALUATE] operation='{operation}'")
        print_manager.custom_debug(f"🔧 [EVALUATE] Checking lambda condition...")
        print_manager.custom_debug(f"🔧 [EVALUATE] operation=='lambda': {operation == 'lambda'}")
        print_manager.custom_debug(f"🔧 [EVALUATE] hasattr(self, 'callables'): {hasattr(self, 'callables')}")
        print_manager.custom_debug(f"🔧 [EVALUATE] name in self.callables: {name in self.callables if hasattr(self, 'callables') else False}")
        
        # LAMBDA VARIABLES: Evaluate the lambda (data already loaded!)
        if operation == 'lambda' and hasattr(self, 'callables') and name in self.callables:
            print_manager.custom_debug(f"🔧 [EVALUATE] ✅ ENTERED LAMBDA PATH!")
            try:
                # STEP 4: Check if we need to load data
                print_manager.custom_debug(f"🔍 [STEP 4] Checking if data load needed for trange {trange}")
                
                # LOAD DEPENDENCIES! (Like br_norm does)
                source_vars = self.get_source_variables(name)
                if source_vars:
                    from ..get_data import get_data
                    print_manager.custom_debug(f"🔍 [STEP 4] Loading {len(source_vars)} dependencies...")
                    get_data(trange, *source_vars)  # Recursive call!
                    print_manager.custom_debug(f"🔍 [STEP 4] Dependencies loaded")
                    
                    # STEP 5: Verify data retrieval
                    print_manager.custom_debug(f"🔍 [STEP 5] Verifying source data retrieval...")
                    for src_var in source_vars:
                        if hasattr(src_var, 'datetime_array') and src_var.datetime_array is not None:
                            print_manager.custom_debug(f"🔍 [STEP 5] {src_var.class_name}.{src_var.subclass_name}: {len(src_var.datetime_array)} points")
                            if len(src_var.datetime_array) > 0:
                                print_manager.custom_debug(f"🔍 [STEP 5]   First: {src_var.datetime_array[0]}, Last: {src_var.datetime_array[-1]}")
                            if hasattr(src_var, 'time'):
                                print_manager.custom_debug(f"🔍 [STEP 5]   .time exists: {src_var.time is not None}")
                        
                        # Set requested_trange on source variables so they clip correctly!
                        if hasattr(src_var, 'requested_trange'):
                            src_var.requested_trange = trange
                
                # STEP 6-7: Cadence check and resampling (TODO - will implement after testing)
                print_manager.custom_debug(f"🔍 [STEP 6] Cadence check: TODO")
                
                # DEBUG: Check source variable data sizes before lambda evaluation
                for src_var in source_vars:
                    if hasattr(src_var, 'data') and hasattr(src_var, 'datetime_array'):
                        dt_len = len(src_var.datetime_array) if src_var.datetime_array is not None else 0
                        data_len = len(src_var.data) if src_var.data is not None else 0
                        print_manager.custom_debug(f"🔧 [PRE-LAMBDA] {src_var.subclass_name}: datetime={dt_len}, .data={data_len}")
                
                # STEP 8: Equation Evaluation
                print_manager.custom_debug(f"🔍 [STEP 8] Evaluating lambda for '{name}'...")
                result = self.callables[name]()
                print_manager.custom_debug(f"🔍 [STEP 8] Result type: {type(result).__name__}, ID: {id(result)}")
                
                # STEP 8 continued: Verify result
                if hasattr(result, 'datetime_array') and result.datetime_array is not None:
                    print_manager.custom_debug(f"🔍 [STEP 8] Result has {len(result.datetime_array)} points")
                    if len(result.datetime_array) > 0:
                        # Spot check first 3 values if possible
                        data_preview = result[:min(3, len(result))] if len(result) > 0 else []
                        print_manager.custom_debug(f"🔍 [STEP 8] First 3 values: {data_preview}")
                    
                    # 🎯 CRITICAL: Clip result to requested trange!
                    # The lambda operates on full merged arrays, but we only want data for THIS trange
                    # FIX: Create NEW plot_manager with clipped data (don't modify in place!)
                    from ..plotbot_helpers import time_clip
                    from ..plot_manager import plot_manager
                    from ..plot_config import plot_config as plot_config_class
                    
                    original_datetime = result.datetime_array.copy() if hasattr(result.datetime_array, 'copy') else result.datetime_array
                    indices = time_clip(original_datetime, trange[0], trange[1])
                    print_manager.custom_debug(f"🔧 [EVALUATE] Clipping to trange, found {len(indices)} points")
                    print_manager.custom_debug(f"🔧 [EVALUATE] Original result size: {len(result.view(np.ndarray))}, datetime size: {len(original_datetime)}")
                    
                    if len(indices) > 0:
                        # Get the raw NumPy array from the result
                        result_raw_array = result.view(np.ndarray)
                        
                        # Clip the raw array
                        if result_raw_array.ndim == 1:
                            clipped_array = result_raw_array[indices]
                        else:
                            clipped_array = result_raw_array[indices, ...]
                        
                        print_manager.custom_debug(f"🔧 [EVALUATE] Clipped array shape: {clipped_array.shape}")
                        
                        # Create new plot_config with clipped data
                        new_config = plot_config_class(**result.plot_config.__dict__)
                        new_config.datetime_array = original_datetime[indices]
                        
                        # Clip time if present
                        if hasattr(result, 'time') and result.time is not None:
                            new_config.time = result.time[indices]
                        
                        # Create NEW plot_manager with clipped data
                        result = plot_manager(clipped_array, plot_config=new_config)
                        
                        print_manager.custom_debug(f"🔧 [EVALUATE] Created new plot_manager with {len(result.datetime_array)} points")
                
                # Preserve user-defined attributes from old variable
                old_var = self.variables[name]
                style_attrs = ['color', 'y_label', 'legend_label', 'plot_type', 'y_scale', 
                              'line_style', 'marker_size', 'marker_style', 'line_width']
                for attr in style_attrs:
                    if hasattr(old_var, attr):
                        old_value = getattr(old_var, attr)
                        object.__setattr__(result, attr, old_value)
                
                # STEP 9: Data Cubby Storage
                print_manager.custom_debug(f"🔍 [STEP 9] Storing result in container.variables...")
                self.variables[name] = result
                print_manager.custom_debug(f"🔍 [STEP 9] Stored '{name}' with ID: {id(result)}")
                
                # Set metadata
                object.__setattr__(result, 'class_name', 'custom_variables')
                object.__setattr__(result, 'subclass_name', name)
                object.__setattr__(result, 'data_type', 'custom_data_type')
                
                # 🎯 CRITICAL: Set requested_trange for proper time clipping
                if hasattr(result, 'requested_trange'):
                    object.__setattr__(result, 'requested_trange', trange)
                    print_manager.custom_debug(f"🔍 [STEP 12] Set requested_trange: {trange}")
                
                # Update global reference
                print_manager.custom_debug(f"🔍 [STEP 9] Making '{name}' globally accessible...")
                self._make_globally_accessible(name, result)
                
                # STEP 10: Tracker update is done in get_data.py
                print_manager.custom_debug(f"🔍 [STEP 10] Tracker will be updated by get_data()")
                
                # STEP 11: Variable Verification
                print_manager.custom_debug(f"🔍 [STEP 11] Verifying final variable state...")
                if hasattr(result, 'data'):
                    print_manager.custom_debug(f"🔍 [STEP 11] ✓ Has .data property")
                if hasattr(result, 'datetime_array'):
                    dt_len = len(result.datetime_array) if result.datetime_array is not None else 0
                    print_manager.custom_debug(f"🔍 [STEP 11] ✓ Has .datetime_array ({dt_len} points)")
                if hasattr(result, 'time'):
                    time_len = len(result.time) if result.time is not None else 0
                    print_manager.custom_debug(f"🔍 [STEP 11] ✓ Has .time ({time_len} points)")
                
                print_manager.custom_debug(f"🔧 [EVALUATE] ✅ Lambda '{name}' ready, returning (ID:{id(result)})")
                return result
                
            except Exception as e:
                print_manager.error(f"Failed to evaluate lambda '{name}': {e}")
                return None
        
        # DIRECT EXPRESSION VARIABLES: Call update() for re-evaluation
        elif self.sources.get(name):
            print_manager.custom_debug(f"🔍 [STEP 3] Direct expression variable '{name}', calling update...")
            
            # STEP 4-5: Load sources first
            source_vars = self.get_source_variables(name)
            if source_vars:
                from ..get_data import get_data
                print_manager.custom_debug(f"🔍 [STEP 4] Loading {len(source_vars)} dependencies...")
                get_data(trange, *source_vars)
                print_manager.custom_debug(f"🔍 [STEP 5] Dependencies loaded")
                
                # Verify retrieval
                for src_var in source_vars:
                    if hasattr(src_var, 'datetime_array') and src_var.datetime_array is not None:
                        print_manager.custom_debug(f"🔍 [STEP 5] {src_var.class_name}.{src_var.subclass_name}: {len(src_var.datetime_array)} points")
            
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

def _check_for_lambda_warning(expression, name):
    """
    Check if a direct expression should have used lambda and warn if so.
    
    Complex expressions that need lambda include:
    - Chained operations (sources that have operations)
    - NumPy ufunc operations (arctan2, degrees, etc.)
    
    Note: Simple binary operations (br * bt) work fine without lambda when accessed
    via the global namespace (plotbot.variable_name).
    """
    from ..plot_manager import plot_manager
    
    # Only check if it's a plot_manager
    if not isinstance(expression, plot_manager):
        return
    
    # Check if it has an operation (meaning it's derived, not raw data)
    if not hasattr(expression, 'operation') or expression.operation is None:
        return
    
    operation = expression.operation
    
    # Get sources if available
    sources = []
    if hasattr(expression, 'source_var') and expression.source_var is not None:
        sources = expression.source_var if isinstance(expression.source_var, list) else [expression.source_var]
    
    # Detect complex operations that need lambda:
    needs_lambda = False
    reason = ""
    
    # Check if any source itself has an operation (chained operations)
    has_chained_operations = False
    for src in sources:
        if hasattr(src, 'operation') and src.operation is not None:
            has_chained_operations = True
            break
    
    # 1. Chained operations (sources that themselves have operations)
    # This is the most important case - e.g., (a/b) + c
    if has_chained_operations:
        needs_lambda = True
        reason = f"chained operations (result of one operation used in '{operation}')"
    
    # 2. NumPy ufunc operations (like arctan2, degrees, etc.)
    # These typically have operation names that are numpy function names
    numpy_funcs = ['arctan2', 'arctan', 'degrees', 'radians', 'sqrt', 'log', 'log10', 'exp',
                   'sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh', 'power', 'square', 'cbrt']
    if operation in numpy_funcs:
        needs_lambda = True
        reason = f"NumPy function '{operation}'"
    
    # 3. Multiple operations in sequence (3+ sources usually means accumulated operations)
    # e.g., (a / b) + c would have 3 sources after accumulation
    elif len(sources) >= 3:
        needs_lambda = True
        reason = f"multiple accumulated operations with {len(sources)} sources"
    
    # If we detected a complex operation, print warning
    if needs_lambda:
        print_manager.status(
            f"⚠️  Complex expression detected for '{name}': {reason}\n"
            f"    💡 Consider using lambda for reliable results:\n"
            f"       custom_variable('{name}', lambda: your_expression)\n"
            f"    📖 See plotbot_custom_variable_examples.ipynb in example_notebooks/ for details."
        )

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
        # STEP 1: Variable Definition
        print_manager.custom_debug(f"🔍 [STEP 1] Creating custom variable '{name}'")
        print_manager.custom_debug(f"🔍 [STEP 1] Type: LAMBDA expression")
        print_manager.debug(f"Custom variable '{name}' uses lambda - will evaluate lazily")
        
        # Clear any existing calculation cache - CRITICAL when redefining!
        global_tracker.clear_calculation_cache('custom_data_type', name)
        print_manager.custom_debug(f"🔍 [STEP 1] Cleared tracker cache")
        
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
    # STEP 1: Variable Definition
    print_manager.custom_debug(f"🔍 [STEP 1] Creating custom variable '{name}'")
    print_manager.custom_debug(f"🔍 [STEP 1] Type: DIRECT expression")
    
    # Check if this should have used lambda (for complex expressions)
    _check_for_lambda_warning(expression, name)
    
    expr_has_data = hasattr(expression, 'datetime_array') and expression.datetime_array is not None and len(expression.datetime_array) > 0
    expr_data_points = len(expression.datetime_array) if expr_has_data else 0
    print_manager.debug(f"DEBUG custom_variable: Incoming expression for '{name}' already has data? {expr_has_data} ({expr_data_points} points)")

    # Clear any existing calculation cache for this variable name
    print_manager.custom_debug(f"🔍 [STEP 1] Clearing tracker cache for '{name}'")
    global_tracker.clear_calculation_cache('custom_data_type', name)
    
    # Get source variables and operation type
    # STEP 2: Dependency Identification (for direct expressions)
    print_manager.custom_debug(f"🔍 [STEP 2.1] Checking for source_var attribute...")
    print_manager.custom_debug(f"🔍 [STEP 2.1] has source_var: {hasattr(expression, 'source_var')}")
    if hasattr(expression, 'source_var'):
        print_manager.custom_debug(f"🔍 [STEP 2.1] source_var is None: {expression.source_var is None}")
        if expression.source_var is not None:
            print_manager.custom_debug(f"🔍 [STEP 2.1] source_var length: {len(expression.source_var)}")
            print_manager.custom_debug(f"🔍 [STEP 2.1] source_var content: {expression.source_var}")
    
    sources = []
    operation = 'div'  # Default to division as most custom vars are ratios
    
    # Extract sources from expression
    if hasattr(expression, 'source_var') and expression.source_var is not None:
        # First try using source_var directly
        for src in expression.source_var:
            if hasattr(src, 'class_name') and hasattr(src, 'subclass_name'):
                sources.append(src)
                print_manager.custom_debug(f"🔍 [STEP 2] Source: {src.class_name}.{src.subclass_name}")
        
        # Get operation type if available
        if hasattr(expression, 'operation'):
            operation = expression.operation
            print_manager.custom_debug(f"🔍 [STEP 2] Operation: {operation}")
    
    print_manager.custom_debug(f"🔍 [STEP 2] Found {len(sources)} source variables for direct expression")
    
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