# tests/speed_test.py
# Global timing tracker for comprehensive performance testing

import time
from typing import Dict, List, Optional, Any
from collections import defaultdict
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from plotbot.print_manager import print_manager

class TimingTracker:
    """
    Global timing tracker that can handle multiple runs and data types.
    Provides dynamic step numbering and comprehensive performance analysis.
    """
    
    def __init__(self):
        # Structure: {test_name: {run_number: {step_name: {start_time, end_time, duration, metadata}}}}
        self.timings: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        self.current_test: Optional[str] = None
        self.current_run: Optional[int] = None
        self.step_counter: int = 0
        self.active_steps: Dict[str, float] = {}  # Track currently active steps
        
    def start_test(self, test_name: str):
        """Start a new test session."""
        self.current_test = test_name
        self.current_run = None
        self.step_counter = 0
        self.active_steps = {}
        print_manager.speed_test(f"🚀 Starting test: {test_name}")
        
    def start_run(self, run_number: int, metadata: Optional[Dict] = None):
        """Start a new run within the current test."""
        if self.current_test is None:
            raise ValueError("Must start a test before starting a run")
        
        self.current_run = run_number
        self.step_counter = 0
        self.active_steps = {}
        
        # Store run metadata
        if metadata:
            self.timings[self.current_test][self.current_run]['_metadata'] = metadata
        
        print_manager.speed_test(f"🏃 Starting run {run_number} for test: {self.current_test}")
        
    def start_step(self, step_name: str, metadata: Optional[Dict] = None) -> str:
        """Start a new step and return the step key."""
        if self.current_test is None or self.current_run is None:
            raise ValueError("Must start a test and run before starting a step")
        
        self.step_counter += 1
        step_key = f"step_{self.step_counter:02d}_{step_name}"
        
        start_time = time.time()
        self.active_steps[step_key] = start_time
        
        # Store step data
        self.timings[self.current_test][self.current_run][step_key] = {
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'metadata': metadata or {}
        }
        
        print_manager.speed_test(f"⏰ Step {self.step_counter}: {step_name} - STARTED")
        return step_key
        
    def end_step(self, step_key: str, metadata: Optional[Dict] = None):
        """End a step and calculate duration."""
        if step_key not in self.active_steps:
            print_manager.speed_test(f"⚠️ Warning: Step {step_key} was not started or already ended")
            return
        
        end_time = time.time()
        duration = end_time - self.active_steps[step_key]
        
        # Update step data
        step_data = self.timings[self.current_test][self.current_run][step_key]
        step_data['end_time'] = end_time
        step_data['duration'] = duration
        if metadata:
            step_data['metadata'].update(metadata)
        
        # Remove from active steps
        del self.active_steps[step_key]
        
        # Extract step name for display
        step_name = step_key.split('_', 2)[2] if '_' in step_key else step_key
        print_manager.speed_test(f"✅ Step {step_key.split('_')[1]}: {step_name} - COMPLETED ({duration*1000:.2f}ms)")
        
    def checkpoint(self, step_name: str, metadata: Optional[Dict] = None):
        """Quick checkpoint - starts and immediately ends a step."""
        step_key = self.start_step(step_name, metadata)
        self.end_step(step_key, metadata)
        
    def get_run_summary(self, test_name: str, run_number: int) -> Dict:
        """Get summary statistics for a specific run."""
        if test_name not in self.timings or run_number not in self.timings[test_name]:
            return {}
        
        run_data = self.timings[test_name][run_number]
        steps = {k: v for k, v in run_data.items() if not k.startswith('_')}
        
        total_duration = sum(step['duration'] for step in steps.values() if step['duration'] is not None)
        step_count = len(steps)
        
        return {
            'total_duration': total_duration,
            'step_count': step_count,
            'steps': steps,
            'metadata': run_data.get('_metadata', {})
        }
    
    def compare_runs(self, test_name: str, run1: int, run2: int) -> Dict:
        """Compare two runs and return analysis."""
        summary1 = self.get_run_summary(test_name, run1)
        summary2 = self.get_run_summary(test_name, run2)
        
        if not summary1 or not summary2:
            return {}
        
        speedup = summary1['total_duration'] / summary2['total_duration'] if summary2['total_duration'] > 0 else 0
        
        # Step-by-step comparison
        step_comparisons = {}
        for step_name in summary1['steps']:
            if step_name in summary2['steps']:
                dur1 = summary1['steps'][step_name]['duration']
                dur2 = summary2['steps'][step_name]['duration']
                if dur1 and dur2:
                    step_speedup = dur1 / dur2 if dur2 > 0 else 0
                    step_comparisons[step_name] = {
                        'run1_duration': dur1,
                        'run2_duration': dur2,
                        'speedup': step_speedup,
                        'difference_ms': (dur1 - dur2) * 1000
                    }
        
        return {
            'run1_total': summary1['total_duration'],
            'run2_total': summary2['total_duration'],
            'overall_speedup': speedup,
            'step_comparisons': step_comparisons
        }
    
    def print_comprehensive_report(self):
        """Print a comprehensive report of all timing data."""
        print_manager.speed_test("="*80)
        print_manager.speed_test("📊 COMPREHENSIVE TIMING REPORT")
        print_manager.speed_test("="*80)
        
        for test_name, test_data in self.timings.items():
            print_manager.speed_test(f"\n🧪 TEST: {test_name}")
            print_manager.speed_test("-" * 60)
            
            # Print each run
            for run_num in sorted(test_data.keys()):
                summary = self.get_run_summary(test_name, run_num)
                if not summary:
                    continue
                    
                print_manager.speed_test(f"\n🏃 RUN {run_num}:")
                
                # Print metadata if available
                if summary['metadata']:
                    metadata_str = ", ".join(f"{k}: {v}" for k, v in summary['metadata'].items())
                    print_manager.speed_test(f"   Metadata: {metadata_str}")
                
                # Print steps
                for step_name, step_data in summary['steps'].items():
                    duration_ms = step_data['duration'] * 1000 if step_data['duration'] else 0
                    step_display = step_name.split('_', 2)[2] if '_' in step_name else step_name
                    print_manager.speed_test(f"   {step_name}: {duration_ms:.2f}ms - {step_display}")
                
                print_manager.speed_test(f"   ⏱️ TOTAL: {summary['total_duration']*1000:.2f}ms")
            
            # Compare runs if we have multiple
            run_numbers = sorted(test_data.keys())
            if len(run_numbers) >= 2:
                print_manager.speed_test(f"\n🔄 COMPARISON (Run {run_numbers[0]} vs Run {run_numbers[1]}):")
                comparison = self.compare_runs(test_name, run_numbers[0], run_numbers[1])
                
                if comparison:
                    print_manager.speed_test(f"   Run {run_numbers[0]} total: {comparison['run1_total']*1000:.2f}ms")
                    print_manager.speed_test(f"   Run {run_numbers[1]} total: {comparison['run2_total']*1000:.2f}ms")
                    print_manager.speed_test(f"   Overall speedup: {comparison['overall_speedup']:.2f}x")
                    
                    # Step-by-step differences
                    print_manager.speed_test("   Step-by-step comparison:")
                    for step_name, step_comp in comparison['step_comparisons'].items():
                        step_display = step_name.split('_', 2)[2] if '_' in step_name else step_name
                        print_manager.speed_test(f"     {step_display}: {step_comp['speedup']:.2f}x ({step_comp['difference_ms']:+.2f}ms)")

# Global instance
timing_tracker = TimingTracker() 