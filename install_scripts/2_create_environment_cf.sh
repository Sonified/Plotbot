#!/bin/bash

echo "🔹 Creating conda-forge-only environment file..."
echo ""

# Check if environment.yml exists
if [ ! -f "environment.yml" ]; then
    echo "❌ Error: environment.yml not found in current directory."
    echo "   Please run this script from the Plotbot root directory."
    exit 1
fi

# Create environment.cf.yml from environment.yml
# This AWK script removes Anaconda defaults and ensures only conda-forge is used
awk '
BEGIN{inchan=0}
/^channels:/ {print "channels:\n  - conda-forge"; inchan=1; next}
inchan && /^ *-/ { next }
inchan && $0 !~ /^ *-/ { inchan=0 }
/https?:\/\/repo\.anaconda\.com/ { next }
{ gsub(/defaults::/,"") }
$1 ~ /^- *anaconda($|[^A-Za-z0-9_-])/ { next }
{ print }
' environment.yml > environment.cf.yml

# Verify the file was created successfully
if [ ! -f "environment.cf.yml" ]; then
    echo "❌ Error: Failed to create environment.cf.yml"
    exit 1
fi

# Check that the file starts with the correct channels section
if ! grep -q "^channels:" environment.cf.yml || ! grep -q "conda-forge" environment.cf.yml; then
    echo "❌ Error: environment.cf.yml does not have the correct channels configuration."
    echo "   Expected to start with:"
    echo "   channels:"
    echo "     - conda-forge"
    exit 1
fi

echo "✅ Created environment.cf.yml successfully!"
echo ""
echo "📄 Differences from original environment.yml:"
echo "   - Channels limited to conda-forge only"
echo "   - Removed any anaconda defaults references"
echo "   - Removed any direct anaconda.com repository URLs"
echo ""

# Show the channels section for verification
echo "🔍 Channels configuration:"
sed -n '/^channels:/,/^[^ ]/p' environment.cf.yml | sed '$d'

echo ""
echo "✅ Environment file ready for micromamba installation!"
echo ""
