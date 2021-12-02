import plotly.express as px
from utils.constants import DATA_PATH, DATA_DASH_PATH

GRAPHS_TEMPLATE = 'plotly_white'

SG_TWEETS_PATH = DATA_PATH + 'sg.csv'
DASH_TEMPLATE = 'plotly_white'

HOME_PATH = '/'
NETWORKING_PATH = '/networking'
ENGAGEMENTS_PATH = '/engagements'
INFLUENCERS_PATH = '/influencers'

ERROR_INSUFFICIENT_TWEETS = 'Oops! Not enough tweets. Try other filter value.'

NAVBAR_TITLE = "Singapore's Pulse Monitoring through Twitter's Lens"
TWITTER_LOGO_PATH = 'assets/twitter-logo.png'
APP_LOGO = 'assets/pulse.png'

# Dates
DASH_NO_YEAR_FORMAT = "%d %b"
DASH_FORMAT = "%d %b, %Y"
DATE_FORMAT = '%Y-%m-%d'

# -------- Basics ----------
TWEETS_STATS_HEADING = 'Tweets Stats'
BASICS_PATH = DATA_DASH_PATH + 'basics/basic.json'

DAILY_TWEETS_HEADING = 'Daily tweets count'
DAILY_TWEETS_PATH = DATA_DASH_PATH + 'basics/daily_tweets.csv'

# -------------------
MENTIONS_HASHTAGS_SENTIMENT_HEADING = 'Trending hashtags, mentions and public sentiments'
MENTIONS_HASHTAGS_SENTIMENT_INFO_CONTENT = '1. Top hashtags and mentions by frequency. \n 2.' \
    + 'Sentiments distribution of public'
HASHTAGS_PATH = DATA_DASH_PATH + 'basics/hashtags.csv'
MENTIONS_PATH = DATA_DASH_PATH + 'basics/mentions.csv'
SENTIMENTS_PATH = DATA_DASH_PATH + 'basics/sentiments.csv'

# ------------------------
PSTS_HEADING = 'Potentially sensitive tweets: '
PSTS_INFO_CONTENT = 'Tweets containing a link that may contain content or media identified as sensitive. ' \
    'It does not pertain to a tweet content itself.'
POTENTIALLY_SENSITIVE_TWEETS_COUNT_PATH = DATA_DASH_PATH + 'basics/pst_counts.csv'
POTENTIALLY_SENSITIVE_TWEETS_PATH = DATA_DASH_PATH + 'basics/pst_tweets.csv'
POTENTIALLY_SENSITIVE_TWEETS_DEFAULT_PERCENTILE = 0.95

# ---------- Influential countries ----------
INFLUENTIAL_COUNTRIES_INFO_CONTENT = 'Tweets by non-Singapore-based users with a high number of engagements' \
    '- retweets and quoted tweets, by Singapore-based users.' \
    ' Bubble sizes reflect the relative total engagements, received by country-specific tweets.'
COUNTRIES_DATA_PATH = DATA_PATH + 'general\countries_geolocation.csv'

TOP_COUNTRY_INFLUENCER_PATH = DATA_DASH_PATH + 'influencers/top_countries.csv'
TOP_COUNTRY_INFLUENCER_TWEETS_PATH = DATA_DASH_PATH + \
    'influencers/top_countries_tweets.csv'
TOP_COUNTRIES_CLEANED_DATA = DATA_PATH + 'general/top_countries_data.csv'

# ---------- Engagements ----------
PERCENTILE = .90
TOP_RTS_POS_NEG = 10

RT_TWEET_ID_LABEL = 'retweeted_tweet_id'
RT_TWEET_DATE_LABEL = 'retweeted_tweet_date'
RT_TWEET_USER_LABEL = 'retweeted_user_screenname'
RT_TWEET_USER_VERIFIED_LABEL = 'retweeted_user_verified'
RT_TWEET_DATE_LABEL = 'retweeted_tweet_date'
RT_USER_GEOCODING = 'retweeted_user_geo_coding'

Q_TWEET_ID_LABEL = 'quoted_tweet_id'
Q_TWEET_DATE_LABEL = 'quoted_tweet_date'
Q_TWEET_USER_LABEL = 'quoted_user_screenname'
Q_TWEET_USER_VERIFIED_LABEL = 'quoted_user_verified'
Q_TWEET_DATE_LABEL = 'quoted_tweet_date'
Q_USER_GEOCODING = 'quoted_user_geo_coding'

SENTIMENT_SPREAD_THRESHOLD = 80

RETWEET = 'retweet'
QUOTED = 'quoted'

# ----------------- Retweets -----------------
VIRAL_RETWEETS_INFO_CONTENT = '(2) highly retweeted by count or (3) received an unusual number of endorsements - retweets and favorites'
VIRAL_RETWEETS_DATE_INFO_CONTENT = 'Tweets created between {} and {} that are (1) by '

# Local
NEG_LOCAL_RTS_TREND_PATH = DATA_DASH_PATH + 'rts/local/neg_local_rts_trend.csv'
NEG_LOCAL_RTS_INFO_PATH = DATA_DASH_PATH + 'rts/local/neg_local_rts_info.csv'

POS_LOCAL_RTS_TREND_PATH = DATA_DASH_PATH + 'rts/local/pos_local_rts_trend.csv'
POS_LOCAL_RTS_INFO_PATH = DATA_DASH_PATH + 'rts/local/pos_local_rts_info.csv'

ALL_LOCAL_RTS_TREND_PATH = DATA_DASH_PATH + 'rts/local/all_local_rts_trend.csv'
ALL_LOCAL_RTS_INFO_PATH = DATA_DASH_PATH + 'rts/local/all_local_rts_info.csv'

# Global
NEG_GLOBAL_RTS_TREND_PATH = DATA_DASH_PATH + \
    'rts/global/neg_global_rts_trend.csv'
NEG_GLOBAL_RTS_INFO_PATH = DATA_DASH_PATH + 'rts/global/neg_global_rts_info.csv'

POS_GLOBAL_RTS_TREND_PATH = DATA_DASH_PATH + \
    'rts/global/pos_global_rts_trend.csv'
POS_GLOBAL_RTS_INFO_PATH = DATA_DASH_PATH + 'rts/global/pos_global_rts_info.csv'

ALL_GLOBAL_RTS_TREND_PATH = DATA_DASH_PATH + \
    'rts/global/all_global_rts_trend.csv'
ALL_GLOBAL_RTS_INFO_PATH = DATA_DASH_PATH + 'rts/global/all_global_rts_info.csv'


# ----------------- Quoted -----------------
QUOTED_SENTIMENT_COUNT_THRESHOLD = 10
VIRAL_QUOTED_INFO_CONTENT = 'Tweets created between {} and {} that are (1) highly quoted by count or (2)' \
    ' received an unusual number of endorsements - retweets and favorites'

REACTIVE_TWEETS_INFO_CONTENT = 'Viral quoted tweets with high intensity of extreme sentiments (positive and negative sentiments)'

QUOTED_SENTIMENT_SPEAD_PATH = DATA_DASH_PATH + 'quoted/sentiment_spread.csv'

# ---------- Graph analysis ----------
# Graph styling
CLUSTER_START_COLOR = 3
CLUSTER_COLORS_DICT = {str(idx): color for idx, color in enumerate(
    px.colors.qualitative.Bold[CLUSTER_START_COLOR:])}
CIRCLE_SIZE = '14px'
FONT_SIZE = '8px'
LINE_WIDTH = '0.2px'
NETWORKING_GRAPH_HEIGHT = '500px'

MIN_DEGREE_TO_HAVE = 40

INTERACTIONS_GRAPH_INFO_CONTENT = 'A directed weighted graph of interactions - replies, retweets, and quoted tweets' \
    ' between the users.  The weights denote the number of interactions between two users.'

INFLUENTIAL_USERS_INFO_CONTENT = 'Applied PageRanking on interactions graph to get the top 50 users.' \
    ' The number signifies the ranking of a user. '

INFLUENTIAL_USERS_PATH = DATA_DASH_PATH + 'influencers/top_users.csv'
INFLUENTIAL_USERS_TWEETS_PATH = DATA_DASH_PATH + \
    'influencers/top_users_tweets.csv'

COMMUNITIES_INFO_CONTENT = 'Detected {} communties: '
COMMUNITIES_PLOT_PATH = DATA_DASH_PATH + 'networking/clusters'
COMMUNITIES_USERS_PATH = DATA_DASH_PATH + 'networking/clusters_users.json'
COMMUNITIES_TWEETS_PATH = DATA_DASH_PATH + 'networking/clusters_tweets.json'
USER_TO_COMMUNITY_PATH = DATA_DASH_PATH + 'networking/user_to_cluster.json'

NETWORKING_DATA = DATA_DASH_PATH + 'networking/networking.json'
NETWORKING_GRAPH_DATA = DATA_DASH_PATH + 'networking/networking.json'
# ----------  ----------
