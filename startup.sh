#!/bin/bash
set -e
set -o pipefail

export PYTHONPATH=$PYTHONPATH:${PWD}
env_file="${PWD}/tokens.env"
if [ ! -f ${env_file} ]
then
    echo "File %{env_file} does not exist"
fi

while IFS= read -r line || [ -n "$line" ]; do
    line="${line// /}"    # Replace space with nothing
    line="${line//\"/}"   # Replace double quotes with nothing
    [ -z "$line" ] && continue # Skip empty lines
    [[ $line = \#* ]] && continue # Skip lines starting with #
    export "$line"
done < "$env_file"

PS3="Select item please: "

items=(
  "Show DB Info",
  "Show Last Modified",
  "Clear Init DB"
  "Confluence statistics"
  "Fill DB with Dummy Data"
  "Fill DB with Confluence Data"
  "Run Slack Bot",
  "Test QA Bot"
  "Store Confluence Documents to output.json")

PYTHONEXEC=venv/bin/python3

select item in "${items[@]}"
do
    case $REPLY in
        1) ${PYTHONEXEC} QAChat/VectorDB/db_cli.py INFO; break;;
        2) ${PYTHONEXEC} QAChat/VectorDB/db_cli.py INFO LastModified; break;;
        3) ${PYTHONEXEC} QAChat/VectorDB/db_cli.py CLEAR; break;;
        4) mkdir -p statistics && ${PYTHONEXEC} QAChat/Data_Processing/confluence_statistic.py; break;;
        5) ${PYTHONEXEC} QAChat/Data_Processing/main.py DUMMY; break;;
        6) ${PYTHONEXEC} QAChat/Data_Processing/main.py CONFLUENCE; break;;
        7) ${PYTHONEXEC} QAChat/Slack_Bot/qa_agent.py; break;;
        8) ${PYTHONEXEC} QAChat/QA_Bot/qa_bot.py; break;;
        9) ${PYTHONEXEC} Testing/store_documents.py CONFLUENCE; break;;
        *) echo "Ooops - unknown choice $REPLY"; break;
    esac
done

