from datetime import datetime, timezone

from QAChat.VectorDB.Documents.document_data import DocumentData, DocumentDataFormat, DocumentDataSource


class ConfluencePage:
    def __init__(self, uniq_id: str, last_changed: datetime, content: str, title: str = None,
                 link: str = None):
        self.created_at: datetime = datetime.now(timezone.utc)
        self.uniq_id: str = uniq_id
        self.last_changed: datetime = last_changed
        self.content: str = content
        self.title: str = title
        self.link: str = link

    def to_document_data(self) -> DocumentData:
        return DocumentData(
            uniq_id=self.uniq_id,
            _format=DocumentDataFormat.CONFLUENCE,
            last_changed=self.last_changed,
            data_source=DocumentDataSource.CONFLUENCE,
            content=self.content,
            title=self.title,
            link=self.link,
        )
