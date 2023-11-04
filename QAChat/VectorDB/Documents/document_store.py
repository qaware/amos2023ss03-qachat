from QAChat.VectorDB.Documents.document_data import DocumentData
from QAChat.VectorDB.vectordb import VectorDB

class DocumentStore:

    def __init__(self):
        self.db = VectorDB()

    def init_class(self):
        if not self.db.weaviate_client.schema.exists("Documents"):
            self.db.weaviate_client.schema.create_class(
                {
                    "class": "Documents",
                    "vectorizer": "none",
                    "vectorIndexConfig": {
                        "skip": True  # disable vectorindex
                    },
                    "properties": [
                        {"name": "uniq_id", "dataType": ["text"]},  ## UUID?
                        {"name": "format", "dataType": ["text"]},  # "CONFLUENCE_XML", "MARKDOWN", ....
                        {"name": "data_source", "dataType": ["text"]},
                        {"name": "last_changed", "dataType": ["text"]},
                        {
                            "name": "title",
                            "dataType": ["text"],
                            "indexFilterable": False,  # disable filterable index for this property
                            "indexSearchable": False,  # disable searchable index for this property
                        },
                        {
                            "name": "content",
                            "dataType": ["text"],
                            "description": "the content as string",
                            "indexFilterable": False,  # disable filterable index for this property
                            "indexSearchable": False,  # disable searchable index for this property
                        },
                        {
                            "name": "link",
                            "dataType": ["text"],
                            "indexFilterable": False,  # disable filterable index for this property
                            "indexSearchable": False,  # disable searchable index for this property
                        },
                    ],
                }
            )

    def update_add_texts(self, all_changed_data: list[DocumentData]):
        print("Update", len(all_changed_data), "Texts")
        print("Delete texts")

        ids: set[str] = set()
        for document in all_changed_data:
            ids.add(document.uniq_id)

        for uniq_id in ids:
            self.db.weaviate_client.batch.delete_objects(
                "Documents",
                where={
                    "path": ["uniq_id"],
                    "operator": "Equal",
                    "valueString": uniq_id,
                },
            )
        print("Store texts")

        # TODO: use batch job
        for document in all_changed_data:
            self.db.weaviate_client.data_object.create(
                {
                    "uniq_id": document.uniq_id,
                    "format": document.format.value,
                    "data_source": document.data_source.value,
                    "last_changed": document.last_changed.isoformat(),
                    "content": document.content,
                    "title": document.title,
                    "link": document.link,
                }, "Documents"
            )

    def remove_id(self, uniq_id):
        self.db.weaviate_client.batch.delete_objects(
            "Documents",
            {
                "path": ["uniq_id"],
                "operator": "Equal",
                "valueString": uniq_id,
            },
        )
