#!/usr/bin/env python3
"""
VDF Data Source Comparison Test

This test compares VDF data from Berkeley vs PySpedas sources to identify
differences in variable names, data structures, and formats that might
explain the plotbot integration issues.

Run with: conda run -n plotbot_env python tests/test_VDF_data_source_comparison.py
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import numpy as np
import cdflib
import pyspedas
from datetime import datetime

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subsection(title):
    """Print a formatted subsection header."""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def analyze_cdf_file(filepath, source_name):
    """Analyze a CDF file and extract comprehensive information."""
    print_subsection(f"{source_name} CDF Analysis")
    
    try:
        dat = cdflib.CDF(filepath)
        
        # Get basic file info
        print(f"📁 File: {os.path.basename(filepath)}")
        print(f"📏 File size: {os.path.getsize(filepath) / (1024*1024):.1f} MB")
        
        # Get all variables
        zvars = dat._get_varnames()[1]  # zVariables
        rvars = dat._get_varnames()[0]  # rVariables (usually metadata)
        
        print(f"\n📊 Variables Summary:")
        print(f"   zVariables (data): {len(zvars)}")
        print(f"   rVariables (metadata): {len(rvars)}")
        
        # List all zVariables
        print(f"\n📋 All zVariables ({len(zvars)} total):")
        for i, var in enumerate(zvars, 1):
            try:
                var_info = dat.varinq(var)
                data_type = var_info.get('Data_Type_Description', 'Unknown')
                print(f"   {i:2d}. {var:<20} ({data_type})")
            except:
                print(f"   {i:2d}. {var:<20} (Error reading info)")
        
        # Focus on key VDF variables
        vdf_vars = ['Epoch', 'TIME', 'THETA', 'PHI', 'ENERGY', 'EFLUX', 'ROTMAT_SC_INST']
        print(f"\n🎯 VDF Key Variables Analysis:")
        
        found_vars = {}
        for var in vdf_vars:
            if var in zvars:
                try:
                    data = dat.varget(var)
                    shape = data.shape if hasattr(data, 'shape') else 'scalar'
                    dtype = data.dtype if hasattr(data, 'dtype') else type(data).__name__
                    print(f"   ✅ {var:<15}: shape={shape}, dtype={dtype}")
                    found_vars[var] = {'shape': shape, 'dtype': dtype, 'data': data}
                    
                    # Special handling for time variables
                    if 'time' in var.lower() or var == 'Epoch':
                        print(f"      📅 Sample times: {data[:3] if hasattr(data, '__getitem__') else data}")
                        
                except Exception as e:
                    print(f"   ❌ {var:<15}: Error reading - {e}")
            else:
                print(f"   ❌ {var:<15}: NOT FOUND")
        
        # Look for time-related variables
        print(f"\n⏰ Time Variable Search:")
        time_vars = [v for v in zvars if any(keyword in v.lower() for keyword in ['time', 'epoch', 'tt2000', 'date'])]
        for var in time_vars:
            try:
                data = dat.varget(var)
                shape = data.shape if hasattr(data, 'shape') else 'scalar'
                print(f"   📅 {var:<15}: shape={shape}")
                if hasattr(data, '__getitem__') and len(data) > 0:
                    print(f"      Sample: {data[:3]}")
            except Exception as e:
                print(f"   ❌ {var:<15}: Error - {e}")
        
        # Look for similar variable names (case variations, etc.)
        print(f"\n🔍 Similar Variable Name Search:")
        target_vars = ['theta', 'phi', 'energy', 'eflux']
        for target in target_vars:
            matches = [v for v in zvars if target.lower() in v.lower()]
            if matches:
                print(f"   🎯 '{target}' matches: {matches}")
            else:
                print(f"   ❌ '{target}' matches: None")
        
        dat.close()
        return found_vars
        
    except Exception as e:
        print(f"❌ Error analyzing {source_name} file: {e}")
        return {}

def test_pyspedas_download():
    """Test direct PySpedas download."""
    print_section("PYSPEDAS DOWNLOAD TEST")
    
    trange = ['2020-01-29/00:00', '2020-01-30/00:00']
    
    try:
        print("🔄 Downloading via PySpedas...")
        files = pyspedas.psp.spi(
            trange=trange, 
            datatype='spi_sf00_8dx32ex8a', 
            level='l2',
            downloadonly=True,
            get_support_data=True,
            notplot=True,
            time_clip=True
        )
        
        if files and len(files) > 0:
            print(f"✅ PySpedas download successful: {len(files)} files")
            pyspedas_file = files[0]
            print(f"   📁 File: {pyspedas_file}")
            
            # Analyze the PySpedas file
            pyspedas_vars = analyze_cdf_file(pyspedas_file, "PySpedas")
            return pyspedas_file, pyspedas_vars
        else:
            print("❌ PySpedas download failed: No files returned")
            return None, {}
            
    except Exception as e:
        print(f"❌ PySpedas download error: {e}")
        return None, {}

def test_berkeley_download():
    """Test Berkeley download via plotbot system."""
    print_section("BERKELEY DOWNLOAD TEST")
    
    trange = ['2020-01-29/00:00', '2020-01-30/00:00']
    
    try:
        # Use plotbot's Berkeley download system
        from plotbot.data_download_berkeley import download_berkeley_data
        
        print("🔄 Downloading via Berkeley...")
        files = download_berkeley_data(trange, 'spi_sf00_8dx32ex8a')
        
        if files and len(files) > 0:
            print(f"✅ Berkeley download successful: {len(files)} files")
            berkeley_file = files[0]
            print(f"   📁 File: {berkeley_file}")
            
            # Analyze the Berkeley file
            berkeley_vars = analyze_cdf_file(berkeley_file, "Berkeley")
            return berkeley_file, berkeley_vars
        else:
            print("❌ Berkeley download failed: No files returned")
            return None, {}
            
    except Exception as e:
        print(f"❌ Berkeley download error: {e}")
        return None, {}

def compare_variable_data(pyspedas_vars, berkeley_vars):
    """Compare variable data between sources."""
    print_section("VARIABLE COMPARISON")
    
    if not pyspedas_vars and not berkeley_vars:
        print("❌ No data to compare - both downloads failed")
        return
    
    if not pyspedas_vars:
        print("❌ PySpedas data missing - cannot compare")
        return
        
    if not berkeley_vars:
        print("❌ Berkeley data missing - cannot compare")
        return
    
    # Compare common variables
    common_vars = set(pyspedas_vars.keys()) & set(berkeley_vars.keys())
    pyspedas_only = set(pyspedas_vars.keys()) - set(berkeley_vars.keys())
    berkeley_only = set(berkeley_vars.keys()) - set(pyspedas_vars.keys())
    
    print(f"📊 Variable Comparison Summary:")
    print(f"   Common variables: {len(common_vars)}")
    print(f"   PySpedas only: {len(pyspedas_only)}")
    print(f"   Berkeley only: {len(berkeley_only)}")
    
    if common_vars:
        print(f"\n✅ Common Variables:")
        for var in sorted(common_vars):
            p_info = pyspedas_vars[var]
            b_info = berkeley_vars[var]
            
            shape_match = p_info['shape'] == b_info['shape']
            dtype_match = p_info['dtype'] == b_info['dtype']
            
            status = "✅" if shape_match and dtype_match else "⚠️"
            print(f"   {status} {var}:")
            print(f"      PySpedas: shape={p_info['shape']}, dtype={p_info['dtype']}")
            print(f"      Berkeley: shape={b_info['shape']}, dtype={b_info['dtype']}")
            
            # Data comparison for small arrays
            try:
                if hasattr(p_info['data'], 'shape') and hasattr(b_info['data'], 'shape'):
                    if p_info['data'].shape == b_info['data'].shape and np.prod(p_info['data'].shape) < 100:
                        data_equal = np.allclose(p_info['data'], b_info['data'], equal_nan=True)
                        print(f"      Data equal: {data_equal}")
            except:
                print(f"      Data comparison: Unable to compare")
    
    if pyspedas_only:
        print(f"\n⚠️ PySpedas-only variables: {sorted(pyspedas_only)}")
        
    if berkeley_only:
        print(f"\n⚠️ Berkeley-only variables: {sorted(berkeley_only)}")

def test_plotbot_integration():
    """Test current plotbot integration."""
    print_section("PLOTBOT INTEGRATION TEST")
    
    try:
        from plotbot.get_data import get_data
        from plotbot import psp_span_vdf
        
        # Clear any existing state
        from plotbot import data_cubby, global_tracker
        global_tracker.calculated_ranges.clear()
        
        trange = ['2020-01-29/00:00', '2020-01-30/00:00']
        
        print("🔄 Testing plotbot get_data()...")
        result = get_data(trange, 'psp_span_vdf')
        
        print(f"📊 Plotbot Results:")
        print(f"   get_data() returned: {result}")
        print(f"   VDF instance: {psp_span_vdf}")
        print(f"   Has datetime_array: {hasattr(psp_span_vdf, 'datetime_array') and psp_span_vdf.datetime_array is not None}")
        
        if hasattr(psp_span_vdf, 'raw_data'):
            print(f"   Raw data keys: {list(psp_span_vdf.raw_data.keys())}")
            print(f"   Epoch data: {type(psp_span_vdf.raw_data.get('epoch'))}")
            print(f"   VDF calculated: {'vdf' in psp_span_vdf.raw_data and psp_span_vdf.raw_data['vdf'] is not None}")
        
    except Exception as e:
        print(f"❌ Plotbot integration error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    print_section("VDF DATA SOURCE COMPARISON DIAGNOSTIC")
    print("This test compares VDF data from Berkeley vs PySpedas sources")
    print("to identify differences that might explain plotbot integration issues.")
    
    # Test downloads
    pyspedas_file, pyspedas_vars = test_pyspedas_download()
    berkeley_file, berkeley_vars = test_berkeley_download()
    
    # Compare the data
    compare_variable_data(pyspedas_vars, berkeley_vars)
    
    # Test plotbot integration
    test_plotbot_integration()
    
    # Summary
    print_section("DIAGNOSTIC SUMMARY")
    
    if pyspedas_file and berkeley_file:
        print("✅ Both downloads successful - comparison complete")
        print(f"📁 PySpedas file: {os.path.basename(pyspedas_file)}")
        print(f"📁 Berkeley file: {os.path.basename(berkeley_file)}")
        
        if pyspedas_vars and berkeley_vars:
            common_vars = set(pyspedas_vars.keys()) & set(berkeley_vars.keys())
            print(f"🔍 Key findings: {len(common_vars)} common variables found")
            
            # Check specifically for time variables
            time_vars = [v for v in common_vars if 'time' in v.lower() or v == 'Epoch']
            if time_vars:
                print(f"⏰ Time variables available: {time_vars}")
            else:
                print("❌ No common time variables found - this may be the issue!")
        
    else:
        print("❌ One or both downloads failed - cannot complete comparison")
    
    print(f"\n📝 Next steps:")
    print(f"   1. Review variable name differences above")
    print(f"   2. Update plotbot VDF configuration if needed")
    print(f"   3. Test time variable handling specifically")
    print(f"   4. Update VDF_data_download_debugging.md with findings")

if __name__ == "__main__":
    main()