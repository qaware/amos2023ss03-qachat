# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Jesse Palarus

import json
import os

import requests

class QABotAPIInterface:
    def request(self, question):
        url = os.getenv("QA_BOT_URL")
        if url is None:
            raise Exception("QA_BOT_URL not set")

        try:
            response = requests.post(url, json={"question": question}, stream=True, timeout=40) # timeout in seconds, default is 20 seconds, throw exception if timeout
            for line in response.iter_lines():
            # filter out keep-alive new lines
                if line:
                    decoded_line = line.decode("utf-8")
                    data = json.loads(decoded_line)
                    if "text" in data and "links" in data:
                        yield str(data["text"]), data["links"]
                    elif "text" in data:
                        yield str(data["text"]), None
                    elif "links" in data:
                        yield None, data["links"]
                    else:
                        print("No text or links in data")
                        raise Exception("The response from the API did not contain any text or links.")

        except requests.exceptions.Timeout:
            print("Timeout")
            # yield "Sorry, I am not able to answer your question right now. Please try again later."
            raise Exception("Timeout")


        
