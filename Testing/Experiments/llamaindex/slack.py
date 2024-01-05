import os
import re
from pprint import pprint

from slack_sdk import WebClient
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt import App

import weaviate
from llama_index import VectorStoreIndex
from llama_index.response_synthesizers import ResponseMode
from llama_index.vector_stores import WeaviateVectorStore

from Testing.Experiments.llamaindex.serviceContext import get_service_context

SLACK_TOKEN = os.getenv("SLACK_TOKEN")
if SLACK_TOKEN is None:
    raise Exception("SLACK_TOKEN not set")

SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
if SLACK_APP_TOKEN is None:
    raise Exception("SLACK_APP_TOKEN not set")

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
if WEAVIATE_URL is None:
    raise Exception("WEAVIATE_URL is not set")

get_service_context()

app = App(token=SLACK_TOKEN)  # Slack-bolt
handler = SocketModeHandler(app, SLACK_APP_TOKEN)  # SDK-bolt

client = weaviate.Client(WEAVIATE_URL)

vector_store = WeaviateVectorStore(
    weaviate_client=client, index_name="LlamaIndex"
)

index = VectorStoreIndex.from_vector_store(vector_store)

# default: similarity_top_k=2
query_engine = index.as_query_engine(
    service_context=get_service_context(),
    vector_store_query_mode="hybrid",
    alpha=0.75,  # basically vector based search
    similarity_top_k=5,
    response_mode=ResponseMode.REFINE,
    streaming=False
)


def url_double_slash_fix(url):
    return url.replace("//", "/").replace(":/", "://")


@app.message(re.compile(".*"))
def on_message(message, say):
    response = query_engine.query(message["text"])
    resp = response.__str__()

    resp += "\n\nFor more information visit:\n"
    for key, value in response.metadata.items():
        resp += "   • <" + url_double_slash_fix(value["url"]) + "|" + value["title"] + ">\n"
        # print(key, value["url"], value["title"])
    say(text=resp)


@app.event("app_home_opened")
def handle_message_events(event, client: WebClient):
    client.views_publish(
        # Use the user ID associated with the event
        user_id=event["user"],
        # Home tab view payload
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Hello"
                    }
                }
            ]
        }
    )

    # pprint(body)
    pprint(event)
    # logger.info(body)


handler.start()
