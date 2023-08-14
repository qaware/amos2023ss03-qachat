#!/bin/bash
export PYTHONPATH=$PYTHONPATH:${PWD}
env_file="${PWD}/tokens.env"
while IFS= read -r line || [ -n "$line" ]; do
    line="${line// /}"    # Replace space with nothing
    line="${line//\"/}"   # Replace double quotes with nothing
    [ -z "$line" ] && continue # Skip empty lines
    export "$line"
done < "$env_file"

venv/bin/python3 ${PWD}/QAChat/Data_Processing/confluence_statistic.py

# NOTE: This script opens a extra window to display the charts. To see the the next chart, close the current window.