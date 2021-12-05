'''
PLEASE DO NOT UPDATE THIS FILE IF:
You intend to collect global tweets i.e., not country-specific tweets

PLEASE ONLY UPDATE THIS FILE IF: 
You intend to collect country-specific tweets
'''

# (String) Should be Alpha2 country code
# Check `COUNTRY_TO_ALPHA2` for reference in constants/commmon.py file
# Example: 'SG'
COUNTRY_CODE = 'US'

# (List) of country slangs
# Example 1: ['sg', 'spore', 'singapore', 'singapura']
# Example 2: ['United States', 'america', 'usa', 'us', 'united states of america', 'u.s.', 'states', 'u.s.a']
# --------- USE: ---------
# 1. Helps in estimating a user's location based on the country name slangs
# 2. Filtering tweets based on the country name slangs  present in
#    `location description` and `profile description` of a user
# 3. Skip the country name slangs from the top hashtags
COUNTRY_SLANGS = ['United States', 'america', 'usa', 'us',
                  'united states of america', 'u.s.', 'states', 'u.s.a']

# (Dictionary) - {<twitter_user_screen_name>: <twitter_user_country_code>} - Prior knowledge of a user's country
# Example {'muttons': 'SG', 'POTUS': 'US'}
KNOWN_USERNAMES_COUNTRY = {}
