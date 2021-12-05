# :round_pushpin:	 Geocoded Tweets Analysis Dashboard :chart_with_downwards_trend:	 :chart_with_upwards_trend:	:bar_chart:	

This is an **interactive**, **configurable** and **generic** dashboard. 
It helps in visualizing some key insights from tweets of **country-specific** or **global** users. 

--------------------------------------------------------------------------------
> The application is built using [Plotly Dash](https://plotly.com/dash/).
--------------------------------------------------------------------------------

The key insights include:

:small_orange_diamond: &nbsp; Top influential users and their country <br />
:small_orange_diamond: &nbsp; Top influential countries and analyzing tweets from those countries <br />
:small_orange_diamond: &nbsp; Communities of users; networking graph and communities' tweets analysis <br />
:small_orange_diamond: &nbsp; Reactive tweets (among the most quoted tweets) - tweets that received extreme sentiments <br />
:small_orange_diamond: &nbsp; Viral local retweets (By users based in the specified country. For global level, viral local tweets are ignored) <br />
:small_orange_diamond: &nbsp; Viral global retweets (By users NOT based in the specified country.) <br />
:small_orange_diamond: &nbsp; Potentially sensitive tweets analysis <br />
:small_orange_diamond: &nbsp; Popular mentions and hashtags <br />
:small_orange_diamond: &nbsp; Sentiment analysis <br />
:small_orange_diamond: &nbsp; Daily tweets counts <br />
:small_orange_diamond: &nbsp; Basic statistics - total tweets, avg no. of tweets per day, no. of unique users, and date range of the collected tweets <br />
  
![Alt text](assets/dash_glimpse.png)


Checkout the demos for: 
- Country-specific 
    - :singapore:	&nbsp; [Singapore](http://sg-tweets-monitoring.herokuapp.com/) 
    - :india: &nbsp; [India](http://sg-tweets-monitoring.herokuapp.com/)
    - :us:	&nbsp; [United States](http://sg-tweets-monitoring.herokuapp.com/)
- :earth_americas:&nbsp; [Global level](http://sg-tweets-monitoring.herokuapp.com/) 

## Content

<!-- toc -->
- [About](#about)
- [Running the Application on Sample Data ](#running-the-application-on-sample-data)
- [Setup for Country-specific or Global Level Tweets Insights Generation](#setup-for-country-specific-or-global-level-tweets-insights-generation)
- [Additional Step for Singapore-based Users Tweets Collection](#additional-step-for-singapore-based-users-tweets-collection)
- [Future Work](#future-work)
<!-- tocstop -->


## About

The repository contains code for: 
- Fetching followers of 59 Singapore-based official accounts (such as Ministry of Education, Health, and so on)  
- Geocoding tweets by using location, user description, place, and coordinates data
- Filtering Singapore-based tweets that are already ingested into MongoDB 
- Notebooks containing exploratory data analysis on the collected tweets
- Pipeline for generating key insights i.e., dashboard data (`csv` and `json` files)
- Plotly Dash application for visualizing the insights


## Running the Application on Sample Data 

###  Step 1: Git clone the repository 

```
git clone https://github.com/anshu0612/geocoded-tweets-analysis.git
```

###  Step 2: Setting up the environment and running the application

- Install dependencies 
```
pip3 install -r requirements.txt
```

- Run the application 
```
python3 app.py
```

If you face environment dependencies then you can use **Docker Image** instead. 

- Install Docker on your system 

- Run the below command to build the docker image
```
docker image build -t geocoded-tweets-insights-dash:latest .
```

- Run the image 
```
docker container run -d -p 5000:5000 geocoded-tweets-insights-dash
```

### Step 3: Access the application on your local
Open  http://localhost:5000/  to see the application running 


## Setup for Country-specific or Global Level Tweets Insights Generation

###  Step :one: &nbsp; : &nbsp; Setup MongoDB configurations 

Create an .env file, and add the below required details for fetching tweets from MongoDB
```python
MONGO_HOST = <mongo_host>
MONGO_USER = <mongo_username>
MONGO_PASS = <mongo_password>
```
--------------------------------------------------------------------------------
> You can update the `get_tweets.py` file for any other source of tweets data
--------------------------------------------------------------------------------


###  Step :two: &nbsp; : &nbsp; Update the `constants/country_config.py` file

For collecting country-specific tweets
```python
# (String) Should be Alpha2 country code
# Check `COUNTRY_TO_ALPHA2` for reference in constants/commmon.py file
# Example: 'SG'
COUNTRY_CODE = None

# (List) of country slangs
# Example 1: ['sg', 'spore', 'singapore', 'singapura']
# Example 2: ['United States', 'america', 'usa', 'us', 'united states of america', 'u.s.', 'states', 'u.s.a']
# --------- USE: ---------
# 1. Helps in estimating a user's location based on the country name slangs
# 2. Filtering tweets based on the country name slangs  present in 
#    `location description` and `profile description` of a user
# 3. Skip the country name slangs from the top hashtags
COUNTRY_SLANGS = []

# (Dictionary) - {<twitter_user_screen_name>: <twitter_user_country_code>} - Prior knowledge of a user's country
# Example {'muttons': 'SG', 'POTUS': 'US'}
KNOWN_USERNAMES_COUNTRIES = {}
```

--------------------------------------------------------------------------------
> :heavy_exclamation_mark: **Important:** Do not update the file if you intend to collect global tweets from the users 
--------------------------------------------------------------------------------


###  Step :three: &nbsp; : &nbsp; Collect tweets 

Sample command to run the python script to collect the tweets
```bash
python3 get_tweets.py --db_name COVID_VACCINE --collection_no_list 88 89
```

**Arguments**
| Argument | Description | Default
| ---- | --- | --- |
| db_name | Database name to fetch tweets from | - |
| collection_no_list | List of MongoDB collections | - |
| running_tweets_save_count | Number of tweets to save during tweets processing | 1000 |
| max_csv_tweets_count | Maximum no. of tweets to save in a csv | 10000 |

The csv files for the: 
- The **country-specific** tweets will be saved in `data/<country>/fragmented_tweets/tweets` and `data/<country>/fragmented_tweets/tweets/tweets_engagements` directories
- The **global** tweets will be saved in `data/global/fragmented_tweets/tweets` and `data/global/fragmented_tweets/tweets_engagements` directories

###  Step :four: &nbsp; : &nbsp; Process tweets 

Run the python script to process the tweets
```bash
python3 process_tweets.py
```

This will merge and join all the csvs files, and then do the required processing. 

The generated file will be stored in:
- For **country-specific** tweets: `data/<country>/<country>_tweets.csv`
- For **global** tweets: `data/global/global_tweets.csv`

###  Step :five: &nbsp; : &nbsp; Generate Dashboard data  

Run the python script to generate data for the dashboard
```bash
python3 generate_dash_data.py
```

This will create the necessary `csv` and `json` data files for the dashboard visualization.

> You can setup the dashboard related constants in the `data/dash_constants.py`

The generated data directories containing the files will be stored in:
- For **country-specific** tweets: `data/<country>/dash_output/....`
- For **global** tweets: `data/global/dash_output/....`

###  Step :six: &nbsp; : &nbsp; Run the application
Yay! If you successfully ran all the above steps, then go ahead and run the application. :partying_face:	

```bash
python3 app.py
```

## Additional Step for Singapore-based Users Tweets Collection

### 1. Fetching followers of the Singapore-based official accounts`

Running the below command fetches the followers of the 59 collected Singapore-based official accounts. 
```
python3 get_sg_users.py --min_following_required 2
```
**Arguments**

| Argument | Description | Default
| ---- | --- | --- |
| min_following_required | Filter users following at least these number of Singapore-based official accounts | 2 |

The file `data/singapore/min_following_users.txt` contains the user ids of the collected twitter Singapore-based official accounts.

The list of followers will be saved in `data/singapore/sg_accounts_followers/` folder.

## Future Work


