# tests/test_orbit_raw_performance.py
# Direct test of orbit data pipeline components without plotbot infrastructure
# To run: conda run -n plotbot_env python tests/test_orbit_raw_performance.py

import sys
import os
import time
import pickle
import numpy as np
from datetime import datetime

# --- Path Setup ---
plotbot_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, plotbot_project_root)

from plotbot.data_classes.psp_orbit import psp_orbit_class

def load_npz_data():
    """Step 1: Load raw NPZ data"""
    start_time = time.time()
    
    # Load the NPZ file directly
    npz_path = "support_data/trajectories/psp_positional_data.npz"
    if not os.path.exists(npz_path):
        print(f"❌ NPZ file not found: {npz_path}")
        return None, 0
    
    npz_data = np.load(npz_path)
    load_time = time.time() - start_time
    
    print(f"✅ NPZ file loaded in {load_time*1000:.2f}ms")
    print(f"   Available keys: {list(npz_data.files)}")
    print(f"   Times shape: {npz_data['times'].shape}")
    print(f"   r_sun shape: {npz_data['r_sun'].shape}")
    
    return npz_data, load_time

def slice_data_for_timerange(npz_data, trange):
    """Step 2: Slice data for specific time range"""
    start_time = time.time()
    
    times = npz_data['times']
    r_sun = npz_data['r_sun']
    carrington_lon = npz_data['carrington_lon']
    carrington_lat = npz_data['carrington_lat']
    icrf_x = npz_data.get('icrf_x', None)
    icrf_y = npz_data.get('icrf_y', None)
    icrf_z = npz_data.get('icrf_z', None)
    
    # Convert trange to numpy datetime64 for comparison
    start_time_np = np.datetime64(trange[0].replace('/', 'T'))
    end_time_np = np.datetime64(trange[1].replace('/', 'T'))
    
    # Find indices for the time range
    indices = np.where((times >= start_time_np) & (times <= end_time_np))[0]
    
    if len(indices) == 0:
        print(f"❌ No data found in time range {trange}")
        return None, 0
    
    # Slice all arrays
    sliced_data = {
        'times': times[indices],
        'r_sun': r_sun[indices],
        'carrington_lon': carrington_lon[indices],
        'carrington_lat': carrington_lat[indices],
        'icrf_x': icrf_x[indices] if icrf_x is not None else None,
        'icrf_y': icrf_y[indices] if icrf_y is not None else None,
        'icrf_z': icrf_z[indices] if icrf_z is not None else None,
    }
    
    slice_time = time.time() - start_time
    print(f"✅ Data sliced in {slice_time*1000:.2f}ms")
    print(f"   Sliced to {len(indices)} points")
    print(f"   Time range: {sliced_data['times'][0]} to {sliced_data['times'][-1]}")
    
    return sliced_data, slice_time

def calculate_orbit_variables(sliced_data):
    """Step 3: Calculate all orbit variables"""
    start_time = time.time()
    
    # Get the data
    times = sliced_data['times']
    r_sun = sliced_data['r_sun']
    carrington_lon = sliced_data['carrington_lon']
    carrington_lat = sliced_data['carrington_lat']
    icrf_x = sliced_data['icrf_x']
    icrf_y = sliced_data['icrf_y']
    icrf_z = sliced_data['icrf_z']
    
    # Convert time array
    datetime_array = np.array(times, dtype='datetime64[ns]')
    
    # Convert r_sun to AU
    rsun_to_au = 696000.0 / 149597871.0
    heliocentric_distance_au = r_sun * rsun_to_au
    
    # Calculate orbital mechanics if ICRF data available
    if icrf_x is not None and icrf_y is not None and icrf_z is not None:
        # Create orbital mechanics instance for calculation
        orbit_calc = psp_orbit_class(None)
        orbital_speed, velocity_x, velocity_y, velocity_z, angular_momentum = orbit_calc._calculate_orbital_mechanics_icrf(
            icrf_x, icrf_y, icrf_z, r_sun)
    else:
        # Fallback calculation
        orbit_calc = psp_orbit_class(None)
        orbital_speed = orbit_calc._calculate_orbital_speed_carrington(r_sun, carrington_lon, carrington_lat)
        velocity_x = velocity_y = velocity_z = angular_momentum = None
    
    # Store all calculated data
    calculated_data = {
        'datetime_array': datetime_array,
        'r_sun': r_sun,
        'carrington_lon': carrington_lon,
        'carrington_lat': carrington_lat,
        'icrf_x': icrf_x,
        'icrf_y': icrf_y,
        'icrf_z': icrf_z,
        'heliocentric_distance_au': heliocentric_distance_au,
        'orbital_speed': orbital_speed,
        'angular_momentum': angular_momentum,
        'velocity_x': velocity_x,
        'velocity_y': velocity_y,
        'velocity_z': velocity_z,
    }
    
    calc_time = time.time() - start_time
    print(f"✅ Variables calculated in {calc_time*1000:.2f}ms")
    print(f"   Orbital speed range: {np.min(orbital_speed):.2f} to {np.max(orbital_speed):.2f} km/s")
    
    return calculated_data, calc_time

def cache_data(calculated_data, cache_filename="test_orbit_cache.pkl"):
    """Step 4: Cache the calculated data"""
    start_time = time.time()
    
    cache_path = os.path.join("tests", cache_filename)
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    
    with open(cache_path, 'wb') as f:
        pickle.dump(calculated_data, f)
    
    cache_time = time.time() - start_time
    print(f"✅ Data cached in {cache_time*1000:.2f}ms")
    print(f"   Cache file: {cache_path}")
    print(f"   File size: {os.path.getsize(cache_path) / 1024:.1f} KB")
    
    return cache_time

def load_cached_data(cache_filename="test_orbit_cache.pkl"):
    """Step 5: Load data from cache"""
    start_time = time.time()
    
    cache_path = os.path.join("tests", cache_filename)
    if not os.path.exists(cache_path):
        print(f"❌ Cache file not found: {cache_path}")
        return None, 0
    
    with open(cache_path, 'rb') as f:
        loaded_data = pickle.load(f)
    
    load_time = time.time() - start_time
    print(f"✅ Data loaded from cache in {load_time*1000:.2f}ms")
    print(f"   Loaded {len(loaded_data['r_sun'])} data points")
    
    return loaded_data, load_time

def run_performance_test():
    """Main test function"""
    print("🚀 ORBIT DATA RAW PERFORMANCE TEST")
    print("="*50)
    
    # Test parameters
    trange = ['2021-11-20/00:00:00.000', '2021-11-23/00:00:00.000']
    cache_filename = f"orbit_cache_{int(time.time())}.pkl"
    
    total_start = time.time()
    
    # Step 1: Load NPZ file
    print("\n📁 STEP 1: Loading NPZ file...")
    npz_data, load_time = load_npz_data()
    if npz_data is None:
        return
    
    # Step 2: Slice data for time range
    print("\n✂️ STEP 2: Slicing data for time range...")
    sliced_data, slice_time = slice_data_for_timerange(npz_data, trange)
    if sliced_data is None:
        return
    
    # Step 3: Calculate orbital variables
    print("\n🧮 STEP 3: Calculating orbital variables...")
    calculated_data, calc_time = calculate_orbit_variables(sliced_data)
    
    # Step 4: Cache the data
    print("\n💾 STEP 4: Caching calculated data...")
    cache_time = cache_data(calculated_data, cache_filename)
    
    # Step 5: Load from cache (simulate second run)
    print("\n📥 STEP 5: Loading from cache...")
    loaded_data, cache_load_time = load_cached_data(cache_filename)
    
    # Cleanup
    cache_path = os.path.join("tests", cache_filename)
    if os.path.exists(cache_path):
        os.remove(cache_path)
        print(f"🗑️ Cleaned up cache file: {cache_filename}")
    
    # Summary
    total_time = time.time() - total_start
    num_points = len(sliced_data['r_sun'])
    
    print("\n📊 PERFORMANCE SUMMARY")
    print("="*50)
    print(f"Data points processed: {num_points}")
    print(f"NPZ load time:         {load_time*1000:.2f}ms ({load_time/num_points*1000:.4f}ms/point)")
    print(f"Data slicing time:     {slice_time*1000:.2f}ms ({slice_time/num_points*1000:.4f}ms/point)")
    print(f"Calculation time:      {calc_time*1000:.2f}ms ({calc_time/num_points*1000:.4f}ms/point)")
    print(f"Cache write time:      {cache_time*1000:.2f}ms ({cache_time/num_points*1000:.4f}ms/point)")
    print(f"Cache read time:       {cache_load_time*1000:.2f}ms ({cache_load_time/num_points*1000:.4f}ms/point)")
    print(f"Total time:            {total_time*1000:.2f}ms ({total_time/num_points*1000:.4f}ms/point)")
    
    # Compare to plotbot performance
    print("\n🔄 COMPARISON TO PLOTBOT PIPELINE")
    print("="*50)
    plotbot_time_per_point = 6.45  # From previous test
    raw_time_per_point = total_time/num_points*1000
    overhead = plotbot_time_per_point - raw_time_per_point
    
    print(f"Raw pipeline:          {raw_time_per_point:.4f}ms/point")
    print(f"Plotbot pipeline:      {plotbot_time_per_point:.4f}ms/point") 
    print(f"Infrastructure overhead: {overhead:.4f}ms/point ({overhead/plotbot_time_per_point*100:.1f}%)")

if __name__ == "__main__":
    run_performance_test() 