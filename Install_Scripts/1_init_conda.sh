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

# Check for connectivity to Anaconda servers with timeout protection
echo "Checking connection to Anaconda servers (with timeout protection)..."

# Test basic connectivity with timeout (use gtimeout on macOS if available, otherwise skip timeout)
if command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_CMD="gtimeout 5"
elif command -v timeout >/dev/null 2>&1; then
    TIMEOUT_CMD="timeout 5"
else
    # Fallback: use ping with built-in timeout
    TIMEOUT_CMD=""
fi

if [ -n "$TIMEOUT_CMD" ]; then
    PING_RESULT=$($TIMEOUT_CMD ping -c 1 anaconda.org &> /dev/null; echo $?)
else
    # Use ping's built-in timeout on macOS (wait max 5 seconds)
    PING_RESULT=$(ping -c 1 -W 5000 anaconda.org &> /dev/null; echo $?)
fi

if [ "$PING_RESULT" -eq 0 ]; then
    echo "✅ Basic connectivity to anaconda.org is working."
    
    # Try to get the latest version number with timeout protection
    echo "Checking for conda updates (this may take a moment)..."
    
    # First, test if conda search works at all with a short timeout
    if [ -n "$TIMEOUT_CMD" ]; then
        SEARCH_RESULT=$($TIMEOUT_CMD conda search conda &> /dev/null; echo $?)
    else
        # Fallback: run conda search with background timeout
        (conda search conda &> /dev/null) &
        SEARCH_PID=$!
        sleep 5
        if kill -0 $SEARCH_PID 2>/dev/null; then
            kill $SEARCH_PID 2>/dev/null
            wait $SEARCH_PID 2>/dev/null
            SEARCH_RESULT=124  # timeout exit code
        else
            wait $SEARCH_PID
            SEARCH_RESULT=$?
        fi
    fi
    
    if [ "$SEARCH_RESULT" -eq 0 ]; then
        echo "✅ Conda search is responsive, checking for latest version..."
        
        # Get the latest version with timeout
        if [ -n "$TIMEOUT_CMD" ]; then
            LATEST_VERSION=$($TIMEOUT_CMD bash -c 'conda search conda | grep -E "^conda\s" | tail -n 1 | awk "{print \$2}"' 2>/dev/null)
        else
            # Fallback without timeout command
            LATEST_VERSION=$(conda search conda 2>/dev/null | grep -E "^conda\s" | tail -n 1 | awk '{print $2}' 2>/dev/null || echo "")
        fi
        
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
        echo "⚠️ Conda search command timed out (>5 seconds)."
        echo "   This is often due to slow server response or network issues."
        echo "   Your current Conda version ($CONDA_VERSION) will work fine for Plotbot."
        echo "   You can manually check for updates later with:"
        echo "   conda update -n base -c defaults conda"
    fi
else
    # Provide specific error messages based on exit code
    case $PING_RESULT in
        1)
            echo "⚠️ No internet connection detected."
            echo "   anaconda.org is unreachable (network unreachable or no internet)."
            echo "   Please connect to the internet and run this script again."
            ;;
        2)
            echo "⚠️ DNS resolution failed for anaconda.org."
            echo "   This could be a DNS server issue or firewall blocking."
            echo "   Try checking your DNS settings or network configuration."
            ;;
        124)
            echo "⚠️ Connection to anaconda.org timed out after 5 seconds."
            echo "   Your internet connection may be very slow or unstable."
            echo "   Try again with a better connection or wait for network conditions to improve."
            ;;
        68)
            echo "⚠️ Host anaconda.org not found."
            echo "   This could be due to no internet connection, DNS issues, or the host being down."
            echo "   Check your internet connection first, then try again in a few minutes."
            ;;
        *)
            echo "⚠️ Connection to anaconda.org failed (exit code: $PING_RESULT)."
            echo "   This could be due to firewall, proxy, or other network issues."
            echo "   Check your network settings and try again."
            ;;
    esac
    echo "   Your current Conda version is $CONDA_VERSION and will work for Plotbot."
    echo "   You can manually check for conda updates later when connectivity is restored."
fi

echo "✅ Conda initialization complete."
echo "" 
echo "🎯 NEXT STEP:"
echo "Copy and paste the following command, including the period, to create the Plotbot environment from the YAML file:"
echo "./install_scripts/2_setup_env.sh"
echo ""
echo "💡 NOTE: If you continue to have connectivity issues, you can proceed with"
echo "   environment creation even if the version check above failed." 