import os
import logging
import pandas as pd
from pymongo import MongoClient
from sshtunnel import SSHTunnelForwarder
from rich import print
from dotenv import load_dotenv
# import re
from utils.detect_place import get_geo_user_location, get_geo_latlng
from constant import ALPHA2_TO_COUNTRY
import time, datetime

from enum import Enum 

# from geopy.geocoders import Nominatim
# geolocator = Nominatim(user_agent="anshu")

load_dotenv()
logging.basicConfig(filename='tweets.log', filemode="a+",
                    level=logging.INFO, format='%(asctime)-15s %(levelname)s:%(message)s')

SG_SLANGS = ['sg', 'spore', 'singapore', 'singapura']


def geo_coding(tweet):
    country_info = None
    coding_type = None
    try:
        u = tweet['user']
        if tweet['coordinates']:  # exact location
            country_info = get_geo_latlng(
                tweet['coordinates']['coordinates'][0], tweet['coordinates']['coordinates'][1])
            coding_type = 'Coordinates'
        elif 'place' in tweet and tweet['place']:  # specific place or country
            p = tweet['place']  # p['country']
            country_info = (
                ALPHA2_TO_COUNTRY[p['country_code']], p['country_code'])
            coding_type = 'Place'
        elif u['location']:
            country_info = get_geo_user_location(u['location'])
            if country_info: coding_type = 'Location'
        if country_info and  u['description']:
                country_info = get_geo_user_location(u['description'])
                if country_info: coding_type = 'Description'
    except Exception as e:
        print(e)
    return country_info, coding_type


def create_geo_users_csv(data, start_csv_no=1, running_tw_save_count=1000, max_csv_tw_count=8000):
    global collection_no, db_name, collection_no, sg_users

    # print("Start time: ")
    st = time.time() 
    tweet_csv_data = {}
    tweet_eng_csv_data = {}

    # ------------- basic tweet's details --5
    tweet_id = []  # string
    tweet_text = []  # string
    tweet_time = []  # string
    tweet_lang = []
    tweet_possibly_sensitive = []

    # ------------- entities in a tweet -- 4
    entity_image_url = []
    entity_mentions = []
    entity_hashtags = []
    entity_link_url = []

    # -------------  user information -- 11
    user_id = []
    user_name = []
    user_screenname = []
    user_friends_count = []
    user_followers_count = []
    user_verified = []
    user_location = []
    user_desc = []
    user_geo_tagging = []
    user_geo_coding = []
    user_geo_coding_type = []

    # ------------- engagements -- 1
    tweet_enagagement_type = []  # {reply, retweet, quote}

    # reply -- 3
    replied_to_tweet_id = []
    replied_to_user_id = []
    replied_to_user_screenname = []

    # retweet -- 10
    retweeted_tweet_id = []
    retweeted_tweet_time = []  # extra over retweet
    retweeted_user_id = []
    retweeted_user_name = []
    retweeted_user_verified = []
    retweeted_user_screenname = []
    retweeted_user_geo_coding = []
    retweeted_user_geo_coding_type = []
    retweeted_retweet_count = []
    retweeted_favorite_count = []

    # quote -- 11
    quoted_tweet_text = []  # extra over retweet
    quoted_tweet_id = []
    quoted_tweet_time = []
    quoted_user_id = []
    quoted_user_name = []
    quoted_user_verified = []
    quoted_user_screenname = []
    quoted_user_geo_coding = []
    quoted_user_geo_coding_type = []
    quoted_retweet_count = []
    quoted_favorite_count = []

    # tracking counters
    total_tweets = 0
    valid_tweets = 0

    for tweet in data.find():
        total_tweets += 1

        # if collection_no == 100 and total_tweets < 7693871:
        #     continue

        if 'limit' in tweet:
            continue

        # if hasattr(tweet, 'limit'):
        #     continue

        u = tweet['user']
        # print(u)
        # filtering SG user
        if not (str(u['id']) in sg_users) and  \
            not (tweet['place'] and tweet['place']['country_code'] == 'SG') and \
                not (u['location'] and any(sg_ref in u['location'].lower().split(' ') for sg_ref in SG_SLANGS)) and \
                not (u['description'] and any(sg_ref in u['description'].lower().split(' ') for sg_ref in SG_SLANGS)):
            continue
        
        # print("FOUND")
        # GEO TAGGING
        geo_info = ''
        if tweet['coordinates']:  # exact location
            geo_info = 'LOC|{}|{}'.format(
                tweet['coordinates']['coordinates'][0], tweet['coordinates']['coordinates'][1])
        elif tweet['place']:  # specific place or country
            p = tweet['place']
            geo_info = 'PLACE|{}|{}|{}'.format(p['full_name'],
                                               p['country'], p['country_code'])

        user_geo_tagging.append(geo_info)

        tweet_time.append(tweet['created_at'])
        tweet_text.append(tweet['text'])
        tweet_id.append(tweet['id'])
        tweet_lang.append(tweet['lang'])
        tweet_possibly_sensitive.append(tweet['possibly_sensitive'] if 'possibly_sensitive' in tweet else None)

        # User Details -- 10
        user_id.append(u['id'])
        user_name.append(u['name'])
        user_screenname.append(u['screen_name'])
        user_friends_count.append(u['friends_count'])
        user_followers_count.append(u['followers_count'])
        user_verified.append(u['verified'])
        user_location.append(u['location'])
        user_desc.append(u['description'])

        ori_geo_coding = geo_coding(tweet)
        oriu_geo_coding = ori_geo_coding[0][0] + '|' + ori_geo_coding[0][1] if ori_geo_coding[0] else None
        user_geo_coding.append(oriu_geo_coding)
        user_geo_coding_type.append(ori_geo_coding[1] if ori_geo_coding[1] else None)

        # entities
        e = tweet['entities']
        entity_link_url.append(
            e['urls'][0]['url'] if e['urls'] else None)
        entity_image_url.append(
            e['media'][0]['media_url_https'] if 'media' in e else None)  # and len(e['media']) > 0

        mentions = ''
        if e['user_mentions']:
            for m in e['user_mentions']:
                mentions += m['screen_name'] + '|'
        entity_mentions.append(mentions.rstrip('|'))

        hashtags = ''
        if e['hashtags']:
            for h in e['hashtags']:
                hashtags += h['text'] + '|'
        entity_hashtags.append(hashtags.rstrip('|'))

        # engagements
        engagement_type = None
        in_reply_to_status_id = None
        in_reply_to_user_id = None
        in_reply_to_screen_name = None

        q_text = None
        q_id = None
        q_created_at = None
        q_retweet_count = None
        q_favorite_count = None
        qu_id = None
        qu_name = None
        qu_verified = None
        qu_screen_name = None
        qu_geo_coding = None
        qu_geo_coding_type = None

        r_id = None
        r_created_at = None
        r_retweet_count = None
        r_favorite_count = None
        ru_id = None
        ru_name = None
        ru_verified = None
        ru_screen_name = None
        ru_geo_coding = None
        ru_geo_coding_type = None

        if tweet['in_reply_to_status_id']:
            engagement_type = 'Reply'
            in_reply_to_status_id = tweet['in_reply_to_status_id']
            in_reply_to_user_id = tweet['in_reply_to_user_id']
            in_reply_to_screen_name = tweet['in_reply_to_screen_name']

        elif 'quoted_status' in tweet:
            engagement_type = 'Quote'

            q = tweet['quoted_status']
            q_text = q['text']
            q_id = q['id']
            q_created_at = q['created_at']
            q_retweet_count = q['retweet_count']
            q_favorite_count = q['favorite_count']

            qu = q['user']
            qu_id = qu['id']
            qu_name = qu['name']
            qu_verified = qu['verified']
            qu_screen_name = qu['screen_name']
            q_geo_coding = geo_coding(q)
            qu_geo_coding = q_geo_coding[0][0] + '|' + \
                q_geo_coding[0][1] if q_geo_coding[0] else None
            qu_geo_coding_type = q_geo_coding[1]

        elif 'retweeted_status' in tweet:
            engagement_type = 'Retweet'

            r = tweet['retweeted_status']
            r_id = r['id']
            r_created_at = r['created_at']
            r_retweet_count = r['retweet_count']
            r_favorite_count = r['favorite_count']

            ru = r['user']
            ru_id = ru['id']
            ru_name = ru['name']
            ru_verified = ru['verified']
            ru_screen_name = ru['screen_name']
            r_geo_coding = geo_coding(r)
            ru_geo_coding = r_geo_coding[0][0] + '|' + \
                r_geo_coding[0][1] if r_geo_coding[0] else None
            ru_geo_coding_type = r_geo_coding[1]

        # append values
        tweet_enagagement_type.append(engagement_type)

        replied_to_tweet_id.append(in_reply_to_status_id)
        replied_to_user_id.append(in_reply_to_user_id)
        replied_to_user_screenname.append(in_reply_to_screen_name)

        quoted_tweet_text.append(q_text)
        quoted_tweet_id.append(q_id)
        quoted_tweet_time.append(q_created_at)
        quoted_retweet_count.append(q_retweet_count)
        quoted_favorite_count.append(q_favorite_count)
        quoted_user_id.append(qu_id)
        quoted_user_name.append(qu_name)
        quoted_user_verified.append(qu_verified)
        quoted_user_screenname.append(qu_screen_name)
        quoted_user_geo_coding.append(qu_geo_coding)
        quoted_user_geo_coding_type.append(qu_geo_coding_type)

        retweeted_tweet_id.append(r_id)
        retweeted_tweet_time.append(r_created_at)
        retweeted_retweet_count.append(r_retweet_count)
        retweeted_favorite_count.append(r_favorite_count)
        retweeted_user_id.append(ru_id)
        retweeted_user_name.append(ru_name)
        retweeted_user_verified.append(ru_verified)
        retweeted_user_screenname.append(ru_screen_name)
        retweeted_user_geo_coding.append(ru_geo_coding)
        retweeted_user_geo_coding_type.append(ru_geo_coding_type)

        valid_tweets += 1
        

        # BATCH SAVING DATA
        if valid_tweets % running_tw_save_count == 0:
            tweet_csv_data['tweet_text'] = tweet_text
            tweet_csv_data['tweet_time'] = tweet_time
            tweet_csv_data['tweet_id'] = tweet_id
            tweet_csv_data['tweet_lang'] = tweet_lang
            tweet_csv_data['tweet_possibly_sensitive'] = tweet_possibly_sensitive

            tweet_csv_data['entity_image_url'] = entity_image_url
            tweet_csv_data['entity_mentions'] = entity_mentions
            tweet_csv_data['entity_hashtags'] = entity_hashtags
            tweet_csv_data['entity_link_url'] = entity_link_url

            tweet_csv_data['user_id'] = user_id
            tweet_csv_data['user_name'] = user_name
            tweet_csv_data['user_screenname'] = user_screenname
            tweet_csv_data['user_friends_count'] = user_friends_count
            tweet_csv_data['user_followers_count'] = user_followers_count
            tweet_csv_data['user_verified'] = user_verified
            tweet_csv_data['user_location'] = user_location
            tweet_csv_data['user_desc'] = user_desc
            tweet_csv_data['user_geo_coding'] = user_geo_coding
            # tweet_csv_data['user_geo_coding_type'] = user_geo_coding_type
            tweet_csv_data['user_geo_tagging'] = user_geo_tagging

            tweet_eng_csv_data['user_id'] = user_id
            tweet_eng_csv_data['user_name'] = user_name
            tweet_eng_csv_data['user_screenname'] = user_screenname
            tweet_eng_csv_data['tweet_id'] = tweet_id

            tweet_eng_csv_data['tweet_enagagement_type'] = tweet_enagagement_type
            tweet_eng_csv_data['replied_to_tweet_id'] = replied_to_tweet_id
            tweet_eng_csv_data['replied_to_user_id'] = replied_to_user_id
            tweet_eng_csv_data['replied_to_user_screenname'] = replied_to_user_screenname
            tweet_eng_csv_data['retweeted_tweet_id'] = retweeted_tweet_id
            tweet_eng_csv_data['retweeted_tweet_time'] = retweeted_tweet_time
            tweet_eng_csv_data['retweeted_user_id'] = retweeted_user_id
            tweet_eng_csv_data['retweeted_user_name'] = retweeted_user_name
            tweet_eng_csv_data['retweeted_user_verified'] = retweeted_user_verified
            tweet_eng_csv_data['retweeted_user_screenname'] = retweeted_user_screenname
            tweet_eng_csv_data['retweeted_user_geo_coding'] = retweeted_user_geo_coding
            tweet_eng_csv_data['retweeted_user_geo_coding_type'] = retweeted_user_geo_coding_type
            tweet_eng_csv_data['retweeted_retweet_count'] = retweeted_retweet_count
            tweet_eng_csv_data['retweeted_favorite_count'] = retweeted_favorite_count

            tweet_eng_csv_data['quoted_tweet_text'] = quoted_tweet_text
            tweet_eng_csv_data['quoted_tweet_id'] = quoted_tweet_id
            tweet_eng_csv_data['quoted_tweet_time'] = quoted_tweet_time
            tweet_eng_csv_data['quoted_user_id'] = quoted_user_id
            tweet_eng_csv_data['quoted_user_name'] = quoted_user_name
            tweet_eng_csv_data['quoted_user_verified'] = quoted_user_verified
            tweet_eng_csv_data['quoted_user_screenname'] = quoted_user_screenname
            tweet_eng_csv_data['quoted_user_geo_coding'] = quoted_user_geo_coding
            tweet_eng_csv_data['quoted_user_geo_coding_type'] = quoted_user_geo_coding_type
            tweet_eng_csv_data['quoted_retweet_count'] = quoted_retweet_count
            tweet_eng_csv_data['quoted_favorite_count'] = quoted_favorite_count

            # batch storing 1000 tweets
            df = pd.DataFrame(data=tweet_csv_data)
            tw_file_name = "data/v2/{}/{}_{}.csv".format("tw_sg_" + db_name.lower(),
                                                      collection_no, start_csv_no)
            df.to_csv(tw_file_name)

            df = pd.DataFrame(data=tweet_eng_csv_data)
            tw_eng_file_name = "data/v2/{}/{}_{}.csv".format("tw_eng_sg_" + db_name.lower(),
                                                          collection_no, start_csv_no)
            df.to_csv(tw_eng_file_name)
            print("Saved tweets --->", tw_file_name, tw_eng_file_name)
            print(valid_tweets, "/", total_tweets)

        if valid_tweets % max_csv_tw_count == 0:
            start_csv_no += 1

            # ------------- basic tweet's details --5
            tweet_id = []  # string
            tweet_text = []  # string
            tweet_time = []  # string
            tweet_lang = []
            tweet_possibly_sensitive = []

            # ------------- entities in a tweet -- 4
            entity_image_url = []
            entity_mentions = []
            entity_hashtags = []
            entity_link_url = []

            # -------------  user information -- 11
            user_id = []
            user_name = []
            user_screenname = []
            user_friends_count = []
            user_followers_count = []
            user_verified = []
            user_location = []
            user_desc = []
            user_geo_tagging = []
            user_geo_coding = []
            user_geo_coding_type = []

            # ------------- engagements -- 1
            tweet_enagagement_type = []  # {reply, retweet, quote}

            # reply -- 3
            replied_to_tweet_id = []
            replied_to_user_id = []
            replied_to_user_screenname = []

            # retweet -- 10
            retweeted_tweet_id = []
            retweeted_tweet_time = []  # extra over retweet
            retweeted_user_id = []
            retweeted_user_name = []
            retweeted_user_verified = []
            retweeted_user_screenname = []
            retweeted_user_geo_coding = []
            retweeted_user_geo_coding_type = []
            retweeted_retweet_count = []
            retweeted_favorite_count = []

            # quote -- 11
            quoted_tweet_text = []  # extra over retweet
            quoted_tweet_id = []
            quoted_tweet_time = []
            quoted_user_id = []
            quoted_user_name = []
            quoted_user_verified = []
            quoted_user_screenname = []
            quoted_user_geo_coding = []
            quoted_user_geo_coding_type = []
            quoted_retweet_count = []
            quoted_favorite_count = []

            print("RENEWING WITH CSV NO - {}".format(start_csv_no).center(100, '-'))

            

    # final save
    tweet_csv_data['tweet_text'] = tweet_text
    tweet_csv_data['tweet_time'] = tweet_time
    tweet_csv_data['tweet_id'] = tweet_id
    tweet_csv_data['tweet_lang'] = tweet_lang
    tweet_csv_data['tweet_possibly_sensitive'] = tweet_possibly_sensitive

    tweet_csv_data['entity_image_url'] = entity_image_url
    tweet_csv_data['entity_mentions'] = entity_mentions
    tweet_csv_data['entity_hashtags'] = entity_hashtags
    tweet_csv_data['entity_link_url'] = entity_link_url

    tweet_csv_data['user_id'] = user_id
    tweet_csv_data['user_name'] = user_name
    tweet_csv_data['user_screenname'] = user_screenname
    tweet_csv_data['user_friends_count'] = user_friends_count
    tweet_csv_data['user_followers_count'] = user_followers_count
    tweet_csv_data['user_verified'] = user_verified
    tweet_csv_data['user_location'] = user_location
    tweet_csv_data['user_desc'] = user_desc
    tweet_csv_data['user_geo_coding'] = user_geo_coding
    tweet_csv_data['user_geo_coding'] = user_geo_coding
    tweet_csv_data['user_geo_tagging'] = user_geo_tagging

    tweet_eng_csv_data['user_id'] = user_id
    tweet_eng_csv_data['user_name'] = user_name
    tweet_eng_csv_data['user_screenname'] = user_screenname
    tweet_eng_csv_data['tweet_id'] = tweet_id

    tweet_eng_csv_data['tweet_enagagement_type'] = tweet_enagagement_type
    tweet_eng_csv_data['replied_to_tweet_id'] = replied_to_tweet_id
    tweet_eng_csv_data['replied_to_user_id'] = replied_to_user_id
    tweet_eng_csv_data['replied_to_user_screenname'] = replied_to_user_screenname
    tweet_eng_csv_data['retweeted_tweet_id'] = retweeted_tweet_id
    tweet_eng_csv_data['retweeted_tweet_time'] = retweeted_tweet_time
    tweet_eng_csv_data['retweeted_user_id'] = retweeted_user_id
    tweet_eng_csv_data['retweeted_user_name'] = retweeted_user_name
    tweet_eng_csv_data['retweeted_user_verified'] = retweeted_user_verified
    tweet_eng_csv_data['retweeted_user_screenname'] = retweeted_user_screenname
    tweet_eng_csv_data['retweeted_user_geo_coding'] = retweeted_user_geo_coding
    tweet_eng_csv_data['retweeted_user_geo_coding_type'] = retweeted_user_geo_coding_type
    tweet_eng_csv_data['retweeted_retweet_count'] = retweeted_retweet_count
    tweet_eng_csv_data['retweeted_favorite_count'] = retweeted_favorite_count

    tweet_eng_csv_data['quoted_tweet_text'] = quoted_tweet_text
    tweet_eng_csv_data['quoted_tweet_id'] = quoted_tweet_id
    tweet_eng_csv_data['quoted_tweet_time'] = quoted_tweet_time
    tweet_eng_csv_data['quoted_user_id'] = quoted_user_id
    tweet_eng_csv_data['quoted_user_name'] = quoted_user_name
    tweet_eng_csv_data['quoted_user_verified'] = quoted_user_verified
    tweet_eng_csv_data['quoted_user_screenname'] = quoted_user_screenname
    tweet_eng_csv_data['quoted_user_geo_coding'] = quoted_user_geo_coding
    tweet_eng_csv_data['quoted_user_geo_coding_type'] = quoted_user_geo_coding_type
    tweet_eng_csv_data['quoted_retweet_count'] = quoted_retweet_count
    tweet_eng_csv_data['quoted_favorite_count'] = quoted_favorite_count

    # batch storing 1000 tweets
    df = pd.DataFrame(data=tweet_csv_data)
    tw_file_name = "data/v2/{}/{}_{}.csv".format("tw_sg_" + db_name.lower(),
                                              collection_no, start_csv_no)
    df.to_csv(tw_file_name)

    df = pd.DataFrame(data=tweet_eng_csv_data)
    tw_eng_file_name = "data/v2/{}/{}_{}.csv".format("tw_eng_sg_" + db_name.lower(),
                                                  collection_no, start_csv_no)
    df.to_csv(tw_eng_file_name)
    print("Final saving Saved tweets --->", tw_file_name, tw_eng_file_name)

    print("Time taken for this CSV: ", datetime.datetime.fromtimestamp(time.time() - st).strftime("%H: %M: %S"))

def _set_connetion():
    return SSHTunnelForwarder(
        os.environ.get('MONGO_HOST'),
        ssh_username=os.environ.get('MONGO_USER'),
        ssh_password=os.environ.get('MONGO_PASS'),
        remote_bind_address=('127.0.0.1', 27017))


if __name__ == "__main__":
    server = _set_connetion()
    server.start()

    client = MongoClient('127.0.0.1', server.local_bind_port)

    CURR_MAX_COLELCTION = 102
    db_name = "COVID_VACCINE"
    # db_name = "AGE_RACE"
    db = client[db_name]

    sg_users = set()
    with open("./min_3_following_users.txt") as f:
        for line in f:
            sg_users.add(line.strip())

    print("Total twitter users: ", len(sg_users))


    for collection_no in [100]:#range(94, 96):#range(87, 89): #CURR_MAX_COLELCTION + 1):
        collection_name = "tweets_" + str(collection_no)
        collection_data = db[collection_name]
        print('Starting to collect tweets for colelction no. {}'.format(
            collection_no).center(100, '-'))

        create_geo_users_csv(collection_data, 4,
                             running_tw_save_count=1000, max_csv_tw_count=10000)

    server.stop()
