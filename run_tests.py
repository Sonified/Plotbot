#!/usr/bin/env python3
"""
Test runner for Plotbot project.
Provides a convenient way to run tests from the tests directory.
"""
import sys
import os
import subprocess

def main():
    """Run tests based on command line arguments."""
    # Construct the pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    if len(sys.argv) > 1:
        # Run specific tests if provided as arguments
        args = sys.argv[1:]
        
        # Make sure paths start with tests/ if they don't already
        for i, arg in enumerate(args):
            if "::" in arg:
                # Handle test function specification (e.g., test_file.py::test_func)
                parts = arg.split("::", 1)
                file_path = parts[0]
                func_name = parts[1]
                
                if not file_path.startswith("tests/"):
                    file_path = "tests/" + file_path
                
                args[i] = f"{file_path}::{func_name}"
            elif not arg.startswith("tests/"):
                args[i] = "tests/" + arg
        
        cmd.extend(["-v"] + args)
    else:
        # Run all tests by default
        cmd.extend(["-v", "tests/"])
    
    # Print the command being run
    print(f"Running: {' '.join(cmd)}")
    
    # Run the command and return its exit code
    return subprocess.call(cmd)

if __name__ == "__main__":
    sys.exit(main()) 