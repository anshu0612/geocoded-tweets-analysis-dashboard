'''
PLEASE DO NOT UPDATE THIS FILE IF:
You intend to collect global tweets i.e., not country-specific tweets

PLEASE ONLY UPDATE THIS FILE IF: 
You intend to collect country-specific tweets
'''

# (String) Should be Alpha2 country code
# Check `COUNTRY_TO_ALPHA2` for reference in constants/commmon.py file
# Example: 'SG'
COUNTRY_CODE = 'SG'

# (List) of country slangs
# Example 1: ['sg', 'spore', 'singapore', 'singapura']
# Example 2: ['United States', 'america', 'usa', 'us', 'united states of america', 'u.s.', 'states', 'u.s.a']
# --------- USE: ---------
# 1. Helps in estimating a user's location based on the country name slangs
# 2. Filtering tweets based on the country name slangs  present in
#    `location description` and `profile description` of a user
# 3. Skip the country name slangs from the top hashtags
COUNTRY_SLANGS = ['sg', 'spore', 'singapore', 'singapura']

# (Dictionary) - {<twitter_user_screen_name>: <twitter_user_country_code>} - Prior knowledge of a user's country
# Example {'muttons': 'SG', 'POTUS': 'US'}
KNOWN_USERNAMES_COUNTRY = {
    'muttons': 'SG',
    'cz_binance': 'SG',
    'leehsienloong': 'SG',
    'ChannelNewsAsia': 'SG',
    'stbusinessdesk': 'SG',
    'IrrawaddyNews': 'MM', 
    'TODAYonline': 'SG',
    'straits_times': 'SG',
    'kixes': 'SG'
}

# -------------------------- EXTRA INFO FOR SINGAPORE ---------------------------
# --------------------------------------------------------------------------------

# Singapore-based official twitter accounts
SG_SCREEN_NAMES = ['mindefsg', 'MOEsg', 'sporeMOH', 'LTAsg', 'SMRT_Singapore', 'SBSTransit_Ltd',
                   'SingaporeHDB', 'MNDSingapore', 'mhasingapore', 'SingaporePolice', 'URAsg',
                   'MAS_sg', 'MOFsg', 'ICASingapore', 'SingaporeMCI', 'nlbsingapore', 'IMDAsg',
                   'NEAsg', 'nparksbuzz', 'SGSportsHub', 'govsingapore', 'SingaporeCAAS', 'MFAsg',
                   'iremembersg', 'youthsg', 'NUSingapore', 'NTUsg', 'sgSMU', 'sutdsg', 'SGRedCross',
                   'STcom', 'ChannelNewsAsia', 'TODAYonline', 'asiaonecom', 'thenewpaper', 'MothershipSG',
                   'Singtel', 'StarHub', 'MyRepublicSG', 'M1Singapore', 'temasekpoly', 'singaporetech',
                   'SingaporePoly', 'PUBsingapore', 'NgeeAnnNP', 'ITESpore', 'mediacorp', 'YahooSG',
                   'TimeOutSG', 'VisitSingapore', 'stb_sg', 'GovTechSG', 'SGmagazine', 'mySingapore',
                   'sgelection', 'SGAG_SG', 'TEDxSingapore', 'STATravelSG', 'STPix']

# fetch users following at least this number of Singapore-based official twitter accounts
DEFAULT_MIN_FOLLOWING_REQUIRED = 2

# path to the directory to save files containing Singapore-based official twitter accounts followers
SG_ACCOUNTS_FOLLOWERS_PATH = 'data/sg_accounts_followers/'

# path to the file to save users who follow x no. of Singapore-based official twitter accounts
MIN_SG_ACCOUNTS_FOLLWERS_PATH = "data/general/min_following_users.txt"
