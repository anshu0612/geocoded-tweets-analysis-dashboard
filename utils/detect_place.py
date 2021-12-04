import re
import spacy
from geopy.geocoders import Nominatim

from constants.common import ALPHA2_TO_COUNTRY, COUNTRY_TO_ALPHA2, GEOCODER_AGENT_NAME
from constants.country_config import COUNTRY, KNOWN_USERNAMES_COUNTRIES

locator = Nominatim(user_agent=GEOCODER_AGENT_NAME)
nlp = spacy.load('en_core_web_sm')


def get_geo_user_location(location_desc):
    '''
    Input: Location Noisy Description - string
    Output: (longitude, latitude, country, country_code) - Tuple
    1. Remove numbers and set to lowercase
    2. Spacy to find GPE entity -- place # performs better than nltk
    3. Use geocoder to find the lat, long, countr, country_code

    More info: #https://geopy.readthedocs.io/en/stable/#geopy.location.Location.address
    '''
    location_desc = re.sub(r'\d+', '', location_desc).lower()
    location_desc = nlp(location_desc)
    for ent in location_desc.ents:
        if ent.label_ == "GPE":
            try:
                loc = locator.geocode(ent.text)
                if loc:
                    return get_geo_latlng(loc.raw['lon'], loc.raw['lat'])
            except Exception as e:
                print("Error in get_geo_user_location function :", e)

    return None


def get_geo_latlng(lng, lat):
    '''
    Input: (longitude, latitude) - float
    Output: (country, country_code) - Tuple 

    Alternative:
    # from geopy.geocoders import GoogleV3
    # geolocator = GoogleV3(api_key='Your_API_Key')
    # location = geolocator.reverse("52.509669, 13.376294")
    # print(location.address)
    '''
    try:
        coordinates = str(lat) + "," + str(lng)
        location = locator.reverse(coordinates)
        cc = location.raw['address']['country_code'].upper()
        return (ALPHA2_TO_COUNTRY[cc], cc)
    except Exception as e:
        print("Error in get_geo_latlng: ", e)
        return None


def geo_coding(tweet):
    '''
        Get country of a tweets user
    '''
    country_info = None
    coding_type = None
    try:
        u = tweet['user']

        if u['screen_name'] in KNOWN_USERNAMES_COUNTRIES:
            country_info = (
                ALPHA2_TO_COUNTRY[u['screen_name']], u['screen_name'])
            coding_type = 'Knowns'
        elif tweet['coordinates']:  # exact location
            country_info = get_geo_latlng(
                tweet['coordinates']['coordinates'][0], tweet['coordinates']['coordinates'][1])
            coding_type = 'Coordinates'
        elif 'place' in tweet and tweet['place']:  # specific place or country
            p = tweet['place']
            country_info = (
                ALPHA2_TO_COUNTRY[p['country_code']], p['country_code'])
            coding_type = 'Place'

        if not country_info and u['location']:
            if COUNTRY and (COUNTRY.lower() in u['location'].lower()):
                # prevent unncessary API call
                country_info = (COUNTRY, COUNTRY_TO_ALPHA2[COUNTRY])
            else:
                country_info = get_geo_user_location(u['location'])

            if country_info:
                coding_type = 'Location'

        if not country_info and u['description']:
            country_info = get_geo_user_location(u['description'])
            if country_info:
                coding_type = 'Description'

    except Exception as e:
        print(e)
    return country_info, coding_type
