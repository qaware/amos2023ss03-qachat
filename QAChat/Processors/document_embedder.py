# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
# SPDX-FileCopyrightText: 2023 Felix Nützel
# SPDX-FileCopyrightText: 2023 Emanuel Erben

from QAChat.Common.deepL_translator import DeepLTranslator
from QAChat.Processors.preprocessor.html_to_text import get_text_markdonify
from QAChat.VectorDB.Documents.document_data import DocumentData, DocumentDataFormat
from QAChat.VectorDB.vector_store import VectorStore
from QAChat.Processors.text_transformer import transform_text_to_chunks


class DocumentEmbedder:
    def __init__(self):
        self.translator = DeepLTranslator()

    def store_information_in_database(self, documents: list[DocumentData]):
        print("Loaded " + str(len(documents)) + " documents.")

        for idx in range(len(documents)):
            content = documents[idx].content

            # remove html tags
            if documents[idx].format == DocumentDataFormat.CONFLUENCE:
                content = get_text_markdonify(content)

            # translate text
            documents[idx].content = self.translator.translate_to(content, "EN-US").text

        # transform long entries into multiple chunks and translation to english
        print("Transform_text_to_chunks")
        documents = transform_text_to_chunks(documents)
        print("number of chunks to update:" + str(len(documents)))
        if len(documents) == 0:
            return

        vector_store = VectorStore()
        vector_store.update_add_texts(documents)
