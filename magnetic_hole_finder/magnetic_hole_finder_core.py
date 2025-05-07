import numpy as np
import pandas as pd
from datetime import datetime
import json # For saving settings to JSON
import os   # For path joining

# Imports from your existing magnetic_hole_finder package
from .asymmetry_calc import process_asymmetry 
from .time_management import extend_time_range, clip_to_original_time_range, determine_sampling_rate, efficient_moving_average
from .data_management import download_and_prepare_high_res_mag_data, setup_output_directory # Added setup_output_directory
from .hole_angle_calc import calculate_hole_angle_and_boundaries
from .zero_crossing_analysis import analyze_derivative_zero_crossings
from .plotting import plot_mag_data_with_holes_and_minimum # Assuming this is where your plot function is
from .MH_format_output import output_magnetic_holes # Assuming this is where your marker output function is
from .data_audification import audify_high_res_mag_data_without_plot # Assuming this is for audio
from collections import Counter

class HoleFinderSettings:
    def __init__(self):
        # --- Core Algorithm Parameters ---
        self.INSTRUMENT_SAMPLING_RATE = 292.9
        self.use_calculated_sampling_rate = True
        self.depth_percentage_threshold = 0.25
        self.smoothing_window_seconds = 8.0
        self.derivative_window_seconds = 0.2
        self.min_max_finding_smooth_window = 0.3
        self.mean_threshold = 0.8
        self.search_in_progress_output = True
        self.additional_seconds_for_min_search = 0.2
        self.asymetric_peak_threshold = 0.25
        self.symmetrical_peak_scan_window_in_secs = 2.0
        self.Bave_scan_seconds = 0.1
        self.Bave_window_seconds = 20.0
        self.wide_angle_threshold = 15.0
        self.small_threshold_cross_flag_samples = 10 
        self.small_threshold_cross_adjustment_samples = 10
        
        # --- Algorithm Breaking Condition Flags ---
        self.break_for_shallow_hole = True
        self.break_for_assymettry = False 
        self.break_for_wide_angle = False 
        self.break_for_small_threshold_cross = False
        self.break_for_complex_hole = False 
        self.threshold_for_derivative_0_crossings_flag = 1000
        self.break_for_derivative_crossings = False

        # --- Output Generation Control Flags ---
        self.OUTPUT_MAIN_PLOT = True 
        self.SAVE_MAIN_PLOT = True   
        self.PLOT_HOLE_MINIMUM_ON_MAIN_PLOT = True 
        self.PLOT_THRESH_CROSS_ON_MAIN_PLOT = True 

        self.OUTPUT_ZERO_CROSSING_PLOT = False # For the specific plot in zero_crossing_analysis

        self.IZOTOPE_MARKER_FILE_OUTPUT_MAX_AND_MIN = True 
        self.IZOTOPE_MARKER_FILE_OUTPUT_GENERAL = False # The other iZotope marker flag
        self.MARKER_FILE_VERSION = 3
        self.MARKER_FILES_WITH_ANNOTATED_MARKERS = False
        self.MARKER_FILES_WITH_HOLE_NUMBERS = False

        self.EXPORT_AUDIO_FILES = True
        self.AUDIO_SAMPLING_RATE = 22000

        # --- New Download Only Mode ---
        self.download_only = False # Default to False for full analysis

# Module-level counter
hole_counter_core = Counter()

def _detect_magnetic_holes_logic(trange, settings: HoleFinderSettings, current_instrument_sampling_rate, times, br, bt, bn, bmag_extended, times_clipped, bmag, bmag_slow_smooth, bmag_fast_smooth):
    """Internal logic for hole detection, separated for clarity."""
    global hole_counter_core # Continue to use the module-level counter
    # hole_counter_core has already been cleared by the calling function

    magnetic_holes = []
    hole_minima = []
    hole_maxima_pairs = []
    magnetic_hole_details = []
    i = 0

    while i < len(bmag):   
        start_of_potential_hole = i
        while start_of_potential_hole < len(bmag) and bmag[start_of_potential_hole] >= bmag_slow_smooth[start_of_potential_hole]:
            start_of_potential_hole += 1
        
        if start_of_potential_hole >= len(bmag):
            break    
        L_threshold_cross = start_of_potential_hole
        hole_counter_core['potential'] += 1
        
        end_of_potential_hole = L_threshold_cross
        while end_of_potential_hole < len(bmag) -1 and bmag[end_of_potential_hole] < bmag_slow_smooth[end_of_potential_hole]:
            end_of_potential_hole += 1
        R_threshold_cross = end_of_potential_hole

        if R_threshold_cross - L_threshold_cross <= settings.small_threshold_cross_flag_samples:
            hole_counter_core['small_threshold_cross'] += 1
            if settings.break_for_small_threshold_cross:
                if settings.search_in_progress_output: print("-----⛔️ Skipping this small threshold cross.")
                i = R_threshold_cross + 1
                continue
            else:
                R_threshold_cross = min(len(bmag)-1, R_threshold_cross + settings.small_threshold_cross_adjustment_samples)
                L_threshold_cross = max(0, L_threshold_cross - settings.small_threshold_cross_adjustment_samples)
                if settings.search_in_progress_output: print(f"🔥 Hole detection threshold crossed near the bottom of a hole, expanding L & R thresholds for analysis: L={L_threshold_cross}, R={R_threshold_cross}")

        if L_threshold_cross >= R_threshold_cross or L_threshold_cross < 0 or R_threshold_cross >= len(bmag):
            if settings.search_in_progress_output: print(f"Warning: Invalid range after adjustment L_threshold_cross={L_threshold_cross}, R_threshold_cross={R_threshold_cross}. Skipping.")
            i = max(L_threshold_cross, R_threshold_cross) + 1 # Ensure forward progress
            continue

        min_idx_relative = np.argmin(bmag[L_threshold_cross:R_threshold_cross + 1])
        min_idx = min_idx_relative + L_threshold_cross
        min_value = bmag[min_idx]
        if settings.search_in_progress_output: print(f"Minimum initially identified at index {min_idx}")
    
        L_plateau_scan = L_threshold_cross
        while L_plateau_scan > 0 and bmag_fast_smooth[L_plateau_scan-1] > bmag_fast_smooth[L_plateau_scan]:
             L_plateau_scan -=1
        L_avg_inflect = L_plateau_scan

        samples_for_1_sec = int(1 * determine_sampling_rate(times_clipped, current_instrument_sampling_rate, True))

        if L_threshold_cross - L_avg_inflect < samples_for_1_sec: 
            L_avg_inflect = max(0, L_threshold_cross - samples_for_1_sec)
        
        left_max_slice = bmag[L_avg_inflect : L_threshold_cross + 1]

        if len(left_max_slice) > 0:
            left_max_value_idx = np.argmax(left_max_slice) + L_avg_inflect
            left_max_value = bmag[left_max_value_idx]
        else:
            if settings.search_in_progress_output: print("Warning: Empty slice for finding the left maximum.")
            i = R_threshold_cross + 1
            continue
        
        R_plateau_scan = R_threshold_cross
        while R_plateau_scan < len(bmag_fast_smooth) - 1 and bmag_fast_smooth[R_plateau_scan+1] > bmag_fast_smooth[R_plateau_scan]:
            R_plateau_scan += 1
        R_avg_inflect = R_plateau_scan
        
        slice_bmag_right = bmag[R_threshold_cross : R_avg_inflect + 1]
        
        if len(slice_bmag_right) > 0:
            right_max_value_idx = np.argmax(slice_bmag_right) + R_threshold_cross
            right_max_value_idx = min(right_max_value_idx, len(bmag) - 1)
            right_max_value = bmag[right_max_value_idx]
        else:
            if settings.search_in_progress_output: print(f"Warning: Empty slice for finding the right maximum.")
            right_max_value_idx = min(R_threshold_cross, len(bmag) - 1)
            right_max_value = bmag[right_max_value_idx]

        hole_info_dict = process_asymmetry(
            left_max_value, right_max_value,
            left_max_value_idx, right_max_value_idx,
            L_threshold_cross, R_threshold_cross,
            times_clipped, settings.asymetric_peak_threshold,
            settings.symmetrical_peak_scan_window_in_secs,
            bmag, bmag_slow_smooth, bmag_fast_smooth,
            determine_sampling_rate, current_instrument_sampling_rate, 
            settings.smoothing_window_seconds, 
            settings.break_for_assymettry, 
            settings.break_for_complex_hole
        )
    
        if hole_info_dict is None: 
            hole_counter_core['asymmetric_skipped'] += 1 
            if settings.break_for_assymettry: 
                if settings.search_in_progress_output: print("-----⛔️ Skipping hole due to asymmetry processing failure/skip (flagged by break_for_assymettry).")
                i = R_threshold_cross + 1
                continue
            if settings.search_in_progress_output: print("Warning: process_asymmetry returned None and not breaking. Hole might be skipped or results partial.")
            i = R_threshold_cross + 1 
            continue

        status = hole_info_dict.get("status")
        if status == "complex" and settings.break_for_complex_hole:
            hole_counter_core['complex_skipped_by_flag'] +=1
            if settings.search_in_progress_output: print("-----⛔️ Skipping complex hole as per break_for_complex_hole setting.")
            i = R_threshold_cross + 1
            continue
        if status == "unresolved_asymmetry" and settings.break_for_assymettry:
            hole_counter_core['unresolved_asymmetry_skipped_by_flag'] +=1
            if settings.search_in_progress_output: print("-----⛔️ Skipping unresolved asymmetry as per break_for_assymettry setting.")
            i = R_threshold_cross + 1
            continue

        left_max_value_idx = hole_info_dict.get("left_max_value_idx", left_max_value_idx)
        right_max_value_idx = hole_info_dict.get("right_max_value_idx", right_max_value_idx)
        left_max_value = hole_info_dict.get("left_max_value", left_max_value)
        right_max_value = hole_info_dict.get("right_max_value", right_max_value)
        L_threshold_cross = hole_info_dict.get("L_threshold_cross", L_threshold_cross)
        R_threshold_cross = hole_info_dict.get("R_threshold_cross", R_threshold_cross)
        min_idx = hole_info_dict.get("min_idx", min_idx)
        min_value = bmag[min_idx]

        if hole_info_dict.get("asymmetrical_initial_peaks_flag", False):
            hole_counter_core['asymmetric_initial'] += 1
        if hole_info_dict.get("complex_hole_flag", False):
             hole_counter_core['complex_holes_flagged'] +=1

        sampling_rate = determine_sampling_rate(times_clipped, current_instrument_sampling_rate, settings.use_calculated_sampling_rate)
        half_second_samples = int(settings.Bave_scan_seconds * sampling_rate)
        
        L_before_idx = max(0, left_max_value_idx - half_second_samples)
        R_after_idx = min(len(bmag) - 1, right_max_value_idx + half_second_samples)
        
        Bave_before_slice = bmag[L_before_idx : left_max_value_idx]
        Bave_after_slice = bmag[right_max_value_idx + 1 : R_after_idx + 1]

        Bave_before = np.mean(Bave_before_slice) if len(Bave_before_slice) > 0 else np.nan
        Bave_after = np.mean(Bave_after_slice) if len(Bave_after_slice) > 0 else np.nan
        
        if np.isnan(Bave_before) or np.isnan(Bave_after):
            if settings.search_in_progress_output: print("Warning: Bave_before or Bave_after is NaN. Using available peak if one is NaN, or average of peaks if both NaN.")
            if np.isnan(Bave_before) and not np.isnan(Bave_after): Bave = Bave_after
            elif not np.isnan(Bave_before) and np.isnan(Bave_after): Bave = Bave_before
            else: Bave = (left_max_value + right_max_value) / 2
        else:
            Bave = (Bave_before + Bave_after) / 2
        
        hole_abs_depth = Bave - min_value
        hole_percentage_depth = (hole_abs_depth / Bave) * 100 if Bave != 0 else float('inf')
        
        if hole_percentage_depth < settings.depth_percentage_threshold * 100:
            hole_counter_core['shallow'] += 1
            if settings.break_for_shallow_hole:
                if settings.search_in_progress_output: print(f"-----⛔️ Skipping shallow hole (depth {hole_percentage_depth:.1f}%). Threshold: {settings.depth_percentage_threshold * 100}%")
                i = R_threshold_cross + 1
                continue
        if settings.search_in_progress_output: print(f"-----🕳️ Hole relative depth is {hole_percentage_depth:.1f}% (Threshold: {settings.depth_percentage_threshold*100}%)")

        tS, tE, W_angle = calculate_hole_angle_and_boundaries(
            bmag, br, bt, bn, left_max_value_idx, right_max_value_idx, min_idx, 
            sampling_rate, settings.Bave_window_seconds, settings.wide_angle_threshold, settings.break_for_wide_angle
        )
        
        if tS is None: 
            hole_counter_core['wide_angle_skipped_by_flag'] += 1 
            if settings.break_for_wide_angle: 
                 if settings.search_in_progress_output: print("-----⛔️ Skipping hole due to wide angle processing (break_for_wide_angle).")
                 i = R_threshold_cross + 1
                 continue
            if settings.search_in_progress_output: print("Warning: Wide angle processing resulted in None for tS, but not breaking.")
            i = R_threshold_cross + 1 
            continue

        hole_info_dict.update({"tS": tS, "tE": tE, "W_angle": W_angle})
        
        zero_crossings, zero_crossings_indices = analyze_derivative_zero_crossings(
            bmag, times_clipped, left_max_value_idx, right_max_value_idx,
            settings.derivative_window_seconds, sampling_rate, settings.mean_threshold,
            settings.OUTPUT_ZERO_CROSSING_PLOT 
        )

        if zero_crossings >= settings.threshold_for_derivative_0_crossings_flag:
            hole_counter_core['derivative_crossings'] += 1
            if settings.break_for_derivative_crossings:
                if settings.search_in_progress_output: print(f"-----⛔️ Skipping hole due to excessive zero crossings ({zero_crossings}).")
                i = R_threshold_cross + 1
                continue
        hole_info_dict.update({"zero_crossings": zero_crossings})
        
        final_hole_info = {
            "L_threshold_cross": L_threshold_cross,
            "R_threshold_cross": R_threshold_cross,
            "min_idx": min_idx,
            "min_value": min_value,
            "left_max_value_idx": left_max_value_idx,
            "left_max_value": left_max_value,
            "right_max_value_idx": right_max_value_idx,
            "right_max_value": right_max_value,
            "tS": tS, "tE": tE, "W_angle": W_angle,
            "zero_crossings": zero_crossings,
            "asymmetrical_initial_peaks_flag": hole_info_dict.get("asymmetrical_initial_peaks_flag", False),
            "complex_hole_flag": hole_info_dict.get("complex_hole_flag", False) 
        }

        magnetic_hole_details.append(final_hole_info)
        hole_minima.append(final_hole_info["min_idx"])
        hole_maxima_pairs.append((final_hole_info["left_max_value_idx"], final_hole_info["right_max_value_idx"]))
        magnetic_holes.append((final_hole_info["L_threshold_cross"], final_hole_info["R_threshold_cross"]))
        
        if settings.search_in_progress_output:
            print(f"-----⭐️ Magnetic hole confirmed from index {final_hole_info['left_max_value_idx']} to {final_hole_info['right_max_value_idx']}")
                
        i = final_hole_info["R_threshold_cross"] + 1
        hole_counter_core['confirmed'] += 1

    return magnetic_holes, hole_minima, hole_maxima_pairs, times_clipped, bmag, magnetic_hole_details, hole_counter_core

def detect_magnetic_holes_and_generate_outputs(trange, base_save_dir: str, settings: HoleFinderSettings):
    """Main orchestrator: detects holes and generates all standard outputs based on settings."""
    global hole_counter_core
    hole_counter_core.clear()

    print(f"Starting analysis for trange: {trange}. Download_only mode: {settings.download_only}")
    # 1. Setup output directory for this specific run
    sub_save_dir = setup_output_directory(trange, base_save_dir)
    print(f"✅ Outputs for this run will be saved in: {sub_save_dir}")

    # 2. Perform Data Preparation 
    # ... (data preparation logic: extend_trange, download_and_prepare_high_res_mag_data, calculate sampling rate, smooth, clip) ...
    # This part needs to run for both download_only and full analysis to get the basic data.
    max_window_seconds = settings.smoothing_window_seconds 
    extended_trange = extend_time_range(trange, max(settings.smoothing_window_seconds, settings.min_max_finding_smooth_window))
    # download_and_prepare_high_res_mag_data now returns 5 values, but we only strictly need times and bmag_extended for this stage
    dl_times, dl_br, dl_bt, dl_bn, dl_bmag_extended = download_and_prepare_high_res_mag_data(extended_trange)
    
    if dl_times is None or dl_bmag_extended is None:
        print("Error: Failed to download or prepare data during initial data prep. Aborting.")
        settings_to_save_on_fail = settings.__dict__.copy()
        settings_to_save_on_fail['trange_run'] = trange
        settings_to_save_on_fail['sub_save_dir'] = sub_save_dir
        settings_to_save_on_fail['status'] = 'ERROR_DATA_DOWNLOAD_FAILED'
        settings_to_save_on_fail['hole_counts'] = dict(hole_counter_core) 
        # Save settings even on failure
        settings_file_path = os.path.join(sub_save_dir, 'run_settings_and_summary.json')
        try:
            with open(settings_file_path, 'w') as f:
                json.dump(settings_to_save_on_fail, f, indent=4, default=str)
            print(f"Run settings (error state) saved to: {settings_file_path}")
        except Exception as e_json:
            print(f"Error saving settings to JSON during failure: {e_json}")
        return [], [], [], None, None, [], hole_counter_core 

    # These are the full extended data arrays. Note names to avoid conflict with clipped versions.
    times_ext = dl_times
    br_ext = dl_br
    bt_ext = dl_bt
    bn_ext = dl_bn
    bmag_ext = dl_bmag_extended

    total_samples = len(bmag_ext)
    start_time_dt = datetime.strptime(extended_trange[0], '%Y-%m-%d/%H:%M:%S.%f' if '.' in extended_trange[0] else '%Y-%m-%d/%H:%M:%S')
    end_time_dt = datetime.strptime(extended_trange[1], '%Y-%m-%d/%H:%M:%S.%f' if '.' in extended_trange[1] else '%Y-%m-%d/%H:%M:%S')
    duration_seconds = (end_time_dt - start_time_dt).total_seconds()

    current_instrument_sampling_rate = settings.INSTRUMENT_SAMPLING_RATE
    if settings.use_calculated_sampling_rate and duration_seconds > 0 and total_samples > 0:
        current_instrument_sampling_rate = total_samples / duration_seconds
        print(f"✳️ Using calculated SR of {current_instrument_sampling_rate:.2f} Hz for the run.")
    else:
        print(f"✳️ Using predefined SR of {current_instrument_sampling_rate} Hz for the run (or calculation failed).")

    # Data for the hole detection algorithm (clipped to original trange)
    times_clipped, bmag_clipped_main = clip_to_original_time_range(times_ext, bmag_ext, trange)
    # Also clip br, bt, bn to original trange for potential use in outputs or if _detect_magnetic_holes_logic needs them
    _, br_clipped = clip_to_original_time_range(times_ext, br_ext, trange)
    _, bt_clipped = clip_to_original_time_range(times_ext, bt_ext, trange)
    _, bn_clipped = clip_to_original_time_range(times_ext, bn_ext, trange)

    if settings.download_only:
        print("Download-only mode activated. Skipping hole detection and related outputs.")
        # Save settings JSON
        settings_to_save = settings.__dict__.copy()
        settings_to_save['trange_run'] = trange
        settings_to_save['sub_save_dir'] = sub_save_dir
        settings_to_save['status'] = 'DOWNLOAD_ONLY_SUCCESSFUL'
        settings_to_save['data_points_downloaded_extended_range'] = len(times_ext)
        settings_to_save['data_points_clipped_range'] = len(times_clipped)
        settings_file_path = os.path.join(sub_save_dir, 'run_settings_and_summary.json')
        try:
            with open(settings_file_path, 'w') as f:
                json.dump(settings_to_save, f, indent=4, default=str)
            print(f"Run settings (download-only) saved to: {settings_file_path}")
        except Exception as e:
            print(f"Error saving run settings to JSON: {e}")
        # Return the downloaded (and clipped) data, but empty results for detection
        # Pass back br_clipped, bt_clipped, bn_clipped as they are from the original trange
        return [], [], [], times_clipped, bmag_clipped_main, [], hole_counter_core # Potentially return br,bt,bn clipped too
    
    # --- If not download_only, proceed with full analysis --- 
    sampling_rate_for_smoothing = determine_sampling_rate(times_ext, current_instrument_sampling_rate, True)
    bmag_slow_smooth_extended = efficient_moving_average(times_ext, bmag_ext, settings.smoothing_window_seconds, sampling_rate_for_smoothing, settings.mean_threshold)
    bmag_fast_smooth_extended = efficient_moving_average(times_ext, bmag_ext, settings.min_max_finding_smooth_window, sampling_rate_for_smoothing, settings.mean_threshold)
    
    _, bmag_slow_smooth_clipped = clip_to_original_time_range(times_ext, bmag_slow_smooth_extended, trange)
    _, bmag_fast_smooth_clipped = clip_to_original_time_range(times_ext, bmag_fast_smooth_extended, trange)

    # 3. Perform the core hole detection
    results = _detect_magnetic_holes_logic(
        trange, settings, current_instrument_sampling_rate, 
        times_ext, br_ext, bt_ext, bn_ext, bmag_ext, # Pass extended raw data, _detect_magnetic_holes_logic might need br,bt,bn from extended range for angle calc
        times_clipped, bmag_clipped_main, bmag_slow_smooth_clipped, bmag_fast_smooth_clipped 
    )
    magnetic_holes, hole_minima, hole_maxima_pairs, _, _, magnetic_hole_details, returned_counter = results

    # 4. Generate outputs based on settings (if not in download_only mode)
    if settings.OUTPUT_MAIN_PLOT and times_clipped is not None and bmag_clipped_main is not None:
        print("Generating main plot...")
        plot_mag_data_with_holes_and_minimum(
            times_clipped, 
            bmag_clipped_main, 
            magnetic_holes, 
            hole_minima, 
            hole_maxima_pairs, 
            settings.PLOT_HOLE_MINIMUM_ON_MAIN_PLOT, 
            settings.PLOT_THRESH_CROSS_ON_MAIN_PLOT,
            trange,
            sub_save_dir, 
            settings.SAVE_MAIN_PLOT 
        )

    if settings.IZOTOPE_MARKER_FILE_OUTPUT_MAX_AND_MIN or settings.IZOTOPE_MARKER_FILE_OUTPUT_GENERAL:
        print("Generating iZotope marker file...")
        output_magnetic_holes(
            magnetic_holes,
            hole_maxima_pairs, 
            times_clipped,     
            bmag_clipped_main, # Use the Bmag for the primary trange          
            settings.IZOTOPE_MARKER_FILE_OUTPUT_GENERAL,
            settings.IZOTOPE_MARKER_FILE_OUTPUT_MAX_AND_MIN, 
            trange,
            settings.MARKER_FILE_VERSION,
            settings.search_in_progress_output, 
            sub_save_dir, 
            current_instrument_sampling_rate, 
            settings.MARKER_FILES_WITH_ANNOTATED_MARKERS,
            settings.MARKER_FILES_WITH_HOLE_NUMBERS,
            magnetic_hole_details # This should contain all info, including angles using original br,bt,bn
        )

    if settings.EXPORT_AUDIO_FILES:
        print("Exporting audio files...")
        audify_high_res_mag_data_without_plot(trange[0], trange[1], sub_save_dir, settings.AUDIO_SAMPLING_RATE, sub_save_dir)

    # 5. Save all run settings to JSON
    settings_file_path = os.path.join(sub_save_dir, 'run_settings_and_summary.json')
    settings_to_save = settings.__dict__.copy() # Get a copy of settings attributes
    settings_to_save['trange_run'] = trange
    settings_to_save['sub_save_dir'] = sub_save_dir
    settings_to_save['hole_counts'] = dict(returned_counter) # Add counts to the JSON
    try:
        with open(settings_file_path, 'w') as f:
            json.dump(settings_to_save, f, indent=4, default=str) # Added default=str for non-serializable like datetime
        print(f"Run settings and summary saved to: {settings_file_path}")
    except Exception as e:
        print(f"Error saving run settings to JSON: {e}")

    print(f"Magnetic hole detection and output generation complete for trange: {trange}")
    # Return the primary detection results and the counter
    return magnetic_holes, hole_minima, hole_maxima_pairs, times_clipped, bmag_clipped_main, magnetic_hole_details, returned_counter 