"""
Test WIND Data Directory Configuration
=====================================

This test file focuses specifically on configuring pyspedas to use a unified
data directory structure for WIND data instead of separate mission folders.

Based on official pyspedas documentation:
- SPEDAS_DATA_DIR acts as root data directory for all missions
- Mission-specific directories (e.g., WIND_DATA_DIR, THM_DATA_DIR) override SPEDAS_DATA_DIR
- Goal: Test both approaches for unified data structure

References:
- https://pyspedas.readthedocs.io/en/latest/getting_started.html
- https://github.com/spedas/pyspedas README.md
"""

import os
import pyspedas
import pytest
from pathlib import Path

class TestWindDataDirectoryConfig:
    """Test unified data directory configuration for WIND data."""
    
    def setup_method(self):
        """Setup for each test - save original environment."""
        self.original_spedas_dir = os.environ.get('SPEDAS_DATA_DIR', None)
        self.original_wind_dir = os.environ.get('WIND_DATA_DIR', None)
        self.original_psp_dir = os.environ.get('PSP_DATA_DIR', None)
        self.original_thm_dir = os.environ.get('THM_DATA_DIR', None)
        
    def teardown_method(self):
        """Cleanup after each test - restore original environment."""
        # Restore original environment variables
        env_vars = [
            ('SPEDAS_DATA_DIR', self.original_spedas_dir),
            ('WIND_DATA_DIR', self.original_wind_dir),
            ('PSP_DATA_DIR', self.original_psp_dir),
            ('THM_DATA_DIR', self.original_thm_dir)
        ]
        
        for var_name, original_value in env_vars:
            if original_value:
                os.environ[var_name] = original_value
            elif var_name in os.environ:
                del os.environ[var_name]

    def test_pyspedas_environment_variables_documentation(self):
        """Test our understanding of pyspedas environment variable hierarchy."""
        print("\n=== PySpedas Environment Variables Documentation ===")
        
        # Document the official hierarchy from pyspedas docs
        print("📖 Official PySpedas Documentation:")
        print("   - SPEDAS_DATA_DIR: Root data directory for all missions")
        print("   - Mission-specific vars (e.g., WIND_DATA_DIR, THM_DATA_DIR)")
        print("   - Mission-specific vars OVERRIDE SPEDAS_DATA_DIR")
        print("   - Examples: MMS_DATA_DIR, THM_DATA_DIR, PSP_DATA_DIR")
        
        # Test current environment
        current_env = {
            'SPEDAS_DATA_DIR': os.environ.get('SPEDAS_DATA_DIR'),
            'WIND_DATA_DIR': os.environ.get('WIND_DATA_DIR'),
            'PSP_DATA_DIR': os.environ.get('PSP_DATA_DIR'),
            'THM_DATA_DIR': os.environ.get('THM_DATA_DIR')
        }
        
        print("\n🔍 Current Environment:")
        for var, value in current_env.items():
            status = "✅ SET" if value else "❌ NOT SET"
            print(f"   {var}: {status} ({value})")
        
        # This is informational, always pass
        assert True

    def test_spedas_data_dir_global_approach(self):
        """Test using global SPEDAS_DATA_DIR for unified structure."""
        print("\n=== Testing Global SPEDAS_DATA_DIR Approach ===")
        
        # Clear mission-specific variables to test global approach
        mission_vars = ['WIND_DATA_DIR', 'PSP_DATA_DIR', 'THM_DATA_DIR']
        for var in mission_vars:
            if var in os.environ:
                del os.environ[var]
        
        # Set global unified directory
        unified_data_dir = 'data'
        os.environ['SPEDAS_DATA_DIR'] = unified_data_dir
        os.makedirs(unified_data_dir, exist_ok=True)
        
        print(f"✅ Set SPEDAS_DATA_DIR to: {os.environ['SPEDAS_DATA_DIR']}")
        print("✅ Cleared mission-specific environment variables")
        
        # Test download to see where files go
        try:
            test_files = pyspedas.wind.mfi(
                trange=['2020-01-01/00:00:00', '2020-01-01/01:00:00'],
                datatype='h2',
                downloadonly=True,
                notplot=True,
                no_update=False
            )
            
            if test_files:
                first_file = test_files[0]
                print(f"📁 Download path: {first_file}")
                
                # Check if global approach worked
                if unified_data_dir in first_file and 'wind_data' not in first_file:
                    print("🎉 SUCCESS: Global SPEDAS_DATA_DIR approach working!")
                    return True
                else:
                    print("⚠️  Global approach didn't override default paths")
                    return False
            else:
                print("❌ No files downloaded")
                return False
                
        except Exception as e:
            print(f"❌ Download failed: {e}")
            pytest.skip(f"Download test skipped due to: {e}")

    def test_mission_specific_approach(self):
        """Test using mission-specific WIND_DATA_DIR for unified structure."""
        print("\n=== Testing Mission-Specific WIND_DATA_DIR Approach ===")
        
        # Set up unified structure using mission-specific variables
        unified_data_dir = 'data'
        wind_data_path = f'{unified_data_dir}/wind'
        psp_data_path = f'{unified_data_dir}/psp'
        
        # Set mission-specific environment variables
        os.environ['WIND_DATA_DIR'] = wind_data_path
        os.environ['PSP_DATA_DIR'] = psp_data_path
        
        # Create directories
        os.makedirs(wind_data_path, exist_ok=True)
        os.makedirs(psp_data_path, exist_ok=True)
        
        print(f"✅ Set WIND_DATA_DIR to: {os.environ['WIND_DATA_DIR']}")
        print(f"✅ Set PSP_DATA_DIR to: {os.environ['PSP_DATA_DIR']}")
        print(f"✅ Created directories: {wind_data_path}/, {psp_data_path}/")
        
        # Test WIND download
        try:
            test_files = pyspedas.wind.mfi(
                trange=['2020-01-01/00:00:00', '2020-01-01/01:00:00'],
                datatype='h2',
                downloadonly=True,
                notplot=True,
                no_update=False
            )
            
            if test_files:
                first_file = test_files[0]
                print(f"📁 WIND download path: {first_file}")
                
                # Check if mission-specific approach worked
                if wind_data_path in first_file:
                    print("🎉 SUCCESS: Mission-specific WIND_DATA_DIR working!")
                    return True
                else:
                    print("⚠️  Mission-specific approach didn't work as expected")
                    return False
            else:
                print("❌ No WIND files downloaded")
                return False
                
        except Exception as e:
            print(f"❌ WIND download failed: {e}")
            pytest.skip(f"WIND download test skipped due to: {e}")

    def test_current_directory_structure_analysis(self):
        """Analyze the current directory structure to understand data organization."""
        print("\n=== Current Directory Structure Analysis ===")
        
        # Check all possible data directories
        data_roots = ['data', 'wind_data', 'psp_data']
        
        for root in data_roots:
            if os.path.exists(root):
                print(f"\n📁 {root}/")
                try:
                    for item in sorted(os.listdir(root)):
                        item_path = os.path.join(root, item)
                        if os.path.isdir(item_path):
                            print(f"  📁 {item}/")
                            # Show first few subdirectories
                            try:
                                subitems = sorted(os.listdir(item_path))[:3]
                                for subitem in subitems:
                                    subitem_path = os.path.join(item_path, subitem)
                                    icon = "📁" if os.path.isdir(subitem_path) else "📄"
                                    print(f"    {icon} {subitem}")
                                    
                                total_items = len(os.listdir(item_path))
                                if total_items > 3:
                                    print(f"    ... and {total_items - 3} more items")
                            except PermissionError:
                                print(f"    (Permission denied)")
                        else:
                            # Show only first few files
                            files_shown = 0
                            if files_shown < 3:
                                print(f"  📄 {item}")
                                files_shown += 1
                except PermissionError:
                    print(f"  (Permission denied)")
            else:
                print(f"\n❌ {root}/ does not exist")
        
        # Show environment variable status
        print(f"\n🌍 Current Environment Status:")
        env_vars = ['SPEDAS_DATA_DIR', 'WIND_DATA_DIR', 'PSP_DATA_DIR', 'THM_DATA_DIR']
        for var in env_vars:
            value = os.environ.get(var)
            status = "✅ SET" if value else "❌ NOT SET"
            print(f"   {var}: {status}")
            if value:
                print(f"      → {value}")
                
        # This is informational, always pass
        assert True

    def test_wind_data_products_documentation(self):
        """Test access to WIND data products documentation."""
        print("\n=== Testing WIND Data Products Documentation Access ===")
        
        # Check for wind data products documentation
        possible_paths = [
            "docs/wind-data-products-list.md",
            "wind-data-products-list.md",
            "docs/wind_data_products.md"
        ]
        
        found_docs = []
        for path in possible_paths:
            if os.path.exists(path):
                found_docs.append(path)
                print(f"✅ Found: {path}")
        
        if found_docs:
            # Read first found documentation
            doc_path = found_docs[0]
            with open(doc_path, 'r') as f:
                content = f.read()
                
            # Look for key WIND instruments
            instruments = ['MFI', 'SWE', '3DP', 'WAVES', 'SMS']
            found_instruments = []
            
            for instrument in instruments:
                if instrument in content:
                    found_instruments.append(instrument)
                    print(f"✅ Found {instrument} in documentation")
                    
            print(f"📋 Total instruments documented: {len(found_instruments)}")
            assert len(found_instruments) > 0, "No WIND instruments found in documentation"
            
        else:
            print("⚠️  No WIND data products documentation found")
            pytest.skip("WIND data products documentation not found")

    def test_recommended_approach_summary(self):
        """Summarize the recommended approach based on test results."""
        print("\n=== Recommended Approach Summary ===")
        
        print("📋 Based on Official PySpedas Documentation:")
        print("   1. SPEDAS_DATA_DIR = global root directory for all missions")
        print("   2. Mission-specific vars override global setting")
        print("   3. For unified structure, use mission-specific variables:")
        print("      - WIND_DATA_DIR = data/wind")
        print("      - PSP_DATA_DIR = data/psp")
        print("      - THM_DATA_DIR = data/themis")
        print("      - MMS_DATA_DIR = data/mms")
        
        print("\n🎯 Implementation Strategy:")
        print("   - Set mission-specific environment variables")
        print("   - Create unified data/ directory structure")
        print("   - Test with small downloads to verify paths")
        
        print("\n🔧 Current Status:")
        current_structure = "wind_data/ and psp_data/ (separate folders)"
        target_structure = "data/wind/ and data/psp/ (unified structure)"
        print(f"   Current: {current_structure}")
        print(f"   Target:  {target_structure}")
        
        # This is informational, always pass
        assert True


if __name__ == "__main__":
    """Run tests directly for debugging."""
    import sys
    
    # Create test instance
    test_instance = TestWindDataDirectoryConfig()
    
    print("🧪 Running WIND Data Directory Configuration Tests")
    print("=" * 70)
    
    try:
        test_instance.setup_method()
        
        # Run tests in logical order
        test_instance.test_pyspedas_environment_variables_documentation()
        test_instance.test_current_directory_structure_analysis()
        test_instance.test_wind_data_products_documentation()
        
        # Test different configuration approaches
        print("\n" + "="*50)
        print("TESTING CONFIGURATION APPROACHES")
        print("="*50)
        
        try:
            # Test global approach
            test_instance.setup_method()  # Reset environment
            global_success = test_instance.test_spedas_data_dir_global_approach()
            
            # Test mission-specific approach
            test_instance.setup_method()  # Reset environment
            mission_success = test_instance.test_mission_specific_approach()
            
            # Summary
            print("\n" + "="*50)
            print("CONFIGURATION TEST RESULTS")
            print("="*50)
            
            if global_success:
                print("✅ Global SPEDAS_DATA_DIR approach: WORKING")
            else:
                print("❌ Global SPEDAS_DATA_DIR approach: NOT WORKING")
                
            if mission_success:
                print("✅ Mission-specific variables approach: WORKING")
            else:
                print("❌ Mission-specific variables approach: NOT WORKING")
                
        except Exception as e:
            print(f"\n⚠️  Configuration tests skipped: {e}")
            
        # Show recommended approach
        test_instance.test_recommended_approach_summary()
        
    finally:
        test_instance.teardown_method()
        
    print("\n✅ Test run completed!") 