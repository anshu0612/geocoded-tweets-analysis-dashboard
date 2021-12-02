DATA_PATH = '../data/'
SG_TWEETS_PATH = 'fragmented_data/tweets_sg/'
SG_TWEETS_ENGAGEMENTS_PATH = 'fragmented_data/tweets_engagements_sg/'



# csvs containing users and tweets specific data
tw_data = pd.concat([pd.read_csv(csv_file, index_col=0, header=0, engine='python') for csv_file in glob.glob(
            os.path.join(DATA_PATH, SG_TWEETS_PATH, "*.csv"))], axis=0, ignore_index=True)

# csvs containing the collected tweets' engagement data - retweets, replies and quoted tweets
tw_eng_data = pd.concat([pd.read_csv(csv_file, index_col=0, header=0, engine='python') for csv_file in glob.glob(
            os.path.join(DATA_PATH, SG_TWEETS_ENGAGEMENTS_PATH, "*.csv"))], axis=0, ignore_index=True)


tweets_data = tw_data.merge(tw_eng_data, on="tweet_id", how = 'inner')
tweets_data.shape

tweets_data['tweet_time'] = pd.to_datetime(tweets_data['tweet_time'], errors='coerce')
tweets_data = tweets_data.dropna(subset=['tweet_time'])

tweets_data['tweet_datetime'] = tweets_data.tweet_time.dt.strftime('%Y-%m-%d %H')
tweets_data['tweet_date'] = tweets_data.tweet_time.dt.strftime('%Y-%m-%d')

tweets_data['quoted_user_geo_coding'].fillna(value='Unknown', inplace=True)
tweets_data['retweeted_user_geo_coding'].fillna(value='Unknown', inplace=True)
tweets_data['user_geo_coding'].fillna(value='Unknown', inplace=True)

geocoded_tw_data = tweets_data['user_geo_coding']

count_geocoded_tw_data = col.Counter(geocoded_tw_data)
count_geocoded_tw_data = count_geocoded_tw_data.most_common()

##### Visualizing the distribution of geocoded tweets 
TOP_X = 15
countries = [c[0].split('|')[0] for c in count_geocoded_tw_data[:TOP_X]]
counts = [c[1] for c in count_geocoded_tw_data[:TOP_X]]

plt.barh(countries[::-1], counts[::-1])
 
plt.ylabel("Country")
plt.xlabel("Tweets Count")
plt.xticks(rotation=45)
plt.title("Distribution of tweets geocoded country")
plt.show()


wrong_geocoded_uganda_users  = list(tweets_data[tweets_data['user_geo_coding'] == 'Uganda|UG']['user_screenname_x'].unique())
for _ in range(5):
    print("https://twitter.com/" + random.choice(wrong_geocoded_uganda_users))


tweets_data['user_geo_coding'].replace(['Uganda|UG'], 'Singapore|SG', inplace=True)
tweets_data['retweeted_user_geo_coding'].replace(['Uganda|UG'], 'Singapore|SG', inplace=True)
tweets_data['quoted_user_geo_coding'].replace(['Uganda|UG'], 'Singapore|SG', inplace=True)


tweets_data['quoted_user_geo_coding'] = [c.split('|')[0] for c in tweets_data['quoted_user_geo_coding']]
tweets_data['retweeted_user_geo_coding'] = [c.split('|')[0] for c in tweets_data['retweeted_user_geo_coding']]
tweets_data['user_geo_coding'] = [c.split('|')[0] for c in tweets_data['user_geo_coding']]


users_geocode_country_count = tweets_data.groupby('user_screenname_x')['user_geo_coding'].nunique().reset_index(name='count')
# list of countries with geocoding > 2
users_geocode_country_count_gtr_2 = users_geocode_country_count[users_geocode_country_count['count'] > 2]['user_screenname_x'].unique()

# Setting location to 'Unknown'
tweets_data.loc[tweets_data['user_screenname_x'].isin(users_geocode_country_count_gtr_2), 'user_geo_coding'] = 'Unknown'
tweets_data.loc[tweets_data['user_screenname_x'].isin(users_geocode_country_count_gtr_2), 'retweeted_user_geo_coding'] = 'Unknown'
tweets_data.loc[tweets_data['user_screenname_x'].isin(users_geocode_country_count_gtr_2), 'retweeted_user_geo_coding'] = 'Unknown'


### 3.3. Filtering out non-Singapore accounts - reducing false positives and false negatives <a id="cell33"></a>
sg_tweets = tweets_data[
                    # 1. geo coded as Singapore
#                     (tweets_data['user_geo_coding'] == 'Unknown') | 
                    (tweets_data['user_geo_coding'] == 'Singapore') | 
                    # 2. user location contains {sg, spore, singapore, singapura}
                    (tweets_data['user_location'].str.contains('sg|spore|singapore|singapura', regex=True, case=False)) |
                    # 3. user description contains {spore, singapore, singapura}
                    (tweets_data['user_desc'].str.contains('spore|singapore|singapura', regex=True, case=False)) |
                     # 4. Quoted tweets by Singaporean and 
                    ((tweets_data['quoted_user_geo_coding'] == 'Singapore') & (tweets_data['user_geo_coding'].isna())) |
                    ((tweets_data['retweeted_user_geo_coding'] == 'Singapore') & (tweets_data['user_geo_coding'].isna()))
            ]

### 3.4. Processing the tweets and quoted tweets <a id="cell34"></a>
sg_tweets['tweet_text'] = [txt.replace('&amp;', '&') if isinstance(txt, str) else '' for txt in sg_tweets['tweet_text']]
sg_tweets['quoted_tweet_text'] = [ txt.replace('&amp;', '&') if isinstance(txt, str) else '' for txt in sg_tweets['quoted_tweet_text']]


from utils.process_text import TwitterDataProcessing
pre = TwitterDataProcessing()


processed_tweets = [pre.clean_text(text) for text in sg_tweets['tweet_text']]
sg_tweets['processed_tweet_text'] = processed_tweets

processed_quoted_tweets = [pre.clean_text(text) if isinstance(text, str) == True else '' for text in sg_tweets['quoted_tweet_text']]
sg_tweets['processed_quoted_tweet_text'] = processed_quoted_tweets


from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
def get_sentiment(doc):
    score = analyzer.polarity_scores(doc)['compound']
    # As per vader's repo : https://github.com/cjhutto/vaderSentiment
    if score >= 0.05:
        sentiment = "positive"
    elif score <= -0.05:

        sentiment = "negative"
    else:
        sentiment = "neutral"
    return sentiment


tw_sentiment = [get_sentiment(text) for text in sg_tweets['processed_tweet_text']]
sg_tweets['tweet_sentiment'] = tw_sentiment

quoted_tw_sentiment = [get_sentiment(text) if text != '' else None for text in sg_tweets['processed_quoted_tweet_text']]
sg_tweets['quoted_tweet_sentiment'] = quoted_tw_sentiment


sg_tweets = sg_tweets.loc[:, ~sg_tweets.columns.str.contains('^Unnamed')]
pd.DataFrame.to_csv(sg_tweets, DATA_PATH + "sg.csv")


