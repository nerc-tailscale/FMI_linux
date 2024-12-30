#!/bin/bash

#Define paths
VENV_DIR="/home/nerc/virtualEnvs/solcast"
PYTHON_SCRIPT="/home/nerc/Documents/solcast/FMI_linux/main.py"

source "$VENV_DIR/bin/activate"

python "$PYTHON_SCRIPT"

deactivate
