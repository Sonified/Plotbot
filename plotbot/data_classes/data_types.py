#plotbot/data_classes/data_types.py

import os

# CONFIGURATION: Data Types, Defines all available data products for multiple missions
#====================================================================
data_types = {
    'mag_RTN': {
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/mag_RTN/',  # URL for data source
        'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'mag_rtn'),  # Local path for storing data
        'password_type': 'mag',  # Type of password required
        'file_pattern': r'psp_fld_{data_level}_mag_RTN_{date_hour_str}_v(\d{{2}})\.cdf',  # Regex pattern for file names
        'file_pattern_import': r'psp_fld_{data_level}_mag_RTN_{date_hour_str}_v*.cdf',  # Regex pattern for importing files
        'data_level': 'l2',  # Data level
        'file_time_format': '6-hour',  # Time format of the files
        'data_vars': ['psp_fld_l2_mag_RTN'],  # Variables to import
    },
    'mag_RTN_4sa': {
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/mag_RTN_4_Sa_per_Cyc/',
        'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'mag_rtn_4_per_cycle'),
        'password_type': 'mag',
        'file_pattern': r'psp_fld_{data_level}_mag_RTN_4_Sa_per_Cyc_{date_str}_v(\d{{2}})\.cdf',      # Added this
        'file_pattern_import': r'psp_fld_{data_level}_mag_RTN_4_Sa_per_Cyc_{date_str}_v*.cdf',  # Fixed case to match actual files
        'spdf_file_pattern': r'psp_fld_{data_level}_mag_rtn_4_sa_per_cyc_{date_str}_v*.cdf',    # SPDF case (lowercase)
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': ['psp_fld_l2_mag_RTN_4_Sa_per_Cyc'],
    },
    'mag_SC': {
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/mag_SC/',
        'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'mag_sc'),
        'password_type': 'mag',
        'file_pattern': r'psp_fld_{data_level}_mag_SC_{date_hour_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_fld_{data_level}_mag_SC_{date_hour_str}_v*.cdf',
        'data_level': 'l2',
        'file_time_format': '6-hour',
        'data_vars': ['psp_fld_l2_mag_SC'],
    },
    'mag_SC_4sa': {
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/mag_SC_4_Sa_per_Cyc/',
        'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'mag_sc_4_per_cycle'),
        'password_type': 'mag',
        'file_pattern': r'psp_fld_{data_level}_mag_SC_4_Sa_per_Cyc_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_fld_{data_level}_mag_SC_4_Sa_per_Cyc_{date_str}_v*.cdf',
        'spdf_file_pattern': r'psp_fld_{data_level}_mag_sc_4_sa_per_cyc_{date_str}_v*.cdf',   # SPDF case (lowercase)
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': ['psp_fld_l2_mag_SC_4_Sa_per_Cyc'],
    },
    'sqtn_rfs_v1v2': {  # QTN (Quasi-Thermal Noise) data
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/sqtn_rfs_V1V2/',  # Berkeley uses uppercase URL
        'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'sqtn_rfs_v1v2'),
        'password_type': 'mag',  # FIELDS instrument uses mag password type
        'file_pattern': r'psp_fld_{data_level}_sqtn_rfs_V1V2_{date_str}_v(\d{{2}})\.cdf',  # Berkeley uses uppercase
        'file_pattern_import': r'psp_fld_{data_level}_sqtn_rfs_V1V2_{date_str}_v*.cdf',   # Berkeley uses uppercase
        'spdf_file_pattern': r'psp_fld_{data_level}_sqtn_rfs_v1v2_{date_str}_v*.cdf',   # SPDF uses lowercase
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': ['electron_density', 'electron_core_temperature'],  # Primary QTN variables
    },
    'spe_sf0_pad': {  # Electron data
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spe/L3/spe_sf0_pad/',
        'local_path': os.path.join('data', 'psp', 'sweap', 'spe', 'l3', 'spe_sf0_pad'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spe_sf0_L3_pad_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_swp_spe_sf0_L3_pad_{date_str}_v*.cdf',
        'spdf_file_pattern': r'psp_swp_spe_sf0_l3_pad_{date_str}_v*.cdf',   # SPDF case (lowercase l3)
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': ['EFLUX_VS_PA_E', 'PITCHANGLE'],
    },
    'spe_af0_pad': {  # High-resolution electron data
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spe/L3/spe_af0_pad/',
        'local_path': os.path.join('data', 'psp', 'sweap', 'spe', 'l3', 'spe_af0_pad'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spe_af0_L3_pad_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_swp_spe_af0_L3_pad_{date_str}_v*.cdf',
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': ['EFLUX_VS_PA_E', 'PITCHANGLE'],
    },
    'spi_sf00_l3_mom': {  # Proton data
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spi/L3/spi_sf00/',
        'local_path': os.path.join('data', 'psp', 'sweap', 'spi', 'l3', 'spi_sf00_l3_mom'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spi_sf00_L3_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_swp_spi_sf00_L3_{date_str}_v*.cdf',
        'spdf_file_pattern': r'psp_swp_spi_sf00_l3_{date_str}_v*.cdf',   # SPDF case (lowercase l3)
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': ['np_moment', 'vp_moment_RTN', 'wp_moment', 'vp_moment_SC'],
    },
    'spi_af00_l3_mom': {  # High-resolution proton data
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spi/L3/spi_af00/',
        'local_path': os.path.join('data', 'psp', 'sweap', 'spi', 'l3', 'spi_af00_l3_mom'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spi_af00_L3_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_swp_spi_af00_L3_{date_str}_v*.cdf',
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': ['np_moment', 'vp_moment_RTN', 'wp_moment', 'vp_moment_SC'],
    },
    'spi_sf0a_l3_mom': {  # Alpha particle data
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spi/L3/spi_sf0a/',
        'local_path': os.path.join('data', 'psp', 'sweap', 'spi', 'l3', 'spi_sf0a_l3_mom'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spi_sf0a_L3_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_swp_spi_sf0a_L3_{date_str}_v*.cdf',
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': ['na_moment', 'va_moment_RTN', 'wa_moment', 'va_moment_SC'],
    },
    'sf00_fits': {  # Local CSV fits data
        'mission': 'psp',
        'data_sources': ['local_csv'],  # Identifies this as local CSV data
        'local_path': os.path.join('data', 'psp', 'sweap', 'spi', 'l3', 'spi_sf00_fits'),
        'file_pattern_import': ['psp_swp_spi_sf00_{date_str}_fits.csv', 'l3_mom_{date_str}_proton.csv'], # list of possible names per day
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': ['see_fits_calculation.py'],
    },
    'sf01_fits': {  # Local CSV fits data
        'mission': 'psp',
        'data_sources': ['local_csv'],
        'local_path': os.path.join('data', 'psp', 'sweap', 'spi', 'l3', 'spi_sf01_fits'),
        'file_pattern_import': ['psp_swp_spi_sf01_{date_str}_fits.csv', 'l3_mom_{date_str}_alpha.csv'], # list of possible names per day
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': ['see_fits_calculation.py'],
    },
    'ham': {  # Hammerhead sensor CSV data
        'mission': 'psp',
        'data_sources': ['local_csv'],
        'local_path': os.path.join('magnetic_hole_finder', 'psp_data'),  # Path relative to project root
        'file_pattern_import': ['*.csv'],  # Search for all CSV files
        'data_level': 'processed',
        'file_time_format': 'dynamic',  # Files can cover various time ranges
        'data_vars': ['B_magnitude', 'temperature', 'density', 'velocity'],
        'datetime_column': 'datetime',  # Column name containing datetime information
    },
    'psp_orbit_data': {  # Parker Solar Probe positional data
        'mission': 'psp',
        'data_sources': ['local_support_data'],  # Identifies this as local support data (not time-specific downloads)
        'local_path': os.path.join('support_data', 'trajectories'),  # Path relative to project root
        'file_pattern_import': 'psp_positional_data.npz',  # NPZ file containing full mission trajectory
        'data_level': 'derived',
        'file_time_format': 'mission',  # Contains data for entire mission duration
        'data_vars': ['times_numeric', 'longitude_values', 'radial_values', 'latitude_values'],
    },
    # PSP FIELDS DFB data types
    'dfb_ac_spec_dv12hg': {
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/dfb_ac_spec/',
        'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'dfb_ac_spec'),
        'password_type': 'mag',
        'file_pattern': r'psp_fld_{data_level}_dfb_ac_spec_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_fld_{data_level}_dfb_ac_spec_{date_str}_v*.cdf',
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': ['dfb_ac_spec_dv12hg', 'dfb_ac_spec_dv34hg'],
    },
    'dfb_ac_spec_dv34hg': {
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/dfb_ac_spec/',
        'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'dfb_ac_spec'),
        'password_type': 'mag',
        'file_pattern': r'psp_fld_{data_level}_dfb_ac_spec_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_fld_{data_level}_dfb_ac_spec_{date_str}_v*.cdf',
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': ['dfb_ac_spec_dv12hg', 'dfb_ac_spec_dv34hg'],
    },
    'dfb_dc_spec_dv12hg': {
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/dfb_dc_spec/',
        'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'dfb_dc_spec'),
        'password_type': 'mag',
        'file_pattern': r'psp_fld_{data_level}_dfb_dc_spec_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_fld_{data_level}_dfb_dc_spec_{date_str}_v*.cdf',
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': ['dfb_dc_spec_dv12hg'],
    },
    # WIND Satellite Data Types
    'wind_mfi_h2': {
        'mission': 'wind',
        'data_sources': ['spdf'],
        'local_path': os.path.join('data', 'wind', 'mfi', 'mfi_h2'),
        'file_pattern_import': r'wi_h2_mfi_{date_str}_v*.cdf',
        'data_level': 'h2',
        'file_time_format': 'daily',
        'data_vars': ['BGSE', 'BGSM'],  # Magnetic field in GSE and GSM coordinates
    },
    'wind_swe_h5': {
        'mission': 'wind',
        'data_sources': ['spdf'],
        'local_path': os.path.join('data', 'wind', 'swe', 'swe_h5'),
        'file_pattern_import': r'wi_h5_swe_{date_str}_v*.cdf',
        'data_level': 'h5',
        'file_time_format': 'daily',
        'data_vars': ['Proton_VEL_nonlin', 'Proton_Np_nonlin', 'Proton_W_nonlin'],
    },
    'wind_swe_h1': {
        'mission': 'wind',
        'data_sources': ['spdf'],
        'local_path': os.path.join('data', 'wind', 'swe', 'swe_h1'),
        'file_pattern_import': r'wi_h1_swe_{date_str}_v*.cdf',
        'data_level': 'h1',
        'file_time_format': 'daily',
        'data_vars': ['Proton_V_nonlin', 'Proton_VX_nonlin', 'Proton_VY_nonlin', 'Proton_VZ_nonlin', 'Proton_Np_nonlin', 'Proton_W_nonlin'],
    },
    'wind_3dp_pm': {
        'mission': 'wind',
        'data_sources': ['spdf'],
        'local_path': os.path.join('data', 'wind', '3dp', '3dp_pm'),
        'file_pattern_import': r'wi_pm_3dp_{date_str}_v*.cdf',
        # 'pyspedas_datatype': '3dp_pm',            # v3.x: Dynamic pyspedas integration
        # 'pyspedas_func': 'pyspedas.wind.threedp', # v3.x: Dynamic pyspedas integration
        'data_level': 'pm',
        'file_time_format': 'daily',
        'data_vars': ['TIME', 'VALID', 'P_VELS', 'P_DENS', 'P_TEMP', 'A_DENS', 'A_TEMP'],
    },
    'wind_3dp_elpd': {
        'mission': 'wind',
        'data_sources': ['spdf'],
        'local_path': os.path.join('data', 'wind', '3dp', '3dp_elpd'),
        'file_pattern_import': r'wi_elpd_3dp_{date_str}_v*.cdf',
        # 'pyspedas_datatype': '3dp_elpd',           # v3.x: Dynamic pyspedas integration
        # 'pyspedas_func': 'pyspedas.wind.threedp', # v3.x: Dynamic pyspedas integration
        'data_level': 'elpd',
        'file_time_format': 'daily',
        'data_vars': ['EPOCH', 'FLUX', 'PANGLE'],  # Time, electron flux and pitch angles
    }
}


# === AUTO-REGISTER CUSTOM CDF CLASSES ===
def add_cdf_data_types():
    """
    Automatically add CDF data types from custom_classes directory to data_types configuration.
    This enables get_data() to handle auto-registered CDF classes properly.
    """
    import glob
    from pathlib import Path
    
    # Get project root using the robust function from data_import
    def get_project_root():
        """Get the absolute path to the project root directory."""
        try:
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_file_dir))  # Go up from data_classes to plotbot to project root
            return project_root
        except:
            return os.getcwd()
    
    # Get path to custom_classes directory
    current_dir = Path(__file__).parent
    custom_classes_dir = current_dir / "custom_classes"
    
    if not custom_classes_dir.exists():
        return
    
    # Find all Python files in custom_classes (these are auto-generated CDF classes)
    cdf_class_files = list(custom_classes_dir.glob("*.py"))
    cdf_class_files = [f for f in cdf_class_files if not f.name.startswith("__")]
    
    for py_file in cdf_class_files:
        class_name = py_file.stem  # e.g., 'psp_waves_auto' from 'psp_waves_auto.py'
        
        # Add CDF data type configuration
        if class_name not in data_types:
            # Use robust project root detection
            project_root = get_project_root()
            default_cdf_path = os.path.join(project_root, "docs", "implementation_plans", "CDF_Integration", "KP_wavefiles")
            
            data_types[class_name] = {
                'mission': 'cdf_custom',
                'data_sources': ['local_cdf'],  # Mark as local CDF data
                'local_path': 'FROM_CLASS_METADATA',  # Signal to read path from class metadata
                'default_cdf_path': default_cdf_path,  # Fallback path if metadata fails
                'file_pattern_import': '*.cdf',  # Will be determined dynamically
                'data_level': 'custom',
                'file_time_format': 'dynamic',
                'data_vars': [],  # Will be populated from CDF metadata
                'cdf_class_name': class_name,  # Link to the actual class name
            }

# Automatically register CDF data types when this module is imported
add_cdf_data_types()
