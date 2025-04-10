dates = ['2021-04-28', '2021-04-29', '2021-04-30']

strahl_energy_index = 8
trange_full = [dates[0] + '/00:00:00', dates[-1] + '/23:59:59']
trange = trange_full

wavpow = True
mag_rtn = None
apply_fov_nans = True
sf00_fits = None
sf01_fits = None

#Read in your local fits file
#protons
sf00_fits_dir = '/home/jovyan/SPAN_fits/'
sf00_fits_prefix = 'spp_swp_spi_sf00_'
sf00_fits_suffix = '_v00_driftswitch.csv'
sf00_fits_fnames = []
for d in range(len(dates)):
    sf00_fits_fnames_ = sf00_fits_dir + sf00_fits_prefix + dates[d] + sf00_fits_suffix
    sf00_fits_fnames.append(sf00_fits_fnames_)
#alphas
sf01_fits_dir = '/home/jovyan/SPAN_fits/'
sf01_fits_prefix = 'spp_swp_spi_sf01_'
sf01_fits_suffix = '_v00.csv'
sf01_fits_fnames = []
for d in range(len(dates)):
    sf01_fits_fnames_ = sf01_fits_dir + sf01_fits_prefix + dates[d] + sf01_fits_suffix
    sf01_fits_fnames.append(sf01_fits_fnames_)

wavePower_dir = '/home/jovyan/PSP_wavePower/'
wavePower_fnames = []
for d in range(len(dates)):
    wavePower_fnames_ = wavePower_dir + 'PSP_wavePower_' + dates[d] + '_v1.3.cdf'
    wavePower_fnames.append(wavePower_fnames_)

# %run '/home/jovyan/plotbot_HCS/🍀 Main_Plotbot_v1.22_with_fits.ipynb'
#Plot with Plotbot!
plt.rcParams.update({'font.size': 12})


trange=trange_full

#This example includes a little bit of everything:
# ploptions('bmag_RTN_4sa', 'line_color', ['blue'])
#ploptions('epad_strahl', 'colorbar_limits', [7, 10.5])  # Adjusted colorbar limits

#ploptions('T_par', 'y_lim', [0, 400]) 
#ploptions('T_perp', 'y_lim', [0, 400]) 
#ploptions('Anisotropy', 'y_lim', [0, 6]) 


trange = ['2021-04-29/07:00', '2021-04-29/08:40']
trange = ['2021-04-29/09:15', '2021-04-29/10:30']
trange = ['2021-04-28/00:00','2021-04-30/00:00']



plotbot(trange, #Testing Mag, Strahl, Proton Energy Flux, Protons + All fits
        'bmag_RTN_4sa', 1,
        'mag_RTN_4sa', 2,
        'epad_strahl', 3,
        'proton_energy_flux', 4,
        'dens_spi', 5,
        'velp_RTN_spi', 6,
        'M_alfven_spi', '6r',
        'T_par', 7,
        'T_perp', 7,
        'Anisotropy', '7r',
        'beta_ppar_spi', 8,
        'beta_pperp_spi', 8,
        'wvpow_LH', 9,
        'wvpow_RH', 9
    
)

#Plot with Plotbot!
plt.rcParams.update({'font.size': 12})


trange=trange_full

#This example includes a little bit of everything:
# ploptions('bmag_RTN_4sa', 'line_color', ['blue'])
ploptions('epad_strahl', 'colorbar_limits', [7, 10.5])  # Adjusted colorbar limits

#ploptions('T_par', 'y_lim', [0, 400]) 
#ploptions('T_perp', 'y_lim', [0, 400]) 
#ploptions('Anisotropy', 'y_lim', [0, 6]) 


trange = ['2021-04-29/07:00', '2021-04-29/08:40']
trange = ['2021-04-29/09:15', '2021-04-29/10:30']
trange = ['2021-04-28/00:00','2021-04-30/00:00']
trange = ['2021-04-28/18:00','2021-04-29/18:00']


plotbot(trange, #Testing Mag, Strahl, Proton Energy Flux, Protons + All fits
        'bmag_RTN_4sa', 1,
        'mag_RTN_4sa', 2,
        'epad_strahl', 3,
        'proton_energy_flux', 4,
        'dens_spi', 5,
        'velp_RTN_spi', 6,
        'M_alfven_spi', '6r',
        'T_par', 7,
        'T_perp', 7,
        'Anisotropy', '7r',
        'beta_ppar_spi', 8,
        'beta_pperp_spi', 8,
        'wvpow_LH', 9,
        'wvpow_RH', 9
    
)

trange = ['2021-04-29/07:00', '2021-04-29/08:40']
showdahodo_brazil(trange, 'beta_ppar_spi', 'Anisotropy', xlim_ = [1e-1, 1e3], ylim_ = [1e-1,2e0], alpha_ = .9)

trange = ['2021-04-29/09:15', '2021-04-29/10:30']
showdahodo_brazil(trange, 'beta_ppar_spi', 'Anisotropy', xlim_ = [1e-1, 1e3], ylim_ = [1e-1,2e0], alpha_ = .9)


showdahodo_brazil_wvpow(trange, xlim_ = [1e-1, 1e3], ylim_ = [1e-1,2e0], alpha_ = .9,vmin_ = -2, vmax_ = 2, s_ = 100)
showdahodo_brazil_wvpow(trange_full, xlim_ = [1e-2, 1e2], ylim_ = [1e-1,5e0], alpha_ = .1,vmin_ = -3, vmax_ = 2, s_ = 100)
trange = ['2021-04-28/00:00','2021-04-30/00:00']
showdahodo_brazil_wvpow(trange, xlim_ = [1e-2, 1e2], ylim_ = [1e-1,5e0], alpha_ = .1,vmin_ = -3, vmax_ = 2, s_ = 100)
trange = ['2021-04-28/18:00','2021-04-29/18:00']
showdahodo_brazil_wvpow(trange, xlim_ = [1e-2, 1e2], ylim_ = [1e-1,5e0], alpha_ = .1,vmin_ = -3, vmax_ = 2, s_ = 100)
showdahodo_brazil(trange_full, 'beta_ppar_spi', 'Anisotropy',xlim_ = [1e-2, 1e2], ylim_ = [1e-1,5e0], alpha_ = .2)
trange = ['2021-04-28/00:00','2021-04-30/00:00']
showdahodo_brazil(trange, 'beta_ppar_spi', 'Anisotropy',xlim_ = [1e-2, 1e2], ylim_ = [1e-1,5e0], alpha_ = .2)
trange = ['2021-04-28/18:00','2021-04-29/18:00']
showdahodo_brazil(trange, 'beta_ppar_spi', 'Anisotropy',xlim_ = [1e-2, 1e2], ylim_ = [1e-1,5e0], alpha_ = .2)
trange = ['2021-04-29/08:14', '2021-04-29/08:40']
showdahodo_brazil(trange, 'beta_ppar_spi', 'Anisotropy', xlim_ = [1e-1, 1e3], ylim_ = [1e-1,2e0], alpha_ = .9)

trange = ['2021-04-29/08:28', '2021-04-29/08:38']
showdahodo_brazil(trange, 'beta_ppar_spi', 'Anisotropy', xlim_ = [1e-1, 1e3], ylim_ = [1e-1,2e0], alpha_ = .9)

#Plot with Plotbot!
plt.rcParams.update({'font.size': 12})


trange=trange

#This example includes a little bit of everything:
# ploptions('bmag_RTN_4sa', 'line_color', ['blue'])
#ploptions('epad_strahl', 'colorbar_limits', [7, 10.5])  # Adjusted colorbar limits

#ploptions('T_par', 'y_lim', [0, 400]) 
#ploptions('T_perp', 'y_lim', [0, 400]) 
#ploptions('Anisotropy', 'y_lim', [0, 6]) 




plotbot(trange, #Testing Mag, Strahl, Proton Energy Flux, Protons + All fits
        'bmag_RTN_4sa', 1,
        'mag_RTN_4sa', 2,
        'epad_strahl', 3,
        'proton_energy_flux', 4,
        'dens_spi', 5,
        'velp_RTN_spi', 6,
        'M_alfven_spi', '6r',
        'T_par', 7,
        'T_perp', 7,
        'Anisotropy', '7r',
        'beta_ppar_spi', 8,
        'beta_pperp_spi', 8,
        'wvpow_LH', 9,
        'wvpow_RH', 9
    
)

trange = ['2021-04-29/08:33', '2021-04-29/08:36']
showdahodo_brazil(trange, 'beta_ppar_spi', 'Anisotropy', xlim_ = [1e-1, 1e3], ylim_ = [1e-1,2e0], alpha_ = .9)

trange = ['2021-04-29/07:00', '2021-04-29/08:14']
showdahodo_brazil(trange, 'beta_ppar_spi', 'Anisotropy', xlim_ = [1e-1, 1e3], ylim_ = [1e-1,2e0], alpha_ = .9)

trange = ['2021-04-29/07:51', '2021-04-29/08:02']
showdahodo_brazil(trange, 'beta_ppar_spi', 'Anisotropy', xlim_ = [4e-1, 1e0], ylim_ = [1.75e-1,2.5e-1], alpha_ = .9, s_ = 50)

