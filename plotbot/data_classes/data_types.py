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
        'file_pattern': r'psp_swp_spi_sf00_L3_mom_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_swp_spi_sf00_L3_mom_{date_str}_v*.cdf',
        'spdf_file_pattern': r'psp_swp_spi_sf00_l3_mom_{date_str}_v*.cdf',   # SPDF case (lowercase l3)
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': [
            'VEL_RTN_SUN', 'DENS', 'TEMP', 'MAGF_INST', 'T_TENSOR_INST',
            'EFLUX_VS_ENERGY', 'EFLUX_VS_THETA', 'EFLUX_VS_PHI',
            'ENERGY_VALS', 'THETA_VALS', 'PHI_VALS', 'SUN_DIST'
        ],
    },
    'spi_sf00_8dx32ex8a': {  # PSP SPAN-I L2 VDF data - CONFIRMED ON BERKELEY!
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spi/L2/spi_sf00/',
        'local_path': os.path.join('data', 'psp', 'sweap', 'spi', 'l2', 'spi_sf00_8dx32ex8a'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spi_sf00_L2_8Dx32Ex8A_{date_str}_v(\d{{2}})\.cdf',      # Berkeley case
        'file_pattern_import': r'psp_swp_spi_sf00_L2_8Dx32Ex8A_{date_str}_v*.cdf',       # Berkeley case
        'spdf_file_pattern': r'psp_swp_spi_sf00_l2_8dx32ex8a_{date_str}_v*.cdf',         # SPDF case (lowercase)
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': ['Epoch', 'THETA', 'PHI', 'ENERGY', 'EFLUX', 'ROTMAT_SC_INST'],
    },
    'spi_af00_L3_mom': {  # High-resolution proton data
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spi/L3/spi_af00/',
        'local_path': os.path.join('data', 'psp', 'sweap', 'spi', 'l3', 'spi_af00_l3_mom'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spi_af00_L3_mom_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_swp_spi_af00_L3_mom_{date_str}_v*.cdf',
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': [
            'VEL_RTN_SUN', 'DENS', 'TEMP', 'MAGF_INST', 'T_TENSOR_INST',
            'EFLUX_VS_ENERGY', 'EFLUX_VS_THETA', 'EFLUX_VS_PHI',
            'ENERGY_VALS', 'THETA_VALS', 'PHI_VALS'
        ],
    },
    'spi_sf0a_l3_mom': {  # Alpha particle data
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spi/L3/spi_sf0a/',
        'local_path': os.path.join('data', 'psp', 'sweap', 'spi', 'l3', 'spi_sf0a_l3_mom'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spi_sf0a_L3_mom_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_swp_spi_sf0a_L3_mom_{date_str}_v*.cdf',
        'spdf_file_pattern': r'psp_swp_spi_sf0a_l3_mom_{date_str}_v*.cdf',   # SPDF case (lowercase l3)
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': [
            'VEL_INST', 'VEL_SC', 'VEL_RTN_SUN', 'DENS', 'TEMP', 'MAGF_INST', 'T_TENSOR_INST',
            'EFLUX_VS_ENERGY', 'EFLUX_VS_THETA', 'EFLUX_VS_PHI',
            'ENERGY_VALS', 'THETA_VALS', 'PHI_VALS', 'SUN_DIST'
        ],
    },
    'dfb_ac_spec_dv12hg': {  # PSP FIELDS Electric Field AC Spectra dV12hg
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/dfb_ac_spec/dv12hg/',
        'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'dfb_ac_spec', 'dv12hg'),
        'password_type': 'mag',  # FIELDS instrument uses mag password type
        'file_pattern': r'psp_fld_{data_level}_dfb_ac_spec_dv12hg_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_fld_{data_level}_dfb_ac_spec_dv12hg_{date_str}_v*.cdf',
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': [
            'psp_fld_l2_dfb_ac_spec_dV12hg',               # AC spectrum dv12 data
            'psp_fld_l2_dfb_ac_spec_dV12hg_frequency_bins'  # AC spectrum dv12 frequencies
        ],
    },
    'dfb_ac_spec_dv34hg': {  # PSP FIELDS Electric Field AC Spectra dV34hg
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/dfb_ac_spec/dv34hg/',
        'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'dfb_ac_spec', 'dv34hg'),
        'password_type': 'mag',  # FIELDS instrument uses mag password type
        'file_pattern': r'psp_fld_{data_level}_dfb_ac_spec_dv34hg_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_fld_{data_level}_dfb_ac_spec_dv34hg_{date_str}_v*.cdf',
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': [
            'psp_fld_l2_dfb_ac_spec_dV34hg',               # AC spectrum dv34 data  
            'psp_fld_l2_dfb_ac_spec_dV34hg_frequency_bins'  # AC spectrum dv34 frequencies
        ],
    },
    'dfb_dc_spec_dv12hg': {  # PSP FIELDS Electric Field DC Spectra dV12hg
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/dfb_dc_spec/dv12hg/',
        'local_path': os.path.join('data', 'psp', 'fields', '{data_level}', 'dfb_dc_spec', 'dv12hg'),
        'password_type': 'mag',  # FIELDS instrument uses mag password type
        'file_pattern': r'psp_fld_{data_level}_dfb_dc_spec_dv12hg_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_fld_{data_level}_dfb_dc_spec_dv12hg_{date_str}_v*.cdf',
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': [
            'psp_fld_l2_dfb_dc_spec_dV12hg',               # DC spectrum dv12 data (only available)
            'psp_fld_l2_dfb_dc_spec_dV12hg_frequency_bins'  # DC spectrum dv12 frequencies
        ],
    },
    'sf00_fits': { # FITS sf00 CSV data
        'mission': 'psp',
        'data_sources': ['local_csv'],
        'local_path': os.path.join('data', 'psp', 'sweap', 'spi_fits', 'sf00', 'p2', 'v00'), # UPDATED PATH AGAIN
        'file_pattern_import': ['spp_swp_spi_sf00_*.csv'], # More specific pattern
        'file_time_format': 'daily',
        'data_vars': [
            'time', 'np1', 'np2', 'vp1_x', 'vp1_y', 'vp1_z',
            'B_inst_x', 'B_inst_y', 'B_inst_z', 'B_SC_x', 'B_SC_y', 'B_SC_z',
            'vdrift', 'Tperp1', 'Tperp2', 'Trat1', 'Trat2',
            'np1_dpar', 'np2_dpar', 'vp1_x_dpar', 'vp1_y_dpar',
            'vp1_z_dpar', 'vdrift_dpar', 'Tperp1_dpar', 'Tperp2_dpar',
            'Trat1_dpar', 'Trat2_dpar', 'chi'
        ]
    },
    'sf01_fits': { # FITS sf01 CSV data
        'mission': 'psp',
        'data_sources': ['local_csv'],
        'local_path': os.path.join('data', 'psp', 'sweap', 'spi_fits', 'sf01', 'p3', 'v00'), # UPDATED PATH
        'file_pattern_import': ['spp_swp_spi_sf01_*.csv'], # More specific pattern
        'file_time_format': 'daily',
        'data_vars': [
            'time', 'na', 'va_x', 'va_y', 'va_z', 'Trata', 'Ta_perp',
            'B_inst_x', 'B_inst_y', 'B_inst_z', # Needed for B_mag calculation
            'na_dpar', 'va_x_dpar', 'va_y_dpar', 'va_z_dpar',
            'Trata_dpar', 'Ta_perp_dpar', 'chi'
        ]
    },
    'ham': { # NEW: Hammerhead CSV data
        'mission': 'psp',
        'data_sources': ['local_csv'],
        'local_path': os.path.join('data', 'psp', 'Hamstrings'),
        'file_pattern_import': ['*_v*.csv'],
        'file_time_format': 'daily',
        'datetime_column': 'datetime',
        'data_vars': [
            'time', 'datetime', 'hamogram_30s', 'hamogram_og_30s',
            'hamogram_2m', 'hamogram_og_2m', 'hamogram_20m', 'hamogram_90m',
            'hamogram_4h', 'hamogram_og_4h', 'trat_ham', 'trat_ham_og',
            'ham_core_drift', 'ham_core_drift_va', 'Nham_div_Ncore', 'Nham_div_Ncore_og',
            'Nham_div_Ntot', 'Nham_div_Ntot_og', 'Tperp_ham_div_core', 'Tperp_ham_div_core_og',
            'Tperprat_driftva_hc', 'Tperprat_driftva_hc_og'
        ]
    },
    'psp_br_norm_calculated': {
        'mission': 'psp',
        'data_sources': ['calculated'],
        'has_dependencies': True,
        'dependencies': {
            'mag_input': 'mag_RTN_4sa',      # Key for the mag data dependency
            'proton_input': 'spi_sf00_l3_mom' # Key for the proton data dependency
        },
        'class_file': 'psp_br_norm',          # New module to be created
        'class_name': 'psp_br_norm_class',  # Corrected class name
        'data_vars': ['br_norm']              # The primary variable this type produces
    },
    'psp_orbit_data': {
        'mission': 'psp',
        'data_sources': ['local_support_data'],  # Local support files (NPZ, CSV, JSON, HDF5, etc.)
        'local_path': 'support_data',  # Base folder to search recursively
        'file_pattern_import': 'psp_positional_data.npz',  # Exact filename to find
        'file_time_format': 'local_support_data',  # Support data files don't follow standard time formats
        'data_vars': ['times', 'r_sun', 'carrington_lon', 'carrington_lat', 'icrf_x', 'icrf_y', 'icrf_z'],
        'class_file': 'psp_orbit',
        'class_name': 'psp_orbit_class',
        'description': 'Parker Solar Probe orbital/positional data including heliocentric distance, Carrington coordinates, and derived quantities'
    },
    'psp_span_vdf': {
        'mission': 'psp',
        'data_sources': ['berkeley', 'spdf'],  # Dual source support
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spi/L2/spi_sf00/',
        'local_path': os.path.join('data', 'psp', 'sweap', 'spi', 'l2', 'spi_sf00_8dx32ex8a'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spi_sf00_L2_8Dx32Ex8A_{date_str}_v(\d{{2}})\.cdf',      # Berkeley case
        'file_pattern_import': r'psp_swp_spi_sf00_L2_8Dx32Ex8A_{date_str}_v*.cdf',       # Berkeley case
        'spdf_file_pattern': r'psp_swp_spi_sf00_l2_8dx32ex8a_{date_str}_v*.cdf',         # SPDF case (lowercase)
        'data_level': 'l2',
        'file_time_format': 'daily',
        'class_file': 'psp_span_vdf',         # Points to our new class file
        'class_name': 'psp_span_vdf_class',   # Our VDF class name
        'data_vars': [
            'THETA',              # Raw angular coordinates (needed for VDF calculation)
            'PHI',                # Raw angular coordinates (needed for VDF calculation)  
            'ENERGY',             # Raw energy bins (needed for VDF calculation)
            'EFLUX',              # Raw energy flux data (needed for VDF calculation)
            'ROTMAT_SC_INST',     # Rotation matrix for coordinate transforms
            # Note: Time comes from imported_data.times, not data_vars
            # Note: Processed variables (vdf_collapsed, vdf_theta_plane, etc.) are calculated by VDF class
        ],
        'description': 'PSP SPAN-I Velocity Distribution Function data for velocity-space analysis',
    },
    
    # === WIND SATELLITE DATA TYPES ===
    # NOTE: v3.x will use dynamic pyspedas calls from these fields, v2.x uses hardcoded PYSPEDAS_MAP
    'wind_mfi_h2': {
        'mission': 'wind',
        'data_sources': ['spdf'],
        'local_path': os.path.join('data', 'wind', 'mfi', 'mfi_h2'),
        'file_pattern_import': r'wi_h2_mfi_{date_str}_v*.cdf',
        # 'pyspedas_datatype': 'mfi_h2',        # v3.x: Dynamic pyspedas integration
        # 'pyspedas_func': 'pyspedas.wind.mfi', # v3.x: Dynamic pyspedas integration
        'data_level': 'h2',
        'file_time_format': 'daily',
        'data_vars': ['Epoch', 'BGSE', 'BF1'],  # Time, vector B in GSE, |B|
    },
    'wind_swe_h1': {
        'mission': 'wind', 
        'data_sources': ['spdf'],
        'local_path': os.path.join('data', 'wind', 'swe', 'swe_h1'),
        'file_pattern_import': r'wi_h1_swe_{date_str}_v*.cdf',
        # 'pyspedas_datatype': 'swe_h1',        # v3.x: Dynamic pyspedas integration
        # 'pyspedas_func': 'pyspedas.wind.swe', # v3.x: Dynamic pyspedas integration
        'data_level': 'h1',
        'file_time_format': 'daily',
        'data_vars': ['fit_flag', 'Proton_Wpar_nonlin', 'Proton_Wperp_nonlin', 'Alpha_W_Nonlin'],
    },
    'wind_swe_h5': {
        'mission': 'wind',
        'data_sources': ['spdf'], 
        'local_path': os.path.join('data', 'wind', 'swe', 'swe_h5'),
        'file_pattern_import': r'wi_h5_swe_{date_str}_v*.cdf',
        # 'pyspedas_datatype': 'swe_h5',        # v3.x: Dynamic pyspedas integration
        # 'pyspedas_func': 'pyspedas.wind.swe', # v3.x: Dynamic pyspedas integration
        'data_level': 'h5',
        'file_time_format': 'daily',
        'data_vars': ['T_elec'],  # Electron temperature
    },
    'wind_3dp_pm': {
        'mission': 'wind',
        'data_sources': ['spdf'],
        'local_path': os.path.join('data', 'wind', '3dp', '3dp_pm'),
        'file_pattern_import': r'wi_pm_3dp_{date_str}_v*.cdf',
        # 'pyspedas_datatype': '3dp_pm',             # v3.x: Dynamic pyspedas integration
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


# === DYNAMIC PATH CONSTRUCTION ===
def get_local_path(data_type_key):
    """
    Get the local path for a data type, using the configurable data directory.
    
    Args:
        data_type_key (str): The data type key (e.g., 'mag_RTN_4sa')
        
    Returns:
        str: Full local path with current data_dir configuration
    """
    # Import here to avoid circular imports
    from ..config import config
    
    if data_type_key not in data_types:
        return None
        
    data_type_config = data_types[data_type_key]
    original_local_path = data_type_config.get('local_path', '')
    
    # Replace 'data' at the beginning with the configured data_dir
    if original_local_path.startswith('data'):
        # Replace 'data' with config.data_dir
        relative_path = original_local_path[4:]  # Remove 'data' prefix
        if relative_path.startswith(os.sep):
            relative_path = relative_path[1:]  # Remove leading separator
        return os.path.join(config.data_dir, relative_path)
    else:
        # If path doesn't start with 'data', assume it's already correctly formatted
        return original_local_path


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
