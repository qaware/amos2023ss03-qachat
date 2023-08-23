# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Emanuel Erben
# SPDX-FileCopyrightText: 2023 Felix Nützel
# SPDX-FileCopyrightText: 2023 Jesse Palarus

import os

import deepl
import xx_ent_wiki_sm
from spacy import Language
from spacy_langdetect import LanguageDetector

DEEPL_TOKEN = os.getenv("DEEPL_TOKEN")
if DEEPL_TOKEN is None:
    raise Exception("DEEPL_TOKEN not set")

TRANSLATE = os.getenv("TRANSLATE")
if TRANSLATE is None:
    raise Exception("TRANSLATE not set")


class Result:
    def __init__(self, text, detected_source_lang):
        self.text = text
        self.detected_source_lang = detected_source_lang


class DeepLTranslator:
    def __init__(self):
        if not TRANSLATE:
            return
        # initialize a DeepL translator service
        self.translator = deepl.Translator(DEEPL_TOKEN)
        self.multi_lang_nlp = xx_ent_wiki_sm.load()
        Language.factory("language_detector", func=self.get_lang_detector)
        if "sentencizer" not in self.multi_lang_nlp.pipe_names:
            self.multi_lang_nlp.add_pipe("sentencizer")
        if "language_detector" not in self.multi_lang_nlp.pipe_names:
            self.multi_lang_nlp.add_pipe("language_detector", last=True)

    def translate_to(self, text, target_lang, use_spacy_to_detect_lang_if_needed=True) -> Result:
        if not TRANSLATE:
            return Result(text, "EN_US")

        if use_spacy_to_detect_lang_if_needed:
            doc = self.multi_lang_nlp(text)
            if (
                    doc._.language["language"] == "en"
                    and doc._.language["score"] > 0.8
                    and target_lang == "EN-US"
            ):
                return Result(text, "EN_US")

        try:
            translated_text = self.translator.translate_text(
                text, target_lang=target_lang, ignore_tags="name"
            )
        except Exception as e:
            print("Error while translating text: ", e)
            return Result(text, "EN-US")
        if translated_text.detected_source_lang == "EN":
            translated_text.detected_source_lang = "EN-US"
        elif translated_text.detected_source_lang == "PT":
            translated_text.detected_source_lang = "PT-PT"
        return Result(translated_text.text, translated_text.detected_source_lang)

    def get_lang_detector(self, nlp, name):
        return LanguageDetector()


if __name__ == "__main__":
    translator = DeepLTranslator()
    result = translator.translate_to("Was sind xyhj", "EN-US")
    result2 = translator.translate_to("How are you", "EN-US")

    print(result.text)
    print(result.detected_source_lang)
    print(result2.text)
    print(result2.detected_source_lang)
