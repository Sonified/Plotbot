"""
Lazy Loading System for Plotbot

This module provides lazy loading infrastructure to significantly improve
plotbot startup times by deferring expensive imports until they're needed.

Key features:
- LazyFunction: Defers function imports until first call
- LazyModule: Defers module imports until first access
- LazyDataClass: Defers data class instantiation until first access
- Transparent API: All lazy objects behave exactly like their non-lazy counterparts
"""

import importlib
import functools
from typing import Any, Dict, Optional, Callable, Union
import threading
from pathlib import Path

class LazyFunction:
    """
    A proxy that defers function import until first call.
    
    Usage:
        plotbot = LazyFunction('plotbot.plotbot_main', 'plotbot')
        # Function not imported yet
        plotbot(trange, var, axis)  # Function imported and called
    """
    
    def __init__(self, module_path: str, function_name: str, alias: Optional[str] = None):
        self.module_path = module_path
        self.function_name = function_name
        self.alias = alias or function_name
        self._function = None
        self._lock = threading.Lock()
        self._loaded = False
        
    def _load_function(self):
        """Load the function if not already loaded."""
        if self._loaded:
            return self._function
            
        with self._lock:
            if self._loaded:  # Double-check locking
                return self._function
                
            try:
                # Import the module
                module = importlib.import_module(self.module_path)
                
                # Get the function
                self._function = getattr(module, self.function_name)
                self._loaded = True
                
                # Optional: Print lazy loading info
                from .import_timer import timer
                if hasattr(timer, 'enabled') and timer.enabled:
                    print(f"🔄 Lazy loaded: {self.alias} from {self.module_path}")
                
                return self._function
                
            except Exception as e:
                raise ImportError(f"Failed to lazy load {self.alias} from {self.module_path}.{self.function_name}: {e}")
    
    def __call__(self, *args, **kwargs):
        """Call the function, loading it first if necessary."""
        func = self._load_function()
        return func(*args, **kwargs)
    
    def __getattr__(self, name):
        """Forward attribute access to the loaded function."""
        func = self._load_function()
        return getattr(func, name)
    
    def __repr__(self):
        status = "loaded" if self._loaded else "not loaded"
        return f"LazyFunction({self.alias}, {status})"

class LazyModule:
    """
    A proxy that defers module import until first access.
    
    Usage:
        plt = LazyModule('matplotlib.pyplot')
        # Module not imported yet
        plt.figure()  # Module imported and used
    """
    
    def __init__(self, module_path: str, alias: Optional[str] = None):
        self.module_path = module_path
        self.alias = alias or module_path.split('.')[-1]
        self._module = None
        self._lock = threading.Lock()
        self._loaded = False
        
    def _load_module(self):
        """Load the module if not already loaded."""
        if self._loaded:
            return self._module
            
        with self._lock:
            if self._loaded:  # Double-check locking
                return self._module
                
            try:
                self._module = importlib.import_module(self.module_path)
                self._loaded = True
                
                # Optional: Print lazy loading info
                from .import_timer import timer
                if hasattr(timer, 'enabled') and timer.enabled:
                    print(f"🔄 Lazy loaded module: {self.alias}")
                
                return self._module
                
            except Exception as e:
                raise ImportError(f"Failed to lazy load module {self.module_path}: {e}")
    
    def __getattr__(self, name):
        """Forward attribute access to the loaded module."""
        module = self._load_module()
        return getattr(module, name)
    
    def __call__(self, *args, **kwargs):
        """Allow the module to be called if it's callable."""
        module = self._load_module()
        return module(*args, **kwargs)
    
    def __repr__(self):
        status = "loaded" if self._loaded else "not loaded"
        return f"LazyModule({self.alias}, {status})"

class LazyDataClass:
    """
    A proxy that defers data class instantiation until first access.
    
    Usage:
        mag_rtn_4sa = LazyDataClass('plotbot.data_classes.psp_mag_rtn_4sa', 'mag_rtn_4sa_class')
        # Class not instantiated yet
        mag_rtn_4sa.br  # Class instantiated and accessed
    """
    
    def __init__(self, module_path: str, class_name: str, instance_name: Optional[str] = None):
        self.module_path = module_path
        self.class_name = class_name
        self.instance_name = instance_name or class_name.replace('_class', '')
        self._instance = None
        self._lock = threading.Lock()
        self._loaded = False
        
    def _load_instance(self):
        """Load the class instance if not already loaded."""
        if self._loaded:
            return self._instance
            
        with self._lock:
            if self._loaded:  # Double-check locking
                return self._instance
                
            try:
                # Import the module
                module = importlib.import_module(self.module_path)
                
                # Get the class
                class_type = getattr(module, self.class_name)
                
                # Instantiate with None (plotbot pattern)
                self._instance = class_type(None)
                self._loaded = True
                
                # Optional: Print lazy loading info
                from .import_timer import timer
                if hasattr(timer, 'enabled') and timer.enabled:
                    print(f"🔄 Lazy loaded data class: {self.instance_name}")
                
                return self._instance
                
            except Exception as e:
                raise ImportError(f"Failed to lazy load {self.instance_name} from {self.module_path}.{self.class_name}: {e}")
    
    def __getattr__(self, name):
        """Forward attribute access to the loaded instance."""
        instance = self._load_instance()
        return getattr(instance, name)
    
    def __setattr__(self, name, value):
        """Forward attribute setting to the loaded instance."""
        # Allow setting of internal attributes
        if name.startswith('_') or name in ['module_path', 'class_name', 'instance_name']:
            object.__setattr__(self, name, value)
        else:
            instance = self._load_instance()
            setattr(instance, name, value)
    
    def __call__(self, *args, **kwargs):
        """Allow the instance to be called if it's callable."""
        instance = self._load_instance()
        return instance(*args, **kwargs)
    
    def __repr__(self):
        status = "loaded" if self._loaded else "not loaded"
        return f"LazyDataClass({self.instance_name}, {status})"

class LazyImportGroup:
    """
    A container for grouping related lazy imports that should be loaded together.
    
    Usage:
        plotting_group = LazyImportGroup('plotting_functions', {
            'plotbot': LazyFunction('plotbot.plotbot_main', 'plotbot'),
            'multiplot': LazyFunction('plotbot.multiplot', 'multiplot')
        })
    """
    
    def __init__(self, group_name: str, lazy_objects: Dict[str, Union[LazyFunction, LazyModule, LazyDataClass]]):
        self.group_name = group_name
        self.lazy_objects = lazy_objects
        self._loaded = False
        self._lock = threading.Lock()
    
    def load_all(self):
        """Load all objects in this group."""
        if self._loaded:
            return
            
        with self._lock:
            if self._loaded:
                return
                
            for name, obj in self.lazy_objects.items():
                if hasattr(obj, '_load_function'):
                    obj._load_function()
                elif hasattr(obj, '_load_module'):
                    obj._load_module()
                elif hasattr(obj, '_load_instance'):
                    obj._load_instance()
            
            self._loaded = True
    
    def __getattr__(self, name):
        """Access a lazy object by name."""
        if name in self.lazy_objects:
            return self.lazy_objects[name]
        raise AttributeError(f"'{self.group_name}' has no attribute '{name}'")

def create_lazy_function(module_path: str, function_name: str, alias: Optional[str] = None) -> LazyFunction:
    """Convenience function to create a LazyFunction."""
    return LazyFunction(module_path, function_name, alias)

def create_lazy_module(module_path: str, alias: Optional[str] = None) -> LazyModule:
    """Convenience function to create a LazyModule."""
    return LazyModule(module_path, alias)

def create_lazy_data_class(module_path: str, class_name: str, instance_name: Optional[str] = None) -> LazyDataClass:
    """Convenience function to create a LazyDataClass."""
    return LazyDataClass(module_path, class_name, instance_name)

# Registry for tracking all lazy objects (useful for debugging)
_lazy_registry: Dict[str, Union[LazyFunction, LazyModule, LazyDataClass]] = {}

def register_lazy_object(name: str, obj: Union[LazyFunction, LazyModule, LazyDataClass]):
    """Register a lazy object for debugging purposes."""
    _lazy_registry[name] = obj

def get_lazy_status() -> Dict[str, bool]:
    """Get the loading status of all registered lazy objects."""
    return {name: obj._loaded for name, obj in _lazy_registry.items()}

def force_load_all():
    """Force load all registered lazy objects (useful for testing)."""
    for name, obj in _lazy_registry.items():
        if hasattr(obj, '_load_function'):
            obj._load_function()
        elif hasattr(obj, '_load_module'):
            obj._load_module()
        elif hasattr(obj, '_load_instance'):
            obj._load_instance()

