import pandas as pd
import numpy as np


class RankingSystem:
    def __init__(self, tweets: pd.DataFrame) -> None:
        self.tweets = tweets
        self.inv_index = self.inverted_index(tweets)

    def inverted_index(self, data: pd.DataFrame) -> dict:
        inv_index = {}
        for doc_num in range(len(data["text"])):
            words = data["text"][doc_num].split()
            for word in words:
                if word in inv_index:
                    if word not in inv_index[word]:
                        inv_index[word].append(doc_num)
                else:
                    inv_index[word] = [doc_num]
        return inv_index

    # REMOVE THIS FUNCTION, THERE MUST BE A LIBRARY THAT DOES THIS
    def tf_idf_normalization(self, tf_idf: list) -> None:
        D_square = np.zeros(len(tf_idf))
        for i in range(len(tf_idf)):
            document_values = list(tf_idf[i].values())
            for j in range(len(document_values)):
                document_values[j] = document_values[j] ** 2
            D_square[i] = np.sum(document_values)

        for i in range(len(tf_idf)):
            for word in tf_idf[i]:
                tf_idf[i][word] = tf_idf[i][word] / np.sqrt(D_square[i])

    def tf_idf(self, docs: list) -> list:
        tf = []
        df = {}
        idf = {}
        tf_idf = []
        N = len(self.tweets)
        for doc_text in docs:
            tf_doc_i = {}
            words = doc_text.split()
            for word in words:
                if word in tf_doc_i:
                    tf_doc_i[word] += 1 / len(words)
                else:
                    tf_doc_i[word] = 1 / len(words)
            tf.append(tf_doc_i)

        for word in self.inv_index:
            df[word] = len(self.inv_index[word])
            idf[word] = np.log(float(N / (df[word] + 1)))

        for doc in range(len(docs)):
            tf_idf_per_doc = {}
            for word in tf[doc]:
                tf_idf_per_doc[word] = tf[doc][word] * idf[word]
            tf_idf.append(tf_idf_per_doc)
        self.tf_idf_normalization(tf_idf)
        return tf_idf

    def query_tfidf(self, query: str, query_vector: dict) -> None:
        query_tf_idf = self.tf_idf([query])
        for word in query.split():
            query_vector[word] = query_tf_idf[0][word]

    def search(self, query) -> list:
        result = set()
        documents = []
        for term in query.split():
            documents.append(set(self.inv_index[term]))
        result = set.intersection(*documents)
        return list(result)

    def cosine_similarity(self, query: str, documents: list) -> float:
        cosine_similarity = np.zeros(len(documents))
        relevant_documents = pd.DataFrame(self.tweets, index=documents)
        relevant_documents_score = self.tf_idf(relevant_documents["text"].tolist())
        i = 0
        for document in relevant_documents_score:
            vectorized_doc = list(document.values())
            vectorized_query = {key: 0 for key in document.keys()}
            self.query_tfidf(query, vectorized_query)
            vectorized_query_values = list(vectorized_query.values())
            cosine_similarity[i] = np.dot(vectorized_query_values, vectorized_doc)
            i += 1

        return cosine_similarity

    def g_d_score(
        self, data: pd.DataFrame
    ) -> pd.DataFrame:  # Hay que pasar tweets database
        # retweets -> 3/6; likes -> 2/6; replies -> 1/6
        # We did not consider the followers of the users, as it would bias the importance
        # Of each tweet. Someone with a lot of followers could write something irrelevant to the query and unfairly, get a higher
        # punctuation than someone with not so many followers that wrote a relevant tweet (with a lot of likes/retweets/replies).
        gd_score = []
        data["g(d)"] = pd.DataFrame(np.zeros(len(data)))
        for tweet in range(len(data)):
            # if str(row[1]["retweeted_status"]) == "nan":
            retweets_score = data["Retweets"][tweet]
            likes_score = data["Likes"][tweet]
            replies_score = data["Replies"][tweet]
            score = (
                (3 / 6) * int(retweets_score)
                + (2 / 6) * int(likes_score)
                + (1 / 6) * int(replies_score)
            )
            data["g(d)"][tweet] = score
            gd_score.append(score)
            """
            else:
                retweets_score = row[1]["retweeted_status"]["retweet_count"]
                likes_score = row[1]["retweeted_status"]["favorite_count"]
                replies_score = row[1]["retweeted_status"]["reply_count"]
                score = (
                    (3 / 6) * int(retweets_score)
                    + (2 / 6) * int(likes_score)
                    + (1 / 6) * int(replies_score)
                )
                gd_score.append(score)
            """
        print(f"max score: {max(gd_score)}")
        print(f"min score: {min(gd_score)}")

        for tweet in range(len(data)):
            try:
                data["g(d)"][tweet] = (float(data["g(d)"][tweet]) - min(gd_score)) / (
                    max(gd_score) - min(gd_score)
                )
            except:
                continue
        return data