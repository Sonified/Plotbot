#!/bin/bash
echo "🚀 Setting up Plotbot in Jupyter..."

# Directly activate the environment without relying on CONDA_EXE
# This is more reliable across different conda installations
source "$(conda info --base)/etc/profile.d/conda.sh"

# Activate the environment
conda activate plotbot_anaconda || { 
    echo "❌ Failed to activate plotbot_anaconda. Please verify it exists with 'conda env list'"; 
    exit 1; 
}

# Verify we're in the right environment
echo "✓ Using Python: $(which python)"

# Install ipykernel if not already installed
pip install ipykernel --quiet

# Remove any existing kernel with the same name
jupyter kernelspec uninstall -f plotbot_anaconda 2>/dev/null || true

# Register the kernel
python -m ipykernel install --user --name=plotbot_anaconda --display-name="Python (Plotbot)"

# Verify the kernel was correctly installed
if jupyter kernelspec list | grep -q plotbot_anaconda; then
    echo "✅ Success! Plotbot is now registered with Jupyter!"
else
    echo "❌ Something went wrong with the Plotbot registration."
    exit 1
fi
