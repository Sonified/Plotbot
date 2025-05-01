import sys
from pathlib import Path
import traceback

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Modify proton_fits_class to add tracing
from plotbot.data_classes.psp_proton_fits_classes import proton_fits_class

# Original properties
original_vsw_mach = proton_fits_class.vsw_mach
original_vdrift_va_p2p1_apfits = proton_fits_class.vdrift_va_p2p1_apfits
original_abs_vdrift_va_p2p1_apfits = proton_fits_class.abs_vdrift_va_p2p1_apfits

# Add tracing to properties
def trace_vsw_mach(self):
    print("\n*** TRACE: vsw_mach property accessed ***")
    traceback.print_stack(limit=8)
    return original_vsw_mach.__get__(self, type(self))

def trace_vdrift_va_p2p1_apfits(self):
    print("\n*** TRACE: vdrift_va_p2p1_apfits property accessed ***")
    traceback.print_stack(limit=8)
    return original_vdrift_va_p2p1_apfits.__get__(self, type(self))

def trace_abs_vdrift_va_p2p1_apfits(self):
    print("\n*** TRACE: abs_vdrift_va_p2p1_apfits property accessed ***")
    traceback.print_stack(limit=8)
    return original_abs_vdrift_va_p2p1_apfits.__get__(self, type(self))

# Replace with traced versions
proton_fits_class.vsw_mach = property(trace_vsw_mach)
proton_fits_class.vdrift_va_p2p1_apfits = property(trace_vdrift_va_p2p1_apfits)
proton_fits_class.abs_vdrift_va_p2p1_apfits = property(trace_abs_vdrift_va_p2p1_apfits)

# Original methods
original_set_ploptions = proton_fits_class.set_ploptions

def trace_set_ploptions(self):
    print("\n*** TRACE: set_ploptions called ***")
    result = original_set_ploptions(self)
    print("*** TRACE: set_ploptions completed ***")
    return result

proton_fits_class.set_ploptions = trace_set_ploptions

# Create a simple test
def run_test():
    print("\n=== Running proton_fits_class trace test ===")
    
    # Import minimal dependencies
    from plotbot.data_import import DataObject
    import numpy as np
    
    # Create a minimal data object
    times = np.array([1, 2, 3])  # Example times
    data = {
        'Epoch': times,
        'n_tot': np.array([10, 20, 30])  # Example density data
    }
    data_obj = DataObject(times=times, data=data)
    
    # Initialize proton_fits_class
    print("\n--- Creating proton_fits_class instance ---")
    instance = proton_fits_class(data_obj)
    
    print("\n--- Accessing specific attributes ---")
    # Only access n_tot, not any CWYN properties
    print("Accessing n_tot...")
    n_tot_data = instance.raw_data.get('n_tot')
    print(f"n_tot data: {n_tot_data}")
    
    # Check if instance has plot_manager for n_tot
    print("\nAccessing n_tot plot_manager...")
    if hasattr(instance, 'n_tot'):
        print(f"n_tot plot_manager exists, type: {type(instance.n_tot)}")
    else:
        print("n_tot plot_manager doesn't exist")
    
    print("\n=== Test complete ===")

if __name__ == "__main__":
    run_test() 