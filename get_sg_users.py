import os
import time

from dotenv import load_dotenv
from twython import Twython
from collections import Counter

load_dotenv()

APP_KEY = os.environ.get('TWITTER_APP_KEY')
APP_SECRET = os.environ.get('TWITTER_APP_SECRET')
OAUTH_TOKEN = os.environ.get('TWITTER_OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = os.environ.get('TWITTER_OAUTH_TOKEN_SECRET')

SCREEN_NAMES = ['mindefsg', 'MOEsg', 'sporeMOH', 'LTAsg', 'SMRT_Singapore', 'SBSTransit_Ltd',
                'SingaporeHDB', 'MNDSingapore', 'mhasingapore', 'SingaporePolice', 'URAsg',
                'MAS_sg', 'MOFsg', 'ICASingapore', 'SingaporeMCI', 'nlbsingapore', 'IMDAsg',
                'NEAsg', 'nparksbuzz', 'SGSportsHub', 'govsingapore', 'SingaporeCAAS', 'MFAsg',
                'iremembersg', 'youthsg', 'NUSingapore', 'NTUsg', 'sgSMU', 'sutdsg', 'SGRedCross',
                'STcom', 'ChannelNewsAsia', 'TODAYonline', 'asiaonecom', 'thenewpaper', 'MothershipSG',
                'Singtel', 'StarHub', 'MyRepublicSG', 'M1Singapore', 'temasekpoly', 'singaporetech',
                'SingaporePoly', 'PUBsingapore', 'NgeeAnnNP', 'ITESpore', 'mediacorp', 'YahooSG',
                'TimeOutSG', 'VisitSingapore', 'stb_sg', 'GovTechSG', 'SGmagazine', 'mySingapore',
                'sgelection', 'SGAG_SG', 'TEDxSingapore', 'STATravelSG', 'STPix']

USER_TXT_PATH = "sg_accounts/"

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
    for txt in os.listdir(USER_TXT_PATH):
        with open(USER_TXT_PATH + txt) as f:
            for line in f:
                sg_accounts_followers.append(line.strip())

    print("total users:", len(sg_accounts_followers))
    print("total unique users:", len(set(sg_accounts_followers)))
    print("total files (accounts)", len(os.listdir(USER_TXT_PATH)))


def _get_min_following_followers_id(min_following_required):
    '''
        Filtering and saving the list of followers who follow atleast 
        `min_following_required`  Singapore-based accounts
    '''
    users_count = Counter(sg_accounts_followers)
    users_2 = [k for k, v in users_count.items() if v >=
               min_following_required]
    f = open("data/min_2_following_users.txt", "w")
    for u in users_2:
        f.write("{}\n".format(u))
    f.flush()
    f.close()


if __name__ == "__main__":
    for screen_name in SCREEN_NAMES:
        file = open('{}.txt'.format(screen_name), 'a+')
        print(screen_name)
        follower_ids = _get_all_followers(screen_name)
        if follower_ids is not None:
            for follower_id in follower_ids:
                file.write('{}\n'.format(follower_id))
        time.sleep(61)
        file.flush()
        file.close()

    sg_accounts_followers = list()
    _merge_all_followers(sg_accounts_followers, )
    _get_min_following_followers_id(2)
