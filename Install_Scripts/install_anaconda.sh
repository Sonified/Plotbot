#!/bin/bash

echo "🔹 Starting Standard Conda Installation"
echo "======================================="
echo ""
echo "This installation method uses conda/miniconda and requires the following prerequisites:"
echo "1. Xcode Command Line Tools"
echo "2. Homebrew"
echo "3. Miniconda (installed via Homebrew)"
echo "4. Git"
echo ""
echo "If you haven't installed these prerequisites, please refer to the README.md"
echo "for detailed installation instructions."
echo ""

# Check for prerequisites
echo "🔍 Checking prerequisites..."

# Check for Xcode Command Line Tools
if ! xcode-select -p &> /dev/null; then
    echo "❌ Xcode Command Line Tools not found."
    echo "   Please install with: xcode-select --install"
    exit 1
else
    echo "✅ Xcode Command Line Tools found"
fi

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found."
    echo "   Please install from: https://brew.sh"
    exit 1
else
    echo "✅ Homebrew found"
fi

# Check for Git
if ! command -v git &> /dev/null; then
    echo "❌ Git not found."
    echo "   Please install with: brew install git"
    exit 1
else
    echo "✅ Git found"
fi

echo ""
echo "🚀 All prerequisites found! Starting installation..."
echo ""

# Step 1: Initialize Conda
echo "🔹 Step 1/3: Initializing Conda..."
./install_scripts/1_init_conda.sh
init_status=$?
if [ $init_status -ne 0 ]; then
    echo "❌ Error: Conda initialization failed with code $init_status."
    exit 1
fi

echo ""
echo "🔹 Step 2/3: Setting up Environment..."
./install_scripts/2_setup_env.sh
setup_status=$?
if [ $setup_status -ne 0 ]; then
    echo "❌ Error: Environment setup failed with code $setup_status."
    exit 1
fi

echo ""
echo "🔹 Step 3/4: Installing Plotbot as Development Package..."
echo "Running: conda run -n plotbot_anaconda pip install -e ."
conda run -n plotbot_anaconda pip install -e .
install_status=$?
if [ $install_status -ne 0 ]; then
    echo "❌ Error: Plotbot package installation failed with code $install_status."
    exit 1
fi
echo "✅ Plotbot successfully installed as development package!"

echo ""
echo "🔹 Step 4/4: Registering Jupyter Kernel..."
./install_scripts/3_register_kernel.sh
kernel_status=$?
if [ $kernel_status -ne 0 ]; then
    echo "❌ Error: Kernel registration failed with code $kernel_status."
    exit 1
fi

echo ""
echo "🔧 Setting up IDE configuration..."
source ./install_scripts/setup_ide.sh
setup_ide_config "/opt/anaconda3/envs/plotbot_anaconda/bin/python3" "plotbot_anaconda"

echo ""
echo "🔧 Setting up auto-activation..."
echo 'conda activate plotbot_anaconda 2>/dev/null || true' >> ~/.zshrc
echo "✅ Auto-activation configured!"

echo ""
echo "🎉 Standard installation completed successfully!"
echo ""
echo "✅ Plotbot installed as development package (globally accessible in environment)"
echo "✅ Magnetic Hole Finder included as installable module"
echo ""
echo "⭐ Next steps:"
echo "1. Restart your terminal: exec zsh"
echo "2. Open VS Code/Cursor"
echo "3. Open example_notebooks/Plotbot.ipynb"
echo "4. Select 'Python (Plotbot)' as your kernel"
echo "5. Run the first cell to confirm setup"
echo "6. Explore one of the example plotbot jupyter notebooks to test the setup"
echo ""
echo "🌟 Happy Plotbotting! 🌟"
