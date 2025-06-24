#!/bin/bash
# PSP Data Migration Script
set -e

echo "🚀 Starting PSP data migration from psp_data/ to data/psp/"

# Create data/psp if it doesn't exist
mkdir -p data/psp

# Use rsync to merge directories (safer than mv)
# -a: archive mode (preserves permissions, timestamps)
# -v: verbose
# -u: update (skip files that are newer in destination)
rsync -avu psp_data/ data/psp/

echo "✅ Migration complete!"
echo "📊 Checking results..."
echo "Files now in data/psp:"
find data/psp -name "*.cdf" | wc -l
find data/psp -name "*.csv" | wc -l
echo "CDF files"
echo "CSV files"

echo "🎯 Hamstrings data:"
ls -la data/psp/Hamstrings/ 2>/dev/null || echo "Hamstrings not found - check migration"

echo "💡 Original psp_data/ is preserved as backup"

