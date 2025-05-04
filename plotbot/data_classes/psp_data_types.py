#plotbot/data_classes/psp_data_types.py

import os

# CONFIGURATION: Data Types, Defines all available PSP data products
#====================================================================
data_types = {
    'mag_RTN': {
        'class_instance_name': 'mag_rtn',
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/mag_RTN/',  # URL for data source
        'local_path': os.path.join('psp_data', 'fields', '{data_level}', 'mag_rtn'),  # Local path for storing data
        'password_type': 'mag',  # Type of password required
        'file_pattern': r'psp_fld_{data_level}_mag_RTN_{date_hour_str}_v(\d{{2}})\.cdf',  # Regex pattern for file names
        'file_pattern_import': r'psp_fld_{data_level}_mag_RTN_{date_hour_str}_v*.cdf',  # Regex pattern for importing files
        'data_level': 'l2',  # Data level
        'file_time_format': '6-hour',  # Time format of the files
        'data_vars': ['psp_fld_l2_mag_RTN'],  # Variables to import
        'var_dims': {
            'psp_fld_l2_mag_RTN': ['time', 'component'],
        },
    },
    'mag_RTN_4sa': {
        'class_instance_name': 'mag_rtn_4sa',
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/mag_RTN_4_Sa_per_Cyc/',
        'local_path': os.path.join('psp_data', 'fields', '{data_level}', 'mag_rtn_4_per_cycle'),
        'password_type': 'mag',
        'file_pattern': r'psp_fld_{data_level}_mag_RTN_4_Sa_per_Cyc_{date_str}_v(\d{{2}})\.cdf',      # Added this
        'file_pattern_import': r'psp_fld_{data_level}_mag_RTN_4_Sa_per_Cyc_{date_str}_v*.cdf',  # Fixed case to match actual files
        'spdf_file_pattern': r'psp_fld_{data_level}_mag_rtn_4_sa_per_cyc_{date_str}_v*.cdf',    # SPDF case (lowercase)
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': ['psp_fld_l2_mag_RTN_4_Sa_per_Cyc'],
        'var_dims': {
            'psp_fld_l2_mag_RTN_4_Sa_per_Cyc': ['time', 'component'],
        },
    },
    'mag_SC': {
        'class_instance_name': 'mag_sc',
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/mag_SC/',
        'local_path': os.path.join('psp_data', 'fields', '{data_level}', 'mag_sc'),
        'password_type': 'mag',
        'file_pattern': r'psp_fld_{data_level}_mag_SC_{date_hour_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_fld_{data_level}_mag_SC_{date_hour_str}_v*.cdf',
        'data_level': 'l2',
        'file_time_format': '6-hour',
        'data_vars': ['psp_fld_l2_mag_SC'],
        'var_dims': {
            'psp_fld_l2_mag_SC': ['time', 'component'],
        },
    },
    'mag_SC_4sa': {
        'class_instance_name': 'mag_sc_4sa',
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/fields/{data_level}/mag_SC_4_Sa_per_Cyc/',
        'local_path': os.path.join('psp_data', 'fields', '{data_level}', 'mag_sc_4_per_cycle'),
        'password_type': 'mag',
        'file_pattern': r'psp_fld_{data_level}_mag_SC_4_Sa_per_Cyc_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_fld_{data_level}_mag_SC_4_Sa_per_Cyc_{date_str}_v*.cdf',
        'spdf_file_pattern': r'psp_fld_{data_level}_mag_sc_4_sa_per_cyc_{date_str}_v*.cdf',   # SPDF case (lowercase)
        'data_level': 'l2',
        'file_time_format': 'daily',
        'data_vars': ['psp_fld_l2_mag_SC_4_Sa_per_Cyc'],
        'var_dims': {
            'psp_fld_l2_mag_SC_4_Sa_per_Cyc': ['time', 'component'],
        },
    },
    'spe_sf0_pad': {  # Electron data
        'class_instance_name': 'epad',
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spe/L3/spe_sf0_pad/',
        'local_path': os.path.join('psp_data', 'sweap', 'spe', 'l3', 'spe_sf0_pad'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spe_sf0_L3_pad_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_swp_spe_sf0_L3_pad_{date_str}_v*.cdf',
        'spdf_file_pattern': r'psp_swp_spe_sf0_l3_pad_{date_str}_v*.cdf',   # SPDF case (lowercase l3)
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': ['EFLUX_VS_PA_E', 'PITCHANGLE'],
        'var_dims': {
            'EFLUX_VS_PA_E': ['time', 'energy', 'angle'],
            'PITCHANGLE': ['energy', 'angle'],
        },
    },
    'spe_af0_pad': {  # High-resolution electron data
        'class_instance_name': 'epad_hr',
        'url': 'https://sprg.ssl.berkeley.edu/data/psp/data/sci/sweap/spe/L3/spe_af0_pad/',
        'local_path': os.path.join('psp_data', 'sweap', 'spe', 'l3', 'spe_af0_pad'),
        'password_type': 'sweap',
        'file_pattern': r'psp_swp_spe_af0_L3_pad_{date_str}_v(\d{{2}})\.cdf',
        'file_pattern_import': r'psp_swp_spe_af0_L3_pad_{date_str}_v*.cdf',
        'data_level': 'l3',
        'file_time_format': 'daily',
        'data_vars': ['EFLUX_VS_PA_E', 'PITCHANGLE'],
        'var_dims': {
            'EFLUX_VS_PA_E': ['time', 'energy', 'angle'],
            'PITCHANGLE': ['energy', 'angle'],
        },
    },
    'spi_sf00_l3_mom': {  # Proton data
        'class_instance_name': 'proton',
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
        'var_dims': {
            'VEL_RTN_SUN': ['time', 'component'],
            'DENS': ['time'],
            'TEMP': ['time'],
            'MAGF_INST': ['time', 'component'],
            'T_TENSOR_INST': ['time', 'component1', 'component2'],
            'EFLUX_VS_ENERGY': ['time', 'energy'],
            'EFLUX_VS_THETA': ['time', 'theta'],
            'EFLUX_VS_PHI': ['time', 'phi'],
            'ENERGY_VALS': ['energy'],
            'THETA_VALS': ['theta'],
            'PHI_VALS': ['phi'],
        },
    },
    'spi_af00_L3_mom': {  # High-resolution proton data
        'class_instance_name': 'proton_hr',
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
        'var_dims': {
            'VEL_RTN_SUN': ['time', 'component'],
            'DENS': ['time'],
            'TEMP': ['time'],
            'MAGF_INST': ['time', 'component'],
            'T_TENSOR_INST': ['time', 'component1', 'component2'],
            'EFLUX_VS_ENERGY': ['time', 'energy'],
            'EFLUX_VS_THETA': ['time', 'theta'],
            'EFLUX_VS_PHI': ['time', 'phi'],
            'ENERGY_VALS': ['energy'],
            'THETA_VALS': ['theta'],
            'PHI_VALS': ['phi'],
        },
    },
    'sf00_fits': { # FITS sf00 CSV data
        'class_instance_name': 'proton_fits',
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
        'class_instance_name': 'alpha_fits',
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
        'class_instance_name': 'ham',
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