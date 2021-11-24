
from constant import BASE_PATH

SG_TWEETS_PATH = BASE_PATH + "sg.csv"
DASH_TEMPLATE = "plotly_white"

# -------- Basics ----------
BASICS_PATH = BASE_PATH + 'output/basics/basic.json'

DAILY_TWEETS_PATH = BASE_PATH + "output/basics/daily_tweets.csv"
 
HASHTAGS_PATH = BASE_PATH + "output/basics/hashtags.csv"
MENTIONS_PATH = BASE_PATH + "output/basics/mentions.csv"
SENTIMENTS_PATH = BASE_PATH + 'output/basics/sentiments.csv'

POTENTIALLY_SENSITIVE_TWEETS_COUNT_PATH = BASE_PATH + "output/basics/pst_counts.csv"
POTENTIALLY_SENSITIVE_TWEETS_PATH = BASE_PATH + "output/basics/pst_tweets.csv"
POTENTIALLY_SENSITIVE_TWEETS_DEFAULT_PERCENTILE = 0.95

# ---------- Influential countries ----------
COUNTRIES_DATA_PATH = BASE_PATH + "countries_geolocation.csv"

TOP_COUNTRY_INFLUENCER_PATH = BASE_PATH + 'output/influencers/top_countries.csv'
TOP_COUNTRY_INFLUENCER_TWEETS_PATH = BASE_PATH + 'output/influencers/top_countries_tweets.csv'

# ---------- Engagements ----------
PERCENTILE = .90
TOP_RTS_POS_NEG = 10

RT_TWEET_ID_LABEL = 'retweeted_tweet_id'
RT_TWEET_DATE_LABEL = 'retweeted_tweet_date'
RT_TWEET_USER_LABEL = 'retweeted_user_screenname'
RT_TWEET_USER_VERIFIED_LABEL = 'retweeted_user_verified'
RT_TWEET_DATE_LABEL = 'retweeted_tweet_date'

Q_TWEET_ID_LABEL = 'quoted_tweet_id'
Q_TWEET_DATE_LABEL = 'quoted_tweet_date'
Q_TWEET_USER_LABEL = 'quoted_user_screenname'
Q_TWEET_USER_VERIFIED_LABEL = 'quoted_user_verified'
Q_TWEET_DATE_LABEL = 'quoted_tweet_date'

SENTIMENT_SPREAD_THRESHOLD = 80

RETWEET = 'retweet'
QUOTED = 'quoted'

## ----------------- Retweets -----------------

# Local
NEG_LOCAL_RTS_TREND_PATH = BASE_PATH + 'output/rts/local/neg_local_rts_trend.csv'
NEG_LOCAL_RTS_INFO_PATH = BASE_PATH + 'output/rts/local/neg_local_rts_info.csv'

POS_LOCAL_RTS_TREND_PATH = BASE_PATH + 'output/rts/local/pos_local_rts_trend.csv'
POS_LOCAL_RTS_INFO_PATH = BASE_PATH + 'output/rts/local/pos_local_rts_info.csv'

ALL_LOCAL_RTS_TREND_PATH = BASE_PATH + 'output/rts/local/all_local_rts_trend.csv'
ALL_LOCAL_RTS_INFO_PATH = BASE_PATH + 'output/rts/local/all_local_rts_info.csv'

# Global
NEG_GLOBAL_RTS_TREND_PATH = BASE_PATH + 'output/rts/global/neg_global_rts_trend.csv'
NEG_GLOBAL_RTS_INFO_PATH = BASE_PATH + 'output/rts/global/neg_global_rts_info.csv'

POS_GLOBAL_RTS_TREND_PATH = BASE_PATH + 'output/rts/global/pos_global_rts_trend.csv'
POS_GLOBAL_RTS_INFO_PATH = BASE_PATH + 'output/rts/global/pos_global_rts_info.csv'

ALL_GLOBAL_RTS_TREND_PATH = BASE_PATH + 'output/rts/global/all_global_rts_trend.csv'
ALL_GLOBAL_RTS_INFO_PATH = BASE_PATH + 'output/rts/global/all_global_rts_info.csv'


## ----------------- Quoted -----------------
QUOTED_SENTIMENT_SPEAD_PATH = BASE_PATH + 'output/quoted/sentiment_spread.csv'

# ---------- Graph analysis ----------
MIN_DEGREE_TO_HAVE = 40

INFLUENTIAL_USERS_PATH = BASE_PATH + "output/influencers/top_users.csv"
INFLUENTIAL_USERS_TWEETS_PATH = BASE_PATH + "output/influencers/top_users_tweets.csv"

COMMUNITIES_PLOT_PATH = BASE_PATH + "output/communities/clusters"
COMMUNITIES_PATH = BASE_PATH + "output/communities/clusters.json"
# ----------  ----------