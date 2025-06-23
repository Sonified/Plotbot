2024 Conjunction

Physics that we are interested in:

-	Some “big picture” (maybe more straightforward?) questions. 

o	What are the basic solar wind parameters between the two observations? (Profiles of magnetic field strength, solar wind speed, particle temperatures, temperature anisotropies, particle densities, electron pitch angle distribution)
o	Does the magnetic field PSD have the same slope in each case when considering similar regions? 
o	Are there regions of instability (e.g., temperature anisotropy instabilities), and do these regions change between observations?

-	Some more involved questions. 

o	Are there ion-scale waves in both cases, and where are they? Do their properties change between observations?
o	Do we see hams in each observation set (and does Wind have the VDFs)? Do ham properties change significantly? Are there waves in our ham?
o	Does the structure of the heliospheric current sheet change significantly between the two observations, or does the general structure look the same? (Which regions should we highlight and compare?)
o	Can we infer or directly observe heating between the two times by, e.g., comparing particle temperatures or distribution functions?
 

Wind data products of interest:


Important notes: 
-	Wind has several instrument suites, some of which provide different measures of parameters, most notably particle moments. SWE and 3DP in particular have different cadence measurements for proton moments. The SWE version is lower-cadence (~92-second measurements) but generally higher-accuracy, while the 3DP version is higher-cadence (~3-second measurements) but at times may be less reliable. The data quality flags are important metrics to consider in this case, because working with the higher-cadence data would be ideal but is not always possible.
-	Electron measurements are significantly less reliable than proton measurements. 


Name of instrument: Magnetic Field Investigation (MFI)

    Description: Magnetic field measurements, 11 samples per second
    Data Format: mfi_h2
    File format: wi_h2_mfi_{YYYY}{MM}{DD}_v05.cdf
    Relevant variables:
    - Epoch: ‘EPOCH’
    - Vector B: ‘BGSE’
        - Vector components are in geocentric solar ecliptic (GSE) coordinates
    - |B|: ‘BF1’

Name of instrument: Solar Wind Experiment (SWE)

    Description: 92-second proton and alpha moments computed from bi-Maxwellian fits 
    Data format: swe_h1
    File format: wi_h1_swe_{YYYY}{MM}{DD}_v01.cdf
    Relevant variables:
        - Epoch: ‘EPOCH’
        - Data quality flag: ‘fit_flag’
        - Proton parallel thermal speed: ‘Proton_Wpar_nonlin’
        - Proton perpendicular thermal speed: ‘Proton_Wperp_nonlin’
        - Alpha thermal speed: ‘Alpha_W_Nonlin’

    Description: Electron moments from quadrature analysis
    Data format: swe_h5
    File format: wi_h5_swe_{YYYY}{MM}{DD}_v01.cdf
    Relevant variable names:
        - Epoch: ‘Epoch’
        - Electron temperature: ‘T_elec’


Name of instrument: 3D Plasma Analyzer (3DP)

    Description: ~24-second electron fluxes for pitch-angle bins in several energy ranges
    Data format: 3dp_elpd
    File format: wi_elpd_3dp_{YYYY}{MM}{DD}_v02.cdf
    Relevant variables:
        - Epoch: ‘EPOCH’
        - Particle flux: ‘FLUX’
            - ‘FLUX’ is the electron flux organized by pitch-angle bins and energy channels
            - ‘FLUX’ has shape [ N x A x E ], where N is the total number of measurements, A=8 is the total number of pitch-angle bins, and E=15 is the total number of energy bins
        - Pitch angle: ‘PANGLE’
            - ‘PANGLE’ is the set of pitch angle bins at each epoch—these change slightly at each time step
            - ‘PANGLE’ has shape [ N x A ], where N is the total number of measurements and A=8 is the total number of pitch-angle bins.

    Description: 3-second ion parameters from Faraday cup measurements
    Data format: 3dp_pm
    File format: wi_pm_3dp_{YYYY}{MM}{DD}_v02.cdf
    Relevant variables:
        - Data quality flag: ‘VALID’
        - Proton velocity (i.e., solar wind velocity): ‘P_VELS’
        - Proton density: ‘P_DENS’
        - Proton temperature: ‘P_TEMP’
        - Alpha density: ‘A_DENS’
        - Alpha temperature: ‘A_TEMP’


