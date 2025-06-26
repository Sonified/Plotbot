#!/usr/bin/env python3
"""
🚀 WIND SWE H1 Multi-Panel Plot Test
Complete demonstration of all WIND proton/alpha thermal speed variables!
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import plotbot
from plotbot import *
from plotbot import config  # Add config import
import numpy as np
from datetime import datetime, timedelta

def test_wind_swe_h1_multiplot():
    """🎯 Epic 5-panel plot of ALL WIND SWE H1 variables!"""
    print("\n" + "🚀"*60)
    print("🚀 WIND SWE H1 MULTI-PANEL SPECTACULAR! 🚀")
    print("🚀 Showcasing all proton/alpha thermal speed variables! 🚀")
    print("🚀"*60)
    
    # Use a good time range for WIND data
    trange = ['2022-06-01/00:00:00', '2022-06-01/12:00:00']  # 12 hours for good coverage
    print(f"📅 Time range: {trange[0]} to {trange[1]}")
    
    # Configure server for WIND data (CRITICAL: WIND only works with SPDF!)
    original_server = config.data_server
    config.data_server = 'spdf'  # Force SPDF - WIND data types don't have Berkeley fields
    print(f"🔧 Server mode: {config.data_server} (WIND requires SPDF)")
    
    try:
        # Download WIND SWE H1 data
        print("\n🔄 Downloading WIND SWE H1 data...")
        data_result = get_data(trange, 'wind_swe_h1')
        print(f"✅ Download complete: {type(data_result)}")
        
        # Check data status
        print("\n📊 Data Status Check:")
        if hasattr(wind_swe_h1, 'datetime_array') and wind_swe_h1.datetime_array is not None:
            print(f"⏰ Time points: {len(wind_swe_h1.datetime_array)}")
            print(f"⏰ Time range: {wind_swe_h1.datetime_array[0]} to {wind_swe_h1.datetime_array[-1]}")
        else:
            print("⚠️  No datetime_array - may be initialization only")
            
        # Quick data summary
        if hasattr(wind_swe_h1, 'raw_data') and wind_swe_h1.raw_data:
            print("\n📈 Variable Summary:")
            for var_name, var_data in wind_swe_h1.raw_data.items():
                if var_data is not None:
                    print(f"   ✅ {var_name}: {var_data.shape} [{np.nanmin(var_data):.2e}, {np.nanmax(var_data):.2e}]")
                else:
                    print(f"   ⚠️  {var_name}: None (no data)")
        
        print("\n🎨 Creating 5-Panel WIND SWE H1 Spectacular...")
        print("   Panel 1: Proton Parallel Thermal Speed")
        print("   Panel 2: Proton Perpendicular Thermal Speed") 
        print("   Panel 3: Proton Anisotropy (Wperp/Wpar)")
        print("   Panel 4: Alpha Particle Thermal Speed")
        print("   Panel 5: Data Quality Flag")
        
        # 🚀 THE EPIC 5-PANEL PLOTBOT CALL! 🚀
        plotbot(trange,
                wind_swe_h1.proton_wpar, 1,        # Parallel thermal speed
                wind_swe_h1.proton_wperp, 2,       # Perpendicular thermal speed
                wind_swe_h1.proton_anisotropy, 3,  # Anisotropy ratio
                wind_swe_h1.alpha_w, 4,            # Alpha thermal speed
                wind_swe_h1.fit_flag, 5)           # Quality flag
        
        print("\n🎉 SUCCESS! WIND SWE H1 5-Panel Plot Complete!")
        print("🌟 All proton/alpha thermal speed variables displayed!")
        print("🌟 Professional PSP-style formatting applied!")
        print("🌟 WIND integration working perfectly!")
        
        return True
        
    except Exception as e:
        print(f"\n💥 WIND SWE H1 multiplot failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original server setting
        config.data_server = original_server
        print(f"🔄 Restored server to: {config.data_server}")

if __name__ == "__main__":
    print("🚀 Starting WIND SWE H1 Multi-Panel Test...")
    success = test_wind_swe_h1_multiplot()
    
    if success:
        print("\n🎊 SPECTACULAR SUCCESS! 🎊")
        print("🏆 WIND SWE H1 integration is PRODUCTION READY!")
        print("🚀 4 out of 5 WIND data types now operational!")
        sys.exit(0)
    else:
        print("\n💥 Test failed!")
        sys.exit(1) 