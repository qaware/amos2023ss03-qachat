# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
import os
import sys

import weaviate

from QAChat.Common import init_db
from document_embedder import DocumentEmbedder, DataSource
from QAChat.Common.bucket_managing import upload_database

if __name__ == "__main__":
    weaviate_client = weaviate.Client(os.getenv("WEAVIATE_URL"))

    for arg in sys.argv[1:]:

        if arg == "CLEAR":
            # if yes, clear the database
            print("Clearing database")
            init_db.clear_db(weaviate_client)
            init_db.init_db(weaviate_client)
        # check if *sys.argv[1:] has "DUMMY" as argument
        elif arg == "DUMMY":
            # if yes, only store dummy data
            print("Storing dummy data")
            DocumentEmbedder().store_information_in_database(DataSource.DUMMY)
        # check if *sys.argv[1:] is empty (to avoid typos)
        elif arg == "CONFLUENCE":
            # store all data
            print("Storing all data")
            DocumentEmbedder().store_information_in_database(DataSource.CONFLUENCE)
            # DocumentEmbedder().store_information_in_database(DataSource.SLACK) # TODO: uncomment later
        # if neither of the above, print error message
        else:
            print("Sorry, wrong argument. Please use 'DUMMY' or no argument at all.")
            sys.exit(1)
