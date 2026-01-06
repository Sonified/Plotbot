#!/usr/bin/env python3
"""
Diagnose how many bins at the beginning and end of each encounter
are going the "wrong way" (right to left, i.e., decreasing Carrington longitude).

If Carrington longitude generally increases through an encounter,
bins where end_lon < start_lon are going backwards.
"""

import json
import os

def is_backward_bin(start_lon, end_lon):
    """
    Check if a bin goes backward (right to left / decreasing longitude).

    Handle the 360° wrap: if the difference is > 180°, it wrapped around.
    """
    delta = end_lon - start_lon

    # Handle wrap-around at 360°
    if delta > 180:
        delta -= 360
    elif delta < -180:
        delta += 360

    # Negative delta = going backward (decreasing longitude)
    return delta < 0


def analyze_encounter(enc_key, bins):
    """Analyze an encounter's bins for backward direction."""
    n_bins = len(bins)

    # Check each bin
    backward_flags = []
    for b in bins:
        backward_flags.append(is_backward_bin(b['start_lon'], b['end_lon']))

    # Count consecutive backward bins at START
    start_backward = 0
    for flag in backward_flags:
        if flag:
            start_backward += 1
        else:
            break

    # Count consecutive backward bins at END
    end_backward = 0
    for flag in reversed(backward_flags):
        if flag:
            end_backward += 1
        else:
            break

    # Total backward bins
    total_backward = sum(backward_flags)

    return {
        'n_bins': n_bins,
        'start_backward': start_backward,
        'end_backward': end_backward,
        'total_backward': total_backward,
        'backward_indices': [i for i, f in enumerate(backward_flags) if f]
    }


def main():
    # Load the JSON
    json_path = os.path.join(os.path.dirname(__file__),
                             'data', 'psp', 'ham_angular_bins',
                             'ham_bin_data_plus_minus_3_days_corrected.json')

    with open(json_path, 'r') as f:
        data = json.load(f)

    print("=" * 70)
    print("BACKWARD BINS DIAGNOSTIC")
    print("=" * 70)
    print()
    print("A 'backward' bin has end_lon < start_lon (after wrap adjustment)")
    print("This means the bin draws right-to-left instead of left-to-right")
    print()

    # Sort encounters by number (E04, E05, etc.)
    enc_keys = sorted(data.keys(), key=lambda x: int(x[1:]))

    print(f"{'Enc':<6} {'Total':<8} {'@ Start':<10} {'@ End':<10} {'Total Bad':<12} {'Bad Indices'}")
    print("-" * 70)

    for enc_key in enc_keys:
        enc_data = data[enc_key]
        bins = enc_data.get('bins', [])

        if not bins:
            print(f"{enc_key:<6} (no bins)")
            continue

        result = analyze_encounter(enc_key, bins)

        # Format the backward indices nicely
        indices = result['backward_indices']
        if len(indices) == 0:
            idx_str = "none"
        elif len(indices) <= 6:
            idx_str = str(indices)
        else:
            idx_str = f"{indices[:3]}...{indices[-3:]}"

        print(f"{enc_key:<6} {result['n_bins']:<8} {result['start_backward']:<10} "
              f"{result['end_backward']:<10} {result['total_backward']:<12} {idx_str}")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Summary stats
    all_start = []
    all_end = []
    all_total = []

    for enc_key in enc_keys:
        enc_data = data[enc_key]
        bins = enc_data.get('bins', [])
        if bins:
            result = analyze_encounter(enc_key, bins)
            all_start.append(result['start_backward'])
            all_end.append(result['end_backward'])
            all_total.append(result['total_backward'])

    print(f"\nAverage backward bins at START: {sum(all_start)/len(all_start):.1f}")
    print(f"Average backward bins at END: {sum(all_end)/len(all_end):.1f}")
    print(f"Average total backward bins: {sum(all_total)/len(all_total):.1f}")

    print(f"\nMax backward bins at START: {max(all_start)}")
    print(f"Max backward bins at END: {max(all_end)}")
    print(f"Max total backward bins: {max(all_total)}")

    # Find encounters with backward bins not at start/end
    print("\n" + "=" * 70)
    print("ENCOUNTERS WITH MID-ENCOUNTER BACKWARD BINS")
    print("=" * 70)

    for enc_key in enc_keys:
        enc_data = data[enc_key]
        bins = enc_data.get('bins', [])
        if not bins:
            continue

        result = analyze_encounter(enc_key, bins)
        indices = result['backward_indices']

        # Check for backward bins that aren't at the edges
        n = result['n_bins']
        start_count = result['start_backward']
        end_count = result['end_backward']

        # Expected indices: 0..start_count-1 at start, n-end_count..n-1 at end
        expected_start = set(range(start_count))
        expected_end = set(range(n - end_count, n)) if end_count > 0 else set()
        expected = expected_start | expected_end
        actual = set(indices)

        mid_backward = actual - expected
        if mid_backward:
            print(f"{enc_key}: Mid-encounter backward bins at indices: {sorted(mid_backward)}")

    print("\nDone!")


if __name__ == '__main__':
    main()
