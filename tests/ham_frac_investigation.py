"""
Quick investigation of ham_frac values.
Srijan says ham_frac should always be < 1.
"""
import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load the 3-day JSON
json_path = os.path.join(BASE_DIR, 'data', 'psp', 'ham_angular_bins', 'ham_bin_data_plus_minus_3_days.json')

with open(json_path, 'r') as f:
    data = json.load(f)

print("=" * 70)
print("HAM_FRAC INVESTIGATION")
print("=" * 70)
print(f"\nFormula used: ham_frac = ham_count / (1 + all_count)")
print("Srijan expects: ham_frac should ALWAYS be < 1")
print("=" * 70)

total_bins = 0
bins_over_1 = 0
max_frac = 0
max_frac_info = None

for enc, enc_data in sorted(data.items(), key=lambda x: int(x[0][1:])):
    enc_bins_over_1 = 0
    for b in enc_data['bins']:
        total_bins += 1
        ham_count = b['ham_count']
        all_count = b['all_count']
        ham_frac = b['ham_frac']
        
        if ham_frac > 1:
            bins_over_1 += 1
            enc_bins_over_1 += 1
        
        if ham_frac > max_frac:
            max_frac = ham_frac
            max_frac_info = {
                'enc': enc,
                'ham_count': ham_count,
                'all_count': all_count,
                'ham_frac': ham_frac,
                'start_lon': b['start_lon'],
                'end_lon': b['end_lon']
            }
    
    if enc_bins_over_1 > 0:
        print(f"{enc}: {enc_bins_over_1} bins with ham_frac > 1 (out of {len(enc_data['bins'])})")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total bins analyzed: {total_bins}")
print(f"Bins with ham_frac > 1: {bins_over_1} ({100*bins_over_1/total_bins:.1f}%)")
print(f"\nMax ham_frac found: {max_frac:.3f}")
if max_frac_info:
    print(f"  Encounter: {max_frac_info['enc']}")
    print(f"  ham_count: {max_frac_info['ham_count']}")
    print(f"  all_count: {max_frac_info['all_count']}")
    print(f"  Calculated: {max_frac_info['ham_count']} / (1 + {max_frac_info['all_count']}) = {max_frac_info['ham_count'] / (1 + max_frac_info['all_count']):.3f}")

print("\n" + "=" * 70)
print("THE PROBLEM:")
print("=" * 70)
print("ham_count = number of hammerhead detections (from CDF, high cadence)")
print("all_count = number of trajectory points (from SPICE, 5-min cadence)")
print("\nThese have DIFFERENT cadences!")
print("If ham detections are at 1-second cadence and trajectory is at 5-min cadence,")
print("you can have 300+ ham detections per trajectory point.")
print("\nSrijan's calculation probably used the SAME cadence for both numerator and denominator.")
