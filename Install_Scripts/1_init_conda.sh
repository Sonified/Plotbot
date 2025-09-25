#!/bin/bash

echo "🔹 Initializing Conda (Timeout-Safe Version)..."

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

# Quick connectivity check
echo "Checking basic connectivity to Anaconda servers..."

# Simple ping test with built-in timeout (macOS compatible)
if ping -c 1 -W 5000 anaconda.org &> /dev/null; then
    echo "✅ Basic connectivity to anaconda.org is working."
    
    # Fast version check using API approach
    echo -n "🔍 Checking for latest conda version"
    START_TIME=$(date +%s)
    (curl -s --max-time 10 "https://api.anaconda.org/package/anaconda/conda" | python3 -c "import sys,json; print(json.load(sys.stdin)['latest_version'])" 2>/dev/null > /tmp/conda_ver_$$) &
    pid=$!; dots=1; while kill -0 $pid 2>/dev/null; do echo -ne "\r🔍 Checking for latest conda version$(printf "%*s" $dots | tr ' ' '.')"; dots=$((dots%3+1)); sleep 0.3; done
    wait $pid; LATEST_VERSION=$(cat /tmp/conda_ver_$$ 2>/dev/null); rm -f /tmp/conda_ver_$$
    END_TIME=$(date +%s); DURATION=$((END_TIME - START_TIME))
    echo -e "\r🔍 Checking for latest conda version... ✅ (${DURATION}s)"
    
    if [ -n "$LATEST_VERSION" ] && [ "$CONDA_VERSION" != "$LATEST_VERSION" ]; then
        echo "🔄 Newer version available: $LATEST_VERSION (you have $CONDA_VERSION)"
        read -p "Would you like to update Conda now? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Updating Conda..."
            conda update -n base conda -y
            if [ $? -eq 0 ]; then
                NEW_VERSION=$(conda --version | awk '{print $2}')
                echo "✅ Conda updated successfully from $CONDA_VERSION to $NEW_VERSION!"
            else
                echo "⚠️ Conda update had issues, but continuing with installation..."
            fi
        else
            echo "✅ Continuing with current Conda version..."
        fi
    else
        echo "✅ Your Conda version ($CONDA_VERSION) is up-to-date!"
    fi
else
    echo "⚠️ Cannot reach anaconda.org (network issue or firewall)."
    echo "   Your current Conda version ($CONDA_VERSION) will work fine for Plotbot."
    echo "   You can check for conda updates later when connectivity is restored:"
    echo "   conda update -n base conda"
fi

echo "✅ Conda initialization complete."
echo "" 
echo "🎯 NEXT STEP:"
echo "Copy and paste the following command, including the period, to create the Plotbot environment from the YAML file:"
echo "./install_scripts/2_setup_env.sh"
echo ""
echo "💡 NOTE: If you continue to have connectivity issues, you can proceed with"
echo "   environment creation even if the version check above failed." 