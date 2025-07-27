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
from .data_download_berkeley import download_berkeley_data
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
        self.default_save_dir_name = "audio_files" # Store default name
        
        # Try to get the saved directory
        self.save_dir = self.get_save_directory()
        
        # If no directory was saved previously, set and create the default
        if self.save_dir is None:
            print(f"No save directory previously set. Defaulting to: ./{self.default_save_dir_name}")
            self.save_dir = self.default_save_dir_name
            os.makedirs(self.save_dir, exist_ok=True)
        
        # Initialize other variables
        self.sample_rate = 44100
        self.markers_per_hour = 2
        self.markers_only = False
        self.quantize_markers = False  # Can be False or number of minutes (10, 60, etc)
        self._channels = 1
        self._fade_samples = 0
    
    def _parse_and_format_trange(self, trange):
        """Parses trange and returns datetime objects and formatted strings, handling multi-day ranges."""
        try:
            start_dt = parse(trange[0])
            end_dt = parse(trange[1])
            
            # Format start date/time parts
            start_date_hyphen = start_dt.strftime('%Y-%m-%d')
            start_date_underscore = start_dt.strftime('%Y_%m_%d')
            start_time_hhmm = self.format_time_for_filename(start_dt.strftime('%H:%M:%S.%f')[:-3])
            
            # Format end time part
            stop_time_hhmm = self.format_time_for_filename(end_dt.strftime('%H:%M:%S.%f')[:-3])
            
            # Check if range spans multiple days
            if start_dt.date() == end_dt.date():
                # Single day range
                range_str_hyphen = f"{start_date_hyphen}_{start_time_hhmm}_to_{stop_time_hhmm}"
                range_str_underscore = f"{start_date_underscore}_{start_time_hhmm}_to_{stop_time_hhmm}"
                # Keep single date format for backward compatibility if needed elsewhere?
                # For now, let's focus on the range strings.
                formatted_date_with_dashes = start_date_hyphen # Original date for potential single-day use case
                formatted_date_underscore = start_date_underscore # Original date for potential single-day use case
            else:
                # Multi-day range
                end_date_hyphen = end_dt.strftime('%Y-%m-%d')
                end_date_underscore = end_dt.strftime('%Y_%m_%d')
                range_str_hyphen = f"{start_date_hyphen}_{start_time_hhmm}_to_{end_date_hyphen}_{stop_time_hhmm}"
                range_str_underscore = f"{start_date_underscore}_{start_time_hhmm}_to_{end_date_underscore}_{stop_time_hhmm}"
                # Keep start date for backward compatibility if needed elsewhere?
                formatted_date_with_dashes = start_date_hyphen
                formatted_date_underscore = start_date_underscore

            return {
                'start_dt': start_dt,
                'end_dt': end_dt,
                'start_date_str': start_date_hyphen, # Keep for encounter lookup
                'range_str_hyphen': range_str_hyphen, # Combined range string with hyphens in dates
                'range_str_underscore': range_str_underscore, # Combined range string with underscores in dates
                # Keep original formatted dates just in case, though likely unused now
                'formatted_date': formatted_date_underscore, 
                'formatted_date_with_dashes': formatted_date_with_dashes 
            }
        except Exception as e:
            # Use logging if available, otherwise print
            try: import logging; logging.error(f"Error parsing/formatting time range strings: {trange}. Error: {e}")
            except: pass
            print(f"Error parsing/formatting time range strings: {trange}. Please use a format like 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD/HH:MM:SS'.")
            return None # Indicate failure

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

        # Add check for valid components and datetime_array
        if not components or not hasattr(components[0], 'datetime_array') or components[0].datetime_array is None:
            print("Warning: Invalid component or missing datetime_array for clipping. Returning empty indices.")
            return np.array([], dtype=int)

        # Parse times without timezone info
        start_dt = np.datetime64(parse(trange[0]))
        stop_dt = np.datetime64(parse(trange[1])) + np.timedelta64(1, 'us')

        # Get indices for the time range
        try:
            # Use raw datetime array for clipping, not the property (which is now clipped)
            datetime_array = components[0].plot_options.datetime_array if hasattr(components[0], 'plot_options') else components[0].datetime_array
            indices = np.where((datetime_array >= start_dt) & 
                              (datetime_array < stop_dt))[0]
        except TypeError as e:
            print(f"Error during datetime comparison: {e}. Returning empty indices.")
            return np.array([], dtype=int)

        print(f"Original data points: {len(components[0]) if hasattr(components[0], '__len__') else 'N/A'}")
        print(f"Points in range: {len(indices)}\n")

        return indices
    
    def set_save_dir(self, directory):
        """Set save directory directly with a path."""
        self.save_dir = directory
        print(f"Save Directory Set: {directory}")
    
    def select_save_dir(self, force_new=False):
        """Open GUI to select save directory ONLY if force_new is True, or if directory isn't set."""
        # Prompt only if forced or if save_dir is somehow None (shouldn't happen after init)
        if force_new or self.save_dir is None:
            print(f"Prompting for new save directory (force_new={force_new}). Current: '{self.save_dir}'")
            selected_dir = set_save_directory(self.last_dir_file)
            if selected_dir: # Only update if a directory was actually selected
                self.save_dir = selected_dir
                print(f"New save directory set: {self.save_dir}")
            else:
                print(f"Directory selection cancelled. Save directory remains: {self.save_dir}")
        else:
             # If not forcing and save_dir is set, just confirm the current directory
             print(f"Using previously set save directory: {self.save_dir}")
            
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
    
    @property
    def channels(self):
        """Get the number of audio channels."""
        return self._channels
    
    @channels.setter
    def channels(self, value):
        """Set the number of audio channels."""
        if value in [1, 2]:
            self._channels = value
        else:
            self._channels = 1
    
    @property
    def fade_samples(self):
        """Get the number of fade samples."""
        return self._fade_samples
    
    @fade_samples.setter
    def fade_samples(self, value):
        """Set the number of fade samples."""
        if value >= 0:
            self._fade_samples = value
        else:
            self._fade_samples = 0
    
    def apply_fade(self, audio_data):
        """Apply fade in/out to audio data."""
        if self._fade_samples == 0:
            return audio_data
            
        # Make a copy of the data as float32 for safe multiplication
        audio_float = audio_data.astype(np.float32)
        
        # Determine if the audio is mono or stereo
        is_stereo = len(audio_float.shape) > 1 and audio_float.shape[1] == 2
        
        # Create fade in/out windows
        fade_in = np.linspace(0, 1, self._fade_samples)
        fade_out = np.linspace(1, 0, self._fade_samples)
        
        if is_stereo:
            # Apply fade to stereo audio (both channels)
            for channel in range(2):
                # Apply fade in
                audio_float[:self._fade_samples, channel] *= fade_in
                # Apply fade out
                audio_float[-self._fade_samples:, channel] *= fade_out
        else:
            # Apply fade to mono audio
            # Apply fade in
            audio_float[:self._fade_samples] *= fade_in
            # Apply fade out
            audio_float[-self._fade_samples:] *= fade_out
        
        # Convert back to int16 before returning
        return audio_float.astype(np.int16)

    def generate_markers(self, times, trange, output_dir):
        """Generate markers for the audified data."""
        print(f"Generating markers for time range: {trange[0]} to {trange[1]}")
        print(f"Number of time points: {len(times)}")
        
        # === PARSE AND FORMAT TIME RANGE using helper ===
        time_info = self._parse_and_format_trange(trange)
        if time_info is None:
            return None # Error already printed by helper
        # ================================================

        # Generate marker times based on parsed datetimes
        start_datetime = time_info['start_dt'] # Use parsed object
        stop_datetime = time_info['end_dt']   # Use parsed object
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
            
        # Get encounter number using formatted date string from helper
        encounter = get_encounter_number(time_info['start_date_str'])
        
        # Format the frequency for filename
        if self.markers_per_hour < 1:
            hours_between = int(1.0 / self.markers_per_hour)
            freq_str = f"every_{hours_between}_hours"
        else:
            freq_str = f"{self.markers_per_hour}_per_hour"
            
        # Create filename using the combined range string from helper
        filename = os.path.join(output_dir,
            f"{encounter}_PSP_FIELDS_MARKER_SET_{time_info['range_str_hyphen']}_{freq_str}.txt")
        
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
        """Convert time string from 'HH:MM:SS.fff' to 'HHMM'"""
        # Remove colons
        formatted = time_str.replace(':', '')
        # Split by dot to remove milliseconds
        formatted = formatted.split('.')[0]
        # If time ends in seconds that are 00, remove them
        if len(formatted) == 6 and formatted.endswith('00'):
            formatted = formatted[:-2]
        return formatted
    
    def audify(self, trange, *components, filename=None, channels=None, markers_per_hour=None,
               sample_rate=None, norm_percentile=None):
        """
        Create a WAV file from the magnetometer time series.
        
        Parameters
        ----------
        trange : two element list
            Time range for audio generation
        components : list
            List of components to include in the WAV file. 
            In mono mode (channels=1), each component is saved as a separate WAV file.
            In stereo mode (channels=2), the first two components are used for left/right channels.
        filename : str
            Filename for output file(s)
        channels : int, optional
            Number of audio channels (1 for mono, 2 for stereo). Defaults to self.channels.
        markers_per_hour : int, optional
            Number of hour markers to include per hour. Default is 0.
        sample_rate : int, optional
            Sample rate. Default is 44100.
        norm_percentile : float, optional
            Percentile for normalization. Default is 99.9.
        """
        channels = channels if channels is not None else self._channels
        self.channels = channels
        
        # Check if channels and components are compatible
        if channels == 2 and len(components) < 2:
            print("Warning: Stereo mode requires at least 2 components. Setting to mono.")
            self.channels = 1
                
        print("Starting " + ("marker generation..." if self.markers_only else "audification process..."))
        
        # === PARSE AND FORMAT TIME RANGE using helper ===
        time_info = self._parse_and_format_trange(trange)
        if time_info is None:
             return {} # Error already printed by helper
        # ===============================================

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
            download_berkeley_data(trange, data_type)
            
            # Get class instance from data_cubby
            class_instance = data_cubby.grab(class_name)
            
            # Check if we need to import data
            needs_import = global_tracker.is_import_needed(trange, data_type)
            needs_refresh = False
            
            # Check if cached data covers our time range
            if hasattr(class_instance, 'datetime_array') and class_instance.datetime_array is not None:
                try:
                    # Compare using numpy datetime64 which should handle different input formats
                    cached_start = np.datetime64(class_instance.datetime_array[0], 's')
                    cached_end = np.datetime64(class_instance.datetime_array[-1], 's')
                    # Use parsed start/end from helper for comparison
                    requested_start = np.datetime64(time_info['start_dt'], 's') 
                    requested_end = np.datetime64(time_info['end_dt'], 's')
                    
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
        encounter = get_encounter_number(time_info['start_date_str'])
        
        # Check if save_dir already ends with the encounter name
        if os.path.basename(self.save_dir.rstrip('/\\')) == encounter:
            encounter_dir = self.save_dir # Use existing directory
            print(f"Save directory already ends with encounter '{encounter}'. Using: {encounter_dir}")
        else:
            encounter_dir = os.path.join(self.save_dir, encounter) # Create encounter dir inside save_dir
            os.makedirs(encounter_dir, exist_ok=True) # Ensure base encounter dir exists if needed
            print(f"Creating encounter directory: {encounter_dir}")

        # Setup output subfolder within the encounter directory using the combined range string from helper
        subfolder_name = f"{encounter}_{time_info['range_str_underscore']}"
        output_dir = os.path.join(encounter_dir, subfolder_name)
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Output directory: {output_dir}")
        
        file_names = {}
        
        # Generate markers using the raw datetime array to match how indices were computed
        raw_datetime_array = processed_components[0].plot_options.datetime_array
        marker_file = self.generate_markers(
            raw_datetime_array[indices],
            trange,
            output_dir
        )
        file_names['markers'] = marker_file
        
        # Generate audio files if not markers_only
        if not self.markers_only:
            # Use pre-formatted date string with dashes for filenames from helper
            sample_rate_str = f"{self.sample_rate}SR"
            
            if self.channels == 1:  # Mono mode - each component gets its own file
                # Process each component as a separate mono file
                for component in processed_components:
                    data = np.array(component[indices])
                    audio_data = self.normalize_to_int16(data)
                    
                    # Apply fade if enabled
                    if self._fade_samples > 0:
                        audio_data = self.apply_fade(audio_data)
                    
                    filename = os.path.join(output_dir,
                        f"{encounter}_PSP_"
                        f"{component.data_type.upper()}_"
                        f"{time_info['range_str_hyphen']}_"
                        f"{sample_rate_str}_"
                        f"{component.subclass_name.capitalize()}.wav")
                    
                    wavfile.write(filename, self.sample_rate, audio_data)
                    print(f"Saved mono audio file: {filename}")
                    file_names[component.subclass_name] = filename
            else:  # Stereo mode (self.channels == 2)
                # Process first two components as stereo
                if len(processed_components) >= 2:
                    left_data = np.array(processed_components[0][indices])
                    right_data = np.array(processed_components[1][indices])
                    
                    # Normalize each channel separately
                    left_normalized = self.normalize_to_int16(left_data)
                    right_normalized = self.normalize_to_int16(right_data)
                    
                    # Make sure both channels have the same length
                    min_length = min(len(left_normalized), len(right_normalized))
                    left_normalized = left_normalized[:min_length]
                    right_normalized = right_normalized[:min_length]
                    
                    # Combine into stereo array
                    stereo_data = np.column_stack((left_normalized, right_normalized))
                    
                    # Apply fade if enabled
                    if self._fade_samples > 0:
                        stereo_data = self.apply_fade(stereo_data)
                    
                    # Create stereo filename using both component names
                    left_name = processed_components[0].subclass_name.capitalize()
                    right_name = processed_components[1].subclass_name.capitalize()
                    
                    filename = os.path.join(output_dir,
                        f"{encounter}_PSP_"
                        f"{processed_components[0].data_type.upper()}_"
                        f"{time_info['range_str_hyphen']}_"
                        f"{sample_rate_str}_"
                        f"{left_name}_L_{right_name}_R.wav")
                    
                    wavfile.write(filename, self.sample_rate, stereo_data)
                    print(f"Saved stereo audio file: {filename}")
                    file_names[f"stereo_{left_name}_{right_name}"] = filename
                    
                    # Process any remaining components as mono files
                    for component in processed_components[2:]:
                        data = np.array(component[indices])
                        audio_data = self.normalize_to_int16(data)
                        
                        # Apply fade if enabled
                        if self._fade_samples > 0:
                            audio_data = self.apply_fade(audio_data)
                        
                        filename = os.path.join(output_dir,
                            f"{encounter}_PSP_"
                            f"{component.data_type.upper()}_"
                            f"{time_info['range_str_hyphen']}_"
                            f"{sample_rate_str}_"
                            f"{component.subclass_name.capitalize()}.wav")
                        
                        wavfile.write(filename, self.sample_rate, audio_data)
                        print(f"Saved mono audio file: {filename}")
                        file_names[component.subclass_name] = filename
                else:
                    print("Not enough components for stereo. Need at least 2.")
        
        # Show access buttons
        show_directory_button(self.save_dir)
        show_file_buttons(file_names)
        
        return file_names

    def _process_and_save_mono_component(self, component, trange, filename, markers_per_hour, 
                                        sample_rate, norm_percentile):
        """Process a single component and save it as a mono WAV file."""
        component_name = getattr(component, 'component_name', 'data')
        component_wavfile = self._create_filename(filename, component_name)
        logging.info(f'Creating audio file: {component_wavfile}')
        
        component_data = self._process_component(component, trange, sample_rate, norm_percentile)
        if component_data is None:
            return
            
        # Apply fade if specified
        if self._fade_samples > 0:
            component_data = self.apply_fade(component_data)
            
        # Save the mono WAV file
        wavfile.write(component_wavfile, sample_rate, component_data)

    def _process_component(self, component, trange, sample_rate, norm_percentile):
        """Process a component to prepare it for audio conversion."""
        # Find the time range for clipping
        tr = trange.copy()
        
        # Get the time and data for this component
        t = getattr(component, 'times', None)
        y = getattr(component, 'data', None)
        
        # If either are None, return None
        if t is None or y is None:
            return None
            
        # Clip data to time range
        t_ind, y = self.clip_data_to_range(t, y, tr)
        
        # Check if we got valid data
        if len(y) == 0:
            logging.warning(f'No data found for component in the time range: {tr}')
            return None
            
        # Normalize and convert to int16
        normalized_data = self.normalize_to_int16(y)
        
        return normalized_data
        
    def _create_filename(self, base_filename, component_suffix):
        """Create a filename based on the base filename and component suffix."""
        if base_filename is None:
            return f'audio_{component_suffix}.wav'
        else:
            # If the filename already has .wav, replace it
            if base_filename.lower().endswith('.wav'):
                base_filename = base_filename[:-4]
            return f'{base_filename}_{component_suffix}.wav'

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