# coding: utf-8
import pickle
import spacy
from sklearn.metrics.pairwise import cosine_similarity

class DocLite:
    def __init__(self, token, vector):
        self.token = token
        self.vector = vector

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.token

    def similarity(self, other):
        return cosine_similarity([self.vector], [other.vector])


class NlpLite:
    def __init__(self, path):
        with open(path, 'rb') as f:
            self.cache = pickle.load(f)

    def __call__(self, key):
        return self.cache[key]


class ModelWrapper:
    def __init__(self, clf, fdict):
        self.clf = clf
        self.fdict = fdict