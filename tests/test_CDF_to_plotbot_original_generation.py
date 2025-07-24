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
    
    # Provide CDF file paths - exactly as user described
    cdf_dir = Path(__file__).parent.parent / "docs" / "implementation_plans" / "CDF_Integration" / "KP_wavefiles"
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
    spectral_cache = cache_dir / f"{spectral_file.stem}_metadata.json"
    timeseries_cache = cache_dir / f"{timeseries_file.stem}_metadata.json"
    
    if spectral_cache.exists():
        print(f"✅ Spectral metadata cached: {spectral_cache}")
    else:
        print(f"⚠️  Spectral metadata cache not found: {spectral_cache}")
    
    if timeseries_cache.exists():
        print(f"✅ Time series metadata cached: {timeseries_cache}")
    else:
        print(f"⚠️  Time series metadata cache not found: {timeseries_cache}")
    
    # Run plotbot calls with variables - exactly as user described
    print(f"\n🎨 Testing plotbot calls with CDF variables...")
    
    try:
        # Get the generated class instances
        spectral_class = data_cubby.grab("psp_waves_spectral")
        timeseries_class = data_cubby.grab("psp_waves_timeseries")
        
        if spectral_class is None:
            print("❌ Could not retrieve spectral class from data_cubby")
            return False
            
        if timeseries_class is None:
            print("❌ Could not retrieve time series class from data_cubby")
            return False
        
        print("✅ Retrieved both classes from data_cubby")
        
        # CRITICAL: Load data into the classes first!
        print(f"\n📥 Loading CDF data into classes...")
        try:
            # Load data for both classes using get_data
            get_data(trange, spectral_class)
            get_data(trange, timeseries_class) 
            print("✅ Data loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load data: {e}")
            return False
        
        # Test plotbot calls with 5 variables (2 time series + 3 spectral) as user mentioned
        print(f"\n🚀 Making plotbot calls with variables...")
        
        # Time series variables (2)
        lh_var = timeseries_class.get_subclass('wavePower_LH')
        rh_var = timeseries_class.get_subclass('wavePower_RH')
        
        # Spectral variables (3) - using successfully tested variable names from examples
        ellipticity_var = spectral_class.get_subclass('ellipticity_b')      # Ellipticity (Bfield)
        b_power_var = spectral_class.get_subclass('B_power_para')           # Bfield Power Compressional  
        wave_normal_var = spectral_class.get_subclass('wave_normal_b')      # Wave Normal Angle (Bfield)
        

        # Check variables more explicitly (avoid potential plot_manager list context issues)
        missing_vars = []
        if lh_var is None:
            missing_vars.append("wavePower_LH")
        if rh_var is None:
            missing_vars.append("wavePower_RH") 
        if ellipticity_var is None:
            missing_vars.append("ellipticity_b")
        if b_power_var is None:
            missing_vars.append("B_power_para")
        if wave_normal_var is None:
            missing_vars.append("wave_normal_b")
        
        if missing_vars:
            print(f"❌ Variables not found: {missing_vars}")
            return False
        
        print("✅ All 5 variables found")
        
        # Make the plotbot call - exactly as user described: plotbot(trange, class.subclass1, 1, class.subclass2, 2...)
        print(f"\n🎯 Calling: plotbot(trange, lh_var, 1, rh_var, 2, ellipticity_var, 3, b_power_var, 4, wave_normal_var, 5)")
        
        plotbot(trange, 
                lh_var, 1,              # Time series LH
                rh_var, 2,              # Time series RH  
                ellipticity_var, 3,     # Spectral ellipticity
                b_power_var, 4,         # Spectral B power
                wave_normal_var, 5)     # Spectral wave normal
        
        print("🎉 SUCCESS! Plotbot call completed with all 5 CDF variables!")
        print("✅ CDF-to-plotbot integration fully functional")
        
        return True
        
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