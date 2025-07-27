import pyspedas

trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']

#note that full resolution would be 'mag_rtn', but only download for short time periods, as it makes plotting very slow
mag_rtn_4sa_datatype = 'mag_rtn_4_sa_per_cyc' #mag
# mag_datatype = 'mag_rtn' 

#later we will add the ability to dynamically change to high-resolution magnetometer data
mag_rtn_4sa_vars = pyspedas.psp.fields(trange=trange, datatype=mag_rtn_4sa_datatype, level='l2', time_clip=True,get_support_data=True)

#note that full resolution would be 'mag_sc', but only download for short time periods, as it makes plotting very slow
mag_sc_4sa_datatype = 'mag_sc_4_sa_per_cyc' #mag

#later we will add the ability to dynamically change to high-resolution magnetometer data
mag_sc_4sa_vars = pyspedas.psp.fields(trange=trange, datatype=mag_sc_4sa_datatype, level='l2', time_clip=True,get_support_data=True)

#specify span-i data type to plot
spi_datatype='spi_sf00_l3_mom' #protons sf means survey cadence, l3 means level 3, mom means moment, 00 means protons
spi_vars = pyspedas.psp.spi(trange=trange, datatype=spi_datatype, level='l3', time_clip=True)

#loading electron data
spe_datatype = 'spe_sf0_pad' #electrons
spe_vars = pyspedas.psp.spe(trange=trange, datatype=spe_datatype, level='l3', time_clip=True,get_support_data=True)