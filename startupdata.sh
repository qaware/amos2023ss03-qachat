#!/bin/bash
export PYTHONPATH=$PYTHONPATH:${PWD}
env_file="${PWD}/tokens.env"
while IFS= read -r line || [ -n "$line" ]; do
    line="${line// /}"    # Replace space with nothing
    line="${line//\"/}"   # Replace double quotes with nothing
    [ -z "$line" ] && continue # Skip empty lines
    export "$line"
done < "$env_file"

venv/bin/python3 ${PWD}/QAChat/Data_Processing/main.py DUMMY

# Initialize the data for the database if it is not already initialized

