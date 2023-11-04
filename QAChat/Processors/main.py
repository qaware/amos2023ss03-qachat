# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
import sys

from QAChat.VectorDB.Documents.document_store import DocumentStore
from document_embedder import DocumentEmbedder

if __name__ == "__main__":
    document_store = DocumentStore()
    print("Get all documents")
    documents = document_store.get_all_documents()
    print("Received", len(documents), "documents")
    DocumentEmbedder().store_information_in_database(documents)



