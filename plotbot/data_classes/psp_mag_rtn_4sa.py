# This file will contain the mag_rtn_4sa_class for PSP data. 

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging

from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
from ._utils import _format_setattr_debug

# 🎉 Define the main class to calculate and store mag_rtn_4sa variables 🎉
class mag_rtn_4sa_class:
    def __init__(self, imported_data):
        # Initialize attributes
        # These are fundamental identifiers for Plotbot
        object.__setattr__(self, 'class_name', 'mag_rtn_4sa') 
        object.__setattr__(self, 'data_type', 'mag_RTN_4sa') # Changed to uppercase RTN to match psp_data_types.py
        # subclass_name is typically for components like .br, .bt, not the main class instance itself initially
        object.__setattr__(self, 'subclass_name', None) 
        object.__setattr__(self, 'raw_data', {
            'all': None,
            'br': None,
            'bt': None,
            'bn': None,
            'bmag': None,
            'pmag': None,
            'br_norm': None  # Add br_norm to raw_data initialization
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)

        print_manager.dependency_management(f"*** MAG_CLASS_INIT (mag_rtn_4sa_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}. ***")
        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.dependency_management("Calculating mag rtn 4sa variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated mag rtn 4sa variables.")
    
    def update(self, imported_data):
        print_manager.dependency_management(f"*** MAG_CLASS_UPDATE (mag_rtn_4sa_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}, .data ID: {id(imported_data.data) if imported_data is not None and hasattr(imported_data, 'data') and imported_data.data is not None else 'N/A'}. Keys: {list(imported_data.data.keys()) if imported_data is not None and hasattr(imported_data, 'data') and imported_data.data is not None else 'N/A'} ***")
        if imported_data is None:                                                # Exit if no new data
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified ploptions) ⭐️THIS print can go inside the data cubby
        current_state = {}
        for subclass_name in self.raw_data.keys():                             # Use keys()
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                if hasattr(var, '_plot_state'):
                    current_state[subclass_name] = dict(var._plot_state)       # Save current plot state
                    print_manager.datacubby(f"Stored {subclass_name} state: {retrieve_ploption_snapshot(current_state[subclass_name])}")

        # Perform update
        self.calculate_variables(imported_data)                                # Update raw data arrays
        self.set_ploptions()                                                  # Recreate plot managers
        
        # Restore state (including any modified ploptions!)
        print_manager.datacubby("Restoring saved state...")
        for subclass_name, state in current_state.items():                    # Restore saved states
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                var._plot_state.update(state)                                 # Restore plot state
                for attr, value in state.items():
                    if hasattr(var.plot_options, attr):
                        setattr(var.plot_options, attr, value)                # Restore individual options
                print_manager.datacubby(f"Restored {subclass_name} state: {retrieve_ploption_snapshot(state)}")
        
        print_manager.datacubby("=== End Update Debug ===\\n")
        
    def get_subclass(self, subclass_name):  # Dynamic component retrieval method
        """Retrieve a specific component"""
        print_manager.dependency_management(f"Getting subclass: {subclass_name}")  # Log which component is requested
        print_manager.dependency_management(f"Accessing subclass: mag_rtn_4sa.{subclass_name}")
        if subclass_name in self.raw_data.keys():  # Check if component exists in raw_data
            print_manager.dependency_management(f"Returning {subclass_name} component")  # Log successful component find
            return getattr(self, subclass_name)  # Return the plot_manager instance
        else:
            print(f"'{subclass_name}' is not a recognized subclass, friend!")  # Friendly error message
            print(f"Try one of these: {', '.join(self.raw_data.keys())}")  # Show available components
            return None  # Return None if not found

    def __getattr__(self, name):
        # Allow direct access to dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                # Re-raise AttributeError if the internal/dunder method truly doesn't exist
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        # Special case for br_norm - calculate it if requested but not yet available
        if name == 'br_norm' and hasattr(self, 'raw_data') and 'br_norm' in self.raw_data:
            if self.raw_data['br_norm'] is None and self.raw_data['br'] is not None:
                # We have br data but no br_norm yet - calculate it
                print_manager.dependency_management("Lazy loading br_norm - calculating now...")
                self._calculate_br_norm()
                
                # Now create a plot_manager if successful calculation
                if self.raw_data['br_norm'] is not None:
                    self._setup_br_norm_plot_manager()
                    return self.br_norm  # Return the newly created plot_manager
        
        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        print_manager.dependency_management('mag_rtn_4sa getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []  # Get list of valid attributes from raw_data
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}") # Show list of valid attributes to use
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.dependency_management(_format_setattr_debug(name, value)) # Use helper function
        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.dependency_management('mag_rtn_4sa setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.dependency_management(f"Attempted to set unknown attribute: {name}")
           
            # Do not set the attrib
    def calculate_variables(self, imported_data):
        # STRATEGIC PRINT I
        print_manager.dependency_management(f"[MAG_CLASS_DEBUG I] calculate_variables called for instance ID: {id(self)}")

        print_manager.dependency_management(f"*** MAG_CLASS_CALCVARS (mag_rtn_4sa_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}, .data ID: {id(imported_data.data) if imported_data is not None and hasattr(imported_data, 'data') and imported_data.data is not None else 'N/A'} ***")
        if hasattr(imported_data, 'data') and isinstance(imported_data.data, dict):
            print_manager.dependency_management(f"    Available keys in imported_data.data for CALCVARS: {list(imported_data.data.keys())}")
        else:
            print_manager.dependency_management(f"    CALCVARS: imported_data.data is missing or not a dict.")
        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))        
        
        # STRATEGIC PRINT J
        dt_len_in_calc_vars = len(self.datetime_array) if self.datetime_array is not None else "None"
        print_manager.dependency_management(f"[MAG_CLASS_DEBUG J] Instance ID: {id(self)} AFTER self.datetime_array assignment in calculate_variables. Length: {dt_len_in_calc_vars}")

        print_manager.dependency_management("self.datetime_array type after conversion: {type(self.datetime_array)}")
        print_manager.dependency_management("First element type: {type(self.datetime_array[0])}")
        
        # Get field data as numpy array
        self.field = np.asarray(imported_data.data['psp_fld_l2_mag_RTN_4_Sa_per_Cyc'])
        
        # Extract components and calculate derived quantities efficiently
        br = self.field[:, 0]
        bt = self.field[:, 1]
        bn = self.field[:, 2]
        
        # Calculate magnitude using numpy operations
        bmag = np.sqrt(br**2 + bt**2 + bn**2)
        
        # Calculate magnetic pressure
        mu_0 = 4 * np.pi * 1e-7  # Permeability of free space
        pmag = (bmag**2) / (2 * mu_0) * 1e-9  # Convert to nPa
        
        # Store all data in raw_data dictionary
        self.raw_data = {
            'all': [br, bt, bn],
            'br': br,
            'bt': bt,
            'bn': bn,
            'bmag': bmag,
            'pmag': pmag,
            'br_norm': None  # br_norm is calculated only when requested (lazy loading)
        }

        # # Convert TT2000 timestamps to datetime objects using cdflib
        # self.datetime = cdflib.cdfepoch.to_datetime(self.time)

        print_manager.dependency_management(f"\nDebug - Data Arrays:")
        print_manager.dependency_management(f"Time array shape: {self.time.shape}")
        print_manager.dependency_management(f"Field data shape: {self.field.shape}")
        print_manager.dependency_management(f"First TT2000 time: {self.time[0]}")
    
    def _calculate_br_norm(self):
        """
        Calculate the normalized radial magnetic field (Br*R²)
        
        This parameter accounts for the 1/r² decrease of the magnetic field strength 
        with distance from the Sun, allowing for meaningful comparisons between
        measurements at different solar distances.
        
        The formula is:
        Br_norm = Br * ((Rsun / conversion_factor)²)
        
        Where:
        - Br is the radial magnetic field component in nT
        - Rsun is the distance from the Sun in solar radii
        - conversion_factor is 215.032867644 (Rsun per AU)
        - The result is in nT*AU²
        
        This method will:
        1. Check if br data exists
        2. Get proton sun_dist_rsun data if not already loaded
        3. Interpolate sun distance to match mag timeline
        4. Calculate br_norm using the validated formula
        5. Store result in raw_data['br_norm']
        """
        # Check if we have valid br data to work with
        if self.raw_data['br'] is None or len(self.raw_data['br']) == 0 or self.datetime_array is None:
            print_manager.datacubby("Cannot calculate br_norm: No br data available")
            return None
        
        try:
            # Import the necessary components
            from plotbot import proton, get_data
            import scipy.interpolate as interpolate
            import matplotlib.dates as mdates
            
            # Get the current time range from our datetime_array
            start_time = self.datetime_array[0].strftime('%Y/%m/%d %H:%M:%S.%f')
            end_time = self.datetime_array[-1].strftime('%Y/%m/%d %H:%M:%S.%f')
            trange = [start_time, end_time]
            
            print_manager.dependency_management(f"Fetching sun_dist_rsun data for br_norm calculation (time range: {trange})")
            
            # Request proton sun_dist_rsun data for our time range
            get_data(trange, proton.sun_dist_rsun)
            
            # Check if we have valid proton data
            if not hasattr(proton, 'sun_dist_rsun') or not hasattr(proton.sun_dist_rsun, 'data') or proton.sun_dist_rsun.data is None:
                print_manager.datacubby("Cannot calculate br_norm: Failed to get proton sun distance data")
                return None
                
            # Get the necessary data arrays
            br_data = self.raw_data['br']
            mag_datetime = self.datetime_array
            proton_datetime = proton.datetime_array
            sun_dist_rsun = proton.sun_dist_rsun.data
            
            print_manager.datacubby(f"Interpolating sun_dist_rsun to match mag timeline...")
            print_manager.datacubby(f"  Mag datetime length: {len(mag_datetime)}")
            print_manager.datacubby(f"  Proton datetime length: {len(proton_datetime)}")
            
            # Convert datetime arrays to numeric for interpolation
            proton_time_numeric = mdates.date2num(proton_datetime)
            mag_time_numeric = mdates.date2num(mag_datetime)
            
            # Create interpolation function
            interp_func = interpolate.interp1d(
                proton_time_numeric, 
                sun_dist_rsun,
                kind='linear',
                bounds_error=False,
                fill_value='extrapolate'
            )
            
            # Apply interpolation to get sun distance at mag timestamps
            sun_dist_interp = interp_func(mag_time_numeric)
            
            # Calculate br_norm using the precise conversion factor
            rsun_to_au_conversion_factor = 215.032867644  # Solar radii per AU
            br_norm = br_data * ((sun_dist_interp / rsun_to_au_conversion_factor) ** 2)
            
            print_manager.datacubby(f"Successfully calculated br_norm (shape: {br_norm.shape})")
            
            # Store the result
            self.raw_data['br_norm'] = br_norm
            return True
            
        except Exception as e:
            print_manager.datacubby(f"Error calculating br_norm: {str(e)}")
            import traceback
            print_manager.datacubby(traceback.format_exc())
            return None
    
    def _setup_br_norm_plot_manager(self):
        """Create plot manager for br_norm with appropriate options"""
        if self.raw_data['br_norm'] is not None and self.datetime_array is not None:
            self.br_norm = plot_manager(
                self.raw_data['br_norm'],
                plot_options=ploptions(
                    data_type='mag_RTN_4sa',    # Actual data product name
                    var_name='br_norm_rtn_4sa',  # Variable name
                    class_name='mag_rtn_4sa',   # Class handling this data
                    subclass_name='br_norm',    # Specific component
                    plot_type='time_series',    # Type of plot
                    datetime_array=self.datetime_array,  # Time data
                    y_label='Br·R² [nT·AU²]',   # Y-axis label
                    legend_label='$B_R \cdot R^2$',  # Legend text
                    color='darkorange',         # Plot color (different from br's forestgreen)
                    y_scale='linear',           # Scale type
                    y_limit=None,               # Y-axis limits
                    line_width=1,               # Line width
                    line_style='-'              # Line style
                )
            )
            print_manager.dependency_management(f"Created plot manager for br_norm")
            return True
        else:
            print_manager.dependency_management(f"Cannot create plot manager for br_norm: No data available")
            return False

    def set_ploptions(self):
        """Create plot managers for each component with default options"""
        # STRATEGIC PRINT K
        dt_len_in_set_ploptions = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else "None_or_NoAttr"
        print_manager.dependency_management(f"[MAG_CLASS_DEBUG K] set_ploptions called for instance ID: {id(self)}. self.datetime_array len: {dt_len_in_set_ploptions}")

        print_manager.dependency_management(f"Setting up plot options for mag_rtn_4sa variables")
        
        self.all = plot_manager(
            [self.raw_data['br'], self.raw_data['bt'], self.raw_data['bn']],
            plot_options=ploptions(
                data_type='mag_RTN_4sa',    # Actual data product name
                var_name=['br_rtn_4sa', 'bt_rtn_4sa', 'bn_rtn_4sa'],  # Variable names
                class_name='mag_rtn_4sa',   # Class handling this data
                subclass_name='all',        # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label=['$B_R$', '$B_T$', '$B_N$'],  # Legend text
                color=['forestgreen', 'orange', 'dodgerblue'],  # Plot colors
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=[1, 1, 1],      # Line widths
                line_style=['-', '-', '-'] # Line styles
            )
        )
        print_manager.dependency_management(f"FYI: Example mag data: Created mag_rtn_4sa.all variable with {3 if self.raw_data['br'] is not None else 0} components")
        
        self.br = plot_manager(
            self.raw_data['br'],
            plot_options=ploptions(
                data_type='mag_RTN_4sa',    # Actual data product name
                var_name='br_rtn_4sa',      # Variable name in data file
                class_name='mag_rtn_4sa',   # Class handling this data type
                subclass_name='br',         # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_R$',      # Legend text
                color='forestgreen',        # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.bt = plot_manager(
            self.raw_data['bt'],
            plot_options=ploptions(
                data_type='mag_RTN_4sa',    # Actual data product name
                var_name='bt_rtn_4sa',      # Variable name in data file
                class_name='mag_rtn_4sa',   # Class handling this data type
                subclass_name='bt',         # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_T$',      # Legend text
                color='orange',            # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.bn = plot_manager(
            self.raw_data['bn'],
            plot_options=ploptions(
                data_type='mag_RTN_4sa',    # Actual data product name
                var_name='bn_rtn_4sa',      # Variable name in data file
                class_name='mag_rtn_4sa',   # Class handling this data type
                subclass_name='bn',         # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='B (nT)',          # Y-axis label
                legend_label='$B_N$',      # Legend text
                color='dodgerblue',        # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )
        
        self.bmag = plot_manager(
            self.raw_data['bmag'],
            plot_options=ploptions(
                data_type='mag_RTN_4sa',    # Actual data product name
                var_name='bmag_rtn_4sa',     # Variable name in data file
                class_name='mag_rtn_4sa',   # Class handling this data type
                subclass_name='bmag',       # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='|B| (nT)',        # Y-axis label
                legend_label='$|B|$',      # Legend text
                color='black',             # Plot color
                y_scale='linear',          # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )

        self.pmag = plot_manager(
            self.raw_data['pmag'],
            plot_options=ploptions(
                data_type='mag_RTN_4sa',    # Actual data product name
                var_name='pmag_rtn_4sa',     # Variable name in data file
                class_name='mag_rtn_4sa',   # Class handling this data type
                subclass_name='pmag',       # Specific component
                plot_type='time_series',    # Type of plot
                datetime_array=self.datetime_array,# Time data
                y_label='Pmag (nPa)',      # Y-axis label
                legend_label='$P_{mag}$',  # Legend text
                color='purple',            # Plot color
                y_scale='log',             # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
            
        )

        # br_norm plot manager is only created when it's data is available (lazy loading)
        # We don't create it here initially to avoid unnecessary proton data loading

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)

    def ensure_internal_consistency(self):
        """Ensures .time and .field are consistent with .datetime_array and .raw_data."""
        print_manager.dependency_management(f"*** GOLD ENSURE ID:{id(self)} *** Called for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")
        original_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        original_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        original_field_shape = self.field.shape if hasattr(self, 'field') and self.field is not None and hasattr(self.field, 'shape') else 'None_or_NoShape'
        
        print_manager.dependency_management(f"    PRE-CHECK - datetime_array len: {original_dt_len}")
        print_manager.dependency_management(f"    PRE-CHECK - time len: {original_time_len}")
        print_manager.dependency_management(f"    PRE-CHECK - field shape: {original_field_shape}")
        
        changed_time = False
        changed_field = False

        if hasattr(self, 'datetime_array') and self.datetime_array is not None and \
           hasattr(self, 'raw_data') and self.raw_data:

            if len(self.datetime_array) > 0:
                new_time_array = self.datetime_array.astype('datetime64[ns]').astype(np.int64)
                if not hasattr(self, 'time') or self.time is None or not np.array_equal(self.time, new_time_array):
                    self.time = new_time_array
                    print_manager.dependency_management(f"    [ENSURE_CONSISTENCY] Updated self.time via direct int64 cast. New len: {len(self.time)}")
                    changed_time = True
            elif not hasattr(self, 'time') or self.time is None or (hasattr(self.time, '__len__') and len(self.time) != 0):
                self.time = np.array([], dtype=np.int64)
                print_manager.dependency_management(f"    [ENSURE_CONSISTENCY] Set self.time to empty int64 array (datetime_array was empty).")
                changed_time = True

            expected_len = len(self.datetime_array)
            if ('br' in self.raw_data and self.raw_data['br'] is not None and
                'bt' in self.raw_data and self.raw_data['bt'] is not None and
                'bn' in self.raw_data and self.raw_data['bn'] is not None and
                len(self.raw_data['br']) == expected_len and
                len(self.raw_data['bt']) == expected_len and
                len(self.raw_data['bn']) == expected_len):
                new_field = np.column_stack((self.raw_data['br'], self.raw_data['bt'], self.raw_data['bn']))
                if not hasattr(self, 'field') or self.field is None or not np.array_equal(self.field, new_field):
                    self.field = new_field
                    print_manager.dependency_management(f"    Updated self.field from RTN components. New shape: {self.field.shape}")
                    changed_field = True
            else:
                if not (hasattr(self, 'field') and self.field is None and expected_len == 0):
                    if hasattr(self, 'field') and self.field is not None:
                         print_manager.dependency_management(f"    Nullifying self.field. Reason: RTN components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
                    elif not hasattr(self, 'field') and expected_len > 0: 
                         print_manager.dependency_management(f"    Setting self.field to None. Reason: RTN components in raw_data missing, None, or inconsistent lengths (expected {expected_len}).")
                         self.field = None
                         changed_field = True
            
            if (changed_time or changed_field) and hasattr(self, 'set_ploptions'):
                print_manager.dependency_management(f"    Calling self.set_ploptions() due to consistency updates (time changed: {changed_time}, field changed: {changed_field}).")
                self.set_ploptions()
        else:
            print_manager.dependency_management(f"    Skipping consistency check (datetime_array or raw_data missing/None).")
        
        final_time_len = len(self.time) if hasattr(self, 'time') and self.time is not None and hasattr(self.time, '__len__') else 'None_or_NoLen'
        final_dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else 'None_or_NoLen'
        final_field_shape = self.field.shape if hasattr(self, 'field') and self.field is not None and hasattr(self.field, 'shape') else 'None_or_NoShape'

        if changed_time or changed_field:
            print_manager.dependency_management(f"*** GOLD ENSURE ID:{id(self)} *** CHANGES WERE MADE.")
            print_manager.dependency_management(f"    POST-FIX - datetime_array len: {final_dt_len}")
            print_manager.dependency_management(f"    POST-FIX - time len: {final_time_len}")
            print_manager.dependency_management(f"    POST-FIX - field shape: {final_field_shape}")
        else:
            print_manager.dependency_management(f"*** GOLD ENSURE ID:{id(self)} *** NO CHANGES MADE by this method. Dt: {final_dt_len}, Time: {final_time_len}, Field: {final_field_shape}")
        print_manager.dependency_management(f"*** GOLD ENSURE ID:{id(self)} *** Finished for {self.class_name}.{self.subclass_name if self.subclass_name else 'MAIN'}.")

mag_rtn_4sa = mag_rtn_4sa_class(None) #Initialize the class with no data
print_manager.dependency_management('initialized mag_rtn_4sa class') 