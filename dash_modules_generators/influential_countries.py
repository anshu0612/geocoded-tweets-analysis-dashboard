import collections as col
import pandas as pd
import matplotlib.pyplot as plt
from constants.dash_constants import *


def plot_top_influential_countries(c_quoted_rts_geo, x_top=10):
    quoted_rts_geo = [c[0] for c in c_quoted_rts_geo[:x_top]]
    quoted_rts_geo_count = [c[1] for c in c_quoted_rts_geo[:x_top]]

    plt.barh(quoted_rts_geo[::-1], quoted_rts_geo_count[::-1])

    plt.ylabel("rts_quoted_geo")
    plt.xlabel("Count")
    plt.xticks(rotation=45)
    plt.title("Distribution of retweeted & quoted users' location")
    plt.show()


def get_top_influential_countries(tweets, top_countries_count=10):
    # Selecting tweets created by users from other countries and known geocoding.
    quoted_tweets = tweets[(tweets['tweet_enagagement_type'] == 'Quote') &
                           (tweets['quoted_user_geo_coding'] != 'Unknown')]

    rts_tweets = tweets[(tweets['tweet_enagagement_type'] == 'Retweet') &
                        (tweets['retweeted_user_geo_coding'] != 'Unknown')]

    if COUNTRY:
        # if country specific then exclude that COUNTRY from top influencers
        quoted_tweets = quoted_tweets[quoted_tweets['quoted_user_geo_coding'] != COUNTRY]
        rts_tweets = rts_tweets[rts_tweets['retweeted_user_geo_coding'] != COUNTRY]

    quoted_rts_geo = list(quoted_tweets['quoted_user_geo_coding']) + \
        list(rts_tweets['retweeted_user_geo_coding'])
    c_quoted_rts_geo = col.Counter(quoted_rts_geo).most_common()
    # plot_top_influential_countries(c_quoted_rts_geo)
    return c_quoted_rts_geo[:top_countries_count]


def generate_dash_influential_countries(top_country_influencer, save=False,
                                        top_country_influencer_save_path=TOP_COUNTRY_INFLUENCER_PATH):

    countries_data = pd.read_csv(COUNTRIES_DATA_PATH)
    top_influential_countries_data = {
        'country': [],
        'lat': [],
        'long': [],
        'count': [],
        'size': []
    }

    sum_influence = sum([c[1] for c in top_country_influencer])

    for i in top_country_influencer:
        top_influential_countries_data['country'].append(i[0])
        top_influential_countries_data['count'].append(i[1])
        top_influential_countries_data['size'].append(
            round(i[1]/sum_influence*150, 2))
        
        country_loc = countries_data[countries_data['Country'] == i[0]]
        
        top_influential_countries_data['long'].append(
            float(country_loc.iloc[0]['Longitude (average)'].strip().strip('"')))
        top_influential_countries_data['lat'].append(
            float(country_loc.iloc[0]['Latitude (average)'].strip().strip('"')))

    top_influential_countries_df = pd.DataFrame(top_influential_countries_data)

    if save:
        pd.DataFrame.to_csv(top_influential_countries_df,
                            top_country_influencer_save_path)
        print("Saved:", top_country_influencer_save_path)

    return top_influential_countries_df


def generate_dash_influential_countries_tweets(tweets, top_influential_countries_df, save=False,
                                               top_country_influencer_tweets_save_path=TOP_COUNTRY_INFLUENCER_TWEETS_PATH):
    top_influential_countries = top_influential_countries_df['country']
    top_countries_tweets_df = tweets[(tweets['retweeted_user_geo_coding'].isin(top_influential_countries))
                                     & (tweets['processed_tweet_text'].notna())][['retweeted_user_geo_coding', 'processed_tweet_text']]

    if save:
        pd.DataFrame.to_csv(top_countries_tweets_df,
                            top_country_influencer_tweets_save_path)
        print("Saved:", top_country_influencer_tweets_save_path)

    return top_countries_tweets_df
