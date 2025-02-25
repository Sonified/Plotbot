#!/bin/bash

echo "🔹 Registering 'plotbot_env' with Jupyter..."
python -m ipykernel install --user --name=plotbot_env --display-name "Python (Plotbot)"

echo "✅ Jupyter kernel registered! Restart VS Code, open the notebook, and select 'Python (Plotbot)' in the kernel dropdown."