import uuid
from datetime import datetime, timezone


class EmbeddingDto:
    def __init__(self, chunk_id: int, type_id: str, last_update: datetime, text: str, link: str, data_source: str):
        self.uuid: uuid.UUID = uuid.uuid4()  # uuid for Weaviate. We create our own, because we need it for references
        self.created_at = datetime.now(timezone.utc)
        self.type_id: str = type_id
        self.text: str = text
        self.link: str = link
        self.data_source: str = data_source
        self.chunk_id: int = chunk_id
        self.last_update = last_update
