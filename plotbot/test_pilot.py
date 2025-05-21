# test_pilot.py - Space-themed pytest framework for Plotbot
import logging
import os

# Define the intended log file path
log_file_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "test_logs")
log_file_path = os.path.join(log_file_dir, "test_data_loading.txt")

try:
    # Ensure the log directory exists
    os.makedirs(log_file_dir, exist_ok=True)
    # Attempt to configure file-based logging
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
except Exception as e:
    # If file logging fails for any reason, fall back to console logging
    print(f"Notice: Could not configure file logging for {log_file_path} ({e}). Falling back to console logging for test_pilot.")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

try:
    import pytest
    import time
    import inspect
    from termcolor import colored
    from datetime import datetime
    import numpy as np

    class TestPilotPlugin:
        """
        Pytest plugin for space-themed test output
        """
        @pytest.hookimpl(trylast=True)
        def pytest_configure(self, config):
            """Register custom markers"""
            config.addinivalue_line("markers", "mission: mark test as part of a specific mission")
            config.mission_start_time = time.time()
            print(colored("========== MISSION CONTROL ==========", "cyan"))
            
        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtest_protocol(self, item, nextitem):
            # Extract mission name
            mission_marker = item.get_closest_marker("mission")
            mission_name = mission_marker.args[0] if mission_marker else "Unnamed Mission"
            
            # Get module name (shortened)
            module_path = item.module.__name__
            module_name = module_path.split('.')[-1] if '.' in module_path else module_path
            
            # Start test message
            print(colored(f"\n🚀 MISSION: {mission_name}", "cyan"))
            print(colored(f"📋 TEST: {item.name}", "cyan"))
            print(colored(f"📁 MODULE: {module_name}", "cyan"))
            print(colored(f"{'=' * 40}", "cyan"))
            
            # Run the test
            start_time = time.time()
            outcome = yield
            duration = time.time() - start_time
            
            # End test message based on result
            result = outcome.get_result()
            if result.passed:
                print(colored(f"🌟 SUCCESS: {mission_name} ({duration:.2f}s)", "green"))
            elif result.failed:
                print(colored(f"💥 FAILED: {mission_name} ({duration:.2f}s)", "red"))
            else:
                print(colored(f"⚠️ SKIPPED: {mission_name} ({duration:.2f}s)", "yellow"))
        
        @pytest.hookimpl(trylast=True)
        def pytest_terminal_summary(self, terminalreporter, exitstatus, config):
            """Generate mission summary"""
            mission_duration = time.time() - config.mission_start_time
            
            print(colored("\n========== MISSION SUMMARY ==========", "cyan"))
            print(colored(f"⏱️ DURATION: {mission_duration:.2f}s", "cyan"))
            print(colored(f"✅ PASSED: {len(terminalreporter.stats.get('passed', []))} tests", "green"))
            print(colored(f"❌ FAILED: {len(terminalreporter.stats.get('failed', []))} tests", "red"))
            print(colored(f"⚠️ SKIPPED: {len(terminalreporter.stats.get('skipped', []))} tests", "yellow"))
            print(colored(f"{'=' * 40}", "cyan"))

    # Try to register the plugin using a compatible method
    try:
        # Modern pytest uses entry points instead of direct registration
        # This is a fallback method for direct registration
        if hasattr(pytest, 'register_plugin'):
            pytest.register_plugin(TestPilotPlugin())
        else:
            # For newer pytest versions, we'll use this approach
            pytest_plugins = ["test_pilot"]  # This should work for dynamically loaded plugins
    except Exception as e:
        print(f"Warning: Could not register TestPilotPlugin: {e}")

    # Helper functions for test phases
    def phase(num, description):
        """Print a test phase marker"""
        print(colored(f"🔵 PHASE {num}: {description}", "blue"))

    def system_check(name, condition, message):
        """Check a system condition"""
        if condition:
            logging.info(f"{name} - PASSED: {message}")
        else:
            logging.error(f"{name} - FAILED: {message}")
            print(colored(f"🔴 FAILURE: {message}", "red"))
            assert condition, message
        print(f"{name} - {'PASSED' if condition else 'FAILED'}: {message}")
        return True

    # Function to run tests in Jupyter notebooks
    def run_missions(test_module=None, test_name=None):
        """
        Run tests with space-themed output, suitable for Jupyter notebooks
        
        Parameters
        ----------
        test_module : str, optional
            Module name containing tests (e.g., 'tests.test_custom_variables')
        test_name : str, optional
            Specific test name to run
            
        Returns
        -------
        int
            Exit code (0 = success)
        """
        args = ["-v"]
        
        if test_module:
            args.append(test_module)
            if test_name:
                args.append(f"-k {test_name}")
        
        return pytest.main(args)

except ImportError:
    # Fallback if pytest is not available
    import time
    from datetime import datetime
    
    def phase(num, description):
        """Print a test phase marker (fallback version)"""
        print(f"--- PHASE {num}: {description} ---")
        
    def system_check(name, condition, message):
        """Check a system condition (fallback version)"""
        if not condition:
            print(f"FAILURE: {message}")
            assert condition, message
        return True
        
    def run_missions(test_module=None, test_name=None):
        """Fallback function when pytest is not installed"""
        print("ERROR: pytest not installed. Please install pytest to run tests:")
        print("  pip install pytest termcolor")
        print("Tests cannot be run without pytest.")
        return 1 