# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
# SPDX-FileCopyrightText: 2023 Felix Nützel
# SPDX-FileCopyrightText: 2023 Emanuel Erben
from datetime import datetime
from typing import List

import de_core_news_sm
import spacy
import spacy.cli
import xx_ent_wiki_sm
from spacy_langdetect import LanguageDetector

from QAChat.Common.deepL_translator import DeepLTranslator
from QAChat.VectorDB.embeddings import Embeddings
from QAChat.VectorDB.vector_store import VectorStore
from QAChat.VectorDB.vectordb import VectorDB
from QAChat.VectorDB.last_modified import LastModified
from QAChat.Data_Processing.preprocessor.data_information import DataInformation
from QAChat.Data_Processing.preprocessor.data_preprocessor import DataPreprocessor
from QAChat.Data_Processing.text_transformer import transform_text_to_chunks


class DocumentEmbedder:
    def __init__(self):
        self.embeddings = Embeddings()
        self.vector_store = VectorStore()
        self.db = VectorDB()

        # name identification
        spacy.cli.download("xx_ent_wiki_sm")
        spacy.load("xx_ent_wiki_sm")
        self.multi_lang_nlp = xx_ent_wiki_sm.load()
        spacy.cli.download("de_core_news_sm")
        spacy.load("de_core_news_sm")
        self.de_lang_nlp = de_core_news_sm.load()
        self.translator = DeepLTranslator()

    def store_information_in_database(self, data_preprocessor: DataPreprocessor):
        last_updated = LastModified().get_last_update(data_preprocessor.get_source())
        current_time = datetime.now()
        print("Start: Load data from "
              + data_preprocessor.get_source().value
              + " and start date "
              + last_updated.isoformat())
        all_changed_data = data_preprocessor.load_preprocessed_data(
            current_time, last_updated
        )
        print("Loaded " + str(len(all_changed_data)) + " documents.")

        # identify names and add name-tags before chunking and translation
        # all_changed_data = self.identify_names(all_changed_data)

        # transform long entries into multiple chunks and translation to english
        print("Start: transform_text_to_chunks")
        all_changed_data = transform_text_to_chunks(all_changed_data)
        print("number of chunks to update:" + str(len(all_changed_data)))
        if len(all_changed_data) == 0:
            return

        self.vector_store.update_add_texts(all_changed_data, data_preprocessor.get_source())

        LastModified().update(data_preprocessor.get_source(), current_time)
        LastModified().show_last_entries()

    def identify_names(self, all_data: List[DataInformation]) -> List[DataInformation]:
        """
        Method identifies names with spacy and adds name tags to the text
        :param all_data:  which is the List of DataInformation that gets send to the chunking
        :return: the input list with added name tags to persons
        """
        for data in all_data:
            # identify language of text
            language = self.get_target_language(data.text)
            # choose spacy model after language
            if language == "de":
                nlp = self.de_lang_nlp
            else:
                nlp = self.multi_lang_nlp
            # identify sentence parts
            doc = nlp(data.text)
            already_replaced = []
            for ent in doc.ents:

                if ent.text in already_replaced or ent.label_ != "PER":
                    continue
                # only person names are flanked by tag and multiplicity is avoided
                already_replaced.append(ent.text)
                print("replace name " + ent.text)
                data.text = data.text.replace(ent.text, "<name>" + ent.text + "</name>")
        return all_data

    def get_lang_detector(self, nlp, name):
        return LanguageDetector()

    def get_target_language(self, text):
        # Language.factory("language_detector", func=self.get_lang_detector)
        if "sentencizer" not in self.multi_lang_nlp.pipe_names:
            self.multi_lang_nlp.add_pipe("sentencizer")
        if "language_detector" not in self.multi_lang_nlp.pipe_names:
            self.multi_lang_nlp.add_pipe("language_detector", last=True)
        doc = self.multi_lang_nlp(text)
        if doc._.language["score"] > 0.8:
            return doc._.language["language"]
        else:
            return self.translator.translate_to(
                text, "EN-US"
            ).detected_source_lang.lower()
