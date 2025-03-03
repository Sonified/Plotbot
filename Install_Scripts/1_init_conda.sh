#!/bin/bash

echo "🔹 Initializing Conda..."
# Detect and initialize the appropriate shell
if [ -n "$ZSH_VERSION" ]; then
    conda init zsh
elif [ -n "$BASH_VERSION" ]; then
    conda init bash
else
    conda init zsh 2>/dev/null || conda init bash
fi
echo "✅ Conda has been initialized (if it wasn't already)."

# Reload terminal settings
if [ -n "$ZSH_VERSION" ] && [ -f ~/.zshrc ]; then
    echo "✅ Reloading terminal settings..."
    source ~/.zshrc
elif [ -n "$BASH_VERSION" ] && [ -f ~/.bashrc ]; then
    echo "✅ Reloading terminal settings..."
    source ~/.bashrc
else
    echo "✅ Reloading terminal settings might be needed manually."
fi

echo "✅ Conda initialization complete."
echo "" 
echo "Copy and paste the following command, including the period, to create the Plotbot environment from the YAML file: ./install_scripts/2_setup_env.sh"
echo ""