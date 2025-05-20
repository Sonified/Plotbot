#plotbot/data_classes/psp_data_types.py

import os

# CONFIGURATION: Data Types, Defines all available PSP data products
#====================================================================
data_types = {
    'mag_RTN': {
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/mag_RTN/',  # URL for data source
        'local_path': os.path.join('psp_data', 'fields', '{data_level}', 'mag_rtn'),  # Local path for storing data
        'password_type': 'mag',  # Type of password required
        'file_pattern': r'psp_fld_{data_level}_mag_RTN_{date_hour_str}_v(\d{{2}})\.cdf',  # Regex pattern for file names
        'file_pattern_import': r'psp_fld_{data_level}_mag_RTN_{date_hour_str}_v*.cdf',  # Regex pattern for importing files
        'data_level': 'l2',  # Data level
        'file_time_format': '6-hour',  # Time format of the files
        'data_vars': ['psp_fld_l2_mag_RTN'],  # Variables to import
    },
    'mag_RTN_4sa': {
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/mag_RTN_4_Sa_per_Cyc/',
        'local_path': os.path.join('psp_data', 'fields', '{data_level}', 'mag_rtn_4_per_cycle'),
        'password_type': 'mag',
        'file_pattern': r'psp_fld_{data_level}_mag_RTN_4_Sa_per_Cyc_{date_str}_v(\d{{2}})\.cdf',      # Added this
        'file_pattern_import': r'psp_fld_{data_level}_mag_RTN_4_Sa_per_Cyc_{date_str}_v*.cdf',  # Fixed case to match actual files
        'spdf_file_pattern': r'psp_fld_{data_level}_mag_rtn_4_sa_per_cyc_{date_str}_v*.cdf',    # SPDF case (lowercase)
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': ['psp_fld_l2_mag_RTN_4_Sa_per_Cyc'],
    },
    'mag_SC': {
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/mag_SC/',
        'local_path': os.path.join('psp_data', 'fields', '{data_level}', 'mag_sc'),
        'password_type': 'mag',
        'file_pattern': r'psp_fld_{data_level}_mag_SC_{date_hour_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_fld_{data_level}_mag_SC_{date_hour_str}_v*.cdf',
        'data_level': 'l2',
        'file_time_format': '6-hour',
        'data_vars': ['psp_fld_l2_mag_SC'],
    },
    'mag_SC_4sa': {
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/mag_SC_4_Sa_per_Cyc/',
        'local_path': os.path.join('psp_data', 'fields', '{data_level}', 'mag_sc_4_per_cycle'),
        'password_type': 'mag',
        'file_pattern': r'psp_fld_{data_level}_mag_SC_4_Sa_per_Cyc_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_fld_{data_level}_mag_SC_4_Sa_per_Cyc_{date_str}_v*.cdf',
        'spdf_file_pattern': r'psp_fld_{data_level}_mag_sc_4_sa_per_cyc_{date_str}_v*.cdf',   # SPDF case (lowercase)
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': ['psp_fld_l2_mag_SC_4_Sa_per_Cyc'],
    },
    'spe_sf0_pad': {  # Electron data
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spe/L3/spe_sf0_pad/',
        'local_path': os.path.join('psp_data', 'sweap', 'spe', 'l3', 'spe_sf0_pad'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spe_sf0_L3_pad_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_swp_spe_sf0_L3_pad_{date_str}_v*.cdf',
        'spdf_file_pattern': r'psp_swp_spe_sf0_l3_pad_{date_str}_v*.cdf',   # SPDF case (lowercase l3)
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': ['EFLUX_VS_PA_E', 'PITCHANGLE'],
    },
    'spe_af0_pad': {  # High-resolution electron data
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spe/L3/spe_af0_pad/',
        'local_path': os.path.join('psp_data', 'sweap', 'spe', 'l3', 'spe_af0_pad'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spe_af0_L3_pad_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_swp_spe_af0_L3_pad_{date_str}_v*.cdf',
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': ['EFLUX_VS_PA_E', 'PITCHANGLE'],
    },
    'spi_sf00_l3_mom': {  # Proton data
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spi/L3/spi_sf00/',
        'local_path': os.path.join('psp_data', 'sweap', 'spi', 'l3', 'spi_sf00_l3_mom'),
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
    'spi_af00_L3_mom': {  # High-resolution proton data
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spi/L3/spi_af00/',
        'local_path': os.path.join('psp_data', 'sweap', 'spi', 'l3', 'spi_af00_l3_mom'),
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
    'sf00_fits': { # FITS sf00 CSV data
        'file_source': 'local_csv',
        'local_path': os.path.join('psp_data', 'sweap', 'spi_fits', 'sf00', 'p2', 'v00'), # UPDATED PATH AGAIN
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
        'file_source': 'local_csv',
        'local_path': os.path.join('psp_data', 'sweap', 'spi_fits', 'sf01', 'p3', 'v00'), # UPDATED PATH
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
        'file_source': 'local_csv',
        'local_path': os.path.join('psp_data', 'Hamstrings'),
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
        'has_dependencies': True,
        'dependencies': {
            'mag_input': 'mag_RTN_4sa',      # Key for the mag data dependency
            'proton_input': 'spi_sf00_l3_mom' # Key for the proton data dependency
        },
        'class_file': 'psp_br_norm',          # New module to be created
        'class_name': 'psp_br_norm_class',  # Corrected class name
        'data_vars': ['br_norm']              # The primary variable this type produces
    }
}

# Increment this version number each time significant changes are pushed.
# Example: __version__ = "YYYY_MM_DD_vX.XX"
__version__ = "2025_05_18_v2.43"

# This commit message will be used in the git commit and the console log.
commit_message = "docs: Create HTML explanation of data update flow (v2.43)"

# Print version information on import
print(f"Plotbot Version: {__version__}")
print(f"Commit Message: {commit_message}")