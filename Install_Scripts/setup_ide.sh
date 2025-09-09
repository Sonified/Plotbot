#!/bin/bash
# Setup IDE configuration for Plotbot
# Creates .vscode/settings.json with correct Python interpreter

setup_ide_config() {
    local python_path="$1"
    local env_name="$2"
    
    # Create .vscode directory if it doesn't exist
    mkdir -p .vscode
    
    # Create/overwrite settings.json with correct Python interpreter
    cat > .vscode/settings.json << EOF
{
    "python.pythonPath": "$python_path",
    "python.defaultInterpreterPath": "$python_path",
    "jupyter.defaultKernel": "Python ($env_name)"
}
EOF

    echo "✅ IDE configured for syntax highlighting"
}

# Export function so other scripts can use it
export -f setup_ide_config
