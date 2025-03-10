#!/bin/bash

echo "🔹 Initializing Conda..."

# Detect which shell is being used
if [ -n "$ZSH_VERSION" ]; then
    SHELL_TYPE="zsh"
    PROFILE_FILE="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_TYPE="bash"
    PROFILE_FILE="$HOME/.bash_profile"
    if [ ! -f "$PROFILE_FILE" ]; then
        PROFILE_FILE="$HOME/.bashrc"
    fi
else
    # Default to bash if we can't detect
    SHELL_TYPE="bash"
    PROFILE_FILE="$HOME/.bash_profile"
fi

# Initialize conda for the detected shell
conda init $SHELL_TYPE
echo "✅ Conda has been initialized for $SHELL_TYPE shell."

# Ensure conda is in PATH before other Python installations
if ! grep -q "export PATH=\"\$CONDA_PREFIX/bin:\$PATH\"" "$PROFILE_FILE"; then
    echo '# Ensure conda Python is used before system Python' >> "$PROFILE_FILE"
    echo 'export PATH="$CONDA_PREFIX/bin:$PATH"' >> "$PROFILE_FILE"
    echo "✅ Added conda to PATH in $PROFILE_FILE"
fi

# Source the profile file to apply changes
echo "✅ Reloading terminal settings..."
source "$PROFILE_FILE"

# Verify conda path is correct
PYTHON_PATH=$(which python)
if [[ "$PYTHON_PATH" == *"conda"* ]]; then
    echo "✅ Conda Python is now your default Python interpreter."
else
    echo "⚠️ Warning: Conda Python is not your default interpreter."
    echo "   Current Python: $PYTHON_PATH"
    echo "   You may need to restart your terminal."
fi

# Check Conda version
CONDA_VERSION=$(conda --version | awk '{print $2}')
echo "ℹ️ Your current Conda version is: $CONDA_VERSION"

# Check for connectivity to Anaconda servers
echo "Checking connection to Anaconda servers..."
if ping -c 1 anaconda.org &> /dev/null; then
    # Try to get the latest version number
    LATEST_VERSION=$(conda search conda | grep -E "^conda\s" | tail -n 1 | awk '{print $2}' 2>/dev/null)

    if [ -n "$LATEST_VERSION" ] && [ "$CONDA_VERSION" != "$LATEST_VERSION" ]; then
        echo "🔄 A newer Conda version is available: $LATEST_VERSION"
        echo "Updating Conda often improves compatibility with VS Code and other tools."
        read -p "Would you like to update Conda now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Updating Conda..."
            conda update -n base -c defaults conda -y
        else
            echo "Continuing with existing Conda version..."
        fi
    else
        echo "✅ Your Conda installation appears to be up-to-date."
    fi
else
    echo "⚠️ Cannot connect to Anaconda servers. Your Conda version is $CONDA_VERSION."
    echo "Please run this script again when you have a connection to check for updates."
    echo "An updated Conda version may improve compatibility with VS Code and other tools."
fi

echo "✅ Conda initialization complete."
echo "" 
echo "Copy and paste the following command, including the period, to create the Plotbot environment from the YAML file: ./install_scripts/2_setup_env.sh"
echo ""