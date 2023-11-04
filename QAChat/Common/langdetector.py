import spacy
from spacy.language import Language
from spacy_language_detection import LanguageDetector

class LangDetector:

    def __init__(self):
        # name identification
        #spacy.cli.download("xx_ent_wiki_sm")
        #spacy.load("xx_ent_wiki_sm")
        #self.multi_lang_nlp = xx_ent_wiki_sm.load()
        #spacy.cli.download("de_core_news_sm")
        #spacy.load("de_core_news_sm")
        #self.de_lang_nlp = de_core_news_sm.load()

        #self.de_lang_nlp = spacy.load("de_core_news_sm")
        self.multi_lang_nlp = spacy.load("xx_ent_wiki_sm")
        Language.factory("language_detector", func=self.get_lang_detector)

        if "sentencizer" not in self.multi_lang_nlp.pipe_names:
            self.multi_lang_nlp.add_pipe("sentencizer")
        if "language_detector" not in self.multi_lang_nlp.pipe_names:
            self.multi_lang_nlp.add_pipe("language_detector", last=True)

    def get_lang_detector(self, nlp, name):
        return LanguageDetector()

    def get_language_details(self, text):
        doc = self.multi_lang_nlp(text)
        return doc._.language

    def get_language(self, text):
        doc = self.multi_lang_nlp(text)
        if doc._.language["score"] > 0.8:
            return doc._.language["language"]
        else:
            return "unknown"

if __name__ == "__main__":
    langdetect = LangDetector()
    print(langdetect.get_language_details("Hello everyone!"))
    print(langdetect.get_language_details("How are you?"))
    print(langdetect.get_language_details("Wie geht es Ihnen?"))
