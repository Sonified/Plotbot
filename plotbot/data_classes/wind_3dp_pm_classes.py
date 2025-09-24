# wind_3dp_pm_classes.py - Calculates and stores WIND 3DP plasma moment variables

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging
import sys
from typing import Optional, List

from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.plot_config import plot_config, retrieve_plot_config_snapshot
from plotbot.time_utils import TimeRangeTracker
from ._utils import _format_setattr_debug

# 🎉 Define the main class to calculate and store WIND 3DP PM ion plasma moment variables 🎉
class wind_3dp_pm_class:
    def __init__(self, imported_data):
        # First, set up the basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', 'wind_3dp_pm')      # Internal Plotbot class identifier
        object.__setattr__(self, 'data_type', 'wind_3dp_pm')      # Key for data_types
        object.__setattr__(self, 'subclass_name', None)           # For the main class instance
        object.__setattr__(self, 'raw_data', {
            'p_vels': None,      # Proton velocity vector [N, 3] - Vx, Vy, Vz in GSE
            'vx': None,          # X-component velocity (GSE)
            'vy': None,          # Y-component velocity (GSE)
            'vz': None,          # Z-component velocity (GSE)
            'v_mag': None,       # |V| velocity magnitude
            'all_v': None,       # All velocity components together
            'p_dens': None,      # Proton number density
            'p_temp': None,      # Proton temperature
            'a_dens': None,      # Alpha particle number density
            'a_temp': None,      # Alpha particle temperature
            'valid': None,       # Data quality flags
        })
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_current_operation_trange', None)

        print_manager.dependency_management(f"*** WIND_3DP_PM_CLASS_INIT (wind_3dp_pm_class) ID:{id(self)}: imported_data ID: {id(imported_data) if imported_data is not None else 'None'}. ***")

        if imported_data is None:
            # Set empty plotting options if imported_data is None (this is how we initialize the class)
            self.set_plot_config()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            # Initialize with data if provided - we're currently using update() method instead, but preserved for future extensibility
            print_manager.dependency_management("Calculating WIND 3DP PM variables...")
            self.calculate_variables(imported_data)
            self.set_plot_config()
            print_manager.status("Successfully calculated WIND 3DP PM variables.")
    
    def update(self, imported_data, original_requested_trange: Optional[List[str]] = None):
        """Method to update class with new data. 
        NOTE: This function updates the class with newly imported data. We need to use the data_cubby
        as a registry to store class instances in order to avoid circular references that would occur
        if the class stored itself as an attribute and tried to reference itself directly. The code breaks without the cubby!"""
        # Store the passed trange
        object.__setattr__(self, '_current_operation_trange', original_requested_trange)
        if original_requested_trange:
            print_manager.dependency_management(f"[WIND_3DP_PM_CLASS_UPDATE] Stored _current_operation_trange: {self._current_operation_trange}")
        else:
            print_manager.dependency_management(f"[WIND_3DP_PM_CLASS_UPDATE] original_requested_trange not provided or None.")

        if imported_data is None:
            print_manager.datacubby(f"No data provided for {self.__class__.__name__} update.")
            return
        
        print_manager.datacubby("\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {self.__class__.__name__} update...")
        
        # Store current state before update (including any modified plot_config)
        current_plot_states = {}
        standard_components = ['p_vels', 'vx', 'vy', 'vz', 'v_mag', 'all_v', 'p_dens', 'p_temp', 'a_dens', 'a_temp', 'valid']
        for comp_name in standard_components:
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager) and hasattr(manager, '_plot_state'):
                    current_plot_states[comp_name] = dict(manager._plot_state)
                    print_manager.datacubby(f"Stored {comp_name} state: {retrieve_plot_config_snapshot(current_plot_states[comp_name])}")

        # Perform update
        self.calculate_variables(imported_data)
        self.set_plot_config()
        
        # Restore state (including any modified plot_config!)
        print_manager.datacubby("Restoring saved state...")
        for comp_name, state in current_plot_states.items():
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager):
                    manager._plot_state.update(state)
                    for attr, value in state.items():
                        if hasattr(manager.plot_config, attr):
                            setattr(manager.plot_config, attr, value)
                    print_manager.datacubby(f"Restored {comp_name} state: {retrieve_plot_config_snapshot(state)}")
        
        print_manager.datacubby("=== End Update Debug ===\n")
        
    def get_subclass(self, subclass_name):
        """
        Retrieves a specific data component (subclass) by its name.
        
        Args:
            subclass_name (str): The name of the component to retrieve.
            
        Returns:
            The requested component, or None if not found.
        """
        print_manager.dependency_management(f"[WIND_3DP_PM_CLASS_GET_SUBCLASS] Attempting to get subclass/property: {subclass_name} for instance ID: {id(self)}")

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
                print_manager.dependency_management(f"[WIND_3DP_PM_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a direct attribute/property. Type: {type(retrieved_attr)}")
                return retrieved_attr
            else:
                print_manager.dependency_management(f"[WIND_3DP_PM_CLASS_GET_SUBCLASS] '{subclass_name}' is an internal attribute, not returning via get_subclass.")
        
        # If not a direct attribute, check if it's a key in raw_data (original behavior for data components)
        if hasattr(self, 'raw_data') and self.raw_data and subclass_name in self.raw_data.keys():
            component = self.raw_data.get(subclass_name)
            print_manager.dependency_management(f"[WIND_3DP_PM_CLASS_GET_SUBCLASS] Found '{subclass_name}' as a key in raw_data. Type: {type(component)}. This might be raw data.")
            return component

        # If not found as a direct attribute or in raw_data keys
        print_manager.warning(f"[WIND_3DP_PM_CLASS_GET_SUBCLASS] '{subclass_name}' is not a recognized subclass, property, or raw_data key for instance ID: {id(self)}.")
        available_attrs = [attr for attr in dir(self) if not attr.startswith('_') and not callable(getattr(self, attr))]
        available_raw_keys = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
        print_manager.dependency_management(f"[WIND_3DP_PM_CLASS_GET_SUBCLASS] Available properties/attributes: {available_attrs}")
        print_manager.dependency_management(f"[WIND_3DP_PM_CLASS_GET_SUBCLASS] Available raw_data keys: {available_raw_keys}")
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
        print_manager.dependency_management('wind_3dp_pm getattr helper!')
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
            print_manager.dependency_management('wind_3dp_pm setattr helper!')
            print(f"'{name}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {', '.join(available_attrs)}")
            print_manager.dependency_management(f"Attempted to set unknown attribute: {name}")
    
    def calculate_variables(self, imported_data):
        """Calculate WIND 3DP PM plasma moment variables from imported CDF data."""
        print_manager.processing("WIND 3DP PM: Starting calculate_variables...")

        if imported_data is None or not hasattr(imported_data, 'data') or imported_data.data is None:
            print_manager.warning("WIND 3DP PM: No data available for calculation")
            return

        data = imported_data.data
        print_manager.processing(f"WIND 3DP PM: Processing data with keys: {list(data.keys())}")

        # Store only TT2000 times as numpy array (following PSP pattern)
        if hasattr(imported_data, 'times') and imported_data.times is not None:
            self.time = np.asarray(imported_data.times)
            self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
            print_manager.dependency_management(f"self.datetime_array type after conversion: {type(self.datetime_array)}")
            print_manager.dependency_management(f"First element type: {type(self.datetime_array[0])}")
            print_manager.processing(f"WIND 3DP PM: Processed {len(self.datetime_array)} time points")
        else:
            print_manager.warning("WIND 3DP PM: No times data found in imported_data")
            return

        # Initialize variables to None
        p_vels_data = None
        p_dens_data = None
        p_temp_data = None
        a_dens_data = None
        a_temp_data = None
        valid_data = None

        # Process proton velocity vector P_VELS [N, 3] - Vx, Vy, Vz in GSE coordinates
        if 'P_VELS' in data:
            p_vels_data = data['P_VELS']  # [N, 3] array
            print_manager.processing(f"WIND 3DP PM: P_VELS shape: {p_vels_data.shape}")
            print_manager.processing(f"WIND 3DP PM: P_VELS range: [{np.nanmin(p_vels_data):.2f}, {np.nanmax(p_vels_data):.2f}] km/s")
        else:
            print_manager.warning("WIND 3DP PM: P_VELS not found in data")

        # Process proton density
        if 'P_DENS' in data:
            p_dens_data = data['P_DENS']
            print_manager.processing(f"WIND 3DP PM: P_DENS shape: {p_dens_data.shape}")
            print_manager.processing(f"WIND 3DP PM: P_DENS range: [{np.nanmin(p_dens_data):.2e}, {np.nanmax(p_dens_data):.2e}] cm⁻³")
        else:
            print_manager.warning("WIND 3DP PM: P_DENS not found in data")

        # Process proton temperature
        if 'P_TEMP' in data:
            p_temp_data = data['P_TEMP']
            print_manager.processing(f"WIND 3DP PM: P_TEMP shape: {p_temp_data.shape}")
            print_manager.processing(f"WIND 3DP PM: P_TEMP range: [{np.nanmin(p_temp_data):.2e}, {np.nanmax(p_temp_data):.2e}] eV")
        else:
            print_manager.warning("WIND 3DP PM: P_TEMP not found in data")

        # Process alpha particle density
        if 'A_DENS' in data:
            a_dens_data = data['A_DENS']
            print_manager.processing(f"WIND 3DP PM: A_DENS shape: {a_dens_data.shape}")
            print_manager.processing(f"WIND 3DP PM: A_DENS range: [{np.nanmin(a_dens_data):.2e}, {np.nanmax(a_dens_data):.2e}] cm⁻³")
        else:
            print_manager.warning("WIND 3DP PM: A_DENS not found in data")

        # Process alpha particle temperature
        if 'A_TEMP' in data:
            a_temp_data = data['A_TEMP']
            print_manager.processing(f"WIND 3DP PM: A_TEMP shape: {a_temp_data.shape}")
            print_manager.processing(f"WIND 3DP PM: A_TEMP range: [{np.nanmin(a_temp_data):.2e}, {np.nanmax(a_temp_data):.2e}] eV")
        else:
            print_manager.warning("WIND 3DP PM: A_TEMP not found in data")

        # Process quality flags
        if 'VALID' in data:
            valid_data = data['VALID']
            print_manager.processing(f"WIND 3DP PM: VALID shape: {valid_data.shape}")
            print_manager.processing(f"WIND 3DP PM: VALID range: [{np.nanmin(valid_data):.0f}, {np.nanmax(valid_data):.0f}]")
            
            # Count flag values
            unique_flags, counts = np.unique(valid_data[~np.isnan(valid_data)], return_counts=True)
            print_manager.processing(f"WIND 3DP PM: VALID flag distribution: {dict(zip(unique_flags, counts))}")
        else:
            print_manager.warning("WIND 3DP PM: VALID not found in data")

        # =====================================================================================
        # ═══════════════════════ VELOCITY COMPONENT EXTRACTION ═══════════════════════════
        # =====================================================================================
        # Extract individual velocity components from P_VELS vector and calculate magnitude
        vx_data = None
        vy_data = None 
        vz_data = None
        v_mag_data = None

        if p_vels_data is not None:
            if p_vels_data.ndim == 2 and p_vels_data.shape[1] == 3:
                # Extract components from [N, 3] velocity vector
                vx_data = p_vels_data[:, 0]  # X-component (GSE)
                vy_data = p_vels_data[:, 1]  # Y-component (GSE)
                vz_data = p_vels_data[:, 2]  # Z-component (GSE)
                
                # Calculate velocity magnitude
                v_mag_data = np.sqrt(vx_data**2 + vy_data**2 + vz_data**2)
                
                print_manager.processing("WIND 3DP PM: Successfully extracted velocity components")
                print_manager.processing(f"WIND 3DP PM: Vx range: [{np.nanmin(vx_data):.2f}, {np.nanmax(vx_data):.2f}] km/s")
                print_manager.processing(f"WIND 3DP PM: Vy range: [{np.nanmin(vy_data):.2f}, {np.nanmax(vy_data):.2f}] km/s") 
                print_manager.processing(f"WIND 3DP PM: Vz range: [{np.nanmin(vz_data):.2f}, {np.nanmax(vz_data):.2f}] km/s")
                print_manager.processing(f"WIND 3DP PM: |V| range: [{np.nanmin(v_mag_data):.2f}, {np.nanmax(v_mag_data):.2f}] km/s")
            else:
                print_manager.warning(f"WIND 3DP PM: P_VELS has unexpected shape: {p_vels_data.shape}, expected [N, 3]")

        # =====================================================================================
        # ═══════════════════════ DATA QUALITY FILTERING SECTION (DISABLED) ═══════════════════════
        # =====================================================================================
        # NOTE: This section has been temporarily disabled to inspect raw data values due to a 
        # lack of metadata in the source CDF files. It will be re-enabled after baseline
        # data validation is complete.
        
        # ⚠️  WIND 3DP PM Quality Filtering Philosophy
        # 
        # Following the pattern established in WIND SWE H1, we apply basic quality filtering
        # for WIND 3DP PM data. The VALID flag indicates measurement quality and should be
        # used to filter out problematic data points.
        #
        # From WIND 3DP documentation, the VALID flag typically indicates:
        # - Data quality and measurement reliability
        # - Instrument operational status
        # - Physical reasonableness of measurements
        #
        # *** ADJUSTABLE PARAMETER: valid_quality_threshold ***
        # Minimum VALID flag value to accept. Modify based on quality requirements:
        # valid_quality_threshold = 1  # Accept VALID >= 1 (reject 0 which often means bad data)
        
        # quality_mask = None
        # if valid_data is not None:
        #     quality_mask = valid_data >= valid_quality_threshold
        #     bad_quality_count = np.sum(~quality_mask)
        #     kept_count = np.sum(quality_mask)
        #     print_manager.processing(f"WIND 3DP PM: Quality filtering with VALID >= {valid_quality_threshold}")
        #     print_manager.processing(f"WIND 3DP PM: Kept {kept_count}/{len(valid_data)} points, excluded {bad_quality_count}")
        
        # # *** ADJUSTABLE PARAMETERS: Physical limits for ion plasma moments ***
        # # Reasonable ranges for solar wind ion measurements at 1 AU:
        # density_min = 0.1      # cm⁻³ - Minimum reasonable ion density
        # density_max = 1000.0   # cm⁻³ - Maximum reasonable ion density  
        # velocity_min = 200.0   # km/s - Minimum reasonable solar wind speed
        # velocity_max = 1000.0  # km/s - Maximum reasonable solar wind speed
        # proton_temp_min = 1.0    # eV - Minimum reasonable proton temperature
        # proton_temp_max = 100.0  # eV - Maximum reasonable proton temperature
        # alpha_temp_min = 1.0     # eV - Minimum reasonable alpha temperature
        # alpha_temp_max = 500.0   # eV - Maximum reasonable alpha temperature
        
        # # Apply quality filtering to proton density
        # if p_dens_data is not None:
        #     # Physical limits filter: exclude unphysical densities
        #     physical_mask = (p_dens_data >= density_min) & (p_dens_data <= density_max)
        #     fill_count = np.sum(~physical_mask)
        #     print_manager.processing(f"WIND 3DP PM: Excluded {fill_count} P_DENS outliers (outside {density_min}-{density_max} cm⁻³)")
            
        #     # Combine quality flag and physical limits filters
        #     if quality_mask is not None:
        #         combined_mask = quality_mask & physical_mask
        #         print_manager.processing(f"WIND 3DP PM: Combined filtering kept {np.sum(combined_mask)}/{len(p_dens_data)} P_DENS measurements")
        #     else:
        #         combined_mask = physical_mask
        #         print_manager.processing(f"WIND 3DP PM: Physical filtering kept {np.sum(combined_mask)}/{len(p_dens_data)} P_DENS measurements")
                
        #     # Apply filtering: replace bad data with NaN (preserves time grid)
        #     p_dens_data = np.where(combined_mask, p_dens_data, np.nan)
        #     print_manager.processing(f"WIND 3DP PM: P_DENS filtered range: [{np.nanmin(p_dens_data):.3f}, {np.nanmax(p_dens_data):.3f}] cm⁻³")

        # # Apply quality filtering to proton temperature
        # if p_temp_data is not None:
        #     # Physical limits filter: exclude unphysical temperatures
        #     physical_mask = (p_temp_data >= proton_temp_min) & (p_temp_data <= proton_temp_max)
        #     fill_count = np.sum(~physical_mask)
        #     print_manager.processing(f"WIND 3DP PM: Excluded {fill_count} P_TEMP outliers (outside {proton_temp_min}-{proton_temp_max} eV)")
            
        #     # Combine quality flag and physical limits filters
        #     if quality_mask is not None:
        #         combined_mask = quality_mask & physical_mask
        #         print_manager.processing(f"WIND 3DP PM: Combined filtering kept {np.sum(combined_mask)}/{len(p_temp_data)} P_TEMP measurements")
        #     else:
        #         combined_mask = physical_mask
        #         print_manager.processing(f"WIND 3DP PM: Physical filtering kept {np.sum(combined_mask)}/{len(p_temp_data)} P_TEMP measurements")
                
        #     # Apply filtering: replace bad data with NaN (preserves time grid)
        #     p_temp_data = np.where(combined_mask, p_temp_data, np.nan)
        #     print_manager.processing(f"WIND 3DP PM: P_TEMP filtered range: [{np.nanmin(p_temp_data):.3f}, {np.nanmax(p_temp_data):.3f}] eV")

        # # Apply quality filtering to velocity components
        # if vx_data is not None and vy_data is not None and vz_data is not None and v_mag_data is not None:
        #     # Physical limits filter: exclude unphysical velocities based on magnitude
        #     physical_mask = (v_mag_data >= velocity_min) & (v_mag_data <= velocity_max)
        #     fill_count = np.sum(~physical_mask)
        #     print_manager.processing(f"WIND 3DP PM: Excluded {fill_count} velocity outliers (|V| outside {velocity_min}-{velocity_max} km/s)")
            
        #     # Combine quality flag and physical limits filters
        #     if quality_mask is not None:
        #         combined_mask = quality_mask & physical_mask
        #         print_manager.processing(f"WIND 3DP PM: Combined filtering kept {np.sum(combined_mask)}/{len(v_mag_data)} velocity measurements")
        #     else:
        #         combined_mask = physical_mask
        #         print_manager.processing(f"WIND 3DP PM: Physical filtering kept {np.sum(combined_mask)}/{len(v_mag_data)} velocity measurements")
                
        #     # Apply filtering to all velocity components
        #     vx_data = np.where(combined_mask, vx_data, np.nan)
        #     vy_data = np.where(combined_mask, vy_data, np.nan)
        #     vz_data = np.where(combined_mask, vz_data, np.nan)
        #     v_mag_data = np.where(combined_mask, v_mag_data, np.nan)
            
        #     # Also apply to full velocity vector
        #     if p_vels_data is not None:
        #         for i in range(3):  # Apply mask to each component of the vector
        #             p_vels_data[:, i] = np.where(combined_mask, p_vels_data[:, i], np.nan)
            
        #     print_manager.processing(f"WIND 3DP PM: Velocity filtered ranges:")
        #     print_manager.processing(f"WIND 3DP PM: Vx: [{np.nanmin(vx_data):.1f}, {np.nanmax(vx_data):.1f}] km/s")
        #     print_manager.processing(f"WIND 3DP PM: Vy: [{np.nanmin(vy_data):.1f}, {np.nanmax(vy_data):.1f}] km/s")
        #     print_manager.processing(f"WIND 3DP PM: Vz: [{np.nanmin(vz_data):.1f}, {np.nanmax(vz_data):.1f}] km/s")
        #     print_manager.processing(f"WIND 3DP PM: |V|: [{np.nanmin(v_mag_data):.1f}, {np.nanmax(v_mag_data):.1f}] km/s")

        # # Apply same filtering to alpha particle data (more permissive due to lower signal-to-noise)
        # alpha_density_min = 0.01   # cm⁻³ - Lower threshold for alpha particles
        # alpha_density_max = 100.0  # cm⁻³ - Alpha density typically < proton density
        
        # if a_dens_data is not None:
        #     # Check for high fill value fraction (alpha particles often have poor data quality)
        #     fill_mask = (a_dens_data <= alpha_density_min) | (a_dens_data >= alpha_density_max)
        #     fill_fraction = np.sum(fill_mask) / len(a_dens_data)
        #     print_manager.processing(f"WIND 3DP PM: Alpha density unphysical fraction: {fill_fraction:.1%}")
            
        #     if fill_fraction > 0.8:  # If >80% unphysical values
        #         print_manager.processing(f"WIND 3DP PM: Alpha density is >{0.8:.0%} unphysical - setting all to NaN")
        #         a_dens_data = np.full_like(a_dens_data, np.nan)
        #     else:
        #         # Apply normal filtering
        #         physical_mask = (a_dens_data >= alpha_density_min) & (a_dens_data <= alpha_density_max)
        #         if quality_mask is not None:
        #             combined_mask = quality_mask & physical_mask
        #         else:
        #             combined_mask = physical_mask
        #         a_dens_data = np.where(combined_mask, a_dens_data, np.nan)
        #         print_manager.processing(f"WIND 3DP PM: Alpha density filtered range: [{np.nanmin(a_dens_data):.3f}, {np.nanmax(a_dens_data):.3f}] cm⁻³")
        
        # if a_temp_data is not None:
        #     # Same approach for alpha temperature
        #     physical_mask = (a_temp_data >= alpha_temp_min) & (a_temp_data <= alpha_temp_max)
        #     fill_fraction = np.sum(~physical_mask) / len(a_temp_data)
        #     print_manager.processing(f"WIND 3DP PM: Alpha temperature unphysical fraction: {fill_fraction:.1%}")
            
        #     if fill_fraction > 0.8:  # If >80% unphysical values
        #         print_manager.processing(f"WIND 3DP PM: Alpha temperature is >{0.8:.0%} unphysical - setting all to NaN")
        #         a_temp_data = np.full_like(a_temp_data, np.nan)
        #     else:
        #         if quality_mask is not None:
        #             combined_mask = quality_mask & physical_mask
        #         else:
        #             combined_mask = physical_mask
        #         a_temp_data = np.where(combined_mask, a_temp_data, np.nan)
        #         print_manager.processing(f"WIND 3DP PM: Alpha temperature filtered range: [{np.nanmin(a_temp_data):.0f}, {np.nanmax(a_temp_data):.0f}] eV")

        # print_manager.processing("WIND 3DP PM: ✅ Data quality filtering complete")
        # # =====================================================================================
        # # ═══════════════════════ END DATA QUALITY FILTERING ═══════════════════════════════
        # # =====================================================================================

        # Store all data in raw_data dictionary
        self.raw_data = {
            'p_vels': p_vels_data,         # Full velocity vector [N, 3]
            'vx': vx_data,                 # X-component velocity
            'vy': vy_data,                 # Y-component velocity  
            'vz': vz_data,                 # Z-component velocity
            'v_mag': v_mag_data,           # Velocity magnitude
            'all_v': [vx_data, vy_data, vz_data] if all(v is not None for v in [vx_data, vy_data, vz_data]) else None,  # All components for multi-line plotting
            'p_dens': p_dens_data,         # Proton density
            'p_temp': p_temp_data,         # Proton temperature  
            'a_dens': a_dens_data,         # Alpha density
            'a_temp': a_temp_data,         # Alpha temperature
            'valid': valid_data,           # Quality flags
        }

        print_manager.processing("WIND 3DP PM: Successfully calculated plasma moment variables")

        print_manager.dependency_management(f"\nDebug - Data Arrays:")
        print_manager.dependency_management(f"Time array shape: {self.time.shape}")
        for var_name, var_data in self.raw_data.items():
            if var_data is not None:
                if hasattr(var_data, 'shape'):
                    print_manager.dependency_management(f"{var_name} data shape: {var_data.shape}")
                else:
                    print_manager.dependency_management(f"{var_name}: {type(var_data)}")
            else:
                print_manager.dependency_management(f"{var_name}: None")
        print_manager.dependency_management(f"First TT2000 time: {self.time[0]}")

    def set_plot_config(self):
        """Set up plot_manager instances for all WIND 3DP PM variables (following PSP proton styling patterns)."""
        print_manager.processing("WIND 3DP PM: Setting up plot options...")

        # === VELOCITY COMPONENTS (Following PSP proton vr/vt/vn styling) ===
        
        # All velocity components together (following PSP pattern)
        self.all_v = plot_manager(
            self.raw_data['all_v'],
            plot_config=plot_config(
                data_type='wind_3dp_pm',
                var_name=['vx_gse', 'vy_gse', 'vz_gse'],
                class_name='wind_3dp_pm',
                subclass_name='all_v',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Velocity (km/s)',
                legend_label=['$V_X$ (GSE)', '$V_Y$ (GSE)', '$V_Z$ (GSE)'],
                color=['red', 'green', 'blue'],  # Following PSP vr/vt/vn color scheme
                y_scale='linear',
                y_limit=None,
                line_width=[1, 1, 1],
                line_style=['-', '-', '-']
            )
        )

        # Individual velocity components (following PSP styling)
        self.vx = plot_manager(
            self.raw_data['vx'],
            plot_config=plot_config(
                data_type='wind_3dp_pm',
                var_name='vx_gse',
                class_name='wind_3dp_pm',
                subclass_name='vx',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$V_X$ (km/s)',
                legend_label='$V_X$ (GSE)',
                color='red',    # Following PSP vr color
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.vy = plot_manager(
            self.raw_data['vy'],
            plot_config=plot_config(
                data_type='wind_3dp_pm',
                var_name='vy_gse',
                class_name='wind_3dp_pm',
                subclass_name='vy',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$V_Y$ (km/s)',
                legend_label='$V_Y$ (GSE)',
                color='green',  # Following PSP vt color
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        self.vz = plot_manager(
            self.raw_data['vz'],
            plot_config=plot_config(
                data_type='wind_3dp_pm',
                var_name='vz_gse',
                class_name='wind_3dp_pm',
                subclass_name='vz',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$V_Z$ (km/s)',
                legend_label='$V_Z$ (GSE)',
                color='blue',   # Following PSP vn color
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Velocity magnitude
        self.v_mag = plot_manager(
            self.raw_data['v_mag'],
            plot_config=plot_config(
                data_type='wind_3dp_pm',
                var_name='v_mag',
                class_name='wind_3dp_pm',
                subclass_name='v_mag',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='$|V|$ (km/s)',
                legend_label='$|V|$',
                color='black',  # Following PSP v_sw style
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Full velocity vector (for advanced use)
        self.p_vels = plot_manager(
            self.raw_data['p_vels'],
            plot_config=plot_config(
                data_type='wind_3dp_pm',
                var_name='p_vels_vector',
                class_name='wind_3dp_pm',
                subclass_name='p_vels',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Velocity Vector',
                legend_label='P_VELS [Vx,Vy,Vz]',
                color='purple',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # === PROTON BASIC PARAMETERS (Following PSP proton styling) ===
        
        # Proton density (following PSP proton.density styling)
        self.p_dens = plot_manager(
            self.raw_data['p_dens'],
            plot_config=plot_config(
                data_type='wind_3dp_pm',
                var_name='p_dens',
                class_name='wind_3dp_pm',
                subclass_name='p_dens',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Density\n(cm$^{-3}$)',
                legend_label='$n_p$ (3DP)',
                color='blue',     # Following PSP proton density color
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Proton temperature (following PSP proton.temperature styling)
        self.p_temp = plot_manager(
            self.raw_data['p_temp'],
            plot_config=plot_config(
                data_type='wind_3dp_pm',
                var_name='p_temp',
                class_name='wind_3dp_pm',
                subclass_name='p_temp',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Temperature (eV)',
                legend_label='$T_p$ (3DP)',
                color='magenta',  # Following PSP proton temperature color
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # === ALPHA PARTICLE PARAMETERS (New styling for WIND-specific products) ===
        
        # Alpha particle density (new product type)
        self.a_dens = plot_manager(
            self.raw_data['a_dens'],
            plot_config=plot_config(
                data_type='wind_3dp_pm',
                var_name='a_dens',
                class_name='wind_3dp_pm',
                subclass_name='a_dens',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Alpha Density\n(cm$^{-3}$)',
                legend_label='$n_{\\alpha}$ (3DP)',
                color='darkorange',  # Distinct color for alpha density
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # Alpha particle temperature (new product type)
        self.a_temp = plot_manager(
            self.raw_data['a_temp'],
            plot_config=plot_config(
                data_type='wind_3dp_pm',
                var_name='a_temp',
                class_name='wind_3dp_pm',
                subclass_name='a_temp',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Alpha Temperature (eV)',
                legend_label='$T_{\\alpha}$ (3DP)',
                color='firebrick',  # Distinct color for alpha temperature
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        # === QUALITY FLAGS ===
        
        # Data quality flags (integer values)
        self.valid = plot_manager(
            self.raw_data['valid'],
            plot_config=plot_config(
                data_type='wind_3dp_pm',
                var_name='valid',
                class_name='wind_3dp_pm',
                subclass_name='valid',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='Quality Flag',
                legend_label='Data Valid',
                color='black',
                y_scale='linear',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )

        print_manager.processing("WIND 3DP PM: Plot options initialized with PSP-compatible styling")

    def ensure_internal_consistency(self):
        """Ensure class instance is internally consistent."""
        print_manager.dependency_management("WIND 3DP PM: Ensuring internal consistency...")
        
        # Check if raw_data exists and time arrays are consistent
        if hasattr(self, 'raw_data') and self.raw_data:
            for var_name, var_data in self.raw_data.items():
                if var_data is not None and hasattr(self, 'time'):
                    if var_name == 'all_v':  # Skip list of arrays
                        continue
                    elif var_name == 'p_vels' and hasattr(var_data, 'shape') and var_data.ndim == 2:
                        # Check 2D velocity vector
                        if var_data.shape[0] != len(self.time):
                            print_manager.warning(f"WIND 3DP PM: Length mismatch for {var_name}: data={var_data.shape[0]}, time={len(self.time)}")
                    elif hasattr(var_data, '__len__') and len(var_data) != len(self.time):
                        print_manager.warning(f"WIND 3DP PM: Length mismatch for {var_name}: data={len(var_data)}, time={len(self.time)}")
                        
        print_manager.dependency_management("WIND 3DP PM: Internal consistency check complete")

    def restore_from_snapshot(self, snapshot_data):
        """Restore class from a data snapshot."""
        print_manager.dependency_management("WIND 3DP PM: Restoring from snapshot...")
        
        if 'raw_data' in snapshot_data:
            self.raw_data = snapshot_data['raw_data']
        if 'datetime_array' in snapshot_data:
            self.datetime_array = snapshot_data['datetime_array']
        if 'time' in snapshot_data:
            self.time = snapshot_data['time']
            
        # Reinitialize plot options
        self.set_plot_config()
        
        print_manager.dependency_management("WIND 3DP PM: Snapshot restoration complete")

# Create global instance for import
wind_3dp_pm = wind_3dp_pm_class(None) 