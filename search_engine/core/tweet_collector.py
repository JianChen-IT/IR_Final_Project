from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API, Cursor
import json


class MyStreamListener(StreamListener):
    """
    Twitter listener, collects streaming tweets and output to a file
    """

    def __init__(self, api, OUTPUT_FILENAME, stop_condition=10):

        super(MyStreamListener, self).__init__()
        self.num_tweets = 0
        self.filename = OUTPUT_FILENAME
        self.stop_condition = stop_condition

    def on_status(self, status):

        """
        this function runs each time a new bunch of tweets is retrived from the streaming
        """
        # Only get retweeted status, since when streaming the likes, comments and retweets are 0
        with open(self.filename, "a+") as f:
            tweet = status._json
            f.write(json.dumps(tweet) + "\n")
            self.num_tweets += 1

            if self.num_tweets <= self.stop_condition:
                return True
            else:
                return False

    def on_error(self, status):
        """
        function useful to handle errors. It's possible to personalize it
        depending on the way we want to handle errors
        """
        print(status)
        return False