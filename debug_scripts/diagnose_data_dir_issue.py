#!/usr/bin/env python
"""
Diagnostic script to understand the data directory issue on fresh installs.
This simulates what happens when a user runs plotbot from a Jupyter notebook.
"""

import os
import sys

print("=" * 80)
print("PLOTBOT DATA DIRECTORY DIAGNOSTIC")
print("=" * 80)

# Step 1: Check initial state
print("\n[STEP 1] Initial Environment State")
print("-" * 80)
print(f"Current Working Directory: {os.getcwd()}")
print(f"Python Executable: {sys.executable}")
print(f"SPEDAS_DATA_DIR (before plotbot): {os.environ.get('SPEDAS_DATA_DIR', 'NOT SET')}")

# Step 2: Import plotbot (like user would do)
print("\n[STEP 2] Importing plotbot...")
print("-" * 80)
import plotbot
print(f"✅ Plotbot imported successfully")

# Step 3: Check config state
print("\n[STEP 3] Plotbot Config State")
print("-" * 80)
print(f"config.data_dir: {plotbot.config.data_dir}")
print(f"SPEDAS_DATA_DIR (after plotbot): {os.environ.get('SPEDAS_DATA_DIR', 'NOT SET')}")
print(f"Is data_dir absolute? {os.path.isabs(plotbot.config.data_dir)}")

# Step 4: Import pyspedas and check its configuration
print("\n[STEP 4] Importing pyspedas...")
print("-" * 80)
import pyspedas
from pyspedas.utilities.pyspedas_functools import get_data_dir
pyspedas_data_dir = get_data_dir()
print(f"✅ PySpedas imported successfully")
print(f"PySpedas data directory: {pyspedas_data_dir}")

# Step 5: Compare directories
print("\n[STEP 5] Directory Comparison")
print("-" * 80)
config_dir_abs = os.path.abspath(plotbot.config.data_dir)
pyspedas_dir_abs = os.path.abspath(pyspedas_data_dir)

print(f"Plotbot config (absolute):  {config_dir_abs}")
print(f"PySpedas using (absolute):  {pyspedas_dir_abs}")

if config_dir_abs == pyspedas_dir_abs:
    print("✅ MATCH: PySpedas is using the correct directory!")
else:
    print("❌ MISMATCH: PySpedas is NOT using config.data_dir!")
    print(f"   Expected: {config_dir_abs}")
    print(f"   Actual:   {pyspedas_dir_abs}")

# Step 6: Test actual download behavior
print("\n[STEP 6] Test Download Behavior")
print("-" * 80)
print("Attempting to download a small test file...")

try:
    # Use no_update=True to just check local files without downloading
    result = pyspedas.psp.fields(
        trange=['2020-01-29/18:00:00', '2020-01-29/18:05:00'],
        datatype='mag_rtn_4_sa_per_cyc',
        level='l2',
        downloadonly=True,
        no_update=True
    )
    
    if result:
        test_file = result[0]
        print(f"Test file location: {test_file}")
        
        # Check if it's in the expected directory
        if config_dir_abs in test_file:
            print("✅ File is in correct plotbot data directory")
        else:
            print("❌ File is NOT in plotbot data directory!")
            
            # Try to understand where it is
            if os.getcwd() in test_file:
                print(f"   File appears to be relative to CWD: {os.getcwd()}")
            
    else:
        print("No files found locally (would download if no_update=False)")
        
except Exception as e:
    print(f"Error during test download: {e}")

# Step 7: Summary
print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)

issues_found = []

if not os.environ.get('SPEDAS_DATA_DIR'):
    issues_found.append("❌ SPEDAS_DATA_DIR environment variable is not set")

if config_dir_abs != pyspedas_dir_abs:
    issues_found.append(f"❌ PySpedas using wrong directory: {pyspedas_dir_abs}")

if not os.path.isabs(plotbot.config.data_dir):
    issues_found.append(f"❌ config.data_dir is not absolute: {plotbot.config.data_dir}")

if issues_found:
    print("\n🔴 ISSUES DETECTED:")
    for issue in issues_found:
        print(f"   {issue}")
else:
    print("\n🟢 No issues detected - configuration appears correct!")

print("\n" + "=" * 80)

