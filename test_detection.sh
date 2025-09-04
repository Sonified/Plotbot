#!/bin/bash

echo "🔍 Testing micromamba detection logic..."

# Source profiles like the fixed script
PROFILE_FILES=("$HOME/.zshrc" "$HOME/.bash_profile" "$HOME/.bashrc")

for profile in "${PROFILE_FILES[@]}"; do
    if [ -f "$profile" ]; then
        echo "Sourcing $profile..."
        source "$profile" 2>/dev/null || true
    fi
done

echo ""
echo "Testing individual commands:"
echo ""

echo "1. command -v micromamba:"
command -v micromamba
echo "Exit code: $?"
echo ""

echo "2. type micromamba:"
type micromamba
echo "Exit code: $?"
echo ""

echo "3. Testing the exact condition from script:"
if ! command -v micromamba &> /dev/null && ! type micromamba &> /dev/null; then
    echo "❌ CONDITION FAILED: Both commands returned non-zero"
else
    echo "✅ CONDITION PASSED: At least one command succeeded"
fi

echo ""
echo "4. Testing each part separately:"
if command -v micromamba &> /dev/null; then
    echo "✅ command -v micromamba: SUCCESS"
else
    echo "❌ command -v micromamba: FAILED"
fi

if type micromamba &> /dev/null; then
    echo "✅ type micromamba: SUCCESS"
else
    echo "❌ type micromamba: FAILED"
fi

echo ""
echo "5. Testing micromamba direct call:"
micromamba --version
echo "Exit code: $?"

