#!/bin/bash

# Check if conda is properly in PATH
CONDA_PATH=$(which conda)
if [[ "$CONDA_PATH" != *"conda"* ]]; then
    echo "⚠️ Warning: Conda may not be in your PATH correctly."
    echo "   Current conda path: $CONDA_PATH"
    echo "   You may need to restart your terminal after running 1_init_conda.sh"
fi

# Check if environment already exists
if conda env list | grep -q plotbot_env; then
    echo "🔹 The 'plotbot_env' environment already exists."
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
            echo "🔹 Updating 'plotbot_env' environment..."
            echo "Running: conda env update -f environment.yml --name plotbot_env"
            
            # Capture output to check if changes were made
            update_output=$(conda env update -f environment.yml --name plotbot_env 2>&1)
            update_status=$?
            
            # Check if the update was successful
            if [ $update_status -ne 0 ]; then
                echo "❌ Error: Environment update failed with code $update_status."
                exit 1
            else
                # Display the output so user can see what happened
                echo "$update_output"
                
                # Check if "Requirement already satisfied" appears for all packages
                if [[ "$update_output" == *"Requirement already satisfied"* ]] && ! [[ "$update_output" == *"Collecting "* ]]; then
                    echo "✅ Environment checked - all packages are already up to date!"
                else
                    echo "✅ Environment updated successfully with new packages!"
                fi
            fi
            ;;
        2)
            echo "🔹 Removing the existing 'plotbot_env' environment..."
            echo "Running: conda remove -n plotbot_env --all -y"
            conda remove -n plotbot_env --all -y
            remove_status=$?
            if [ $remove_status -ne 0 ]; then
                echo "❌ Error: Environment removal failed with code $remove_status."
                exit 1
            else
                echo "✅ Environment removed successfully!"
                echo "🔹 Creating a new 'plotbot_env' environment..."
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
    echo "🔹 Creating 'plotbot_env' environment..."
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