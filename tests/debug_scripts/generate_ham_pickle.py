#!/usr/bin/env python3
"""
Generate a pickle file from ALL ham CDF files.
Compatible with plotbot's load_simple_snapshot() function.
Run once, then use load_simple_snapshot('all_ham_data.pkl') for instant loading.
"""

import cdflib
import numpy as np
import pickle
import os
from glob import glob
from datetime import datetime

# Find all ham CDF files
cdf_dir = 'data/cdf_files/Hamstrings'
cdf_files = sorted(glob(os.path.join(cdf_dir, 'hamstring_*_v*.cdf')))
print(f"Found {len(cdf_files)} ham CDF files")

# Load ALL data from ALL files
all_data = {}
all_times = []

for i, cdf_path in enumerate(cdf_files):
    print(f"Loading {i+1}/{len(cdf_files)}: {os.path.basename(cdf_path)}")

    with cdflib.CDF(cdf_path) as cdf:
        info = cdf.cdf_info()

        # Get epoch/time
        epoch = cdf.varget('Epoch')
        all_times.append(epoch)

        # Get ALL other variables
        for var_name in info.zVariables:
            if var_name == 'Epoch':
                continue
            try:
                data = cdf.varget(var_name)
                if var_name not in all_data:
                    all_data[var_name] = []
                all_data[var_name].append(data)
            except Exception as e:
                print(f"  Warning: Could not load {var_name}: {e}")

print(f"\nLoaded {len(all_data)} variables")

# Concatenate all arrays
print("Concatenating arrays...")
times = np.concatenate(all_times)
for var_name in all_data:
    all_data[var_name] = np.concatenate(all_data[var_name])

# Sort by time
print("Sorting by time...")
sort_idx = np.argsort(times)
times = times[sort_idx]
for var_name in all_data:
    all_data[var_name] = all_data[var_name][sort_idx]

# Convert epoch to datetime
print("Converting times to datetime...")
datetime_array = np.array(cdflib.cdfepoch.to_datetime(times))

# Now create the plotbot-compatible structure
print("Creating plotbot-compatible ham instance...")

# Import plotbot to get the ham_class
import sys
sys.path.insert(0, '.')
from plotbot.data_classes.psp_ham_classes import ham_class

# Create a mock ImportedData object that ham_class expects
class MockImportedData:
    def __init__(self, data_dict, times):
        self.data = data_dict
        self.times = times

# Add Epoch to data dict (ham_class looks for it)
all_data['Epoch'] = times

mock_data = MockImportedData(all_data, times)

# Create a fresh ham instance with the data
ham_instance = ham_class(mock_data)

# Create snapshot in the format load_simple_snapshot expects
snapshot = {
    'data': {'ham': ham_instance},
    'tracker': {'ham': [[datetime_array[0], datetime_array[-1]]]},
    'timestamp': datetime.now()
}

# Save to pickle
output_path = 'all_ham_data.pkl'
print(f"\nSaving to {output_path}...")
with open(output_path, 'wb') as f:
    pickle.dump(snapshot, f)

# Summary
file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f"\n=== Done ===")
print(f"Total records: {len(times):,}")
print(f"Variables: {list(all_data.keys())}")
print(f"Time range: {datetime_array[0]} to {datetime_array[-1]}")
print(f"File size: {file_size_mb:.1f} MB")
print(f"\nTo use: load_simple_snapshot('all_ham_data.pkl')")
