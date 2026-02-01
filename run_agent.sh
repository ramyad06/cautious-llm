#!/bin/bash
# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Use the virtual environment's python to run the agent
./.venv/bin/python3 agent.py "$@"