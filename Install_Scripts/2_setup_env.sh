#!/bin/bash

echo "🔹 Creating 'plotbot_env' environment..."
conda env create -f environment.yml -y
echo "✅ Environment created!"
echo "" 
echo "Copy and paste the following command, including the period, to  register Plotbot as a Jupyter kernel: ./install_scripts/3_register_kernel.sh"
echo "" 