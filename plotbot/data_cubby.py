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
        
        result = (cls.cubby.get(identifier) or 
                 cls.class_registry.get(identifier) or 
                 cls.subclass_registry.get(identifier))
                 
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

# Create global instance
data_cubby = data_cubby() 
print('initialized data_cubby')