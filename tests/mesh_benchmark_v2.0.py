import numpy as np
import time
import pickle
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, Dict, List
import gc
import psutil
import os

@dataclass
class BenchmarkResults:
    """Store benchmark results for analysis"""
    reconstruction_times: List[float]
    direct_access_times: List[float]
    storage_sizes: Dict[str, int]
    memory_usage: Dict[str, float]

class ComponentStorageApproach:
    """Current approach: Store components, reconstruct mesh on demand"""
    
    def __init__(self, datetime_array: np.ndarray, pitch_angles: np.ndarray):
        self.datetime_array = datetime_array
        self.pitch_angles = pitch_angles
        self._times_mesh = None  # Cache for reconstruction
        
    def get_times_mesh(self) -> np.ndarray:
        """Reconstruct times_mesh on demand with caching (matches EPAD logic)"""
        if self._times_mesh is None:
            start_time = time.perf_counter()
            # This matches the EPAD mesh creation logic exactly
            self._times_mesh = np.meshgrid(
                self.datetime_array,
                np.arange(len(self.pitch_angles)),  # pitch angle bins
                indexing='ij'
            )[0]
            reconstruction_time = time.perf_counter() - start_time
            return self._times_mesh, reconstruction_time
        return self._times_mesh, 0.0
    
    def clear_cache(self):
        """Clear cached mesh to force reconstruction"""
        self._times_mesh = None
    
    def get_memory_usage(self) -> int:
        """Calculate memory usage in bytes"""
        size = self.datetime_array.nbytes + self.pitch_angles.nbytes
        if self._times_mesh is not None:
            size += self._times_mesh.nbytes
        return size

class FullMeshStorageApproach:
    """Alternative: Store complete times_mesh directly"""
    
    def __init__(self, datetime_array: np.ndarray, pitch_angles: np.ndarray):
        # Pre-compute and store the full times_mesh (matches EPAD logic)
        start_time = time.perf_counter()
        self.times_mesh = np.meshgrid(
            datetime_array,
            np.arange(len(pitch_angles)),  # pitch angle bins
            indexing='ij'
        )[0]
        self.creation_time = time.perf_counter() - start_time
        
        # Store components for reference (needed for other calculations)
        self.datetime_array = datetime_array
        self.pitch_angles = pitch_angles
    
    def get_times_mesh(self) -> Tuple[np.ndarray, float]:
        """Direct access to pre-computed mesh"""
        start_time = time.perf_counter()
        result = self.times_mesh
        access_time = time.perf_counter() - start_time
        return result, access_time
    
    def get_memory_usage(self) -> int:
        """Calculate memory usage in bytes"""
        return (self.datetime_array.nbytes + 
                self.pitch_angles.nbytes + 
                self.times_mesh.nbytes)

def create_realistic_data(time_points: int, pitch_angle_bins: int) -> Tuple[np.ndarray, np.ndarray]:
    """Create realistic electron PAD data dimensions"""
    # Typical PSP data: hours to days of data at various cadences
    datetime_array = np.array([
        np.datetime64('2023-01-01T00:00:00') + np.timedelta64(int(i * 60), 's') 
        for i in range(time_points)
    ])
    
    # EPAD pitch angle bins - typically 32 bins from 0° to 180°
    pitch_angles = np.linspace(0, 180, pitch_angle_bins)
    
    return datetime_array, pitch_angles

def benchmark_scenario(time_points: int, pitch_angle_bins: int, iterations: int = 100) -> BenchmarkResults:
    """Run comprehensive benchmark for a specific data size scenario"""
    
    print(f"\n🔬 Benchmarking: {time_points:,} time points × {pitch_angle_bins} pitch angle bins")
    print(f"   Mesh size: ~{(time_points * pitch_angle_bins * 8 / 1024**2):.1f} MB")
    print(f"   Total memory (with components): ~{(time_points * 16 + pitch_angle_bins * 8 + time_points * pitch_angle_bins * 8) / 1024**2:.1f} MB")
    
    # Create test data
    datetime_array, pitch_angles = create_realistic_data(time_points, pitch_angle_bins)
    
    # Initialize both approaches
    component_approach = ComponentStorageApproach(datetime_array, pitch_angles)
    full_mesh_approach = FullMeshStorageApproach(datetime_array, pitch_angles)
    
    reconstruction_times = []
    direct_access_times = []
    
    # Benchmark reconstruction approach
    print("   Testing component + reconstruction approach...")
    for i in range(iterations):
        component_approach.clear_cache()  # Force reconstruction each time
        gc.collect()  # Ensure clean state
        
        _, recon_time = component_approach.get_times_mesh()
        reconstruction_times.append(recon_time)
    
    # Benchmark direct access approach  
    print("   Testing full mesh storage approach...")
    for i in range(iterations):
        gc.collect()  # Ensure clean state
        
        _, access_time = full_mesh_approach.get_times_mesh()
        direct_access_times.append(access_time)
    
    # Memory usage analysis
    comp_memory = component_approach.get_memory_usage()
    full_memory = full_mesh_approach.get_memory_usage()
    
    # Storage size analysis (simulate pickle)
    comp_pickle_size = len(pickle.dumps(component_approach))
    full_pickle_size = len(pickle.dumps(full_mesh_approach))
    
    return BenchmarkResults(
        reconstruction_times=reconstruction_times,
        direct_access_times=direct_access_times,
        storage_sizes={
            'component_memory': comp_memory,
            'full_mesh_memory': full_memory,
            'component_pickle': comp_pickle_size,
            'full_mesh_pickle': full_pickle_size
        },
        memory_usage={
            'component_mb': comp_memory / 1024**2,
            'full_mesh_mb': full_memory / 1024**2
        }
    )

def run_comprehensive_benchmark():
    """Run benchmarks across multiple realistic data scenarios"""
    
    # Realistic PSP EPAD data scenarios
    scenarios = [
        # (time_points, pitch_angle_bins, description)
        (1000, 32, "Short interval (~17 min), 32 PA bins"),
        (5000, 32, "Medium interval (~83 min), 32 PA bins"), 
        (20000, 32, "Long interval (~5.5 hours), 32 PA bins"),
        (50000, 32, "Very long interval (~14 hours), 32 PA bins"),
        (100000, 32, "Extended interval (~28 hours), 32 PA bins"),
        (20000, 64, "High-res PA bins (~5.5 hours), 64 PA bins"),
    ]
    
    results = {}
    
    print("🚀 Starting Comprehensive Mesh Storage Benchmark")
    print("   Testing both SPEED and STORAGE SIZE implications")
    print("   Metrics: Access time, Memory usage, Pickle size, Speedup factor")
    print("=" * 60)
    
    for time_points, pitch_bins, description in scenarios:
        scenario_key = f"{time_points}x{pitch_bins}"
        results[scenario_key] = {
            'description': description,
            'data': benchmark_scenario(time_points, pitch_bins, iterations=50)
        }
    
    return results

def analyze_results(results: Dict) -> None:
    """Analyze and visualize benchmark results"""
    
    print("\n📊 PERFORMANCE ANALYSIS")
    print("=" * 60)
    print("📏 STORAGE COMPARISON:")
    print("   Component Approach: datetime_array + pitch_angles + (mesh cache)")
    print("   Full Mesh Approach: datetime_array + pitch_angles + times_mesh")
    print("   🎯 Key Trade-off: Storage size vs Access speed")
    print("")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    scenarios = []
    recon_means = []
    direct_means = []
    memory_ratios = []
    storage_ratios = []
    
    for scenario_key, scenario_data in results.items():
        desc = scenario_data['description']
        data = scenario_data['data']
        
        scenarios.append(scenario_key)
        
        # Performance analysis
        recon_mean = np.mean(data.reconstruction_times) * 1000  # Convert to ms
        direct_mean = np.mean(data.direct_access_times) * 1000
        
        recon_means.append(recon_mean)
        direct_means.append(direct_mean)
        
        # Memory analysis
        memory_ratio = data.storage_sizes['full_mesh_memory'] / data.storage_sizes['component_memory']
        storage_ratio = data.storage_sizes['full_mesh_pickle'] / data.storage_sizes['component_pickle']
        
        memory_ratios.append(memory_ratio)
        storage_ratios.append(storage_ratio)
        
        # Detailed output
        speedup = recon_mean / direct_mean if direct_mean > 0 else float('inf')
        
        print(f"\n{desc}:")
        print(f"  Reconstruction: {recon_mean:.3f} ms (±{np.std(data.reconstruction_times)*1000:.3f})")
        print(f"  Direct Access:  {direct_mean:.6f} ms (±{np.std(data.direct_access_times)*1000:.6f})")
        print(f"  Speedup:        {speedup:.0f}x faster")
        print(f"  Memory Ratio:   {memory_ratio:.1f}x larger (full mesh)")
        print(f"  Storage Ratio:  {storage_ratio:.1f}x larger (pickled)")
    
    # Create visualizations
    x_pos = np.arange(len(scenarios))
    
    # Performance comparison
    ax1.bar(x_pos - 0.2, recon_means, 0.4, label='Component + Reconstruction', alpha=0.8, color='coral')
    ax1.bar(x_pos + 0.2, direct_means, 0.4, label='Full Mesh Storage', alpha=0.8, color='lightblue')
    ax1.set_ylabel('Time (ms)')
    ax1.set_title('Access Time Comparison')
    ax1.set_yscale('log')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(scenarios, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Speedup visualization
    speedups = [r/d if d > 0 else 0 for r, d in zip(recon_means, direct_means)]
    ax2.bar(x_pos, speedups, color='green', alpha=0.7)
    ax2.set_ylabel('Speedup Factor')
    ax2.set_title('Full Mesh Speedup vs Reconstruction')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(scenarios, rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # Memory usage comparison
    ax3.bar(x_pos, memory_ratios, color='red', alpha=0.7)
    ax3.set_ylabel('Memory Ratio (Full/Component)')
    ax3.set_title('Memory Usage Overhead')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(scenarios, rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # Storage size comparison
    ax4.bar(x_pos, storage_ratios, color='purple', alpha=0.7)
    ax4.set_ylabel('Storage Ratio (Full/Component)')
    ax4.set_title('Pickled Storage Overhead')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(scenarios, rotation=45)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("mesh_benchmark_results.png")  # Explicitly save the figure
    plt.show()
    
    # Summary recommendations
    print(f"\n🎯 RECOMMENDATIONS")
    print("=" * 60)
    
    avg_speedup = np.mean(speedups)
    avg_memory_overhead = np.mean(memory_ratios)
    
    print(f"Average speedup with full mesh storage: {avg_speedup:.0f}x")
    print(f"Average memory overhead: {avg_memory_overhead:.1f}x")
    
    if avg_speedup > 100 and avg_memory_overhead < 3:
        print("✅ RECOMMENDATION: Full mesh storage")
        print("   - Dramatic performance improvement")
        print("   - Acceptable memory overhead")
        print("   - Best for production NASA data system")
    elif avg_speedup > 10 and avg_memory_overhead < 2:
        print("✅ RECOMMENDATION: Full mesh storage")
        print("   - Significant performance improvement")
        print("   - Low memory overhead")
    else:
        print("✅ RECOMMENDATION: Component + reconstruction")
        print("   - Memory efficient")
        print("   - Performance penalty may be acceptable")
        print("   - Consider caching strategy")

if __name__ == "__main__":
    print("🔬 EPAD MESH BENCHMARK - Testing Component vs Full Storage")
    print("=" * 60)
    print("📐 What we're testing:")
    print("   - times_mesh: 2D array of (time_points × pitch_angle_bins)")
    print("   - Typical EPAD: 32 pitch angle bins, various time lengths")
    print("   - After energy channel selection (index 8 or 12)")
    print("   - Both ACCESS SPEED and STORAGE SIZE implications")
    print("")
    
    # Run the comprehensive benchmark
    benchmark_results = run_comprehensive_benchmark()
    
    # Analyze and visualize results
    analyze_results(benchmark_results)
    
    print(f"\n💡 Additional Considerations for NASA Baseline:")
    print("   - Network I/O dominates vs memory/CPU in most cases")
    print("   - Consider hybrid approach: cache mesh for 'hot' data")
    print("   - File compression effectiveness varies by approach")
    print("   - Multi-user concurrent access patterns")
    print("   - GPU acceleration potential for mesh operations")