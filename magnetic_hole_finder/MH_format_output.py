from datetime import datetime, timedelta
import numpy as np
import importlib
from dateutil.parser import parse as dateutil_parse

from .data_management import *
from .data_audification import *
from .time_management import format_time, convert_time_range_to_str

def output_magnetic_holes(magnetic_holes,
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
):  # Add settings parameter

    if IZOTOPE_MARKER_FILE_OUTPUT or IZOTOPE_MARKER_FILE_OUTPUT_MAX_AND_MIN:
        print("Saving iZotope marker file output")

        izotope_output = []
        
        # Set up the output directory structure based on trange and encounter number
        print(f"Running setup_output_directory from iZotope_marker_file_output:")
        sub_save_dir = setup_output_directory(trange, save_dir)

        # Determine the encounter number using the get_encounter_number function
        start_date = trange[0].split(' ')[0] if ' ' in trange[0] else trange[0].split('/')[0]  # Extract the date part from trange[0]
        encounter_number = get_encounter_number(start_date)

        # Add metadata to the izotope_output
        izotope_output.extend([
            # f"[Metadata/Settings]\t0\t\tMEAN_WINDOW = {settings['MEAN_WINDOW']}  # Number of samples to consider for calculating the mean",
            # f"[Metadata/Settings]\t0\t\tLOOK_AHEAD_WINDOW = {settings['LOOK_AHEAD_WINDOW']}  # Number of samples to look ahead for a MH",
            # f"[Metadata/Settings]\t0\t\tDEPTH_PERCENTAGE_THRESHOLD = {settings['DEPTH_PERCENTAGE_THRESHOLD']}  # Percentage drop to consider a MH",
            # f"[Metadata/Settings]\t0\t\tMIN_MAX_HOLE_FINDER_SMOOTHING = {settings['MIN_MAX_HOLE_FINDER_SMOOTHING']}  # Smoothing factor for finding the min and max of the hole",
            # f"[Metadata/Settings]\t0\t\tMIN_SEARCH_RANGE = {settings['MIN_SEARCH_RANGE']}  # Number of samples to search forward and backward for the actual minimum",
            # f"[Metadata/Settings]\t0\t\tMAX_SEARCH_RANGE = {settings['MAX_SEARCH_RANGE']}  # Number of samples to search forward and backward for the actual maximum",
            # f"[Metadata/Settings]\t0\t\tMINIMUM_PEAK_THRESHOLD = {settings['MINIMUM_PEAK_THRESHOLD']}  # Minimum percentage of average-magnitude above which peaks will be considered",
            f"[Metadata/trange]\t0\t\ttrange = {trange}",
            f"[Metadata/Encountr]\t0\t\t{encounter_number}",
            f"[Metadata/Holes]\t0\t\tHoles Found: {len(magnetic_holes)}",
        ])

        # Calculate average hole width and depth
        widths = [end - start for start, end in magnetic_holes]
        avg_width = np.mean(widths)
        depths = [(bmag[start] + bmag[end]) / 2 - min(bmag[start:end+1]) for start, end in magnetic_holes]
        avg_depth_percentage = np.mean([(depth / ((bmag[start] + bmag[end]) / 2)) * 100 for depth, (start, end) in zip(depths, magnetic_holes)])

        izotope_output.extend([
            f"[Metadata/AvgWidth]\t0\t\tAvg Hole Width: {avg_width:.2f}",
            f"[Metadata/AvgDepth]\t0\t\tAvg Hole Depth: {avg_depth_percentage:.2f}%",
        ])

        # Calculate duration and add to metadata
        # Use dateutil.parser.parse to handle both space and slash-separated formats flexibly
        try:
            start_time = dateutil_parse(trange[0])
            end_time = dateutil_parse(trange[1])
            duration = end_time - start_time
            izotope_output.append(f"[Metadata/Duration]\t0\t\tTotal Duration: {duration}")
        except Exception as e:
            print(f"Warning: Error parsing time range for duration calculation: {e}")
            izotope_output.append(f"[Metadata/Duration]\t0\t\tTotal Duration: CALCULATION_ERROR")

        # Add total samples and sampling rate to metadata
        total_samples = len(bmag)
        # sampling_rate = settings['sampling_rate']
        izotope_output.extend([
            f"[Metadata/Samples]\t0\t\tTotal Samples: {total_samples}",
            f"[Metadata/InstrSR]\t0\t\tInstr Sampling Rate: {INSTRUMENT_SAMPLING_RATE:.2f} s/s",
        ])

        # Add an empty line after metadata
        izotope_output.append("")

        for idx, ((left_max, right_max), (start, end), hole_info) in enumerate(zip(hole_maxima_pairs, magnetic_holes, magnetic_hole_details)):
            start_value = bmag[left_max]
            end_value = bmag[right_max]
            min_value = min(bmag[start:end+1])
            min_idx = start + np.argmin(bmag[start:end+1])
            average_peak = (start_value + end_value) / 2
            hole_width = right_max - left_max
            percentage_decrease = (1 - (min_value / average_peak)) * 100

            complex_flag = "Complex" if hole_info.get("complex_hole_flag", False) else ""

            if Marker_Files_With_Hole_Numbers == 1:
                if Marker_Files_With_Annotated_Markers == 1:
                    marker_description = f"MH {idx+1} - {hole_width} samples wide\t{left_max}\t{right_max}\t{percentage_decrease:.2f}% Drop\t{complex_flag}".strip()
                else:
                    marker_description = f"MH {idx+1}\t{left_max}\t{right_max}\t{complex_flag}"
            else:
                if Marker_Files_With_Annotated_Markers == 1:
                    marker_description = f"MH - {hole_width} samples wide\t{left_max}\t{right_max}\t{percentage_decrease:.2f}% Drop\t{complex_flag}"
                else:
                    marker_description = f"MH\t{left_max}\t{right_max}\t{complex_flag}"

            izotope_output.append(marker_description)

            if IZOTOPE_MARKER_FILE_OUTPUT_MAX_AND_MIN:
                if Marker_Files_With_Hole_Numbers == 1:
                    izotope_output.append(f"MH_MIN {idx+1}\t{min_idx}")
                else:
                    izotope_output.append(f"MH_MIN\t{min_idx}")

        if save_dir:
            file_name = generate_marker_file_name(trange, MARKER_FILE_VERSION)
            
            if IZOTOPE_MARKER_FILE_OUTPUT_MAX_AND_MIN:
                file_name = file_name.replace(".txt", "_MAX_AND_MIN.txt")
            
            file_path = f"{sub_save_dir}/{file_name}"
            print(f"File path: {file_path}")
            try:
                with open(file_path, 'w') as file:
                    # Write metadata first
                    for line in izotope_output:
                        if line.startswith('[Metadata'):
                            file.write(line + '\n')
                    
                    # Write an empty line after metadata
                    file.write('\n')
                    
                    # Write marker data
                    for line in izotope_output:
                        if not line.startswith('[Metadata'):
                            file.write(line + '\n')
                print(f"iZotope marker file saved to {file_path}")
            except Exception as e:
                print(f"Error saving file: {e}")

        show_directory_button(save_dir)

def generate_marker_file_name(trange, version):
    # Use dateutil.parser to handle different time formats
    try:
        start_time_dt = dateutil_parse(trange[0])
        end_time_dt = dateutil_parse(trange[1])
        
        # Convert to standard format for further processing
        start_datetime_str = start_time_dt.strftime('%Y_%m_%d_%Hh_%Mm_%Ss')
        stop_datetime_str = end_time_dt.strftime('%Y_%m_%d_%Hh_%Mm_%Ss')
        
        start_date, start_time = format_time(start_datetime_str)
        stop_date, stop_time = format_time(stop_datetime_str)
        
        encounter_number = get_encounter_number(start_date)
        
        # Adjust for day-crossing in the file naming
        if start_date == stop_date:
            stop_time_formatted = stop_time
        else:
            if start_date[:4] == stop_date[:4]:  # Same year
                stop_time_formatted = f"{stop_date[5:]}_{stop_time}"
            else:
                stop_time_formatted = f"{stop_date}_{stop_time}"
                
        file_name = f"PSP_MH_Marker_Set_{encounter_number}_{start_date}_{start_time}_to_{stop_time_formatted}_V{version}.txt"
        return file_name
    except Exception as e:
        print(f"Error in generate_marker_file_name: {e}")
        # Fall back to a basic name if parsing fails
        return f"PSP_MH_Marker_Set_E00_{trange[0].replace('/', '_').replace(' ', '_')}_to_{trange[1].replace('/', '_').replace(' ', '_')}_V{version}.txt"

current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f'{current_time} - 🙂 MH Outputs are happy!')