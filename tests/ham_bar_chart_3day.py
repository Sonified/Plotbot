"""
Plot ham bar chart using ±3 days JSON data.
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

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


if __name__ == '__main__':
    json_path = os.path.join(BASE_DIR, 'data', 'psp', 'ham_angular_bins', 'ham_bin_data_plus_minus_3_days.json')
    output_path = os.path.join(os.path.dirname(__file__), 'ham_bar_chart_3day_E04-E23.png')

    fig, axes = plot_from_json(json_path, output_path)
    plt.show()
