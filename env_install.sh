#!/bin/bash

# Stop the script on any error
set -e

# Check for Conda installation and initialize Conda in script
if [ -z "$(which conda)" ]; then
    echo "Conda is not installed or not in the PATH"
    exit 1
fi

# Store the path of the Conda interpreter
CONDA_INTERPRETER_PATH=$(which python)

# Generate the generation.config.js file for PM2 with specified configurations
cat <<EOF > receiver.config.js
module.exports = {
  apps : [{
    name: 'prompts_receiver',
    script: 'serve.py',
    interpreter: '${CONDA_INTERPRETER_PATH}',
    args: '--port 8093'
  }]
};
EOF

echo -e "\n\n[INFO] receiver.config.js generated for PM2."

conda env create -f environment.yml
conda activate three-gen-prompt-receiver
conda info --env

conda install pnpm
pnpm install pm2 -g
pnpm fund
