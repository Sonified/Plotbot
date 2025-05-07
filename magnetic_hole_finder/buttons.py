#file: buttons.py

from .data_management import *
from .time_management import convert_time_range_to_str, format_time

from datetime import datetime, timedelta
save_dir = None # Initialize module-level variable, removed incorrect 'global' keyword here
import ipywidgets as widgets
import os


#Import Libraries
# Scientific Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors
from matplotlib import ticker, cm
from scipy.io import readsav, wavfile
from scipy.io.wavfile import write
from scipy import interpolate
import bisect

# PySPEDAS and PyTPlot Libraries
import pyspedas
from pyspedas import time_string, time_double, tinterpol, tdpwrspc
import pytplot
from pytplot import (
    tplot, store_data, get_data, tlimit, xlim, ylim, tplot_options, options,
    split_vec, cdf_to_tplot, divide, tplot_names, get_timespan, tplot_rename,
    time_datetime
)

# System and File Operations
import os
import sys
import contextlib
import cdflib
from datetime import datetime, timedelta
from tkinter import Tk, filedialog
import pickle #for saving data locally
import time

# IPython Widgets
import ipywidgets as widgets
from IPython.display import display

def open_directory(directory):
    if os.name == 'nt':  # For Windows
        os.startfile(directory)
    elif os.name == 'posix':  # For macOS and Linux
        os.system(f'open "{directory}"')
    #print(f"Directory opened: {directory}")


def save_plot_button(trange, times, b_values, magnetic_holes):
    global save_dir  # Ensure we can modify the global save_dir variable
    
    button = widgets.Button(description="Save Plot")

    def on_button_click(b):
        print("Button clicked!")  # Debug print statement to confirm the button was clicked
        
        global save_dir  # Ensure we can modify the global save_dir variable
        if not save_dir:  # If no save directory is selected, prompt the user to choose one
            print("No save directory selected. Prompting for directory...")
            save_dir = select_directory()
            ensure_directory_exists(save_dir)
        
        if save_dir:
            print(f"Save directory selected: {save_dir}")  # Debug print to confirm the directory
            
            # Setup output directory based on trange
            print(f"Running setup_output_directory from save_plot_button:")  # Debug print
            final_directory = setup_output_directory(trange)
            print(f"Final directory for saving plot: {final_directory}")  # Debug print

            # Extract start and stop times from the trange
            start_datetime_str, stop_datetime_str = convert_time_range_to_str(trange[0], trange[1])
            print(f"Start time: {start_datetime_str}, Stop time: {stop_datetime_str}")  # Debug print
            
            start_date, start_time = format_time(start_datetime_str)
            stop_date, stop_time = format_time(stop_datetime_str)
            print(f"Formatted Start: {start_date} {start_time}, Formatted Stop: {stop_date} {stop_time}")  # Debug print
            
            # Adjust for day-crossing in the file naming
            if start_date[:4] == stop_date[:4]:  # Same year
                if start_date == stop_date:  # Same day
                    stop_time_formatted = f"{stop_time}"
                else:  # Different day, same year
                    stop_time_formatted = f"{stop_date[5:]}_{stop_time}"  # Exclude the year from stop_date
            else:
                stop_time_formatted = f"{stop_date}_{stop_time}"
            
            print(f"Stop time formatted: {stop_time_formatted}")  # Debug print
            
            # Get the encounter number
            encounter_number = get_encounter_number(start_date)
            print(f"Encounter number: {encounter_number}")  # Debug print
            
            # Generate the file name using the specified time range
            plot_filename = os.path.join(final_directory, f"{encounter_number}_PSP_FIELDS_{start_date}_{start_time}_to_{stop_time_formatted}_Bmag_With_Holes.png")
            print(f"Plot filename: {plot_filename}")  # Debug print
            
            # Plot the magnetic field magnitude with magnetic holes
            plt.figure(figsize=(12, 6))
            plt.plot(times, b_values, label='|B|', color='black')
            print(f"Plotting data with {len(times)} time points.")  # Debug print
            
            for start_idx, min_idx, end_idx in magnetic_holes:
                plt.axvspan(times[start_idx], times[end_idx], color='red', alpha=0.3)
                print(f"Highlighting magnetic hole from {times[start_idx]} to {times[end_idx]}")  # Debug print
            
            plt.xlabel('Time')
            plt.ylabel('Magnetic Field Strength (nT)')
            plt.title('Magnetic Field Strength with Detected Magnetic Holes')
            plt.legend()
            
            # Save the plot
            plt.savefig(plot_filename)
            plt.close()  # Close the plot to avoid displaying it in the notebook
            
            print(f"Plot saved: {plot_filename}")  # Debug print after saving the plot
        else:
            print("No save directory selected. Please select a directory first.")  # Debug print if no directory was selected

    button.on_click(on_button_click)
    display(button)

def show_directory_button(directory):
    """
    Display a button that opens the specified directory.
    
    Parameters:
    directory (str): The directory to open.
    """
    #print('show directory button called')
    #print('show directory savedir',save_dir)
    button = widgets.Button(description="Show Directory")

    def on_button_click(b):
        print(f"Button clicked to open directory: {directory}")
        open_directory(directory)
    
    button.on_click(on_button_click)
    display(button)


# Function to display the save button
def save_multiplot_button(trange, selected_vars):
    """
    Display a button to save the multiplot to the selected directory with a specific naming format.
    """
    button = widgets.Button(description="Save Multiplot")

    def on_button_click(b):
        print('Button clicked')
        save_multiplot(trange, selected_vars)

    button.on_click(on_button_click)
    display(button)

def show_file_buttons(file_paths):
    """
    Display buttons to open specified files.
    
    Parameters:
    file_paths (dict): A dictionary containing file paths with labels as keys.
    """
    for label, file_path in file_paths.items():
        button = widgets.Button(description=f"Open {label}")

        def on_button_click(b, path=file_path):
            #print(f"Button clicked to open file: {path}")
            open_file(path)
        
        button.on_click(on_button_click)
        display(button)

# def show_directory_button(directory):
#     button = widgets.Button(description="Show Directory")

#     def on_button_click(b):
#         print("Show Directory button clicked")
#         if directory:
#             open_directory(directory)
#         else:
#             print("No directory selected.")
    
#     button.on_click(on_button_click)
#     display(button)

current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f'{current_time} - 🔘 Buttons Initialized')