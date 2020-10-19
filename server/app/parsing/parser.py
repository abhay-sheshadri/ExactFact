from app.parsing.sentence import Sentence

import spacy
import neuralcoref
import claucy
from app.database.database import *
import re
import os
from io import StringIO
from html.parser import HTMLParser

# Initialize SpaCy parsers
nlp = spacy.load("en")
neuralcoref.add_to_pipe(nlp, greedyness=0.5, blacklist=False)
claucy.add_to_pipe(nlp)


def parse_into_sentences(text):
    """
    Parses text into a set of valid sentences
    """
    return [Sentence(sent) for sent in split_into_sentences(text) if valid_sentence(sent)]


def split_into_sentences(text, min_chars_per_element=15, min_words_per_element=4):
    """
    Takes in a string
    Returns a list of setntences
    """
    # Tokenize
    sents = []
    for section in re.split("\t|\n|\r|\xa0|\x0b|\x0c", text):
        if len(section) >= min_chars_per_element:
            docx = nlp(section)
            if len(docx) <= min_words_per_element:
                continue
            sents += list(docx.sents)
    return sents


def valid_sentence(sent):
    """
    Checks if there is a verb and two noun in the sent span
    """
    # Check for two nouns
    has_noun = len(list(sent.noun_chunks)) >= 2
    # Check for one verb
    for token in sent:
        if token.pos_ == "VERB":
            return has_noun
    return False
    

class Misinformation():
    """
    Class for adding misinformation 
    """

    def __init__(self, misinfo, link, info, clean_html=False, split=False):
        open_database() # Open database over here
        # Clean up the text
        misinfo = misinfo.replace("\n", "").replace("\r", "").replace("\t", "")
        if clean_html:
            misinfo = self.strip_tags(misinfo)
        # Encode and put the stuff into the database
        misinfo_sent = Sentence(nlp(misinfo)[:], get_propositions=split)
        insert_sentence_object(misinfo, link, info, misinfo_sent.embeddings)
    def strip_tags(self, html):
        s = self.MLStripper()
        s.feed(html)
        return s.get_data()

    class MLStripper(HTMLParser):
    
        def __init__(self):
            super().__init__()
            self.reset()
            self.strict = False
            self.convert_charrefs= True
            self.text = StringIO()
    
        def handle_data(self, d):
            self.text.write(d)
    
        def get_data(self):
            return self.text.getvalue()

