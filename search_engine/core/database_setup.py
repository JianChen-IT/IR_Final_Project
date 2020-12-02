import pandas as pd

# Normalize functions:


class TwitterDatabaseSetup:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    # NO SALEN HASHTAGS NI DEL TEXT NI DE ENTITIES.MIRAR RETWEETED STATUS Y TIENE QUE DEVOLVER
    def get_hashtags(self, data: pd.DataFrame) -> None:
        hashtag_list = []
        for i in range(len(data)):
            hashtags = []
            try:
                hashtags_info = data["entities"]["hashtags"]
            except:
                hashtags_info = data["entities"][i]["hashtags"]
            for i in range(len(hashtags_info)):
                hashtags.append(hashtags_info[i]["text"])
            hashtag_list.append(hashtags)
        data["hashtags"] = hashtag_list

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

    # retweeted_status only exists if the tweet has been retweeted by someone. If not, extended_tweet exists if Truncated is true.
    # If both are not the case, we use directly the information given in the tweet.
    def get_tweet_data(self) -> pd.DataFrame:
        #  Tweet| Username | Date | Hashtags | Likes | Retweets | Url
        tweets_text = []
        tweets_username = []
        tweets_date = []
        tweets_hashtags = []
        tweets_likes = []
        tweets_retweets = []
        tweets_replies = []
        tweets_url = []
        for tweet in range(len(self.data)):

            if self.data["truncated"][tweet] == False:
                tweets_text.append(self.data["text"][tweet])
                tweets_hashtags.append(self.get_hashtags(self.data))
            else:
                tweets_text.append(self.data["extended_tweet"][tweet]["full_text"])
                tweets_hashtags.append(
                    self.get_hashtags(self.data["extended_tweet"][tweet])
                )

            tweets_date.append(self.data["created_at"][tweet])
            tweets_username.append(self.data["user"][tweet]["name"])
            tweets_url.append(
                "https://twitter.com/i/web/status/" + self.data["id_str"][tweet]
            )
            tweets_likes.append(self.data["favorite_count"][tweet])
            tweets_retweets.append(self.data["retweet_count"][tweet])
            tweets_replies.append(self.data["reply_count"][tweet])
            # else:
            """
                tweets_text.append(self.data["retweeted_status"][tweet]["text"])
                # We supposed it is the name and not the @name (screen_name)
                tweets_username.append(
                    self.data["retweeted_status"][tweet]["user"]["name"]
                )
                tweets_date.append(self.data["retweeted_status"][tweet]["created_at"])
                tweets_hashtags.append(
                    self.get_hashtags((self.data["retweeted_status"][tweet]))
                )
                tweets_likes.append(
                    self.data["retweeted_status"][tweet]["favorite_count"]
                )
                tweets_retweets.append(
                    self.data["retweeted_status"][tweet]["retweet_count"]
                )
            tweets_url.append(
                "https://twitter.com/i/web/status/" + self.data["id_str"][tweet]
            )
            """
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