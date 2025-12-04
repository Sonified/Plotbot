#!/usr/bin/env python
"""
🧪 Carrington Longitude Comparison Test

Compares two approaches for computing Carrington longitude:
1. Our approach: psp_positional_data.npz (pre-computed trajectory data)
2. Srijan's approach: SPICE kernels with sunpy/astropy

Tests 3 encounters to see if the numbers match up!
"""

import numpy as np
import pandas as pd
import datetime
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'srijan'))

# === OUR APPROACH: NPZ positional data ===
from plotbot.x_axis_positional_data_helpers import XAxisPositionalDataMapper

# === SRIJAN'S APPROACH: SPICE ===
import glob
from sunpy.coordinates import spice, HeliographicCarrington
import astropy.units as u

# Initialize SPICE kernels (Srijan's approach)
kernel_files = glob.glob("data/psp/spice_data/*.bsp")
if kernel_files:
    spice.initialize(kernel_files)
    SPICE_AVAILABLE = True
    print(f"✅ SPICE initialized with {len(kernel_files)} kernel files")
else:
    SPICE_AVAILABLE = False
    print("⚠️ No SPICE kernel files found - will only test our approach")

# Test encounters E04-E23 (perihelion dates from Srijan's encounters.py)
ENCOUNTERS = {
    'E04': '2020-01-29',
    'E05': '2020-06-07',
    'E06': '2020-09-27',
    'E07': '2021-01-17',
    'E08': '2021-04-28',
    'E09': '2021-08-09',
    'E10': '2021-11-21',
    'E11': '2022-02-25',
    'E12': '2022-06-01',
    'E13': '2022-09-06',
    'E14': '2022-12-11',
    'E15': '2023-03-17',
    'E16': '2023-06-22',
    'E17': '2023-09-27',
    'E18': '2023-12-29',
    'E19': '2024-03-30',
    'E20': '2024-06-30',
    'E21': '2024-09-30',
    'E22': '2024-12-24',
    'E23': '2025-03-22',
}


def get_our_carrington_lon(times_datetime, mapper):
    """
    Get Carrington longitude using OUR approach (NPZ interpolation).

    Args:
        times_datetime: array of datetime objects
        mapper: XAxisPositionalDataMapper instance

    Returns:
        array of longitude values in degrees
    """
    # Convert to numpy datetime64
    times_np = np.array(times_datetime, dtype='datetime64[ns]')
    return mapper.map_to_position(times_np, 'carrington_lon')


def get_srijan_carrington_lon(times_datetime):
    """
    Get Carrington longitude using SRIJAN'S approach (SPICE).

    This is adapted from srijan/misc_functions.py gen_trajectory()

    Args:
        times_datetime: array of datetime objects

    Returns:
        array of longitude values in degrees
    """
    if not SPICE_AVAILABLE:
        return None

    # Get trajectory from SPICE (Srijan's approach)
    parker_trajectory_inertial = spice.get_body('SPP', times_datetime)
    parker_trajectory_carrington = parker_trajectory_inertial.transform_to(
        HeliographicCarrington(observer="self")
    )
    parker_trajectory_carrington.representation_type = "spherical"

    # Extract longitude in degrees
    return parker_trajectory_carrington.lon.to(u.deg).value


def get_srijan_carrington_lat(times_datetime):
    """
    Get Carrington latitude using SRIJAN'S approach (SPICE).
    """
    if not SPICE_AVAILABLE:
        return None

    parker_trajectory_inertial = spice.get_body('SPP', times_datetime)
    parker_trajectory_carrington = parker_trajectory_inertial.transform_to(
        HeliographicCarrington(observer="self")
    )
    parker_trajectory_carrington.representation_type = "spherical"

    return parker_trajectory_carrington.lat.to(u.deg).value


def compare_for_encounter(enc_name, date_str, mapper, hours_around=24):
    """
    Compare Carrington longitude values for a specific encounter.

    Args:
        enc_name: Encounter name (e.g., 'E08')
        date_str: Date string (e.g., '2021-04-29')
        mapper: XAxisPositionalDataMapper instance
        hours_around: Hours before/after perihelion to test

    Returns:
        dict with comparison results
    """
    print(f"\n{'='*60}")
    print(f"🛰️  Testing {enc_name}: {date_str}")
    print(f"{'='*60}")

    # Create array of test times (hourly around perihelion)
    center_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    times = []
    for h in range(-hours_around, hours_around + 1, 1):  # Every hour
        times.append(center_date + datetime.timedelta(hours=h))
    times = np.array(times)

    print(f"📅 Testing {len(times)} timestamps from {times[0]} to {times[-1]}")

    # Get OUR values
    our_lon = get_our_carrington_lon(times, mapper)

    # Get SRIJAN's values
    srijan_lon = get_srijan_carrington_lon(times)

    results = {
        'encounter': enc_name,
        'date': date_str,
        'n_points': len(times),
        'times': times,
        'our_lon': our_lon,
        'srijan_lon': srijan_lon,
    }

    # Print comparison
    print(f"\n📊 Sample values (every 6 hours around perihelion):")
    print(f"{'Time':^25} | {'OUR (°)':^12} | {'SRIJAN (°)':^12} | {'Diff (°)':^10}")
    print("-" * 65)

    for i in range(0, len(times), 6):  # Every 6 hours
        our_val = our_lon[i] if our_lon is not None else np.nan
        srijan_val = srijan_lon[i] if srijan_lon is not None else np.nan
        diff = our_val - srijan_val if (our_lon is not None and srijan_lon is not None) else np.nan

        print(f"{str(times[i]):^25} | {our_val:^12.2f} | {srijan_val:^12.2f} | {diff:^+10.3f}")

    # Statistics
    if our_lon is not None and srijan_lon is not None:
        # Handle wraparound at 0/360 boundary
        diff = our_lon - srijan_lon
        # Wrap differences to [-180, 180]
        diff = np.mod(diff + 180, 360) - 180

        results['diff_mean'] = np.nanmean(diff)
        results['diff_std'] = np.nanstd(diff)
        results['diff_max'] = np.nanmax(np.abs(diff))

        print(f"\n📈 Statistics:")
        print(f"   Mean difference:  {results['diff_mean']:+.4f}°")
        print(f"   Std deviation:    {results['diff_std']:.4f}°")
        print(f"   Max |difference|: {results['diff_max']:.4f}°")

        if results['diff_max'] < 0.1:
            print(f"   ✅ EXCELLENT MATCH! (max diff < 0.1°)")
        elif results['diff_max'] < 1.0:
            print(f"   👍 GOOD MATCH (max diff < 1°)")
        elif results['diff_max'] < 5.0:
            print(f"   ⚠️ MODERATE MATCH (max diff < 5°)")
        else:
            print(f"   ❌ POOR MATCH (max diff >= 5°)")

    return results


def run_all_tests():
    """Run comparison tests for all encounters."""
    print("🚀 Carrington Longitude Comparison Test")
    print("=" * 60)
    print("Comparing OUR approach (NPZ) vs SRIJAN's approach (SPICE)")
    print("=" * 60)

    # Initialize our mapper
    npz_path = 'support_data/trajectories/psp_positional_data.npz'
    mapper = XAxisPositionalDataMapper(npz_path)

    if not mapper.data_loaded:
        print("❌ Failed to load our positional data!")
        return

    # Run tests for each encounter
    all_results = []
    for enc_name, date_str in ENCOUNTERS.items():
        results = compare_for_encounter(enc_name, date_str, mapper)
        all_results.append(results)

    # Summary
    print(f"\n{'='*60}")
    print("📋 SUMMARY")
    print(f"{'='*60}")
    print(f"{'Encounter':^12} | {'Max Diff (°)':^14} | {'Status':^20}")
    print("-" * 50)

    for r in all_results:
        if 'diff_max' in r:
            status = "✅ EXCELLENT" if r['diff_max'] < 0.1 else \
                     "👍 GOOD" if r['diff_max'] < 1.0 else \
                     "⚠️ MODERATE" if r['diff_max'] < 5.0 else "❌ POOR"
            print(f"{r['encounter']:^12} | {r['diff_max']:^14.4f} | {status:^20}")
        else:
            print(f"{r['encounter']:^12} | {'N/A':^14} | {'SPICE unavailable':^20}")

    print(f"\n🏁 Done!")


def test_angular_binning(enc_name, date_str, mapper, angular_sep_deg=1.0):
    """
    Test Srijan's angular binning approach using BOTH data sources.

    This replicates Srijan's bin_by_angular_separation_fast() logic
    but uses our NPZ data instead of SPICE.
    """
    print(f"\n{'='*60}")
    print(f"🎯 Testing Angular Binning for {enc_name}: {date_str}")
    print(f"   Angular separation threshold: {angular_sep_deg}°")
    print(f"{'='*60}")

    # Create timestamps at 5-minute cadence (like SPAN VDF data)
    center_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    times = []
    for m in range(-60*12, 60*12 + 1, 5):  # Every 5 minutes, +/- 12 hours
        times.append(center_date + datetime.timedelta(minutes=m))
    times = np.array(times)

    print(f"📅 Testing {len(times)} timestamps (5-min cadence, ±12h around perihelion)")

    # Get coordinates using OUR approach
    our_lon = get_our_carrington_lon(times, mapper)
    times_np = np.array(times, dtype='datetime64[ns]')
    our_lat = mapper.map_to_position(times_np, 'carrington_lat')

    # Get coordinates using SRIJAN's approach (SPICE)
    srijan_lon = get_srijan_carrington_lon(times)
    srijan_lat = get_srijan_carrington_lat(times)

    if srijan_lon is None:
        print("⚠️ SPICE not available, can't compare binning")
        return

    # === SRIJAN'S BINNING ALGORITHM (adapted from misc_functions.py) ===
    def bin_by_angular_separation(lon, lat, max_sep_deg):
        """
        Simplified version of Srijan's bin_by_angular_separation_fast()
        Returns number of bins created.
        """
        lon_rad = np.radians(lon)
        lat_rad = np.radians(lat)

        valid = np.isfinite(lon_rad) & np.isfinite(lat_rad)
        n = len(lon)
        bins = []
        bin_count = 0

        i = 0
        while i < n:
            if not valid[i]:
                i += 1
                continue

            # Find end of valid block
            j = i + 1
            while j < n and valid[j]:
                j += 1

            # Process this valid block
            start = i
            while start < j:
                ref_lon = lon_rad[start]
                ref_lat = lat_rad[start]

                # Vectorized angular distance (haversine)
                lon_block = lon_rad[start:j]
                lat_block = lat_rad[start:j]

                dlon = lon_block - ref_lon
                dlat = lat_block - ref_lat

                sin_dlat2 = np.sin(dlat * 0.5)**2
                sin_dlon2 = np.sin(dlon * 0.5)**2
                a = sin_dlat2 + np.cos(ref_lat) * np.cos(lat_block) * sin_dlon2
                a = np.clip(a, 0.0, 1.0)
                angle_deg = np.rad2deg(2.0 * np.arcsin(np.sqrt(a)))

                # Find first point exceeding threshold
                too_far = np.where(angle_deg > max_sep_deg)[0]
                if too_far.size == 0:
                    end = j
                else:
                    end = start + too_far[0]

                bins.append((start, end))
                bin_count += 1
                start = end

            i = j

        return bin_count, bins

    # Run binning with OUR data
    our_n_bins, our_bins = bin_by_angular_separation(our_lon, our_lat, angular_sep_deg)

    # Run binning with SRIJAN's data
    srijan_n_bins, srijan_bins = bin_by_angular_separation(srijan_lon, srijan_lat, angular_sep_deg)

    print(f"\n📊 Binning Results:")
    print(f"   OUR approach:    {our_n_bins} bins")
    print(f"   SRIJAN approach: {srijan_n_bins} bins")

    if our_n_bins == srijan_n_bins:
        print(f"   ✅ PERFECT MATCH! Same number of bins")
    else:
        print(f"   ⚠️ Bin count differs by {abs(our_n_bins - srijan_n_bins)}")

    # Compare bin boundaries
    matching_bins = 0
    for i in range(min(len(our_bins), len(srijan_bins))):
        if our_bins[i] == srijan_bins[i]:
            matching_bins += 1

    print(f"   Matching bin boundaries: {matching_bins}/{min(len(our_bins), len(srijan_bins))}")

    # Show a few sample bins
    print(f"\n📍 Sample bin boundaries (first 5):")
    print(f"   {'Bin':^6} | {'OUR (start,end)':^20} | {'SRIJAN (start,end)':^20} | {'Match':^8}")
    print(f"   {'-'*60}")
    for i in range(min(5, len(our_bins), len(srijan_bins))):
        match = "✅" if our_bins[i] == srijan_bins[i] else "❌"
        print(f"   {i+1:^6} | {str(our_bins[i]):^20} | {str(srijan_bins[i]):^20} | {match:^8}")

    return {
        'our_n_bins': our_n_bins,
        'srijan_n_bins': srijan_n_bins,
        'match': our_n_bins == srijan_n_bins
    }


def run_all_tests():
    """Run comparison tests for all encounters."""
    print("🚀 Carrington Longitude Comparison Test")
    print("=" * 60)
    print("Comparing OUR approach (NPZ) vs SRIJAN's approach (SPICE)")
    print("=" * 60)

    # Initialize our mapper
    npz_path = 'support_data/trajectories/psp_positional_data.npz'
    mapper = XAxisPositionalDataMapper(npz_path)

    if not mapper.data_loaded:
        print("❌ Failed to load our positional data!")
        return

    # Run tests for each encounter
    all_results = []
    for enc_name, date_str in ENCOUNTERS.items():
        results = compare_for_encounter(enc_name, date_str, mapper)
        all_results.append(results)

    # Summary
    print(f"\n{'='*60}")
    print("📋 LONGITUDE COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"{'Encounter':^12} | {'Max Diff (°)':^14} | {'Status':^20}")
    print("-" * 50)

    for r in all_results:
        if 'diff_max' in r:
            status = "✅ EXCELLENT" if r['diff_max'] < 0.1 else \
                     "👍 GOOD" if r['diff_max'] < 1.0 else \
                     "⚠️ MODERATE" if r['diff_max'] < 5.0 else "❌ POOR"
            print(f"{r['encounter']:^12} | {r['diff_max']:^14.4f} | {status:^20}")
        else:
            print(f"{r['encounter']:^12} | {'N/A':^14} | {'SPICE unavailable':^20}")

    # Now test angular binning
    print(f"\n\n{'='*60}")
    print("🎯 ANGULAR BINNING COMPARISON")
    print(f"{'='*60}")

    binning_results = []
    for enc_name, date_str in ENCOUNTERS.items():
        result = test_angular_binning(enc_name, date_str, mapper, angular_sep_deg=1.0)
        if result:
            binning_results.append({'encounter': enc_name, **result})

    # Binning summary
    print(f"\n{'='*60}")
    print("📋 BINNING SUMMARY")
    print(f"{'='*60}")
    print(f"{'Encounter':^12} | {'OUR bins':^12} | {'SRIJAN bins':^12} | {'Match':^10}")
    print("-" * 50)

    for r in binning_results:
        match = "✅ YES" if r['match'] else "❌ NO"
        print(f"{r['encounter']:^12} | {r['our_n_bins']:^12} | {r['srijan_n_bins']:^12} | {match:^10}")

    print(f"\n🏁 Done!")


if __name__ == '__main__':
    run_all_tests()
