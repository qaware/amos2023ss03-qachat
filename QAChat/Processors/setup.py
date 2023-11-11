import spacy.cli
import xx_ent_wiki_sm

spacy.cli.download("xx_ent_wiki_sm")
spacy.load("xx_ent_wiki_sm")
xx_ent_wiki_sm.load()
