# Plotbot Startup Optimization: Lazy Loading Implementation Plan

## Current Problem
Plotbot takes 30+ seconds to initialize because it eagerly loads all dependencies:
- 20+ data classes (PSP, WIND, custom CDF classes)  
- Heavy scientific libraries (matplotlib, scipy, pandas, cdflib)
- Auto-registration of custom classes
- Instance creation for every data class

## Proposed Solution: Multi-Level Lazy Loading

### Level 1: Core-Only Import (Target: <2 seconds)
```python
import plotbot  # Only loads essential components
```
**Loads only:**
- Core utilities (print_manager, config, data_cubby)
- Basic numpy support
- No data classes, no plotting libraries

### Level 2: On-Demand Class Loading
```python
# Classes loaded only when first accessed
plotbot.mag_rtn_4sa.br  # Triggers: import matplotlib, load mag class
plotbot(trange, mag_rtn_4sa.br, 1)  # Triggers: full plotting stack
```

### Level 3: Fast Mode Toggle
```python
plotbot.config.fast_mode = True  # Skip custom class scanning
plotbot.config.lazy_mode = False  # Disable all lazy loading (current behavior)
```

## Implementation Strategy

### 1. Lazy Import Wrapper System
Create a proxy class that defers imports until first access:

```python
class LazyDataClass:
    def __init__(self, module_path, class_name):
        self._module_path = module_path
        self._class_name = class_name
        self._instance = None
        
    def __getattr__(self, name):
        if self._instance is None:
            self._load_class()
        return getattr(self._instance, name)
        
    def _load_class(self):
        # Import and instantiate on first access
        module = importlib.import_module(self._module_path)
        class_type = getattr(module, f"{self._class_name}_class")
        self._instance = class_type(None)
```

### 2. Deferred Scientific Library Loading
Move heavy imports from `__init__.py` to function-level imports:

**Current (eager):**
```python
# __init__.py
import matplotlib.pyplot as plt
from .plotbot_main import plotbot  # Imports scipy, pandas, etc.
```

**Proposed (lazy):**
```python
# __init__.py - minimal imports only
from .lazy_loader import LazyModule

plt = LazyModule('matplotlib.pyplot')
plotbot = LazyModule('plotbot.plotbot_main', 'plotbot')
```

### 3. Smart Custom Class Registration
Replace auto-scanning with on-demand discovery:

**Current:**
```python
# Scans ALL files at startup
_auto_register_custom_classes()  # Expensive!
```

**Proposed:**
```python
# Only scan when custom classes are first accessed
def get_custom_class(name):
    if name not in _custom_cache:
        _discover_custom_class(name)
    return _custom_cache[name]
```

### 4. Tiered __init__.py Structure

```python
# plotbot/__init__.py - CORE ONLY
from .config import config
from .print_manager import print_manager
from .data_cubby import data_cubby

# Lazy imports - loaded on first access
from .lazy_loader import create_lazy_classes

# Create lazy proxies for all data classes
mag_rtn_4sa = create_lazy_classes('psp_mag_rtn_4sa', 'mag_rtn_4sa')
proton = create_lazy_classes('psp_proton', 'proton') 
# ... etc for all classes

# Functions loaded on first call
plotbot = LazyFunction('plotbot.plotbot_main', 'plotbot')
multiplot = LazyFunction('plotbot.multiplot', 'multiplot')
```

## File Changes Required

### New Files:
1. `plotbot/lazy_loader.py` - Core lazy loading infrastructure
2. `plotbot/fast_init.py` - Ultra-fast initialization mode
3. `plotbot/config_startup.py` - Startup configuration options

### Modified Files:
1. `plotbot/__init__.py` - Replace eager imports with lazy proxies
2. `plotbot/plotbot_main.py` - Move heavy imports to function level
3. `plotbot/data_classes/*.py` - Optional lazy dependency imports

## Performance Targets

| Mode | Startup Time | Features Available |
|------|-------------|-------------------|
| **Fast** | <1 second | Core utils only, lazy everything |
| **Standard** | <5 seconds | Common classes loaded, plotting deferred |
| **Full** | ~30 seconds | Everything loaded (current behavior) |

## Implementation Phases

### Phase 1: Lazy Scientific Libraries (Week 1)
- Move matplotlib/scipy imports to function level
- Create LazyModule wrapper system
- Target: 15-20 second improvement

### Phase 2: Lazy Data Classes (Week 2) 
- Implement LazyDataClass proxies
- Replace eager class instantiation
- Target: Additional 5-10 second improvement

### Phase 3: Smart Custom Class Loading (Week 3)
- Replace auto-scanning with on-demand discovery
- Implement custom class caching
- Target: 2-5 second improvement for users with many custom classes

### Phase 4: Fast Mode Toggle (Week 4)
- Ultra-minimal startup option
- Configuration system for startup behavior
- Target: <2 second startup for basic usage

## Backward Compatibility

The lazy loading system will be **100% backward compatible**:
```python
# All existing code continues to work unchanged
import plotbot
from plotbot import *
plotbot(trange, mag_rtn_4sa.br, 1)  # Same API, just faster startup
```

Users will see:
- ✅ Same API and functionality
- ✅ Faster startup (transparent lazy loading)
- ✅ Optional fast mode for power users
- ✅ No breaking changes

## Testing Strategy

1. **Performance benchmarking** - Measure startup times before/after
2. **Functionality testing** - Ensure all existing features work
3. **Lazy loading testing** - Verify deferred imports work correctly
4. **Memory testing** - Confirm memory usage improvements

## Rollout Plan

1. **Development branch** - Implement lazy loading system
2. **Alpha testing** - Test with core users on performance
3. **Beta release** - Broader testing with fallback to current system
4. **Production release** - Default to lazy loading with config option to disable

This implementation will dramatically reduce startup time while maintaining full compatibility and functionality.

