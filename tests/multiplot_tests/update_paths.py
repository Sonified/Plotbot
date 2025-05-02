import os
import pathlib
import re

def update_file_paths(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Replace parent.parent with parent.parent.parent
    updated_content = re.sub(
        r'pathlib\.Path\(__file__\)\.parent\.parent',
        'pathlib.Path(__file__).parent.parent.parent',
        content
    )
    
    if updated_content != content:
        with open(file_path, 'w') as file:
            file.write(updated_content)
        print(f"Updated {file_path}")
    else:
        print(f"No changes needed in {file_path}")

def main():
    multiplot_tests_dir = pathlib.Path(__file__).parent / "multiplot_tests"
    
    for file_name in os.listdir(multiplot_tests_dir):
        if file_name.endswith('.py') and file_name != '__init__.py':
            file_path = multiplot_tests_dir / file_name
            update_file_paths(file_path)
            
    print("All files updated!")

if __name__ == "__main__":
    main() 