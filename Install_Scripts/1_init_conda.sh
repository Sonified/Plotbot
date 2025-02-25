#!/bin/bash

echo "🔹 Initializing Conda..."
conda init zsh 2>/dev/null || conda init bash
echo "✅ Conda has been initialized (if it wasn't already)."

# Reload terminal settings.  Source is enough.
if [ -f ~/.zshrc ]; then
    echo "✅ Reloading terminal settings..."
    source ~/.zshrc
elif [ -f ~/.bashrc ]; then
    echo "✅ Reloading terminal settings..."
    source ~/.bashrc
fi

echo "✅ Conda initialization complete."
echo "" 
echo "Copy and paste the following command, including the period, to run script #2: ./install_scripts/2_setup_env.sh"
echo "" 