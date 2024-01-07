import os
import re
from pprint import pprint

from llama_index.agent import ReActAgent
from llama_index.chat_engine.types import ChatMode
from slack_sdk import WebClient
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt import App

from llama_index import VectorStoreIndex

from Testing.Experiments.llamaindex.serviceContext import get_service_context, get_vector_store

SLACK_TOKEN = os.getenv("SLACK_TOKEN")
if SLACK_TOKEN is None:
    raise Exception("SLACK_TOKEN not set")

SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
if SLACK_APP_TOKEN is None:
    raise Exception("SLACK_APP_TOKEN not set")

service_context = get_service_context()
vector_store = get_vector_store()

app = App(token=SLACK_TOKEN)  # Slack-bolt
handler = SocketModeHandler(app, SLACK_APP_TOKEN)  # SDK-bolt

index = VectorStoreIndex.from_vector_store(vector_store)

cache = {}


def get_query_engine(ts: str) -> ReActAgent:
    if ts in cache:
        return cache[ts]
    else:
        query_engine: ReActAgent = index.as_chat_engine(
            service_context=service_context,
            chat_mode=ChatMode.REACT,
            vector_store_query_mode="hybrid",
            alpha=0.75,  # basically vector based search
            similarity_top_k=5,
            verbose=True
        )
        cache[ts] = query_engine
        return query_engine


def url_double_slash_fix(url):
    return url.replace("//", "/").replace(":/", "://")


@app.message(re.compile(".*"))
def on_message(message, say):
    pprint(message)
    ts = message['ts']
    query_engine = get_query_engine(ts)
    response = query_engine.chat(message["text"])
    resp = response.__str__()
    if len(response.source_nodes) > 0:
        resp += "\n\nMehr Informationen unter:\n"
        for source in response.source_nodes:
            resp += "   • <" + url_double_slash_fix(source.metadata["url"]) + "|" + source.metadata["title"] + ">\n"

        for source in response.sources:
            resp += "_Query: " + str(source.raw_input) + "_"

    say(text=resp, thread_ts=ts)


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
                        "text": "Noch nichts zu sehen. Klicke auf den Tab Nachrichten um zu beginnen"
                    }
                }
            ]
        }
    )

    # pprint(body)
    # pprint(event)
    # logger.info(body)


handler.start()
