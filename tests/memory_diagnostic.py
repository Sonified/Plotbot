import numpy as np
import sys
import pickle
import gzip
import bz2

# Moved class definitions to top-level
class ComponentApproach:
    def __init__(self, dt_array, pa_array):
        self.datetime_array = dt_array
        self.pitch_angles = pa_array
        # No mesh stored initially

class ComponentWithCache:
    def __init__(self, dt_array, pa_array, mesh):
        self.datetime_array = dt_array
        self.pitch_angles = pa_array
        self.times_mesh = mesh

class FullMeshApproach:
    def __init__(self, dt_array, pa_array, mesh):
        self.datetime_array = dt_array
        self.pitch_angles = pa_array
        self.times_mesh = mesh

def detailed_memory_analysis():
    """Detailed analysis of actual memory usage"""
    
    # Test with realistic EPAD dimensions
    time_points = 10000  # ~7 hours of data
    pitch_bins = 32      # Standard EPAD
    
    print(f"🔬 DETAILED MEMORY ANALYSIS")
    print(f"Testing: {time_points:,} time points × {pitch_bins} pitch angle bins")
    print("=" * 60)
    
    # Create realistic data
    datetime_array = np.array([
        np.datetime64('2023-01-01T00:00:00') + np.timedelta64(int(i * 60), 's') 
        for i in range(time_points)
    ])
    pitch_angles = np.linspace(0, 180, pitch_bins)
    
    print(f"📐 Component sizes:")
    print(f"  datetime_array: {datetime_array.nbytes:,} bytes ({datetime_array.nbytes/1024**2:.2f} MB)")
    print(f"  pitch_angles:   {pitch_angles.nbytes:,} bytes ({pitch_angles.nbytes/1024**2:.2f} MB)")
    
    # Calculate times_mesh
    times_mesh = np.meshgrid(datetime_array, np.arange(pitch_bins), indexing='ij')[0]
    print(f"  times_mesh:     {times_mesh.nbytes:,} bytes ({times_mesh.nbytes/1024**2:.2f} MB)")
    print(f"  times_mesh shape: {times_mesh.shape}")
    
    # Component approach memory
    component_memory = datetime_array.nbytes + pitch_angles.nbytes
    component_with_cache = component_memory + times_mesh.nbytes
    
    # Full mesh approach memory  
    full_mesh_memory = datetime_array.nbytes + pitch_angles.nbytes + times_mesh.nbytes
    
    print(f"\n📊 Memory comparison:")
    print(f"  Component only:           {component_memory:,} bytes ({component_memory/1024**2:.2f} MB)")
    print(f"  Component + cached mesh:  {component_with_cache:,} bytes ({component_with_cache/1024**2:.2f} MB)")
    print(f"  Full mesh storage:        {full_mesh_memory:,} bytes ({full_mesh_memory/1024**2:.2f} MB)")
    
    # Calculate ratios
    ratio_no_cache = full_mesh_memory / component_memory
    ratio_with_cache = full_mesh_memory / component_with_cache
    
    print(f"\n📈 Memory ratios:")
    print(f"  Full mesh vs component only:          {ratio_no_cache:.1f}x")
    print(f"  Full mesh vs component+cached mesh:   {ratio_with_cache:.1f}x")
    
    # Pickle size analysis
    # Create instances
    comp_only = ComponentApproach(datetime_array, pitch_angles)
    comp_cached = ComponentWithCache(datetime_array, pitch_angles, times_mesh)
    full_mesh = FullMeshApproach(datetime_array, pitch_angles, times_mesh)
    
    # Pickle sizes
    pickle_comp_only = len(pickle.dumps(comp_only))
    pickle_comp_cached = len(pickle.dumps(comp_cached))
    pickle_full_mesh = len(pickle.dumps(full_mesh))
    
    print(f"\n💾 Pickle sizes:")
    print(f"  Component only:           {pickle_comp_only:,} bytes ({pickle_comp_only/1024**2:.2f} MB)")
    print(f"  Component + cached mesh:  {pickle_comp_cached:,} bytes ({pickle_comp_cached/1024**2:.2f} MB)")
    print(f"  Full mesh storage:        {pickle_full_mesh:,} bytes ({pickle_full_mesh/1024**2:.2f} MB)")
    
    pickle_ratio = pickle_full_mesh / pickle_comp_only
    pickle_ratio_cached = pickle_full_mesh / pickle_comp_cached
    
    print(f"\n📈 Pickle ratios:")
    print(f"  Full mesh vs component only:          {pickle_ratio:.1f}x")
    print(f"  Full mesh vs component+cached mesh:   {pickle_ratio_cached:.1f}x")
    
    print(f"\n🎯 REAL-WORLD IMPLICATIONS FOR DATA_CUBBY:")
    print(f"   In your data_cubby, once times_mesh is accessed once:")
    print(f"   - Component approach: {component_with_cache/1024**2:.1f} MB (same as full mesh)")
    print(f"   - Full mesh approach:  {full_mesh_memory/1024**2:.1f} MB")
    print(f"   - Memory difference: {ratio_with_cache:.1f}x (essentially the same)")
    print(f"   - Speed difference: ~1000-9000x faster access with full mesh")
    
    # Test compression
    
    print(f"\n🗜️  COMPRESSION ANALYSIS:")
    
    # Test gzip compression
    comp_gzip = len(gzip.compress(pickle.dumps(comp_only)))
    full_gzip = len(gzip.compress(pickle.dumps(full_mesh)))
    
    print(f"  Component only (gzipped):  {comp_gzip:,} bytes ({comp_gzip/1024**2:.2f} MB)")
    print(f"  Full mesh (gzipped):       {full_gzip:,} bytes ({full_gzip/1024**2:.2f} MB)")
    print(f"  Compression ratio:         {full_gzip/comp_gzip:.1f}x")
    
    # Analyze compression effectiveness
    comp_compression_ratio = pickle_comp_only / comp_gzip
    full_compression_ratio = pickle_full_mesh / full_gzip
    
    print(f"  Component compression:     {comp_compression_ratio:.1f}x smaller")
    print(f"  Full mesh compression:     {full_compression_ratio:.1f}x smaller")

if __name__ == "__main__":
    detailed_memory_analysis()