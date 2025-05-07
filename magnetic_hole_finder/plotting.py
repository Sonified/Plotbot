#file: plotting.py
global save_dir

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .data_management import *
from .time_management import *

def plot_mag_data_with_holes(times, b_values, magnetic_holes): #The mac daddy
    # Plot magnetic field strength
    plt.figure(figsize=(12, 3))
    plt.plot(times, b_values, label='|B|', color='black')

    # Plot detected magnetic holes as shaded regions
    for start_idx, min_idx, end_idx in magnetic_holes:  # Adjusted to handle three values
        plt.axvspan(times[start_idx], times[end_idx], color='red', alpha=0.3)
        plt.axvline(times[min_idx], color='blue', linestyle='--', label='Minimum in Hole')

    plt.xlabel('Time')
    plt.ylabel('Magnetic Field Strength (nT)')
    plt.title('Magnetic Field Strength with Detected Magnetic Holes')
    plt.legend()
    plt.show()

def plot_mag_data_with_holes_and_minimum(times, b_values, magnetic_holes, hole_minima, hole_maxima_pairs, plot_hole_minimum, plot_smooth_threshold_crossing, trange, save_dir, save_plot=False):
    plt.figure(figsize=(12, 6))
    plt.plot(times, b_values, label='|B|', color='black')

    if plot_hole_minimum:
        for i, min_idx in enumerate(hole_minima):
            plt.axvline(times[min_idx], color='green', linestyle='--', label='Minimum in Hole' if i == 0 else '')

    if plot_smooth_threshold_crossing:
        for (L_threshold_cross, R_threshold_cross) in magnetic_holes:
            if R_threshold_cross < len(times):
                plt.axvline(times[L_threshold_cross], color='blue', linestyle='-', label='Left Crossing' if L_threshold_cross == magnetic_holes[0][0] else "")
                plt.axvline(times[R_threshold_cross], color='purple', linestyle='-', label='Right Crossing' if R_threshold_cross == magnetic_holes[0][1] else "")
            else:
                print(f"Skipping R_threshold_cross {R_threshold_cross} as it is out of bounds.")

    for i, (left_max_value_idx, right_max_value_idx) in enumerate(hole_maxima_pairs):
        plt.axvspan(times[left_max_value_idx], times[right_max_value_idx], color='red', alpha=0.3, label='Hole Area' if i == 0 else '')

    plt.xlabel('Time')
    plt.ylabel('Magnetic Field Strength (nT)')
    plt.title('Magnetic Field Strength with Detected Magnetic Holes')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

    if save_plot:
        # Use the setup_output_directory function to get the correct subdirectory
        sub_dir_path = setup_output_directory(trange, save_dir)
        
        start_datetime_str, stop_datetime_str = convert_time_range_to_str(trange[0], trange[1])
        start_date, start_time = format_time(start_datetime_str)
        stop_date, stop_time = format_time(stop_datetime_str)

        if start_date == stop_date:
            stop_time_formatted = stop_time
        else:
            if start_date[:4] == stop_date[:4]:  # Same year
                stop_time_formatted = f"{stop_date[5:]}_{stop_time}"
            else:
                stop_time_formatted = f"{stop_date}_{stop_time}"

        encounter_number = get_encounter_number(start_date)
        plot_filename = f"{encounter_number}_PSP_FIELDS_001_{start_date}_{start_time}_to_{stop_time_formatted}_Bmag_HOLES_PLOT.png"
        plot_path = os.path.join(sub_dir_path, plot_filename)
        plt.savefig(plot_path)
        print(f"Plot saved: {plot_path}")

    plt.show()  # This will display the plot regardless of whether it's saved or not

    if save_plot:
        return plot_path

# Define the new function to plot high-resolution magnetic field data and magnitude
def plot_high_res_mag_data(rangeStart, rangeStop):
    global times, x_data, y_data, z_data, bmag, trange, trange_start, trange_stop  # Ensure these variables are global
    
    """
    Download and plot high-resolution magnetic field data, including the magnitude of the magnetic field.

    Parameters:
    rangeStart (str): Start time in the format 'YYYY/MM/DD HH:MM:SS.sss'
    rangeStop (str): Stop time in the format 'YYYY/MM/DD HH:MM:SS.sss'
    """
    # Convert dates
    trange_start = convert_to_trange_format(rangeStart)
    trange_stop = convert_to_trange_format(rangeStop)
    trange = [trange_start, trange_stop]

    # Download high-resolution magnetic field data
    print("Downloading high-resolution magnetic field data...")
    data_quants = pyspedas.psp.fields(trange=trange, datatype='mag_rtn', level='l2', time_clip=True, get_support_data=True, notplot=True)

    if 'psp_fld_l2_mag_RTN' in data_quants:
        # Access the magnetic field vector data
        mag_data = data_quants['psp_fld_l2_mag_RTN']
        times = mag_data['x']
        data_values = mag_data['y']

        # Ensure times are in datetime format for comparison
        import pandas as pd
        if not isinstance(times[0], datetime):
            times = pd.to_datetime(times).to_pydatetime()

        # Clip the data to the desired time range
        start_time = datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S')
        end_time = datetime.strptime(trange[1], '%Y-%m-%d/%H:%M:%S')
        time_indices = (times >= start_time) & (times <= end_time)
        
        clipped_times = times[time_indices]
        clipped_data_values = data_values[time_indices]

        # Split the magnetic field vector into its components
        x_data = clipped_data_values[:, 0]
        y_data = clipped_data_values[:, 1]
        z_data = clipped_data_values[:, 2]

        # Store Br, Bt, Bn in separate panels
        store_data('Br_high', data={'x': clipped_times, 'y': x_data})
        store_data('Bt_high', data={'x': clipped_times, 'y': y_data})
        store_data('Bn_high', data={'x': clipped_times, 'y': z_data})

        # Rename variables to apply metadata
        tplot_rename('Br_high', 'Br')
        tplot_rename('Bt_high', 'Bt')
        tplot_rename('Bn_high', 'Bn')

        # Calculate the magnitude of the magnetic field
        bmag = np.sqrt(x_data**2 + y_data**2 + z_data**2)
        store_data('|B|', data={'x': clipped_times, 'y': bmag})
        options('|B|', 'color', 'green')

        # Set plot options and titles
        options('Br', 'color', 'black')
        options('Bt', 'color', 'red')
        options('Bn', 'color', 'blue')

        [options(name, 'ytitle', name) for name in ['Br', 'Bt', 'Bn', '|B|']]
        xlim(trange_start, trange_stop)
        set_mag_plot_title(rangeStart, rangeStop)

        # Plot the data
        tplot(['|B|', 'Br', 'Bt', 'Bn'])

        # Display the button to save the plot
        save_plot_button(trange)
    else:
        print("The expected variable 'psp_fld_l2_mag_RTN' was not found in the downloaded data. Please check the data availability and try again.")

def plot_existing_high_res_mag_data(rangeStart, rangeStop):
    """
    Plot high-resolution magnetic field data, including the magnitude of the magnetic field, using already defined variables.

    Parameters:
    rangeStart (str): Start time in the format 'YYYY/MM/DD HH:MM:SS.sss'
    rangeStop (str): Stop time in the format 'YYYY/MM/DD HH:MM:SS.sss'
    """
    global times, x_data, y_data, z_data, bmag, trange, trange_start, trange_stop

    # Convert dates
    trange_start = convert_to_trange_format(rangeStart)
    trange_stop = convert_to_trange_format(rangeStop)
    trange = [trange_start, trange_stop]

    # Ensure times are in datetime format for comparison
    if not isinstance(times[0], datetime):
        times = np.array([datetime.utcfromtimestamp(time) for time in times])

    # Clip the data to the desired time range
    start_time = datetime.strptime(trange_start, '%Y-%m-%d/%H:%M:%S')
    end_time = datetime.strptime(trange_stop, '%Y-%m-%d/%H:%M:%S')
    time_indices = (times >= start_time) & (times <= end_time)
    
    clipped_times = times[time_indices]
    clipped_x_data = x_data[time_indices]
    clipped_y_data = y_data[time_indices]
    clipped_z_data = z_data[time_indices]
    clipped_bmag = bmag[time_indices]

    # Store Br, Bt, Bn in separate panels
    store_data('Br_high', data={'x': clipped_times, 'y': clipped_x_data})
    store_data('Bt_high', data={'x': clipped_times, 'y': clipped_y_data})
    store_data('Bn_high', data={'x': clipped_times, 'y': clipped_z_data})
    store_data('|B|_high', data={'x': clipped_times, 'y': clipped_bmag})

    # Set plot options and titles
    options('Br_high', 'color', 'black')
    options('Bt_high', 'color', 'red')
    options('Bn_high', 'color', 'blue')
    options('|B|_high', 'color', 'green')

    [options(name, 'ytitle', name) for name in ['Br_high', 'Bt_high', 'Bn_high', '|B|_high']]
    xlim(trange_start, trange_stop)
    set_mag_plot_title(rangeStart, rangeStop)

    # Plot the data
    tplot(['Br_high', 'Bt_high', 'Bn_high', '|B|_high'])

    # Display the button to save the plot
    save_plot_button([trange_start, trange_stop])
    show_directory_button(save_dir)



def set_mag_plot_title(rangeStart, rangeStop):
    """
    Generate and set the plot title based on the start and stop times.

    Parameters:
    rangeStart (str): Start time in the format 'YYYY/MM/DD HH:MM:SS.fff'
    rangeStop (str): Stop time in the format 'YYYY/MM/DD HH:MM:SS.fff'

    Returns:
    None
    """
    # Convert the time range to formatted strings
    start_datetime_str, stop_datetime_str = convert_time_range_to_str(rangeStart, rangeStop)
    
    # Determine the encounter number
    start_date = '-'.join(start_datetime_str.split('_')[0:3])
    
    encounter_number = get_encounter_number(start_date)

    start_date, start_time = rangeStart.split(' ')[0], rangeStart.split(' ')[1]
    stop_date, stop_time = rangeStop.split(' ')[0], rangeStop.split(' ')[1]

    if start_date == stop_date:
        plot_title = f"PSP FIELDS Fluxgate Magnetometer (BRTN) {encounter_number} {start_date} {start_time.split('.')[0]} to {stop_time.split('.')[0]}"
    else:
        if start_date[:4] == stop_date[:4]:  # Same year
            plot_title = f"PSP FIELDS Fluxgate Magnetometer (BRTN) {encounter_number} {start_date} {start_time.split('.')[0]} to {stop_date[5:]} {stop_time.split('.')[0]}"  # Exclude the year from stop_date
        else:
            plot_title = f"PSP FIELDS Fluxgate Magnetometer (BRTN) {encounter_number} {rangeStart.split('.')[0]} to {rangeStop.split('.')[0]}"

    # Set the title of the plot
    options('|B|', 'title', plot_title)

def save_multiplot(trange, selected_vars):
    global save_dir  # Ensure we can modify the global save_dir variable
    if not save_dir:  # If no save directory is selected, prompt the user to choose one
        save_dir = select_directory()
        ensure_directory_exists(save_dir)

    if save_dir:
        # Generate the filename for the multiplot
        start_datetime_str, stop_datetime_str = convert_time_range_to_str(trange[0], trange[1])

        start_date, start_time = format_time(start_datetime_str)
        stop_date, stop_time = format_time(stop_datetime_str)

        # Adjust for day-crossing in the file naming
        if start_date == stop_date:
            stop_time_formatted = stop_time
        else:
            if start_date[:4] == stop_date[:4]:  # Same year
                stop_time_formatted = f"{stop_date[5:]}_{stop_time}"
            else:
                stop_time_formatted = f"{stop_date}_{stop_time}"

        # Get the encounter number
        encounter_number = get_encounter_number(start_date)

        # Generate the file name using the specified time range
        plot_filename = os.path.join(save_dir, f"{encounter_number}_PSP_Multiplot_{start_date}_{start_time}_to_{stop_time_formatted}.png")

        # Save the plot
        tplot(selected_vars, save_png=plot_filename)
        print(f"Multiplot saved: {plot_filename}")
    else:
        print("No directory selected. Please select a directory first.")


def set_multiplot_title(rangeStart, rangeStop):
    """
    Generate and set the multiplot title based on the start and stop times.

    Parameters:
    rangeStart (str): Start time in the format 'YYYY/MM/DD HH:MM:SS.fff'
    rangeStop (str): Stop time in the format 'YYYY/MM/DD HH:MM:SS.fff'

    Returns:
    str: Generated title string.
    """
    # Convert the time range to formatted strings
    start_datetime_str, stop_datetime_str = convert_time_range_to_str(rangeStart, rangeStop)
    
    # Determine the encounter number
    start_date = '-'.join(start_datetime_str.split('_')[0:3])
    
    encounter_number = get_encounter_number(start_date)

    # Split the rangeStart and rangeStop based on the detected format
    try:
        start_date, start_time = rangeStart.split(' ')[0], rangeStart.split(' ')[1]
        stop_date, stop_time = rangeStop.split(' ')[0], rangeStop.split(' ')[1]
    except IndexError:
        start_date, start_time = rangeStart.split('/')[0], rangeStart.split('/')[1]
        stop_date, stop_time = rangeStop.split('/')[0], rangeStop.split('/')[1]

    if start_date == stop_date:
        plot_title = f"PSP Multiplot {encounter_number} {start_date} {start_time.split('.')[0]} to {stop_time.split('.')[0]}"
    else:
        if start_date[:4] == stop_date[:4]:  # Same year
            plot_title = f"PSP Multiplot {encounter_number} {start_date} {start_time.split('.')[0]} to {stop_date[5:]} {stop_time.split('.')[0]}"  # Exclude the year from stop_date
        else:
            plot_title = f"PSP Multiplot {encounter_number} {rangeStart.split('.')[0]} to {rangeStop.split('.')[0]}"

    return plot_title


#---------- DERIVATIVES -------//
def plot_mag_and_derivatives_for_trange(trange):
    """
    Load data from the pickle cache and then plot the magnetic field magnitude,
    first derivative, and second derivative.

    Parameters:
    trange (list): Time range in the format ['YYYY-MM-DD/HH:MM:SS', 'YYYY-MM-DD/HH:MM:SS']
    """
    # Ensure magnetic data is loaded from the pickle cache
    start_time_loading = time.time()
    times, br, bt, bn, bmag = download_and_prepare_high_res_mag_data(trange)
    end_time_loading = time.time()
    print(f"Data loaded in {end_time_loading - start_time_loading:.2f} seconds")

    if bmag is None or len(times) == 0:
        print("No magnetic field data available for the given time range.")
        return

    # Convert times to seconds since the start time
    times_in_seconds = (pd.to_datetime(times) - pd.to_datetime(times[0])).total_seconds()

    # Calculate the first and second derivatives
    first_derivative = np.gradient(bmag, times_in_seconds)
    second_derivative = np.gradient(first_derivative, times_in_seconds)

    # Plotting
    plt.figure(figsize=(12, 12))

    # Plot Magnetic Field Magnitude
    plt.subplot(3, 1, 1)
    plt.plot(times, bmag, color='black', label='|B|')
    plt.xlabel('Time')
    plt.ylabel('Magnetic Field Magnitude (nT)')
    plt.title('Magnetic Field Magnitude')
    plt.legend()

    # Plot First Derivative
    plt.subplot(3, 1, 2)
    plt.plot(times, first_derivative, color='blue', label="d|B|/dt")
    plt.xlabel('Time')
    plt.ylabel('First Derivative (nT/s)')
    plt.title('First Derivative of Magnetic Field Magnitude')
    plt.legend()

    # Plot Second Derivative
    plt.subplot(3, 1, 3)
    plt.plot(times, second_derivative, color='red', label="d²|B|/dt²")
    plt.xlabel('Time')
    plt.ylabel('Second Derivative (nT/s²)')
    plt.title('Second Derivative of Magnetic Field Magnitude')
    plt.legend()

    plt.tight_layout()
    plt.show()


def plot_derivatives_for_smoothing_windows(times, bmag, smoothing_windows, sampling_rate, line_thickness, mean_threshold):
    plt.figure(figsize=(12, 12))  # Adjust figure size to accommodate three plots
    
    colors = ['red', 'orange', 'gold', 'green', 'blue', 'indigo', 'violet']
    
    # Plot 1: Magnetic Field Magnitude with 10s Smoothing
    plt.subplot(3, 1, 1)
    plt.plot(times, bmag, color='black', linewidth=line_thickness, label='|B| (Original)')
    smoothed_bmag_10s = efficient_moving_average(times, bmag, 10, sampling_rate, mean_threshold)
    plt.plot(times, smoothed_bmag_10s, color='red', linewidth=line_thickness, label='10s Smoothing')
    plt.xlabel('Time')
    plt.ylabel('Magnetic Field Magnitude (nT)')
    plt.title(f'Magnetic Field Magnitude with 10s Smoothing (Mean Threshold: {mean_threshold})')
    plt.legend()
    plt.grid(True)

    # Plot 2: Magnetic Field Magnitude and All Smoothed Data
    plt.subplot(3, 1, 2)
    plt.plot(times, bmag, color='black', linewidth=line_thickness, label='|B| (Original)')
    for window, color in zip(smoothing_windows, colors):
        smoothed_bmag = efficient_moving_average(times, bmag, window, sampling_rate, mean_threshold)
        plt.plot(times, smoothed_bmag, color=color, linewidth=line_thickness, label=f'{window}s Smoothing')
    plt.xlabel('Time')
    plt.ylabel('Magnetic Field Magnitude (nT)')
    plt.title('Magnetic Field Magnitude with Various Smoothing Windows')
    plt.legend()
    plt.grid(True)

    # Plot 3: First Derivatives of Smoothed Data
    plt.subplot(3, 1, 3)
    for window, color in zip(smoothing_windows, colors):
        smoothed_bmag = efficient_moving_average(times, bmag, window, sampling_rate, mean_threshold)
        first_derivative = np.gradient(smoothed_bmag, np.arange(len(times)) / sampling_rate)
        plt.plot(times, first_derivative, color=color, linewidth=line_thickness, label=f'd|B|/dt ({window}s Smoothing)')
    plt.xlabel('Time')
    plt.ylabel('First Derivative (nT/s)')
    plt.title('First Derivative of Magnetic Field Magnitude')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# -------- Plotting Function with Derivatives -------- #
def plot_with_derivatives(times, bmag, smoothing_windows, sampling_rate, line_thickness, mean_threshold):
    print('📈Called Plot With Derivatives in plotting.py')
    plt.figure(figsize=(12, 16))  # Adjust figure size to accommodate four plots
    
    colors = ['red', 'orange', 'gold', 'green', 'blue', 'indigo', 'violet']
    
    # Plot 1: Magnetic Field Magnitude with 10s Smoothing
    plt.subplot(4, 1, 1)
    plt.plot(times, bmag, color='black', linewidth=line_thickness, label='|B| (Original)')
    # smoothed_bmag_10s = efficient_moving_average(times, bmag, 10, sampling_rate, mean_threshold)
    smoothed_bmag_8s = efficient_moving_average(times, bmag, 8, sampling_rate, mean_threshold)
    # plt.plot(times, smoothed_bmag_10s, color='red', linewidth=line_thickness, label='10s Smoothing')
    plt.plot(times, smoothed_bmag_8s, color='red', linewidth=line_thickness, label='8s Smoothing')
    plt.xlabel('Time')
    plt.ylabel('Magnetic Field Magnitude (nT)')
    plt.title(f'Magnetic Field Magnitude with 8s Smoothing (Mean Threshold: {mean_threshold})')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Position legend outside plot
    plt.grid(True)

    # Plot 2: Magnetic Field Magnitude and All Smoothed Data
    plt.subplot(4, 1, 2)
    plt.plot(times, bmag, color='black', linewidth=line_thickness, label='|B| (Original)')
    for window, color in zip(smoothing_windows, colors):
        smoothed_bmag = efficient_moving_average(times, bmag, window, sampling_rate, mean_threshold)
        plt.plot(times, smoothed_bmag, color=color, linewidth=line_thickness, label=f'{window}s Smoothing')
    plt.xlabel('Time')
    plt.ylabel('Magnetic Field Magnitude (nT)')
    plt.title('Magnetic Field Magnitude with Various Smoothing Windows')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Position legend outside plot
    plt.grid(True)

    # Plot 3: First Derivatives of Smoothed Data
    plt.subplot(4, 1, 3)
    for window, color in zip(smoothing_windows, colors):
        smoothed_bmag = efficient_moving_average(times, bmag, window, sampling_rate, mean_threshold)
        first_derivative = np.gradient(smoothed_bmag, np.arange(len(times)) / sampling_rate)
        plt.plot(times, first_derivative, color=color, linewidth=line_thickness, label=f'd|B|/dt ({window}s Smoothing)')
    plt.xlabel('Time')
    plt.ylabel('First Derivative (nT/s)')
    plt.title('First Derivative of Magnetic Field Magnitude')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Position legend outside plot
    plt.grid(True)

    # Plot 4: Second Derivatives of Smoothed Data
    plt.subplot(4, 1, 4)
    for window, color in zip(smoothing_windows, colors):
        smoothed_bmag = efficient_moving_average(times, bmag, window, sampling_rate, mean_threshold)
        first_derivative = np.gradient(smoothed_bmag, np.arange(len(times)) / sampling_rate)
        second_derivative = np.gradient(first_derivative, np.arange(len(times)) / sampling_rate)
        plt.plot(times, second_derivative, color=color, linewidth=line_thickness, label=f'd²|B|/dt² ({window}s Smoothing)')
    plt.xlabel('Time')
    plt.ylabel('Second Derivative (nT/s²)')
    plt.title('Second Derivative of Magnetic Field Magnitude')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Position legend outside plot
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# -------- For Derivative plot -------- #
def plot_magnitude_with_smoothing_multiAvg(times, bmag, line_thickness, plot_trange, fig_height, fig_width, smoothed_bmag_dict, mean_threshold):
    # Clip the data to the plot_trange
    mask = (times >= pd.to_datetime(plot_trange[0])) & (times <= pd.to_datetime(plot_trange[1]))
    times = times[mask]
    bmag = bmag[mask]

    print(f"\nPlotting with time range: {plot_trange[0]} to {plot_trange[1]}")
    print(f"Number of data points: {len(times)}")

    plt.figure(figsize=(fig_width, fig_height))

    plt.plot(times, bmag, color='black', linewidth=line_thickness, label='|B| (Original)')

    colors = ['red', 'orange', 'gold', 'green', 'blue', 'indigo', 'violet']

    for (window_size_seconds, smoothed_bmag), color in zip(smoothed_bmag_dict.items(), colors):
        plt.plot(times, smoothed_bmag, color=color, linewidth=line_thickness, label=f'{window_size_seconds}s Smoothing')

    plt.xlabel('Time')
    plt.ylabel('Magnetic Field Magnitude (nT)')
    plt.title(f'Magnetic Field Magnitude with Various Time-Based Smoothing Functions ({mean_threshold} Mean Threshold Applied)')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Position legend outside plot
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -------- Plot Stdev Ranges Function -------- #
def plot_bmag_with_stdev_ranges(times, bmag, stdev_bounds_dict, line_thickness):
    print(f"\nPlotting Bmag with Multiple Standard Deviation Ranges")
    print(f"Number of data points: {len(times)}")

    plt.figure(figsize=(14, 8))

    # Plot the original magnetic field magnitude
    plt.plot(times, bmag, color='black', linewidth=line_thickness, label='|B| (Original)')

    colors = ['red', 'orange', 'brown', 'green', 'blue', 'indigo', 'violet']
    
    # Plot the lower bound for each window
    for (window_seconds, (_, lower_bound)), color in zip(stdev_bounds_dict.items(), colors):
        plt.plot(times, lower_bound, color=color, linewidth=line_thickness, linestyle='--', label=f'Bave0 - δB ({window_seconds}s)')
    
    plt.xlabel('Time')
    plt.ylabel('Magnetic Field Magnitude (nT)')
    plt.title(f'Magnetic Field Magnitude with Lower Bound (Bave0 - δB) for Various Windows')
    plt.legend(loc='upper right', fontsize='small')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def calculate_and_plot_derivative_zero_crossings(
        bmag, times_clipped, left_max_value_idx, right_max_value_idx, 
        derivative_window_seconds, sampling_rate, mean_threshold, smoothed_bmag_for_derivative, first_derivative,
        zero_crossings_indices, zero_crossings
    ):
    """
    Calculate the smoothed bmag, its first derivative, and plot zero crossings.

    Parameters:
    - bmag: The magnetic field magnitude array.
    - times_clipped: The clipped time array.
    - left_max_value_idx: The left index of the magnetic hole.
    - right_max_value_idx: The right index of the magnetic hole.
    - derivative_window_seconds: Window for smoothing before calculating the first derivative.
    - sampling_rate: The sampling rate of the data.
    - mean_threshold: The mean threshold used in smoothing.

    Returns:
    - zero_crossings: The number of zero crossings.
    - zero_crossings_indices: The indices of zero crossings.
    """
    # Define times_for_plot using the same indices range
    times_for_plot = times_clipped[left_max_value_idx:right_max_value_idx + 1]

    # Plotting
    plt.figure(figsize=(14, 8))

    # Plot the raw magnetic field magnitude (using clipped time array for consistency)
    plt.plot(times_clipped, bmag, color='black', linestyle='-', linewidth=1, label='Raw |B|')

    # Plot the smoothed magnetic field data (clip to the same time range for comparison)
    plt.plot(times_for_plot, smoothed_bmag_for_derivative, color='gray', label='Smoothed Bmag')

    # Plot the first derivative, scaled down
    plt.plot(times_for_plot, first_derivative / 4, color='red', label='First Derivative of Smoothed Bmag / 4')

    # Plot a thin horizontal line at y=0 to highlight zero crossings
    plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    # Plot vertical lines at zero crossings
    for idx in zero_crossings_indices:
        plt.axvline(x=times_for_plot[idx - left_max_value_idx], color='blue', linestyle='--', label='Zero Crossing' if idx == zero_crossings_indices[0] else "")

    # Adding labels and title
    plt.xlabel('Time')
    plt.ylabel('Magnetic Field / Derivative')
    plt.title('Magnetic Field Magnitude and its First Derivative with Zero Crossings')

    # Move the legend outside the plot, on the upper right corner
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))  # Position legend outside plot

    # Show plot
    plt.show()
    print(f"Number of Zero Crossings: {zero_crossings}")
    return zero_crossings, zero_crossings_indices


current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f'{current_time} - 📊 plot management initialized')