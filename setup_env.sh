#!/bin/bash

# Stop the script on any error
set -e

# Check for Conda installation and initialize Conda in script
if [ -z "$(which conda)" ]; then
    echo "Conda is not installed or not in the PATH"
    exit 1
fi

# Attempt to find Conda's base directory and source it (required for `conda activate`)
CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"

conda env create -f conda_env.yml
conda activate three-gen-get-prompts
conda info --env

# Store the path of the Conda interpreter
CONDA_INTERPRETER_PATH=$(which python)

# Generate the generation.config.js file for PM2 with specified configurations
cat <<EOF > three-gen-get-prompts.config.js
module.exports = {
  apps : [{
    name: 'three-gen-get-prompts',
    script: 'serve.py',
    interpreter: '${CONDA_INTERPRETER_PATH}',
  }]
};
EOF

echo -e "[INFO] three-gen-get-prompts.config.js was generated for PM2."
echo -e "[INFO] Start initialization of the conda environment."
