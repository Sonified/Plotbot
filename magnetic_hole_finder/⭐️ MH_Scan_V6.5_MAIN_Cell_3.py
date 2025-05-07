# ✨✨✨ShInY NeW wOrKiG cOdE cOdE✨✨✨ 
global save_dir

import importlib

#region Import Modules Block
from collections import Counter
import asymmetry_calc
importlib.reload(asymmetry_calc)
from asymmetry_calc import *
import time_management
importlib.reload(time_management)
from time_management import *
import data_management
importlib.reload(data_management)
from data_management import *
import plotting
importlib.reload(plotting)
from plotting import *
import data_management
importlib.reload(data_management)
from data_management import *
import data_audification
importlib.reload(data_audification)
from data_audification import *
import plotting
importlib.reload(plotting)
from plotting import *
import zero_crossing_analysis
importlib.reload(zero_crossing_analysis)
from zero_crossing_analysis import analyze_derivative_zero_crossings
import MH_format_output
importlib.reload(MH_format_output)
from MH_format_output import *

import hole_angle_calc
importlib.reload(hole_angle_calc)
from hole_angle_calc import *


# from hole_counter import hole_counter
#endregion  

# Initialize the counter
hole_counter = Counter()

def detect_magnetic_holes(trange, smoothing_window_seconds, min_max_finding_smooth_window, mean_threshold, search_in_progress_output, Bave_scan_seconds, break_for_assymettry, small_threshold_cross_flag, small_threshold_cross_adjustment, break_for_small_threshold_cross, break_for_complex_hole, derivative_window_seconds, OUTPUT_ZERO_CROSSING_PLOT, SEARCH_IN_PROGRESS_OUTPUT, INSTRUMENT_SAMPLING_RATE, use_calculated_sampling_rate):
    global hole_counter  # Add this line to use the global hole_counter
    
    max_window_seconds = smoothing_window_seconds
    
    # 📈 Data Preparation Step 1: Extend the Time Range
    extended_trange = extend_time_range(trange, max(smoothing_window_seconds, min_max_finding_smooth_window))

    # 📈 Data Preparation Step 2: Download Data for the Extended Range
    times, br, bt, bn, bmag_extended = download_and_prepare_high_res_mag_data(extended_trange)
    print(f"length of bmag_extended is {len(bmag_extended)}")

    # Calculate sampling rate based on the extended data
    total_samples = len(bmag_extended)
    start_time = datetime.strptime(extended_trange[0], '%Y-%m-%d/%H:%M:%S.%f' if '.' in extended_trange[0] else '%Y-%m-%d/%H:%M:%S')
    end_time = datetime.strptime(extended_trange[1], '%Y-%m-%d/%H:%M:%S.%f' if '.' in extended_trange[1] else '%Y-%m-%d/%H:%M:%S')
    duration = end_time - start_time
    duration_seconds = duration.total_seconds()

    if use_calculated_sampling_rate:
        INSTRUMENT_SAMPLING_RATE = total_samples / duration_seconds
        print(f"✳️ Using calculated SR of {INSTRUMENT_SAMPLING_RATE:.2f} Hz")
    else:
        print(f"✳️ Using predefined SR of {INSTRUMENT_SAMPLING_RATE} Hz")

    # 📈 Data Preparation Step 3: Apply smoothing to the bmag data for detection and maxima finding
    bmag_slow_smooth_extended = efficient_moving_average(times, bmag_extended, smoothing_window_seconds, determine_sampling_rate(times, INSTRUMENT_SAMPLING_RATE, True), mean_threshold)
    bmag_fast_smooth_extended = efficient_moving_average(times, bmag_extended, min_max_finding_smooth_window, determine_sampling_rate(times, INSTRUMENT_SAMPLING_RATE, True), mean_threshold)

    # 📈 Data Preparation Step 4: Clip the smoothed data to the original time range
    times_clipped, bmag = clip_to_original_time_range(times, bmag_extended, trange)
    _, bmag_slow_smooth = clip_to_original_time_range(times, bmag_slow_smooth_extended, trange)
    _, bmag_fast_smooth = clip_to_original_time_range(times, bmag_fast_smooth_extended, trange)

    print(f"Post-clipping length of bmag is {len(bmag)}")

    # # Calculate sampling rate
    # total_samples = len(bmag)
    # start_time = datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f' if '.' in trange[0] else '%Y-%m-%d/%H:%M:%S')
    # end_time = datetime.strptime(trange[1], '%Y-%m-%d/%H:%M:%S.%f' if '.' in trange[1] else '%Y-%m-%d/%H:%M:%S')
    # duration = end_time - start_time
    # duration_seconds = duration.total_seconds()

    # if USE_CALCULATED_SAMPLING_RATE:
    #     calculated_sampling_rate = total_samples / duration_seconds
    #     INSTRUMENT_SAMPLING_RATE = calculated_sampling_rate
    #     print(f"✳️ Using calculated SR of {INSTRUMENT_SAMPLING_RATE:.2f} Hz")
    # else:
    #     print(f"✳️ Using predefined SR of {INSTRUMENT_SAMPLING_RATE} Hz")

    
    magnetic_holes = []
    hole_minima = []  # To store the minima for plotting
    hole_maxima_pairs = []  # To store the left and right maxima pairs for plotting
    magnetic_hole_details = []  # To store details of each detected magnetic hole
    i = 0

    #----- ✅✅✅ 1: Scan through the data to detect drops below the slow smoothed value-----//
    
    while i < len(bmag):   
        while i < len(bmag) and bmag[i] > bmag_slow_smooth[i]:  # skip over where bmag > bmag_slow_smooth
            i += 1
        if i >= len(bmag):
            break    
        L_threshold_cross = i
        hole_counter['potential'] += 1
        
    #----- ✅✅✅ 2: Continue scanning forward until bmag rises above the slow smoothed value-----// 
        #region Right Threshold Cross Block
        while i < len(bmag) - 1 and bmag[i] < bmag_slow_smooth[i]:
            i += 1
        R_threshold_cross = i

        if R_threshold_cross - L_threshold_cross <= small_threshold_cross_flag:
            hole_counter['small_threshold_cross'] += 1
            if break_for_small_threshold_cross:
                print("-----⛔️ Skipping this small threshold cross.")
                continue  # Skip the remaining processing for this hole and move to the next iteration
            else:
                R_threshold_cross += small_threshold_cross_adjustment
                L_threshold_cross -= small_threshold_cross_adjustment
                print(f"🔥 Hole detection threshold crossed near the bottom of a hole, expanding L & R thresholds for analysis:")
                print(f"New L_threshold_cross: {L_threshold_cross}")
                print(f"New R_threshold_cross: {R_threshold_cross}")
        #endregion

    #----- ✅✅✅ 3: Scan for minimum where bmag[i] < slow smoothed value-----//
        min_idx = np.argmin(bmag[L_threshold_cross:R_threshold_cross + 1]) + L_threshold_cross  # Offset to slice start, end is exclusive so +1
        min_value = bmag[min_idx]
        print(f"Minimum initially identified at {min_idx}")
    
    #----- ✅ 4: Find the left peak (maximum) before the drop using the fast smoothing window-----//
        #region Left Peak Scan Block
        # Move left while the current smoothed value is lower than the previous smoothed value
        L_plateau_scan = L_threshold_cross
        while L_plateau_scan > 0 and bmag_fast_smooth[L_plateau_scan] < bmag_fast_smooth[L_plateau_scan - 1]:
            L_plateau_scan -= 1
        L_avg_inflect = L_plateau_scan

        # If the identified inflection point is too close to the threshold cross, scan further back in time
        if L_threshold_cross - L_avg_inflect < int(1 * determine_sampling_rate(times_clipped, INSTRUMENT_SAMPLING_RATE, True)):
            L_avg_inflect = max(0, L_threshold_cross - int(1 * determine_sampling_rate(times_clipped, INSTRUMENT_SAMPLING_RATE, True)))
            left_max_slice = bmag[L_avg_inflect:L_threshold_cross + 1]
            print(f"Left peak search extended range: {L_avg_inflect} to {L_threshold_cross}, slice length: {len(left_max_slice)}")
        else:
            left_max_slice = bmag[L_avg_inflect:L_threshold_cross + 1]
            print(f"Left peak search range: {L_avg_inflect} to {L_threshold_cross}, slice length: {len(left_max_slice)}")

        if len(left_max_slice) > 0:
            left_max_value_idx = np.argmax(left_max_slice) + L_avg_inflect
            left_max_value = bmag[left_max_value_idx]
            print(f"Left maximum detected at index {left_max_value_idx}, value: {left_max_value}")
        else:
            print("Warning: Empty slice for finding the left maximum.")
            continue  # Skip this hole and move to the next one
        #endregion
        
    #----- ✅ 5: Find the right peak (maximum) after the drop using the fast smoothing window-----//
        #region Right Peak Scan Block
        R_plateau_scan = R_threshold_cross
        while R_plateau_scan < len(bmag_fast_smooth) - 1 and bmag_fast_smooth[R_plateau_scan] < bmag_fast_smooth[R_plateau_scan + 1]:
            R_plateau_scan += 1
        
        R_avg_inflect = R_plateau_scan  # Assign the inflection point index for R
        
        # Now scan the region from R_avg_inflect to R_plateau_scan for the true maximum
        slice_bmag = bmag[R_threshold_cross:R_avg_inflect + 1]
        print(f"Right peak search range: {R_threshold_cross} to {R_avg_inflect}, slice length: {len(slice_bmag)}")
        
        if len(slice_bmag) > 0:
            right_max_value_idx = np.argmax(slice_bmag) + R_threshold_cross
            right_max_value_idx = min(right_max_value_idx, len(bmag) - 1)  # Ensure it's within bounds
            right_max_value = bmag[right_max_value_idx]
            print(f"Right maximum detected at index {right_max_value_idx}, value: {right_max_value}")
        else:
            # Handle the case where the slice is empty
            print(f"Warning: Empty slice for finding the right maximum: R_threshold_cross={R_threshold_cross}, R_avg_inflect={R_avg_inflect}")
            right_max_value_idx = min(R_threshold_cross, len(bmag) - 1)  # Ensure it's within bounds
            right_max_value = bmag[right_max_value_idx]
            break
        #endregion

    #----- ✅ 6: Process Asymmetry-----//
        #region Assymetry Processing
        hole_info = process_asymmetry(
            left_max_value, right_max_value,
            left_max_value_idx, right_max_value_idx,
            L_threshold_cross, R_threshold_cross,
            times_clipped, asymetric_peak_threshold,
            symmetrical_peak_scan_window_in_secs,
            bmag, bmag_slow_smooth, bmag_fast_smooth,
            determine_sampling_rate, INSTRUMENT_SAMPLING_RATE,
            max_window_seconds,
            break_for_assymettry,
            break_for_complex_hole
        )
    
        if hole_info is None:  # If the processing was skipped due to asymmetry
            hole_counter['asymmetric'] += 1
            if break_for_assymettry:
                continue  # Skip to the next iteration
        else:
            if hole_info.get("status") == "complex":
                hole_counter['complex'] += 1
                continue  # Skip to the next iteration

            if hole_info.get("status") == "unresolved_asymmetry":
                hole_counter['unresolved_asymmetry'] += 1
                continue  # Skip to the next iteration

            # If we're here, the hole is either not asymmetric or the asymmetry was resolved
            if hole_info.get("asymmetrical_initial_peaks_flag", False):
                hole_counter['asymmetric_initial'] += 1

            if hole_info.get("complex_hole_flag", True):
                hole_counter['complex_holes'] += 1

            # Update all relevant variables based on the result from process_asymmetry  
            left_max_value_idx = hole_info.get("left_max_value_idx")
            right_max_value_idx = hole_info.get("right_max_value_idx")
            left_max_value = hole_info.get("left_max_value")
            right_max_value = hole_info.get("right_max_value")
            L_threshold_cross = hole_info.get("L_threshold_cross")
            R_threshold_cross = hole_info.get("R_threshold_cross")
            min_idx = hole_info.get("min_idx")
            min_value = hole_info.get("min_value")
            complex_hole_flag = hole_info.get("complex_hole_flag")
        #endregion
                
    #----- ✅ 7: Determine the Bave for Bave_scan_seconds before and after the hole itself (save one value for before and one for after)-----//
        #region Calculate Bave Block
        # Calculate the sampling rate
        sampling_rate = determine_sampling_rate(times_clipped, INSTRUMENT_SAMPLING_RATE, use_calculated_sampling_rate)

        # Convert search seconds into number of samples
        half_second_samples = int(Bave_scan_seconds * sampling_rate)
        
        # Ensure the indices are within bounds
        L_before_idx = max(0, left_max_value_idx - half_second_samples)
        R_after_idx = min(len(bmag) - 1, right_max_value_idx + half_second_samples)
        
        # Calculate Bave before and after the hole
        Bave_before = np.mean(bmag[L_before_idx:left_max_value_idx])
        Bave_after = np.mean(bmag[right_max_value_idx:R_after_idx])
        
        print(f"Bave_before: {Bave_before}, Bave_after: {Bave_after}")
        #endregion
        
    #----- ✅ 8: Calculate hole depth (take the avg of the two before and after values), first absolute hole depth and then relative-----//
        #region Calculate Hole Depth Block
        Bave = (Bave_before + Bave_after) / 2  # Average of the field before and after the hole
        
        # Calculate absolute hole depth
        hole_abs_depth = Bave - min_value
        # Calculate relative hole depth
        hole_percentage_depth = (hole_abs_depth / Bave) * 100
        
        print(f"Absolute Hole Depth: {hole_abs_depth}, Relative Hole Depth: {hole_percentage_depth}%")
        
        # If the relative depth is not greater than depth_percentage_threshold, print a flag as 🇲🇦 too shallow
        if hole_percentage_depth < depth_percentage_threshold * 100:  # Convert threshold to percentage for comparison
            print(f"🇲🇦 Too shallow: relative depth is {hole_percentage_depth}%")
            hole_counter['shallow'] += 1
            # Conditional behavior: If break_for_shallow_hole is enabled, skip this hole and move to the next
            if break_for_shallow_hole:
                print("-----⛔️ Skipping this hole due to insufficient depth.")
                continue  # Skip the remaining processing for this hole and move to the next iteration
        print(f"-----🕳️ Hole relative depth is {hole_percentage_depth:.1f}%")
        #endregion

    #----- ✅ 9: Calculate the hole change angle and redefine hole boundaries based on stdev-----//
        #region Calculate Hole Angle and Boundaries Block
        # Inside the main loop where you're processing holes:
        tS, tE, W_angle = calculate_hole_angle_and_boundaries(
            bmag, br, bt, bn, left_max_value_idx, right_max_value_idx, min_idx, 
            sampling_rate, Bave_window_seconds, wide_angle_threshold, break_for_wide_angle
        )
        
        # If the hole was skipped, continue to the next iteration
        if tS is None or tE is None or W_angle is None:
            hole_counter['wide_angle'] += 1
            if break_for_wide_angle:
                continue
        
        # Update hole_info to include the new boundaries tS and tE
        hole_info.update({"tS": tS, "tE": tE, "W_angle": W_angle})
        #endregion
    #----- ✅ 10: Calculate the number of First Derivative 0 Crossings (with a specified smoothing window) between beginning and end of the hole-----//
        #region Zero Crossing Block 
        zero_crossings, zero_crossings_indices = analyze_derivative_zero_crossings(
            bmag, times_clipped, left_max_value_idx, right_max_value_idx,
            derivative_window_seconds, sampling_rate, mean_threshold,
            OUTPUT_ZERO_CROSSING_PLOT
        )

        # Check if zero crossings exceed the threshold
        if zero_crossings >= threshold_for_derivative_0_crossings_flag:
            print(f"🇲🇦 Too many zero crossings: {zero_crossings} (Threshold: {threshold_for_derivative_0_crossings_flag})")
            hole_counter['derivative_crossings'] += 1
            if break_for_derivative_crossings:
                print("-----⛔️ Skipping this hole due to excessive zero crossings.")
                continue  # Skip the remaining processing for this hole and move to the next iteration

        # Update hole_info with zero crossings data
        hole_info.update({"zero_crossings": zero_crossings})
        #endregion  

    #----- ✅ 11: Store the results-----//
        #region Store Results Block
        # Store the results and flags for the current hole
        magnetic_hole_details.append(hole_info)
        hole_minima.append(hole_info["min_idx"])
        hole_maxima_pairs.append((hole_info["left_max_value_idx"], hole_info["right_max_value_idx"]))
        magnetic_holes.append((hole_info["L_threshold_cross"], hole_info["R_threshold_cross"]))
        

        if search_in_progress_output:
            print(f"-----⭐️ Magnetic hole identified from index {hole_info['left_max_value_idx']} to {hole_info['right_max_value_idx']}")
                
        i = hole_info["R_threshold_cross"] + 1
        hole_counter['confirmed'] += 1
        #endregion
    
    print(f"Returning: {len(magnetic_holes)} holes, {len(hole_minima)} minima, {len(hole_maxima_pairs)} max pairs")
    return magnetic_holes, hole_minima, hole_maxima_pairs, times_clipped, bmag,  magnetic_hole_details

#-------- ⚙️ Constants--------//
#region Constants Block
INSTRUMENT_SAMPLING_RATE = 292.9  # Will not be used if use_calculated_sampling_rate = 1
use_calculated_sampling_rate = 1
depth_percentage_threshold = .25
smoothing_window_seconds = 8
derivative_window_seconds = .2
min_max_finding_smooth_window = .3
mean_threshold = 0.8
search_in_progress_output = True
additional_seconds_for_min_search = 0.2
asymetric_peak_threshold = .25
symmetrical_peak_scan_window_in_secs = 2
Bave_scan_seconds = .1
Bave_window_seconds = 20
wide_angle_threshold = 15
small_threshold_cross_flag = 10
small_threshold_cross_adjustment = 10
#endregion

smoothing_window_seconds = 8  # 8-second smoothing for primary detection
derivative_window_seconds = .2  # Window for smoothing before calculating the first derivative

# min_max_finding_smooth_window = .05  # 0.05 was being tried for a special case and seemed to work well...
min_max_finding_smooth_window = .3  # 0.3-second smoothing for detailed max finding, this was the OG

mean_threshold = 0.8  # 80% of the smoothed value
search_in_progress_output = True  # Set to True for detailed output
additional_seconds_for_min_search = 0.2  # Extend the search range

# Define a threshold for peak asymmetry
asymetric_peak_threshold = .25  # 🪐 25% asymmetry threshold, was originally 10
symmetrical_peak_scan_window_in_secs = 2  # Time window to scan for symmetrical peaks in seconds

Bave_scan_seconds = .1

# New constant for wide angle threshold
Bave_window_seconds = 20  # Window size for calculating Bave and delta_B, this is where the angle is calculated
wide_angle_threshold = 15  # 15 degrees threshold for W angle

small_threshold_cross_flag = 10  # Define the small threshold cross (i.e. we only cross the threshold for _ samples)
small_threshold_cross_adjustment = 10  # Define the adjustment when small threshold cross is detected (i.e. widen by _ to help our algorithm)
#endregion

# -------- 🤗 File Output & Plotting Options--------//
#region File Output & Plotting Options Block
OUTPUT_PLOT = 1  # Set to 1 to output the plot
plot_hole_minimum = 0  # Set to 1 to plot green lines at the minimum points within holes
plot_smooth_threshold_crossing = 1  # Set to 1 to plot blue and purple lines at smooth threshold crossings (see mean_threshold defined below)
SAVE_PLOT = 1 #Save the plot to the subdirectory


OUTPUT_ZERO_CROSSING_PLOT = 0 #⛰️

IZOTOPE_MARKER_FILE_OUTPUT_MAX_AND_MIN = 1  # Set to 1 to save iZotope formatted output with max and min indices to a .txt file
MARKER_FILE_VERSION = 3  # Version number for marker file
IZOTOPE_MARKER_FILE_OUTPUT = 0

EXPORT_AUDIO_FILES = 1  # Set to 1 to export audio files
AUDIO_SAMPLING_RATE = 22000  # Sampling rate for the audio files

# New Option for Annotated Markers
Marker_Files_With_Annotated_Markers = 0  # Set to 1 to include drop percentage and width in marker name
Marker_Files_With_Hole_Numbers = 0

SEARCH_IN_PROGRESS_OUTPUT = 1

#-------- 📈 Plotting Options --------//
plot_hole_minimum = 1  # 1 to plot minima, 0 to skip
plot_smooth_threshold_crossing = 1  # 1 to plot threshold crossings, 0 to skip
#endregion

#-------- 🇲🇦 Flag Handling--------//
#region Flag Handling Block 
break_for_shallow_hole = 1 # 🇲🇦 flag for skipping if a hole is too shallow
break_for_assymettry = 0 # 🇲🇦 flag for skipping if a whole is assymetrical
break_for_wide_angle = 0  # 🇲🇦 flag for handling wide angle cases
break_for_small_threshold_cross = 0  # 🇲🇦 flag to skip small threshold crosses
break_for_complex_hole = 0 # 🇲🇦 flag for skipping complex holes
threshold_for_derivative_0_crossings_flag = 1000 #If the .1s smoothed first derivative crosses this many times or higher, raise a flag
break_for_derivative_crossings = 0
#endregion

#--------⏱️ Set time range--------//
#region Time Range Block
# Define the input parameters
# trange = ['2023-09-28/06:10:00.000', '2023-09-28/07:10:00.000'] #Whole Shebang
# trange = ['2023-09-28/06:37:15.000', '2023-09-28/06:37:45.000'] #wide lots o dips
# trange = ['2023-09-28/06:37:05.500', '2023-09-28/06:37:08.000'] #Interesting Test Case WE'VE BEEN USING for Derivative
# trange = ['2023-09-28/06:39:00.000', '2023-09-28/06:40:10.000'] #⭐️⭐️⭐️ GREAT region for solid hole testing⭐️⭐️⭐️
trange = ['2023-09-28/06:38:10.000', '2023-09-28/06:40:10.000'] #⭐️⭐️⭐️ GREAT region for solid hole testing⭐️⭐️⭐️
# trange = ['2023-09-28/06:39:07.000', '2023-09-28/06:39:10.000'] #WONKY WONKS
# trange = ['2023-09-28/06:39:50.000', '2023-09-28/06:39:55.000'] #⭐️⭐️⭐️ Checking a single hole
# trange = ['2023-09-28/06:39:31.000', '2023-09-28/06:39:35.000'] #⭐️⭐️⭐️ PERFECT Single hole for testing⭐️⭐️⭐️
# trange = ['2023-09-28/06:39:45.000', '2023-09-28/06:39:50.000'] #⭐️⭐️⭐️ ANOTHER PERFECT Single hole for testing⭐️⭐️⭐️
# trange = ['2023-09-28/06:37:05.500', '2023-09-28/06:37:08.000'] #Interesting Test Case WE'VE BEEN USING for Derivative
# trange = ['2023-09-28/06:36:022', '2023-09-28/06:36:24'] # A pretty hole ⭐️
# trange = ['2023-09-28/06:29:18', '2023-09-28/06:29:22'] #with a larger window #🇲🇦 Asymmetry between peaks: 42.25%
#endregion

time_check(trange)

# At the beginning of your main script, after setting up save_dir
sub_save_dir = setup_output_directory(trange, save_dir)
print(f"🙌🙌🙌Main script: sub_save_dir set to {sub_save_dir}")

# Call the function to detect magnetic holes
magnetic_holes, hole_minima, hole_maxima_pairs, times_clipped, bmag, magnetic_hole_details = detect_magnetic_holes(
    trange, 
    smoothing_window_seconds, 
    min_max_finding_smooth_window, 
    mean_threshold, 
    search_in_progress_output, 
    Bave_scan_seconds, 
    break_for_assymettry, 
    small_threshold_cross_flag,          
    small_threshold_cross_adjustment,    
    break_for_small_threshold_cross,     
    break_for_complex_hole,
    derivative_window_seconds,  # Pass the derivative window into the function
    OUTPUT_ZERO_CROSSING_PLOT,
    SEARCH_IN_PROGRESS_OUTPUT,
    INSTRUMENT_SAMPLING_RATE,
    use_calculated_sampling_rate
    
)

# Plotting the results if configured
if OUTPUT_PLOT:
    plot_mag_data_with_holes_and_minimum(
        times_clipped, 
        bmag, 
        magnetic_holes, 
        hole_minima, 
        hole_maxima_pairs, 
        plot_hole_minimum, 
        plot_smooth_threshold_crossing,
        trange,  # Add this
        save_dir,  # Add this
        SAVE_PLOT  # Add this if you don't want to save the plot by default
    )
# Create the settings dictionary
settings = {
    "INSTRUMENT_SAMPLING_RATE": INSTRUMENT_SAMPLING_RATE,
    "use_calculated_sampling_rate": use_calculated_sampling_rate,
    "depth_percentage_threshold": depth_percentage_threshold,
    "smoothing_window_seconds": smoothing_window_seconds,
    "derivative_window_seconds": derivative_window_seconds,
    "min_max_finding_smooth_window": min_max_finding_smooth_window,
    "mean_threshold": mean_threshold,
    "search_in_progress_output": search_in_progress_output,
    "additional_seconds_for_min_search": additional_seconds_for_min_search,
    "asymetric_peak_threshold": asymetric_peak_threshold,
    "symmetrical_peak_scan_window_in_secs": symmetrical_peak_scan_window_in_secs,
    "Bave_scan_seconds": Bave_scan_seconds,
    "Bave_window_seconds": Bave_window_seconds,
    "wide_angle_threshold": wide_angle_threshold,
    "small_threshold_cross_flag": small_threshold_cross_flag,
    "small_threshold_cross_adjustment": small_threshold_cross_adjustment,
    "OUTPUT_PLOT": OUTPUT_PLOT,
    "plot_hole_minimum": plot_hole_minimum,
    "plot_smooth_threshold_crossing": plot_smooth_threshold_crossing,
    "OUTPUT_ZERO_CROSSING_PLOT": OUTPUT_ZERO_CROSSING_PLOT,
    "IZOTOPE_MARKER_FILE_OUTPUT_MAX_AND_MIN": IZOTOPE_MARKER_FILE_OUTPUT_MAX_AND_MIN,
    "MARKER_FILE_VERSION": MARKER_FILE_VERSION,
    "IZOTOPE_MARKER_FILE_OUTPUT": IZOTOPE_MARKER_FILE_OUTPUT,
    "EXPORT_AUDIO_FILES": EXPORT_AUDIO_FILES,
    "AUDIO_SAMPLING_RATE": AUDIO_SAMPLING_RATE,
    "Marker_Files_With_Annotated_Markers": Marker_Files_With_Annotated_Markers,
    "SEARCH_IN_PROGRESS_OUTPUT": SEARCH_IN_PROGRESS_OUTPUT,
    "break_for_shallow_hole": break_for_shallow_hole,
    "break_for_assymettry": break_for_assymettry,
    "break_for_wide_angle": break_for_wide_angle,
    "break_for_small_threshold_cross": break_for_small_threshold_cross,
    "break_for_complex_hole": break_for_complex_hole,
    "threshold_for_derivative_0_crossings_flag": threshold_for_derivative_0_crossings_flag,
    "break_for_derivative_crossings": break_for_derivative_crossings
}

# Get the sub-directory path
# sub_save_dir = setup_output_directory(trange, save_dir)

# last_dir_file = "last_selected_dir.txt"
# save_dir = set_save_directory(last_dir_file)
print(f'🛟 save_dir = {save_dir}')

# Use sub_save_dir for all file operations
settings_file_path = os.path.join(sub_save_dir, 'magnetic_hole_detection_settings.json')
with open(settings_file_path, 'w') as f:
    json.dump(settings, f, indent=4)

print(f"Settings saved to: {settings_file_path}")

# Generate marker file if needed
if IZOTOPE_MARKER_FILE_OUTPUT or IZOTOPE_MARKER_FILE_OUTPUT_MAX_AND_MIN:
    # Call the output_magnetic_holes function with the settings dictionary
    output_magnetic_holes(
        magnetic_holes,
        hole_maxima_pairs,
        times_clipped,
        bmag,
        IZOTOPE_MARKER_FILE_OUTPUT,
        IZOTOPE_MARKER_FILE_OUTPUT_MAX_AND_MIN,
        trange,
        MARKER_FILE_VERSION,
        SEARCH_IN_PROGRESS_OUTPUT,
        save_dir,
        INSTRUMENT_SAMPLING_RATE,
        Marker_Files_With_Annotated_Markers,
        Marker_Files_With_Hole_Numbers,
        magnetic_hole_details
    )

# Export audio files if needed
if EXPORT_AUDIO_FILES:
    audify_high_res_mag_data_without_plot(trange[0], trange[1], sub_save_dir, AUDIO_SAMPLING_RATE, sub_save_dir)

# Summary print statements
print("\n--- Magnetic Hole Detection Summary ---")
print(f"🔢 {hole_counter['potential']} Total potential holes identified")
print(f"✅ {hole_counter['confirmed']} Total holes confirmed")
print(f"🌀 {hole_counter['complex_holes']} Complex/Assymetrical holes")
print(f"{'⛔️' if break_for_shallow_hole else '🆗'} {hole_counter['shallow']} Shallow holes")
# print(f"{'⛔️' if break_for_assymettry else '🆗'} {hole_counter['asymmetric']} Asymmetric holes")
print(f"{'⛔️' if break_for_wide_angle else '🆗'} {hole_counter['wide_angle']} Wide angle holes")
print(f"{'⛔️' if break_for_small_threshold_cross else '🆗'} {hole_counter['small_threshold_cross']} Small threshold crosses")
print(f"{'⛔️' if break_for_assymettry else '🆗'} {hole_counter['unresolved_asymmetry']} Unresolved asymmetric holes")
print(f"🆗 {hole_counter['asymmetric_initial']} Initially asymmetric holes (resolved)")
# print(f"🆗 {hole_counter['complex_resolved']} Complex holes (resolved)")
# print(f"{'⛔️' if break_for_complex_hole else '🆗'} {hole_counter.get('complex', 0)} Complex holes")
# print(f"{'⛔️' if break_for_derivative_crossings else '🆗'} {hole_counter['derivative_crossings']} Excessive derivative crossings")
print("-------------------------------------")

print("Settings have been saved to a JSON file in the sub-directory.")
