# Captain's Log - 2025-08-06

## VDF Widget User Experience Improvements

### Major Enhancements to `vdyes()` Widget Interface

**Problem Solved**: The VDF widget had several user experience issues including matplotlib log scale warnings, black background artifacts, non-functional directory dialog, and poor status feedback.

**Key Improvements Made**:

### 1. **Matplotlib Warning Suppression** 
- **Issue**: VDF data naturally contains zero/negative values causing `Log scale: values of z <= 0 have been masked` warnings
- **Solution**: Added comprehensive warning filters in `vdyes.py`:
  ```python
  warnings.filterwarnings('ignore', message='Log scale: values of z <= 0 have been masked')
  warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
  warnings.filterwarnings('ignore', message='.*values of z <= 0.*')
  ```
- **Result**: Clean output without expected VDF warnings

### 2. **Widget Background and Display Issues**
- **Issue**: Black background areas around VDF plots in widget mode
- **Solution**: Applied consistent white backgrounds:
  ```python
  # Global matplotlib settings
  plt.rcParams['figure.facecolor'] = 'white'
  plt.rcParams['axes.facecolor'] = 'white'
  plt.rcParams['savefig.facecolor'] = 'white'
  
  # Explicit figure/axes backgrounds
  fig = plt.figure(figsize=(18, 6), facecolor='white')
  fig.patch.set_facecolor('white')
  ax = fig.add_subplot(gs[0], facecolor='white')
  ```
- **Removed**: `plt.tight_layout()` calls that caused compatibility warnings with gridspec
- **Result**: Clean white backgrounds, no layout warnings

### 3. **Directory Selection Dialog Fixes**
- **Issue**: Tkinter dialog not appearing in front, hanging "tk" windows
- **Solution**: Emulated proven `audifier.py` pattern:
  ```python
  def on_set_directory_click(b):
      from tkinter import Tk, filedialog
      
      root = Tk()
      root.withdraw()
      root.attributes('-topmost', True)
      
      try:
          selected_dir = filedialog.askdirectory(title="Select VDF Save Directory")
          # Process result...
      finally:
          root.quit()  # Stop the mainloop
          root.destroy()  # Ensure cleanup
  ```
- **Result**: Proper dialog appearance and cleanup

### 4. **Comprehensive Status System**
- **Issue**: No user feedback during operations, unclear what was happening
- **Solution**: Added real-time status label with detailed messaging:
  
  **Status Label**: 900px wide label showing current operations
  
  **Time Slider**: `Status: Displaying time 2020-01-29 18:00:04`
  
  **Save Current**: 
  - `Status: 💾 Saving /path/to/VDF_2020-01-29_18h_00m_04s.png...`
  - `Status: ✅ Complete! Saved to /path/to/VDF_2020-01-29_18h_00m_04s.png`
  
  **Render All**: 
  - `Status: 🎬 Rendering 86 VDF images...`
  - `Status: 🎬 Saving /path/to/VDF_2020-01-29_18h_00m_04s.png (1/86)`
  - `Status: ✅ Complete! All 86 images saved to /path/to/directory`
  
  **Directory Selection**:
  - `Status: 📁 Opening save directory dialog... Look for a 'Python' app in your dock/taskbar!`
  - `Status: ✅ Save directory set: /new/path`

### 5. **Widget Layout Optimization**
- **Issue**: Poor spacing and widget container styling
- **Solution**: 
  - Removed unnecessary padding (`padding='0px'`)
  - Simplified widget output styling
  - Added dedicated status display area
  - Improved button layout and spacing

### Files Modified:
- `plotbot/vdyes.py` - Complete widget user experience overhaul

### Technical Notes:
1. **VDF Log Warnings Are Normal**: Zero/negative values in velocity distribution functions are expected due to instrument noise floor and data gaps
2. **Audifier Pattern**: The directory selection follows the proven `audifier.py` pattern for reliable tkinter dialog handling
3. **Status vs Print**: Widget button handlers capture regular `print()` output, so status updates use direct label manipulation
4. **Full Path Display**: Status messages show complete file paths for transparency and debugging

### User Experience Impact:
- **Clean Interface**: No more warning clutter or black backgrounds
- **Clear Feedback**: Real-time status updates for all operations
- **Reliable Dialogs**: Directory selection works consistently
- **Professional Appearance**: Widget looks polished and production-ready

### Testing:
- Verified warning suppression with various VDF datasets
- Tested directory selection on macOS with dock behavior
- Confirmed status updates for all widget operations
- Validated full path display in status messages

This represents a major user experience improvement for the VDF widget system, making it suitable for production use and user demonstrations.

---

## VDF Parameter System and Smart Bounds Fixes

### Critical Issues Resolved in VDF Plotting System

**Problem**: The VDF plotting system had several critical issues preventing user parameter changes from working correctly:
1. Theta smart zoom used raw data range instead of bulk data percentile (causing poor zoom)
2. Intelligent zero clipping wasn't working for theta plane bounds
3. User parameter changes (like `psp_span_vdf.theta_smart_padding = 50`) had no effect on plots
4. Notebook examples used deprecated parameter names

### 1. **Smart Theta Bounds with Bulk Data Detection**
- **Issue**: `theta_square_bounds()` used full data range instead of bulk data percentile for zoom calculation
- **Solution**: Created new `theta_smart_bounds()` function in `vdf_helpers.py`:
  ```python
  def theta_smart_bounds(
      vx_theta, vz_theta, vdf_data, percentile, padding, enable_zero_clipping=True
  ):
      # Find bulk data using percentile threshold (default 10th percentile)
      valid_vdf = vdf_data[valid_mask]
      vdf_threshold = np.percentile(valid_vdf, percentile)
      bulk_mask = vdf_data > vdf_threshold
      
      # Calculate square bounds around bulk data only
      # Apply intelligent zero clipping for X-axis
      # Preserve Y-axis symmetry for theta plane
  ```
- **Result**: Theta plane now intelligently zooms to bulk data distribution, not full data range

### 2. **Intelligent Zero Clipping for Theta Plane**
- **Issue**: Zero clipping wasn't applied to theta bounds, causing plots to extend unnecessarily into positive velocity space when solar wind is entirely negative
- **Solution**: Integrated `apply_zero_clipping()` from `vdf_helpers.py` into theta bounds calculation
- **Logic**: 
  - If bulk data max Vx < 0 but padding pushes xlim past zero → clip X upper bound to 0
  - Preserve Y-axis symmetry around zero for theta plane (field-perpendicular structure)
- **Result**: Theta plane X-axis intelligently stops at zero when bulk solar wind is entirely negative

### 3. **Parameter System Fixes**
- **Issue**: User parameter changes weren't being respected in plots
- **Root Cause**: 
  - `vdyes()` static mode called wrong bounds function
  - `vdyes()` widget mode called wrong bounds function  
  - Parameter attribute access issues in `psp_span_vdf.py`
  
- **Solutions Applied**:
  ```python
  # Fixed vdyes.py static mode (line 160)
  theta_xlim, theta_ylim = vdf_class.get_theta_square_bounds(vx_theta, vz_theta, df_theta)
  
  # Fixed vdyes.py widget mode (line 282) 
  theta_xlim, theta_ylim = vdf_class.get_theta_square_bounds(vx_theta, vz_theta, df_theta)
  
  # Fixed psp_span_vdf.py bounds calculation
  def get_theta_square_bounds(self, vx_theta, vz_theta, df_theta):
      padding = getattr(self, 'theta_smart_padding', 100)  # Now reads user changes
      percentile = getattr(self, 'vdf_threshold_percentile', 10)
      enable_clipping = getattr(self, 'enable_zero_clipping', True)
  ```

### 4. **Notebook Parameter Examples Fixed**
- **Issue**: `plotbot_vdf_examples.ipynb` contained references to deprecated parameter names
- **Fixed**: Updated examples to use correct parameter system:
  ```python
  # OLD (didn't work):
  psp_span_vdf.theta_x_smart_padding = 50
  psp_span_vdf.theta_y_smart_padding = 50
  
  # NEW (works correctly):
  psp_span_vdf.theta_smart_padding = 50        # Single padding for square theta plane
  psp_span_vdf.vdf_figure_width = 18           # Plot size control
  psp_span_vdf.vdf_figure_height = 6
  ```

### 5. **Validated Parameter Hierarchy**
**Working Parameter System** (Manual > Smart > Jaye's defaults):

1. **Manual Limits** (highest priority):
   ```python
   psp_span_vdf.theta_x_axis_limits = (-800, 0)  
   psp_span_vdf.theta_y_axis_limits = (-400, 400)
   ```

2. **Smart Bounds** (with user control):
   ```python
   psp_span_vdf.enable_smart_padding = True
   psp_span_vdf.theta_smart_padding = 50         # User adjustable!
   psp_span_vdf.enable_zero_clipping = True      # User controllable!
   psp_span_vdf.vdf_threshold_percentile = 10    # Bulk data detection threshold
   ```

3. **Jaye's Reference Bounds** (fallback): `(-800, 0), (-400, 400)`

### Files Modified:
- `plotbot/vdf_helpers.py` - Added `theta_smart_bounds()` with bulk data detection
- `plotbot/data_classes/psp_span_vdf.py` - Fixed parameter access and bounds calculation  
- `plotbot/vdyes.py` - Fixed both static and widget modes to use smart bounds
- `plotbot_vdf_examples.ipynb` - User added plot size control demonstration

### User Impact:
- ✅ **Parameter changes now work**: `psp_span_vdf.theta_smart_padding = 50` immediately affects next plot
- ✅ **Intelligent zoom**: Theta plane focuses on bulk solar wind data, not full instrument range
- ✅ **Smart zero clipping**: X-axis automatically stops at zero when appropriate
- ✅ **Plot size control**: Users can adjust figure dimensions with `vdf_figure_width/height`

### Technical Notes:
- **Bulk Data Logic**: 10th percentile threshold separates bulk solar wind from instrument noise floor
- **Zero Clipping**: Only applied when bulk data is entirely on one side of zero (preserves bi-directional flows)
- **Square Aspect**: Theta plane maintains square aspect ratio with Y-axis centered at zero (preserves field-perpendicular structure visualization)

This fixes a critical user experience issue where VDF parameter adjustments appeared to do nothing, making the system properly responsive to user customization.

---

## Version Information
- **Previous Version**: v3.05 - "v3.05 Enhancement: Major VDF widget UX improvements - status system, background fixes, directory dialog, warning suppression"
- **Current Version**: v3.06 - "v3.06 Fix: VDF parameter system - manual bounds now work, smart theta bounds with bulk data detection, intelligent zero clipping"
- **Date**: 2025-08-06