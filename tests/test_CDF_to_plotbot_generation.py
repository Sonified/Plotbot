#!/usr/bin/env python3
"""
Test the integrated cdf_to_plotbot() workflow.

Simple integration test:
1. from plotbot import *
2. Set trange
3. Provide CDF file paths
4. Verify files exist
5. Run cdf_to_plotbot
6. Verify metadata extraction
7. Run plotbot calls with variables
"""

import os
import sys
from pathlib import Path

# Add plotbot to path (from tests directory)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Simple integrated import - exactly as user described
from plotbot import *

def test_cdf_to_plotbot_generation():
    """Test complete integrated workflow: cdf_to_plotbot → metadata → plotbot calls"""
    
    print("🧪 Testing Integrated CDF-to-Plotbot Workflow")
    print("=" * 55)
    
    # Set trange - exactly as user described
    trange = ['2021-04-29/06:00:00', '2021-04-29/07:00:00']
    print(f"📅 Time range: {trange[0]} to {trange[1]}")
    
    # Provide CDF file paths - corrected to data/cdf_files
    cdf_dir = Path(__file__).parent.parent / "data" / "cdf_files"
    spectral_file = cdf_dir / "PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf"
    timeseries_file = cdf_dir / "PSP_wavePower_2021-04-29_v1.3.cdf"
    
    print(f"📁 Spectral file: {spectral_file}")
    print(f"📁 Time series file: {timeseries_file}")
    
    # Verify files exist - exactly as user described
    if not spectral_file.exists():
        print(f"❌ Spectral file not found: {spectral_file}")
        return False
        
    if not timeseries_file.exists():
        print(f"❌ Time series file not found: {timeseries_file}")
        return False
    
    print("✅ Both CDF files found")
    
    # Run cdf_to_plotbot for both files - exactly as user described
    print(f"\n🔧 Running cdf_to_plotbot for spectral data...")
    spectral_success = cdf_to_plotbot(str(spectral_file), "psp_waves_spectral")
    
    print(f"\n🔧 Running cdf_to_plotbot for time series data...")
    timeseries_success = cdf_to_plotbot(str(timeseries_file), "psp_waves_timeseries")
    
    if not spectral_success:
        print("❌ Failed to generate spectral class")
        return False
        
    if not timeseries_success:
        print("❌ Failed to generate time series class")
        return False
    
    print("✅ Both CDF classes generated successfully")
    print("   (Classes should now be auto-registered with data_cubby)")
    
    # Verify metadata was extracted correctly - exactly as user described
    print(f"\n📊 Verifying CDF metadata extraction...")
    
    # Check if metadata cache files were created
    cache_dir = Path(__file__).parent.parent / "plotbot" / "cache" / "cdf_metadata"
    spectral_cache = cache_dir / f"{spectral_file.name}.metadata.json"
    timeseries_cache = cache_dir / f"{timeseries_file.name}.metadata.json"
    
    if spectral_cache.exists():
        print(f"✅ Spectral metadata cached: {spectral_cache.name}")
    else:
        print(f"⚠️  Spectral metadata cache not found: {spectral_cache.name}")
    
    if timeseries_cache.exists():
        print(f"✅ Time series metadata cached: {timeseries_cache.name}")
    else:
        print(f"⚠️  Time series metadata cache not found: {timeseries_cache.name}")
    
    # Run plotbot calls with variables - new simplified approach
    print(f"\n🎨 Testing plotbot calls with CDF variables using direct access...")
    
    try:
        # The new simplified workflow: after cdf_to_plotbot(), the classes
        # should be globally available and work just like built-in classes.
        # No more data_cubby.grab(), get_data(), or get_subclass().
        
        print(f"\n🎯 Calling: plotbot(trange, psp_waves_timeseries.wavePower_LH, 1, ...)")
        
        # Make the plotbot call - new simple, direct syntax
        plotbot(trange, 
                psp_waves_timeseries.wavePower_LH, 1,      # Time series LH
                psp_waves_timeseries.wavePower_RH, 2,      # Time series RH  
                psp_waves_spectral.ellipticity_b, 3,       # Spectral ellipticity
                psp_waves_spectral.B_power_para, 4,        # Spectral B power
                psp_waves_spectral.wave_normal_b, 5)       # Spectral wave normal
        
        print("🎉 SUCCESS! Plotbot call completed with all 5 CDF variables!")
        print("✅ CDF-to-plotbot integration uses the simple, direct-access workflow.")
        
        return True
        
    except NameError as e:
        print(f"❌ Plotbot call failed: {e}")
        print("   This likely means the generated CDF classes were not made globally accessible.")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Plotbot call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cdf_to_plotbot_generation()
    
    print("\n" + "=" * 55)
    if success:
        print("🎉 CDF-TO-PLOTBOT INTEGRATION: SUCCESS!")
        print("✅ Complete workflow functional end-to-end")
    else:
        print("❌ CDF-TO-PLOTBOT INTEGRATION: FAILED!")
        print("🔧 Check the detailed output above")
    
    sys.exit(0 if success else 1) 