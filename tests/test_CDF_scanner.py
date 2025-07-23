"""
Test the new CDF metadata scanner functionality.

This test validates the CDFMetadataScanner class against Jaye's wave analysis files
to ensure proper metadata extraction and caching.
"""

import os
import sys
# Add project root to path (from tests directory)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plotbot.data_import_cdf import CDFMetadataScanner, scan_cdf_directory, create_dynamic_cdf_class

def test_cdf_scanner():
    """Test CDF metadata scanning functionality."""
    print("🔍 Testing CDF Metadata Scanner")
    print("=" * 60)
    
    # Test data paths
    test_dir = "docs/implementation_plans/CDF_Integration/KP_wavefiles"
    wave_analysis_file = os.path.join(test_dir, "PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf")
    wave_power_file = os.path.join(test_dir, "PSP_wavePower_2021-04-29_v1.3.cdf")
    
    # Test 1: Scan individual files
    print("\n📊 Test 1: Individual File Scanning")
    scanner = CDFMetadataScanner()
    
    # Scan the spectral file
    print(f"\nScanning spectral file: {os.path.basename(wave_analysis_file)}")
    spectral_metadata = scanner.scan_cdf_file(wave_analysis_file)
    
    if spectral_metadata:
        print(f"  ✅ Found {spectral_metadata.variable_count} variables")
        print(f"  ⏰ Time variable: {spectral_metadata.time_variable}")
        print(f"  📊 Frequency variable: {spectral_metadata.frequency_variable}")
        
        print(f"\n  📋 Variables discovered:")
        for var in spectral_metadata.variables[:5]:  # Show first 5
            print(f"    - {var.name}: {var.plot_type} ({var.shape})")
        if len(spectral_metadata.variables) > 5:
            print(f"    ... and {len(spectral_metadata.variables) - 5} more")
    else:
        print("  ❌ Failed to scan spectral file")
    
    # Scan the time series file
    print(f"\nScanning time series file: {os.path.basename(wave_power_file)}")
    timeseries_metadata = scanner.scan_cdf_file(wave_power_file)
    
    if timeseries_metadata:
        print(f"  ✅ Found {timeseries_metadata.variable_count} variables")
        print(f"  ⏰ Time variable: {timeseries_metadata.time_variable}")
        print(f"  📊 Frequency variable: {timeseries_metadata.frequency_variable}")
        
        print(f"\n  📋 Variables discovered:")
        for var in timeseries_metadata.variables:
            print(f"    - {var.name}: {var.plot_type} ({var.shape})")
    else:
        print("  ❌ Failed to scan time series file")
    
    # Test 2: Directory scanning
    print(f"\n📁 Test 2: Directory Scanning")
    metadata_dict = scan_cdf_directory(test_dir)
    
    if metadata_dict:
        print(f"  ✅ Successfully scanned {len(metadata_dict)} files")
        for file_path, metadata in metadata_dict.items():
            print(f"    - {os.path.basename(file_path)}: {metadata.variable_count} variables")
    else:
        print("  ❌ No files found or scan failed")
    
    # Test 3: Dynamic class generation
    print(f"\n🏗️ Test 3: Dynamic Class Generation")
    if spectral_metadata:
        print(f"Generating class for spectral data...")
        class_code = create_dynamic_cdf_class(spectral_metadata, "WaveAnalysisVariables")
        
        # Save the generated class to a file for inspection
        output_file = "test_generated_wave_class.py"
        with open(output_file, 'w') as f:
            f.write(class_code)
        
        print(f"  ✅ Generated class saved to: {output_file}")
        print(f"  📝 Class contains {spectral_metadata.variable_count} variable definitions")
        
        # Show a sample of the generated code
        lines = class_code.split('\n')
        print(f"\n  📄 Sample of generated code:")
        for i, line in enumerate(lines[:15]):
            print(f"    {i+1:2d}: {line}")
        if len(lines) > 15:
            print(f"    ... and {len(lines) - 15} more lines")
    
    # Test 4: Cache functionality
    print(f"\n💾 Test 4: Cache Functionality")
    if spectral_metadata:
        print(f"Testing cache with spectral file...")
        
        # Scan again to test cache loading
        cached_metadata = scanner.scan_cdf_file(wave_analysis_file)
        
        if cached_metadata:
            print(f"  ✅ Cache loaded successfully")
            print(f"  📊 Cached variables: {cached_metadata.variable_count}")
            print(f"  🔄 Same as original: {cached_metadata.variable_count == spectral_metadata.variable_count}")
        else:
            print(f"  ❌ Cache loading failed")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 CDF Scanner Test Complete!")
    
    return spectral_metadata, timeseries_metadata

if __name__ == "__main__":
    spectral_meta, timeseries_meta = test_cdf_scanner() 