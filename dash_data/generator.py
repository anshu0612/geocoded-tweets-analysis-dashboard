import pandas as pd

BASE_PATH = '../data/'
sg_tweets = pd.read_csv(BASE_PATH + "sg.csv")

MAX_DATE = sg_tweets['tweet_date'].max()
MIN_DATE = sg_tweets['tweet_date'].min()


class TweetsEngagements


