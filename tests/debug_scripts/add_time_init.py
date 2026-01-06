#!/usr/bin/env python3
"""
Add object.__setattr__(self, 'time', None) initialization right after 
object.__setattr__(self, 'datetime_array', None) in all data class __init__ methods.
"""

import re
from pathlib import Path

DATA_CLASSES_DIR = Path(__file__).parent.parent / "plotbot" / "data_classes"

files_modified = 0

for filepath in DATA_CLASSES_DIR.rglob("*.py"):
    if filepath.name.endswith('.pyi'):
        continue
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find pattern: object.__setattr__(self, 'datetime_array', None)
        # Add:            object.__setattr__(self, 'time', None) right after
        pattern = r"(object\.__setattr__\(self, 'datetime_array', None\))"
        replacement = r"\1\n        object.__setattr__(self, 'time', None)"
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            files_modified += 1
            print(f"✅ Fixed: {filepath.relative_to(DATA_CLASSES_DIR.parent)}")
    except Exception as e:
        print(f"❌ Error in {filepath}: {e}")

print(f"\n✅ Fixed {files_modified} files")

