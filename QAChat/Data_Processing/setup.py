import spacy
import spacy.cli
import xx_ent_wiki_sm
import de_core_news_sm

spacy.cli.download("xx_ent_wiki_sm")
spacy.load("xx_ent_wiki_sm")
xx_ent_wiki_sm.load()

spacy.cli.download("de_core_news_sm")
spacy.load("de_core_news_sm")
de_core_news_sm.load()