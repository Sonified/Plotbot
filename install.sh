#!/bin/bash

echo "🚀 Welcome to Plotbot Installation"
echo "===================================="
echo ""
echo "Plotbot is a space physics data visualization, audification, and analysis tool"
echo "for multiple spacecraft, currently featuring Parker Solar Probe and WIND."
echo ""
echo "Please select your installation method:"
echo ""
echo "1) ⭐ Micromamba Installation (Recommended for ALL users)"
echo "   - Zero prerequisites - handles everything automatically!"
echo "   - Works in restricted environments (government, NASA, etc.)"
echo "   - Uses micromamba with conda-forge"
echo "   - No sudo required, installs in user directory"
echo ""
echo "2) Anaconda Installation (Traditional method)"
echo "   - Uses conda/miniconda package manager"
echo "   - Full access to all conda channels"
echo "   - Requires manual prerequisite installation"
echo ""
# Loop until we get a valid choice
while true; do
    read -p "Enter your choice (1 or 2): " -r INSTALL_CHOICE
    echo ""

    case $INSTALL_CHOICE in
    1)
        echo ""
        echo "🔹 You selected: Micromamba Installation"
        echo "   This will automatically set up everything you need with zero prerequisites!"
        echo ""
        echo "Starting micromamba installation..."
        exec ./install_scripts/install_micromamba.sh
        ;;
    2)
        echo ""
        echo "🔹 You selected: Anaconda Installation"
        echo "   This will set up conda/miniconda and create the environment."
        echo ""
        echo "Starting anaconda installation..."
        exec ./install_scripts/install_standard.sh
        ;;
    *)
        echo "❌ Invalid choice '$INSTALL_CHOICE'. Please enter 1 or 2."
        echo ""
        continue
        ;;
    esac
    break  # Exit the loop when we get a valid choice
done
