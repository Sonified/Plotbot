#plotbot/data_classes/psp_data_types.py

import os

# Notes:
# `file_pattern` is used when interacting with the remote server during the download process.
# It often includes a specific regex capture group to capture the two-digit version number.
# This allows the download logic to identify the latest available version of a file on the server.
# 
# `file_pattern_import` is used when searching for files locally after they have been downloaded.
# It uses a wildcard to locate any matching version on the local disk.
# This distinction allows the downloader to get the newest file from the source, while the importer can find whatever version was actually downloaded locally.

# `file_time_format` is used to specify the time granularity of the files on the server.
# This is important because files are often divided into different lengths based on the sampling cadence.
# Having a pattern for this helps the system to correctly identify and process files of different time resolutions.
# For example, '6-hour' indicates that files are divided into 6-hour segments, while 'daily' indicates a daily resolution.

# The `data_vars` variable in each data type configuration serves as a container for the specific variables to be imported. 
# In some cases, like the `mag_RTN` data, `data_vars` returns a composite variable that aggregates related components, such as br, bt, and bn. 
# In contrast, for data types like `spe` and `spi`, the `data_vars` are more specific, directly identifying the individual variables of interest. 

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
            'ENERGY_VALS', 'THETA_VALS', 'PHI_VALS'
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
    'sf00_fits': { # UPDATED: Now points to CDF FITS data
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/.sav/spi_fits/cdf_files/sf00/p2/v00/', # ADDED: URL for CDFs
        'local_path': os.path.join('psp_data', 'sweap', 'spi_fits', 'sf00', 'p2', 'v00'), # UPDATED: Path simplified, removed 'cdf_files'
        'password_type': 'sweap', # ADDED: Password needed
        'file_pattern': r'spp_swp_spi_sf00_fits_(\d{{4}}-\d{{2}}-\d{{2}})_v(\d{{2}})\.cdf', # UPDATED: CDF pattern for download
        'file_pattern_import': r'spp_swp_spi_sf00_fits_{date_str}_v*.cdf', # UPDATED: CDF pattern for import
        'data_level': 'l3', # Assuming L3, adjust if needed
        'file_time_format': 'daily',
        'time_variable': 'Epoch', # ADDED: Explicitly define time variable -- not yet used
        'data_vars': [ # UPDATED: List based on observed CDF variables
            'Epoch', 'np1', 'np2', 'Tperp1', 'Tperp2', 'Trat1', 'Trat2',
            'vdrift', 'vp1', 'B_inst', 'B_SC', 'chi_p',
            # Include calculated vars now present in CDF
            'Tpar1', 'Tpar2', 'Tpar_tot', 'Tperp_tot', 'Temp_tot', 'n_tot', 
            'vp2', 'vcm', 'bhat_inst', 'qz_p',
            # Include magnitudes and uncertainties if available/needed
            'vp1_mag', 'vcm_mag', 'vp2_mag', 
            'np1_dpar', 'np2_dpar', 'Tperp1_dpar', 'Tperp2_dpar', 
            'Trat1_dpar', 'Trat2_dpar', 'vdrift_dpar', 'vp1_dpar',
            # Include other potentially useful vars
            'epad_strahl_centroid', 'ps_ht1', 'ps_ht2',
            'qz_p_par', 'qz_p_perp'
            # Add/remove as needed based on usage in proton_fits_class
        ]
    },
    'sf01_fits': { # UPDATED: Now points to CDF FITS data
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/.sav/spi_fits/cdf_files/sf01/p3/v00/', # ADDED: URL for CDFs
        'local_path': os.path.join('psp_data', 'sweap', 'spi_fits', 'cdf_files', 'sf01', 'p3', 'v00'), # UPDATED: Path reflects new structure
        'password_type': 'sweap', # ADDED: Password needed
        'file_pattern': r'spp_swp_spi_sf01_fits_(\d{{4}}-\d{{2}}-\d{{2}})_v(\d{{2}})\.cdf', # UPDATED: CDF pattern for download
        'file_pattern_import': r'spp_swp_spi_sf01_fits_{date_str}_v*.cdf', # UPDATED: CDF pattern for import
        'data_level': 'l3', # Assuming L3, adjust if needed
        'file_time_format': 'daily',
        'data_vars': [ # UPDATED: List based on observed CDF variables
            'Epoch', 'na', 'va', 'Tperpa', 'Trata', 'chi_a',
            # Include calculated/other vars present in CDF
            'Tpara', 'B_inst_a', 'B_SC_a', 'vp2_mag',
            # Uncertainties
            'na_dpar', 'va_dpar', 'Tperpa_dpar', 'Trata_dpar'
            # Add/remove as needed based on usage in alpha_fits_class
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
    }
}