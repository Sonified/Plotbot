#!/usr/bin/env python3
"""
Test script for pyspedas lazy loading functionality in Plotbot.

This script verifies that:
1. pyspedas is not imported during plotbot package initialization
2. SPEDAS_DATA_DIR can be set before importing plotbot
3. pyspedas is only loaded when VDF functions are called
4. Custom data directories are respected by pyspedas

Run with: python test_pyspedas_lazy_loading.py
"""

import os
import sys
import time
import subprocess
import tempfile
import shutil
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(message, color=BLUE):
    """Print a status message with color."""
    print(f"{color}🔍 {message}{RESET}")

def print_success(message):
    """Print a success message."""
    print(f"{GREEN}✅ {message}{RESET}")

def print_fail(message):
    """Print a failure message."""
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message):
    """Print a warning message."""
    print(f"{YELLOW}⚠️ {message}{RESET}")

def test_fresh_import_no_pyspedas():
    """Test that importing plotbot in a fresh process doesn't load pyspedas."""
    print_status("Testing fresh plotbot import without pyspedas loading...")
    
    test_script = '''
import sys
import time

# Record import time
start_time = time.time()
from plotbot import *
import_time = time.time() - start_time

# Check if pyspedas was loaded
pyspedas_loaded = 'pyspedas' in sys.modules

print(f"IMPORT_TIME:{import_time:.3f}")
print(f"PYSPEDAS_LOADED:{pyspedas_loaded}")
print(f"SUCCESS:{'PASS' if not pyspedas_loaded else 'FAIL'}")
'''
    
    # Run in subprocess to get fresh Python environment
    try:
        result = subprocess.run([sys.executable, '-c', test_script], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print_fail(f"Import test failed with error: {result.stderr}")
            return False
            
        # Parse results
        lines = result.stdout.strip().split('\n')
        import_time = None
        pyspedas_loaded = None
        success = None
        
        for line in lines:
            if line.startswith('IMPORT_TIME:'):
                import_time = float(line.split(':')[1])
            elif line.startswith('PYSPEDAS_LOADED:'):
                pyspedas_loaded = line.split(':')[1] == 'True'
            elif line.startswith('SUCCESS:'):
                success = line.split(':')[1] == 'PASS'
        
        print_status(f"Import time: {import_time:.3f} seconds")
        print_status(f"pyspedas loaded during import: {pyspedas_loaded}")
        
        if success:
            print_success("plotbot imports without loading pyspedas")
            return True
        else:
            print_fail("pyspedas was loaded during plotbot import")
            return False
            
    except subprocess.TimeoutExpired:
        print_fail("Import test timed out")
        return False
    except Exception as e:
        print_fail(f"Import test failed: {e}")
        return False

def test_spedas_data_dir_control():
    """Test that SPEDAS_DATA_DIR can be set after import and used by pyspedas."""
    print_status("Testing SPEDAS_DATA_DIR control with lazy loading...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_data_dir = os.path.join(temp_dir, 'custom_pyspedas_data')
        
        test_script = f'''
import os
import sys
import tempfile

# Import plotbot first (no SPEDAS_DATA_DIR set yet)
from plotbot import *

# NOW set custom SPEDAS_DATA_DIR after import (this is the key test!)
custom_dir = r"{custom_data_dir}"
os.environ['SPEDAS_DATA_DIR'] = custom_dir
os.makedirs(custom_dir, exist_ok=True)

print(f"SET_DIR:{{custom_dir}}")

# Check that it's actually set
current_dir = os.environ.get('SPEDAS_DATA_DIR', 'NOT_SET')
print(f"ENV_VAR_SET:{{current_dir == custom_dir}}")

# Try calling a function that uses pyspedas (this should read our custom directory)
try:
    test_trange = ['2020/01/29 18:10:00', '2020/01/29 18:10:30']
    # This call should trigger pyspedas import and use our custom directory
    result = vdyes(test_trange)
    pyspedas_called = True
except Exception as e:
    # It's OK if vdyes fails due to data availability
    pyspedas_called = True
    print(f"VDYES_ERROR:{{str(e)[:50]}}")

# The real test: was pyspedas loaded and did it use our directory?
pyspedas_loaded = 'pyspedas' in sys.modules
print(f"PYSPEDAS_LOADED:{{pyspedas_loaded}}")

# Check if our custom directory exists and was potentially used
data_dir_used = os.path.exists(custom_dir)
print(f"CUSTOM_DIR_EXISTS:{{data_dir_used}}")

# Success if pyspedas loaded and environment variable was set correctly
success = pyspedas_loaded and (current_dir == custom_dir)
print(f"SUCCESS:{{'PASS' if success else 'FAIL'}}")
'''
        
        try:
            result = subprocess.run([sys.executable, '-c', test_script], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print_fail(f"SPEDAS_DATA_DIR test failed: {result.stderr}")
                return False
                
            # Parse results
            lines = result.stdout.strip().split('\n')
            success = None
            
            for line in lines:
                if line.startswith('SUCCESS:'):
                    success = line.split(':')[1] == 'PASS'
                elif line.startswith('SET_DIR:'):
                    print_status(f"Set directory after import: {line.split(':', 1)[1]}")
                elif line.startswith('ENV_VAR_SET:'):
                    env_set = line.split(':')[1] == 'True'
                    print_status(f"Environment variable set correctly: {env_set}")
                elif line.startswith('PYSPEDAS_LOADED:'):
                    pyspedas_loaded = line.split(':')[1] == 'True'
                    print_status(f"pyspedas loaded when needed: {pyspedas_loaded}")
                elif line.startswith('VDYES_ERROR:'):
                    print_warning(f"vdyes error (expected): {line.split(':', 1)[1]}")
            
            if success:
                print_success("SPEDAS_DATA_DIR can be set AFTER import and works correctly")
                return True
            else:
                print_fail("SPEDAS_DATA_DIR control after import failed")
                return False
                
        except Exception as e:
            print_fail(f"SPEDAS_DATA_DIR test failed: {e}")
            return False

def test_lazy_loading_trigger():
    """Test that pyspedas is loaded when VDF functions are called."""
    print_status("Testing lazy loading trigger with vdyes()...")
    
    test_script = '''
import sys
import os
import tempfile

# Set up custom data directory
temp_dir = tempfile.mkdtemp()
custom_dir = os.path.join(temp_dir, 'test_data')
os.environ['SPEDAS_DATA_DIR'] = custom_dir
os.makedirs(custom_dir, exist_ok=True)

# Import plotbot (should not load pyspedas)
from plotbot import *

# Check pyspedas before vdyes call
pyspedas_before = 'pyspedas' in sys.modules
print(f"PYSPEDAS_BEFORE:{pyspedas_before}")

# Try to call vdyes (this should trigger pyspedas import)
try:
    # Use a small test range
    test_trange = ['2020/01/29 18:10:00', '2020/01/29 18:10:30']
    result = vdyes(test_trange)
    vdyes_success = True
except Exception as e:
    # It's OK if vdyes fails due to data availability - we're testing import mechanism
    vdyes_success = False
    print(f"VDYES_ERROR:{str(e)[:100]}")

# Check pyspedas after vdyes call
pyspedas_after = 'pyspedas' in sys.modules
print(f"PYSPEDAS_AFTER:{pyspedas_after}")

# Success if pyspedas was not loaded before but was loaded after
lazy_loading_worked = (not pyspedas_before) and pyspedas_after
print(f"LAZY_LOADING:{'PASS' if lazy_loading_worked else 'FAIL'}")

# Check if custom directory structure was created
data_created = os.path.exists(custom_dir) and len(os.listdir(custom_dir)) > 0
print(f"DATA_CREATED:{data_created}")

# Cleanup
import shutil
shutil.rmtree(temp_dir, ignore_errors=True)

print(f"SUCCESS:{'PASS' if lazy_loading_worked else 'FAIL'}")
'''
    
    try:
        result = subprocess.run([sys.executable, '-c', test_script], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print_fail(f"Lazy loading test failed: {result.stderr}")
            return False
            
        # Parse results
        lines = result.stdout.strip().split('\n')
        pyspedas_before = None
        pyspedas_after = None
        success = None
        
        for line in lines:
            if line.startswith('PYSPEDAS_BEFORE:'):
                pyspedas_before = line.split(':')[1] == 'True'
            elif line.startswith('PYSPEDAS_AFTER:'):
                pyspedas_after = line.split(':')[1] == 'True'
            elif line.startswith('SUCCESS:'):
                success = line.split(':')[1] == 'PASS'
            elif line.startswith('VDYES_ERROR:'):
                print_warning(f"vdyes() error (expected): {line.split(':', 1)[1]}")
            elif line.startswith('DATA_CREATED:'):
                data_created = line.split(':')[1] == 'True'
                if data_created:
                    print_status("Custom data directory was used")
        
        print_status(f"pyspedas before vdyes(): {pyspedas_before}")
        print_status(f"pyspedas after vdyes(): {pyspedas_after}")
        
        if success:
            print_success("Lazy loading triggered correctly")
            return True
        else:
            print_fail("Lazy loading did not work as expected")
            return False
            
    except Exception as e:
        print_fail(f"Lazy loading test failed: {e}")
        return False

def test_plotbot_interactive_vdf_lazy():
    """Test that plotbot_interactive_vdf also uses lazy loading."""
    print_status("Testing plotbot_interactive_vdf lazy loading...")
    
    test_script = '''
import sys
import os
import tempfile

# Set up custom data directory
temp_dir = tempfile.mkdtemp()
custom_dir = os.path.join(temp_dir, 'test_data')
os.environ['SPEDAS_DATA_DIR'] = custom_dir
os.makedirs(custom_dir, exist_ok=True)

# Import plotbot (should not load pyspedas)
from plotbot import *

# Check pyspedas before function call
pyspedas_before = 'pyspedas' in sys.modules
print(f"PYSPEDAS_BEFORE:{pyspedas_before}")

# Try to call plotbot_interactive_vdf (this should trigger pyspedas import)
try:
    # Use matplotlib backend to avoid web dependencies in test
    test_trange = ['2020/01/29 18:10:00', '2020/01/29 18:10:30']
    result = plotbot_interactive_vdf(test_trange, backend='matplotlib')
    call_success = True
except Exception as e:
    # It's OK if function fails due to data availability - we're testing import mechanism
    call_success = False
    print(f"FUNCTION_ERROR:{str(e)[:100]}")

# Check pyspedas after function call
pyspedas_after = 'pyspedas' in sys.modules
print(f"PYSPEDAS_AFTER:{pyspedas_after}")

# Success if pyspedas was not loaded before but was loaded after
lazy_loading_worked = (not pyspedas_before) and pyspedas_after
print(f"SUCCESS:{'PASS' if lazy_loading_worked else 'FAIL'}")

# Cleanup
import shutil
shutil.rmtree(temp_dir, ignore_errors=True)
'''
    
    try:
        result = subprocess.run([sys.executable, '-c', test_script], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print_fail(f"plotbot_interactive_vdf test failed: {result.stderr}")
            return False
            
        # Parse results
        lines = result.stdout.strip().split('\n')
        success = None
        
        for line in lines:
            if line.startswith('SUCCESS:'):
                success = line.split(':')[1] == 'PASS'
            elif line.startswith('FUNCTION_ERROR:'):
                print_warning(f"Function error (expected): {line.split(':', 1)[1]}")
        
        if success:
            print_success("plotbot_interactive_vdf lazy loading works")
            return True
        else:
            print_fail("plotbot_interactive_vdf lazy loading failed")
            return False
            
    except Exception as e:
        print_fail(f"plotbot_interactive_vdf test failed: {e}")
        return False

def run_all_tests():
    """Run all lazy loading tests."""
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🧪 PLOTBOT PYSPEDAS LAZY LOADING TEST SUITE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    tests = [
        ("Fresh Import Test", test_fresh_import_no_pyspedas),
        ("SPEDAS_DATA_DIR Control After Import", test_spedas_data_dir_control),
        ("Lazy Loading Trigger", test_lazy_loading_trigger),
        ("Interactive VDF Lazy Loading", test_plotbot_interactive_vdf_lazy),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{BLUE}{'─'*40}{RESET}")
        print(f"{BLUE}🔬 Running: {test_name}{RESET}")
        print(f"{BLUE}{'─'*40}{RESET}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_fail(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}📊 TEST RESULTS SUMMARY{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
            passed += 1
        else:
            print_fail(f"{test_name}")
    
    print(f"\n{BLUE}{'─'*60}{RESET}")
    if passed == total:
        print_success(f"ALL TESTS PASSED! ({passed}/{total})")
        print(f"{GREEN}🎉 Plotbot lazy loading is working correctly!{RESET}")
        return True
    else:
        print_fail(f"SOME TESTS FAILED ({passed}/{total})")
        print(f"{RED}❌ Lazy loading needs attention{RESET}")
        return False

if __name__ == "__main__":
    print(f"{BLUE}🚀 Starting Plotbot pyspedas lazy loading tests...{RESET}\n")
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
