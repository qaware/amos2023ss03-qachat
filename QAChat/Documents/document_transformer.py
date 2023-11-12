from QAChat.Common.deepL_translator import DeepLTranslator
from QAChat.Documents.html_to_text import get_text_markdonify
from QAChat.VectorDB.Documents.document_data import DocumentData, DocumentDataFormat


class DocumentTransformer:

    def __init__(self):
        self.translator = DeepLTranslator()

    def transform(self, documents: list[DocumentData]):
        print("Loaded " + str(len(documents)) + " documents.")

        for idx in range(len(documents)):
            content = documents[idx].content

            # remove html tags
            if documents[idx].format == DocumentDataFormat.CONFLUENCE:
                content = get_text_markdonify(content)

            # translate text
            documents[idx].content = self.translator.translate_to(content, "EN-US").text
            documents[idx].format = DocumentDataFormat.TEXT
