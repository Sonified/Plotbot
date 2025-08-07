# tests/test_VDF_plotting_coordinates.py

"""
VDF Coordinate System Plotting Tests - Phase 3, Step 3.2

Tests VDF plotting in different coordinate systems:
- Instrument coordinates (SPAN-I native)
- Field-aligned coordinates (parallel/perpendicular to B)

Reference Source: files_from_Jaye/PSP_SPAN-I_VDF_Plot_Tutorial_pypedasdownload.ipynb
- Cells 50-55: Instrument coordinate plotting
- Cells 56-60: Field-aligned coordinate plotting  
- Cell 189: Consolidated coordinate transformation plotting
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
from test_VDF_plotting_basic import plot_vdf_2d_contour

# Add test utilities if available
from tests.utils.test_helpers import system_check, phase

def plot_instrument_coordinates(vx, vz, vdf, title="Instrument Coordinates", ax=None):
    """
    Plot VDF in SPAN-I instrument coordinates (Jaye's approach).
    
    Args:
        vx: 2D array of x-velocities in instrument frame (km/s)
        vz: 2D array of z-velocities in instrument frame (km/s)  
        vdf: 2D array of VDF values
        title: Plot title
        ax: Existing matplotlib axis (optional)
    
    Returns:
        fig, ax: Matplotlib figure and axis objects
    """
    fig, ax = plot_vdf_2d_contour(vx, vz, vdf, title=title, ax=ax)
    
    # Add instrument-specific annotations
    ax.set_xlabel('Vx (km/s) - Instrument Frame', fontsize=12)
    ax.set_ylabel('Vz (km/s) - Instrument Frame', fontsize=12)
    
    # Add reference lines for typical solar wind directions
    ax.axhline(0, color='white', alpha=0.7, linestyle='-', linewidth=1)
    ax.axvline(0, color='white', alpha=0.7, linestyle='-', linewidth=1)
    
    return fig, ax

def plot_field_aligned_coordinates(v_par, v_perp, vdf, title="Field-Aligned Coordinates", ax=None):
    """
    Plot VDF in field-aligned coordinates (Jaye's approach).
    
    Args:
        v_par: 2D array of parallel velocities (km/s)
        v_perp: 2D array of perpendicular velocities (km/s)
        vdf: 2D array of VDF values
        title: Plot title
        ax: Existing matplotlib axis (optional)
    
    Returns:
        fig, ax: Matplotlib figure and axis objects
    """
    fig, ax = plot_vdf_2d_contour(v_par, v_perp, vdf, title=title, ax=ax)
    
    # Add field-aligned specific annotations
    ax.set_xlabel('V|| (km/s) - Parallel to B', fontsize=12)
    ax.set_ylabel('V_perp (km/s) - Perpendicular to B', fontsize=12)
    
    # Add reference lines for magnetic field direction
    ax.axhline(0, color='white', alpha=0.7, linestyle='-', linewidth=1, label='B direction')
    ax.axvline(0, color='white', alpha=0.7, linestyle='-', linewidth=1)
    
    return fig, ax

def create_coordinate_comparison_plot(vdf_data_dict, magnetic_field):
    """
    Create side-by-side comparison of instrument vs field-aligned coordinates.
    
    Args:
        vdf_data_dict: Dictionary with VDF data (from processing pipeline)
        magnetic_field: [Bx, By, Bz] magnetic field vector in instrument frame
    
    Returns:
        fig: Matplotlib figure with comparison plots
    """
    fig = plt.figure(figsize=(16, 6))
    
    # Extract data
    vdf = vdf_data_dict['vdf']
    vx = vdf_data_dict['vx']
    vy = vdf_data_dict['vy']
    vz = vdf_data_dict['vz']
    epoch = vdf_data_dict['epoch']
    
    # Take a 2D slice for plotting (middle theta bin)
    theta_middle = 4
    vdf_2d = vdf[:, :, theta_middle]
    vx_2d = vx[:, :, theta_middle]
    vy_2d = vy[:, :, theta_middle]
    vz_2d = vz[:, :, theta_middle]
    
    # Plot 1: Instrument coordinates (Vx-Vz plane)
    ax1 = plt.subplot(1, 2, 1)
    plot_instrument_coordinates(vx_2d, vz_2d, vdf_2d, 
                               title="Instrument Coordinates\n(SPAN-I Frame)", ax=ax1)
    
    # Plot 2: Field-aligned coordinates
    ax2 = plt.subplot(1, 2, 2)
    
    # Transform velocities to field-aligned coordinates
    Bx, By, Bz = magnetic_field
    (Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz) = field_aligned_coordinates(Bx, By, Bz)
    
    # Transform each velocity component
    v_parallel = np.zeros_like(vx_2d)
    v_perp1 = np.zeros_like(vx_2d)
    v_perp2 = np.zeros_like(vx_2d)
    
    # Transform the 2D velocity arrays
    for i in range(vx_2d.shape[0]):
        for j in range(vx_2d.shape[1]):
            (v_par, v_p1, v_p2) = rotate_vector_into_field_aligned(
                vx_2d[i,j], vy_2d[i,j], vz_2d[i,j], 
                Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz)
            v_parallel[i,j] = v_par
            v_perp1[i,j] = v_p1
            v_perp2[i,j] = v_p2
    
    # Plot in field-aligned coordinates (parallel vs perp1)
    plot_field_aligned_coordinates(v_parallel, v_perp1, vdf_2d,
                                 title="Field-Aligned Coordinates\n(B-aligned Frame)", ax=ax2)
    
    # Add overall title
    fig.suptitle(f'VDF Coordinate Comparison - {epoch.strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'B = [{Bx:.1f}, {By:.1f}, {Bz:.1f}] nT', fontsize=14, y=0.95)
    
    plt.tight_layout()
    return fig

def test_instrument_coordinate_plotting():
    """Test VDF plotting in instrument coordinates"""
    # Create mock instrument coordinate data
    vx = np.linspace(-1000, 1000, 30)
    vz = np.linspace(-800, 800, 30)
    VX, VZ = np.meshgrid(vx, vz)
    
    # Create realistic VDF with solar wind structure
    # Peak around +400 km/s in vx (typical solar wind)
    V_mag = np.sqrt((VX-400)**2 + VZ**2)
    vdf_inst = 1e-12 * np.exp(-(V_mag/200)**2) * (1 + 0.3*np.random.random(VX.shape))
    
    # Test plotting
    fig, ax = plot_instrument_coordinates(VX, VZ, vdf_inst, title="Test Instrument VDF")
    
    # Validate plot properties
    assert 'Instrument Frame' in ax.get_xlabel(), "X-label should mention instrument frame"
    assert 'Instrument Frame' in ax.get_ylabel(), "Y-label should mention instrument frame"
    assert len(ax.collections) > 0, "Should have contour collections"
    
    # Check for reference lines (coordinate axes)
    h_lines = [line for line in ax.lines if line.get_xdata()[0] == line.get_xdata()[1]]  # Vertical lines
    v_lines = [line for line in ax.lines if line.get_ydata()[0] == line.get_ydata()[1]]  # Horizontal lines
    assert len(h_lines) > 0 or len(v_lines) > 0, "Should have reference coordinate lines"
    
    plt.close(fig)
    print("✅ Instrument coordinate plotting: axes, labels, and reference lines validated")

def test_field_aligned_coordinate_plotting():
    """Test VDF plotting in field-aligned coordinates"""
    # Create mock field-aligned coordinate data
    v_par = np.linspace(-800, 1200, 30)  # Parallel to B (solar wind direction)
    v_perp = np.linspace(-600, 600, 30)   # Perpendicular to B
    V_PAR, V_PERP = np.meshgrid(v_par, v_perp)
    
    # Create realistic VDF with field-aligned structure
    # Peak around +400 km/s parallel, narrow in perpendicular
    vdf_fac = 1e-12 * np.exp(-((V_PAR-400)/200)**2 - (V_PERP/150)**2) * (1 + 0.2*np.random.random(V_PAR.shape))
    
    # Test plotting
    fig, ax = plot_field_aligned_coordinates(V_PAR, V_PERP, vdf_fac, title="Test Field-Aligned VDF")
    
    # Validate plot properties
    assert 'Parallel to B' in ax.get_xlabel(), "X-label should mention parallel to B"
    assert 'Perpendicular to B' in ax.get_ylabel(), "Y-label should mention perpendicular to B"
    assert len(ax.collections) > 0, "Should have contour collections"
    
    # Check for magnetic field reference lines
    ref_lines = ax.lines
    assert len(ref_lines) >= 2, "Should have reference lines for B direction"
    
    plt.close(fig)
    print("✅ Field-aligned coordinate plotting: axes, labels, and B-field references validated")

def test_coordinate_transformation_accuracy():
    """Test that coordinate transformations preserve VDF structure"""
    # Create test data with known magnetic field
    Bx, By, Bz = 5.0, 3.0, 4.0  # nT
    B_mag = np.sqrt(Bx**2 + By**2 + Bz**2)
    
    # Create velocity grid in instrument coordinates
    vx = np.linspace(-1000, 1000, 20)
    vz = np.linspace(-800, 800, 20)
    VX, VZ = np.meshgrid(vx, vz)
    VY = np.zeros_like(VX)  # Simplify to vx-vz plane
    
    # Create VDF with structure along magnetic field direction
    # Field direction unit vector
    bx_hat, by_hat, bz_hat = Bx/B_mag, By/B_mag, Bz/B_mag
    
    # Velocity component along B field
    v_along_B = VX*bx_hat + VY*by_hat + VZ*bz_hat
    v_perp_B = np.sqrt((VX - v_along_B*bx_hat)**2 + (VZ - v_along_B*bz_hat)**2)
    
    # VDF peaked along magnetic field direction
    vdf_original = 1e-12 * np.exp(-((v_along_B-400)/200)**2 - (v_perp_B/100)**2)
    
    # Transform to field-aligned coordinates
    (Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz) = field_aligned_coordinates(Bx, By, Bz)
    
    v_parallel = VX*Nx + VY*Ny + VZ*Nz
    v_perp1 = VX*Px + VY*Py + VZ*Pz
    
    # In field-aligned coordinates, the peak should be along v_parallel axis
    # Find the peak location
    peak_idx = np.unravel_index(np.argmax(vdf_original), vdf_original.shape)
    peak_v_par = v_parallel[peak_idx]
    peak_v_perp1 = v_perp1[peak_idx]
    
    # Peak should be predominantly parallel
    assert abs(peak_v_par) > abs(peak_v_perp1), "Peak should be primarily in parallel direction"
    assert peak_v_par > 200, "Peak should be in positive parallel direction (solar wind)"
    
    print(f"✅ Coordinate transformation: peak at v_par={peak_v_par:.0f}, v_perp={peak_v_perp1:.0f} km/s")

def test_coordinate_comparison_workflow():
    """Test complete coordinate comparison workflow"""
    # Get real VDF data from processing pipeline
    print("📊 Processing real VDF data for coordinate comparison...")
    processed_data = test_complete_processing_pipeline()
    
    # Use realistic PSP magnetic field values
    magnetic_field = [-8.5, 2.3, -4.1]  # nT, typical solar wind
    
    # Test coordinate comparison plot
    fig = create_coordinate_comparison_plot(processed_data, magnetic_field)
    
    # Validate figure structure
    assert len(fig.axes) >= 2, "Should have at least 2 subplots for comparison"
    assert fig.get_figwidth() > 14, "Should be wide figure for side-by-side comparison"
    
    # Check that main subplots have content (skip colorbar axes)
    main_axes = [ax for ax in fig.axes if not hasattr(ax, 'get_label') or ax.get_label() != '<colorbar>']
    assert len(main_axes) >= 2, f"Should have at least 2 main plot axes, got {len(main_axes)}"
    
    for i, ax in enumerate(main_axes[:2]):  # Check first 2 main axes
        assert len(ax.collections) > 0, f"Main subplot {i+1} should have contour data"
        title = ax.get_title()
        if i == 0:  # Instrument coordinates
            assert 'Instrument' in title, f"First plot should be instrument coordinates, got: '{title}'"
        else:  # Field-aligned coordinates  
            assert 'Field-Aligned' in title, f"Second plot should be field-aligned coordinates, got: '{title}'"
    
    plt.close(fig)
    print("✅ Coordinate comparison workflow: real data processing and dual plotting validated")

def test_realistic_coordinate_scenarios():
    """Test coordinate plotting with realistic PSP scenarios"""
    # Test different magnetic field orientations
    test_scenarios = [
        {"name": "Radial field", "B": [-25.0, 1.0, 0.5], "desc": "Strong radial magnetic field"},
        {"name": "Parker spiral", "B": [-8.0, 5.0, -2.0], "desc": "Typical Parker spiral field"},
        {"name": "Tangential field", "B": [0.5, 15.0, 8.0], "desc": "Primarily tangential field"},
    ]
    
    # Create mock VDF data structure matching real pipeline output
    n_phi, n_energy, n_theta = 8, 32, 8
    vx = np.random.uniform(-1000, 1000, (n_phi, n_energy, n_theta))
    vy = np.random.uniform(-1000, 1000, (n_phi, n_energy, n_theta))
    vz = np.random.uniform(-500, 500, (n_phi, n_energy, n_theta))
    vel = np.sqrt(vx**2 + vy**2 + vz**2)
    vdf = 1e-12 * np.exp(-(vel/400)**2) * (1 + 0.3*np.random.random(vel.shape))
    
    test_data = {
        'vdf': vdf, 'vx': vx, 'vy': vy, 'vz': vz, 'vel': vel,
        'epoch': datetime.datetime(2020, 1, 29, 18, 10, 6)
    }
    
    for scenario in test_scenarios:
        print(f"🔍 Testing {scenario['name']}: {scenario['desc']}")
        
        # Test coordinate comparison for this scenario
        fig = create_coordinate_comparison_plot(test_data, scenario['B'])
        
        # Validate that both coordinate systems work
        assert len(fig.axes) >= 2, f"Should have comparison plots for {scenario['name']}"
        assert fig._suptitle is not None, f"Should have title with B field info for {scenario['name']}"
        
        # Check that magnetic field values appear in title
        title_text = fig._suptitle.get_text()
        for b_val in scenario['B']:
            assert f"{b_val:.1f}" in title_text, f"B field component {b_val} should appear in title"
        
        plt.close(fig)
        print(f"✅ {scenario['name']}: coordinate transformation and plotting successful")

def test_coordinate_labels_and_units():
    """Test that coordinate system labels and units are correct"""
    # Create simple test data
    coords = np.linspace(-500, 500, 20)
    X, Y = np.meshgrid(coords, coords)
    test_vdf = np.exp(-(X**2 + Y**2)/100000)
    
    # Test instrument coordinates
    fig1, ax1 = plot_instrument_coordinates(X, Y, test_vdf)
    xlabel1 = ax1.get_xlabel()
    ylabel1 = ax1.get_ylabel()
    
    assert 'km/s' in xlabel1 and 'km/s' in ylabel1, "Should have velocity units"
    assert 'Instrument' in xlabel1 and 'Instrument' in ylabel1, "Should specify instrument frame"
    
    plt.close(fig1)
    
    # Test field-aligned coordinates  
    fig2, ax2 = plot_field_aligned_coordinates(X, Y, test_vdf)
    xlabel2 = ax2.get_xlabel()
    ylabel2 = ax2.get_ylabel()
    
    assert 'km/s' in xlabel2 and 'km/s' in ylabel2, "Should have velocity units"
    assert 'Parallel' in xlabel2, "X-axis should indicate parallel direction"
    assert 'Perpendicular' in ylabel2, "Y-axis should indicate perpendicular direction"
    
    plt.close(fig2)
    print("✅ Coordinate labels and units: proper notation and physics terminology validated")

if __name__ == "__main__":
    # Run key tests for manual verification
    print("🧪 Running VDF Coordinate System Plotting Tests...")
    test_instrument_coordinate_plotting()
    test_field_aligned_coordinate_plotting()
    test_coordinate_transformation_accuracy()
    test_coordinate_labels_and_units()
    test_realistic_coordinate_scenarios()
    test_coordinate_comparison_workflow()
    print("🎉 All coordinate system plotting tests completed!")