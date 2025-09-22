#!/bin/bash

echo "🔹 Starting Micromamba Installation (No-Sudo)"
echo "=============================================="
echo ""
echo "This installation method is designed for restricted environments"
echo "such as government systems (NASA, etc.) where:"
echo "- No sudo/administrator access"
echo "- Anaconda repositories may be blocked"
echo "- Only conda-forge channel is accessible"
echo ""
echo "This process will:"
echo "1. Install Homebrew in your home directory (no sudo required)"
echo "2. Install micromamba via Homebrew"
echo "3. Create a conda-forge-only environment file"
echo "4. Set up the plotbot_env environment"
echo "5. Register the Jupyter kernel"
echo ""

read -p "Do you want to continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo "🚀 Starting micromamba installation..."
echo ""

# Step 1: Initialize Micromamba (includes Homebrew setup)
echo "🔹 Step 1/4: Setting up Homebrew and Micromamba..."
./install_scripts/1_init_micromamba.sh
init_status=$?
if [ $init_status -ne 0 ]; then
    echo "❌ Error: Micromamba initialization failed with code $init_status."
    exit 1
fi

echo ""
echo "🔹 Step 2/4: Creating conda-forge-only environment file..."
./install_scripts/2_create_environment_cf.sh
env_file_status=$?
if [ $env_file_status -ne 0 ]; then
    echo "❌ Error: Environment file creation failed with code $env_file_status."
    exit 1
fi

echo ""
echo "🔹 Step 3/4: Setting up Environment with Micromamba..."
./install_scripts/3_setup_env_micromamba.sh
setup_status=$?
if [ $setup_status -ne 0 ]; then
    echo "❌ Error: Environment setup failed with code $setup_status."
    exit 1
fi

echo ""
echo "🔹 Step 4/5: Installing Plotbot as Development Package..."
echo "Running: micromamba run -n plotbot_micromamba pip install -e ."
$HOME/homebrew/opt/micromamba/bin/micromamba run -n plotbot_micromamba pip install -e .
install_status=$?
if [ $install_status -ne 0 ]; then
    echo "❌ Error: Plotbot package installation failed with code $install_status."
    exit 1
fi
echo "✅ Plotbot successfully installed as development package!"

echo ""
echo "🔹 Step 5/5: Registering Jupyter Kernel..."
./install_scripts/4_register_kernel_micromamba.sh
kernel_status=$?
if [ $kernel_status -ne 0 ]; then
    echo "❌ Error: Kernel registration failed with code $kernel_status."
    exit 1
fi

echo ""
echo "🔧 Setting up IDE configuration..."
source ./install_scripts/setup_ide.sh
setup_ide_config "$HOME/micromamba/envs/plotbot_micromamba/bin/python3" "plotbot_micromamba"

echo ""
echo "🎉 Micromamba installation completed successfully!"
echo ""
echo "✅ Homebrew installed in: \$HOME/homebrew"
echo "✅ Micromamba environment: plotbot_micromamba"
echo "✅ Plotbot installed as development package (globally accessible)"
echo "✅ Magnetic Hole Finder included as installable module"
echo "✅ Jupyter kernel registered: Python (plotbot_micromamba)"
echo ""
echo "⭐ Next steps:"
echo "1. Restart your terminal (exec zsh)"
echo "2. Open VS Code/Cursor"
echo "3. Open example_notebooks/Plotbot.ipynb"
echo "4. Select 'Python (plotbot_micromamba)' as your kernel"
echo "5. Run the first cell to confirm setup"
echo "6. Explore one of the example plotbot jupyter notebooks to test the setup"
echo ""
