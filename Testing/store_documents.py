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

        documents = data_preprocessor.load_preprocessed_data(
            datetime.now(),
            datetime(1970, 1, 1),
            do_filter=False)

        nchars = 0
        for doc in documents:
            nchars += len(doc.text)

        print("Loaded " + str(len(documents)) + " documents with " + str(nchars) + " characters.")

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

        with open("documents.txt", "w") as text_file:
            for doc in documents:
                text_file.write("title: " + doc.title + "\n")
                text_file.write("id: " + doc.id + "\n")
                text_file.write("last changed: " + doc.last_changed.isoformat() + "\n")
                text_file.write("typ: " + doc.typ.value + "\n")
                text_file.write("link: " + doc.link + "\n")
                text_file.write("space: " + doc.space + "\n")
                text_file.write("text:\n" +doc.text + "\n")
                text_file.write("\n\n------------------------------------------------------\n\n")

        print("Stored documents in documents.txt")
