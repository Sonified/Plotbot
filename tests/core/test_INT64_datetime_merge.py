import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
import time
import pytest

class Int64TimeArrayTests:
    """
    Comprehensive test suite for int64-based time arrays with focus on multi-component
    structures similar to those in mag_rtn_4sa_class.
    
    This test suite addresses the specific issue where 'all' is a list of component arrays
    (length 3) while datetime_array is a single array of timestamps (length N).
    """
    
    @staticmethod
    def generate_int64_time_array(size, start_time=None, step_ns=1_000_000_000):
        """Generate a synthetic int64 time array (nanoseconds since epoch)."""
        if start_time is None:
            start_time = datetime.now().replace(tzinfo=timezone.utc)
        elif isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
        # Convert to nanoseconds since epoch
        start_ns = int(start_time.timestamp() * 1_000_000_000)
        
        # Generate regularly spaced timestamps
        return np.arange(start_ns, start_ns + size * step_ns, step_ns, dtype=np.int64)
    
    @staticmethod
    def generate_components(time_array, num_components=3):
        """Generate simulated data components (br, bt, bn) for time series."""
        components = []
        for i in range(num_components):
            # Create data with some relation to time but different patterns
            phase = i * 0.5
            amplitude = 10.0 / (i + 1)
            component = np.sin(time_array / 1e12 + phase) * amplitude
            components.append(component)
        return components
    
    @staticmethod
    def create_data_structure(time_array, components):
        """Create a data structure similar to mag_rtn_4sa_class."""
        # Convert int64 time array to datetime64 for compatibility with Plotbot
        datetime_array = np.array(time_array, dtype='datetime64[ns]')
        
        # Create the problematic structure (list of arrays)
        raw_data = {
            'all': components.copy(),  # List of component arrays
        }
        
        # Add individual components with names
        component_names = ['br', 'bt', 'bn']
        for i, comp in enumerate(components):
            if i < len(component_names):
                raw_data[component_names[i]] = comp
        
        # Return a structure similar to actual class instances
        return {
            'datetime_array': datetime_array,
            'time': time_array,
            'raw_data': raw_data,
            'field': np.column_stack(components) if len(components) > 0 else None
        }
    
    @staticmethod
    def test_structure_verification():
        """Test proper verification of multi-component structures."""
        print("\n===== TEST 1: Structure Verification =====")
        
        # Generate test data
        size = 1000
        time_array = Int64TimeArrayTests.generate_int64_time_array(size)
        components = Int64TimeArrayTests.generate_components(time_array)
        struct = Int64TimeArrayTests.create_data_structure(time_array, components)
        
        # The problematic check from the original code
        all_length = len(struct['raw_data']['all'])
        dt_array_length = len(struct['datetime_array'])
        print(f"all length: {all_length}")  # Will be 3 (components)
        print(f"datetime_array length: {dt_array_length}")  # Will be 1000 (timestamps)
        
        # This is why the tests were failing:
        assert all_length != dt_array_length, "This inequality shows the problem!"
        
        # The correct way to verify the structure
        component_length = len(struct['raw_data']['all'][0])
        assert component_length == dt_array_length, "This is the correct check"
        
        print("✅ Successfully demonstrated the issue with length verification")
        
    @staticmethod
    def test_merge_with_components():
        """Test merging two datasets with components."""
        print("\n===== TEST 2: Merging with Components =====")
        
        # Create two time-separated datasets
        time1 = Int64TimeArrayTests.generate_int64_time_array(500, 
                                        datetime(2023, 1, 1))
        time2 = Int64TimeArrayTests.generate_int64_time_array(600, 
                                        datetime(2023, 1, 1, 1))  # 1 hour later
        
        components1 = Int64TimeArrayTests.generate_components(time1)
        components2 = Int64TimeArrayTests.generate_components(time2)
        
        struct1 = Int64TimeArrayTests.create_data_structure(time1, components1)
        struct2 = Int64TimeArrayTests.create_data_structure(time2, components2)
        
        # Perform merge (simplified version of what DataCubby._merge_arrays does)
        print("Merging datasets...")
        # 1. Concatenate time arrays
        combined_times = np.concatenate([struct1['time'], struct2['time']])
        
        # 2. Get sorting indices
        sort_indices = np.argsort(combined_times)
        sorted_times = combined_times[sort_indices]
        
        # 3. Create merged datetime array
        merged_dt = np.array(sorted_times, dtype='datetime64[ns]')
        
        # 4. Merge components
        merged_comps = []
        for i in range(len(components1)):
            # Concatenate corresponding components
            combined_comp = np.concatenate([struct1['raw_data']['all'][i], 
                                           struct2['raw_data']['all'][i]])
            # Apply same sorting
            sorted_comp = combined_comp[sort_indices]
            merged_comps.append(sorted_comp)
        
        # 5. Create the merged structure
        merged_data = {
            'datetime_array': merged_dt,
            'time': sorted_times,
            'raw_data': {
                'all': merged_comps,
                'br': merged_comps[0],
                'bt': merged_comps[1], 
                'bn': merged_comps[2]
            },
            'field': np.column_stack(merged_comps)
        }
        
        # Verify the merged structure
        print(f"Original lengths: {len(time1)}, {len(time2)}")
        print(f"Merged datetime array length: {len(merged_data['datetime_array'])}")
        print(f"First component length: {len(merged_data['raw_data']['all'][0])}")
        
        # Key verification
        assert len(merged_data['datetime_array']) == len(time1) + len(time2)
        assert len(merged_data['datetime_array']) == len(merged_data['raw_data']['all'][0])
        assert merged_data['field'].shape == (len(merged_data['datetime_array']), 3)
        
        print("✅ Successfully merged datasets with proper component handling")
    
    @staticmethod
    def test_corrected_verification_function():
        """Test a corrected verification function that handles the structure properly."""
        print("\n===== TEST 3: Corrected Verification Function =====")
        
        # Create test data
        time_array = Int64TimeArrayTests.generate_int64_time_array(1000)
        components = Int64TimeArrayTests.generate_components(time_array)
        struct = Int64TimeArrayTests.create_data_structure(time_array, components)
        
        # This is the correct verification function that should be used
        def verify_instance_state(instance):
            """Properly verify consistency between datetime_array and components."""
            if 'datetime_array' not in instance or instance['datetime_array'] is None:
                return False, "Missing datetime_array"
                
            if 'raw_data' not in instance or instance['raw_data'] is None or 'all' not in instance['raw_data']:
                return False, "Missing 'all' in raw_data"
                
            all_data = instance['raw_data']['all']
            
            # Check if 'all' is a list of components (like in mag_rtn_4sa)
            if isinstance(all_data, list):
                if not all_data:
                    return False, "'all' is empty list"
                    
                # Check first component length against datetime_array
                first_comp_len = len(all_data[0])
                dt_len = len(instance['datetime_array'])
                
                if first_comp_len != dt_len:
                    return False, f"Instance has inconsistencies: all[0] length ({first_comp_len}) != datetime_array length ({dt_len})"
                
                # Check all components have same length
                for i, comp in enumerate(all_data):
                    if len(comp) != dt_len:
                        return False, f"Component {i} length mismatch"
                
                return True, "Instance is consistent"
            else:
                # For direct array case
                all_len = len(all_data)
                dt_len = len(instance['datetime_array'])
                
                if all_len != dt_len:
                    return False, f"Instance has inconsistencies: all length ({all_len}) != datetime_array length ({dt_len})"
                
                return True, "Instance is consistent"
        
        # Test the function
        is_valid, message = verify_instance_state(struct)
        print(f"Verification result: {is_valid}")
        print(f"Message: {message}")
        
        # Create an invalid structure for testing
        bad_struct = struct.copy()
        bad_struct['datetime_array'] = bad_struct['datetime_array'][:-100]  # Truncate
        
        is_valid_bad, message_bad = verify_instance_state(bad_struct)
        print(f"Bad structure verification: {is_valid_bad}")
        print(f"Message: {message_bad}")
        
        assert is_valid, "Valid structure should pass verification"
        assert not is_valid_bad, "Invalid structure should fail verification"
        
        print("✅ Corrected verification function successfully detects consistency issues")
    
    @staticmethod
    def test_structure_repair():
        """Test repairing an inconsistent structure."""
        print("\n===== TEST 4: Structure Repair =====")
        
        # Create a valid structure
        time_array = Int64TimeArrayTests.generate_int64_time_array(1000)
        components = Int64TimeArrayTests.generate_components(time_array)
        struct = Int64TimeArrayTests.create_data_structure(time_array, components)
        
        # Create an inconsistent state (like what happens after multiple merges)
        bad_struct = struct.copy()
        # Truncate datetime_array but not components
        bad_struct['datetime_array'] = bad_struct['datetime_array'][:800]
        bad_struct['time'] = bad_struct['time'][:800]
        
        print("Before fix:")
        print(f"datetime_array length: {len(bad_struct['datetime_array'])}")
        print(f"first component length: {len(bad_struct['raw_data']['all'][0])}")
        
        # This is one way to fix the inconsistency - truncate components to match datetime
        fixed_struct = bad_struct.copy()
        dt_len = len(fixed_struct['datetime_array'])
        
        # Fix each component
        for i in range(len(fixed_struct['raw_data']['all'])):
            fixed_struct['raw_data']['all'][i] = fixed_struct['raw_data']['all'][i][:dt_len]
            
        # Also fix the named components
        for name in ['br', 'bt', 'bn']:
            if name in fixed_struct['raw_data']:
                fixed_struct['raw_data'][name] = fixed_struct['raw_data'][name][:dt_len]
                
        # Rebuild field array
        fixed_struct['field'] = np.column_stack([
            fixed_struct['raw_data']['br'],
            fixed_struct['raw_data']['bt'],
            fixed_struct['raw_data']['bn']
        ])
        
        print("\nAfter fix:")
        print(f"datetime_array length: {len(fixed_struct['datetime_array'])}")
        print(f"first component length: {len(fixed_struct['raw_data']['all'][0])}")
        print(f"field shape: {fixed_struct['field'].shape}")
        
        # Verify fix
        assert len(fixed_struct['datetime_array']) == len(fixed_struct['raw_data']['all'][0])
        assert fixed_struct['field'].shape[0] == len(fixed_struct['datetime_array'])
        
        print("✅ Successfully repaired inconsistent structure")
        
    @staticmethod
    def run_all_tests():
        """Run all tests in sequence."""
        print("\n===== INT64 TIME ARRAY TEST SUITE =====")
        print("This test suite addresses the structure inconsistency issues")
        
        Int64TimeArrayTests.test_structure_verification()
        Int64TimeArrayTests.test_merge_with_components()
        Int64TimeArrayTests.test_corrected_verification_function()
        Int64TimeArrayTests.test_structure_repair()
        
        print("\n✅ All tests completed!")
        
if __name__ == "__main__":
    Int64TimeArrayTests.run_all_tests()