import typing
from datetime import datetime, timezone
from typing import List

from QAChat.VectorDB.Documents.document_data import DocumentDto, DocumentDataFormat, DocumentDataSource


class ConfluencePage:
    def __init__(self, page_id: str, last_changed: datetime, content: str, title: str = None,
                 link: str = None):
        self.created_at: datetime = datetime.now(timezone.utc)
        self.page_id: str = page_id
        self.last_changed: datetime = last_changed
        self.content: str = content
        self.title: str = title
        self.link: str = link
        # helper to determine the correct title
        self.child_pages: List[str] = []
        self.parent_page: typing.Optional[str] = None

    def to_document_data(self) -> DocumentDto:
        doc = DocumentDto(
            uniq_id=self.page_id,
            _format=DocumentDataFormat.CONFLUENCE,
            last_changed=self.last_changed,
            data_source=DocumentDataSource.CONFLUENCE,
            content=self.content,
            title=self.title,
            link=self.link,
        )
        return doc
