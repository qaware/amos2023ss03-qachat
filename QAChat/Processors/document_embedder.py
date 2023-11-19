# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
# SPDX-FileCopyrightText: 2023 Felix Nützel
# SPDX-FileCopyrightText: 2023 Emanuel Erben
from typing import List

from QAChat.Documents.document_transformer import DocumentTransformer
from QAChat.Processors.data_information import DataInformation
from QAChat.Processors.text_transformer import transform_text_to_chunks
from QAChat.VectorDB.Documents.document_data import DocumentDto
from QAChat.VectorDB.Embeddings.vector_store import VectorStore


class DocumentEmbedder:
    def __init__(self):
        self.transformer = DocumentTransformer()

    def store_information_in_database(self, documents: list[DocumentDto]):
        print("Loaded " + str(len(documents)) + " documents.")
        self.transformer.transform(documents)

        # transform long entries into multiple chunks and translation to english
        print("Transform_text_to_chunks")
        chunks: List[DataInformation] = transform_text_to_chunks(documents)

        print("number of chunks to update:" + str(len(chunks)))
        if len(chunks) == 0:
            return

        embeddings = [data.to_embedding_dto() for data in chunks]
        vector_store = VectorStore()
        vector_store.remove_texts(embeddings)
        vector_store.store_texts(embeddings)
