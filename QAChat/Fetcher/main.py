import sys

from document_storer import DocumentStorer

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if arg == "DUMMY":
            print("Storing dummy data")
            from QAChat.Fetcher.Dummy.dummy_fetcher import DummyFetcher
            data_fetcher = DummyFetcher()
            DocumentStorer().store(data_fetcher)
        elif arg == "CONFLUENCE":
            print("Storing confluence data")
            from QAChat.Fetcher.Confluence.confluence_fetcher import ConfluenceFetcher
            data_fetcher = ConfluenceFetcher()
            DocumentStorer().store(data_fetcher)
        else:
            print("Sorry, wrong argument.")
            sys.exit(1)
