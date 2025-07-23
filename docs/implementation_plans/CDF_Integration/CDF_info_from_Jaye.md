Emails from Jaye:

Here is a drive link to examples of wave files from KP:
https://drive.google.com/drive/folders/1CbOICZWYIjyQqZaPqcv7bzB8Ol4DBPjq?usp=drive_link

'PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf'
is a large file with 2d contour (spectra) data and the included notebook shows how to open and plot variables from that file. Note that the power spectra I tried to plot does not look pretty at all and it made me sad. Maybe you know how to make it pretty ?

'PSP_wavePower_2021-04-29_v1.3.cdf' is a reduced version of
'PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf' that only has 1d summed quantities of Right-handed (RH) and left-handed (LH) wavepower. I would start with this reduced file and move to the more complex file with spectra.

Thanks!

'PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf' is in 6 hour chunks. This file is covering 6 hours, ie 6-12, just like the mag_RTN files

For 'PSP_wavePower_2021-04-29_v1.3.cdf' could do RH as and LH as blue

specifications:
⭐️Jaye’s thoughts⭐️
Time is of the essence! 
Input -  filepath ‘/Users/jlverniero/blah/filename.cdf’, new class name (could be optional for bonus points)

Read cdf, extract all variables:
Read all ZVariables and Rvariables
Extract metadata for each one (such as units). Note each cdf may have different metadata. For nasa cdaweb files, all metadata is standard. Log vs linear.
Make plotbot variables of name of each variable, with ylabel as variable name (units) 
Colors: make something automatic such as rainbow it
A nuance will be to automatically make the 2d contour plots (like the pads).
Color
Extract datetime information.
Different files will have different datetime formats, have algorithm detect what type it is and convert to tt2000.
Default to line plots, for e.g. density of the moments. It would be a bonus point to have the option to change the plot type, e.g. line to scatter and vice versa.

Output - make new class called ____
Create a .pyi file.

