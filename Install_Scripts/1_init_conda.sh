#!/bin/bash

echo "🔹 Initializing Conda..."
conda init zsh 2>/dev/null || conda init bash  # Supports both Zsh and Bash
echo "✅ Conda has been initialized."

# Disable auto-activation of base environment
echo "🔹 Disabling auto-activation of (base) environment..."
conda config --set auto_activate_base false
echo "✅ Auto-activation of (base) is now OFF."

# Reload terminal settings without requiring manual restart
if [ -f ~/.zshrc ]; then
    source ~/.zshrc
elif [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

echo "✅ Terminal session will now refresh automatically..."
exec zsh  # Restart shell session automatically