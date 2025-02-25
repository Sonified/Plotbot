#!/bin/bash

echo "🔹 Creating and activating 'plotbot_env' environment..."
conda env create -f install_scripts/environment.yml -y
conda activate plotbot_env
echo "✅ Environment created and activated!"