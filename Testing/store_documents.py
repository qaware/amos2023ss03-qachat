# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
import json
import sys
import xml.etree.ElementTree as ET
from markdownify import markdownify as md
from bs4 import BeautifulSoup
from datetime import datetime
from enum import Enum

from QAChat.Documents.document_transformer import DocumentTransformer
from QAChat.VectorDB.Documents.document_data import DocumentDataFormat

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if arg == "DUMMY":
            print("Storing dummy data")
            from QAChat.Fetcher.Dummy.dummy_fetcher import DummyFetcher

            data_fetcher = DummyFetcher()
        elif arg == "CONFLUENCE":
            print("Storing confluence data")
            from QAChat.Fetcher.Confluence.confluence_fetcher import ConfluenceFetcher

            data_fetcher = ConfluenceFetcher()
        elif arg == "SLACK":
            print("Storing slack data")
            # from QAChat.Fetcher.preprocessor.slack_preprocessor import SlackPreprocessor
            # data_preprocessor = SlackPreprocessor()
        else:
            print("Sorry, wrong argument.")
            sys.exit(1)

        documents = data_fetcher.load_preprocessed_data(
            datetime.now(),
            datetime(1970, 1, 1))

        nchars = 0
        for doc in documents:
            nchars += len(doc.content)

        print("Loaded " + str(len(documents)) + " documents with " + str(nchars) + " characters.")


        # transformer = DocumentTransformer()
        # transformer.transform(documents)

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
                text_file.write("format: " + doc.format.value + "\n")
                text_file.write("uniq_id: " + doc.uniq_id + "\n")
                text_file.write("last changed: " + doc.last_changed.isoformat() + "\n")
                text_file.write("typ: " + doc.data_source.value + "\n")
                text_file.write("link: " + doc.link + "\n")
                text_file.write("text:\n" + doc.content + "\n")
                text_file.write("markdown:\n" + md(doc.content) + "\n")
                if doc.format == DocumentDataFormat.CONFLUENCE and doc.content is not None and len(doc.content) > 3:
                    #dom = ET.XML(doc.content)
                    #ET.indent(dom)
                    bs = BeautifulSoup(doc.content, 'html')
                    pretty_xml = bs.prettify()
                    text_file.write("beautify:\n" + pretty_xml + "\n")
                    #print(pretty_xml)

                text_file.write("\n\n------------------------------------------------------\n\n")

        print("Stored documents in documents.txt")
