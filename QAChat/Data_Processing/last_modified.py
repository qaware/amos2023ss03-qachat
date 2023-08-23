from datetime import datetime

from QAChat.VectorDB.vectordb import VectorDB
from QAChat.Data_Processing.preprocessor.data_information import DataSource


class LastModified:

    def __init__(self):
        self.db = VectorDB()

    def get_last_update(self, source: DataSource) -> datetime:
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

    def update(self, source: DataSource, current_time: datetime):
        self.db.weaviate_client.data_object.create(
            {"type": source.value, "last_update": current_time.isoformat()},
            "LastModified",
        )

    def show_last_entries(self):
        print(
            self.db.weaviate_client.query.get("LastModified", ["last_update", "type"])
            .do()
            .items()
        )

