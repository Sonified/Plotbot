#!/usr/bin/env python3
"""
Test WIND SWE H5 electron temperature with real data
Tests the complete pipeline: download → processing → plotting
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from plotbot import config
from plotbot.plotbot_main import plotbot
from plotbot.print_manager import print_manager
from plotbot import wind_swe_h5

# Enable detailed output
print_manager.show_status = True
print_manager.show_processing = True
print_manager.show_datacubby = True

print("🧪 Testing WIND SWE H5 electron temperature with real data...")
print("🎯 This will test: download → CDF processing → plotting")

# Zoom in to see the negative spike area
trange_strings = ['2022/06/02 00:48:00.000', '2022/06/02 00:50:00.000']
print(f"📅 Time range: {trange_strings}")

# Configure for dynamic server (SPDF first)
original_server = config.data_server
config.data_server = 'dynamic'
print(f"🌐 Server: {config.data_server}")

try:
    print("\n🚀 Testing WIND SWE H5 electron temperature plotting...")
    
    # Test basic plotting
    plotbot(trange_strings, wind_swe_h5.t_elec, 1)
    
    print("✅ WIND SWE H5 electron temperature plotting successful!")
    print("🎉 Complete pipeline working: download → processing → plotting")
    
except Exception as e:
    print(f"❌ WIND SWE H5 test failed: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    # Restore original server setting
    config.data_server = original_server
    print(f"🔄 Restored server to: {config.data_server}")

print("\n🎯 WIND SWE H5 real data test complete!") 