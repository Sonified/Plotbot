#!/bin/bash
# Test comment to check Cursor UI behavior

echo "🔹 Setting up Plotbot environment with Micromamba..."
echo ""

# Add homebrew to PATH if not already there
export PATH="$HOME/homebrew/bin:$PATH"

# Set up micromamba environment variables using Homebrew's location
export MAMBA_EXE="$(brew --prefix micromamba)/bin/micromamba"
export MAMBA_ROOT_PREFIX="$HOME/micromamba"

# Initialize micromamba shell hook for bash
__mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX" 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__mamba_setup"
else
    # Enhanced fallback - create a function that mimics micromamba behavior
    micromamba() {
        "$MAMBA_EXE" "$@"
    }
    export -f micromamba
fi

# Ensure micromamba is available - try direct path if command fails
if ! command -v micromamba &> /dev/null; then
    # Try using the direct path
    if [ -f "$MAMBA_EXE" ]; then
        echo "⚠️  Using direct path to micromamba: $MAMBA_EXE"
        micromamba() {
            "$MAMBA_EXE" "$@"
        }
        export -f micromamba
    else
        echo "❌ Error: micromamba command not found."
        echo "   Please ensure micromamba is installed and your terminal is restarted."
        echo "   You may need to run: exec zsh"
        exit 1
    fi
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

# Check if environment already exists in micromamba
if micromamba env list | grep -q "plotbot_micromamba" && [ -d "$MAMBA_ROOT_PREFIX/envs/plotbot_micromamba" ]; then
    echo "⚠️  Environment 'plotbot_micromamba' already exists."
    echo ""
    echo "What would you like to do?"
    echo "1) Update the existing environment (recommended)"
    echo "2) Remove and recreate the environment"
    echo "3) Keep existing environment unchanged"
    echo ""
    
    # Loop until we get a valid choice
    while true; do
        read -p "Enter your choice (1-3): " -r choice
        echo ""
        
        case $choice in
        1)
            echo "🔹 Updating the existing 'plotbot_micromamba' environment..."
            echo "Running: micromamba env update -n plotbot_micromamba -f environment.cf.yml"
            micromamba env update -n plotbot_micromamba -f environment.cf.yml --yes --no-rc --override-channels -c conda-forge --channel-priority strict
            update_status=$?
            if [ $update_status -ne 0 ]; then
                echo "❌ Error: Environment update failed with code $update_status."
                exit 1
            else
                echo "✅ Environment updated successfully!"
            fi
            ;;
        2)
            echo "🔹 Removing the existing 'plotbot_micromamba' environment..."
            echo "Running: micromamba env remove -n plotbot_micromamba"
            micromamba env remove -n plotbot_micromamba --yes
            remove_status=$?
            if [ $remove_status -ne 0 ]; then
                echo "❌ Error: Environment removal failed with code $remove_status."
                exit 1
            else
                echo "✅ Environment removed successfully!"
                echo "🔹 Creating a new 'plotbot_micromamba' environment..."
                echo "Running: micromamba create -n plotbot_micromamba -f environment.cf.yml --no-rc --override-channels -c conda-forge"
                micromamba create -n plotbot_micromamba -f environment.cf.yml --yes --no-rc --override-channels -c conda-forge --channel-priority strict
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
            exit 0
            ;;
        *)
            echo "❌ Invalid choice '$choice'. Please enter 1, 2, or 3."
            echo ""
            continue
            ;;
        esac
        break  # Exit the loop when we get a valid choice
    done
else
    echo "🔹 Creating 'plotbot_micromamba' environment with micromamba..."
    echo "Running: micromamba create -n plotbot_micromamba -f environment.cf.yml --no-rc --override-channels -c conda-forge"
    echo ""
    echo "This may take several minutes as packages are downloaded and installed..."
    echo ""
    
    micromamba create -n plotbot_micromamba -f environment.cf.yml --yes --no-rc --override-channels -c conda-forge --channel-priority strict
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
if micromamba env list | grep -q "plotbot_micromamba"; then
    echo "✅ plotbot_micromamba environment is available"
    
    # Show environment location
    ENV_PATH=$(micromamba env list | grep plotbot_micromamba | awk '{print $2}')
    echo "📍 Environment location: $ENV_PATH"
else
    echo "❌ Error: plotbot_micromamba environment was not created properly"
    exit 1
fi

echo ""
echo "🎉 Environment setup completed successfully!"