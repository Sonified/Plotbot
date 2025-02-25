#!/bin/bash
echo "🚀 Setting up Plotbot in Jupyter..."

# Find Conda's activate script
if [ -z "$CONDA_EXE" ]; then
  echo "❌ Oops! Conda not initialized. Please run 1_init_conda.sh first." >&2
  exit 1
fi
CONDA_ROOT=$(dirname $(dirname "$CONDA_EXE"))
source "$CONDA_ROOT/etc/profile.d/conda.sh"

# Activate the environment
conda activate plotbot_env

# Remove any existing kernel with the same name
jupyter kernelspec uninstall -f plotbot_env 2>/dev/null || true

# Register the kernel
python -m ipykernel install --user --name=plotbot_env --display-name="Python (Plotbot)"

# Verify the kernel was correctly installed
if jupyter kernelspec list | grep -q plotbot_env; then
  echo "✅ Success! Plotbot is now registered with Jupyter!"
else
  echo "❌ Hmm, something went wrong with the Plotbot registration."
  exit 1
fi

# Print friendly instructions
echo ""
echo "📣 ONE LAST IMPORTANT STEP:"
echo "   If VS Code is currently open, you'll need to:"
echo ""
echo "   1. ❌ CLOSE VS Code completely"
echo "   2. 🟢 REOPEN VS Code"
echo "   3. 📂 Open Plotbot.ipynb"
echo "   4. 🔍 Select 'Python (Plotbot)' from the kernel list in the top right"
echo ""
echo "   This restart is REQUIRED for VS Code to detect your shiny new Plotbot environment!"
echo ""
echo "   If VS code is your default platform and is not already open, this command will open Plotbot: open Plotbot.ipynb"
echo ""
echo "🌟 Happy Plotbotting! 🌟"