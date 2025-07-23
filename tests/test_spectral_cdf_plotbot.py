#!/usr/bin/env python3
"""
FOCUSED TEST: Spectral CDF data with plotbot() calls.

This test ONLY focuses on getting spectral CDF data working with actual plotbot() calls.
DO NOT TEST TIME SERIES DATA IN THIS FILE.
"""

import os
import sys
import numpy as np
import cdflib
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import plotbot
from plotbot.data_cubby import data_cubby

def test_spectral_cdf_plotbot():
    """
    Test spectral CDF data with REAL plotbot() calls.
    This focuses ONLY on the spectral class and spectral data.
    """
    print("🌈 TESTING SPECTRAL CDF WITH LATEX UNITS")
    print("=" * 60)
    
    # Disable debugging for clean output
    from plotbot.print_manager import print_manager
    print_manager.dependency_management_enabled = False
    print("🎨 TESTING LATEX UNIT FORMATTING")
    
    # Load spectral CDF file
    cdf_dir = Path(__file__).parent.parent / "docs/implementation_plans/CDF_Integration/KP_wavefiles"
    spectral_file = cdf_dir / "PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf"
    
    if not spectral_file.exists():
        print(f"❌ Spectral CDF file not found: {spectral_file}")
        return False
    
    print(f"📁 Testing with spectral file: {spectral_file.name}")
    
    # Get the registered spectral class
    if 'psp_spectral_waves' not in data_cubby.class_registry:
        print("❌ psp_spectral_waves not found in data_cubby registry")
        print(f"Available classes: {list(data_cubby.class_registry.keys())}")
        return False
    
    spectral_class = data_cubby.class_registry['psp_spectral_waves']
    print(f"✅ Found psp_spectral_waves class: {type(spectral_class)}")
    
    # Load REAL spectral data from CDF
    print("\n📖 Loading real spectral data...")
    with cdflib.CDF(str(spectral_file)) as cdf:
        # Load much more data for meaningful spectral plots
        times = cdf.varget('FFT_time', startrec=0, endrec=999)  # 1000 time points
        ellipticity = cdf.varget('ellipticity_b', startrec=0, endrec=999)
        b_power = cdf.varget('B_power_para', startrec=0, endrec=999)
        wave_normal = cdf.varget('wave_normal_b', startrec=0, endrec=999)
        
        print(f"  ⏰ FFT_time: {times.shape}")
        print(f"  🌈 ellipticity_b: {ellipticity.shape}")
        print(f"  🌈 B_power_para: {b_power.shape}")
        print(f"  🌈 wave_normal_b: {wave_normal.shape}")
        
        # Load the actual DEPEND_1 frequency variables from CDF metadata
        frequencies_1 = cdf.varget('Frequencies')  # For ellipticity_b (DEPEND_1: Frequencies)
        frequencies_3 = cdf.varget('Frequencies_3')  # For B_power_para (DEPEND_1: Frequencies_3) 
        
        print(f"  📈 Frequencies: {frequencies_1.shape}")
        print(f"  📈 Frequencies_3: {frequencies_3.shape}")
        
        # Create complete data dict using the actual DEPEND_1 variables
        data_dict = {
            'FFT_time': times,
            'Frequencies': frequencies_1,  # DEPEND_1 for ellipticity_b
            'Frequencies_3': frequencies_3,  # DEPEND_1 for B_power_para
            'ellipticity_b': ellipticity,
            'B_power_para': b_power,
            'wave_normal_b': wave_normal
        }
        
        # Add minimal data for other variables the class expects (but don't overwrite real data)
        for var in spectral_class.raw_data.keys():
            if var not in data_dict:
                # Load actual frequency variables if they exist, otherwise use minimal data
                if 'freq' in var.lower():
                    try:
                        actual_data = cdf.varget(var)
                        data_dict[var] = actual_data
                        print(f"  📈 Loaded {var}: {actual_data.shape}")
                    except:
                        data_dict[var] = np.array([0])  # Fallback for missing freq vars
                else:
                    data_dict[var] = np.array([0])  # Minimal data for non-frequency vars
        
        # Create ImportedData object
        class ImportedData:
            def __init__(self):
                self.times = times
                self.data = data_dict
        
        # Update the spectral class with real data
        print("\n🔄 Updating spectral class with real data...")
        spectral_class.update(ImportedData())
        
        print(f"✅ Updated class with {len(spectral_class.datetime_array)} time points")
        
        # Check that spectral variables exist and are accessible
        print("\n🔍 Checking spectral variables...")
        ellip_var = spectral_class.get_subclass('ellipticity_b')
        b_power_var = spectral_class.get_subclass('B_power_para')
        wave_normal_var = spectral_class.get_subclass('wave_normal_b')
        
        if ellip_var is None:
            print("❌ ellipticity_b variable not found")
            return False
        if b_power_var is None:
            print("❌ B_power_para variable not found")
            return False
        if wave_normal_var is None:
            print("❌ wave_normal_b variable not found")
            return False
        
        print("✅ All spectral variables accessible")
        
        # Check additional_data (this is where the issue likely is)
        print(f"🔍 ellipticity_b additional_data: {ellip_var.additional_data.shape if ellip_var.additional_data is not None else 'None'}")
        print(f"🔍 B_power_para additional_data: {b_power_var.additional_data.shape if b_power_var.additional_data is not None else 'None'}")
        
        # DEBUG TIME RANGES AND DATA
        print(f"\n🔍 DEBUGGING DATA BEFORE PLOTTING")
        print(f"📅 Class time range: {spectral_class.datetime_array[0]} to {spectral_class.datetime_array[-1]}")
        print(f"📊 Ellipticity data shape: {ellip_var.data.shape}")
        print(f"📊 Ellipticity data range: {np.nanmin(ellip_var.data):.2e} to {np.nanmax(ellip_var.data):.2e}")
        print(f"📊 Finite values: {np.sum(np.isfinite(ellip_var.data))} / {ellip_var.data.size}")
        
        # THE ACTUAL SPECTRAL PLOTBOT TEST
        print("\n🚀 TESTING SPECTRAL PLOTBOT CALLS")
        # Use the actual data time range (convert numpy datetime64 to string)
        import pandas as pd
        start_time = pd.Timestamp(spectral_class.datetime_array[0]).strftime('%Y-%m-%d/%H:%M:%S')
        end_time = pd.Timestamp(spectral_class.datetime_array[-1]).strftime('%Y-%m-%d/%H:%M:%S')
        trange = [start_time, end_time]
        print(f"📅 Using actual data trange: {trange}")
        
        try:
            print("🚀 plotbot(trange, spectral_class.ellipticity_b, 1)")
            plotbot.plotbot(trange, spectral_class.ellipticity_b, 1)
            print("🎉 SPECTRAL PLOTBOT CALL 1 SUCCESS!")
            
        except Exception as e:
            print(f"❌ SPECTRAL PLOTBOT CALL 1 FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        try:
            print("\n🚀 plotbot(trange, spectral_class.B_power_para, 1, spectral_class.wave_normal_b, 2)")
            plotbot.plotbot(trange, spectral_class.B_power_para, 1, spectral_class.wave_normal_b, 2)
            print("🎉 SPECTRAL PLOTBOT CALL 2 SUCCESS!")
            
        except Exception as e:
            print(f"❌ SPECTRAL PLOTBOT CALL 2 FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n🎉 ALL SPECTRAL PLOTBOT TESTS PASSED!")
        print("✅ Spectral CDF integration working with plotbot()")
        return True

if __name__ == "__main__":
    print("🎯 FOCUSED SPECTRAL CDF PLOTBOT TEST")
    success = test_spectral_cdf_plotbot()
    
    if success:
        print("\n🎉 SPECTRAL CDF PLOTBOT TEST: PASSED")
    else:
        print("\n❌ SPECTRAL CDF PLOTBOT TEST: FAILED")
        print("🔧 Fix the spectral class additional_data issue!") 