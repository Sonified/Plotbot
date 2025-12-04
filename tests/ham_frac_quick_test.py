#!/usr/bin/env python
"""Quick test: verify ham_frac < 1 using pyspedas SPI L3 approach."""

import sys
import os
import glob
import re
import numpy as np
import cdflib.xarray
import xarray
import pandas as pd
from datetime import datetime
import astropy.units as u

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from sunpy.coordinates import spice, HeliographicCarrington
import pyspedas

# Initialize SPICE
kernel_files = glob.glob(os.path.join(BASE_DIR, 'data', 'psp', 'spice_data', '*.bsp'))
spice.initialize(kernel_files)
spice.install_frame('IAU_SUN')
print("SPICE ready")

# Just test E17 (has cached data)
ENC = 17
PERI = '2023/09/27 23:28:00.000'
NUM_DAYS = 3

def datetime2unix(dt_arr):
    """Convert datetime-like array to unix timestamps."""
    # Handle numpy datetime64
    if hasattr(dt_arr[0], 'timestamp'):
        return np.array([dt.timestamp() for dt in dt_arr])
    else:
        # numpy datetime64 - convert via pandas
        return pd.to_datetime(dt_arr).astype(np.int64) / 1e9

# Load ham data
print(f"\n=== Loading ham data for E{ENC} ===")
hamstring_dir = os.path.join(BASE_DIR, 'data', 'cdf_files', 'Hamstrings')
peri_dt = datetime.strptime(PERI, '%Y/%m/%d %H:%M:%S.%f')
pday = np.datetime64(peri_dt).astype('datetime64[D]')
enc_days = np.arange(pday - np.timedelta64(NUM_DAYS, 'D'), pday + np.timedelta64(NUM_DAYS + 1, 'D'))

filenames = [f for f in os.listdir(hamstring_dir) if f.startswith('hamstring_')]
filedates = {np.datetime64(re.split('[_]', f)[1]).astype('datetime64[D]'): f for f in filenames}

xrs = []
for day in enc_days:
    if day.astype('datetime64[D]') in filedates:
        xrs.append(cdflib.xarray.cdf_to_xarray(os.path.join(hamstring_dir, filedates[day.astype('datetime64[D]')])))

hamdata = xarray.concat(xrs, dim='record0')
hammertimes = list(pd.to_datetime(hamdata['epoch'].data).to_pydatetime())
print(f"Ham detections: {len(hammertimes)}")

# Get SPAN timestamps via pyspedas
tstart, tend = hammertimes[0], hammertimes[-1]
tstart_str = f'{tstart.year:04d}-{tstart.month:02d}-{tstart.day:02d}'
tend_str = f'{tend.year:04d}-{tend.month:02d}-{tend.day:02d}'
print(f"\n=== Getting SPI L3 data ===")
spi_vars = pyspedas.psp.spi(trange=[tstart_str, tend_str], datatype='spi_sf0a_l3_mom', level='l3', notplot=True)

# Find the timestamps
for k in spi_vars.keys():
    if 'x' in spi_vars[k]:
        span_times = spi_vars[k]['x']
        print(f"SPAN measurements: {len(span_times)}")
        break

# Get trajectory at SPAN times
print(f"\n=== Getting trajectory at SPAN times ===")
traj = spice.get_body('SPP', span_times)
traj_carr = traj.transform_to(HeliographicCarrington(observer='self'))

# Simple binning - just split into ~50 equal time chunks for quick test
n_bins = 50
chunk_size = len(span_times) // n_bins
print(f"Using {n_bins} bins, ~{chunk_size} SPAN points each")

ham_unix = datetime2unix(hammertimes)
span_unix = datetime2unix(span_times)

ham_counts = []
all_counts = []
for i in range(n_bins):
    start_idx = i * chunk_size
    end_idx = (i + 1) * chunk_size if i < n_bins - 1 else len(span_times)

    t_start = span_unix[start_idx]
    t_end = span_unix[end_idx - 1]

    # Count ham detections in this time range
    ham_in_bin = np.sum((ham_unix >= t_start) & (ham_unix <= t_end))
    span_in_bin = end_idx - start_idx

    ham_counts.append(ham_in_bin)
    all_counts.append(span_in_bin)

ham_counts = np.array(ham_counts)
all_counts = np.array(all_counts)
ham_frac = ham_counts / (1 + all_counts)

print(f"\n=== RESULTS ===")
print(f"Ham counts per bin: min={ham_counts.min()}, max={ham_counts.max()}, mean={ham_counts.mean():.1f}")
print(f"All counts per bin: min={all_counts.min()}, max={all_counts.max()}, mean={all_counts.mean():.1f}")
print(f"Ham fraction: min={ham_frac.min():.4f}, max={ham_frac.max():.4f}, mean={ham_frac.mean():.4f}")

if ham_frac.max() <= 1.0:
    print(f"\n✅ SUCCESS! ham_frac max = {ham_frac.max():.4f} <= 1.0")
else:
    print(f"\n❌ FAILED! ham_frac max = {ham_frac.max():.4f} > 1.0")
