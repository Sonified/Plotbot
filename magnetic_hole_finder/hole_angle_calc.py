#file: hole_angle_calc.py

from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def calculate_moving_avg_and_stdev(data, window_seconds, sampling_rate):
    window_size = int(window_seconds * sampling_rate)  # Calculate window size in number of samples
    moving_avg = pd.Series(data).rolling(window=window_size, center=True, min_periods=1).mean().to_numpy()
    moving_stdev = pd.Series(data).rolling(window=window_size, center=True, min_periods=1).std().to_numpy()
    return moving_avg, moving_stdev

def calculate_boundaries_and_w_angle(bmag, times, min_idx, lower_bound):
    tS = None
    tE = None

    # Search for the point on the left side of the minimum where bmag is closest to lower_bound
    for i in range(min_idx, 0, -1):
        if bmag[i] >= lower_bound[i]:
            tS = i
            break
    
    # Search for the point on the right side of the minimum where bmag is closest to lower_bound
    for i in range(min_idx, len(bmag)):
        if bmag[i] >= lower_bound[i]:
            tE = i
            break
    
    if tS is not None and tE is not None:
        # Calculate the directional change angle ω between the vectors at tS and tE
        B_tS = bmag[tS]
        B_tE = bmag[tE]
        W_angle = np.arccos(np.dot(B_tS, B_tE) / (np.linalg.norm(B_tS) * np.linalg.norm(B_tE))) * 180 / np.pi
    else:
        W_angle = None  # Handle cases where boundaries couldn't be found
    
    return tS, tE, W_angle

current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f'{current_time} - 📐 Hole Angle Calc Initialized')

def calculate_hole_angle_and_boundaries(bmag, br, bt, bn, left_max_value_idx, right_max_value_idx, min_idx, sampling_rate, Bave_window_seconds, wide_angle_threshold, break_for_wide_angle):
    # Calculate the moving average and standard deviation for the specific window
    Bave, delta_B = calculate_moving_avg_and_stdev(bmag, Bave_window_seconds, sampling_rate)
    lower_bound = Bave - delta_B  # Calculate the lower bound
    
    # Find the left boundary (tS) where bmag crosses Bave0 - δB starting from the left max and moving right
    for tS in range(left_max_value_idx, min_idx):
        if bmag[tS] <= lower_bound[tS]:  # Adjusted to use <= instead of >= since you're looking for when it drops below the bound
            break
    
    # Find the right boundary (tE) where bmag crosses Bave0 - δB starting from the right max and moving left
    for tE in range(right_max_value_idx, min_idx, -1):
        if bmag[tE] <= lower_bound[tE]:  # Adjusted to use <= instead of >= since you're looking for when it drops below the bound
            break
    
    # Calculate the directional change angle ω between the vectors at tS and tE
    B_tS = np.array([br[tS], bt[tS], bn[tS]])
    B_tE = np.array([br[tE], bt[tE], bn[tE]])
    W_angle = np.arccos(np.dot(B_tS, B_tE) / (np.linalg.norm(B_tS) * np.linalg.norm(B_tE))) * 180 / np.pi
    
    print(f"-----📐 W angle between boundaries is {W_angle} degrees.")
    
    # Check if the W angle exceeds the threshold
    if W_angle > wide_angle_threshold:
        print(f"🇲🇦 Too large W angle: {W_angle}°")
        if break_for_wide_angle:
            print("-----⛔️ Skipping this hole due to excessive W angle.")
            return None, None, None  # Skip this hole if the angle exceeds the threshold
    
    return tS, tE, W_angle
