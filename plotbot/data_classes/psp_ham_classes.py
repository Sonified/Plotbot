import numpy as np
import pandas as pd
import logging
import cdflib # Needed for TT2000 conversion in calculate_variables

# Import our custom managers
from plotbot.print_manager import print_manager
from plotbot.data_cubby import data_cubby
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot

class ham_class:
    def __init__(self, imported_data):
        # Initialize raw_data with keys for all expected variables from CSV header
        # plus original placeholders if needed (though they might be redundant now)
        object.__setattr__(self, 'raw_data', {
            # Original placeholders (can potentially be removed if not used elsewhere)
            'hamstring': None,
            'hamstring_og': None,
            'hamstring_dt': None,
            'N_core': None,         # Note: N_core, N_neck, N_ham seem specific to SPAN data, not HAM CSV
            'N_core_og': None,
            'N_neck': None,
            'N_neck_og': None,
            'N_ham': None,
            'N_ham_og': None,
            # Variables from HAM CSV Header (excluding time/datetime)
            'hamogram_30s': None,
            'hamogram_og_30s': None,
            'hamogram_1m': None,        # Placeholder - not in provided header/specs, maybe remove?
            'hamogram_og_1m': None,     # Placeholder - maybe remove?
            'hamogram_2m': None,
            'hamogram_og_2m': None,
            'hamogram_20m': None,
            'hamogram_og_20m': None,    # Placeholder - maybe remove?
            'hamogram_90m': None,
            'hamogram_og_90m': None,    # Placeholder - maybe remove?
            'hamogram_4h': None,
            'hamogram_og_4h': None,
            'hamogram_12h': None,       # Placeholder - maybe remove?
            'hamogram_og_12h': None,    # Placeholder - maybe remove?
            'trat_ham': None,
            'trat_ham_og': None,
            'ham_core_drift': None,
            'ham_core_drift_va': None,
            'Nham_div_Ncore': None,
            'Nham_div_Ncore_og': None,
            'Nham_div_Ntot': None,
            'Nham_div_Ntot_og': None,
            'Tperp_ham_div_core': None,
            'Tperp_ham_div_core_og': None,
            'Tperprat_driftva_hc': None,
            'Tperprat_driftva_hc_og': None,
        })
        object.__setattr__(self, 'time', None) # To store raw TT2000 time
        object.__setattr__(self, 'datetime_array', None) # To store Python datetime objects

        if imported_data is None:
            self.set_ploptions() # Set empty ploptions on init
            print_manager.debug("Ham class: No data provided; initialized with empty attributes.")
        else:
            print_manager.debug("Ham class: Processing imported data...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Ham class: Successfully processed imported data.")

        # Stash the instance in data_cubby
        data_cubby.stash(self, class_name='ham')

    def update(self, imported_data):
        """Method to update class with new data."""
        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return

        print_manager.datacubby(f"\n=== Starting {self.__class__.__name__} update... ===")

        # Store current plot state before update
        current_state = {}
        # Use all keys defined in raw_data that might have a plot_manager
        # A more robust way is to iterate through attributes that ARE plot_managers
        plottable_attrs = [attr for attr in dir(self) if isinstance(getattr(self, attr, None), plot_manager)]
        for subclass_name in plottable_attrs:
             var = getattr(self, subclass_name)
             if hasattr(var, '_plot_state'):
                 current_state[subclass_name] = dict(var._plot_state)
                 print_manager.datacubby(f"Stored {subclass_name} state: {retrieve_ploption_snapshot(current_state[subclass_name])}")
             else:
                 # Handle case where attribute exists but has no _plot_state (e.g., if data was None initially)
                 print_manager.debug(f"Attribute {subclass_name} has no _plot_state to store.")


        # Perform update
        self.calculate_variables(imported_data)

        # Recreate plot managers
        self.set_ploptions()

        # Restore state
        print_manager.datacubby("Restoring saved state...")
        for subclass_name, state in current_state.items():
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                # Ensure the plot_manager instance exists AND is the correct type before restoring
                if isinstance(var, plot_manager) and hasattr(var, '_plot_state'):
                    var._plot_state.update(state)
                    for attr, value in state.items():
                        if hasattr(var.plot_options, attr):
                            setattr(var.plot_options, attr, value)
                    print_manager.datacubby(f"Restored {subclass_name} state: {retrieve_ploption_snapshot(state)}")
                else:
                    print_manager.debug(f"Could not restore state for {subclass_name}, plot_manager instance might be missing or invalid.")


        print_manager.datacubby(f"=== Finished {self.__class__.__name__} update ===\n")

    def get_subclass(self, subclass_name):
        """Retrieve a specific plot_manager attribute by its name."""
        print_manager.debug(f"Attempting to get subclass/attribute: {subclass_name}")

        if hasattr(self, subclass_name):
            attribute_value = getattr(self, subclass_name)
            if isinstance(attribute_value, plot_manager):
                print_manager.debug(f"Returning plot_manager instance for: {subclass_name}")
                return attribute_value
            else:
                print_manager.warning(f"Attribute '{subclass_name}' exists but is not a plot_manager instance (Type: {type(attribute_value)}). Returning None.")
                return None
        else:
            print(f"'{subclass_name}' is not a recognized subclass/attribute for ham data!")
            available_attrs = [attr for attr in dir(self) if isinstance(getattr(self, attr, None), plot_manager) and not attr.startswith('_')]
            print(f"Available plot managers: {', '.join(sorted(available_attrs))}")
            return None

    def __getattr__(self, name):
        """Provide a helpful error message when an attribute is not found."""
        print_manager.debug(f'ham_class __getattr__ triggered for: {name}')
        available_attrs = [attr for attr in dir(self)
                           if isinstance(getattr(self, attr, None), plot_manager)
                           and not attr.startswith('_')]
        error_message = f"'{name}' is not a recognized ham attribute, friend!"
        if available_attrs:
            error_message += f"\nAvailable plot managers: {', '.join(sorted(available_attrs))}"
        else:
            error_message += "\nNo plot manager attributes seem to be available yet."
        raise AttributeError(error_message)

    def __setattr__(self, name, value):
        """Allow setting attributes directly."""
        super().__setattr__(name, value)

    def calculate_variables(self, imported_data):
        """Assigns data from imported object to raw_data and sets time arrays."""
        try:
            # imported_data is expected to be a DataObject instance
            if not hasattr(imported_data, 'data') or not hasattr(imported_data, 'times'):
                logging.error("Error in ham calculate_variables: imported_data is not a valid DataObject.")
                # Clear all data if input is invalid
                for key in self.raw_data:
                    self.raw_data[key] = None
                self.time = None
                self.datetime_array = None
                return

            data_dict = imported_data.data # Access the dictionary within the DataObject
            self.time = np.asarray(imported_data.times) # Store the raw TT2000 array

            if self.time is None or self.time.size == 0:
                logging.error("Imported DataObject for ham has empty or None 'times' attribute.")
                # Clear all data if time is invalid
                for key in self.raw_data:
                    self.raw_data[key] = None
                self.datetime_array = None
                return

            # Convert TT2000 to Python datetime objects for plotting
            try:
                 self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
                 print_manager.debug(f"Successfully converted {len(self.datetime_array)} TT2000 timestamps to datetime objects.")
            except Exception as time_conv_e:
                 logging.error(f"Error converting TT2000 timestamps to datetime: {time_conv_e}")
                 # Clear all data if time conversion fails
                 for key in self.raw_data:
                     self.raw_data[key] = None
                 self.time = None
                 self.datetime_array = None
                 return


            # Directly assign data from imported object to raw_data dictionary
            # using the keys defined in __init__ (which should match CSV headers)
            for key in self.raw_data.keys():
                if key in data_dict:
                    # Ensure data is numpy array for consistency
                    data_val = data_dict[key]
                    if isinstance(data_val, (list, tuple)):
                        self.raw_data[key] = np.array(data_val)
                    elif isinstance(data_val, pd.Series):
                        self.raw_data[key] = data_val.to_numpy()
                    elif isinstance(data_val, np.ndarray):
                        self.raw_data[key] = data_val
                    else:
                        # Handle unexpected data types if necessary, maybe convert or log warning
                        logging.warning(f"Unexpected data type for key '{key}': {type(data_val)}. Assigning as is.")
                        self.raw_data[key] = data_val

                    print_manager.debug(f"Assigned data for key: {key}, shape: {self.raw_data[key].shape if hasattr(self.raw_data[key], 'shape') else 'N/A'}")
                    # --- NaN Check ---
                    if isinstance(self.raw_data[key], np.ndarray) and np.isnan(self.raw_data[key]).all():
                        logging.warning(f"All values for key '{key}' are NaN.")
                    # ---------------

                else:
                    # Keep as None if key is missing in imported data, log warning
                    # This is expected for the old placeholder keys if they aren't in the CSV
                    if key not in ['hamstring', 'hamstring_og', 'hamstring_dt', 'N_core', 'N_core_og', 'N_neck', 'N_neck_og', 'N_ham', 'N_ham_og', 'hamogram_1m', 'hamogram_og_1m', 'hamogram_og_20m', 'hamogram_og_90m', 'hamogram_12h', 'hamogram_og_12h']:
                         logging.warning(f"Key '{key}' not found in imported ham data dictionary.")
                    self.raw_data[key] = None # Ensure it's None if missing

        except Exception as e:
            logging.error(f"Error during ham data assignment in calculate_variables: {e}")
            import traceback
            logging.error(traceback.format_exc())
            # Clear all fields if a generic error occurs
            for key in self.raw_data:
                self.raw_data[key] = None
            self.time = None
            self.datetime_array = None

        # Stash instance after update
        data_cubby.stash(self, class_name='ham')

    def _create_ham_scatter_ploptions(self, var_name, subclass_name, y_label, legend_label, color, marker_style=(5, 1), marker_size=20, alpha=0.2, y_limit=None):
        """Helper method for standard ham scatter plot options."""
        # Default star marker (5, 1), size 20, alpha 0.2 if not overridden
        # print('Running _create_ham_scatter_ploptions')
        return ploptions(
            var_name=var_name,
            data_type='ham',
            class_name='ham',
            subclass_name=subclass_name,
            plot_type='scatter',
            datetime_array=self.datetime_array,
            y_label=y_label,
            legend_label=legend_label,
            color=color,
            y_scale='linear',
            marker_style=marker_style,
            marker_size=marker_size,
            alpha=alpha,
            y_limit=y_limit # Default to auto-limits
        )

    def _create_ham_timeseries_ploptions(self, var_name, subclass_name, y_label, legend_label, color, y_limit=[0, None], line_width=1, line_style='-'):
        """Helper method for standard ham time series plot options."""
        # Default y_limit [0, None], lw 1, ls '-' if not overridden
        return ploptions(
            var_name=var_name,
            data_type='ham',
            class_name='ham',
            subclass_name=subclass_name,
            plot_type='time_series',
            datetime_array=self.datetime_array,
            y_label=y_label,
            legend_label=legend_label,
            color=color,
            y_scale='linear',
            line_width=line_width,
            line_style=line_style,
            y_limit=y_limit
        )

    def set_ploptions(self):
        """Initialize or update plot_manager instances based on CSV headers and specs."""

        # --- Original Placeholders (Keep or Remove?) ---
        # These might be redundant if not actually present in HAM CSVs
        # If keeping, ensure data is actually loaded for them if expected.
        self.hamstring = plot_manager(
             self.raw_data.get('hamstring'),
             plot_options=self._create_ham_scatter_ploptions(
                 var_name='hamstring', subclass_name='hamstring',
                 y_label='Hamstring (Placeholder)', legend_label='Hamstring (Placeholder)', color='grey'
             )
        )
        # ... (keep other placeholders like N_core, etc. if needed, maybe with grey color) ...

        # --- Variables from HAM CSV Header & Specs ---

        # 1 - hamogram_30s (Time Series)
        self.hamogram_30s = plot_manager(
            self.raw_data.get('hamogram_30s'),
            plot_options=self._create_ham_timeseries_ploptions(
                var_name='hamogram_30s', subclass_name='hamogram_30s',
                y_label=r'Hamogram', legend_label=r'Hamogram_30s', color='palevioletred',
                y_limit=[0, None], line_width=1, line_style='-' # Spec values
            )
        )

        # 2 - hamogram_og_30s (Time Series)
        self.hamogram_og_30s = plot_manager(
            self.raw_data.get('hamogram_og_30s'),
            plot_options=self._create_ham_timeseries_ploptions(
                var_name='hamogram_og_30s', subclass_name='hamogram_og_30s',
                y_label=r'Hamogram_og_30s', legend_label=r'Hamogram_og_30s ', color='palevioletred',
                y_limit=None, line_width=1, line_style='-' # Spec values (Note: y_limit=None)
            )
        )

        # 3 - hamogram_2m (Time Series)
        self.hamogram_2m = plot_manager(
            self.raw_data.get('hamogram_2m'),
            plot_options=self._create_ham_timeseries_ploptions(
                var_name='hamogram_2m', subclass_name='hamogram_2m',
                y_label=r'Hamogram', legend_label=r'Hamogram_2m', color='palevioletred',
                y_limit=[0, None], line_width=1, line_style='-' # Spec values
            )
        )

        # 4 - hamogram_og_2m (Time Series)
        self.hamogram_og_2m = plot_manager(
            self.raw_data.get('hamogram_og_2m'),
            plot_options=self._create_ham_timeseries_ploptions(
                var_name='hamogram_og_2m', subclass_name='hamogram_og_2m',
                y_label=r'Hamogram_og_2m', legend_label=r'Hamogram_og_2m ', color='palevioletred',
                y_limit=None, line_width=1, line_style='-' # Spec values (Note: y_limit=None)
            )
        )

        # 5 - hamogram_20m (Time Series)
        self.hamogram_20m = plot_manager(
            self.raw_data.get('hamogram_20m'),
            plot_options=self._create_ham_timeseries_ploptions(
                var_name='hamogram_20m', subclass_name='hamogram_20m',
                y_label=r'Hamogram', legend_label=r'Hamogram_20m', color='palevioletred',
                y_limit=[0, None], line_width=1, line_style='-' # Spec values
            )
        )

        # 6 - hamogram_90m (Time Series)
        self.hamogram_90m = plot_manager(
            self.raw_data.get('hamogram_90m'),
            plot_options=self._create_ham_timeseries_ploptions(
                var_name='hamogram_90m', subclass_name='hamogram_90m',
                y_label=r'Hamogram', legend_label=r'Hamogram_90m', color='palevioletred',
                y_limit=[0, None], line_width=1, line_style='-' # Spec values
            )
        )

        # 7 - hamogram_4h (Time Series)
        self.hamogram_4h = plot_manager(
            self.raw_data.get('hamogram_4h'),
            plot_options=self._create_ham_timeseries_ploptions(
                var_name='hamogram_4h', subclass_name='hamogram_4h',
                y_label=r'Hamogram', legend_label=r'Hamogram_4h', color='palevioletred',
                y_limit=[0, None], line_width=1, line_style='-' # Spec values
            )
        )

        # 8 - hamogram_og_4h (Time Series)
        self.hamogram_og_4h = plot_manager(
            self.raw_data.get('hamogram_og_4h'),
            plot_options=self._create_ham_timeseries_ploptions(
                var_name='hamogram_og_4h', subclass_name='hamogram_og_4h',
                y_label=r'Hamogram_og_4h', legend_label=r'Hamogram_og_4h', color='palevioletred',
                y_limit=None, line_width=1, line_style='-' # Spec values (Note: y_limit=None)
            )
        )

        # 9 - trat_ham (Scatter) - CSV name: trat_ham, Spec name: ham_trat
        self.trat_ham = plot_manager(
            self.raw_data.get('trat_ham'),
            plot_options=self._create_ham_scatter_ploptions(
                var_name='trat_ham', subclass_name='trat_ham',
                y_label=r'$T_\perp/T_\parallel$', legend_label=r'$(T_\perp/T_\parallel)_{{ham}}$', color='palevioletred',
                marker_style=(5, 1), marker_size=50, alpha=0.9 # Spec values
            )
        )

        # 10 - trat_ham_og (Scatter) - CSV name: trat_ham_og
        self.trat_ham_og = plot_manager(
            self.raw_data.get('trat_ham_og'),
            plot_options=self._create_ham_scatter_ploptions(
                var_name='trat_ham_og', subclass_name='trat_ham_og',
                y_label=r'$(T_\perp/T_\parallel)_{{og}}$', legend_label=r'$(T_\perp/T_\parallel)_{{ham,og}}$', color='palevioletred',
                marker_style=(5, 1), marker_size=50, alpha=0.9 # Spec values
            )
        )

        # 11 - ham_core_drift (Scatter) - CSV name: ham_core_drift
        self.ham_core_drift = plot_manager(
            self.raw_data.get('ham_core_drift'),
            plot_options=self._create_ham_scatter_ploptions(
                var_name='ham_core_drift', subclass_name='ham_core_drift',
                y_label='$v_{{drift}}$ km/s', legend_label=r'$(vd)_{{h-c}}$ km/s', color='palevioletred',
                marker_style=(5, 1), marker_size=50, alpha=0.9 # Spec values
            )
        )

        # 12 - ham_core_drift_va (Scatter) - CSV name: ham_core_drift_va
        self.ham_core_drift_va = plot_manager(
            self.raw_data.get('ham_core_drift_va'),
            plot_options=self._create_ham_scatter_ploptions(
                var_name='ham_core_drift_va', subclass_name='ham_core_drift_va',
                y_label='$v_{{drift}}/v_{{A}}$', legend_label=r'$(v_{{d}}/v_{{A}})_{{h-c}}$', color='palevioletred',
                marker_style=(5, 1), marker_size=50, alpha=0.9 # Spec values
            )
        )

        # 13 - Nham_div_Ncore (Scatter) - CSV name: Nham_div_Ncore, Spec name: N_ham/N_core
        self.Nham_div_Ncore = plot_manager(
            self.raw_data.get('Nham_div_Ncore'),
            plot_options=self._create_ham_scatter_ploptions(
                var_name='Nham_div_Ncore', subclass_name='Nham_div_Ncore',
                y_label=r'$N_{{s}}/N_{{core}}$', legend_label=r'$N_{{ham}}/N_{{core}}$', color='palevioletred',
                marker_style=(5, 1), marker_size=20, alpha=0.2 # Spec values
            )
        )

        # 14 - Nham_div_Ncore_og (Scatter) - CSV name: Nham_div_Ncore_og, Spec name: N_ham_og/N_core_og
        self.Nham_div_Ncore_og = plot_manager(
            self.raw_data.get('Nham_div_Ncore_og'),
            plot_options=self._create_ham_scatter_ploptions(
                var_name='Nham_div_Ncore_og', subclass_name='Nham_div_Ncore_og',
                y_label=r'$N_{{s,og}}/N_{{core,og}}$', legend_label=r'$N_{{ham}}/N_{{core,og}}$', color='palevioletred',
                marker_style=(5, 1), marker_size=20, alpha=0.2 # Spec values
            )
        )

        # 15 - Nham_div_Ntot (Scatter) - CSV name: Nham_div_Ntot, Spec name: N_ham/N_tot
        self.Nham_div_Ntot = plot_manager(
            self.raw_data.get('Nham_div_Ntot'),
            plot_options=self._create_ham_scatter_ploptions(
                var_name='Nham_div_Ntot', subclass_name='Nham_div_Ntot',
                y_label=r'$N_{{s}}/N_{{tot}}$', legend_label=r'$N_{{ham}}/N_{{tot}}$', color='palevioletred',
                marker_style=(5, 1), marker_size=50, alpha=0.9 # Spec values
            )
        )

        # 16 - Nham_div_Ntot_og (Scatter) - CSV name: Nham_div_Ntot_og, Spec name: N_ham_og/N_tot_og
        self.Nham_div_Ntot_og = plot_manager(
            self.raw_data.get('Nham_div_Ntot_og'),
            plot_options=self._create_ham_scatter_ploptions(
                var_name='Nham_div_Ntot_og', subclass_name='Nham_div_Ntot_og',
                y_label=r'$N_{{s,og}}/N_{{tot,og}}$', legend_label=r'$N_{{ham,og}}/N_{{tot,og}}$', color='palevioletred',
                marker_style=(5, 1), marker_size=50, alpha=0.9 # Spec values
            )
        )

        # 17 - Tperp_ham_div_core (Scatter) - CSV name: Tperp_ham_div_core
        self.Tperp_ham_div_core = plot_manager(
            self.raw_data.get('Tperp_ham_div_core'),
            plot_options=self._create_ham_scatter_ploptions(
                var_name='Tperp_ham_div_core', subclass_name='Tperp_ham_div_core',
                y_label=r'$T_{{\perp,h}}/T_{{\perp,c}}$', legend_label=r'$T_{{\perp,h}}/T_{{\perp,c}}$', color='palevioletred',
                marker_style=(5, 1), marker_size=20, alpha=0.2 # Spec values
            )
        )

        # 18 - Tperp_ham_div_core_og (Scatter) - CSV name: Tperp_ham_div_core_og
        self.Tperp_ham_div_core_og = plot_manager(
            self.raw_data.get('Tperp_ham_div_core_og'),
            plot_options=self._create_ham_scatter_ploptions(
                var_name='Tperp_ham_div_core_og', subclass_name='Tperp_ham_div_core_og',
                y_label=r'$T_{{\perp,h}}/T_{{\perp,c}}$', legend_label=r'$T_{{\perp,h}}/T_{{\perp,c}}$', color='palevioletred', # Note: Spec legend label same as #17?
                marker_style=(5, 1), marker_size=20, alpha=0.2 # Spec values
            )
        )

        # 19 - Tperprat_driftva_hc (Scatter) - CSV name: Tperprat_driftva_hc
        self.Tperprat_driftva_hc = plot_manager(
            self.raw_data.get('Tperprat_driftva_hc'),
            plot_options=self._create_ham_scatter_ploptions(
                var_name='Tperprat_driftva_hc', subclass_name='Tperprat_driftva_hc',
                y_label='ham param1', legend_label='ham param1', color='palevioletred',
                marker_style=(5, 1), marker_size=20, alpha=0.2 # Spec values
            )
        )

        # 20 - Tperprat_driftva_hc_og (Scatter) - CSV name: Tperprat_driftva_hc_og, Spec name: ham_param1_og
        self.Tperprat_driftva_hc_og = plot_manager(
            self.raw_data.get('Tperprat_driftva_hc_og'),
            plot_options=self._create_ham_scatter_ploptions(
                var_name='Tperprat_driftva_hc_og', subclass_name='Tperprat_driftva_hc_og',
                y_label='ham param1 og', legend_label='ham param1 og', color='palevioletred',
                marker_style=(5, 1), marker_size=20, alpha=0.2 # Spec values
            )
        )

# Initialize with no data - this creates the global singleton instance in data_cubby
ham = ham_class(None)
print('initialized ham_class')

