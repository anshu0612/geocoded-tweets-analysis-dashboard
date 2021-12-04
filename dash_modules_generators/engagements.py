import re
import pandas as pd
import collections as col
import plotly.express as px
import matplotlib.pyplot as plt

from constants.dash_constants import *


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
    # print("Total spiky tweets:", len(spike_ids))
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
    engagement_date = RT_TWEET_DATE_LABEL if engagement_type == RETWEET else Q_TWEET_DATE_LABEL
    engagement_geocoding_label = RT_USER_GEOCODING if engagement_type == RETWEET else Q_USER_GEOCODING

    # remove @ from RTs
    tweets_df['tweet_text_'] = [re.sub(
        "RT @[A-Z_a-z_0-9:]+", "", txt).strip() for txt in tweets_df['tweet_text']]
    details_tweets_df = tweets_df[['tweet_text_', 'tweet_date', 'tweet_sentiment', engagement_geocoding_label, engagement_date, engagement_user_label, 'total_engagement',
                                   engagement_user_verified_label, engagement_id_label]] \
        .groupby(engagement_id_label) \
        .apply(pd.DataFrame.sort_values, 'total_engagement') \
        .reset_index(drop=True).groupby(engagement_id_label).last().reset_index()
    details_tweets_df = details_tweets_df.loc[:, ~
                                              details_tweets_df.columns.str.contains('^Unnamed')]

    details_tweets_df['color'] = px.colors.qualitative.Alphabet[:details_tweets_df.shape[0]]
    return details_tweets_df


def get_retweets(tweets):
    retweets = tweets[tweets['tweet_enagagement_type'] == 'Retweet']

    # `retweeted_tweet_time` processing
    retweets['retweeted_tweet_time'] = pd.to_datetime(
        retweets['retweeted_tweet_time'], errors='coerce')
    retweets = retweets.dropna(
        subset=['retweeted_tweet_time'])
    retweets['retweeted_tweet_date'] = retweets.retweeted_tweet_time.dt.strftime(
        '%Y-%m-%d')

    # adding `total_engagement` = RTs + <3
    retweets['total_engagement'] = retweets['retweeted_retweet_count'] + \
        retweets['retweeted_favorite_count']

    # converting `retweeted_tweet_id` and `total_engagement` to int
    retweets[['retweeted_tweet_id', 'total_engagement']] = retweets[[
        'retweeted_tweet_id', 'total_engagement']].astype(int)
    retweets = retweets.loc[:, ~retweets.columns.str.contains('^Unnamed')]
    return retweets


def generate_dash_bursty_retweets(eng_tweets,
                                  save,
                                  trend_save_path,
                                  info_save_path,
                                  tweets_limit=25,
                                  percentile=PERCENTILE,
                                  top_tweets_count=TOP_RTS_POS_NEG):

    c_ids = get_tweet_id_by_count(eng_tweets, RETWEET, top_tweets_count)
    s_ids = get_tweet_id_by_spike(eng_tweets, RETWEET, percentile)

    bursty_trend_df, bursty_tweets_df = get_bursty_tweets(
        # eng_tweets, list(set(c_ids + s_ids)), RETWEET, True)
        eng_tweets, list(set(c_ids + s_ids))[:tweets_limit], RETWEET, True)
    bursty_info_df = get_bursty_tweets_info(bursty_tweets_df, RETWEET)

    if save:
        pd.DataFrame.to_csv(bursty_trend_df, trend_save_path)
        pd.DataFrame.to_csv(bursty_info_df, info_save_path)
        print("Saved: ", trend_save_path)
        print("Saved: ", info_save_path)

    return bursty_trend_df, bursty_info_df


def plot_countries_with_most_rts_creators(tweet_enagagement_retweet, top_x):
    rts_geo = tweet_enagagement_retweet['retweeted_user_geo_coding']
    c_rts_geo = col.Counter(rts_geo).most_common()

    rts_geo = [c[0] for c in c_rts_geo[:top_x]]
    counts = [c[1] for c in c_rts_geo[:top_x]]

    plt.barh(rts_geo[::-1], counts[::-1])

    plt.ylabel("rts_quoted_geo")
    plt.xlabel("Count")
    plt.xticks(rotation=45)
    plt.title("Distribution of original retweet location")
    plt.show()


def get_quoted_tweets(tweets):
    tweet_enagagement_quotes = tweets[tweets['tweet_enagagement_type'] == 'Quote']

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


def get_quoted_tweets_by_date(tweet_enagagement_quotes, min_date, max_date, from_date=None, to_date=None):
    if not from_date:
        from_date = min_date
    if not to_date:
        to_date = max_date

    return tweet_enagagement_quotes[(tweet_enagagement_quotes['quoted_tweet_date'].between(from_date, to_date, inclusive='both'))]


def get_high_spreadrate_quoted_by_sentiment(tweets_df, rate=SENTIMENT_SPREAD_THRESHOLD):
    quoted_by_sentiment = tweets_df.groupby(['quoted_tweet_id', 'tweet_sentiment']).size()\
        .unstack(fill_value=0).reset_index()

    quoted_by_sentiment = quoted_by_sentiment[(
        quoted_by_sentiment['positive'] > QUOTED_SENTIMENT_COUNT_THRESHOLD) |
        (quoted_by_sentiment['negative'] > QUOTED_SENTIMENT_COUNT_THRESHOLD)]

    quoted_by_sentiment['pos_percent'] = quoted_by_sentiment['positive'] / (quoted_by_sentiment['positive'] +
                                                                            quoted_by_sentiment['negative'] +
                                                                            quoted_by_sentiment['neutral'])*100

    quoted_by_sentiment['neg_percent'] = quoted_by_sentiment['negative'] / (quoted_by_sentiment['positive'] +
                                                                            quoted_by_sentiment['negative'] +
                                                                            quoted_by_sentiment['neutral'])*100

    return quoted_by_sentiment[(quoted_by_sentiment['pos_percent'] >= rate) |
                               (quoted_by_sentiment['neg_percent'] >= rate)]


def generate_dash_bursty_quotes_by_sentiment(bursty_quoted_tweets,
                                             high_spreadrate_quoted_by_sentiment,
                                             save=False,
                                             sentiment_spread_save_path=QUOTED_SENTIMENT_SPEAD_PATH):
    most_spread_quoted_ids = list(
        high_spreadrate_quoted_by_sentiment['quoted_tweet_id'])
    most_spread_quoted_info = bursty_quoted_tweets[bursty_quoted_tweets['quoted_tweet_id'].isin(
        most_spread_quoted_ids)]
    most_spread_quoted_info = most_spread_quoted_info[['quoted_tweet_id', 'quoted_tweet_text', 'quoted_user_screenname',
                                                       'quoted_user_geo_coding', 'quoted_tweet_date',
                                                       'quoted_user_verified', 'total_engagement']]
    most_spread_quoted_info = most_spread_quoted_info.loc[most_spread_quoted_info.groupby(
        ["quoted_tweet_id"])["total_engagement"].idxmax()]

    final_most_spread_quoted = most_spread_quoted_info.merge(
        high_spreadrate_quoted_by_sentiment, on="quoted_tweet_id", how='inner')

    final_most_spread_quoted.drop(
        ['negative', 'positive', 'neutral'], 1, inplace=True)

    # Adding `spread_type` and `spread_rate`. SENTIMENT_SPREAD_THRESHOLD% <= positivity spread and SENTIMENT_SPREAD_THRESHOLD% <= negativity spread
    final_most_spread_quoted['spread_type'] = ['positive' if spread_rate >=
                                               SENTIMENT_SPREAD_THRESHOLD else 'negative' for spread_rate in final_most_spread_quoted['pos_percent']]
    final_most_spread_quoted['spread_rate'] = [round(row['pos_percent'], 2) if row['spread_type'] == 'positive'
                                               else round(row['neg_percent'], 2) for _, row in final_most_spread_quoted.iterrows()]

    final_most_spread_quoted.drop(
        ['pos_percent', 'neg_percent'], 1, inplace=True)

    final_most_spread_quoted = final_most_spread_quoted
    if save:
        pd.DataFrame.to_csv(final_most_spread_quoted,
                            sentiment_spread_save_path)
        print("Saved: ", sentiment_spread_save_path)
    return final_most_spread_quoted


def get_bursty_quoted_tweets(eng_tweets, percentile=PERCENTILE, top_tweets_count=TOP_RTS_POS_NEG):
    c_ids = get_tweet_id_by_count(eng_tweets, QUOTED, top_tweets_count)
    s_ids = get_tweet_id_by_spike(eng_tweets, QUOTED, percentile)

    # temp fix to get only 10
    _, bursty_tweets_df = get_bursty_tweets(
        eng_tweets, list(set(c_ids + s_ids)), QUOTED, False)
    return bursty_tweets_df
