import re
import spacy
from geopy.geocoders import Nominatim
from constant import ALPHA2_TO_COUNTRY


locator = Nominatim(user_agent="anshu")
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
                print("here is the error:", e)


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
        print(e)
        return None
