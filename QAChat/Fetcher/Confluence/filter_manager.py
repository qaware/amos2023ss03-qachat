import os
from typing import List

from QAChat.Common.blacklist_reader import read_blacklist_items

CONFLUENCE_SPACE_WHITELIST = os.getenv("CONFLUENCE_SPACE_WHITELIST").split(",")
if CONFLUENCE_SPACE_WHITELIST is None:
    raise ValueError("Please set CONFLUENCE_SPACE_WHITELIST environment variable")

BLACKLIST_PATH = os.getenv("BLACKLIST_PATH")
if BLACKLIST_PATH is None:
    raise Exception("BLACKLIST_PATH is not set")

class FilterManager:
    def __init__(self):
        self.restricted_pages: List[str] = []
        self.restricted_spaces: List[str] = []

        # Retrieve blacklist data from file
        blacklist = read_blacklist_items(BLACKLIST_PATH)

        # Extract restricted spaces and restricted pages from the blacklist data
        for entries in blacklist:
            if "/pages/" in entries.identifier:
                # Split by slash and get the page id, https://.../pages/PAGE_ID
                self.restricted_pages.append(entries.identifier.split("/")[7])
            else:
                # Split by slash and get the space name, https://.../space/SPACE_NAME
                self.restricted_spaces.append(entries.identifier.split("/")[5])

    def is_valid_page(self, page_id: str) -> bool:
        return page_id not in self.restricted_pages

    def is_valid_space(self, space_name: str) -> bool:
        return space_name not in self.restricted_spaces and space_name in CONFLUENCE_SPACE_WHITELIST
