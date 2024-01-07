import logging
import sys

from llama_index import VectorStoreIndex
from llama_index.agent import OpenAIAgent
from llama_index.chat_engine.types import ChatMode, BaseChatEngine
from llama_index.prompts import display_prompt_dict

from Testing.Experiments.llamaindex.serviceContext import get_service_context, get_vector_store

service_context = get_service_context()
vector_store = get_vector_store()

index = VectorStoreIndex.from_vector_store(vector_store)

query_engine: OpenAIAgent = index.as_chat_engine(
    service_context=service_context,
    chat_mode=ChatMode.REACT,
    verbose=True
)

#display_prompt_dict(query_engine.get_prompts())

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

response = query_engine.chat("Unterstützen wir Linux?")

print(response)
#print(len(response.sources))
#print(response.sources[0])

#response = query_engine.query("Can you tell me more?")
#for key, value in response.metadata.items():
#    print(key, value["url"])
#print(response)

