# Local Build Documentation

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.8](https://www.python.org/downloads/release/python-380/)

## Installation

### 1. Clone the repository

```` bash
git clone https://github.com/amosproj/amos2023ss03-qachat
````

### 2. Set Python Path:

Go to the cloned repository and there set the Python-Path. This will look something like:

**Windows:**

```` bash
$env:PYTHONPATH += "PATH_TO_THE_REPOSITORY"
````

**Unix:**

```` bash
export PYTHONPATH=$PYTHONPATH:PATH_TO_THE_REPOSITORY
````

### 3. Create python environment, activate it & load required dependencies

First create the Virtual Python Enviroment:

**Windows:**

```` bash
python.exe -m venv venv
````

**Unix:**

```` bash
python -m venv venv
````

***
After this activate it with:

**Windows:**

```` bash
.\venv\Scripts\activate
````

**Unix:**

```` bash
./venv/bin/activate
````

***
Now you activated the environment and need to download the required dependencies:
Go in the "QAChat\Data_Processing" folder and run the following command:
**Windows:**

```` bash
pip install -r .\requirements.txt
````

**Unix:**

```` bash
pip install -r ./requirements.txt
````

Repeat the same process for the "QAChat\QA_Bot" and "QAChat\Slack_Bot" folders.

When running the DataProcessing there can be a problem, that it can not find the needed spacy packages. It will be
something like can not find package de_name_name_sm. To fix this download the needed models. Therefore, after installing
the requirements run the following commands:

```` bash
python -m spacy download xx_ent_wiki_sm
python -m spacy download de_core_news_sm
````

### 4. Install Docker

Go to the [Docker Website](https://docs.docker.com/engine/install/) and follow the instructions to install Docker.

### 5. Add the tokens to the project

Create a file called "tokens.env" in the root directory of the project. In this file add the following tokens:

```` bash
# Slack Tokens
SLACK_TOKEN = <YOUR_SLACK_TOKEN>
SLACK_APP_TOKEN = <YOUR_SLACK_APP_TOKEN>
SIGNING_SECRET = <YOUR_SLACK_SIGNING_SECRET>

# Confluence Tokens
CONFLUENCE_ADRESS = <YOUR_CONFLUENCE_ADRESS>
CONFLUENCE_USERNAME = <YOUR_CONFLUENCE_USERNAME>
CONFLUENCE_TOKEN = <YOUR_CONFLUENCE_TOKEN>

# Google Cloud Token (for instance http://localhost:8080)
GOOGLE_CLOUD_QA_TOKEN = <YOUR_GOOGLE_CLOUD_QA_TOKEN>

# Weaviate Token (for instance http://localhost:8081)
WEAVIATE_URL = <YOUR_WEAVIATE_URL>

# DeepL Token
DEEPL_TOKEN = <YOUR_DEEPL_TOKEN>
````

**NOTE**
Make sure that the Google Cloud QA Token is different from the Weaviate Token.
<!-- TODO: Add the tokens to the project -->
<!-- TODO: Maybe there'll be different token files -> add to documentation --> 

### 6. Loading Data into the Weaviate Database 
First you need to install poppler: 
```bash
brew install poppler
brew install tesseract
```

## Setup

### 1. Start the Docker Containers

Start the Docker Containers with the following command:

```` bash
docker-compose up -d
````

### 2. Connect to server

In order to connect to the VM of the QA Bot you need to connect to the server with the following command:

```` bash
ssh <USER>@<HOST> -L <LOCAL_PORT>:<REMOTE_HOST>:<REMOTE_PORT>
````

### 3. Start the Slack Bot

If you want to run the Slack Bot local, make sure that the there is _no other instance_ of the Slack Bot running.
You can start the Slack Bot with the following command:

```` bash
./startup.sh
````

**NOTE**
Currently the Slack Bot run with the VM instance of the QA-Bot to ensure performance. <!-- TODO: Add possibility to run
the Slack-Bot local (without VM) -->

### 4. Start the QA Bot

 <!--- TODO: Add guide how to increase performance on MacBook ---> 

````bash 
./startupbot.sh
````

**NOTE**
Because of the used AI Model, the QA-Bot needs a lot of performance and it can quite a long time to generate answers.
Therefore, it is
recommended to run the QA-Bot on a VM and only use the QA-Bot for local testing.

### 5. Initialize the Database

If you run the project local you will have an empty database. To load dummy data run the following command:

````bash
./startupdata.sh
````

This will load the dummy data into the database.
If you want to load your own data, you can use the following command:

````bash
````

<!-- TODO: Add guide how to load own data into the database; currently have to go into the startupdata.sh file and delete "DUMMY" -->

### 6. Check Content of the Database

To see the content of the database you can use the following command:

````bash
./startupproccessor.sh
````

This will show you all classes and their content. 