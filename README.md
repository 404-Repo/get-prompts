# Prompts Receiving Server
#### *Questions* can be addressed to Maxim Bladyko

### Project description
This server-based tool serves as a client for giving away the prompts that it received from outside, e.g. 
from another process or server that constantly generates prompts.

### Requirements
Packages:
- miniconda3
- python 3.10

### Installation

The packages to run this implementation on a PC can be installed as follows:
```commandline
bash env_install.sh
conda activate three-gen-prompt-receiver
pnpm setup
pnpm install pm2
```
The script will create a conda environment with all packages being installed within it.
The script will also create **receiver.config.js** file that can be used for running the 
server as a separate process.

You can uninstall conda environment and delete generated files using the following script:
```commandline
bash env_uninstall.sh
```

You can also install project using provided **pyproject.toml** file:
```commandline
python install -e .
```

### Running server
To run the server as a separate process you will need to do the following:
```commandline
pm2 start receiver.config.js
```