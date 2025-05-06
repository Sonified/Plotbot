import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pathlib
from datetime import datetime, timedelta
from plotbot.x_axis_positional_data_helpers import XAxisPositionalDataMapper

PERIHELION_TIMES = {
    1: '2018/11/06 03:27:00.000', 2: '2019/04/04 22:39:00.000', 3: '2019/09/01 17:50:00.000',
    4: '2020/01/29 09:37:00.000', 5: '2020/06/07 08:23:00.000', 6: '2020/09/27 09:16:00.000',
    7: '2021/01/17 17:40:00.000', 8: '2021/04/29 08:48:00.000', 9: '2021/08/09 19:11:00.000',
    10: '2021/11/21 08:23:00.000', 11: '2022/02/25 15:38:00.000', 12: '2022/06/01 22:51:00.000',
    13: '2022/09/06 06:04:00.000', 14: '2022/12/11 13:16:00.000', 15: '2023/03/17 20:30:00.000',
    16: '2023/06/22 03:46:00.000', 17: '2023/09/27 23:28:00.000', 18: '2023/12/29 00:56:00.000',
    19: '2024/03/30 02:21:00.000', 20: '2024/06/30 03:47:00.000', 21: '2024/09/30 05:15:00.000',
    22: '2024/12/24 11:53:00.000', 23: '2025/03/22 22:42:00.000',
}

def test_print_debug():
    print("PRINT DEBUG WORKS", flush=True)

def test_plot_perihelion_windows():
    npz_path = pathlib.Path(__file__).parent.parent / "support_data" / "trajectories" / "Parker_positional_data.npz"
    assert npz_path.exists(), f"NPZ file not found: {npz_path}"
    mapper = XAxisPositionalDataMapper(str(npz_path))
    with np.load(npz_path) as data:
        times = pd.to_datetime(data['times'])
        # carr_lon = data['carrington_lon']  # No longer needed directly
    
    # Use E21 which crosses the 0°/360° boundary to properly test the fix
    encounters = [21]
    fig, axes = plt.subplots(len(encounters), 1, figsize=(14, 4), sharex=False)
    
    hour_offsets = np.arange(-12, 13, 2)
    
    if len(encounters) == 1:
        axs = [axes]
    
    for i, enc in enumerate(encounters):
        peri_time = pd.to_datetime(PERIHELION_TIMES[enc])
        print(f"\n================= E{enc} ({PERIHELION_TIMES[enc]}) =================", flush=True)
        # Generate timestamps at perihelion ± multiples of 10 hours
        sample_times = [peri_time + pd.Timedelta(hours=dt) for dt in hour_offsets]
        sample_times_np = np.array([np.datetime64(t) for t in sample_times])
        peri_time_np = np.array([np.datetime64(peri_time)])
        # Use the robust longitude mapping with unwrapping
        interp_lons = mapper.map_to_position(sample_times_np, 'carrington_lon', unwrap_angles=True)
        perihelion_lon = mapper.map_to_position(peri_time_np, 'carrington_lon', unwrap_angles=True)[0]
        deg_from_peri = interp_lons - perihelion_lon
        # No need to wrap, since unwrapped is continuous and centered
        print(f"{'Offset (hr)':>12} | {'Timestamp':>24} | {'Longitude':>12} | {'Deg from Peri':>15}", flush=True)
        print("-"*70, flush=True)
        for dt, t, lon, deg in zip(hour_offsets, sample_times, interp_lons, deg_from_peri):
            print(f"{dt:12.1f} | {t} | {lon:12.4f} | {deg:15.4f}", flush=True)
        # Plot
        ax = axs[i]
        ax.plot(hour_offsets, deg_from_peri, marker='o', color='green', label='Deg from Perihelion (unwrapped)')
        ax.axvline(0, color='r', linestyle='--', linewidth=1, label='Perihelion (0 hr)')
        ax.axhline(0, color='k', linestyle=':', linewidth=1)
        ax.set_xlabel('Hours from Perihelion', fontsize=13)
        ax.set_ylabel(f"E{enc}\n{PERIHELION_TIMES[enc]}", fontsize=11, rotation=0, labelpad=50, va='center')
        ax.set_title(f"E{enc} - Degrees from Perihelion (Unwrapped) - {PERIHELION_TIMES[enc]}", fontsize=13)
        ax.grid(True)
        ax.legend(loc='upper right')
        
    axs[0].set_xlabel("Hours from Perihelion", fontsize=13)
    
    plt.tight_layout()
    
    # Print final diagnostic message
    print("\n==== FINAL CHECK ====", flush=True)
    print("Zero offset (0 hr) should correspond to exactly zero degrees from perihelion.", flush=True)
    
    plt.show()
    plt.close(fig) 