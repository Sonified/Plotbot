#!/usr/bin/env python3
"""
Orbit Performance Test Using TimingTracker
Tests that the orbit data time range slicing bug fix is working correctly.
Uses the existing speed_test.py TimingTracker system.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from plotbot import plotbot, psp_orbit, mag_rtn_4sa, print_manager, plt
from speed_test import timing_tracker

def test_orbit_performance():
    """Test orbit performance using the existing TimingTracker system"""
    
    # Enable speed test output
    print_manager.show_speed_test = True
    
    # Use a time range that has actual PSP data
    trange = ['2021-11-20/00:00:00.000', '2021-11-21/00:00:00.000']
    
    # Start PSP Orbit test
    timing_tracker.start_test("PSP_Orbit_Performance")
    
    # Run 1: First call (should be slow)
    timing_tracker.start_run(1, {"description": "First run - no caching"})
    step1 = timing_tracker.start_step("plotbot_call", {"trange": trange, "variable": "psp_orbit.r_sun"})
    plotbot(trange, psp_orbit.r_sun, 1)
    timing_tracker.end_step(step1)
    
    # Run 2: Second call (should be cached and fast)
    timing_tracker.start_run(2, {"description": "Second run - cached"})
    step2 = timing_tracker.start_step("plotbot_call", {"trange": trange, "variable": "psp_orbit.r_sun"})
    plotbot(trange, psp_orbit.r_sun, 1)
    timing_tracker.end_step(step2)
    
    # Start Magnetic Field test
    timing_tracker.start_test("Magnetic_Field_Performance")
    
    # Run 1: First call (should be slow)
    timing_tracker.start_run(1, {"description": "First run - no caching"})
    step3 = timing_tracker.start_step("plotbot_call", {"trange": trange, "variable": "mag_rtn_4sa.br"})
    plotbot(trange, mag_rtn_4sa.br, 1)
    timing_tracker.end_step(step3)
    
    # Run 2: Second call (should be cached and fast)
    timing_tracker.start_run(2, {"description": "Second run - cached"})
    step4 = timing_tracker.start_step("plotbot_call", {"trange": trange, "variable": "mag_rtn_4sa.br"})
    plotbot(trange, mag_rtn_4sa.br, 1)
    timing_tracker.end_step(step4)
    
    # Print comprehensive report
    timing_tracker.print_comprehensive_report()
    
    # Cleanup
    try:
        plt.close('all')
        print_manager.speed_test("🧹 Cleanup complete - all matplotlib figures closed")
    except:
        pass

if __name__ == "__main__":
    test_orbit_performance() 