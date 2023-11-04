from datetime import datetime
from enum import Enum

class DocumentDataSource(Enum):
    SLACK = "slack"
    CONFLUENCE = "confluence"
    DRIVE = "drive"
    DUMMY = "dummy"

class DocumentDataFormat(Enum):
    CONFLUENCE = "CONFLUENCE_XML"
    TEXT = "TEXT"

class DocumentData:
    def __init__(self, uniq_id: str, _format: DocumentDataFormat, last_changed: datetime, data_source: DocumentDataSource, content: str, title: str = None,
                 link: str = None):
        self.uniq_id: str = uniq_id
        self.format: DocumentDataFormat = _format
        self.last_changed: datetime = last_changed
        self.data_source: DocumentDataSource = data_source
        self.content: str = content
        self.title: str = title
        self.link: str = link
