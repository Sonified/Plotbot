#!/usr/bin/env python
"""
Generate HAM angular bin JSON using Srijan's CORRECT approach.

Uses pyspedas to get SPI L3 timestamps (cached locally), then:
1. Interpolate SPICE trajectory onto SPAN timestamps
2. Bin by angular separation
3. Count ham detections vs total SPAN measurements
4. ham_frac = ham_counts / (1 + all_counts) -- always <= 1
"""

import sys
import os
import glob
import re
import json
import numpy as np
import cdflib
import cdflib.xarray
import xarray
import pandas as pd
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import astropy.units as u

# Add paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(BASE_DIR, 'srijan'))

# Import from Srijan's code
from sunpy.coordinates import spice, HeliographicCarrington
import pyspedas

# Initialize SPICE
spice_kernel_dir = os.path.join(BASE_DIR, 'data', 'psp', 'spice_data')
kernel_files = glob.glob(os.path.join(spice_kernel_dir, '*.bsp'))
print(f"Loading {len(kernel_files)} SPICE kernel files...")
spice.initialize(kernel_files)
spice.install_frame('IAU_SUN')
print("SPICE initialized")

PERIHELION_TIMES = {
    4: '2020/01/29 09:37:00.000', 5: '2020/06/07 08:23:00.000',
    6: '2020/09/27 09:16:00.000', 7: '2021/01/17 17:40:00.000',
    8: '2021/04/29 08:48:00.000', 9: '2021/08/09 19:11:00.000',
    10: '2021/11/21 08:23:00.000', 11: '2022/02/25 15:38:00.000',
    12: '2022/06/01 22:51:00.000', 13: '2022/09/06 06:04:00.000',
    14: '2022/12/11 13:16:00.000', 15: '2023/03/17 20:30:00.000',
    16: '2023/06/22 03:46:00.000', 17: '2023/09/27 23:28:00.000',
    18: '2023/12/29 00:56:00.000', 19: '2024/03/30 02:21:00.000',
    20: '2024/06/30 03:47:00.000', 21: '2024/09/30 05:15:00.000',
    22: '2024/12/24 11:53:00.000', 23: '2025/03/22 22:42:00.000',
}

def datetime2unix(dt_arr):
    """Convert datetime-like array to unix timestamps."""
    # Handle numpy datetime64
    if hasattr(dt_arr[0], 'timestamp'):
        return np.array([dt.timestamp() for dt in dt_arr])
    else:
        # numpy datetime64 - convert via pandas
        return pd.to_datetime(dt_arr).astype(np.int64) / 1e9

def get_span_timestamps(tstart, tend):
    """
    Get SPAN SPI L3 timestamps using pyspedas (downloads/uses cache).
    This is the key - we need SPAN cadence for proper ham_frac calculation.
    """
    tstart_str = f'{tstart.year:04d}-{tstart.month:02d}-{tstart.day:02d}/{tstart.hour:02d}:{tstart.minute:02d}:{tstart.second:02d}'
    tend_str = f'{tend.year:04d}-{tend.month:02d}-{tend.day:02d}/{tend.hour:02d}:{tend.minute:02d}:{tend.second:02d}'

    print(f"    Getting SPI L3 data from {tstart_str} to {tend_str}...")
    spi_vars = pyspedas.psp.spi(trange=[tstart_str, tend_str], datatype='spi_sf0a_l3_mom', level='l3',
                                time_clip=True, notplot=True)

    # Handle different pyspedas key names
    spi_key = 'psp_spi_DENS' if 'psp_spi_DENS' in spi_vars else 'DENS'
    if spi_key not in spi_vars:
        # Try to find any key with timestamps
        for k in spi_vars.keys():
            if 'x' in spi_vars[k]:
                spi_key = k
                break

    dt_span = spi_vars[spi_key]['x']  # Array of datetime objects
    print(f"    Got {len(dt_span)} SPAN timestamps")
    return dt_span

def get_trajectory_at_times(times):
    """Get SPICE trajectory at specific times, return in Carrington coords."""
    trajectory = spice.get_body('SPP', times)
    traj_carr = trajectory.transform_to(HeliographicCarrington(observer='self'))
    return traj_carr

def bin_by_angular_separation(coords, max_sep_deg=1.0):
    """
    Bin coordinates by angular separation (Srijan's algorithm).
    Returns list of coordinate slices, one per bin.
    """
    lon = coords.lon.to_value(u.rad)
    lat = coords.lat.to_value(u.rad)
    valid = np.isfinite(lon) & np.isfinite(lat)
    n = len(lon)
    bins = []

    i = 0
    while i < n:
        if not valid[i]:
            i += 1
            continue
        j = i + 1
        while j < n and valid[j]:
            j += 1

        start = i
        while start < j:
            ref_lon, ref_lat = lon[start], lat[start]
            lon_block, lat_block = lon[start:j], lat[start:j]
            dlon, dlat = lon_block - ref_lon, lat_block - ref_lat
            sin_dlat2 = np.sin(dlat * 0.5)**2
            sin_dlon2 = np.sin(dlon * 0.5)**2
            a = sin_dlat2 + np.cos(ref_lat) * np.cos(lat_block) * sin_dlon2
            a = np.clip(a, 0.0, 1.0)
            angle_deg = np.rad2deg(2.0 * np.arcsin(np.sqrt(a)))
            too_far_idx = np.where(angle_deg > max_sep_deg)[0]
            end = j if too_far_idx.size == 0 else start + too_far_idx[0]
            bins.append(coords[start:end])
            start = end
        i = j

    return bins

def count_ham_in_bins(hammertimes, bins):
    """Count ham detections and total SPAN measurements per bin."""
    hammer_unix = datetime2unix(hammertimes)
    bin_start_unix = np.array([b.obstime[0].to_datetime().timestamp() for b in bins])
    bin_end_unix = np.array([b.obstime[-1].to_datetime().timestamp() for b in bins])

    left_idx = np.searchsorted(hammer_unix, bin_start_unix, side='left')
    right_idx = np.searchsorted(hammer_unix, bin_end_unix, side='right')
    ham_counts = right_idx - left_idx

    # all_counts = number of SPAN measurements in each bin (same cadence as ham!)
    all_counts = np.array([len(b) for b in bins])

    return ham_counts, all_counts

def load_ham_data(enc, hamstring_dir, num_days=3):
    """Load hamstring CDF data for an encounter."""
    peri_str = PERIHELION_TIMES[enc]
    peri_dt = datetime.strptime(peri_str, '%Y/%m/%d %H:%M:%S.%f')
    pday = np.datetime64(peri_dt).astype('datetime64[D]')
    enc_days = np.arange(pday - np.timedelta64(num_days, 'D'),
                         pday + np.timedelta64(num_days + 1, 'D'))

    filenames = [f for f in os.listdir(hamstring_dir) if f.startswith('hamstring_')]
    filedates = {np.datetime64(re.split('[_]', f)[1]).astype('datetime64[D]'): f for f in filenames}

    xrs = []
    for day in enc_days:
        day_d = day.astype('datetime64[D]')
        if day_d in filedates:
            xrs.append(cdflib.xarray.cdf_to_xarray(os.path.join(hamstring_dir, filedates[day_d])))

    if not xrs:
        return None, None

    hamdata = xarray.concat(xrs, dim='record0')
    hammertimes = list(pd.to_datetime(hamdata['epoch'].data).to_pydatetime())
    return hamdata, hammertimes

def process_encounter(enc, hamstring_dir, num_days=3):
    """Process one encounter using Srijan's correct approach."""
    print(f"  Loading ham data...")
    hamdata, hammertimes = load_ham_data(enc, hamstring_dir, num_days)
    if not hammertimes:
        return None
    print(f"  {len(hammertimes)} ham detections")

    tstart, tend = hammertimes[0], hammertimes[-1]

    # KEY: Get SPAN timestamps from SPI L3 (pyspedas downloads/caches)
    span_times = get_span_timestamps(tstart, tend)
    print(f"  {len(span_times)} SPAN measurements")

    # Get trajectory at SPAN timestamps (same cadence!)
    print(f"  Getting trajectory at SPAN times...")
    traj_carr = get_trajectory_at_times(span_times)

    # Bin by angular separation
    print(f"  Binning by angular separation...")
    bins = bin_by_angular_separation(traj_carr, max_sep_deg=1.0)
    print(f"  {len(bins)} bins")

    # Count ham detections and SPAN measurements per bin
    ham_counts, all_counts = count_ham_in_bins(hammertimes, bins)
    ham_frac = ham_counts / (1 + all_counts)

    # Verify ham_frac <= 1
    max_frac = np.max(ham_frac)
    print(f"  Max ham_frac: {max_frac:.4f} (should be <= 1)")
    if max_frac > 1:
        print(f"  WARNING: ham_frac > 1 detected!")

    start_lons = np.array([b[0].lon.to_value(u.deg) for b in bins])
    end_lons = np.array([b[-1].lon.to_value(u.deg) for b in bins])

    return {
        'bins': bins,
        'ham_frac': ham_frac,
        'ham_counts': ham_counts,
        'all_counts': all_counts,
        'start_lons': start_lons,
        'end_lons': end_lons,
        'n_detections': len(hammertimes),
        'n_span_measurements': len(span_times),
    }

def save_to_json(encounters, hamstring_dir, output_path, num_days=3):
    """Process all encounters and save to JSON."""
    print(f"Processing {len(encounters)} encounters...")
    all_data = {}

    for enc in encounters:
        enc_str = f'E{enc:02d}' if enc < 10 else f'E{enc}'
        print(f"\n{'='*60}")
        print(f"Processing {enc_str}...")
        print(f"{'='*60}")

        result = process_encounter(enc, hamstring_dir, num_days)
        if not result:
            print(f"  No data for {enc_str}")
            continue

        bins_list = [{
            'start_lon': float(result['start_lons'][i]),
            'end_lon': float(result['end_lons'][i]),
            'ham_frac': float(result['ham_frac'][i]),
            'ham_count': int(result['ham_counts'][i]),
            'all_count': int(result['all_counts'][i])
        } for i in range(len(result['bins']))]

        all_data[enc_str] = {
            'n_bins': len(result['bins']),
            'n_detections': result['n_detections'],
            'n_span_measurements': result['n_span_measurements'],
            'perihelion': PERIHELION_TIMES[enc],
            'window_days': num_days,
            'bins': bins_list
        }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"\n{'='*60}")
    print(f"Saved to: {output_path}")
    print(f"{'='*60}")

if __name__ == '__main__':
    hamstring_dir = os.path.join(BASE_DIR, 'data', 'cdf_files', 'Hamstrings')
    json_output = os.path.join(BASE_DIR, 'data', 'psp', 'ham_angular_bins', 'ham_bin_data_plus_minus_3_days_corrected.json')
    save_to_json(list(range(4, 24)), hamstring_dir, json_output, num_days=3)
