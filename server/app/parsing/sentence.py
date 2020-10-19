from transformers import DistilBertTokenizer
from sentence_transformers import SentenceTransformer
import os
from itertools import combinations
import numpy as np

tokenizer = DistilBertTokenizer(os.path.join("app", "models", "0_Transformer", "vocab.txt"))
model = SentenceTransformer(model_name_or_path=os.path.join("app", "models"))


class Sentence():
    """
    Class for managing sentences
    """

    def __init__(self, span, resolve_coreferences=True, get_propositions=True, max_length=None):
        """
        resolve_coreferences: whether the detected coreferences should be resolved
        max_length: the number of ids (includes the start token)
        """

        self.main_span = span
        self.embeddings = []

        if resolve_coreferences:
            self.tokens = self.resolve_coreferences(span)
        else:
            self.tokens = list(span)
        
        self.ids = [self.get_ids(self.tokens)]
        # Not used because of glitches in the python package
        if get_propositions:
            props = self.get_propositions()
            self.ids += [self.get_ids(proposition) for proposition in props]

        #if max_length:
        #    self.ids = ids[0][:max_length]

        self.embeddings = self.get_embeddings()

    def get_propositions(self):
        """
        Extracts the propositions from the sentences
        """
        props = []
        for clause in self.main_span._.clauses:
            prop = []
            adverbials = [adverbial for adverbial in clause.adverbials if len(adverbial) > 1]
            # If we are like any of these, just skip
            if clause.subject == None or clause.verb == None or (clause.type =="SV" and len(adverbials) == 0):
                continue
            # add subject and verb to proposition
            prop += list(clause.subject)
            prop += list(clause.verb)
            # Add indirect, direct, and complement in order
            if clause.indirect_object:
                prop += list(clause.indirect_object)
            if clause.direct_object:
                prop += list(clause.direct_object)
            if clause.complement:
                prop += list(clause.complement)
            # If there are adverbials, then iterate through all possible combinations of them
            # Messy way to do it but good enough for now
            start = 0
            for i in range(start, len(adverbials) + 1):
                for combo in combinations(adverbials, i):
                    ad = []
                    for adverbial in combo:
                        ad += list(adverbial)
                    props.append(prop + ad)
        return [self.resolve_coreferences(prop) for prop in props]

    def get_embeddings(self):
        """
        Puts the tokenized ids through the DistilBert model
        """
        return  model.encode(self.ids, is_pretokenized=True, convert_to_numpy=True)

    def resolve_coreferences(self, sent):
        """
        Create a list of words with coreferences replaced with main reference in cluster
        """
        tokens = []
        i = 0
        while i < len(sent):
            if sent[i]._.in_coref:
                # Add coreference to list of tokens
                coref = sent[i]._.coref_clusters[0].main
                tokens += list(coref)
                # Find the end of the mention
                j = i
                while j < len(sent) and sent[j]._.in_coref and sent[j]._.coref_clusters[0].main == coref:
                   j += 1
                i = j
            else:
                # Add token to list
                tokens.append(sent[i])
                i += 1
        return [token for token in tokens]
        
    def get_ids(self, tokens):
        """
        Converts coreference resolved tokens to their Albert Tokenizer ids.
        Allos us to feed these into the model
        """
        # We start out with a list of ids only containing the begining of sequence id
        ids = [101]
        for token in tokens:
            token_id = tokenizer._convert_token_to_id(token.text.lower())
            if token_id != 100:
                ids.append(token_id)
            else:
                # for works with unknown ids, try to split it into parts using the sentpiece tokenizer
                ids += tokenizer(token.text)["input_ids"][1:-1]
        # Return with end of sequence id at the end
        return ids + [102]

    def _convert_ids_to_tokens(self):
        """
        Returns a list of the tokens in the ids list converted to strings
        """
        return [ [tokenizer._convert_id_to_token(i) for i in ids] for ids in self.ids]

    def _get_distance(self, sentence):
        """
        Returns the distance between the primary vectors of the sentences
        """
        return np.linalg.norm(self.embeddings[0] - sentence.embeddings[0])

    def __str__(self):
        """
        Converts the sentence to a string
        """
        return self.main_span.text
