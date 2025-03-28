from .print_manager import print_manager
import numpy as np  # Needed for array handling in debug printing

class data_cubby:
    cubby = {}
    class_registry = {}
    subclass_registry = {}

    @classmethod
    def stash(cls, obj, class_name=None, subclass_name=None):
        """Store object with class and subclass tracking."""
        print_manager.datacubby("\n=== Stashing Debug (INSIDE DATA CUBBY)===")
        identifier = f"{class_name}.{subclass_name}" if class_name and subclass_name else class_name
        print_manager.datacubby(f"Stashing with identifier: {identifier}")
        print_manager.variable_testing(f"Stashing variable in data_cubby: {identifier}")
        
        # Debug print object attributes before stashing
        print_manager.datacubby(f"Attributes before stash:")
        for attr in dir(obj):
            if not attr.startswith('__'):
                value = getattr(obj, attr, 'not set')
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
        print_manager.datacubby("\n=== Retrieval Debug INSIDE DATA CUBBY===")
        print_manager.datacubby(f"Attempting to retrieve: {identifier}")
        print_manager.variable_testing(f"Retrieving variable from data_cubby: {identifier}")
        
        result = (cls.cubby.get(identifier) or 
                 cls.class_registry.get(identifier) or 
                 cls.subclass_registry.get(identifier))
        
        if result is not None:
            print_manager.variable_testing(f"Successfully retrieved {identifier} from data_cubby")
        else:
            print_manager.variable_testing(f"Failed to retrieve {identifier} from data_cubby")
                 
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

    def make_globally_accessible(self, variable, name):
        """
        Make a variable accessible globally with the given name.
        
        Parameters
        ----------
        variable : Variable
            The variable to make globally accessible
        name : str
            The name to use for the variable in the global scope
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