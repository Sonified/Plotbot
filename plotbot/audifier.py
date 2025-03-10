from tkinter import Tk, filedialog
import os
import ipywidgets as widgets
from IPython.display import display
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy.io import wavfile
from dateutil.parser import parse
from .get_encounter import get_encounter_number
from .data_cubby import data_cubby
from .data_tracker import global_tracker
from .data_download import download_new_psp_data
from .data_import import import_data_function
from .print_manager import print_manager
from .plotbot_helpers import time_clip

def open_directory(directory):
    """Open directory in system file explorer."""
    if os.name == 'nt':  # For Windows
        os.startfile(directory)
    elif os.name == 'posix':  # For macOS and Linux
        os.system(f'open "{directory}"')

def show_directory_button(directory):
    """Display a button that opens the specified directory."""
    button = widgets.Button(description="Show Directory")
    def on_button_click(b):
        open_directory(directory)
    button.on_click(on_button_click)
    display(button)

def show_file_buttons(file_paths):
    """Display buttons to open specified files."""
    for label, file_path in file_paths.items():
        button = widgets.Button(description=f"Open {label}")
        def on_button_click(b, path=file_path):
            if os.name == 'nt':  # For Windows
                os.startfile(path)
            elif os.name == 'posix':  # For macOS and Linux
                os.system(f'open "{path}"')
        button.on_click(on_button_click)
        display(button)

def set_save_directory(last_dir_file):
    """Set and remember the save directory."""
    if os.path.exists(last_dir_file):
        with open(last_dir_file, 'r') as f:
            start_dir = f.read().strip()
    else:
        start_dir = None

    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    try:
        if start_dir and os.path.exists(start_dir):
            save_dir = filedialog.askdirectory(initialdir=start_dir)
        else:
            save_dir = filedialog.askdirectory()
        
        if save_dir:
            with open(last_dir_file, 'w') as f:
                f.write(save_dir)
        else:
            print("No directory selected.")
            return None
            
        return save_dir
        
    finally:
        root.quit()  # Stop the mainloop
        root.destroy()  # Ensure the Tk window is destroyed even if there's an error



class Audifier:
    def __init__(self):
        # Initialize last_dir_file first
        self.last_dir_file = 'last_dir.txt'
        
        # Now we can get the save directory since last_dir_file exists
        self.save_dir = self.get_save_directory()
        
        # Initialize other variables
        self.sample_rate = 44100
        self.markers_per_hour = 2
        self.markers_only = False
        self.quantize_markers = False  # Can be False or number of minutes (10, 60, etc)
    
    def get_save_directory(self):
        """Get the saved directory path."""
        if os.path.exists(self.last_dir_file):
            with open(self.last_dir_file, 'r') as f:
                return f.read().strip()
        return None
    
    def clip_data_to_range(self, components, trange):
        """Get indices for the specified time range."""

        print(f"\nDEBUG CLIPPING:")
        print(f"Clipping data to range: {trange[0]} to {trange[1]}")

        # Parse times without timezone info
        start_dt = np.datetime64(parse(trange[0]))
        stop_dt = np.datetime64(parse(trange[1])) + np.timedelta64(1, 'us')

        # Get indices for the time range
        indices = np.where((components[0].datetime_array >= start_dt) & 
                          (components[0].datetime_array < stop_dt))[0]

        print(f"Original data points: {len(components[0])}")
        print(f"Points in range: {len(indices)}\n")

        return indices
    
    def set_save_dir(self, directory):
        """Set save directory directly with a path."""
        self.save_dir = directory
        print(f"Save Directory Set: {directory}")
    
    def select_save_dir(self, force_new=False):
        """Open GUI to select save directory if needed or forced.
        
        Args:
            force_new (bool): If True, always prompt for new directory
        """
        if force_new or self.save_dir is None:
            self.save_dir = set_save_directory(self.last_dir_file)
            
        # Create button to open save directory
        try:
            import platform
            import subprocess

            def open_save_dir(b):
                system = platform.system()
                try:
                    if system == 'Darwin':  # macOS
                        subprocess.run(['open', self.save_dir])
                    elif system == 'Windows':
                        subprocess.run(['explorer', self.save_dir.replace('/', '\\')])
                    elif system == 'Linux':
                        try:
                            subprocess.run(['xdg-open', self.save_dir])
                        except FileNotFoundError:
                            print(f"Could not find a file manager. Directory path: {self.save_dir}")
                    else:
                        print(f"Directory path: {self.save_dir}")
                        print("Note: Automatic directory opening not supported on this OS")
                except Exception as e:
                    print(f"Error opening directory: {e}")
                    print(f"Directory path: {self.save_dir}")
                    print(f"Operating System: {system}")

            open_dir_button = widgets.Button(
                description='Open Save Directory',
                button_style='info',
                tooltip='Click to open the save directory in your file explorer'
            )
            
            open_dir_button.on_click(open_save_dir)
            display(open_dir_button)
            
        except ImportError:
            print(f"\nFiles will be saved in: {self.save_dir}")
        
    def set_markers_per_hour(self, markers):
        """Set number of markers per hour."""
        self.markers_per_hour = markers
        print(f"Markers per hour set to: {markers}")

    def generate_markers(self, times, trange, output_dir):
        """Generate markers for the audified data."""
        print(f"Generating markers for time range: {trange[0]} to {trange[1]}")
        print(f"Number of time points: {len(times)}")
        
        # Parse start and end times
        start_datetime = datetime.strptime(trange[0], '%Y-%m-%d/%H:%M:%S.%f')
        stop_datetime = datetime.strptime(trange[1], '%Y-%m-%d/%H:%M:%S.%f')
        
        # Generate marker times
        marker_times = []
        
        if self.quantize_markers:
            # Calculate hours between markers
            hours_interval = 1.0 / self.markers_per_hour
            
            # Find the first marker time before our data
            first_marker = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Generate markers at the specified interval
            current = first_marker
            while current <= stop_datetime:  # Just check against stop_datetime
                if current >= start_datetime:
                    marker_times.append(current)
                current += timedelta(hours=hours_interval)
        else:
            # Original behavior
            duration = (stop_datetime - start_datetime).total_seconds() / 3600.0
            interval = duration / self.markers_per_hour
            
            current = start_datetime
            while current <= stop_datetime:
                marker_times.append(current)
                current += timedelta(hours=interval)
        
        # Convert marker times to pandas DatetimeIndex
        marker_times = pd.DatetimeIndex(marker_times)
        
        # Convert times to datetime
        times_datetime = pd.to_datetime(times)
        
        print(f"Data time range: {times_datetime.min()} to {times_datetime.max()}")
        
        # Find closest indices for each marker time
        closest_indices = np.searchsorted(times_datetime, marker_times)
        
        # Filter out markers that fall outside the data range
        valid_markers = closest_indices < len(times)
        marker_times = marker_times[valid_markers]
        closest_indices = closest_indices[valid_markers]
        print(f"Total markers generated: {len(marker_times)}")
        
        # Check if any markers are valid
        if not valid_markers.any():
            print("No valid markers found within the data range.")
            return None
            
        # Get start date with hyphens preserved
        start_date = trange[0].split('/')[0]  # This keeps the hyphens in 2023-09-26
        encounter = get_encounter_number(start_date)
        
        # Format times for filename
        start_time = self.format_time_for_filename(trange[0].split('/')[1])
        stop_time = self.format_time_for_filename(trange[1].split('/')[1])
        
        # Format the frequency for filename
        if self.markers_per_hour < 1:
            hours_between = int(1.0 / self.markers_per_hour)
            freq_str = f"every_{hours_between}_hours"
        else:
            freq_str = f"{self.markers_per_hour}_per_hour"
            
        filename = os.path.join(output_dir,
            f"{encounter}_PSP_FIELDS_MARKER_SET_{start_date}_"
            f"{start_time}_to_{stop_time}_{freq_str}.txt")
        
        with open(filename, 'w') as f:
            for marker_time, sample_number in zip(marker_times, closest_indices):
                if marker_time.microsecond:
                    time_str = marker_time.strftime('%H:%M:%S.%f')[:12]
                else:
                    time_str = marker_time.strftime('%H:%M:%S')
                date_str = marker_time.strftime('('+'%Y-%m-%d'+')')
                f.write(f"{time_str} {date_str}\t{sample_number}\n")
        
        print(f"Marker file created: {filename}")
        return filename
    
    def format_time_for_filename(self, time_str):
        """Convert time string from 'HH:MM.fff' to 'HHMM'"""
        return time_str.replace(':', '').split('.')[0]
    
    def audify(self, trange, *components):
        """Generate audio files and markers.
        
        Args:
            trange: Time range in format ['YYYY-MM-DD/HH:MM:SS.fff', 'YYYY-MM-DD/HH:MM:SS.fff']
            *components: Variable components to audify (e.g., mag_rtn.br, mag_rtn.bt)
        """
        if self.save_dir is None:
            print("Please set a save directory first")
            return
                
        print("Starting " + ("marker generation..." if self.markers_only else "audification process..."))
        
        # ====================================================================
        # DOWNLOAD AND PROCESS DATA FOR EACH COMPONENT
        # ====================================================================
        processed_components = []
        
        for component in components:
            # Get configuration for data download and import
            data_type = component.data_type
            class_name = component.class_name
            subclass_name = component.subclass_name
            
            print_manager.debug(f"\nProcessing {data_type} - {subclass_name}")
            
            # Download data if needed
            download_new_psp_data(trange, data_type)
            
            # Get class instance from data_cubby
            class_instance = data_cubby.grab(class_name)
            
            # Check if we need to import data
            needs_import = global_tracker.is_import_needed(trange, data_type)
            needs_refresh = False
            
            # Check if cached data covers our time range
            if hasattr(class_instance, 'datetime_array') and class_instance.datetime_array is not None:
                try:
                    cached_start = np.datetime64(class_instance.datetime_array[0], 's')
                    cached_end = np.datetime64(class_instance.datetime_array[-1], 's')
                    requested_start = np.datetime64(parse(trange[0]), 's')
                    requested_end = np.datetime64(parse(trange[1]), 's')
                    
                    # Add buffer for timing differences
                    buffered_start = cached_start - np.timedelta64(10, 's')
                    buffered_end = cached_end + np.timedelta64(10, 's')
                    
                    if buffered_start > requested_start or buffered_end < requested_end:
                        needs_refresh = True
                except Exception as e:
                    print(f"Error checking data range: {e}")
                    needs_refresh = True
            else:
                needs_refresh = True
            
            # Import data if needed
            if needs_import or needs_refresh:
                print_manager.debug(f"Importing data for {data_type}")
                data_obj = import_data_function(trange, data_type)
                if data_obj is not None:
                    class_instance.update(data_obj)
                    if needs_import:
                        global_tracker.update_imported_range(trange, data_type)
            
            # Get the specific subclass instance
            processed_component = class_instance.get_subclass(subclass_name)
            processed_components.append(processed_component)
        
        if not processed_components:
            print("No components available after processing")
            return
        
        # Get time range indices using the processed components
        indices = self.clip_data_to_range(processed_components, trange)
        
        if len(indices) == 0:
            print("No data points found within the specified time range.")
            return
        
        # Setup directories
        start_date = trange[0].split('/')[0]
        encounter = get_encounter_number(start_date)
        encounter_dir = os.path.join(self.save_dir, encounter)
        os.makedirs(encounter_dir, exist_ok=True)
        
        # Setup output directory
        start_date = start_date.replace('-', '_')
        start_time = self.format_time_for_filename(trange[0].split('/')[1])
        stop_time = self.format_time_for_filename(trange[1].split('/')[1])
        subfolder_name = f"{encounter}_{start_date}_{start_time}_to_{stop_time}"
        output_dir = os.path.join(encounter_dir, subfolder_name)
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Output directory: {output_dir}")
        
        file_names = {}
        
        # Generate markers using clipped datetime array
        marker_file = self.generate_markers(
            processed_components[0].datetime_array[indices],
            trange,
            output_dir
        )
        file_names['markers'] = marker_file
        
        # Generate audio files if not markers_only
        if not self.markers_only:
            for component in processed_components:
                data = np.array(component[indices])
                audio_data = self.normalize_to_int16(data)
                
                filename = os.path.join(output_dir,
                    f"{encounter}_PSP_"
                    f"{component.data_type.upper()}_"
                    f"{component.class_name.upper()}_"
                    f"{start_date}_"
                    f"{start_time}_to_{stop_time}_"
                    f"{component.subclass_name.capitalize()}.wav")
                
                wavfile.write(filename, self.sample_rate, audio_data)
                print(f"Saved audio file: {filename}")
                file_names[component.subclass_name] = filename
        
        # Show access buttons
        show_directory_button(self.save_dir)
        show_file_buttons(file_names)
        
        return file_names

    @staticmethod
    def normalize_to_int16(data):
        """Normalize data to int16 range for audio creation."""
        data = np.array(data, dtype=np.float32)
        
        # Check for empty arrays first
        if data.size == 0:
            print("Warning: Empty data array, returning empty audio data")
            return np.array([], dtype=np.int16)
        
        # Handle NaN values through interpolation
        nan_mask = np.isnan(data)
        if np.any(nan_mask):
            indices = np.arange(len(data))
            valid_indices = ~nan_mask
            # Check if we have any valid data points
            if np.any(valid_indices):
                data[nan_mask] = np.interp(indices[nan_mask], indices[valid_indices], data[valid_indices])
            else:
                print("Warning: All values are NaN, returning zeros")
                return np.zeros(data.shape, dtype=np.int16)
        
        # Safely calculate min and max
        try:
            max_val = np.max(data)
            min_val = np.min(data)
        except ValueError as e:
            print(f"Error calculating min/max: {e}")
            return np.zeros(data.shape, dtype=np.int16)
        
        if max_val == min_val:
            return np.zeros(data.shape, dtype=np.int16)
        
        normalized_data = (2 * (data - min_val) / (max_val - min_val) - 1) * 32767
        return normalized_data.astype(np.int16)

# Initialize global audifier instance
audifier = Audifier()

print('🔉 initialized audifier')