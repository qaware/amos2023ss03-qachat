# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
import sys

from document_embedder import DocumentEmbedder

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if arg == "CONFLUENCE":
            print("Storing confluence data")
            from QAChat.Data_Processing.preprocessor.confluence_preprocessor import ConfluencePreprocessor
            data_preprocessor = ConfluencePreprocessor()
            DocumentEmbedder().store_information_in_database(data_preprocessor)
            # DocumentEmbedder().store_information_in_database(DataSource.SLACK) # TODO: uncomment later
        elif arg == "SLACK":
            print("Storing slack data")
            from QAChat.Data_Processing.preprocessor.slack_preprocessor import SlackPreprocessor
            data_preprocessor = SlackPreprocessor()
            DocumentEmbedder().store_information_in_database(data_preprocessor)
            # DocumentEmbedder().store_information_in_database(DataSource.SLACK) # TODO: uncomment later
        else:
            print("Sorry, wrong argument.")
            sys.exit(1)
