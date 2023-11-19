from datetime import datetime


class EmbeddingResultDto:
    def __init__(self, type_id: str, chunk_id: str, last_update: datetime):
        self.type_id = type_id
        self.chunk_id = chunk_id
        self.last_update = last_update
