"""
Students: Irene Cantero (U151206) & Jian Chen (U150279)
Project Title: INFORMATION RETRIEVAL - FINAL PROJECT
DATE: 06/12/2020
Content description: this module contains functions useful to adapt the data to our purposes
"""
import pandas as pd
import math

# Function used in search_engine.py to set the full text if the data is truncated
def set_full_text(data: pd.DataFrame) -> None:
    for tweet in range(len(data)):
        if data["truncated"][tweet] is True:
            try:
                # First try to find it in the extended tweet
                data["text"][tweet] = data["extended_tweet"][tweet]["full_text"]
            except:
                # If it does not exist, try to find in the retweeted status
                data["text"][tweet] = data["retweeted_status"][tweet]["text"]


# Function used in the tweet_ranking.py to normalize the vectors, and be able to ease the
# cosine similarity computation
def normalize_vector(vector: list):
    denominator = 0
    sum_ = 0
    for number in vector:
        sum_ += number ** 2
    denominator = math.sqrt(sum_)
    return [number / denominator for number in vector]


# Links removal, used in the setup of the search_engine.py, because we considered that links should not
# appear in the content
def remove_links(data: pd.DataFrame) -> None:
    for tweet in range(len(data)):
        new_tweet = []
        for word in data["text"][tweet].split():
            if word.startswith("https://") or word.startswith("http://"):
                new_tweet.append("")
            else:
                new_tweet.append(word)
        data["text"][tweet] = " ".join(new_tweet)


# Return unique tweets, to make sure that there is no repetitions. This is used in the function get_original_tweets
def unique_tweets(data: pd.DataFrame) -> pd.DataFrame:
    return data.drop_duplicates(subset=["id"])


# It gets the data of the original tweet, which is located in retweeted status
def get_original_tweets(data: pd.DataFrame) -> pd.DataFrame:
    result = {}
    i = 0
    # It iterates each tweet finding the retweeted status and replace the retweet by
    # the content of the retweeted status.
    for tweet in range(len(data)):
        if str(data["retweeted_status"][tweet]) != "nan":
            result[i] = data["retweeted_status"][tweet]
            i += 1
    # Creates a dataframe containing the original tweets
    result_dataframe = pd.DataFrame.from_dict(result, orient="index").reset_index(
        drop=True
    )
    # Remove those tweets that are repeated
    return unique_tweets(result_dataframe)
