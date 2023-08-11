# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
import os
import sys

import weaviate
from dotenv import load_dotenv

from QAChat.Common import init_db
from document_embedder import DocumentEmbedder, DataSource
from QAChat.Common.bucket_managing import upload_database
from get_tokens import get_tokens_path

if __name__ == "__main__":

    # check if *sys.argv[1:] has "DUMMY" as argument
    if ("DUMMY" in sys.argv[1:]):
        # if yes, only store dummy data
        print("Storing dummy data")
        DocumentEmbedder().store_information_in_database(DataSource.DUMMY)
    # check if *sys.argv[1:] is empty (to avoid typos)
    elif ("CLEAR" in sys.argv[1:]):
        # if yes, clear the database
        print("Clearing database")
        load_dotenv(get_tokens_path())
        weaviate_client = weaviate.Client(os.getenv("WEAVIATE_URL"))
        init_db.clear_db(weaviate_client)
        init_db.init_db(weaviate_client)
    elif (len(sys.argv[1:]) == 0):
        # store all data
        print("Storing all data")
        DocumentEmbedder().store_information_in_database(DataSource.CONFLUENCE)
        # DocumentEmbedder().store_information_in_database(DataSource.SLACK) # TODO: uncomment later
    # if neither of the above, print error message
    else:
        print("Sorry, wrong argument. Please use 'DUMMY' or no argument at all.")

#    upload_database()
