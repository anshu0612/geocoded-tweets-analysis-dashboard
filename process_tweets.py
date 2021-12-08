import os
import glob
import pandas as pd
import collections as col
import matplotlib.pyplot as plt
from constants.dash_constants import QUOTED, RETWEET
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from utils.process_text import TwitterDataProcessing
from constants.common import FRAGMENTED_TWEETS_PATH, \
    FRAGMENTED_TWEETS_ENGAGEMENTS_PATH, DATE_FORMAT
from constants.country_config import COUNTRY_SLANGS, KNOWN_USERNAMES_COUNTRY
from constants.common import COUNTRY, TWEETS_PATH, SINGAPORE_LABEL


def return_on_failure(value):
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except:
                print('Error')
                return value

        return applicator

    return decorate


class ProcessData():
    def __init__(self):
        print(TWEETS_PATH)
        self.tweets = pd.read_csv(TWEETS_PATH)

    def concat_and_join_data(self, tweets_path=FRAGMENTED_TWEETS_PATH,
                             engagements_tweets_path=FRAGMENTED_TWEETS_ENGAGEMENTS_PATH):
        '''
            1. Concats the fragmented data stored in csvs
            2. Join tweets and tweets' engagement data
        '''
        print(FRAGMENTED_TWEETS_PATH, FRAGMENTED_TWEETS_ENGAGEMENTS_PATH)
        # csvs containing users and tweets specific data
        tw_data = pd.concat([pd.read_csv(csv_file, index_col=0, header=0, engine='c') for csv_file in glob.glob(
            os.path.join(tweets_path, "*.csv"))], axis=0, ignore_index=True)

        # csvs containing the collected tweets' engagement data - retweets, replies and quoted tweets
        tw_eng_data = pd.concat([pd.read_csv(csv_file, index_col=0, header=0, engine='c') for csv_file in glob.glob(
            os.path.join(engagements_tweets_path, "*.csv"))], axis=0, ignore_index=True)

        self.tweets = tw_data.merge(tw_eng_data, on="tweet_id", how='inner')

    def add_tweet_date(self):
        '''
            Adds `tweet_date`
        '''
        # Drops incorrect datetime format for `tweet_time`
        self.tweets['tweet_time'] = pd.to_datetime(
            self.tweets['tweet_time'], errors='coerce')
        self.tweets = self.tweets.dropna(subset=['tweet_time'])

        # Adds tweet_date
        self.tweets['tweet_date'] = self.tweets.tweet_time.dt.strftime(
            DATE_FORMAT)

    def fill_nan_geocodings(self):
        ''''
            Replace nan geocodings with `Unknown`
        '''
        self.tweets['quoted_user_geo_coding'].fillna(
            value='Unknown', inplace=True)
        self.tweets['retweeted_user_geo_coding'].fillna(
            value='Unknown', inplace=True)
        self.tweets['user_geo_coding'].fillna(value='Unknown', inplace=True)

    def plot_countries_distribution(self, top_x=15):
        ''''
            Visualizing the distribution of geocoded tweets
        '''

        geocoded_tw_data = self.tweets['user_geo_coding']
        count_geocoded_tw_data = col.Counter(geocoded_tw_data)
        count_geocoded_tw_data = count_geocoded_tw_data.most_common()
        countries = [c[0].split('|')[0]
                     for c in count_geocoded_tw_data[:top_x]]
        counts = [c[1] for c in count_geocoded_tw_data[:top_x]]

        plt.barh(countries[::-1], counts[::-1])

        plt.ylabel("Country")
        plt.xlabel("Tweets Count")
        plt.xticks(rotation=45)
        plt.title("Distribution of tweets geocoded country")
        plt.show()

    def correct_uganda_geocoding_for_singapore(self):
        ''' 
            Bug fixing: Users whose location contains a `specific region in Singapore` 
            (e.g., West Singpore, North-east regions) are erroneously coded as `Uganda`
        '''
        # Replacing "Uganda|UG" with "Singapore|SG"
        self.tweets['user_geo_coding'].replace(
            ['Uganda|UG'], 'Singapore|SG', inplace=True)
        self.tweets['retweeted_user_geo_coding'].replace(
            ['Uganda|UG'], 'Singapore|SG', inplace=True)
        self.tweets['quoted_user_geo_coding'].replace(
            ['Uganda|UG'], 'Singapore|SG', inplace=True)

    def remove_country_code(self):
        '''
            Remove the country code from the data
        '''
        self.tweets['quoted_user_geo_coding'] = [
            c.split('|')[0] for c in self.tweets['quoted_user_geo_coding']]
        self.tweets['retweeted_user_geo_coding'] = [
            c.split('|')[0] for c in self.tweets['retweeted_user_geo_coding']]
        self.tweets['user_geo_coding'] = [
            c.split('|')[0] for c in self.tweets['user_geo_coding']]

    def set_unknown_for_multiple_geocodings(self):
        '''
            List of users with more than 2 geocoding are set to Unknown
            Note: This issue is taken care of during tweets collection
        '''
        users_geocode_country_count = self.tweets.groupby(
            'user_screenname_x')['user_geo_coding'].nunique().reset_index(name='count')
        # list of users with geocoding > 2
        users_geocode_country_count_gtr_2 = users_geocode_country_count[
            users_geocode_country_count['count'] > 2]['user_screenname_x'].unique()

        # Setting location to 'Unknown'
        self.tweets.loc[self.tweets['user_screenname_x'].isin(
            users_geocode_country_count_gtr_2), 'user_geo_coding'] = 'Unknown'
        self.tweets.loc[self.tweets['user_screenname_x'].isin(
            users_geocode_country_count_gtr_2), 'retweeted_user_geo_coding'] = 'Unknown'
        self.tweets.loc[self.tweets['user_screenname_x'].isin(
            users_geocode_country_count_gtr_2), 'retweeted_user_geo_coding'] = 'Unknown'

    def set_known_geocodings(self):
        '''
            Set the known geocodings provided in the `country_config.py` file
        '''

        # t = self.tweets[self.tweets['user_screenname_x'] == 'ChannelNewsAsia'][['user_screenname_x', 'user_geo_coding']]
        # print(t)

        for _, row in self.tweets.iterrows():
            if row['user_screenname_x'] in KNOWN_USERNAMES_COUNTRY:
                # print(row['user_screenname_x'])
                row['user_geo_coding'] = KNOWN_USERNAMES_COUNTRY[row['user_screenname_x']]

            if row['tweet_enagagement_type'] == RETWEET:
                if row['retweeted_user_screenname'] in KNOWN_USERNAMES_COUNTRY:
                    row['retweeted_user_geo_coding'] = KNOWN_USERNAMES_COUNTRY[row['retweeted_user_screenname']]

            if row['tweet_enagagement_type'] == QUOTED:
                if row['quoted_user_screenname'] in KNOWN_USERNAMES_COUNTRY:
                    row['quoted_user_geo_coding'] = KNOWN_USERNAMES_COUNTRY[row['quoted_user_screenname']]

        # t = self.tweets[self.tweets['user_screenname_x'] == 'ChannelNewsAsia'][['user_screenname_x', 'user_geo_coding']]
        # print(t)

    def filter_country_tweets(self):
        '''
            Filter tweets for `COUNTRY`
        '''
        country_slangs = '|'.join(COUNTRY_SLANGS)
        self.tweets = self.tweets[
            # 1. geo coded as Singapore
            # (self.tweets['user_geo_coding'] == 'Unknown') |
            (self.tweets['user_geo_coding'] == COUNTRY) |
            # 2. user location contains `COUNTRY_LOCATION_SLANGS`
            (self.tweets['user_location'].str.contains(country_slangs, regex=True, case=False)) |
            # 3. user description contains `COUNTRY_USER_DESCRIPTION_SLANGS`
            (self.tweets['user_desc'].str.contains(country_slangs, regex=True, case=False)) |
            # 4. Quoted tweets by `COUNTRY`` users and
            ((self.tweets['quoted_user_geo_coding'] == COUNTRY) & (self.tweets['user_geo_coding'].isna())) |
            ((self.tweets['retweeted_user_geo_coding'] == COUNTRY) & (self.tweets['user_geo_coding'].isna()))]

    def remove_amp_from_tweets_text(self):
        '''
            Remove amp from the tweets
        '''
        self.tweets['tweet_text'] = [txt.replace('&amp;', '&') if isinstance(
            txt, str) else '' for txt in self.tweets['tweet_text']]
        self.tweets['quoted_tweet_text'] = [txt.replace('&amp;', '&') if isinstance(
            txt, str) else '' for txt in self.tweets['quoted_tweet_text']]

    def processed_tweets_text(self):
        '''
            Cleaning up tweets text
        '''
        pre = TwitterDataProcessing()
        print("Processing tweets")
        processed_tweets = [pre.clean_text(text, for_sentiment_analysis=True)
                            for text in self.tweets['tweet_text']]
        self.tweets['processed_tweet_text'] = processed_tweets

        print("Processing QUOTED tweets")
        processed_quoted_tweets = [pre.clean_text(text, for_sentiment_analysis=True) if
                                   isinstance(text, str) == True else '' for text in self.tweets['quoted_tweet_text']]
        self.tweets['processed_quoted_tweet_text'] = processed_quoted_tweets

    @staticmethod
    def get_sentiment(doc):
        '''
            Mapping sentiment scores to a label
        '''
        # As per vader's repo : https://github.com/cjhutto/vaderSentiment
        analyzer = SentimentIntensityAnalyzer()
        score = analyzer.polarity_scores(doc)['compound']

        if score >= 0.05:
            sentiment = "positive"
        elif score <= -0.05:

            sentiment = "negative"
        else:
            sentiment = "neutral"
        return sentiment

    def add_sentiments(self):
        '''
            Adding sentiments to tweets and quoted tweets
        '''
        print('Adding sentiments for tweets')
        tw_sentiment = [self.get_sentiment(
            text) for text in self.tweets['processed_tweet_text']]
        self.tweets['tweet_sentiment'] = tw_sentiment

        print('Adding sentiments for QUOTED tweets')
        quoted_tw_sentiment = [self.get_sentiment(
            text) if text != '' else None for text in self.tweets['processed_quoted_tweet_text']]
        self.tweets['quoted_tweet_sentiment'] = quoted_tw_sentiment

    def save_final_csv(self):
        '''
            Saving the tweets
        '''
        self.tweets = self.tweets.loc[:, ~
                                      self.tweets.columns.str.contains('^Unnamed')]
        pd.DataFrame.to_csv(self.tweets, TWEETS_PATH)


if __name__ == "__main__":
    process = ProcessData()
    formatter = '-'*10

    print("concat_and_join_data 🚧 {}".format(formatter))
    process.concat_and_join_data()
    print("concat_and_join_data ✅ {}".format(formatter))

    print("add_tweet_date 🚧 {}".format(formatter))
    process.add_tweet_date()
    print("add_tweet_date ✅ {}".format(formatter))

    print("fill_nan_geocodings 🚧 {}".format(formatter))
    process.fill_nan_geocodings()
    print("fill_nan_geocodings ✅ {}".format(formatter))

    if COUNTRY == SINGAPORE_LABEL:
        print("correct_uganda_geocoding_for_singapore 🚧 {}".format(formatter))
        process.correct_uganda_geocoding_for_singapore()
        print("correct_uganda_geocoding_for_singapore ✅ {}".format(formatter))

    print("remove_country_code 🚧 {}".format(formatter))
    process.remove_country_code()
    print("remove_country_code ✅ {}".format(formatter))

    print("set_unknown_for_multiple_geocodings 🚧 {}".format(formatter))
    process.set_unknown_for_multiple_geocodings()
    print("set_unknown_for_multiple_geocodings ✅ {}".format(formatter))

    print("set_known_geocodings 🚧 {}".format(formatter))
    process.set_known_geocodings()
    print("set_known_geocodings ✅ {}".format(formatter))

    # filtering only if country-specific required
    if COUNTRY:
        print("filter_country_tweets 🚧 {}".format(formatter))
        process.filter_country_tweets()
        print("filter_country_tweets ✅ {}".format(formatter))

    print("remove_amp_from_tweets_text 🚧 {}".format(formatter))
    process.remove_amp_from_tweets_text()
    print("remove_amp_from_tweets_text ✅ {}".format(formatter))

    print("processed_tweets_text 🚧 {} Note: This might take time depending on the data size. 🧹, 🧽 in-progress".format(formatter))
    process.processed_tweets_text()
    print("processed_tweets_text ✅ {}".format(formatter))

    print("add_sentiments 🙂 😐 😒 🚧 {} Note: This might take time depending on the data size.".format(formatter))
    process.add_sentiments()
    print("add_sentiments ✅ {}".format(formatter))

    print("save_final_csv 🚧 {}".format(formatter))
    process.save_final_csv()
    print("save_final_csv ✅ {}".format(formatter))
