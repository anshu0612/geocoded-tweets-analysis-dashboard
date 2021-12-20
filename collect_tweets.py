'''
    Major part of this code has been written by Jithin Vachery (@jithinvachery). 
'''
import os
import json
import tweepy
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import argparse

load_dotenv()

# get filters
def get_list_from_csv(f_name, key):
    data = []
    _df = pd.read_csv(f_name)

    for _, row in _df.iterrows():
        data.append(row[key].strip())

    return data

# import filters from csvs
hashtags_fiters = get_list_from_csv(
    "data/tweets_collection_filters/hashtags.csv", 'hashtag')
keywords_filters = get_list_from_csv(
    "data/tweets_collection_filters/keywords.csv", 'Keyword')

# get db name
parser = argparse.ArgumentParser()
parser.add_argument('--db_name', type=str,
                    help="MongoDB name to store tweets")
args = parser.parse_args()
DB_NAME = args.db_name

# get Twitter API credentials
APP_KEY = os.environ.get('TWITTER_APP_KEY')
APP_SECRET = os.environ.get('TWITTER_APP_SECRET')
OAUTH_TOKEN = os.environ.get('TWITTER_OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = os.environ.get('TWITTER_OAUTH_TOKEN_SECRET')

# connect to Mongo DB
client = MongoClient('localhost', 27017)
db = client[DB_NAME]

f_name_counter = "collection.counter"


def get_coll_num():
    with open(f_name_counter, 'r') as reader:
        processed = int(reader.read())
        return processed


def set_coll_num(n):
    with open(f_name_counter, "w") as outfile:
        outfile.write(str(n))


def get_collection(n):
    collections_name = "tweets_" + str(n)
    print()
    print("collection set to ", collections_name)
    return db[collections_name]


coll_num = get_coll_num()
collection = get_collection(coll_num)
num_tweets = 1

First_Time = True


class StreamListener(tweepy.StreamListener):
    # This is a class provided by tweepy to access the Twitter Streaming API.

    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")​

    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occurred: ' + repr(status_code))
        return False

    def on_data(self, data):
        global num_tweets, db, collection, coll_num
        # This is the meat of the script...it connects to your mongoDB and stores the tweet
        try:
            # client = MongoClient(MONGO_HOST)

            # Use twitter_db database. If it doesn't exist, it will be created.
            # db = client.twitter_db

            # Decode the JSON from Twitter
            data_json = json.loads(data)

            # grab the 'created_at' data from the Tweet to use for display
            # created_at = data_json['created_at']

            # print out a message to the screen that we have collected a tweet
            # print("Tweet collected at " + str(created_at))
            print("\r", num_tweets, end='')
            num_tweets += 1

            global First_Time
            if First_Time:
                First_Time = False
                print("Tweet id: ", data_json["id_str"])

            if num_tweets % 1000 == 0:
                # see if we need to start a new collection
                c = collection.estimated_document_count()
                print(" estimated count : ", c, end='')
                if c > 10*1000*1000:
                    # start a new collection
                    coll_num += 1
                    set_coll_num(coll_num)
                    collection = get_collection(coll_num)

            # insert the data into the mongoDB into a collection called twitter_search
            # if twitter_search doesn't exist, it will be created.
            collection.insert(data_json)
        except Exception as e:
            print(e)


auth = tweepy.OAuthHandler(APP_KEY, APP_SECRET)
auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

# Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.
listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
streamer = tweepy.Stream(auth=auth, listener=listener)

search_terms = []
search_terms.extend(hashtags_fiters)
search_terms.extend(keywords_filters)
# search_terms.extend(handles_filters)

print("DB_NAME : ", DB_NAME)
print("Tracking: " + str(search_terms))
streamer.filter(track=search_terms)
# streamer.filter(follow=search_handles)
