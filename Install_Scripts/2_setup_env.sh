#!/bin/bash

# Try to source conda.sh from common install locations if conda is not already available
if ! command -v conda &> /dev/null; then
    for CONDA_SH in \
        "$HOME/miniconda3/etc/profile.d/conda.sh" \
        "$HOME/anaconda3/etc/profile.d/conda.sh" \
        "/opt/anaconda3/etc/profile.d/conda.sh" \
        "/opt/miniconda3/etc/profile.d/conda.sh"
    do
        if [ -f "$CONDA_SH" ]; then
            source "$CONDA_SH"
            break
        fi
    done
fi

# If conda is still not available, try to dynamically find and source conda.sh
if ! command -v conda &> /dev/null; then
    CONDA_EXE_PATH=$(command -v conda)
    if [ -z "$CONDA_EXE_PATH" ]; then
        echo "❌ Conda not found in PATH. Please install Miniconda or Anaconda."
        exit 1
    fi

    # Get the base directory (strip /bin/conda)
    CONDA_BASE=$(dirname $(dirname "$CONDA_EXE_PATH"))
    CONDA_SH="$CONDA_BASE/etc/profile.d/conda.sh"

    if [ -f "$CONDA_SH" ]; then
        source "$CONDA_SH"
    else
        echo "❌ Could not find conda.sh at $CONDA_SH"
        exit 1
    fi
fi

# Check if conda is properly in PATH
CONDA_PATH=$(which conda)
if [[ "$CONDA_PATH" != *"conda"* ]]; then
    echo "⚠️ Warning: Conda may not be in your PATH correctly."
    echo "   Current conda path: $CONDA_PATH"
    echo "   You may need to restart your terminal after running 1_init_conda.sh"
fi

# Check if environment already exists
if conda env list | grep -q plotbot_anaconda; then
    echo "🔹 The 'plotbot_anaconda' environment already exists."
    echo ""
    echo "Choose an option:"
    echo "  1) Update existing environment with any new dependencies (keeps current setup)"
    echo "  2) Remove existing environment and create fresh installation (reinstalls everything)"
    echo "  3) Keep environment as is and exit"
    echo ""
    echo "To select an option, type the number (1, 2, or 3) and press Enter/Return."
    read -p "Enter your choice: " option
    
    case $option in
        1)
            echo "🔹 Updating 'plotbot_anaconda' environment..."
            echo "Running: conda env update -f environment.yml --name plotbot_anaconda -v"
            
            # Run the command and let it print directly to terminal
            conda env update -f environment.yml --name plotbot_anaconda -v
            update_status=$? # Capture exit status immediately
            
            # Check if the update was successful
            if [ $update_status -ne 0 ]; then
                echo "❌ Error: Environment update failed. See detailed conda output above. (Exit code: $update_status)"
                exit 1
            else
                # Simplified success message since details are printed above
                echo "✅ Environment updated successfully!"
            fi
            ;;
        2)
            echo "🔹 Removing the existing 'plotbot_anaconda' environment..."
            echo "Running: conda remove -n plotbot_anaconda --all -y"
            conda remove -n plotbot_anaconda --all -y
            remove_status=$?
            if [ $remove_status -ne 0 ]; then
                echo "❌ Error: Environment removal failed with code $remove_status."
                exit 1
            else
                echo "✅ Environment removed successfully!"
                echo "🔹 Creating a new 'plotbot_anaconda' environment..."
                echo "Running: conda env create -f environment.yml"
                conda env create -f environment.yml
                create_status=$?
                if [ $create_status -ne 0 ]; then
                    echo "❌ Error: Environment creation failed with code $create_status."
                    exit 1
                else
                    echo "✅ Environment created successfully!"
                fi
            fi
            ;;
        3)
            echo "✅ Keeping existing environment unchanged."
            echo "   You can run this script again later if you want to update."
            echo "" 
            echo "Copy and paste the following command, including the period, to register Plotbot as a Jupyter kernel: ./install_scripts/3_register_kernel.sh"
            echo ""
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Exiting without making changes."
            exit 1
            ;;
    esac
else
    echo "🔹 Creating 'plotbot_anaconda' environment..."
    echo "Running: conda env create -f environment.yml"
    conda env create -f environment.yml
    create_status=$?
    if [ $create_status -ne 0 ]; then
        echo "❌ Error: Environment creation failed with code $create_status."
        exit 1
    else
        echo "✅ Environment created successfully!"
    fi
fi

echo "" 
echo "Copy and paste the following command, including the period, to register Plotbot as a Jupyter kernel: ./install_scripts/3_register_kernel.sh"
echo ""