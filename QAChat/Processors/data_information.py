import typing
from datetime import datetime

from QAChat.VectorDB.Documents.document_data import DocumentDataSource


class DataInformation:
    def __init__(self, id: str, chunk: int, last_changed: datetime, data_source: DocumentDataSource, text: str,
                 title: str = None, link: str = None):
        self.id: str = id
        self.chunk: int = chunk
        self.last_changed: datetime = last_changed
        self.data_source: DocumentDataSource = data_source
        self.text: str = text
        self.title: str = title
        self.link: str = link
        self.document_ref_uuid: typing.Optional[str] = None  # reference to the document in the Documents Class
