
import pandas as pd
import plotly.express as px
import re
import collections as col
import matplotlib.pyplot as plt
from dash_constants import *


def get_tweet_id_by_count(tweets_df, engagement_type, tweets_count=TOP_RTS_POS_NEG):
    engagement_id_label = RT_TWEET_ID_LABEL if engagement_type == RETWEET else Q_TWEET_ID_LABEL

    # count of RTs
    c_tweets_df = tweets_df.value_counts(subset=[engagement_id_label]).reset_index(
        name='local_count').sort_values('local_count', ascending=False)
    return list(c_tweets_df[:tweets_count][engagement_id_label])


def get_tweet_id_by_spike(tweets_df, engagement_type, percentile=PERCENTILE):
    engagement_id_label = RT_TWEET_ID_LABEL if engagement_type == RETWEET else Q_TWEET_ID_LABEL

    grouped_sorted_date = tweets_df.groupby([engagement_id_label, 'tweet_date']).apply(
        pd.DataFrame.sort_values, 'tweet_date').reset_index(drop=True)
    max_grouped_sorted_date = grouped_sorted_date.groupby(
        [engagement_id_label, 'tweet_date'])['total_engagement'].max().reset_index()
    max_grouped_sorted_date['delta_engagement'] = max_grouped_sorted_date.groupby(
        [engagement_id_label])['total_engagement'].diff().fillna(0).astype(int)
    spike_df = max_grouped_sorted_date.groupby(engagement_id_label).nth(1)

    spike_value = spike_df['delta_engagement'].quantile(percentile)
    spike_ids = list(spike_df[spike_df['delta_engagement']
                     > spike_value].reset_index()[engagement_id_label])
    print("Total spiky tweets:", len(spike_ids))
    return spike_ids


def get_bursty_tweets(tweets_df, ids, engagement_type, get_trend=False):
    engagement_id_label = RT_TWEET_ID_LABEL if engagement_type == RETWEET else Q_TWEET_ID_LABEL
    engagement_date_label = RT_TWEET_DATE_LABEL if engagement_type == RETWEET else Q_TWEET_DATE_LABEL
    engagement_user_label = RT_TWEET_USER_LABEL if engagement_type == RETWEET else Q_TWEET_USER_LABEL

    viral_tweets = tweets_df[tweets_df[engagement_id_label].isin(ids)]

    # get data for delta and cumulative graphs
    grouped_sorted_date = viral_tweets.groupby([engagement_id_label, engagement_date_label, 'tweet_date', engagement_user_label]).apply(
        pd.DataFrame.sort_values, 'tweet_date').reset_index(drop=True)

    max_grouped_sorted_date = None
    if get_trend:
        max_grouped_sorted_date = grouped_sorted_date.groupby(
            [engagement_id_label, engagement_date_label, 'tweet_date', engagement_user_label])['total_engagement'].max().reset_index()
        max_grouped_sorted_date['delta_engagement'] = max_grouped_sorted_date.groupby(
            [engagement_id_label])['total_engagement'].diff().fillna(0).astype(int)

    return max_grouped_sorted_date, viral_tweets


def get_bursty_tweets_info(tweets_df, engagement_type):
    engagement_id_label = RT_TWEET_ID_LABEL if engagement_type == RETWEET else Q_TWEET_ID_LABEL
#     engagement_date_label = RT_TWEET_DATE_LABEL if engagement_type == RETWEET else Q_TWEET_DATE_LABEL
    engagement_user_label = RT_TWEET_USER_LABEL if engagement_type == RETWEET else Q_TWEET_USER_LABEL
    engagement_user_verified_label = RT_TWEET_USER_LABEL if engagement_type == RETWEET else Q_TWEET_USER_LABEL

    # remove @ from RTs
    tweets_df['tweet_text_'] = [re.sub(
        "RT @[A-Z_a-z_0-9:]+", "", txt).strip() for txt in tweets_df['tweet_text']]
    details_tweets_df = tweets_df[['tweet_text_', 'tweet_date', 'tweet_sentiment', engagement_user_label, 'total_engagement',
                                   engagement_user_verified_label, engagement_id_label]] \
        .groupby(engagement_id_label) \
        .apply(pd.DataFrame.sort_values, 'total_engagement') \
        .reset_index(drop=True).groupby(engagement_id_label).last().reset_index()
    details_tweets_df = details_tweets_df.loc[:, ~
                                              details_tweets_df.columns.str.contains('^Unnamed')]
    k = px.colors.qualitative.Pastel[:details_tweets_df.shape[0]]
    details_tweets_df['color'] = k
    return details_tweets_df


def generate_dash_bursty_retweets(eng_tweets,
                                  trend_save_path,
                                  info_save_path,
                                  percentile=PERCENTILE,
                                  top_tweets_count=TOP_RTS_POS_NEG,
                                  save=False):
    c_ids = get_tweet_id_by_count(eng_tweets, RETWEET, top_tweets_count)
    s_ids = get_tweet_id_by_spike(eng_tweets, RETWEET, percentile)

    # temp fix to get only 10
    bursty_trend_df, bursty_tweets_df = get_bursty_tweets(
        eng_tweets, list(set(c_ids + s_ids))[:10], RETWEET, True)
    bursty_info_df = get_bursty_tweets_info(bursty_tweets_df, RETWEET)

    if save:
        pd.DataFrame.to_csv(bursty_trend_df, trend_save_path)
        pd.DataFrame.to_csv(bursty_info_df, info_save_path)

    print("Saved trend and info!")

    return bursty_trend_df, bursty_info_df


def get_bursty_quoted_tweets(eng_tweets, percentile=PERCENTILE, top_tweets_count=TOP_RTS_POS_NEG):
    c_ids = get_tweet_id_by_count(eng_tweets, QUOTED, top_tweets_count)
    s_ids = get_tweet_id_by_spike(eng_tweets, QUOTED, percentile)

    # temp fix to get only 10
    _, bursty_tweets_df = get_bursty_tweets(
        eng_tweets, list(set(c_ids + s_ids)), QUOTED, True)
    return bursty_tweets_df


def get_formatted_quoted_tweets(sg_tweets):
    tweet_enagagement_quotes = sg_tweets[sg_tweets['tweet_enagagement_type'] == 'Quote']

    tweet_enagagement_quotes['quoted_tweet_time'] = pd.to_datetime(
        tweet_enagagement_quotes['quoted_tweet_time'], errors='coerce')
    tweet_enagagement_quotes = tweet_enagagement_quotes.dropna(
        subset=['quoted_tweet_time'])
    tweet_enagagement_quotes['quoted_tweet_date'] = tweet_enagagement_quotes.quoted_tweet_time.dt.strftime(
        '%Y-%m-%d')

    tweet_enagagement_quotes['total_engagement'] = tweet_enagagement_quotes['quoted_retweet_count'] + \
        tweet_enagagement_quotes['quoted_favorite_count']

    tweet_enagagement_quotes[['quoted_tweet_id', 'total_engagement']] = tweet_enagagement_quotes[[
        'quoted_tweet_id', 'total_engagement']].astype(int)
    tweet_enagagement_quotes = tweet_enagagement_quotes.loc[:,
                                                            ~tweet_enagagement_quotes.columns.str.contains('^Unnamed')]
    return tweet_enagagement_quotes


def get_quoted_tweets_by_date(tweet_enagagement_quotes, from_date, to_date):
    return tweet_enagagement_quotes[(tweet_enagagement_quotes['quoted_tweet_date'].between(from_date, to_date, inclusive='both'))]


def get_most_spread_quoted_by_sentiment_with_rate(tweets_df, rate):
    quoted_by_sentiment = tweets_df.groupby(['quoted_tweet_id', 'tweet_sentiment']).size()\
        .unstack(fill_value=0).reset_index()

    quoted_by_sentiment['pos_count'] = quoted_by_sentiment['positive'] / (quoted_by_sentiment['positive'] +
                                                                          quoted_by_sentiment['negative'] +
                                                                          quoted_by_sentiment['neutral'])*100

    quoted_by_sentiment['neg_count'] = quoted_by_sentiment['negative'] / (quoted_by_sentiment['positive'] +
                                                                          quoted_by_sentiment['negative'] +
                                                                          quoted_by_sentiment['neutral'])*100

    return quoted_by_sentiment[(quoted_by_sentiment['pos_count'] >= rate) | (quoted_by_sentiment['neg_count'] >= rate)]


def generate_dash_bursty_quotes_by_sentiment(bursty_quoted_tweets,
                                             most_spread_quoted_by_sentiment_with_rate,
                                             save=False,
                                             sentiment_spread_save_path=QUOTED_SENTIMENT_SPEAD_PATH):
    most_spread_quoted_ids = list(
        most_spread_quoted_by_sentiment_with_rate['quoted_tweet_id'])
    most_spread_quoted_info = bursty_quoted_tweets[bursty_quoted_tweets['quoted_tweet_id'].isin(
        most_spread_quoted_ids)]
    most_spread_quoted_info = most_spread_quoted_info[['quoted_tweet_id', 'quoted_tweet_text', 'quoted_user_screenname',
                                                       'quoted_user_geo_coding', 'quoted_tweet_date', 'quoted_user_verified', 'total_engagement']]
    most_spread_quoted_info = most_spread_quoted_info.loc[most_spread_quoted_info.groupby(
        ["quoted_tweet_id"])["total_engagement"].idxmax()]

    final_most_spread_quoted = most_spread_quoted_info.merge(
        most_spread_quoted_by_sentiment_with_rate, on="quoted_tweet_id", how='inner')
    print(final_most_spread_quoted.shape)

    final_most_spread_quoted.drop(
        ['negative', 'positive', 'neutral'], 1, inplace=True)

    # Adding `spread_type` and `spread_rate`. SENTIMENT_SPREAD_THRESHOLD% <= positivity spread and SENTIMENT_SPREAD_THRESHOLD% <= negativity spread
    final_most_spread_quoted['spread_type'] = ['positive' if spread_rate >=
                                               SENTIMENT_SPREAD_THRESHOLD else 'negative' for spread_rate in final_most_spread_quoted['pos_count']]
    final_most_spread_quoted['spread_rate'] = [round(row['pos_count'], 2) if row['spread_type'] == 'positive'
                                               else round(row['neg_count'], 2) for _, row in final_most_spread_quoted.iterrows()]

    final_most_spread_quoted.drop(['pos_count', 'neg_count'], 1, inplace=True)

    if save:
        pd.DataFrame.to_csv(final_most_spread_quoted,
                            sentiment_spread_save_path)
    return final_most_spread_quoted


def get_formatted_retweets(sg_tweets):
    tweet_enagagement_retweet = sg_tweets[sg_tweets['tweet_enagagement_type'] == 'Retweet']

    # retweet time processing
    tweet_enagagement_retweet['retweeted_tweet_time'] = pd.to_datetime(
        tweet_enagagement_retweet['retweeted_tweet_time'], errors='coerce')
    tweet_enagagement_retweet = tweet_enagagement_retweet.dropna(
        subset=['retweeted_tweet_time'])
    tweet_enagagement_retweet['retweeted_tweet_date'] = tweet_enagagement_retweet.retweeted_tweet_time.dt.strftime(
        '%Y-%m-%d')

    # summing RTs + <3
    tweet_enagagement_retweet['total_engagement'] = tweet_enagagement_retweet['retweeted_retweet_count'] + \
        tweet_enagagement_retweet['retweeted_favorite_count']
    tweet_enagagement_retweet[['retweeted_tweet_id', 'total_engagement']] = tweet_enagagement_retweet[[
        'retweeted_tweet_id', 'total_engagement']].astype(int)
    tweet_enagagement_retweet = tweet_enagagement_retweet.loc[:,
                                                              ~tweet_enagagement_retweet.columns.str.contains('^Unnamed')]
    return tweet_enagagement_retweet


def plot_countries_with_most_rts_creators(tweet_enagagement_retweet, get_formatted_retweets):
    rts_geo = tweet_enagagement_retweet['retweeted_user_geo_coding']
    c_rts_geo = col.Counter(rts_geo).most_common()

    x_top = 20

    rts_geo = [c[0] for c in c_rts_geo[:x_top]]
    counts = [c[1] for c in c_rts_geo[:x_top]]

    plt.barh(rts_geo[::-1], counts[::-1])

    plt.ylabel("rts_quoted_geo")
    plt.xlabel("Count")
    plt.xticks(rotation=45)
    plt.title("Distribution of original retweet location")
    plt.show()
