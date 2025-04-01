# Plotbot

A tool for downloading and plotting data from the Parker Solar Probe. Created by Dr. Jaye Verniero and Dr. Robert Alexander. Note: this is a work in progress.

## Features

*   Automatic downloading and processing of data from PSP instruments including FIELDS, SWEPAM, and SPAN-I
*   Access to data variables in a straightforward class structure
    *   "mag_rtn.br" accesses FIELDS Mag Br data in RTN coordinate system.
    *   "mag_rtn.br.color = 'blue'" sets the line color to blue.
*   Rapid Time series visualization with the `plotbot()` function.
    *   "plotbot(trange, mag_sc.br, 1, proton.anisotropy, 2)" plots Br and proton Ta for your trange on panels 1 and 2 respectively.
*   Rapid Hodogram visualization with the `showdahodo` function.
*   Rapid Multi-panel comparisons ofa single variable using the `multiplot` function.
*   Rapid Audio generation using the 'audifier' function.

## Installation (macOS Instructions Only, other OS instructions coming soon)

### Prerequisites

1. **Install Command Line Tools for Xcode:**
    
    Command Line Tools are required for Git, Homebrew, and other development utilities. To install, open Terminal (cmd+space and type "terminal") and run:
    ```bash
    xcode-select --install
    ```
    A popup will appear asking if you want to install the developer tools. Click "Install" and follow the prompts. This installation typically takes 5-10 minutes.
    
    If you skip this step, you might see this error when trying to use Git or Homebrew:
    ```
    xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools), missing xcrun at: /Library/Developer/CommandLineTools/usr/bin/xcrun
    ```

2. **Install Homebrew Package Manager:**
    
    After Command Line Tools are installed, install Homebrew, which makes installing other tools much easier:
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

3. **Install Miniconda:**
    
    Plotbot uses Python and requires Miniconda to manage its dependencies. Install it with:
    ```bash
    brew install --cask miniconda && conda init "$(basename "${SHELL}")"
    ```
    After running this command, close and reopen your terminal.

4. **Install Git:**
    
    Git is needed to download the Plotbot code. If you don't have it installed, run:
    ```bash
    brew install git
    ```

5. **Install Visual Studio Code (VS Code):** 
    
    VS Code is a popular, free, and powerful code editor that works very well with Jupyter Notebooks and Python. While you can use other editors, these instructions assume you're using VS Code. Install in terminal with:
    ```bash
    brew install --cask visual-studio-code
    ```

### PlotBot Download and Setup

1.  **Clone This Repository**
    *   Open a terminal window and navigate to your desired directory for downloading the repository. You can use the command below to create a GitHub folder in your root directory and switch to it (optional):

        ```bash
        mkdir -p ~/GitHub && cd ~/GitHub
        ```

    *   If you've previously attempted to install Plotbot, remove any existing installation:

        ```bash
        rm -rf ~/GitHub/Plotbot
        ```

    *   Clone this repository and change your working directory to the Plotbot directory. After you run this command you can follow the instructions in the terminal to complete the installation 💻:

        ```bash
        git clone https://github.com/Sonified/Plotbot.git && cd Plotbot && echo "✅ Download complete" && echo "" && echo "Copy and paste the following command, including the period, to initialize Conda for your shell: ./install_scripts/1_init_conda.sh" && echo ""
        ```

2.  **Now Run the Environment Setup Scripts in the Same Terminal Window** 

    *   First, initialize Conda for your shell:
       
        ```bash
        ./install_scripts/1_init_conda.sh
        ```

    *   Next, create the Plotbot environment from the YAML file:
        
        ```bash
        ./install_scripts/2_setup_env.sh
        ```

    *   Finally, register Plotbot as a Jupyter kernel (👉 if VS Code is open, close ❌ and reopen 🟢 it after this):
        
        ```bash
        ./install_scripts/3_register_kernel.sh
        ````

3.  **Open VS Code & Select the Environment**

    *   Open VS Code.
    *   Open `Plotbot.ipynb`.
    *   Click the kernel selector (top-right).
    *   Select "Python (Plotbot)".
    *   Run the first cell to confirm setup.

## Quick Start

In VS code hit 'Run All' and scroll down to see example plots:

*   Basic time series plots
*   Multi-panel synchronization
*   Hodogram (scatter) plots
*   Sonification/audification

## Required Versions (included in the environment)

*   Python: 3.12.4
*   NumPy: 1.26.4
*   Pandas: 2.2.2
*   Matplotlib: 3.9.2
*   cdflib: 1.3.1
*   BeautifulSoup: 4.12.3
*   requests: 2.32.2
*   python-dateutil: 2.9.0.post0
*   pytest: 7.4.4
*   termcolor: 2.4.0

## Running Tests

All tests for Plotbot are located in the `tests/` directory. You can run tests using the provided test runner:

```bash
# Run all tests
python run_tests.py

# Run a specific test file
python run_tests.py test_custom_variables.py

# Run a specific test function
python run_tests.py test_custom_variables.py::test_create_custom_variable
```

Alternatively, you can use pytest directly:

```bash
# Run all tests
pytest tests/

# Run a specific test file
pytest tests/test_custom_variables.py -v

# Run a specific test function
pytest tests/test_custom_variables.py::test_create_custom_variable -v
```

### Running Tests with Conda Environment
Make sure you're in the correct directory and using the plotbot_env conda environment:

```bash
# Run all tests in test_multiplot.py
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_multiplot.py -v

# Run a specific test function
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_multiplot.py::test_multiplot_single_custom_variable -v

# Run the options reset test
cd ~/GitHub/Plotbot && conda run -n plotbot_env python -m pytest tests/test_multiplot.py::test_options_reset -v
```

The `-v` flag provides verbose output, showing more detail about what's happening in the tests.

## Print Manager

Plotbot includes a comprehensive print manager system that controls all console output. This system allows you to filter the types of messages displayed, making it easier to debug or focus on specific aspects of the application.

### Basic Usage

The print manager is accessible through the `print_manager` singleton:

```python
from plotbot.print_manager import print_manager
```

### Debug Modes

There are several specialized debug modes you can enable:

```python
# Enable full debugging output (all message types)
print_manager.enable_debug()

# Enable only test output (useful for running tests)
print_manager.enable_test()

# Enable data cubby debugging (for tracking data storage)
print_manager.enable_datacubby()
```

### Fine-Grained Control

You can also control specific output types individually:

```python
# Control debug messages
print_manager.show_debug = True  # Show detailed technical diagnostic information

# Control variable and operation messages
print_manager.show_custom_debug = True  # Show custom variable operations debugging
print_manager.show_variable_testing = True  # Show variable testing specific debugging
print_manager.show_variable_basic = True  # Show basic user-facing variable info

# Control time tracking messages
print_manager.show_time_tracking = True  # Show time range tracking information

# Control test output messages
print_manager.show_test = True  # Show test-specific output
```

### For Legacy Code

For backward compatibility, the following aliases are also supported:

```python
# Legacy alias (same as show_variable_basic)
print_manager.show_status = True  

# Legacy alias (same as show_custom_debug)
print_manager.show_derived = True
```

### Sending Messages

To output messages through the print manager, use the appropriate method:

```python
# Regular debug messages
print_manager.debug("This is a detailed debug message")

# Critical debug messages (shown even when debug is disabled)
print_manager.debug("DBG-CRITICAL: This critical message is always shown")

# Test-specific messages
print_manager.test("This is a test-related message")

# Error messages
print_manager.error("This is an error message")

# Time tracking
print_manager.time_tracking("Time-related diagnostic information")

# Status messages
print_manager.status("User-friendly status update")
```

### Example: Testing with Isolated Output

When running tests, you often want to see only the test-related output:

```python
# In your test script
from plotbot.print_manager import print_manager

# Turn on only test output
print_manager.enable_test()

# Now run your tests
# Only messages sent via print_manager.test() will be displayed
```

This is particularly useful when debugging test failures, as it reduces noise from other parts of the system.

## Data Structure

Downloaded data is stored in:

```
psp_data/
  ├── fields/
  │    ├── l2/
  │    │    ├── mag_rtn/  <--- High Resolution
  │    │    ├── mag_rtn_4_Sa_per_Cyc/  <--- Standard Resolution
  │    │    ├── mag_sc/   <--- High Resolution
  │    │    └── mag_sc_4_Sa_per_Cyc/  <--- Standard Resolution
  ├── sweap/
  │    ├── spe/
  │    │    ├── l3/
  │    │    │    ├── spe_sf0_pad/  <--- Standard Resolution
  │    │    │    └── spe_af0_pad/  <--- High Resolution
  │    └── spi/
  │         └── l3/
  │              ├── spi_sf00_l3_mom/  <--- Standard Resolution
  │              └── spi_af00_l3_mom/  <--- High Resolution
  └── ...
```

## Using Plotbot's Data Classes

Plotbot is built around a system of data classes that make it easy to access, download, process, and plot Parker Solar Probe data. Here's a brief overview:

**1. Defining a Time Range:**

Our time range is defined as a list of strings in the format: 

`['YYYY-MM-DD/HH:MM:SS.fff', 'YYYY-MM-DD/HH:MM:SS.fff']`.  

For example:

```python
trange = ['2020-09-27/08:00:00.000', '2020-09-27/10:00:00.000']
```

**2. Calling the plotbot function:**

The core function is plotbot. You pass it the time range and pairs of data objects and axis numbers. For instance:

```python
plotbot(trange, mag_rtn.br, 1, epad.strahl, 2, proton.anisotropy, 3)
```

This call will:

*   Download standard resolution data for the:
    *   solar magnetic field as measured by the FIELDS instrument.
    *   associated electron strahl data as measured by the Solar Wind Electrons Alphas and Protons (SWEAP) / SPAN-e instrument.
    *   proton anisotropy from the SWEAP/SPAN-i instrument.
*   Plot `mag_rtn.br` on the first axis, `epad.strahl` on the second and `proton.anisotropy` on the third.\

**3. Customizing Plots**
Each of the data components (like mag_rtn.br) has various properties that you can modify to customize the plot appearance. You can set these properties before calling plotbot. Some examples:

```python
mag_rtn.br.color = 'green'  # Change the line color
mag_rtn.br.y_limit = (-50, 50)  # Set y-axis limits
```
**4. Available Data Products**

Here's a list of the currently available data products and their components.

**FIELDS Instrument (Magnetic Field):**

*   **Standard Resolution (4 samples per cycle, approximately 4 samples/second):**
    *   `mag_rtn_4sa`:  RTN (Radial, Tangential, Normal) coordinate system.
        *   `mag_rtn_4sa.br`: Radial component of the magnetic field.
        *   `mag_rtn_4sa.bt`: Tangential component.
        *   `mag_rtn_4sa.bn`: Normal component.
        *   `mag_rtn_4sa.bmag`: Magnetic field magnitude.
        *   `mag_rtn_4sa.all`: All three components (`br`, `bt`, `bn`) together, useful for multi-panel plots.
        *   `mag_rtn_4sa.pmag`: Magnetic pressure

    *   `mag_sc_4sa`: Spacecraft coordinate system.
        *   `mag_sc_4sa.bx`: X component.
        *   `mag_sc_4sa.by`: Y component.
        *   `mag_sc_4sa.bz`: Z component.
        *    `mag_sc_4sa.bmag`: Magnitude
        *   `mag_sc_4sa.all`: All three components.
        *    `mag_sc_4sa.pmag`: Magnetic pressure

*   **High Resolution:** Data is available using `mag_rtn` and `mag_sc` (without the `_4sa`).

**SWEAP/SPAN-e Instrument (Electron Data):**

*   **Standard Resolution:**
    *   `epad`:  Electron Pitch Angle Distributions (PAD).
        *    `epad.strahl`: Electron strahl data, displayed as a spectrogram.
        * `epad.centroids`: Centroid.

*   **High Resolution:** Data is available using `epad_hr`.

**SWEAP/SPAN-i Instrument (Proton Data):**

*   **Standard Resolution:**
    *   `proton`:  Proton moments and derived quantities.
        *   `proton.vr`: Radial velocity.
        *   `proton.vt`: Tangential velocity.
        *   `proton.vn`: Normal velocity.
        *   `proton.v_sw`: Solar wind speed.
        *   `proton.temperature`: Proton temperature.
        *   `proton.density`: Proton density.
        *   `proton.t_par`: Parallel temperature.
        *   `proton.t_perp`: Perpendicular temperature.
        *   `proton.anisotropy`: Temperature anisotropy (T_perp / T_par).
        *   `proton.v_alfven`:  Alfvén speed.
        *   `proton.beta_ppar`:  Parallel plasma beta.
        *   `proton.beta_pperp`: Perpendicular plasma beta.
        *   `proton.pressure`: Proton thermal pressure.
        *   `proton.pressure_ppar`: Parallel proton pressure.
        *   `proton.pressure_pperp`: Perpendicular proton pressure.
        *   `proton.energy_flux`: Proton energy flux spectrogram.
        *   `proton.theta_flux`: Proton theta flux spectrogram.
        *   `proton.phi_flux`: Proton phi flux spectrogram.

*   **High Resolution:** Data is available using `proton_hr`.

**5. Other Plotting Functions**
There are two other primary plotting methods in `Plotbot`:

*    `multiplot()`: The `multiplot` function provides similar capability to `plotbot` but allows for automated generation of many subplots, e.g. around perihelion.  See the 'Multiplotting Magic' section of the notebook for details on usage.
*   `showdahodo()`:  Creates a hodogram (scatter) plot of two variables.  This is useful for visualizing the relationship between, for example, two components of the magnetic field.  Examples are provided in the notebook.

**6. Data Audification:**

Plotbot also includes an `audifier` object, which allows you to create audio files (WAV format) from any of the data components.  Furthermore, you can generate a text file containing time markers.  This marker file can be directly imported into audio processing software like iZotope RX, allowing you to visually navigate the audio based on specific time points within the data. See the included Jupyter Notebook for examples.

Note: The current version of plotbot requires that you first use plotbot to download the data for the time range of interest, this will be updated soon.

Have Fun Plotbotting!

(This is a work in progress)
