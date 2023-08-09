# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus

import json
import os

import requests
from dotenv import load_dotenv
from get_tokens import get_tokens_path

load_dotenv(get_tokens_path())


class QABotAPIInterface:
    def request(self, question):
        url = os.getenv("GOOGLE_CLOUD_QA_BOT")
        try:
            response = requests.post(url, json={"question": question}, stream=True, timeout=20) # timeout in seconds, default is 20 seconds, throw exception if timeout
            for line in response.iter_lines():
            # filter out keep-alive new lines
                if line:
                    decoded_line = line.decode("utf-8")
                    data = json.loads(decoded_line)
                    yield data["text"]

        except requests.exceptions.Timeout:
            print("Timeout")
            # yield "Sorry, I am not able to answer your question right now. Please try again later."
            raise Exception("Timeout")


        
