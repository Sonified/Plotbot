#!/usr/bin/env python3
"""
Test script for the smart CDF filename pattern detector.
Tests the pattern generation on various CDF naming conventions found in the data directory.
"""

import os
import sys
import re
from pathlib import Path

# Add plotbot to path (from tests directory)  
sys.path.insert(0, '..')
from plotbot.data_import_cdf import generate_file_pattern_from_cdf, _find_files_matching_pattern

def test_pattern_detection():
    """Test the smart pattern detector on various CDF file naming conventions."""
    
    print("🧪 Testing Smart CDF Pattern Detection\n")
    print("=" * 60)
    
    # Test cases found in our data directory
    test_cases = [
        # PSP Wave files (our original test cases)
        ("../data/cdf_files/PSP_Waves/PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf", "../data/cdf_files/PSP_Waves"),
        ("../data/cdf_files/PSP_Waves/PSP_wavePower_2021-04-29_v1.3.cdf", "../data/cdf_files/PSP_Waves"),
        
        # WIND master files (placeholder dates)
        ("../data/windwind_masters/wi_h5_swe_00000000_v01.cdf", "../data/windwind_masters"),
        ("../data/windwind_masters/wi_h2_mfi_00000000_v01.cdf", "../data/windwind_masters"),
        ("../data/windwind_masters/wi_pm_3dp_00000000_v01.cdf", "../data/windwind_masters"),
        
        # PSP DFB files (compact date format)
        ("../data/test_precise_dfb/dfb_dc_spec/dv12hg/2021/psp_fld_l2_dfb_dc_spec_dv12hg_20211125_v01.cdf", 
         "../data/test_precise_dfb/dfb_dc_spec/dv12hg/2021"),
        ("../data/test_precise_dfb/dfb_ac_spec/dv34hg/2021/psp_fld_l2_dfb_ac_spec_dv34hg_20211125_v01.cdf",
         "../data/test_precise_dfb/dfb_ac_spec/dv34hg/2021"),
         
                 # PSP QTN files (different version format)
        ("../data/psp/fields/l3/sqtn_rfs_v1v2/2022/psp_fld_l3_sqtn_rfs_v1v2_20220602_v2.0.cdf",
         "../data/psp/fields/l3/sqtn_rfs_v1v2/2022"),
        ("../data/psp/fields/l3/sqtn_rfs_v1v2/2023/psp_fld_l3_sqtn_rfs_v1v2_20230928_v2.0.cdf",
         "../data/psp/fields/l3/sqtn_rfs_v1v2/2023"),
         
                 # PSP MAG files (case variations)
        ("../data/psp/fields/l2/mag_rtn_4_per_cycle/2022/psp_fld_l2_mag_RTN_4_Sa_per_Cyc_20221211_v02.cdf",
         "../data/psp/fields/l2/mag_rtn_4_per_cycle/2022"),
        ("../data/psp/fields/l2/mag_rtn_4_per_cycle/2022/psp_fld_l2_mag_rtn_4_sa_per_cyc_20220601_v02.cdf",
         "../data/psp/fields/l2/mag_rtn_4_per_cycle/2022"),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, (file_path, search_dir) in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {os.path.basename(file_path)}")
        print(f"   Directory: {search_dir}")
        
        if not os.path.exists(file_path):
            print(f"   ❌ File not found: {file_path}")
            continue
            
        try:
            # Generate pattern
            pattern = generate_file_pattern_from_cdf(file_path, search_dir)
            print(f"   🎯 Generated Pattern: {pattern}")
            
            # Test pattern by finding matching files
            if search_dir and os.path.exists(search_dir):
                matching_files = _find_files_matching_pattern(pattern, search_dir)
                matching_basenames = [os.path.basename(f) for f in matching_files]
                
                print(f"   📁 Files found: {len(matching_files)}")
                if matching_files:
                    print(f"   📋 Matches: {', '.join(matching_basenames[:3])}" + 
                          (f" ... (+{len(matching_files)-3} more)" if len(matching_files) > 3 else ""))
                    success_count += 1
                else:
                    print(f"   ⚠️  No matches found (pattern may be too specific)")
            else:
                print(f"   ⚠️  Search directory not found: {search_dir}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Pattern Detection Summary:")
    print(f"   ✅ Successful: {success_count}/{total_count}")
    print(f"   🎯 Success Rate: {success_count/total_count*100:.1f}%")
    
    return success_count == total_count


def test_edge_cases():
    """Test edge cases and unusual naming patterns."""
    
    print("\n\n🧪 Testing Edge Cases\n")
    print("=" * 40)
    
    edge_cases = [
        # Custom/unusual names
        "custom_experiment_results.cdf",
        "my_data_file_001.cdf", 
        "final_analysis_v2.cdf",
        "data_20241225_FINAL.cdf",
        "test.cdf",
        "PSP_COMPLEX_data_2021-12-25_1430_UTC_v3.2.1_FINAL.cdf"
    ]
    
    for case in edge_cases:
        print(f"\n🔍 Edge Case: {case}")
        try:
            pattern = generate_file_pattern_from_cdf(case, search_directory=None)
            print(f"   🎯 Pattern: {pattern}")
        except Exception as e:
            print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    print("🧪 CDF Pattern Detection Test Suite")
    print("=" * 60)
    
    # Test on real files
    success = test_pattern_detection()
    
    # Test edge cases  
    test_edge_cases()
    
    print(f"\n🏁 Overall Result: {'✅ PASSED' if success else '❌ FAILED'}") 