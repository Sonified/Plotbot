#!/bin/bash

echo "🚀 Welcome to Plotbot Installation"
echo "===================================="
echo ""
echo "Plotbot is a space physics data visualization, audification, and analysis tool"
echo "for multiple spacecraft, currently featuring Parker Solar Probe and WIND."
echo ""
echo "Please select your installation method:"
echo ""
echo "1) Standard Installation (Recommended for most users)"
echo "   - Uses conda/miniconda via Homebrew"
echo "   - Full access to all conda channels"
echo "   - Best for personal computers and standard environments"
echo ""
echo "2) Micromamba Installation (For restricted environments)"
echo "   - Uses micromamba with conda-forge only"
echo "   - No Anaconda defaults or proprietary channels"
echo "   - Recommended for government systems (NASA, etc.)"
echo "   - No sudo required, installs in user directory"
echo ""
echo "Enter your choice (1 or 2): "
read -r INSTALL_CHOICE

case $INSTALL_CHOICE in
    1)
        echo ""
        echo "🔹 You selected: Standard Installation"
        echo "   This will use the existing conda-based installation process."
        echo ""
        echo "Starting standard installation..."
        exec ./install_scripts/install_standard.sh
        ;;
    2)
        echo ""
        echo "🔹 You selected: Micromamba Installation"
        echo "   This will use micromamba with conda-forge only."
        echo "   Perfect for government systems and restricted environments."
        echo ""
        echo "Starting micromamba installation..."
        exec ./install_scripts/install_micromamba.sh
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run the installer again and select 1 or 2."
        exit 1
        ;;
esac
