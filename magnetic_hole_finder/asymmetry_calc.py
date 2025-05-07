#file: asymmetry_calc.py
import numpy as np
import pandas as pd

def process_asymmetry(
    left_max_value, right_max_value,
    left_max_value_idx, right_max_value_idx,
    L_threshold_cross, R_threshold_cross,
    times_clipped, asymetric_peak_threshold,
    symmetrical_peak_scan_window_in_secs,
    bmag_clipped, bmag_slow_smooth_clipped, bmag_fast_smooth_clipped,
    determine_sampling_rate, INSTRUMENT_SAMPLING_RATE,
    max_window_seconds,
    break_for_assymettry,
    break_for_complex_hole  # New flag for skipping complex holes
):
    # Initialize flags
    asymmetrical_initial_peaks_flag = False
    symmetrical_peak_found_flag = False
    complex_hole_flag = False

    # Calculate asymmetry
    peak_diff_percentage = abs(left_max_value - right_max_value) / min(left_max_value, right_max_value)
    print(f"🪐 Asymmetry between peaks: {peak_diff_percentage:.2%}")

    # Determine the minimum index and value within the current hole using the clipped data
    min_idx = np.argmin(bmag_clipped[L_threshold_cross:R_threshold_cross + 1]) + L_threshold_cross
    min_value = bmag_clipped[min_idx]
    min_timestamp = times_clipped[min_idx]

    # Convert numpy.datetime64 to pandas Timestamp to use strftime
    min_timestamp_pd = pd.Timestamp(min_timestamp)
    min_timestamp_str = min_timestamp_pd.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]
    print(f"Minimum detected at index {min_idx}, value: {min_value}, timestamp: {min_timestamp_str}")

    if peak_diff_percentage > asymetric_peak_threshold:
        asymmetrical_initial_peaks_flag = True
        complex_hole_flag = True
        print(f"🇲🇦 Peaks are NOT within the threshold of {asymetric_peak_threshold*100}%.")
        print("Initial asymmetry detected, marking as complex hole.")

        if break_for_complex_hole:
            print("-----⛔️ Skipping this hole due to complexity.")
            return {"status": "complex"}
        
        # Step 1: Check if Bmag crosses below the slow smooth Bmag in the next second
        sampling_rate = determine_sampling_rate(times_clipped, INSTRUMENT_SAMPLING_RATE, True)
        next_second_samples = int(1 * sampling_rate)
        extended_search_end = min(len(bmag_clipped), right_max_value_idx + next_second_samples)

        crossed_below = False
        for j in range(right_max_value_idx, extended_search_end):
            if bmag_clipped[j] < bmag_slow_smooth_clipped[j]:
                crossed_below = True
                break

        if crossed_below:
            # Step 2: Find where Bmag rises above slow smooth Bmag again
            for j in range(j, len(bmag_clipped)):
                if bmag_clipped[j] > bmag_slow_smooth_clipped[j]:
                    R_threshold_cross = j
                    break

            # Now apply the fast smoothing method
            R_plateau_scan = R_threshold_cross
            while R_plateau_scan < len(bmag_fast_smooth_clipped) - 1 and bmag_fast_smooth_clipped[R_plateau_scan] < bmag_fast_smooth_clipped[R_plateau_scan + 1]:
                R_plateau_scan += 1
            
            R_avg_inflect = R_plateau_scan
            slice_bmag = bmag_clipped[R_threshold_cross:R_avg_inflect + 1]
            print(f"Right peak search range: {R_threshold_cross} to {R_avg_inflect}, slice length: {len(slice_bmag)}")
            
            if len(slice_bmag) > 0:
                right_max_value_idx = np.argmax(slice_bmag) + R_threshold_cross
                right_max_value_idx = min(right_max_value_idx, len(bmag_clipped) - 1)
                right_max_value = bmag_clipped[right_max_value_idx]
                print(f"Right maximum detected at index {right_max_value_idx}, value: {right_max_value}")
            else:
                print(f"Warning: Empty slice for finding the right maximum: R_threshold_cross={R_threshold_cross}, R_avg_inflect={R_avg_inflect}")
                right_max_value_idx = min(R_threshold_cross, len(bmag_clipped) - 1)
                right_max_value = bmag_clipped[right_max_value_idx]
        else:
            # Step 3: If no crossing below, look forward two seconds for a new peak
            extended_search_end = min(len(bmag_clipped), int(right_max_value_idx + 2 * sampling_rate))
            for j in range(right_max_value_idx, extended_search_end):
                current_diff_percentage = abs(left_max_value - bmag_clipped[j]) / min(left_max_value, bmag_clipped[j])
                if current_diff_percentage <= asymetric_peak_threshold:
                    right_max_value_idx = j
                    right_max_value = bmag_clipped[right_max_value_idx]
                    print(f"New right maximum detected at index {right_max_value_idx}, value: {right_max_value}")
                    break

        # Re-scan the entire new region for a new minimum
        new_min_idx = np.argmin(bmag_clipped[L_threshold_cross:right_max_value_idx + 1]) + L_threshold_cross
        new_min_value = bmag_clipped[new_min_idx]
        print(f"New minimum detected at index {new_min_idx}, value: {new_min_value}")

        # Recalculate asymmetry after adjustment
        adjusted_peak_diff_percentage = abs(left_max_value - right_max_value) / min(left_max_value, right_max_value)
        print(f"Asymmetry between peaks after adjustment: {adjusted_peak_diff_percentage:.2%}")

        if adjusted_peak_diff_percentage <= asymetric_peak_threshold:
            print(f"Peaks are now within the threshold of {asymetric_peak_threshold * 100}%.")
        else:
            print(f"Peaks are STILL NOT within the threshold of {asymetric_peak_threshold * 100}%.")
            if break_for_assymettry:
                print("-----⛔️ Skipping this hole due to unresolved asymmetry.")
                return {"status": "unresolved_asymmetry"}

        # Update variables
        min_idx = new_min_idx
        min_value = new_min_value

    else:
        print(f"Peaks are within the threshold of {asymetric_peak_threshold*100}%.")

    # Prepare a dictionary with all relevant data
    
    hole_info = {
        "status": "resolved",
        "L_threshold_cross": L_threshold_cross,
        "R_threshold_cross": R_threshold_cross,
        "min_idx": min_idx,
        "min_value": bmag_clipped[min_idx],
        "left_max_value_idx": left_max_value_idx,
        "left_max_value": left_max_value,
        "right_max_value_idx": right_max_value_idx,
        "right_max_value": right_max_value,
        "asymmetrical_initial_peaks_flag": asymmetrical_initial_peaks_flag,
        "symmetrical_peak_found_flag": symmetrical_peak_found_flag,
        "complex_hole_flag": complex_hole_flag,
    }

    print(f"Final hole info: {hole_info}")

    return hole_info
