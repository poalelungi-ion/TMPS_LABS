from sklearn.base import BaseEstimator, TransformerMixin
import re
from nltk import FreqDist

class TextNormalizer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, y=None, **fit_params):
        for i in range(len(X)):
            X[i] = X[i].lower()
            X[i] = X[i].replace('\n', ' ')
            X[i] = X[i].replace('\r', ' ')
            X[i] = X[i].strip()
            X[i] = ' '.join(re.findall('[a-z]+', X[i]))
        return X

    def fit_transform(self, X, y=None, **fit_params):
        return self.fit(X).transform(X)


class WordExtractor(BaseEstimator, TransformerMixin):
    def __init__(self, stop_words, tokenizer):
        self.stop_words = stop_words
        self.tokenizer = tokenizer

    def fit(self, X, y=None, **fit_params):
        self.freq_dist = FreqDist()
        for i in range(len(X)):
            self.freq_dist.update(self.tokenizer(X[i]))
        self.hapax = self.freq_dist.hapaxes()
        return self

    def transform(self, X, y=None, **fit_params):
        for i in range(len(X)):
            X[i] = ' '.join([word for word in self.tokenizer(X[i])
                             if word not in self.stop_words or word not in self.hapax])
        return X

    def fit_transform(self, X, y=None, **fit_params):
        return self.fit(X).transform(X)