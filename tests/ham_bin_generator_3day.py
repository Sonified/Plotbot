"""
Generate ham bin data using:
- Our PERIHELION_TIMES table
- SPICE trajectory (Srijan's approach)
- ±3 days from perihelion
"""

import sys
import os
import glob
import re
import json
import time
import numpy as np
import cdflib
import cdflib.xarray
import xarray
import pandas as pd
from datetime import datetime, timedelta
import astropy.units as u

print(f"[{time.time():.1f}] Imports done, about to import sunpy.coordinates...")
sys.stdout.flush()

from sunpy.coordinates import spice, HeliographicCarrington

print(f"[{time.time():.1f}] sunpy.coordinates imported")
sys.stdout.flush()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Initialize SPICE
spice_kernel_dir = os.path.join(BASE_DIR, 'data', 'psp', 'spice_data')
kernel_files = glob.glob(os.path.join(spice_kernel_dir, '*.bsp'))
print(f"[{time.time():.1f}] Loading {len(kernel_files)} SPICE kernel files...")
sys.stdout.flush()
spice.initialize(kernel_files)
print(f"[{time.time():.1f}] SPICE initialized")
sys.stdout.flush()
spice.install_frame('IAU_SUN')
print(f"[{time.time():.1f}] IAU_SUN frame installed")
sys.stdout.flush()

# Our perihelion times
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
    return np.array([d.timestamp() for d in dt_arr])

def gen_dt_arr(tstart, tend, cadence_days):
    dt_arr = []
    current = tstart
    delta = timedelta(days=cadence_days)
    while current <= tend:
        dt_arr.append(current)
        current += delta
    return dt_arr

def get_trajectory_from_spice(tstart, tend, cadence_days=1/(12*24)):
    dt_arr = gen_dt_arr(tstart, tend, cadence_days)
    trajectory = spice.get_body('SPP', dt_arr)
    return dt_arr, trajectory

def bin_by_angular_separation(coords, max_sep_deg):
    max_sep_deg = float(max_sep_deg)
    lon = coords.lon.to_value(u.rad)
    lat = coords.lat.to_value(u.rad)
    valid = np.isfinite(lon) & np.isfinite(lat)
    n = lon.size
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
    hammer_unix = datetime2unix(hammertimes)
    bin_start_unix = np.array([b.obstime[0].to_datetime().timestamp() for b in bins])
    bin_end_unix = np.array([b.obstime[-1].to_datetime().timestamp() for b in bins])
    left_idx = np.searchsorted(hammer_unix, bin_start_unix, side='left')
    right_idx = np.searchsorted(hammer_unix, bin_end_unix, side='right')
    return right_idx - left_idx, np.array([len(b) for b in bins])

def load_ham_data(enc, hamstring_dir, num_days=3):
    print(f"    [load_ham_data] ENTERING for enc={enc}")
    sys.stdout.flush()
    t0 = time.time()
    peri_str = PERIHELION_TIMES[enc]
    print(f"    [load_ham_data] peri_str={peri_str}")
    sys.stdout.flush()
    peri_dt = datetime.strptime(peri_str, '%Y/%m/%d %H:%M:%S.%f')
    pday = np.datetime64(peri_dt).astype('datetime64[D]')  # MUST cast to day precision!
    enc_days = np.arange(pday - np.timedelta64(num_days, 'D'), pday + np.timedelta64(num_days + 1, 'D'))
    print(f"    [load_ham_data] enc_days calculated")
    sys.stdout.flush()
    filenames = [f for f in os.listdir(hamstring_dir) if f.startswith('hamstring_')]
    print(f"    [load_ham_data] {len(filenames)} files found")
    sys.stdout.flush()
    filedates = {np.datetime64(re.split('[_]', f)[1]).astype('datetime64[D]'): f for f in filenames}
    xrs = []
    print(f"    [load_ham_data] Looking for {len(enc_days)} days of data...")
    sys.stdout.flush()
    for day in enc_days:
        day_d = day.astype('datetime64[D]')
        if day_d in filedates:
            print(f"    [load_ham_data] Loading {filedates[day_d]}...")
            sys.stdout.flush()
            xrs.append(cdflib.xarray.cdf_to_xarray(os.path.join(hamstring_dir, filedates[day_d])))
    if not xrs:
        return None, None
    print(f"    [load_ham_data] Concatenating {len(xrs)} files...")
    sys.stdout.flush()
    hamdata = xarray.concat(xrs, dim='record0')
    print(f"    [load_ham_data] Done in {time.time()-t0:.2f}s")
    sys.stdout.flush()
    return hamdata, list(pd.to_datetime(hamdata['epoch'].data).to_pydatetime())

def process_encounter(enc, hamstring_dir, num_days=3):
    hamdata, hammertimes = load_ham_data(enc, hamstring_dir, num_days)
    if not hammertimes:
        return None
    print(f"  {len(hammertimes)} ham detections")
    sys.stdout.flush()
    tstart, tend = hammertimes[0], hammertimes[-1]

    t0 = time.time()
    print(f"    [process] Getting trajectory from SPICE...")
    sys.stdout.flush()
    dt_traj, trajectory = get_trajectory_from_spice(tstart, tend)
    print(f"    [process] SPICE trajectory done in {time.time()-t0:.2f}s ({len(dt_traj)} points)")
    sys.stdout.flush()

    t0 = time.time()
    print(f"    [process] Transforming to Carrington...")
    sys.stdout.flush()
    traj_carr = trajectory.transform_to(HeliographicCarrington(observer='self'))
    print(f"    [process] Transform done in {time.time()-t0:.2f}s")
    sys.stdout.flush()

    t0 = time.time()
    print(f"    [process] Binning by angular separation...")
    sys.stdout.flush()
    bins = bin_by_angular_separation(traj_carr, max_sep_deg=1.0)
    print(f"    [process] Binning done in {time.time()-t0:.2f}s ({len(bins)} bins)")
    sys.stdout.flush()

    ham_counts, all_counts = count_ham_in_bins(hammertimes, bins)
    ham_frac = ham_counts / (1 + all_counts)
    start_lons = np.array([b[0].lon.value for b in bins])
    end_lons = np.array([b[-1].lon.value for b in bins])
    return {'bins': bins, 'ham_frac': ham_frac, 'ham_counts': ham_counts, 'all_counts': all_counts,
            'start_lons': start_lons, 'end_lons': end_lons, 'n_detections': len(hammertimes)}

def save_to_json(encounters, hamstring_dir, output_path, num_days=3):
    print(f"[{time.time():.1f}] Starting save_to_json with {len(encounters)} encounters...")
    sys.stdout.flush()
    all_data = {}
    for enc in encounters:
        enc_str = f'E{enc:02d}' if enc < 10 else f'E{enc}'
        print(f"\n[{time.time():.1f}] Processing {enc_str}...")
        sys.stdout.flush()
        result = process_encounter(enc, hamstring_dir, num_days)
        if not result:
            continue
        bins_list = [{'start_lon': float(result['start_lons'][i]), 'end_lon': float(result['end_lons'][i]),
                      'ham_frac': float(result['ham_frac'][i]), 'ham_count': int(result['ham_counts'][i]),
                      'all_count': int(result['all_counts'][i])} for i in range(len(result['bins']))]
        all_data[enc_str] = {'n_bins': len(result['bins']), 'n_detections': result['n_detections'],
                             'perihelion': PERIHELION_TIMES[enc], 'window_days': num_days, 'bins': bins_list}
        print(f"  {len(result['bins'])} bins")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"\nSaved to: {output_path}")

if __name__ == '__main__':
    hamstring_dir = os.path.join(BASE_DIR, 'data', 'cdf_files', 'Hamstrings')
    json_output = os.path.join(BASE_DIR, 'data', 'psp', 'ham_angular_bins', 'ham_bin_data_plus_minus_3_days.json')
    save_to_json(list(range(4, 24)), hamstring_dir, json_output, num_days=3)
