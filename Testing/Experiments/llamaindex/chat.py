import logging
import sys

import weaviate
from llama_index import VectorStoreIndex
from llama_index.chat_engine.types import ChatMode
from llama_index.vector_stores import WeaviateVectorStore
from Testing.Experiments.llamaindex.serviceContext import get_service_context
import os

get_service_context()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
if WEAVIATE_URL is None:
    raise Exception("WEAVIATE_URL is not set")
client = weaviate.Client(WEAVIATE_URL)

vector_store = WeaviateVectorStore(
    weaviate_client=client,
    index_name="LlamaIndex"
)

index = VectorStoreIndex.from_vector_store(vector_store)

query_engine = index.as_chat_engine(
    service_context=get_service_context(),
    chat_mode=ChatMode.BEST,
    verbose=True
)

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

response = query_engine.chat("Unterstützen wir Linux?")
#for key, value in response.metadata.items():
#    print(key, value["url"])
print(response)

#response = query_engine.query("Can you tell me more?")
#for key, value in response.metadata.items():
#    print(key, value["url"])
#print(response)

