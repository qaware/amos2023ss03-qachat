import io
import os
import re
from datetime import datetime
from pprint import pprint
from typing import List

import dateutil.parser
import requests
from atlassian import Confluence
from tqdm import tqdm

from QAChat.Fetcher.Confluence.confluence_page import ConfluencePage
from QAChat.Fetcher.data_fetcher import DataFetcher
from QAChat.Fetcher.Confluence.filter_manager import FilterManager
from QAChat.Fetcher.PDF.pdf_reader import PDFReader
from QAChat.VectorDB.Documents.document_data import DocumentDto, DocumentDataSource

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


class ConfluenceFetcher(DataFetcher):
    def __init__(self):
        self.confluence = Confluence(
            url=CONFLUENCE_ADDRESS,
            username=CONFLUENCE_USERNAME,
            password=CONFLUENCE_TOKEN,
        )
        self.pdf_reader = PDFReader()
        self.page_information: List[ConfluencePage] = []
        self.filter_manager = FilterManager()

    def get_source(self) -> DocumentDataSource:
        return DocumentDataSource.CONFLUENCE

    def get_all_spaces(self) -> List[str]:
        start = 0
        limit = 500
        all_spaces = []
        # Get all spaces first
        while True:
            # Get all confluence spaces from the confluence instance
            spaces_data = self.confluence.get_all_spaces(
                start=start, limit=limit, expand=None
            )
            for space in spaces_data["results"]:
                # exclude personal/user spaces only global spaces
                if space["type"] == "global":
                    # exclude blacklisted spaces
                    if self.filter_manager.is_valid_space(space["key"]):
                        all_spaces.append(space["key"])

            # Check if there are more spaces
            if len(spaces_data) < limit:
                break
            start = start + limit
        return all_spaces

    def get_page_ids_from_spaces(self, space_key: str) -> List[str]:
        # Get all pages from a space
        start = 0
        limit = 100

        page_ids: List[str] = []

        while True:
            pages_data = self.confluence.get_all_pages_from_space(
                space_key,
                start=start,
                limit=limit,
                status=None,
                expand=None,
                content_type="page",
            )
            #  Get all page id
            for page in pages_data:
                if self.filter_manager.is_valid_page(page["id"]):
                    page_ids.append(page["id"])

            # Check if there are more pages
            if len(pages_data) < limit:
                break
            start = start + limit

        return page_ids

    def get_data_from_page(self, page_id) -> ConfluencePage:
        # Get page by id
        page_with_body = self.confluence.get_page_by_id(
            page_id,
            expand="body.storage, version",
            status=None,
            version=None
        )
        page_info = self.confluence.get_page_by_id(
            page_id,
            expand=None,
            status=None,
            version=None
        )

        # print("-------------------------------")
        # print(page_children)
        # pprint(page_info)

        # Set final parameters for DataInformation
        last_changed = self.get_last_modified_formatted_date(page_info)
        text = self.get_raw_text_from_page(page_with_body)

        # get googledoc url:
        # urls = re.findall(r"https?://docs\.google\.com\S+", text)

        # get content from googledoc
        # commented out because we don't have access tho client's google drive
        # google_doc_content = self.get_content_from_google_drive(urls)

        # get content from confluence attachments
        pdf_content = ""  # self.get_content_from_page_attachments(page_id)

        # replace consecutive occurrences of \n into one \n
        text = re.sub(r"\n+", "\n", text)
        # replace " \n" with "\n"
        text = re.sub(r" \n", "\n", text)
        # remove leading \n
        text = re.sub(r"^\n", "", text)

        # commented out because we don't have access tho client's google drive
        # + " " + google_doc_content
        # + " " + pdf_content,

        # print(f"Länge {page_id}: %d \n" % len(text))
        # Add Page content to list of DocumentData
        # print(page_info["_links"]["base"] + page_info["_links"]["webui"].split("overview")[0])

        page = ConfluencePage(
            page_id=page_id,
            last_changed=last_changed,
            content=text,
            title=page_info["title"],
            link=page_info["_links"]["base"] + page_info["_links"]["webui"].split("overview")[0],
        )

        child_pages = self.confluence.get_child_pages(page_id)
        for child_page in child_pages:
            page.child_pages.append(child_page["id"])
            # print(f"Page Title: {page['title']}, Page ID: {page['id']}")

        return page

    def get_last_modified_formatted_date(self, page_info) -> datetime:
        # Get date of last modified page
        data_last_changed = page_info["version"]["when"]
        return dateutil.parser.isoparse(data_last_changed)

    def get_raw_text_from_page(self, page_with_body) -> str:
        # Get page content
        page_in_html = page_with_body["body"]["storage"]["value"]
        return page_in_html
        # return page_in_html
        # return get_text(page_in_html)
        # return get_text_markdonify(page_in_html)

    #    def get_content_from_google_drive(self, urls):
    #        pdf_content = ""
    #
    #        # go through all urls
    #        for url in urls:
    #            # get id from url
    #            google_drive_id = url.split("/d/")[1].split("/")[0]
    #
    #            # get pdf by id
    #            pdf_bytes = self.g_docs_proc.export_pdf(google_drive_id)
    #
    #            # get content from pdf
    #            pdf_content += self.pdf_reader.read_pdf(pdf_bytes) + " "

    #        return pdf_content

    def get_content_from_page_attachments(self, page_id) -> str:
        start = 0
        limit = 100
        attachments = []

        number_of_attachments = self.confluence.get_attachments_from_content(
            page_id=page_id, start=start, limit=limit)["size"]
        pdf_content = ""

        if number_of_attachments > 0:
            # iterate over all attachments
            while True:
                attachments_container = self.confluence.get_attachments_from_content(
                    page_id=page_id, start=start, limit=limit
                )

                attachments.extend(attachments_container["results"])

                # Check if there are more spaces
                if len(attachments_container) < limit:
                    break
                start = start + limit

            if len(attachments) > 0:
                for attachment in attachments:

                    if "application/pdf" == attachment["extensions"]["mediaType"]:
                        download_link = (
                                self.confluence.url + attachment["_links"]["download"]
                        )
                        r = requests.get(
                            download_link,
                            auth=(self.confluence.username, self.confluence.password),
                        )

                        if r.status_code == 200:
                            pdf_bytes = io.BytesIO(r.content).read()

                            try:
                                pdf_content += self.pdf_reader.read_pdf(pdf_bytes) + " "
                                print(
                                    f"Content: {pdf_content}, Page id: {page_id}, Attachment: {attachment['title']}, Link: {download_link}")
                            except Exception as e:
                                print(f"Error while reading pdf: {e}")
                                print(
                                    f"Page id: {page_id}, Attachment: {attachment['title']}, Link: {download_link}")
                                continue
        return pdf_content

    # set parent page for all pages and set the toc path
    def set_parent_and_fill_title(self):
        # create a map structure with page_id as key and page as value
        page_map: dict[str, ConfluencePage] = {}
        for page in self.page_information:
            page_map[page.page_id] = page

        # iterate over all pages
        for page in self.page_information:
            # iterate over all child pages
            for child_page_id in page.child_pages:
                # set parent page
                page_map[child_page_id].parent_page = page.page_id

        # based on the parent page, set the toc path
        # iterate over all pages
        for page in self.page_information:
            path = ""
            iterate_page = page
            # iterate over all parent pages
            while iterate_page.parent_page is not None:
                # add parent page to path
                path = iterate_page.title + " / " + path
                # set next parent page
                iterate_page = page_map[iterate_page.parent_page]
            # set path
            page.title = path

    def load_preprocessed_data(
            self, end_of_timeframe: datetime, start_of_timeframe: datetime
    ) -> List[DocumentDto]:

        all_spaces: List[str] = self.get_all_spaces()
        for space in all_spaces:
            print("Load Space: " + space)
            page_ids: List[str] = self.get_page_ids_from_spaces(space)

            for page_id in tqdm(page_ids):
                page = self.get_data_from_page(page_id)
                self.page_information.append(page)

        self.set_parent_and_fill_title()
        return [data.to_document_data() for data in self.page_information]


if __name__ == "__main__":
    cf = ConfluenceFetcher()

    date_string = "2070-01-01"
    format_string = "%Y-%m-%d"

    z = cf.load_preprocessed_data(
        datetime.now(),
        datetime.strptime(date_string, format_string),
    )
    for i in z:
        print(i.uniq_id)
        print(i.format)
        print(i.title)
        print(i.last_changed)
        print("length:", len(i.content))
        # print(i.content)
        print("----" * 5)
