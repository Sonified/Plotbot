#!/bin/bash

echo "🔹 Initializing Micromamba (No-Sudo Installation)..."
echo ""

# Set Homebrew prefix in user directory
export HOMEBREW_PREFIX="$HOME/homebrew"

# Check if Homebrew is already installed
if [ -f "$HOMEBREW_PREFIX/bin/brew" ]; then
    echo "✅ Homebrew already installed at $HOMEBREW_PREFIX"
else
    echo "📦 Installing Homebrew in user directory (no sudo required)..."
    
    # Create directories
    mkdir -p "$HOMEBREW_PREFIX"
    
    # Clone Homebrew
    echo "   Cloning Homebrew repository..."
    GIT_SSL_NO_VERIFY=true \
    git clone https://github.com/Homebrew/brew "$HOMEBREW_PREFIX/Homebrew"
    
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to clone Homebrew repository."
        exit 1
    fi
    
    # Set up symlinks
    mkdir -p "$HOMEBREW_PREFIX/bin"
    ln -s "$HOMEBREW_PREFIX/Homebrew/bin/brew" "$HOMEBREW_PREFIX/bin/brew"
    
    echo "✅ Homebrew installed successfully"
fi

# Update PATH for current session
export PATH="$HOMEBREW_PREFIX/bin:$HOMEBREW_PREFIX/sbin:$PATH"

# Detect shell and profile file using more reliable method
SHELL_BASE="$(basename "${SHELL:-/bin/bash}")"
if [ "$SHELL_BASE" = "zsh" ]; then
    SHELL_TYPE="zsh"
    PROFILE_FILE="$HOME/.zshrc"
    # Also update .zprofile for macOS zsh login shells
    ZPROFILE_FILE="$HOME/.zprofile"
elif [ "$SHELL_BASE" = "bash" ]; then
    SHELL_TYPE="bash"
    PROFILE_FILE="$HOME/.bash_profile"
    if [ ! -f "$PROFILE_FILE" ]; then
        PROFILE_FILE="$HOME/.bashrc"
    fi
else
    SHELL_TYPE="bash"
    PROFILE_FILE="$HOME/.bash_profile"
fi

# Add Homebrew to shell profile if not already present
if ! grep -q "HOMEBREW_PREFIX.*homebrew" "$PROFILE_FILE" 2>/dev/null; then
    echo ""
    echo "📝 Adding Homebrew to $PROFILE_FILE..."
    
    cat >> "$PROFILE_FILE" << 'EOF'

# Homebrew (user installation)
export HOMEBREW_PREFIX="$HOME/homebrew"
export PATH="$HOMEBREW_PREFIX/bin:$HOMEBREW_PREFIX/sbin:$PATH"
export MANPATH="$HOMEBREW_PREFIX/share/man:$MANPATH"
export INFOPATH="$HOMEBREW_PREFIX/share/info:$INFOPATH"
export HOMEBREW_CASK_OPTS="--appdir=$HOME/Applications"
export HOMEBREW_FORCE_VENDOR_RUBY=1
EOF
    
    echo "✅ Homebrew configuration added to $PROFILE_FILE"
    
    # For zsh, also add to .zprofile for login shells (macOS compatibility)
    if [ "$SHELL_TYPE" = "zsh" ] && [ -n "$ZPROFILE_FILE" ]; then
        if ! grep -q "HOMEBREW_PREFIX.*homebrew" "$ZPROFILE_FILE" 2>/dev/null; then
            cat >> "$ZPROFILE_FILE" << 'EOF'

# Homebrew (user installation)
export HOMEBREW_PREFIX="$HOME/homebrew"
export PATH="$HOMEBREW_PREFIX/bin:$HOMEBREW_PREFIX/sbin:$PATH"
export MANPATH="$HOMEBREW_PREFIX/share/man:$MANPATH"
export INFOPATH="$HOMEBREW_PREFIX/share/info:$INFOPATH"
export HOMEBREW_CASK_OPTS="--appdir=$HOME/Applications"
export HOMEBREW_FORCE_VENDOR_RUBY=1
EOF
            echo "✅ Homebrew configuration also added to $ZPROFILE_FILE"
        fi
    fi
else
    echo "✅ Homebrew already configured in $PROFILE_FILE"
fi

# Source the profile to apply changes
source "$PROFILE_FILE"

# Verify Homebrew installation
if ! command -v brew &> /dev/null; then
    echo "❌ Error: Homebrew installation failed. 'brew' command not found."
    exit 1
fi

echo "✅ Homebrew version: $(brew --version | head -n1)"

# Install micromamba if not already installed
if ! command -v micromamba &> /dev/null; then
    echo ""
    echo "📦 Installing micromamba..."
    brew install micromamba
    
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install micromamba."
        exit 1
    fi
    
    echo "✅ Micromamba installed successfully"
else
    echo "✅ Micromamba already installed"
fi

# Install git if not already installed
if ! command -v git &> /dev/null; then
    echo ""
    echo "📦 Installing git..."
    brew install git
    
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install git."
        exit 1
    fi
    
    echo "✅ Git installed successfully"
else
    echo "✅ Git already installed"
fi

# Initialize micromamba
MICROMAMBA_ROOT_PREFIX="$HOME/micromamba"

if [ ! -d "$MICROMAMBA_ROOT_PREFIX" ]; then
    echo ""
    echo "🔧 Initializing micromamba..."
    
    # Find micromamba with failsafe approach
    MICROMAMBA_PATH=""
    
    # Method 1: Ask Homebrew directly (most reliable for our installation)
    if BREW_PREFIX=$(brew --prefix micromamba 2>/dev/null); then
        CANDIDATE="$BREW_PREFIX/bin/micromamba"
        if [ -f "$CANDIDATE" ] && [ -x "$CANDIDATE" ]; then
            MICROMAMBA_PATH="$CANDIDATE"
            echo "✅ Found micromamba via Homebrew: $MICROMAMBA_PATH"
        fi
    fi
    
    # Method 2: Fallback to PATH-based detection
    if [ -z "$MICROMAMBA_PATH" ]; then
        if COMMAND_PATH=$(command -v micromamba 2>/dev/null); then
            # Resolve if it's a function/alias to get the actual binary
            if [ -f "$COMMAND_PATH" ] && [ -x "$COMMAND_PATH" ]; then
                MICROMAMBA_PATH="$COMMAND_PATH"
                echo "✅ Found micromamba in PATH: $MICROMAMBA_PATH"
            fi
        fi
    fi
    
    # Method 3: Common fallback locations
    if [ -z "$MICROMAMBA_PATH" ]; then
        FALLBACK_PATHS=(
            "$HOMEBREW_PREFIX/bin/micromamba"
            "$HOMEBREW_PREFIX/opt/micromamba/bin/micromamba"
        )
        
        for path in "${FALLBACK_PATHS[@]}"; do
            if [ -f "$path" ] && [ -x "$path" ]; then
                MICROMAMBA_PATH="$path"
                echo "✅ Found micromamba at fallback location: $MICROMAMBA_PATH"
                break
            fi
        done
    fi
    
    # Final check
    if [ -z "$MICROMAMBA_PATH" ]; then
        echo "❌ Error: micromamba not found anywhere!"
        echo "   Checked:"
        echo "   - Homebrew registry: brew --prefix micromamba"
        echo "   - System PATH: command -v micromamba"
        echo "   - Common locations: $HOMEBREW_PREFIX/bin/ and $HOMEBREW_PREFIX/opt/"
        echo ""
        echo "   This suggests the Homebrew installation failed."
        echo "   Try running: brew install micromamba"
        exit 1
    fi
    
    # Initialize micromamba for the shell
    "$MICROMAMBA_PATH" shell init --shell $SHELL_TYPE --root-prefix "$MICROMAMBA_ROOT_PREFIX"
    
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to initialize micromamba."
        exit 1
    fi
    
    echo "✅ Micromamba initialized successfully"
else
    echo "✅ Micromamba already initialized"
fi

# Update PATH for current session AND source profile
export PATH="$HOMEBREW_PREFIX/bin:$HOMEBREW_PREFIX/sbin:$PATH"
source "$PROFILE_FILE"

# Verify micromamba installation
if command -v micromamba &> /dev/null; then
    echo "✅ Micromamba version: $(micromamba --version)"
else
    echo "⚠️  Micromamba initialized but not yet available in PATH."
    echo "   You may need to restart your terminal."
fi

echo ""
echo "🎉 Micromamba initialization completed!"
echo ""
echo "Important: You may need to restart your terminal or run 'exec $SHELL_TYPE'"
echo "before proceeding to the next step."
echo ""
