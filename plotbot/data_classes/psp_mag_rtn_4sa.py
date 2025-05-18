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
# from plotbot.get_data import get_data # MOVED into br_norm property to avoid circular import
# from plotbot import proton # MOVED into br_norm property to avoid circular import

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
            'br_norm': None # ADDED for lazy loading
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_br_norm_pm', None) # ADDED for lazy loading br_norm
        object.__setattr__(self, '_current_trange', None) # ADDED to store trange for get_data calls

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
        
        # Store the time range associated with this update if available
        if hasattr(imported_data, 'trange') and imported_data.trange:
            object.__setattr__(self, '_current_trange', imported_data.trange)
        elif self.datetime_array is not None and len(self.datetime_array) > 0:
             # Fallback if trange not directly on imported_data, try to derive from existing datetime_array
            start_time = self.datetime_array[0].strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]
            end_time = self.datetime_array[-1].strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]
            object.__setattr__(self, '_current_trange', [start_time, end_time])

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
        object.__setattr__(self, '_br_norm_pm', None) # Reset cached br_norm plot_manager on update
        
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
        # This method is called only if regular attribute access (via __getattribute__)
        # fails to find the attribute. Properties like br_norm should ideally be handled
        # by __getattribute__ before this method is ever called for them.

        # Allow direct access to dunder OR single underscore methods/attributes
        # by attempting to fetch them using object.__getattribute__.
        if name.startswith('_'):
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                # If even object.__getattribute__ fails for an underscored name,
                # then it truly doesn't exist.
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        # If __getattr__ is reached for a non-underscored name, it means the attribute
        # was not found through normal means (including properties).
        # Therefore, an AttributeError should be raised.
        # The previous implementation incorrectly printed a message and returned None implicitly.
        print_manager.dependency_management(f"__getattr__: Attribute '{name}' not found through standard access for {self.__class__.__name__}. Raising AttributeError.")
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
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
            # Store the time range if it's part of the imported_data object (might be useful for br_norm)
            if hasattr(imported_data, 'trange'):
                object.__setattr__(self, '_current_trange', imported_data.trange)
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
            'br_norm': None # Ensure br_norm is in raw_data but not calculated here
        }

        # # Convert TT2000 timestamps to datetime objects using cdflib
        # self.datetime = cdflib.cdfepoch.to_datetime(self.time)

        print_manager.dependency_management(f"\nDebug - Data Arrays:")
        print_manager.dependency_management(f"Time array shape: {self.time.shape}")
        print_manager.dependency_management(f"Field data shape: {self.field.shape}")
        print_manager.dependency_management(f"First TT2000 time: {self.time[0]}")
    
    def set_ploptions(self):
        """Create plot managers for each component with default options"""
        # STRATEGIC PRINT K
        dt_len_in_set_ploptions = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else "None_or_NoAttr"
        print_manager.dependency_management(f"[MAG_CLASS_DEBUG K] set_ploptions called for instance ID: {id(self)}. self.datetime_array len: {dt_len_in_set_ploptions}")

        print_manager.dependency_management(f"Setting up plot options for mag_rtn_4sa variables")
        
        # Ensure datetime_array is available before creating plot managers
        if self.datetime_array is None:
            print_manager.warning(f"Cannot set plot options for {self.class_name}: datetime_array is None.")
            # Initialize empty plot_managers for attributes if datetime_array is None
            # This prevents AttributeError if attributes are accessed before data is loaded.
            self.all = plot_manager(None, plot_options=ploptions(data_type='mag_RTN_4sa', class_name='mag_rtn_4sa', subclass_name='all', datetime_array=None))
            self.br = plot_manager(None, plot_options=ploptions(data_type='mag_RTN_4sa', class_name='mag_rtn_4sa', subclass_name='br', datetime_array=None))
            self.bt = plot_manager(None, plot_options=ploptions(data_type='mag_RTN_4sa', class_name='mag_rtn_4sa', subclass_name='bt', datetime_array=None))
            self.bn = plot_manager(None, plot_options=ploptions(data_type='mag_RTN_4sa', class_name='mag_rtn_4sa', subclass_name='bn', datetime_array=None))
            self.bmag = plot_manager(None, plot_options=ploptions(data_type='mag_RTN_4sa', class_name='mag_rtn_4sa', subclass_name='bmag', datetime_array=None))
            self.pmag = plot_manager(None, plot_options=ploptions(data_type='mag_RTN_4sa', class_name='mag_rtn_4sa', subclass_name='pmag', datetime_array=None))
            # Note: br_norm is handled by its property, so it doesn't need explicit empty initialization here.
            return

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
                legend_label=[r'$B_R$', r'$B_T$', r'$B_N$'],  # Legend text
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
                legend_label=r'$B_R$',      # Legend text
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
                legend_label=r'$B_T$',      # Legend text
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
                legend_label=r'$B_N$',      # Legend text
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
                legend_label=r'$|B|$',      # Legend text
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
                legend_label=r'$P_{mag}$',  # Legend text
                color='purple',            # Plot color
                y_scale='log',             # Scale type
                y_limit=None,              # Y-axis limits
                line_width=1,              # Line width
                line_style='-'             # Line style
            )
        )
        # br_norm plot_manager is now created on-demand by its property
        print_manager.dependency_management(f"FYI: Example mag data: Created mag_rtn_4sa.pmag variable with data shape {self.raw_data['pmag'].shape if self.raw_data['pmag'] is not None else 'None'}")

    @property
    def br_norm(self):
        """
        Lazily calculates Br normalized by solar distance squared (R^2).
        Fetches proton.sun_dist_rsun via get_data if needed.
        """
        from plotbot.get_data import get_data # MOVED HERE to avoid circular import
        from plotbot import proton # MOVED HERE to avoid circular import

        print_manager.dependency_management("br_norm property: Entered.") # DEBUG
        print_manager.dependency_management(f"br_norm property: type(proton) is {type(proton)}, type(proton.sun_dist_rsun) is {type(proton.sun_dist_rsun)}") # DEBUG

        if self._br_norm_pm is not None:
            print_manager.dependency_management("br_norm: Returning cached plot_manager.")
            return self._br_norm_pm

        print_manager.dependency_management("br_norm: Attempting calculation.")

        if self.datetime_array is None or len(self.datetime_array) == 0:
            print_manager.dependency_management("WARNING: br_norm: Cannot calculate. Mag data (self.datetime_array) not loaded yet.")
            self._br_norm_pm = plot_manager(None, plot_options=ploptions(
                data_type='mag_RTN_4sa', class_name='mag_rtn_4sa', subclass_name='br_norm', 
                datetime_array=None, y_label=r'$B_R \cdot R^2$' + ' (nT AU$^2$)', legend_label=r'$B_R \cdot R^2$'
            ))
            return self._br_norm_pm
        
        current_trange_for_proton = None
        print_manager.dependency_management(f"br_norm property: Checking self._current_trange. Type: {type(self._current_trange)}, Value: {self._current_trange}") # DEBUG
        if self._current_trange:
            current_trange_for_proton = self._current_trange
            print_manager.dependency_management(f"br_norm property: Used self._current_trange: {current_trange_for_proton}") # DEBUG
        else: 
            print_manager.dependency_management(f"br_norm property: self._current_trange is Falsey. Deriving from self.datetime_array. len={len(self.datetime_array)}") # DEBUG
            print_manager.dependency_management(f"br_norm property: Type of self.datetime_array[0] is {type(self.datetime_array[0])}") # DEBUG
            # Convert numpy.datetime64 to pandas Timestamp or Python datetime before strftime
            start_dt_obj = pd.Timestamp(self.datetime_array[0])
            end_dt_obj = pd.Timestamp(self.datetime_array[-1])
            
            start_time = start_dt_obj.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]
            print_manager.dependency_management(f"br_norm property: Calculated start_time: {start_time}") # DEBUG
            end_time = end_dt_obj.strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]
            print_manager.dependency_management(f"br_norm property: Calculated end_time: {end_time}") # DEBUG
            current_trange_for_proton = [start_time, end_time]
            print_manager.dependency_management(f"br_norm property: Derived trange for proton data: {current_trange_for_proton}")
        
        print_manager.dependency_management(f"br_norm property: Calling get_data for proton.sun_dist_rsun with trange: {current_trange_for_proton}")
        get_data(current_trange_for_proton, proton.sun_dist_rsun) # Ensures proton data is loaded/calculated
        print_manager.dependency_management(f"DEBUG MAG: br_norm: After get_data for proton.sun_dist_rsun.")
        if hasattr(proton, 'sun_dist_rsun') and proton.sun_dist_rsun is not None and hasattr(proton.sun_dist_rsun, 'data'):
            print_manager.dependency_management(f"DEBUG MAG: br_norm: proton.sun_dist_rsun.data type={type(proton.sun_dist_rsun.data)}, shape={getattr(proton.sun_dist_rsun.data, 'shape', 'N/A')}, ndim={getattr(proton.sun_dist_rsun.data, 'ndim', 'N/A')}")
        else:
            print_manager.dependency_management(f"DEBUG MAG: br_norm: proton.sun_dist_rsun or its .data attribute is None or missing.")
        if hasattr(proton, 'datetime_array'):
            print_manager.dependency_management(f"DEBUG MAG: br_norm: proton.datetime_array type={type(proton.datetime_array)}, len={len(proton.datetime_array) if proton.datetime_array is not None else 'None'}")
        else:
            print_manager.dependency_management(f"DEBUG MAG: br_norm: proton.datetime_array is missing.")

        print_manager.dependency_management(f"br_norm property: After get_data for proton. proton.sun_dist_rsun.data is type {type(proton.sun_dist_rsun.data)}, proton.datetime_array is type {type(proton.datetime_array)}") # DEBUG
        if proton.sun_dist_rsun.data is None or proton.datetime_array is None or len(proton.datetime_array) == 0:
            print_manager.dependency_management("WARNING: br_norm: Proton sun_dist_rsun data or datetime_array not available after get_data call.")
            self._br_norm_pm = plot_manager(None, plot_options=ploptions(
                data_type='mag_RTN_4sa', class_name='mag_rtn_4sa', subclass_name='br_norm', 
                datetime_array=self.datetime_array, y_label=r'$B_R \cdot R^2$' + ' (nT AU$^2$)', legend_label=r'$B_R \cdot R^2$'
            ))
            return self._br_norm_pm

        br_data = self.raw_data.get('br')
        if br_data is None:
            print_manager.dependency_management("WARNING: br_norm: Mag br data not available.")
            self._br_norm_pm = plot_manager(None, plot_options=ploptions(
                data_type='mag_RTN_4sa', class_name='mag_rtn_4sa', subclass_name='br_norm', 
                datetime_array=self.datetime_array, y_label=r'$B_R \cdot R^2$' + ' (nT AU$^2$)', legend_label=r'$B_R \cdot R^2$'
            ))
            return self._br_norm_pm

        # Ensure proton.datetime_array is sorted for np.interp
        print_manager.dependency_management("br_norm property: Preparing for interpolation.") # DEBUG
        print_manager.dependency_management(f"br_norm property: proton.datetime_array (before sort): type={type(proton.datetime_array)}, len={len(proton.datetime_array) if proton.datetime_array is not None else 'None'}") # DEBUG
        # Commenting out this line because it fails when proton.sun_dist_rsun.data is a scalar
        # print_manager.dependency_management(f"br_norm property: proton.sun_dist_rsun.data (before sort): type={type(proton.sun_dist_rsun.data)}, len={len(proton.sun_dist_rsun.data) if proton.sun_dist_rsun.data is not None else 'None'}") # DEBUG
        
        # Sort datetime array for proper interpolation
        sort_indices = np.argsort(proton.datetime_array)
        proton_dt_sorted = proton.datetime_array[sort_indices]
        
        # Safely examine and log details about sun_dist_rsun.data before attempting to index it
        if getattr(proton.sun_dist_rsun.data, 'ndim', None) == 0 or isinstance(proton.sun_dist_rsun.data, (int, float)):
            print_manager.dependency_management(f"DEBUG MAG: CRITICAL - Found scalar value in proton.sun_dist_rsun.data: {proton.sun_dist_rsun.data}")
            print_manager.dependency_management("DEBUG MAG: This is likely because SUN_DIST in CDF is stored as a scalar, not an array")
            
            # Check if we can use the data from raw_data directly
            if hasattr(proton, 'raw_data') and isinstance(proton.raw_data, dict) and 'sun_dist_rsun' in proton.raw_data:
                print_manager.dependency_management(f"DEBUG MAG: Found sun_dist_rsun in proton.raw_data. Type={type(proton.raw_data['sun_dist_rsun'])}, shape={getattr(proton.raw_data['sun_dist_rsun'], 'shape', 'No shape')}")
                # Use the array from raw_data instead
                print_manager.dependency_management(f"DEBUG MAG: Using sun_dist_rsun array from proton.raw_data with length {len(proton.raw_data['sun_dist_rsun'])}")
                proton_sun_dist_sorted = proton.raw_data['sun_dist_rsun'][sort_indices]
            else:
                # Fallback - create a properly sized array using the scalar value
                print_manager.dependency_management(f"DEBUG MAG: Creating array of length {len(proton.datetime_array)} with repeated scalar value")
                proton_sun_dist_data = np.full(len(proton.datetime_array), proton.sun_dist_rsun.data, dtype=float)
                # Proceed with this array
                proton_sun_dist_sorted = proton_sun_dist_data[sort_indices]
        else:
            print_manager.dependency_management(f"DEBUG MAG: Using original array with shape {proton.sun_dist_rsun.data.shape}")
            proton_sun_dist_sorted = proton.sun_dist_rsun.data[sort_indices]
        
        print_manager.dependency_management("br_norm property: Converted datetimes to timestamps for interpolation.") # DEBUG
        # Convert datetimes to timestamps for interpolation
        mag_timestamps = self.datetime_array.astype(np.int64) // 10**9
        proton_timestamps_sorted = proton_dt_sorted.astype(np.int64) // 10**9
        
        # Handle cases where proton data might not span the mag data range
        # Or if proton_timestamps_sorted is empty or has duplicate timestamps after conversion
        if len(proton_timestamps_sorted) < 2 or np.all(proton_timestamps_sorted == proton_timestamps_sorted[0]):
             print_manager.dependency_management("WARNING: br_norm: Proton datetime data is insufficient for interpolation (too few unique points).")
             self._br_norm_pm = plot_manager(None, plot_options=ploptions(
                data_type='mag_RTN_4sa', class_name='mag_rtn_4sa', subclass_name='br_norm', 
                datetime_array=self.datetime_array, y_label=r'$B_R \cdot R^2$' + ' (nT AU$^2$)', legend_label=r'$B_R \cdot R^2$'
            ))
             return self._br_norm_pm

        try:
            print_manager.dependency_management("br_norm property: Attempting np.interp.") # DEBUG
            sun_dist_interp_rsun = np.interp(mag_timestamps, proton_timestamps_sorted, proton_sun_dist_sorted)
            print_manager.dependency_management("br_norm property: np.interp successful.") # DEBUG
        except Exception as e:
            print_manager.dependency_management(f"ERROR: br_norm: Error during interpolation of sun_dist_rsun: {e}")
            self._br_norm_pm = plot_manager(None, plot_options=ploptions(
                data_type='mag_RTN_4sa', class_name='mag_rtn_4sa', subclass_name='br_norm', 
                datetime_array=self.datetime_array, y_label=r'$B_R \cdot R^2$' + ' (nT AU$^2$)', legend_label=r'$B_R \cdot R^2$'
            ))
            return self._br_norm_pm

        rsun_to_au_conversion_factor = 215.03286764414261
        
        calculated_br_norm_data = br_data * ((sun_dist_interp_rsun / rsun_to_au_conversion_factor) ** 2)
        self.raw_data['br_norm'] = calculated_br_norm_data
        
        print_manager.dependency_management(f"br_norm property: Successfully calculated br_norm data. Shape: {calculated_br_norm_data.shape}") # DEBUG
        print_manager.dependency_management("br_norm property: Creating final plot_manager for br_norm.") # DEBUG
        
        # Ensure data is a properly shaped array (flattened to 1D if needed)
        if calculated_br_norm_data.ndim != 1:
            print_manager.dependency_management(f"DEBUG MAG: br_norm: Reshaping calculated_br_norm_data from {calculated_br_norm_data.ndim}D to 1D")
            calculated_br_norm_data = calculated_br_norm_data.flatten()

        # Debug the shape AFTER ensuring 1D
        print_manager.dependency_management(f"DEBUG MAG: br_norm: Final calculated_br_norm_data shape before plot_manager: {calculated_br_norm_data.shape}, ndim={calculated_br_norm_data.ndim}")

        # Create a custom plot_manager class that properly handles scalar values for Plotbot
        class BrNormPlotManager(plot_manager):
            def __array__(self, dtype=None):
                # Create a proper 1D array instead of scalar
                arr = np.asarray(self.view(np.ndarray), dtype=dtype)
                # Ensure it's 1D, not 0D (scalar)
                if arr.ndim == 0:
                    print_manager.dependency_management("BrNormPlotManager: Converting scalar to 1D array")
                    arr = np.expand_dims(arr, axis=0)
                return plot_manager(arr, self.plot_options)

        self._br_norm_pm = BrNormPlotManager(
            calculated_br_norm_data,
            plot_options=ploptions(
                data_type='mag_RTN_4sa',
                var_name='br_norm_rtn_4sa', # Suggested var_name
                class_name='mag_rtn_4sa',
                subclass_name='br_norm',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label=r'$B_R \cdot R^2$' + ' (nT AU$^2$)', # Updated label
                legend_label=r'$B_R \cdot R^2$',       # Updated legend
                color='cyan', 
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )
        return self._br_norm_pm

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