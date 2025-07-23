#!/usr/bin/env python3
"""
Comprehensive test for CDF time boundary extraction and integration.
Tests the entire pipeline: metadata scanning → time extraction → file filtering.

This validates the critical bug fix for time boundary extraction and ensures
the time-based file filtering works with plotbot's native time format.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add plotbot to path (from tests directory)
sys.path.insert(0, '../plotbot')
sys.path.insert(0, '..')

# Handle imports more robustly
try:
    from plotbot.data_import_cdf import CDFMetadataScanner, filter_cdf_files_by_time, generate_file_pattern_from_cdf
    from plotbot.print_manager import print_manager
except ImportError:
    # Fallback for direct execution
    from data_import_cdf import CDFMetadataScanner, filter_cdf_files_by_time, generate_file_pattern_from_cdf
    import print_manager

def test_time_boundary_extraction():
    """Test that time boundaries are properly extracted in plotbot format."""
    
    print("🕒 Testing Time Boundary Extraction (Core Fix)")
    print("=" * 55)
    
    # Test files in our cdf_files directory
    test_files = [
        '../data/cdf_files/PSP_wavePower_2021-04-29_v1.3.cdf',
        '../data/cdf_files/PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf'
    ]
    
    scanner = CDFMetadataScanner()
    results = {}
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
            
        print(f"\n📁 Testing: {os.path.basename(file_path)}")
        
        # Force fresh scan to ensure we get the fixed time extraction
        metadata = scanner.scan_cdf_file(file_path, force_rescan=True)
        
        if metadata:
            print(f"   ✅ Metadata extracted successfully")
            print(f"   ⏰ Time variable: {metadata.time_variable}")
            print(f"   📅 Start: {metadata.start_time}")
            print(f"   📅 End: {metadata.end_time}")
            print(f"   ⏳ Coverage: {metadata.time_coverage_hours:.2f} hours")
            
            # Validate time format (plotbot native: YYYY/MM/DD HH:MM:SS.mmm)
            if metadata.start_time and metadata.end_time:
                start_format_ok = '/' in metadata.start_time and ' ' in metadata.start_time
                end_format_ok = '/' in metadata.end_time and ' ' in metadata.end_time
                
                if start_format_ok and end_format_ok:
                    print(f"   ✅ Time format: Plotbot-native (YYYY/MM/DD HH:MM:SS.mmm)")
                    results[file_path] = {
                        'success': True,
                        'start_time': metadata.start_time,
                        'end_time': metadata.end_time,
                        'coverage_hours': metadata.time_coverage_hours
                    }
                else:
                    print(f"   ❌ Time format: Not plotbot-native")
                    results[file_path] = {'success': False, 'error': 'Wrong time format'}
            else:
                print(f"   ❌ Time boundaries: NULL (extraction failed)")
                results[file_path] = {'success': False, 'error': 'NULL time boundaries'}
        else:
            print(f"   ❌ Metadata extraction failed")
            results[file_path] = {'success': False, 'error': 'Metadata extraction failed'}
    
    return results


def test_time_based_filtering():
    """Test time-based file filtering using the extracted boundaries."""
    
    print("\n\n🔍 Testing Time-Based File Filtering")
    print("=" * 45)
    
    # Test files
    test_files = [
        '../data/cdf_files/PSP_wavePower_2021-04-29_v1.3.cdf',
        '../data/cdf_files/PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf'
    ]
    
    # Define test time ranges
    test_scenarios = [
        {
            'name': 'Early morning (should match both - wavePower covers full day)',
            'start': datetime(2021, 4, 29, 6, 0, 0),
            'end': datetime(2021, 4, 29, 8, 0, 0),
            'expected_matches': ['PSP_wavePower_2021-04-29_v1.3.cdf', 'PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf']
        },
        {
            'name': 'Full day (should match both)',
            'start': datetime(2021, 4, 29, 0, 0, 0),
            'end': datetime(2021, 4, 30, 0, 0, 0),
            'expected_matches': ['PSP_wavePower_2021-04-29_v1.3.cdf', 'PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf']
        },
        {
            'name': 'Late evening (should match wavePower only)',
            'start': datetime(2021, 4, 29, 20, 0, 0),
            'end': datetime(2021, 4, 29, 23, 59, 59),
            'expected_matches': ['PSP_wavePower_2021-04-29_v1.3.cdf']
        },
        {
            'name': 'Wrong date (should match nothing)',
            'start': datetime(2021, 4, 28, 0, 0, 0),
            'end': datetime(2021, 4, 28, 23, 59, 59),
            'expected_matches': []
        }
    ]
    
    # Filter existing files
    existing_files = [f for f in test_files if os.path.exists(f)]
    print(f"Testing with {len(existing_files)} available files")
    
    results = {}
    
    for scenario in test_scenarios:
        print(f"\n🎯 Scenario: {scenario['name']}")
        print(f"   Time range: {scenario['start']} to {scenario['end']}")
        
        try:
            # Use our fixed time filtering function
            filtered_files = filter_cdf_files_by_time(
                existing_files, 
                scenario['start'], 
                scenario['end']
            )
            
            # Extract just filenames for comparison
            filtered_basenames = [os.path.basename(f) for f in filtered_files]
            expected_basenames = scenario['expected_matches']
            
            print(f"   📁 Found files: {filtered_basenames}")
            print(f"   📋 Expected: {expected_basenames}")
            
            # Check if results match expectations
            if set(filtered_basenames) == set(expected_basenames):
                print(f"   ✅ PASS: Filtering worked correctly")
                results[scenario['name']] = {'success': True, 'found': filtered_basenames}
            else:
                print(f"   ❌ FAIL: Unexpected filtering results")
                results[scenario['name']] = {
                    'success': False, 
                    'found': filtered_basenames, 
                    'expected': expected_basenames
                }
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results[scenario['name']] = {'success': False, 'error': str(e)}
    
    return results


def test_pattern_and_time_integration():
    """Test pattern detection + time filtering integration."""
    
    print("\n\n🔗 Testing Pattern Detection + Time Filtering Integration")
    print("=" * 65)
    
    # Test with our actual files
    base_file = '../data/cdf_files/PSP_wavePower_2021-04-29_v1.3.cdf'
    
    if not os.path.exists(base_file):
        print(f"❌ Base file not found: {base_file}")
        return {'success': False, 'error': 'Base file missing'}
    
    print(f"📁 Base file: {os.path.basename(base_file)}")
    
    try:
        # Step 1: Generate pattern
        pattern = generate_file_pattern_from_cdf(base_file, '../data/cdf_files')
        print(f"🎯 Generated pattern: {pattern}")
        
        # Step 2: Find matching files (would be multiple in real scenario)
        search_dir = '../data/cdf_files'
        import glob
        pattern_path = os.path.join(search_dir, pattern)
        matching_files = glob.glob(pattern_path)
        
        print(f"📁 Pattern matches: {len(matching_files)} files")
        for f in matching_files:
            print(f"   - {os.path.basename(f)}")
        
        # Step 3: Apply time filtering to matched files
        test_time_range = (
            datetime(2021, 4, 29, 0, 0, 0),
            datetime(2021, 4, 30, 0, 0, 0)
        )
        
        print(f"\n⏰ Applying time filter: {test_time_range[0]} to {test_time_range[1]}")
        filtered_files = filter_cdf_files_by_time(
            matching_files,
            test_time_range[0],
            test_time_range[1]
        )
        
        print(f"✅ Time-filtered results: {len(filtered_files)} files")
        for f in filtered_files:
            print(f"   - {os.path.basename(f)}")
        
        return {
            'success': True,
            'pattern': pattern,
            'pattern_matches': len(matching_files),
            'time_filtered': len(filtered_files)
        }
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return {'success': False, 'error': str(e)}


def run_comprehensive_test():
    """Run all time boundary integration tests."""
    
    print("🧪 CDF Time Boundary Integration Test Suite")
    print("=" * 65)
    print("Testing the complete pipeline: metadata → time extraction → filtering")
    print()
    
    # Test 1: Core time boundary extraction
    extraction_results = test_time_boundary_extraction()
    
    # Test 2: Time-based file filtering
    filtering_results = test_time_based_filtering()
    
    # Test 3: Pattern + time integration
    integration_results = test_pattern_and_time_integration()
    
    # Summary
    print("\n\n📊 TEST SUMMARY")
    print("=" * 35)
    
    extraction_success = sum(1 for r in extraction_results.values() if r.get('success', False))
    filtering_success = sum(1 for r in filtering_results.values() if r.get('success', False))
    integration_success = integration_results.get('success', False)
    
    print(f"⏰ Time Extraction: {extraction_success}/{len(extraction_results)} files")
    print(f"🔍 Time Filtering: {filtering_success}/{len(filtering_results)} scenarios")
    print(f"🔗 Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    overall_success = (
        extraction_success == len(extraction_results) and
        filtering_success == len(filtering_results) and
        integration_success
    )
    
    print(f"\n🏁 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 CDF time boundary extraction and integration is working perfectly!")
        print("   - Time boundaries extracted in plotbot-native format")
        print("   - Time-based file filtering operational")
        print("   - Pattern detection + time filtering integration successful")
    else:
        print("\n⚠️  Some tests failed. Check the detailed output above.")
    
    return overall_success


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 