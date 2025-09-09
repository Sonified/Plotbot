"""
Import Timer System for Plotbot Startup Optimization

This module provides tools to measure and analyze import times during plotbot initialization.
Use this to identify the slowest imports and prioritize optimization efforts.

Usage:
    from plotbot.import_timer import ImportTimer
    
    timer = ImportTimer()
    timer.start_session("plotbot_init")
    
    # Time individual imports
    numpy = timer.time_import('numpy')
    matplotlib = timer.time_import('matplotlib.pyplot') 
    
    # Time code blocks
    with timer.time_block("data_classes"):
        from .data_classes.psp_mag_rtn_4sa import mag_rtn_4sa
        
    timer.end_session()
    timer.print_report()
"""

import time
import sys
import importlib
from contextlib import contextmanager
from collections import defaultdict
from typing import Dict, List, Optional, Any
import threading

class ImportTimer:
    """Timer for measuring import performance and code execution blocks."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.session_name: Optional[str] = None
        self.session_start: Optional[float] = None
        self.import_times: Dict[str, float] = {}
        self.block_times: Dict[str, List[float]] = defaultdict(list)
        self.import_order: List[tuple] = []  # (name, time, duration)
        self._lock = threading.Lock()
        
    def start_session(self, name: str = "import_session"):
        """Start a new timing session."""
        if not self.enabled:
            return
            
        with self._lock:
            self.session_name = name
            self.session_start = time.time()
            self.import_times.clear()
            self.block_times.clear()
            self.import_order.clear()
            print(f"\n🕒 Starting import timing session: {name}")
    
    def time_import(self, module_name: str, from_module: Optional[str] = None) -> Any:
        """
        Time the import of a module and return the imported module.
        
        Args:
            module_name: Name of module to import (e.g., 'numpy', 'matplotlib.pyplot')
            from_module: If specified, import from this module (e.g., from_module='matplotlib', module_name='pyplot')
        
        Returns:
            The imported module
        """
        if not self.enabled:
            if from_module:
                return getattr(__import__(from_module, fromlist=[module_name]), module_name)
            else:
                return __import__(module_name)
        
        start_time = time.time()
        
        try:
            if from_module:
                # Handle "from X import Y" style imports
                module = __import__(from_module, fromlist=[module_name])
                imported_obj = getattr(module, module_name)
                display_name = f"from {from_module} import {module_name}"
            else:
                # Handle "import X" style imports
                imported_obj = __import__(module_name)
                display_name = module_name
                
            elapsed = time.time() - start_time
            
            with self._lock:
                self.import_times[display_name] = elapsed
                session_elapsed = start_time - self.session_start if self.session_start else 0
                self.import_order.append((display_name, session_elapsed, elapsed))
                
            self._print_import_result(display_name, elapsed)
            return imported_obj
            
        except ImportError as e:
            elapsed = time.time() - start_time
            self._print_import_result(f"{module_name} (FAILED)", elapsed, error=str(e))
            raise
    
    @contextmanager
    def time_block(self, block_name: str):
        """
        Context manager to time a block of code.
        
        Usage:
            with timer.time_block("loading_data_classes"):
                # Your code here
                pass
        """
        if not self.enabled:
            yield
            return
            
        start_time = time.time()
        session_elapsed = start_time - self.session_start if self.session_start else 0
        
        print(f"  🔧 Starting block: {block_name}")
        
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            
            with self._lock:
                self.block_times[block_name].append(elapsed)
                
            print(f"  ✅ Block '{block_name}' completed in {elapsed:.3f}s")
    
    def _print_import_result(self, name: str, elapsed: float, error: Optional[str] = None):
        """Print the result of an import timing."""
        if error:
            print(f"  ❌ {name}: {elapsed:.3f}s (ERROR: {error})")
        elif elapsed > 2.0:
            print(f"  🐌 {name}: {elapsed:.3f}s (SLOW)")
        elif elapsed > 0.5:
            print(f"  ⚠️  {name}: {elapsed:.3f}s")
        else:
            print(f"  ✅ {name}: {elapsed:.3f}s")
    
    def end_session(self):
        """End the current timing session."""
        if not self.enabled or not self.session_start:
            return
            
        total_elapsed = time.time() - self.session_start
        print(f"\n🏁 Session '{self.session_name}' completed in {total_elapsed:.3f}s")
    
    def print_report(self, top_n: int = 10):
        """Print a detailed timing report."""
        if not self.enabled:
            print("Import timing is disabled.")
            return
            
        print(f"\n" + "="*60)
        print(f"📊 IMPORT TIMING REPORT - {self.session_name}")
        print(f"="*60)
        
        if self.session_start:
            total_time = time.time() - self.session_start
            print(f"Total session time: {total_time:.3f}s")
        
        # Sort imports by time (slowest first)
        sorted_imports = sorted(self.import_times.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n🐌 SLOWEST IMPORTS (Top {min(top_n, len(sorted_imports))}):")
        print("-" * 50)
        for i, (name, elapsed) in enumerate(sorted_imports[:top_n], 1):
            percentage = (elapsed / sum(self.import_times.values())) * 100 if self.import_times else 0
            print(f"{i:2d}. {name:30s} {elapsed:6.3f}s ({percentage:4.1f}%)")
        
        # Block timing summary
        if self.block_times:
            print(f"\n🔧 BLOCK TIMING SUMMARY:")
            print("-" * 50)
            for block_name, times in self.block_times.items():
                avg_time = sum(times) / len(times)
                total_time = sum(times)
                print(f"{block_name:30s} {total_time:6.3f}s (avg: {avg_time:.3f}s, runs: {len(times)})")
        
        # Import timeline
        print(f"\n⏰ IMPORT TIMELINE:")
        print("-" * 50)
        for name, session_time, duration in self.import_order:
            print(f"{session_time:6.3f}s: {name:30s} (+{duration:.3f}s)")
        
        # Optimization suggestions
        self._print_optimization_suggestions()
    
    def _print_optimization_suggestions(self):
        """Print optimization suggestions based on timing data."""
        if not self.import_times:
            return
            
        print(f"\n💡 OPTIMIZATION SUGGESTIONS:")
        print("-" * 50)
        
        slow_imports = [(name, time) for name, time in self.import_times.items() if time > 1.0]
        total_slow_time = sum(time for _, time in slow_imports)
        
        if slow_imports:
            print(f"• {len(slow_imports)} imports take >1s each (total: {total_slow_time:.1f}s)")
            print(f"• Consider lazy loading for: {', '.join([name.split('.')[0] for name, _ in slow_imports[:3]])}")
        
        matplotlib_imports = [name for name in self.import_times.keys() if 'matplotlib' in name.lower()]
        if matplotlib_imports:
            matplotlib_time = sum(self.import_times[name] for name in matplotlib_imports)
            print(f"• Matplotlib imports: {matplotlib_time:.1f}s - good candidate for lazy loading")
        
        scipy_imports = [name for name in self.import_times.keys() if 'scipy' in name.lower()]
        if scipy_imports:
            scipy_time = sum(self.import_times[name] for name in scipy_imports)
            print(f"• Scipy imports: {scipy_time:.1f}s - consider function-level imports")
        
        print(f"• Focus optimization on imports >0.5s for maximum impact")
    
    def save_report(self, filename: str):
        """Save the timing report to a file."""
        if not self.enabled:
            return
            
        with open(filename, 'w') as f:
            f.write(f"Import Timing Report - {self.session_name}\n")
            f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for name, elapsed in sorted(self.import_times.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{name},{elapsed:.3f}\n")
        
        print(f"Report saved to: {filename}")

# Global timer instance
timer = ImportTimer()

# Convenience functions for easy use
def start_timing(session_name: str = "plotbot_startup"):
    """Start timing imports for plotbot startup."""
    timer.start_session(session_name)

def time_import(module_name: str, from_module: Optional[str] = None):
    """Time an import and return the module."""
    return timer.time_import(module_name, from_module)

def time_block(block_name: str):
    """Time a block of code."""
    return timer.time_block(block_name)

def end_timing():
    """End timing and print report."""
    timer.end_session()
    timer.print_report()

def save_timing_report(filename: str):
    """Save timing report to file."""
    timer.save_report(filename)




