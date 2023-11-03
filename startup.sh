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

PYTHONEXEC=venv/bin/python3
if [ ! -f "$PYTHONEXEC" ]; then
    PYTHONEXEC=python3
fi

PS3="Select item please: "

function DBFunctions {
    items=(
        "Show DB Info",
        "Show Last Modified",
        "Show Embeddings",
        "Clear Init DB"
    )

    select item in "${items[@]}"
    do
        case $REPLY in
            1) ${PYTHONEXEC} QAChat/VectorDB/db_cli.py INFO; break;;
            2) ${PYTHONEXEC} QAChat/VectorDB/db_cli.py INFO LastModified; break;;
            3) ${PYTHONEXEC} QAChat/VectorDB/db_cli.py INFO Embeddings; break;;
            4) ${PYTHONEXEC} QAChat/VectorDB/db_cli.py CLEAR; ${PYTHONEXEC} QAChat/VectorDB/db_cli.py INIT; break;;
            *) echo "Ooops - unknown choice $REPLY"; break;
        esac
    done
}

function TestFunctions {
    items=(
        "List All Confluence Spaces"
        "Confluence statistics"
        "Fetch Confluence Documents and write to stdout"
        "Store Confluence Documents to json and txt files"
    )

    select item in "${items[@]}"
    do
        case $REPLY in
            1) ${PYTHONEXEC} Testing/list_all_spaces.py; break;;
            2) mkdir -p statistics && ${PYTHONEXEC} Testing/confluence_statistic.py; break;;
            3) ${PYTHONEXEC} QAChat/Fetcher/confluence_fetcher.py; break;;
            4) ${PYTHONEXEC} Testing/store_documents.py CONFLUENCE; break;;
            *) echo "Ooops - unknown choice $REPLY"; break;
        esac
    done
}

function FetchFunctions {
    items=(
        "Fetch Confluence Documents"
        "Fetch Dummy Documents"
    )

    select item in "${items[@]}"
    do
        case $REPLY in
            1) ${PYTHONEXEC} QAChat/Fetcher/main.py CONFLUENCE; break;;
            2) ${PYTHONEXEC} QAChat/Fetcher/main.py DUMMY; break;;
            *) echo "Ooops - unknown choice $REPLY"; break;
        esac
    done
}

items=(
  "Database Maintenance"
  "Tests"
  "Fetchers"
  "Fill DB with Dummy Data"
  "Fill DB with Confluence Data"
  "Run Slack Bot",
  "Run QA Bot")

select item in "${items[@]}"
do
    case $REPLY in
        1) DBFunctions; break;;
        2) TestFunctions; break;;
        3) FetchFunctions; break;;
        3) ${PYTHONEXEC} QAChat/Data_Processing/main.py DUMMY; break;;
        4) ${PYTHONEXEC} QAChat/Data_Processing/main.py CONFLUENCE; break;;
        5) ${PYTHONEXEC} QAChat/Slack_Bot/qa_agent.py; break;;
        6) ${PYTHONEXEC} QAChat/QA_Bot/qa_bot.py; break;;
        *) echo "Ooops - unknown choice $REPLY"; break;
    esac
done


