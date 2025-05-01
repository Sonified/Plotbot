from .print_manager import print_manager
import numpy as np  # Needed for array handling in debug printing

class data_cubby:
    cubby = {}
    class_registry = {}
    subclass_registry = {}

    @classmethod
    def stash(cls, obj, class_name=None, subclass_name=None):
        """Store object with class and subclass tracking."""
        print(f"DEBUG data_cubby STASH: Storing object id={id(obj)} with class_name='{class_name}', subclass_name='{subclass_name}'")
        
        print_manager.datacubby("\n=== Stashing Debug (INSIDE DATA CUBBY)===")
        identifier = f"{class_name}.{subclass_name}" if class_name and subclass_name else class_name
        print_manager.datacubby(f"Stashing with identifier: {identifier}")
        print_manager.variable_testing(f"Stashing variable in data_cubby: {identifier}")
        
        # Debug print object attributes before stashing
        print_manager.datacubby(f"Attributes before stash:")
        for attr in dir(obj):
            if not attr.startswith('__'):
                value = getattr(obj, attr, 'not set')
                if attr == 'datetime_array':
                    is_none = value is None
                    length = len(value) if hasattr(value, '__len__') else 'N/A'
                    print_manager.datacubby(f"- {attr}: Is None={is_none}, Length={length}")
                    continue
                # ALWAYS truncate arrays/lists to 10 items
                if isinstance(value, (list, np.ndarray)):
                    if isinstance(value, np.ndarray):
                        preview = str(value.flatten()[:10]) + "..."
                    else:
                        preview = str(value[:10]) + "..."
                    print_manager.datacubby(f"- {attr}: {preview}")
                else:
                    print_manager.datacubby(f"- {attr}: {value}")
            
        cls.cubby[identifier] = obj
        if class_name:
            cls.class_registry[class_name] = obj
            print_manager.datacubby(f"Stored in class_registry: {class_name}")
            
        if subclass_name:
            cls.subclass_registry[subclass_name] = obj
            print_manager.datacubby(f"Stored in subclass_registry: {subclass_name}")
            
        print_manager.datacubby("=== End Stashing Debug (LEAVING DATA CUBBY)===\n")
        return obj

    @classmethod
    def grab(cls, identifier):
        """Retrieve object by its identifier."""
        print(f"DEBUG data_cubby GRAB: Attempting to grab identifier='{identifier}'")
        
        print_manager.datacubby(f"\n=== Retrieving {identifier} from data_cubby ===")
        
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
        
        retrieved_id = id(result) if result is not None else 'None'
        print(f"DEBUG data_cubby GRAB: Retrieved object id={retrieved_id} for identifier='{identifier}'")
        
        if result is not None:
            print_manager.datacubby(f"✅ Successfully retrieved {identifier}")
        else:
            print_manager.datacubby(f"❌ Failed to retrieve {identifier}")
        
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
        
        print_manager.datacubby("=== End Retrieval Debug (LEAVING DATA CUBBY)===\n")
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
print('initialized data_cubby')