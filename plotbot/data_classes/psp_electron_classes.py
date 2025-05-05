#plotbot/data_classes/psp_electron_classes.py

import numpy as np
import pandas as pd 
import cdflib 
from datetime import datetime, timedelta, timezone

# Import our custom managers (UPDATED PATHS)
from plotbot.print_manager import print_manager
# from plotbot.data_cubby import data_cubby # REMOVED Circular Import
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
from plotbot.get_encounter import get_encounter_number

class epad_strahl_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'raw_data', {
            'strahl': None,
            'centroids': None
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'times_mesh', [])
        object.__setattr__(self, 'pitch_angle', None)

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.debug("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.debug("Calculating EPAD strahl variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated EPAD strahl variables.")

        # Stash the instance in data_cubby for later retrieval / to avoid circular references
        # data_cubby.stash(self, class_name='epad')


    #strahl_update
    def update(self, imported_data): #This is function is the exact same across all classes :)
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        if imported_data is None:                                                # Exit if no new data
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified ploptions)
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
        
        print_manager.datacubby("=== End Update Debug ===\n")

    def get_subclass(self, subclass_name):  # Dynamic component retrieval method
        """Retrieve a specific component"""
        print_manager.debug(f"Getting subclass: {subclass_name}")  # Log which component is requested
        if subclass_name in self.raw_data.keys():  # Check if component exists in raw_data
            print_manager.debug(f"Returning {subclass_name} component")  # Log successful component find
            return getattr(self, subclass_name)  # Return the component
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
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        print('epad_strahl getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []  # Get list of valid attributes from raw_data
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}") # Show list of valid attributes to use
        # raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        # return None
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.debug(f"Setting attribute: {name} with value: {value}")
        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field', 'times_mesh', 'pitch_angle', 'energy_index'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.debug('epad_strahl setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            # Do not set the attrib
    
    def calculate_variables(self, imported_data):
        """Calculate and store EPAD strahl variables"""
        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
        
        # Extract data
        eflux = imported_data.data['EFLUX_VS_PA_E']
        self.pitch_angle = imported_data.data['PITCHANGLE']  # Store pitch angle as class attribute

        # Debug the time values
        print_manager.debug(f"Time values type: {type(self.time)}")
        print_manager.debug(f"Time values range: {self.time[0]} to {self.time[-1]}")

        # Set energy index based on encounter number
        # Convert numpy.datetime64 to datetime before using strftime
        date_str = pd.Timestamp(self.datetime_array[0]).strftime('%Y-%m-%d')
        encounter_number = get_encounter_number(date_str)
        if encounter_number in ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9']:
            self.energy_index = 8
        else:
            self.energy_index = 12

        print_manager.debug(f"Encounter number: {encounter_number}")
        print_manager.debug(f"Energy index: {self.energy_index}")

        # Extract strahl flux for specific energy
        strahl = eflux[:, :, self.energy_index]
        
        # Replace zeros and calculate log version
        strahl = np.where(strahl == 0, 1e-10, strahl)  # Replace zeros
        log_strahl = np.log10(strahl)
        strahl = log_strahl

        # Create time mesh to match strahl data dimensions
        self.times_mesh = np.meshgrid(
            self.datetime_array,
            np.arange(strahl.shape[1]),
            indexing='ij'
        )[0]

        # Calculate centroids
        centroids = np.ma.average(self.pitch_angle, 
                                weights=strahl, 
                                axis=1)

        strahl_centroids = centroids
        # Store raw data
        self.raw_data = {
            'strahl': strahl,
            'centroids': centroids
        }

    def set_ploptions(self):
        """Set up the plotting options for strahl data"""
        self.strahl = plot_manager(
            self.raw_data['strahl'],
            plot_options=ploptions(
                data_type='spe_sf0_pad',
                var_name='log_strahl',
                class_name='epad',
                subclass_name='strahl',
                plot_type='spectral',
                datetime_array=self.times_mesh,  # Use the mesh for time array
                y_label='Pitch Angle\n(degrees)',
                legend_label='Electron PAD',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.pitch_angle,
                colormap='jet',
                colorbar_scale='log',
                colorbar_limits=None
                # colorbar_limits=[9.4, 10.5]
            )
        )

        # Initialize centroids with plot_manager
        self.centroids = plot_manager(
            self.raw_data['centroids'],
            plot_options=ploptions(
                data_type='spe_sf0_pad',
                var_name='strahl_centroids',
                class_name='epad',
                subclass_name='centroids',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Pitch Angle \n (degrees)',
                legend_label='Strahl Centroids',
                color='crimson',
                y_scale='linear',
                y_limit=[0, 180],
                line_width=1,
                line_style='-'
            )
        )

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)

epad = epad_strahl_class(None) #Initialize the class with no data
print('initialized epad class')

class epad_strahl_high_res_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'raw_data', {
            'strahl': None,
            'centroids': None
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, 'times_mesh', [])
        object.__setattr__(self, 'pitch_angle', None)

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.debug("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.debug("Calculating high-resolution EPAD strahl variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated high-resolution EPAD strahl variables.")

        # Stash the instance in data_cubby for later retrieval / to avoid circular references
        # data_cubby.stash(self, class_name='epad_hr')

    def update(self, imported_data): #This is function is the exact same across all classes :)
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        if imported_data is None:                                                # Exit if no new data
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified ploptions)
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
        
        print_manager.datacubby("=== End Update Debug ===\n")

    def get_subclass(self, subclass_name):  # Dynamic component retrieval method
        """Retrieve a specific component"""
        print_manager.debug(f"Getting subclass: {subclass_name}")  # Log which component is requested
        if subclass_name in self.raw_data.keys():  # Check if component exists in raw_data
            print_manager.debug(f"Returning {subclass_name} component")  # Log successful component find
            return getattr(self, subclass_name)  # Return the component
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
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        print_manager.debug('epad_strahl_hr getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []  # Get list of valid attributes from raw_data
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}") # Show list of valid attributes to use
        # raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        # return None
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'): # Check for either '__' or '_' start
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.debug(f"Setting attribute: {name} with value: {value}")
        if name in ['datetime', 'datetime_array', 'raw_data', 'time', 'field', 'times_mesh', 'pitch_angle', 'energy_index'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.debug('epad_strahl_hr setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            # Do not set the attrib
    
    def calculate_variables(self, imported_data):
        """Calculate and store high-resolution EPAD strahl variables"""
        # Store only TT2000 times as numpy array
        self.time = np.asarray(imported_data.times)
        self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
        
        # Extract data
        eflux = imported_data.data['EFLUX_VS_PA_E']
        self.pitch_angle = imported_data.data['PITCHANGLE']  # Store pitch angle as class attribute

        # Debug the time values
        print_manager.debug(f"Time values type: {type(self.time)}")
        print_manager.debug(f"Time values range: {self.time[0]} to {self.time[-1]}")

        # Set energy index based on encounter number
        # Convert numpy.datetime64 to datetime before using strftime
        date_str = pd.Timestamp(self.datetime_array[0]).strftime('%Y-%m-%d')
        encounter_number = get_encounter_number(date_str)
        if encounter_number in ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9']:
            self.energy_index = 8
        else:
            self.energy_index = 12

        print_manager.debug(f"Encounter number: {encounter_number}")
        print_manager.debug(f"Energy index: {self.energy_index}")
        
        # Extract strahl flux for specific energy
        strahl = eflux[:, :, self.energy_index]
        
        # Calculate log version
        log_strahl = np.log10(strahl)
        strahl = log_strahl

        # Create time mesh to match strahl data dimensions
        self.times_mesh = np.meshgrid(
            self.datetime_array,
            np.arange(strahl.shape[1]),
            indexing='ij'
        )[0]

        # Calculate centroids
        centroids = np.ma.average(self.pitch_angle, 
                                weights=strahl, 
                                axis=1)

        strahl_centroids = centroids
        # Store raw data
        self.raw_data = {
            'strahl': strahl,
            'centroids': centroids
        }
    
    def set_ploptions(self):
        """Set up the plotting options for high-resolution strahl data"""
        self.strahl = plot_manager(
            self.raw_data['strahl'],
            plot_options=ploptions(
                data_type='spe_af0_pad',
                var_name='log_strahl_hr',
                class_name='epad_hr',
                subclass_name='strahl',
                plot_type='spectral',
                datetime_array=self.times_mesh,  # Use the mesh for time array
                y_label='Pitch Angle\n(degrees)',
                legend_label='Electron PAD (High Res)',
                color=None,
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data=self.pitch_angle,
                colormap='jet',
                colorbar_scale='log',
                colorbar_limits=None
            )
        )

        # Initialize centroids with plot_manager
        self.centroids = plot_manager(
            self.raw_data['centroids'],
            plot_options=ploptions(
                data_type='spe_af0_pad',
                var_name='strahl_centroids',
                class_name='epad_hr',
                subclass_name='centroids',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Pitch Angle \n (degrees)',
                legend_label='Strahl Centroids',
                color='crimson',
                y_scale='linear',
                y_limit=[0, 180],
                line_width=0.5,
                line_style='-'
            )
        )

    def restore_from_snapshot(self, snapshot_data):
        """
        Restore all relevant fields from a snapshot dictionary/object.
        This is used to directly assign all attributes from a pickled object,
        bypassing calculation.
        """
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)

epad_hr = epad_strahl_high_res_class(None) #Initialize the class with no data
print('initialized epad_hr class')