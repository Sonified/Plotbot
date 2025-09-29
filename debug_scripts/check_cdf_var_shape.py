#!/usr/bin/env python3
"""
Quick check to see what Dim_Sizes returns for wavePower variables
"""

from cdflib import CDF
import os

cdf_file_path = "/Users/robertalexander/GitHub/Plotbot/data/cdf_files/PSP_Waves/PSP_wavePower_2021-04-29_v1.3.cdf"

print(f"Opening: {cdf_file_path}")
print(f"File exists: {os.path.exists(cdf_file_path)}")

cdf = CDF(cdf_file_path)

print("\n" + "=" * 60)
print("CDF Variable Information")
print("=" * 60)

for var_name in ['epoch', 'wavePower_LH', 'wavePower_RH']:
    print(f"\n📊 Variable: {var_name}")
    try:
        var_info = cdf.varinq(var_name)
        print(f"   Dim_Sizes: {var_info.Dim_Sizes}")
        print(f"   len(Dim_Sizes): {len(var_info.Dim_Sizes)}")
        if len(var_info.Dim_Sizes) > 0:
            print(f"   Dim_Sizes[0]: {var_info.Dim_Sizes[0]}")
        
        # Try to get actual data shape
        data = cdf.varget(var_name)
        print(f"   Actual data shape: {data.shape}")
        print(f"   Data type: {data.dtype}")
        
        # Check the condition in the code
        var_shape = var_info.Dim_Sizes
        is_metadata = len(var_shape) == 0 or (len(var_shape) == 1 and var_shape[0] <= 1000)
        print(f"   Would be treated as metadata? {is_metadata}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

cdf.close()

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)
print("If wavePower_LH/RH are being treated as metadata variables,")
print("then Dim_Sizes must be returning something unexpected!")
