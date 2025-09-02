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
echo "🔹 Step 3/3: Registering Jupyter Kernel..."
./install_scripts/3_register_kernel.sh
kernel_status=$?
if [ $kernel_status -ne 0 ]; then
    echo "❌ Error: Kernel registration failed with code $kernel_status."
    exit 1
fi

echo ""
echo "🎉 Standard installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Open VS Code"
echo "2. Open Plotbot.ipynb"
echo "3. Select 'Python (Plotbot)' as your kernel"
echo "4. Run the first cell to confirm setup"
echo ""
