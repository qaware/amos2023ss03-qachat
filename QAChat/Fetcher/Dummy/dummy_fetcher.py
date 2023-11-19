from datetime import datetime, timezone
from typing import List

import pandas as pd

from QAChat.Fetcher.data_fetcher import DataFetcher
from QAChat.VectorDB.Documents.document_data import DocumentData, DocumentDataFormat, DocumentDataSource


class DummyFetcher(DataFetcher):

    def get_source(self) -> DocumentDataSource:
        return DocumentDataSource.DUMMY

    def load_preprocessed_data(
        self, end_of_timeframe: datetime, start_of_timeframe: datetime
    ) -> List[DocumentData]:
        df = pd.read_csv("./DummyData/qa.csv", sep=";")

        raw_data = []
        for index, row in df.iterrows():
            raw_data.append(
                DocumentData(
                    uniq_id=f"{index}",
                    _format=DocumentDataFormat.TEXT,
                    last_changed=datetime(2021, 1, 1, tzinfo=timezone.utc),
                    data_source=DocumentDataSource.DUMMY,
                    content=row["Answer"],
                    link="https://www.test.com",
                )
            )

        return [data for data in raw_data]
