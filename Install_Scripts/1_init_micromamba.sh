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

# Detect shell and profile file
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
    
    # Get the actual micromamba path
    MICROMAMBA_PATH=$(brew --prefix)/bin/micromamba
    
    if [ ! -f "$MICROMAMBA_PATH" ]; then
        echo "❌ Error: micromamba not found at $MICROMAMBA_PATH"
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

# Source the shell configuration to make micromamba available
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
