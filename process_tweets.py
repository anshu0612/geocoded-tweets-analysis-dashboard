from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from utils.process_text import TwitterDataProcessing
import os
import pandas as pd
from constants.common import FRAGMENTED_TWEETS_PATH, \
    FRAGMENTED_TWEETS_ENGAGEMENTS_PATH
from constants.country_config import COUNTRY_LOCATION_SLANGS, \
    COUNTRY_USER_DESCRIPTION_SLANGS, COUNTRY
import collections as col
import matplotlib.pyplot as plt
from constants.common import TWEETS_PATH
import glob

class ProcessData():
    def __init__(self):
        self.tweets = None

    def concat_and_merge_data(self, tweets_path=FRAGMENTED_TWEETS_PATH,
                              engagements_tweets_path=FRAGMENTED_TWEETS_ENGAGEMENTS_PATH):
        # csvs containing users and tweets specific data
        tw_data = pd.concat([pd.read_csv(csv_file, index_col=0, header=0, engine='python') for csv_file in glob.glob(
            os.path.join(tweets_path, "*.csv"))], axis=0, ignore_index=True)

        # csvs containing the collected tweets' engagement data - retweets, replies and quoted tweets
        tw_eng_data = pd.concat([pd.read_csv(csv_file, index_col=0, header=0, engine='python') for csv_file in glob.glob(
            os.path.join(engagements_tweets_path, "*.csv"))], axis=0, ignore_index=True)

        self.tweets = tw_data.merge(tw_eng_data, on="tweet_id", how='inner')
        # self.tweets.shape

    def add_tweet_date(self):
        self.tweets['tweet_time'] = pd.to_datetime(
            self.tweets['tweet_time'], errors='coerce')
        self.tweets = self.tweets.dropna(subset=['tweet_time'])

        self.tweets['tweet_datetime'] = self.tweets.tweet_time.dt.strftime(
            '%Y-%m-%d %H')
        self.tweets['tweet_date'] = self.tweets.tweet_time.dt.strftime(
            '%Y-%m-%d')

    def fill_geocoded_unknown(self):
        self.tweets['quoted_user_geo_coding'].fillna(
            value='Unknown', inplace=True)
        self.tweets['retweeted_user_geo_coding'].fillna(
            value='Unknown', inplace=True)
        self.tweets['user_geo_coding'].fillna(value='Unknown', inplace=True)

    def plot_countries_distribution(self):
        ''''
            Visualizing the distribution of geocoded tweets
        '''

        geocoded_tw_data = self.tweets['user_geo_coding']
        count_geocoded_tw_data = col.Counter(geocoded_tw_data)
        count_geocoded_tw_data = count_geocoded_tw_data.most_common()

        TOP_X = 15
        countries = [c[0].split('|')[0]
                    for c in count_geocoded_tw_data[:TOP_X]]
        counts = [c[1] for c in count_geocoded_tw_data[:TOP_X]]

        plt.barh(countries[::-1], counts[::-1])

        plt.ylabel("Country")
        plt.xlabel("Tweets Count")
        plt.xticks(rotation=45)
        plt.title("Distribution of tweets geocoded country")
        plt.show()

    def correct_geocodings(self):
        # wrong_geocoded_uganda_users = list(
        #     self.tweets[self.tweets['user_geo_coding'] == 'Uganda|UG']['user_screenname_x'].unique())
        # for _ in range(5):
        #     print("https://twitter.com/" +
        #           random.choice(wrong_geocoded_uganda_users))

        # self.tweets['user_geo_coding'].replace(
        #     ['Uganda|UG'], 'Singapore|SG', inplace=True)
        # self.tweets['retweeted_user_geo_coding'].replace(
        #     ['Uganda|UG'], 'Singapore|SG', inplace=True)
        # self.tweets['quoted_user_geo_coding'].replace(
        #     ['Uganda|UG'], 'Singapore|SG', inplace=True)

        self.tweets['quoted_user_geo_coding'] = [
            c.split('|')[0] for c in self.tweets['quoted_user_geo_coding']]
        self.tweets['retweeted_user_geo_coding'] = [
            c.split('|')[0] for c in self.tweets['retweeted_user_geo_coding']]
        self.tweets['user_geo_coding'] = [
            c.split('|')[0] for c in self.tweets['user_geo_coding']]

        users_geocode_country_count = self.tweets.groupby(
            'user_screenname_x')['user_geo_coding'].nunique().reset_index(name='count')
        # list of countries with geocoding > 2
        users_geocode_country_count_gtr_2 = users_geocode_country_count[
            users_geocode_country_count['count'] > 2]['user_screenname_x'].unique()

        # Setting location to 'Unknown'
        self.tweets.loc[self.tweets['user_screenname_x'].isin(
            users_geocode_country_count_gtr_2), 'user_geo_coding'] = 'Unknown'
        self.tweets.loc[self.tweets['user_screenname_x'].isin(
            users_geocode_country_count_gtr_2), 'retweeted_user_geo_coding'] = 'Unknown'
        self.tweets.loc[self.tweets['user_screenname_x'].isin(
            users_geocode_country_count_gtr_2), 'retweeted_user_geo_coding'] = 'Unknown'

    def filter_country_tweets(self):
        self.tweets = self.tweets[
            # 1. geo coded as Singapore
            #                     (self.tweets['user_geo_coding'] == 'Unknown') |
            (self.tweets['user_geo_coding'] == COUNTRY) |
            # 2. user location contains {sg, spore, singapore, singapura}
            (self.tweets['user_location'].str.contains(COUNTRY_LOCATION_SLANGS, regex=True, case=False)) |
            # 3. user description contains {spore, singapore, singapura}
            (self.tweets['user_desc'].str.contains(COUNTRY_USER_DESCRIPTION_SLANGS, regex=True, case=False)) |
            # 4. Quoted tweets by Singaporean and
            ((self.tweets['quoted_user_geo_coding'] == COUNTRY) & (self.tweets['user_geo_coding'].isna())) |
            ((self.tweets['retweeted_user_geo_coding'] == COUNTRY) & (self.tweets['user_geo_coding'].isna()))]

    def processed_tweets(self):
        # 3.4. Processing the tweets and quoted tweets <a id="cell34"></a>
        self.tweets['tweet_text'] = [txt.replace('&amp;', '&') if isinstance(
            txt, str) else '' for txt in self.tweets['tweet_text']]
        self.tweets['quoted_tweet_text'] = [txt.replace('&amp;', '&') if isinstance(
            txt, str) else '' for txt in self.tweets['quoted_tweet_text']]

        pre = TwitterDataProcessing()
        processed_tweets = [pre.clean_text(text)
                            for text in self.tweets['tweet_text']]
        self.tweets['processed_tweet_text'] = processed_tweets

        processed_quoted_tweets = [pre.clean_text(text) if
                                   isinstance(text, str) == True else '' for text in self.tweets['quoted_tweet_text']]
        self.tweets['processed_quoted_tweet_text'] = processed_quoted_tweets

    @staticmethod
    def get_sentiment(doc):
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
        tw_sentiment = [self.get_sentiment(
            text) for text in self.tweets['processed_tweet_text']]
        self.tweets['tweet_sentiment'] = tw_sentiment

        quoted_tw_sentiment = [self.get_sentiment(text) if text != '' else None for text in self.tweets['processed_quoted_tweet_text']]
        self.tweets['quoted_tweet_sentiment'] = quoted_tw_sentiment

    def save_final_csv(self):
        from constants.common import DATA_PATH
        self.tweets = self.tweets.loc[:, ~self.tweets.columns.str.contains('^Unnamed')]
        pd.DataFrame.to_csv(self.tweets, TWEETS_PATH)

    
if __name__ == "__main__":
    process = ProcessData()

    process.concat_and_merge_data() 
    print("Done concat_and_merge_data")
    process.add_tweet_date()
    print("Done add_tweet_date")

    process.fill_geocoded_unknown()
    print("Done fill_geocoded_unknown")

    process.correct_geocodings()
    print("Done correct_geocodings")

    # process.filter_country_tweets()
    # print("Done filter_country_tweets")

    process.processed_tweets()
    print("Done processed_tweets")

    process.add_sentiments()
    print("Done add_sentiments")

    process.save_final_csv()
    print("Done save_final_csv")
