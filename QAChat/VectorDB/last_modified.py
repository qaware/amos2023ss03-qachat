from datetime import datetime
from pprint import pprint

from QAChat.VectorDB.Documents.document_data import DocumentDataSource
from QAChat.VectorDB.vectordb import VectorDB

class LastModified:
    def __init__(self):
        self.db = VectorDB()

    def init_class(self):
        if not self.db.weaviate_client.schema.exists("LastModified"):
            self.db.weaviate_client.schema.create_class(
                {
                    "class": "LastModified",
                    "vectorizer": "none",
                    "vectorIndexConfig": {
                        "skip": True  # disable vectorindex
                    },
                    "properties": [
                        {"name": "type", "dataType": ["text"]},
                        {"name": "last_update", "dataType": ["text"]},
                    ],
                }
            )


    def get_last_update(self, source: DocumentDataSource) -> datetime:
        where_filter_last_update = {
            "path": ["type"],
            "operator": "Equal",
            "valueString": source.value,
        }
        last_update_object = (
            self.db.weaviate_client.query.get("LastModified", ["last_update"])
            .with_where(where_filter_last_update)
            .do()
        )
        if len(last_update_object["data"]["Get"]["LastModified"]) == 0:
            last_updated = datetime(1970, 1, 1)
        else:
            last_updated = datetime.strptime(
                last_update_object["data"]["Get"]["LastModified"][0]["last_update"],
                "%Y-%m-%dT%H:%M:%S.%f",
            )
        return last_updated

    def update(self, source: DocumentDataSource, current_time: datetime):
        self.db.weaviate_client.data_object.create(
            {"type": source.value, "last_update": current_time.isoformat()},
            "LastModified",
        )

    def show_last_entries(self):
        pprint(
            self.db.weaviate_client.query.get("LastModified", ["last_update", "type"])
            .do()["data"]["Get"]["LastModified"]
        )

