from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dateutil.parser import parse
import pathlib

# --- BEGIN: Perihelion Time Lookup Logic (mirrored from multiplot.py/utils.py) ---
PERIHELION_TIMES = {
    1: '2018/11/06 03:27:00.000',
    2: '2019/04/04 22:39:00.000',
    3: '2019/09/01 17:50:00.000',
    4: '2020/01/29 09:37:00.000',
    5: '2020/06/07 08:23:00.000',
    6: '2020/09/27 09:16:00.000',
    7: '2021/01/17 17:40:00.000',
    8: '2021/04/29 08:48:00.000',
    9: '2021/08/09 19:11:00.000',
    10: '2021/11/21 08:23:00.000',
    11: '2022/02/25 15:38:00.000',
    12: '2022/06/01 22:51:00.000',
    13: '2022/09/06 06:04:00.000',
    14: '2022/12/11 13:16:00.000',
    15: '2023/03/17 20:30:00.000',
    16: '2023/06/22 03:46:00.000',
    17: '2023/09/27 23:28:00.000',
    18: '2023/12/29 00:56:00.000',
    19: '2024/03/30 02:21:00.000',
    20: '2024/06/30 03:47:00.000',
    21: '2024/09/30 05:15:00.000',
    22: '2024/12/24 11:53:00.000',
    23: '2025/03/22 22:42:00.000',
}

def get_encounter_number(start_date):
    date = datetime.strptime(start_date, '%Y-%m-%d')
    encounters = {
        'E1': datetime(2018, 10, 31),
        'E2': datetime(2019, 3, 30),
        'E3': datetime(2019, 8, 27),
        'E4': datetime(2020, 1, 23),
        'E5': datetime(2020, 6, 7),
        'E6': datetime(2020, 9, 27),
        'E7': datetime(2021, 1, 17),
        'E8': datetime(2021, 4, 29),
        'E9': datetime(2021, 8, 9),
        'E10': datetime(2021, 11, 21),
        'E11': datetime(2022, 2, 25),
        'E12': datetime(2022, 6, 1),
        'E13': datetime(2022, 9, 6),
        'E14': datetime(2023, 1, 1),
        'E15': datetime(2023, 4, 10),
        'E16': datetime(2023, 6, 17),
        'E17': datetime(2023, 9, 27),
        'E18': datetime(2024, 1, 4)
    }
    closest_encounter = None
    min_diff = float('inf')
    for encounter, encounter_date in encounters.items():
        diff = (date - encounter_date).total_seconds()
        if 0 <= diff < min_diff:
            min_diff = diff
            closest_encounter = encounter
    return closest_encounter

def str_to_datetime(date_str):
    try:
        return parse(date_str)
    except (ValueError, TypeError):
        print(f"[WARNING] Could not parse date string: {date_str}")
        return None

def get_perihelion_time(center_time):
    if isinstance(center_time, str):
        center_dt = str_to_datetime(center_time)
        if center_dt is None:
            print(f"[ERROR] Invalid center_time format: {center_time}. Cannot determine perihelion.")
            return None
    elif isinstance(center_time, np.datetime64):
        center_dt = pd.Timestamp(center_time).to_pydatetime()
    elif isinstance(center_time, datetime):
        center_dt = center_time
    else:
        print(f"[ERROR] Unsupported center_time type: {type(center_time)}. Expected string, datetime, or numpy.datetime64.")
        return None
    try:
        center_date_str = center_dt.strftime('%Y-%m-%d')
        enc_num_str = get_encounter_number(center_date_str)
        if enc_num_str:
            enc_num = int(enc_num_str[1:])
            peri_time = PERIHELION_TIMES.get(enc_num)
            if peri_time:
                print(f"[DEBUG] Found perihelion time {peri_time} for encounter {enc_num}")
                return peri_time
            else:
                print(f"[WARNING] Perihelion time not defined for encounter {enc_num}.")
                return None
        else:
            print(f"[WARNING] Could not determine encounter number for date {center_date_str}.")
            return None
    except Exception as e:
        print(f"[ERROR] Error determining encounter or looking up perihelion time: {e}")
        return None
# --- END: Perihelion Time Lookup Logic ---

def resolve_data_path(data_path):
    path = pathlib.Path(data_path)
    if not path.is_absolute():
        resolved_path = pathlib.Path.cwd() / path
        if resolved_path.exists():
            return str(resolved_path.resolve())
        else:
            print(f"[WARNING] Relative path {path} not found relative to CWD. Trying as is.")
            return str(path)
    return str(path.resolve())

def load_parker_positional_data(data_path):
    data_path = resolve_data_path(data_path)
    print(f"[DEBUG] Loading Parker positional data from: {data_path}")
    with np.load(data_path) as data:
        print(f"[DEBUG] Keys in NPZ file: {list(data.keys())}")
        times_raw = data['times']
        r_sun = data['r_sun'] if 'r_sun' in data else None
        carrington_lon = data['carrington_lon'] if 'carrington_lon' in data else None
        carrington_lat = data['carrington_lat'] if 'carrington_lat' in data else None
        if r_sun is None:
            print("[WARNING] 'r_sun' key missing in NPZ file.")
        if carrington_lon is None:
            print("[WARNING] 'carrington_lon' key missing in NPZ file.")
        if carrington_lat is None:
            print("[WARNING] 'carrington_lat' key missing in NPZ file.")
        print(f"[DEBUG] times_raw shape: {times_raw.shape}, dtype: {times_raw.dtype}")
        print(f"[DEBUG] r_sun shape: {None if r_sun is None else r_sun.shape}, dtype: {None if r_sun is None else r_sun.dtype}")
        print(f"[DEBUG] carrington_lon shape: {None if carrington_lon is None else carrington_lon.shape}, dtype: {None if carrington_lon is None else carrington_lon.dtype}")
        print(f"[DEBUG] carrington_lat shape: {None if carrington_lat is None else carrington_lat.shape}, dtype: {None if carrington_lat is None else carrington_lat.dtype}")
    datetime_array_pd = pd.to_datetime(times_raw, utc=True).tz_convert(None)
    datetime_array_np = datetime_array_pd.to_numpy()
    times_numeric = datetime_array_np.astype(np.int64) / 1e9
    print(f"[DEBUG] times_raw (first 3): {times_raw[:3]}")
    print(f"[DEBUG] times_raw (last 3): {times_raw[-3:]}")
    print(f"[DEBUG] times_numeric (first 3): {times_numeric[:3]}")
    print(f"[DEBUG] times_numeric (last 3): {times_numeric[-3:]}")
    if carrington_lon is not None:
        print(f"[DEBUG] carrington_lon (first 3): {carrington_lon[:3]}")
        print(f"[DEBUG] carrington_lon (last 3): {carrington_lon[-3:]}")
    if carrington_lat is not None:
        print(f"[DEBUG] carrington_lat (first 3): {carrington_lat[:3]}")
        print(f"[DEBUG] carrington_lat (last 3): {carrington_lat[-3:]}")
    return {
        'times_numeric': times_numeric,
        'r_sun': r_sun,
        'carrington_lon': carrington_lon,
        'carrington_lat': carrington_lat
    }

def map_to_position(datetime_array, data_type, data_dict):
    if data_type == 'r_sun':
        positional_values = data_dict['r_sun']
        data_units = "R_sun"
    elif data_type == 'carrington_lon':
        positional_values = data_dict['carrington_lon']
        data_units = "deg"
    elif data_type == 'carrington_lat':
        positional_values = data_dict['carrington_lat']
        data_units = "deg"
    else:
        print(f"[WARNING] Invalid data_type: {data_type}. Must be 'r_sun', 'carrington_lon', or 'carrington_lat'.")
        return None
    if positional_values is None:
        print(f"[WARNING] No {data_type} data available in the loaded positional data file.")
        return None
    if not isinstance(datetime_array, np.ndarray) or datetime_array.ndim == 0:
        try:
            datetime_array = np.array([datetime_array])
            print(f"[DEBUG] Converted scalar/0-dim input to 1-element array. New shape: {datetime_array.shape}")
        except Exception as e:
            print(f"[WARNING] Could not convert input {type(datetime_array)} to a NumPy array: {e}")
            return None
    if not np.issubdtype(datetime_array.dtype, np.datetime64):
        print(f"[DEBUG] Input array has dtype {datetime_array.dtype}, attempting to convert to datetime64")
        try:
            datetime_array = pd.to_datetime(datetime_array).to_numpy()
            print(f"[DEBUG] Successfully converted input to datetime64 format")
        except Exception as e:
            print(f"[WARNING] Failed to convert input to datetime64: {str(e)}")
            return None
    if len(datetime_array) == 0:
        print(f"[DEBUG] Input datetime_array is empty, returning empty positional array.")
        return np.array([])
    science_times_numeric = datetime_array.astype(np.int64) / 1e9
    min_time = np.min(science_times_numeric)
    max_time = np.max(science_times_numeric)
    min_ref_time = np.min(data_dict['times_numeric'])
    max_ref_time = np.max(data_dict['times_numeric'])
    print(f"[DEBUG] Position mapping time ranges:")
    print(f"  Input data: {pd.to_datetime(min_time * 1e9)} to {pd.to_datetime(max_time * 1e9)}")
    print(f"  Reference data: {pd.to_datetime(min_ref_time * 1e9)} to {pd.to_datetime(max_ref_time * 1e9)}")
    if min_time < min_ref_time or max_time > max_ref_time:
        print(f"[WARNING] Input time range extends outside reference positional data range.")
        print(f"  Input range exceeds reference range by: {min_ref_time - min_time:.2f}s before, {max_time - max_ref_time:.2f}s after")
        print(f"  Results will use extrapolation which may be inaccurate.")
    if len(science_times_numeric) > 0:
        query_time = science_times_numeric[0]
        insert_idx = np.searchsorted(data_dict['times_numeric'], query_time)
        idx0 = max(0, insert_idx - 2)
        idx1 = min(len(data_dict['times_numeric']) - 1, insert_idx + 2)
        print(f"[DEBUG]    Interpolation Context (around first query time {pd.to_datetime(query_time * 1e9)}):")
        print(f"      Ref Times : {pd.to_datetime(data_dict['times_numeric'][idx0:idx1+1] * 1e9).values}")
        print(f"      Ref Values ({data_type}): {positional_values[idx0:idx1+1]}")
    interpolated_values = np.interp(
        science_times_numeric,
        data_dict['times_numeric'],
        positional_values
    )
    print(f"[DEBUG] {data_type.capitalize()} mapping output range: {np.min(interpolated_values):.2f}{data_units} to {np.max(interpolated_values):.2f}{data_units}")
    return interpolated_values

def test_perihelion_offset_calculation():
    """
    Pytest-compatible test focusing on the +/- 10s around perihelion 
    to diagnose the 0-degree offset issue. Outputs to console.
    Completely standalone: does not use XAxisPositionalDataMapper or any plotbot code.
    """
    print("--- Running Perihelion Offset Debug Test (Tight Focus) ---")

    # --- Configuration ---
    center_time_str = '2023-09-27 23:28:00.000' # E17 perihelion
    time_delta_seconds = 10 # Focus: +/- 10 seconds around perihelion
    step_seconds = 1      # Step size: 1 second

    # --- Print test window info ---
    window_hours = 144  # ±72h
    print(f"[TEST CONFIG] Center (perihelion): {center_time_str}")
    print(f"[TEST CONFIG] Window size: ±{window_hours//2} hours ({window_hours} hours total)")

    # --- Load Parker positional data ---
    project_root = pathlib.Path(__file__).parent.parent
    data_path = project_root / "support_data" / "trajectories" / "Parker_positional_data.npz"
    assert data_path.exists(), f"Data file not found: {data_path}"
    data_dict = load_parker_positional_data(str(data_path))
    print("Positional Data loaded.")

    # Print first and last values of times_numeric and longitude_values for context
    print("\n[DEBUG] times_numeric (first 3):", data_dict['times_numeric'][:3])
    print("[DEBUG] times_numeric (last 3):", data_dict['times_numeric'][-3:])
    print("[DEBUG] carrington_lon (first 3):", data_dict['carrington_lon'][:3])
    print("[DEBUG] carrington_lon (last 3):", data_dict['carrington_lon'][-3:])

    # Print Parker data cadence
    parker_times = data_dict['times_numeric']
    print("\n[DEBUG] Parker data cadence (seconds between first 5 points):")
    for i in range(4):
        dt = parker_times[i+1] - parker_times[i]
        print(f"  {i} -> {i+1}: {dt} seconds ({dt/60:.2f} minutes)")

    # --- Get Perihelion Time and Longitude ---
    center_dt = pd.Timestamp(center_time_str).to_pydatetime() # Use python datetime
    perihelion_time_str = get_perihelion_time(center_dt)
    assert perihelion_time_str, f"Could not retrieve perihelion time for {center_dt}."

    try:
        perihelion_dt = datetime.strptime(perihelion_time_str, '%Y/%m/%d %H:%M:%S.%f')
        perihelion_time_np = np.array([np.datetime64(perihelion_dt, 'ns')])
        print(f"Perihelion datetime object: {perihelion_dt}")
    except ValueError:
        raise AssertionError(f"Could not parse perihelion time string: {perihelion_time_str}")
        
    perihelion_lon_arr = map_to_position(perihelion_time_np, 'carrington_lon', data_dict)
    assert perihelion_lon_arr is not None and len(perihelion_lon_arr) > 0 and not np.isnan(perihelion_lon_arr[0]), "Failed to map perihelion time to a valid longitude."
    perihelion_lon_val = perihelion_lon_arr[0]
    print(f"Successfully mapped Perihelion Time {perihelion_time_str} to Longitude: {perihelion_lon_val:.6f}°")

    # Print perihelion_time_numeric and insert_idx
    perihelion_time_numeric = (np.datetime64(perihelion_dt, 'ns').astype(np.int64) / 1e9)
    insert_idx = np.searchsorted(data_dict['times_numeric'], perihelion_time_numeric)
    print(f"[DEBUG] perihelion_time_numeric: {perihelion_time_numeric}")
    print(f"[DEBUG] insert_idx in times_numeric: {insert_idx}")

    # Print Raw Reference Data Around Perihelion
    print("\n--- Raw Reference Data from Data Dict --- ")
    idx_start = max(0, insert_idx - 5)
    idx_end = min(len(data_dict['times_numeric']) - 1, insert_idx + 5)
    print("Idx    | Ref Timestamp                 | Ref Carrington Lon (°)")
    print("-------|-------------------------------|------------------------")
    for i in range(idx_start, idx_end + 1):
        ref_ts = pd.to_datetime(data_dict['times_numeric'][i] * 1e9)
        ref_lon = data_dict['carrington_lon'][i]
        highlight = " <--- Perihelion Here" if i == insert_idx else ""
        print(f"{i: <6} | {ref_ts.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]: <29} | {ref_lon:.6f}{highlight}")

    # Divide Parker time series into 10 equal chunks
    n_total = len(parker_times)
    chunk_size = n_total // 10
    print(f"\n[DEBUG] Parker data divided into 10 chunks (total points: {n_total}):")
    for i in range(10):
        idx_start = i * chunk_size
        idx_end = (i + 1) * chunk_size - 1 if i < 9 else n_total - 1
        t_start = parker_times[idx_start]
        t_end = parker_times[idx_end]
        print(f"  Chunk {i+1}: idx {idx_start} to {idx_end}, time {pd.to_datetime(t_start * 1e9)} to {pd.to_datetime(t_end * 1e9)}")

    # --- Multiplot-style window and position setup ---
    position = 'around'  # Only 'around' is supported in this test
    window = timedelta(hours=144)  # 144 hours = ±72h
    center_time = perihelion_dt
    if position == 'around':
        start_time_dt = center_time - window / 2
        end_time_dt = center_time + window / 2
    elif position == 'before':
        start_time_dt = center_time - window
        end_time_dt = center_time
    elif position == 'after':
        start_time_dt = center_time
        end_time_dt = center_time + window
    else:
        raise ValueError(f"Unsupported position: {position}")
    print(f"\n[DEBUG] Using multiplot-style window: position={position}, window={window}, center_time={center_time}")
    print(f"[DEBUG] start_time: {start_time_dt}, end_time: {end_time_dt}")

    # Generate test timestamps (1 hour steps)
    test_datetimes = []
    dt = start_time_dt
    while dt <= end_time_dt:
        test_datetimes.append(dt)
        dt += timedelta(hours=1)
    test_times = [(np.datetime64(dt, 'ns').astype(np.int64) / 1e9) for dt in test_datetimes]
    print(f"[DEBUG] Main test window: {len(test_times)} points from {test_datetimes[0]} to {test_datetimes[-1]}")
    # Confirm perihelion is in the window
    perihelion_numeric = (np.datetime64(center_time, 'ns').astype(np.int64) / 1e9)
    perihelion_in_window = any(abs(t - perihelion_numeric) < 1 for t in test_times)
    print(f"[DEBUG] Perihelion time {center_time} is in test window: {perihelion_in_window}")

    print("\nIdx | Test Timestamp           | Mapped Lon (interp)   | Nearest Parker idx | Parker Time           | Parker Lon   | Diff")
    print("----|-------------------------|-----------------------|--------------------|----------------------|-------------|----------")
    for idx, (t, dt) in enumerate(zip(test_times, test_datetimes)):
        ts_np = np.array([np.datetime64(dt, 'ns')])
        mapped_lon = map_to_position(ts_np, 'carrington_lon', data_dict)[0]
        # Find nearest Parker index
        parker_idx = np.argmin(np.abs(parker_times - t))
        parker_time = parker_times[parker_idx]
        parker_lon = data_dict['carrington_lon'][parker_idx]
        diff = mapped_lon - parker_lon
        print(f"{idx: <3} | {dt} | {mapped_lon: <21.8f} | {parker_idx: <18} | {pd.to_datetime(parker_time * 1e9)} | {parker_lon: <11.8f} | {diff: .8f}")

    # --- Plotting ---
    if len(test_times) > 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(test_times, test_times, marker='.', linestyle='-', markersize=6)
        ax.axvline(perihelion_numeric, color='r', linestyle='--', linewidth=1, label='Perihelion (0°)')
        ax.set_xlabel("Calculated Degrees from Perihelion (°)")
        ax.set_ylabel("Time Step Index (Dummy Y)")
        ax.set_title(f"Perihelion Offset Debug ({step_seconds}s steps around E17 Perihelion)")
        ax.grid(True)
        ax.legend()
        min_deg, max_deg = np.nanmin(test_times), np.nanmax(test_times)
        if np.isfinite(min_deg) and np.isfinite(max_deg) and not np.isclose(min_deg, max_deg):
            padding = max(0.01, abs(max_deg - min_deg) * 0.1)
            ax.set_xlim(min_deg - padding, max_deg + padding)
        else:
            ax.set_xlim(-0.1, 0.1)
        plt.show()
        plt.close(fig)
    else:
        print("No valid data points to plot after NaN filtering.") 