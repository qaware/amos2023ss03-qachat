# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
import sys

import weaviate

from document_embedder import DocumentEmbedder, DataSource
from QAChat.Common.bucket_managing import upload_database

if __name__ == "__main__":

    # check if *sys.argv[1:] has "DUMMY" as argument
    if ("DUMMY" in sys.argv[1:]):
        # if yes, only store dummy data
        print("Storing dummy data")
        DocumentEmbedder().store_information_in_database(DataSource.DUMMY)
    # check if *sys.argv[1:] is empty (to avoid typos)
    elif (len(sys.argv[1:]) == 0):
        # store all data
        print("Storing all data")
        DocumentEmbedder().store_information_in_database(DataSource.CONFLUENCE)
        DocumentEmbedder().store_information_in_database(DataSource.SLACK)

    # DocumentEmbedder().store_information_in_database(DataSource.DUMMY)


#    upload_database()
