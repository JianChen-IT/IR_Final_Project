"""
Students: Irene Cantero (U151206) & Jian Chen (U150279)
Project Title: INFORMATION RETRIEVAL - FINAL PROJECT
DATE: 06/12/2020
Content description: this module contains all the functions to normalize the text.
"""
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
import re


class Normalizer:
    def __init__(self):
        pass

    # We thought that decontraction methods should be introduced to avoid words such as "t" coming from words like
    # don't (After normalized: (don , t))
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

    # Removing all kind of punctuations [",", ".", "'", etc.]
    def punctuation_removal(self, text: str) -> str:
        tokenizer = RegexpTokenizer(r"\w+")
        return tokenizer.tokenize(self.decontracted(text.lower()))

    # The stemming is the one we used in class, to map all the combination of words to one word, and in this way reduce
    # the vocabulary.
    def stemming(self, text: list) -> list:
        ps = PorterStemmer()
        stemmed_text = []
        for word in text:
            stemmed_text.append(ps.stem(word))
        return stemmed_text

    # We only excludes the English stop words, since we are dealing with only english tweets.
    def remove_stop_words(self, word_list: list) -> list:
        stop_words = set(stopwords.words("english"))
        # Add the RT to the list of stop words, because use the retweeted_status to check if it is a RT,
        # and other than that the word does not give meaningful information
        stop_words.add("rt")
        text_without_stopwords = []
        # For each word in the tweet, remove the stopwords
        for word in word_list:
            if not word in stop_words:
                text_without_stopwords.append(word)
        return text_without_stopwords

    # Function that wraps up all the functions defined above and calls them in the right order.
    def text_normalization(self, text: str) -> str:
        # 1. Decontract the text
        text_decontracted = self.decontracted(text)
        # 2. Remove punctuations
        text_normalized = self.punctuation_removal(text_decontracted)
        # 3. Remove stop words
        text_without_stopwords = self.remove_stop_words(text_normalized)
        # 3. Stem the text
        text_stemmed = self.stemming(text_without_stopwords)
        return " ".join(text_stemmed)