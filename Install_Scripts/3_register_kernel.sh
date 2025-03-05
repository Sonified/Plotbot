#!/bin/bash
echo "🚀 Setting up Plotbot in Jupyter..."

# Directly activate the environment without relying on CONDA_EXE
# This is more reliable across different conda installations
source "$(conda info --base)/etc/profile.d/conda.sh"

# Activate the environment
conda activate plotbot_env || { 
    echo "❌ Failed to activate plotbot_env. Please verify it exists with 'conda env list'"; 
    exit 1; 
}

# Verify we're in the right environment
echo "✓ Using Python: $(which python)"

# Install ipykernel if not already installed
pip install ipykernel --quiet

# Remove any existing kernel with the same name
jupyter kernelspec uninstall -f plotbot_env 2>/dev/null || true

# Register the kernel
python -m ipykernel install --user --name=plotbot_env --display-name="Python (Plotbot)"

# Verify the kernel was correctly installed
if jupyter kernelspec list | grep -q plotbot_env; then
    echo "✅ Success! Plotbot is now registered with Jupyter!"
else
    echo "❌ Something went wrong with the Plotbot registration."
    exit 1
fi

# Check for VS Code installation and add instructions
if [ -d "/Applications/Visual Studio Code.app" ] || [ -d "$HOME/Applications/Visual Studio Code.app" ]; then
    echo ""
    echo "📣 VS Code Instructions:"
    echo "   1. ❌ CLOSE VS Code completely if it's open"
    echo "   2. 🟢 Open Terminal and run: code"
    echo "   3. In VS Code, press Cmd+Shift+P and type 'Python: Select Interpreter'"
    echo "   4. Select the Plotbot environment or browse to: $(conda info --base)/envs/plotbot_env/bin/python"
    echo "   5. 📂 Open Plotbot.ipynb and select 'Python (Plotbot)' kernel"
    echo ""
else
    echo ""
    echo "📣 VS Code not detected. If you use VS Code:"
    echo "   After installation, you'll need to manually select the Python interpreter:"
    echo "   - Press Cmd+Shift+P and type 'Python: Select Interpreter'"
    echo "   - Select the Plotbot environment or browse to: $(conda info --base)/envs/plotbot_env/bin/python"
    echo ""
fi

echo "🌟 Happy Plotbotting! 🌟"