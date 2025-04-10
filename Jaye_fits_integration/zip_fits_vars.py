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