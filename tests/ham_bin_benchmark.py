"""
Benchmark: Compare computing bins from scratch vs loading from JSON.
Also verify the JSON matches fresh computation.
"""

import sys
import os
import json
import time

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))

# Import from our test script
from ham_bar_chart_test import process_encounter, BASE_DIR

def load_from_json(json_path):
    """Load bin data from JSON."""
    with open(json_path, 'r') as f:
        return json.load(f)

def compute_fresh(encounters, hamstring_dir):
    """Compute bin data from scratch."""
    results = {}
    for enc in encounters:
        enc_str = f'E{enc:02d}' if enc < 10 else f'E{enc}'
        result = process_encounter(enc, hamstring_dir)
        if result:
            results[enc_str] = result
    return results

def verify_match(json_data, fresh_data):
    """Verify JSON matches fresh computation."""
    mismatches = []

    for enc_str in json_data:
        if enc_str not in fresh_data:
            mismatches.append(f"{enc_str}: missing from fresh data")
            continue

        json_bins = json_data[enc_str]['bins']
        fresh = fresh_data[enc_str]

        if len(json_bins) != len(fresh['bins']):
            mismatches.append(f"{enc_str}: bin count mismatch ({len(json_bins)} vs {len(fresh['bins'])})")
            continue

        for i, jb in enumerate(json_bins):
            if abs(jb['start_lon'] - fresh['start_lons'][i]) > 0.001:
                mismatches.append(f"{enc_str} bin {i}: start_lon mismatch")
            if abs(jb['end_lon'] - fresh['end_lons'][i]) > 0.001:
                mismatches.append(f"{enc_str} bin {i}: end_lon mismatch")
            if abs(jb['ham_frac'] - fresh['ham_frac'][i]) > 0.001:
                mismatches.append(f"{enc_str} bin {i}: ham_frac mismatch")

    return mismatches

if __name__ == '__main__':
    hamstring_dir = os.path.join(BASE_DIR, 'data', 'cdf_files', 'Hamstrings')
    json_path = os.path.join(BASE_DIR, 'data', 'psp', 'ham_angular_bins', 'ham_bin_data.json')

    # Test with just 3 encounters for speed
    test_encounters = [18, 19, 20]

    print("=" * 60)
    print("BENCHMARK: Fresh Computation vs JSON Loading")
    print("=" * 60)

    # Time JSON loading
    print("\n1. Loading from JSON...")
    t0 = time.time()
    json_data = load_from_json(json_path)
    json_time = time.time() - t0
    print(f"   JSON load time: {json_time:.4f} seconds")

    # Time fresh computation
    print(f"\n2. Computing fresh (encounters {test_encounters})...")
    t0 = time.time()
    fresh_data = compute_fresh(test_encounters, hamstring_dir)
    compute_time = time.time() - t0
    print(f"   Compute time: {compute_time:.4f} seconds")

    # Verify match
    print("\n3. Verifying JSON matches fresh computation...")
    # Filter json_data to only test encounters
    json_subset = {f'E{e}': json_data[f'E{e}'] for e in test_encounters}
    mismatches = verify_match(json_subset, fresh_data)

    if mismatches:
        print(f"   MISMATCHES FOUND:")
        for m in mismatches[:10]:
            print(f"     - {m}")
    else:
        print("   All data matches!")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"JSON load:    {json_time:.4f} sec")
    print(f"Fresh compute: {compute_time:.4f} sec")
    print(f"Speedup:      {compute_time/json_time:.1f}x faster with JSON")
