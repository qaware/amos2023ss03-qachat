from datetime import datetime

import dateutil.parser

from QAChat.VectorDB.Documents.document_data import DocumentDto, DocumentDataFormat, DocumentDataSource
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
                        {"name": "created_at", "dataType": ["date"]},  # class entry creation date
                        {"name": "uniq_id", "dataType": ["text"]},  # UUID?
                        {"name": "format", "dataType": ["text"]},  # "CONFLUENCE_XML", "MARKDOWN", ....
                        {"name": "language", "dataType": ["text"]},
                        {"name": "data_source", "dataType": ["text"]},
                        # The document last changed date from the source system (e.g. confluence)
                        {"name": "last_changed", "dataType": ["date"]},
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
                            "name": "tags",
                            "dataType": ["text[]"],
                            "description": "tag information",
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

    def update_add_texts(self, all_changed_data: list[DocumentDto]):
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
                    "created_at": document.created_at.isoformat(),
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

    def get_all_documents(self) -> list[DocumentDto]:
        documents: list[DocumentDto] = []

        document_uuid = None
        while True:
            data = (
                self.db.weaviate_client.data_object.get(class_name="Documents", after=document_uuid, limit=1000)[
                    'objects']
            )
            print("  Paging: Got", len(data), "documents")
            for d in data:
                prop = d['properties']
                uniq_id = prop["uniq_id"]
                _format = DocumentDataFormat(prop["format"])
                data_source = DocumentDataSource(prop["data_source"])
                content = prop["content"]
                if "title" not in prop:
                    title = None
                else:
                    title = prop["title"]
                link = prop["link"]
                last_changed = dateutil.parser.isoparse(prop["last_changed"])
                doc = DocumentDto(uniq_id, _format, last_changed, data_source, content, title, link)
                doc.created_at = dateutil.parser.isoparse(prop["created_at"])
                doc.uuid = d['id']
                documents.append(doc)

            if len(data) == 0:
                break
            document_uuid = data[-1]['id']

        return documents
