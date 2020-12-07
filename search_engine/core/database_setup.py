"""
Students: Irene Cantero (U151206) & Jian Chen (U150279)
Project Title: INFORMATION RETRIEVAL - FINAL PROJECT
DATE: 06/12/2020
Content description: this module removes irrelevant tweet information and sets up the search engine output
"""
import pandas as pd


class TwitterDatabaseSetup:
    # The initialization of this class gets as input the dataframe to be modified.
    def __init__(self, data: pd.DataFrame):
        self.data = data

    # Collection of hashtags through the "entities" field
    def get_hashtags(self, data: pd.DataFrame) -> list:
        hashtags_list = []
        # If there are no hashtags, then return empty list
        if len(data["hashtags"]) < 1:
            return []
        # Otherwise return the list of hashtags
        else:
            for i in range(len(data["hashtags"])):
                hashtags_list.append(data["hashtags"][i]["text"])
        return hashtags_list

    # Simple function to remove columns that are not used for the search engine
    def remove_unnecessary_columns(self) -> pd.DataFrame:
        cols_to_remove = [
            "id",
            "display_text_range",
            "in_reply_to_status_id",
            "in_reply_to_status_id_str",
            "in_reply_to_user_id",
            "in_reply_to_user_id_str",
            "geo",
            "coordinates",
            "place",
            "contributors",
            "is_quote_status",
            "quote_count",
            "lang",
            "possibly_sensitive",
            "quoted_status_id",
            "quoted_status_id_str",
            "quoted_status",
            "quoted_status_permalink",
        ]

        data = self.data.drop(columns=cols_to_remove)
        return data

    # The idea of this function is to get the most relevant information. This includes: Tweet| Username | Date | Hashtags | Likes | Retweets | Url
    # Often, the information of the Likes, replies and hashtags are stored in the retweeted_status, but this field  only exists if the tweet is a retweet.
    # If both are not the case, we use directly the information given in the tweet.

    # This is not needed in our use case, but we also support when there is the field "extended_tweet", which exists when the truncated field is true and
    # the tweet is not a retweet (no retweeted_status).

    # The strategy followed here is to create a DataFrame only with the relevant data to be shown to the user.
    def get_tweet_data(self) -> pd.DataFrame:

        tweets_text = []
        tweets_username = []
        tweets_date = []
        tweets_hashtags = []
        tweets_likes = []
        tweets_retweets = []
        tweets_replies = []
        tweets_url = []

        # For each tweet...
        for tweet in range(len(self.data)):
            # If the retweeted status exists, get the data from there
            try:
                tweets_text.append(self.data["retweeted_status"][tweet]["text"])
                # We get the name of the user
                tweets_username.append(
                    self.data["retweeted_status"][tweet]["user"]["name"]
                )
                # Get the date of creation
                tweets_date.append(self.data["retweeted_status"][tweet]["created_at"])
                # Get the hashtags
                tweets_hashtags.append(
                    self.get_hashtags(
                        (self.data["retweeted_status"][tweet]["entities"])
                    )
                )
                # Get likes
                tweets_likes.append(
                    self.data["retweeted_status"][tweet]["favorite_count"]
                )
                # Get the number of retweets
                tweets_retweets.append(
                    self.data["retweeted_status"][tweet]["retweet_count"]
                )
                # Get the URL
                tweets_url.append(
                    "https://twitter.com/i/web/status/" + self.data["id_str"][tweet]
                )
                # Get the number of replies
                tweets_replies.append(
                    self.data["retweeted_status"][tweet]["reply_count"]
                )
            # If not, check if it is truncated or not, to get the text from there. (This is irrelevant, because in the
            # initialization we already get the full text, but we leave it, because if we continue this project in the future
            # this might be needed)
            except:
                if self.data["truncated"][tweet] == False:
                    tweets_text.append(self.data["original_text"][tweet])
                    if self.get_hashtags(self.data["entities"][tweet]) is not None:
                        tweets_hashtags.append(
                            self.get_hashtags(self.data["entities"][tweet])
                        )
                else:
                    tweets_text.append(self.data["extended_tweet"][tweet]["full_text"])
                    tweets_hashtags.append(
                        self.get_hashtags(
                            self.data["extended_tweet"][tweet]["entities"]
                        )
                    )

                # Get the creation date
                tweets_date.append(self.data["created_at"][tweet])
                # Get the user name
                tweets_username.append(self.data["user"][tweet]["name"])
                # Get the URL
                tweets_url.append(
                    "https://twitter.com/i/web/status/" + self.data["id_str"][tweet]
                )
                # Get the number of likes
                tweets_likes.append(self.data["favorite_count"][tweet])
                # Get the number of retweets
                tweets_retweets.append(self.data["retweet_count"][tweet])
                # Get the number of replies
                tweets_replies.append(self.data["reply_count"][tweet])

        tweet_info = {
            "Tweet": tweets_text,
            "Username": tweets_username,
            "Date": tweets_date,
            "Hashtags": tweets_hashtags,
            "Likes": tweets_likes,
            "Retweets": tweets_retweets,
            "Replies": tweets_replies,
            "Url": tweets_url,
        }

        return pd.DataFrame(data=tweet_info)