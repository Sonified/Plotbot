# Plotbot

A tool for downloading and plotting data from the Parker Solar Probe!

## Features

- Time series visualization with `plotbot()`
- Multi-panel comparisons with `multiplot()`
- Hodogram visualization with `showdahodo()`
- Audio generation from magnetic field data
- Automatic data downloading and processing

## Installation

### For macOS users:

1. Clone this repository:


git clone https://github.com/Sonified/Plotbot.git
cd Plotbot

2. Create and activate the environment:

source /opt/anaconda3/etc/profile.d/conda.sh  # May be needed on some systems
conda env create -f environment.yml
conda activate plotbot_env

3. Launch Jupyter Lab:

jupyter lab

4. Open the notebook and run the version check in the first cell to verify your setup.

## Quick Start

In Jupyter, hit 'Run All' and then scroll down to see various example plots you can create! The notebook contains examples of:

- Basic time series plots
- Multi-panel synchronization
- Hodogram (scatter) plots
- Sonification/audification

## Required Versions

- Python: 3.12.4
- NumPy: 1.26.4
- Pandas: 2.2.2
- Matplotlib: 3.9.2
- cdflib: 1.3.1
- BeautifulSoup: 4.12.3
- requests: 2.32.2
- python-dateutil: 2.9.0.post0

## Data Structure

Downloaded data is stored in the following structure:
- psp_data/
- fields/
 - l2/
   - mag_rtn/
   - mag_sc/
- sweap/
 - ...
