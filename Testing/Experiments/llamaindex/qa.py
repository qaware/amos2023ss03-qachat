from llama_index import VectorStoreIndex
from llama_index.prompts import display_prompt_dict
from llama_index.response_synthesizers import ResponseMode

from Testing.Experiments.llamaindex.serviceContext import get_service_context, get_vector_store

service_context = get_service_context()
vector_store = get_vector_store()

index = VectorStoreIndex.from_vector_store(vector_store)

# default: similarity_top_k=2
query_engine = index.as_query_engine(
    vector_store_query_mode="hybrid",
    alpha=0.75,  # basically vector based search
    similarity_top_k=5,
    response_mode=ResponseMode.REFINE,
    streaming=True
)
#display_prompt_dict(query_engine.get_prompts())

response = query_engine.query("Do we support Linux?")
for key, value in response.metadata.items():
    print(key, value["url"])
# print(response)
response.print_response_stream()
