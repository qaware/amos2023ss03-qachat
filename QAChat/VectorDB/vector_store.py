import os
from typing import Any, List, Dict, Union

from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import Weaviate

from QAChat.Processors.preprocessor.data_information import DataInformation
from QAChat.VectorDB.vectordb import VectorDB

class VectorStore:
    def __init__(self, embeddings_gpu=True):
        self.db = VectorDB()
        VECTORIZER_DEVICE: str = os.getenv("VECTORIZER_DEVICE")
        if VECTORIZER_DEVICE is None:
            raise Exception("VECTORIZER_DEVICE is not set")

        self.embedder = HuggingFaceInstructEmbeddings(
            model_name="hkunlp/instructor-xl",
            model_kwargs={"device": VECTORIZER_DEVICE},
        )

        self.vector_store = Weaviate(
            client=self.db.weaviate_client,
            embedding=self.embedder,
            index_name="Embeddings",
            text_key="text",
        )

    def update_add_texts(self, all_changed_data : list[DataInformation]):
        print("delete texts")

        ids: set[str] = set()
        for data in all_changed_data:
            ids.add(data.id)

        for type_id in ids:
            self.db.weaviate_client.batch.delete_objects(
                "Embeddings",
                where={
                    "path": ["type_id"],
                    "operator": "Equal",
                    "valueString": type_id,
                },
            )
        print("store texts")

        self.vector_store.add_texts(
            [data.text for data in all_changed_data],
            [
                {
                    "type_id": data.id,
                    "chunk": data.chunk,
                    "type": data.typ.value,
                    "last_changed": data.last_changed.isoformat(),
                    "text": data.text,
                    "link": data.link,
                }
                for data in all_changed_data
            ],
        )

    def sim_search(self, question: str) -> dict[str, list[str | dict[str, Any]]]:
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
        embedding: List[float] = self.embedder.embed_query(question)
        # return [
        #     context.page_content
        #     for context in self.database.similarity_search_by_vector(embedding, k=3)
        # ]

        # Search for similar documents and get the metadata and content arrays
        result = self.search_similar_documents(
            k=3,
            embedding=embedding,
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
            metadata_fields = self.db.weaviate_client.schema.get_properties_of_kind(index_name, include_inherited=True)
        # Include the metadata fields in the query
        fields = text_key + metadata_fields
        # Search for similar documents and get the metadata and content
        try:
            vector = {"vector": embedding}
            query_obj = self.db.weaviate_client.query.get(
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
