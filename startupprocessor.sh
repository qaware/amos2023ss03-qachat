#!/bin/bash
export PYTHONPATH=$PYTHONPATH:${PWD}
env_file="${PWD}/tokens.env"
while IFS= read -r line || [ -n "$line" ]; do
    line="${line// /}"    # Replace space with nothing
    line="${line//\"/}"   # Replace double quotes with nothing
    [ -z "$line" ] && continue # Skip empty lines
    export "$line"
done < "$env_file"

#venv/bin/python3 ${PWD}/Testing/db_integration_test.py
#venv/bin/python3 ${PWD}/QAChat/Data_Processing/main.py DUMMY

venv/bin/python3 ${PWD}/QAChat/Common/db_info.py LastModified
venv/bin/python3 ${PWD}/QAChat/Common/db_info.py LoadedChannels
venv/bin/python3 ${PWD}/QAChat/Common/db_info.py Embeddings


