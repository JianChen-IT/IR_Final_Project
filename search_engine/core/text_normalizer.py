import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
import re


class Normalizer:
    def __init__(self):
        pass

    def decontracted(self, text: str) -> str:
        text = re.sub(r"won\'t", "will not", text)
        text = re.sub(r"can\'t", "can not", text)
        text = re.sub(r"n\'t", " not", text)
        text = re.sub(r"\'re", " are", text)
        text = re.sub(r"\'s", " is", text)
        text = re.sub(r"\'d", " would", text)
        text = re.sub(r"\'ll", " will", text)
        text = re.sub(r"\'t", " not", text)
        text = re.sub(r"\'ve", " have", text)
        text = re.sub(r"\'m", " am", text)
        return text

    def punctuation_removal(self, text: str) -> str:
        tokenizer = RegexpTokenizer(r"\w+")
        return tokenizer.tokenize(self.decontracted(text.lower()))

    def stemming(self, text: list) -> list:
        ps = PorterStemmer()
        stemmed_text = []
        for word in text:
            stemmed_text.append(ps.stem(word))
        return stemmed_text

    def remove_stop_words(self, word_list: list) -> list:
        stop_words = set(stopwords.words("english"))
        stop_words.add("rt")
        text_without_stopwords = []
        for word in word_list:
            if not word in stop_words:
                text_without_stopwords.append(word)
        return text_without_stopwords

    def text_normalization(self, text: str) -> str:
        text_normalized = self.punctuation_removal(text)
        text_stemmed = self.stemming(text_normalized)
        text_without_stopwords = self.remove_stop_words(text_stemmed)
        return " ".join(text_without_stopwords)