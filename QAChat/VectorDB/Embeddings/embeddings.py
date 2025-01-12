from QAChat.VectorDB.Embeddings.embedding_result_dto import EmbeddingResultDto
from QAChat.VectorDB.vectordb import VectorDB

from typing import List


class Embeddings:
    def __init__(self):
        self.db = VectorDB()

    def init_class(self):
        if not self.db.weaviate_client.schema.exists("Embeddings"):
            self.db.weaviate_client.schema.create_class(
                {
                    "class": "Embeddings",
                    "vectorizer": "none",  # We want to import our own vectors
                    "vectorIndexType": "hnsw",  # default
                    "vectorIndexConfig": {
                        "distance": "cosine",
                    },
                    "invertedIndexConfig": {
                        "stopwords": {
                            "preset": "en",
                            "additions": []
                        }
                    },
                    "properties": [
                        {"name": "created_at", "dataType": ["date"]},  # class entry creation date
                        {"name": "last_changed", "dataType": ["text"]},
                        {"name": "type_id", "dataType": ["text"]},
                        {
                            "name": "chunk",
                            "dataType": ["int"],
                            "indexFilterable": False,  # disable filterable index for this property
                            "indexSearchable": False,  # disable searchable index for this property
                        },
                        {"name": "data_source", "dataType": ["text"]},
                        {
                            "name": "text",
                            "dataType": ["text"],
                            "tokenization": "word",
                        },
                        {
                            "name": "link",
                            "dataType": ["text"],
                            "indexFilterable": False,  # disable filterable index for this property
                            "indexSearchable": False,  # disable searchable index for this property
                        },
                        {
                            "name": "document_ref",
                            "dataType": ["Documents"],  # reference to the documents class
                            "description": "reference to the document",
                        },
                    ],
                }
            )

    def show_embeddings(self):
        print(
            self.db.weaviate_client.query.get("Embeddings", ["type_id", "text"])
            .do()
            .items()
        )

    def get_all_for_documenttype(self, data_source: str) -> List[EmbeddingResultDto]:
        data = (
            self.db.weaviate_client.query.get(
                "Embeddings", ["type_id", "chunk", "last_changed"]
            )
            .with_where(
                {"path": ["data_source"], "operator": "Equal", "valueString": data_source}
            )
            .do()["data"]["Get"]["Embeddings"]
        )
        embedded = []
        for d in data:
            type_id = d["type_id"]
            chunk_id = d["chunk"]
            last_update = d["last_changed"]
            embedded.append(EmbeddingResultDto(type_id, chunk_id, last_update))

        return embedded

    def remove_id(self, type_id):
        self.db.weaviate_client.batch.delete_objects(
            "Embeddings",
            {
                "path": ["type_id"],
                "operator": "Equal",
                "valueString": type_id,
            },
        )
