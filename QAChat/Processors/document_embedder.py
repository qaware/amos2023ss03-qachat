# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
# SPDX-FileCopyrightText: 2023 Felix Nützel
# SPDX-FileCopyrightText: 2023 Emanuel Erben
from datetime import datetime
from typing import List

from QAChat.Common.deepL_translator import DeepLTranslator
from QAChat.VectorDB.vector_store import VectorStore
from QAChat.VectorDB.vectordb import VectorDB
from QAChat.VectorDB.last_modified import LastModified
from QAChat.Processors.preprocessor.data_preprocessor import DataPreprocessor
from QAChat.Processors.text_transformer import transform_text_to_chunks


class DocumentEmbedder:
    def __init__(self):
        self.db = VectorDB()
        self.translator = DeepLTranslator()

    def store_information_in_database(self, data_preprocessor: DataPreprocessor):
        all_changed_data = data_preprocessor.load_preprocessed_data()
        print("Loaded " + str(len(all_changed_data)) + " documents.")

        # transform long entries into multiple chunks and translation to english
        print("Transform_text_to_chunks")
        all_changed_data = transform_text_to_chunks(all_changed_data)
        print("number of chunks to update:" + str(len(all_changed_data)))
        if len(all_changed_data) == 0:
            return

        vector_store = VectorStore()
        vector_store.update_add_texts(all_changed_data, data_preprocessor.get_source())

        LastModified().update(data_preprocessor.get_source(), current_time)
        LastModified().show_last_entries()
