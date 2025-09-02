#!/bin/bash

echo "🔹 Registering Plotbot as Jupyter kernel (Micromamba)..."
echo ""

# Ensure micromamba is available
if ! command -v micromamba &> /dev/null; then
    echo "❌ Error: micromamba command not found."
    echo "   Please ensure micromamba is installed and your terminal is restarted."
    exit 1
fi

# Check if plotbot_env exists
if ! micromamba env list | grep -q "plotbot_env"; then
    echo "❌ Error: plotbot_env environment not found."
    echo "   Please run 3_setup_env_micromamba.sh first."
    exit 1
fi

echo "✅ Found plotbot_env environment"
echo ""

# Activate the environment and install ipykernel
echo "🔹 Installing ipykernel in plotbot_env..."
micromamba run -n plotbot_env python -m pip install ipykernel

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install ipykernel."
    exit 1
fi

echo "✅ ipykernel installed successfully"
echo ""

# Register the Jupyter kernel
echo "🔹 Registering Jupyter kernel..."
micromamba run -n plotbot_env python -m ipykernel install --user --name plotbot_env --display-name "Python (plotbot_env)"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to register Jupyter kernel."
    exit 1
fi

echo "✅ Jupyter kernel registered successfully"
echo ""

# Verify kernel registration
echo "🔍 Verifying kernel registration..."
if micromamba run -n plotbot_env jupyter kernelspec list | grep -q "plotbot_env"; then
    echo "✅ plotbot_env kernel is registered and available"
else
    echo "⚠️  Kernel may be registered but not showing in current environment"
    echo "   This is often normal - try checking in Jupyter/VS Code"
fi

# Test Python version and key packages
echo ""
echo "🔍 Environment verification:"
echo "   Python version: $(micromamba run -n plotbot_env python --version)"

# Test import of key packages
echo "   Testing key package imports..."
micromamba run -n plotbot_env python -c "
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
echo ""
echo "✅ Setup Summary:"
echo "   Environment: plotbot_env (micromamba)"
echo "   Kernel: Python (plotbot_env)"
echo "   Installation type: conda-forge only"
echo ""
echo "📋 Next steps:"
echo "1. Restart your terminal (or run: exec zsh)"
echo "2. Open VS Code or Jupyter"
echo "3. Open Plotbot.ipynb"
echo "4. Select 'Python (plotbot_env)' as your kernel"
echo "5. Run the first cell to confirm setup"
echo ""
echo "🔧 To activate the environment manually:"
echo "   micromamba activate plotbot_env"
echo ""
