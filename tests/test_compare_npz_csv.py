import numpy as np
import pandas as pd
import pathlib

def test_npz_csv_alignment():
    """
    Compare the first 10 rows of the NPZ and CSV for time, r_sun, carrington_lon, carrington_lat.
    Print mismatches or confirm alignment.
    """
    npz_path = pathlib.Path(__file__).parent.parent / "support_data" / "trajectories" / "Parker_positional_data.npz"
    csv_path = "/Users/robertalexander/Downloads/Parker-SolO-Earth-15min-Trajectories-20180815-20300101.csv"
    assert npz_path.exists(), f"NPZ file not found: {npz_path}"
    assert pathlib.Path(csv_path).exists(), f"CSV file not found: {csv_path}"

    # Load NPZ
    with np.load(npz_path) as data:
        times_npz = pd.to_datetime(data['times'])
        r_sun_npz = data['r_sun']
        lon_npz = data['carrington_lon']
        lat_npz = data['carrington_lat']
    # Load CSV
    df = pd.read_csv(csv_path)
    times_csv = pd.to_datetime(df['Time'])
    r_sun_csv = df['Parker-CARR-R(Rsun)']
    lon_csv = df['Parker-CARR-LON(deg)']
    lat_csv = df['Parker-CARR-LAT(deg)']

    print("Comparing first 10 rows of NPZ and CSV:")
    for i in range(10):
        print(f"Row {i}:")
        t_npz, t_csv = times_npz[i], times_csv[i]
        r_npz, r_csv = r_sun_npz[i], r_sun_csv.iloc[i]
        lon_n, lon_c = lon_npz[i], lon_csv.iloc[i]
        lat_n, lat_c = lat_npz[i], lat_csv.iloc[i]
        print(f"  Time:         NPZ={t_npz} | CSV={t_csv} | {'MATCH' if t_npz==t_csv else 'MISMATCH'}")
        print(f"  r_sun:        NPZ={r_npz} | CSV={r_csv} | {'MATCH' if np.isclose(r_npz, r_csv) else 'MISMATCH'}")
        print(f"  carr_lon:     NPZ={lon_n} | CSV={lon_c} | {'MATCH' if np.isclose(lon_n, lon_c) else 'MISMATCH'}")
        print(f"  carr_lat:     NPZ={lat_n} | CSV={lat_c} | {'MATCH' if np.isclose(lat_n, lat_c) else 'MISMATCH'}")
        print("") 