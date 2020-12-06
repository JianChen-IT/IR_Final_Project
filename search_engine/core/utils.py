"""
Students: Irene Cantero (U151206) & Jian Chen (U150279)
Project Title: INFORMATION RETRIEVAL - FINAL PROJECT
DATE: 06/12/2020
Content description: this module contains functions useful to adapt the data to our purposes
"""
import pandas as pd


def set_full_text(data: pd.DataFrame) -> None:
    for tweet in range(len(data)):
        if data["truncated"][tweet] is True:
            try:
                data["text"][tweet] = data["extended_tweet"][tweet]["full_text"]
            except:
                data["text"][tweet] = data["retweeted_status"][tweet]["text"]


def remove_links(data: pd.DataFrame) -> None:
    for tweet in range(len(data)):
        new_tweet = []
        for word in data["text"][tweet].split():
            if word.startswith("https://") or word.startswith("http://"):
                new_tweet.append("")
            else:
                new_tweet.append(word)
        data["text"][tweet] = " ".join(new_tweet)


def unique_tweets(data: pd.DataFrame) -> pd.DataFrame:
    return data.drop_duplicates(subset=["id"])


def get_original_tweets(data: pd.DataFrame) -> pd.DataFrame:
    result = {}
    i = 0

    for tweet in range(len(data)):
        if str(data["retweeted_status"][tweet]) != "nan":
            result[i] = data["retweeted_status"][tweet]
            i += 1
    result_dataframe = pd.DataFrame.from_dict(result, orient="index").reset_index(
        drop=True
    )
    return unique_tweets(result_dataframe)
