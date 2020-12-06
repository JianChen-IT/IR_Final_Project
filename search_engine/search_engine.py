from .core.tweet_collector import MyStreamListener
from .core.database_setup import TwitterDatabaseSetup
from .core.text_normalizer import Normalizer
from .core.tweet_ranking import RankingSystem
from .core.utils import unique_tweets, set_full_text, remove_links, get_original_tweets
import json
from tweepy import OAuthHandler, Stream, API, Cursor
import pandas as pd
import numpy as np
import os.path as path

GET_TWEETS = 0
LOAD_ALL = 0
OUTPUT_FILENAME = "other-outputs/tweets_US_Election_2020.json"


class SearchEngine:

    ## access token informations
    def __init__(self):
        self.access_token1 = "1222829174802538496-AXkAccE1dWMjuEFlEYChpgOibc6SbF"
        self.access_token_secret1 = "jtr66CvVvspsANplSBpuMEQR5iLwK2fRtzM6aDhaC1rZT"

        self.consumer_key1 = "sL9E5QL83DVEshfttLjEEj930"
        self.consumer_secret1 = "R9L4Ar7UWTKB4WQw7cEoybumyTInZ6pYP3cQ5GFlWYFllYAeec"

        self.auth = OAuthHandler(self.consumer_key1, self.consumer_secret1)
        self.auth.set_access_token(self.access_token1, self.access_token_secret1)
        self.api = API(
            auth_handler=self.auth,
            wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True,
        )

        self.json_election_file = []
        self.tweets = pd.DataFrame()
        self.original_tweets = pd.DataFrame()
        self.query_results = pd.DataFrame()
        self.query_results_with_g = pd.DataFrame()
        self.ranking_system = None
        self.database_setup = None
        self.tfidf = []
        self.setup()

    def setup(self):
        if GET_TWEETS:
            stop_condition = 100000
            l = MyStreamListener(self.api, OUTPUT_FILENAME, stop_condition)
            # here we recall the Stream Class from Tweepy to input the authentication info and our personalized listener
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
        self.initialize()
        self.results()

    def initialize(self):
        stop_condition = 10000
        i = 0
        for line in open(OUTPUT_FILENAME, "r"):
            if LOAD_ALL:
                self.json_election_file.append(json.loads(line))
            else:
                if i >= stop_condition:
                    break
                else:
                    self.json_election_file.append(json.loads(line))
                i += 1
        dict_tweets = {}
        i = 0
        for tweet in self.json_election_file:
            dict_tweets[i] = tweet
            i += 1

        self.tweets = pd.DataFrame.from_dict(
            dict_tweets, orient="index"
        ).drop_duplicates(subset=["id"])
        self.original_tweets = get_original_tweets(self.tweets)

        self.tweets.reset_index(level=0, inplace=True, drop=True)
        set_full_text(self.tweets)
        remove_links(self.tweets)

        self.original_tweets.reset_index(level=0, inplace=True, drop=True)
        remove_links(self.original_tweets)
        self.normalizer = Normalizer()
        self.tweets["original_text"] = self.tweets["text"]
        self.original_tweets["original_text"] = self.original_tweets["text"]

        for i in range(len(self.tweets)):
            self.tweets["text"][i] = self.normalizer.text_normalization(
                self.tweets["text"][i]
            )
        for i in range(len(self.original_tweets)):
            self.original_tweets["text"][i] = self.normalizer.text_normalization(
                self.original_tweets["text"][i]
            )

    def results(self):
        self.database_setup = TwitterDatabaseSetup(self.original_tweets)
        self.query_results = self.database_setup.get_tweet_data()
        self.query_results_with_g = self.database_setup.get_tweet_data()
        self.ranking_system = RankingSystem(self.original_tweets)
        self.database_setup_tweets = TwitterDatabaseSetup(self.tweets)
        self.tweets = self.database_setup_tweets.remove_unnecessary_columns()
        self.tfidf = self.ranking_system.tf_idf(self.original_tweets["text"].tolist())

    def run(self, query):
        query = self.normalizer.text_normalization(query)
        relevant_documents = self.ranking_system.search(query)
        relevant_documents_score = self.ranking_system.cosine_similarity(
            query, relevant_documents
        )
        self.query_results["score"] = pd.DataFrame(np.zeros(len(self.query_results)))
        i = 0
        for document in relevant_documents:
            self.query_results["score"][document] = relevant_documents_score[i]
            i += 1
        query_results_sorted = self.query_results.sort_values(
            by=["score"], ascending=False
        )

        return query_results_sorted.reset_index(drop=True)

    def run_g(self, query):
        self.query_results_with_g = self.run(query)
        self.query_results_with_g = self.ranking_system.g_d_score(
            self.query_results_with_g
        )
        self.query_results_with_g["total_score"] = pd.DataFrame(
            np.zeros(len(self.original_tweets))
        )
        index = 0
        for score in self.query_results_with_g["score"]:
            if score > 0:
                self.query_results_with_g["total_score"][index] = (
                    self.query_results_with_g["score"][index]
                    + self.query_results_with_g["g(d)"][index]
                )
            index += 1
        query_results_sorted_with_g = self.query_results_with_g.sort_values(
            by=["total_score"], ascending=False
        )

        return query_results_sorted_with_g.reset_index(drop=True)