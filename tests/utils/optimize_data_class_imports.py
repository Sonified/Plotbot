#!/usr/bin/env python3
"""
Data Class Import Optimization Script

This script automatically converts data class files from eager imports to lazy imports
for numpy, pandas, and cdflib to improve plotbot startup performance.

Usage:
    python tests/utils/optimize_data_class_imports.py --test  # Test on a few files
    python tests/utils/optimize_data_class_imports.py --all   # Apply to all files
    python tests/utils/optimize_data_class_imports.py --file path/to/file.py  # Single file
"""

import re
import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Heavy imports to optimize
HEAVY_IMPORTS = [
    'import numpy as np',
    'import pandas as pd', 
    'import cdflib'
]

# Pattern to find methods that need these imports
USAGE_PATTERNS = {
    'numpy': [
        r'\bnp\.',           # np.array(), np.zeros(), etc.
        r'numpy\.',          # numpy.array(), etc. 
        r'isinstance\([^)]*,\s*np\.',  # isinstance(obj, np.ndarray)
        r'np\b(?=\s*[\[\.])',  # np followed by [ or . (np.ndarray, np[0])
    ],  
    'pandas': [
        r'\bpd\.', 
        r'pandas\.', 
        r'isinstance\([^)]*,\s*pd\.',  # isinstance(obj, pd.DataFrame)
    ],  
    'cdflib': [
        r'\bcdflib\.', 
        r'cdflib\b(?=\s*[\[\.])',  # bare cdflib references
    ]
}

class DataClassOptimizer:
    def __init__(self):
        self.changes_made = []
        
    def find_heavy_imports(self, content: str) -> List[Tuple[str, int]]:
        """Find heavy imports and their line numbers."""
        imports_found = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            for heavy_import in HEAVY_IMPORTS:
                if stripped == heavy_import or stripped.startswith(heavy_import + ' '):
                    imports_found.append((heavy_import, i))
                    
        return imports_found
    
    def find_methods_using_imports(self, content: str) -> Dict[str, List[str]]:
        """Find methods that use numpy, pandas, or cdflib."""
        methods_needing_imports = {}
        lines = content.split('\n')
        current_method = None
        method_content = []
        indent_level = 0
        
        for i, line in enumerate(lines):
            # Detect method definitions
            if re.match(r'^\s*def\s+\w+\(', line):
                # Save previous method if it needed imports
                if current_method and method_content:
                    needed_imports = self._analyze_method_imports(method_content)
                    if needed_imports:
                        methods_needing_imports[current_method] = needed_imports
                
                # Start new method
                current_method = f"line_{i+1}"  # Store line number for reference
                method_content = [line]
                indent_level = len(line) - len(line.lstrip())
                
            elif current_method:
                # Check if we're still in the method
                if line.strip() == "" or len(line) - len(line.lstrip()) > indent_level:
                    method_content.append(line)
                else:
                    # Method ended, analyze it
                    needed_imports = self._analyze_method_imports(method_content)
                    if needed_imports:
                        methods_needing_imports[current_method] = needed_imports
                    current_method = None
                    method_content = []
        
        # Handle last method
        if current_method and method_content:
            needed_imports = self._analyze_method_imports(method_content)
            if needed_imports:
                methods_needing_imports[current_method] = needed_imports
                
        return methods_needing_imports
    
    def _analyze_method_imports(self, method_lines: List[str]) -> List[str]:
        """Analyze which imports a method needs."""
        method_text = '\n'.join(method_lines)
        needed = []
        
        if any(re.search(pattern, method_text) for pattern in USAGE_PATTERNS['numpy']):
            needed.append('import numpy as np')
        if any(re.search(pattern, method_text) for pattern in USAGE_PATTERNS['pandas']):
            needed.append('import pandas as pd')
        if any(re.search(pattern, method_text) for pattern in USAGE_PATTERNS['cdflib']):
            needed.append('import cdflib')
            
        return needed
    
    def optimize_file(self, file_path: str, dry_run: bool = False) -> bool:
        """Optimize a single data class file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Step 1: Comment out heavy imports at module level
            heavy_imports = self.find_heavy_imports(content)
            if not heavy_imports:
                print(f"ℹ️  {file_path}: No heavy imports found to optimize")
                return False
            
            # Comment out the imports
            lines = content.split('\n')
            for import_line, line_num in heavy_imports:
                if not lines[line_num].strip().startswith('#'):
                    lines[line_num] = f"# MOVED TO METHOD LEVEL: {lines[line_num]}"
            
            content = '\n'.join(lines)
            
            # Step 2: Add lazy imports to methods (AFTER commenting imports to preserve line numbers)
            methods_needing_imports = self.find_methods_using_imports(content)
            
            if methods_needing_imports:
                content = self._add_lazy_imports_to_methods(content, methods_needing_imports)
            
            # Step 3: Add header comment if changes were made
            if content != original_content:
                # Add optimization comment at the top
                header_comment = "# STARTUP OPTIMIZATION: Heavy imports (numpy, pandas, cdflib) moved to method level for faster initialization\n"
                if not content.startswith(header_comment):
                    content = header_comment + content
                
                if not dry_run:
                    # Write the optimized file
                    with open(file_path, 'w') as f:
                        f.write(content)
                    
                    self.changes_made.append(file_path)
                    print(f"✅ {file_path}: Optimized {len(heavy_imports)} imports in {len(methods_needing_imports)} methods")
                else:
                    print(f"🔍 {file_path}: Would optimize {len(heavy_imports)} imports in {len(methods_needing_imports)} methods")
                
                return True
            else:
                print(f"ℹ️  {file_path}: No optimization needed")
                return False
                
        except Exception as e:
            print(f"❌ {file_path}: Error - {e}")
            return False
    
    def _add_lazy_imports_to_methods(self, content: str, methods_needing_imports: Dict[str, List[str]]) -> str:
        """Add lazy imports to the beginning of methods that need them."""
        lines = content.split('\n')
        
        print(f"🔧 Adding lazy imports to {len(methods_needing_imports)} methods...")
        
        # CRITICAL FIX: Process methods in REVERSE order (bottom to top) so insertions don't affect line numbers
        sorted_methods = sorted(methods_needing_imports.items(), 
                               key=lambda x: int(x[0].split('_')[1]), reverse=True)
        
        for method_line_ref, needed_imports in sorted_methods:
            line_num = int(method_line_ref.split('_')[1]) - 1  # Convert back to 0-based index
            print(f"  🎯 Processing method at line {line_num + 1}: {needed_imports}")
            
            # Find the method definition line
            found_method = False
            for i in range(line_num, min(len(lines), line_num + 5)):
                if re.match(r'^\s*def\s+\w+\(', lines[i]):
                    print(f"    📍 Found method def at line {i + 1}: {lines[i].strip()}")
                    # Find the first line of method body (after docstring if present)
                    method_start = i + 1
                    
                    # Skip docstring if present
                    if method_start < len(lines) and '"""' in lines[method_start]:
                        print(f"    📝 Skipping docstring at line {method_start + 1}")
                        # Skip to end of docstring
                        while method_start < len(lines) and not (lines[method_start].count('"""') >= 2 or 
                              (method_start > i + 1 and '"""' in lines[method_start])):
                            method_start += 1
                        method_start += 1
                    
                    print(f"    💉 Will insert lazy imports at line {method_start + 1}")
                    print(f"    📝 Current line {method_start + 1}: '{lines[method_start] if method_start < len(lines) else 'EOF'}'")
                    
                    # Insert lazy imports
                    indent = '        '  # Standard method indentation
                    lazy_import_comment = f'{indent}# LAZY IMPORT: Only import when actually needed'
                    lazy_imports = [f'{indent}{imp}' for imp in needed_imports]
                    empty_line = f'{indent}'
                    
                    insert_lines = [lazy_import_comment] + lazy_imports + [empty_line]
                    print(f"    🔧 Inserting {len(insert_lines)} lines: {[line.strip() for line in insert_lines]}")
                    
                    # Insert the lines
                    for j, insert_line in enumerate(insert_lines):
                        lines.insert(method_start + j, insert_line)
                        print(f"      ✅ Inserted at line {method_start + j + 1}: '{insert_line.strip()}'")
                    
                    found_method = True
                    break
            
            if not found_method:
                print(f"    ❌ Could not find method definition around line {line_num + 1}")
        
        return '\n'.join(lines)
    
    def get_data_class_files(self, data_classes_dir: str) -> List[str]:
        """Get all Python data class files to optimize."""
        files = []
        data_classes_path = Path(data_classes_dir)
        
        if not data_classes_path.exists():
            print(f"❌ Data classes directory not found: {data_classes_dir}")
            return files
        
        # Get main data class files
        for py_file in data_classes_path.glob("*.py"):
            if not py_file.name.startswith("_") and py_file.name != "__init__.py":
                files.append(str(py_file))
        
        # Get custom class files
        custom_dir = data_classes_path / "custom_classes"
        if custom_dir.exists():
            for py_file in custom_dir.glob("*.py"):
                if not py_file.name.startswith("_") and py_file.name != "__init__.py":
                    files.append(str(py_file))
        
        return sorted(files)

def main():
    parser = argparse.ArgumentParser(description='Optimize data class imports for faster startup')
    parser.add_argument('--test', action='store_true', help='Test on 2-3 files only')
    parser.add_argument('--all', action='store_true', help='Apply to all data class files')
    parser.add_argument('--file', type=str, help='Optimize a specific file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    
    args = parser.parse_args()
    
    # Find plotbot root directory
    script_dir = Path(__file__).parent
    plotbot_root = script_dir.parent.parent  # Go up from tests/utils/
    data_classes_dir = plotbot_root / "plotbot" / "data_classes"
    
    optimizer = DataClassOptimizer()
    
    if args.file:
        # Optimize single file
        success = optimizer.optimize_file(args.file, dry_run=args.dry_run)
        if success:
            print(f"\n✅ Optimization completed!")
        else:
            print(f"\n❌ Optimization failed or not needed")
            
    elif args.test:
        # Test on a few files
        files = optimizer.get_data_class_files(str(data_classes_dir))
        test_files = files[:3]  # Just first 3 files
        
        print(f"🧪 Testing optimization on {len(test_files)} files...")
        successes = 0
        
        for file_path in test_files:
            if optimizer.optimize_file(file_path, dry_run=args.dry_run):
                successes += 1
        
        print(f"\n✅ Test completed: {successes}/{len(test_files)} files optimized")
        
    elif args.all:
        # Apply to all files
        files = optimizer.get_data_class_files(str(data_classes_dir))
        
        print(f"🚀 Optimizing all {len(files)} data class files...")
        successes = 0
        
        for file_path in files:
            if optimizer.optimize_file(file_path, dry_run=args.dry_run):
                successes += 1
        
        print(f"\n✅ Optimization completed: {successes}/{len(files)} files optimized")
        
        if optimizer.changes_made and not args.dry_run:
            print(f"\n📋 Files modified:")
            for file_path in optimizer.changes_made:
                print(f"  - {file_path}")
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
