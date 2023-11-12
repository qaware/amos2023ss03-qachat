from datetime import datetime

from QAChat.Fetcher.data_fetcher import DataFetcher
from QAChat.VectorDB.Documents.document_data import DocumentData
from QAChat.VectorDB.Documents.document_store import DocumentStore
from QAChat.VectorDB.last_modified_store import LastModifiedStore


class DocumentStorer:
    @staticmethod
    def store(data_fetcher: DataFetcher):
        last_updated = LastModifiedStore().get_last_update(data_fetcher.get_source())
        current_time = datetime.now()
        print("Start: Load data from "
              + data_fetcher.get_source().value
              + " and start date "
              + last_updated.isoformat())
        all_changed_data: list[DocumentData] = data_fetcher.load_preprocessed_data(
                current_time, last_updated
            )
        print("Loaded " + str(len(all_changed_data)) + " documents.")

        if len(all_changed_data) == 0:
            return

        document_store = DocumentStore()
        document_store.update_add_texts(all_changed_data)

        LastModifiedStore().update(data_fetcher.get_source(), current_time)
        LastModifiedStore().show_last_entries()
