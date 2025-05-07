# #Note: Control + Shift + [ and ] will move left and right in the tabs.

# # Step 1: Import the modules explicitly so you can reload them
# import data_management
# import data_audification
# import time_management
# import plotting
# import buttons
# import MH_format_output
# import MH_helper_functions
# import asymmetry_calc
# import multiAvg_calc
# import stdev
# import hole_angle_calc
# import printing

# import importlib

# # Step 2: Reload the modules to update their contents
# importlib.reload(data_management)
# importlib.reload(data_audification)
# importlib.reload(time_management)
# importlib.reload(plotting)
# importlib.reload(buttons)
# importlib.reload(MH_format_output)
# importlib.reload(MH_helper_functions)
# importlib.reload(asymmetry_calc)
# importlib.reload(multiAvg_calc)
# importlib.reload(stdev)
# importlib.reload(hole_angle_calc)
# importlib.reload(printing)

# # Step 3: Bring the updated functions, classes, and variables into the current namespace
# from data_management import *
# from data_audification import *
# from time_management import *
# from plotting import *
# from buttons import *
# from MH_format_output import *
# from MH_helper_functions import *
# from asymmetry_calc import *
# from multiAvg_calc import *
# from stdev import *
# from hole_angle_calc import *
# from printing import *
# from collections import Counter

# #Import Libraries
# # Scientific Libraries
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.colors
# from matplotlib import ticker, cm
# from scipy.io import readsav, wavfile
# from scipy.io.wavfile import write
# from scipy import interpolate
# import bisect
# import json

# # PySPEDAS and PyTPlot Libraries
# import pyspedas
# from pyspedas import time_string, time_double, tinterpol, tdpwrspc
# import pytplot
# from pytplot import (
#     tplot, store_data, get_data, tlimit, xlim, ylim, tplot_options, options,
#     split_vec, cdf_to_tplot, divide, tplot_names, get_timespan, tplot_rename,
#     time_datetime
# )

# # System and File Operations
# import os
# import sys
# import contextlib
# import cdflib
# from datetime import datetime, timedelta
# from tkinter import Tk, filedialog
# import pickle #for saving data locally
# import time

# # IPython Widgets
# import ipywidgets as widgets
# from IPython.display import display

# # Warnings Handling
# from warnings import simplefilter
# import warnings

# # Suppress warnings
# simplefilter(action='ignore', category=DeprecationWarning)
# warnings.filterwarnings("ignore")
# warnings.filterwarnings("ignore", category=DeprecationWarning, module="IPython.core.pylabtools")

# # Global Variables
# global save_dir, trange, trange_start, trange_stop

# current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# print(f'{current_time} - 📚 libraries imported')


# #Former Cell 2
# #Set The Global Save Directory
# #Running this code will trigger a pop-up menu that will ask you to specify a directory where you'd like to save your files.
# #If you don't see a pop-up check your dock for a bouncing white python page and click that.
# #Each time you change this directory you'll need to re-run the cells that generate plots before they'll recognize the new location.
# #If this directory is not specified the code will not run properly.

# # Set The Global Save Directory
# global save_dir
# last_dir_file = "last_selected_dir.txt"  # Path to save the last selected directory
# save_dir = set_save_directory(last_dir_file)

# show_directory_button(save_dir) # Display the button to show the directory

# current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# print(f'{current_time} - 🛟 Save Directory Set: {save_dir}')

# #👇 Your save directory is confirmed here and you can click the button to see it.
