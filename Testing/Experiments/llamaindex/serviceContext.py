import os

from llama_index import OpenAIEmbedding, ServiceContext, set_global_service_context
from llama_index.embeddings.openai import OpenAIEmbeddingModelType
from llama_index.llms import OpenAI

import weaviate
from llama_index.vector_stores import WeaviateVectorStore


def get_service_context() -> ServiceContext:
    embed_model = OpenAIEmbedding(embed_batch_size=10, model=OpenAIEmbeddingModelType.TEXT_EMBED_ADA_002)
    llm = OpenAI(model="gpt-4-1106-preview")

    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embed_model,
        chunk_size=1024
    )

    set_global_service_context(service_context)

    return service_context


def get_vector_store() -> WeaviateVectorStore:
    WEAVIATE_URL = os.getenv("WEAVIATE_URL")
    if WEAVIATE_URL is None:
        raise Exception("WEAVIATE_URL is not set")
    client = weaviate.Client(WEAVIATE_URL)

    vector_store = WeaviateVectorStore(
        weaviate_client=client,
        index_name="LlamaIndex"
    )
    return vector_store
