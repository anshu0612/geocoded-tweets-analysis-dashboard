import json
import pandas as pd
import collections as col
from dash_constants import *
# import matplotlib.pyplot as plt


def get_date_range(sg_tweets):
    max_date = sg_tweets['tweet_date'].max()
    min_date = sg_tweets['tweet_date'].min()
    return min_date, max_date


def get_user_is_verified(sg_tweets):
    sg_tweets[sg_tweets['user_']]


def generate_dash_basic_stats(sg_tweets, save=False, basics_save_path=BASICS_PATH):
    total_tweets = len(sg_tweets)

    min_date, max_date = get_date_range(sg_tweets)

    daily_tweets = sg_tweets.groupby(
        'tweet_date')['tweet_id'].count().reset_index(name='count')
    avg_tweets = sum(daily_tweets['count'][:-1]) / \
        len(daily_tweets['count'][:-1])

    users = sg_tweets['user_id_x'].nunique()

    basic = {
        'total_tweets': total_tweets,
        'min_date': min_date,
        'max_date': max_date,
        'users_count': users,
        'avg_tweets': int(avg_tweets)
    }

    if save:
        with open(basics_save_path, 'w') as fp:
            json.dump(basic, fp)
            print("Saved:", basics_save_path)

    return basic


def generate_dash_daily_tweets(sg_tweets, save=False, daily_tweets_save_path=DAILY_TWEETS_PATH):
    daily_tweets = sg_tweets.groupby(
        'tweet_date')['tweet_id'].count().reset_index(name='count')
    if save:
        pd.DataFrame.to_csv(daily_tweets, daily_tweets_save_path)
        print("Saved:", daily_tweets_save_path)

    return daily_tweets


def generate_dash_hashtags(sg_tweets, from_date, to_date, save=False, hashtags_save_path=HASHTAGS_PATH, top_hash_count=20):
    min_date, max_date = get_date_range(sg_tweets)
    # print("----&&&&&&&&&&&-------", min_date, max_date)
    if not from_date:
        from_date = min_date
    if not to_date:
        to_date = max_date

    sg_tweets_hashtags = sg_tweets[sg_tweets['entity_hashtags'].notna(
    ) & sg_tweets['tweet_date'].between(from_date, to_date, inclusive='both')]['entity_hashtags']

    # print("Count of tweets with hashtags {}".format(len(sg_tweets_hashtags)))
    # print("% of tweets with hashtags {}".format(
    #     len(sg_tweets_hashtags)/len(sg_tweets)*100))

    hashtags = []

    for h in sg_tweets_hashtags:
        h_list = [hh for hh in h.split('|') if hh not in [
            'Singapore', 'singapore', 'sg']]
        hashtags.extend(h_list)

    # print("Total hashtags:", len(hashtags))
    # print("Total unique hashtags:", len(set(hashtags)))

    count_hashtags = col.Counter(hashtags).most_common()
    hashtags = [c[0] for c in count_hashtags[:top_hash_count]]
    counts = [c[1] for c in count_hashtags[:top_hash_count]]

    # Saving data for the dashboard
    hashtags_data = {
        "counts": counts[::-1],
        "hashtag": hashtags[::-1]
    }

    df_hashtags_data = pd.DataFrame(data=hashtags_data)

    if save:
        pd.DataFrame.to_csv(df_hashtags_data, hashtags_save_path)
        print("Saved:", hashtags_save_path)

    return df_hashtags_data


def generate_dash_mentions(sg_tweets, from_date, to_date, save=False, mentions_save_path=MENTIONS_PATH, top_mentions_count=20):
    min_date, max_date = get_date_range(sg_tweets)
    if not from_date:
        from_date = min_date
    if not to_date:
        to_date = max_date

    sg_tweets_mentions = sg_tweets[sg_tweets['entity_mentions'].notna(
    ) & sg_tweets['tweet_date'].between(from_date, to_date, inclusive='both')]['entity_mentions']

    # print("Count of tweets with mentions {}".format(len(sg_tweets_mentions)))
    # print("% tweets with mentions {}".format(
    #     len(sg_tweets_mentions)/len(sg_tweets)*100))

    mentions = []

    for m in sg_tweets_mentions:
        m_list = [mm for mm in m.split('|')]
        mentions.extend(m_list)

    # print("Total mentions:", len(mentions))
    # print("Total unique mentions:", len(set(mentions)))

    count_mentions = col.Counter(mentions).most_common()

    mentions = [c[0] for c in count_mentions[:top_mentions_count]]
    counts = [c[1] for c in count_mentions[:top_mentions_count]]

    # plot_mentions(mentions, counts)

    # Saving data for the dashboard
    mentions_data = {
        "counts": counts[::-1],
        "mention": mentions[::-1]
    }

    df_mentions_data = pd.DataFrame(data=mentions_data)

    if save:
        pd.DataFrame.to_csv(df_mentions_data, mentions_save_path)
        print("Saved:", mentions_save_path)

    return df_mentions_data


def generate_dash_sentiments(sg_tweets, from_date, to_date, save=False, sentiments_save_path=SENTIMENTS_PATH):
    min_date, max_date = get_date_range(sg_tweets)
    if not from_date:
        from_date = min_date
    if not to_date:
        to_date = max_date

    df_sentiments = sg_tweets[sg_tweets['tweet_date'].between(from_date, to_date, inclusive='both')] \
        .value_counts(subset=['tweet_sentiment']).reset_index(name='count').sort_values(['count'], ascending=False)

    if save:
        pd.DataFrame.to_csv(df_sentiments, sentiments_save_path)
        print("Saved:", sentiments_save_path)
    return df_sentiments


def generate_dash_potentially_sensitive_tweets(sg_tweets, save=False,
                                               pst_count_save_path=POTENTIALLY_SENSITIVE_TWEETS_COUNT_PATH,
                                               pst_tweets_save_path=POTENTIALLY_SENSITIVE_TWEETS_PATH,
                                               percentile=POTENTIALLY_SENSITIVE_TWEETS_DEFAULT_PERCENTILE):
    sg_tweets_pst = sg_tweets[sg_tweets['tweet_possibly_sensitive'] == True]

    # print("Total possibily sensitive tweets {}".format(len(sg_tweets_pst)))
    # print("% possibily sensitive tweets {}".format(
    #     len(sg_tweets_pst)/len(sg_tweets)*100))

    c_sg_tweets_pst = sg_tweets_pst.value_counts(subset=['tweet_date']).reset_index(name='count') \
        .sort_values(['tweet_date'], ascending=False)
    # print("Average number of Potentially sensitive tweets: ",
    #       sum(c_sg_tweets_pst['count'])/len(c_sg_tweets_pst))
    spike_value = c_sg_tweets_pst['count'].quantile(percentile)
    # print("spike_value", spike_value)
#     pst_counts = c_sg_tweets_pst[c_sg_tweets_pst['count'] > spike_value]
    pst_tweets = sg_tweets_pst[['tweet_date', 'processed_tweet_text']]

    if save:
        pd.DataFrame.to_csv(c_sg_tweets_pst, pst_count_save_path)
        pd.DataFrame.to_csv(pst_tweets, pst_tweets_save_path)
        print("Saved:", pst_count_save_path, pst_tweets_save_path)

    return (c_sg_tweets_pst, pst_tweets)
