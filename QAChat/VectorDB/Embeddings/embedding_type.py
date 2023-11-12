from datetime import datetime


class EmbeddingType:
    def __init__(self, page_id: str, chunk_id: str, last_update: datetime):
        self.page_id = page_id
        self.chunk_id = chunk_id
        self.last_update = last_update
