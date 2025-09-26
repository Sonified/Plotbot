#!/bin/bash

echo "🔍 DEBUG: Detailed micromamba detection analysis"
echo "=============================================="

# Set up micromamba environment variables using Homebrew's location
export MAMBA_EXE="$(brew --prefix micromamba)/bin/micromamba"
export MAMBA_ROOT_PREFIX="$HOME/micromamba"

echo "1. Environment Variables:"
echo "   MAMBA_EXE: $MAMBA_EXE"
echo "   MAMBA_ROOT_PREFIX: $MAMBA_ROOT_PREFIX"
echo ""

echo "2. Binary Check:"
if [ -f "$MAMBA_EXE" ]; then
    echo "   ✅ Binary exists at: $MAMBA_EXE"
    echo "   Binary info: $(ls -la "$MAMBA_EXE")"
else
    echo "   ❌ Binary NOT found at: $MAMBA_EXE"
    exit 1
fi
echo ""

echo "3. Before Shell Hook - Detection Tests:"
echo "   command -v micromamba: $(command -v micromamba 2>/dev/null || echo "FAILED")"
echo "   type micromamba: $(type micromamba 2>/dev/null || echo "FAILED")"
echo "   which micromamba: $(which micromamba 2>/dev/null || echo "FAILED")"
echo ""

echo "4. Running Shell Hook:"
echo "   Command: \"$MAMBA_EXE\" shell hook --shell bash --root-prefix \"$MAMBA_ROOT_PREFIX\""
__mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX" 2> /dev/null)"
hook_exit_code=$?
echo "   Hook exit code: $hook_exit_code"
echo "   Hook output length: ${#__mamba_setup} characters"
echo ""

if [ $hook_exit_code -eq 0 ]; then
    echo "5. Evaluating Shell Hook:"
    echo "   Running: eval \"\$__mamba_setup\""
    eval "$__mamba_setup"
    eval_exit_code=$?
    echo "   Eval exit code: $eval_exit_code"
    echo ""
    
    echo "6. After Shell Hook - Detection Tests:"
    echo "   command -v micromamba: $(command -v micromamba 2>/dev/null || echo "FAILED")"
    echo "   type micromamba: $(type micromamba 2>/dev/null || echo "FAILED")" 
    echo "   which micromamba: $(which micromamba 2>/dev/null || echo "FAILED")"
    echo ""
    
    echo "7. Function Analysis:"
    if declare -f micromamba >/dev/null 2>&1; then
        echo "   ✅ micromamba function is defined"
        echo "   Function type: $(type -t micromamba 2>/dev/null || echo "UNKNOWN")"
    else
        echo "   ❌ micromamba function is NOT defined"
    fi
    echo ""
    
    echo "8. Testing micromamba command:"
    if micromamba --version >/dev/null 2>&1; then
        echo "   ✅ micromamba --version works: $(micromamba --version)"
    else
        echo "   ❌ micromamba --version failed"
    fi
    echo ""
    
else
    echo "5. Shell Hook Failed - Using Fallback:"
    alias micromamba="$MAMBA_EXE"
    echo "   Set alias: micromamba=\"$MAMBA_EXE\""
    echo ""
    
    echo "6. After Alias - Detection Tests:"
    echo "   command -v micromamba: $(command -v micromamba 2>/dev/null || echo "FAILED")"
    echo "   type micromamba: $(type micromamba 2>/dev/null || echo "FAILED")"
    echo "   which micromamba: $(which micromamba 2>/dev/null || echo "FAILED")"
    echo ""
fi

echo "9. Final Combined Detection Logic (from original script):"
if ! command -v micromamba &> /dev/null && ! type micromamba &> /dev/null; then
    echo "   ❌ DETECTION FAILED: Both command -v and type failed"
    echo "   This is why the original script fails"
else
    echo "   ✅ DETECTION SUCCESS: At least one method worked"
fi

echo ""
echo "🔍 DEBUG: Analysis complete"