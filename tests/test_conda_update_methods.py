#!/usr/bin/env python3
"""
Test script to evaluate different methods for checking conda updates from Anaconda servers.
This will help optimize the installer scripts by finding the fastest approach.

Run with: python tests/test_conda_update_methods.py
Or with conda environment: conda run -n plotbot_anaconda python tests/test_conda_update_methods.py
"""

import subprocess
import time
import json
import requests
import sys
from typing import Dict, Tuple, Optional
import re

def time_command(command: str, shell: bool = True, timeout: int = 30) -> Tuple[float, bool, str]:
    """
    Time a command and return duration, success status, and output.
    
    Args:
        command: Command to run
        shell: Whether to run in shell
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (duration_seconds, success, output)
    """
    start_time = time.time()
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        duration = time.time() - start_time
        success = result.returncode == 0
        output = result.stdout.strip() if success else result.stderr.strip()
        return duration, success, output
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return duration, False, f"TIMEOUT after {timeout}s"
    except Exception as e:
        duration = time.time() - start_time
        return duration, False, f"ERROR: {str(e)}"

def method_1_conda_search_full() -> Tuple[float, bool, str]:
    """Method 1: Full conda search (current slow method)"""
    print("  Testing: conda search conda")
    duration, success, output = time_command("conda search conda | tail -1")
    if success and output:
        version = output.split()[1] if len(output.split()) > 1 else "unknown"
        return duration, success, f"Latest version: {version}"
    return duration, success, output

def method_2_conda_search_limited() -> Tuple[float, bool, str]:
    """Method 2: Conda search with head to limit results"""
    print("  Testing: conda search conda | head -10")
    duration, success, output = time_command("conda search conda | head -10 | tail -1")
    if success and output:
        version = output.split()[1] if len(output.split()) > 1 else "unknown"
        return duration, success, f"Latest version: {version}"
    return duration, success, output

def method_3_conda_update_dry_run() -> Tuple[float, bool, str]:
    """Method 3: Conda update dry run"""
    print("  Testing: conda update --dry-run")
    duration, success, output = time_command("conda update -n base conda --dry-run")
    if success:
        # Look for update information in output
        if "conda" in output and "->" in output:
            return duration, success, "Update available (found in dry-run)"
        else:
            return duration, success, "No updates available"
    return duration, success, output

def method_4_conda_list_current() -> Tuple[float, bool, str]:
    """Method 4: Get current conda version only"""
    print("  Testing: conda list conda")
    duration, success, output = time_command("conda list conda")
    if success and output:
        lines = output.strip().split('\n')
        for line in lines:
            if line.startswith('conda ') and not line.startswith('#'):
                version = line.split()[1]
                return duration, success, f"Current version: {version}"
    return duration, success, output

def method_5_conda_info() -> Tuple[float, bool, str]:
    """Method 5: Conda info command"""
    print("  Testing: conda info")
    duration, success, output = time_command("conda info")
    if success:
        # Extract conda version from info
        for line in output.split('\n'):
            if 'conda version' in line:
                version = line.split(':')[-1].strip()
                return duration, success, f"Conda version: {version}"
    return duration, success, output

def method_6_conda_search_json() -> Tuple[float, bool, str]:
    """Method 6: Conda search with JSON output"""
    print("  Testing: conda search conda --json")
    duration, success, output = time_command("conda search conda --json")
    if success:
        try:
            data = json.loads(output)
            if 'conda' in data and data['conda']:
                latest = data['conda'][-1]
                version = latest.get('version', 'unknown')
                return duration, success, f"Latest version: {version}"
        except json.JSONDecodeError:
            pass
    return duration, success, output[:100] + "..." if len(output) > 100 else output

def method_7_curl_anaconda_api() -> Tuple[float, bool, str]:
    """Method 7: Direct curl to Anaconda API"""
    print("  Testing: curl to Anaconda API")
    start_time = time.time()
    try:
        response = requests.get(
            "https://api.anaconda.org/package/anaconda/conda",
            timeout=10
        )
        duration = time.time() - start_time
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get('latest_version', 'unknown')
            return duration, True, f"Latest version: {latest_version}"
        else:
            return duration, False, f"HTTP {response.status_code}"
    except Exception as e:
        duration = time.time() - start_time
        return duration, False, f"ERROR: {str(e)}"

def method_8_curl_conda_forge() -> Tuple[float, bool, str]:
    """Method 8: Curl to conda-forge channel"""
    print("  Testing: curl to conda-forge")
    start_time = time.time()
    try:
        response = requests.get(
            "https://api.anaconda.org/package/conda-forge/conda",
            timeout=10
        )
        duration = time.time() - start_time
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get('latest_version', 'unknown')
            return duration, True, f"Latest version: {latest_version}"
        else:
            return duration, False, f"HTTP {response.status_code}"
    except Exception as e:
        duration = time.time() - start_time
        return duration, False, f"ERROR: {str(e)}"

def method_9_conda_search_timeout() -> Tuple[float, bool, str]:
    """Method 9: Conda search with 5-second timeout"""
    print("  Testing: conda search with 5s timeout")
    duration, success, output = time_command("conda search conda | tail -1", timeout=5)
    if success and output:
        version = output.split()[1] if len(output.split()) > 1 else "unknown"
        return duration, success, f"Latest version: {version}"
    return duration, success, output

def method_10_ping_and_version() -> Tuple[float, bool, str]:
    """Method 10: Just ping + get current version (fastest baseline)"""
    print("  Testing: ping + current version only")
    start_time = time.time()
    
    # Quick ping test
    ping_duration, ping_success, _ = time_command("ping -c 1 -W 1000 anaconda.org", timeout=5)
    
    if ping_success:
        # Get current version
        version_duration, version_success, output = time_command("conda --version")
        total_duration = time.time() - start_time
        
        if version_success:
            version = output.split()[-1] if output else "unknown"
            return total_duration, True, f"Current version: {version} (server reachable)"
        else:
            return total_duration, False, "Could not get conda version"
    else:
        total_duration = time.time() - start_time
        return total_duration, False, "Anaconda server unreachable"

def run_all_tests() -> Dict[str, Tuple[float, bool, str]]:
    """Run all test methods and return results"""
    
    methods = [
        ("Method 1: conda search conda (full)", method_1_conda_search_full),
        ("Method 2: conda search conda (limited)", method_2_conda_search_limited),
        ("Method 3: conda update --dry-run", method_3_conda_update_dry_run),
        ("Method 4: conda list conda", method_4_conda_list_current),
        ("Method 5: conda info", method_5_conda_info),
        ("Method 6: conda search --json", method_6_conda_search_json),
        ("Method 7: curl Anaconda API", method_7_curl_anaconda_api),
        ("Method 8: curl conda-forge API", method_8_curl_conda_forge),
        ("Method 9: conda search (5s timeout)", method_9_conda_search_timeout),
        ("Method 10: ping + current version", method_10_ping_and_version),
    ]
    
    results = {}
    
    print("🧪 Testing 10 different methods to check conda updates...")
    print("=" * 60)
    
    for name, method in methods:
        print(f"\n🔍 {name}")
        try:
            duration, success, output = method()
            results[name] = (duration, success, output)
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"   Result: {status} ({duration:.2f}s)")
            print(f"   Output: {output}")
        except Exception as e:
            print(f"   Result: ❌ EXCEPTION ({str(e)})")
            results[name] = (999.0, False, f"Exception: {str(e)}")
    
    return results

def analyze_results(results: Dict[str, Tuple[float, bool, str]]):
    """Analyze and display results"""
    
    print("\n" + "=" * 60)
    print("📊 ANALYSIS RESULTS")
    print("=" * 60)
    
    # Sort by speed (successful methods first, then by duration)
    successful = [(name, duration, output) for name, (duration, success, output) in results.items() if success]
    failed = [(name, duration, output) for name, (duration, success, output) in results.items() if not success]
    
    successful.sort(key=lambda x: x[1])  # Sort by duration
    failed.sort(key=lambda x: x[1])
    
    print(f"\n✅ SUCCESSFUL METHODS ({len(successful)} total):")
    print("-" * 40)
    for i, (name, duration, output) in enumerate(successful, 1):
        print(f"{i:2d}. {name:<35} {duration:6.2f}s - {output}")
    
    print(f"\n❌ FAILED METHODS ({len(failed)} total):")
    print("-" * 40)
    for name, duration, output in failed:
        print(f"    {name:<35} {duration:6.2f}s - {output}")
    
    if successful:
        fastest = successful[0]
        print(f"\n🏆 FASTEST SUCCESSFUL METHOD:")
        print(f"    {fastest[0]} ({fastest[1]:.2f}s)")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if fastest[1] < 2.0:
            print(f"    ✅ Use '{fastest[0]}' for production (under 2 seconds)")
        elif fastest[1] < 5.0:
            print(f"    ⚠️  '{fastest[0]}' is acceptable but consider optimization")
        else:
            print(f"    ❌ All methods are slow (>{fastest[1]:.1f}s). Consider skipping version checks.")
        
        # Find methods under 3 seconds
        fast_methods = [m for m in successful if m[1] < 3.0]
        if len(fast_methods) > 1:
            print(f"    📋 Fast alternatives (under 3s):")
            for method, duration, _ in fast_methods[1:4]:  # Show top 3 alternatives
                print(f"       - {method} ({duration:.2f}s)")

def main():
    """Main test runner"""
    print("🚀 Conda Update Speed Test")
    print("Testing various methods to check for conda updates...")
    print(f"Python version: {sys.version}")
    print(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get baseline conda version
    duration, success, output = time_command("conda --version")
    if success:
        print(f"Current conda version: {output}")
    else:
        print("⚠️  Could not determine conda version")
    
    # Run all tests
    results = run_all_tests()
    
    # Analyze results
    analyze_results(results)
    
    print(f"\n📝 Test completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("💾 Save these results to optimize your installer scripts!")

if __name__ == "__main__":
    main()
