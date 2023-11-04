from datetime import datetime

from QAChat.VectorDB.Documents.document_data import DocumentDataSource


class DataInformation:
    def __init__(self, id: str, chunk: int, last_changed: datetime, typ: DocumentDataSource, text: str, title: str = None, space: str = None, link: str = None):
        self.id: str = id
        self.chunk: int = chunk
        self.last_changed: datetime = last_changed
        self.typ: DocumentDataSource = typ
        self.text: str = text
        self.title: str = title
        self.space: str = space
        self.link: str = link

