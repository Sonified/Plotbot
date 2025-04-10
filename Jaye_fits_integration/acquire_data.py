#specify time range in the form ['yyyy-mm-dd/hh:mm:ss','yyyy-mm-dd/hh:mm:ss']
# trange = ['2023-09-28/06:32:00.000', '2023-09-28/06:45:00.000']
# trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']


    #trange = trange_full
    #ebin = electron strahl energy bin, 8 for E1-8, 12 E10+
    #to do: automatically set based on trange

    #-----In RTN coordinates-----\
    #4 Samples Per Cycle
if mag_rtn_4sa is not None:
   # mag_rtn_4sa_datatype = 'mag_rtn_4_sa_per_cyc' #mag
    mag_rtn_4sa_datatype = 'mag_RTN_4_Sa_per_Cyc'

        #later we will add the ability to dynamically change to high-resolution magnetometer data
    print('Acquiring mag RTN data...')
    for no_update in [True, False]:
        try:
            mag_rtn_4sa_vars = pyspedas.psp.fields(
                trange=trange,
                datatype=mag_rtn_4sa_datatype,
                level='l2',
                time_clip=True,
                get_support_data=False,
                no_update=no_update
            )
            if mag_rtn_4sa_vars and 'psp_fld_l2_mag_RTN_4_Sa_per_Cyc' in mag_rtn_4sa_vars:
                print("RTN mag data loaded", "from local cache." if no_update else "successfully.")
                break
        except KeyError as e:
            print(f"⚠️ KeyError during data load: {e}")
    else:
        print("Failed to load RTN mag data from both local cache and remote source.")
      
if mag_rtn is not None:
    mag_rtn_datatype = 'mag_rtn' #mag

    #loading full resolution magnetometer data in RTN coordinates
    mag_rtn_vars = pyspedas.psp.fields(trange=trange, datatype=mag_rtn_datatype, level='l2', time_clip=True, get_support_data=True)

if spi_sf00_mom is not None:
        #-----Specify span-i data type to plot-----\

    spi_datatype='spi_sf00_l3_mom' #protons sf means survey cadence, l3 means level 3, mom means moment, 00 means protons

    print('Acquiring SPI data...')

    #for no_update in [True, False]:
    for no_update in [False]:
        if nonpublic is not None:
            spi_vars = pyspedas.psp.spi(
            trange=trange,
            datatype='spi_sf00',
            level='L3',
            time_clip=True,
            no_update=no_update,
            get_support_data=True,
            username = 'sbdas',
            password = 'SlapHappeeGranpappy01238'
            )
        else:    
            spi_vars = pyspedas.psp.spi(
                trange=trange,
                datatype=spi_datatype,
                level='l3',
                time_clip=True,
                no_update=no_update,
                get_support_data=True,
            )
        
        #rename tplot variables to distinguish proton variable name from alpha variable name
        tplot_rename("psp_spi_QUALITY_FLAG","psp_spi_sf00_QUALITY_FLAG")
        tplot_rename("psp_spi_DENS","psp_spi_sf00_DENS")
        tplot_rename("psp_spi_VEL_INST","psp_spi_sf00_VEL_INST")
        tplot_rename("psp_spi_VEL_SC","psp_spi_sf00_VEL_SC")
        tplot_rename("psp_spi_VEL_RTN_SUN","psp_spi_sf00_VEL_RTN_SUN")
        tplot_rename("psp_spi_T_TENSOR_INST","psp_spi_sf00_T_TENSOR_INST")
        tplot_rename("psp_spi_TEMP","psp_spi_sf00_TEMP")
        tplot_rename("psp_spi_EFLUX_VS_ENERGY","psp_spi_sf00_EFLUX_VS_ENERGY")
        tplot_rename("psp_spi_EFLUX_VS_THETA","psp_spi_sf00_EFLUX_VS_THETA")
        tplot_rename("psp_spi_EFLUX_VS_PHI","psp_spi_sf00_EFLUX_VS_PHI")
        tplot_rename("psp_spi_SUN_DIST","psp_spi_sf00_SUN_DIST")
        tplot_rename("psp_spi_VENUS_DIST","psp_spi_sf00_VENUS_DIST")
        tplot_rename("psp_spi_SC_VEL_RTN_SUN","psp_spi_sf00_SC_VEL_RTN_SUN")
        tplot_rename("psp_spi_QUAT_SC_TO_RTN","psp_spi_sf00_QUAT_SC_TO_RTN")
        tplot_rename("psp_spi_MAGF_SC","psp_spi_sf00_MAGF_SC")
        tplot_rename("psp_spi_MAGF_INST","psp_spi_sf00_MAGF_INST")
        tplot_rename("psp_spi_Epoch","psp_spi_sf00_Epoch")
        
        if spi_vars and 'psp_spi_DENS' in spi_vars:
            print("SPI data loaded", "from local cache." if no_update else "successfully.")
            break
    else:
        print("Failed to load SPI data from both local cache and remote source.")
        

if spi_sf00_mom is not None:
        #-----Specify span-i data type to plot-----\

    spi_sf0a_datatype = 'spi_sf0a_l3_mom' #protons sf means survey cadence, l3 means level 3, mom means moment, 00 means protons

    print('Acquiring SPI data...')

    #for no_update in [True, False]:
    for no_update in [False]:
        if nonpublic is not None:
            spi_sf0a_vars = pyspedas.psp.spi(
            trange=trange,
            datatype=spi_sf0a_datatype,
            level='L3',
            time_clip=True,
            no_update=no_update,
            get_support_data=True,
            username = 'sbdas',
            password = 'SlapHappeeGranpappy01238'
            )
        else:    
            spi_sf0a_vars = pyspedas.psp.spi(
                trange=trange,
                datatype=spi_sf0a_datatype,
                level='l3',
                time_clip=True,
                no_update=no_update,
                get_support_data=True,
            )
        
        #rename tplot variables to distinguish proton variable name from alpha variable name
        tplot_rename("psp_spi_QUALITY_FLAG","psp_spi_sf0a_QUALITY_FLAG")
        tplot_rename("psp_spi_DENS","psp_spi_sf0a_DENS")
        tplot_rename("psp_spi_VEL_INST","psp_spi_sf0a_VEL_INST")
        tplot_rename("psp_spi_VEL_SC","psp_spi_sf00_VEL_SC")
        tplot_rename("psp_spi_VEL_RTN_SUN","psp_spi_sf0a_VEL_RTN_SUN")
        tplot_rename("psp_spi_T_TENSOR_INST","psp_spi_sf0a_T_TENSOR_INST")
        tplot_rename("psp_spi_TEMP","psp_spi_sf0a_TEMP")
        tplot_rename("psp_spi_EFLUX_VS_ENERGY","psp_spi_sf0a_EFLUX_VS_ENERGY")
        tplot_rename("psp_spi_EFLUX_VS_THETA","psp_spi_sf0a_EFLUX_VS_THETA")
        tplot_rename("psp_spi_EFLUX_VS_PHI","psp_spi_sf0a_EFLUX_VS_PHI")
        tplot_rename("psp_spi_SUN_DIST","psp_spi_sf0a_SUN_DIST")
        tplot_rename("psp_spi_VENUS_DIST","psp_spi_sf0a_VENUS_DIST")
        tplot_rename("psp_spi_SC_VEL_RTN_SUN","psp_spi_sf0a_SC_VEL_RTN_SUN")
        tplot_rename("psp_spi_QUAT_SC_TO_RTN","psp_spi_sf0a_QUAT_SC_TO_RTN")
        tplot_rename("psp_spi_MAGF_SC","psp_spi_sf0a_MAGF_SC")
        tplot_rename("psp_spi_MAGF_INST","psp_spi_sf0a_MAGF_INST")
        tplot_rename("psp_spi_Epoch","psp_spi_sf0a_Epoch")
        
        if spi_sf0a_vars and 'psp_spi_DENS' in spi_sf0a_vars:
            print("SPI sf0a data loaded", "from local cache." if no_update else "successfully.")
            break
    else:
        print("Failed to load SPI sf0a data from both local cache and remote source.")

if spe_sf0_pad is not None:
    #loading electron data
    if nonpublic is not None:
        spe_vars = pyspedas.psp.spe(
        trange=trange,
        datatype='spe_sf0',
        level='L3',
        time_clip=True,
        no_update=no_update,
        get_support_data=True,
        username = 'sbdas',
        password = 'SlapHappeeGranpappy01238'
        )
    else:
        spe_datatype = 'spe_sf0_pad' #electrons
        spe_vars = pyspedas.psp.spe(trange=trange, datatype=spe_datatype, level='l3', time_clip=True,get_support_data=True)
    

    

if wvpow is not None:
    wavePower_dir = '/home/jovyan/PSP_wavePower/'
    wavePower_fnames = []
    for d in range(len(dates)):
        wavePower_fnames_ = wavePower_dir + 'PSP_wavePower_' + dates[d] + '_v1.3.cdf'
        wavePower_fnames.append(wavePower_fnames_)
    #open KP wave file
    cdf_to_tplot(filenames = wavePower_fnames, merge = True)   

    
if sf00_fits is not None:
    #Read in your local fits file
    #protons
   # sf00_fits_dir = '/home/jovyan/SPAN_fits/'
    sf00_fits_prefix = 'spp_swp_spi_sf00_'
    sf00_fits_suffix = '_v00_driftswitch.csv'
    sf00_fits_fnames = []
    for d in range(len(dates)):
        sf00_fits_dir = '/home/jovyan/SPAN_fits/sf00/p1p2/v00/' + dates[d][:4] + '/' + dates[d][5:7] + '/'
        sf00_fits_fnames_ = sf00_fits_dir + sf00_fits_prefix + dates[d] + sf00_fits_suffix
        sf00_fits_fnames.append(sf00_fits_fnames_)
    df_sf00 = pd.concat(map(pd.read_csv, sf00_fits_fnames), ignore_index=True)    
    
if sf01_fits is not None:
        #alphas
    #sf01_fits_dir = '/home/jovyan/SPAN_fits/'
    sf01_fits_prefix = 'spp_swp_spi_sf01_'
    sf01_fits_suffix = '_v00.csv'
    sf01_fits_fnames = []
    for d in range(len(dates)):
        sf01_fits_dir = '/home/jovyan/SPAN_fits/sf01/p3/v00/' + dates[d][:4] + '/' + dates[d][5:7] + '/'
        sf01_fits_fnames_ = sf01_fits_dir + sf01_fits_prefix + dates[d] + sf01_fits_suffix
        sf01_fits_fnames.append(sf01_fits_fnames_)
    df_sf01 = pd.concat(map(pd.read_csv, sf01_fits_fnames), ignore_index=True) 

    
if ham is not None:
    ham_dir = '/home/jovyan/hammerheading/hamstrings/'
    #ham_date = np.arange('2020-01-25','2020-02-05',dtype = 'datetime64[D]')
#ham_date = '2020-01-29'
    ham_date = dates
    datham = read_pickle(ham_dir + f'hamstring_{ham_date[0]}')

    for d in ham_date[1:]:
        datham.update(read_pickle(ham_dir + f'hamstring_{d}'))