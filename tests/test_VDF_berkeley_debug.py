#!/usr/bin/env python3
"""
VDF Berkeley Download Debug Test

Rebuilds the Berkeley download logic step by step with debug prints
to see exactly where it's failing.
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from datetime import timezone

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

def debug_berkeley_download():
    """Debug Berkeley download step by step."""
    
    print("🔍 BERKELEY DOWNLOAD DEBUG")
    print("=" * 50)
    
    # 1. Check the VDF configuration
    print("\n1. 📋 Checking VDF configuration...")
    from plotbot.data_classes.data_types import data_types
    
    if 'spi_sf00_8dx32ex8a' in data_types:
        config = data_types['spi_sf00_8dx32ex8a']
        print(f"✅ Found config for spi_sf00_8dx32ex8a")
        print(f"   URL: {config.get('url', 'NOT FOUND')}")
        print(f"   Password type: {config.get('password_type', 'NOT FOUND')}")
        print(f"   File pattern: {config.get('file_pattern', 'NOT FOUND')}")
        print(f"   Data sources: {config.get('data_sources', 'NOT FOUND')}")
    else:
        print("❌ spi_sf00_8dx32ex8a not found in data_types")
        return
    
    # 2. Test time parsing
    print("\n2. ⏰ Testing time parsing...")
    trange = ['2020-01-29/00:00', '2020-01-30/00:00']
    try:
        start_time = parse(trange[0]).replace(tzinfo=timezone.utc)
        end_time = parse(trange[1]).replace(tzinfo=timezone.utc)
        print(f"✅ Parsed start: {start_time}")
        print(f"✅ Parsed end: {end_time}")
    except Exception as e:
        print(f"❌ Time parsing failed: {e}")
        return
    
    # 3. Build URL
    print("\n3. 🌐 Building Berkeley URL...")
    base_url = config['url']
    year = start_time.year
    month = start_time.month
    full_url = f"{base_url}{year}/{month:02d}/"
    print(f"Target URL: {full_url}")
    
    # 4. Test server access (directory listing, NOT file download)
    print("\n4. 🔗 Testing server connection...")
    try:
        # First test without authentication - just get directory listing
        print("   Testing directory listing (not downloading files)...")
        print(f"   URL: {full_url}")
        response = requests.get(full_url)  # No timeout - let it take as long as needed
        print(f"   Response status: {response.status_code}")
        print(f"   Response size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("✅ Server accessible")
            
            # Check for our specific file
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a')
            
            target_file = "psp_swp_spi_sf00_L2_8Dx32Ex8A_20200129_v04.cdf"
            found_files = []
            
            print(f"\n   Looking for files matching VDF pattern...")
            for link in links:
                href = link.get('href', '')
                if 'psp_swp_spi_sf00_L2_8Dx32Ex8A' in href and '20200129' in href:
                    found_files.append(href)
                    print(f"   ✅ Found: {href}")
            
            if found_files:
                print(f"✅ Found {len(found_files)} matching files")
                
                # 4.5. TEST ACTUAL FILE DOWNLOAD
                print(f"\n   🚀 Testing actual file download...")
                target_file = found_files[0]
                file_url = full_url + target_file
                print(f"   File URL: {file_url}")
                
                # Create a test download directory
                import tempfile
                temp_dir = tempfile.mkdtemp()
                local_path = os.path.join(temp_dir, target_file)
                print(f"   Local path: {local_path}")
                
                print(f"   Starting download (this will take a while for 484MB file)...")
                try:
                    file_response = requests.get(file_url)
                    print(f"   Download response status: {file_response.status_code}")
                    
                    if file_response.status_code == 200:
                        with open(local_path, 'wb') as f:
                            f.write(file_response.content)
                        
                        file_size = os.path.getsize(local_path)
                        print(f"   ✅ Download successful! File size: {file_size / (1024*1024):.1f} MB")
                        
                        # Clean up
                        os.remove(local_path)
                        os.rmdir(temp_dir)
                        return found_files
                    else:
                        print(f"   ❌ Download failed: Status {file_response.status_code}")
                        return []
                except Exception as e:
                    print(f"   ❌ Download error: {e}")
                    return []
                
            else:
                print("❌ No matching files found")
                print("   Available files (first 10):")
                file_count = 0
                for link in links:
                    href = link.get('href', '')
                    if href.endswith('.cdf'):
                        print(f"     {href}")
                        file_count += 1
                        if file_count >= 10:
                            break
                
        elif response.status_code == 401:
            print("❌ Authentication required")
            print("   Need to test with SWEAP credentials")
            
            # 5. Test with authentication
            print("\n5. 🔐 Testing with authentication...")
            from plotbot.server_access import server_access
            
            # Set password type
            server_access.password_type = 'sweap'
            print(f"   Set password type to: {server_access.password_type}")
            
            # Test with session
            if hasattr(server_access, 'session'):
                print("   Testing with authenticated session...")
                auth_response = server_access.session.get(full_url)  # No timeout
                print(f"   Auth response status: {auth_response.status_code}")
                
                if auth_response.status_code == 200:
                    print("✅ Authentication successful")
                    # Parse files again
                    soup = BeautifulSoup(auth_response.content, 'html.parser')
                    links = soup.find_all('a')
                    
                    found_files = []
                    for link in links:
                        href = link.get('href', '')
                        if 'psp_swp_spi_sf00_L2_8Dx32Ex8A' in href and '20200129' in href:
                            found_files.append(href)
                            print(f"   ✅ Found: {href}")
                    
                    return found_files
                else:
                    print(f"❌ Authentication failed: {auth_response.status_code}")
            else:
                print("❌ No session available in server_access")
        else:
            print(f"❌ Server error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return []
    
    return []

def main():
    """Main test function."""
    print("VDF BERKELEY DOWNLOAD DEBUG")
    print("Rebuilding Berkeley download with step-by-step debugging")
    
    found_files = debug_berkeley_download()
    
    print(f"\n🎯 SUMMARY:")
    if found_files:
        print(f"✅ Berkeley download working - found {len(found_files)} files")
        print(f"Files: {found_files}")
    else:
        print(f"❌ Berkeley download failed")
        
    print(f"\n💡 Next steps:")
    print(f"   1. If auth failed: Check SWEAP credentials")
    print(f"   2. If files not found: Check date/pattern matching")  
    print(f"   3. If working: Fix plotbot Berkeley integration")

if __name__ == "__main__":
    main()