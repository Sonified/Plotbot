#!/bin/bash

echo "🚀 Welcome to Plotbot Installation"
echo "===================================="
echo ""
echo "Plotbot is a space physics data visualization, audification, and analysis tool"
echo "for multiple spacecraft, currently featuring Parker Solar Probe and WIND."
echo ""
echo "Please select your installation method:"
echo ""
echo "1) ⭐ Micromamba Installation (Recommended / Quick)"
echo "   - Lightweight and fast environment setup"
echo "   - Zero prerequisites - handles everything automatically!"
echo "   - Works in restricted environments (government, NASA, etc.)"
echo "   - No sudo required, installs in user directory"
echo ""
echo "2) Anaconda Installation (Full Ecosystem)"
echo "   - Complete conda package manager with all channels"
echo "   - Access to entire Anaconda ecosystem"
echo "   - Requires manual prerequisite installation"
echo ""
echo "3) Cancel"
echo ""
# Loop until we get a valid choice
while true; do
    read -p "Enter your choice (1, 2, or 3): " -r INSTALL_CHOICE
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
        exec ./install_scripts/install_anaconda.sh
        ;;
    3)
        echo ""
        echo "🔹 Installation cancelled."
        echo "   Thanks for considering Plotbot!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice '$INSTALL_CHOICE'. Please enter 1, 2, or 3."
        echo ""
        continue
        ;;
    esac
    break  # Exit the loop when we get a valid choice
done
