#!/bin/bash

echo "🔹 Setting up Plotbot environment with Micromamba..."
echo ""

# Ensure micromamba is available
if ! command -v micromamba &> /dev/null; then
    echo "❌ Error: micromamba command not found."
    echo "   Please ensure micromamba is installed and your terminal is restarted."
    echo "   You may need to run: exec zsh"
    exit 1
fi

# Check if environment.cf.yml exists
if [ ! -f "environment.cf.yml" ]; then
    echo "❌ Error: environment.cf.yml not found."
    echo "   Please run 2_create_environment_cf.sh first."
    exit 1
fi

echo "✅ Micromamba version: $(micromamba --version)"
echo "📄 Using environment file: environment.cf.yml"
echo ""

# Check if environment already exists
if micromamba env list | grep -q "plotbot_env"; then
    echo "⚠️  Environment 'plotbot_env' already exists."
    echo ""
    echo "What would you like to do?"
    echo "1) Update the existing environment (recommended)"
    echo "2) Remove and recreate the environment"
    echo "3) Keep existing environment unchanged"
    echo ""
    read -p "Enter your choice (1-3): " -r choice
    echo ""
    
    case $choice in
        1)
            echo "🔹 Updating the existing 'plotbot_env' environment..."
            echo "Running: micromamba env update -n plotbot_env -f environment.cf.yml"
            micromamba env update -n plotbot_env -f environment.cf.yml --yes \
                --no-rc --override-channels -c conda-forge --channel-priority strict
            update_status=$?
            if [ $update_status -ne 0 ]; then
                echo "❌ Error: Environment update failed with code $update_status."
                exit 1
            else
                echo "✅ Environment updated successfully!"
            fi
            ;;
        2)
            echo "🔹 Removing the existing 'plotbot_env' environment..."
            echo "Running: micromamba env remove -n plotbot_env"
            micromamba env remove -n plotbot_env --yes
            remove_status=$?
            if [ $remove_status -ne 0 ]; then
                echo "❌ Error: Environment removal failed with code $remove_status."
                exit 1
            else
                echo "✅ Environment removed successfully!"
                echo "🔹 Creating a new 'plotbot_env' environment..."
                echo "Running: micromamba create -n plotbot_env -f environment.cf.yml"
                micromamba create -n plotbot_env -f environment.cf.yml --yes \
                    --no-rc --override-channels -c conda-forge --channel-priority strict
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
            echo "Next step: Run ./install_scripts/4_register_kernel_micromamba.sh"
            echo ""
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Exiting without making changes."
            exit 1
            ;;
    esac
else
    echo "🔹 Creating 'plotbot_env' environment with micromamba..."
    echo "Running: micromamba create -n plotbot_env -f environment.cf.yml"
    echo ""
    echo "This may take several minutes as packages are downloaded and installed..."
    echo ""
    
    micromamba create -n plotbot_env -f environment.cf.yml --yes \
        --no-rc --override-channels -c conda-forge --channel-priority strict
    create_status=$?
    
    if [ $create_status -ne 0 ]; then
        echo "❌ Error: Environment creation failed with code $create_status."
        echo ""
        echo "Common issues and solutions:"
        echo "1. Network connectivity - check internet connection"
        echo "2. Disk space - ensure sufficient space available"
        echo "3. Channel access - ensure conda-forge is accessible"
        echo ""
        exit 1
    else
        echo "✅ Environment created successfully!"
    fi
fi

# Verify the environment was created
echo ""
echo "🔍 Verifying environment..."
if micromamba env list | grep -q "plotbot_env"; then
    echo "✅ plotbot_env environment is available"
    
    # Show environment location
    ENV_PATH=$(micromamba env list | grep plotbot_env | awk '{print $2}')
    echo "📍 Environment location: $ENV_PATH"
else
    echo "❌ Error: plotbot_env environment was not created properly"
    exit 1
fi

echo ""
echo "🎉 Environment setup completed successfully!"
echo ""
echo "Next step: Run ./install_scripts/4_register_kernel_micromamba.sh"
echo ""
