#!/usr/bin/env python3
"""
Comprehensive Data Cubby Performance Test with Timer Integration
Captures all sub-process timing and organizes by duration (most to least)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from plotbot import *
from speed_test import timing_tracker
import time
import io
import contextlib
import re

class TimingCapture:
    """Captures and organizes all timer output from plotbot operations"""
    
    def __init__(self):
        self.captured_timings = []
        self.current_test = None
        
    def capture_plotbot_call(self, test_name, call_func, *args, **kwargs):
        """Capture all timing output from a plotbot call"""
        self.current_test = test_name
        
        # Capture stdout to get all the timer outputs
        captured_output = io.StringIO()
        
        start_time = time.time()
        with contextlib.redirect_stdout(captured_output):
            result = call_func(*args, **kwargs)
        end_time = time.time()
        
        # Parse the captured output for timing information
        output_lines = captured_output.getvalue().split('\n')
        timings = self._parse_timing_output(output_lines)
        
        # Add total time
        total_time = (end_time - start_time) * 1000
        timings.append({"process": "TOTAL_PLOTBOT_CALL", "time_ms": total_time})
        
        # Store results
        self.captured_timings.append({
            "test_name": test_name,
            "total_time_ms": total_time,
            "timings": timings
        })
        
        return result
    
    def _parse_timing_output(self, lines):
        """Parse timer decorator outputs from captured lines"""
        timings = []
        
        for line in lines:
            # Look for timer decorator patterns like "⏱️ [TIMER_NAME] operation: 123.45ms"
            timer_match = re.search(r'⏱️ \[([^\]]+)\] ([^:]+): ([\d.]+)ms', line)
            if timer_match:
                timer_name = timer_match.group(1)
                operation = timer_match.group(2)
                time_ms = float(timer_match.group(3))
                
                timings.append({
                    "process": f"{timer_name}_{operation}",
                    "time_ms": time_ms
                })
        
        return timings
    
    def get_timing_summary(self, test_name):
        """Get organized timing summary for a test"""
        test_data = None
        for test in self.captured_timings:
            if test["test_name"] == test_name:
                test_data = test
                break
        
        if not test_data:
            return None
        
        # Sort timings by duration (most to least)
        sorted_timings = sorted(test_data["timings"], key=lambda x: x["time_ms"], reverse=True)
        
        return {
            "test_name": test_name,
            "total_time_ms": test_data["total_time_ms"],
            "sorted_timings": sorted_timings
        }
    
    def compare_tests(self, test1_name, test2_name):
        """Compare two test runs"""
        test1 = self.get_timing_summary(test1_name)
        test2 = self.get_timing_summary(test2_name)
        
        if not test1 or not test2:
            return None
        
        speedup = test1["total_time_ms"] / test2["total_time_ms"] if test2["total_time_ms"] > 0 else 0
        
        return {
            "test1": test1,
            "test2": test2,
            "speedup": speedup
        }

def test_comprehensive_timing_analysis():
    """Test with comprehensive timing analysis and organization"""
    
    print("=" * 100)
    print("COMPREHENSIVE TIMING ANALYSIS - ORGANIZED BY DURATION")
    print("=" * 100)
    
    # Test parameters
    trange = ['2021-01-01/00:00:00', '2021-01-01/01:00:00']
    
    # Create timing capture
    timing_capture = TimingCapture()
    
    # Test 1: PSP Orbit - First Run
    print("\n" + "🚀" * 60)
    print("TEST 1: PSP ORBIT DATA - FIRST RUN")
    print("🚀" * 60)
    
    timing_capture.capture_plotbot_call("PSP_Orbit_First", plotbot, trange, psp_orbit.r_sun, 1)
    
    # Get data points
    data_points = len(psp_orbit.datetime_array) if hasattr(psp_orbit, 'datetime_array') and psp_orbit.datetime_array is not None else 0
    print(f"📊 Data Points: {data_points}")
    
    # Test 2: PSP Orbit - Second Run
    print("\n" + "🚀" * 60)
    print("TEST 2: PSP ORBIT DATA - SECOND RUN (CACHED)")
    print("🚀" * 60)
    
    timing_capture.capture_plotbot_call("PSP_Orbit_Second", plotbot, trange, psp_orbit.r_sun, 1)
    
    # Test 3: Magnetic Field - First Run
    print("\n" + "🧲" * 60)
    print("TEST 3: MAGNETIC FIELD DATA - FIRST RUN")
    print("🧲" * 60)
    
    timing_capture.capture_plotbot_call("Mag_Field_First", plotbot, trange, mag_rtn_4sa.br, 1)
    
    # Get data points
    data_points = len(mag_rtn_4sa.datetime_array) if hasattr(mag_rtn_4sa, 'datetime_array') and mag_rtn_4sa.datetime_array is not None else 0
    print(f"📊 Data Points: {data_points}")
    
    # Test 4: Magnetic Field - Second Run
    print("\n" + "🧲" * 60)
    print("TEST 4: MAGNETIC FIELD DATA - SECOND RUN (CACHED)")
    print("🧲" * 60)
    
    timing_capture.capture_plotbot_call("Mag_Field_Second", plotbot, trange, mag_rtn_4sa.br, 1)
    
    # DETAILED ANALYSIS
    print("\n" + "=" * 100)
    print("DETAILED TIMING ANALYSIS - PROCESSES SORTED BY DURATION")
    print("=" * 100)
    
    test_names = ["PSP_Orbit_First", "PSP_Orbit_Second", "Mag_Field_First", "Mag_Field_Second"]
    
    for test_name in test_names:
        summary = timing_capture.get_timing_summary(test_name)
        if summary:
            print(f"\n{'='*20} {test_name} {'='*20}")
            print(f"🕐 Total Time: {summary['total_time_ms']:.2f}ms")
            print(f"📊 Processes (Most to Least Time):")
            
            for i, timing in enumerate(summary['sorted_timings'][:10], 1):  # Show top 10
                process_name = timing['process'].replace('_', ' ').title()
                print(f"   {i:2d}. {process_name:<40} {timing['time_ms']:>8.2f}ms")
    
    # CACHING ANALYSIS
    print("\n" + "=" * 100)
    print("CACHING PERFORMANCE ANALYSIS")
    print("=" * 100)
    
    # Compare PSP Orbit runs
    orbit_comparison = timing_capture.compare_tests("PSP_Orbit_First", "PSP_Orbit_Second")
    if orbit_comparison:
        print(f"\n🚀 PSP ORBIT CACHING ANALYSIS:")
        print(f"   First Run:  {orbit_comparison['test1']['total_time_ms']:.2f}ms")
        print(f"   Second Run: {orbit_comparison['test2']['total_time_ms']:.2f}ms")
        print(f"   Speedup:    {orbit_comparison['speedup']:.2f}x")
        
        if orbit_comparison['speedup'] > 2:
            print(f"   Status:     ✅ CACHING WORKING")
        else:
            print(f"   Status:     ❌ POOR CACHING")
    
    # Compare Magnetic Field runs
    mag_comparison = timing_capture.compare_tests("Mag_Field_First", "Mag_Field_Second")
    if mag_comparison:
        print(f"\n🧲 MAGNETIC FIELD CACHING ANALYSIS:")
        print(f"   First Run:  {mag_comparison['test1']['total_time_ms']:.2f}ms")
        print(f"   Second Run: {mag_comparison['test2']['total_time_ms']:.2f}ms")
        print(f"   Speedup:    {mag_comparison['speedup']:.2f}x")
        
        if mag_comparison['speedup'] > 2:
            print(f"   Status:     ✅ CACHING WORKING")
        else:
            print(f"   Status:     ❌ POOR CACHING")
    
    # FINAL SUMMARY
    print(f"\n" + "=" * 100)
    print("FINAL SUMMARY")
    print("=" * 100)
    
    orbit_working = orbit_comparison and orbit_comparison['speedup'] > 2
    mag_working = mag_comparison and mag_comparison['speedup'] > 2
    
    print(f"PSP Orbit Data Cubby:     {'✅ WORKING' if orbit_working else '❌ NEEDS IMPROVEMENT'}")
    print(f"Magnetic Field Data Cubby: {'✅ WORKING' if mag_working else '❌ NEEDS IMPROVEMENT'}")
    
    if orbit_comparison:
        print(f"\nPSP Orbit Performance:")
        print(f"  • First run took {orbit_comparison['test1']['total_time_ms']:.0f}ms")
        print(f"  • Second run took {orbit_comparison['test2']['total_time_ms']:.0f}ms")
        print(f"  • Caching provided {orbit_comparison['speedup']:.1f}x speedup")
    
    if mag_comparison:
        print(f"\nMagnetic Field Performance:")
        print(f"  • First run took {mag_comparison['test1']['total_time_ms']:.0f}ms")
        print(f"  • Second run took {mag_comparison['test2']['total_time_ms']:.0f}ms")
        print(f"  • Caching provided {mag_comparison['speedup']:.1f}x speedup")

if __name__ == "__main__":
    test_comprehensive_timing_analysis() 