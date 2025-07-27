# Captain's Log - 2025-05-01

---

*   **Bug Fix: SPDF Data Download Completeness:** Resolved an issue where the SPDF download mechanism (used in `spdf` and `dynamic` modes) would incorrectly stop if *any* local file matching the data type was found within the requested time range, even if the local files didn't cover the *entire* range. This could lead to incomplete datasets being loaded. The fix involved removing the initial local-only check (`no_update=True`) in `plotbot/data_download_pyspedas.py`, ensuring that the function now always proceeds to the `no_update=False` check, which correctly assesses local files against the required range and downloads missing data or newer versions from the server as needed. 

*   **Enhancement: Case-Insensitive Server Config:** Modified `plotbot/get_data.py` to handle the `config.data_server` setting (`'spdf'`, `'berkeley'`, `'dynamic'`) in a case-insensitive manner. It now converts the value to lowercase before checking it, preventing potential issues caused by inconsistent capitalization in the configuration. 

*   **Bug Fix: Longitude Mapping Axis Issues:** Fixed a critical issue where enabling longitude mapping (`use_longitude_x_axis=True`) would sometimes show no data on the plot or display time values on the x-axis instead of longitude values. The fixes include:
    * Better handling of datetime formats in the `LongitudeMapper` class
    * Explicit disabling of `use_longitude_x_axis` if the longitude data fails to load
    * Auto-disabling of `use_relative_time` when longitude mapping is active (these features conflict)
    * Improved x-axis formatting for longitude display, including proper tick placement and limits
    * Additional diagnostic information to troubleshoot longitude mapping issues
    * Added a test utility that can verify longitude mapping functionality independently

*   **Enhancement: Robust Longitude Data Type Conversion:** Enhanced the `map_to_longitude` method to handle different datetime formats by attempting automatic conversion to `numpy.datetime64`, making the function more robust to different input data types.

*   **Feature: Enhanced Positional X-Axis Support for Multiplots:** Implemented comprehensive support for using different positional data types on the x-axis in multi-panel plots:
    * Added support for three positional x-axis options: 
      * Carrington longitude (degrees)
      * Radial distance (solar radii / R_sun)
      * Carrington latitude (degrees)
    * Created a mutually exclusive API where setting one option automatically disables others
    * Implemented read-only properties to check which option is active
    * Added `x_axis_positional_range` property to allow setting fixed ranges for the x-axis
    * Implemented smart range handling for both single and multiple x-axis modes:
      * Common x-axis: applies the same range to all panels 
      * Separate axes: each panel has its own range based on its data
    * Added `positional_tick_density` property to control the number of ticks on positional x-axes
    * Fixed `reset()` method to properly reset all positional x-axis properties
    * Created diagnostic utilities:
      * `analyze_positional_data_ranges.py`: Analyzes ranges for different encounters
      * `demo_x_axis_positional_options.py`: Demonstrates how to use the new options
    * Created comprehensive test suite to verify positional x-axis functionality

*   **Enhancement: Added default settings to the plot to optimize display (multiplot)**

*   **Feature: HAM Data Integration for Multiplot Right Axis:** Designed a comprehensive implementation plan to display HAM data on the right axis of multiplot panels:
    * Step 1: Add new options to `MultiplotOptions` class in `multiplot_options.py`: (DONE)
      ```python
      # Original (in reset method)
      # No HAM-specific options
      
      # New (in reset method)
      self.hamify = False
      self.ham_var = None  # Will hold the actual plot_manager object
      ```
    
    * Step 2: Add corresponding property getters/setters: (DONE)
      ```python
      @property
      def hamify(self) -> bool:
          """Whether to display HAM data on right axis when available."""
          return self.__dict__['hamify']
          
      @hamify.setter
      def hamify(self, value: bool):
          self.__dict__['hamify'] = value
          
      @property
      def ham_var(self):
          """HAM variable to display on right axis (actual plot_manager object)."""
          return self.__dict__['ham_var']
          
      @ham_var.setter
      def ham_var(self, value):
          self.__dict__['ham_var'] = value
      ```
    
    * Step 3: Update the stub file `multiplot_options.pyi` to include new properties: (DONE)
      ```python
      # In MultiplotOptions class
      hamify: bool
      ham_var: Any  # Will be a plot_manager object
      ```
    
    * Step 4: Implement HAM plotting in `multiplot.py`, adding this logic after primary variable plotting: (DONE)
      ```python
      # Add after primary variable plotting for each panel
      if options.hamify and options.ham_var is not None and not options.second_variable_on_right_axis:
          # Use ham_var directly - it's already the plot_manager object
          ham_var = options.ham_var
          
          if ham_var is not None and hasattr(ham_var, 'datetime_array') and ham_var.datetime_array is not None:
              # Create a twin axis for the HAM data
              ax2 = axs[i].twinx()
              
              # Get color - use right axis color if specified, otherwise use ham_var's color
              if hasattr(axis_options, 'r') and axis_options.r.color is not None:
                  plot_color = axis_options.r.color
              else:
                  plot_color = ham_var.color
                  
              # Get time-clipped indices
              ham_indices = time_clip(ham_var.datetime_array, trange[0], trange[1])
              
              if len(ham_indices) > 0:
                  # Get x-axis data and handle positional mapping
                  x_data = ham_var.datetime_array[ham_indices]
                  if using_positional_axis and positional_mapper is not None:
                      lon_vals = positional_mapper.map_to_position(x_data, data_type)
                      if lon_vals is not None:
                          x_data = lon_vals
                  
                  # Plot the HAM data
                  ax2.plot(x_data, 
                          ham_var.data[ham_indices],
                          linewidth=ham_var.line_width,
                          linestyle=ham_var.line_style,
                          label=ham_var.legend_label,
                          color=plot_color)
                  
                  # Apply y-limits if specified
                  if hasattr(axis_options, 'r') and axis_options.r.y_limit is not None:
                      ax2.set_ylim(axis_options.r.y_limit)
                  elif hasattr(ham_var, 'y_limit') and ham_var.y_limit:
                      ax2.set_ylim(ham_var.y_limit)
                      
                  # Include HAM in legend
                  lines_left, labels_left = axs[i].get_legend_handles_labels()
                  lines_right, labels_right = ax2.get_legend_handles_labels()
                  axs[i].legend(lines_left + lines_right, 
                              labels_left + labels_right,
                              bbox_to_anchor=(1.025, 1),
                              loc='upper left')
      ```
    
    * Step 5: Create a test for HAM data multiplot functionality: (DONE)
      * Create a new test file in the tests folder
      * Implement a multiplot that shows data +/- 3 hours around noon on 2025-03-19, 2025-03-20, and 2025-03-21
      * Configure the test to use HAM data on the right axis
      * Verify that the HAM data is properly displayed on the plot
      * Test with both time-based and positional x-axis options

---

*   **Version Update:** Updated version number from `2025_05_01_v1.16` to `2025_05_02_v1.17` to reflect the new positional x-axis functionality. Updated documentation in README.md with examples of how to use the new positional x-axis options.