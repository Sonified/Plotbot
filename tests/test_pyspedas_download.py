#!/usr/bin/env python3
"""
Minimal test to reproduce the local file detection issue.

Issue: plotbot says "Local files not found" even when files exist locally.
"""

import os
import sys
from pathlib import Path

# Add plotbot to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_mag_sc_4sa_file_detection():
    """Test local file detection for mag_SC_4sa."""
    
    from plotbot.data_download_pyspedas import smart_check_local_pyspedas_files
    from plotbot.data_classes.data_types import data_types
    from plotbot.config import config
    
    print("Testing local file detection for mag_SC_4sa")
    print("=" * 50)
    
    # Test parameters (the problematic case from notebook)
    plotbot_key = 'mag_SC_4sa'
    trange = ['2021/04/26 00:00:00.000', '2021/04/27 00:00:00.000']
    
    print(f"Plotbot key: {plotbot_key}")
    print(f"Time range: {trange}")
    
    # Check what files actually exist
    print("\n1. Checking what files actually exist:")
    if plotbot_key in data_types:
        config_data = data_types[plotbot_key]
        data_level = config_data['data_level']
        local_path = config_data['local_path'].format(data_level=data_level)
        year_path = Path(config.data_dir) / local_path / "2021"
        
        print(f"   Looking in: {year_path}")
        if year_path.exists():
            files = list(year_path.glob("*2021042*"))
            print(f"   Found {len(files)} files:")
            for f in files:
                print(f"     - {f.name}")
        else:
            print(f"   Directory does not exist: {year_path}")
    
    # Test the smart_check function
    print("\n2. Testing smart_check_local_pyspedas_files:")
    try:
        result = smart_check_local_pyspedas_files(plotbot_key, trange)
        if result:
            print(f"   SUCCESS: Found {len(result)} files")
            for f in result:
                print(f"     - {f}")
        else:
            print("   FAILED: No files found by smart_check function")
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mag_sc_4sa_file_detection()

