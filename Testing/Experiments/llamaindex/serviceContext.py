from llama_index import OpenAIEmbedding, ServiceContext, set_global_service_context
from llama_index.embeddings.openai import OpenAIEmbeddingModelType
from llama_index.llms import OpenAI


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
