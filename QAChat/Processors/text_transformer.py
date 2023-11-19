# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Emanuel Erben
# SPDX-FileCopyrightText: 2023 Felix Nützel

from typing import List
from uuid import UUID

import nltk
from langchain.text_splitter import RecursiveCharacterTextSplitter

from QAChat.Processors.data_information import DataInformation
from QAChat.VectorDB.Documents.document_data import DocumentDto

CHUNK_SIZE = 200
CHUNK_OVERLAP = 50


def transform_text_to_chunks(data_information_list: List[DocumentDto]) -> List[DataInformation]:
    """
    Splits the data information needed for our vector database into chunks.

    :param data_information_list: a list of data_information objects with attributes id, typ, last_changed and text
    :return: a new data_information_list in which the data was split into chunks with a specific size and overlap
    """

    nltk.download("punkt", quiet=True)  # TODO: why?
    new_data_information_list = []

    for data_information in data_information_list:
        # data_information.text = (
        #     data_information.text.replace("<name>", "").replace("</name>", "")
        # )

        # split the text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )

        chunks = text_splitter.split_text(data_information.content)

        for index, text_chunk in enumerate(chunks):
            new_data_information: DataInformation = DataInformation(
                data_information.uniq_id,
                index,  # chunk number
                data_information.last_changed,
                data_information.data_source,
                text_chunk,
                data_information.title,
                data_information.link
            )
            new_data_information.document_ref_uuid = UUID(data_information.uuid)
            new_data_information_list.append(new_data_information)

    return new_data_information_list
