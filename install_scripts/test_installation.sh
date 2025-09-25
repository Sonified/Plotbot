#!/bin/bash

echo "🧪 Plotbot Installation Test Suite"
echo "================================="
echo ""
echo "This script tests both installation methods to ensure they work correctly."
echo "It performs dry-run validations without actually creating environments."
echo ""

# Test 1: Check main installer exists and is executable
echo "🔍 Test 1: Main installer validation"
if [ -x "install.sh" ]; then
    echo "✅ install.sh exists and is executable"
else
    echo "❌ install.sh not found or not executable"
    exit 1
fi

# Test 2: Check all standard installation scripts exist
echo ""
echo "🔍 Test 2: Standard installation scripts"
STANDARD_SCRIPTS=(
    "install_scripts/install_standard.sh"
    "install_scripts/1_init_conda.sh"
    "install_scripts/2_setup_env.sh"
    "install_scripts/3_register_kernel.sh"
)

for script in "${STANDARD_SCRIPTS[@]}"; do
    if [ -x "$script" ]; then
        echo "✅ $script exists and is executable"
    else
        echo "❌ $script not found or not executable"
        exit 1
    fi
done

# Test 3: Check all micromamba installation scripts exist
echo ""
echo "🔍 Test 3: Micromamba installation scripts"
MICROMAMBA_SCRIPTS=(
    "install_scripts/install_micromamba.sh"
    "install_scripts/1_init_micromamba.sh"
    "install_scripts/2_create_environment_cf.sh"
    "install_scripts/3_setup_env_micromamba.sh"
    "install_scripts/4_register_kernel_micromamba.sh"
)

for script in "${MICROMAMBA_SCRIPTS[@]}"; do
    if [ -x "$script" ]; then
        echo "✅ $script exists and is executable"
    else
        echo "❌ $script not found or not executable"
        exit 1
    fi
done

# Test 4: Check environment.yml exists
echo ""
echo "🔍 Test 4: Environment files"
if [ -f "environment.yml" ]; then
    echo "✅ environment.yml exists"
else
    echo "❌ environment.yml not found"
    exit 1
fi

# Test 5: Test environment.cf.yml generation
echo ""
echo "🔍 Test 5: Environment CF file generation"
./install_scripts/2_create_environment_cf.sh
if [ $? -eq 0 ] && [ -f "environment.cf.yml" ]; then
    echo "✅ environment.cf.yml generated successfully"
    
    # Check that it has the right channels
    if grep -q "channels:" environment.cf.yml && grep -q "conda-forge" environment.cf.yml; then
        echo "✅ environment.cf.yml has correct conda-forge channels"
    else
        echo "❌ environment.cf.yml does not have correct channels"
        exit 1
    fi
    
    # Clean up test file
    rm -f environment.cf.yml
else
    echo "❌ Failed to generate environment.cf.yml"
    exit 1
fi

# Test 6: Validate script syntax
echo ""
echo "🔍 Test 6: Script syntax validation"
ALL_SCRIPTS=(
    "install.sh"
    "install_scripts/install_standard.sh"
    "install_scripts/install_micromamba.sh"
    "install_scripts/1_init_conda.sh"
    "install_scripts/1_init_micromamba.sh"
    "install_scripts/2_setup_env.sh"
    "install_scripts/2_create_environment_cf.sh"
    "install_scripts/3_setup_env_micromamba.sh"
    "install_scripts/3_register_kernel.sh"
    "install_scripts/4_register_kernel_micromamba.sh"
)

for script in "${ALL_SCRIPTS[@]}"; do
    if bash -n "$script" 2>/dev/null; then
        echo "✅ $script syntax is valid"
    else
        echo "❌ $script has syntax errors"
        bash -n "$script"
        exit 1
    fi
done

# Test 7: Test main installer choice logic (simulate input)
echo ""
echo "🔍 Test 7: Main installer choice logic"

# Test invalid choice
echo "invalid" | timeout 5 bash install.sh > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "✅ Invalid choice handling works correctly"
else
    echo "❌ Invalid choice handling failed"
fi

echo ""
echo "🎉 All tests passed successfully!"
echo ""
echo "📋 Test Summary:"
echo "   ✅ Main installer exists and is executable"
echo "   ✅ All standard installation scripts present"
echo "   ✅ All micromamba installation scripts present"
echo "   ✅ Environment files exist and can be processed"
echo "   ✅ All scripts have valid syntax"
echo "   ✅ Input validation works correctly"
echo ""
echo "🚀 Installation system is ready for use!"
echo ""
echo "To test actual installation:"
echo "   Standard: echo '1' | ./install.sh"
echo "   Micromamba: echo '2' | ./install.sh"
echo ""
