#!/bin/bash

echo "🔹 Checking if Conda is installed..."
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Anaconda or Miniconda first!"
    exit 1
fi

echo "🔹 Checking if the 'plotbot_env' environment exists..."
if conda env list | grep -q "plotbot_env"; then
    echo "✅ 'plotbot_env' already exists. Activating it..."
else
    echo "🔹 Creating the 'plotbot_env' environment..."
    conda env create -f environment.yml
fi

echo "🔹 Activating 'plotbot_env'..."
source /opt/anaconda3/etc/profile.d/conda.sh  # Ensures Conda is sourced
conda activate plotbot_env
echo "✅ Environment activated!"

echo "🔹 Now run: ./3_register_kernel.sh"