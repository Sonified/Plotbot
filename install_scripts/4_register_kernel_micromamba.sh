#!/bin/bash

echo "🔹 Registering Plotbot as Jupyter kernel (Micromamba)..."
echo ""

# Set up micromamba environment variables
export MAMBA_EXE="$HOME/homebrew/bin/micromamba"
export MAMBA_ROOT_PREFIX="$HOME/micromamba"

# Add homebrew to PATH if not already there
export PATH="$HOME/homebrew/bin:$PATH"

# Initialize micromamba shell hook for bash
__mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX" 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__mamba_setup"
else
    # Enhanced fallback - create a function that mimics micromamba behavior
    micromamba() {
        "$MAMBA_EXE" "$@"
    }
    export -f micromamba
fi

# Ensure micromamba is available - try direct path if command fails
if ! command -v micromamba &> /dev/null; then
    # Try using the direct path
    if [ -f "$MAMBA_EXE" ]; then
        echo "⚠️  Using direct path to micromamba: $MAMBA_EXE"
        micromamba() {
            "$MAMBA_EXE" "$@"
        }
        export -f micromamba
    else
        echo "❌ Error: micromamba command not found."
        echo "   Please ensure micromamba is installed and your terminal is restarted."
        exit 1
    fi
fi

# Check if plotbot_micromamba exists
if ! micromamba env list | grep -q "plotbot_micromamba"; then
    echo "❌ Error: plotbot_micromamba environment not found."
    echo "   Please run 3_setup_env_micromamba.sh first."
    exit 1
fi

echo "✅ Found plotbot_micromamba environment"
echo ""

# Activate the environment and install ipykernel
echo "🔹 Installing ipykernel in plotbot_micromamba..."
micromamba run -n plotbot_micromamba python -m pip install ipykernel

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install ipykernel."
    exit 1
fi

echo "✅ ipykernel installed successfully"
echo ""

# Register the Jupyter kernel
echo "🔹 Registering Jupyter kernel..."
micromamba run -n plotbot_micromamba python -m ipykernel install --user --name plotbot_micromamba --display-name "Plotbot (Micromamba)"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to register Jupyter kernel."
    exit 1
fi

echo "✅ Jupyter kernel registered successfully"
echo ""

# Verify kernel registration
echo "🔍 Verifying kernel registration..."
if micromamba run -n plotbot_micromamba jupyter kernelspec list | grep -q "plotbot_micromamba"; then
    echo "✅ plotbot_micromamba kernel is registered and available"
else
    echo "⚠️  Kernel may be registered but not showing in current environment"
    echo "   This is often normal - try checking in Jupyter/VS Code"
fi

# Test Python version and key packages
echo ""
echo "🔍 Environment verification:"
echo "   Python version: $(micromamba run -n plotbot_micromamba python --version)"

# Test import of key packages
echo "   Testing key package imports..."
micromamba run -n plotbot_micromamba python -c "
import sys
packages = ['numpy', 'matplotlib', 'pandas', 'scipy']
failed = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f'   ✅ {pkg}')
    except ImportError:
        print(f'   ❌ {pkg}')
        failed.append(pkg)
        
if failed:
    print(f'   ⚠️  Failed imports: {failed}')
    sys.exit(1)
else:
    print('   ✅ All key packages imported successfully')
"

if [ $? -ne 0 ]; then
    echo "❌ Error: Some required packages are not available."
    echo "   The environment may not be set up correctly."
    exit 1
fi

echo ""
echo "🎉 Kernel registration completed successfully!"
