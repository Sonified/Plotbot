#!/usr/bin/env python3
"""
Fix the time=self.time issue by adding hasattr check.
Change: time=self.time,
To:     time=self.time if hasattr(self, 'time') else None,
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
        
        # Replace pattern: time=self.time, -> time=self.time if hasattr(self, 'time') else None,
        new_content = re.sub(
            r'(\s+)time=self\.time,',
            r"\1time=self.time if hasattr(self, 'time') else None,",
            content
        )
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            files_modified += 1
            print(f"✅ Fixed: {filepath.relative_to(DATA_CLASSES_DIR.parent)}")
    except Exception as e:
        print(f"❌ Error in {filepath}: {e}")

print(f"\n✅ Fixed {files_modified} files")

