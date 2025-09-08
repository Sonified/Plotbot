#!/usr/bin/env python3
"""
Test individual data class import timing to identify bottlenecks.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import plotbot
sys.path.insert(0, str(Path(__file__).parent))

from plotbot.import_timer import ImportTimer

def time_data_class_imports():
    """Time individual data class imports."""
    
    timer = ImportTimer()
    timer.start_session("data_class_imports")
    
    # Test PSP data classes
    print("\n🔍 TIMING PSP DATA CLASSES:")
    timer.time_import('psp_mag_rtn_4sa', from_module='plotbot.data_classes')
    timer.time_import('psp_mag_rtn', from_module='plotbot.data_classes') 
    timer.time_import('psp_proton', from_module='plotbot.data_classes')
    timer.time_import('psp_proton_hr', from_module='plotbot.data_classes')
    
    # Test WIND data classes
    print("\n🔍 TIMING WIND DATA CLASSES:")
    timer.time_import('wind_mfi_classes', from_module='plotbot.data_classes')
    timer.time_import('wind_swe_h5_classes', from_module='plotbot.data_classes')
    
    # Test other classes
    print("\n🔍 TIMING OTHER CLASSES:")
    timer.time_import('psp_qtn_classes', from_module='plotbot.data_classes')
    timer.time_import('psp_orbit', from_module='plotbot.data_classes')
    
    timer.end_session()
    timer.print_report()

if __name__ == "__main__":
    time_data_class_imports()
