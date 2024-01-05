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

# create virtual env via "python3 -m venv venv"
if [ -f "venv/bin/python3" ]; then
    echo "Found venv. Activating..."
    source venv/bin/activate
fi

PYTHONEXEC=python3

PS3="Select item please: "

function DBFunctions {
    items=(
        "Show DB Info",
        "Clear Init DB (Dangerous)"
        "Show Last Modified",
        "Show Embeddings",
        "Show Documents",
    )

    select item in "${items[@]}"
    do
        case $REPLY in
            1) ${PYTHONEXEC} QAChat/VectorDB/db_cli.py INFO; break;;
            2)
                read -p "Are you sure? " -n 1 -r
                echo    # (optional) move to a new line
                if [[ ! $REPLY =~ ^[Yy]$ ]]
                then
                    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
                fi
                ${PYTHONEXEC} QAChat/VectorDB/db_cli.py CLEAR; ${PYTHONEXEC} QAChat/VectorDB/db_cli.py INIT; break;;
            3) ${PYTHONEXEC} QAChat/VectorDB/db_cli.py INFO LastModified; break;;
            4) ${PYTHONEXEC} QAChat/VectorDB/db_cli.py INFO Embeddings; break;;
            5) ${PYTHONEXEC} QAChat/VectorDB/db_cli.py INFO Documents; break;;
            *) echo "Ooops - unknown choice $REPLY"; break;
        esac
    done
}

function TestFunctions {
    items=(
        "List All Confluence Spaces"
        "Confluence statistics"
        "Fetch Confluence Documents and write to stdout"
        "Fetch Confluence Documents to json and txt files"
        "Language Detection Test"
        "DeepL Translation Test"
    )

    select item in "${items[@]}"
    do
        case $REPLY in
            1) ${PYTHONEXEC} Testing/list_all_confluence_spaces.py; break;;
            2) mkdir -p statistics && ${PYTHONEXEC} Testing/confluence_statistic.py; break;;
            3) ${PYTHONEXEC} QAChat/Fetcher/Confluence/confluence_fetcher.py; break;;
            4) ${PYTHONEXEC} Testing/store_documents.py CONFLUENCE; break;;
            5) ${PYTHONEXEC} QAChat/Common/langdetector.py; break;;
            6) ${PYTHONEXEC} QAChat/Common/deepL_translator.py; break;;
            *) echo "Ooops - unknown choice $REPLY"; break;
        esac
    done
}

function ExperimentFunctions {
    items=(
        "llamaindex Confluence Indexer"
        "llamaindex Q/A"
        "llamaindex Chat"
        "llamaindex Slack Bot"
    )

    select item in "${items[@]}"
    do
        case $REPLY in
            1) ${PYTHONEXEC} Testing/Experiments/llamaindex/confluenceIndexer.py; break;;
            2) ${PYTHONEXEC} Testing/Experiments/llamaindex/qa.py; break;;
            3) ${PYTHONEXEC} Testing/Experiments/llamaindex/chat.py; break;;
            4) ${PYTHONEXEC} Testing/Experiments/llamaindex/slack.py; break;;
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

function SetupFunctions {
    items=(
        "Setup python"
    )

    select item in "${items[@]}"
    do
        case $REPLY in
            1)
              sudo apt update
              sudo apt install gcc g++ cmake python3.10-venv
              mkdir -p venv
              python3 -m venv venv
              source venv/bin/activate
              pip install -r requirements.txt
              ${PYTHONEXEC} -m spacy download xx_ent_wiki_sm
              ${PYTHONEXEC} QAChat/Processors/setup.py
              break;;
            *) echo "Ooops - unknown choice $REPLY"; break;
        esac
    done
}


items=(
  "Database Maintenance"
  "Setup"
  "Tests"
  "Experiments"
  "Fetchers"
  "Embed fetched documents"
  "Run Slack Bot"
  "Run QA Bot")

select item in "${items[@]}"
do
    case $REPLY in
        1) DBFunctions; break;;
        2) SetupFunctions; break;;
        3) TestFunctions; break;;
        4) ExperimentFunctions; break;;
        5) FetchFunctions; break;;
        6) ${PYTHONEXEC} QAChat/Processors/main.py; break;;
        7) ${PYTHONEXEC} QAChat/Slack_Bot/qa_agent.py; break;;
        8) ${PYTHONEXEC} QAChat/QA_Bot/qa_bot.py; break;;
        *) echo "Ooops - unknown choice $REPLY"; break;
    esac
done


