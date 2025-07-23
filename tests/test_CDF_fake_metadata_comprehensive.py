#!/usr/bin/env python3
"""
🧠 GENIUS-LEVEL CDF Time Filtering Algorithm Test

Uses comprehensive fake metadata to test the core time filtering algorithm
against 100 fake CDF files with 12 sophisticated test scenarios.

This tests the ALGORITHM LOGIC, not file I/O - perfect for validation!
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any
from collections import namedtuple

# Add plotbot to path (from tests directory)
sys.path.insert(0, '..')
sys.path.insert(0, '../plotbot')

# Create a mock CDFMetadata structure that matches our real one
MockCDFMetadata = namedtuple('MockCDFMetadata', [
    'file_path', 'start_time', 'end_time', 'time_coverage_hours'
])

class MockCDFMetadataScanner:
    """Mock scanner that returns fake metadata instead of reading real CDF files."""
    
    def __init__(self, fake_metadata_db: Dict[str, Dict]):
        """Initialize with fake metadata database."""
        self.fake_db = fake_metadata_db
        
    def scan_cdf_file(self, file_path: str, force_rescan: bool = False) -> MockCDFMetadata:
        """Return fake metadata for the given file path."""
        filename = os.path.basename(file_path)
        
        # Search through all groups to find this file
        for group_type in ['sequential_coverage_groups', 'sparse_coverage_groups']:
            for group in self.fake_db['test_scenarios'][group_type]['groups']:
                for file_info in group['files']:
                    if file_info['filename'] == filename:
                        return MockCDFMetadata(
                            file_path=file_path,
                            start_time=file_info['start_time'],
                            end_time=file_info['end_time'],
                            time_coverage_hours=file_info['coverage_hours']
                        )
        
        # File not found in fake database
        return None

def mock_filter_cdf_files_by_time(file_paths: List[str], start_time: datetime, end_time: datetime, scanner: MockCDFMetadataScanner) -> List[str]:
    """
    Mock version of filter_cdf_files_by_time that uses fake metadata.
    
    This tests the CORE ALGORITHM LOGIC for time overlap detection.
    """
    relevant_files = []
    
    print(f"    🔍 Filtering {len(file_paths)} files for time range:")
    print(f"        📅 Request: {start_time} to {end_time}")
    
    for file_path in file_paths:
        try:
            # Get fake metadata
            metadata = scanner.scan_cdf_file(file_path, force_rescan=False)
            
            if not metadata or not metadata.start_time or not metadata.end_time:
                # No time info, include to be safe
                relevant_files.append(file_path)
                print(f"        📄 {os.path.basename(file_path)}: No time info, including")
                continue
            
            # Parse time boundaries (they're already in plotbot format!)
            try:
                # Convert plotbot format to datetime for comparison
                from datetime import datetime
                file_start = datetime.strptime(metadata.start_time, '%Y/%m/%d %H:%M:%S.%f')
                file_end = datetime.strptime(metadata.end_time, '%Y/%m/%d %H:%M:%S.%f')
                
                # *** CORE ALGORITHM TEST ***
                # Check for overlap: file_start <= requested_end AND file_end >= requested_start
                has_overlap = file_start <= end_time and file_end >= start_time
                
                if has_overlap:
                    relevant_files.append(file_path)
                    overlap_hours = min(file_end, end_time) - max(file_start, start_time)
                    overlap_hours = overlap_hours.total_seconds() / 3600.0
                    print(f"        ✅ {os.path.basename(file_path)}: {overlap_hours:.2f}h overlap")
                else:
                    print(f"        ❌ {os.path.basename(file_path)}: No overlap")
                    
            except Exception as e:
                # If time parsing fails, include to be safe
                relevant_files.append(file_path)
                print(f"        ⚠️  {os.path.basename(file_path)}: Time parsing failed, including")
                
        except Exception as e:
            # If metadata reading fails, include to be safe
            relevant_files.append(file_path)
            print(f"        ❌ {os.path.basename(file_path)}: Metadata error, including")
    
    print(f"        🎯 Result: {len(relevant_files)}/{len(file_paths)} files match")
    return relevant_files

def load_fake_metadata() -> Dict:
    """Load the comprehensive fake metadata from JSON file."""
    metadata_file = '../data/cdf_files/TEST_CDF_METADATA/comprehensive_test_metadata.json'
    
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"Fake metadata file not found: {metadata_file}")
    
    with open(metadata_file, 'r') as f:
        return json.load(f)

def build_fake_file_list(fake_metadata: Dict) -> List[str]:
    """Build a list of all fake file paths from the metadata."""
    file_list = []
    
    # Add sequential coverage files
    for group in fake_metadata['test_scenarios']['sequential_coverage_groups']['groups']:
        for file_info in group['files']:
            # Create fake file paths
            file_path = f"fake_data/{group['group_id']}/{file_info['filename']}"
            file_list.append(file_path)
    
    # Add sparse coverage files
    for group in fake_metadata['test_scenarios']['sparse_coverage_groups']['groups']:
        for file_info in group['files']:
            file_path = f"fake_data/{group['group_id']}/{file_info['filename']}"
            file_list.append(file_path)
    
    return file_list

def run_comprehensive_algorithm_test():
    """Run the comprehensive algorithm test with fake metadata."""
    
    print("🧠 GENIUS-LEVEL CDF Time Filtering Algorithm Test")
    print("=" * 65)
    print("Testing core algorithm logic with 100 fake files + 12 scenarios")
    print()
    
    # Load fake metadata
    print("📋 Loading comprehensive fake metadata...")
    try:
        fake_metadata = load_fake_metadata()
        print(f"    ✅ Loaded metadata for {len(fake_metadata['test_scenarios']['sequential_coverage_groups']['groups']) * 10 + len(fake_metadata['test_scenarios']['sparse_coverage_groups']['groups']) * 2} fake files")
    except Exception as e:
        print(f"    ❌ Failed to load fake metadata: {e}")
        return False
    
    # Build fake file list
    print("\n📁 Building fake file database...")
    fake_files = build_fake_file_list(fake_metadata)
    print(f"    ✅ Generated {len(fake_files)} fake file paths")
    
    # Create mock scanner
    scanner = MockCDFMetadataScanner(fake_metadata)
    
    # Run test scenarios
    print(f"\n🧪 Running {len(fake_metadata['test_queries']['scenarios'])} Test Scenarios")
    print("=" * 55)
    
    test_results = {}
    
    for i, scenario in enumerate(fake_metadata['test_queries']['scenarios'], 1):
        print(f"\n🎯 Test {i}: {scenario['name']}")
        print(f"    📝 {scenario['description']}")
        
        try:
            # Parse query times
            query_start = datetime.strptime(scenario['query_start'], '%Y/%m/%d %H:%M:%S.%f')
            query_end = datetime.strptime(scenario['query_end'], '%Y/%m/%d %H:%M:%S.%f')
            
            # Run the core algorithm
            matching_files = mock_filter_cdf_files_by_time(fake_files, query_start, query_end, scanner)
            
            # Extract just filenames for comparison
            matching_basenames = [os.path.basename(f) for f in matching_files]
            expected_basenames = scenario['expected_matches']
            expected_count = scenario['expected_count']
            
            print(f"    📊 Results:")
            print(f"        Found: {len(matching_basenames)} files")
            print(f"        Expected: {expected_count} files")
            print(f"        Matches: {matching_basenames}")
            print(f"        Expected: {expected_basenames}")
            
            # Check results
            if len(matching_basenames) == expected_count and set(matching_basenames) == set(expected_basenames):
                print(f"    ✅ PASS: Algorithm correctly identified matching files")
                test_results[scenario['name']] = {'success': True, 'found': matching_basenames}
            else:
                print(f"    ❌ FAIL: Algorithm results don't match expectations")
                test_results[scenario['name']] = {
                    'success': False, 
                    'found': matching_basenames, 
                    'expected': expected_basenames,
                    'found_count': len(matching_basenames),
                    'expected_count': expected_count
                }
                
        except Exception as e:
            print(f"    ❌ ERROR: Test scenario failed with exception: {e}")
            test_results[scenario['name']] = {'success': False, 'error': str(e)}
    
    # Summary
    print(f"\n\n📊 ALGORITHM TEST SUMMARY")
    print("=" * 45)
    
    passed_tests = sum(1 for result in test_results.values() if result.get('success', False))
    total_tests = len(test_results)
    
    print(f"🎯 Overall Results: {passed_tests}/{total_tests} tests passed")
    print(f"📈 Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    # Detailed failure analysis
    failed_tests = [name for name, result in test_results.items() if not result.get('success', False)]
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for test_name in failed_tests:
            result = test_results[test_name]
            print(f"    • {test_name}")
            if 'error' in result:
                print(f"        Error: {result['error']}")
            else:
                print(f"        Found {result.get('found_count', 0)}, expected {result.get('expected_count', 0)}")
                print(f"        Extra files: {set(result.get('found', [])) - set(result.get('expected', []))}")
                print(f"        Missing files: {set(result.get('expected', [])) - set(result.get('found', []))}")
    
    overall_success = passed_tests == total_tests
    
    if overall_success:
        print(f"\n🎉 ALGORITHM VALIDATION: PERFECT SUCCESS!")
        print(f"    ✅ Core time overlap detection working flawlessly")
        print(f"    ✅ All edge cases handled correctly")
        print(f"    ✅ Gap detection working properly")
        print(f"    ✅ Overlap scenarios working correctly")
        print(f"    ✅ Boundary conditions handled properly")
    else:
        print(f"\n⚠️  ALGORITHM ISSUES DETECTED:")
        print(f"    Some test scenarios failed - review core logic")
    
    return overall_success

if __name__ == "__main__":
    success = run_comprehensive_algorithm_test()
    print(f"\n🏁 Exit Code: {0 if success else 1}")
    sys.exit(0 if success else 1) 