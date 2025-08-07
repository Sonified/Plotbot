# tests/test_VDF_coordinates.py

"""
VDF Field-Aligned Coordinates Tests - Phase 2, Step 2.2

Tests field-aligned coordinate transformations from Jaye's notebook Cell 37.
Implements and validates coordinate system generation and vector rotation.

Reference Source: files_from_Jaye/PSP_SPAN-I_VDF_Plot_Tutorial_pypedasdownload.ipynb Cell 37
- Function: fieldAlignedCoordinates(Bx, By, Bz)
- Function: rotateVectorIntoFieldAligned(Ax, Ay, Az, Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz)
"""

import numpy as np
import pytest
from datetime import datetime

# Add test utilities if available
from tests.utils.test_helpers import system_check, phase

def field_aligned_coordinates(Bx, By, Bz):
    """
    Generate field-aligned coordinate system from magnetic field.
    
    Exact implementation from Jaye's notebook Cell 37.
    
    Returns:
        (Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz): Field-aligned coordinate system
    """
    import numpy as np

    Bmag = np.sqrt(Bx**2 + By**2 + Bz**2)

    # Define field-aligned vector
    Nx = Bx/Bmag
    Ny = By/Bmag
    Nz = Bz/Bmag

    # Make up some unit vector
    if np.isscalar(Nx):
        Rx = 0
        Ry = 1.
        Rz = 0
    else:
        Rx = np.zeros(len(Nx))  # Fixed from Jaye's typo: Nx.len() -> len(Nx)
        Ry = np.ones(len(Nx))
        Rz = np.zeros(len(Nx))

    # Find some vector perpendicular to field NxR 
    TEMP_Px = ( Ny * Rz ) - ( Nz * Ry )  # P = NxR
    TEMP_Py = ( Nz * Rx ) - ( Nx * Rz )  # This is temporary in case we choose a vector R that is not unitary
    TEMP_Pz = ( Nx * Ry ) - ( Ny * Rx )

    Pmag = np.sqrt( TEMP_Px**2 + TEMP_Py**2 + TEMP_Pz**2 ) #Have to normalize, since previous definition does not imply unitarity, just orthogonality
  
    Px = TEMP_Px / Pmag # for R=(0,1,0), NxR = P ~= RTN_N
    Py = TEMP_Py / Pmag
    Pz = TEMP_Pz / Pmag

    Qx = ( Pz * Ny ) - ( Py * Nz )   # N x P
    Qy = ( Px * Nz ) - ( Pz * Nx )  
    Qz = ( Py * Nx ) - ( Px * Ny )  

    return(Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz)

def rotate_vector_into_field_aligned(Ax, Ay, Az, Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz):
    """
    Transform vector A into field-aligned coordinates.
    
    Exact implementation from Jaye's notebook Cell 37.
    """
    # For some Vector A in the SAME COORDINATE SYSTEM AS THE ORIGINAL B-FIELD VECTOR:

    An = (Ax * Nx) + (Ay * Ny) + (Az * Nz)  # A dot N = A_parallel
    Ap = (Ax * Px) + (Ay * Py) + (Az * Pz)  # A dot P = A_perp (~RTN_N (+/- depending on B), perpendicular to s/c y)
    Aq = (Ax * Qx) + (Ay * Qy) + (Az * Qz)  # 

    return(An, Ap, Aq)

def test_field_aligned_coordinate_generation():
    """Test field-aligned coordinate system generation"""
    # Test with simple magnetic field cases
    
    # Case 1: B field along x-axis
    Bx, By, Bz = 10.0, 0.0, 0.0
    (Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz) = field_aligned_coordinates(Bx, By, Bz)
    
    # Validate N vector (should be along x)
    assert np.allclose([Nx, Ny, Nz], [1, 0, 0]), "N should be along x-axis"
    
    # Validate orthogonality
    assert np.allclose(Nx*Px + Ny*Py + Nz*Pz, 0), "N and P should be orthogonal"
    assert np.allclose(Nx*Qx + Ny*Qy + Nz*Qz, 0), "N and Q should be orthogonal"
    assert np.allclose(Px*Qx + Py*Qy + Pz*Qz, 0), "P and Q should be orthogonal"
    
    # Validate unit vectors
    assert np.allclose(np.sqrt(Nx**2 + Ny**2 + Nz**2), 1), "N should be unit vector"
    assert np.allclose(np.sqrt(Px**2 + Py**2 + Pz**2), 1), "P should be unit vector"
    assert np.allclose(np.sqrt(Qx**2 + Qy**2 + Qz**2), 1), "Q should be unit vector"
    
    print(f"✅ Field-aligned coordinates for B=[{Bx}, {By}, {Bz}]:")
    print(f"   N=[{Nx:.3f}, {Ny:.3f}, {Nz:.3f}]")
    print(f"   P=[{Px:.3f}, {Py:.3f}, {Pz:.3f}]")
    print(f"   Q=[{Qx:.3f}, {Qy:.3f}, {Qz:.3f}]")

def test_vector_rotation_to_field_aligned():
    """Test vector rotation into field-aligned coordinates"""
    # Create known magnetic field and coordinate system
    Bx, By, Bz = 5.0, 3.0, 4.0  # |B| = 7.07
    (Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz) = field_aligned_coordinates(Bx, By, Bz)
    
    # Test rotation of B field itself (should give [|B|, 0, 0])
    Bmag = np.sqrt(Bx**2 + By**2 + Bz**2)
    (Bn, Bp, Bq) = rotate_vector_into_field_aligned(Bx, By, Bz, Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz)
    
    assert np.allclose(Bn, Bmag), f"B parallel should equal |B|: {Bn} vs {Bmag}"
    assert np.allclose(Bp, 0, atol=1e-10), f"B perp1 should be zero: {Bp}"
    assert np.allclose(Bq, 0, atol=1e-10), f"B perp2 should be zero: {Bq}"
    
    print(f"✅ Vector rotation: B=[{Bx}, {By}, {Bz}] → B_fac=[{Bn:.3f}, {Bp:.3e}, {Bq:.3e}]")
    print(f"   |B| = {Bmag:.3f}, B_parallel = {Bn:.3f}")

def test_round_trip_transformation():
    """Test that round-trip transformation preserves vector magnitudes"""
    # Create test vectors and magnetic field
    Bx, By, Bz = 2.0, 1.0, 3.0
    Ax, Ay, Az = 100.0, 200.0, 150.0
    
    original_magnitude = np.sqrt(Ax**2 + Ay**2 + Az**2)
    
    # Transform to field-aligned coordinates
    (Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz) = field_aligned_coordinates(Bx, By, Bz)
    (An, Ap, Aq) = rotate_vector_into_field_aligned(Ax, Ay, Az, Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz)
    
    # Check magnitude preservation
    fac_magnitude = np.sqrt(An**2 + Ap**2 + Aq**2)
    assert np.allclose(original_magnitude, fac_magnitude), "Vector magnitude should be preserved"
    
    print(f"✅ Round-trip test: |A|_original = {original_magnitude:.3f}, |A|_fac = {fac_magnitude:.3f}")

def test_array_input_handling():
    """Test field-aligned coordinates with array inputs"""
    # Test with arrays (multiple time points)
    n_times = 10
    Bx = np.random.uniform(-10, 10, n_times)
    By = np.random.uniform(-10, 10, n_times)
    Bz = np.random.uniform(-10, 10, n_times)
    
    # Should handle arrays without errors
    try:
        (Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz) = field_aligned_coordinates(Bx, By, Bz)
        
        # Validate output shapes
        assert Nx.shape == (n_times,), "N vector should have correct shape"
        assert Px.shape == (n_times,), "P vector should have correct shape" 
        assert Qx.shape == (n_times,), "Q vector should have correct shape"
        
        # Validate all are unit vectors
        N_mag = np.sqrt(Nx**2 + Ny**2 + Nz**2)
        assert np.allclose(N_mag, 1), "All N vectors should be unit vectors"
        
        print(f"✅ Array input test: {n_times} time points processed successfully")
        
    except Exception as e:
        pytest.fail(f"Array input handling failed: {e}")

def test_velocity_to_field_aligned_example():
    """Test velocity transformation to field-aligned coordinates (VDF application)"""
    # Simulate typical solar wind scenario
    # Magnetic field in RTN coordinates (typical PSP values)
    Bx, By, Bz = -5.2, 3.1, 1.8  # nT
    
    # Generate field-aligned coordinate system
    (Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz) = field_aligned_coordinates(Bx, By, Bz)
    
    # Test multiple velocity vectors (simulating VDF data)
    n_particles = 50
    vx = np.random.uniform(-1000, 1000, n_particles)  # km/s
    vy = np.random.uniform(-1000, 1000, n_particles)  # km/s  
    vz = np.random.uniform(-1000, 1000, n_particles)  # km/s
    
    # Transform to field-aligned coordinates
    v_parallel = (vx * Nx) + (vy * Ny) + (vz * Nz)
    v_perp1 = (vx * Px) + (vy * Py) + (vz * Pz)
    v_perp2 = (vx * Qx) + (vy * Qy) + (vz * Qz)
    
    # Validate magnitude preservation
    original_speeds = np.sqrt(vx**2 + vy**2 + vz**2)
    fac_speeds = np.sqrt(v_parallel**2 + v_perp1**2 + v_perp2**2)
    
    assert np.allclose(original_speeds, fac_speeds), "Speed magnitudes should be preserved"
    
    # Check that we have reasonable distributions
    assert np.std(v_parallel) > 0, "Should have spread in parallel velocities"
    assert np.std(v_perp1) > 0, "Should have spread in perp1 velocities"
    assert np.std(v_perp2) > 0, "Should have spread in perp2 velocities"
    
    print(f"✅ Velocity transformation test:")
    print(f"   v_parallel: mean={np.mean(v_parallel):.1f}, std={np.std(v_parallel):.1f} km/s")
    print(f"   v_perp1: mean={np.mean(v_perp1):.1f}, std={np.std(v_perp1):.1f} km/s")
    print(f"   v_perp2: mean={np.mean(v_perp2):.1f}, std={np.std(v_perp2):.1f} km/s")

def test_realistic_magnetic_field_values():
    """Test with realistic PSP magnetic field values"""
    # Test cases based on typical PSP magnetic field measurements
    test_cases = [
        {"name": "Typical solar wind", "B": [-8.5, 2.3, -4.1]},
        {"name": "Strong radial field", "B": [-25.0, 1.2, 0.8]},
        {"name": "Weak field", "B": [-1.2, 0.5, 0.3]},
        {"name": "Pure tangential", "B": [0.0, 5.0, 3.0]},
    ]
    
    for case in test_cases:
        Bx, By, Bz = case["B"]
        (Nx, Ny, Nz, Px, Py, Pz, Qx, Qy, Qz) = field_aligned_coordinates(Bx, By, Bz)
        
        # Validate coordinate system properties
        # Check orthogonality
        assert np.allclose(Nx*Px + Ny*Py + Nz*Pz, 0, atol=1e-10), f"N·P != 0 for {case['name']}"
        assert np.allclose(Nx*Qx + Ny*Qy + Nz*Qz, 0, atol=1e-10), f"N·Q != 0 for {case['name']}"
        assert np.allclose(Px*Qx + Py*Qy + Pz*Qz, 0, atol=1e-10), f"P·Q != 0 for {case['name']}"
        
        # Check unit vectors
        N_mag = np.sqrt(Nx**2 + Ny**2 + Nz**2)
        P_mag = np.sqrt(Px**2 + Py**2 + Pz**2)
        Q_mag = np.sqrt(Qx**2 + Qy**2 + Qz**2)
        
        assert np.allclose(N_mag, 1, atol=1e-10), f"|N| != 1 for {case['name']}"
        assert np.allclose(P_mag, 1, atol=1e-10), f"|P| != 1 for {case['name']}"
        assert np.allclose(Q_mag, 1, atol=1e-10), f"|Q| != 1 for {case['name']}"
        
        # Check right-handed coordinate system (N × P = Q)
        cross_x = Ny*Pz - Nz*Py
        cross_y = Nz*Px - Nx*Pz
        cross_z = Nx*Py - Ny*Px
        
        assert np.allclose([cross_x, cross_y, cross_z], [Qx, Qy, Qz], atol=1e-10), f"N×P != Q for {case['name']}"
        
        print(f"✅ {case['name']}: B=[{Bx:.1f}, {By:.1f}, {Bz:.1f}] → Valid FAC system")

if __name__ == "__main__":
    # Run key tests for manual verification
    print("🧪 Running VDF Field-Aligned Coordinates Tests...")
    test_field_aligned_coordinate_generation()
    test_vector_rotation_to_field_aligned()
    test_round_trip_transformation()
    test_array_input_handling()
    test_velocity_to_field_aligned_example()
    test_realistic_magnetic_field_values()
    print("🎉 All field-aligned coordinate tests completed!")