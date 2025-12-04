"""
Plot ham bar chart using ±3 days JSON data.

Two modes:
1. Carrington Longitude (original) - plots bins at absolute Carrington longitude
2. Degrees from Perihelion - plots bins relative to perihelion longitude
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add plotbot to path so we can use the positional mapper
sys.path.insert(0, BASE_DIR)
from plotbot.x_axis_positional_data_helpers import PositionalDataMapper

def plot_from_json(json_path, output_path):
    """Create multi-panel bar chart from JSON data."""
    with open(json_path, 'r') as f:
        all_data = json.load(f)

    encounters = sorted(all_data.keys(), key=lambda x: int(x[1:]))
    n_enc = len(encounters)

    # Clean layout: compact but readable
    fig, axes = plt.subplots(n_enc, 1, figsize=(12, 0.5 * n_enc), sharex=True)
    fig.subplots_adjust(hspace=0.25, top=0.95, bottom=0.05, left=0.06, right=0.98)
    fig.suptitle('Hammerhead Occurrence Rate vs Carrington Longitude (±3 days)',
                 fontsize=14, fontweight='bold')

    if n_enc == 1:
        axes = [axes]

    for idx, enc_str in enumerate(encounters):
        ax = axes[idx]
        data = all_data[enc_str]

        if not data['bins']:
            ax.text(0.5, 0.5, f'{enc_str}: No data', transform=ax.transAxes,
                   ha='center', va='center')
            continue

        start_lons = np.array([b['start_lon'] for b in data['bins']])
        end_lons = np.array([b['end_lon'] for b in data['bins']])
        ham_frac = np.array([b['ham_frac'] for b in data['bins']])

        # Calculate bar widths - handle wrap-around
        raw_widths = end_lons - start_lons
        bar_widths = np.zeros_like(raw_widths)
        for i in range(len(raw_widths)):
            w = raw_widths[i]
            if w > 180:
                w = w - 360
            elif w < -180:
                w = w + 360
            bar_widths[i] = abs(w)

        # Minimum width of 1 degree
        bar_widths = np.maximum(bar_widths, 1.0)

        # Calculate bar centers
        bar_centers = (start_lons + end_lons) / 2
        for i in range(len(bar_centers)):
            if abs(end_lons[i] - start_lons[i]) > 180:
                if start_lons[i] > end_lons[i]:
                    bar_centers[i] = (start_lons[i] + end_lons[i] + 360) / 2 % 360
                else:
                    bar_centers[i] = (start_lons[i] + end_lons[i] - 360) / 2 % 360

        # Plot bars
        ax.bar(bar_centers, ham_frac, width=bar_widths,
               alpha=0.7, edgecolor='black', linewidth=0.5)

        enc_num = int(enc_str[1:])
        ax.set_ylabel(f'E{enc_num}', fontsize=9, fontweight='bold', rotation=0, labelpad=15)
        ax.set_xlim(0, 360)
        ax.grid(True, alpha=0.3, axis='x')
        ax.tick_params(axis='y', labelsize=7)

        # Add detection count
        ax.text(0.99, 0.9, f'n={data["n_detections"]}', transform=ax.transAxes,
               ha='right', va='top', fontsize=7, color='gray')

    axes[-1].set_xlabel('Carrington Longitude [degrees]')

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_path}")

    return fig, axes


def plot_degrees_from_perihelion(json_path, output_path):
    """
    Create multi-panel bar chart from JSON data, plotted in DEGREES FROM PERIHELION.

    For each encounter:
    1. Get perihelion time from JSON
    2. Map perihelion time to Carrington longitude using positional mapper
    3. Convert bin longitudes to degrees from perihelion
    4. Plot with x-axis in [-180, 180] range
    """
    with open(json_path, 'r') as f:
        all_data = json.load(f)

    # Initialize positional mapper
    positional_data_path = os.path.join(BASE_DIR, 'support_data', 'trajectories', 'psp_positional_data.npz')
    mapper = PositionalDataMapper(positional_data_path)

    if not mapper.data_loaded:
        print("ERROR: Could not load positional data!")
        return None, None

    encounters = sorted(all_data.keys(), key=lambda x: int(x[1:]))
    n_enc = len(encounters)

    # Clean layout: compact but readable
    fig, axes = plt.subplots(n_enc, 1, figsize=(14, 0.6 * n_enc), sharex=True)
    fig.subplots_adjust(hspace=0.25, top=0.95, bottom=0.05, left=0.06, right=0.98)
    fig.suptitle('Hammerhead Occurrence Rate vs Degrees from Perihelion (±3 days)',
                 fontsize=14, fontweight='bold')

    if n_enc == 1:
        axes = [axes]

    for idx, enc_str in enumerate(encounters):
        ax = axes[idx]
        data = all_data[enc_str]

        if not data['bins']:
            ax.text(0.5, 0.5, f'{enc_str}: No data', transform=ax.transAxes,
                   ha='center', va='center')
            continue

        # Get perihelion longitude for this encounter
        perihelion_str = data['perihelion']
        perihelion_dt = datetime.strptime(perihelion_str, '%Y/%m/%d %H:%M:%S.%f')
        perihelion_time_np = np.array([np.datetime64(perihelion_dt)])

        # Map perihelion time to Carrington longitude (with unwrap for consistency)
        perihelion_lon_arr = mapper.map_to_position(perihelion_time_np, 'carrington_lon', unwrap_angles=True)

        if perihelion_lon_arr is None or len(perihelion_lon_arr) == 0 or np.isnan(perihelion_lon_arr[0]):
            ax.text(0.5, 0.5, f'{enc_str}: Could not map perihelion', transform=ax.transAxes,
                   ha='center', va='center')
            print(f"WARNING: Could not map perihelion for {enc_str}")
            continue

        perihelion_lon = perihelion_lon_arr[0]

        # Extract bin data
        start_lons = np.array([b['start_lon'] for b in data['bins']])
        end_lons = np.array([b['end_lon'] for b in data['bins']])
        ham_frac = np.array([b['ham_frac'] for b in data['bins']])

        # Calculate bin centers in absolute Carrington longitude
        # Handle wrap-around cases
        bar_centers_abs = np.zeros(len(start_lons))
        for i in range(len(start_lons)):
            if abs(end_lons[i] - start_lons[i]) > 180:
                # Wrap-around case
                if start_lons[i] > end_lons[i]:
                    bar_centers_abs[i] = (start_lons[i] + end_lons[i] + 360) / 2
                else:
                    bar_centers_abs[i] = (start_lons[i] + end_lons[i] - 360) / 2
            else:
                bar_centers_abs[i] = (start_lons[i] + end_lons[i]) / 2

        # Convert to degrees from perihelion
        # degrees_from_peri = bin_lon - perihelion_lon
        degrees_from_peri = bar_centers_abs - perihelion_lon

        # Wrap to [-180, 180]
        degrees_from_peri = (degrees_from_peri + 180) % 360 - 180

        # Calculate bar widths
        raw_widths = end_lons - start_lons
        bar_widths = np.zeros_like(raw_widths)
        for i in range(len(raw_widths)):
            w = raw_widths[i]
            if w > 180:
                w = w - 360
            elif w < -180:
                w = w + 360
            bar_widths[i] = abs(w)

        # Minimum width of 1 degree
        bar_widths = np.maximum(bar_widths, 1.0)

        # Plot bars
        ax.bar(degrees_from_peri, ham_frac, width=bar_widths,
               alpha=0.7, edgecolor='black', linewidth=0.5, color='steelblue')

        enc_num = int(enc_str[1:])
        ax.set_ylabel(f'E{enc_num}', fontsize=9, fontweight='bold', rotation=0, labelpad=15)
        ax.set_xlim(-180, 180)
        ax.grid(True, alpha=0.3, axis='x')
        ax.tick_params(axis='y', labelsize=7)

        # Add vertical line at 0 (perihelion)
        ax.axvline(x=0, color='red', linestyle='--', linewidth=1, alpha=0.7)

        # Add detection count and perihelion lon
        ax.text(0.99, 0.9, f'n={data["n_detections"]}', transform=ax.transAxes,
               ha='right', va='top', fontsize=7, color='gray')
        ax.text(0.01, 0.9, f'peri_lon={perihelion_lon:.1f}°', transform=ax.transAxes,
               ha='left', va='top', fontsize=6, color='gray')

    axes[-1].set_xlabel('Degrees from Perihelion [°]')

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_path}")

    return fig, axes


if __name__ == '__main__':
    json_path = os.path.join(BASE_DIR, 'data', 'psp', 'ham_angular_bins', 'ham_bin_data_plus_minus_3_days.json')

    # Generate both plots
    print("=" * 60)
    print("Generating Carrington Longitude plot...")
    print("=" * 60)
    output_path_carrington = os.path.join(os.path.dirname(__file__), 'ham_bar_chart_3day_carrington.png')
    fig1, axes1 = plot_from_json(json_path, output_path_carrington)

    print("\n" + "=" * 60)
    print("Generating Degrees from Perihelion plot...")
    print("=" * 60)
    output_path_degrees = os.path.join(os.path.dirname(__file__), 'ham_bar_chart_3day_degrees_from_perihelion.png')
    fig2, axes2 = plot_degrees_from_perihelion(json_path, output_path_degrees)

    print("\n" + "=" * 60)
    print("Done! Generated:")
    print(f"  1. {output_path_carrington}")
    print(f"  2. {output_path_degrees}")
    print("=" * 60)

    # plt.show()  # Commented out for headless operation
