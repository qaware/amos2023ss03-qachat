# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
import sys
import json
from datetime import datetime
from enum import Enum

if __name__ == "__main__":

    for arg in sys.argv[1:]:
        if arg == "DUMMY":
            # if yes, only store dummy data
            print("Storing dummy data")
            from QAChat.Data_Processing.preprocessor.dummy_preprocessor import DummyPreprocessor

            data_preprocessor = DummyPreprocessor()
        elif arg == "CONFLUENCE":
            print("Storing confluence data")
            from QAChat.Data_Processing.preprocessor.confluence_preprocessor import ConfluencePreprocessor

            data_preprocessor = ConfluencePreprocessor()
            # DocumentEmbedder().store_information_in_database(DataSource.SLACK) # TODO: uncomment later
        elif arg == "SLACK":
            print("Storing slack data")
            from QAChat.Data_Processing.preprocessor.slack_preprocessor import SlackPreprocessor

            data_preprocessor = SlackPreprocessor()
            # DocumentEmbedder().store_information_in_database(DataSource.SLACK) # TODO: uncomment later
        else:
            print("Sorry, wrong argument.")
            sys.exit(1)

        documents = data_preprocessor.load_preprocessed_data(datetime.now(), datetime(1970, 1, 1))


        def dumper(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, Enum):
                return obj.value
            try:
                return obj.toJSON()
            except:
                return obj.__dict__

        documentsAsJson = json.dumps(documents, indent=4, sort_keys=True, default=dumper)

        with open("documents.json", "w") as text_file:
            text_file.write(documentsAsJson)

        print("Stored documents in documents.json")
