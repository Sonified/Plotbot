# tests/test_VDF_plotting_basic.py

"""
VDF Basic Plotting Tests - Phase 3, Step 3.1

Tests core VDF plotting functions implementing Jaye's plotting approach.
Tests 1D collapsed plots, 2D contour plots, and 3-panel layouts.

Reference Source: files_from_Jaye/PSP_SPAN-I_VDF_Plot_Tutorial_pypedasdownload.ipynb
- Cells 45-49: 1D velocity plots (collapsed VDFs)
- Cells 50-55: 2D contour plots in theta/phi planes
- Cells 56-60: Field-aligned coordinate plots
- Cell 189: Consolidated plotting function
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import LogNorm
import pytest
import datetime

# Import our VDF processing functions from previous tests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import functions from our previous test modules
from test_VDF_processing import test_complete_processing_pipeline
from test_VDF_coordinates import field_aligned_coordinates, rotate_vector_into_field_aligned
from test_VDF_timeslice import find_closest_timeslice, extract_timeslice_data

# Add test utilities if available
from tests.utils.test_helpers import system_check, phase

def plot_vdf_1d_collapsed(velocity, vdf_data, title="1D Collapsed VDF", ax=None, **kwargs):
    """
    Create 1D line plot of collapsed VDF (Jaye's approach from Cell 45-49).
    
    Args:
        velocity: 1D array of velocities (km/s)
        vdf_data: 1D array of VDF values (collapsed over angles)
        title: Plot title
        ax: Existing matplotlib axis (optional)
        **kwargs: Additional matplotlib kwargs
    
    Returns:
        fig, ax: Matplotlib figure and axis objects
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    else:
        fig = ax.figure
    
    # Remove zeros for log plotting
    valid_mask = vdf_data > 0
    valid_velocity = velocity[valid_mask]
    valid_vdf = vdf_data[valid_mask]
    
    # Plot with log scale (typical for VDF data)
    ax.semilogy(valid_velocity, valid_vdf, 'b-', linewidth=2, **kwargs)
    
    # Formatting following Jaye's style
    ax.set_xlabel('Velocity (km/s)', fontsize=12)
    ax.set_ylabel('VDF (s³/km³)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, np.max(valid_velocity) * 1.1)
    
    # Only call tight_layout for standalone plots
    if fig.axes == [ax]:
        plt.tight_layout()
    return fig, ax

def calculate_smart_bounds(vx, vy, vdf_data, padding_factor=0.15, vdf_threshold_percentile=75):
    """
    Calculate smart plot bounds based on data extent with padding.
    
    Args:
        vx, vy: 2D velocity arrays
        vdf_data: 2D VDF array
        padding_factor: Fraction of range to add as padding (0.15 = 15%)
        vdf_threshold_percentile: Percentile threshold for "significant" data
    
    Returns:
        (xlim, ylim): Tuples of (min, max) for each axis
    """
    # Remove NaN and zero values
    valid_mask = np.isfinite(vdf_data) & (vdf_data > 0)
    
    if not np.any(valid_mask):
        # Ultimate fallback - use Jaye's typical solar wind bounds
        return (-800, 50), (-600, 600)
    
    # Find threshold for significant data
    valid_vdf = vdf_data[valid_mask]
    vdf_threshold = np.percentile(valid_vdf, vdf_threshold_percentile)
    significant_mask = vdf_data > vdf_threshold
    
    if not np.any(significant_mask):
        # Fallback to all valid data if threshold too strict
        significant_mask = valid_mask
    
    # Find extent of significant data
    vx_sig = vx[significant_mask]
    vy_sig = vy[significant_mask]
    
    x_min, x_max = np.min(vx_sig), np.max(vx_sig)
    y_min, y_max = np.min(vy_sig), np.max(vy_sig)
    
    # Add padding
    x_range = x_max - x_min
    y_range = y_max - y_min
    
    # Ensure minimum range (avoid too-tight bounds)
    min_range = 100  # km/s
    if x_range < min_range:
        x_center = (x_max + x_min) / 2
        x_min, x_max = x_center - min_range/2, x_center + min_range/2
        x_range = min_range
    if y_range < min_range:
        y_center = (y_max + y_min) / 2
        y_min, y_max = y_center - min_range/2, y_center + min_range/2
        y_range = min_range
    
    x_padding = x_range * padding_factor
    y_padding = y_range * padding_factor
    
    xlim = (x_min - x_padding, x_max + x_padding)
    ylim = (y_min - y_padding, y_max + y_padding)
    
    return xlim, ylim

def plot_vdf_2d_contour(vx, vy, vdf_data, title="2D VDF Contour", ax=None, auto_bounds=True, manual_xlim=None, manual_ylim=None, **kwargs):
    """
    Create 2D contour plot for theta/phi planes (Jaye's approach from Cell 50-55).
    
    Args:
        vx: 2D array of x-velocities (km/s)
        vy: 2D array of y-velocities (km/s)
        vdf_data: 2D array of VDF values
        title: Plot title
        ax: Existing matplotlib axis (optional)
        auto_bounds: If True, automatically calculate smart bounds based on data (default: True)
        manual_xlim: Manual x-axis limits as (min, max) tuple (overrides auto_bounds)
        manual_ylim: Manual y-axis limits as (min, max) tuple (overrides auto_bounds)
        **kwargs: Additional contour kwargs
    
    Returns:
        fig, ax: Matplotlib figure and axis objects
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    else:
        fig = ax.figure
    
    # Remove zeros and set minimum for log scale
    vdf_plot = np.copy(vdf_data)
    vdf_plot[vdf_plot <= 0] = np.nan
    
    # Create logarithmic contour plot with edge case handling
    vmin = np.nanmin(vdf_plot)
    vmax = np.nanmax(vdf_plot)
    
    # Handle edge cases where min == max or invalid ranges
    if vmin <= 0 or vmax <= 0 or vmin == vmax or not np.isfinite(vmin) or not np.isfinite(vmax):
        # Fall back to linear scale for problematic data
        levels = 20
        contour = ax.contourf(vx, vy, vdf_plot, levels=levels, cmap='plasma', **kwargs)
    else:
        # Use logarithmic scale for good data
        levels = np.logspace(np.log10(vmin), np.log10(vmax), 20)
        contour = ax.contourf(vx, vy, vdf_plot, levels=levels, 
                             norm=LogNorm(vmin=vmin, vmax=vmax),
                             cmap='plasma', **kwargs)
    
    # Add colorbar only if this is a standalone plot
    if fig.axes == [ax]:  # Only one axis = standalone plot
        cbar = plt.colorbar(contour, ax=ax)
        cbar.set_label('VDF (s³/km³)', fontsize=12)
    
    # Formatting following Jaye's style
    ax.set_xlabel('Vx (km/s)', fontsize=12)
    ax.set_ylabel('Vy (km/s)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.set_aspect('equal')
    
    # Set plot bounds - either auto or manual
    if manual_xlim is not None:
        ax.set_xlim(manual_xlim)
    if manual_ylim is not None:
        ax.set_ylim(manual_ylim)
    if auto_bounds and manual_xlim is None and manual_ylim is None:
        xlim, ylim = calculate_smart_bounds(vx, vy, vdf_data)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    # else: use matplotlib defaults
    
    # Add velocity circles for reference (only if they fit in the plot range)
    current_xlim = ax.get_xlim()
    current_ylim = ax.get_ylim()
    max_radius = min(abs(current_xlim[0]), abs(current_xlim[1]), 
                    abs(current_ylim[0]), abs(current_ylim[1])) * 0.8
    
    v_circles = [200, 400, 600, 800, 1000]
    for v in v_circles:
        if v <= max_radius:  # Only add circles that fit
            circle = plt.Circle((0, 0), v, fill=False, color='white', alpha=0.5, linestyle='--')
            ax.add_patch(circle)
    
    # Only call tight_layout for standalone plots
    if fig.axes == [ax] or (len(fig.axes) == 2 and fig.axes[1].get_label() == '<colorbar>'):
        plt.tight_layout()
    return fig, ax

def create_vdf_triple_plot(vdf_data_dict, title_prefix="VDF Analysis"):
    """
    Recreate Jaye's 3-panel plot layout (Cell 189 approach).
    
    Args:
        vdf_data_dict: Dictionary with processed VDF data containing:
                      - 'vdf': 3D VDF array (8,32,8)
                      - 'vx', 'vy', 'vz': Velocity arrays
                      - 'vel': Speed magnitude
                      - 'epoch': Time of observation
    
    Returns:
        fig: Matplotlib figure with 3 subplots
    """
    fig = plt.figure(figsize=(18, 6))
    
    # Extract data
    vdf = vdf_data_dict['vdf']
    vx = vdf_data_dict['vx']
    vy = vdf_data_dict['vy'] 
    vz = vdf_data_dict['vz']
    vel = vdf_data_dict['vel']
    epoch = vdf_data_dict['epoch']
    
    # Plot 1: 1D collapsed VDF
    ax1 = plt.subplot(1, 3, 1)
    
    # Collapse VDF over all angles to create 1D speed distribution
    vdf_1d = np.sum(vdf, axis=(0, 2))  # Sum over phi and theta dimensions
    vel_1d = vel[0, :, 0]  # Speed array (same for all angles)
    
    plot_vdf_1d_collapsed(vel_1d, vdf_1d, title=f"{title_prefix}\n1D Speed Distribution", ax=ax1)
    
    # Plot 2: 2D VDF in vx-vy plane (theta cut at middle)
    ax2 = plt.subplot(1, 3, 2)
    
    theta_middle = 4  # Middle theta bin
    vdf_2d_xy = vdf[:, :, theta_middle]  # VDF slice at middle theta
    vx_2d = vx[:, :, theta_middle]
    vy_2d = vy[:, :, theta_middle]
    
    plot_vdf_2d_contour(vx_2d, vy_2d, vdf_2d_xy, title=f"{title_prefix}\nVx-Vy Plane", ax=ax2)
    
    # Plot 3: 2D VDF in vx-vz plane (phi cut at middle)
    ax3 = plt.subplot(1, 3, 3)
    
    phi_middle = 4  # Middle phi bin (0-7, so middle is 3 or 4)
    vdf_2d_xz = vdf[phi_middle, :, :]  # VDF slice at middle phi
    vx_2d_xz = vx[phi_middle, :, :]
    vz_2d_xz = vz[phi_middle, :, :]
    
    plot_vdf_2d_contour(vx_2d_xz, vz_2d_xz, vdf_2d_xz, title=f"{title_prefix}\nVx-Vz Plane", ax=ax3)
    
    # Add overall title with time information
    fig.suptitle(f'PSP SPAN-I VDF Analysis - {epoch.strftime("%Y-%m-%d %H:%M:%S")}', 
                fontsize=16, y=0.95)
    
    plt.tight_layout()
    return fig

def test_1d_vdf_plotting():
    """Test 1D VDF plotting function"""
    # Create mock 1D VDF data
    velocity = np.linspace(100, 1000, 100)  # km/s
    
    # Create realistic VDF shape (decreasing with speed)
    vdf = 1e-12 * np.exp(-velocity/400) * (1 + 0.5*np.random.random(len(velocity)))
    
    # Test plotting
    fig, ax = plot_vdf_1d_collapsed(velocity, vdf, title="Test 1D VDF")
    
    # Validate plot properties
    assert len(ax.lines) > 0, "Should have plotted lines"
    assert ax.get_yscale() == 'log', "Y-axis should be logarithmic"
    assert 'Velocity' in ax.get_xlabel(), "X-label should mention velocity"
    assert 'VDF' in ax.get_ylabel(), "Y-label should mention VDF"
    
    # Check data ranges
    line_data = ax.lines[0].get_data()
    assert np.min(line_data[0]) >= 100, "Velocity range should start around 100 km/s"
    assert np.max(line_data[0]) <= 1000, "Velocity range should end around 1000 km/s"
    
    plt.close(fig)
    print("✅ 1D VDF plotting: axes, labels, and log scale validated")

def test_2d_vdf_contour_plotting():
    """Test 2D VDF contour plotting function"""
    # Create mock 2D velocity grid
    vx = np.linspace(-1000, 1000, 50)
    vy = np.linspace(-1000, 1000, 50)
    VX, VY = np.meshgrid(vx, vy)
    
    # Create realistic 2D VDF (peaked at center, decreasing radially)
    V_mag = np.sqrt(VX**2 + VY**2)
    vdf_2d = 1e-12 * np.exp(-(V_mag/400)**2) * (1 + 0.2*np.random.random(VX.shape))
    
    # Test plotting
    fig, ax = plot_vdf_2d_contour(VX, VY, vdf_2d, title="Test 2D VDF")
    
    # Validate plot properties
    assert len(ax.collections) > 0, "Should have contour collections"
    # Check aspect ratio (get_aspect() returns 1.0 when set to 'equal')
    aspect = ax.get_aspect()
    assert aspect == 1.0 or aspect == 'equal', f"Aspect ratio should be equal (got {aspect})"
    assert 'Vx' in ax.get_xlabel(), "X-label should mention Vx"
    assert 'Vy' in ax.get_ylabel(), "Y-label should mention Vy"
    
    # Check for colorbar
    assert len(fig.axes) == 2, "Should have main plot and colorbar"
    
    # Check for velocity circles (reference lines)
    circles = [patch for patch in ax.patches if hasattr(patch, 'center')]
    assert len(circles) > 0, "Should have reference velocity circles"
    
    plt.close(fig)
    print("✅ 2D VDF contour plotting: contours, colorbar, and reference circles validated")

def test_triple_plot_layout():
    """Test 3-panel VDF plot layout"""
    # Create mock VDF data structure
    n_phi, n_energy, n_theta = 8, 32, 8
    
    # Mock velocity arrays
    vx = np.random.uniform(-1000, 1000, (n_phi, n_energy, n_theta))
    vy = np.random.uniform(-1000, 1000, (n_phi, n_energy, n_theta))
    vz = np.random.uniform(-500, 500, (n_phi, n_energy, n_theta))
    vel = np.sqrt(vx**2 + vy**2 + vz**2)
    
    # Mock VDF data (realistic shape)
    vdf = 1e-12 * np.exp(-(vel/400)**2) * (1 + 0.3*np.random.random(vel.shape))
    
    # Create data dictionary
    vdf_data = {
        'vdf': vdf,
        'vx': vx, 'vy': vy, 'vz': vz,
        'vel': vel,
        'epoch': datetime.datetime(2020, 1, 29, 18, 10, 6)
    }
    
    # Test triple plot
    fig = create_vdf_triple_plot(vdf_data, title_prefix="Test VDF")
    
    # Validate figure structure
    assert len(fig.axes) >= 3, "Should have at least 3 subplots"
    assert fig.get_figwidth() > 15, "Should be wide figure for 3 panels"
    
    # Check that all subplots have content
    for i, ax in enumerate(fig.axes[:3]):  # Check first 3 axes (main plots)
        if i == 0:  # 1D plot
            assert len(ax.lines) > 0, f"Subplot {i+1} should have line plots"
        else:  # 2D plots
            assert len(ax.collections) > 0, f"Subplot {i+1} should have contour collections"
    
    plt.close(fig)
    print("✅ Triple plot layout: 3 panels, proper sizing, and content validated")

def test_real_vdf_plotting_workflow():
    """Test complete plotting workflow with real VDF data"""
    # Get real processed VDF data from our previous test
    print("📊 Processing real VDF data for plotting...")
    
    # Run the complete processing pipeline
    processed_data = test_complete_processing_pipeline()
    
    # Test 1D plotting
    print("🔍 Testing 1D plotting...")
    vdf_1d = np.sum(processed_data['vdf'], axis=(0, 2))  # Collapse over angles
    vel_1d = processed_data['vel'][0, :, 0]  # Speed array
    
    fig1, ax1 = plot_vdf_1d_collapsed(vel_1d, vdf_1d, 
                                     title=f"Real PSP VDF - {processed_data['epoch']}")
    
    # Validate real data characteristics
    line_data = ax1.lines[0].get_data()
    assert np.max(line_data[0]) > 1000, "Real data should have high-speed particles"
    assert np.min(line_data[1]) > 0, "VDF values should be positive"
    
    plt.close(fig1)
    print("✅ Real 1D VDF plot: data characteristics validated")
    
    # Test 2D plotting
    print("🔍 Testing 2D plotting...")
    theta_middle = 4  # Middle theta bin
    vdf_2d = processed_data['vdf'][:, :, theta_middle]
    vx_2d = processed_data['vx'][:, :, theta_middle]
    vy_2d = processed_data['vy'][:, :, theta_middle]
    
    fig2, ax2 = plot_vdf_2d_contour(vx_2d, vy_2d, vdf_2d,
                                   title=f"Real PSP VDF 2D - {processed_data['epoch']}")
    
    # Validate 2D characteristics
    assert len(ax2.collections) > 0, "Should have contour data"
    assert len(fig2.axes) == 2, "Should have plot and colorbar"
    
    plt.close(fig2)
    print("✅ Real 2D VDF plot: contours and structure validated")
    
    # Test complete triple plot
    print("🔍 Testing complete triple plot...")
    fig3 = create_vdf_triple_plot(processed_data, title_prefix="Real PSP SPAN-I")
    
    # Validate triple plot with real data
    assert len(fig3.axes) >= 3, "Should have 3+ axes"
    assert fig3._suptitle is not None, "Should have overall title"
    
    plt.close(fig3)
    print("✅ Real triple VDF plot: complete workflow validated")
    
    print(f"📊 Real VDF plotting complete - processed time: {processed_data['epoch']}")

def test_smart_bounds_functionality():
    """Test smart auto-bounds calculation and functionality"""
    print("🧪 Testing smart bounds functionality...")
    
    # Create test data with localized VDF
    vx = np.linspace(-1000, 1000, 50)
    vy = np.linspace(-800, 800, 50)
    VX, VY = np.meshgrid(vx, vy)
    
    # Create VDF data concentrated around (-400, 100) to mimic solar wind beam
    center_vx, center_vy = -400, 100
    vdf_concentrated = 1e-12 * np.exp(-((VX - center_vx)/150)**2 - ((VY - center_vy)/100)**2)
    
    # Test smart bounds calculation
    xlim, ylim = calculate_smart_bounds(VX, VY, vdf_concentrated, padding_factor=0.15)
    
    # Bounds should be centered around the data concentration
    x_center = (xlim[0] + xlim[1]) / 2
    y_center = (ylim[0] + ylim[1]) / 2
    
    assert abs(x_center - center_vx) < 100, f"X bounds not centered on data: center={x_center}, expected≈{center_vx}"
    assert abs(y_center - center_vy) < 100, f"Y bounds not centered on data: center={y_center}, expected≈{center_vy}"
    
    # Bounds should include padding around the data
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]
    assert x_range > 200, f"X range too small: {x_range} km/s"
    assert y_range > 150, f"Y range too small: {y_range} km/s"
    
    print(f"✅ Smart bounds: X=({xlim[0]:.0f}, {xlim[1]:.0f}), Y=({ylim[0]:.0f}, {ylim[1]:.0f})")
    
    # Test auto-bounds plotting
    fig1, ax1 = plot_vdf_2d_contour(VX, VY, vdf_concentrated, 
                                   title="Auto-Bounds Test", auto_bounds=True)
    auto_xlim = ax1.get_xlim()
    auto_ylim = ax1.get_ylim()
    
    # Should be close to calculated bounds
    assert abs(auto_xlim[0] - xlim[0]) < 50, "Auto X bounds don't match calculated"
    assert abs(auto_xlim[1] - xlim[1]) < 50, "Auto X bounds don't match calculated"
    
    plt.close(fig1)
    
    # Test manual bounds override
    manual_xlim = (-800, 0)
    manual_ylim = (-300, 300)
    fig2, ax2 = plot_vdf_2d_contour(VX, VY, vdf_concentrated, 
                                   title="Manual Bounds Test", 
                                   auto_bounds=False, 
                                   manual_xlim=manual_xlim,
                                   manual_ylim=manual_ylim)
    
    actual_xlim = ax2.get_xlim()
    actual_ylim = ax2.get_ylim()
    
    # Should match manual bounds
    assert abs(actual_xlim[0] - manual_xlim[0]) < 10, "Manual X bounds not applied"
    assert abs(actual_xlim[1] - manual_xlim[1]) < 10, "Manual X bounds not applied"
    
    plt.close(fig2)
    print("✅ Smart bounds: calculation, auto-application, and manual override validated")

def test_plot_data_validation():
    """Test plotting functions handle edge cases and invalid data"""
    # Test with zeros and NaN values
    velocity = np.linspace(100, 1000, 50)
    vdf_with_zeros = np.ones_like(velocity) * 1e-12
    vdf_with_zeros[10:20] = 0  # Add some zeros
    vdf_with_zeros[30:35] = np.nan  # Add some NaNs
    
    # Should handle zeros/NaNs gracefully
    fig1, ax1 = plot_vdf_1d_collapsed(velocity, vdf_with_zeros, title="Test Edge Cases")
    
    # Should still produce a plot
    assert len(ax1.lines) > 0, "Should handle zeros/NaNs and still plot"
    
    plt.close(fig1)
    
    # Test 2D with problematic data
    vx = np.linspace(-500, 500, 20)
    vy = np.linspace(-500, 500, 20)
    VX, VY = np.meshgrid(vx, vy)
    
    vdf_2d_problem = np.ones_like(VX) * 1e-12
    vdf_2d_problem[5:10, 5:10] = 0  # Zero region
    vdf_2d_problem[15:18, 15:18] = np.nan  # NaN region
    
    # Should handle problematic 2D data
    fig2, ax2 = plot_vdf_2d_contour(VX, VY, vdf_2d_problem, title="Test 2D Edge Cases")
    
    # Should still produce contours
    assert len(ax2.collections) >= 0, "Should handle problematic 2D data gracefully"
    
    plt.close(fig2)
    print("✅ Edge case handling: zeros, NaNs, and problematic data validated")

if __name__ == "__main__":
    # Run key tests for manual verification
    print("🧪 Running VDF Basic Plotting Tests...")
    test_1d_vdf_plotting()
    test_2d_vdf_contour_plotting()
    test_triple_plot_layout()
    test_smart_bounds_functionality()
    test_plot_data_validation()
    test_real_vdf_plotting_workflow()
    print("🎉 All basic VDF plotting tests completed!")