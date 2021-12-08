import pandas as pd

from dash_modules_generators.engagements import *
from dash_modules_generators.basics import *
from dash_modules_generators.influential_countries import *
from dash_modules_generators.graph_analysis import *

from constants.dash_constants import *
from constants.common import TWEETS_PATH, COUNTRY

from pathlib import Path

import warnings
warnings.filterwarnings('ignore')


class DashGenerator():
    def __init__(self):

        Path(DATA_DASH_PATH).mkdir(parents=True, exist_ok=True)

        # load the file containing selected country tweets
        self.tweets = pd.read_csv(TWEETS_PATH)
        # storing min and max date of the data
        self.min_date = self.tweets['tweet_date'].min()
        self.max_date = self.tweets['tweet_date'].max()

        self.retweets = get_retweets(self.tweets)
        self.G = None
        self.G_pruned = None

    def get_basics(self):
        # create `basics` directory  if not existing
        Path(DATA_DASH_PATH + 'basics').mkdir(parents=True, exist_ok=True)

        generate_dash_basic_stats(self.tweets, True)
        generate_dash_daily_tweets(self.tweets, True)

        generate_dash_hashtags(
            self.tweets, self.min_date, self.max_date, True)
        generate_dash_mentions(
            self.tweets, self.min_date, self.max_date, True)
        generate_dash_sentiments(
            self.tweets, self.min_date, self.max_date, True)

        generate_dash_potentially_sensitive_tweets(self.tweets, True)

    def get_influential_countries(self):
        # create `influencers` directory if not existing
        Path(DATA_DASH_PATH + 'influencers').mkdir(parents=True, exist_ok=True)

        top_influential_countries = get_top_influential_countries(
            self.tweets)
        top_influential_countries_df = generate_dash_influential_countries(
            top_influential_countries, True)

        # Saving tweets from the top influential countries for word frequencies analysis
        generate_dash_influential_countries_tweets(
            self.tweets, top_influential_countries_df, True)

    def get_interactions_graph(self):
        # create `influencers` directory if not existing
        Path(DATA_DASH_PATH + 'influencers').mkdir(parents=True, exist_ok=True)

        all_interacting_users = get_all_interacting_users(self.tweets)
        weighted_interacting_edges = get_weighted_interacting_edges(
            self.tweets)
        self.G = create_weighted_directed_graph(
            all_interacting_users, weighted_interacting_edges)

    # def get_prominenet_groups(self):
    #     generate_prominenet_groups(self.G)

    def get_influential_users(self):
        top_ranking = get_top_ranked_users(self.G)
        generate_dash_influential_users(self.tweets, top_ranking, True)

    def get_networking_data(self):
        Path(DATA_DASH_PATH + 'networking').mkdir(parents=True, exist_ok=True)

        generate_networking_graph_data(self.G_pruned)

    def get_communities(self):
        Path(DATA_DASH_PATH + 'networking').mkdir(parents=True, exist_ok=True)
        self.G_pruned = create_min_degree_graph(self.G)
        get_communities(self.G_pruned, self.tweets, True)

    def get_reactive_tweets(self):
        Path(DATA_DASH_PATH + 'quoted').mkdir(parents=True, exist_ok=True)

        # get the tweets with quotes
        quoted_tws = get_quoted_tweets(self.tweets)

        # filter the tweets by date range
        quoted_tws = get_quoted_tweets_by_date(
            quoted_tws, self.min_date, self.max_date)
        
        # get viral quoted tweets
        viral_quoted_tweets = get_viral_quoted_tweets(quoted_tws)

        # get reactive tweets
        reactive_tweets_with_extreme_sentiments = get_reactive_tweets_with_extreme_sentiments(
            viral_quoted_tweets)
        
        generate_dash_reactive_tweets_with_extreme_sentiments(
            viral_quoted_tweets, reactive_tweets_with_extreme_sentiments, True)

    def get_global_viral_retweeted_tweets(self):
        Path(DATA_DASH_PATH + 'rts/global').mkdir(parents=True, exist_ok=True)

        neg_retweeted_tweets = self.retweets[(self.retweets['tweet_sentiment'] == 'negative') &
                                             (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        pos_retweeted_tweets = self.retweets[(self.retweets['tweet_sentiment'] == 'positive') &
                                             (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        all_retweeted_tweets = self.retweets[(self.retweets['retweeted_tweet_date'].between(
            self.min_date, self.max_date, inclusive='both'))]

        if COUNTRY:
            # if country-specific tweets collection then global tweets should exclude the country's tweets
            neg_retweeted_tweets = neg_retweeted_tweets[
                neg_retweeted_tweets['retweeted_user_geo_coding'] != COUNTRY]
            pos_retweeted_tweets = pos_retweeted_tweets[
                pos_retweeted_tweets['retweeted_user_geo_coding'] != COUNTRY]
            all_retweeted_tweets = all_retweeted_tweets[
                all_retweeted_tweets['retweeted_user_geo_coding'] != COUNTRY]

        generate_dash_viral_retweeted_tweets(
            pos_retweeted_tweets, True, POS_GLOBAL_RTS_TREND_PATH, POS_GLOBAL_RTS_INFO_PATH)
        generate_dash_viral_retweeted_tweets(
            neg_retweeted_tweets, True, NEG_GLOBAL_RTS_TREND_PATH, NEG_GLOBAL_RTS_INFO_PATH)
        generate_dash_viral_retweeted_tweets(
            all_retweeted_tweets, True, ALL_GLOBAL_RTS_TREND_PATH, ALL_GLOBAL_RTS_INFO_PATH)

    def get_local_viral_retweeted_tweets(self):
        Path(DATA_DASH_PATH + 'rts/local').mkdir(parents=True, exist_ok=True)
        neg_retweeted_tweets = self.retweets[(self.retweets['tweet_sentiment'] == 'negative') &
                                             (self.retweets['retweeted_user_geo_coding'] == COUNTRY) &
                                             (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        pos_retweeted_tweets = self.retweets[(self.retweets['tweet_sentiment'] == 'positive') &
                                             (self.retweets['retweeted_user_geo_coding'] == COUNTRY) &
                                             (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        all_retweeted_tweets = self.retweets[(self.retweets['retweeted_user_geo_coding'] == COUNTRY) &
                                             (self.retweets['retweeted_tweet_date'].between(self.min_date, self.max_date, inclusive='both'))]

        generate_dash_viral_retweeted_tweets(
            pos_retweeted_tweets, True, POS_LOCAL_RTS_TREND_PATH, POS_LOCAL_RTS_INFO_PATH)
        generate_dash_viral_retweeted_tweets(
            neg_retweeted_tweets, True, NEG_LOCAL_RTS_TREND_PATH, NEG_LOCAL_RTS_INFO_PATH)
        generate_dash_viral_retweeted_tweets(
            all_retweeted_tweets, True, ALL_LOCAL_RTS_TREND_PATH, ALL_LOCAL_RTS_INFO_PATH)


if __name__ == '__main__':
    dg = DashGenerator()
    formatter = '-'*10

    # Generates basics stats about the tweets
    print('{} 1/8 Generating basics data 🚧'.format(formatter))
    dg.get_basics()
    print('{} Basics data generated ✅ '.format(formatter))

    # Generates global viral tweets
    print('{} 2/8 Generating global viral retweeted tweets data 🚧'.format(formatter))
    dg.get_global_viral_retweeted_tweets()
    print('{} Global global retweeted tweets data generated ✅ '.format(formatter))

    # Generates local viral tweets
    if COUNTRY:
        print('{} 3/8 Generating local viral retweeted tweets data 🚧'.format(formatter))
        dg.get_local_viral_retweeted_tweets()
        print('{} Local viral retweeted tweets data generated ✅ '.format(formatter))

    # Generates reactive quoted tweets
    print('{} 4/8 Generating reactive tweets data 🚧'.format(formatter))
    dg.get_reactive_tweets()
    print('{} Reactive tweets data generated ✅ '.format(formatter))

    # Generates list of top influential countries
    print('{} 5/8 Generating influential countries data 🚧'.format(formatter))
    dg.get_influential_countries()
    print('{} Influential countries data generated ✅ '.format(formatter))

    # Generates list of top influential users
    print('{} 6/8 Generating influential countries data 🚧'.format(formatter))
    dg.get_interactions_graph()
    # dg.get_prominenet_groups()
    dg.get_influential_users()
    print('{} Influential countries data generated ✅ '.format(formatter))

    # Generates communities of users
    print('{} 7/8 Generating communities data 🚧'.format(formatter))
    dg.get_communities()
    print('{} Communities data generated ✅ '.format(formatter))

    # Generates data for creating networking graphs
    # Tweets by the communities of users
    print('{} 8/8 Generating networking data 🚧 '.format(formatter))
    dg.get_networking_data()
    print('{} Networking data generated ✅ '.format(formatter))
