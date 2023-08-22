# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Hafidz Arifin
# SPDX-FileCopyrightText: 2023 Abdelkader Alkadour

import io
import os
import re
from datetime import datetime
from typing import List

import requests
from atlassian import Confluence

from QAChat.Common.blacklist_reader import read_blacklist_items
from QAChat.Common.vectordb import VectorDB
from QAChat.Data_Processing.pdf_reader import PDFReader
from QAChat.Data_Processing.preprocessor.data_information import DataInformation, DataSource
from QAChat.Data_Processing.preprocessor.data_preprocessor import DataPreprocessor
from QAChat.Data_Processing.preprocessor.google_doc_preprocessor import GoogleDocPreProcessor
from QAChat.Data_Processing.preprocessor.html_to_text import get_text

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


class ConfluencePreprocessor(DataPreprocessor):
    def __init__(self):
        self.db = VectorDB()
        self.confluence = Confluence(
            url=CONFLUENCE_ADDRESS,
            username=CONFLUENCE_USERNAME,
            password=CONFLUENCE_TOKEN,
            cloud=True,
        )
        self.pdf_reader = PDFReader()
        self.__all_spaces = []
        self.all_pages_id = []
        self.all_page_information = []
        self.restricted_pages = []
        self.restricted_spaces = []
        self.db = VectorDB()
        self.last_update_lookup = dict()
        self.chunk_id_lookup_table = dict()
        self.g_docs_proc = GoogleDocPreProcessor()
        self.pdf_reader = PDFReader()

    def get_source(self) -> DataSource:
        return DataSource.CONFLUENCE

    def init_blacklist(self):
        # Retrieve blacklist data from file
        blacklist = read_blacklist_items()

        # Extract restricted spaces and restricted pages from the blacklist data
        for entries in blacklist:
            if "/pages/" in entries.identifier:
                # Split by slash and get the page id, https://.../pages/PAGE_ID
                self.restricted_pages.append(entries.identifier.split("/")[7])
            else:
                # Split by slash and get the space name, https://.../space/SPACE_NAME
                self.restricted_spaces.append(entries.identifier.split("/")[5])

    def get_all_spaces(self):
        start = 0
        limit = 500
        all_spaces = []
        if len(self.__all_spaces) > 0:
            return self.__all_spaces
        # Get all spaces first
        while True:
            # url:      to the confluence parameter
            # username: to your email used in confluence
            # password: if confluence is cloud set Confluence API Token https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
            #           if confluence is server set your password
            # cloud:    True if confluence is cloud version

            # Get all confluence spaces from the confluence instance
            spaces_data = self.confluence.get_all_spaces(
                start=start, limit=limit, expand=None
            )
            for space in spaces_data["results"]:
                # exclude personal/user spaces only global spaces
                if space["type"] == "global":
                    # exclude blacklisted spaces
                    if space["key"] not in self.restricted_spaces and space["key"] in CONFLUENCE_SPACE_WHITELIST:
                        all_spaces.append(space)

            # Check if there are more spaces
            if len(spaces_data) < limit:
                break
            start = start + limit
        return all_spaces

    def get_all_page_ids_from_spaces(self):
        # Get all pages from a space
        for space in self.__all_spaces:
            start = 0
            limit = 100

            while True:
                pages_data = self.confluence.get_all_pages_from_space(
                    space["key"],
                    start=start,
                    limit=limit,
                    status=None,
                    expand=None,
                    content_type="page",
                )
                #  Get all page id
                for page in pages_data:
                    if page["id"] not in self.restricted_pages:
                        self.all_pages_id.append(page["id"])

                # Check if there are more pages
                if len(pages_data) < limit:
                    break
                start = start + limit

    def get_relevant_data_from_pages(self):
        # Get all relevant information from each page
        for page_id in self.all_pages_id:
            # Get page by id

            page_with_body = self.confluence.get_page_by_id(
                page_id, expand="body.storage, version", status=None, version=None
            )
            page_info = self.confluence.get_page_by_id(
                page_id, expand=None, status=None, version=None
            )
            # Set final parameters for DataInformation
            last_changed = self.get_last_modified_formatted_date(page_info)
            text = self.get_raw_text_from_page(page_with_body)

            # skip pages with less than 5 characters
            if len(text) < 5:
                continue

            # get googledoc url:
            urls = re.findall(r"https?://docs\.google\.com\S+", text)

            # get content from googledoc
            # commented out because we don't have access tho client's google drive
            # google_doc_content = self.get_content_from_google_drive(urls)

            # get content from confluence attachments
            pdf_content = ""  # self.get_content_from_page_attachments(page_id)

            # replace consecutive occurrences of \n into one \n
            text = re.sub(r"\n+","\n",  text)
            # replace " \n" with "\n"
            text = re.sub(r" \n","\n",  text)
            # remove leading \n
            text = re.sub(r"^\n", "", text)

            # commented out because we don't have access tho client's google drive
            # + " " + google_doc_content
            # + " " + pdf_content,

            # print(f"Länge {page_id}: %d \n" % len(text))
            # Add Page content to list of DataInformation
            # print(page_info["_links"]["base"] + page_info["_links"]["webui"].split("overview")[0])
            self.all_page_information.append(
                DataInformation(
                    id=page_id,
                    last_changed=last_changed,
                    typ=DataSource.CONFLUENCE,
                    text=text,
                    title=page_info["title"],
                    space=page_info["space"]["key"],
                    link=page_info["_links"]["base"] + page_info["_links"]["webui"].split("overview")[0],
                )
            )

    def get_last_modified_formatted_date(self, page_info) -> datetime:
        # Get date of last modified page
        data_last_changed = page_info["version"]["when"]
        year_string = data_last_changed[0:4]
        month_string = data_last_changed[5:7]
        day_string = data_last_changed[8:10]

        # Convert string to int
        year = int(year_string)
        month = int(month_string)
        day = int(day_string)

        return datetime(year, month, day)


    def get_raw_text_from_page(self, page_with_body) -> str:
        # Get page content
        page_in_html = page_with_body["body"]["storage"]["value"]
        #return page_in_html
        return get_text(page_in_html)

    def get_content_from_google_drive(self, urls):
        pdf_content = ""

        # go through all urls
        for url in urls:
            # get id from url
            google_drive_id = url.split("/d/")[1].split("/")[0]

            # get pdf by id
            pdf_bytes = self.g_docs_proc.export_pdf(google_drive_id)

            # get content from pdf
            pdf_content += self.pdf_reader.read_pdf(pdf_bytes) + " "

        return pdf_content

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
                                    f"Content: {pdf_content}, Page id: {page_id}, Attachment: {attachment['title']}, Link: {download_link}, Space: {self.all_page_information[-1].space}")
                            except Exception as e:
                                print(f"Error while reading pdf: {e}")
                                print(
                                    f"Page id: {page_id}, Attachment: {attachment['title']}, Link: {download_link}, Space: {self.all_page_information[-1].space}")
                                continue
        return pdf_content

    def load_preprocessed_data(
            self, end_of_timeframe: datetime, start_of_timeframe: datetime
    ) -> List[DataInformation]:
        self.init_lookup_tables()
        self.init_blacklist()
        self.__all_spaces = self.get_all_spaces()
        self.get_all_page_ids_from_spaces()
        self.get_relevant_data_from_pages()
        self.filter_pages()
        return [data for data in self.all_page_information]

    def init_lookup_tables(self):
        # get the metadata of type Confluence from DB
        data = self.db.get_all_for_type("confluence")

        for d in data:
            # add each ID in dict last_update_lookup
            if d.page_id not in self.last_update_lookup:
                self.last_update_lookup[d.page_id] = datetime.strptime(
                    d.last_update.split("T")[0], "%Y-%m-%d"
                )

            # add max of chunk ID to chunk_id_lookup_table
            if d.page_id not in self.chunk_id_lookup_table:
                self.chunk_id_lookup_table[d.page_id] = d.chunk_id
            else:
                if d.chunk_id > self.chunk_id_lookup_table[d.page_id]:
                    self.chunk_id_lookup_table[d.page_id] = d.chunk_id

    def filter_pages(self):
        to_delete = []
        for i in self.all_page_information:
            if i.id in self.last_update_lookup:  # if page is already in DB
                if (
                        i.last_changed > self.last_update_lookup[i.id]
                ):  # if there is a change in the page
                    self.remove_from_db(i.id)  # remove from DB
                    self.last_update_lookup[i.id] = None  # make the dict's entry None -> To detect remove page
                elif (
                        i.last_changed == self.last_update_lookup[i.id]
                ):  # if no change in the page
                    to_delete.append(i)  # append in the list
                    self.last_update_lookup[
                        i.id
                    ] = None  # make the dict's entry None -> To detect remove page
            # if i.last_changed.year >= 2022:
            #    to_delete.append(i)

        for i in to_delete:
            self.all_page_information.remove(
                i
            )  # remove the page where no changes from the internal list

        for i in self.last_update_lookup:
            if (
                    self.last_update_lookup[i] is not None
            ):  # check which entry is not None -> Page is deleted from website
                self.remove_from_db(i)  # remove it from DB

    def remove_from_db(self, id):
        # loop over max number in chunk id and remove all the rows from DB
        for i in range(0, int(self.chunk_id_lookup_table[id]) + 1):
            self.db.weaviate_client.batch.delete_objects(
                "Embeddings",
                {
                    "path": ["type_id"],
                    "operator": "Equal",
                    "valueString": str(id) + "_" + str(i),
                },
            )

    def create_whitelist(self):
        spaces = self.get_all_pages_for_whitelist()
        output = ""  # TODO: current output for the whitelist
        for space in spaces:
            output += space["key"] + ","
        print(output)

    def get_all_pages_for_whitelist(self):
        start = 0
        limit = 500

        whitelist = []
        # Get all spaces first
        while True:
            # url:      to the confluence parameter
            # username: to your email used in confluence
            # password: if confluence is cloud set Confluence API Token https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
            #           if confluence is server set your password
            # cloud:    True if confluence is cloud version

            # Get all confluence spaces from the confluence instance
            spaces = self.confluence.get_all_spaces(
                start=start, limit=limit, expand=None
            )

            for space in spaces["results"]:
                # exclude personal/user spaces only global spaces
                if space["type"] == "global":
                    # exclude blacklisted spaces
                    if space["key"] not in self.restricted_spaces and space["key"].startswith("QAWARE") or space["key"].startswith("QAware"):
                        whitelist.append(space)

            # Check if there are more spaces
            if len(spaces) < limit:
                break
            start = start + limit
        return whitelist


if __name__ == "__main__":
    cp = ConfluencePreprocessor()

    date_string = "2070-01-01"
    format_string = "%Y-%m-%d"

    z = cp.load_preprocessed_data(
        datetime.now(), datetime.strptime(date_string, format_string)
    )
    for i in z:
        print(i.space)
        print(i.id)
        print(i.title)
        print(i.text)
        print(len(i.text))
        print(i.typ)
        print(i.last_changed)
        print("----" * 5)

    cp.create_whitelist()
