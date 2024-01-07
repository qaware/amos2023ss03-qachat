from typing import List

from llama_hub.confluence import ConfluenceReader
import os
import logging
import sys

from llama_index import VectorStoreIndex, StorageContext, Document, get_response_synthesizer, DocumentSummaryIndex
from llama_index.response_synthesizers import ResponseMode
from llama_index.vector_stores import WeaviateVectorStore

from Testing.Experiments.llamaindex.serviceContext import get_service_context, get_vector_store

service_context = get_service_context()
vector_store = get_vector_store()


# Get Confluence API credentials from environment variables
CONFLUENCE_ADDRESS = os.getenv("CONFLUENCE_ADDRESS")
if CONFLUENCE_ADDRESS is None:
    raise ValueError("Please set CONFLUENCE_ADDRESS environment variable")

CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
if CONFLUENCE_USERNAME is None:
    raise ValueError("Please set CONFLUENCE_USERNAME environment variable")

CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_TOKEN")
if CONFLUENCE_TOKEN is None:
    raise ValueError("Please set CONFLUENCE_TOKEN environment variable")

CONFLUENCE_SPACE_WHITELIST = os.getenv("CONFLUENCE_SPACE_WHITELIST").split(",")
if CONFLUENCE_SPACE_WHITELIST is None:
    raise ValueError("Please set CONFLUENCE_SPACE_WHITELIST environment variable")

reader = ConfluenceReader(base_url=CONFLUENCE_ADDRESS)

documents: List[Document] = []

for space_key in CONFLUENCE_SPACE_WHITELIST:
    documents.extend(reader.load_data(space_key=space_key,
                                      include_attachments=False,
                                      page_status="current",
                                      start=0,
                                      max_num_results=5000))

print("Found {} documents".format(len(documents)))
# for document in documents:
#    pprint(document.metadata["title"])
#    print(document.text)


# response_synthesizer = get_response_synthesizer(
#    response_mode=ResponseMode.TREE_SUMMARIZE,
#    use_async=True
# )
# doc_summary_index = DocumentSummaryIndex.from_documents(
#    documents,
#    service_context=get_service_context(),
#    response_synthesizer=response_synthesizer,
#    show_progress=True,
# )
# doc_summary_index.storage_context.persist("index")


# print(doc_summary_index.summary)

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    service_context=get_service_context()
)

# index = VectorStoreIndex.from_documents(documents)
# PERSIST_DIR = "./storage"
# index.storage_context.persist(persist_dir=PERSIST_DIR)
