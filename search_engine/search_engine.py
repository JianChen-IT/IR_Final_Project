"""
Students: Irene Cantero (U151206) & Jian Chen (U150279)
Project Title: INFORMATION RETRIEVAL - FINAL PROJECT
DATE: 06/12/2020
Content description: this module contains the search engine core functions, and all the needed setup to make it work.
"""
from .core.tweet_collector import MyStreamListener
from .core.database_setup import TwitterDatabaseSetup
from .core.text_normalizer import Normalizer
from .core.tweet_ranking import RankingSystem
from .core.utils import set_full_text, remove_links, get_original_tweets
import json
from tweepy import OAuthHandler, Stream, API, Cursor
import pandas as pd
import numpy as np
import os.path as path
import time

# Flags to avoid loading all the data or prevent the collection. False = 0. True = 1
GET_TWEETS = 0
LOAD_ALL = 0
OUTPUT_FILENAME = "other-outputs/tweets_US_Election_2020.json"

# Core function to run the search engine. Everything class is connected here to make the search engine work
class SearchEngine:
    def __init__(self):
        # Tweepy access tokens initialization
        self.access_token1 = "1222829174802538496-AXkAccE1dWMjuEFlEYChpgOibc6SbF"
        self.access_token_secret1 = "jtr66CvVvspsANplSBpuMEQR5iLwK2fRtzM6aDhaC1rZT"

        self.consumer_key1 = "sL9E5QL83DVEshfttLjEEj930"
        self.consumer_secret1 = "R9L4Ar7UWTKB4WQw7cEoybumyTInZ6pYP3cQ5GFlWYFllYAeec"
        # Twitter API initialization
        self.auth = OAuthHandler(self.consumer_key1, self.consumer_secret1)
        self.auth.set_access_token(self.access_token1, self.access_token_secret1)
        self.api = API(
            auth_handler=self.auth,
            wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True,
        )
        # These are the attributes to be able to run all functions of the search engine

        self.tweets = pd.DataFrame()  # Contains all the tweets collected
        self.original_tweets = (
            pd.DataFrame()
        )  # Contains only the original tweets, not the retweets
        self.query_results = (
            pd.DataFrame()
        )  # Simplified database of original_tweets, only containing relevant information
        self.query_results_custom_score = (
            pd.DataFrame()
        )  # Same as query_results, but we did not wanted to overwrite query_results, when running with our custom scoring function
        self.ranking_system = None  # Needed for the ranking of the tweets
        self.ranking_system_ex_3 = None  # We need a different ranking system considering all the tweets and retweets for ex.3B
        self.database_setup = None  # used for giving shape for tweets, query_results and query_results_custom_score by removing columns, and easing the Twitter API tweet structure
        self.setup()  # Running the initialization of the Search engine

    # Function that collects and calls the rest of the functions
    def setup(self):
        start = time.time()
        if GET_TWEETS:
            stop_condition = 10000
            # Collection of tweets
            l = MyStreamListener(self.api, OUTPUT_FILENAME, stop_condition)
            stream = Stream(auth=self.api.auth, listener=l)
            # keywords we may want decide to track
            TRACKING_KEYWORDS = [
                "Donald",
                "Trump",
                "Joe",
                "Biden",
                "America",
                "USA",
                "fraud",
                "Pennsylvania",
                "Georgia" "Republicans",
                "Democrats",
                "Votes",
                "States",
            ]
            stream.filter(track=TRACKING_KEYWORDS, is_async=False, languages=["en"])
        end = time.time()
        print(f"Collection time: {end - start }")
        # After collection of tweets continue with the initialization
        self.initialize()
        # Initialization of the attributes
        self.attributes_initialization()

    # Creates the dataframe for all tweets and for the original tweets.
    def initialize(self):
        stop_condition = 10000
        i = 0
        json_election_file = []
        # Read the json file , append it to a dictionary and create the dataframe
        for line in open(OUTPUT_FILENAME, "r"):
            # if the flag is activated, append all. If not, stop reading in the stop_condition
            if LOAD_ALL:
                json_election_file.append(json.loads(line))
            else:
                if i >= stop_condition:
                    break
                else:
                    json_election_file.append(json.loads(line))
                i += 1
        dict_tweets = {}
        i = 0
        for tweet in json_election_file:
            dict_tweets[i] = tweet
            i += 1

        # Creation of the dataframe with the collected tweets
        self.tweets = pd.DataFrame.from_dict(
            dict_tweets, orient="index"
        ).drop_duplicates(subset=["id"])

        # Filtering to only get the original tweets
        self.original_tweets = get_original_tweets(self.tweets)

        self.tweets.reset_index(level=0, inplace=True, drop=True)
        # Some tweets are truncated, force to have the full text
        set_full_text(self.tweets)
        # Revoming https links
        remove_links(self.tweets)

        self.original_tweets.reset_index(level=0, inplace=True, drop=True)
        remove_links(self.original_tweets)
        self.normalizer = Normalizer()

        # Creating a copy of the text, because the "text" field will be normalized. However, in the ranking results,
        # we still want to show the original text. Otherwise, is difficult to read after applying the normalization proccess
        self.tweets["original_text"] = self.tweets["text"]
        self.original_tweets["original_text"] = self.original_tweets["text"]

        # Normalization process for tweets and original_tweets
        for i in range(len(self.tweets)):
            self.tweets["text"][i] = self.normalizer.text_normalization(
                self.tweets["text"][i]
            )
        for i in range(len(self.original_tweets)):
            self.original_tweets["text"][i] = self.normalizer.text_normalization(
                self.original_tweets["text"][i]
            )

    def attributes_initialization(self):
        # query_results and query_results_g are assigned with the relevant documents set at the function "run" and "run_g"
        self.database_setup = TwitterDatabaseSetup(self.original_tweets)
        self.query_results = self.database_setup.get_tweet_data()
        self.query_results_custom_score = self.database_setup.get_tweet_data()
        self.ranking_system = RankingSystem(self.original_tweets)
        self.ranking_system_ex_3 = RankingSystem(self.tweets)
        self.database_setup_tweets = TwitterDatabaseSetup(self.tweets)
        self.tweets = self.database_setup_tweets.remove_unnecessary_columns()

    # Function to run TF-IDF + Cosine similarity or Word2Vec + Cosine similarity,
    # depending on the flag defined in the RankingSystem
    def run(self, query):
        # Query normalization
        query = self.normalizer.text_normalization(query)
        # Relevant documents identification
        relevant_documents = self.ranking_system.search(query)
        # Relevant document scoring
        relevant_documents_score = self.ranking_system.cosine_similarity(
            query, relevant_documents
        )
        # Score assignation
        self.query_results["score"] = pd.DataFrame(np.zeros(len(self.query_results)))
        i = 0
        for document in relevant_documents:
            self.query_results["score"][document] = relevant_documents_score[i]
            i += 1

        # Sort by descending score
        query_results_sorted = self.query_results.sort_values(
            by=["score"], ascending=False
        )

        return query_results_sorted.reset_index(drop=True)

    # It runs using the custom score Doc2Vec*G(d) that we have the defined
    def run_custom_score(self, query):
        # Query normalization
        query = self.normalizer.text_normalization(query)
        # Relevant documents identification
        relevant_documents = self.ranking_system.search(query)

        self.ranking_system.custom_score(
            self.query_results_custom_score, query, relevant_documents
        )
        # Sort by descending total score
        query_results_sorted_with_custom_score = (
            self.query_results_custom_score.sort_values(
                by=["custom_score"], ascending=False
            )
        )

        return query_results_sorted_with_custom_score.reset_index(drop=True)