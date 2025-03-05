#!/bin/bash

echo "🔹 Creating 'plotbot_env' environment..."

# Check if conda is properly in PATH
CONDA_PATH=$(which conda)
if [[ "$CONDA_PATH" != *"conda"* ]]; then
    echo "⚠️ Warning: Conda may not be in your PATH correctly."
    echo "   Current conda path: $CONDA_PATH"
    echo "   You may need to restart your terminal after running 1_init_conda.sh"
fi

echo "Running: conda env create -f environment.yml"
# Create environment without flags for maximum compatibility
conda env create -f environment.yml

# Check if environment was created
if conda env list | grep -q plotbot_env; then
    echo "✅ Environment created successfully!"
    echo "" 
    echo "Copy and paste the following command, including the period, to register Plotbot as a Jupyter kernel: ./install_scripts/3_register_kernel.sh"
    echo ""
else
    echo "❌ Error: Environment creation failed."
    echo ""
    echo "Troubleshooting:"
    echo "1. Checking conda version: $(conda --version)"
    echo "2. Checking which Python is active: $(which python)"
    echo ""
    echo "👉 Try updating conda with the following command:"
    echo "   conda update -n base -c defaults conda"
    echo ""
    echo "After updating conda, run this script again:"
    echo "   ./install_scripts/2_setup_env.sh"
    echo ""
    echo "Or try creating the environment manually:"
    echo "   conda create -n plotbot_env python=3.12"
    echo "   conda activate plotbot_env"
    echo "   conda install -c conda-forge jupyterlab matplotlib pandas numpy"
    echo ""
    exit 1
fi