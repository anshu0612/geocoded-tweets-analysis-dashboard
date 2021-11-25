import pandas as pd

from dash_constants import *
from dash_modules.engagements import *
from dash_modules.basics import *
from dash_modules.influential_countries import *
from dash_modules.graph_analysis import *
from constants import COUNTRY

import warnings
warnings.filterwarnings('ignore')


class DashGenerator():
    def __init__(self):
        self.sg_tweets = pd.read_csv(SG_TWEETS_PATH)

        self.min_date = self.sg_tweets['tweet_date'].min()
        self.max_date = self.sg_tweets['tweet_date'].max()

        self.retweets = get_retweets(self.sg_tweets)
        self.G = None
        self.G_pruned = None

    def generate_basic(self):
        generate_dash_basic_stats(self.sg_tweets, True)
        generate_dash_daily_tweets(self.sg_tweets, True)

        generate_dash_hashtags(
            self.sg_tweets, self.min_date, self.max_date, True)
        generate_dash_mentions(
            self.sg_tweets, self.min_date, self.max_date, True)
        generate_dash_sentiments(
            self.sg_tweets, self.min_date, self.max_date, True)

        generate_dash_potentially_sensitive_tweets(self.sg_tweets, True)

    def generate_influential_countries(self):
        top_influential_countries = get_top_influential_countries(
            self.sg_tweets)
        top_influential_countries_df = generate_dash_influential_countries(
            top_influential_countries, True)

        # Saving tweets from the top influential countries for word frequencies analysis
        generate_dash_influential_countries_tweets(
            self.sg_tweets, top_influential_countries_df, True)

    def generate_influential_users(self):
        all_interacting_users = get_all_interacting_users(self.sg_tweets)
        weighted_interacting_edges = get_weighted_interacting_edges(
            self.sg_tweets)
        self.G = create_weighted_directed_graph(
            all_interacting_users, weighted_interacting_edges)
        top_ranking = get_top_ranked_users(self.G)
        generate_dash_influential_users(self.sg_tweets, top_ranking, True)

    def generate_networking_data(self):
        generate_cytograph_data(self.G_pruned)

    def generate_communities(self):
        self.G_pruned = get_min_degree_graph(self.G, 5)
        get_communities(self.G_pruned, self.sg_tweets, True)

    def generate_bursty_quoted(self):
        quoted_tws = get_quoted_tweets(self.sg_tweets)
        quoted_tws = get_quoted_tweets_by_date(
            quoted_tws, self.min_date, self.max_date)
        bursty_quoted_tws = get_bursty_quoted_tweets(quoted_tws)

        quoted_tws_by_sentiment_spreadrate = get_high_spreadrate_quoted_by_sentiment(
            bursty_quoted_tws, rate=SENTIMENT_SPREAD_THRESHOLD)
        generate_dash_bursty_quotes_by_sentiment(
            bursty_quoted_tws, quoted_tws_by_sentiment_spreadrate, True)

    def generate_global_retweets(self):
        neg_global_retweet = self.retweets[(self.retweets['tweet_sentiment'] == 'negative') &
                                           (self.retweets['retweeted_user_geo_coding'] != COUNTRY) &
                                           (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        pos_global_retweet = self.retweets[(self.retweets['tweet_sentiment'] == 'positive') &
                                           (self.retweets['retweeted_user_geo_coding'] != COUNTRY) &
                                           (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        all_global_retweet = self.retweets[(self.retweets['retweeted_user_geo_coding'] != COUNTRY) &
                                           (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        generate_dash_bursty_retweets(
            pos_global_retweet, True, POS_GLOBAL_RTS_TREND_PATH, POS_GLOBAL_RTS_INFO_PATH)
        generate_dash_bursty_retweets(
            neg_global_retweet, True, NEG_GLOBAL_RTS_TREND_PATH, NEG_GLOBAL_RTS_INFO_PATH)
        generate_dash_bursty_retweets(
            all_global_retweet, True, ALL_GLOBAL_RTS_TREND_PATH, ALL_GLOBAL_RTS_INFO_PATH)

    def generate_local_retweets(self):
        neg_local_retweet = self.retweets[(self.retweets['tweet_sentiment'] == 'negative') &
                                          (self.retweets['retweeted_user_geo_coding'] == COUNTRY) &
                                          (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        pos_local_retweet = self.retweets[(self.retweets['tweet_sentiment'] == 'positive') &
                                          (self.retweets['retweeted_user_geo_coding'] == COUNTRY) &
                                          (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        all_local_retweet = self.retweets[(self.retweets['retweeted_user_geo_coding'] == COUNTRY) &
                                          (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        generate_dash_bursty_retweets(
            pos_local_retweet, True, POS_LOCAL_RTS_TREND_PATH, POS_LOCAL_RTS_INFO_PATH)
        generate_dash_bursty_retweets(
            neg_local_retweet, True, NEG_LOCAL_RTS_TREND_PATH, NEG_LOCAL_RTS_INFO_PATH)
        generate_dash_bursty_retweets(
            all_local_retweet, True, ALL_LOCAL_RTS_TREND_PATH, ALL_LOCAL_RTS_INFO_PATH)


if __name__ == '__main__':
    dg = DashGenerator()

    # dg.generate_basic()



    # dg.generate_global_retweets()
    # dg.generate_local_retweets()
    # dg.generate_bursty_quoted()

    # dg.generate_influential_countries()

    dg.generate_influential_users()
    dg.generate_communities()
    dg.generate_networking_data()
