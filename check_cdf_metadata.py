#!/usr/bin/env python3
"""
Check CDF metadata to see if the two files have different variable descriptions
"""

import cdflib
import sys
import os

def examine_cdf_metadata(file_path):
    """Examine CDF file metadata"""
    print(f"\n📁 File: {os.path.basename(file_path)}")
    print("=" * 60)
    
    try:
        cdf = cdflib.CDF(file_path)
        
        # Check wavePower_LH metadata
        if 'wavePower_LH' in cdf.cdf_info().zVariables:
            lh_attrs = cdf.varattsget('wavePower_LH')
            print("🔵 wavePower_LH attributes:")
            for attr, value in lh_attrs.items():
                if attr in ['CATDESC', 'FIELDNAM', 'LABLAXIS', 'VAR_TYPE']:
                    print(f"   {attr}: {value}")
        
        # Check wavePower_RH metadata  
        if 'wavePower_RH' in cdf.cdf_info().zVariables:
            rh_attrs = cdf.varattsget('wavePower_RH')
            print("\n🔴 wavePower_RH attributes:")
            for attr, value in rh_attrs.items():
                if attr in ['CATDESC', 'FIELDNAM', 'LABLAXIS', 'VAR_TYPE']:
                    print(f"   {attr}: {value}")
                    
        cdf.close()
        
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")

# Check both CDF files
file1 = "data/cdf_files/PSP_Waves/PSP_wavePower_2021-04-29_v1.3.cdf"
file2 = "data/cdf_files/PSP_Waves/PSP_wavePower_2023-06-22_v1.3.cdf"

print("🔍 CDF Metadata Comparison")
print("Checking if the two files have different variable descriptions...")

examine_cdf_metadata(file1)
examine_cdf_metadata(file2)

print("\n🧠 Analysis:")
print("If the CATDESC/FIELDNAM attributes are different between files,")
print("that would explain why the generated class has different styling!")
