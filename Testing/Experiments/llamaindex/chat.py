import logging
import sys

from llama_index import VectorStoreIndex, ChatPromptTemplate
from llama_index.agent import OpenAIAgent, ReActAgent
from llama_index.chat_engine.types import ChatMode, BaseChatEngine
from llama_index.llms import ChatMessage, MessageRole
from llama_index.prompts import display_prompt_dict

from Testing.Experiments.llamaindex.serviceContext import get_service_context, get_vector_store

service_context = get_service_context()
vector_store = get_vector_store()

index = VectorStoreIndex.from_vector_store(vector_store)

#chat_refine_msgs = [
#    ChatMessage(
#        role=MessageRole.SYSTEM,
#        content=(
#            "Always answer the question, even if the context isn't helpful."
#        ),
#    )]
#refine_template = ChatPromptTemplate(chat_refine_msgs)

query_engine: ReActAgent = index.as_chat_engine(
    service_context=service_context,
    chat_mode=ChatMode.REACT,
    vector_store_query_mode="hybrid",
    alpha=0.75,  # basically vector based search
    similarity_top_k=5,
    verbose=True
)
#query_engine.update_prompts()
print(query_engine.get_prompts())

#print(type(query_engine))
#display_prompt_dict(query_engine.get_prompts())

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

#response = query_engine.chat("Dürfen wir Linux auf unseren Firmenrechnern installieren?")

#response = query_engine.chat("Wo finde ich mehr Informationen über Konferenzen?")
#response = query_engine.chat("Bitte suche nach 'Can I install Linux on my company laptop?'")
response = query_engine.chat("Bitte suche ob ich einen Firmenlaptop mit Linux bekommen kann.")

print(response)
#for source in response.source_nodes:
#    print(source.metadata["title"], source.metadata["url"])

#for source in response.sources:
#    print(source.raw_input)
    #print(source.metadata["title"], source.metadata["url"])

#print(response.sources)

#response = query_engine.query("Can you tell me more?")
#for key, value in response.metadata.items():
#    print(key, value["url"])
#print(response)

