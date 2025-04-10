zipped_data = {}
if mag_rtn_4sa is not None:
    zipped_data_mag_rtn_4sa = {

        #region 🧲 MAG 4SA ---------------------------------------------------//
        # 🧲 MAG_RTN_4SA
        'mag_RTN_4sa': (                                        # Magnetic Field Components in RTN Coordinates (4 samples per cycle = ~4.57 S/s)
            'time_series',                                      # Plot type
            # 'psp_fld_l2_mag_rtn_4_sa_per_cyc',                  # CDF variable name ⭐️
            [br_RTN_4sa, bt_RTN_4sa, bn_RTN_4sa],               # Data arrays
            ['br_RTN_4sa', 'bt_RTN_4sa', 'bn_RTN_4sa'],         # Plotbot Variable names
            datetime_mag_RTN_4sa,                               # Time Array (x-axis)
            [r'B \n (nT)', r'B \n (nT)', r'B \n (nT)'],                  # Y-axis labels
            [r'$B_R$', r'$B_T$', r'$B_N$'],                     # Legend labels
            ['forestgreen', 'orange', 'dodgerblue'],            # Line colors
            'linear',                                           # Y-axis scale
            None,                                               # Y-axis limits
            [1, 1, 1],                                          # Line widths
            ['-', '-', '-'],                                    # Line styles
            None,                                               # Additional data (required for spectral plotting)
            None,                                               # Spectrogram Colormap
            None,                                               # Spectrogram Colorbar scaling
            None                                                # Spectrogram Colorbar limits
        ),
        'bmag_RTN_4sa': (                  # Magnetic Field Magnitude in RTN Coordinates (4 samples per cycle = ~4.57 S/s)
            'time_series',                 # Plot type
            [bmag_RTN_4sa],                # Data array
            ['bmag_RTN_4sa'],              # Plotbot Variable name
            datetime_mag_RTN_4sa,          # Time Array (x-axis)
            [r'B (nT)'],                   # Y-axis label
            [r'|B|'],                      # Legend label
            ['k'],                         # Line color
            'linear',                      # Y-axis scale
            None,                          # Y-axis limits
            [1],                           # Line width
            ['-'],                         # Line style
            None,                          # Additional data (required for spectral plotting)
            None,                          # Spectrogram Colormap
            None,                          # Spectrogram Colorbar scaling
            None                           # Spectrogram Colorbar limits
        ),

        'br_RTN_4sa': (                    # Radial component of Magnetic Field in RTN Coordinates (4 samples per cycle = ~4.57 S/s)
            'time_series',                 # Plot type
            [br_RTN_4sa],                  # Data array
            ['br_RTN_4sa'],                # Plotbot Variable name
            datetime_mag_RTN_4sa,          # Time Array (x-axis)
            [r'B (nT)'],                   # Y-axis label
            [r'$B_R$'],                    # Legend label
            ['forestgreen'],               # Line color
            'linear',                      # Y-axis scale
            None,                          # Y-axis limits
            [1],                           # Line width
            ['-'],                         # Line style
            None,                          # Additional data (required for spectral plotting)
            None,                          # Spectrogram Colormap
            None,                          # Spectrogram Colorbar scaling
            None                           # Spectrogram Colorbar limits
        ),
        'bt_RTN_4sa': (                    # Tangential component of Magnetic Field in RTN Coordinates (4 samples per cycle = ~4.57 S/s)
            'time_series',                 # Plot type
            [bt_RTN_4sa],                  # Data array
            ['bt_RTN_4sa'],                # Plotbot Variable name
            datetime_mag_RTN_4sa,          # Time Array (x-axis)
            [r'B (nT)'],                   # Y-axis label
            [r'$B_T$'],                    # Legend label
            ['orange'],                    # Line color
            'linear',                      # Y-axis scale
            None,                          # Y-axis limits
            [1],                           # Line width
            ['-'],                         # Line style
            None,                          # Additional data (required for spectral plotting)
            None,                          # Spectrogram Colormap
            None,                          # Spectrogram Colorbar scaling
            None                           # Spectrogram Colorbar limits
        ),
        'bn_RTN_4sa': (                    # Normal component of Magnetic Field in RTN Coordinates (4 samples per cycle = ~4.57 S/s)
            'time_series',                 # Plot type
            [bn_RTN_4sa],                  # Data array
            ['bn_RTN_4sa'],                # Plotbot Variable name
            datetime_mag_RTN_4sa,          # Time Array (x-axis)
            [r'B (nT)'],                   # Y-axis label
            [r'$B_N$'],                    # Legend label
            ['dodgerblue'],                # Line color
            'linear',                      # Y-axis scale
            None,                          # Y-axis limits
            [1],                           # Line width
            ['-'],                         # Line style
            None,                          # Additional data (required for spectral plotting)
            None,                          # Spectrogram Colormap
            None,                          # Spectrogram Colorbar scaling
            None                           # Spectrogram Colorbar limits
        ),
        'pmag_RTN_4sa': (                          # Magnetic Pressure in RTN Coordinates (4 samples per cycle = ~4.57 S/s)
            'time_series',                         # Plot type
            [pmag_RTN_4sa],                        # Data array
            ['pmag_RTN_4sa'],                      # Plotbot Variable name
            datetime_mag_RTN_4sa,                  # Time Array (x-axis)
            [r'Magnetic \n Pressure \n (nPa)'],    # Y-axis label
            [r'$Press_{B}$'],                        # Legend label
            ['darkblue'],                          # Line color
            'linear',                              # Y-axis scale
            None,                                  # Y-axis limits
            [1],                                   # Line width
            ['-'],                                 # Line style
            None,                                  # Additional data (required for spectral plotting)
            None,                                  # Spectrogram Colormap
            None,                                  # Spectrogram Colorbar scaling
            None                                   # Spectrogram Colorbar limits
        ),

        'pmag_spi': (                          # Magnetic Pressure in RTN Coordinates (4 samples per cycle = ~4.57 S/s)
            'time_series',                         # Plot type
            [pmag_spi],                        # Data array
            ['pmag_spi'],                      # Plotbot Variable name
            datetime_spi,                  # Time Array (x-axis)
            [r'Magnetic \n Pressure \n (nPa)'],    # Y-axis label
            [r'$Press_{B}$'],                        # Legend label
            ['darkblue'],                          # Line color
            'linear',                              # Y-axis scale
            None,                                  # Y-axis limits
            [1],                                   # Line width
            ['-'],                                 # Line style
            None,                                  # Additional data (required for spectral plotting)
            None,                                  # Spectrogram Colormap
            None,                                  # Spectrogram Colorbar scaling
            None                                   # Spectrogram Colorbar limits
        ),
    }
    zipped_data.update(zipped_data_mag_rtn_4sa)

if mag_rtn is not None:

    
    # # Get magnetic field and time data for RTN coordinates at full resolution
    mag_data_RTN = get_data('psp_fld_l2_mag_RTN')
    mag_time_RTN, mag_field_RTN = mag_data_RTN.times, mag_data_RTN.y

    # # Access components of magnetic field in RTN coordinates at full resolution
    split_vec('psp_fld_l2_mag_RTN')
    br_RTN = get_data('psp_fld_l2_mag_RTN_x')
    bt_RTN = get_data('psp_fld_l2_mag_RTN_y')
    bn_RTN = get_data('psp_fld_l2_mag_RTN_z')
    bmag_RTN = np.sqrt(br_RTN.y**2 + bt_RTN.y**2 + bn_RTN.y**2)

    br_RTN = br_RTN.y
    bt_RTN = bt_RTN.y
    bn_RTN = bn_RTN.y

    # # Converting the magnetic field time to a timezone-aware datetime object
    datetime_mag_RTN = np.array([dt.replace(tzinfo=timezone.utc) for dt in time_datetime(mag_time_RTN)])
    
    mu_0 = constants.mu_0  # Permeability of free space
    # # Calculate magnetic pressure
    pmag_RTN = (bmag_RTN**2) / (2 * mu_0)

    # # Convert to nPa (nanoPascals) to match your other pressure units
    pmag_RTN = pmag_RTN * 1e9
    
        #region 🧲 MAG Full Cadence ---------------------------------------------------//
    # 🧲 MAG_RTN Full Cadence
    zipped_magRTN_data = {
    'mag_RTN': (                                       # Magnetic Field Components in RTN Coordinates (Full Cadence)
        'time_series',                                 # Plot type
        [br_RTN, bt_RTN, bn_RTN],                      # Data arrays
        ['br_RTN', 'bt_RTN', 'bn_RTN'],                # Plotbot Variable names
        datetime_mag_RTN,                              # Time Array (x-axis)
        [r'B (nT)', r'B (nT)', r'B (nT)'],             # Y-axis labels
        [r'$B_R$', r'$B_T$', r'$B_N$'],                # Legend labels
        ['forestgreen', 'orange', 'dodgerblue'],       # Line colors
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
        [1, 1, 1],                                     # Line widths
        ['-', '-', '-'],                               # Line styles
        None,                                          # Additional data (required for spectral plotting)
        None,                                          # Spectrogram Colormap
        None,                                          # Spectrogram Colorbar scaling
        None                                           # Spectrogram Colorbar limits
    ),
    'bmag_RTN': (                      # Magnetic Field Magnitude in RTN Coordinates (Full Cadence)
        'time_series',                 # Plot type
        [bmag_RTN],                    # Data array
        ['bmag_RTN'],                  # Plotbot Variable name
        datetime_mag_RTN,              # Time Array (x-axis)
        [r'B (nT)'],                   # Y-axis label
        [r'|B|'],                      # Legend label
        ['k'],                         # Line color
        'linear',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'br_RTN': (                        # Radial component of Magnetic Field in RTN Coordinates (Full Cadence)
        'time_series',                 # Plot type
        [br_RTN],                      # Data array
        ['br_RTN'],                    # Plotbot Variable name
        datetime_mag_RTN,              # Time Array (x-axis)
        [r'B (nT)'],                   # Y-axis label
        [r'$B_R$'],                    # Legend label
        ['forestgreen'],               # Line color
        'linear',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'bt_RTN': (                        # Tangential component of Magnetic Field in RTN Coordinates (Full Cadence)
        'time_series',                 # Plot type
        [bt_RTN],                      # Data array
        ['bt_RTN'],                    # Plotbot Variable name
        datetime_mag_RTN,              # Time Array (x-axis)
        [r'B (nT)'],                   # Y-axis label
        [r'$B_T$'],                    # Legend label
        ['orange'],                    # Line color
        'linear',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'bn_RTN': (                        # Normal component of Magnetic Field in RTN Coordinates (Full Cadence)
        'time_series',                 # Plot type
        [bn_RTN],                      # Data array
        ['bn_RTN'],                    # Plotbot Variable name
        datetime_mag_RTN,              # Time Array (x-axis)
        [r'B (nT)'],                   # Y-axis label
        [r'$B_N$'],                    # Legend label
        ['dodgerblue'],                # Line color
        'linear',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'pmag_RTN': (                                      # Magnetic Pressure in RTN Coordinates (Full Cadence)
        'time_series',                                 # Plot type
        [pmag_RTN],                                    # Data array
        ['pmag_RTN'],                                  # Plotbot Variable name
        datetime_mag_RTN,                              # Time Array (x-axis)
        [r'Magnetic \n Pressure \n (nPa)'],            # Y-axis label
        [r'$P_{mag}$'],                                # Legend label
        ['darkblue'],                                  # Line color
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
        [1],                                           # Line width
        ['-'],                                         # Line style
        None,                                          # Additional data (required for spectral plotting)
        None,                                          # Spectrogram Colormap
        None,                                          # Spectrogram Colorbar scaling
        None                                           # Spectrogram Colorbar limits
    )
    }

    #endregion
    zipped_data.update(zipped_magRTN_data)


if spi_sf00_mom is not None:
    zipped_spi_sf00_mom = {
           #region Protons / SPI Instrument---------------------------------------------------//
        'T_par': (                            #Parallel Temperature
            'time_series',                    # Plot type
            [T_parallel],                     # Data array
            ['T_parallel'],                   # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'Temp \n (eV)'],            # Y-axis label
            [r'$T_{p\parallel}$'],               # Legend label
            ['deepskyblue'],                  # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'T_perp': (                           #Perpendicular Temperature
            'time_series',                    # Plot type
            [T_perpendicular],                # Data array
            ['T_perpendicular'],              # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'Temp \n (eV)'],            # Y-axis label
            [r'$T_{p\perp}$'],                   # Legend label
            ['hotpink'],                      # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'Anisotropy': (                       #Temperature Anisotropy
            'time_series',                    # Plot type
            [Anisotropy],                     # Data array
            ['Anisotropy'],                   # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'$T_\perp/T_\parallel$'],       # Y-axis label
            [r'$T_\perp/T_\parallel$'],       # Legend label
            ['mediumspringgreen'],            # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'v_alfven_spi': (                     # Alfvén velocity
            'time_series',                    # Plot type
            [v_alfven_spi],                   # Data array
            ['v_alfven_spi'],                 # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'$V_{A}$ (km/s)'],              # Y-axis label
            [r'$V_{A}$'],                     # Legend label
            ['deepskyblue'],                  # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'beta_ppar_spi': (                    # Parallel Plasma Beta
            'time_series',                    # Plot type
            [beta_ppar_spi],                  # Data array
            ['beta_ppar_spi'],                # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'$\beta$'],                     # Y-axis label
            [r'$\beta_{p\parallel}$'],           # Legend label
            ['purple'],                       # Line color
            'log',                            # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'beta_pperp_spi': (                   # Perpendicular Plasma Beta
            'time_series',                    # Plot type
            [beta_pperp_spi],                 # Data array
            ['beta_pperp_spi'],               # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'$\beta$'],                     # Y-axis label
            [r'$\beta_{p\perp}$'],               # Legend label
            ['green'],                        # Line color
            'log',                            # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'beta_p_spi': (                       # Tot prot Plasma Beta
            'time_series',                    # Plot type
            [beta_p_spi],                     # Data array
            ['beta_p_spi'],                   # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'$\beta$'],                     # Y-axis label
            [r'$\beta_p$'],                   # Legend label
            ['green'],                        # Line color
            'log',                            # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'pressure_ppar_spi': (                # Parallel Proton Pressure
            'time_series',                    # Plot type
            [pressure_ppar_spi],              # Data array
            ['pressure_ppar_spi'],            # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'Pressure \n (nPa)'],              # Y-axis label
            [r'$Press_{p\parallel}$'],               # Legend label
            ['darkviolet'],                   # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'pressure_pperp_spi': (               # Perpendicular Proton Pressure
            'time_series',                    # Plot type
            [pressure_pperp_spi],             # Data array
            ['pressure_pperp_spi'],           # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'Pressure \n (nPa)'],              # Y-axis label
            [r'$Press_{p\perp}$'],                   # Legend label
            ['limegreen'],                    # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'pressure_tot_mag_p': (               # Total mag + Proton Pressure
            'time_series',                    # Plot type
            [pressure_tot_mag_p],             # Data array
            ['pressure_tot_mag_p'],           # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'Pressure \n (nPa)'],              # Y-axis label
            [r'$Press_\{B + P}$'],                # Legend label
            ['black'],                        # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'proton_energy_flux': (               # Proton Energy Flux
            'spectral',                       # Plot type
            [log_spi_nrg_flux],                   # Data array
            ['log_proton_energy_flux'],           # Plotbot Variable name
            times_spi_repeat,                 # Time Array (x-axis)
            [r'P \n Energy \n Flux (eV)'], # Y-axis label
            [r'Proton Energy Flux'],          # Legend label
            None,                             # Line color
            'log',                            # Y-axis scale
            [1e1, 1e5],                       # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            spi_nrg_vals,                     # Additional data (required for spectral plotting)
            'terrain',                            # Spectrogram Colormap
            None,                         # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'proton_theta_flux': (                # Proton Theta Flux
            'spectral',                       # Plot type
            [log_spi_nrg_flux_theta],             # Data array
            ['log_proton_theta_flux'],            # Plotbot Variable name
            times_spi_repeat_angle,           # Time Array (x-axis)
            [r'P $\theta$ flux /n' + r'($^\circ$)'],             # Y-axis label
            [r'Proton Theta Flux'],           # Legend label
            None,                             # Line color
            'linear',                         # Y-axis scale
            [-70,70],                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            spi_nrg_vals_theta,               # Additional data (required for spectral plotting)
            'terrain',                            # Spectrogram Colormap
            None,                         # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'proton_phi_flux': (                  # Proton Phi Flux
            'spectral',                       # Plot type
            [log_spi_nrg_flux_phi],               # Data array
            ['log_proton_phi_flux'],              # Plotbot Variable name
            times_spi_repeat_angle,           # Time Array (x-axis)
            [r'P $\phi$ flux /n' + r'($^\circ$)'],               # Y-axis label
            [r'Proton Phi Flux'],             # Legend label
            [80,190],                             # Line color
            'linear',                         # Y-axis scale
            None,                 # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            spi_nrg_vals_phi,                 # Additional data (required for spectral plotting)
            'terrain',                            # Spectrogram Colormap
            'linear',                         # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'centroids_spi_phi': (                         # Solar Wind Velocity
            'time_series',                    # Plot type
            [centroids_spi_phi],                       # Data array
            ['centroids_spi_phi'],                     # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'deg'],             # Y-axis label
            [r'deg'],                    # Legend label
            ['black'],                          # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['--'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'spi_phi_thresh163': (                         # Solar Wind Velocity
            'time_series',                    # Plot type
            [163.125*np.ones(len(datetime_spi))],                       # Data array
            ['spi_phi_thresh163'],                     # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'deg'],             # Y-axis label
            [r'deg'],                    # Legend label
            ['red'],                          # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'spi_phi_thresh168': (                         # Solar Wind Velocity
            'time_series',                    # Plot type
            [168.75*np.ones(len(datetime_spi))],                       # Data array
            ['spi_phi_thresh168'],                     # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'deg'],             # Y-axis label
            [r'deg'],                    # Legend label
            ['orange'],                          # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'v_sw_spi': (                         # Solar Wind Velocity
            'time_series',                    # Plot type
            [v_sw_spi],                       # Data array
            ['v_sw_spi'],                     # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'$V_{SW}$ \n (km/s)'],             # Y-axis label
            [r'$V_{SW}$'],                    # Legend label
            ['red'],                          # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'M_alfven_spi': (                     # Alfvén Mach Number
            'time_series',                    # Plot type
            [M_alfven_spi],                   # Data array
            ['M_alfven_spi'],                 # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'$M_A$'],                       # Y-axis label
            [r'$M_A$'],                       # Legend label
            ['black'],                        # Line color
            'log',                            # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'pressure_p_spi': (                   # Proton Pressure
            'time_series',                    # Plot type
            [pressure_p_spi],                 # Data array
            ['pressure_p_spi'],               # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'Pressure \n (nPa)'],              # Y-axis label
            [r'$Press_{p}$'],                   # Legend label
            ['cyan'],                         # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'dens_spi': (                         # Proton Density
            'time_series',                    # Plot type
            [dens_spi.y],                     # Data array
            ['dens_spi'],                     # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'Density \n (cm$^{-3}$)'],         # Y-axis label
            [r'$N_{p}$'],                   # Legend label
            ['blue'],                         # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'temp_spi': (                         # Proton Density
            'time_series',                    # Plot type
            [temp_spi.y],                     # Data array
            ['temp_spi'],                     # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'Temp \n (eV)'],         # Y-axis label
            [r'$T_{p}$'],                   # Legend label
            ['orange'],                         # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
         'bmag_spi': (                                    # Magnetic Field Magnitude (measured at the cadence of the protons)
            'time_series',                                # Plot type
            [np.sqrt(np.sum(b_spi.y**2, axis=1))],        # Data array
            ['bmag_spi'],                                 # Plotbot Variable name
            datetime_spi,                                 # Time Array (x-axis)
            [r'|B| \n (nT)'],                                # Y-axis label
            [r'$|B|_{SPI}$'],                             # Legend label
            ['purple'],                                   # Line color
            'linear',                                     # Y-axis scale
            None,                                         # Y-axis limits
            [1],                                          # Line width
            ['-'],                                        # Line style
            None,                                         # Additional data (required for spectral plotting)
            None,                                         # Spectrogram Colormap
            None,                                         # Spectrogram Colorbar scaling
            None                                          # Spectrogram Colorbar limits
        ),
        'velp_RTN_spi': (                                       # Proton velocity in RTN Coordinates 
            'time_series',                                      # Plot type
            [vr, vt, vn],                                       # Data arrays
            ['vr', 'vt', 'vn'],                                 # Plotbot Variable names
            datetime_spi,                                       # Time Array (x-axis)
            [r'Vp \n (km/s)', r'Vp \n (km/s)', r'Vp \n (km/s)'],         # Y-axis labels
            [r'$V_R$', r'$V_T$', r'$V_N$'],                     # Legend labels
            ['forestgreen', 'orange', 'dodgerblue'],            # Line colors
            'linear',                                           # Y-axis scale
            None,                                               # Y-axis limits
            [1, 1, 1],                                          # Line widths
            ['-', '-', '-'],                                    # Line styles
            None,                                               # Additional data (required for spectral plotting)
            None,                                               # Spectrogram Colormap
            None,                                               # Spectrogram Colorbar scaling
            None                                                # Spectrogram Colorbar limits
        ),
        'vr_spi': (                                       # Proton velocity in RTN Coordinates 
            'time_series',                                      # Plot type
            [vr],                                       # Data arrays
            ['vr'],                                 # Plotbot Variable names
            datetime_spi,                                       # Time Array (x-axis)
            [r'Vp \n (km/s)'],         # Y-axis labels
            [r'$V_R$'],                     # Legend labels
            ['forestgreen'],            # Line colors
            'linear',                                           # Y-axis scale
            None,                                               # Y-axis limits
            [1, 1, 1],                                          # Line widths
            ['-', '-', '-'],                                    # Line styles
            None,                                               # Additional data (required for spectral plotting)
            None,                                               # Spectrogram Colormap
            None,                                               # Spectrogram Colorbar scaling
            None                                                # Spectrogram Colorbar limits
        ),
        'vt_spi': (                                       # Proton velocity in RTN Coordinates 
            'time_series',                                      # Plot type
            [vt],                                       # Data arrays
            ['vt'],                                 # Plotbot Variable names
            datetime_spi,                                       # Time Array (x-axis)
            [r'Vp \n (km/s)'],         # Y-axis labels
            [r'$V_T$'],                     # Legend labels
            ['orange'],            # Line colors
            'linear',                                           # Y-axis scale
            None,                                               # Y-axis limits
            [1, 1, 1],                                          # Line widths
            ['-', '-', '-'],                                    # Line styles
            None,                                               # Additional data (required for spectral plotting)
            None,                                               # Spectrogram Colormap
            None,                                               # Spectrogram Colorbar scaling
            None                                                # Spectrogram Colorbar limits
        ),
        'vn_spi': (                                       # Proton velocity in RTN Coordinates 
            'time_series',                                      # Plot type
            [vn],                                       # Data arrays
            ['vn'],                                 # Plotbot Variable names
            datetime_spi,                                       # Time Array (x-axis)
            [r'Vp \n (km/s)'],         # Y-axis labels
            [r'$V_N$'],                     # Legend labels
            ['dodgerblue'],            # Line colors
            'linear',                                           # Y-axis scale
            None,                                               # Y-axis limits
            [1, 1, 1],                                          # Line widths
            ['-', '-', '-'],                                    # Line styles
            None,                                               # Additional data (required for spectral plotting)
            None,                                               # Spectrogram Colormap
            None,                                               # Spectrogram Colorbar scaling
            None                                                # Spectrogram Colorbar limits
        ),
        'sun_dist_rs': (                         # solar distance
            'time_series',                    # Plot type
            [sun_dist_rsun],                     # Data array
            ['sun_dist_rs'],                     # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'Distance \n ($R_S$)'],         # Y-axis label
            [r'$Dist R_S$'],                   # Legend label
            ['blue'],                         # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        )

        #endregion

    }
        
    zipped_data.update(zipped_spi_sf00_mom)
if spi_sf0a_mom is not None:
    zipped_spi_sf0a_mom = {
           #region Protons / SPI Instrument---------------------------------------------------//
        'T_par_sf0a': (                            #Parallel Temperature
            'time_series',                    # Plot type
            [T_parallel_sf0a],                     # Data array
            ['T_parallel_sf0a'],                   # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'Temp \n (eV)'],            # Y-axis label
            [r'$T_{p\parallel}$'],               # Legend label
            ['deepskyblue'],                  # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'T_perp_sf0a': (                           #Perpendicular Temperature
            'time_series',                    # Plot type
            [T_perpendicular_sf0a],                # Data array
            ['T_perpendicular_sf0a'],              # Plotbot Variable name
            datetime_spi,                     # Time Array (x-axis)
            [r'Temp \n (eV)'],            # Y-axis label
            [r'$T_{p\perp}$'],                   # Legend label
            ['hotpink'],                      # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'Anisotropy_sf0a': (                       #Temperature Anisotropy
            'time_series',                    # Plot type
            [Anisotropy_sf0a],                     # Data array
            ['Anisotropy_sf0a'],                   # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'$T_\perp/T_\parallel$'],       # Y-axis label
            [r'$T_\perp/T_\parallel$'],       # Legend label
            ['mediumspringgreen'],            # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'v_alfven_spi_sf0a': (                     # Alfvén velocity
            'time_series',                    # Plot type
            [v_alfven_spi_sf0a],                   # Data array
            ['v_alfven_spi_sf0a'],                 # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'$V_{A}$ (km/s)'],              # Y-axis label
            [r'$V_{A}$'],                     # Legend label
            ['deepskyblue'],                  # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'beta_ppar_spi_sf0a': (                    # Parallel Plasma Beta
            'time_series',                    # Plot type
            [beta_ppar_spi_sf0a],                  # Data array
            ['beta_ppar_spi_sf0a'],                # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'$\beta$'],                     # Y-axis label
            [r'$\beta_{p\parallel}$'],           # Legend label
            ['purple'],                       # Line color
            'log',                            # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'beta_pperp_spi_sf0a': (                   # Perpendicular Plasma Beta
            'time_series',                    # Plot type
            [beta_pperp_spi_sf0a],                 # Data array
            ['beta_pperp_spi_sf0a'],               # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'$\beta$'],                     # Y-axis label
            [r'$\beta_{p\perp}$'],               # Legend label
            ['green'],                        # Line color
            'log',                            # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'beta_p_spi_sf0a': (                       # Tot prot Plasma Beta
            'time_series',                    # Plot type
            [beta_p_spi_sf0a],                     # Data array
            ['beta_p_spi_sf0a'],                   # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'$\beta$'],                     # Y-axis label
            [r'$\beta_a$'],                   # Legend label
            ['green'],                        # Line color
            'log',                            # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'pressure_ppar_spi_sf0a': (                # Parallel Proton Pressure
            'time_series',                    # Plot type
            [pressure_ppar_spi_sf0a],              # Data array
            ['pressure_ppar_spi_sf0a'],            # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'Pressure \n (nPa)'],              # Y-axis label
            [r'$Press_{p\parallel}$'],               # Legend label
            ['darkviolet'],                   # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'pressure_pperp_spi_sf0a': (               # Perpendicular Proton Pressure
            'time_series',                    # Plot type
            [pressure_pperp_spi_sf0a],             # Data array
            ['pressure_pperp_spi_sf0a'],           # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'Pressure \n (nPa)'],              # Y-axis label
            [r'$Press_{p\perp}$'],                   # Legend label
            ['limegreen'],                    # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'pressure_tot_mag_p_sf0a': (               # Total mag + Proton Pressure
            'time_series',                    # Plot type
            [pressure_tot_mag_p_sf0a],             # Data array
            ['pressure_tot_mag_p_sf0a'],           # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'Pressure \n (nPa)'],              # Y-axis label
            [r'$Press_\{B + A}$'],                # Legend label
            ['black'],                        # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'alpha_energy_flux': (               # alpha Energy Flux
            'spectral',                       # Plot type
            [log_spi_sf0a_nrg_flux],                   # Data array
            ['log_alpha_energy_flux'],           # Plotbot Variable name
            times_spi_sf0a_repeat,                 # Time Array (x-axis)
            [r'A \n Energy \n Flux (eV)'], # Y-axis label
            [r'Alpha Energy Flux'],          # Legend label
            None,                             # Line color
            'log',                            # Y-axis scale
            [1e1, 1e5],                       # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            spi_sf0a_nrg_vals,                     # Additional data (required for spectral plotting)
            'terrain',                            # Spectrogram Colormap
            None,                         # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'alpha_theta_flux': (                # alpha Theta Flux
            'spectral',                       # Plot type
            [log_spi_sf0a_nrg_flux_theta],             # Data array
            ['log_alpha_theta_flux'],            # Plotbot Variable name
            times_spi_sf0a_repeat_angle,           # Time Array (x-axis)
            [r'P $\theta$ flux /n' + r'($^\circ$)'],             # Y-axis label
            [r'alpha Theta Flux'],           # Legend label
            None,                             # Line color
            'linear',                         # Y-axis scale
            [-70,70],                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            spi_sf0a_nrg_vals_theta,               # Additional data (required for spectral plotting)
            'terrain',                            # Spectrogram Colormap
            None,                         # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'alpha_phi_flux': (                  # alpha Phi Flux
            'spectral',                       # Plot type
            [log_spi_sf0a_nrg_flux_phi],               # Data array
            ['log_alpha_phi_flux'],              # Plotbot Variable name
            times_spi_sf0a_repeat_angle,           # Time Array (x-axis)
            [r'A $\phi$ flux /n' + r'($^\circ$)'],               # Y-axis label
            [r'alpha Phi Flux'],             # Legend label
            [80,190],                             # Line color
            'linear',                         # Y-axis scale
            None,                 # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            spi_sf0a_nrg_vals_phi,                 # Additional data (required for spectral plotting)
            'terrain',                            # Spectrogram Colormap
            'linear',                         # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'centroids_spi_sf0a_phi': (                         # Solar Wind Velocity
            'time_series',                    # Plot type
            [centroids_spi_sf0a_phi],                       # Data array
            ['centroids_spi_sf0a_phi'],                     # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'deg'],             # Y-axis label
            [r'deg'],                    # Legend label
            ['black'],                          # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['--'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'spi_sf0a_phi_thresh163': (                         # Solar Wind Velocity
            'time_series',                    # Plot type
            [163.125*np.ones(len(datetime_spi_sf0a))],                       # Data array
            ['spi_sf0a_phi_thresh163'],                     # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'deg'],             # Y-axis label
            [r'deg'],                    # Legend label
            ['red'],                          # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'spi_sf0a_phi_thresh168': (                         # Solar Wind Velocity
            'time_series',                    # Plot type
            [168.75*np.ones(len(datetime_spi_sf0a))],                       # Data array
            ['spi_sf0a_phi_thresh168'],                     # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'deg'],             # Y-axis label
            [r'deg'],                    # Legend label
            ['orange'],                          # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'vmag_spi_sf0a': (                         # alpha Velocity
            'time_series',                    # Plot type
            [vmag_sf0a],                       # Data array
            ['vmag_sf0a'],                     # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'$V_{\alpha}$ \n (km/s)'],             # Y-axis label
            [r'$V_{\alpha}$'],                    # Legend label
            ['red'],                          # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'M_alfven_spi_sf0a': (                     # Alfvén Mach Number
            'time_series',                    # Plot type
            [M_alfven_spi_sf0a],                   # Data array
            ['M_alfven_spi_sf0a'],                 # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'$M_A$'],                       # Y-axis label
            [r'$M_A$'],                       # Legend label
            ['black'],                        # Line color
            'log',                            # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'pressure_p_spi_sf0a': (                   # Proton Pressure
            'time_series',                    # Plot type
            [pressure_p_spi_sf0a],                 # Data array
            ['pressure_p_spi_sf0a'],               # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'Pressure \n (nPa)'],              # Y-axis label
            [r'$Press_{a}$'],                   # Legend label
            ['cyan'],                         # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'dens_spi_sf0a': (                         # Proton Density
            'time_series',                    # Plot type
            [dens_spi_sf0a.y],                     # Data array
            ['dens_spi_sf0a'],                     # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'Density \n (cm$^{-3}$)'],         # Y-axis label
            [r'$N_{a}$'],                   # Legend label
            ['blue'],                         # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'temp_spi_sf0a': (                         # Proton Density
            'time_series',                    # Plot type
            [temp_spi_sf0a.y],                     # Data array
            ['temp_spi_sf0a'],                     # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'Temp \n (eV)'],         # Y-axis label
            [r'$T_{a}$'],                   # Legend label
            ['orange'],                         # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
         'bmag_spi_sf0a': (                                    # Magnetic Field Magnitude (measured at the cadence of the protons)
            'time_series',                                # Plot type
            [np.sqrt(np.sum(b_spi_sf0a.y**2, axis=1))],        # Data array
            ['bmag_spi_sf0a'],                                 # Plotbot Variable name
            datetime_spi_sf0a,                                 # Time Array (x-axis)
            [r'|B| \n (nT)'],                                # Y-axis label
            [r'$|B|_{SPI}$'],                             # Legend label
            ['purple'],                                   # Line color
            'linear',                                     # Y-axis scale
            None,                                         # Y-axis limits
            [1],                                          # Line width
            ['-'],                                        # Line style
            None,                                         # Additional data (required for spectral plotting)
            None,                                         # Spectrogram Colormap
            None,                                         # Spectrogram Colorbar scaling
            None                                          # Spectrogram Colorbar limits
        ),
        'velp_RTN_spi_sf0a': (                                       # Proton velocity in RTN Coordinates 
            'time_series',                                      # Plot type
            [vr_sf0a, vt_sf0a, vn_sf0a],                                       # Data arrays
            ['vr_sf0a', 'vt_sf0a', 'vn_sf0a'],                                 # Plotbot Variable names
            datetime_spi_sf0a,                                       # Time Array (x-axis)
            [r'Va \n (km/s)', r'Va \n (km/s)', r'Va \n (km/s)'],         # Y-axis labels
            [r'$V_R$', r'$V_T$', r'$V_N$'],                     # Legend labels
            ['forestgreen', 'orange', 'dodgerblue'],            # Line colors
            'linear',                                           # Y-axis scale
            None,                                               # Y-axis limits
            [1, 1, 1],                                          # Line widths
            ['-', '-', '-'],                                    # Line styles
            None,                                               # Additional data (required for spectral plotting)
            None,                                               # Spectrogram Colormap
            None,                                               # Spectrogram Colorbar scaling
            None                                                # Spectrogram Colorbar limits
        ),
        'vr_spi_sf0a': (                                       # Proton velocity in RTN Coordinates 
            'time_series',                                      # Plot type
            [vr_sf0a],                                       # Data arrays
            ['vr_sf0a'],                                 # Plotbot Variable names
            datetime_spi_sf0a,                                       # Time Array (x-axis)
            [r'Va \n (km/s)'],         # Y-axis labels
            [r'$V_R$'],                     # Legend labels
            ['forestgreen'],            # Line colors
            'linear',                                           # Y-axis scale
            None,                                               # Y-axis limits
            [1, 1, 1],                                          # Line widths
            ['-', '-', '-'],                                    # Line styles
            None,                                               # Additional data (required for spectral plotting)
            None,                                               # Spectrogram Colormap
            None,                                               # Spectrogram Colorbar scaling
            None                                                # Spectrogram Colorbar limits
        ),
        'vt_spi_sf0a': (                                       # Proton velocity in RTN Coordinates 
            'time_series',                                      # Plot type
            [vt_sf0a],                                       # Data arrays
            ['vt_sf0a'],                                 # Plotbot Variable names
            datetime_spi_sf0a,                                       # Time Array (x-axis)
            [r'Va \n (km/s)'],         # Y-axis labels
            [r'$V_T$'],                     # Legend labels
            ['orange'],            # Line colors
            'linear',                                           # Y-axis scale
            None,                                               # Y-axis limits
            [1, 1, 1],                                          # Line widths
            ['-', '-', '-'],                                    # Line styles
            None,                                               # Additional data (required for spectral plotting)
            None,                                               # Spectrogram Colormap
            None,                                               # Spectrogram Colorbar scaling
            None                                                # Spectrogram Colorbar limits
        ),
        'vn_spi_sf0a': (                                       # Proton velocity in RTN Coordinates 
            'time_series',                                      # Plot type
            [vn_sf0a],                                       # Data arrays
            ['vn_sf0a'],                                 # Plotbot Variable names
            datetime_spi_sf0a,                                       # Time Array (x-axis)
            [r'Va \n (km/s)'],         # Y-axis labels
            [r'$V_N$'],                     # Legend labels
            ['dodgerblue'],            # Line colors
            'linear',                                           # Y-axis scale
            None,                                               # Y-axis limits
            [1, 1, 1],                                          # Line widths
            ['-', '-', '-'],                                    # Line styles
            None,                                               # Additional data (required for spectral plotting)
            None,                                               # Spectrogram Colormap
            None,                                               # Spectrogram Colorbar scaling
            None                                                # Spectrogram Colorbar limits
        ),
        'sun_dist_sf0a_rs': (                         # solar distance
            'time_series',                    # Plot type
            [sun_dist_sf0a_rsun],                     # Data array
            ['sun_dist_sf0a_rs'],                     # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'Distance \n ($R_S$)'],         # Y-axis label
            [r'$Dist R_S$'],                   # Legend label
            ['blue'],                         # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        )

        #endregion

    }
        
    zipped_data.update(zipped_spi_sf0a_mom)
if (spi_sf00_mom and spi_sf0a_mom) is not None:
    zipped_spi_sf00_sf0a_mom = {
           #region Protons / SPI Instrument---------------------------------------------------//
        'Na/Np': (                            #Parallel Temperature
            'time_series',                    # Plot type
            [na_div_np],                     # Data array
            ['Na/Np'],                   # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'Na/Np'],            # Y-axis label
            [r'$Na/Np$'],               # Legend label
            ['deepskyblue'],                  # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'vdrift_ap': (                           #a-p drift
            'time_series',                    # Plot type
            [vdrift_ap],                # Data array
            ['vdrift_ap'],              # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'vdrift\n (km/s)'],            # Y-axis label
            [r'$vdrift_{\alpha,p}$'],                   # Legend label
            ['hotpink'],                      # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        '|vdrift_ap|': (                           #a-p drift
            'time_series',                    # Plot type
            [np.abs(vdrift_ap)],                # Data array
            ['|vdrift_ap|'],              # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'|vdrift|\n (km/s)'],            # Y-axis label
            [r'$|vdrift|_{\alpha,p}$'],                   # Legend label
            ['hotpink'],                      # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'vdrift_ap_va': (                           #a-p drift
            'time_series',                    # Plot type
            [vdrift_ap_va],                # Data array
            ['vdrift_ap_va'],              # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'vdrift/vA'],            # Y-axis label
            [r'$vdrift/vA_{\alpha,p}$'],                   # Legend label
            ['hotpink'],                      # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        '|vdrift|_ap_va': (                           #a-p drift
            'time_series',                    # Plot type
            [np.abs(vdrift_ap_va)],                # Data array
            ['|vdrift|_ap_va'],              # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'|vdrift|/vA|'],            # Y-axis label
            [r'$|vdrift/vA|_{\alpha,p}$'],                   # Legend label
            ['hotpink'],                      # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        ),
        'Ta/Tp': (                           #a-p drift
            'time_series',                    # Plot type
            [ta_div_tp],                # Data array
            ['Ta/Tp'],              # Plotbot Variable name
            datetime_spi_sf0a,                     # Time Array (x-axis)
            [r'Ta/Tp'],            # Y-axis label
            [r'$Ta/Tp$'],                   # Legend label
            ['hotpink'],                      # Line color
            'linear',                         # Y-axis scale
            None,                             # Y-axis limits
            [1],                              # Line width
            ['-'],                            # Line style
            None,                             # Additional data (required for spectral plotting)
            None,                             # Spectrogram Colormap
            None,                             # Spectrogram Colorbar scaling
            None                              # Spectrogram Colorbar limits
        )
       
    }
            
        
    zipped_data.update(zipped_spi_sf00_sf0a_mom)
if spe_sf0_pad is not None:
    zipped_spe_sf0_pads = {
            #region Electron PAD's / SPE Instrument---------------------------------------------------//
    # Electron PADs
    'epad_strahl': (                      # Electron Pitch Angle Distribution
        'spectral',                       # Plot type
        [log_epad_strahl],                # Data array
        ['log_epad_strahl'],              # Plotbot Variable name
        times_spe_repeat,                 # Time Array (x-axis)
        [r'E Strahl \n PAD' + r'($^\circ$)'],    # Y-axis label
        [r'Electron PAD'],                # Legend label
        None,                             # Line color (set to None for spectral plots)
        'linear',                         # Y-axis scale
        None,                             # Y-axis limits
        [1],                              # Line width
        ['-'],                            # Line style
        epad_PA_vals,                     # Additional data (required for spectral plotting)
        'gist_stern',                            # Spectrogram Colormap
        None,                            # Spectrogram Colorbar scaling
        None                       # Spectrogram Colorbar limits
    ),
    'centroids_epad': (                         # solar distance
        'time_series',                    # Plot type
        [centroids_epad],                     # Data array
        ['centroids_epad'],                     # Plotbot Variable name
        datetime_spe,                     # Time Array (x-axis)
        [r'ePAD centroids'],         # Y-axis label
        [r'ePAD centroids'],                   # Legend label
        ['k'],                         # Line color
        'linear',                         # Y-axis scale
        None,                             # Y-axis limits
        [1],                              # Line width
        ['--'],                            # Line style
        None,                             # Additional data (required for spectral plotting)
        None,                             # Spectrogram Colormap
        None,                             # Spectrogram Colorbar scaling
        None                              # Spectrogram Colorbar limits
    )
    }
    #endregion
    zipped_data.update(zipped_spe_sf0_pads)
if wvpow is not None:
    zipped_wavpow_data = {
                   #region wavePow ---------------------------------------------------//
        # KP wavepow
    'wvpow_LH': (                                        # Magnetic Field Components in RTN Coordinates (4 samples per cycle = ~4.57 S/s)
        'scatter',                                       # Plot type
        # 'psp_fld_l2_mag_rtn_4_sa_per_cyc',                  # CDF variable name ⭐️
        [wvpow_LH],                                         # Data arrays
        ['wvpow_LH'],                                       # Plotbot Variable names
        datetime_wvpow,                               # Time Array (x-axis)
        r'Wave Power',                                    # Y-axis labels
        [r'WvPow (LH)'],                                    # Legend labels
        ['royalblue'],                                           # Line colors
        [(5, 1)],                                           # marker_styles
        [5],                                                # marker_sizes
        [0.7],                                              # alphas
        'log',                                              # y_scale
        None                                                 # y_lim
    ),
    'wvpow_RH': (                                        # Magnetic Field Components in RTN Coordinates (4 samples per cycle = ~4.57 S/s)
        'scatter',                                       # Plot type
        # 'psp_fld_l2_mag_rtn_4_sa_per_cyc',                  # CDF variable name ⭐️
        [wvpow_RH],                                         # Data arrays
        ['wvpow_RH'],                                       # Plotbot Variable names
        datetime_wvpow,                               # Time Array (x-axis)
        r'Wave Power',                                    # Y-axis labels
        [r'WvPow (RH)'],                                    # Legend labels
        ['maroon'],                                           # Line colors
        [(5, 1)],                                           # marker_styles
        [5],                                                # marker_sizes
        [0.7],                                              # alphas
        'log',                                              # y_scale
        None                                                 # y_lim
    )
    }

    zipped_data.update(zipped_wavpow_data)
    
    zipped_wv_hist_data = {
    'wvpow_RH_hist_20m': (               # Proton Energy Flux
        'spectral',                       # Plot type
        [h_RH_20m.T],                   # Data array
        ['h_RH_20m'],           # Plotbot Variable name
        times_RH_repeat_20m,                 # Time Array (x-axis)
        [r'wvpow RH'], # Y-axis label
        [r'wvpow RH_20m'],          # Legend label
        None,                             # Line color
        'log',                            # Y-axis scale
        [1e-3, 2e2],                       # Y-axis limits
        [1],                              # Line width
        ['-'],                            # Line style
        ydat_RH_repeat_20m,                     # Additional data (required for spectral plotting)
        'hot',                            # Spectrogram Colormap
        None,                         # Spectrogram Colorbar scaling
        [0,1e-5]                            # Spectrogram Colorbar limits
    ),       
    'wvpow_LH_hist_20m':(               # Proton Energy Flux
        'spectral',                       # Plot type
        [h_LH_20m.T],                   # Data array
        ['h_LH_20m'],           # Plotbot Variable name
        times_LH_repeat_20m,                 # Time Array (x-axis)
        [r'wvpow LH'], # Y-axis label
        [r'wvpow LH_20m'],          # Legend label
        None,                             # Line color
        'log',                            # Y-axis scale
        [1e-3, 1e2],                       # Y-axis limits
        [1],                              # Line width
        ['-'],                            # Line style
        ydat_LH_repeat_20m,                     # Additional data (required for spectral plotting)
        'Blues',                            # Spectrogram Colormap
        None,                         # Spectrogram Colorbar scaling
        None                              # Spectrogram Colorbar limits
    ),
    'centroids_RH_20m':(                    # histogram of hamstrings
        'time_series',                 # Plot type
        [centroids_RH_20m],                  # Data array
        ['centroids_RH_20m'],                # Plotbot Variable name
        bin_centers_datetime_utc_RH_20m,          # Time Array (x-axis)
        [r'Centroids_RH'],                   # Y-axis label
        [r'Centroids_RH_20m'],                    # Legend label
        ['orange'],               # Line color
        'log',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['--'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'centroids_LH_20m':(                    # histogram of hamstrings
        'time_series',                 # Plot type
        [centroids_LH_20m],                  # Data array
        ['centroids_RH_20m'],                # Plotbot Variable name
        bin_centers_datetime_utc_LH_20m,          # Time Array (x-axis)
        [r'Centroids_LH'],                   # Y-axis label
        [r'Centroids_LH_20m'],                    # Legend label
        ['purple'],               # Line color
        'log',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['--'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'wvpow_RH_hist_90m':(               # Proton Energy Flux
        'spectral',                       # Plot type
        [h_RH_90m.T],                   # Data array
        ['h_RH_90m'],           # Plotbot Variable name
        times_RH_repeat_90m,                 # Time Array (x-axis)
        [r'wvpow RH'], # Y-axis label
        [r'wvpow RH_90m'],          # Legend label
        None,                             # Line color
        'log',                            # Y-axis scale
        [1e-3, 2e2],                       # Y-axis limits
        [1],                              # Line width
        ['-'],                            # Line style
        ydat_RH_repeat_90m,                     # Additional data (required for spectral plotting)
        'hot',                            # Spectrogram Colormap
        None,                         # Spectrogram Colorbar scaling
        [0,1e-5]                            # Spectrogram Colorbar limits
    ),
    'wvpow_LH_hist_90m':(               # Proton Energy Flux
        'spectral',                       # Plot type
        [h_LH_90m.T],                   # Data array
        ['h_LH_90m'],           # Plotbot Variable name
        times_LH_repeat_90m,                 # Time Array (x-axis)
        [r'wvpow LH'], # Y-axis label
        [r'wvpow LH_90m'],          # Legend label
        None,                             # Line color
        'log',                            # Y-axis scale
        [1e-3, 1e2],                       # Y-axis limits
        [1],                              # Line width
        ['-'],                            # Line style
        ydat_LH_repeat_90m,                     # Additional data (required for spectral plotting)
        'Blues',                            # Spectrogram Colormap
        None,                         # Spectrogram Colorbar scaling
        None                              # Spectrogram Colorbar limits
    ),
    'centroids_RH_90m':(                    # histogram of hamstrings
        'time_series',                 # Plot type
        [centroids_RH_90m],                  # Data array
        ['centroids_RH_90m'],                # Plotbot Variable name
        bin_centers_datetime_utc_RH_90m,          # Time Array (x-axis)
        [r'Centroids_RH'],                   # Y-axis label
        [r'Centroids_RH_90m'],                    # Legend label
        ['orange'],               # Line color
        'log',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['--'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'centroids_LH_90m':(                    # histogram of hamstrings
        'time_series',                 # Plot type
        [centroids_LH_90m],                  # Data array
        ['centroids_RH_90m'],                # Plotbot Variable name
        bin_centers_datetime_utc_LH_90m,          # Time Array (x-axis)
        [r'Centroids_LH'],                   # Y-axis label
        [r'Centroids_LH_90m'],                    # Legend label
        ['purple'],               # Line color
        'log',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['--'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    
    'wvpow_RH_hist_4h':(               # Proton Energy Flux
        'spectral',                       # Plot type
        [h_RH_4h.T],                   # Data array
        ['h_RH_4h'],           # Plotbot Variable name
        times_RH_repeat_4h,                 # Time Array (x-axis)
        [r'wvpow RH'], # Y-axis label
        [r'wvpow RH_4h'],          # Legend label
        None,                             # Line color
        'log',                            # Y-axis scale
        [1e-3, 2e2],                       # Y-axis limits
        [1],                              # Line width
        ['-'],                            # Line style
        ydat_RH_repeat_4h,                     # Additional data (required for spectral plotting)
        'hot',                            # Spectrogram Colormap
        None,                         # Spectrogram Colorbar scaling
        [0,1e-5]                            # Spectrogram Colorbar limits
    ),
    'wvpow_LH_hist_4h':(               # Proton Energy Flux
        'spectral',                       # Plot type
        [h_LH_4h.T],                   # Data array
        ['h_LH_4h'],           # Plotbot Variable name
        times_LH_repeat_4h,                 # Time Array (x-axis)
        [r'wvpow LH'], # Y-axis label
        [r'wvpow LH_4h'],          # Legend label
        None,                             # Line color
        'log',                            # Y-axis scale
        [1e-3, 1e2],                       # Y-axis limits
        [1],                              # Line width
        ['-'],                            # Line style
        ydat_LH_repeat_4h,                     # Additional data (required for spectral plotting)
        'Blues',                            # Spectrogram Colormap
        None,                         # Spectrogram Colorbar scaling
        None                              # Spectrogram Colorbar limits
    ),
    'centroids_RH_4h':(                    # histogram of hamstrings
        'time_series',                 # Plot type
        [centroids_RH_4h],                  # Data array
        ['centroids_RH_4h'],                # Plotbot Variable name
        bin_centers_datetime_utc_RH_4h,          # Time Array (x-axis)
        [r'Centroids_RH'],                   # Y-axis label
        [r'Centroids_RH_4h'],                    # Legend label
        ['orange'],               # Line color
        'log',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['--'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'centroids_LH_4h':(                    # histogram of hamstrings
        'time_series',                 # Plot type
        [centroids_LH_4h],                  # Data array
        ['centroids_RH_4h'],                # Plotbot Variable name
        bin_centers_datetime_utc_LH_4h,          # Time Array (x-axis)
        [r'Centroids_LH'],                   # Y-axis label
        [r'Centroids_LH_4h'],                    # Legend label
        ['purple'],               # Line color
        'log',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['--'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'wvpow_RH_hist_12h':(               # Proton Energy Flux
        'spectral',                       # Plot type
        [h_RH_12h.T],                   # Data array
        ['h_RH_12h'],           # Plotbot Variable name
        times_RH_repeat_12h,                 # Time Array (x-axis)
        [r'wvpow RH'], # Y-axis label
        [r'wvpow RH_12h'],          # Legend label
        None,                             # Line color
        'log',                            # Y-axis scale
        [1e-3, 2e2],                       # Y-axis limits
        [1],                              # Line width
        ['-'],                            # Line style
        ydat_RH_repeat_12h,                     # Additional data (required for spectral plotting)
        'hot',                            # Spectrogram Colormap
        None,                         # Spectrogram Colorbar scaling
        [0,1e-5]                            # Spectrogram Colorbar limits
    ),
    'wvpow_LH_hist_12h':(               # Proton Energy Flux
        'spectral',                       # Plot type
        [h_LH_12h.T],                   # Data array
        ['h_LH_12h'],           # Plotbot Variable name
        times_LH_repeat_12h,                 # Time Array (x-axis)
        [r'wvpow LH'], # Y-axis label
        [r'wvpow LH_12h'],          # Legend label
        None,                             # Line color
        'log',                            # Y-axis scale
        [1e-3, 1e2],                       # Y-axis limits
        [1],                              # Line width
        ['-'],                            # Line style
        ydat_LH_repeat_12h,                     # Additional data (required for spectral plotting)
        'Blues',                            # Spectrogram Colormap
        None,                         # Spectrogram Colorbar scaling
        None                              # Spectrogram Colorbar limits
    ),
    'centroids_RH_12h':(                    # histogram of hamstrings
        'time_series',                 # Plot type
        [centroids_RH_12h],                  # Data array
        ['centroids_RH_12h'],                # Plotbot Variable name
        bin_centers_datetime_utc_RH_12h,          # Time Array (x-axis)
        [r'Centroids_RH'],                   # Y-axis label
        [r'Centroids_RH_12h'],                    # Legend label
        ['orange'],               # Line color
        'log',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['--'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'centroids_LH_12h':(                    # histogram of hamstrings
        'time_series',                 # Plot type
        [centroids_LH_12h],                  # Data array
        ['centroids_RH_12h'],                # Plotbot Variable name
        bin_centers_datetime_utc_LH_12h,          # Time Array (x-axis)
        [r'Centroids_LH'],                   # Y-axis label
        [r'Centroids_LH_12h'],                    # Legend label
        ['purple'],               # Line color
        'log',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['--'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
   
  #  'wvpow_RH_med_20m': (                    # histogram of hamstrings
  #      'scatter',                 # Plot type
  #      [wvpow_RH_med],                  # Data array
  #      ['wvpow_RH_med_20m'],                # Plotbot Variable name
  #      bin_centers_datetime_utc_RH,          # Time Array (x-axis)
  #      'wvpow_RH_med',                   # Y-axis label
  #      [r'wvpow_RH_med_20m'],                    # Legend label
  #      ['maroon'],               # Line color
   #     [(5, 1)],                 # marker_styles (Star marker)
  #      [20],                     # marker_sizes
  #      [0.2],                    # alphas
  #      'linear',                                      # Y-axis scale
  # #     None,                                          # Y-axis limits
  #  )
    }

    zipped_data.update(zipped_wv_hist_data)

if sf00_fits is not None:
                   #------Adding our FITS data------//

    zipped_sf00_fits = {
    'qz_p': (                     # heat flux of the proton beam
        'scatter',                # plot_type
        [qz_p],                   # data_arrays
        ['qz_p'],                 # variable_names
        datetime_array,           # time_array
        r'$q_{z,p}$ (W/m$^2$)',   # y_label (Heat flux of proton beam)
        [r'$q_{z,p}$'],           # legend_labels
        ['blueviolet'],           # colors
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vsw_mach_pfits': (           # solar wind Mach number
        'scatter',                # plot_type
        [vsw_mach_pfits],         # data_arrays
        ['vsw_mach_pfits'],       # variable_names
        datetime_array,           # time_array
        r'$V_{sw}/V_A$',          # y_label
        [r'$V_{sw}/V_A$'],        # legend_labels
        ['gold'],                 # colors
        [(5, 1)],                 # marker_styles
        [20],                     # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'beta_ppar_pfits': (          # total Proton parallel beta
        'scatter',                # plot_type
        [beta_ppar_pfits],        # data_arrays
        ['beta_ppar_pfits'],      # variable_names
        datetime_array,           # time_array
        r'$\beta_{\parallel,p}$', # y_label
        [r'$\beta_{\parallel,p}$'], # legend_labels
        ['hotpink'],              # colors
        [(5, 1)],                 # marker_styles
        [20],                     # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'beta_pperp_pfits': (         # total Proton perpendicular beta
        'scatter',                # plot_type
        [beta_pperp_pfits],       # data_arrays
        ['beta_pperp_pfits'],     # variable_names
        datetime_array,           # time_array
        r'$\beta_{\perp,p}$',     # y_label
        [r'$\beta_{\perp,p}$'],   # legend_labels
        ['lightskyblue'],         # colors
        [(5, 1)],                 # marker_styles
        [20],                     # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'ham_param': (                # hammerhead parameter
        'scatter',                # plot_type
        [ham_param],              # data_arrays
        ['ham_param'],            # variable_names
        datetime_array,           # time_array
        'Hamplitude',             # y_label
        ['Hamplitude'],           # legend_labels
        ['palevioletred'],        # colors
        [(5, 1)],                 # marker_styles
        [20],                     # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'np1': (                      # core density
        'scatter',                # plot_type
        [np1],                    # data_arrays
        ['np1'],                  # variable_names
        datetime_array,           # time_array
        r'Density (cm$^{-3}$)',   # y_label
        [r'$n_{p1}$'],            # legend_labels
        ['hotpink'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'np2': (                      # beam density
        'scatter',                # plot_type
        [np2],                    # data_arrays
        ['np2'],                  # variable_names
        datetime_array,           # time_array
        r'Density (cm$^{-3}$)',   # y_label
        [r'$n_{p2}$'],            # legend_labels
        ['deepskyblue'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'np1_delta': (                      # core density uncertainty
        'scatter',                # plot_type
        [np1_dpar],                    # data_arrays
        ['np1_delta'],                  # variable_names
        datetime_array,           # time_array
        r'$\delta N$ (cm$^{-3}$)',   # y_label
        [r'$\delta n_{p1}$'],            # legend_labels
        ['orange'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'np2_delta': (                      # beam density uncertainty
        'scatter',                # plot_type
        [np2_dpar],                    # data_arrays
        ['np2_delta'],                  # variable_names
        datetime_array,           # time_array
        r'$\delta N$ (cm$^{-3}$)',   # y_label
        [r'$\delta n_{p2}$'],            # legend_labels
        ['mediumseagreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'np1_delta/np1': (                      # core density uncertainty
        'scatter',                # plot_type
        [np1_dpar/np1],                    # data_arrays
        ['np1_delta/np1'],                  # variable_names
        datetime_array,           # time_array
        r'$\delta N/N$',   # y_label
        [r'$\delta n_{p1}/n_{p1}$'],            # legend_labels
        ['orange'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'np2_delta/np2': (                      # beam density uncertainty
        'scatter',                # plot_type
        [np2_dpar/np2],                    # data_arrays
        ['np2_delta/np2'],                  # variable_names
        datetime_array,           # time_array
        r'$\delta N/N$',   # y_label
        [r'$\delta n_{p2}/n_{p2}$'],            # legend_labels
        ['mediumseagreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'n_tot': (                      # total beam+core density
        'scatter',                # plot_type
        [n_tot],                    # data_arrays
        ['n_tot'],                  # variable_names
        datetime_array,           # time_array
        r'Density (cm$^{-3}$)',   # y_label
        [r'$n_{ptot}$'],            # legend_labels
        ['deepskyblue'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'np2/np1': (                      # beam density
        'scatter',                # plot_type
        [np2/np1],                    # data_arrays
        ['np2/np1'],                  # variable_names
        datetime_array,           # time_array
        r'$\frac{n_{p2}}{n_{p1}}$)',   # y_label
        [r'$\frac{n_{p2}}{n_{p1}}$'],            # legend_labels
        ['deepskyblue'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vp1_x': (                    # core velocity x
        'scatter',                # plot_type
        [vp1_x],                  # data_arrays
        ['vp1_x'],                # variable_names
        datetime_array,           # time_array
        r'Velocity (km/s)',       # y_label
        [r'$vx_{p1}$'],           # legend_labels
        ['forestgreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vp1_y': (                    # core velocity y
        'scatter',                # plot_type
        [vp1_y],                  # data_arrays
        ['vp1_y'],                # variable_names
        datetime_array,           # time_array
        r'Velocity (km/s)',       # y_label
        [r'$vy_{p1}$'],           # legend_labels
        ['orange'],               # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vp1_z': (                    # core velocity z
        'scatter',                # plot_type
        [vp1_z],                  # data_arrays
        ['vp1_z'],                # variable_names
        datetime_array,           # time_array
        r'Velocity (km/s)',       # y_label
        [r'$vz_{p1}$'],           # legend_labels
        ['dodgerblue'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vp1_x_delta': (                    # core velocity x uncertainty
        'scatter',                # plot_type
        [vp1_x_dpar],                  # data_arrays
        ['vp1_x_delta'],                # variable_names
        datetime_array,           # time_array
        r'$\delta V$ (km/s)',       # y_label
        [r'$\delta vx_{p1}$'],           # legend_labels
        ['forestgreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vp1_y_delta': (                    # core velocity y uncertainty
        'scatter',                # plot_type
        [vp1_y_dpar],                  # data_arrays
        ['vp1_y_delta'],                # variable_names
        datetime_array,           # time_array
        r'$\delta V$ (km/s)',       # y_label
        [r'$\delta vy_{p1}$'],           # legend_labels
        ['orange'],               # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vp1_z_delta': (                    # core velocity z uncertainty
        'scatter',                # plot_type
        [vp1_z_dpar],                  # data_arrays
        ['vp1_z_delta'],                # variable_names
        datetime_array,           # time_array
        r'$\delta V$ (km/s)',       # y_label
        [r'$\delta vz_{p1}$'],           # legend_labels
        ['dodgerblue'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vp1_x_delta/vp1_x': (                    # core velocity x uncertainty
        'scatter',                # plot_type
        [vp1_x_dpar/vp1_x],                  # data_arrays
        ['vp1_x_delta/vp1_x'],                # variable_names
        datetime_array,           # time_array
        r'$\delta V/V$',       # y_label
        [r'$\delta vx_{p1}/vx_{p1}$'],           # legend_labels
        ['forestgreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vp1_y_delta/vp1_y': (                    # core velocity y uncertainty
        'scatter',                # plot_type
        [vp1_y_dpar/vp1_y],                  # data_arrays
        ['vp1_y_delta/vp1_y'],                # variable_names
        datetime_array,           # time_array
        r'$\delta V/V$',       # y_label
        [r'$\delta vy_{p1}/vy_{p1}$'],           # legend_labels
        ['orange'],               # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vp1_z_delta/vp1_z': (                    # core velocity z uncertainty
        'scatter',                # plot_type
        [vp1_z_dpar/vp1_z],                  # data_arrays
        ['vp1_z_delta/vp1_z'],                # variable_names
        datetime_array,           # time_array
        r'$\delta V/V$',       # y_label
        [r'$\delta vz_{p1}/vz_{p1}$'],           # legend_labels
        ['dodgerblue'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vp1_mag': (                    # core velocity mag
        'scatter',                # plot_type
        [vp1_mag],                  # data_arrays
        ['vp1_mag'],                # variable_names
        datetime_array,           # time_array
        r'Velocity (km/s)',       # y_label
        [r'$vmag_{p1}$'],           # legend_labels
        ['dodgerblue'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vp1_mag_delta': (                    # core velocity mag uncertainty
        'scatter',                # plot_type
        [vp1_mag_dpar],                  # data_arrays
        ['vp1_mag_delta'],                # variable_names
        datetime_array,           # time_array
        r'$\delta V$ (km/s)',       # y_label
        [r'$\delta vmag_{p1}$'],           # legend_labels
        ['orange'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vp1_mag_delta/vp1_mag': (                    # core velocity mag uncertainty
        'scatter',                # plot_type
        [vp1_mag_dpar/vp1_mag],                  # data_arrays
        ['vp1_mag_delta/vp1_mag'],                # variable_names
        datetime_array,           # time_array
        r'$\delta V/V$',       # y_label
        [r'$\delta |V_{p1}|/|V_{p1}|$'],           # legend_labels
        ['orange'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vcm_x': (                    # cm velocity x
        'scatter',                # plot_type
        [vcm_x],                  # data_arrays
        ['vcm_x'],                # variable_names
        datetime_array,           # time_array
        r'Velocity (km/s)',       # y_label
        [r'$vx_{cm}$'],           # legend_labels
        ['forestgreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vcm_y': (                    # cm velocity y
        'scatter',                # plot_type
        [vcm_y],                  # data_arrays
        ['vcm_y'],                # variable_names
        datetime_array,           # time_array
        r'Velocity (km/s)',       # y_label
        [r'$vy_{cm}$'],           # legend_labels
        ['orange'],               # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vcm_z': (                    # cm velocity z
        'scatter',                # plot_type
        [vcm_z],                  # data_arrays
        ['vcm_z'],                # variable_names
        datetime_array,           # time_array
        r'Velocity (km/s)',       # y_label
        [r'$vz_{cm}$'],           # legend_labels
        ['dodgerblue'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vcm_mag': (                    # cm velocity mag
        'scatter',                # plot_type
        [vcm_mag],                  # data_arrays
        ['vcm_mag'],                # variable_names
        datetime_array,           # time_array
        r'Velocity (km/s)',       # y_label
        [r'$vmag_{cm}$'],           # legend_labels
        ['dodgerblue'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vdrift': (          #  drift speed
        'scatter',                # plot_type
        [vdrift],        # data_arrays
        ['vdrift'],      # variable_names
        datetime_array,           # time_array
        r'$V_{drift}$',       # y_label
        [r'$vdrift_{p2}$'],    # legend_labels
        ['navy'],                 # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vdrift_delta': (          #  drift speed uncertainty
        'scatter',                # plot_type
        [vdrift_dpar],        # data_arrays
        ['vdrift_delta'],      # variable_names
        datetime_array,           # time_array
        r'$\delta V_{drift}$',       # y_label
        [r'$\delta vdrift_{p2}$'],    # legend_labels
        ['navy'],                 # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    '|vdrift|': (          #  |drift speed| uncertainty
        'scatter',                # plot_type
        [np.abs(vdrift)],        # data_arrays
        ['|vdrift|'],      # variable_names
        datetime_array,           # time_array
        r'$|V_{drift}|$',       # y_label
        [r'$|vdrift_{p2}|$'],    # legend_labels
        ['navy'],                 # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    '|vdrift|_delta': (          #  |drift speed| uncertainty
        'scatter',                # plot_type
        [np.abs(vdrift_dpar)],        # data_arrays
        ['|vdrift|_delta'],      # variable_names
        datetime_array,           # time_array
        r'$\delta |V_{drift}|$',       # y_label
        [r'$\delta |vdrift_{p2}|$'],    # legend_labels
        ['navy'],                 # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    '|vdrift|_delta/|vdrift|': (          #  |drift speed| uncertainty
        'scatter',                # plot_type
        [np.abs(vdrift_dpar)/np.abs(vdrift)],        # data_arrays
        ['|vdrift|_delta/|vdrift|'],      # variable_names
        datetime_array,           # time_array
        r'$\delta |V_{drift}|/|V_{drift}|$',       # y_label
        [r'$\delta |vdrift_{p2}|/|vdrift_{p2}|$'],    # legend_labels
        ['navy'],                 # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vdrift_va_pfits': (          # normalized drift speed
        'scatter',                # plot_type
        [vdrift_va_pfits],        # data_arrays
        ['vdrift_va_pfits'],      # variable_names
        datetime_array,           # time_array
        r'$V_{drift}/V_A$',       # y_label
        [r'$vdrift_{p2}/vA$'],    # legend_labels
        ['navy'],                 # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Trat1': (                    # Temperature anisotropy of the core
        'scatter',                # plot_type
        [Trat1],                  # data_arrays
        ['Trat1'],                # variable_names
        datetime_array,           # time_array
        r'$T_{\perp}/T_{\parallel}$', # y_label
        [r'$T_{\perp}/T_{\parallel,p1}$'], # legend_labels
        ['hotpink'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Trat2': (                    # Temperature anisotropy of the beam
        'scatter',                # plot_type
        [Trat2],                  # data_arrays
        ['Trat2'],                # variable_names
        datetime_array,           # time_array
        r'$T_{\perp}/T_{\parallel}$', # y_label
        [r'$T_{\perp}/T_{\parallel,p2}$'], # legend_labels
        ['deepskyblue'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Trat1_delta': (                    # Temperature anisotropy of the core uncertainty
        'scatter',                # plot_type
        [Trat1_dpar],                  # data_arrays
        ['Trat1_delta'],                # variable_names
        datetime_array,           # time_array
        r'$\delta T_{\perp}/T_{\parallel}$', # y_label
        [r'$\delta T_{\perp}/T_{\parallel,p1}$'], # legend_labels
        ['orange'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Trat2_delta': (                    # Temperature anisotropy of the beam uncertainty
        'scatter',                # plot_type
        [Trat2_dpar],                  # data_arrays
        ['Trat2_delta'],                # variable_names
        datetime_array,           # time_array
        r'$\delta T_{\perp}/T_{\parallel}$', # y_label
        [r'$\delta T_{\perp}/T_{\parallel,p2}$'], # legend_labels
        ['mediumseagreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Trat1_delta/Trat1': (                    # Temperature anisotropy of the core uncertainty
        'scatter',                # plot_type
        [Trat1_dpar/Trat1],                  # data_arrays
        ['Trat1_delta/Trat1'],                # variable_names
        datetime_array,           # time_array
        r'$\delta \frac{T_{\perp}/T_{\parallel}}/{T_{\perp}/T_{\parallel}}$', # y_label
        [r'$\delta \frac{T_{\perp}/T_{\parallel,p1}}{T_{\perp}/T_{\parallel,p1}}$'], # legend_labels
        ['orange'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Trat2_delta/Trat2': (                    # Temperature anisotropy of the core uncertainty
        'scatter',                # plot_type
        [Trat2_dpar/Trat2],                  # data_arrays
        ['Trat2_delta/Trat2'],                # variable_names
        datetime_array,           # time_array
        r'$\delta \frac{T_{\perp}/T_{\parallel}}/{T_{\perp}/T_{\parallel}}$', # y_label
        [r'$\delta \frac{T_{\perp}/T_{\parallel,p2}}{T_{\perp}/T_{\parallel,p2}}$'], # legend_labels
        ['orange'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Trat_tot': (                 # Total temperature anisotropy
        'scatter',                # plot_type
        [Trat_tot],               # data_arrays
        ['Trat_tot'],             # variable_names
        datetime_array,           # time_array
        r'$T_\perp/T_\parallel$', # y_label
        [r'$T_\perp/T_\parallel$'], # legend_labels
        ['mediumspringgreen'],    # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tpar1': (                    # Temperature par of the core
        'scatter',                # plot_type
        [Tpar1],                  # data_arrays
        ['Tpar1'],                # variable_names
        datetime_array,           # time_array
        r'$T_{\parallel}$', # y_label
        [r'$T_{\parallel,p1}$'], # legend_labels
        ['hotpink'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tpar2': (                    # Temperature par of the beam
        'scatter',                # plot_type
        [Tpar2],                  # data_arrays
        ['Tpar2'],                # variable_names
        datetime_array,           # time_array
        r'$T_{\parallel}$', # y_label
        [r'$T_{\parallel,p2}$'], # legend_labels
        ['deepskyblue'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tpar_tot': (                 # Total temperature par
        'scatter',                # plot_type
        [Tpar_tot],               # data_arrays
        ['Tpar_tot'],             # variable_names
        datetime_array,           # time_array
        r'$T_\parallel$', # y_label
        r'$T_\parallel$', # legend_labels
        ['mediumspringgreen'],    # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tperp1': (                    # Temperature perp of the core
        'scatter',                # plot_type
        [Tperp1],                  # data_arrays
        ['Tperp1'],                # variable_names
        datetime_array,           # time_array
        r'$T_{\perp}$', # y_label
        [r'$T_{\perp,p1}$'], # legend_labels
        ['hotpink'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tperp2': (                    # Temperature perp of the beam
        'scatter',                # plot_type
        [Tperp2],                  # data_arrays
        ['Tperp2'],                # variable_names
        datetime_array,           # time_array
        r'$T_{\perp}$', # y_label
        [r'$T_{\perp,p2}$'], # legend_labels
        ['deepskyblue'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tperp1_delta': (                    # Temperature perp of the core uncertainty
        'scatter',                # plot_type
        [Tperp1_dpar],                  # data_arrays
        ['Tperp1_delta'],                # variable_names
        datetime_array,           # time_array
        r'$\delta T_{\perp}$', # y_label
        [r'$\delta T_{\perp,p1}$'], # legend_labels
        ['orange'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tperp2_delta': (                    # Temperature perp of the beam uncertainty
        'scatter',                # plot_type
        [Tperp2_dpar],                  # data_arrays
        ['Tperp2_delta'],                # variable_names
        datetime_array,           # time_array
        r'$\delta T_{\perp}$', # y_label
        [r'$\delta T_{\perp,p2}$'], # legend_labels
        ['mediumseagreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tperp_tot': (                 # Total temperature perp
        'scatter',                # plot_type
        [Tperp_tot],               # data_arrays
        ['Tperp_tot'],             # variable_names
        datetime_array,           # time_array
        r"$T_{\perp}$", # y_label
        r"$T_{\perp}$", # legend_labels
        ['mediumspringgreen'],    # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Temp_tot': (                 # Total temperature 
        'scatter',                # plot_type
        [Temp_tot],               # data_arrays
        ['Temp_tot'],             # variable_names
        datetime_array,           # time_array
        r"$Temp_{tot}$", # y_label
        r"$T_{tot}$", # legend_labels
        ['mediumspringgreen'],    # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tperp1_delta/Tperp1': (                    # Temperature perp of the core uncertainty
        'scatter',                # plot_type
        [Tperp1_dpar/Tperp1],                  # data_arrays
        ['Tperp1_delta/Tperp1'],                # variable_names
        datetime_array,           # time_array
        r'$\delta T_{\perp}/T_{\perp}$', # y_label
        [r'$\delta T_{\perp,p1}/T_{\perp,1}$'], # legend_labels
        ['orange'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tperp2_delta': (                    # Temperature perp of the beam uncertainty
        'scatter',                # plot_type
        [Tperp2_dpar],                  # data_arrays
        ['Tperp2_delta'],                # variable_names
        datetime_array,           # time_array
        r'$\delta T_{\perp}$', # y_label
        [r'$\delta T_{\perp,p2}$'], # legend_labels
        ['mediumseagreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tperp2_delta/Tperp2': (                    # Temperature perp of the beam uncertainty
        'scatter',                # plot_type
        [Tperp2_dpar/Tperp2],                  # data_arrays
        ['Tperp2_delta/Tperp2'],                # variable_names
        datetime_array,           # time_array
        r'$\delta T_{\perp}/T_{\perp}$', # y_label
        [r'$\delta T_{\perp,p2}/T_{\perp,p2}$'], # legend_labels
        ['mediumseagreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    '|qz_p|': (                 # heat flux
        'scatter',                # plot_type
        [abs_qz_p],               # data_arrays
        ['|qz_p|'],             # variable_names
        datetime_array,           # time_array
        r'$|Q_p| W/m^2$', # y_label
        [r'$|Q_p|$'], # legend_labels
        ['mediumspringgreen'],    # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'chi_p': (                 # chi of whole proton fit
        'scatter',                # plot_type
        [chi_p],               # data_arrays
        ['chi_p'],             # variable_names
        datetime_array,           # time_array
        r'$\chi_p$', # y_label
        [r'$\chi_p$'], # legend_labels
        ['rebeccapurple'],    # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'chi_p_norm': (                 # chi of whole proton fit
        'scatter',                # plot_type
        [chi_p/2038],               # data_arrays #2048 data points, 10 free parameters
        ['chi_p_norm'],             # variable_names
        datetime_array,           # time_array
        r'$\chi_p norm$', # y_label
        [r'$\chi_p norm$'], # legend_labels
        ['rebeccapurple'],    # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    )  
    }
    zipped_data.update(zipped_sf00_fits)
if sf01_fits is not None:
        #alpha fits
    zipped_sf01_fits = {
    'na': (                      # alpha density
        'scatter',                # plot_type
        [na],                    # data_arrays
        ['na'],                  # variable_names
        datetime_array_sf01,           # time_array
        r'$N_\alpha$ \n (cm$^{-3}$)',   # y_label
        [r'$n_{a}$'],            # legend_labels
        ['black'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'na_delta': (                      # alpha density
        'scatter',                # plot_type
        [na_dpar],                    # data_arrays
        ['na_delta'],                  # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta N_\alpha$ \n (cm$^{-3}$)',   # y_label
        [r'$\delta n_{a}$'],            # legend_labels
        ['black'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'na_delta/na': (                      # alpha density
        'scatter',                # plot_type
        [na_dpar/na],                    # data_arrays
        ['na_delta/na'],                  # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta N_\alpha/N_\alpha$',   # y_label
        [r'$\delta n_{\alpha}/n_{\alpha}$'],            # legend_labels
        ['black'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'na/np': (                      # alpha/proton density
        'scatter',                # plot_type
        [na_div_nptot],                    # data_arrays
        ['na/np'],                  # variable_names
        datetime_array_sf01,           # time_array
        r'$N_\alpha/N_p$',   # y_label
        [r'$N_{\alpha}/N_p$'],            # legend_labels
        ['teal'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'na/np1': (                      # alpha/proton core density
        'scatter',                # plot_type
        [na_div_np1],                    # data_arrays
        ['na/np1'],                  # variable_names
        datetime_array_sf01,           # time_array
        r'$N_\alpha/N_{p1}$',   # y_label
        [r'$N_{\alpha}/N_{p1}$'],            # legend_labels
        ['hotpink'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'na/np2': (                      # alpha/proton beam density
        'scatter',                # plot_type
        [na_div_np2],                    # data_arrays
        ['na/np2'],                  # variable_names
        datetime_array_sf01,           # time_array
        r'$N_\alpha/N_{p2}$',   # y_label
        [r'$N_{\alpha}/N_{p2}$'],            # legend_labels
        ['deepskyblue'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_x': (                    # core velocity x
        'scatter',                # plot_type
        [va_x],                  # data_arrays
        ['va_x'],                # variable_names
        datetime_array_sf01,           # time_array
        r'Velocity (km/s)',       # y_label
        [r'$vx_{\alpha}$'],           # legend_labels
        ['forestgreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_y': (                    # alpha velocity y
        'scatter',                # plot_type
        [va_y],                  # data_arrays
        ['va_y'],                # variable_names
        datetime_array_sf01,           # time_array
        r'Velocity (km/s)',       # y_label
        [r'$vy_{\alpha}$'],           # legend_labels
        ['orange'],               # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_z': (                    # core velocity z
        'scatter',                # plot_type
        [va_z],                  # data_arrays
        ['va_z'],                # variable_names
        datetime_array_sf01,           # time_array
        r'Velocity (km/s)',       # y_label
        [r'$vz_{\alpha}$'],           # legend_labels
        ['dodgerblue'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_x_delta': (                    # core velocity x uncertainty
        'scatter',                # plot_type
        [va_x_dpar],                  # data_arrays
        ['va_x_delta'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta V$ (km/s)',       # y_label
        [r'$\delta vx_{a}$'],           # legend_labels
        ['forestgreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_y_delta': (                    # core velocity y uncertainty
        'scatter',                # plot_type
        [va_y_dpar],                  # data_arrays
        ['va_y_delta'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta V$ (km/s)',       # y_label
        [r'$\delta vy_{a}$'],           # legend_labels
        ['orange'],               # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_z_delta': (                    # core velocity z uncertainty
        'scatter',                # plot_type
        [va_z_dpar],                  # data_arrays
        ['va_z_delta'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta V$ (km/s)',       # y_label
        [r'$\delta vz_{a}$'],           # legend_labels
        ['dodgerblue'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_x_delta/va_x': (                    # core velocity x uncertainty
        'scatter',                # plot_type
        [va_x_dpar/va_x],                  # data_arrays
        ['va_x_delta/va_x'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta V/V$',       # y_label
        [r'$\delta vx_{a}/vx_{a}$'],           # legend_labels
        ['forestgreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_y_delta/va_y': (                    # core velocity y uncertainty
        'scatter',                # plot_type
        [va_y_dpar/va_y],                  # data_arrays
        ['va_y_delta/va_y'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta V/V$',       # y_label
        [r'$\delta vy_{a}/vy_{a}$'],           # legend_labels
        ['orange'],               # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_z_delta/va_z': (                    # core velocity z uncertainty
        'scatter',                # plot_type
        [va_z_dpar/va_z],                  # data_arrays
        ['va_z_delta/va_z'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta V/V$',       # y_label
        [r'$\delta vz_{a}/vz_{a}$'],           # legend_labels
        ['dodgerblue'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_mag': (                      # alpha vel
        'scatter',                # plot_type
        [va_mag],                    # data_arrays
        ['va_mag'],                  # variable_names
        datetime_array_sf01,           # time_array
        r'$|V_\alpha|$ \n (km/s)',   # y_label
        [r'$|V_\alpha|$'],            # legend_labels
        ['black'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_mag_delta': (                      # alpha vel
        'scatter',                # plot_type
        [va_mag_dpar],                    # data_arrays
        ['va_mag_delta'],                  # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta |V_\alpha|$ \n (km/s)',   # y_label
        [r'$\delta |V_\alpha|$'],            # legend_labels
        ['black'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_mag_delta/va_mag': (                      # alpha vel
        'scatter',                # plot_type
        [va_mag_dpar/va_mag],                    # data_arrays
        ['va_mag_delta/va_mag'],                  # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta |V_\alpha|/|V_\alpha|$',   # y_label
        [r'$\delta |V_\alpha|/|V_\alpha|$'],            # legend_labels
        ['black'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vdrift_ap1': (          # alpha-proton core normalized drift speed using va including alphas
        'scatter',                # plot_type
        [vdrift_ap1],        # data_arrays
        ['vdrift_ap1'],      # variable_names
        datetime_array_sf01,           # time_array
        r'$V_{drift}$',       # y_label
        [r'$Vd_{\alpha}/V_A$'],    # legend_labels
        ['darkgoldenrod'],                 # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vdrift_va_p2-p1_apfits': (          # sf00 normalized drift speed using va including alphas
        'scatter',                # plot_type
        [vdrift_va_apfits],        # data_arrays
        ['vdrift_va_p2-p1_apfits'],      # variable_names
        datetime_array,           # time_array
        r'$V_{drift}/V_A$',       # y_label
        [r'$Vd_{p2-p1}/vA$'],    # legend_labels
        ['navy'],                 # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    '|vdrift|_va_p2-p1_apfits': (          # sf00 normalized drift speed using va including alphas
        'scatter',                # plot_type
        [np.abs(vdrift_va_apfits)],        # data_arrays
        ['|vdrift|_va_p2-p1_apfits'],      # variable_names
        datetime_array,           # time_array
        r'$|V_{drift}|/V_A$',       # y_label
        [r'$|Vd_{p2-p1}|/vA$'],    # legend_labels
        ['navy'],                 # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'vdrift_va_ap1': (          # alpha-proton core normalized drift speed using va including alphas
        'scatter',                # plot_type
        [vdrift_va_ap1],        # data_arrays
        ['vdrift_va_ap1'],      # variable_names
        datetime_array_sf01,           # time_array
        r'$V_{drift}/V_A$',       # y_label
        [r'$Vd_{\alpha}/V_A$'],    # legend_labels
        ['darkgoldenrod'],                 # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    '|vdrift|_va_ap1': (          # alpha-proton core |normalized drift| speed using va including alphas
        'scatter',                # plot_type
        [np.abs(vdrift_va_ap1)],        # data_arrays
        ['|vdrift_va_ap1|'],      # variable_names
        datetime_array_sf01,           # time_array
        r'$|V_{drift}|/V_A$',       # y_label
        [r'$|Vd_{\alpha}|/V_A$'],    # legend_labels
        ['darkgoldenrod'],                 # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Trata': (                    # Temperature anisotropy of the alpha
        'scatter',                # plot_type
        [Trata],                  # data_arrays
        ['Trata'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$T_{\perp}/T_{\parallel}$', # y_label
        [r'$T_{\perp}/T_{\parallel,\alpha}$'], # legend_labels
        ['grey'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Trata_delta': (                    # Temperature anisotropy of the alpha
        'scatter',                # plot_type
        [Trata_dpar],                  # data_arrays
        ['Trata_delta'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta T_{\perp}/T_{\parallel}$', # y_label
        [r'$\delta T_{\perp}/T_{\parallel,\alpha}$'], # legend_labels
        ['grey'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Trata_delta/Trata': (                    # Temperature anisotropy of the alpha
        'scatter',                # plot_type
        [Trata_dpar/Trata],                  # data_arrays
        ['Trata_delta/Trata'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta \frac{T_{\perp}/T_{\parallel}}{T_{\perp}/T_{\parallel}}$', # y_label
        [r'$\delta \frac{T_{\perp}/T_{\parallel,\alpha}}{T_{\perp}/T_{\parallel,\alpha}}$'], # legend_labels
        ['grey'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tperpa': (                    # Perp Temperature of the alpha
        'scatter',                # plot_type
        [Tperpa],                  # data_arrays
        ['Tperpa'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$T_{\perp}$ \n (eV)', # y_label
        [r'$T_{\perp,\alpha}$'], # legend_labels
        ['grey'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tperpa_delta': (                    # Perp Temperature of the alpha
        'scatter',                # plot_type
        [Tperpa_dpar],                  # data_arrays
        ['Tperpa_delta'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta T_{\perp}$ \n (eV)', # y_label
        [r'$\delta T_{\perp,\alpha}$'], # legend_labels
        ['grey'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tperpa_delta/Tperpa': (                    # Perp Temperature of the alpha
        'scatter',                # plot_type
        [Tperpa_dpar/Tperpa],                  # data_arrays
        ['Tperpa_delta/Tperpa'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta T_{\perp}/T_{\perp}$', # y_label
        [r'$\delta T_{\perp,\alpha}/ T_{\perp,\alpha}$'], # legend_labels
        ['grey'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),    
    'Tpara': (                    # parallel Temperature  of the alpha
        'scatter',                # plot_type
        [Tpara],                  # data_arrays
        ['Tpara'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$T_{\parallel}$ \n (eV)', # y_label
        [r'$T_{\parallel,\alpha}$'], # legend_labels
        ['grey'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'beta_par_a': (                    # Temperature anisotropy of the alpha
        'scatter',                # plot_type
        [beta_par_a],                  # data_arrays
        ['beta_par_a'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\beta_{\parallel}$ \n (eV)', # y_label
        [r'$\beta_{\parallel,\alpha}$'], # legend_labels
        ['grey'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Trata_dpar': (                    # Temperature anisotropy of the alpha
        'scatter',                # plot_type
        [Trata_dpar],                  # data_arrays
        ['Trata_dpar'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta T_{\perp}/T_{\parallel}$', # y_label
        [r'$\delta T_{\perp}/T_{\parallel,\alpha}$'], # legend_labels
        ['grey'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'Tperpa_dpar': (                    # Temperature anisotropy of the alpha
        'scatter',                # plot_type
        [Tperpa_dpar],                  # data_arrays
        ['Tperpa_dpar'],                # variable_names
        datetime_array_sf01,           # time_array
        r'$\delta T_{\perp} \n (eV)$', # y_label
        [r'$\delta T_{\perp,\alpha}$'], # legend_labels
        ['grey'],              # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_x_dpar': (                    # core velocity x
        'scatter',                # plot_type
        [va_x_dpar],                  # data_arrays
        ['va_x_dpar'],                # variable_names
        datetime_array_sf01,           # time_array
        r'\delta Velocity \n (km/s)',       # y_label
        [r'$\delta vx_{\alpha}$'],           # legend_labels
        ['forestgreen'],          # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_y_dpar': (                    # alpha velocity y
        'scatter',                # plot_type
        [va_y_dpar],                  # data_arrays
        ['va_y_dpar'],                # variable_names
        datetime_array_sf01,           # time_array
        r'\delta Velocity \n (km/s)',       # y_label
        [r'$\delta vy_{\alpha}$'],           # legend_labels
        ['orange'],               # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_z_dpar': (                    # core velocity z
        'scatter',                # plot_type
        [va_z_dpar],                  # data_arrays
        ['va_z_dpar'],                # variable_names
        datetime_array_sf01,           # time_array
        r'\delta Velocity \n (km/s)',       # y_label
        [r'$\delta vz_{\alpha}$'],           # legend_labels
        ['dodgerblue'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'va_mag_dpar': (                    # core velocity z
        'scatter',                # plot_type
        [va_mag_dpar],                  # data_arrays
        ['va_mag_dpar'],                # variable_names
        datetime_array_sf01,           # time_array
        r'\delta Velocity \n (km/s)',       # y_label
        [r'$\delta |V_{\alpha}|$'],           # legend_labels
        ['dodgerblue'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'chi_a': (                    # core velocity z
        'scatter',                # plot_type
        [chi_a],                  # data_arrays
        ['chi_a'],                # variable_names
        datetime_array_sf01,           # time_array
        r'\Chi',       # y_label
        [r'$\Chi_{\alpha}$'],           # legend_labels
        ['dodgerblue'],           # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    ),
    'chi_a_norm': (                 # chi of whole alpha fit
        'scatter',                # plot_type
        [chi_a/2041],               # data_arrays #2048 data points, 7 free parameters (for just alpha core)
        ['chi_a_norm'],             # variable_names
        datetime_array_sf01,           # time_array
        r'$\chi_a norm$', # y_label
        [r'$\chi_a norm$'], # legend_labels
        ['rebeccapurple'],    # colors
        [(5, 1)],                 # marker_styles
        [5],                      # marker_sizes
        [0.7],                    # alphas
        'linear',                 # y_scale
        None                      # y_lim
    )     
    }
    
    zipped_data.update(zipped_sf01_fits)

if ham is not None:
    zipped_ham_data = {
    'hamstring': (                                 # hardham timestrings
        'scatter',                                 # Plot type
        [hamstring],                                    # Data array
        ['hamstring'],                                  # Plotbot Variable name
        hardham_datetime_utc,                              # Time Array (x-axis)
        r'Hamstring',            # Y-axis label
        [r'Hamstring'],                                # Legend label
        ['palevioletred'],                                  # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'hamstring_og': (                                 # hardham timestrings
        'scatter',                                 # Plot type
        [hamstring[ogflag_list]],                                    # Data array
        ['hamstring_og'],                                  # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],                              # Time Array (x-axis)
        r'Hamstring_og',            # Y-axis label
        [r'Hamstring_og'],                                # Legend label
        ['palevioletred'],                                  # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
 
    'hamstring_dt': (                                 # hardham timestrings
        'scatter',                                 # Plot type
        [hamstring_plus_dt],                                    # Data array
        ['hamstring_dt'],                                  # Plotbot Variable name
        hardham_datetime_utc_plus_dt,                              # Time Array (x-axis)
        r'Hamstring_dt',            # Y-axis label
        [r'Hamstring_dt'],                                # Legend label
        ['palevioletred'],                                  # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'hamogram_30s': (                    # histogram of hamstrings
        'time_series',                 # Plot type
        [c_30s_up],                  # Data array
        ['hamogram_30s'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        [r'Hamogram'],                   # Y-axis label
        [r'Hamogram_30s'],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        [0,None],                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'hamogram_og_30s': (                    # histogram of hamstrings
        'time_series',                 # Plot type
        [c_og_30s_up],                  # Data array
        ['hamogram_og_30s'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        [r'Hamogram_og_30s'],                   # Y-axis label
        [r'Hamogram_og_30s '],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'hamogram_1m': (                    # histogram of hamstrings
        'time_series',                 # Plot type
        [c_1m],                  # Data array
        ['hamogram_1m'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        [r'Hamogram'],                   # Y-axis label
        [r'Hamogram_1m'],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        [0,None],                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'hamogram_og_1m': (                    # histogram of hamstrings
        'time_series',                 # Plot type
        [c_og_1m],                  # Data array
        ['hamogram_og_1m'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        [r'Hamogram_og_1m'],                   # Y-axis label
        [r'Hamogram_og_1m '],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'hamogram_2m': (                    # histogram of hamstrings
        'time_series',                 # Plot type
        [c_2m_up],                  # Data array
        ['hamogram_2m'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        [r'Hamogram'],                   # Y-axis label
        [r'Hamogram_2m'],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        [0,None],                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'hamogram_og_2m': (                    # histogram of hamstrings
        'time_series',                 # Plot type
        [c_og_2m_up],                  # Data array
        ['hamogram_og_2m'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        [r'Hamogram_og_2m'],                   # Y-axis label
        [r'Hamogram_og_2m '],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),

    'hamogram_20m': (                    # histogram of hamstrings
        'time_series',                 # Plot type
        [c_20m_up],                  # Data array
        ['hamogram_20m'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        [r'Hamogram'],                   # Y-axis label
        [r'Hamogram_20m'],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        [0,None],                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'hamogram_og_20m': (                    # histogram of hamstrings
        'time_series',                 # Plot type
        [c_og_20m_up],                  # Data array
        ['hamogram_og_20m'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        [r'Hamogram_og_20m'],                   # Y-axis label
        [r'Hamogram_og_20m '],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),

    'hamogram_90m': (                    # histogram of hamstrings
        'time_series',                 # Plot type
        [c_90m_up],                  # Data array
        ['hamogram_90m'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        [r'Hamogram'],                   # Y-axis label
        [r'Hamogram_90m'],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        [0,None],                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'hamogram_og_90m': (                    # histogram of hamstrings
        'time_series',                 # Plot type
        [c_og_90m_up],                  # Data array
        ['hamogram_og_90m'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        [r'Hamogram_og_90m'],                   # Y-axis label
        [r'Hamogram_og_90m '],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'hamogram_4h': (                    # histogram of hamstrings
        'time_series',                 # Plot type
        [c_4h_up],                  # Data array
        ['hamogram_4h'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        [r'Hamogram'],                   # Y-axis label
        [r'Hamogram_4h'],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        [0,None],                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'hamogram_og_4h':(                   # histogram of hamstrings
        'time_series',                 # Plot type
        [c_og_4h_up],                  # Data array
        ['hamogram_og_4h'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        [r'Hamogram_og_4h'],                   # Y-axis label
        [r'Hamogram_og_4h'],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    
    'hamogram_12h': (                    # histogram of hamstrings
        'time_series',                 # Plot type
        [c_12h_up],                 # Data array
        ['hamogram_12h'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        [r'Hamogram'],                   # Y-axis label
        [r'Hamogram_12h'],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        [0,None],                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),
    'hamogram_og_12h':(                   # histogram of hamstrings
        'time_series',                 # Plot type
        [c_og_12h_up],                  # Data array
        ['hamogram_og_12h'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        [r'Hamogram_og_12h'],                   # Y-axis label
        [r'Hamogram_og_12h'],                    # Legend label
        ['palevioletred'],               # Line color
        'linear',                      # Y-axis scale
        None,                          # Y-axis limits
        [1],                           # Line width
        ['-'],                         # Line style
        None,                          # Additional data (required for spectral plotting)
        None,                          # Spectrogram Colormap
        None,                          # Spectrogram Colorbar scaling
        None                           # Spectrogram Colorbar limits
    ),

    'N_core': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [core_dens_list],                  # Data array
        ['N_core'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        'N $(cm^{-3})$',                   # Y-axis label
        [r'$N_{{core}}$'],                    # Legend label
        ['aquamarine'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'N_core_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [core_dens_list[ogflag_list]],                  # Data array
        ['N_core_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        '$N (cm^{-3})$',                   # Y-axis label
        [r'$N_{{core,og}}$'],                    # Legend label
        ['aquamarine'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'N_neck': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [neck_dens_list],                  # Data array
        ['N_neck'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        'N $(cm^{-3})$',                   # Y-axis label
        [r'$N_{{neck}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'N_neck_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [neck_dens_list[ogflag_list]],                  # Data array
        ['N_neck_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        '$N (cm^{-3})$',                   # Y-axis label
        [r'$N_{{neck,og}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'N_ham': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [ham_dens_list],                  # Data array
        ['N_ham'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        'N $(cm^{-3})$',                   # Y-axis label
        [r'$N_{{ham}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'N_ham_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [ham_dens_list[ogflag_list]],                  # Data array
        ['N_ham'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        '$N (cm^{-3})$',                   # Y-axis label
        [r'$N_{{ham,og}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'N_ham/N_tot': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Nham_div_Ntot_up],                  # Data array
        ['N_ham/N_tot'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        r'$N_{{s}}/N_{{tot}}$',                   # Y-axis label
        [r'$N_{{ham}}/N_{{tot}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [50],                     # marker_sizes
        [0.9],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'N_ham_og/N_tot_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Nham_div_Ntot[ogflag_list]],                  # Data array
        ['N_ham_og/N_tot_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$N_{{s,og}}/N_{{tot,og}}$',                   # Y-axis label
        [r'$N_{{ham,og}}/N_{{tot,og}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [50],                     # marker_sizes
        [0.9],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'N_ham/N_core': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Nham_div_Ncore_up],                  # Data array
        ['N_ham/N_core'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        r'$N_{{s}}/N_{{core}}$',                   # Y-axis label
        [r'$N_{{ham}}/N_{{core}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),

    'N_ham_og/N_core_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Nham_div_Ncore],                  # Data array
        ['N_ham/N_core'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$N_{{s,og}}/N_{{core,og}}$',                   # Y-axis label
        [r'$N_{{ham}}/N_{{core,og}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'N_neck/N_core': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Nneck_div_Ncore],                  # Data array
        ['N_neck/N_core'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        r'$N_{{s}}/N_{{core}}$',                   # Y-axis label
        [r'$N_{{neck}}/N_{{core}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),

    'N_neck_og/N_core_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Nneck_div_Ncore],                  # Data array
        ['N_neck/N_core'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$N_{{s,og}}/N_{{core,og}}$',                   # Y-axis label
        [r'$N_{{neck}}/N_{{core,og}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'N_tot': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Ntot],                  # Data array
        ['N_tot'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        r'$N_{{tot}}$',                   # Y-axis label
        [r'$N_{{tot}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'N_tot_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Ntot[ogflag_list]],                  # Data array
        ['N_tot_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$N_{{tot,og}}$',                   # Y-axis label
        [r'$N_{{tot,og}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'vmag_core': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [core_umag],                  # Data array
        ['vmag_core'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        '$|V|$ km/s',                   # Y-axis label
        [r'$|V|_{{core}}$'],                    # Legend label
        ['aquamarine'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'vmag_core_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [core_umag[ogflag_list]],                  # Data array
        ['vmag_core'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        '$|V|$ km/s',                   # Y-axis label
        [r'$|V|_{{core,og}}$'],                    # Legend label
        ['aquamarine'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'vmag_neck': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [neck_umag],                  # Data array
        ['vmag_neck'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        '$|V|$ km/s',                   # Y-axis label
        [r'$|V|_{{neck}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'vmag_neck_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [neck_umag[ogflag_list]],                  # Data array
        ['vmag_neck_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        '$|V|$ km/s',                   # Y-axis label
        [r'$|V|_{{neck,og}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'vmag_ham': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [ham_umag],                  # Data array
        ['vmag_ham'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        '$|V|$ km/s',                   # Y-axis label
        [r'$|V|_{{ham}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'vmag_ham_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [ham_umag[ogflag_list]],                  # Data array
        ['vmag_ham_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        '$|V|$ km/s',                   # Y-axis label
        [r'$|V|_{{ham,og}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'ham_core_drift': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [ham_core_drift_up],                  # Data array
        ['ham_core_drift'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        '$v_{{drift}}$ km/s',                   # Y-axis label
        [r'$(vd)_{{h-c}}$ km/s'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [50],                     # marker_sizes
        [0.9],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'ham_core_drift_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [ham_core_drift[ogflag_list]],                  # Data array
        ['ham_core_drift'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        '$v_{{drift,og}}$ km/s',                   # Y-axis label
        [r'$(vd)_{{h-c,og}}$ km/s'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [50],                     # marker_sizes
        [0.9],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'ham_core_drift_va': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [ham_core_drift_va_up],                  # Data array
        ['ham_core_drift_va'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        '$v_{{drift}}/v_{{A}}$',                   # Y-axis label
        [r'$(v_{{d}}/v_{{A}})_{{h-c}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [50],                     # marker_sizes
        [0.9],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'ham_core_drift_va_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [ham_core_drift_va[ogflag_list]],                  # Data array
        ['ham_core_drift_va_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        '$(v_{{drift}}/v_{{A}})_{{og}}$',                   # Y-axis label
        [r'$(v_{{d}}/v_{{A}})_{{h-c,og}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [50],                     # marker_sizes
        [0.9],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'neck_core_drift_va': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [neck_core_drift_va],                  # Data array
        ['neck_core_drift_va'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        '$v_{{drift}}/v_{{A}}$',                   # Y-axis label
        [r'$(v_{{d}}/v_{{A}})_{{n-c}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'neck_core_drift_va_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [neck_core_drift_va[ogflag_list]],                  # Data array
        ['neck_core_drift_va_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        '$(v_{{drift}}/v_{{A}})_{{og}}$',                   # Y-axis label
        [r'$(v_{{d}}/v_{{A}})_{{n-c,og}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
        
    'core_temp': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [core_temp],                  # Data array
        ['core_temp'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        '$Temp$ (eV)',                   # Y-axis label
        [r'$T_{{core}}$'],                    # Legend label
        ['aquamarine'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'core_temp_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [core_temp[ogflag_list]],                  # Data array
        ['core_temp_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        '$Temp$ (eV)',                   # Y-axis label
        [r'$T_{{core,og}}$'],                    # Legend label
        ['aquamarine'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'neck_temp': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [neck_temp],                  # Data array
        ['neck_temp'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        '$Temp$ (eV)',                   # Y-axis label
        [r'$T_{neck}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'neck_temp_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [neck_temp[ogflag_list]],                  # Data array
        ['neck_temp_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        '$Temp$ (eV)',                   # Y-axis label
        [r'$T_{neck,og}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'ham_temp': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [ham_temp],                  # Data array
        ['ham_temp'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        '$Temp$ (eV)',                   # Y-axis label
        [r'$T_{{ham}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'ham_temp_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [ham_temp[ogflag_list]],                  # Data array
        ['ham_temp_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        '$Temp$ (eV)',                   # Y-axis label
        [r'$T_{{ham,og}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'core_trat': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Anisotropy_core],                  # Data array
        ['core_trat'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        r'$T_\perp/T_\parallel$',                   # Y-axis label
        [r'$(T_\perp/T_\parallel)_{{core}}$'],                    # Legend label
        ['aquamarine'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ), 
    'core_trat_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Anisotropy_core[ogflag_list]],                  # Data array
        ['core_trat_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$(T_\perp/T_\parallel)_{{og}}$',                   # Y-axis label
        [r'$(T_\perp/T_\parallel)_{{core,og}}$'],                    # Legend label
        ['aquamarine'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'neck_trat': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Anisotropy_neck],                  # Data array
        ['neck_trat'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        r'$T_\perp/T_\parallel$',                   # Y-axis label
        [r'$(T_\perp/T_\parallel)_{{neck}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ), 
    'neck_trat_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Anisotropy_neck[ogflag_list]],                  # Data array
        ['neck_trat_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$(T_\perp/T_\parallel)_{{og}}$',                   # Y-axis label
        [r'$(T_\perp/T_\parallel)_{{neck,og}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'ham_trat': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Anisotropy_ham_up],                  # Data array
        ['ham_trat'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        r'$T_\perp/T_\parallel$',                   # Y-axis label
        [r'$(T_\perp/T_\parallel)_{{ham}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [50],                     # marker_sizes
        [0.9],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ), 
    'ham_trat_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Anisotropy_ham[ogflag_list]],                  # Data array
        ['ham_trat_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$(T_\perp/T_\parallel)_{{og}}$',                   # Y-axis label
        [r'$(T_\perp/T_\parallel)_{{ham,og}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [50],                     # marker_sizes
        [0.9],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'ham_tperp': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [T_perp_ham],                  # Data array
        ['ham_tperp'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        r'$T_\perp$',                   # Y-axis label
        [r'$(T_\perp)_{{ham}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ), 
    'ham_tperp_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [T_perp_ham[ogflag_list]],                  # Data array
        ['ham_tperp_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$(T_\perp)_{{og}}$',                   # Y-axis label
        [r'$(T_\perp)_{{ham,og}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'neck_tperp': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [T_perp_neck],                  # Data array
        ['ham_neck'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        r'$T_\perp$',                   # Y-axis label
        [r'$(T_\perp)_{{neck}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ), 
    'neck_tperp_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [T_perp_neck[ogflag_list]],                  # Data array
        ['neck_tperp_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$(T_\perp)_{{og}}$',                   # Y-axis label
        [r'$(T_\perp)_{{neck,og}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'core_tperp': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [T_perp_core],                  # Data array
        ['core_tperp'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        r'$T_\perp$',                   # Y-axis label
        [r'$(T_\perp)_{{core}}$'],                    # Legend label
        ['aquamarine'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ), 
    'core_tperp_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [T_perp_core[ogflag_list]],                  # Data array
        ['core_tperp_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$(T_\perp)_{{og}}$',                   # Y-axis label
        [r'$(T_\perp)_{{core,og}}$'],                    # Legend label
        ['aquamarine'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'ham_tpar': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [T_parallel_ham],                  # Data array
        ['ham_tpar'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        r'$T_\parallel$',                   # Y-axis label
        [r'$(T_\parallel)_{{ham}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ), 
    'ham_tpar_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [T_parallel_ham[ogflag_list]],                  # Data array
        ['ham_tpar_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$(T_\parallel)_{{og}}$',                   # Y-axis label
        [r'$(T_\parallel)_{{ham,og}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'neck_tpar': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [T_parallel_neck],                  # Data array
        ['neck_tpar'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        r'$T_\parallel$',                   # Y-axis label
        [r'$(T_\parallel)_{{neck}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ), 
    'neck_tpar_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [T_parallel_neck[ogflag_list]],                  # Data array
        ['neck_tpar_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$(T_\parallel)_{{og}}$',                   # Y-axis label
        [r'$(T_\parallel)_{{neck,og}}$'],                    # Legend label
        ['lightskyblue'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'core_tpar': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [T_parallel_core],                  # Data array
        ['core_tpar'],                # Plotbot Variable name
        hardham_datetime_utc,          # Time Array (x-axis)
        r'$T_\parallel$',                   # Y-axis label
        [r'$(T_\parallel)_{{core}}$'],                    # Legend label
        ['aquamarine'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ), 
    'core_tpar_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [T_parallel_core[ogflag_list]],                  # Data array
        ['core_tpar_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$(T_\parallel)_{{og}}$',                   # Y-axis label
        [r'$(T_\parallel)_{{core,og}}$'],                    # Legend label
        ['aquamarine'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'Tperp_ham_div_core': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Tperp_ham_div_core_up],                  # Data array
        ['tperp_ham_div_core'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        r'$T_{{\perp,h}}/T_{{\perp,c}}$',                   # Y-axis label
        [r'$T_{{\perp,h}}/T_{{\perp,c}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ), 
    'Tperp_ham_div_core_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Tperp_ham_div_core[ogflag_list]],                  # Data array
        ['tperp_ham_div_core_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        r'$T_{{\perp,h}}/T_{{\perp,c}}$',                   # Y-axis label
        [r'$T_{{\perp,h}}/T_{{\perp,c}}$'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ),
    'Tperprat_driftva_hc': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Tperprat_driftva_hc_up],                  # Data array
        ['ham_param1'],                # Plotbot Variable name
        datetime_spi,          # Time Array (x-axis)
        'ham param1',                   # Y-axis label
        ['ham param1'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    ), 
    'ham_param1_og': (                    # histogram of hamstrings
        'scatter',                 # Plot type
        [Tperprat_driftva_hc[ogflag_list]],                  # Data array
        ['ham_param1_og'],                # Plotbot Variable name
        hardham_datetime_utc[ogflag_list],          # Time Array (x-axis)
        'ham param1 og',                   # Y-axis label
        ['ham param1 og'],                    # Legend label
        ['palevioletred'],               # Line color
        [(5, 1)],                 # marker_styles (Star marker)
        [20],                     # marker_sizes
        [0.2],                    # alphas
        'linear',                                      # Y-axis scale
        None,                                          # Y-axis limits
    )

        
    }

    zipped_data.update(zipped_ham_data)

