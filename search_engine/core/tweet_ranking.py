"""
Students: Irene Cantero (U151206) & Jian Chen (U150279)
Project Title: INFORMATION RETRIEVAL - FINAL PROJECT
DATE: 06/12/2020
Content description: this module contains the tweet collector. This code has been taken from Scrapping Tweets practice of IR
"""
import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.utils import simple_preprocess
import enum
import itertools
import math
from .utils import normalize_vector

# Options to let the user choose the word embedding
class Options(enum.Enum):
    TF_IDF = 1
    WORD2VEC = 2


# This class contains the logic behind the search engine
class RankingSystem:
    def __init__(self, tweets: pd.DataFrame) -> None:
        # print("What ranking mode do you want?")
        # print("1. TF-IDF")
        # print("2. WORD2VEC")
        # The attributes contains the embedding method, the inverted index and the Word2Vec initialization.
        self.user_input = 1  # Default embedding method TF-IDF
        self.tweets = tweets
        self.inv_index = self.inverted_index(tweets)
        self.w2v = self.word2vec_initialization()
        self.d2v = self.doc2vec_initialization()

    # Auxiliar function to change the default word embedding
    def change_user_input(self, user_input: str) -> None:
        self.user_input = user_input

    # Function to initialize the Word2Vec model
    def word2vec_initialization(self) -> Word2Vec:
        words = [tweet.split() for tweet in self.tweets["text"]]
        w2v_model = Word2Vec(
            sentences=words, size=100, window=10, min_count=1, negative=15, sg=1
        )
        return w2v_model

    def doc2vec_initialization(self) -> Doc2Vec:
        tweets_ = []
        i = 0
        # Preparing the data to be put in Doc2Vec
        for line in self.tweets["text"]:
            tokens = simple_preprocess(line)
            tweets_.append(TaggedDocument(tokens, [i]))
            i += 1
        # Train the data and return
        d2v_model = Doc2Vec(
            documents=tweets_,
            vector_size=100,
            window=2,
            min_count=1,
            negative=0,
            workers=4,
        )
        return d2v_model

    # The inverted index is a list, each instance has the shape: -->
    # |Word: [doc1, doc2, ..., docn]|, where [doc1, doc2, ..., docn] are the documents that contains the Word.
    def inverted_index(self, data: pd.DataFrame) -> dict:
        inv_index = {}
        # For each tweet, we get the text
        for doc_num in range(len(data["text"])):
            words = data["text"][doc_num].split()
            # For each word, we add it to the inverted index with the document number, if it does not exist. Otherwise,
            # add the document number to the word list
            for word in words:
                if word in inv_index:
                    if word not in inv_index[word]:
                        inv_index[word].append(doc_num)
                else:
                    inv_index[word] = [doc_num]
        return inv_index

    # TF-IDF core function.
    def tf_idf(self, docs: list) -> list:
        tf = []
        df = {}
        idf = {}
        tf_idf = []
        N = len(self.tweets)  # Total number of tweets
        # TF implementation: Terms counting
        for doc_text in docs:
            tf_doc_i = {}
            words = doc_text.split()
            for word in words:
                if word in tf_doc_i:
                    tf_doc_i[word] += 1
                else:
                    tf_doc_i[word] = 1
            tf.append(tf_doc_i)

        # IDF computation, taking advantage of the inverted index.
        # We use the inverted index, because it has the df, which is the length of each word list
        for word in self.inv_index:
            df[word] = len(self.inv_index[word])
            idf[word] = np.log10(
                float(N / (df[word]))
            )  # Applying the formula of the idf --> Log10(N/df)

        # Computing the TF-IDF for each document
        for doc in range(len(docs)):
            tf_idf_per_doc = {}
            for word in docs[doc].split():
                # Applying the formula of TF-IDF --> 1+log10(tf) * idf (Formula taken from p.34 of IR-WA-2.pdf)
                tf_idf_per_doc[word] = (1 + np.log10(tf[doc][word])) * idf[word]
            tf_idf.append(tf_idf_per_doc)
        return tf_idf

    # Function to compute the TF-IDF of the query
    def query_tfidf(self, query: str, query_vector: dict) -> None:
        query_tf_idf = self.tf_idf([query])
        for word in query.split():
            query_vector[word] = query_tf_idf[0][word]

    # A function to return 3 similar queries
    def similar_words(self, content: str) -> list:
        similar_queries = []
        for word in content.split():
            similar_queries.append(
                [similar_word[0] for similar_word in self.w2v.most_similar(word)[:3]]
            )
        return similar_queries

    # Search function, by using the inverted index
    # Since the project required to only show documents that contains ALL query words,
    # we collected only collected those documents satisfying that condition.
    def search(self, query) -> list:
        result = set()
        documents = []
        # For each term, get the list of documents that contains such term in the inverted lists
        for term in query.split():
            try:
                documents.append(set(self.inv_index[term]))
            except:
                # If the term is not in the inverted index, return nothing
                print(f"No related tweets found for the query: '{query}'")
                return
        result = set.intersection(*documents)
        return list(result)

    # Tweet2Vec implementation here
    def word2vec_embedding(self, documents: list) -> list:
        docs_embedding = []
        # For each document do the mean of the words embeddings to represent the tweet
        for document in documents:
            doc_embedding = []
            # Loop for doing the word embedding
            for word in document.split():
                doc_embedding.append(self.w2v[word])
            # Doing the mean and appending
            tweet_embedding = np.mean(np.array(doc_embedding), axis=0)
            docs_embedding.append(tweet_embedding)
        return docs_embedding

    # The cosine similarity computes the vector representation of the documents and the query,
    # It normalizes the vectors and performs the dot product (Formula of cosine similarity)
    def cosine_similarity(self, query: str, documents: list) -> float:
        # The input already gives the relevant documents, which are extracted using the search function (Call done in search_engine.py)
        cosine_similarity = np.zeros(len(documents))
        relevant_documents = pd.DataFrame(self.tweets, index=documents)
        # Here we decide whether to use TF-IDF or Word2Vec
        # TF-IDF model embedding of documents.
        if int(self.user_input) == int(Options.TF_IDF.value):
            relevant_documents_score = self.tf_idf(relevant_documents["text"].tolist())
        # Word2Vec model embedding of documents
        if int(self.user_input) == int(Options.WORD2VEC.value):
            relevant_documents_score = self.word2vec_embedding(
                relevant_documents["text"].tolist()
            )
            i = 0
            # Cosine similarity between the normalized query vector and normalized document. This is done for each relevant document.
            for document in relevant_documents_score:
                embedded_query = normalize_vector(self.word2vec_embedding([query])[0])
                # Cosine similarity formula application
                cosine_similarity[i] = np.dot(
                    embedded_query, normalize_vector(document)
                )
                i += 1
        else:
            # TF-IDF case, the query embedding is done using TF-IDF, the rest is the same as in the Word2Vec case
            i = 0
            for document in relevant_documents_score:
                document_plus_query = set(query.split()) | set(document.keys())
                doc = {}
                for key in document_plus_query:
                    if key in document.keys():
                        doc.update({key: document[key]})
                    else:
                        doc.update({key: 0})

                vectorized_doc = normalize_vector(list(doc.values()))
                # Initialization of the query with the keys of the documents. This is done, because we must have the same size for the query vector
                # document vector.
                vectorized_query = {key: 0 for key in document_plus_query}
                # Computing the query TF-IDF
                self.query_tfidf(query, vectorized_query)
                vectorized_query_values = normalize_vector(
                    list(vectorized_query.values())
                )
                # Cosine similarity formula application
                cosine_similarity[i] = np.dot(vectorized_query_values, vectorized_doc)
                i += 1

        return cosine_similarity

    def run_doc2vec(self, input_: str):
        # Infer the vector to be able to let Doc2Vec do Cosine similarity
        embedded_input = self.d2v.infer_vector(input_.split())
        # Perform cosine similarity for every tweet and return it sorted
        recommendations = self.d2v.docvecs.most_similar(
            [embedded_input], topn=len(self.tweets)
        )
        recommendation_positions = [document[0] for document in recommendations]
        recommendation_score = [document[1] for document in recommendations]
        return recommendation_positions, recommendation_score

    def custom_score(
        self, data: pd.DataFrame, query: str, document_indices: list
    ) -> pd.DataFrame:
        # custom_score = num_retweets·3/6 + num_likes·2/6 + num_replies·1/6
        # We did not consider the followers of the users, as it would bias the importance Of each tweet; i.e. someone with a lot of followers could write something
        # irrelevant to the query and unfairly, get a higher punctuation than someone with not so many followers that wrote a relevant tweet.
        custom_score_ = []
        # Create a column to store the score of custom_score
        data["custom_score"] = pd.DataFrame(np.zeros(len(data)))
        recommendation_positions, recommendation_scores = self.run_doc2vec(query)
        # Apply custom_score and store it in the created column custom_score
        for tweet in range(len(data)):
            retweets_score = data["Retweets"][tweet]
            likes_score = data["Likes"][tweet]
            replies_score = data["Replies"][tweet]
            score = (
                (3 / 6) * int(retweets_score)
                + (2 / 6) * int(likes_score)
                + (1 / 6) * int(replies_score)
            )
            data["custom_score"][tweet] = score
            custom_score_.append(score)

        # Normalize the score to narrow the range to [0,1], because otherwise the scores would have way too big numbers.
        for tweet in range(len(data)):
            try:
                if tweet in document_indices:
                    data["custom_score"][tweet] = (
                        float(data["custom_score"][tweet]) - min(custom_score_)
                    ) / (max(custom_score_) - min(custom_score_))
                    data["custom_score"][tweet] *= recommendation_scores[tweet]
                else:
                    data["custom_score"][tweet] = 0
            except:
                continue
