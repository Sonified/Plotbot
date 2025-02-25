#!/bin/bash

echo "🔹 Creating 'plotbot_env' environment..."
conda env create -f environment.yml -y
echo "✅ Environment created! Activate with: conda activate plotbot_env"