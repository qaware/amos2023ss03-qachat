# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
# SPDX-FileCopyrightText: 2023 Felix Nützel
# SPDX-FileCopyrightText: 2023 Emanuel Erben

from QAChat.Documents.document_transformer import DocumentTransformer
from QAChat.Processors.text_transformer import transform_text_to_chunks
from QAChat.VectorDB.Documents.document_data import DocumentData
from QAChat.VectorDB.Embeddings.vector_store import VectorStore


class DocumentEmbedder:
    def __init__(self):
        self.transformer = DocumentTransformer()

    def store_information_in_database(self, documents: list[DocumentData]):
        print("Loaded " + str(len(documents)) + " documents.")
        self.transformer.transform(documents)

        # transform long entries into multiple chunks and translation to english
        print("Transform_text_to_chunks")
        documents = transform_text_to_chunks(documents)
        print("number of chunks to update:" + str(len(documents)))
        if len(documents) == 0:
            return

        vector_store = VectorStore()
        vector_store.update_add_texts(documents)
