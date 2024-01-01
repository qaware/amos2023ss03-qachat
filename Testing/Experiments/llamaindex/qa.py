import weaviate
from llama_index import VectorStoreIndex
from llama_index.response_synthesizers import ResponseMode
from llama_index.vector_stores import WeaviateVectorStore
import os

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
if WEAVIATE_URL is None:
    raise Exception("WEAVIATE_URL is not set")
client = weaviate.Client(WEAVIATE_URL)

vector_store = WeaviateVectorStore(
    weaviate_client=client, index_name="LlamaIndex"
)

index = VectorStoreIndex.from_vector_store(vector_store)

# default: similarity_top_k=2
query_engine = index.as_query_engine(
    vector_store_query_mode="hybrid",
    alpha=0.75,  # basically vector based search
    similarity_top_k=5,
    response_mode=ResponseMode.REFINE,
    streaming=True
)

response = query_engine.query("Do we support Linux?")
for key, value in response.metadata.items():
    print(key, value["url"])
# print(response)
response.print_response_stream()
