"""
Test script to create bar chart visualization of hammerhead occurrence rate
vs Carrington longitude, using Srijan's angular binning approach.

FAST VERSION - only uses SPICE for trajectory, no pyspedas downloads.

For encounters 18-23 initially.
"""

import sys
import os
import glob
import re

import json
import numpy as np
import matplotlib.pyplot as plt
import cdflib
import cdflib.xarray
import xarray
import pandas as pd
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import astropy.units as u
from astropy.coordinates import SkyCoord

# Get the base path for the project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Initialize SPICE
from sunpy.coordinates import spice, HeliographicCarrington
spice_kernel_dir = os.path.join(BASE_DIR, 'data', 'psp', 'spice_data')
kernel_files = glob.glob(os.path.join(spice_kernel_dir, '*.bsp'))
print(f"Loading {len(kernel_files)} SPICE kernel files from {spice_kernel_dir}")
spice.initialize(kernel_files)
spice.install_frame('IAU_SUN')

# Encounter perihelion dates (from srijan/encounters.py)
ENCOUNTER_DATES = {
    4: '2020-01-29', 5: '2020-06-07', 6: '2020-09-27', 7: '2021-01-17',
    8: '2021-04-28', 9: '2021-08-09', 10: '2021-11-21', 11: '2022-02-25',
    12: '2022-06-01', 13: '2022-09-06', 14: '2022-12-11', 15: '2023-03-17',
    16: '2023-06-22', 17: '2023-09-27', 18: '2023-12-29', 19: '2024-03-30',
    20: '2024-06-30', 21: '2024-09-30', 22: '2024-12-24', 23: '2025-03-22',
}


def datetime2unix(dt_arr):
    """Convert datetime array to unix timestamps."""
    return np.array([d.timestamp() for d in dt_arr])


def gen_dt_arr(tstart, tend, cadence_days):
    """Generate datetime array at given cadence."""
    dt_arr = []
    current = tstart
    delta = timedelta(days=cadence_days)
    while current <= tend:
        dt_arr.append(current)
        current += delta
    return dt_arr


def get_trajectory_from_spice(tstart, tend, cadence_days=1/(12*24)):
    """Get PSP trajectory using only SPICE (no data downloads)."""
    dt_arr = gen_dt_arr(tstart, tend, cadence_days)
    trajectory = spice.get_body('SPP', dt_arr)  # SPP = Solar Probe Plus (Parker)
    return dt_arr, trajectory


def bin_by_angular_separation(coords, max_sep_deg):
    """
    Group coordinates into bins where all points are within max_sep_deg
    of the first point in that bin.

    Simplified version of Srijan's bin_by_angular_separation_fast.
    """
    max_sep_deg = float(max_sep_deg)

    lon = coords.lon.to_value(u.rad)
    lat = coords.lat.to_value(u.rad)

    valid = np.isfinite(lon) & np.isfinite(lat)
    n = lon.size
    bins = []
    bin_idx = np.zeros(len(lon), dtype='int')
    bin_count = 1

    i = 0
    while i < n:
        if not valid[i]:
            i += 1
            continue

        # Find end of valid block
        j = i + 1
        while j < n and valid[j]:
            j += 1

        start = i
        while start < j:
            ref_lon = lon[start]
            ref_lat = lat[start]

            lon_block = lon[start:j]
            lat_block = lat[start:j]

            dlon = lon_block - ref_lon
            dlat = lat_block - ref_lat

            # Haversine formula
            sin_dlat2 = np.sin(dlat * 0.5)**2
            sin_dlon2 = np.sin(dlon * 0.5)**2
            a = sin_dlat2 + np.cos(ref_lat) * np.cos(lat_block) * sin_dlon2
            a = np.clip(a, 0.0, 1.0)
            angle_rad = 2.0 * np.arcsin(np.sqrt(a))
            angle_deg = np.rad2deg(angle_rad)

            too_far_idx = np.where(angle_deg > max_sep_deg)[0]
            if too_far_idx.size == 0:
                end = j
            else:
                end = start + too_far_idx[0]

            bins.append(coords[start:end])
            bin_idx[start:end] = bin_count
            bin_count += 1

            start = end

        i = j

    return bins, bin_idx


def count_ham_in_bins(hammertimes, bins):
    """Count hammerhead detections in each bin."""
    hammer_unix = datetime2unix(hammertimes)

    bin_start_unix = np.array([
        bins[i].obstime[0].to_datetime().timestamp()
        for i in range(len(bins))
    ])
    bin_end_unix = np.array([
        bins[i].obstime[-1].to_datetime().timestamp()
        for i in range(len(bins))
    ])

    left_idx = np.searchsorted(hammer_unix, bin_start_unix, side='left')
    right_idx = np.searchsorted(hammer_unix, bin_end_unix, side='right')

    ham_counts = right_idx - left_idx
    all_counts = np.array([len(bins[i]) for i in range(len(bins))])

    return ham_counts, all_counts


def load_ham_data_for_encounter(enc, hamstring_dir, num_days=10):
    """Load hammerhead CDF data for a given encounter."""
    pday = np.datetime64(ENCOUNTER_DATES[enc])
    enc_days = np.arange(
        pday - np.timedelta64(num_days, 'D'),
        pday + np.timedelta64(num_days + 1, 'D')
    )

    filenames = [f for f in os.listdir(hamstring_dir) if f.startswith('hamstring_')]
    filedates = {
        np.datetime64(re.split('[_]', f)[1]).astype('datetime64[D]'): f
        for f in filenames
    }

    xrs = []
    for day in enc_days:
        day_d = day.astype('datetime64[D]')
        if day_d in filedates:
            filepath = os.path.join(hamstring_dir, filedates[day_d])
            xr = cdflib.xarray.cdf_to_xarray(filepath)
            xrs.append(xr)

    if not xrs:
        return None, None

    hamdata = xarray.concat(xrs, dim='record0')
    hammertimes = pd.to_datetime(hamdata['epoch'].data).to_pydatetime()

    return hamdata, list(hammertimes)


def process_encounter(enc, hamstring_dir, num_days=10):
    """Process one encounter - get bins and ham fractions."""
    print(f"  Loading ham data...")
    hamdata, hammertimes = load_ham_data_for_encounter(enc, hamstring_dir, num_days)

    if hammertimes is None or len(hammertimes) == 0:
        return None

    print(f"  {len(hammertimes)} hammerhead detections")

    # Get trajectory from SPICE (no downloads!)
    tstart = hammertimes[0]
    tend = hammertimes[-1]

    print(f"  Getting trajectory from SPICE...")
    dt_traj, trajectory = get_trajectory_from_spice(tstart, tend, cadence_days=1/(12*24))

    # Convert trajectory to HeliographicCarrington
    traj_carr = trajectory.transform_to(HeliographicCarrington(observer='self'))

    print(f"  Binning {len(traj_carr)} trajectory points...")
    bins, bin_idx = bin_by_angular_separation(traj_carr, max_sep_deg=1.0)

    print(f"  Counting hammerheads in {len(bins)} bins...")
    ham_counts, all_counts = count_ham_in_bins(hammertimes, bins)

    # Calculate fraction
    ham_frac = ham_counts / (1 + all_counts)

    # Extract bin boundaries
    start_lons = np.array([bins[i][0].lon.value for i in range(len(bins))])
    end_lons = np.array([bins[i][-1].lon.value for i in range(len(bins))])

    return {
        'bins': bins,
        'ham_frac': ham_frac,
        'ham_counts': ham_counts,
        'all_counts': all_counts,
        'start_lons': start_lons,
        'end_lons': end_lons,
        'n_detections': len(hammertimes),
    }


def plot_ham_bar_chart(encounters_to_plot, hamstring_dir):
    """Create multi-panel bar chart."""
    n_enc = len(encounters_to_plot)

    fig, axes = plt.subplots(n_enc, 1, figsize=(14, 1.5 * n_enc), sharex=False)
    fig.subplots_adjust(hspace=0.4)
    fig.suptitle('Raw bin output per encounter', fontsize=14, fontweight='bold', y=1.02)
    if n_enc == 1:
        axes = [axes]

    for idx, enc in enumerate(encounters_to_plot):
        ax = axes[idx]
        enc_str = f'E{enc:02d}' if enc < 10 else f'E{enc}'

        print(f"\nProcessing {enc_str}...")

        result = process_encounter(enc, hamstring_dir)

        if result is None:
            ax.text(0.5, 0.5, f'{enc_str}: No data', transform=ax.transAxes,
                   ha='center', va='center')
            continue

        start_lons = result['start_lons']
        end_lons = result['end_lons']
        ham_frac = result['ham_frac']

        # Debug dump for E18
        if enc == 18:
            print(f"\n=== DEBUG DUMP FOR E18 ===")
            print(f"Longitude range: {start_lons.min():.2f} to {start_lons.max():.2f}")
            print(f"First 10 bins:")
            for i in range(min(10, len(start_lons))):
                print(f"  Bin {i}: {start_lons[i]:.2f} -> {end_lons[i]:.2f}")
            print(f"Last 10 bins:")
            for i in range(max(0, len(start_lons)-10), len(start_lons)):
                print(f"  Bin {i}: {start_lons[i]:.2f} -> {end_lons[i]:.2f}")
            print(f"=== END DEBUG ===\n")

        # Calculate bar widths - use absolute value since trajectory can go either direction
        # Only treat as wrap-around if the angular distance is large (> 180°)
        raw_widths = end_lons - start_lons

        bar_widths = np.zeros_like(raw_widths)
        for i in range(len(raw_widths)):
            w = raw_widths[i]
            if w > 180:
                # Wrap case: end near 0, start near 360
                w = w - 360
            elif w < -180:
                # Wrap case: start near 0, end near 360
                w = w + 360
            bar_widths[i] = abs(w)

        # Single-point bins get minimum width of 1 degree
        min_width = 1.0
        bar_widths = np.maximum(bar_widths, min_width)

        # Calculate bar centers as midpoint of start and end
        bar_centers = (start_lons + end_lons) / 2

        # Handle wrap-around for center calculation
        for i in range(len(bar_centers)):
            if abs(end_lons[i] - start_lons[i]) > 180:
                # Wrap case - calculate center properly
                if start_lons[i] > end_lons[i]:
                    bar_centers[i] = (start_lons[i] + end_lons[i] + 360) / 2 % 360
                else:
                    bar_centers[i] = (start_lons[i] + end_lons[i] - 360) / 2 % 360

        # Plot bars
        ax.bar(bar_centers, ham_frac, width=bar_widths,
               alpha=0.7, edgecolor='black', linewidth=0.5)

        ax.set_ylabel(f'$\\mathbf{{E{enc}}}$', fontsize=12, rotation=0, labelpad=20)
        ax.set_xlim(0, 360)
        ax.grid(True, alpha=0.3)

        print(f"  Done! {len(result['bins'])} bins")

    axes[-1].set_xlabel('Carrington Longitude [degrees]')
    plt.tight_layout()

    return fig, axes


def save_bin_data_to_json(encounters, hamstring_dir, output_path):
    """Compute and save all bin data to JSON for fast loading later."""
    all_data = {}

    for enc in encounters:
        enc_str = f'E{enc:02d}' if enc < 10 else f'E{enc}'
        print(f"Processing {enc_str}...")

        result = process_encounter(enc, hamstring_dir)
        if result is None:
            continue

        bins_list = []
        for i in range(len(result['bins'])):
            bins_list.append({
                'start_lon': result['start_lons'][i],
                'end_lon': result['end_lons'][i],
                'ham_frac': result['ham_frac'][i],
                'ham_count': int(result['ham_counts'][i]),
                'all_count': int(result['all_counts'][i]),
            })

        all_data[enc_str] = {
            'n_bins': len(result['bins']),
            'n_detections': result['n_detections'],
            'bins': bins_list,
        }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(all_data, f, indent=2)

    print(f"\nSaved bin data to: {output_path}")
    return all_data


if __name__ == '__main__':
    hamstring_dir = os.path.join(BASE_DIR, 'data', 'cdf_files', 'Hamstrings')
    print(f"Ham data directory: {hamstring_dir}")

    if not os.path.exists(hamstring_dir):
        print(f"ERROR: Directory not found: {hamstring_dir}")
        sys.exit(1)

    encounters_to_plot = list(range(4, 24))  # E04 through E23

    # Save bin data to JSON
    json_output = os.path.join(BASE_DIR, 'data', 'psp', 'ham_angular_bins', 'ham_bin_data.json')
    save_bin_data_to_json(encounters_to_plot, hamstring_dir, json_output)

    # Plot
    fig, axes = plot_ham_bar_chart(encounters_to_plot, hamstring_dir)

    output_path = os.path.join(os.path.dirname(__file__), 'ham_bar_chart_all_encounters.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved figure to: {output_path}")

    plt.show()
