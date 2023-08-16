# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Emanuel Erben
# SPDX-FileCopyrightText: 2023 Felix Nützel
# SPDX-FileCopyrightText: 2023 Jesse Palarus
# SPDX-FileCopyrightText: 2023 Amela Pucic
from __future__ import annotations  # todo: remove when python 3.10 is installed (for local use)

import os
from time import time
from xml.dom.minidom import Document

from huggingface_hub import hf_hub_download
from langchain import LlamaCpp, PromptTemplate
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import Weaviate
from weaviate.embedded import EmbeddedOptions
import weaviate
from typing import List, Dict, Any

from QAChat.Common.deepL_translator import DeepLTranslator
from QAChat.QA_Bot.stream_LLM_callback_handler import StreamLLMCallbackHandler
from QAChat.Common.bucket_managing import download_database

from typing import List, Dict, Any, Union
from weaviate.client import Client
from weaviate.util import _get_dict_from_object

# Get WEAVIATE_URL
WEAVIATE_URL = os.getenv("WEAVIATE_URL")


class QABot:
    def __init__(
            self,
            embeddings=None,
            database=None,
            model=None,
            translator=None,
            embeddings_gpu=False,
            repo_id="TheBloke/WizardLM-13B-V1-1-SuperHOT-8K-GGML",
            filename="wizardlm-13b-v1.1-superhot-8k.ggmlv3.q5_0.bin",
    ):
        self.answer = None
        self.context = None
        # download_database()
        self.embeddings = embeddings
        if embeddings is None:
            self.embeddings = HuggingFaceInstructEmbeddings(
                model_name="hkunlp/instructor-xl",
                model_kwargs=None if embeddings_gpu else {"device": "cpu"},
            )

        self.database = database
        if database is None:
            client = weaviate.Client(url=WEAVIATE_URL)
            self.database = Weaviate(
                client=client,
                embedding=self.embeddings,
                index_name="Embeddings",
                text_key="text",
            )
        self.model = model
        if model is None:
            self.model = self.get_llama_model(repo_id=repo_id, filename=filename)
        self.client = weaviate.Client(url=WEAVIATE_URL)
        # self.translator = translator
        # if translator is None:
        #     self.translator = DeepLTranslator()

    def get_llama_model(
            self,
            repo_id,
            filename,
            n_ctx=2048,
            max_tokens=512,
    ):
        path = hf_hub_download(repo_id=repo_id, filename=filename)

        return LlamaCpp(
            model_path=path,
            verbose=False,
            n_ctx=n_ctx,
            max_tokens=max_tokens,
            temperature=0,
            n_gpu_layers=100,
            repeat_penalty=0.9,
            n_batch=256,
        )

    def answer_question_with_context(
            self, question: str, context: List[str], handler=None
    ) -> str:
        """
        This method takes a question and a list of context strings as input, and attempts to answer the question using the provided context.

        The method uses the context to understand the scope and reference points for the given question and then formulates an answer based on that context.

        Parameters:
        question (str): The question that needs to be answered. This should be a string containing a clear, concise question.

        context (list[str]): A list of strings providing context for the question. The list should provide relevant information that can be used to answer the question.

        Returns:
        str: The method returns a string that contains the answer to the question, formulated based on the provided context.

        Example:
        >> ask_question("What is the color of the sky?", ["The sky is blue during a clear day."])
        'The sky is blue during a clear day.'
        """

        context_str = "\n\n".join(f"{x}" for i, x in enumerate(context))

        template = (
            "You are a chatbot, your primary task is to help people by answering their questions. Keep your responses short, precise, and directly related to the user's question, using the following context to guide your answer:\n"
            "{context_str}\n\n"
            "Try your best to answer based on the given context, and avoid creating new information. If the context does not provide enough details to formulate a response, or if you are unsure, kindly state that you can't provide a certain answer.\n"
            "\n\n"
            "USER: {question}"
            "ASSISTANT:"
        )
        prompt = PromptTemplate(
            template=template, input_variables=["question", "context_str"]
        )

        print(prompt.format_prompt(question=question, context_str=context_str))
        answer = self.model.generate_prompt(
            [
                prompt.format_prompt(question=question, context_str=context_str),
            ],
            stop=["</s>"],
            callbacks=None if handler is None else [handler],
        )
        return answer.generations[0][0].text.strip()

    def __sim_search(self, question: str) -> dict[str, list[str | dict[str, Any]]]:
        """
        This method uses the given question to conduct a similarity search in the database, retrieving the most relevant information for answering the question.

        The method parses the question, identifies key words and phrases, and uses these to perform a similarity search in the database. The results of the search, which are the pieces of information most similar or relevant to the question, are then returned as a list of strings.

        Parameters:
        question (str): The question that needs to be answered. This should be a string containing a clear, concise question.

        Returns:
        list[str]: The method returns a list of strings, each string being a piece of information retrieved from the database that is considered relevant for answering the question.

        Example:
        >> sim_search("What is the color of the sky?")
        ['The sky is blue during a clear day.', 'The color of the sky can change depending on the time of day, weather, and location.']

        Note: The actual return value will depend on the contents of your database.
        """
        embedding = self.embeddings.embed_query(question)
        # return [
        #     context.page_content
        #     for context in self.database.similarity_search_by_vector(embedding, k=3)
        # ]

        # Search for similar documents and get the metadata and content arrays
        result = self.search_similar_documents(
            client=self.client,
            embedding=embedding,
            k=3,
            text_key=["text"],
            metadata_fields=["link"],
        )
        # Convert the result to a dictionary with metadata and content arrays
        metadata_list = [doc["metadata"] for doc in result]
        content_list = [doc["content"] for doc in result]
        result_dict = {"metadata": metadata_list, "content": content_list}
        return result_dict

    def search_similar_documents(
            self,
            client: weaviate.Client,
            embedding: List[float],
            k: int = 3,
            index_name: str = "Embeddings",
            text_key: Union[str, List[str]] = "text",
            metadata_fields: Union[str, List[str]] = None,
    ) -> List[Dict[str, Union[str, Dict[str, Any]]]]:
        """A method to search for similarity in the database. This method is based on the Weaviate
        similarity_search_by_vector method. Becuase the original method does not allow several text keys (e.g. text
        and link), this method is used instead
        Parameters:
            client (weaviate.Client): The Weaviate client object
            embedding (List[float]): The embedding of the question
            k (int): The limit of the number of results
            index_name (str): The name of the index to search in
            text_key (Union[str, List[str]]): The name of the text key(s) to search in
            metadata_fields (Union[str, List[str]]): The name of the metadata field(s) to search in

        Returns:
            List[Dict[str, Union[str, Dict[str, Any]]]]: A list of dictionaries containing the metadata and content of the
            most similar documents (content is the text_key(s), metadata is the metadata_fields)
            """
        # Convert text_key and metadata_fields to lists if they are strings
        metadata_fields = metadata_fields
        # If metadata_fields is not specified, use all metadata fields
        if metadata_fields is None:
            metadata_fields = client.schema.get_properties_of_kind(index_name, include_inherited=True)
        # Include the metadata fields in the query
        fields = text_key + metadata_fields
        # Search for similar documents and get the metadata and content
        try:
            vector = {"vector": embedding}
            query_obj = client.query.get(
                index_name,
                [key for key in fields],
            )
            result = query_obj.with_near_vector(vector).with_limit(k).do()
        except Exception as e:
            return []
        docs = []
        for res in result["data"]["Get"][index_name]:
            # Get the page content from the text_key(s)
            page_content = " ".join([res.get(key, "") for key in text_key])
            # Get the metadata fields
            metadata = {key: res.get(key, "") for key in metadata_fields}
            docs.append({"metadata": metadata, "content": page_content})
        return docs

    # def translate_text(self, question, language="EN-US"):
    #     return self.translator.translate_to(
    #         question, language, use_spacy_to_detect_lang_if_needed=False
    #     )

    def answer_question(self, question: str, handler: StreamLLMCallbackHandler | None):
        """
        This method takes a user's question as input and returns an appropriate answer.

        Parameters:
        question (str): The question that needs to be answered. This should be a string containing a clear, concise question.


        Returns:
        str: The method returns a string that contains the answer to the question.

        Example:
        >> answer_question("What is the color of the sky?")
        'The sky is blue during a clear day.'
        """

        print(f"Receive Question: {question}")
        # translation = self.translate_text(question)
        # if handler is not None:
        #     handler.lang = translation.detected_source_lang

        # translated_question = translation.text
        print(f"Translation: {question}")
        context = self.__sim_search(question)
        print(context["content"])
        print(context["metadata"])
        print(f"Context: {context}")
        answer = self.answer_question_with_context(
            question, context["content"], handler
        )
        print(f"Answer: {answer}")
        # if translation.detected_source_lang != "EN-US":
        #     answer = self.translate_text(answer, translation.detected_source_lang).text

        print(f"Translated answer: {answer}")
        return {
            "answer": answer,
            "question": question,
            "context": context,
        }


if __name__ == "__main__":
    qa_bot = QABot()
    start = time()
    qa_bot.answer_question("What is the color of the sky?", None)
    print(f"Time: {time() - start}")
