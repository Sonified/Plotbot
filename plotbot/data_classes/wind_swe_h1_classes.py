# wind_swe_h1_classes.py - Calculates and stores WIND SWE H1 proton/alpha thermal speed variables

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging
import sys
from typing import Optional, List

from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
from plotbot.time_utils import TimeRangeTracker
from ._utils import _format_setattr_debug

# 🎉 Define the main class to calculate and store WIND SWE H1 proton/alpha thermal speed variables 🎉
class wind_swe_h1_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', 'wind_swe_h1')      # Internal Plotbot class identifier
        object.__setattr__(self, 'data_type', 'wind_swe_h1')      # Key for data_types
        object.__setattr__(self, 'subclass_name', None)           # For the main class instance
        object.__setattr__(self, 'raw_data', {
            'proton_wpar': None,        # Proton parallel thermal speed
            'proton_wperp': None,       # Proton perpendicular thermal speed
            'proton_anisotropy': None,  # Calculated: Wperp/Wpar
            'alpha_w': None,            # Alpha particle thermal speed
            'fit_flag': None,           # Data quality flag
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_current_operation_trange', None)

        print_manager.dependency_management(f"*** WIND_SWE_H1_CLASS_INIT (wind_swe_h1_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}. ***")

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_ploptions()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.dependency_management("Calculating WIND SWE H1 variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status("Successfully calculated WIND SWE H1 variables.")
    
    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None):
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        # Store the passed trange
        object.__setattr__(self, '_current_operation_trange', original_requested_trange)
        if original_requested_trange:
            print_manager.dependency_management(f"[WIND_SWE_H1_CLASS_UPDATE] Stored _current_operation_trange: {self._current_operation_trange}")
        else:
            print_manager.dependency_management(f"[WIND_SWE_H1_CLASS_UPDATE] original_requested_trange not provided or None.")

        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified ploptions)
        current_plot_states = {}
        standard_components = ['proton_wpar', 'proton_wperp', 'proton_anisotropy', 'alpha_w', 'fit_flag']
        for comp_name in standard_components:
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager) and hasattr(manager, '_plot_state'):
                    current_plot_states[comp_name] = dict(manager._plot_state)
                    print_manager.datacubby(f"Stored {comp_name} state: {retrieve_ploption_snapshot(current_plot_states[comp_name])}")

        # Perform update
        self.calculate_variables(imported_data)
        self.set_ploptions()
        
        # Restore state (including any modified ploptions!)
        print_manager.datacubby("Restoring saved state...")
        for comp_name, state in current_plot_states.items():
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager):
                    manager._plot_state.update(state)
                    for attr, value in state.items():
                        if hasattr(manager.plot_options, attr):
                            setattr(manager.plot_options, attr, value)
                    print_manager.datacubby(f"Restored {comp_name} state: {retrieve_ploption_snapshot(state)}")
        
        print_manager.datacubby("=== End Update Debug ===\n")
        
    def get_subclass(self, subclass_name):
        """
        Retrieves a specific data component (subclass) by its name.
        
        Args:
            subclass_name (str): The name of the component to retrieve.
            
        Returns:
            The requested component, or None if not found.
        """
        print_manager.dependency_management(f"[WIND_SWE_H1_CLASS_GET_SUBCLASS] Attempting to get subclass/property: {subclass_name} for instance ID: {id(self)}")

        # First, check if it's a direct attribute/property of the instance
        if hasattr(self, subclass_name):
            # 🚀 PERFORMANCE FIX: Only set requested_trange on the SPECIFIC subclass being requested
            current_trange = TimeRangeTracker.get_current_trange()
            if current_trange:
                try:
                    attr_value = getattr(self, subclass_name)
                    if isinstance(attr_value, plot_manager):
                        attr_value.requested_trange = current_trange
                except Exception:
                    pass
            # Verify it's not a private or dunder attribute unless explicitly intended
            if not subclass_name.startswith('_'): 
                retrieved_attr = getattr(self, subclass_name)
                print_manager.dependency_management(f"[WIND_SWE_H1_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a direct attribute/property. Type: {type(retrieved_attr)}")
                return retrieved_attr
            else:
                print_manager.dependency_management(f"[WIND_SWE_H1_CLASS_GET_SUBCLASS] '{subclass_name}' is an internal attribute, not returning via get_subclass.")
        
        # If not a direct attribute, check if it's a key in raw_data (original behavior for data components)
        if hasattr(self, 'raw_data') and self.raw_data and subclass_name in self.raw_data.keys():
            component = self.raw_data.get(subclass_name)
            print_manager.dependency_management(f"[WIND_SWE_H1_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a key in raw_data. Type: {type(component)}. This might be raw data.")
            return component

        # If not found as a direct attribute or in raw_data keys
        print_manager.warning(f"[WIND_SWE_H1_CLASS_GET_SUBCLASS] '{subclass_name}' is not a recognized subclass, property, or raw_data key for instance ID: {id(self)}.")
        available_attrs = [attr for attr in dir(self) if not attr.startswith('_') and not callable(getattr(self, attr))]
        available_raw_keys = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
        print_manager.dependency_management(f"[WIND_SWE_H1_CLASS_GET_SUBCLASS] Available properties/attributes: {available_attrs}")
        print_manager.dependency_management(f"[WIND_SWE_H1_CLASS_GET_SUBCLASS] Available raw_data keys: {available_raw_keys}")
        return None

    def __getattr__(self, name):
        # Allow direct access to dunder OR single underscore methods/attributes
        if name.startswith('_'):
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}' (raw_data not initialized)")
        print_manager.dependency_management('wind_swe_h1 getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []
        print(f"'{name}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {', '.join(available_attrs)}")
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.dependency_management(_format_setattr_debug(name, value))
        if name in ['datetime', 'datetime_array', 'raw_data', 'time'] or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            # Print friendly error message
            print_manager.dependency_management('wind_swe_h1 setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.dependency_management(f"Attempted to set unknown attribute: {name}")
    
    def calculate_variables(self, imported_data):
        """Calculate WIND SWE H1 proton/alpha thermal speed variables from imported CDF data."""
        print_manager.processing("WIND SWE H1: Starting calculate_variables...")

        if imported_data is None or not hasattr(imported_data, 'data') or imported_data.data is None:
            print_manager.warning("WIND SWE H1: No data available for calculation")
            return

        data = imported_data.data
        print_manager.processing(f"WIND SWE H1: Processing data with keys: {list(data.keys())}")

        # Store only TT2000 times as numpy array (following PSP pattern)
        if hasattr(imported_data, 'times') and imported_data.times is not None:
            self.time = np.asarray(imported_data.times)
            self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
            print_manager.dependency_management(f"self.datetime_array type after conversion: {type(self.datetime_array)}")
            print_manager.dependency_management(f"First element type: {type(self.datetime_array[0])}")
            print_manager.processing(f"WIND SWE H1: Processed {len(self.datetime_array)} time points")
        else:
            print_manager.warning("WIND SWE H1: No times data found in imported_data")
            return

        # Extract thermal speed and quality flag data
        proton_wpar_data = None
        proton_wperp_data = None
        alpha_w_data = None
        fit_flag_data = None

        # Process proton parallel thermal speed
        if 'Proton_Wpar_nonlin' in data:
            proton_wpar_data = data['Proton_Wpar_nonlin']
            print_manager.processing(f"WIND SWE H1: Proton_Wpar shape: {proton_wpar_data.shape}")
            print_manager.processing(f"WIND SWE H1: Proton_Wpar range: [{np.nanmin(proton_wpar_data):.2e}, {np.nanmax(proton_wpar_data):.2e}] km/s")
        else:
            print_manager.warning("WIND SWE H1: Proton_Wpar_nonlin not found in data")

        # Process proton perpendicular thermal speed
        if 'Proton_Wperp_nonlin' in data:
            proton_wperp_data = data['Proton_Wperp_nonlin']
            print_manager.processing(f"WIND SWE H1: Proton_Wperp shape: {proton_wperp_data.shape}")
            print_manager.processing(f"WIND SWE H1: Proton_Wperp range: [{np.nanmin(proton_wperp_data):.2e}, {np.nanmax(proton_wperp_data):.2e}] km/s")
        else:
            print_manager.warning("WIND SWE H1: Proton_Wperp_nonlin not found in data")

        # Process alpha particle thermal speed
        if 'Alpha_W_Nonlin' in data:
            alpha_w_data = data['Alpha_W_Nonlin']
            print_manager.processing(f"WIND SWE H1: Alpha_W shape: {alpha_w_data.shape}")
            print_manager.processing(f"WIND SWE H1: Alpha_W range: [{np.nanmin(alpha_w_data):.2e}, {np.nanmax(alpha_w_data):.2e}] km/s")
        else:
            print_manager.warning("WIND SWE H1: Alpha_W_Nonlin not found in data")

        # Process fit quality flag
        if 'fit_flag' in data:
            fit_flag_data = data['fit_flag']
            print_manager.processing(f"WIND SWE H1: fit_flag shape: {fit_flag_data.shape}")
            print_manager.processing(f"WIND SWE H1: fit_flag range: [{np.nanmin(fit_flag_data):.0f}, {np.nanmax(fit_flag_data):.0f}]")
            
            # Count flag values
            unique_flags, counts = np.unique(fit_flag_data[~np.isnan(fit_flag_data)], return_counts=True)
            print_manager.processing(f"WIND SWE H1: fit_flag distribution: {dict(zip(unique_flags, counts))}")
        else:
            print_manager.warning("WIND SWE H1: fit_flag not found in data")

        # =====================================================================================
        # ═══════════════════════ DATA QUALITY FILTERING SECTION ═══════════════════════
        # =====================================================================================
        # 
        # ⚠️  IMPORTANT: This is a MAJOR DEPARTURE from Plotbot's normal philosophy!
        # 
        # Plotbot typically follows a "take data and plot it" approach with minimal 
        # processing. However, WIND SWE H1 thermal speed data can contain quality issues
        # that may make raw data scientifically misleading, including:
        #
        # 1. Fill values (commonly 99,999.9 km/s) indicating missing/invalid measurements
        # 2. Quality flags (fit_flag) indicating analysis contingencies and fit quality
        # 3. Unphysical values outside reasonable thermal speed ranges
        #
        # Per WIND SWE documentation: "Data reported within this file do not exceed the 
        # limits of various parameters... There may be more valid data in the original
        # dataset that requires additional work to interpret but was discarded due to limits.
        # In particular we have tried to exclude non-solar wind data and questionable alpha
        # data from these files."
        #
        # Quality limits in original processing: max uncertainty 70%, max chi-squared 100,000,
        # minimum mach number 1.5, minimum distance to bow shock 5.0 Re.
        #
        # This filtering preserves scientific integrity while maintaining data transparency.
        #
        print_manager.processing("WIND SWE H1: ⚠️  Applying data quality filtering (departure from normal Plotbot)")
        print_manager.processing("WIND SWE H1: Filtering based on quality flags and physical limits")
        
        # === QUALITY FLAG FILTERING ===
        #From: https://cdaweb.gsfc.nasa.gov/misc/NotesW.html?utm_source=chatgpt.com#WI_H1_SWE
        # The fit_flag variable indicates analysis contingencies (WIND SWE documentation):
        # 10: Solar wind parameters OK -- no action necessary  
        # 9: Alpha particles relatively too cold
        # 8: Alpha particles overlap within protons in CDF
        # 7: Alphas too fast, out of SWE range
        # 6: Alpha particle peak may be confused with second proton peak
        # 5: Parameters OK, but Tp=Ta constraint used
        # 4: alphas are unusually cold, Tp=Ta constraint used
        # 3: alpha params relatively too hot, Tp=Ta constraint used
        # 2: The speed of the alpha is unusually low
        # 1: Poor peak identification
        # 0: Spectrum cannot be fit with a bimax model
        #
        # *** ADJUSTABLE PARAMETER: allowed_fit_flags ***
        # List of fit_flag values to accept. Modify based on your quality requirements:
        # Conservative (best quality): [10, 5]  
        # Moderate (accept some issues): [10, 9, 8, 7, 6, 5]
        # Permissive (accept most data): [10, 9, 8, 7, 6, 5, 4, 3, 2]
        allowed_fit_flags = [10, 9, 8, 7, 6, 5]  # Accept good data, some alpha issues OK
        
        quality_mask = None
        if fit_flag_data is not None:
            quality_mask = np.isin(fit_flag_data, allowed_fit_flags)
            bad_quality_count = np.sum(~quality_mask)
            kept_count = np.sum(quality_mask)
            print_manager.processing(f"WIND SWE H1: Accepted fit_flag values: {allowed_fit_flags}")
            print_manager.processing(f"WIND SWE H1: Kept {kept_count}/{len(fit_flag_data)} points, excluded {bad_quality_count}")
            
            # Show distribution of fit_flag values for transparency
            unique_flags, counts = np.unique(fit_flag_data, return_counts=True)
            flag_dist = dict(zip(unique_flags, counts))
            print_manager.processing(f"WIND SWE H1: fit_flag distribution in data: {flag_dist}")
        
        # === PHYSICAL LIMITS FILTERING ===
        # Remove fill values and unphysical measurements based on known solar wind physics:
        # - Typical proton thermal speeds: 10-100 km/s in solar wind
        # - Fill values in WIND data: 99,999.9 km/s (3x speed of light!)
        # - Zero/very low values: likely instrumental issues
        #
        # *** ADJUSTABLE PARAMETERS: thermal_speed_min, thermal_speed_max ***
        thermal_speed_min = 5.0    # km/s - Minimum realistic thermal speed. Increase to 10.0 for stricter filtering.
        thermal_speed_max = 1000.0 # km/s - Maximum realistic thermal speed. Decrease to 200.0 for stricter filtering.
        
        # Apply quality filtering to proton parallel thermal speed
        if proton_wpar_data is not None:
            # Physical limits filter: exclude fill values and unphysical speeds
            physical_mask = (proton_wpar_data >= thermal_speed_min) & (proton_wpar_data < thermal_speed_max)
            fill_count = np.sum(~physical_mask)
            print_manager.processing(f"WIND SWE H1: Excluded {fill_count} proton Wpar fill values/outliers (outside {thermal_speed_min}-{thermal_speed_max} km/s)")
            
            # Combine quality flag and physical limits filters
            if quality_mask is not None:
                combined_mask = quality_mask & physical_mask
                print_manager.processing(f"WIND SWE H1: Combined filtering kept {np.sum(combined_mask)}/{len(proton_wpar_data)} Wpar measurements")
            else:
                combined_mask = physical_mask
                print_manager.processing(f"WIND SWE H1: Physical filtering kept {np.sum(combined_mask)}/{len(proton_wpar_data)} Wpar measurements")
                
            # Apply filtering: replace bad data with NaN (preserves time grid)
            proton_wpar_data = np.where(combined_mask, proton_wpar_data, np.nan)
            print_manager.processing(f"WIND SWE H1: Proton Wpar filtered range: [{np.nanmin(proton_wpar_data):.1f}, {np.nanmax(proton_wpar_data):.1f}] km/s")
        
        # Apply same filtering to proton perpendicular thermal speed
        if proton_wperp_data is not None:
            # Physical limits filter: exclude fill values and unphysical speeds
            physical_mask = (proton_wperp_data >= thermal_speed_min) & (proton_wperp_data < thermal_speed_max)
            fill_count = np.sum(~physical_mask)
            print_manager.processing(f"WIND SWE H1: Excluded {fill_count} proton Wperp fill values/outliers (outside {thermal_speed_min}-{thermal_speed_max} km/s)")
            
            # Combine quality flag and physical limits filters
            if quality_mask is not None:
                combined_mask = quality_mask & physical_mask
                print_manager.processing(f"WIND SWE H1: Combined filtering kept {np.sum(combined_mask)}/{len(proton_wperp_data)} Wperp measurements")
            else:
                combined_mask = physical_mask
                print_manager.processing(f"WIND SWE H1: Physical filtering kept {np.sum(combined_mask)}/{len(proton_wperp_data)} Wperp measurements")
                
            # Apply filtering: replace bad data with NaN (preserves time grid)
            proton_wperp_data = np.where(combined_mask, proton_wperp_data, np.nan)
            print_manager.processing(f"WIND SWE H1: Proton Wperp filtered range: [{np.nanmin(proton_wperp_data):.1f}, {np.nanmax(proton_wperp_data):.1f}] km/s")

        # === ALPHA PARTICLE SPECIAL HANDLING ===
        # Alpha thermal speeds may be predominantly fill values in some time periods.
        # This section detects and handles high fill value fractions adaptively.
        #
        # *** ADJUSTABLE PARAMETER: fill_value_threshold ***
        fill_value_threshold = 0.9  # Fraction of fill values to trigger complete rejection. Lower to 0.5 for less strict.
        
        if alpha_w_data is not None:
            # Check what fraction of data are fill values (commonly 99,999.9 km/s)
            fill_mask = np.abs(alpha_w_data - 99999.9) < 0.1  # Allow 0.1 km/s tolerance for floating point comparison
            fill_fraction = np.sum(fill_mask) / len(alpha_w_data)
            print_manager.processing(f"WIND SWE H1: Alpha thermal speed fill value fraction: {fill_fraction:.1%}")
            
            if fill_fraction > fill_value_threshold:  # If >90% fill values by default
                print_manager.processing(f"WIND SWE H1: Alpha thermal speed is >{fill_value_threshold:.0%} fill values - setting all to NaN")
                alpha_w_data = np.full_like(alpha_w_data, np.nan)
            else:
                # Apply normal filtering if real data exists
                print_manager.processing("WIND SWE H1: Alpha thermal speed has real data - applying normal filtering")
                physical_mask = (alpha_w_data >= thermal_speed_min) & (alpha_w_data < thermal_speed_max)
                if quality_mask is not None:
                    combined_mask = quality_mask & physical_mask
                else:
                    combined_mask = physical_mask
                alpha_w_data = np.where(combined_mask, alpha_w_data, np.nan)
                print_manager.processing(f"WIND SWE H1: Alpha filtered range: [{np.nanmin(alpha_w_data):.1f}, {np.nanmax(alpha_w_data):.1f}] km/s")
        
        print_manager.processing("WIND SWE H1: ✅ Data quality filtering complete")
        # =====================================================================================
        # ═══════════════════════ END DATA QUALITY FILTERING ═══════════════════════════════
        # =====================================================================================

        # Calculate proton anisotropy (Wperp/Wpar) if both components available
        proton_anisotropy_data = None
        if proton_wpar_data is not None and proton_wperp_data is not None:
            # Avoid division by zero and use filtered data
            valid_mask = (~np.isnan(proton_wpar_data)) & (~np.isnan(proton_wperp_data)) & (proton_wpar_data != 0)
            proton_anisotropy_data = np.full_like(proton_wpar_data, np.nan)
            proton_anisotropy_data[valid_mask] = proton_wperp_data[valid_mask] / proton_wpar_data[valid_mask]
            
            print_manager.processing(f"WIND SWE H1: Calculated proton anisotropy (Wperp/Wpar)")
            print_manager.processing(f"WIND SWE H1: Anisotropy range: [{np.nanmin(proton_anisotropy_data):.3f}, {np.nanmax(proton_anisotropy_data):.3f}]")

        # Store data in raw_data dictionary
        self.raw_data = {
            'proton_wpar': proton_wpar_data,              # Proton parallel thermal speed
            'proton_wperp': proton_wperp_data,            # Proton perpendicular thermal speed
            'proton_anisotropy': proton_anisotropy_data,  # Calculated anisotropy
            'alpha_w': alpha_w_data,                      # Alpha thermal speed
            'fit_flag': fit_flag_data,                    # Quality flag
        }

        print_manager.processing("WIND SWE H1: Successfully calculated thermal speed variables")

        print_manager.dependency_management(f"\nDebug - Data Arrays:")
        print_manager.dependency_management(f"Time array shape: {self.time.shape}")
        for var_name, var_data in self.raw_data.items():
            if var_data is not None:
                print_manager.dependency_management(f"{var_name} data shape: {var_data.shape}")
            else:
                print_manager.dependency_management(f"{var_name}: None")
        print_manager.dependency_management(f"First TT2000 time: {self.time[0]}")

    def set_ploptions(self):
        """Set up plot_manager instances for all WIND SWE H1 variables."""
        print_manager.processing("WIND SWE H1: Setting up plot options...")

        # Proton parallel thermal speed (following PSP proton styling)
        self.proton_wpar = plot_manager(
            self.raw_data['proton_wpar'],
            plot_options=ploptions(
                data_type='wind_swe_h1',
                var_name='proton_wpar',
                class_name='wind_swe_h1',
                subclass_name='proton_wpar',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Thermal Speed\n(km/s)',
                legend_label=r'$W_{\parallel,p}$',
                color='deepskyblue',  # Following PSP proton t_par color
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Proton perpendicular thermal speed (following PSP proton styling)
        self.proton_wperp = plot_manager(
            self.raw_data['proton_wperp'],
            plot_options=ploptions(
                data_type='wind_swe_h1',
                var_name='proton_wperp',
                class_name='wind_swe_h1',
                subclass_name='proton_wperp',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Thermal Speed\n(km/s)',
                legend_label=r'$W_{\perp,p}$',
                color='hotpink',  # Following PSP proton t_perp color
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Proton anisotropy (following PSP proton anisotropy styling)
        self.proton_anisotropy = plot_manager(
            self.raw_data['proton_anisotropy'],
            plot_options=ploptions(
                data_type='wind_swe_h1',
                var_name='proton_anisotropy',
                class_name='wind_swe_h1',
                subclass_name='proton_anisotropy',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label=r'$W_{\perp}/W_{\parallel}$',
                legend_label=r'$W_{\perp}/W_{\parallel}$',
                color='mediumspringgreen',  # Following PSP proton anisotropy color
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Alpha particle thermal speed (new product type for WIND)
        self.alpha_w = plot_manager(
            self.raw_data['alpha_w'],
            plot_options=ploptions(
                data_type='wind_swe_h1',
                var_name='alpha_w',
                class_name='wind_swe_h1',
                subclass_name='alpha_w',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Alpha Thermal Speed\n(km/s)',
                legend_label=r'$W_{\alpha}$',
                color='darkorange',  # Distinct color for alpha particles
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Fit quality flag (integer values)
        self.fit_flag = plot_manager(
            self.raw_data['fit_flag'],
            plot_options=ploptions(
                data_type='wind_swe_h1',
                var_name='fit_flag',
                class_name='wind_swe_h1',
                subclass_name='fit_flag',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Fit Flag',
                legend_label='Data Quality',
                color='black',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        print_manager.processing("WIND SWE H1: Plot options initialized")

    def ensure_internal_consistency(self):
        """Ensure class instance is internally consistent."""
        print_manager.dependency_management("WIND SWE H1: Ensuring internal consistency...")
        
        # Check if raw_data exists and time arrays are consistent
        if hasattr(self, 'raw_data') and self.raw_data:
            for var_name, var_data in self.raw_data.items():
                if var_data is not None and hasattr(self, 'time'):
                    if len(var_data) != len(self.time):
                        print_manager.warning(f"WIND SWE H1: Length mismatch for {var_name}: data={len(var_data)}, time={len(self.time)}")
                        
        print_manager.dependency_management("WIND SWE H1: Internal consistency check complete")

    def restore_from_snapshot(self, snapshot_data):
        """Restore class from a data snapshot."""
        print_manager.dependency_management("WIND SWE H1: Restoring from snapshot...")
        
        if 'raw_data' in snapshot_data:
            self.raw_data = snapshot_data['raw_data']
        if 'datetime_array' in snapshot_data:
            self.datetime_array = snapshot_data['datetime_array']
        if 'time' in snapshot_data:
            self.time = snapshot_data['time']
            
        # Reinitialize plot options
        self.set_ploptions()
        
        print_manager.dependency_management("WIND SWE H1: Snapshot restoration complete")

# Create global instance for import
wind_swe_h1 = wind_swe_h1_class(None) 