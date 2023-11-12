from QAChat.VectorDB.vectordb import VectorDB


class LoadedChannelsStore:

    def __init__(self):
        self.db = VectorDB()

    def init_class(self):
        if not self.db.weaviate_client.schema.exists("LoadedChannels"):
            self.db.weaviate_client.schema.create_class(
                {
                    "class": "LoadedChannels",
                    "vectorIndexConfig": {
                        "skip": "true"  # disable vectorindex
                    },
                    "properties": [
                        {"name": "channel_id", "dataType": ["text"]},
                        {"name": "channel_name", "dataType": ["text"]},
                    ],
                }
            )

