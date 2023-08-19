# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic

from datetime import datetime
from typing import List

import pandas as pd

from QAChat.Data_Processing.preprocessor.data_information import DataInformation, DataSource
from QAChat.Data_Processing.preprocessor.data_preprocessor import DataPreprocessor


class DummyPreprocessor(DataPreprocessor):

    def get_source(self) -> DataSource:
        return DataSource.DUMMY

    def load_preprocessed_data(
        self, end_of_timeframe: datetime, start_of_timeframe: datetime
    ) -> List[DataInformation]:
        df = pd.read_csv("./DummyData/qa.csv", sep=";")

        raw_data = []
        for index, row in df.iterrows():
            raw_data.append(
                DataInformation(
                    id=f"{index}",
                    last_changed=datetime(2021, 1, 1),
                    typ=DataSource.DUMMY,
                    text=row["Answer"],
                    link="https://www.test.com",
                )
            )

        return [
            data
            for data in raw_data
        ]
