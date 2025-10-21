#!/bin/bash

# Change to the directory where the venv is located (adjust if needed)
VENV_DIR="./venv"  # Assuming virtual environment is in a 'venv' directory in the current folder

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Run the Python script with example arguments
# Adjust the arguments as needed for your use case
python openrouter_helper.py --user-prompt "What are the main differences between Python and JavaScript?" --csv "test_prompts.csv" --ability-csv "champion_abilities.csv"