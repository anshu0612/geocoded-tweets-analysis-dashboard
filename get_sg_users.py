# from io import DEFAULT_BUFFER_SIZE
import os
import time
import argparse

from dotenv import load_dotenv
from twython import Twython
from collections import Counter

from utils.constants import DEFAULT_MIN_FOLLOWING_REQUIRED, MIN_SG_ACCOUNTS_FOLLWERS_PATH, SCREEN_NAMES, SG_ACCOUNTS_FOLLOWERS_PATH, USER_TXT_PATH

load_dotenv()

APP_KEY = os.environ.get('TWITTER_APP_KEY')
APP_SECRET = os.environ.get('TWITTER_APP_SECRET')
OAUTH_TOKEN = os.environ.get('TWITTER_OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = os.environ.get('TWITTER_OAUTH_TOKEN_SECRET')

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)


def _get_all_followers(screen_name):
    '''
        Collecting the list of followers of Singapore-based accounts
    '''
    id_list = []
    next_cursor = -1
    while True:
        response = twitter.get_followers_ids(
            screen_name=screen_name, cursor=next_cursor)
        id_list.extend(response['ids'])
        print(len(id_list))
        next_cursor = response['next_cursor']
        if next_cursor == 0:
            return id_list
        time.sleep(61)
    return None


def _merge_all_followers(sg_accounts_followers):
    '''
        Merging the list of followers of Singapore-based accounts
    '''
    for txt in os.listdir(SG_ACCOUNTS_FOLLOWERS_PATH):
        with open(SG_ACCOUNTS_FOLLOWERS_PATH + txt) as f:
            for line in f:
                sg_accounts_followers.append(line.strip())

    print("total users:", len(sg_accounts_followers))
    print("total unique users:", len(set(sg_accounts_followers)))
    print("total files (accounts)", len(os.listdir(USER_TXT_PATH)))

    return sg_accounts_followers


def _get_min_following_followers_id(sg_accounts_followers, min_following_required):
    '''
        Filtering and saving the list of followers who follow atleast 
        `min_following_required`  Singapore-based accounts
    '''
    users_count = Counter(sg_accounts_followers)
    users_2 = [k for k, v in users_count.items() if v >=
               min_following_required]
    f = open(MIN_SG_ACCOUNTS_FOLLWERS_PATH, "w")
    for u in users_2:
        f.write("{}\n".format(u))
    f.flush()
    f.close()


def get_sg_users(min_following_required=DEFAULT_MIN_FOLLOWING_REQUIRED):
    for screen_name in SCREEN_NAMES:
        file = open(os.path.join(SG_ACCOUNTS_FOLLOWERS_PATH,
                    '{}.txt'.format(screen_name)), 'a+')
        fosllower_ids = _get_all_followers(screen_name)
        if follower_ids is not None:
            for follower_id in follower_ids:
                file.write('{}'.format(follower_id))
        time.sleep(61)
        file.flush()
        file.close()

    sg_accounts_followers = list()
    sg_accounts_followers = _merge_all_followers(sg_accounts_followers, )
    _get_min_following_followers_id(
        sg_accounts_followers, min_following_required)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--min_following_required', type=int, default=2,
                        help="Filter users following at least these"
                        "number of Singapore-based official accounts")
    args = parser.parse_args()
    get_sg_users(args.min_following_required)
