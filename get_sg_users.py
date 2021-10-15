APP_KEY = '7W6kb6pJp1fsWl3rNC8XhWBtW'
APP_SECRET = 'Uj3yuxuQXL0pSuUiVGKmRGFfpla8lebIRFyelHCTDmuEvSdaex'
OAUTH_TOKEN = '1224622085932113920-ST4ayJj7iV34OsOzMYFHVdnxfXFHxz'
OAUTH_TOKEN_SECRET = '2tjutFSybgh0ewJfzt2wBEqwkZT2GY7CU49MHMQi7NMdW'

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

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

def get_all_followers(screen_name):
    id_list = []
    next_cursor = -1
    while True:
        response = twitter.get_followers_ids(screen_name=screen_name, cursor=next_cursor)
        id_list.extend(response['ids'])
        print(len(id_list))
        next_cursor = response['next_cursor']
        if next_cursor == 0:
            return id_list
        time.sleep(61)
    return None

for screen_name in SCREEN_NAMES:
    file = open('{}.txt'.format(screen_name), 'a+')
    print(screen_name)
    follower_ids = get_all_followers(screen_name)
    if follower_ids is not None:
        for follower_id in follower_ids:
            file.write('{}\n'.format(follower_id))
        print("done-->", screen_name)
    time.sleep(61)
    file.flush()
    file.close()


# Merging the list of users from SG accounts
USER_TXT_PATH = "sg_accounts/"

# users = set()
users = list()
for txt in os.listdir(USER_TXT_PATH):
    with open(USER_TXT_PATH + txt) as f:
        for line in f:
            users.append(line.strip())

print("total users:", len(users))    
print("total unique users:", len(set(users))) 
print("total files (accounts)", len(os.listdir(USER_TXT_PATH)))

# STcom.txt -------------------0
# ChannelNewsAsia.txt -------------------0