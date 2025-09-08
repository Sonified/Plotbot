#!/usr/bin/env python3
"""
Test script to measure plotbot startup timing.

This script imports plotbot and generates a detailed timing report
to identify startup bottlenecks.

Usage:
    cd tests/
    python test_startup_timing.py
    
    OR with conda:
    conda run -n plotbot_env python tests/test_startup_timing.py
"""

import sys
import time
import subprocess
from pathlib import Path

# Add parent directory to path so we can import plotbot
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_timing_test():
    """Run the plotbot import timing test."""
    print("🕒 Starting Plotbot Import Timing Test")
    print("=" * 50)
    
    # Record overall timing
    start_time = time.time()
    
    try:
        # Import plotbot - this triggers all our timing measurements
        print("Importing plotbot...")
        import plotbot
        
        # The timing report is automatically printed by our modified __init__.py
        total_time = time.time() - start_time
        
        print(f"\n🎯 OVERALL RESULT:")
        print(f"Total import time: {total_time:.3f} seconds")
        
        # Test basic functionality to ensure everything still works
        print(f"\n🧪 BASIC FUNCTIONALITY TEST:")
        print(f"✅ plotbot.np available: {hasattr(plotbot, 'np')}")
        print(f"✅ plotbot.mag_rtn_4sa available: {hasattr(plotbot, 'mag_rtn_4sa')}")
        print(f"✅ plotbot.plotbot function available: {hasattr(plotbot, 'plotbot')}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR during import: {e}")
        return False

def save_timing_to_file():
    """Save timing results to a file for analysis."""
    try:
        # Import the timer to save results
        from plotbot.import_timer import timer
        import os
        
        # Save to proper tests/timing_reports directory
        reports_dir = os.path.join(os.path.dirname(__file__), "timing_reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = os.path.join(reports_dir, f"timing_report_{time.strftime('%Y%m%d_%H%M%S')}.csv")
        timer.save_report(filename)
        print(f"💾 Saved detailed timing data to: {filename}")
    except Exception as e:
        print(f"⚠️  Could not save timing report: {e}")

if __name__ == "__main__":
    print("Plotbot Startup Performance Analysis")
    print("=====================================\n")
    
    success = run_timing_test()
    
    if success:
        print("\n✅ Import test completed successfully!")
        save_timing_to_file()
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Look for imports >1s in the report above")
        print(f"   2. Focus on matplotlib, scipy, and data classes")
        print(f"   3. Consider lazy loading for the slowest components")
        
    else:
        print("\n❌ Import test failed!")
        sys.exit(1)
