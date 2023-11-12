# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Nützel
import sys

from QAChat.VectorDB.Documents.document_store import DocumentStore
from QAChat.VectorDB.Embeddings.embeddings import Embeddings
from QAChat.VectorDB.last_modified_store import LastModifiedStore
from QAChat.VectorDB.loaded_channels_store import LoadedChannelsStore
from QAChat.VectorDB.vectordb import VectorDB

db = VectorDB()

def print_index_content(index_name=None, condition=None, limit=1000):
    if index_name is None:
        db.show_schema()
    else:
        db.show_data(index_name, condition, limit)


def print_content_length(index_name=None):
    """
    A function to get the total number of entries in an index
    :param index_name: Name of the class you want to see. Leave as None if you want to see all classes and their length
    """
    if index_name is None:  # If index_name is None, get the length of all classes
        for index in db.get_all_classes():
            print(f"Total length of {index}: {db.get_size(index)}")
    else:
        print(f"Total length of {index_name}: {db.get_size(index_name)}")

if __name__ == "__main__":
    arg = sys.argv[1]
    if arg == "INFO":
        print_index_content(*sys.argv[2:])
        print_content_length(*sys.argv[2:])
    elif arg == "CLEAR":
        db.clear_db()
    elif arg == "INIT":
        DocumentStore().init_class()
        LastModifiedStore().init_class()
        Embeddings().init_class()
        LoadedChannelsStore().init_class()
    else:
        print("Sorry, wrong argument.")
        sys.exit(1)
