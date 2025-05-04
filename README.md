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

## Example Usage & Notebook

The primary way to learn and use Plotbot is through the included Jupyter Notebook: `Plotbot.ipynb`. This notebook contains numerous examples demonstrating how to load data, customize plots, and use the various functions like `plotbot()`, `multiplot()`, `showdahodo()`, and `audifier()`.

A typical `plotbot()` call looks like this:

```python
# Import necessary components (This is done at the top of the notebook)
import plotbot
from plotbot import *

# Define the time range
trange = ['2018-10-22 12:00:00', '2018-10-27 13:00:00'] # Note: .fff for milliseconds is optional

# Plot variables on different axes
plotbot(trange, 
        mag_rtn_4sa.br, 1,  # Plot Br component of B-field (RTN, ~4 samples/sec) on axis 1
        epad.strahl, 2)     # Plot electron strahl spectrogram on axis 2 
```
This simple call automatically downloads the required data for the specified time range and generates a two-panel plot.

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

These versions are defined in the `environment.yml` file located in the project root directory.

*   Python: 3.12.4
*   NumPy: 1.26.4
*   Pandas: 2.2.2
*   Matplotlib: 3.9.2
*   SciPy: 1.15.2 
*   ipympl: (latest compatible) # For %matplotlib widget
*   ipywidgets: (latest compatible via pip) # For audifier and potentially other widgets
*   ipykernel: (latest compatible via pip) # For Jupyter kernel
*   pyspedas: (latest compatible via pip) # Space physics data analysis
*   cdflib: >=1.3.1
*   BeautifulSoup: 4.12.3 (beautifulsoup4)
*   requests: 2.32.2
*   python-dateutil: 2.9.0.post0
*   pytest: 7.4.4
*   termcolor: 2.4.0

**Data Source Configuration (`config.data_server`):**

By default, Plotbot now prioritizes downloading data from NASA's public CDAWeb/SPDF archive using the `pyspedas` library. This behavior can be controlled via the `config.data_server` setting found in `plotbot/config.py`. The available modes are:

*   **`'dynamic'` (Default):** Plotbot first attempts to download data from the SPDF server using `pyspedas`. If the data is not found on SPDF (e.g., it's too recent or not available), it will automatically fall back to attempting a download from the original Berkeley server. **Note:** Data unavailable on SPDF is often not yet public on the Berkeley server either and may require password authentication.
*   **`'spdf'`:** Plotbot will *only* attempt to download data from the SPDF server via `pyspedas`. If the data isn't found there, it will not attempt to download from Berkeley.
*   **`'berkeley'`:** Plotbot will *only* use the original method to download data directly from the Berkeley server, bypassing `pyspedas` and SPDF entirely.

This setting allows users to choose their preferred data source or rely on the dynamic fallback for maximum data availability.

### Enhanced IDE Support with Stub Files (`.pyi`)

To significantly improve the development experience within IDEs like VS Code, Plotbot now includes `.pyi` stub files for many core modules (e.g., `plot_manager.pyi` corresponds to `plot_manager.py`).

These stub files define the type signatures for functions, methods, classes, and attributes, acting as explicit blueprints for the code structure. The primary goal of adopting this approach was to:

*   **Supercharge Auto-Completion:** Provide the IDE with precise type information, leading to vastly more accurate and helpful suggestions as you type (e.g., seeing available methods and attributes for objects like `mag_rtn_4sa.br`).
*   **Improve Code Navigation:** Allow the IDE to better understand connections within the code, making it easier to jump to definitions and find usages.
*   **Clarify Expectations:** Make it clearer what kinds of data functions expect and return, directly within the development environment.

While these stubs *can* also be used by external type-checking tools, their main purpose within Plotbot is to make interacting with the code faster, easier, and less error-prone directly within your editor by boosting its built-in intelligence features.

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
mag_rtn.br.y_scale = 'log' # Set y-axis to log scale
```

**Note:** The `plotbot()` function can handle various plot types automatically based on the variable's definition, including:
*   `time_series`: Standard line plots.
*   `spectral`: 2D color mesh plots (spectrograms).
*   `scatter`: Scatter plots for data points that may not be continuous.

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

*    `multiplot()`: Designed for comparing a *single* variable across multiple consecutive time intervals. It automatically generates subplots for each interval, making it easy to analyze changes over extended periods or around events like perihelion. See the 'Multiplotting Magic' section of the notebook for usage details.
*   `showdahodo()`:  Creates a hodogram (scatter) plot comparing two variables against each other (instead of against time). This is useful for visualizing the relationship between, for example, two components of the magnetic field. Examples are provided in the notebook.

### Positional X-Axis in Multiplot

Plotbot supports plotting data against positional information on the x-axis (instead of time) in multi-panel plots:

```python
# 1. Setting positional data type (pick one to set to true)
plt.options.x_axis_r_sun = True           # Use radial distance (R_sun)
plt.options.x_axis_carrington_lon = True  # Use longitude (degrees)
plt.options.x_axis_carrington_lat = True  # Use latitude (degrees)

# 2. X-axis range control:
# Fixed range (min, max) - units depend on data type (degrees or R_sun)
plt.options.x_axis_positional_range = (0, 360)  # For longitude
plt.options.x_axis_positional_range = (11, 14)  # For radial

# Auto-scaling
plt.options.x_axis_positional_range = None

# 3. Common vs. separate axes:
plt.options.use_single_x_axis = True   # Common x-axis (shared across panels)
plt.options.use_single_x_axis = False  # Separate x-axis for each panel

# 4. Tick density control:
plt.options.positional_tick_density = 1  # Normal tick density
plt.options.positional_tick_density = 2  # Twice as many ticks
plt.options.positional_tick_density = 3  # Three times as many ticks

# Resetting options to ensure a clean slate
plt.options.reset() 
```

These options are mutually exclusive - setting one positional data type automatically disables the others. When using a positional x-axis, each panel's data is plotted against the corresponding positional values instead of time, making it easy to visualize how measurements change with distance from the Sun or across different Carrington longitudes/latitudes.

**6. Data Audification:**

Plotbot also includes an `audifier` object, which allows you to create audio files (WAV format) from any of the data components.  Furthermore, you can generate a text file containing time markers.  This marker file can be directly imported into audio processing software like iZotope RX, allowing you to visually navigate the audio based on specific time points within the data. See the included Jupyter Notebook for examples.

## Advanced Features

Beyond basic plotting, Plotbot offers powerful features for data analysis:

### Custom Variables

You can easily create new variables derived from existing data using standard arithmetic operations. Plotbot automatically handles the underlying data loading and calculation.

```python
from plotbot import custom_variable, proton, mag_rtn_4sa

# Example: Calculate Temperature Anisotropy over B Magnitude
ta_over_b = custom_variable('MyAnisotropyRatio', proton.anisotropy / mag_rtn_4sa.bmag)

# You can then plot this new variable like any other:
plotbot(trange, ta_over_b, 1)

# Customize its appearance:
ta_over_b.y_label = 'T_perp/T_par / B'
ta_over_b.y_scale = 'log'
```

Plotbot's `plotbot.data_classes.custom_variables.py` module manages these operations, ensuring that source data is available and calculations are updated when the time range changes. See `tests/test_custom_variables.py` and `tests/test_arithmetic.py` for more examples.

### Proton Distribution Function Fits

Plotbot includes capabilities for analyzing proton velocity distribution functions (VDFs) measured by SPAN-i. The `plotbot.data_classes.psp_proton_fits_classes.py` module defines classes to handle fitting parameters (like core/beam densities, temperatures, drifts) derived from these VDFs. The calculations themselves are performed by functions within `plotbot.calculations.calculate_proton_fits.py`.

While the fitting process itself is complex and currently requires manual setup or integration within specific analysis workflows, the resulting fit parameters can potentially be loaded and plotted using Plotbot's standard mechanisms once calculated. This feature is under active development. See `tests/test_fits_integration.py` for related tests.

### Print Manager

Plotbot includes a comprehensive print manager system that controls all console output. This system allows you to filter the types of messages displayed, making it easier to debug or focus on specific aspects of the application.

### Basic Usage

The print manager is accessible through the `print_manager` singleton:

```python
from plotbot.print_manager import print_manager
```
This is your best friend:
print_manager.show_status = True  

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

## Code Structure Overview

For those interested in contributing or understanding the internals:

*   **`Plotbot.ipynb`**: The main Jupyter Notebook demonstrating usage.
*   **`plotbot/`**: Contains the core Python code.
    *   **`__init__.py`**: Makes the package importable and exposes key functions/classes.
    *   **`plotbot.py`**: Simple import helper.
    *   **`plotbot_main.py`**: Contains the primary `plotbot()` function logic.
    *   **`multiplot.py`, `showdahodo.py`, `audifier.py`**: Implement other main features.
    *   **`data_classes/`**: Defines classes for each instrument/data product (e.g., `psp_mag_classes.py`, `psp_proton_classes.py`, `custom_variables.py`). These handle data attributes, plotting defaults, and sometimes calculations.
    *   **`calculations/`**: Houses more complex analysis code, like `calculate_proton_fits.py`.
    *   **`data_download.py`, `data_import.py`, `get_data.py`**: Handle fetching and loading data.
    *   **`data_cubby.py`, `data_tracker.py`**: Internal mechanisms for managing loaded data.
    *   **`plot_manager.py`**: Handles the underlying Matplotlib plotting logic.
    *   **`print_manager.py`**: Controls console output.
    *   **`test_pilot.py`**: Custom pytest runner framework.
    *   **`utils.py`, `time_utils.py`, `plotbot_helpers.py`, etc.**: Utility functions.
*   **`tests/`**: Contains all `pytest` tests.
*   **`install_scripts/`**: Scripts for setting up the Conda environment.
*   **`psp_data/`**: Default location for downloaded data (can be configured).
*   **`docs/`**: Additional documentation (if any).
*   **`environment.yml`**: Defines the Conda environment.
*   **`run_tests.py`**: Convenience script for running tests.

## Running Tests

Plotbot utilizes the `pytest` framework along with a custom space-themed runner (`plotbot/test_pilot.py`) for organized and informative testing. All tests reside in the `tests/` directory, categorized by the functionality they cover (e.g., `test_plotbot.py`, `test_multiplot.py`, `test_custom_variables.py`).

### Test Structure with `test_pilot.py`

Our tests follow a mission structure provided by `test_pilot.py`:
*   **Missions:** Each test function is marked with `@pytest.mark.mission("Mission Name")` to group related checks.
*   **Phases:** Within a test, `phase(number, "Description")` calls structure the test flow into logical steps.
*   **System Checks:** `system_check("Check Name", condition, "Failure Message")` performs assertions with clear reporting.

This structure, visible in files like `tests/test_plotbot.py`, provides detailed, space-themed output in the terminal, making it easier to track test progress and diagnose failures.

### Executing Tests

You can run tests using the provided `run_tests.py` script or directly with `pytest`.

**Using `run_tests.py`:**

```bash
# Run all tests
python run_tests.py

# Run a specific test file (e.g., test_custom_variables.py)
python run_tests.py test_custom_variables.py

# Run a specific test function within a file
python run_tests.py test_custom_variables.py::test_create_custom_variable
```

**Using `pytest` directly (often with Conda environment activation):**

Make sure you're in the correct directory (`~/GitHub/Plotbot`) and using the `plotbot_env` conda environment.

```bash
# Run all tests
conda run -n plotbot_env python -m pytest tests/ -v

# Run all tests in a specific file (e.g., test_multiplot.py)
conda run -n plotbot_env python -m pytest tests/test_multiplot.py -v

# Run a specific test function (e.g., test_multiplot_single_custom_variable)
conda run -n plotbot_env python -m pytest tests/test_multiplot.py::test_multiplot_single_custom_variable -v

# Run a specific mission
conda run -n plotbot_env python -m pytest tests/ -m "Custom Variable Time Range Update - Log Scale" -v
```

The `-v` flag provides verbose output. Add the `-s` flag (`pytest -v -s`) if you want to see output from `print()` statements within the tests (including `print_manager.test()` output when tests are run).

**Stardust Test Suite (`tests/test_stardust.py`):**
This special test file aggregates key tests from various modules (basic plotting, multiplot, showdahodo, HAM data, FITS data, custom variables, audification). It serves as a rapid, catch-all check for core Plotbot functionality. Running `conda run -n plotbot_env python -m pytest tests/test_stardust.py -v -s` is a good way to quickly verify the system's health after making changes.

Have Fun Plotbotting!

## Technical Notes For Developers:
**Important Note on Standard Variable Caching:**

A key aspect of Plotbot's efficiency for standard data products (like `mag_rtn_4sa`, `proton`, etc.) is how calculated data is stored and reused. Unlike custom variables which have a separate calculation tracking mechanism, standard variables cache their **calculated results** within the class instance itself, managed by `data_cubby`. Here's a breakdown confirmed by code analysis:

*   **Initial State:** When Plotbot starts, empty instances of data classes (e.g., `mag_rtn_4sa_class`) are created and stored in `data_cubby`.
*   **First Data Request:** When data is requested for a time range (`trange`) not yet covered:
    *   `get_data.py` identifies the need via `data_tracker.is_import_needed`.
    *   `data_import.py` fetches the **raw data** from files.
    *   This raw data is passed to the relevant class's `.update()` method (e.g., `mag_rtn_4sa.update(raw_data)`).
    *   Inside the class, `calculate_variables()` uses the raw data to perform calculations (e.g., `bmag = np.sqrt(...)`).
    *   The **calculated results** (e.g., the `bmag` NumPy array) are stored in the instance's internal `self.raw_data` dictionary.
    *   `set_ploptions()` then creates `plot_manager` objects (e.g., `self.bmag`), packaging these **calculated arrays** from `self.raw_data`.
    *   `data_cubby.stash(self, ...)` saves the *entire class instance*, which now contains the `plot_manager` objects holding the **calculated results**, back into the `data_cubby`.
    *   `data_tracker.update_imported_range` logs that this `trange` has been imported.
*   **Subsequent Requests (Covered `trange`):**
    *   `get_data.py` checks `data_tracker.is_import_needed` and finds the `trange` is covered.
    *   It **skips** calling `data_import.py` and **skips** calling the class's `.update()` method. No recalculation occurs for this standard variable.
    *   When plotting (`plotbot_main.py`), `data_cubby.grab(...)` retrieves the *existing class instance* (saved during the first request).
    *   The required `plot_manager` (e.g., `mag_rtn_4sa.bmag`) is extracted from this instance.
    *   Plotting proceeds using the **previously calculated and stored results** contained within that `plot_manager`.

In essence, standard variables recalculate *only when new raw data is imported* for a time range. Otherwise, the results calculated during the last relevant import are efficiently reused from the cached class instance.

**How Custom Variables Differ:**

Custom variables (created using arithmetic like `proton.anisotropy / mag_rtn_4sa.bmag`) handle caching differently:

*   **Dependency on Standard Variables:** They use standard variables as their inputs. When a custom variable needs to be recalculated (because `is_calculation_needed` returns true), it fetches the *current state* of its source standard variables from the `data_cubby`.
*   **Storing Calculated Results:** After recalculation, the new `plot_manager` object containing the **calculated result** is stored within the `CustomVariablesContainer` (which itself resides in `data_cubby`), replacing the previous result for that variable name.
*   **Triggering Data Updates:** Custom variables themselves don't directly trigger downloads. Instead, the main `plotbot` function ensures that the necessary source standard variables are up-to-date (by calling `get_data` on them) *before* it attempts to update or calculate the custom variable.

This difference allows custom variables to recalculate only when their specific cached calculation is deemed outdated for the requested time range, based on their own tracking, rather than being tied solely to the import status of their underlying source data files.

Now, let's look at the role of each module in this pipeline:

**`plotbot/get_data.py` (The Conductor):**
*   This is the main entry point called by functions like `plotbot()` when data is needed for a specific time range (`trange`) and set of variables.

**Plotbot Data Acquisition Pipeline Overview:**

```text
Simplified Data Flow

Request: plotbot(trange, mag_rtn.br, 1)
            |
          Calls
            |
            V
            get_data.py (The conductor)
            |
            V
            1. Identify Data Type Needed
            |
            [psp_data_types.py] <----- Data Configuration Hub 
            |                          (e.g. provides data_type key)
            |             
            V
            2. Check Cache for this data_type w/in provided trange
            |     
            [data_tracker.py] <----- Cache Manager
            |
            V
            3. Is Download Needed? (Y/N)
            |
    +---<---+-->--+
    |             |
   (N)           (Y)
    |             |
    |             V
    |             4. Initiate Download
    |             |                  
    |             V
    |             [data_download.py] (uses data_download_helpers.py)
    |             |              (process_directory calls server_access.py)
    |             V
    |<-------(Files Downloaded)
    |
    V
    5. Is Data Import Needed? 
    |                               
    [data_tracker.py] (tracks what's stored in data_cubby cache)
    |
    +-------------+
    |             |
   (N)           (Y)
    |             |
    |             6. Initiate Import of RAW Data
    |             |  
    |             [get_data.py]
    |             |  
    |            Calls
    |             |
    |             V
    |             [data_import.py] <----Reads RAW Variables/Columns from Files (CDF/CSV)
    |             |                     Uses Config: psp_data_types.py
    |             |                     Uses Libs: cdflib, pandas
    |             V                  
    |<---(Returns RAW DataObject)
    |
    (RAW DataObject ready from Importer)
    |
    V
    7. Update Class, Calculate Variables & Update Cache
       (get_data calls Class.update(RAW DataObject))
            |
            V [Inside Data Class Instance (e.g., psp_mag_classes.py)]
              - Takes RAW DataObject
              - Calls internal calculate_variables() -> Calculates derived quantities (e.g., Bmag) from raw data
              - Calls internal set_ploptions()      -> Stores results as interactive plot_manager objects (e.g., self.bmag)
       (get_data calls data_tracker.update...())
            |
            V
    ---> Data Ready for Plotting 
         (Accessible via Class instance, e.g., mag_rtn_4sa.bmag)
```

The process of getting data from a request (e.g., in `plotbot()` or `get_data()`) to being available for plotting involves several coordinated modules:

1.  **`plotbot/get_data.py` (The Conductor):**
    *   This is the main entry point called by functions like `plotbot()` when data is needed for a specific time range (`trange`) and set of variables.
    *   It first identifies the unique *types* of data required (e.g., `mag_RTN_4sa`, `proton`, `proton_fits`, `ham`) based on the input variables, consulting the configuration in `plotbot/data_classes/psp_data_types.py`.
    *   For each required data type, it orchestrates the subsequent steps.

2.  **`plotbot/data_tracker.py` (The Cache Manager):**
    *   Before fetching or loading, `get_data` consults the `global_tracker` instance defined here.
    *   This tracker remembers which time ranges have already been successfully *imported* from files or *calculated* (for types like `proton_fits`).
    *   Functions like `is_import_needed()` and `is_calculation_needed()` tell `get_data` whether it can skip fetching/loading/calculating steps if the requested `trange` is already covered by a previously processed range for that specific data type.

3.  **`plotbot/data_classes/psp_data_types.py` (The Configuration Hub):**
    *   This crucial dictionary defines the properties of *every* known data type Plotbot can handle.
    *   For standard downloadable CDF data (like FIELDS mag or SWEAP moments), it specifies the remote URL, local storage path structure, filename patterns (for finding/downloading), required password type (via `server_access`), expected CDF variable names inside the files, and time granularity (daily vs. 6-hour).
    *   For data sourced from local CSV files (like pre-calculated FITS results or Hammerhead data), it specifies `file_source: 'local_csv'`, the base path to search, filename patterns, and expected column names.

4.  **`plotbot/data_download.py` & `plotbot/data_download_helpers.py` (The Fetching Crew):**
    *   If `get_data` determines (based on `data_tracker` and `psp_data_types`) that remote CDF files *might* be needed, it calls `download_new_psp_data`.
    *   `download_new_psp_data` first calls `check_local_files` (from `data_download_helpers`) to see if the required files *already exist* locally for the `trange`.
    *   If files are missing, `download_new_psp_data` uses the URL and patterns from the `psp_data_types` config.
    *   `process_directory` (in `data_download_helpers`) handles contacting the remote server (using `authenticate_session` which leverages `plotbot/server_access.py`), parsing the HTML directory listing (`BeautifulSoup`) to find the *latest version* of the required file(s), and calling `download_file` to save them to the configured local path.

5.  **`plotbot/data_import.py` (The Importer & Calculator):**
    *   Once `get_data` knows the necessary files are available locally (either downloaded or inherently local like CSVs) and determines an import/refresh is needed (via `data_tracker`), it calls `import_data_function`.
    *   **For CDFs:** This function finds the relevant local CDF files for the `trange`, opens them using `cdflib`, extracts the time arrays and the specific data variables listed in `psp_data_types.py`, handles fill values (converting them to `NaN`), concatenates data from multiple files if necessary, sorts by time, and returns a structured `DataObject`.
    *   **For Calculated FITS (`proton_fits`):** When triggered by `get_data` (using a specific key like `'fits_calculated'`), this function reads the *raw* input CSVs (e.g., `sf00` type defined in `psp_data_types`) needed for the calculation, potentially calls the actual calculation function (like `calculate_proton_fits_vars` from `plotbot/calculations/`), processes the results, and returns them in the `DataObject` structure. *(Note: The exact triggering and calculation logic for FITS might be complex).*
    *   **For Other Local CSVs (`ham`):** Similar to FITS, it finds the relevant local CSVs based on the `psp_data_types` config, reads them (using `pandas`), handles time conversion (to TT2000), filters by the requested `trange`, concatenates, sorts, and returns a `DataObject`.

6.  **Back to `plotbot/get_data.py`:**
    *   Receives the `DataObject` (containing time and data arrays) from `data_import`.
    *   Updates the relevant global data class instance (e.g., `mag_rtn_4sa`, `proton`, `proton_fits`, `ham`) by calling its `.update()` method. This instance likely stores the data internally (potentially using `plotbot/data_cubby.py`).
    *   Calls `data_tracker.update_imported_range` or `update_calculated_range` to record that this `trange` has now been successfully processed for the given data type.

### Data Class and Plotting Architecture

```
Simplified Flow:
User Access          Instance of Data Class       plot_manager instance
(e.g. mag_rtn.br)    (e.g., mag_rtn object)       (The object returned)
      |                        |                           |
      '----------------------->' Access attribute (.br) ---> Returns the specific plot_manager
                                                               |
                                                        Holds Data (is ndarray)
                                                        Holds Plot Config (its ploptions attribute)

Internal Setup (within Data Class):
 __init__ / update()
      |
      V
 calculate_variables() <-- Reads imported DataObject (from data_import.py)
      |                   Stores results in self.raw_data
      V
 set_ploptions() ------> Creates plot_manager instance for each variable
                        (e.g., self.br = plot_manager(self.raw_data['br'], ploptions(...)))

Arithmetic & Custom Variables:
 plot_manager_A + plot_manager_B  (via __add__ etc. in plot_manager.py)
      |
      V
 New (Derived) plot_manager instance <-- Holds calculated data, links to sources A & B
      |
      V
 custom_variable("MyVar", ...) ------> Registers derived instance globally (plotbot.MyVar)
      |                                (Managed by custom_variables.py)
      V
 User Access (e.g. plotbot.MyVar) --> Acts like a standard plot_manager
```

**Detailed Explanation:**

1.  **Data Classes (`psp_*.py`, `psp_ham_classes.py`): The Organizers**
    *   **Role:** Each file defines a class (e.g., `mag_rtn_class`) managing data from a specific source (FIELDS, SPAN-i, SPAN-e, FITS CSVs, HAM CSVs).
    *   **Instantiation:** An instance of each class is created globally (e.g., `mag_rtn`) usually without data initially, and registered in the `data_cubby`.
    *   **`calculate_variables()`:** Triggered by the `update()` method when new data arrives from `data_import.py`. It processes the raw input `DataObject` and calculates specific physical quantities (e.g., B components, proton moments), storing results (NumPy arrays) in its internal `self.raw_data` dictionary.
    *   **`set_ploptions()`:** Called after `calculate_variables`. This method is key: it creates a separate `plot_manager` instance for *each* plottable variable (e.g., `self.br`, `self.bmag`).
    *   **Linking Data & Plotting:** When creating the `plot_manager` for `br`, it passes `self.raw_data['br']` (the actual data array) and a `ploptions` object containing default plot settings (labels, color, scale) specific to `br`.

2.  **`plotbot/ploptions.py`: The Style Configurator**
    *   **Role:** Defines the simple `ploptions` class.
    *   **Function:** Acts as a container holding plotting configuration attributes (like `y_label`, `color`, `line_style`, `plot_type`). An instance of `ploptions` is created and configured within the Data Class's `set_ploptions()` method for each variable.

3.  **`plotbot/plot_manager.py`: The Interactive Variable**
    *   **Role:** This is the object users typically interact with (e.g., `mag_rtn.br`). It represents a single plottable variable.
    *   **Dual Nature:** It subclasses `numpy.ndarray`, meaning it *is* the data array itself, allowing direct NumPy operations. It *also* holds the associated `ploptions` instance containing its plotting configuration and metadata (`data_type`, `class_name`, etc.).
    *   **User Customization:** Provides properties (`@property`, `@*.setter`) so users can easily get/set plotting attributes (`mag_rtn.br.color = 'blue'`), which modifies the underlying `ploptions` state.
    *   **Arithmetic (`__add__`, `__truediv__`, etc.):** Defines how operators work between `plot_manager` instances. When you perform `var_A / var_B`:
        *   It aligns the data arrays from `var_A` and `var_B` to a common time grid (interpolation).
        *   Performs the division.
        *   Creates and returns a *new* (derived) `plot_manager` instance containing the result. This derived instance stores references to its sources (`var_A`, `var_B`) and the operation ('div').

4.  **`plotbot/custom_variables.py`: Managing Derived Variables**
    *   **Role:** Manages user-defined variables created through arithmetic operations on `plot_manager` instances.
    *   **`custom_variable(name, expression)`:**
        *   Takes the derived `plot_manager` instance (`expression`) returned by an arithmetic operation (like `proton.anisotropy / mag_rtn_4sa.bmag`).
        *   Extracts the source variables and operation type stored on the `expression` object.
        *   Registers this derived variable under the given `name` in the `CustomVariablesContainer`.
        *   Makes the variable globally accessible (e.g., `plotbot.MyRatio`) so it can be used like any built-in variable.
        *   Assigns an `update` method that allows Plotbot to recalculate the variable using fresh source data when the time range changes, preserving user styling.


This structure separates data calculation (in Data Classes) from plotting configuration (`ploptions`) and interactive data handling (`plot_manager`), while allowing seamless creation and management of derived quantities (`custom_variables`).

### Standard Variable State Management: `data_cubby`, Class Instances, and Update Logic

While the main pipeline overview describes the general flow, the precise logic for updating standard data variables (like `mag_rtn_4sa`, `proton`, etc.) involves specific checks managed by `get_data.py` interacting with `data_cubby` and `data_tracker`.

1.  **Role of `data_cubby`:** The `data_cubby` acts as a registry, holding the global *instances* of the standard data classes (e.g., the `mag_rtn_4sa` object, which is an instance of `mag_rtn_4sa_class`). It does not store raw data separately for these types.

2.  **The Update Trigger - Two Conditions:** When `get_data.py` processes a request for a standard data type and a specific time range (`trange`), it determines if the cached instance needs updating based on *two* conditions:
    *   **`needs_import` Check:** It first asks `data_tracker.is_import_needed(trange, data_type)`. This checks if an import for this `data_type` covering this `trange` has been logged previously.
    *   **`needs_refresh` Check:** Independently, `get_data.py` retrieves the current class instance from `data_cubby`. It then directly inspects the time range of the data held within that instance (usually by checking the `datetime_array` attribute). It compares this cached time range against the requested `trange`. If the cached data doesn't fully cover the request, `needs_refresh` becomes true.

3.  **Executing the Update:** The `class_instance.update(data_obj)` method (which involves reading files via `import_data_function`, recalculating variables, and storing the results back in the instance) is called only if **`needs_import` is TRUE *OR* `needs_refresh` is TRUE**.
    *   **Handling Extended Ranges:** It's important to note that if the update is triggered because the requested `trange` extends beyond the time range currently held in the instance, `import_data_function` is designed to read the source files for the *entire extended `trange`*. It then concatenates this data and returns a complete `DataObject` covering the full extended period. The subsequent `class_instance.update()` call uses this new, larger `DataObject` to recalculate variables and store the results, effectively replacing the previous, shorter time range data within the instance with the complete data for the extended range.

4.  **Skipping the Update:** If *both* the tracker indicates the range was previously imported (`needs_import` is FALSE) *and* the direct check shows the currently cached instance already holds data covering the requested `trange` (`needs_refresh` is FALSE), then the `.update()` method is skipped entirely. `plotbot` will later retrieve this existing instance from `data_cubby` and use its already calculated data.

5.  **Contrast with Custom Variables:** This dual-check logic differs from custom variables. Custom variables rely solely on a single check (`data_tracker.is_calculation_needed`) which uses a separate tracking mechanism (`calculated_ranges`) specific to that variable's calculation state.

This ensures that standard variables are updated not only when new time ranges are encountered according to the tracker, but also if the specific data held in the cache doesn't adequately cover the request, providing robustness against potential inconsistencies.

### SPDF vs. Berkeley Filename Case Sensitivity

**Issue:** A case-sensitivity conflict was identified between local files downloaded via the Berkeley server and the local file check performed by `pyspedas` (specifically when using `no_update=True`, which is intended to check locally without hitting the network). Berkeley filenames often use different capitalization (e.g., `...mag_RTN_4_Sa_per_Cyc...`) than the patterns `pyspedas` typically expects or generates (e.g., `...mag_rtn_4_sa_per_cyc...`). On case-sensitive filesystems (or case-preserving filesystems like default macOS/APFS), the `pyspedas` `no_update=True` check fails to recognize the existing Berkeley-cased file, leading it to believe the file is missing locally.

**Symptom:** This resulted in the `download_spdf_data` function unnecessarily proceeding to the `no_update=False` step (which *does* contact the network index) even when a file covering the time range existed locally (downloaded from Berkeley). While the `no_update=False` step correctly identified the file as current and prevented a full re-download, it caused confusing log messages and bypassed the intended optimization of the `no_update=True` check.

**Solution:** The `plotbot/data_download_pyspedas.py` module now includes pre-emptive logic. Before calling `pyspedas` (when in `'spdf'` or `'dynamic'` mode), it checks the local data directory for files matching the Berkeley naming convention for the requested data type and time range. If found, it automatically renames the file(s) to match the expected SPDF (lowercase) naming convention defined by the `spdf_file_pattern` key in `plotbot/data_classes/psp_data_types.py`. This ensures the subsequent `pyspedas` `no_update=True` check finds the correctly-cased file, improving the reliability of the local check.

(This is a work in progress)

